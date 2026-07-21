#!/usr/bin/env python3
"""Codex-delegated video-team runtime supervisor.

Seedance block-parallel workflow edition.
Creates project folders and launches independent Codex lane jobs with the user's
Codex App / CLI runtime. It intentionally does not restore the old Hermes
video-team runtime.
"""
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

HOME = Path(os.environ.get('VIDEO_TEAM_HOME', str(Path.home())))
RUNTIME = HOME / '.hermes' / 'codex-video-runtime'
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
ALIASES = {
    # Backward-compatible names from the first scaffold.
    'visual': ['image_creator_01', 'image_creator_02', 'image_qc', 'seedance', 'seedance_qc'],
    'qc': ['image_qc', 'seedance_qc'],
    # Useful phase groups.
    'image_pool': ['image_creator_01', 'image_creator_02'],
    'image': ['image_creator_01', 'image_creator_02', 'image_qc'],
    'i2v': ['seedance', 'seedance_qc'],
    'parallel': ['image_creator_01', 'image_creator_02', 'image_qc', 'seedance', 'seedance_qc'],
    'all': LANES,
}
QUEUES = [
    'intake_queue',
    'music_queue',
    'planning_queue',
    'image_reference_queue',
    'image_retry_queue',
    'image_review_queue',
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
        'runtime': 'codex-app-delegated-video-team-seedance-block-parallel',
        'workflow_version': '2026-05-16-seedance-block-parallel',
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
        'parallel_production_enabled': False,
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


def dispatch(args) -> None:
    project = Path(args.project).expanduser().resolve()
    if not (project / 'state.json').exists():
        raise SystemExit(f'not a runtime project: {project}')
    if not CODEX.exists():
        raise SystemExit(f'codex not found: {CODEX}')
    lanes = expand_lanes(args.lanes)
    launched = []
    skipped = []
    for lane in lanes:
        # Hard dispatch gates: prevent generic "continue"/fan-in from starting downstream lanes
        # before their true upstream owner has handed off. This keeps roles separated:
        # Image -> Image QC -> Seedance/video -> Seedance QC -> Editor -> Package.
        skip_reason = None
        if lane == 'seedance':
            qtxt = read(project / 'queues' / 'seedance_block_queue.jsonl')
            handoff_ok = (project / 'lanes' / 'seedance' / 'ROLE_VISIBLE_HANDOFF_APPROVED.json').exists() or 'TOJI_VISIBLE_HANDOFF_APPROVED' in qtxt
            bundle_handoff_ok = 'SUKUNA_REFERENCE_BUNDLE_HANDOFF_TO_TOJI' in qtxt
            if not bundle_handoff_ok:
                skip_reason = 'WAIT_SUKUNA_REFERENCE_BUNDLE_HANDOFF: Sukuna/Image has not yet briefed and handed a complete approved reference bundle to Toji/video.'
            elif not handoff_ok:
                skip_reason = 'WAIT_VISIBLE_TOJI_HANDOFF: video/Seedance bot has not been visibly handed off/summoned in the project thread.'
            elif 'SEEDANCE_BLOCK_READY' not in qtxt:
                skip_reason = 'WAIT_IMAGE_QC_BLOCK_READY: no SEEDANCE_BLOCK_READY event; do not launch video/Seedance from Planner-only state.'
        elif lane == 'seedance_qc':
            qtxt = read(project / 'queues' / 'seedance_review_queue.jsonl')
            if not qtxt.strip():
                skip_reason = 'WAIT_SEEDANCE_OUTPUT: no Seedance review/output event.'
        elif lane == 'editor':
            sqc = json.loads(read(project / 'lanes' / 'seedance_qc' / 'status.json') or '{}')
            if int(sqc.get('approved_for_edit_count') or 0) <= 0:
                skip_reason = 'WAIT_SEEDANCE_QC_PASS: no approved video clips.'
        elif lane == 'package':
            est = json.loads(read(project / 'lanes' / 'editor' / 'status.json') or '{}')
            if est.get('status') not in ['DONE', 'READY_FOR_USER_REVIEW']:
                skip_reason = 'WAIT_EDITOR_DONE: package cannot start before editor output.'
        if skip_reason:
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
                f"HOME={shlex.quote(str(HOME))} {shlex.quote(sys.executable)} {shlex.quote(str(runner))} "
                f"--project {shlex.quote(str(project))} --lane {shlex.quote(lane)}"
            )
        elif lane == 'image_qc':
            runner = RUNTIME / 'scripts' / 'image_qc_lane_runner.py'
            inner = (
                f"HOME={shlex.quote(str(HOME))} {shlex.quote(sys.executable)} {shlex.quote(str(runner))} "
                f"--project {shlex.quote(str(project))}"
            )
        else:
            inner = (
                f"HOME={shlex.quote(str(HOME))} {shlex.quote(str(CODEX))} exec "
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
        append_jsonl(project / 'queues' / 'retry_router_queue.jsonl', {
            'ts': dt.datetime.now().isoformat(),
            'event': 'lane_dispatched',
            'lane': lane,
            'pid': proc.pid,
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
        running = pid_running(pid)
        result_exists = (lane_dir / 'result.md').exists() and (lane_dir / 'result.md').stat().st_size > 0
        rows.append({
            'lane': lane,
            'status': s.get('status', 'PENDING'),
            'pid': pid,
            'running': running,
            'result_exists': result_exists,
            'result': str(lane_dir / 'result.md'),
            'log': str(lane_dir / 'run.log'),
        })
    manifest = json.loads(read(project / 'manifest.json') or '{}')
    print(json.dumps({
        'project': str(project),
        'phase': manifest.get('project_phase'),
        'music': manifest.get('music'),
        'parallel_production_enabled': manifest.get('parallel_production_enabled'),
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
        'workflow': 'Seedance block-parallel video team',
        'serial': ['director', 'music', 'planner'],
        'parallel_after_locks': ['image_creator_01', 'image_creator_02', 'image_qc', 'seedance', 'seedance_qc'],
        'limited_serial': ['editor', 'package'],
        'lanes': LANES,
        'aliases': ALIASES,
        'queues': QUEUES,
        'kanban_assignee_map': kanban_assignee_map(),
        'safety_gates': [
            'public upload/publish', 'contest/government final submission', 'email send',
            'personal-info form submit', 'payment', 'password/2FA', 'permanent deletion',
        ],
    }, ensure_ascii=False, indent=2))


def kanban_assignee_map() -> dict[str, str]:
    """Map runtime lanes to stable Hermes profiles.

    This deliberately does not invent one-off subagents. The current video-team
    uses distinct physical Discord bots/Hermes profiles: Director, Music,
    Planner, image, Seedance/video, QC, and Edit. Keep Image and Seedance split
    so one Visual-style profile does not roleplay both jobs.
    """
    return {
        'director': 'director',
        'music': 'music',
        'planner': 'planner',
        'image_creator_01': 'visual',  # Discord display: 료멘 스쿠나(image)
        'image_creator_02': 'visual',  # profile name remains visual; role is image-only
        'image_qc': 'qc',
        'seedance': 'seedance',
        'seedance_qc': 'qc',
        'editor': 'editor',
        'package': 'editor',
        'retry_router': 'director',
    }


def run_kanban(cmd: list[str], want_json: bool = False):
    env = os.environ.copy()
    env.setdefault('HOME', str(HOME))
    proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
    if proc.returncode != 0:
        raise SystemExit(f"kanban command failed ({proc.returncode}): {' '.join(cmd)}\n{proc.stdout}")
    if want_json:
        return json.loads(proc.stdout)
    return proc.stdout


def kanban_task_body(project: Path, lane: str, action: str) -> str:
    return f"""VISIBILITY ONLY — FIXED VIDEO-RUNTIME KANBAN RAIL.
DO NOT EXECUTE VIA HERMES WORKER.
DO NOT CLAIM OR EXECUTE THIS CARD DIRECTLY.
DO NOT CREATE ARBITRARY SUBAGENTS, DELEGATE_TASK CHILDREN, OR NEW HERMES PROFILES.

PROJECT:
{project}

RUNTIME COMMAND:
~/.local/bin/video-codex-runtime

LANE/ACTION:
{lane.upper()} / {action}

ALLOWED EXECUTION MODEL:
USE ONLY FIXED VIDEO RUNTIME LANES:
DIRECTOR, MUSIC, PLANNER, IMAGE_CREATOR_01, IMAGE_CREATOR_02, IMAGE_QC, SEEDANCE, SEEDANCE_QC, EDITOR, PACKAGE.

SOURCE OF TRUTH:
video-codex-runtime report --project {project}

EVIDENCE PATH:
{project / 'lanes' / lane}

CANONICAL STATE:
manifest.json
queues/*

IMAGE CREATOR POLICY:
IMAGE_CREATOR LANES MAY USE ONLY CODEX RUNTIME + NON-GUI FILE-BACKED IMAGE PROVIDER/API/CLI.
BROWSER USE, COMPUTER USE, SAFARI/CHROME, CHATGPT WEB UI, AND GUI DOWNLOADS ARE FORBIDDEN.
SEEDANCE OPERATOR IS THE ONLY PRODUCTION COMPUTER USE OWNER.

BLOCKED UNTIL:
A NON-GUI FILE-BACKED IMAGE PROVIDER/API/CLI IS CONFIGURED, VERIFIED, AND THE LANE IS EXPLICITLY RESET/UNBLOCKED.

COMPLETION RULE:
COMPLETE ONLY WHEN THE LANE HAS A REAL RESULT/STATUS FILE OR VERIFIED ARTIFACT EVIDENCE.

GATES:
IF LOGIN/CAPTCHA/PAYMENT/PERMISSION/ACCOUNT-LIMIT/FINAL-SUBMIT GATE APPEARS, BLOCK WITH EXACT USER ACTION.
NEVER PUBLIC UPLOAD, SUBMIT, EMAIL, PERSONAL-INFO FORM, PAYMENT, PASSWORD/2FA, OR PERMANENTLY DELETE WITHOUT EXPLICIT USER APPROVAL.
"""


def kanban_plan(args) -> None:
    project = Path(args.project).expanduser().resolve()
    if not (project / 'state.json').exists():
        raise SystemExit(f'not a runtime project: {project}')
    board = args.board or slugify('video-' + project.name)
    run_kanban([
        'hermes', 'kanban', 'boards', 'create', board,
        '--name', args.name or f'Video: {project.name}',
        '--description', f'Fixed Seedance block-parallel rail for {project}',
        '--icon', '🎬',
        '--color', '#8b5cf6',
    ])
    assignees = kanban_assignee_map()

    specs = [
        ('director', '[Director] intake / mode / safety gates', [], 'Project mode, assumptions, safety gates, orchestrator run card.'),
        ('music', '[Music] serial Music Lock + beat map', ['director'], 'Lock or block music; write beat/section/energy map.'),
        ('planner', '[Planner] Cut Map + Multi-reference Block Map', ['music'], 'Create cut list, music cue map, block map, reference order/counts.'),
        ('image_creator_01', '[Image] 료멘 스쿠나(image) — reference 01', ['planner'], 'Generate primary block reference images from image_reference_queue.'),
        ('image_creator_02', '[Image] 료멘 스쿠나(image) — reference 02 / retry', ['planner'], 'Generate retry references and next-block refs without project-wide lock.'),
        ('image_qc', '[QC] Image QC — individual + block continuity', ['image_creator_01', 'image_creator_02'], 'Approve references for I2V or route to retry/planning.'),
        ('seedance', '[Video] 후시구로토우지(video) — Seedance Operator', ['image_qc'], 'Run Seedance 2.0 for approved blocks; lock only block/stage.'),
        ('seedance_qc', '[QC] Seedance Video QC', ['seedance'], 'Verify Seedance outputs and route PASS/retry/delete/edit-trim.'),
        ('retry_router', '[Director] Retry router / manifest fan-in', ['image_qc', 'seedance_qc'], 'Keep manifest/queues coherent; route failures to exact lane.'),
        ('editor', '[Editor] CapCut/edit from verified clips only', ['seedance_qc'], 'Assemble verified clips to locked music; no raw still final.'),
        ('package', '[Package] delivery package / submission gate', ['editor'], 'Prepare package/disclosure/copy; stop before final side effects.'),
    ]

    ids: dict[str, str] = {}
    created = []
    for lane, title, parents, action in specs:
        cmd = [
            'hermes', 'kanban', '--board', board, 'create', title,
            '--body', kanban_task_body(project, lane if lane != 'retry_router' else 'director', action),
            '--assignee', assignees[lane],
            '--workspace', f'dir:{project}',
            '--created-by', 'video-codex-runtime',
            '--idempotency-key', f'{project.name}:{lane}',
            '--max-retries', '1',
            '--skill', 'codex',
            '--json',
        ]
        for parent in parents:
            cmd.extend(['--parent', ids[parent]])
        task = run_kanban(cmd, want_json=True)
        ids[lane] = task['id']
        created.append({'lane': lane, 'task_id': task['id'], 'assignee': assignees[lane], 'status': task.get('status')})

    # Store the bridge in the project manifest for dashboard/runtime cross-reference.
    manifest_path = project / 'manifest.json'
    manifest = json.loads(read(manifest_path) or '{}')
    manifest['kanban'] = {'board': board, 'tasks': ids, 'created_at': dt.datetime.now().isoformat()}
    write_json(manifest_path, manifest)

    print(json.dumps({'project': str(project), 'board': board, 'tasks': created}, ensure_ascii=False, indent=2))


def report(args) -> None:
    """Print a compact human-readable runtime board for Discord/status posts."""
    project = Path(args.project).expanduser().resolve()
    manifest = json.loads(read(project / 'manifest.json') or '{}')
    lines = []
    lines.append(f"[Codex Runtime] {project.name}")
    lines.append(f"project: {project}")
    if manifest.get('kanban'):
        lines.append(f"kanban: {manifest.get('kanban', {}).get('board')}")
    lines.append(f"phase: {manifest.get('project_phase')}")
    lines.append(f"parallel_enabled: {manifest.get('parallel_production_enabled')}")
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


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('init')
    p.add_argument('--slug', default='')
    p.add_argument('--brief', required=True)
    p.set_defaults(func=init_project)

    p = sub.add_parser('dispatch')
    p.add_argument('--project', required=True)
    p.add_argument('--lanes', nargs='+', required=True)
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

    p = sub.add_parser('kanban-plan')
    p.add_argument('--project', required=True)
    p.add_argument('--board', default='')
    p.add_argument('--name', default='')
    p.set_defaults(func=kanban_plan)

    p = sub.add_parser('report')
    p.add_argument('--project', required=True)
    p.set_defaults(func=report)

    args = ap.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
