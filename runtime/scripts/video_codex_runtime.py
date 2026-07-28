#!/usr/bin/env python3
"""Codex-delegated video-team runtime supervisor."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import shlex
import signal
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lane_gates  # shared gate/status-enum/validation logic (P1/P2/P3)

HOME = Path('/Users/gnudas')
RUNTIME = Path('/Users/gnudas/Documents/Codex/video-team-runtime/runtime')
TEMPLATES = RUNTIME / 'templates'
PROJECT_ROOT = HOME / 'Documents' / 'Codex' / 'video-team-runtime'
CODEX = Path('/opt/homebrew/bin/codex')

LANES = [
    'director',
    'music',
    'planner',
    'image_creator_01',
    'image_creator_02',
    'image_qc',
    'seedance',
    'seedance_qc',
    'editor',
    'package',
]
TEMPLATE_BY_LANE = {
    'director': 'director.md',
    'music': 'music.md',
    'planner': 'planner.md',
    'image_creator_01': 'image_creator.md',
    'image_creator_02': 'image_creator.md',
    'image_qc': 'image_qc.md',
    'seedance': 'seedance.md',
    'seedance_qc': 'seedance_qc.md',
    'editor': 'editor.md',
    'package': 'package.md',
}
ALIASES: dict[str, list[str]] = {}
QUEUES = [
    'intake_queue',
    'music_queue',
    'planning_queue',
    'image_reference_queue',
    'image_retry_queue',
    'image_review_queue',
    'reference_bundle_queue',
    'seedance_block_queue',
    'seedance_review_queue',
    'seedance_retry_queue',
    'edit_queue',
    'typography_queue',
    'package_qc_queue',
    'submission_queue',
    'retry_router_queue',
]


def slugify(s: str) -> str:
    out = ''.join(c.lower() if c.isalnum() else '-' for c in s.strip())
    out = '-'.join(x for x in out.split('-') if x)
    return out[:60] or 'video-project'


def now() -> str:
    return dt.datetime.now().strftime('%Y%m%d_%H%M%S')


def read(p: Path) -> str:
    return p.read_text(encoding='utf-8') if p.exists() else ''


def write_json(p: Path, obj) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def append_jsonl(p: Path, obj) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('a', encoding='utf-8') as f:
        f.write(json.dumps(obj, ensure_ascii=False) + '\n')


def expand_lanes(items: list[str]) -> list[str]:
    expanded: list[str] = []
    for item in items:
        vals = ALIASES.get(item, [item])
        for lane in vals:
            if lane not in LANES:
                raise SystemExit(f'unknown lane {lane}; valid={LANES}; aliases={sorted(ALIASES)}')
            if lane not in expanded:
                expanded.append(lane)
    return expanded


def init_project(args) -> None:
    slug = slugify(args.slug or args.brief[:40] or 'video-project')
    project = PROJECT_ROOT / f'{now()}_{slug}'
    project.mkdir(parents=True, exist_ok=False)
    for lane in LANES:
        (project / 'lanes' / lane).mkdir(parents=True, exist_ok=True)
    for q in QUEUES:
        qp = project / 'queues' / f'{q}.jsonl'
        qp.parent.mkdir(parents=True, exist_ok=True)
        qp.touch()
    for sub in [
        'assets/audio',
        'assets/images_candidates',
        'assets/images_approved',
        'assets/i2v_clips',
        'assets/contact_sheets',
        'assets/keyframes',
        'assets/edit',
        'assets/package',
        'locks',
        'docs',
    ]:
        (project / sub).mkdir(parents=True, exist_ok=True)
    (project / 'brief.md').write_text(args.brief.rstrip() + '\n', encoding='utf-8')

    state = {
        'project': str(project),
        'created_at': dt.datetime.now().isoformat(),
        'slug': slug,
        'runtime': 'codex-app-delegated-video-team-sequential',
        'workflow_version': '2026-07-06-sequential-codex-only',
        'project_phase': 'intake',
        'lanes': {lane: {'status': 'PENDING'} for lane in LANES},
        'safety': {
            'public_upload_requires_user_approval': True,
            'contest_submit_requires_user_approval': True,
            'email_send_requires_user_approval': True,
            'personal_info_form_requires_user_approval': True,
            'payment_password_2fa_forbidden': True,
            'permanent_deletion_requires_user_approval': True,
        },
    }
    manifest = {
        'project_id': slug,
        'project_root': str(project),
        'project_phase': 'intake',
        'computer_use_owner': None,
        'sequential_agent_mode': True,
        'global_rules': {
            'music_first': True,
            'block_map_required': True,
            'seedance_primary': True,
            'no_raw_stills_in_final': True,
            'project_wide_lock': False,
            'block_stage_lock': True,
            'submission_requires_user_approval': True,
        },
        'lanes': {lane: {'status': 'PENDING'} for lane in LANES},
        'queues': {q: str(project / 'queues' / f'{q}.jsonl') for q in QUEUES},
        'locks': [],
        'music': {'status': 'NOT_LOCKED', 'music_file': None},
        'cut_list': [],
        'blocks': [],
        'edit': {'status': 'NOT_STARTED'},
        'package': {'status': 'NOT_STARTED'},
        'safety': state['safety'],
    }
    write_json(project / 'state.json', state)
    write_json(project / 'manifest.json', manifest)
    append_jsonl(project / 'queues' / 'intake_queue.jsonl', {
        'ts': dt.datetime.now().isoformat(),
        'event': 'project_created',
        'project': str(project),
        'brief': str(project / 'brief.md'),
    })
    print(str(project))


def make_prompt(project: Path, lane: str) -> str:
    shared = read(TEMPLATES / 'shared_lane_contract.md')
    template_name = TEMPLATE_BY_LANE[lane]
    lane_prompt = read(TEMPLATES / template_name)
    if not lane_prompt:
        raise SystemExit(f'missing lane template: {lane} -> {template_name}')
    return f"""{shared}

---

{lane_prompt}

---

Project root: {project}
Lane name: {lane}
Lane directory: {project / 'lanes' / lane}

Before doing work, write RUNNING to `{project / 'lanes' / lane / 'status.json'}`.
At finish, write your final result to `{project / 'lanes' / lane / 'result.md'}` and update status.json.
When updating shared files, keep JSON valid and do not erase other lanes' data.
"""


def pid_running(pid: int | None) -> bool:
    if not pid:
        return False
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def update_manifest_lane(project: Path, lane: str, data: dict) -> None:
    manifest_path = project / 'manifest.json'
    manifest = json.loads(read(manifest_path) or '{}')
    manifest.setdefault('lanes', {}).setdefault(lane, {}).update(data)
    write_json(manifest_path, manifest)


def start_seedance_monitor(project: Path, interval_seconds: int = 900) -> dict:
    interval_seconds = max(900, interval_seconds)
    lane_dir = project / 'lanes' / 'seedance'
    pid_path = lane_dir / 'monitor.pid'
    pid = None
    if pid_path.exists():
        try:
            pid = int(read(pid_path).strip())
        except ValueError:
            pid = None
    if pid_running(pid):
        return {'monitor_started': False, 'monitor_pid': pid, 'monitor_running': True}
    script = RUNTIME / 'scripts' / 'seedance_inflight_monitor.py'
    log_path = lane_dir / 'monitor.log'
    out = open(log_path, 'ab', buffering=0)
    proc = subprocess.Popen(
        [sys.executable, str(script), '--project', str(project), '--interval-seconds', str(interval_seconds)],
        cwd=str(project),
        stdout=out,
        stderr=out,
        start_new_session=True,
    )
    pid_path.write_text(str(proc.pid) + '\n', encoding='utf-8')
    result = {'monitor_started': True, 'monitor_pid': proc.pid, 'monitor_running': True, 'monitor_log': str(log_path), 'monitor_interval_seconds': interval_seconds}
    append_jsonl(project / 'queues' / 'retry_router_queue.jsonl', {
        'ts': dt.datetime.now().isoformat(),
        'event': 'seedance_inflight_monitor_started',
        **result,
    })
    return result


def dispatch(args) -> None:
    project = Path(args.project).expanduser().resolve()
    if not (project / 'state.json').exists():
        raise SystemExit(f'not a runtime project: {project}')
    if not CODEX.exists():
        raise SystemExit(f'codex not found: {CODEX}')
    lanes = expand_lanes(args.lanes)
    if len(lanes) != 1:
        raise SystemExit(
            'SEQUENTIAL_DISPATCH_ONLY: dispatch accepts exactly one lane. '
            f'got {lanes}. Run `video-codex-runtime next --project {project}` '
            'and dispatch only the first returned lane.'
        )
    launched = []
    skipped = []
    for lane in lanes:
        # Hard dispatch gates: single source of truth lives in lane_gates.gate_check
        # so `dispatch`, `gate`, `next`, and lanes doing manual work all apply the
        # SAME judgment. Rail: Director -> Music -> Planner -> Image -> Image QC ->
        # Seedance -> Seedance QC -> Editor -> Package.
        ok, skip_reason = lane_gates.gate_check(project, lane)
        if not ok and (lane_gates.gate_level(lane) == 'soft' or getattr(args, 'force', False)):
            # Soft gate (new ordering check) or explicit --force: warn, do not block.
            append_jsonl(project / 'queues' / 'retry_router_queue.jsonl', {
                'ts': dt.datetime.now().isoformat(), 'event': 'lane_dispatch_soft_gate_warning',
                'lane': lane, 'reason': skip_reason, 'forced': bool(getattr(args, 'force', False)),
            })
            ok, skip_reason = True, None
        if not ok:
            append_jsonl(project / 'queues' / 'retry_router_queue.jsonl', {
                'ts': dt.datetime.now().isoformat(), 'event': 'lane_dispatch_skipped_by_gate', 'lane': lane, 'reason': skip_reason,
            })
            skipped.append({'lane': lane, 'reason': skip_reason})
            continue

        lane_dir = project / 'lanes' / lane
        lane_dir.mkdir(parents=True, exist_ok=True)
        prompt_path = lane_dir / 'prompt.md'
        result_path = lane_dir / 'result.md'
        log_path = lane_dir / 'run.log'
        prompt_path.write_text(make_prompt(project, lane), encoding='utf-8')
        status = {'lane': lane, 'status': 'LAUNCHING', 'launched_at': dt.datetime.now().isoformat()}
        write_json(lane_dir / 'status.json', status)
        update_manifest_lane(project, lane, status)

        if lane.startswith('image_creator_'):
            runner = RUNTIME / 'scripts' / 'image_creator_lane_runner.py'
            inner = (
                f"HOME=/Users/gnudas {shlex.quote(sys.executable)} {shlex.quote(str(runner))} "
                f"--project {shlex.quote(str(project))} --lane {shlex.quote(lane)}"
            )
        elif lane == 'image_qc':
            runner = RUNTIME / 'scripts' / 'image_qc_lane_runner.py'
            inner = (
                f"HOME=/Users/gnudas {shlex.quote(sys.executable)} {shlex.quote(str(runner))} "
                f"--project {shlex.quote(str(project))}"
            )
        else:
            inner = (
                f"HOME=/Users/gnudas {shlex.quote(str(CODEX))} exec "
                f"--skip-git-repo-check --full-auto "
                f"--output-last-message {shlex.quote(str(result_path))} "
                f"-C {shlex.quote(str(project))} -m gpt-5.5 < {shlex.quote(str(prompt_path))}"
            )
        # /usr/bin/script gives Codex/non-Codex lane commands a pseudo-tty and records transcript.
        cmd = ['/usr/bin/script', '-q', str(log_path), '/bin/zsh', '-lc', inner]
        out = open(lane_dir / 'supervisor.out', 'ab', buffering=0)
        err = open(lane_dir / 'supervisor.err', 'ab', buffering=0)
        proc = subprocess.Popen(cmd, cwd=str(project), stdout=out, stderr=err, start_new_session=True)
        (lane_dir / 'pid').write_text(str(proc.pid) + '\n', encoding='utf-8')
        status.update({'status': 'RUNNING', 'pid': proc.pid, 'log': str(log_path), 'prompt': str(prompt_path), 'result': str(result_path)})
        write_json(lane_dir / 'status.json', status)
        update_manifest_lane(project, lane, status)
        monitor = None
        if lane == 'seedance':
            monitor = start_seedance_monitor(project)
            status.update(monitor)
            write_json(lane_dir / 'status.json', status)
            update_manifest_lane(project, lane, status)
        append_jsonl(project / 'queues' / 'retry_router_queue.jsonl', {
            'ts': dt.datetime.now().isoformat(),
            'event': 'lane_dispatched',
            'lane': lane,
            'pid': proc.pid,
            'monitor': monitor,
        })
        launched.append({'lane': lane, 'pid': proc.pid, 'log': str(log_path), 'result': str(result_path)})
    print(json.dumps({'project': str(project), 'launched': launched, 'skipped': skipped}, ensure_ascii=False, indent=2))


def status(args) -> None:
    project = Path(args.project).expanduser().resolve()
    rows = []
    for lane in LANES:
        lane_dir = project / 'lanes' / lane
        status_path = lane_dir / 'status.json'
        s = json.loads(read(status_path) or '{}')
        pid = None
        if (lane_dir / 'pid').exists():
            try:
                pid = int(read(lane_dir / 'pid').strip())
            except Exception:
                pid = None
        monitor_pid = None
        if (lane_dir / 'monitor.pid').exists():
            try:
                monitor_pid = int(read(lane_dir / 'monitor.pid').strip())
            except Exception:
                monitor_pid = None
        watch_generate_pid = None
        if (lane_dir / 'watch_generate.pid').exists():
            try:
                watch_generate_pid = int(read(lane_dir / 'watch_generate.pid').strip())
            except Exception:
                watch_generate_pid = None
        running = pid_running(pid)
        monitor_running = pid_running(monitor_pid)
        watch_generate_running = pid_running(watch_generate_pid)
        result_exists = (lane_dir / 'result.md').exists() and (lane_dir / 'result.md').stat().st_size > 0
        rows.append({
            'lane': lane,
            'status': s.get('status', 'PENDING'),
            'pid': pid,
            'running': running,
            'monitor_pid': monitor_pid,
            'monitor_running': monitor_running,
            'watch_generate_pid': watch_generate_pid,
            'watch_generate_running': watch_generate_running,
            'result_exists': result_exists,
            'result': str(lane_dir / 'result.md'),
            'log': str(lane_dir / 'run.log'),
        })
    manifest = json.loads(read(project / 'manifest.json') or '{}')
    print(json.dumps({
        'project': str(project),
        'phase': manifest.get('project_phase'),
        'music': manifest.get('music'),
        'sequential_agent_mode': manifest.get('sequential_agent_mode', True),
        'block_count': len(manifest.get('blocks') or []),
        'lanes': rows,
    }, ensure_ascii=False, indent=2))


def kill(args) -> None:
    project = Path(args.project).expanduser().resolve()
    killed = []
    for lane in expand_lanes(args.lanes):
        lane_dir = project / 'lanes' / lane
        pid_path = lane_dir / 'pid'
        if not pid_path.exists():
            continue
        pid = int(read(pid_path).strip())
        try:
            os.killpg(pid, signal.SIGTERM)
            killed.append({'lane': lane, 'pid': pid})
            status = {'lane': lane, 'status': 'KILLED', 'killed_at': dt.datetime.now().isoformat(), 'pid': pid}
            write_json(lane_dir / 'status.json', status)
            update_manifest_lane(project, lane, status)
        except Exception as e:
            killed.append({'lane': lane, 'pid': pid, 'error': str(e)})
    print(json.dumps({'killed': killed}, ensure_ascii=False, indent=2))


def workflow(args) -> None:
    print(json.dumps({
        'workflow': 'Sequential Codex-only video team',
        'mode': 'one lane at a time; run next, then dispatch exactly one returned lane; multi-lane dispatch is rejected',
        'serial_order': LANES,
        'aliases': ALIASES,
        'alias_policy': 'no grouped lane aliases in sequential mode',
        'prompt_author': {
            'model': 'gpt-5.6-sol',
            'reasoning_effort': 'high',
            'route': 'runtime/scripts/sol_prompt_bridge.py',
            'claude_route': 'retired',
        },
        'internal_parallel_exceptions': [
            'image shards inside one image_creator stage for plans with 10+ cuts',
            'provider-split Grok I2V while Seedance work remains owned by the seedance stage',
        ],
        'queues': QUEUES,
        'safety_gates': [
            'public upload/publish', 'contest/government final submission', 'email send',
            'personal-info form submit', 'payment', 'password/2FA', 'permanent deletion',
        ],
    }, ensure_ascii=False, indent=2))


def report(args) -> None:
    """Print a compact human-readable runtime status board."""
    project = Path(args.project).expanduser().resolve()
    manifest = json.loads(read(project / 'manifest.json') or '{}')
    lines = []
    lines.append(f"[Codex Runtime] {project.name}")
    lines.append(f"project: {project}")
    lines.append(f"phase: {manifest.get('project_phase')}")
    lines.append(f"sequential_agent_mode: {manifest.get('sequential_agent_mode', True)}")
    lines.append("")
    lines.append("lanes:")
    for lane in LANES:
        lane_dir = project / 'lanes' / lane
        st = json.loads(read(lane_dir / 'status.json') or '{}')
        pid = None
        if (lane_dir / 'pid').exists():
            try:
                pid = int(read(lane_dir / 'pid').strip())
            except Exception:
                pid = None
        running = pid_running(pid)
        result_path = lane_dir / 'result.md'
        result = result_path.exists() and result_path.stat().st_size > 0
        status_txt = st.get('status', 'PENDING')
        icon = '●' if running else ('✓' if result else ('◌' if status_txt in {'PENDING', ''} else '○'))
        lines.append(f"- {icon} {lane:17s} status={status_txt} running={str(running).lower()} pid={pid or '-'} result={'yes' if result else 'no'}")
    lines.append("")
    lines.append("key paths:")
    lines.append(f"- manifest: {project / 'manifest.json'}")
    lines.append(f"- queues:   {project / 'queues'}")
    lines.append(f"- lanes:    {project / 'lanes'}")
    print('\n'.join(lines))


def prompts_cmd(args) -> None:
    """Deterministic Sol authoring: the runtime calls the bridge, not the lane.

    Scans ready work lacking prompt packs and routes each one to GPT-5.6 Sol:
    - seedance: blocks with BLOCK_READY_FOR_I2V (or legacy ready events, or a
      block_spec file) but no <BLOCK>_sol_prompt_pack.json
    - image: blocks in image_reference_queue whose reference prompt .txt files
      are missing in the target creator lane.
    Lanes use this command instead of invoking a chat or model CLI directly.
    """
    project = Path(args.project).expanduser().resolve()
    bridge = RUNTIME / 'scripts' / 'sol_prompt_bridge.py'
    results = []

    def summon(task: str, block: str, lane: str | None = None) -> None:
        cmd = [sys.executable, str(bridge), '--project', str(project), '--task', task, '--block', block]
        if lane:
            cmd += ['--lane', lane]
        proc = subprocess.run(cmd, text=True, capture_output=True)
        results.append({'task': task, 'block': block, 'rc': proc.returncode,
                        'out': proc.stdout.strip()[-400:], 'err': proc.stderr.strip()[-400:]})

    # --- seedance blocks ---
    ready_blocks: set[str] = set()
    qtxt = read(project / 'queues' / 'seedance_block_queue.jsonl')
    for line in qtxt.splitlines():
        try:
            e = json.loads(line)
        except Exception:
            continue
        if e.get('event') in ('BLOCK_READY_FOR_I2V', 'SEEDANCE_BLOCK_READY', 'IMAGE_REFERENCE_BUNDLE_READY') and e.get('block_id'):
            ready_blocks.add(e['block_id'])
    for spec in (project / 'lanes' / 'seedance' / 'prompts').glob('*_block_spec.json'):
        ready_blocks.add(spec.name.replace('_block_spec.json', ''))
    if args.block:
        ready_blocks &= {args.block}
    for block in sorted(ready_blocks):
        pack = project / 'lanes' / 'seedance' / 'prompts' / f'{block}_sol_prompt_pack.json'
        if pack.exists() and not args.force:
            results.append({'task': 'seedance', 'block': block, 'rc': 0, 'out': 'pack exists (use --force to regenerate)'})
            continue
        summon('seedance', block)

    # --- image blocks ---
    img_blocks: dict[str, list[str]] = {}
    for line in read(project / 'queues' / 'image_reference_queue.jsonl').splitlines():
        try:
            e = json.loads(line)
        except Exception:
            continue
        rid = e.get('reference_id') or e.get('work_item_id')
        bid = e.get('block_id') or 'NOBLOCK'
        if rid and not rid.upper().startswith('CHAR'):
            img_blocks.setdefault(bid, []).append(rid)
    lane = args.lane or 'image_creator_01'
    pdir = project / 'lanes' / lane / 'prompts'
    for bid, rids in sorted(img_blocks.items()):
        if args.block and bid != args.block:
            continue
        missing = [r for r in rids if not (pdir / f'{r}.prompt.txt').exists()]
        if missing:
            summon('image', bid, lane)
    print(json.dumps({'project': str(project), 'summons': results}, ensure_ascii=False, indent=2))
    if any(result['rc'] != 0 for result in results):
        raise SystemExit(1)


def image_shards_cmd(args) -> None:
    """Parallel image production for big cut plans (>=10 cuts).

    Splits PENDING refs (prompt.txt exists, PNG missing) into shards of
    --shard-size and spawns one detached runner per shard with slot-striped
    generation locks. This is the sanctioned §0 exception: sharding INSIDE the
    image stage, not multi-lane dispatch. Fan-in via `shards-status`.
    """
    project = Path(args.project).expanduser().resolve()
    lane = args.lane
    lane_dir = project / 'lanes' / lane
    prompt_dir = lane_dir / 'prompts'
    artifacts = lane_dir / 'artifacts'
    pending = []
    for pf in sorted(prompt_dir.glob('*.prompt.txt')):
        rid = pf.name[:-len('.prompt.txt')]
        out = artifacts / f'{rid}.png'
        if not (out.exists() and out.stat().st_size > 0):
            pending.append(rid)
    if not pending:
        print(json.dumps({'project': str(project), 'note': 'no pending refs (all generated or no prompts)'}))
        return
    # --shard-size defaults to auto: spread the pending refs across --max-parallel
    # workers. With a fixed size of 10, an 8-image batch produced a single shard and
    # no parallelism at all, so the documented "8+ images -> 4 workers" never held.
    if args.shard_size:
        size = max(1, args.shard_size)
    else:
        size = max(1, -(-len(pending) // max(1, args.max_parallel)))
    shards = [pending[i:i + size] for i in range(0, len(pending), size)]
    parallel = min(len(shards), args.max_parallel)
    shards_dir = lane_dir / 'shards'
    shards_dir.mkdir(parents=True, exist_ok=True)
    runner = Path(__file__).resolve().parent / 'image_creator_lane_runner.py'
    launched = []
    for i, refs in enumerate(shards):
        sid = f'shard_{i:02d}'
        mpath = shards_dir / f'{sid}.json'
        write_json(mpath, {'shard_id': sid, 'reference_ids': refs})
        log = open(shards_dir / f'{sid}.log', 'ab', buffering=0)
        proc = subprocess.Popen(
            [sys.executable, str(runner), '--project', str(project), '--lane', lane,
             '--shard-manifest', str(mpath), '--parallel-slots', str(parallel)],
            stdout=log, stderr=log, stdin=subprocess.DEVNULL, start_new_session=True)
        (shards_dir / f'{sid}.pid').write_text(str(proc.pid) + '\n', encoding='utf-8')
        launched.append({'shard': sid, 'refs': len(refs), 'pid': proc.pid})
    write_json(shards_dir / 'orchestrator.json', {
        'ts': dt.datetime.now().isoformat(), 'lane': lane, 'pending_total': len(pending),
        'shard_size': size, 'parallel_slots': parallel, 'shards': launched})
    status = {'lane': lane, 'status': 'RUNNING',
              'detail': f'sharded image production: {len(shards)} shards x <= {size} refs, parallel={parallel}',
              'updated_at': dt.datetime.now().isoformat(), 'sharded': True}
    write_json(lane_dir / 'status.json', status)
    update_manifest_lane(project, lane, status)
    print(json.dumps({'project': str(project), 'pending': len(pending), 'shards': launched,
                      'parallel_slots': parallel, 'fan_in': 'video-codex-runtime shards-status --project ...'},
                     ensure_ascii=False, indent=2))


def shards_status_cmd(args) -> None:
    """Fan-in: merge shard statuses; when all finished, finalize lane status/result."""
    project = Path(args.project).expanduser().resolve()
    lane = args.lane
    lane_dir = project / 'lanes' / lane
    shards_dir = lane_dir / 'shards'
    rows, all_done, gen_total, fail_total = [], True, 0, 0
    for sp in sorted(shards_dir.glob('shard_*.status.json')):
        s = json.loads(read(sp) or '{}')
        pid = None
        pidf = shards_dir / (sp.name.replace('.status.json', '.pid'))
        if pidf.exists():
            try:
                pid = int(read(pidf).strip())
            except Exception:
                pid = None
        running = pid_running(pid)
        done = s.get('phase') == 'complete'
        all_done &= (done and not running)
        gen_total += int(s.get('generated_count') or 0)
        fail_total += int(s.get('failure_count') or 0)
        rows.append({'shard': s.get('shard_id'), 'status': s.get('status'), 'running': running,
                     'generated': s.get('generated_count', 0), 'failed': s.get('failure_count', 0)})
    out = {'project': str(project), 'lane': lane, 'shards': rows,
           'all_done': all_done, 'generated_total': gen_total, 'failure_total': fail_total}
    if all_done and rows:
        final = 'DONE' if gen_total and not fail_total else ('PARTIAL_BLOCKED' if gen_total else 'BLOCKED')
        status = {'lane': lane, 'status': final,
                  'detail': f'sharded fan-in: {len(rows)} shards, generated={gen_total}, failed={fail_total}',
                  'updated_at': dt.datetime.now().isoformat(),
                  'generated_count': gen_total, 'failure_count': fail_total, 'sharded': True}
        write_json(lane_dir / 'status.json', status)
        update_manifest_lane(project, lane, status)
        out['finalized'] = final
    print(json.dumps(out, ensure_ascii=False, indent=2))


def gate_cmd(args) -> None:
    project = Path(args.project).expanduser().resolve()
    out = []
    for lane in expand_lanes(args.lanes):
        ok, reason = lane_gates.gate_check(project, lane)
        out.append({'lane': lane, 'gate_ok': ok, 'reason': reason})
    print(json.dumps({'project': str(project), 'gates': out}, ensure_ascii=False, indent=2))


def next_cmd(args) -> None:
    project = Path(args.project).expanduser().resolve()
    print(json.dumps(lane_gates.next_actions(project), ensure_ascii=False, indent=2))


def validate_cmd(args) -> None:
    project = Path(args.project).expanduser().resolve()
    result = lane_gates.validate_project(project)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result['ok']:
        raise SystemExit(1)


def seedance_monitor_cmd(args) -> None:
    project = Path(args.project).expanduser().resolve()
    script = RUNTIME / 'scripts' / 'seedance_inflight_monitor.py'
    cmd = [sys.executable, str(script), '--project', str(project), '--interval-seconds', str(args.interval_seconds)]
    if args.block:
        cmd.extend(['--block', args.block])
    if args.once:
        cmd.append('--once')
    raise SystemExit(subprocess.run(cmd).returncode)


def seedance_monitor_start_cmd(args) -> None:
    project = Path(args.project).expanduser().resolve()
    result = start_seedance_monitor(project, args.interval_seconds)
    print(json.dumps({'project': str(project), **result}, ensure_ascii=False, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('init')
    p.add_argument('--slug', default='')
    p.add_argument('--brief', required=True)
    p.set_defaults(func=init_project)

    p = sub.add_parser('dispatch')
    p.add_argument('--project', required=True)
    p.add_argument('--lanes', nargs='+', required=True, help='exactly one lane for dispatch; multi-lane aliases are rejected')
    p.add_argument('--force', action='store_true', help='launch even when a hard gate is not satisfied (records a warning event)')
    p.set_defaults(func=dispatch)

    p = sub.add_parser('status')
    p.add_argument('--project', required=True)
    p.set_defaults(func=status)

    p = sub.add_parser('kill')
    p.add_argument('--project', required=True)
    p.add_argument('--lanes', nargs='+', required=True)
    p.set_defaults(func=kill)

    p = sub.add_parser('workflow')
    p.set_defaults(func=workflow)

    p = sub.add_parser('report')
    p.add_argument('--project', required=True)
    p.set_defaults(func=report)

    p = sub.add_parser('prompts', help='runtime-driven GPT-5.6 Sol authoring for missing ready-block prompt packs')
    p.add_argument('--project', required=True)
    p.add_argument('--block', default='')
    p.add_argument('--lane', default='')
    p.add_argument('--force', action='store_true', help='regenerate even if a pack exists')
    p.set_defaults(func=prompts_cmd)

    p = sub.add_parser('dispatch-image-shards', help='parallel image production inside the image lane: split pending refs across up to --max-parallel detached runners (batches of ~8+)')
    p.add_argument('--project', required=True)
    p.add_argument('--lane', default='image_creator_01', choices=['image_creator_01', 'image_creator_02'])
    p.add_argument('--shard-size', type=int, default=None,
                   help='refs per shard; default auto = ceil(pending / --max-parallel)')
    p.add_argument('--max-parallel', type=int, default=4,
                   help='worker cap (AGENTS.md §3-1 fixes this at 4)')
    p.set_defaults(func=image_shards_cmd)

    p = sub.add_parser('shards-status', help='fan-in for sharded image production; finalizes lane status when all shards done')
    p.add_argument('--project', required=True)
    p.add_argument('--lane', default='image_creator_01', choices=['image_creator_01', 'image_creator_02'])
    p.set_defaults(func=shards_status_cmd)

    p = sub.add_parser('gate', help='check whether lanes may start work now (same judgment as dispatch)')
    p.add_argument('--project', required=True)
    p.add_argument('--lanes', nargs='+', required=True)
    p.set_defaults(func=gate_cmd)

    p = sub.add_parser('next', help='compute current rail position, next owner lanes, and required user actions')
    p.add_argument('--project', required=True)
    p.set_defaults(func=next_cmd)

    p = sub.add_parser('validate', help='lint state/manifest/lane statuses (enum) and queue files')
    p.add_argument('--project', required=True)
    p.set_defaults(func=validate_cmd)

    p = sub.add_parser('seedance-monitor', help='run Seedance in-flight monitor in the foreground')
    p.add_argument('--project', required=True)
    p.add_argument('--block', default='')
    p.add_argument('--interval-seconds', type=int, default=900)
    p.add_argument('--once', action='store_true')
    p.set_defaults(func=seedance_monitor_cmd)

    p = sub.add_parser('seedance-monitor-start', help='start the Seedance in-flight monitor in the background')
    p.add_argument('--project', required=True)
    p.add_argument('--interval-seconds', type=int, default=900)
    p.set_defaults(func=seedance_monitor_start_cmd)

    args = ap.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
