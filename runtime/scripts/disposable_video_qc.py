#!/usr/bin/env python3
"""Owned QC copies: register, review, Trash, and optionally purge that exact copy.

Permanent purge needs recorded project-scoped permission. Never empties Trash.
This is not a downloader or perception tool; reports must state unverified checks.
"""
import argparse
import json
import os
from pathlib import Path

import media_registry as registry

MODE = 'TEMP_DOWNLOAD_REVIEW_THEN_TRASH'
PERMANENT_MODE = 'TEMP_DOWNLOAD_REVIEW_THEN_DELETE'
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
    if (data.get('mode') not in {MODE, PERMANENT_MODE} or not data.get('user_quote')
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


def cleanup(project, asset_id, report, apply=False, permanent_authorization=None):
    project = Path(project).resolve()
    if permanent_authorization is not None:
        permanent_permission(project, permanent_authorization)
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
        if permanent_authorization is not None:
            return purge(project, asset_id, report, permanent_authorization, apply)
        return {'ok': True, 'state': 'ALREADY_TRASHED', 'asset_id': asset_id, 'path': asset['current_path']}
    if asset['state'] != 'candidate':
        raise ValueError('PROTECTED_OR_CHANGED_ASSET_STATE')
    source = checked_file(registry.folder(project, 'videos_candidates'), asset['current_path'])
    if registry.sha256(source) != asset['sha256'] or source.stat().st_size != asset['size_bytes']:
        raise ValueError('OWNED_FILE_CHANGED')
    item = {'asset_id': asset_id, 'path': str(source), 'sha256': asset['sha256'],
            'reason': f'disposable_qc review={report_path.relative_to(project)} report_sha256={report_hash}'}
    if not apply:
        return {'ok': True, 'state': 'DRY_RUN', 'candidate': item,
                'permanent_deletion_requested': permanent_authorization is not None}
    result = registry.move_candidates_to_trash(project, [item])
    if len(result) != 1 or source.exists():
        raise ValueError('TRASH_MOVE_NOT_CONFIRMED')
    target = Path(result[0]['trashed_path'])
    if registry.sha256(target) != asset['sha256']:
        raise ValueError('TRASH_HASH_MISMATCH')
    if permanent_authorization is not None:
        return purge(project, asset_id, report, permanent_authorization, True)
    return {'ok': True, 'state': 'TRASHED', 'event': result[0],
            'disk_space_freed': False, 'cloud_preserved': True}


def permanent_permission(project, path):
    p, data = read_json(project, path)
    if (data.get('mode') != 'PERMANENT_QC_COPY_DELETE'
            or data.get('source') != 'current_explicit_user_request'
            or not data.get('user_quote') or data.get('permanent_delete') is not True
            or data.get('scope') != 'manifest_owned_qc_copies_only'
            or data.get('project') != str(project)):
        raise ValueError('EXPLICIT_PERMANENT_QC_PERMISSION_REQUIRED')
    return {'path': str(p), 'sha256': registry.sha256(p)}


def purge(project, asset_id, report, permanent_authorization, apply=False):
    """Delete only a previously reviewed registry-owned Trash copy, never a tree.

    Persist intent before unlink. Missing-without-intent is not proof of our
    deletion. Crash recovery verifies absence against the same saved intent.
    """
    project = Path(project).resolve()
    permission = permanent_permission(project, permanent_authorization)
    checked = cleanup(project, asset_id, report)  # validates immutable source/report ownership
    if checked['state'] != 'ALREADY_TRASHED':
        raise ValueError('VERIFIED_TRASH_STEP_REQUIRED')
    asset = registry.get_asset(project, asset_id)
    report_path = checked_file(project, report)
    report_hash = registry.sha256(report_path)
    with registry.connect(project) as conn:
        journal = conn.execute('SELECT * FROM cleanup_journal WHERE asset_id=? ORDER BY id DESC LIMIT 1',
                               (asset_id,)).fetchone()
        # Creating an empty journal table is metadata-only even in dry run.
        conn.execute('''CREATE TABLE IF NOT EXISTS disposable_qc_purge_journal (
            asset_id TEXT PRIMARY KEY, status TEXT NOT NULL, trashed_path TEXT NOT NULL,
            source_sha256 TEXT NOT NULL, report_sha256 TEXT NOT NULL,
            authorization_path TEXT NOT NULL, authorization_sha256 TEXT NOT NULL,
            size_bytes INTEGER NOT NULL, intent_at TEXT NOT NULL, deleted_at TEXT)''')
        previous = conn.execute('SELECT * FROM disposable_qc_purge_journal WHERE asset_id=?',
                                (asset_id,)).fetchone()
    root = Path(os.environ.get('VIDEO_TEAM_TRASH_ROOT', str(Path.home()/'.Trash'))).expanduser()
    if root.is_symlink():
        raise ValueError('TRASH_ROOT_SYMLINK_REJECTED')
    target = Path(asset['current_path'])
    if (not journal or journal['trashed_path'] != str(target)
            or journal['sha256'] != asset['sha256']
            or not journal['reason'].startswith('disposable_qc ')
            or target.parent != root.resolve()
            or not target.name.startswith(f'{project.name}__{asset_id}__')):
        raise ValueError('EXACT_OWNED_TRASH_JOURNAL_REQUIRED')
    intent = {'asset_id': asset_id, 'trashed_path': str(target), 'source_sha256': asset['sha256'],
              'report_sha256': report_hash, 'authorization_path': permission['path'],
              'authorization_sha256': permission['sha256'], 'size_bytes': asset['size_bytes']}
    if previous and any(previous[k] != v for k, v in intent.items()):
        raise ValueError('DELETE_INTENT_BINDING_CHANGED')
    exists = target.exists() or target.is_symlink()
    if previous and previous['status'] == 'DELETED':
        if exists:
            raise ValueError('PURGED_PATH_REAPPEARED')
        return {'ok': True, 'state': 'ALREADY_DELETED', 'asset_id': asset_id,
                'logical_bytes_deleted': asset['size_bytes'], 'cloud_preserved': True}
    if not exists and not previous:
        raise ValueError('MISSING_WITHOUT_DELETE_INTENT')
    if exists:
        checked_file(root, target)
        if registry.sha256(target) != asset['sha256'] or target.stat().st_size != asset['size_bytes']:
            raise ValueError('TRASH_COPY_CHANGED')
    if not apply:
        return {'ok': True, 'state': 'PURGE_DRY_RUN', 'candidate': intent}
    if not previous:
        with registry.connect(project) as conn:
            conn.execute('''INSERT INTO disposable_qc_purge_journal
                (asset_id,status,trashed_path,source_sha256,report_sha256,authorization_path,
                 authorization_sha256,size_bytes,intent_at) VALUES (?,?,?,?,?,?,?,?,?)''',
                (asset_id, 'INTENT', str(target), asset['sha256'], report_hash,
                 permission['path'], permission['sha256'], asset['size_bytes'], registry.now_iso()))
    recovered_absence = not exists
    if exists:
        # Recheck exact inode and immutable evidence immediately before unlink.
        checked_file(root, target)
        fd = os.open(target, os.O_RDONLY | os.O_NOFOLLOW)
        try:
            stat = os.fstat(fd)
            current = target.lstat()
            if (stat.st_dev, stat.st_ino, stat.st_nlink) != (current.st_dev, current.st_ino, 1):
                raise ValueError('TRASH_INODE_CHANGED')
            if (registry.sha256(target) != asset['sha256']
                    or registry.sha256(report_path) != report_hash
                    or permanent_permission(project, permanent_authorization) != permission):
                raise ValueError('DELETE_EVIDENCE_CHANGED')
            target.unlink()  # exact verified file; no glob/rmtree/empty-Trash operation
        finally:
            os.close(fd)
    if target.exists() or target.is_symlink():
        raise ValueError('DELETE_ABSENCE_NOT_VERIFIED')
    at = registry.now_iso()
    with registry.connect(project) as conn:
        conn.execute('UPDATE disposable_qc_purge_journal SET status=?,deleted_at=? WHERE asset_id=?',
                     ('DELETED', at, asset_id))
        metadata = json.loads(asset['metadata_json'])
        metadata['disposable_qc']['permanent_deletion'] = dict(intent, deleted_at=at)
        conn.execute('UPDATE assets SET metadata_json=?,active=0,updated_at=? WHERE asset_id=?',
                     (json.dumps(metadata, ensure_ascii=False), at, asset_id))
    return {'ok': True, 'state': 'PERMANENTLY_DELETED', 'asset_id': asset_id,
            'path': str(target), 'logical_bytes_deleted': asset['size_bytes'],
            'recovered_saved_intent_absence': recovered_absence, 'cloud_preserved': True,
            'physical_free_space_measured': False, 'deleted_at': at}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True)
    sub = parser.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('register')
    p.add_argument('--receipt', required=True); p.add_argument('--authorization', required=True)
    p = sub.add_parser('cleanup')
    p.add_argument('--asset-id', required=True); p.add_argument('--report', required=True)
    p.add_argument('--apply', action='store_true')
    p.add_argument('--permanent-authorization', help='recorded project-scoped consent; purge only this owned copy after Trash')
    p = sub.add_parser('purge')
    p.add_argument('--asset-id', required=True); p.add_argument('--report', required=True)
    p.add_argument('--authorization', required=True); p.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    try:
        if args.cmd == 'register':
            result = register(args.project, args.receipt, args.authorization)
        elif args.cmd == 'purge':
            result = purge(args.project, args.asset_id, args.report, args.authorization, args.apply)
        else:
            result = cleanup(args.project, args.asset_id, args.report, args.apply, args.permanent_authorization)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError) as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}, ensure_ascii=False))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
