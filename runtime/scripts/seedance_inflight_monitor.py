#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

HOME = Path('/Users/gnudas')


def now_iso() -> str:
    return dt.datetime.now().astimezone().isoformat()


def safe_name(text: str) -> str:
    out = ''.join(c if c.isalnum() or c in '.-_' else '_' for c in text)
    return out[:180] or 'download.mp4'


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8', errors='ignore')
    except OSError:
        return ''


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def append_jsonl(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as handle:
        handle.write(json.dumps(value, ensure_ascii=False) + '\n')


def parse_time(value: str) -> float | None:
    text = value.strip()
    if not text:
        return None
    try:
        return dt.datetime.fromisoformat(text).timestamp()
    except ValueError:
        return None


def latest_submit_record(project: Path, block: str) -> Path | None:
    prompt_dir = project / 'lanes' / 'seedance' / 'prompts'
    status = read_json(project / 'lanes' / 'seedance' / 'status.json')
    status_record = status.get('submit_success_record')
    if isinstance(status_record, str) and status_record:
        path = Path(status_record).expanduser()
        if path.exists() and (not block or block in path.name):
            return path
    records = sorted(
        prompt_dir.glob('*submit_success*.json'),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    for record in records:
        if not block or block in record.name:
            return record
    return None


def submit_info(project: Path, block: str) -> tuple[str, Path | None, dict, float]:
    record = latest_submit_record(project, block)
    data = read_json(record) if record else {}
    block_id = str(data.get('block') or block or 'UNKNOWN_SEEDANCE_BLOCK')
    submitted_at = parse_time(str(data.get('updated_at') or ''))
    fallback = record.stat().st_mtime if record else time.time()
    since = (submitted_at if submitted_at is not None else fallback) - 600
    return block_id, record, data, since


def screenshot(project: Path, block: str) -> dict:
    out_dir = project / 'lanes' / 'seedance' / 'polls' / 'monitor_screens'
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime('%Y%m%d_%H%M%S')
    path = out_dir / f'{stamp}_{safe_name(block)}.png'
    proc = subprocess.run(['/usr/sbin/screencapture', '-x', str(path)], text=True, capture_output=True, timeout=20)
    ok = proc.returncode == 0 and path.exists() and path.stat().st_size > 0
    return {'ok': ok, 'path': str(path) if ok else None, 'rc': proc.returncode, 'stderr': proc.stderr.strip()[-500:]}


def ffprobe(path: Path) -> dict:
    cmd = [
        '/opt/homebrew/bin/ffprobe',
        '-v', 'error',
        '-show_entries', 'format=duration,size,bit_rate:stream=codec_name,width,height,r_frame_rate',
        '-of', 'json',
        str(path),
    ]
    try:
        proc = subprocess.run(cmd, text=True, capture_output=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {'ok': False, 'error': str(exc)}
    if proc.returncode != 0:
        return {'ok': False, 'rc': proc.returncode, 'stderr': proc.stderr.strip()[-1000:]}
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {'ok': False, 'error': 'ffprobe_json_decode_failed'}
    data['ok'] = True
    return data


def load_state(project: Path) -> dict:
    state = read_json(project / 'lanes' / 'seedance' / 'monitor_state.json')
    state.pop('last_new_download_count', None)
    state.pop('seen_sources', None)
    return state


def save_status(project: Path, status: str, detail: str, extra: dict, persistent: bool) -> None:
    lane_dir = project / 'lanes' / 'seedance'
    current = read_json(lane_dir / 'status.json')
    current.update({
        'lane': 'seedance',
        'status': status,
        'detail': detail,
        'updated_at': now_iso(),
        'monitor_state': str(lane_dir / 'monitor_state.json'),
    })
    if persistent:
        current['monitor_pid'] = os.getpid()
    else:
        current['last_manual_monitor_pid'] = os.getpid()
    current.update(extra)
    write_json(lane_dir / 'status.json', current)


# Removed 2026-07-28: candidate_downloads() / copy_new_downloads().
#
# They scanned ~/Downloads for MP4s newer than the submit timestamp, copied them
# into lanes/seedance/downloads/<block>/, and published
# SEEDANCE_OUTPUT_DOWNLOADED_BY_MONITOR to seedance_review_queue — the very event
# that opens the seedance_qc gate. Attribution was a timestamp guess, so any
# unrelated download could be adopted as a block's output, and the files landed
# under lanes/ rather than assets/i2v_clips.
#
# poll() already refused to call them and records
# download_scan='forbidden_as_completion_signal', matching AGENTS.md §4.2:
# Runway never auto-downloads, so a file in Downloads is a result the operator
# produced after confirming a completed job card, never the signal itself.
# Dead code that contradicts the policy is a trap for the next edit, so it is
# gone; git history keeps it.

def poll(project: Path, block_arg: str, persistent: bool) -> dict:
    block, record, submit_data, since_ts = submit_info(project, block_arg)
    state = load_state(project)
    shot = screenshot(project, block)
    event = {
        'ts': now_iso(),
        'event': 'SEEDANCE_MONITOR_POLL',
        'signal_chain': 'runway_ui_only',
        'completion_signal': 'Generate button active/blue plus completed Runway job card; Downloads are not a signal',
        'block_id': block,
        'submit_record': str(record) if record else None,
        'submit_result': submit_data.get('result'),
        'screenshot': shot,
        'download_scan': 'forbidden_as_completion_signal',
        'pid': os.getpid(),
    }
    append_jsonl(project / 'lanes' / 'seedance' / 'ui_evidence.jsonl', event)
    state_update = {'last_poll_at': event['ts'], 'last_block_id': block, 'last_screenshot': shot.get('path'), 'completion_signal': event['completion_signal']}
    if persistent:
        state_update['pid'] = os.getpid()
    else:
        state_update['last_manual_monitor_pid'] = os.getpid()
    state.update(state_update)
    write_json(project / 'lanes' / 'seedance' / 'monitor_state.json', state)
    save_status(project, 'RUNNING', 'Seedance UI-signal monitor heartbeat active; completion must be judged from Runway UI, then downloaded by operator.', {'last_monitor_poll_at': event['ts'], 'last_monitor_screenshot': shot.get('path'), 'completion_signal': event['completion_signal']}, persistent)
    return event


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', required=True)
    parser.add_argument('--block', default='')
    parser.add_argument('--interval-seconds', type=int, default=900)
    parser.add_argument('--once', action='store_true')
    args = parser.parse_args()
    if not args.once and args.interval_seconds < 900:
        args.interval_seconds = 900
    project = Path(args.project).expanduser().resolve()
    lane_dir = project / 'lanes' / 'seedance'
    lane_dir.mkdir(parents=True, exist_ok=True)
    if not args.once:
        (lane_dir / 'monitor.pid').write_text(str(os.getpid()) + '\n', encoding='utf-8')
    while True:
        event = poll(project, args.block, not args.once)
        print(json.dumps(event, ensure_ascii=False), flush=True)
        if args.once:
            return 0
        time.sleep(max(30, args.interval_seconds))


if __name__ == '__main__':
    raise SystemExit(main())
