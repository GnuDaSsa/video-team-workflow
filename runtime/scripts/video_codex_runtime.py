#!/usr/bin/env python3
"""Sequential video workflow; delegated dispatch is an explicitly approved exception."""
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
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lane_gates  # shared gate/status-enum/validation logic (P1/P2/P3)
import generation_settings
import media_registry
import model_routing
import video_knowledge_router
import lane_sessions
import preprod

HOME = Path('/Users/gnudas')
RUNTIME = Path('/Users/gnudas/Documents/Codex/video-team-runtime/runtime')
TEMPLATES = Path(__file__).resolve().parents[1] / 'templates'
# Rules (AGENTS.md), session_policy.json and pre-2026-11-10 project symlinks stay on the local disk.
PROJECT_ROOT = HOME / 'Documents' / 'Codex' / 'video-team-runtime'
# 2026-11-10: the local disk was 93% full, so project folders (all media) live on the external
# SSD volume `gnudas-ssd` (a separate APFS volume next to the Time Machine volume).
PROJECTS_HOME = Path(os.environ.get('VIDEO_TEAM_PROJECTS_ROOT', '/Volumes/gnudas-ssd/video-team/projects'))


def project_dirs() -> list[Path]:
    """Every real project folder: SSD first, then any project not yet moved off the local root."""
    found: dict[str, Path] = {}
    for root in (PROJECTS_HOME, PROJECT_ROOT):
        if not root.is_dir():
            continue
        for p in sorted(root.iterdir()):
            # legacy local entries are symlinks to the SSD copy; count each project once
            if p.is_dir() and not p.is_symlink() and (p / 'state.json').exists():
                found.setdefault(p.name, p)
    return [found[k] for k in sorted(found)]
CODEX = Path('/opt/homebrew/bin/codex')
IMAGE_MAX_PARALLEL = 3
STANDARD_I2V_MODE = 'standard_i2v'
NO_I2V_MODE = 'no_i2v_reference_native'
GENERATION_MODES = (STANDARD_I2V_MODE, NO_I2V_MODE)

LANES = [
    'director',
    'music',
    'planner',
    'image_creator_01',
    'image_creator_02',
    'image_qc',
    'seedance',
    'flow',
    'seedance_qc',
    'package',
]
TEMPLATE_BY_LANE = {
    'flow': 'flow.md',
    'director': 'director.md',
    'music': 'music.md',
    'planner': 'planner.md',
    'image_creator_01': 'image_creator.md',
    'image_creator_02': 'image_creator.md',
    'image_qc': 'image_qc.md',
    'seedance': 'seedance.md',
    'seedance_qc': 'seedance_qc.md',
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


def run_due_cleanup(project: Path) -> list[dict]:
    """Apply the user-selected 24-hour Trash policy during normal runtime use.

    This is synchronous and bounded; it does not create a scheduler, daemon, or
    agent. Only registry-marked inactive work-area files can be selected.
    """
    project = Path(project).expanduser().resolve()
    if not media_registry.is_v4_project(project):
        return []
    candidates = media_registry.cleanup_candidates(project, older_than_hours=24)
    moved = media_registry.move_candidates_to_trash(project, candidates)
    if moved:
        append_jsonl(project / 'queues' / 'retry_router_queue.jsonl', {
            'ts': dt.datetime.now().isoformat(),
            'event': 'AUTO_TRASH_24H',
            'moved_count': len(moved),
            'asset_ids': [item['asset_id'] for item in moved],
            'trash_emptied': False,
        })
    return moved


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
    generation_mode = getattr(args, 'mode', STANDARD_I2V_MODE)
    if generation_mode not in GENERATION_MODES:
        raise SystemExit(f'unknown generation mode {generation_mode}; valid={GENERATION_MODES}')
    slug = slugify(args.slug or args.brief[:40] or 'video-project')
    if not PROJECTS_HOME.is_dir():
        raise SystemExit(f'PROJECTS_SSD_NOT_MOUNTED: {PROJECTS_HOME} is missing. Connect the external SSD '
                         '(volume gnudas-ssd) and retry; do not create the project on the local disk.')
    project = PROJECTS_HOME / f'{now()}_{slug}'
    project.mkdir(exist_ok=False)
    for lane in LANES:
        (project / 'lanes' / lane).mkdir(parents=True, exist_ok=True)
    for q in QUEUES:
        qp = project / 'queues' / f'{q}.jsonl'
        qp.parent.mkdir(parents=True, exist_ok=True)
        qp.touch()
    for sub in ['locks', 'docs']:
        (project / sub).mkdir(parents=True, exist_ok=True)
    (project / 'brief.md').write_text(args.brief.rstrip() + '\n', encoding='utf-8')

    state = {
        'project': str(project),
        'created_at': dt.datetime.now().isoformat(),
        'slug': slug,
        'runtime': 'codex-app-delegated-video-team-sequential',
        'workflow_version': '2026-07-31-sequential-media-v4',
        'generation_mode': generation_mode,
        'media_schema_version': media_registry.MEDIA_SCHEMA_VERSION,
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
        'generation_mode': generation_mode,
        'visual_generation_strategy': {
            'mode': generation_mode,
            'per_cut_styleframes': generation_mode == STANDARD_I2V_MODE,
            'reference_minimal': generation_mode == NO_I2V_MODE,
            'prompt_heavy': generation_mode == NO_I2V_MODE,
            'new_image_policy': (
                'only_missing_provider_safe_references'
                if generation_mode == NO_I2V_MODE
                else 'one_standalone_source_frame_per_planned_cut'
            ),
        },
        'media_schema_version': media_registry.MEDIA_SCHEMA_VERSION,
        'media_root': str(project / 'media'),
        'asset_registry': str(project / media_registry.REGISTRY_NAME),
        'knowledge_routing': {
            'enabled': True,
            'router_version': video_knowledge_router.ROUTER_VERSION,
            'catalog': str(video_knowledge_router.DEFAULT_WIKI_ROOT / video_knowledge_router.DEFAULT_CATALOG_REL),
            'attributes': str(project / 'lanes' / 'planner' / 'video_attributes.json'),
            'budget_chars': video_knowledge_router.DEFAULT_BUDGET_CHARS,
            'max_selections': video_knowledge_router.DEFAULT_MAX_SELECTIONS,
            'required_before_prompt_attestation': True,
            'full_wiki_auto_read': False,
        },
        'execution_budget': {
            'default_active_lanes': 1,
            'image_generation_workers_max': IMAGE_MAX_PARALLEL,
            'browser_operators_max': 1,
            'parallel_providers_max': 1,
            'detached_monitors_max': 0,
        },
        'model_routing': {
            'policy_version': model_routing.POLICY_VERSION,
            'routes': model_routing.matrix(),
            'seedance_split_phase': True,
            'auto_spawn_next_phase': False,
        },
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
        'package': {'status': 'NOT_STARTED'},
        'safety': state['safety'],
    }
    write_json(project / 'state.json', state)
    write_json(project / 'manifest.json', manifest)
    generation_settings.initialize_duration_lock(project)
    media_registry.init_registry(project)
    append_jsonl(project / 'queues' / 'intake_queue.jsonl', {
        'ts': dt.datetime.now().isoformat(),
        'event': 'project_created',
        'project': str(project),
        'brief': str(project / 'brief.md'),
        'generation_mode': generation_mode,
    })
    if getattr(args, 'preprod', False):
        import preprod
        preprod.init(project)
        if getattr(args, 'author', ''):
            import claude_author
            claude_author.set_mode(project, args.author, 'init --author ' + args.author)
    print(str(project))


def set_mode(args) -> None:
    """Change future unsubmitted blocks between standard I2V and No-I2V."""
    project = Path(args.project).expanduser().resolve()
    mode = args.mode
    if mode not in GENERATION_MODES:
        raise SystemExit(f'unknown generation mode {mode}; valid={GENERATION_MODES}')
    manifest_path, state_path = project / 'manifest.json', project / 'state.json'
    manifest = json.loads(read(manifest_path) or '{}')
    state = json.loads(read(state_path) or '{}')
    previous = manifest.get('generation_mode', STANDARD_I2V_MODE)
    if previous == mode:
        print(json.dumps({'project': str(project), 'changed': False, 'mode': mode},
                         ensure_ascii=False, indent=2))
        return

    changed_blocks, preserved_submitted = [], []
    for block in manifest.get('blocks') or []:
        submitted = bool(
            block.get('provider_job_id') or block.get('submitted_at')
            or str(block.get('status', '')).upper() in {
                'SUBMITTED', 'IN_QUEUE', 'GENERATING', 'PROCESSING', 'COMPLETED',
            }
        )
        if submitted:
            preserved_submitted.append(block.get('block_id'))
            continue
        block['generation_mode'] = mode
        if mode == NO_I2V_MODE:
            block['source_frame_file'] = None
            block['keyframe_refs'] = []
            block['reference_policy'] = 'minimum_identity_environment_refs_only'
        changed_blocks.append(block.get('block_id'))

    strategy = {
        'mode': mode,
        'per_cut_styleframes': mode == STANDARD_I2V_MODE,
        'reference_minimal': mode == NO_I2V_MODE,
        'prompt_heavy': mode == NO_I2V_MODE,
        'new_image_policy': (
            'only_missing_provider_safe_references'
            if mode == NO_I2V_MODE
            else 'one_standalone_source_frame_per_planned_cut'
        ),
    }
    manifest['generation_mode'] = mode
    manifest['visual_generation_strategy'] = strategy
    manifest['mode_switch'] = {
        'from': previous,
        'to': mode,
        'changed_at': dt.datetime.now().isoformat(),
        'changed_unsubmitted_blocks': changed_blocks,
        'preserved_submitted_blocks': preserved_submitted,
        'existing_media_deleted': False,
    }
    state['generation_mode'] = mode
    state['mode_switch'] = manifest['mode_switch']
    write_json(manifest_path, manifest)
    write_json(state_path, state)
    append_jsonl(project / 'queues' / 'planning_queue.jsonl', {
        'ts': dt.datetime.now().isoformat(),
        'event': 'GENERATION_MODE_CHANGED',
        'from': previous,
        'to': mode,
        'changed_unsubmitted_blocks': changed_blocks,
        'preserved_submitted_blocks': preserved_submitted,
    })
    print(json.dumps({
        'project': str(project),
        'changed': True,
        'from': previous,
        'to': mode,
        'changed_unsubmitted_blocks': changed_blocks,
        'preserved_submitted_blocks': preserved_submitted,
    }, ensure_ascii=False, indent=2))


def seedance_phase(project: Path, requested: str = 'auto') -> str:
    """Resolve one sequential Seedance owner phase without starting anything."""
    if requested in {'prompting', 'production'}:
        return requested
    if requested != 'auto':
        raise SystemExit('seedance phase must be auto|prompting|production')
    status = json.loads(read(project / 'lanes' / 'seedance' / 'status.json') or '{}')
    if preprod.is_preprod_project(project):
        released = preprod.released_blocks(project)
        if released and (lane_sessions.production_batch(project, released)[0]
                         or lane_sessions.undownloaded_jobs(project)):
            return 'production'
    normalized = str(status.get('status') or '').upper()
    phase = str(status.get('phase') or '').lower()
    if normalized == 'READY_FOR_PRODUCTION' or phase in {
            'prompting_complete', 'ready_for_production', 'production'}:
        return 'production'
    recovery = json.loads(
        read(project / 'lanes' / 'seedance' / 'recovery_state.json') or '{}')
    if str(recovery.get('status') or '').upper() in {
            'RECOVERING', 'USER_ACTION_REQUIRED', 'ACTIVE'}:
        return 'production'
    if lane_gates._seedance_resume_needed(project):
        return 'production'
    return 'prompting'


def image_phase(project: Path, requested: str = 'auto') -> str | None:
    """Image lanes: `production` (GUI route, reaches Aside/Runway) once every P3 prompt exists and
    images are not locked; `None` (authoring route) while prompts are still being written."""
    if requested == 'production':
        return 'production'
    if requested == 'prompting' or not preprod.is_preprod_project(project):
        return None
    plan = preprod.image_plan(project)
    if not plan.get('references') or preprod.lock_state(project, 'images')['state'] == 'LOCKED':
        return None
    authoring_left = [e for e in preprod.validate_images(project)
                      if not ('_not_generated_or_not_approved' in e or '_asset_not_' in e)]
    return None if authoring_left else 'production'


def lane_phase(project: Path, lane: str, requested: str = 'auto') -> str | None:
    if lane == 'seedance':
        return seedance_phase(project, requested)
    if lane.startswith('image_creator_'):
        return image_phase(project, requested)
    if requested != 'auto':
        raise SystemExit('--phase is valid only for seedance and image_creator_* lanes')
    return None


def _attested_seedance_packs(project: Path) -> list[str]:
    rows = []
    for path in sorted((project / 'lanes' / 'seedance' / 'prompts').glob('*_attestation.json')):
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
        except Exception:
            continue
        if data.get('verdict') == 'ATTESTED' and not data.get('errors'):
            pack = Path(str(data.get('pack') or ''))
            if pack.is_file():
                rows.append(str(path))
    return rows


def _seedance_phase_contract(project: Path, phase: str, route: dict) -> str:
    if phase == 'prompting':
        return f"""
# MODEL/PHASE CONTRACT — Seedance prompting only

- This foreground owner is `{route['model'] or 'inherit_session'}` with `{route['reasoning_effort'] or 'session-selected'}` reasoning.
- Author, validate, and attest the complete eligible Seedance prompt shelf. Do not open or
  control Aside/Runway, do not invoke Computer Use, and do not click Generate.
- When at least one package has a current `ATTESTED` receipt, finish with
  `status=READY_FOR_PRODUCTION`, `phase=prompting_complete`, and list the attestation paths in
  `{project / 'lanes' / 'seedance' / 'prompting_handoff.json'}`.
- Return the local handoff to the original session executor. Do not spawn a production owner.
"""
    return f"""
# MODEL/PHASE CONTRACT — Seedance production only

- This foreground owner is `{route['model'] or 'inherit_session'}` with `{route['reasoning_effort'] or 'session-selected'}` reasoning.
- Use only current `ATTESTED` prompt packages. Do not rewrite, improve, or silently replace a
  prompt; return to the same owner's prompting step when a creative revision is required.
- Aside is the sole visible Runway owner. Bind the exact existing Runway tab with deterministic
  `aside repl` (`listBrowserTabs()` -> exact targetId -> `attachBrowserTab(targetId)`). Never
  open a new Runway tab or use Chrome, Safari, in-app browser, connector, or API.{_new_tab_recovery_exception(project)}
- Use the same session-selected owner for permitted native Computer Use/file chooser steps. Keep one owner
  tool at a time on the same Aside tab; no second browser loop or nested browser agent.
- Follow the canonical Seedance production skill for recovery, exactly-once Generate, queue
  continuation, download, ffprobe, registry ingest, and evidence.
"""


def _new_tab_recovery_exception(project: Path) -> str:
    """One-off exception: the user approved opening the same session URL in one new tab."""
    state = json.loads(read(project / 'lanes/seedance/recovery_state.json') or '{}')
    answer = state.get('user_answer') or {}
    if state.get('next_action') != 'OPEN_NEW_VISIBLE_TAB_SAME_SESSION_URL' or not answer.get('quote'):
        return ''
    url = (state.get('checkpoint') or {}).get('session_url') or ''
    return (
        f"\n- Recovery exception (user: \"{answer['quote']}\", {answer.get('evidence', '')}): the bound tab is"
        f"\n  unresponsive, so open exactly one visible new Aside tab at the recorded session URL {url}."
        "\n  It is the same Runway session, not a new one; never re-Generate accepted cards."
    )


def make_prompt(project: Path, lane: str, phase: str | None = None) -> str:
    shared = read(TEMPLATES / 'shared_lane_contract.md')
    template_name = TEMPLATE_BY_LANE[lane]
    lane_prompt = read(TEMPLATES / template_name)
    if not lane_prompt:
        raise SystemExit(f'missing lane template: {lane} -> {template_name}')
    route = model_routing.resolve(lane, phase)
    phase_contract = (
        _seedance_phase_contract(project, phase, route)
        if lane == 'seedance' else
        f"""
# MODEL ROUTING CONTRACT

- Required owner: `{route['model'] or 'inherit_session'}` with `{route['reasoning_effort'] or 'session-selected'}` reasoning.
- Route purpose: `{route['purpose']}`.
- This is one explicit sequential owner, not permission to spawn another lane or agent.
"""
    )
    return f"""{phase_contract}

---

{shared}

---

{lane_prompt}

---

Project root: {project}
Lane name: {lane}
Lane directory: {project / 'lanes' / lane}

Before doing work, write RUNNING to `{project / 'lanes' / lane / 'status.json'}`.
At finish, write your final result to `{project / 'lanes' / lane / 'result.md'}` and update status.json.
When updating shared files, keep JSON valid and do not erase other lanes' data.
All media input/output for this v4 project belongs under `{project / 'media'}` and
must be registered in `{project / media_registry.REGISTRY_NAME}`. `lanes/` is for
status, prompts, manifests, QC records and logs only; never store media there.
{lane_sessions.result_contract(project, lane)}"""


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


def pid_reused(pid: int, pid_path: Path) -> bool:
    """A finished lane's pid file can outlive its process; the OS later hands that pid to an
    unrelated process (seen: cfprefsd, 2026-11-07/08) and every dispatch then reports
    SEQUENTIAL_OWNER_EXISTS forever. The real owner started before its pid file was written."""
    try:
        out = subprocess.run(['ps', '-o', 'lstart=', '-p', str(pid)], capture_output=True, text=True,
                             env={**os.environ, 'LC_ALL': 'C'}, timeout=5).stdout.strip()
        started = time.mktime(time.strptime(out, '%a %b %d %H:%M:%S %Y'))
    except (OSError, ValueError, subprocess.SubprocessError):
        return False  # cannot tell: keep the conservative "still running" answer
    return started > pid_path.stat().st_mtime + 5


def update_manifest_lane(project: Path, lane: str, data: dict) -> None:
    manifest_path = project / 'manifest.json'
    manifest = json.loads(read(manifest_path) or '{}')
    manifest.setdefault('lanes', {}).setdefault(lane, {}).update(data)
    write_json(manifest_path, manifest)


def active_lane_owners(project: Path) -> list[dict]:
    owners = []
    for lane in LANES:
        pid_path = project / 'lanes' / lane / 'pid'
        if not pid_path.is_file():
            continue
        try:
            pid = int(read(pid_path).strip())
        except (TypeError, ValueError):
            continue
        if pid_running(pid) and not pid_reused(pid, pid_path):
            status = json.loads(read(project / 'lanes' / lane / 'status.json') or '{}')
            owners.append({
                'lane': lane, 'pid': pid,
                'phase': status.get('dispatch_phase') or status.get('phase') or 'lane',
                'model': status.get('model'),
            })
    return owners


def codex_exec_inner(project: Path, prompt_path: Path, result_path: Path, route: dict) -> str:
    """One fresh lane session. No model in the route = the user's own Codex default.
    `--json` makes run*.log a JSONL event stream the phone console can show live."""
    model = ''
    if route['model']:
        effort_config = 'model_reasoning_effort=' + json.dumps(route['reasoning_effort'])
        model = f"-m {shlex.quote(route['model'])} -c {shlex.quote(effort_config)} "
    sandbox = ' '.join(shlex.quote(a) for a in lane_sessions.sandbox_args(route['route_key']))
    return (
        f"VIDEO_TEAM_LANE={shlex.quote(route['lane'])} HOME=/Users/gnudas {shlex.quote(str(CODEX))} exec "
        f"--skip-git-repo-check --json {sandbox} "
        f"--output-last-message {shlex.quote(str(result_path))} "
        f"-C {shlex.quote(str(project))} {model}< {shlex.quote(str(prompt_path))}"
    )


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
        # Image generation needs the GUI route (full access): the workspace-write authoring
        # route cannot reach the Aside daemon, so `auto` picks production once prompts exist.
        phase = lane_phase(project, lane, getattr(args, 'phase', 'auto'))
        route = model_routing.resolve(lane, phase)
        approval_token = f'{lane}:{phase or "lane"}'
        standing = lane_sessions.load_policy(PROJECT_ROOT)
        if lane == 'director':
            raise SystemExit('DIRECTOR_STAYS_IN_MAIN_THREAD: the director talks to the user; dispatch the next lane instead')
        if getattr(args, 'approved_spawn', None) != approval_token and not standing:
            raise SystemExit(
                'SPAWN_APPROVAL_REQUIRED: this dispatch creates one Codex lane session. '
                f'After explicit current-conversation approval, retry with '
                f'--approved-spawn {approval_token} (or record a standing session-policy)')
        if getattr(args, 'parallel_browserless', False):
            raise SystemExit('PARALLEL_DISABLED: 2026-10-24 parallel lane sessions froze the 16GB Mac; '
                             'wait for the running owner, then dispatch')
        # One Codex lane owner machine-wide, not per project.
        owners = [dict(o, project=str(p)) for p in project_dirs() for o in active_lane_owners(p)]
        if owners:
            raise SystemExit(
                'SEQUENTIAL_OWNER_EXISTS: another Codex lane owner is still running: '
                + json.dumps(owners, ensure_ascii=False))
        # Hard dispatch gates: single source of truth lives in lane_gates.gate_check
        # so `dispatch`, `gate`, `next`, and lanes doing manual work all apply the
        # SAME judgment. Rail: Director -> Music -> Planner -> Image -> Image QC ->
        # Seedance -> Seedance QC -> Editor -> Package.
        ok, skip_reason = lane_gates.gate_check(project, lane)
        non_bypassable = lane_gates.non_bypassable_reason(project, skip_reason or '')
        if not ok and not non_bypassable and (lane_gates.gate_level(lane) == 'soft' or getattr(args, 'force', False)):
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
        if lane == 'seedance':
            prompt_path = lane_dir / f'prompt.{phase}.md'
            result_path = lane_dir / f'result.{phase}.md'
            log_path = lane_dir / f'run.{phase}.log'
        else:
            prompt_path = lane_dir / 'prompt.md'
            result_path = lane_dir / 'result.md'
            log_path = lane_dir / 'run.log'
        batch, remaining, harvest = [], [], []
        if lane == 'seedance' and phase == 'production' and preprod.is_preprod_project(project):
            batch, remaining = lane_sessions.production_batch(
                project, preprod.released_blocks(project), getattr(args, 'blocks', None))
            if not batch:
                harvest = lane_sessions.undownloaded_jobs(project)
                if not harvest:
                    raise SystemExit('SEEDANCE_NOTHING_LEFT: every released block is generated and downloaded; '
                                     'dispatch seedance_qc')
        elif lane == 'seedance' and phase == 'production':
            attested = _attested_seedance_packs(project)
            recovery = json.loads(read(lane_dir / 'recovery_state.json') or '{}')
            resume = lane_gates._seedance_resume_needed(project)
            if not attested and not recovery and not resume:
                raise SystemExit(
                    'SEEDANCE_PRODUCTION_NOT_READY: no current ATTESTED package, recovery '
                    'checkpoint, or in-flight job. Dispatch --phase prompting first.')
        run_due_cleanup(project)  # only after explicit spawn approval and dispatch gates
        previous = lane_dir / lane_sessions.RESULT_NAME
        if previous.exists():
            previous.replace(lane_dir / (lane_sessions.RESULT_NAME + '.prev'))
        prompt_path.write_text(
            lane_sessions.production_prompt(project, batch, remaining, route) if batch
            else lane_sessions.harvest_prompt(project, harvest, route) if harvest
            else make_prompt(project, lane, phase), encoding='utf-8')
        status = {
            'lane': lane, 'status': 'LAUNCHING',
            'launched_at': dt.datetime.now().isoformat(),
            'dispatch_phase': phase or 'lane',
            'model': route['model'],
            'reasoning_effort': route['reasoning_effort'],
            'model_policy_version': route['policy_version'],
            'approved_spawn': approval_token if getattr(args, 'approved_spawn', None) == approval_token
                              else 'standing:' + standing.get('recorded_at', ''),
            'blocks': batch,
        }
        write_json(lane_dir / 'model_route.json', {
            **route,
            'approved_spawn': approval_token,
            'selected_at': status['launched_at'],
            'codex_app_label': (
                f"[model-route] {route['model']} {route['reasoning_effort']} "
                f"| {lane}:{phase or 'lane'}"),
        })
        # provider_jobs is the Runway job ledger (harvest reads it); a new session must not erase it
        prev_jobs = (json.loads(read(lane_dir / 'status.json') or '{}') or {}).get('provider_jobs')
        if prev_jobs:
            status['provider_jobs'] = prev_jobs
        write_json(lane_dir / 'status.json', status)
        update_manifest_lane(project, lane, status)

        inner = codex_exec_inner(project, prompt_path, result_path, route)
        # /usr/bin/script gives Codex/non-Codex lane commands a pseudo-tty and records transcript.
        cmd = ['/usr/bin/script', '-q', str(log_path), '/bin/zsh', '-lc', inner]
        out = open(lane_dir / 'supervisor.out', 'ab', buffering=0)
        err = open(lane_dir / 'supervisor.err', 'ab', buffering=0)
        proc = subprocess.Popen(cmd, cwd=str(project), stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                                start_new_session=True)  # script needs a non-socket stdin
        (lane_dir / 'pid').write_text(str(proc.pid) + '\n', encoding='utf-8')
        status.update({'status': 'RUNNING', 'pid': proc.pid, 'log': str(log_path), 'prompt': str(prompt_path), 'result': str(result_path)})
        write_json(lane_dir / 'status.json', status)
        update_manifest_lane(project, lane, status)
        append_jsonl(project / 'queues' / 'retry_router_queue.jsonl', {
            'ts': dt.datetime.now().isoformat(),
            'event': 'lane_dispatched',
            'lane': lane,
            'pid': proc.pid,
            'phase': phase or 'lane',
            'model': route['model'],
            'reasoning_effort': route['reasoning_effort'],
            'model_policy_version': route['policy_version'],
            'approved_spawn': approval_token,
            'monitor': None,
        })
        launched.append({
            'lane': lane, 'phase': phase or 'lane', 'pid': proc.pid, 'blocks': batch,
            'wait': f'video-codex-runtime wait --project {project} --lane {lane}',
            'model': route['model'], 'reasoning_effort': route['reasoning_effort'],
            'log': str(log_path), 'result': str(result_path)})
    print(json.dumps({'project': str(project), 'launched': launched, 'skipped': skipped}, ensure_ascii=False, indent=2))


def wait_cmd(args) -> None:
    project = Path(args.project).expanduser().resolve()
    print(json.dumps(lane_sessions.wait(project, args.lane, pid_running, args.timeout_min),
                     ensure_ascii=False, indent=2))


def session_policy_cmd(args) -> None:
    if args.show:
        print(json.dumps(lane_sessions.load_policy(PROJECT_ROOT) or {'auto_lane_sessions': False},
                         ensure_ascii=False, indent=2))
        return
    print(json.dumps(lane_sessions.set_policy(PROJECT_ROOT, bool(args.enable), args.approval_quote),
                     ensure_ascii=False, indent=2))


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
        result_path = Path(str(s.get('result') or lane_dir / 'result.md'))
        log_path = Path(str(s.get('log') or lane_dir / 'run.log'))
        result_exists = result_path.exists() and result_path.stat().st_size > 0
        rows.append({
            'lane': lane,
            'status': s.get('status', 'PENDING'),
            'phase': s.get('dispatch_phase') or s.get('phase') or 'lane',
            'model': s.get('model'),
            'reasoning_effort': s.get('reasoning_effort'),
            'model_policy_version': s.get('model_policy_version'),
            'pid': pid,
            'running': running,
            'monitor_pid': None,
            'monitor_running': False,
            'result_exists': result_exists,
            'result': str(result_path),
            'log': str(log_path),
            'model_route': str(lane_dir / 'model_route.json'),
        })
    manifest = json.loads(read(project / 'manifest.json') or '{}')
    print(json.dumps({
        'project': str(project),
        'phase': manifest.get('project_phase'),
        'music': manifest.get('music'),
        'sequential_agent_mode': manifest.get('sequential_agent_mode', True),
        'block_count': len(manifest.get('blocks') or []),
        'active_owners': active_lane_owners(project),
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
            prev_jobs = (json.loads(read(lane_dir / 'status.json') or '{}') or {}).get('provider_jobs')
            if prev_jobs:
                status['provider_jobs'] = prev_jobs
            write_json(lane_dir / 'status.json', status)
            update_manifest_lane(project, lane, status)
        except Exception as e:
            killed.append({'lane': lane, 'pid': pid, 'error': str(e)})
    print(json.dumps({'killed': killed}, ensure_ascii=False, indent=2))


def workflow(args) -> None:
    print(json.dumps({
        'workflow': 'Sequential Codex-only video team',
        'generation_modes': {
            STANDARD_I2V_MODE: 'per-cut source frames followed by I2V',
            NO_I2V_MODE: 'minimum reusable references; no per-cut frames; prompt-heavy native video',
        },
        'mode': 'one current owner, one lane at a time; next selects a responsibility, not a new agent; dispatch is optional and separately approved',
        'serial_order': LANES,
        'aliases': ALIASES,
        'alias_policy': 'no grouped lane aliases in sequential mode',
        'prompt_ownership': {
            'dedicated_prompt_agent': False,
            'image_prompts': 'owning image_creator lane, fixed before workers start',
            'seedance_prompts': 'owning seedance lane, Korean, validated before Runway operation',
        },
        'model_routing': {
            'policy_version': model_routing.POLICY_VERSION,
            'routes': model_routing.matrix(),
            'seedance_phase_handoff': 'same-owner sequential by default; approved new-owner dispatch preferences: prompting(Astra xhigh), production(session-selected)',
            'auto_spawn_next_phase': False,
        },
        'internal_parallel_exceptions': [
            'image generation only: at most three bounded workers inside one image_creator stage',
            'one 15-minute same-task foreground tool wait while a prepared package waits on a full queue',
        ],
        'seedance_recovery': {
            'controller': '/Users/gnudas/.codex/skills/seedance-prompt-en/scripts/runway_ui_helper.py recovery-checkpoint|recovery-record|recovery-resolve',
            'runtime_helper_role': 'compatibility shim only; Seedance skill owns implementation',
            'scope': 'same Aside tab, exact existing Runway session, exact block and slot',
            'transport_failure_consumes_attachment_attempt': False,
            'premature_terminal_blocked_rejected': True,
            'queue_wake_reused_for_session_errors': False,
        },
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
    lines.append(f"generation_mode: {manifest.get('generation_mode', STANDARD_I2V_MODE)}")
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
        result_path = Path(str(st.get('result') or lane_dir / 'result.md'))
        result = result_path.exists() and result_path.stat().st_size > 0
        status_txt = st.get('status', 'PENDING')
        icon = '●' if running else ('✓' if result else ('◌' if status_txt in {'PENDING', ''} else '○'))
        model = st.get('model') or '-'
        effort = st.get('reasoning_effort') or '-'
        phase = st.get('dispatch_phase') or st.get('phase') or 'lane'
        lines.append(
            f"- {icon} {lane:17s} status={status_txt} phase={phase} "
            f"model={model}/{effort} running={str(running).lower()} "
            f"pid={pid or '-'} result={'yes' if result else 'no'}")
    lines.append("")
    lines.append("key paths:")
    lines.append(f"- manifest: {project / 'manifest.json'}")
    lines.append(f"- queues:   {project / 'queues'}")
    lines.append(f"- lanes:    {project / 'lanes'}")
    print('\n'.join(lines))


def image_shards_cmd(args) -> None:
    """Prepare immutable work for the CURRENT owner's built-in imagegen; no spawn."""
    project = Path(args.project).expanduser().resolve()
    lane = args.lane
    if not 1 <= args.max_parallel <= IMAGE_MAX_PARALLEL:
        raise SystemExit(f'IMAGE_WORKER_CAP_EXCEEDED: max-parallel must be 1..{IMAGE_MAX_PARALLEL}')
    ok, reason = lane_gates.gate_check(project, lane)
    if not ok:
        raise SystemExit(reason)
    prompt_dir = project / 'lanes' / lane / 'prompts'
    items = []
    for prompt in sorted(prompt_dir.glob('*.prompt.txt')):
        rid = prompt.name[:-len('.prompt.txt')]
        digest = media_registry.sha256(prompt)
        existing = media_registry.latest_asset(project, rid, kind='image', states={'candidate', 'approved', 'selected'}) if media_registry.is_v4_project(project) else None
        if existing and existing.get('prompt_hash') == digest:
            continue
        refs_path = prompt.parent / f'{rid}.refs.json'
        references = []
        if refs_path.exists():
            raw = json.loads(refs_path.read_text())
            if not isinstance(raw, list) or not raw:
                raise SystemExit('IMAGE_REFERENCE_SIDECAR_INVALID: ' + rid)
            for value in raw:
                ref = Path(value).expanduser().resolve()
                asset = media_registry.asset_for_path(project, ref)
                if (not asset or not asset.get('active') or asset.get('state') not in {'approved', 'selected', 'locked'}
                        or not ref.is_file() or media_registry.sha256(ref) != asset.get('sha256')):
                    raise SystemExit('BLOCKED_CHARACTER_SHEET_ATTACHMENT_NOT_VERIFIED: ' + rid)
                references.append({'asset_id': asset['asset_id'], 'path': str(ref), 'sha256': asset['sha256']})
        items.append({'work_item_id': rid, 'prompt_path': str(prompt), 'prompt_sha256': digest,
                      'references': references, 'attachment_verified_by_generator': False})
    size = args.max_parallel
    result = {'status': 'HANDOFF_TO_CURRENT_OWNER_IMAGEGEN', 'generation_started': False,
              'agents_spawned': 0, 'batches': [items[i:i+size] for i in range(0,len(items),size)],
              'next_action': 'Current owner reads Gongnyang/imagegen skills, rechecks immutable hashes, verifies required image attachments, calls built-in image_gen per item, saves/registers real files, then image QC. No codex thread/start or API fallback.'}
    out = project / 'lanes' / lane / 'imagegen_handoff.json'
    write_json(out, result)
    print(json.dumps({**result, 'handoff_path': str(out)}, ensure_ascii=False, indent=2))


def shards_status_cmd(args) -> None:
    """Fan-in: merge shard statuses; when all finished, finalize lane status/result."""
    project = Path(args.project).expanduser().resolve()
    lane = args.lane
    lane_dir = project / 'lanes' / lane
    shards_dir = lane_dir / 'shards'
    rows, all_done, gen_total, fail_total = [], True, 0, 0
    orchestrator = json.loads(read(shards_dir / 'orchestrator.json') or '{}')
    expected_ids = [row.get('shard') for row in orchestrator.get('shards', []) if row.get('shard')]
    if not expected_ids:
        expected_ids = [sp.name.replace('.status.json', '') for sp in sorted(shards_dir.glob('shard_*.status.json'))]
    for shard_id in expected_ids:
        sp = shards_dir / f'{shard_id}.status.json'
        s = json.loads(read(sp) or '{}')
        pid = None
        pidf = shards_dir / f'{shard_id}.pid'
        if pidf.exists():
            try:
                pid = int(read(pidf).strip())
            except Exception:
                pid = None
        running = pid_running(pid)
        done = sp.exists() and s.get('phase') == 'complete'
        all_done &= (done and not running)
        gen_total += int(s.get('generated_count') or 0)
        fail_total += int(s.get('failure_count') or 0)
        rows.append({'shard': shard_id, 'status': s.get('status', 'STARTING'), 'running': running,
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
    result = lane_gates.next_actions(project)
    dispatch = []
    for lane in result.get('next_lanes') or []:
        phase = lane_phase(project, lane)
        dispatch.append(model_routing.resolve(lane, phase))
    result['default_execution'] = {
        'action': 'CONTINUE_IN_CURRENT_CONVERSATION',
        'new_owner': False,
        'new_approval_for_role_change': False,
        'automatic_model_switch': False,
        'authoring_model': 'inherit_session',
        'same_owner_authoring_allowed': True,
        'next_roles': [{'lane': row['lane'], 'phase': row['phase'],
                        'preferred_author_model': row['model'],
                        'author_model_preference_only': True,
                        'author_protocol': 'AGENTS.md §1.3'} for row in dispatch],
        'dispatch_note': 'next_dispatch is optional new-owner routing only. Continue prompting and production here with the actual session model; do not spawn or request routine approval.',
    }
    gate = (lane_sessions.user_gate(project, result.get('preprod') or {})
            if preprod.is_preprod_project(project) else None)
    if gate:
        result['default_execution'] = {
            **gate, 'new_owner': False, 'new_approval_for_role_change': False, 'automatic_model_switch': False,
            'dispatch_note': ('Director: ' + ('show the user the listed file(s), ask once, then record their words with the command.'
                                              if gate['action'] == 'ASK_USER' else 'lock this stage, then run next again.')),
        }
    elif lane_sessions.load_policy(PROJECT_ROOT):
        lanes = [row for row in dispatch if row['lane'] != 'director']
        result['default_execution'] = {
            'action': 'DISPATCH_LANE_SESSION' if lanes else 'DIRECTOR_IN_MAIN_THREAD',
            'new_owner': bool(lanes),
            'new_approval_for_role_change': False,
            'automatic_model_switch': False,
            'commands': [f"video-codex-runtime dispatch --project {project} --lanes {row['lane']}"
                         + (f" --phase {row['phase']}" if row['phase'] != 'lane' else '')
                         + f" && video-codex-runtime wait --project {project} --lane {row['lane']}"
                         for row in lanes[:1]],
            'dispatch_note': ('Main thread = director. Start the next lane as its own session, wait, read only '
                              'session_result.json, talk to the user. Do not do lane work in the main thread.'),
        }
    result['next_dispatch'] = dispatch
    print(json.dumps(result, ensure_ascii=False, indent=2))


def model_route_cmd(args) -> None:
    project = Path(args.project).expanduser().resolve() if args.project else None
    if args.lane:
        phase = args.phase
        if args.lane == 'seedance' and phase == 'auto':
            if project is None:
                raise SystemExit('--project is required for seedance --phase auto')
            phase = seedance_phase(project, 'auto')
        elif args.lane.startswith('image_creator_'):
            phase = image_phase(project, phase) if project else (None if phase != 'production' else phase)
        elif args.lane != 'seedance':
            phase = None
        print(json.dumps(model_routing.resolve(args.lane, phase), ensure_ascii=False, indent=2))
        return
    print(json.dumps({
        'policy_version': model_routing.POLICY_VERSION,
        'routes': model_routing.matrix(),
    }, ensure_ascii=False, indent=2))


def validate_cmd(args) -> None:
    project = Path(args.project).expanduser().resolve()
    result = lane_gates.validate_project(project)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result['ok']:
        raise SystemExit(1)


def knowledge_select_cmd(args) -> None:
    project = Path(args.project).expanduser().resolve()
    manifest = json.loads(read(project / 'manifest.json') or '{}')
    config = manifest.get('knowledge_routing') or {}
    receipt = video_knowledge_router.select_knowledge(
        project,
        args.block,
        wiki_root=Path(args.wiki_root or video_knowledge_router.DEFAULT_WIKI_ROOT),
        catalog_path=Path(args.catalog or config.get('catalog')) if (args.catalog or config.get('catalog')) else None,
        attributes_path=Path(args.attributes) if args.attributes else None,
        budget_chars=args.budget_chars or int(config.get('budget_chars') or video_knowledge_router.DEFAULT_BUDGET_CHARS),
        max_selections=args.max_selections or int(
            config.get('max_selections') or video_knowledge_router.DEFAULT_MAX_SELECTIONS),
    )
    print(json.dumps({
        'selection_id': receipt['selection_id'],
        'block_id': receipt['block_id'],
        'context': receipt['context'],
        'receipt': receipt['receipt'],
        'context_chars': receipt['context_chars'],
        'selected_ids': [item['id'] for item in receipt['selected']],
        'warnings': receipt['warnings'],
    }, ensure_ascii=False, indent=2))


def lock_duration_cmd(args) -> None:
    project = Path(args.project).expanduser().resolve()
    result = generation_settings.lock_duration(
        project, args.seconds, args.source, block_id=args.block)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == 'author':
        # `video-codex-runtime author set-mode|mode|run ...` → Claude/Codex authoring mode.
        import claude_author
        sys.argv = [sys.argv[0] + ' author'] + sys.argv[2:]
        raise SystemExit(claude_author.main())
    if len(sys.argv) > 1 and sys.argv[1] == 'preprod':
        # `video-codex-runtime preprod <cmd> ...` forwards to the preprod stage tool.
        import preprod
        sys.argv = [sys.argv[0] + ' preprod'] + sys.argv[2:]
        raise SystemExit(preprod.main())
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('init')
    p.add_argument('--slug', default='')
    p.add_argument('--brief', required=True)
    p.add_argument('--mode', choices=GENERATION_MODES, default=STANDARD_I2V_MODE)
    p.add_argument('--no-preprod', dest='preprod', action='store_false',
                   help='legacy rail without the fixed preprod/ stages (new projects use preprod by default)')
    p.add_argument('--author', choices=('claude', 'codex'), default='',
                   help='authoring mode chosen by the user; omit to ask at P0')
    p.set_defaults(func=init_project, preprod=True)

    p = sub.add_parser('set-mode', help='switch future unsubmitted blocks between standard I2V and No-I2V')
    p.add_argument('--project', required=True)
    p.add_argument('--mode', choices=GENERATION_MODES, required=True)
    p.set_defaults(func=set_mode)

    p = sub.add_parser('dispatch')
    p.add_argument('--project', required=True)
    p.add_argument('--lanes', nargs='+', required=True, help='exactly one lane for dispatch; multi-lane aliases are rejected')
    p.add_argument('--force', action='store_true', help='bypass eligible rail gates with a warning; v4 MEDIA_HARD_GATE is never bypassed')
    p.add_argument('--phase', choices=['auto', 'prompting', 'production'], default='auto',
                   help='seedance and image_creator_*: auto picks production (GUI/Aside route) when prompts are ready')
    p.add_argument('--approved-spawn',
                   help='exact current-conversation spawn approval token (not needed under a standing session-policy)')
    p.add_argument('--blocks', nargs='+', help='seedance production: released blocks for this session (default: next 4)')
    p.add_argument('--parallel-browserless', action='store_true',
                   help='disabled 2026-10-24: lane sessions run one at a time machine-wide')
    p.set_defaults(func=dispatch)

    p = sub.add_parser('wait', help='foreground wait for the running lane session; prints its compact session_result')
    p.add_argument('--project', required=True)
    p.add_argument('--lane', required=True, choices=LANES)
    p.add_argument('--timeout-min', type=float, default=10)
    p.set_defaults(func=wait_cmd)

    p = sub.add_parser('session-policy', help='record the user standing approval for director-started lane sessions')
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument('--enable', action='store_true')
    g.add_argument('--disable', action='store_true')
    g.add_argument('--show', action='store_true')
    p.add_argument('--approval-quote', default='')
    p.set_defaults(func=session_policy_cmd)

    p = sub.add_parser('status')
    p.add_argument('--project', required=True)
    p.set_defaults(func=status)

    p = sub.add_parser('kill')
    p.add_argument('--project', required=True)
    p.add_argument('--lanes', nargs='+', required=True)
    p.set_defaults(func=kill)

    p = sub.add_parser('workflow')
    p.set_defaults(func=workflow)

    p = sub.add_parser('model-route', help='show the deterministic lane/phase model policy')
    p.add_argument('--project')
    p.add_argument('--lane', choices=LANES)
    p.add_argument('--phase', choices=['auto', 'prompting', 'production'], default='auto')
    p.set_defaults(func=model_route_cmd)

    p = sub.add_parser('report')
    p.add_argument('--project', required=True)
    p.set_defaults(func=report)

    p = sub.add_parser('dispatch-image-shards', aliases=['prepare-image-batch'], help='prepare immutable image batches for current-owner built-in imagegen; launches no workers')
    p.add_argument('--project', required=True)
    p.add_argument('--lane', default='image_creator_01', choices=['image_creator_01', 'image_creator_02'])
    p.add_argument('--max-parallel', type=int, default=IMAGE_MAX_PARALLEL,
                   help=f'image worker count, hard cap {IMAGE_MAX_PARALLEL}')
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

    p = sub.add_parser('knowledge-select', help='build a token-bounded wiki context packet for one block')
    p.add_argument('--project', required=True)
    p.add_argument('--block', required=True)
    p.add_argument('--attributes')
    p.add_argument('--wiki-root')
    p.add_argument('--catalog')
    p.add_argument('--budget-chars', type=int)
    p.add_argument('--max-selections', type=int)
    p.set_defaults(func=knowledge_select_cmd)

    p = sub.add_parser(
        'lock-duration',
        help='workflow-owned Seedance duration lock; required before prompt attestation')
    p.add_argument('--project', required=True)
    p.add_argument('--seconds', required=True, type=int)
    p.add_argument('--source', required=True)
    p.add_argument('--block', help='optional one-block override; omit for project default')
    p.set_defaults(func=lock_duration_cmd)

    args = ap.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
