#!/usr/bin/env python3
"""Explicitly opted-in QC copies only: register, review, then dry-run/apply Trash.

This is not a downloader or a perception tool. Never empties Trash. The operator
must record an exact UI download mapping and a truthful, source-bound QC report.
"""
import argparse
import json
from pathlib import Path

import media_registry as registry

MODE = 'TEMP_DOWNLOAD_REVIEW_THEN_TRASH'
VIDEO_EXT = {'.mp4', '.mov', '.mkv', '.webm'}


def checked_file(root, value):
    root = Path(root).resolve()
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = root / path
    if '..' in path.parts or not path.is_relative_to(root):
        raise ValueError('OUTSIDE_OWNED_ROOT')
    if any(p.is_symlink() for p in [path, *path.parents] if p.is_relative_to(root)):
        raise ValueError('SYMLINK_REJECTED')
    if not path.is_file() or path.stat().st_nlink != 1:
        raise ValueError('REGULAR_SINGLE_LINK_FILE_REQUIRED')
    return path


def read_json(project, path):
    p = checked_file(project, path)
    return p, json.loads(p.read_text())


def authorization(project, path):
    p, data = read_json(project, path)
    if (data.get('mode') != MODE or not data.get('user_quote')
            or data.get('source') != 'current_explicit_user_request'
            or data.get('max_concurrent_local_clips') != 1):
        raise ValueError('EXPLICIT_TEMP_QC_AUTHORIZATION_REQUIRED')
    return {'path': str(p), 'sha256': registry.sha256(p)}


def register(project, receipt, auth):
    project = Path(project).resolve()
    auth_binding = authorization(project, auth)
    receipt_path, data = read_json(project, receipt)
    temp_root = registry.folder(project, 'videos_candidates') / '_qc_temp'
    source = checked_file(temp_root, data['path'])
    if source.suffix.lower() not in VIDEO_EXT:
        raise ValueError('VIDEO_ONLY')
    if (data.get('owned_by_qc_run') is not True or data.get('cloud_preserved') is not True
            or not data.get('source_ui') or not data.get('block_id')):
        raise ValueError('EXACT_NEW_DOWNLOAD_RECEIPT_REQUIRED')
    _, baseline = read_json(project, data['download_baseline'])
    if not data.get('download_original_path') or data['download_original_path'] in baseline:
        raise ValueError('PREEXISTING_DOWNLOAD_REJECTED')
    digest = registry.sha256(source)
    if digest != data.get('sha256') or source.stat().st_size != data.get('bytes'):
        raise ValueError('DOWNLOAD_HASH_SIZE_MISMATCH')
    if registry.asset_for_path(project, source):
        raise ValueError('EXISTING_ASSET_ADOPTION_REJECTED')
    with registry.connect(project) as conn:
        for row in conn.execute('SELECT metadata_json FROM assets WHERE state<>?', ('trashed',)):
            if json.loads(row['metadata_json']).get('disposable_qc'):
                raise ValueError('ONE_PENDING_QC_COPY_LIMIT')
    return registry.ingest(project, source, kind='video', state='candidate',
        work_item_id=data['block_id'], origin_lane='seedance_qc', provider='runway',
        run_id=receipt_path.stem, metadata={'disposable_qc': {
            'authorization': auth_binding, 'receipt': str(receipt_path),
            'receipt_sha256': registry.sha256(receipt_path), 'source_ui': data['source_ui'],
            'cloud_preserved': True}})


def cleanup(project, asset_id, report, apply=False):
    project = Path(project).resolve()
    asset = registry.get_asset(project, asset_id)
    owned = json.loads(asset['metadata_json']).get('disposable_qc')
    if not owned or asset['kind'] != 'video' or asset['origin_lane'] != 'seedance_qc':
        raise ValueError('NOT_A_DISPOSABLE_QC_COPY')
    binding = owned['authorization']
    if authorization(project, binding['path']) != binding:
        raise ValueError('AUTHORIZATION_CHANGED')
    receipt_path = checked_file(project, owned['receipt'])
    if registry.sha256(receipt_path) != owned['receipt_sha256']:
        raise ValueError('DOWNLOAD_RECEIPT_CHANGED')
    report_path, data = read_json(project, report)
    review = data.get('disposable_copy_review', {})
    if (review.get('asset_id') != asset_id or review.get('source_sha256') != asset['sha256']
            or review.get('review_complete_for_declared_scope') is not True
            or review.get('disposal_approved') is not True or not review.get('method')
            or not review.get('findings') or 'unverified_checks' not in review
            or review.get('cloud_preserved') is not True):
        raise ValueError('SOURCE_BOUND_COMPLETED_REVIEW_REQUIRED')
    report_hash = registry.sha256(report_path)
    if asset['state'] == 'trashed':
        with registry.connect(project) as conn:
            journal = conn.execute('SELECT reason FROM cleanup_journal WHERE asset_id=? ORDER BY id DESC LIMIT 1',
                                   (asset_id,)).fetchone()
        if not journal or f'report_sha256={report_hash}' not in journal['reason']:
            raise ValueError('TRASH_REPORT_BINDING_MISMATCH')
        return {'ok': True, 'state': 'ALREADY_TRASHED', 'asset_id': asset_id,
                'path': asset['current_path']}
    if asset['state'] != 'candidate':
        raise ValueError('PROTECTED_OR_CHANGED_ASSET_STATE')
    source = checked_file(registry.folder(project, 'videos_candidates'), asset['current_path'])
    if registry.sha256(source) != asset['sha256'] or source.stat().st_size != asset['size_bytes']:
        raise ValueError('OWNED_FILE_CHANGED')
    item = {'asset_id': asset_id, 'path': str(source), 'sha256': asset['sha256'],
            'reason': f'disposable_qc review={report_path.relative_to(project)} report_sha256={report_hash}'}
    if not apply:
        return {'ok': True, 'state': 'DRY_RUN', 'candidate': item}
    result = registry.move_candidates_to_trash(project, [item])
    if len(result) != 1 or source.exists():
        raise ValueError('TRASH_MOVE_NOT_CONFIRMED')
    target = Path(result[0]['trashed_path'])
    if registry.sha256(target) != asset['sha256']:
        raise ValueError('TRASH_HASH_MISMATCH')
    return {'ok': True, 'state': 'TRASHED', 'event': result[0],
            'disk_space_freed': False, 'cloud_preserved': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True)
    sub = parser.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('register')
    p.add_argument('--receipt', required=True); p.add_argument('--authorization', required=True)
    p = sub.add_parser('cleanup')
    p.add_argument('--asset-id', required=True); p.add_argument('--report', required=True)
    p.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    try:
        result = (register(args.project, args.receipt, args.authorization) if args.cmd == 'register'
                  else cleanup(args.project, args.asset_id, args.report, args.apply))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError) as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}, ensure_ascii=False))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
