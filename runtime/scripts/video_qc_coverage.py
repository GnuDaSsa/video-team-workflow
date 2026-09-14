#!/usr/bin/env python3
"""Read-only review coverage/next-check audit; never judges, extracts or promotes media.

Extend the existing per-asset QC report with ``coverage``; do not create another
queue/ledger. Source identity comes from the registry plus the real file/probe.
Evidence hashes bind operator observations, not proof of perception or quality.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sqlite3
import subprocess

import media_registry


METHODS = {'samples', 'native_frames', 'full_speed_video', 'audio', 'user_audio_approval'}


def interval(value, duration: float) -> tuple[float, float]:
    if (not isinstance(value, list) or len(value) != 2
            or any(type(n) not in (int, float) or not math.isfinite(n) for n in value)):
        raise ValueError('QC_INTERVAL_INVALID')
    start, end = value
    if not 0 <= start < end <= duration + 0.001:
        raise ValueError('QC_INTERVAL_OUT_OF_SOURCE')
    return float(start), float(end)


def covers(ranges: list, duration: float) -> bool:
    return not uncovered(ranges, duration)


def uncovered(ranges: list, duration: float) -> list:
    cursor = 0.0
    gaps = []
    for start, end in sorted(ranges):
        if start > cursor + 0.001:
            gaps.append([cursor, start])
        cursor = max(cursor, end)
    if cursor < duration - 0.001:
        gaps.append([cursor, duration])
    return gaps


def audit_coverage(report: dict, source: dict, project: Path, *, request: dict = None) -> dict:
    """Validate declarations and choose unreviewed work, never infer unseen QC."""
    project = project.resolve()
    coverage = report.get('coverage')
    if not isinstance(coverage, dict) or coverage.get('version') != 1:
        raise ValueError('QC_COVERAGE_BINDING_REQUIRED: extend the existing report, do not invent past review')
    if (coverage.get('asset_id') != source['asset_id']
            or coverage.get('source_sha256') != source['sha256']):
        raise ValueError('QC_SOURCE_CHANGED_REVIEW_REQUIRED')
    duration = source['duration_seconds']
    if type(duration) not in (int, float) or not math.isfinite(duration) or duration <= 0:
        raise ValueError('QC_SOURCE_DURATION_INVALID')
    if type(source.get('has_audio')) is not bool:
        raise ValueError('QC_SOURCE_AUDIO_UNKNOWN')
    checks = coverage.get('checks')
    if not isinstance(checks, list) or not checks:
        raise ValueError('QC_CHECK_PLAN_REQUIRED')
    issues, resolved, actionable, blocked = [], [], [], []
    seen = set()
    for row in checks:
        if not isinstance(row, dict):
            raise ValueError('QC_CHECK_INVALID')
        key = row.get('check_id')
        if not isinstance(key, str) or not key.strip() or key in seen:
            raise ValueError('QC_CHECK_ID_MISSING_OR_DUPLICATE')
        seen.add(key)
        interval(row.get('range_seconds'), duration)
        if row.get('method') not in METHODS or row.get('status') not in {'resolved', 'pending', 'blocked'}:
            raise ValueError('QC_CHECK_METHOD_OR_STATUS_INVALID')
        if row['status'] != 'resolved':
            if row['status'] == 'blocked' and not row.get('reason'):
                raise ValueError('QC_BLOCK_REASON_REQUIRED')
            (blocked if row['status'] == 'blocked' else actionable).append(row)
            continue
        if row.get('outcome') not in {'pass', 'fail', 'hold'} or not row.get('finding'):
            raise ValueError('QC_RESOLVED_FINDING_REQUIRED')
        evidence = row.get('evidence')
        if not isinstance(evidence, list) or not evidence:
            issues.append('QC_EVIDENCE_MISSING:' + key)
            continue
        valid = True
        for item in evidence:
            if not isinstance(item, dict) or not isinstance(item.get('path'), str):
                valid = False
                break
            path = (project / item['path']).resolve()
            if (not path.is_relative_to(project) or not path.is_file()
                    or not path.stat().st_size or media_registry.sha256(path) != item.get('sha256')):
                valid = False
                break
        if not valid:
            issues.append('QC_EVIDENCE_MISSING_OR_CHANGED:' + key)
            continue
        resolved.append(row)
    ranges = lambda methods: [r['range_seconds'] for r in resolved if r['method'] in methods]
    video_reviewed = covers(ranges({'full_speed_video'}), duration)
    audio_reviewed = not source['has_audio'] or covers(ranges({'audio', 'user_audio_approval'}), duration)
    blockers = list(issues)
    if actionable or blocked:
        blockers.append('QC_CHECKS_UNRESOLVED')
    if any(r['outcome'] != 'pass' for r in resolved):
        blockers.append('QC_CREATIVE_FAIL_OR_HOLD')
    if not video_reviewed:
        blockers.append('QC_FULL_SPEED_VIDEO_REVIEW_MISSING')
    if not audio_reviewed:
        blockers.append('QC_AUDIO_REVIEW_MISSING')
    # A trim-only useful interval does not approve its defective source file.
    if report.get('verdict') != 'PASS':
        blockers.append('QC_WHOLE_ASSET_NOT_PASS')
    next_check = actionable[0] if actionable else None
    if next_check is None and not issues:
        # Finish missing mandatory modalities before spending another due check
        # on an already resolved geometry/identity slice. Respect blocked methods.
        for method, done in [('full_speed_video', video_reviewed), ('audio', audio_reviewed)]:
            related = {'audio', 'user_audio_approval'} if method == 'audio' else {method}
            if not done and not any(r['method'] in related for r in blocked):
                next_check = {'check_id': 'remaining_' + method, 'method': method,
                              'range_seconds': uncovered(ranges(related), duration)[0], 'status': 'pending'}
                break
    if issues:
        action = 'REPAIR_EVIDENCE_BINDING'
    elif next_check:
        action = 'REVIEW_NEXT_UNRESOLVED_CHECK'
    elif blocked:
        action = 'BLOCKED_REQUIRES_EXTERNAL_ACTION'
    else:
        action = 'DISPOSITION_COMPLETE'  # may be FAIL/HOLD, not approval
    if request:
        start, end = interval(request.get('range_seconds'), duration)
        if request.get('method') not in METHODS:
            raise ValueError('QC_REQUEST_METHOD_INVALID')
        reuse = [r for r in resolved if r['check_id'] == request.get('check_id')
                 and r['method'] == request['method']
                 and r['range_seconds'][0] <= start and r['range_seconds'][1] >= end]
        if reuse and not issues:
            action = ('REOPEN_WITH_EXPLICIT_REASON' if str(request.get('reopen_reason') or '').strip()
                      else 'REUSE_EXISTING_REVIEW')
    return {
        'ok': not issues, 'read_only': True, 'asset_id': source['asset_id'],
        'issues': issues, 'action': action, 'next_check': next_check,
        'resolved_check_ids': [r['check_id'] for r in resolved],
        'blocked_checks': blocked, 'promotion_blockers': blockers,
        'declarations_sufficient_for_manual_gate': not blockers,
        'full_speed_video_coverage_declared': video_reviewed,
        'audio_coverage_declared': audio_reviewed,
        'perception_verified_by_this_check': False, 'media_promoted': False,
    }


def registered_source(project: Path, asset_id: str) -> dict:
    database = media_registry.db_path(project)
    if not database.is_file():
        raise ValueError('QC_REGISTRY_MISSING')
    with sqlite3.connect(database.as_uri() + '?mode=ro', uri=True) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute('SELECT * FROM assets WHERE asset_id=?', (asset_id,)).fetchone()
    if not row or row['kind'] != 'video':
        raise ValueError('QC_REGISTERED_VIDEO_REQUIRED')
    path = Path(row['current_path']).resolve()
    if (not path.is_relative_to(project / 'media') or not path.is_file()
            or media_registry.sha256(path) != row['sha256']):
        raise ValueError('QC_REGISTERED_SOURCE_MISSING_OR_CHANGED')
    probe = subprocess.run(['ffprobe', '-v', 'error', '-show_format', '-show_streams',
                            '-of', 'json', str(path)], check=True, capture_output=True, text=True)
    data = json.loads(probe.stdout)
    if not any(s.get('codec_type') == 'video' for s in data['streams']):
        raise ValueError('QC_SOURCE_HAS_NO_VIDEO_STREAM')
    return {'asset_id': asset_id, 'sha256': row['sha256'],
            'duration_seconds': float(data['format']['duration']),
            'has_audio': any(s.get('codec_type') == 'audio' for s in data['streams'])}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--check-id', help='optional planned check to test for reuse')
    parser.add_argument('--start-sec', type=float)
    parser.add_argument('--end-sec', type=float)
    parser.add_argument('--method', choices=sorted(METHODS))
    parser.add_argument('--reopen-reason')
    args = parser.parse_args()
    try:
        project = args.project.expanduser().resolve()
        report_path = args.report.expanduser().resolve()
        if not report_path.is_relative_to(project):
            raise ValueError('QC_REPORT_OUTSIDE_PROJECT')
        report = json.loads(report_path.read_text(encoding='utf-8'))
        if not isinstance(report, dict):
            raise ValueError('QC_REPORT_MUST_BE_OBJECT')
        coverage = report.get('coverage')
        asset_id = coverage.get('asset_id') if isinstance(coverage, dict) else None
        if not asset_id:
            raise ValueError('QC_COVERAGE_BINDING_REQUIRED')
        source = registered_source(project, asset_id)
        request = ({'check_id': args.check_id, 'range_seconds': [args.start_sec, args.end_sec],
                    'method': args.method, 'reopen_reason': args.reopen_reason} if args.check_id else None)
        result = audit_coverage(report, source, project, request=request)
    except (OSError, ValueError, KeyError, TypeError, sqlite3.Error, subprocess.CalledProcessError) as exc:
        result = {'ok': False, 'error': str(exc), 'read_only': True, 'media_promoted': False}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
