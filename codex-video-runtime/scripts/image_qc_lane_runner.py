#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import sys
import time


def now() -> str:
    return dt.datetime.now().astimezone().isoformat()


def load_json(path: Path, default=None):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return default


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def append_jsonl(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False) + '\n')


def read_queue(path: Path) -> list[dict]:
    rows = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding='utf-8', errors='ignore').splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return rows


def emit_ready_blocks(project: Path, qc_by_ref: dict[str, dict]) -> list[str]:
    """Fan in per-reference QC PASS/WARN_PASS events into Sukuna image-bundle handoffs.

    Image QC must not directly start or address Seedance. It emits a reference-bundle
    readiness event for Sukuna/Image. Sukuna then posts/briefs the bundle and hands it
    to Toji/Seedance. Runtime dispatch gates video on that visible handoff, not on QC alone.
    """
    block_map_path = project / 'lanes' / 'planner' / 'multi_reference_block_map.json'
    if not block_map_path.exists():
        return []
    block_map = load_json(block_map_path, {}) or {}
    qpath = project / 'queues' / 'reference_bundle_queue.jsonl'
    existing_ready = set()
    for row in read_queue(qpath):
        if row.get('event') == 'REFERENCE_BUNDLE_QC_READY_FOR_SUKUNA_HANDOFF' and row.get('block_id'):
            existing_ready.add(row.get('block_id'))
    emitted = []
    for block in block_map.get('blocks', []) or []:
        block_id = block.get('block_id')
        if not block_id or block_id in existing_ready:
            continue
        refs = block.get('reference_order') or [r.get('reference_id') for r in block.get('references', []) or []]
        refs = [r for r in refs if r]
        if not refs or not all(r in qc_by_ref for r in refs):
            continue
        event = {
            'ts': now(),
            'event': 'REFERENCE_BUNDLE_QC_READY_FOR_SUKUNA_HANDOFF',
            'lane': 'image_qc',
            'block_id': block_id,
            'status': 'APPROVED_FOR_I2V',
            'reference_count_ready': len(refs),
            'reference_count_required': len(refs),
            'reference_order': refs,
            'ui_image_order': refs,
            'image_paths': [qc_by_ref[r].get('image_path') for r in refs],
            'reference_qc': {r: {'verdict': qc_by_ref[r].get('verdict'), 'image_path': qc_by_ref[r].get('image_path')} for r in refs},
            'seedance_prompt': block.get('seedance_prompt_starter'),
            'covered_cuts': block.get('covered_cuts'),
            'time_start': block.get('time_start'),
            'time_end': block.get('time_end'),
        }
        append_jsonl(qpath, event)
        emitted.append(block_id)
    return emitted


def image_info(path: Path) -> dict:
    from PIL import Image
    with Image.open(path) as im:
        return {'width': im.size[0], 'height': im.size[1], 'mode': im.mode, 'format': im.format}


def qc_one(project: Path, lane_dir: Path, row: dict) -> dict:
    ref = row.get('reference_id') or Path(row.get('image_path','unknown')).stem
    img = Path(row.get('image_path',''))
    prompt = Path(row.get('prompt_path','')) if row.get('prompt_path') else None
    prov = Path(row.get('provenance_path','')) if row.get('provenance_path') else img.with_suffix(img.suffix + '.provenance.json')
    checks = []
    reasons = []
    verdict = 'PASS'

    if not img.exists() or img.stat().st_size <= 0:
        verdict = 'FAIL'
        reasons.append('missing_or_empty_image')
        info = {}
    else:
        try:
            info = image_info(img)
            checks.append({'check': 'decode_image', 'pass': True, **info})
            aspect = info['width'] / max(info['height'], 1)
            aspect_ok = 1.70 <= aspect <= 1.82
            checks.append({'check': 'landscape_16x9ish', 'pass': aspect_ok, 'aspect': aspect})
            if not aspect_ok:
                verdict = 'RETRY'
                reasons.append('bad_aspect_ratio')
            size_ok = info['width'] >= 1280 and info['height'] >= 720
            checks.append({'check': 'minimum_resolution', 'pass': size_ok})
            if not size_ok:
                verdict = 'RETRY'
                reasons.append('low_resolution')
        except Exception as exc:
            verdict = 'FAIL'
            reasons.append(f'image_decode_error:{exc}')
            info = {}

    prov_data = load_json(prov, {}) if prov.exists() else {}
    checks.append({'check': 'provenance_present', 'pass': prov.exists(), 'path': str(prov)})
    if prov_data:
        checks.append({'check': 'codex_app_provider', 'pass': prov_data.get('provider') == 'codex-app-server-imageGeneration', 'provider': prov_data.get('provider')})
        checks.append({'check': 'non_gui_flags', 'pass': bool(prov_data.get('non_gui_browser')) and bool(prov_data.get('no_computer_use'))})
    else:
        # Existing/smoke images may lack full provenance; do not fail, but mark warning.
        checks.append({'check': 'provenance_warning', 'pass': False, 'warning': 'missing provenance for pre-run existing artifact'})

    prompt_text = ''
    if prompt and prompt.exists():
        prompt_text = prompt.read_text(encoding='utf-8', errors='ignore')[:4000]
    policy_terms = ['No text', 'no logo', 'no watermark']
    policy_ok = all(term.lower() in (prompt_text + ' ' + json.dumps(prov_data, ensure_ascii=False)).lower() for term in ['no text', 'no logo', 'no watermark'])
    checks.append({'check': 'prompt_contains_no_text_logo_watermark_policy', 'pass': policy_ok})
    if not policy_ok and verdict == 'PASS':
        verdict = 'WARN_PASS'
        reasons.append('policy_terms_not_all_found')

    qc = {
        'ts': now(),
        'reference_id': ref,
        'source_lane': row.get('lane'),
        'image_path': str(img),
        'prompt_path': str(prompt) if prompt else None,
        'provenance_path': str(prov) if prov.exists() else None,
        'verdict': verdict,
        'reasons': reasons,
        'checks': checks,
        'image_info': info,
        'qc_scope': 'file_integrity_seedance_readiness_policy_metadata_fast_qc',
        'note': 'Fast lane QC runs while image creators continue. Detailed visual continuity QC can re-check before Seedance if required.',
    }
    out = lane_dir / 'artifacts' / f'{ref}.image_qc.json'
    write_json(out, qc)
    return qc


def creators_done(project: Path) -> bool:
    for lane in ['image_creator_01', 'image_creator_02']:
        st = load_json(project / 'lanes' / lane / 'status.json', {}) or {}
        if st.get('status') == 'RUNNING':
            return False
        pid_file = project / 'lanes' / lane / 'pid'
        if pid_file.exists():
            try:
                pid = int(pid_file.read_text().strip())
                os.kill(pid, 0)
                return False
            except Exception:
                pass
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--project', required=True)
    ap.add_argument('--watch-seconds', type=int, default=0, help='0 = until creators done and queue drained')
    ap.add_argument('--poll', type=float, default=5.0)
    args = ap.parse_args()
    project = Path(args.project).expanduser().resolve()
    lane = 'image_qc'
    lane_dir = project / 'lanes' / lane
    lane_dir.mkdir(parents=True, exist_ok=True)
    (lane_dir / 'artifacts').mkdir(parents=True, exist_ok=True)
    qpath = project / 'queues' / 'image_review_queue.jsonl'
    state_path = lane_dir / 'processed_refs.json'
    processed = set(load_json(state_path, []) or [])
    status = {'lane': lane, 'status': 'RUNNING', 'updated_at': now(), 'pid': os.getpid(), 'phase': 'watch_image_review_queue'}
    write_json(lane_dir / 'status.json', status)

    deadline = time.time() + args.watch_seconds if args.watch_seconds else None
    pass_count = retry_count = fail_count = 0
    idle_rounds = 0
    qc_by_ref = {}
    for p in (lane_dir / 'artifacts').glob('*.image_qc.json'):
        qc_prev = load_json(p, {}) or {}
        if qc_prev.get('verdict') in ['PASS', 'WARN_PASS'] and qc_prev.get('reference_id'):
            qc_by_ref[qc_prev['reference_id']] = qc_prev
    log_path = lane_dir / 'logs' / 'image_qc_watch.log'
    log_path.parent.mkdir(parents=True, exist_ok=True)
    while True:
        rows = read_queue(qpath)
        new_rows = []
        for row in rows:
            ref = row.get('reference_id') or Path(row.get('image_path','unknown')).stem
            if ref in processed:
                continue
            if not row.get('image_path'):
                continue
            new_rows.append(row)
        if new_rows:
            idle_rounds = 0
            with log_path.open('a', encoding='utf-8') as log:
                for row in new_rows:
                    qc = qc_one(project, lane_dir, row)
                    ref = qc['reference_id']
                    processed.add(ref)
                    verdict = qc['verdict']
                    if verdict in ['PASS', 'WARN_PASS']:
                        pass_count += 1
                        qc_by_ref[ref] = qc
                        append_jsonl(project / 'queues' / 'reference_bundle_queue.jsonl', {'ts': now(), 'event': 'IMAGE_QC_PASS_READY_FOR_BUNDLE', **qc})
                        ready_blocks = emit_ready_blocks(project, qc_by_ref)
                        for block_id in ready_blocks:
                            log.write(json.dumps({'ts': now(), 'block_id': block_id, 'event': 'REFERENCE_BUNDLE_QC_READY_FOR_SUKUNA_HANDOFF'}, ensure_ascii=False) + '\n')
                    elif verdict == 'RETRY':
                        retry_count += 1
                        append_jsonl(project / 'queues' / 'image_retry_queue.jsonl', {'ts': now(), 'event': 'IMAGE_QC_RETRY', **qc})
                    else:
                        fail_count += 1
                        append_jsonl(project / 'queues' / 'retry_router_queue.jsonl', {'ts': now(), 'event': 'IMAGE_QC_FAIL', **qc})
                    log.write(json.dumps({'ts': now(), 'ref': ref, 'verdict': verdict}, ensure_ascii=False) + '\n')
            write_json(state_path, sorted(processed))
            status.update({'updated_at': now(), 'processed_count': len(processed), 'pass_count': pass_count, 'retry_count': retry_count, 'fail_count': fail_count})
            write_json(lane_dir / 'status.json', status)
        else:
            idle_rounds += 1

        if deadline and time.time() >= deadline:
            break
        if not deadline and creators_done(project) and idle_rounds >= 2:
            break
        time.sleep(args.poll)

    status.update({'status': 'DONE', 'updated_at': now(), 'processed_count': len(processed), 'pass_count': pass_count, 'retry_count': retry_count, 'fail_count': fail_count, 'phase': 'complete'})
    write_json(lane_dir / 'status.json', status)
    result = lane_dir / 'result.md'
    result.write_text(f"# Image QC result\n\nStatus: {status['status']}\nProcessed refs total: {len(processed)}\nPass this run: {pass_count}\nRetry this run: {retry_count}\nFail this run: {fail_count}\nReference bundle queue: {project / 'queues' / 'reference_bundle_queue.jsonl'}\nNote: Image QC does not call Seedance directly; Sukuna/Image must brief and hand off each approved reference bundle to Toji/video.\n", encoding='utf-8')
    print(json.dumps(status, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
