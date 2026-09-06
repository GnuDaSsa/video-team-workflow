#!/usr/bin/env python3
"""Shared gate/validation logic for the video-codex-runtime rail.

Single source of truth for:
- STATUS_ENUM: the only machine-readable lane statuses.
- gate_check(project, lane): may this lane start work now?
- validate_project(project): consistency lint for state/manifest/lanes/queues.

Used by video_codex_runtime.py (dispatch / gate / next / validate) and meant
to be callable by lanes themselves before manual work.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import media_registry
import lane_inputs
import generation_settings
from prompt_packet_utils import prompt_sha256

STATUS_ENUM = {
    'PENDING', 'LAUNCHING', 'RUNNING', 'DONE', 'PARTIAL_DONE', 'PARTIAL_BLOCKED',
    'BLOCKED', 'FAILED', 'KILLED', 'NOT_LOCKED', 'LOCKED', 'PASS', 'FAIL',
    'REWORK_ONLY', 'READY_FOR_USER_REVIEW',
    'READY_FOR_PRODUCTION',
}
DONE_LIKE = {'DONE', 'PASS', 'READY_FOR_USER_REVIEW', 'LOCKED', 'PARTIAL_DONE'}

LANES = [
    'director', 'music', 'planner',
    'image_creator_01', 'image_creator_02', 'image_qc',
    'seedance', 'seedance_qc', 'editor', 'package',
]

# Canonical block-ready events for the sequential Codex runtime.
BLOCK_READY_EVENT = 'BLOCK_READY_FOR_SEEDANCE'
LEGACY_BLOCK_READY = (
    'BLOCK_READY_FOR_I2V', 'SEEDANCE_BLOCK_READY', 'IMAGE_REFERENCE_BUNDLE_READY',
)
QUEUES = [
    'intake_queue', 'music_queue', 'planning_queue',
    'image_reference_queue', 'image_retry_queue', 'image_review_queue',
    'reference_bundle_queue',
    'seedance_block_queue', 'seedance_review_queue', 'seedance_retry_queue',
    'edit_queue', 'typography_queue', 'package_qc_queue', 'submission_queue',
    'retry_router_queue',
]


# --- artifact audit (2026-07-28) --------------------------------------------
# Every gate below judges self-reported JSON: a status string, a queue event, or
# a count a lane wrote about itself. Nothing ever looked at a file. `init` creates
# assets/* and then no code reads those folders again — `assets` did not appear
# anywhere in this module.
#
# Result observed in production: the independence-activist project accumulated
# 1.5 GB across 68 ad-hoc session folders under lanes/seedance/ while
# assets/images_approved/ and assets/i2v_clips/ stayed empty, and `validate`
# still returned ok=true. The rail was bypassed with a clean bill of health.
#
# AGENTS.md §1 already states the rule ("완료 인정: 실제 파일 + 검증 증거만"),
# so this is the code catching up to the written contract.

import re as _re_mod
_re_v = _re_mod.compile(r'_v\\d+')

MEDIA_EXT = {'.png', '.jpg', '.jpeg', '.webp', '.mp4', '.mov', '.wav', '.mp3', '.m4a'}
VIDEO_EXT = {'.mp4', '.mov'}
IMAGE_EXT = {'.png', '.jpg', '.jpeg', '.webp'}
# Staging/working areas inside a lane that are expected to hold media in transit.
_TRANSIENT_HINTS = ('upload_staging', 'downloads', 'tmp', '_sweep_trash', 'shards')


def _count_media(d: Path, exts: set[str]) -> int:
    if not d.exists():
        return 0
    return sum(1 for p in d.rglob('*') if p.is_file() and p.suffix.lower() in exts)


def _project_video_count(project: Path) -> int:
    """Videos anywhere in the project. Gates ask 'does media exist at all', not
    'is it filed correctly' — location discipline is validate's job, so a
    mid-project rail cleanup never blocks a lane that genuinely has clips."""
    project = Path(project)
    if media_registry.is_v4_project(project):
        return media_registry.registry_count(
            project, kind='video', states={'approved', 'selected'}
        )
    n = _count_media(project / 'assets', VIDEO_EXT)
    if n:
        return n
    return _count_media(project / 'lanes', VIDEO_EXT)


TERMINAL_STATES = {
    'SHELF_EXHAUSTED',
    'ALL_REMAINING_BLOCKED',
    'BLOCKED_RUNWAY_QUEUE_STALLED',
}
QUEUE_WAIT_STATE = 'QUEUE_FULL_WAITING'
RESUME_CONTRACT_VERSION = 'seedance_foreground_wait_v4_20260819'
QUEUE_RUNTIME_VERSION = 'seedance_queue_runtime_v2_20260819'
SEEDANCE_RECOVERY_VERSION = 'seedance_same_session_recovery_v1_20260810'


def _seedance_recovery(project: Path) -> dict:
    """Read and integrity-check the active same-session recovery controller."""
    raw = _json(Path(project) / 'lanes' / 'seedance' / 'recovery_state.json', {}) or {}
    if not raw:
        return {'present': False, 'valid': False, 'status': None}
    checkpoint = raw.get('checkpoint') or {}
    stored_hash = checkpoint.get('checkpoint_sha256')
    unsigned = {key: value for key, value in checkpoint.items() if key != 'checkpoint_sha256'}
    valid = (
        raw.get('contract_version') == SEEDANCE_RECOVERY_VERSION
        and bool(raw.get('block_id'))
        and raw.get('block_id') == checkpoint.get('block_id')
        and str(checkpoint.get('session_url') or '').startswith('https://app.runwayml.com/')
        and bool(stored_hash)
        and stored_hash == prompt_sha256(json.dumps(
            unsigned, ensure_ascii=False, sort_keys=True, separators=(',', ':')))
    )
    return {
        'present': True,
        'valid': valid,
        'status': str(raw.get('status') or '').upper() or None,
        'block_id': raw.get('block_id'),
        'next_action': raw.get('next_action'),
        'required_user_action': raw.get('required_user_action'),
    }


def _seedance_recovery_needed(project: Path) -> bool:
    recovery = _seedance_recovery(project)
    return bool(
        recovery['present'] and recovery['valid']
        and recovery['status'] == 'RECOVERING'
        and recovery.get('next_action')
    )


def cycle_status(project: Path) -> dict:
    """Is this run legitimately stopped, or did it just trail off?

    Rule sets drift toward halting by omission: every incident adds a "do not",
    nothing adds a "keep going", and eventually stopping is what happens when no
    rule says otherwise. Prose cannot hold that line — the sentence that says
    "then continue" is exactly the one that gets forgotten.

    So the contract is positive: a run ends only by declaring one of
    TERMINAL_STATES in the seedance lane status. A full queue is intermediate:
    it is valid only while queue_runtime records one actually running bounded
    foreground wait process. A timer file or boolean claim cannot re-enter
    Codex reasoning and is not an automatic scheduler.
    """
    project = Path(project)
    st = _json(project / 'lanes' / 'seedance' / 'status.json', {}) or {}
    declared = str(st.get('terminal_state') or '').upper()
    running = str(st.get('status', '')).upper() == 'RUNNING'
    owner_pid_path = project / 'lanes' / 'seedance' / 'pid'
    try:
        owner_pid = int(_read(owner_pid_path).strip()) if owner_pid_path.is_file() else None
    except (TypeError, ValueError):
        owner_pid = None
    owner_alive = _pid_running(owner_pid)

    shelf = 0
    prompts = project / 'lanes' / 'seedance' / 'prompts'
    if prompts.exists():
        shelf = len([p for p in prompts.glob('*_prompt.txt')])
    queued = _queue_has_event(project, 'seedance_block_queue',
                              (BLOCK_READY_EVENT,) + LEGACY_BLOCK_READY)
    recovery = _seedance_recovery(project)

    queue_runtime_path = project / 'lanes' / 'seedance' / 'queue_runtime.json'
    queue_runtime = _json(queue_runtime_path, {}) or {}
    out = {'declared_terminal_state': declared or None, 'lane_running': running,
           'owner_pid': owner_pid, 'owner_alive': owner_alive,
           'staged_prompts': shelf, 'block_ready_events': queued,
           'recovery': recovery,
           'queue_runtime_verdict': queue_runtime.get('verdict'),
           'queue_runtime_active_count': queue_runtime.get('active_count')}

    if running:
        if owner_alive:
            out['verdict'] = 'RECOVERY_ACTIVE' if _seedance_recovery_needed(project) else 'RUNNING'
            return out
        out['verdict'] = 'STOPPED_INCOMPLETE'
        if (queue_runtime.get('contract_version') == QUEUE_RUNTIME_VERSION
                and queue_runtime.get('may_stop') is False):
            out['problem'] = (
                'SEEDANCE_RUNNING_WITHOUT_LIVE_OWNER: status.json says RUNNING but no '
                'lane owner PID is alive while queue_runtime.json says may_stop=false. '
                'A completed foreground wake must continue in the same turn; "next owning '
                'turn" is not a valid pause state.')
        else:
            out['problem'] = (
                'SEEDANCE_RUNNING_WITHOUT_LIVE_OWNER: status.json says RUNNING but no '
                'lane owner PID is alive. Resume with one approved owner or record a '
                'machine-valid terminal state; prose cannot keep a turn alive.')
        return out

    if declared == QUEUE_WAIT_STATE:
        if _seedance_recovery_needed(project):
            out['verdict'] = 'STOPPED_INCOMPLETE'
            out['problem'] = (
                'SEEDANCE_RECOVERY_ABANDONED: finish the machine-actionable same-session '
                'recovery before entering a queue wait.')
            return out
        contract = _json(project / 'lanes' / 'seedance' / 'resume_contract.json', {}) or {}
        wait_instruction = str(contract.get('wait_return_instruction_ko') or '')
        stored_hash = contract.get('contract_sha256')
        unsigned = {key: value for key, value in contract.items() if key != 'contract_sha256'}
        computed_hash = prompt_sha256(json.dumps(
            unsigned, ensure_ascii=False, sort_keys=True, separators=(',', ':')))
        queue_hash = (
            prompt_sha256(queue_runtime_path.read_text(encoding='utf-8'))
            if queue_runtime_path.is_file() else None
        )
        valid_contract = (
            contract.get('contract_version') == RESUME_CONTRACT_VERSION
            and contract.get('delay_seconds') == 900
            and contract.get('same_codex_task_only') is True
            and contract.get('same_runway_browser_only') is True
            and contract.get('continuation_mode') == 'FOREGROUND_TOOL_LONG_POLL_ONLY'
            and contract.get('automatic_model_reentry') is False
            and contract.get('external_scheduler') is False
            and contract.get('additional_agents') == 0
            and contract.get('resident_processes') == 0
            and 1 <= len(wait_instruction) <= 100
            and bool(_re_mod.search(r'[가-힣]', wait_instruction))
            and not any(token in wait_instruction for token in (
                '/Users/', 'state.json', 'manifest.json', '@Image', 'TEST', 'BLOCK_'))
            and stored_hash == computed_hash
            and (contract.get('snapshot') or {}).get('queue_runtime_sha256') == queue_hash
        )
        wake = queue_runtime.get('wake') if isinstance(queue_runtime.get('wake'), dict) else {}
        pending_wake = (
            queue_runtime.get('contract_version') == QUEUE_RUNTIME_VERSION
            and queue_runtime.get('verdict') in {
                'QUEUE_FULL_WAKE_REQUIRED', 'DRAIN_QUEUE_WAKE_REQUIRED'}
            and int(queue_runtime.get('active_count') or 0) > 0
            and wake.get('pending') is True
            and bool(wake.get('due_at'))
            and wake.get('last_result') == 'WAITING_IN_FOREGROUND_TOOL_SESSION'
            and wake.get('elapsed_unconsumed') is False
            and _pid_running(wake.get('wait_pid'))
        )
        out['resume_contract_valid'] = valid_contract
        out['pending_wake_valid'] = pending_wake
        if valid_contract and pending_wake:
            out['verdict'] = 'WAITING_FOREGROUND_TOOL_SESSION'
        else:
            out['verdict'] = 'STOPPED_INCOMPLETE'
            out['problem'] = (
                'QUEUE_FULL_WAITING is intermediate and requires queue_runtime.json with a '
                'live foreground wait_pid plus a matching v4 wait contract. A timer that '
                'already elapsed, next_check_scheduled text, or a contract file cannot wake Codex.')
        return out

    if declared in TERMINAL_STATES:
        out['verdict'] = 'STOPPED_DECLARED'
        if _seedance_recovery_needed(project):
            out['verdict'] = 'STOPPED_INCOMPLETE'
            out['problem'] = (
                'SEEDANCE_RECOVERY_ABANDONED: recovery_state.json still has a machine-actionable '
                f'next step for {recovery.get("block_id")}: {recovery.get("next_action")}. '
                'Resume that same-session recovery before declaring a terminal state.')
            return out
        if (declared == 'ALL_REMAINING_BLOCKED'
                and recovery.get('status') == 'USER_ACTION_REQUIRED'
                and not recovery.get('required_user_action')):
            out['verdict'] = 'STOPPED_INCOMPLETE'
            out['problem'] = (
                'ALL_REMAINING_BLOCKED requires one exact required_user_action for the active '
                'Seedance recovery checkpoint.')
            return out
        if declared in {'SHELF_EXHAUSTED', 'ALL_REMAINING_BLOCKED'}:
            valid_terminal = (
                queue_runtime.get('contract_version') == QUEUE_RUNTIME_VERSION
                and queue_runtime.get('verdict') == declared
                and int(queue_runtime.get('active_count') or 0) == 0
                and not queue_runtime.get('settled_jobs')
                and queue_runtime.get('may_stop') is True
            )
            if not valid_terminal:
                out['verdict'] = 'STOPPED_INCOMPLETE'
                out['problem'] = (
                    f'{declared} is terminal only when queue_runtime confirms no active or '
                    'settled/download-backlog cards remain.')
        elif declared == 'BLOCKED_RUNWAY_QUEUE_STALLED':
            valid_stall = (
                queue_runtime.get('contract_version') == QUEUE_RUNTIME_VERSION
                and queue_runtime.get('verdict') == declared
                and int(queue_runtime.get('unchanged_in_queue_wakes') or 0) >= 3
            )
            if not valid_stall:
                out['verdict'] = 'STOPPED_INCOMPLETE'
                out['problem'] = (
                    'BLOCKED_RUNWAY_QUEUE_STALLED requires three consecutive unchanged '
                    'In queue wake observations in queue_runtime.json.')
        return out
    if (queue_runtime.get('contract_version') == QUEUE_RUNTIME_VERSION
            and queue_runtime.get('may_stop') is False):
        out['verdict'] = 'STOPPED_INCOMPLETE'
        out['problem'] = (
            'SEEDANCE_NONTERMINAL_QUEUE_WITHOUT_LIVE_OWNER: queue_runtime.json '
            f'reports verdict={queue_runtime.get("verdict")}, '
            f'active_count={int(queue_runtime.get("active_count") or 0)}, and '
            'may_stop=false, but no foreground lane owner/wait is alive. Resume '
            'the same queue controller; a future-turn note is not continuation.')
        return out
    if _seedance_recovery_needed(project):
        out['verdict'] = 'STOPPED_INCOMPLETE'
        out['problem'] = (
            'SEEDANCE_RECOVERY_ABANDONED: a recoverable session/upload incident still has '
            f'next_action={recovery.get("next_action")} for {recovery.get("block_id")}. '
            'Resume the same Seedance lane; do not convert it to BLOCKED.')
        return out
    if shelf or queued:
        out['verdict'] = 'STOPPED_INCOMPLETE'
        out['problem'] = (f'lane is not running and declared no terminal state, but work is available '
                          f'({shelf} staged prompt(s), block-ready={queued}). Declare one of '
                          f'{sorted(TERMINAL_STATES)} or resume the cycle.')
        return out
    out['verdict'] = 'IDLE_NO_WORK'
    return out


def audit_artifacts(project: Path) -> dict:
    """Compare what the lanes claim against what is actually on disk."""
    project = Path(project)
    if media_registry.is_v4_project(project):
        result = media_registry.audit_project(project)
        return {
            'problems': result['problems'],
            'warnings': result['warnings'],
            'stats': result['stats'],
        }
    problems, warnings, stats = [], [], {}

    approved_img = _count_media(project / 'assets' / 'images_approved', IMAGE_EXT)
    clips = _count_media(project / 'assets' / 'i2v_clips', VIDEO_EXT)
    stats['assets_images_approved'] = approved_img
    stats['assets_i2v_clips'] = clips

    # Media parked under lanes/ instead of assets/ — the 68-folder scatter.
    scattered, scattered_dirs = 0, {}
    lanes_root = project / 'lanes'
    if lanes_root.exists():
        for p in lanes_root.rglob('*'):
            if not p.is_file() or p.suffix.lower() not in MEDIA_EXT:
                continue
            rel = p.relative_to(lanes_root).as_posix()
            if any(h in rel.lower() for h in _TRANSIENT_HINTS):
                continue
            scattered += 1
            top = rel.split('/')[1] if '/' in rel else rel
            scattered_dirs[top] = scattered_dirs.get(top, 0) + 1
    stats['media_under_lanes'] = scattered
    stats['media_under_lanes_top_dirs'] = dict(sorted(
        scattered_dirs.items(), key=lambda kv: -kv[1])[:8])

    if scattered and (approved_img + clips) == 0:
        problems.append(
            f'RAIL_BYPASSED: {scattered} media files live under lanes/ but assets/images_approved '
            f'and assets/i2v_clips are both empty. Lane output is not reaching the canonical library.')
    elif scattered > max(20, (approved_img + clips) * 2):
        warnings.append(
            f'{scattered} media files under lanes/ vs {approved_img + clips} in assets/ — '
            f'most output is sitting in working folders. Promote finals into assets/.')

    # Claims that no file backs.
    sqc = _json(project / 'lanes' / 'seedance_qc' / 'status.json', {}) or {}
    claimed = int(sqc.get('approved_for_edit_count') or 0)
    stats['seedance_qc_approved_claim'] = claimed
    if claimed > 0 and clips == 0:
        problems.append(
            f'CLAIM_WITHOUT_MEDIA: seedance_qc claims approved_for_edit_count={claimed} '
            f'but assets/i2v_clips holds no video file.')

    # Ordered-library discipline: one library, edited in place.
    lib = project / 'assets' / 'images_approved'
    if lib.exists():
        import re as _re
        seq = _re.compile(r'^(\d{3,4})_')
        nums = [int(seq.match(p.name).group(1)) for p in lib.iterdir()
                if p.is_file() and seq.match(p.name)]
        if nums:
            dupes = sorted({n for n in nums if nums.count(n) > 1})
            gaps = [n for n in range(1, max(nums) + 1) if n not in nums]
            stats['ordered_library_count'] = len(nums)
            if dupes:
                problems.append(f'SEQUENCE_DUPLICATE_SLOTS: {dupes} in assets/images_approved — '
                                f'renumber with sequence_manager.py')
            if gaps:
                warnings.append(f'sequence gaps {gaps[:10]} in assets/images_approved — '
                                f'run sequence_manager.py renumber to re-pack')
    # Sibling "ordered image" folders are how the 68-folder sprawl started.
    rival = []
    for d in (project / 'lanes').rglob('*') if (project / 'lanes').exists() else []:
        n = d.name.lower()
        if d.is_dir() and ('ordered_image' in n or n.startswith('redesign_')
                           or 'restructured' in n or _re_v.search(n)):
            rival.append(str(d.relative_to(project)))
    if rival:
        warnings.append(f'{len(rival)} versioned/ordered image folders under lanes/ '
                        f'(e.g. {rival[0]}) — the ordered library is assets/images_approved, '
                        f'edited in place with sequence_manager.py, not copied to a new folder')
        stats['rival_ordered_folders'] = rival[:5]

    for lane, folder, exts, label in (
        ('image_qc', 'images_approved', IMAGE_EXT, 'approved images'),
        ('seedance_qc', 'i2v_clips', VIDEO_EXT, 'video clips'),
    ):
        if lane_status(project, lane)['status'] in DONE_LIKE and \
                _count_media(project / 'assets' / folder, exts) == 0:
            warnings.append(f'{lane} is DONE-like but assets/{folder} has no {label}.')

    return {'problems': problems, 'warnings': warnings, 'stats': stats}


def _read(p: Path) -> str:
    try:
        return p.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return ''


def _json(p: Path, default=None):
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except Exception:
        return default


def lane_status(project: Path, lane: str) -> dict:
    """Return {'status': <enum or UNKNOWN>, 'raw': <raw value>, 'detail': ...}."""
    s = _json(project / 'lanes' / lane / 'status.json', {}) or {}
    raw = str(s.get('status', 'PENDING'))
    norm = raw.strip().upper()
    if norm in STATUS_ENUM:
        return {'status': norm, 'raw': raw, 'detail': s.get('detail'), 'meta': s}
    # Heuristic salvage for legacy free-form values.
    guess = 'UNKNOWN'
    if 'BLOCK' in norm:
        guess = 'BLOCKED'
    elif 'DONE' in norm or 'PASS' in norm or 'READY' in norm or 'LOCKED' in norm:
        guess = 'PARTIAL_DONE'
    elif 'PROGRESS' in norm or 'RUNNING' in norm or 'GENERATING' in norm:
        guess = 'RUNNING'
    return {'status': guess, 'raw': raw, 'detail': s.get('detail') or raw, 'meta': s}


def _queue_has_event(project: Path, queue: str, events: tuple[str, ...]) -> bool:
    txt = _read(project / 'queues' / f'{queue}.jsonl')
    return any(e in txt for e in events)


def _lane_pid(project: Path, lane: str) -> int | None:
    txt = _read(project / 'lanes' / lane / 'pid').strip()
    if not txt:
        return None
    try:
        return int(txt)
    except ValueError:
        return None


def _pid_running(pid: int | None) -> bool:
    if not pid:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def lane_process_running(project: Path, lane: str) -> bool:
    return _pid_running(_lane_pid(project, lane))


def _seedance_resume_needed(project: Path) -> bool:
    info = lane_status(project, 'seedance')
    if info['status'] != 'RUNNING':
        return False
    if lane_process_running(project, 'seedance'):
        return False
    meta = info.get('meta') or {}
    submit_record = str(meta.get('submit_success_record') or '')
    haystack = ' '.join(
        str(meta.get(key) or '')
        for key in ('reason', 'detail', 'active_runway_state', 'next_required', 'submit_success_record')
    ).lower()
    inflight_markers = (
        'in queue', 'generating', 'poll runway', 'submit_success',
        'submitted', 'visible in queue',
    )
    if any(marker in haystack for marker in inflight_markers):
        return True

    if submit_record:
        record_path = Path(submit_record).expanduser()
        if record_path.exists():
            record_text = _read(record_path).lower()
            if any(marker in record_text for marker in inflight_markers):
                return True

    evidence_tail = _read(project / 'lanes' / 'seedance' / 'ui_evidence.jsonl')[-20000:].lower()
    evidence_markers = (
        'submitted_hidden_success_visible_in_queue', 'submitted_visible_in_queue',
        'in queue', 'generating',
    )
    return any(marker in evidence_tail for marker in evidence_markers)


# Gate strength. HARD = block dispatch (these existed before 2026-07-03 and
# match the original runtime behavior). SOFT = newly added ordering checks:
# warn + record, but NEVER block, so previously-working free dispatch flows
# keep working exactly as before.
HARD_GATES = {'seedance', 'seedance_qc', 'editor', 'package'}


def gate_level(lane: str) -> str:
    return 'hard' if lane in HARD_GATES else 'soft'


def non_bypassable_reason(project: Path, reason: str) -> bool:
    """V4 media gates cannot be converted to warnings or bypassed by --force."""
    return media_registry.is_v4_project(Path(project)) and reason.startswith('MEDIA_HARD_GATE:')


def gate_check(project: Path, lane: str) -> tuple[bool, str]:
    """Return (ok, reason). Reason explains what is missing when not ok.

    Enforced everywhere (dispatch, `gate`, `next`, and lanes before manual work).
    """
    project = Path(project)
    st = lambda l: lane_status(project, l)['status']  # noqa: E731

    if media_registry.is_v4_project(project):
        audit = media_registry.audit_project(project)
        if audit['problems']:
            return False, 'MEDIA_HARD_GATE: ' + audit['problems'][0]

    if lane == 'director':
        return True, 'OK: director is the entry lane.'
    if lane == 'music':
        if st('director') in DONE_LIKE:
            return True, 'OK'
        return False, 'WAIT_DIRECTOR: music starts after director locks direction/safety gates (music_first rail).'
    if lane == 'planner':
        if media_registry.is_v4_project(project):
            problem = lane_inputs.music_error(project, _json(project / 'manifest.json', {}) or {})
            return (False, 'MEDIA_HARD_GATE: ' + problem) if problem else (True, 'OK')
        music = (_json(project / 'manifest.json', {}) or {}).get('music', {})
        if st('music') in DONE_LIKE or music.get('status') == 'LOCKED':
            return True, 'OK'
        return False, 'WAIT_MUSIC_LOCK: planner needs Music Lock (manifest.music.status=LOCKED or music lane DONE).'
    if lane in ('image_creator_01', 'image_creator_02'):
        if media_registry.is_v4_project(project):
            problem = lane_inputs.planner_error(project)
            return (False, 'MEDIA_HARD_GATE: ' + problem) if problem else (True, 'OK')
        if st('planner') in DONE_LIKE or (project / 'lanes' / 'planner' / 'multi_reference_block_map.json').exists():
            return True, 'OK'
        return False, 'WAIT_PLANNER: image creators need the cut/block map from planner.'
    if lane == 'image_qc':
        manifest = _json(project / 'manifest.json', {}) or {}
        no_i2v = manifest.get('generation_mode') == 'no_i2v_reference_native'
        if media_registry.is_v4_project(project):
            candidate_count = media_registry.registry_count(
                project, kind='image', states={'candidate'})
            approved_count = media_registry.registry_count(
                project, kind='image', states={'approved', 'selected'})
            if candidate_count <= 0 and not (no_i2v and approved_count > 0):
                return False, (
                    'MEDIA_HARD_GATE: image_qc requires a registered image candidate, '
                    'or in No-I2V mode an already approved reusable reference.'
                )
        return True, 'OK: image_qc watches image_review_queue.'
    if lane == 'seedance':
        recovery = _seedance_recovery(project)
        if recovery.get('valid') and recovery.get('status') == 'USER_ACTION_REQUIRED':
            return False, (
                'WAIT_SEEDANCE_USER_ACTION: '
                f'{recovery.get("required_user_action") or "exact user action is missing"}')
        if _seedance_recovery_needed(project):
            return True, (
                'RESUME_SEEDANCE_RECOVERY: restore the exact same Aside/Runway transaction '
                f'for {recovery.get("block_id")} and execute {recovery.get("next_action")}. '
                'Do not create a new session or consume an attachment attempt for transport failure.')
        if _seedance_resume_needed(project):
            return True, ('RESUME_SEEDANCE_INFLIGHT: a submitted Runway job is queued/generating; '
                          'relaunch the same Seedance lane. Do not start a detached monitor.')
        duration_errors, _duration_lock = generation_settings.validate_duration_lock(project)
        if duration_errors:
            return False, (
                'DURATION_LOCK_REQUIRED: Planner/project workflow must lock generation duration '
                'before any new Seedance prompt attestation or submission: ' + duration_errors[0])
        if media_registry.is_v4_project(project) and media_registry.registry_count(
                project, kind='image', states={'approved', 'selected'}) <= 0:
            return False, 'MEDIA_HARD_GATE: Seedance requires registered approved images.'
        if _queue_has_event(project, 'seedance_block_queue', (BLOCK_READY_EVENT,) + LEGACY_BLOCK_READY):
            return True, 'OK'
        return False, ('WAIT_BLOCK_READY: no %s event in seedance_block_queue (Image QC has not approved a full '
                       'reference bundle for any block).' % BLOCK_READY_EVENT)
    if lane == 'seedance_qc':
        if media_registry.is_v4_project(project) and media_registry.registry_count(
                project, kind='video', states={'candidate'}) <= 0:
            return False, 'MEDIA_HARD_GATE: seedance_qc requires a registered downloaded video candidate.'
        if _read(project / 'queues' / 'seedance_review_queue.jsonl').strip():
            return True, 'OK'
        return False, 'WAIT_SEEDANCE_OUTPUT: no Seedance review/output event.'
    if lane == 'editor':
        sqc = _json(project / 'lanes' / 'seedance_qc' / 'status.json', {}) or {}
        claimed = int(sqc.get('approved_for_edit_count') or 0)
        if claimed <= 0:
            return False, 'WAIT_SEEDANCE_QC_PASS: no approved video clips (seedance_qc.approved_for_edit_count == 0).'
        # The count is a lane's claim about itself. Require real video behind it —
        # AGENTS.md §1: completion is real files, never a status field.
        if _project_video_count(project) == 0:
            return False, ('CLAIM_WITHOUT_MEDIA: seedance_qc claims %d approved clips but no video file '
                           'exists in the project. Download and verify the clips before editing.' % claimed)
        return True, 'OK'
    if lane == 'package':
        if lane_status(project, 'editor')['status'] not in {'DONE', 'READY_FOR_USER_REVIEW', 'PASS'}:
            return False, 'WAIT_EDITOR_DONE: package starts after editor status DONE/READY_FOR_USER_REVIEW/PASS.'
        if _project_video_count(project) == 0:
            return False, ('CLAIM_WITHOUT_MEDIA: editor reports done but the project contains no video file. '
                           'A package cannot be assembled from status fields alone.')
        if media_registry.is_v4_project(project) and media_registry.registry_count(
                project, kind='final', states={'final', 'approved', 'selected'}) <= 0:
            return False, 'MEDIA_HARD_GATE: package requires a registered final export in media/09_final_최종본.'
        return True, 'OK'
    return False, f'unknown lane {lane}'


def next_actions(project: Path) -> dict:
    """Compute the current rail position: per-lane view + suggested next lanes + user actions."""
    project = Path(project)
    lanes = {}
    next_lanes, user_actions = [], []
    for lane in LANES:
        info = lane_status(project, lane)
        ok, reason = gate_check(project, lane)
        lanes[lane] = {'status': info['status'], 'raw': info['raw'], 'gate_ok': ok, 'gate_reason': reason}
        recovery_restart = lane == 'seedance' and _seedance_recovery_needed(project)
        recovery = _seedance_recovery(project) if lane == 'seedance' else {}
        recovery_user_action = bool(
            recovery.get('valid') and recovery.get('status') == 'USER_ACTION_REQUIRED')
        if recovery_user_action:
            user_actions.append({
                'lane': lane,
                'detail': recovery.get('required_user_action') or 'exact user action is missing',
            })
        elif info['status'] == 'BLOCKED' and not recovery_restart:
            user_actions.append({'lane': lane, 'detail': info.get('detail') or info['raw']})
        resume_restart = lane == 'seedance' and (
            recovery_restart or (info['status'] == 'RUNNING' and _seedance_resume_needed(project)))
        if ok and (resume_restart or info['status'] in {
                'PENDING', 'UNKNOWN', 'NOT_LOCKED', 'PARTIAL_BLOCKED', 'FAILED',
                'REWORK_ONLY', 'READY_FOR_PRODUCTION'}):
            next_lanes.append(lane)
    phase = (_json(project / 'manifest.json', {}) or {}).get('project_phase')
    return {'project': str(project), 'phase': phase, 'lanes': lanes,
            'next_lanes': next_lanes, 'user_actions_required': user_actions}


def validate_project(project: Path) -> dict:
    """Lint the project: JSON validity, status enum compliance, queue registration."""
    project = Path(project)
    problems, warnings = [], []
    for name in ['state.json', 'manifest.json']:
        if _json(project / name) is None:
            problems.append(f'{name}: missing or invalid JSON')
    for lane in LANES:
        sp = project / 'lanes' / lane / 'status.json'
        if not sp.exists():
            continue
        s = _json(sp)
        if s is None:
            problems.append(f'lanes/{lane}/status.json: invalid JSON')
            continue
        raw = str(s.get('status', ''))
        if raw and raw.strip().upper() not in STATUS_ENUM:
            problems.append(f'lanes/{lane}/status.json: non-enum status "{raw}" (move free text to "detail")')
    qdir = project / 'queues'
    if qdir.exists():
        for q in qdir.glob('*.jsonl'):
            if q.stem not in QUEUES and not q.stem.startswith('operator_events') and q.stem not in {'grok_review_queue'}:
                warnings.append(f'queues/{q.name}: not in canonical QUEUES registry')
            for i, line in enumerate(_read(q).splitlines(), 1):
                if line.strip():
                    try:
                        json.loads(line)
                    except Exception:
                        problems.append(f'queues/{q.name}:{i}: invalid JSONL line')
                        break
    manifest = _json(project / 'manifest.json', {}) or {}
    for q in QUEUES:
        if q not in (manifest.get('queues') or {}):
            warnings.append(f'manifest.queues missing registration: {q}')
    art = audit_artifacts(project)
    problems.extend(art['problems'])
    warnings.extend(art['warnings'])
    recovery = _seedance_recovery(project)
    if recovery['present'] and not recovery['valid']:
        problems.append(
            'SEEDANCE_RECOVERY_CHECKPOINT_INVALID: recovery_state.json version, session URL, '
            'block identity, or checkpoint hash does not validate.')
    duration_required = (
        lane_status(project, 'planner')['status'] in DONE_LIKE
        or (project / 'lanes' / 'seedance' / 'prompts').exists()
        or _queue_has_event(
            project, 'seedance_block_queue', (BLOCK_READY_EVENT,) + LEGACY_BLOCK_READY)
    )
    if duration_required:
        duration_errors, _duration_lock = generation_settings.validate_duration_lock(project)
        problems.extend(duration_errors)
    cyc = cycle_status(project)
    if cyc.get('problem'):
        problems.append(cyc['problem'])
    if media_registry.is_v4_project(project):
        for pid_name in ('monitor.pid', 'watch_generate.pid'):
            pid_text = _read(project / 'lanes' / 'seedance' / pid_name).strip()
            try:
                pid = int(pid_text) if pid_text else None
            except ValueError:
                pid = None
            if _pid_running(pid):
                problems.append(
                    f'DETACHED_SEEDANCE_MONITOR_FORBIDDEN: {pid_name} pid={pid}; '
                    'v4 uses one bounded foreground wait, not a resident process or scheduler.'
                )
    return {'project': str(project), 'ok': not problems, 'problems': problems,
            'warnings': warnings, 'artifacts': art['stats'], 'cycle': cyc}
