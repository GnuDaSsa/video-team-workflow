#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys

IMAGE_CLI = Path(os.environ.get("VIDEO_IMAGE_CLI", str(Path.home() / ".local" / "bin" / "video-image-cli")))


def now() -> str:
    return dt.datetime.now().astimezone().isoformat()


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def append_jsonl(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False) + '\n')


def ref_id_from_prompt(path: Path) -> str:
    name = path.name
    for suffix in ['.prompt.txt', '_chatgpt_image2_prompt.txt', '.txt']:
        if name.endswith(suffix):
            return name[:-len(suffix)]
    return path.stem


def image_size(path: Path):
    try:
        from PIL import Image
        with Image.open(path) as im:
            return {'width': im.size[0], 'height': im.size[1], 'mode': im.mode, 'format': im.format}
    except Exception as exc:
        return {'error': str(exc)}


def update_manifest(project: Path, lane: str, status: dict, generated: list[dict]) -> None:
    manifest_path = project / 'manifest.json'
    try:
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    except Exception:
        manifest = {}
    manifest.setdefault('lanes', {}).setdefault(lane, {}).update(status)
    manifest.setdefault('image_creator_outputs', {})[lane] = generated
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--project', required=True)
    ap.add_argument('--lane', required=True, choices=['image_creator_01', 'image_creator_02'])
    ap.add_argument('--limit', type=int, default=0, help='0 = all')
    args = ap.parse_args()

    project = Path(args.project).expanduser().resolve()
    lane = args.lane
    lane_dir = project / 'lanes' / lane
    prompt_dir = lane_dir / 'prompts'
    artifacts = lane_dir / 'artifacts'
    logs = lane_dir / 'logs'
    artifacts.mkdir(parents=True, exist_ok=True)
    logs.mkdir(parents=True, exist_ok=True)

    status = {'lane': lane, 'status': 'RUNNING', 'updated_at': now(), 'phase': 'file_backed_codex_app_image_generation', 'pid': os.getpid()}
    write_json(lane_dir / 'status.json', status)
    update_manifest(project, lane, status, [])

    prompts = sorted(list(prompt_dir.glob('*.prompt.txt')) + list(prompt_dir.glob('*_chatgpt_image2_prompt.txt')))
    seen = set()
    unique = []
    for p in prompts:
        rid = ref_id_from_prompt(p)
        if rid not in seen:
            unique.append((rid, p))
            seen.add(rid)
    if args.limit:
        unique = unique[:args.limit]

    # Map planner queue metadata onto generated review items so Image QC/Seedance gates know
    # which block/reference each file belongs to. Character preflight refs may not have block_id.
    ref_meta = {}
    qpath = project / 'queues' / 'image_reference_queue.jsonl'
    if qpath.exists():
        for line in qpath.read_text(encoding='utf-8', errors='ignore').splitlines():
            try:
                row = json.loads(line)
            except Exception:
                continue
            rid0 = row.get('reference_id')
            if rid0:
                ref_meta[rid0] = {k: row.get(k) for k in ['block_id', 'downstream_seedance_block_id', 'reference_order', 'reference_count_required_for_block', 'role', 'expected_file'] if k in row}

    generated = []
    failures = []
    commands_log = logs / 'direct_file_backed_commands.log'
    gen_log = logs / 'direct_file_backed_generation.log'
    with commands_log.open('a', encoding='utf-8') as clog, gen_log.open('a', encoding='utf-8') as glog:
        print(f'{now()} START lane={lane} prompts={len(unique)}', file=glog, flush=True)
        for rid, prompt in unique:
            out = artifacts / f'{rid}.png'
            if out.exists() and out.stat().st_size > 0:
                meta = {'reference_id': rid, 'image_path': str(out), 'prompt_path': str(prompt), 'status': 'EXISTS', 'size': image_size(out)}
                meta.update(ref_meta.get(rid, {}))
                generated.append(meta)
                append_jsonl(project / 'queues' / 'image_review_queue.jsonl', {'ts': now(), 'lane': lane, 'event': 'IMAGE_REFERENCE_READY_FOR_QC', **meta})
                continue
            cmd = [str(IMAGE_CLI), '--prompt-file', str(prompt), '--out', str(out), '--aspect-ratio', 'landscape', '--timeout', '180']
            print(now(), ' '.join(cmd), file=clog, flush=True)
            print(f'{now()} WAIT_GLOBAL_CODEX_IMAGE_LOCK {rid}', file=glog, flush=True)
            lock_path = project / 'locks' / 'GLOBAL_CODEX_APP_IMAGE_GENERATION.lock'
            lock_path.parent.mkdir(parents=True, exist_ok=True)
            with lock_path.open('w', encoding='utf-8') as lock_file:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
                lock_file.seek(0)
                lock_file.truncate()
                lock_file.write(json.dumps({'lane': lane, 'reference_id': rid, 'pid': os.getpid(), 'locked_at': now()}, ensure_ascii=False) + '\n')
                lock_file.flush()
                print(f'{now()} GENERATE {rid}', file=glog, flush=True)
                proc = subprocess.run(cmd, cwd=str(project), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=240)
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
            print(proc.stdout, file=glog, flush=True)
            if proc.returncode == 0 and out.exists() and out.stat().st_size > 0:
                prov = out.with_suffix(out.suffix + '.provenance.json')
                meta = {'reference_id': rid, 'image_path': str(out), 'prompt_path': str(prompt), 'provenance_path': str(prov) if prov.exists() else None, 'status': 'READY_FOR_QC', 'bytes': out.stat().st_size, 'size': image_size(out)}
                meta.update(ref_meta.get(rid, {}))
                generated.append(meta)
                append_jsonl(project / 'queues' / 'image_review_queue.jsonl', {'ts': now(), 'lane': lane, 'event': 'IMAGE_REFERENCE_READY_FOR_QC', **meta})
            else:
                fail = {'reference_id': rid, 'prompt_path': str(prompt), 'status': 'FAILED', 'returncode': proc.returncode, 'tail': proc.stdout[-2000:]}
                failures.append(fail)
                append_jsonl(project / 'queues' / 'image_retry_queue.jsonl', {'ts': now(), 'lane': lane, 'event': 'IMAGE_REFERENCE_GENERATION_FAILED', **fail})

            status.update({'updated_at': now(), 'generated_count': len(generated), 'failure_count': len(failures), 'current_reference': rid})
            write_json(lane_dir / 'status.json', status)
            update_manifest(project, lane, status, generated)

    final_status = 'DONE' if generated and not failures else ('PARTIAL_BLOCKED' if generated else 'BLOCKED')
    status.update({'status': final_status, 'updated_at': now(), 'generated_count': len(generated), 'failure_count': len(failures), 'phase': 'complete'})
    write_json(lane_dir / 'status.json', status)
    update_manifest(project, lane, status, generated)

    result = [f'# {lane} result', '', f'Status: {final_status}', f'Generated: {len(generated)}', f'Failures: {len(failures)}', '', '## Generated images']
    for g in generated:
        result.append(f"- {g['reference_id']}: {g['image_path']} ({g.get('size')})")
    if failures:
        result += ['', '## Failures']
        for f in failures:
            result.append(f"- {f['reference_id']}: rc={f.get('returncode')} {f.get('tail','')[-300:]}")
    (lane_dir / 'result.md').write_text('\n'.join(result) + '\n', encoding='utf-8')
    print(json.dumps(status, ensure_ascii=False, indent=2))
    return 0 if final_status == 'DONE' else 1


if __name__ == '__main__':
    raise SystemExit(main())
