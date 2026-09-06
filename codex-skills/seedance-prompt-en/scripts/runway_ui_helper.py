#!/usr/bin/env python3
"""Canonical Seedance/Runway UI and same-session recovery helper.

Ownership lives with the global ``seedance-prompt-en`` skill, not with any one
video-team runtime. A runtime may expose a thin compatibility shim, but must not
fork or restate this implementation.

Targets the one visible Aside tab that holds the Runway board. Aside is the
only production browser owner; Chrome, Safari, the Codex in-app browser, and
connector/API routes are not fallbacks. All JS goes through browser_js().

Agents must NOT hand-roll osascript for clipboard/keystroke/picker work. DOM operations use the exact bound tab through Aside CLI.
Only permitted native picker/key helpers use frontmost-verified AppleScript.

Commands:
  frontmost                              print frontmost app
  escape                                 send ESC to the Runway browser (verified)
  prepare-upload-alias --project P       make one temporary ASCII symlink for a registry asset
                       --asset-id A --block-id B [--slot N]
  cleanup-upload-alias --path P          remove only a helper-owned temporary upload symlink
  paste-prompt --file F [--replace]      Korean-validated Lexical paste + exact content/hash check
  picker-go    --path P                  verified file-picker sheet -> Cmd+Shift+G -> path -> Return
  recovery-checkpoint --project P        persist the same-session transaction before ATTACH
  recovery-record --project P            classify an incident and return the next fixed recovery rung
  recovery-resolve --project P           record recovery success and resume from the checkpoint
  queue-sync --project P                 persist the visible queue and compute the mandatory next action
  queue-cycle --project P                sync once and immediately hold when the reducer requires a wait
  queue-wait --project P                 hold one bounded 15-minute foreground tool session
  queue-exit-check --project P           refuse a final response while the queue cycle is nonterminal
  queue-doctor --project P               read-only wait/receipt diagnosis; never starts monitoring
  queue-mode --project P --mode scheduled --request-evidence F   persist intent, never register a scheduler
  resume-contract --project P            write state for that foreground wait; never schedules Codex
  recover                                focus-pollution ritual step: ESC + frontmost report

Common flags: --evidence <jsonl path> --state <label>  (evidence line per command)
Exit codes: 0 ok, 2 focus-abort, 3 control error.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sqlite3
import subprocess
import sys
import time
import unicodedata
from pathlib import Path
from urllib.parse import urlparse

# Registry-backed commands integrate with the canonical video-team runtime when
# a v4 project is supplied. Keeping this dependency path explicit lets the
# Seedance skill own UI/recovery procedure while the runtime continues to own
# project media validation and Korean prompt attestation.
VIDEO_TEAM_RUNTIME_SCRIPTS = Path(os.environ.get(
    'VIDEO_TEAM_RUNTIME_SCRIPTS',
    '/Users/gnudas/Documents/Codex/video-team-runtime/runtime/scripts',
)).expanduser().resolve()
if str(VIDEO_TEAM_RUNTIME_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(VIDEO_TEAM_RUNTIME_SCRIPTS))

sys.path.insert(0, str(Path(__file__).resolve().parent))
import aside_bridge
import media_registry
import generation_settings
from prompt_packet_utils import language_stats, normalize_prompt, prompt_sha256, validate_seedance


UPLOAD_ALIAS_ROOT = Path(os.environ.get('RUNWAY_UPLOAD_ALIAS_ROOT', '/tmp/codex-runway-upload'))
UPLOAD_ALIAS_MAX_AGE_SECONDS = 3600

RECOVERY_CONTRACT_VERSION = 'seedance_same_session_recovery_v1_20260810'
RECOVERY_STATE_REL = Path('lanes/seedance/recovery_state.json')
RECOVERY_EVENT_REL = Path('lanes/seedance/recovery_events.jsonl')
REQUIRED_GENERATION_MODEL = 'Seedance 2.0'

# Transport incidents mean that the control surface failed before Runway could
# semantically accept or reject an attachment. They must never consume the
# attachment retry budget. That distinction is the core of the recovery loop:
# two raw tool timeouts are not two bad uploads.
SESSION_TRANSPORT_INCIDENTS = {
    'SESSION_CONTROL_TIMEOUT',
    'SESSION_TAB_NOT_FOUND',
    'SESSION_CLAIM_RESET',
    'ASIDE_CONTROL_UNAVAILABLE',
    'RUNWAY_UI_STALE',
    'SESSION_DISCONNECTED',
}
UPLOAD_TRANSPORT_INCIDENTS = {
    'NATIVE_CHOOSER_TIMEOUT',
    'NATIVE_CHOOSER_UNAVAILABLE',
    'FILE_PICKER_NOT_EXPOSED',
    'UPLOAD_CONTROL_TIMEOUT',
}
UPLOAD_SEMANTIC_INCIDENTS = {
    'WRONG_REFERENCE_VISIBLE',
    'UPLOAD_MISSING_AFTER_OPEN',
    'UPLOAD_100_PERCENT_STALLED',
    'UPLOAD_PROVIDER_REJECTED',
}
HUMAN_ACTION_INCIDENTS = {
    'LOGIN_REQUIRED',
    'CAPTCHA_REQUIRED',
    'PAYMENT_REQUIRED',
    'ACCOUNT_LIMIT',
    'ASIDE_FILE_UPLOAD_ACCESS_REQUIRED',
    'OS_PERMISSION_REQUIRED',
}
RECOVERY_INCIDENTS = (
    SESSION_TRANSPORT_INCIDENTS
    | UPLOAD_TRANSPORT_INCIDENTS
    | UPLOAD_SEMANTIC_INCIDENTS
    | HUMAN_ACTION_INCIDENTS
)

SAME_SESSION_RECOVERY_LADDER = (
    'RE_READ_EXISTING_ASIDE_RUNWAY_TAB',
    'REDISCOVER_AND_RECLAIM_EXACT_SAME_SESSION_URL',
    'REFRESH_EXACT_SAME_SESSION_AND_POLL_5S_X12',
    'SWITCH_OWNER_TOOL_ON_SAME_ASIDE_TAB_ONCE',
)


def normalize_visible_seedance_model(value: str) -> str:
    """Return one unambiguous Seedance model from visible Runway text."""
    text = re.sub(r'\s+', ' ', str(value or '')).strip()
    versions = {
        f'Seedance 2.{suffix}'
        for suffix in re.findall(r'(?i)seedance\s*2\.([05])', text)
    }
    if len(versions) != 1:
        raise ValueError(
            'SETTINGS_VISIBLE_MODEL_UNREADABLE_OR_AMBIGUOUS: '
            f'expected one visible Seedance 2.0/2.5 label, got {value!r}')
    return next(iter(versions))


def require_seedance_20(value: str, *, error_prefix: str = 'SETTINGS') -> str:
    """Fail closed unless the freshly read visible model is Seedance 2.0."""
    visible_model = normalize_visible_seedance_model(value)
    if visible_model != REQUIRED_GENERATION_MODEL:
        raise ValueError(
            f'{error_prefix}_VISIBLE_MODEL_MISMATCH: '
            f'expected={REQUIRED_GENERATION_MODEL},visible={visible_model}; '
            'select Seedance 2.0, close the model menu, re-read the visible '
            'label, and rerun settings-verify before Generate')
    return visible_model

def osa(script: str) -> tuple[int, str, str]:
    p = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, timeout=60)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


# --- browser targeting: exact project-bound Aside CLI tab -------------------
RUNWAY_HOST = 'app.runwayml.com'


def resolve_target_app() -> str:
    forced = os.environ.get('RUNWAY_BROWSER')
    if forced and forced != 'Aside':
        raise SystemExit(f'ASIDE_ONLY_RUNWAY_OWNER: RUNWAY_BROWSER={forced!r}; use Aside')
    return 'Aside'


TARGET_APP = resolve_target_app()


def browser_js(js: str) -> tuple[int, str, str]:
    """CLI/repl only; rejects missing binding or session drift before DOM access."""
    return aside_bridge.browser_js(js)


# --- input-method guard ----------------------------------------------------
# macOS routes System Events keystrokes through the active input method. With a
# CJK IME selected, "ZZTEST123" arrives as Hangul fragments and Cmd+V loses its
# modifier and types a literal character — silently. That is how a 3,201-char
# prompt ended up with zero Hangul while every step reported success.
#
# Silent corruption is the worst failure mode available, so any keystroke path
# stops here instead. paste-prompt does not use keystrokes and is unaffected.
# (2026-07-31)

CJK_IME_MARKERS = ('Korean', 'Japanese', 'SCIM', 'TCIM', 'TYIM', 'Chinese', 'Pinyin', 'Zhuyin')


def ime_state() -> dict:
    rc, out, _ = osa('do shell script "defaults read com.apple.HIToolbox AppleSelectedInputSources"')
    if rc != 0:
        return {'readable': False, 'cjk_active': False, 'raw': ''}
    tail = out[-1200:]
    hit = next((m for m in CJK_IME_MARKERS if m.lower() in tail.lower()), None)
    mode = ''
    for line in tail.splitlines():
        if '"Input Mode"' in line or '"KeyboardLayout Name"' in line:
            v = line.split('=', 1)[-1].strip().strip('";, ')
            if v and v not in ('Input Mode', 'KeyboardLayout Name'):
                mode = v
    return {'readable': True, 'cjk_active': bool(hit), 'marker': hit, 'input_mode': mode}


IME_REMEDY = ('BLOCKED_IME_ACTIVE — a CJK input method is selected, so synthetic keystrokes '
              'would be mangled (Cmd+V loses its modifier; typed text becomes jamo). '
              'Either switch the input source to ABC/English for this operation, or use a '
              'route that sends no keystrokes: `paste-prompt --file F [--replace]` for prompt '
              'text. Do not retry the keystroke path while a CJK IME is active.')


def cmd_ime_check(args) -> int:
    st = ime_state()
    st['verdict'] = 'CJK_IME_ACTIVE_KEYSTROKES_UNSAFE' if st['cjk_active'] else 'OK_KEYSTROKES_SAFE'
    if st['cjk_active']:
        st['required_action'] = IME_REMEDY
    evidence(args, 'ime-check', 'input source safe for keystrokes',
             json.dumps(st, ensure_ascii=False), st['verdict'])
    print(json.dumps(st, ensure_ascii=False))
    return 1 if st['cjk_active'] else 0


def evidence(args, action: str, expected: str, observed: str, verdict: str) -> None:
    row = {'ts': dt.datetime.now().isoformat(timespec='seconds'), 'tool': 'runway_ui_helper',
           'state': getattr(args, 'state', None), 'action': action,
           'expected': expected, 'observed': observed, 'verdict': verdict}
    print(json.dumps(row, ensure_ascii=False))
    ev = getattr(args, 'evidence', None)
    if ev:
        p = Path(ev).expanduser()
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open('a', encoding='utf-8') as f:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')


def _ascii_token(value: str, fallback: str) -> str:
    token = re.sub(r'[^A-Za-z0-9_-]+', '_', value).strip('_')
    return token[:48] or fallback


def sweep_stale_upload_aliases(root: Path = UPLOAD_ALIAS_ROOT,
                               max_age_seconds: int = UPLOAD_ALIAS_MAX_AGE_SECONDS) -> list[str]:
    """Remove only stale helper-owned symlinks; never touch canonical media."""
    if not root.exists():
        return []
    cutoff = time.time() - max_age_seconds
    removed = []
    for path in root.iterdir():
        try:
            if path.is_symlink() and path.lstat().st_mtime <= cutoff:
                path.unlink()
                removed.append(str(path))
        except FileNotFoundError:
            continue
    return removed


def prepare_upload_alias(project: Path, asset_id: str, block_id: str,
                         slot: int = 1, root: Path = UPLOAD_ALIAS_ROOT,
                         modality: str = 'Image') -> dict:
    """Create a short-lived ASCII symlink to one approved registry asset.

    This avoids copied media in Downloads/chat work folders and gives the native
    chooser a unique ASCII filename. The alias is not a second asset and must be
    removed immediately after the visible Runway thumbnail is verified.
    """
    project = project.expanduser().resolve()
    if not media_registry.is_v4_project(project):
        raise ValueError(f'MEDIA_V4_REQUIRED: {project}')
    asset = media_registry.get_asset(project, asset_id)
    modality = modality.title()
    allowed_kinds = {
        'Image': {'image', 'character'},
        'Video': {'video'},
        'Audio': {'audio'},
    }
    if modality not in allowed_kinds:
        raise ValueError(f'UPLOAD_ALIAS_MODALITY_NOT_ALLOWED: {modality}')
    if asset['kind'] not in allowed_kinds[modality]:
        raise ValueError(
            f'UPLOAD_ALIAS_KIND_NOT_ALLOWED: {modality}{int(slot)}={asset["kind"]}')
    if asset['state'] not in {'approved', 'selected', 'source', 'locked'} or not asset['active']:
        raise ValueError(f'UPLOAD_ALIAS_ASSET_NOT_ACTIVE_APPROVED: {asset_id}:{asset["state"]}')
    source = Path(asset['current_path'])
    if not source.is_file() or media_registry.sha256(source) != asset['sha256']:
        raise ValueError(f'UPLOAD_ALIAS_SOURCE_INVALID: {asset_id}')
    root.mkdir(parents=True, exist_ok=True)
    os.chmod(root, 0o700)
    sweep_stale_upload_aliases(root)
    block = _ascii_token(block_id, 'BLOCK')
    suffix = source.suffix.lower()
    reference_token = f'{modality}{int(slot)}'
    alias = root / f'{block}__{reference_token.upper()}__{asset_id[-8:]}{suffix}'
    if alias.exists() or alias.is_symlink():
        alias.unlink()
    alias.symlink_to(source)
    return {
        'alias_path': str(alias),
        'alias_name': alias.name,
        'canonical_path': str(source),
        'asset_id': asset_id,
        'block_id': block_id,
        'slot': int(slot),
        'reference_token': reference_token,
        'modality': modality,
        'sha256': asset['sha256'],
        'cleanup_required_after_thumbnail_verification': True,
    }


def cleanup_upload_alias(path: Path, root: Path = UPLOAD_ALIAS_ROOT) -> dict:
    root = Path(os.path.abspath(root.expanduser()))
    candidate = path.expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    candidate = Path(os.path.abspath(candidate))
    if candidate.parent != root:
        raise ValueError(f'UPLOAD_ALIAS_OUTSIDE_HELPER_ROOT: {candidate}')
    if not candidate.is_symlink():
        raise ValueError(f'UPLOAD_ALIAS_NOT_SYMLINK: {candidate}')
    candidate.unlink()
    return {'removed': True, 'alias_path': str(candidate)}


# --- same-session recovery controller --------------------------------------

def _recovery_state_path(project: Path) -> Path:
    return project.expanduser().resolve() / RECOVERY_STATE_REL


def _recovery_event_path(project: Path) -> Path:
    return project.expanduser().resolve() / RECOVERY_EVENT_REL


def _safe_block_token(block_id: str) -> str:
    return _ascii_token(block_id, 'BLOCK')


def _hash_payload(value: dict) -> str:
    return prompt_sha256(json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(',', ':')))


def _valid_sha256(value: str | None) -> bool:
    return not value or bool(re.fullmatch(r'[0-9a-fA-F]{64}', value))


def _validate_runway_session_url(session_url: str) -> str:
    parsed = urlparse(session_url)
    if parsed.scheme != 'https' or parsed.hostname != RUNWAY_HOST:
        raise ValueError(
            f'RECOVERY_REQUIRES_EXACT_RUNWAY_SESSION_URL: expected https://{RUNWAY_HOST}/..., '
            f'got {session_url!r}')
    return session_url


def _parse_reference_arg(value: str) -> tuple[str, str]:
    if '=' not in value:
        raise ValueError(f'REFERENCE_FORMAT_REQUIRED: use ImageN|VideoN|AudioN=AST_..., got {value!r}')
    slot, asset_id = (part.strip() for part in value.split('=', 1))
    if not re.fullmatch(r'(Image|Video|Audio)[1-9][0-9]*', slot):
        raise ValueError(f'REFERENCE_SLOT_INVALID: {slot!r}')
    if not asset_id:
        raise ValueError(f'REFERENCE_ASSET_ID_MISSING: {value!r}')
    return slot, asset_id


def _registered_reference(project: Path, slot: str, asset_id: str) -> dict:
    asset = media_registry.get_asset(project, asset_id)
    modality = re.match(r'(Image|Video|Audio)', slot)
    allowed_kinds = {
        'Image': {'image', 'character'},
        'Video': {'video'},
        'Audio': {'audio'},
    }
    if modality is None or asset['kind'] not in allowed_kinds[modality.group(1)]:
        raise ValueError(f'RECOVERY_REFERENCE_KIND_NOT_ALLOWED: {slot}={asset_id}:{asset["kind"]}')
    if asset['state'] not in {'approved', 'selected', 'source', 'locked'} or not asset['active']:
        raise ValueError(f'RECOVERY_REFERENCE_NOT_ACTIVE_APPROVED: {slot}={asset_id}:{asset["state"]}')
    path = Path(asset['current_path'])
    if not path.is_file() or media_registry.sha256(path) != asset['sha256']:
        raise ValueError(f'RECOVERY_REFERENCE_FILE_INVALID: {slot}={asset_id}')
    return {
        'slot': slot,
        'asset_id': asset_id,
        'kind': asset['kind'],
        'path': str(path),
        'sha256': asset['sha256'],
    }


def _load_recovery_state(
    project: Path,
    block_id: str | None = None,
    *,
    validate_settings_model: bool = True,
) -> dict:
    path = _recovery_state_path(project)
    try:
        state = json.loads(path.read_text(encoding='utf-8'))
    except FileNotFoundError as exc:
        raise ValueError(f'RECOVERY_CHECKPOINT_MISSING: {path}') from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f'RECOVERY_CHECKPOINT_INVALID_JSON: {path}') from exc
    if not isinstance(state, dict):
        raise ValueError(f'RECOVERY_CHECKPOINT_INVALID_OBJECT: {path}')
    if state.get('contract_version') != RECOVERY_CONTRACT_VERSION:
        raise ValueError(f'RECOVERY_CHECKPOINT_VERSION_MISMATCH: {state.get("contract_version")}')
    if block_id and state.get('block_id') != block_id:
        raise ValueError(
            f'RECOVERY_BLOCK_MISMATCH: active={state.get("block_id")} requested={block_id}')
    checkpoint = state.get('checkpoint') or {}
    expected_hash = checkpoint.get('checkpoint_sha256')
    unsigned = {key: value for key, value in checkpoint.items() if key != 'checkpoint_sha256'}
    if not expected_hash or expected_hash != _hash_payload(unsigned):
        raise ValueError('RECOVERY_CHECKPOINT_HASH_MISMATCH')
    if validate_settings_model:
        settings = checkpoint.get('settings') or {}
        if not settings.get('model'):
            raise ValueError(
                'RECOVERY_SETTINGS_MODEL_REQUIRED: rebuild the checkpoint from '
                'the current visible Seedance 2.0 setting')
        require_seedance_20(
            str(settings['model']), error_prefix='RECOVERY_SETTINGS')
    return state


def _write_recovery_state(project: Path, state: dict, event: dict) -> dict:
    project = project.expanduser().resolve()
    now = dt.datetime.now().astimezone().isoformat(timespec='seconds')
    state['updated_at'] = now
    state_path = _recovery_state_path(project)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    history_path = state_path.parent / 'recovery' / f'{_safe_block_token(str(state["block_id"]))}.json'
    history_path.parent.mkdir(parents=True, exist_ok=True)
    history_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    event_row = {
        'ts': now,
        'contract_version': RECOVERY_CONTRACT_VERSION,
        'block_id': state['block_id'],
        **event,
    }
    event_path = _recovery_event_path(project)
    with event_path.open('a', encoding='utf-8') as handle:
        handle.write(json.dumps(event_row, ensure_ascii=False) + '\n')
    return state


def create_recovery_checkpoint(
    project: Path,
    block_id: str,
    session_url: str,
    phase: str,
    *,
    session_id: str = '',
    prompt_sha256_value: str = '',
    reference_manifest_sha256: str = '',
    references: list[tuple[str, str]] | None = None,
    verified_slots: list[str] | None = None,
    settings: dict | None = None,
) -> dict:
    """Persist enough identity to recover the same transaction after UI loss."""
    project = project.expanduser().resolve()
    if not media_registry.is_v4_project(project):
        raise ValueError(f'MEDIA_V4_REQUIRED: {project}')
    if not block_id.strip():
        raise ValueError('RECOVERY_BLOCK_ID_REQUIRED')
    _validate_runway_session_url(session_url)
    if not _valid_sha256(prompt_sha256_value):
        raise ValueError('RECOVERY_PROMPT_SHA256_INVALID')
    if not _valid_sha256(reference_manifest_sha256):
        raise ValueError('RECOVERY_REFERENCE_MANIFEST_SHA256_INVALID')

    previous: dict = {}
    if _recovery_state_path(project).exists():
        # A stale 2.5 checkpoint may be opened only by this replacement path.
        # Recovery/incident commands validate and reject it; re-checkpointing
        # the same transaction with freshly visible 2.0 settings repairs it.
        previous = _load_recovery_state(project, validate_settings_model=False)
        if previous.get('block_id') == block_id:
            old = previous.get('checkpoint') or {}
            if old.get('session_url') != session_url:
                raise ValueError(
                    'RECOVERY_SAME_BLOCK_SESSION_URL_CHANGED: resolve/archive the existing '
                    'transaction instead of silently replacing its Runway session')
            if session_id and old.get('session_id') and old.get('session_id') != session_id:
                raise ValueError(
                    'RECOVERY_SAME_BLOCK_SESSION_ID_CHANGED: exact same-session recovery required')
        else:
            previous = {}

    old_checkpoint = previous.get('checkpoint') or {}
    if previous:
        session_id = session_id or str(old_checkpoint.get('session_id') or '')
        prompt_sha256_value = prompt_sha256_value or str(old_checkpoint.get('prompt_sha256') or '')
        if references is None:
            references = [
                (str(row.get('slot') or ''), str(row.get('asset_id') or ''))
                for row in (old_checkpoint.get('references') or [])
            ]
        if verified_slots is None:
            verified_slots = list(old_checkpoint.get('verified_slots') or [])
        if settings is None:
            settings = dict(old_checkpoint.get('settings') or {})

    if not isinstance(settings, dict) or not settings:
        raise ValueError(
            'RECOVERY_SETTINGS_REQUIRED: checkpoint the visible model, mode, '
            'audio, ratio, resolution, and duration before ATTACH')
    if not settings.get('model'):
        raise ValueError('RECOVERY_SETTINGS_MODEL_REQUIRED')
    settings = dict(settings)
    settings['model'] = require_seedance_20(
        str(settings['model']), error_prefix='RECOVERY_SETTINGS')

    resolved_refs = [
        _registered_reference(project, slot, asset_id)
        for slot, asset_id in (references or [])
    ]
    if len({row['slot'] for row in resolved_refs}) != len(resolved_refs):
        raise ValueError('RECOVERY_REFERENCE_SLOT_DUPLICATE')
    verified = sorted(set(verified_slots or []))
    expected_slots = {row['slot'] for row in resolved_refs}
    if not set(verified) <= expected_slots:
        raise ValueError(
            f'RECOVERY_VERIFIED_SLOT_NOT_EXPECTED: {sorted(set(verified) - expected_slots)}')
    ref_hash = reference_manifest_sha256 or (
        str(old_checkpoint.get('reference_manifest_sha256') or '')
        if previous and resolved_refs == list(old_checkpoint.get('references') or [])
        else _hash_payload({'references': resolved_refs})
    )
    checkpoint = {
        'project': str(project),
        'block_id': block_id,
        'session_url': session_url,
        'session_id': session_id,
        'phase': phase.upper(),
        'prompt_sha256': prompt_sha256_value.lower(),
        'reference_manifest_sha256': ref_hash.lower(),
        'references': resolved_refs,
        'verified_slots': verified,
        'settings': settings or {},
        'checkpoint_revision': int(
            ((previous.get('checkpoint') or {}).get('checkpoint_revision') or 0)) + 1,
    }
    checkpoint['checkpoint_sha256'] = _hash_payload(checkpoint)
    state = {
        'contract_version': RECOVERY_CONTRACT_VERSION,
        'block_id': block_id,
        'status': 'READY',
        'next_action': 'CONTINUE_FROM_CHECKPOINT',
        'required_user_action': None,
        'checkpoint': checkpoint,
        # Re-checkpointing the same transaction updates hashes/settings/visible
        # slots; it must not launder away prior failures or drag usage.
        'incident_counts': dict(previous.get('incident_counts') or {}),
        'transport_failures_total': int(previous.get('transport_failures_total') or 0),
        'consecutive_transport_failures': int(previous.get('consecutive_transport_failures') or 0),
        'semantic_attachment_failures_by_slot': dict(
            previous.get('semantic_attachment_failures_by_slot') or {}),
        'drag_used_by_slot': dict(previous.get('drag_used_by_slot') or {}),
    }
    return _write_recovery_state(project, state, {
        'event': 'RECOVERY_CHECKPOINT_UPDATED' if previous else 'RECOVERY_CHECKPOINT_CREATED',
        'phase': checkpoint['phase'],
        'checkpoint_revision': checkpoint['checkpoint_revision'],
        'checkpoint_sha256': checkpoint['checkpoint_sha256'],
    })


def _human_action_for_incident(incident: str) -> str:
    actions = {
        'LOGIN_REQUIRED': '같은 Aside Runway 탭에서 다시 로그인한 뒤 “로그인 완료”라고 알려 달라.',
        'CAPTCHA_REQUIRED': '같은 Aside Runway 탭의 CAPTCHA를 직접 완료한 뒤 “완료”라고 알려 달라.',
        'PAYMENT_REQUIRED': '결제 또는 크레딧 변경은 자동 수행하지 않는다. 원하는 처리 방향을 명시해 달라.',
        'ACCOUNT_LIMIT': 'Runway 계정 제한 화면을 확인·해제한 뒤 같은 세션을 유지하고 “제한 해제”라고 알려 달라.',
        'ASIDE_FILE_UPLOAD_ACCESS_REQUIRED': 'Aside에서 Runway 파일 업로드 권한을 허용한 뒤 “파일 접근 켬”이라고 알려 달라.',
        'OS_PERMISSION_REQUIRED': 'macOS가 요청한 Aside/Computer Use 파일·접근성 권한을 허용한 뒤 “권한 허용”이라고 알려 달라.',
    }
    return actions[incident]


def record_recovery_incident(
    project: Path,
    block_id: str,
    incident: str,
    *,
    slot: str = '',
    detail: str = '',
    drag_approved: bool = False,
) -> dict:
    """Advance one fixed recovery ladder without inventing a new UI route."""
    project = project.expanduser().resolve()
    incident = incident.upper()
    if incident not in RECOVERY_INCIDENTS:
        raise ValueError(f'RECOVERY_INCIDENT_UNKNOWN: {incident}')
    state = _load_recovery_state(project, block_id)
    counts = state.setdefault('incident_counts', {})
    counts[incident] = int(counts.get(incident) or 0) + 1
    event = {
        'event': 'RECOVERY_INCIDENT_RECORDED',
        'incident': incident,
        'incident_count': counts[incident],
        'slot': slot or None,
        'detail': detail,
        'attachment_attempt_charged': False,
    }

    if incident in HUMAN_ACTION_INCIDENTS:
        state['status'] = 'USER_ACTION_REQUIRED'
        state['next_action'] = 'WAIT_FOR_EXACT_USER_ACTION'
        state['required_user_action'] = _human_action_for_incident(incident)
    elif incident in SESSION_TRANSPORT_INCIDENTS | UPLOAD_TRANSPORT_INCIDENTS:
        state['transport_failures_total'] = int(state.get('transport_failures_total') or 0) + 1
        consecutive = int(state.get('consecutive_transport_failures') or 0) + 1
        state['consecutive_transport_failures'] = consecutive
        event['transport_failure'] = True
        # A control timeout is not an upload attempt. Walk the same-session
        # transport ladder first, then restore the exact slot from checkpoint.
        if consecutive <= len(SAME_SESSION_RECOVERY_LADDER):
            state['status'] = 'RECOVERING'
            state['next_action'] = SAME_SESSION_RECOVERY_LADDER[consecutive - 1]
            state['after_recovery_action'] = 'RESTORE_CHECKPOINT_AND_RETRY_SAME_SLOT'
            state['required_user_action'] = None
        else:
            state['status'] = 'USER_ACTION_REQUIRED'
            state['next_action'] = 'WAIT_FOR_EXACT_USER_ACTION'
            state['after_recovery_action'] = None
            state['required_user_action'] = (
                '같은 Aside 창에서 기존 Runway 세션 URL을 다시 열고 Aside 제어 연결을 '
                '복구한 뒤 “세션 연결됨”이라고 알려 달라. 새 생성 세션을 만들거나 Generate를 누르지 않는다.')
    else:
        key = slot or 'UNSPECIFIED_SLOT'
        semantic = state.setdefault('semantic_attachment_failures_by_slot', {})
        semantic[key] = int(semantic.get(key) or 0) + 1
        failure_count = semantic[key]
        event['attachment_attempt_charged'] = True
        event['semantic_attachment_failure_count'] = failure_count
        state['consecutive_transport_failures'] = 0
        if failure_count == 1:
            state['status'] = 'RECOVERING'
            state['next_action'] = 'CANCEL_ONLY_FAILED_SLOT_REBUILD_ALIAS_FRESH_AX_RETRY_ONCE'
            state['after_recovery_action'] = 'VERIFY_ENLARGED_THUMBNAIL_AND_UPDATE_CHECKPOINT'
            state['required_user_action'] = None
        elif failure_count == 2 and drag_approved and not state['drag_used_by_slot'].get(key):
            state['status'] = 'RECOVERING'
            state['next_action'] = 'FINDER_DRAG_DROP_ONCE_CURRENT_THREAD_APPROVED'
            state['after_recovery_action'] = 'VERIFY_ENLARGED_THUMBNAIL_AND_UPDATE_CHECKPOINT'
            state['drag_used_by_slot'][key] = True
            state['required_user_action'] = None
        else:
            state['status'] = 'USER_ACTION_REQUIRED'
            state['next_action'] = 'WAIT_FOR_EXACT_USER_ACTION'
            state['after_recovery_action'] = None
            state['required_user_action'] = (
                f'{key}의 selector+fresh-alias 재시도가 실제 Runway 결과로 실패했다. '
                '현재 대화에서 Finder drag 1회 사용을 명시적으로 승인하거나, 같은 세션에서 해당 '
                '파일을 직접 첨부한 뒤 Generate를 누르지 말고 “첨부 완료”라고 알려 달라.')

    event.update({
        'status': state['status'],
        'next_action': state['next_action'],
        'required_user_action': state.get('required_user_action'),
    })
    return _write_recovery_state(project, state, event)


def resolve_recovery(
    project: Path,
    block_id: str,
    *,
    phase: str = '',
    verified_slot: str = '',
    detail: str = '',
) -> dict:
    """Record a successful rung and resume the transaction from its checkpoint."""
    project = project.expanduser().resolve()
    state = _load_recovery_state(project, block_id)
    checkpoint = state['checkpoint']
    if verified_slot:
        expected = {row['slot'] for row in checkpoint.get('references') or []}
        if verified_slot not in expected:
            raise ValueError(f'RECOVERY_VERIFIED_SLOT_NOT_EXPECTED: {verified_slot}')
        checkpoint['verified_slots'] = sorted(set(
            list(checkpoint.get('verified_slots') or []) + [verified_slot]))
    if phase:
        checkpoint['phase'] = phase.upper()
    unsigned = {key: value for key, value in checkpoint.items() if key != 'checkpoint_sha256'}
    checkpoint['checkpoint_sha256'] = _hash_payload(unsigned)
    state['status'] = 'READY'
    state['next_action'] = 'CONTINUE_FROM_CHECKPOINT'
    state['after_recovery_action'] = None
    state['required_user_action'] = None
    state['consecutive_transport_failures'] = 0
    return _write_recovery_state(project, state, {
        'event': 'RECOVERY_STEP_RESOLVED',
        'phase': checkpoint['phase'],
        'verified_slot': verified_slot or None,
        'detail': detail,
        'next_action': state['next_action'],
        'checkpoint_sha256': checkpoint['checkpoint_sha256'],
    })


def cmd_prepare_upload_alias(args) -> int:
    try:
        result = prepare_upload_alias(
            Path(args.project), args.asset_id, args.block_id, args.slot,
            modality=args.modality)
    except (OSError, ValueError) as exc:
        evidence(args, 'prepare-upload-alias', 'validated registry asset -> ASCII symlink',
                 str(exc), 'FAIL')
        print(json.dumps({'ok': False, 'error': str(exc)}, ensure_ascii=False))
        return 1
    receipt = Path(args.project).expanduser().resolve() / 'lanes' / 'seedance' / 'upload_alias_receipts.jsonl'
    receipt.parent.mkdir(parents=True, exist_ok=True)
    row = {'ts': dt.datetime.now().astimezone().isoformat(timespec='seconds'), **result}
    with receipt.open('a', encoding='utf-8') as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + '\n')
    evidence(args, 'prepare-upload-alias', 'validated registry asset -> ASCII symlink',
             json.dumps(result, ensure_ascii=False), 'READY_FOR_NATIVE_CHOOSER')
    print(json.dumps({'ok': True, **result}, ensure_ascii=False, indent=2))
    return 0


def cmd_cleanup_upload_alias(args) -> int:
    try:
        result = cleanup_upload_alias(Path(args.path))
    except (OSError, ValueError) as exc:
        evidence(args, 'cleanup-upload-alias', 'remove helper-owned symlink only', str(exc), 'FAIL')
        print(json.dumps({'ok': False, 'error': str(exc)}, ensure_ascii=False))
        return 1
    evidence(args, 'cleanup-upload-alias', 'remove helper-owned symlink only',
             json.dumps(result, ensure_ascii=False), 'REMOVED')
    print(json.dumps({'ok': True, **result}, ensure_ascii=False))
    return 0


def cmd_recovery_checkpoint(args) -> int:
    try:
        references = [_parse_reference_arg(value) for value in (args.reference or [])]
        settings = json.loads(args.settings_json) if args.settings_json else None
        if settings is not None and not isinstance(settings, dict):
            raise ValueError('RECOVERY_SETTINGS_JSON_MUST_BE_OBJECT')
        state = create_recovery_checkpoint(
            Path(args.project), args.block_id, args.session_url, args.phase,
            session_id=args.session_id or '',
            prompt_sha256_value=args.prompt_sha256 or '',
            reference_manifest_sha256=args.reference_manifest_sha256 or '',
            references=references if args.reference is not None else None,
            verified_slots=args.verified_slot,
            settings=settings,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        evidence(args, 'recovery-checkpoint', 'valid same-session recovery checkpoint',
                 str(exc), 'FAIL')
        print(json.dumps({'ok': False, 'error': str(exc)}, ensure_ascii=False))
        return 1
    summary = {
        'ok': True,
        'contract_version': state['contract_version'],
        'block_id': state['block_id'],
        'status': state['status'],
        'next_action': state['next_action'],
        'checkpoint': state['checkpoint'],
        'state_path': str(_recovery_state_path(Path(args.project))),
    }
    evidence(args, 'recovery-checkpoint', 'valid same-session recovery checkpoint',
             json.dumps(summary, ensure_ascii=False), 'READY')
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def cmd_recovery_record(args) -> int:
    try:
        state = record_recovery_incident(
            Path(args.project), args.block_id, args.incident,
            slot=args.slot or '', detail=args.detail or '',
            drag_approved=bool(args.drag_approved),
        )
    except (OSError, ValueError) as exc:
        evidence(args, 'recovery-record', 'advance fixed recovery ladder', str(exc), 'FAIL')
        print(json.dumps({'ok': False, 'error': str(exc)}, ensure_ascii=False))
        return 1
    summary = {
        'ok': True,
        'block_id': state['block_id'],
        'status': state['status'],
        'next_action': state['next_action'],
        'after_recovery_action': state.get('after_recovery_action'),
        'required_user_action': state.get('required_user_action'),
        'consecutive_transport_failures': state.get('consecutive_transport_failures'),
        'semantic_attachment_failures_by_slot': state.get('semantic_attachment_failures_by_slot'),
        'attachment_attempt_charged': args.incident.upper() in UPLOAD_SEMANTIC_INCIDENTS,
    }
    verdict = 'USER_ACTION_REQUIRED' if state['status'] == 'USER_ACTION_REQUIRED' else 'RECOVERING'
    evidence(args, 'recovery-record', 'advance fixed recovery ladder',
             json.dumps(summary, ensure_ascii=False), verdict)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 2 if state['status'] == 'USER_ACTION_REQUIRED' else 0


def cmd_recovery_resolve(args) -> int:
    try:
        state = resolve_recovery(
            Path(args.project), args.block_id, phase=args.phase or '',
            verified_slot=args.verified_slot or '', detail=args.detail or '')
    except (OSError, ValueError) as exc:
        evidence(args, 'recovery-resolve', 'resume exact transaction from checkpoint',
                 str(exc), 'FAIL')
        print(json.dumps({'ok': False, 'error': str(exc)}, ensure_ascii=False))
        return 1
    summary = {
        'ok': True,
        'block_id': state['block_id'],
        'status': state['status'],
        'next_action': state['next_action'],
        'checkpoint': state['checkpoint'],
    }
    evidence(args, 'recovery-resolve', 'resume exact transaction from checkpoint',
             json.dumps(summary, ensure_ascii=False), 'READY')
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


VERIFY_BLOCK = f'''
tell application "{TARGET_APP}" to activate
delay 0.5
tell application "System Events"
    set fm to name of first application process whose frontmost is true
end tell
if fm is not "{TARGET_APP}" then error "ABORT_FOCUS_NOT_{TARGET_APP.upper()}: " & fm
'''


def native_picker_guard() -> str:
    """Read exact CLI identity; native modal proof never navigates or selects."""
    binding = aside_bridge.require_project()
    observed = aside_bridge.repl(aside_bridge.binding_script(
        binding, '({windowId:matches[0].windowId,url:await page.url()})',
        require_active=True, require_focused=False), binding.get('account'))
    window_id = str(observed.get('windowId', ''))
    if not re.fullmatch(r'[1-9][0-9]*', window_id):
        raise ValueError('ASIDE_NATIVE_WINDOW_ID_INVALID')
    current_url = observed.get('url', '')
    if aside_bridge.session_identity(current_url) != aside_bridge.session_identity(binding['session_url']):
        raise ValueError('ASIDE_NATIVE_SESSION_MISMATCH')
    return f'''
tell application "{TARGET_APP}"
    if (id of front window as text) is not {json.dumps(window_id)} then error "ABORT_NATIVE_WINDOW_CHANGED"
    if (URL of active tab of front window) is not {json.dumps(current_url)} then error "ABORT_NATIVE_TAB_CHANGED"
end tell
tell application "System Events"
    tell process "{TARGET_APP}"
        if (value of attribute "AXMain" of window 1) is not true then error "ABORT_NATIVE_MAIN_WINDOW"
        if not (exists sheet 1 of window 1) then error "ABORT_NO_PICKER_SHEET"
        if (value of attribute "AXIdentifier" of sheet 1 of window 1) is not "open-panel" then error "ABORT_NOT_OPEN_PANEL"
    end tell
end tell
'''


def run_verified(args, action: str, tail: str, pre: str = '', *, native_picker: bool = False) -> int:
    """Validate/activate/revalidate, then guarded pre + tail in one osascript.

    Refuses to fire keys while a CJK IME is active — see the input-method guard.
    """
    # First require the exact active tab, but permit Aside to be in the
    # background: requiring window focus here prevents our own activation.
    # This preliminary observation never authorizes keys or clipboard writes.
    rc, _out, err = aside_bridge.browser_js('true', require_active=True, require_focused=False)
    if rc:
        evidence(args, action, 'exact bound tab active before native action', err, 'FOCUS_ABORT')
        return 2
    rc, out, err = osa(VERIFY_BLOCK)
    if rc:
        evidence(args, action, 'activate existing Aside without input', err or out, 'FOCUS_ABORT')
        return 2
    # Activation can select another window, and the user may have switched
    # tabs. Re-read both exact identity and focused-window state before input.
    rc, _out, err = aside_bridge.browser_js('true', require_active=True)
    picker_guard = ''
    if rc and native_picker and 'ASIDE_NATIVE_BOUND_TAB_NOT_ACTIVE' in err:
        try:
            picker_guard = native_picker_guard()
            rc, _out, err = osa(VERIFY_BLOCK + picker_guard)
        except (ValueError, OSError, KeyError, TypeError) as exc:
            rc, err = 2, str(exc)
    if rc:
        evidence(args, action, 'exact bound tab focused after activation', err, 'FOCUS_ABORT')
        return 2
    if 'keystroke' in tail or 'key code' in tail:
        st = ime_state()
        if st.get('cjk_active'):
            evidence(args, action, 'input source safe for keystrokes',
                     json.dumps({**st, 'required_action': IME_REMEDY}, ensure_ascii=False),
                     'BLOCKED_IME_ACTIVE')
            return 4
    rc, out, err = osa(VERIFY_BLOCK + picker_guard + pre + tail)
    if rc != 0:
        verdict = 'FOCUS_ABORT' if 'ABORT_FOCUS' in err else 'ASIDE_CONTROL_ERROR'
        evidence(args, action, f'frontmost={TARGET_APP} then action', err or out, verdict)
        return 2 if verdict == 'FOCUS_ABORT' else 3
    evidence(args, action, f'frontmost={TARGET_APP} then action', out or 'done', 'DONE_VERIFY_VISUALLY')
    return 0


def cmd_frontmost(args) -> int:
    rc, out, err = osa('tell application "System Events" to name of first application process whose frontmost is true')
    print(out or err)
    return rc


def cmd_escape(args) -> int:
    return run_verified(args, 'ESC', 'tell application "System Events" to key code 53')


def cmd_picker_go(args) -> int:
    path = str(Path(args.path).expanduser())
    pre = f'set the clipboard to {json.dumps(path)}\n'
    tail = f'''
tell application "System Events"
    tell process "{TARGET_APP}"
        if not (exists sheet 1 of window 1) then error "ABORT_NO_PICKER_SHEET"
        keystroke "g" using {{command down, shift down}}
        delay 0.5
        if not (exists sheet 1 of window 1) then error "ABORT_GO_SHEET_LOST"
        keystroke "a" using {{command down}}
        delay 0.1
        key code 51
        delay 0.1
        keystroke "v" using {{command down}}
        delay 0.3
        key code 36
    end tell
end tell
'''
    return run_verified(args, f'picker-go {path}', tail, pre=pre, native_picker=True)


def cmd_picker_select(args) -> int:
    """Select one visible helper alias via AX, without keyboard/IME events."""
    path = Path(os.path.abspath(Path(args.path).expanduser()))
    if path.parent.resolve() != UPLOAD_ALIAS_ROOT.resolve() or not path.is_symlink() or not path.is_file():
        raise ValueError('PICKER_SELECT_REQUIRES_LIVE_HELPER_ALIAS')
    if not re.fullmatch(r'[A-Za-z0-9_]+\.(png|jpg|jpeg|webp|mp4|mov|wav|mp3)', path.name):
        raise ValueError('PICKER_SELECT_ALIAS_NAME_INVALID')
    tail = f'''
tell application "System Events"
    tell process "{TARGET_APP}"
        if (value of pop up button 1 of splitter group 1 of sheet 1 of window 1) is not {json.dumps(UPLOAD_ALIAS_ROOT.name)} then error "ABORT_NATIVE_ALIAS_FOLDER"
        set listView to outline 1 of scroll area 1 of splitter group 1 of splitter group 1 of sheet 1 of window 1
        if (value of attribute "AXIdentifier" of listView) is not "ListView" then error "ABORT_NATIVE_LIST_LAYOUT"
        set candidates to {{}}
        repeat with rr in rows of listView
            repeat with cell in UI elements of rr
                repeat with field in text fields of cell
                    if value of field is {json.dumps(path.name)} then set end of candidates to contents of rr
                end repeat
            end repeat
        end repeat
        if (count candidates) is not 1 then error "ABORT_NATIVE_UNIQUE_FILE_ROW"
        set targetRow to item 1 of candidates
        set value of attribute "AXSelected" of targetRow to true
        if (value of attribute "AXSelected" of targetRow) is not true then error "ABORT_NATIVE_SELECTION_NOT_APPLIED"
    end tell
end tell
return "ROW_SELECTED_VERIFY_OPEN_AND_THUMBNAIL"
'''
    return run_verified(args, f'picker-select {path.name}', tail, native_picker=True)


GEN_BTN_JS = r"""
(() => {
  const buttons = [...document.querySelectorAll('button')].filter(x => x.getClientRects().length && /^generate(?:\s|$)/i.test((x.innerText || '').trim()));
  if (buttons.length !== 1) return 'NO_GENERATE_BUTTON';
  const b = buttons[0];
  const chain = [];
  let el = b;
  for (let i = 0; el && i < 4; i++, el = el.parentElement) {
    const cs = getComputedStyle(el);
    chain.push({
      tag: el.tagName,
      text: (el.textContent || '').trim().slice(0, 40),
      backgroundColor: cs.backgroundColor,
      color: cs.color,
      className: String(el.className || '').slice(0, 120)
    });
  }
  const rect = b.getBoundingClientRect();
  return JSON.stringify({
    text: (b.textContent || '').trim().slice(0, 40),
    rect: {x: Math.round(rect.x), y: Math.round(rect.y), w: Math.round(rect.width), h: Math.round(rect.height)},
    color_source: 'visible CSS button/ancestor background only; disabled/aria/data-soft-disabled ignored by user rule',
    chain
  });
})()
"""


def _rgb_triplet(value: str):
    import re
    m = re.search(r'rgba?\((\d+),\s*(\d+),\s*(\d+)', value or '')
    if not m:
        return None
    return tuple(map(int, m.groups()))


def _is_blue(rgb) -> bool:
    if not rgb:
        return False
    r, g, b = rgb
    return b >= 100 and b > r + 25 and b > g + 10


def _is_gray(rgb) -> bool:
    if not rgb:
        return False
    r, g, b = rgb
    return max(r, g, b) - min(r, g, b) <= 18


def read_generate_state() -> dict:
    """Read visible Generate button color. User rule: blue=clickable, gray=inactive; ignore AX/DOM disabled heuristics."""
    rc, out, err = browser_js(GEN_BTN_JS)
    if rc != 0:
        return {'verdict': 'ASIDE_CONTROL_ERROR', 'browser': TARGET_APP, 'error': err[-500:]}
    if out == 'NO_GENERATE_BUTTON':
        return {'verdict': 'NO_GENERATE_BUTTON'}
    try:
        st = json.loads(out)
    except Exception:
        return {'verdict': 'PARSE_ERROR', 'raw': out[:200]}
    rgbs = []
    for item in st.get('chain', []):
        rgb = _rgb_triplet(item.get('backgroundColor', ''))
        if rgb and rgb != (0, 0, 0):
            rgbs.append(rgb)
    st['sampled_background_rgbs'] = rgbs
    if any(_is_blue(rgb) for rgb in rgbs):
        st['verdict'] = 'BLUE_ENABLED'
    elif any(_is_gray(rgb) for rgb in rgbs):
        st['verdict'] = 'GRAY_INACTIVE'
    else:
        st['verdict'] = 'UNKNOWN_COLOR_TREAT_AS_INACTIVE'
    return st



# Require the unique visible Lexical editor; never a generic contenteditable.
PROMPT_SEL = '[contenteditable][data-lexical-editor]'


# innerText of the editor adds CSS paragraph separators; read actual P blocks
# without collapsing spaces, intentional blank paragraphs, or inline BRs.
PROMPT_DOM_TEXT_JS = r"""(el => {
  const nodes = Array.from(el.childNodes);
  if (nodes.length && nodes.every(n => n.nodeType === 1 && n.tagName === 'P')) {
    return nodes.map(p => p.childNodes.length === 1 && p.firstChild.nodeName === 'BR'
      ? '' : (p.innerText || '')).join('\n');
  }
  return el.innerText || '';
})"""


def cmd_paste_prompt(args) -> int:
    """Insert prompt text without any keystroke.

    The prompt box is a Lexical editor: execCommand and DOM writes are ignored,
    but real paste events are handled. Going through System Events instead is
    what broke Korean input — macOS routes synthetic keystrokes through the
    active input method, so with the 2-set Hangul IME on, "ZZTEST123" arrived as
    Hangul fragments and Cmd+V typed a literal character instead of pasting.
    A dispatched ClipboardEvent bypasses the IME entirely. (2026-07-29)
    """
    prompt_path = Path(args.file).expanduser().resolve()
    if prompt_path.suffix.lower() != '.txt':
        st = {'ok': False, 'verdict': 'PROMPT_FILE_MUST_BE_UTF8_NFC_TXT',
              'path': str(prompt_path)}
        evidence(args, 'paste-prompt-preflight', 'UTF-8 NFC .txt prompt file',
                 json.dumps(st, ensure_ascii=False), st['verdict'])
        print(json.dumps(st, ensure_ascii=False))
        return 1
    try:
        text = prompt_path.read_text(encoding='utf-8')
    except (OSError, UnicodeError) as exc:
        st = {'ok': False, 'verdict': 'PROMPT_FILE_UTF8_READ_FAILED',
              'path': str(prompt_path), 'error': str(exc)}
        evidence(args, 'paste-prompt-preflight', 'readable UTF-8 .txt prompt file',
                 json.dumps(st, ensure_ascii=False), st['verdict'])
        print(json.dumps(st, ensure_ascii=False))
        return 1
    if text != unicodedata.normalize('NFC', text):
        st = {'ok': False, 'verdict': 'PROMPT_FILE_NOT_NFC',
              'path': str(prompt_path)}
        evidence(args, 'paste-prompt-preflight', 'NFC-normalized prompt text',
                 json.dumps(st, ensure_ascii=False), st['verdict'])
        print(json.dumps(st, ensure_ascii=False))
        return 1
    expected_normalized = normalize_prompt(text)
    expected_stats = language_stats(expected_normalized)
    if len(expected_normalized) > 3500 or not expected_stats['korean_dominant']:
        st = {
            'ok': False,
            'verdict': 'KOREAN_PROMPT_PREFLIGHT_FAILED',
            'language': expected_stats,
            'over_limit': len(expected_normalized) > 3500,
            'prompt_sha256': prompt_sha256(expected_normalized),
        }
        evidence(args, 'paste-prompt-preflight',
                 'Korean-dominant prompt <=3500 characters',
                 json.dumps(st, ensure_ascii=False), st['verdict'])
        print(json.dumps(st, ensure_ascii=False))
        return 1
    try:
        aside_bridge.require_project(prompt_file=prompt_path)
    except (OSError, ValueError) as exc:
        evidence(args, 'paste-prompt', 'prompt belongs to the bound project', str(exc), 'ASIDE_BINDING_ERROR')
        return 3
    # Lexical's replace selection has been observed to append instead. Refuse to
    # touch a non-empty editor; the visible operator must clear it and verify an
    # empty field first. This prevents duplicated prompts after a false replace.
    rc, before_out, before_err = browser_js("""(() => {
  const el = (() => { const a = [...document.querySelectorAll('%s')].filter(e => e.getClientRects().length); return a.length === 1 ? a[0] : null; })();
  return JSON.stringify(el ? {ok:true, text:(%s)(el)} : {ok:false});
})()""" % (PROMPT_SEL, PROMPT_DOM_TEXT_JS))
    if rc != 0:
        evidence(args, 'paste-prompt-preflight', 'read empty Lexical editor',
                 before_err[-200:], 'ASIDE_CONTROL_ERROR')
        return 3
    before_state = json.loads(before_out)
    if not before_state.get('ok'):
        evidence(args, 'paste-prompt-preflight', 'read empty Lexical editor',
                 before_out, 'NO_PROMPT_EDITOR')
        return 1
    before_normalized = normalize_prompt(str(before_state.get('text', '')))
    if before_normalized:
        verdict = ('REPLACE_UNSAFE_CLEAR_VISIBLE_EDITOR_FIRST' if args.replace
                   else 'PROMPT_NOT_EMPTY_DO_NOT_APPEND')
        st = {'ok': False, 'verdict': verdict, 'before_chars': len(before_normalized),
              'before_prompt_sha256': prompt_sha256(before_normalized)}
        evidence(args, 'paste-prompt-preflight', 'empty Lexical editor before one paste',
                 json.dumps(st, ensure_ascii=False), verdict)
        print(json.dumps(st, ensure_ascii=False))
        return 1
    payload = json.dumps({'text': text, 'replace': bool(args.replace), 'sel': PROMPT_SEL})
    js = """(() => {
  const cfg = %s;
  const el = (() => { const a = [...document.querySelectorAll(cfg.sel)].filter(e => e.getClientRects().length); return a.length === 1 ? a[0] : null; })();
  if (!el) return JSON.stringify({ok:false, error:'NO_PROMPT_EDITOR'});
  if ((el.innerText || '').trim()) return JSON.stringify({ok:false,error:'PROMPT_CHANGED_BEFORE_PASTE'});
  el.focus();
  const sel = window.getSelection(), r = document.createRange();
  r.selectNodeContents(el);
  r.collapse(false);
  sel.removeAllRanges(); sel.addRange(r);
  const dt = new DataTransfer();
  dt.setData('text/plain', cfg.text);
  el.dispatchEvent(new ClipboardEvent('paste', {clipboardData: dt, bubbles: true, cancelable: true}));
  return JSON.stringify({ok:true, dispatched:true});
})()""" % payload
    rc, out, err = browser_js(js)
    if rc != 0:
        evidence(args, 'paste-prompt', 'lexical paste', err[-200:], 'ASIDE_CONTROL_ERROR')
        return 3
    try:
        st = json.loads(out)
    except Exception:
        evidence(args, 'paste-prompt', 'lexical paste', out[:200], 'PARSE_ERROR')
        return 3
    if not st.get('ok'):
        evidence(args, 'paste-prompt', 'lexical paste', out, 'NO_PROMPT_EDITOR')
        return 1
    # The paste event returns before Lexical commits its React state. Poll the
    # actual editor for up to two seconds instead of emitting a false mismatch.
    actual_text = ''
    waited_ms = 0
    for attempt in range(11):
        rc, read_out, read_err = browser_js("""(() => {
  const el = (() => { const a = [...document.querySelectorAll('%s')].filter(e => e.getClientRects().length); return a.length === 1 ? a[0] : null; })();
  return JSON.stringify(el ? {ok:true, text:(%s)(el)} : {ok:false});
})()""" % (PROMPT_SEL, PROMPT_DOM_TEXT_JS))
        if rc != 0:
            evidence(args, 'paste-prompt-verify', 'read committed Lexical text',
                     read_err[-200:], 'ASIDE_CONTROL_ERROR')
            return 3
        read_state = json.loads(read_out)
        actual_text = str(read_state.get('text', ''))
        if normalize_prompt(actual_text) == expected_normalized:
            break
        if attempt < 10:
            time.sleep(0.2)
            waited_ms += 200
    actual_normalized = normalize_prompt(actual_text)
    actual_stats = language_stats(actual_normalized)
    content_match = actual_normalized == expected_normalized
    st.update({
        'before': 0,
        'after': len(actual_text),
        'expected': len(expected_normalized),
        'hangul_runs': len(re.findall(r'[가-힣]+', actual_text)),
        'over_limit': len(actual_text) > 3500,
        'tail': actual_text[-60:],
        'waited_ms': waited_ms,
    })
    verdict = ('OVER_3500_LIMIT' if st['over_limit']
               else 'CONTENT_MISMATCH_DO_NOT_GENERATE' if not content_match
               else 'KOREAN_VALIDATION_FAILED' if not actual_stats['korean_dominant']
               else 'OK')
    st['expected_prompt_sha256'] = prompt_sha256(expected_normalized)
    st['actual_prompt_sha256'] = prompt_sha256(actual_normalized)
    st['content_match'] = content_match
    st['language'] = actual_stats
    st['verdict'] = verdict
    evidence(args, 'paste-prompt', f"expect {st['expected']} chars", json.dumps(st, ensure_ascii=False), verdict)
    print(json.dumps(st, ensure_ascii=False))
    return 0 if verdict == 'OK' else 1


def cmd_read_prompt(args) -> int:
    """Report what is actually in the prompt box."""
    rc, out, err = browser_js("""(() => {
  const el = (() => { const a = [...document.querySelectorAll('%s')].filter(e => e.getClientRects().length); return a.length === 1 ? a[0] : null; })();
  if (!el) return JSON.stringify({ok:false, error:'NO_PROMPT_EDITOR'});
  const t = (%s)(el);
  return JSON.stringify({ok:true, text:t, len:t.length, over_limit:t.length>3500,
    hangul_runs:(t.match(/[가-힣]+/g)||[]).length,
    head:t.slice(0,60), tail:t.slice(-60)});
})()""" % (PROMPT_SEL, PROMPT_DOM_TEXT_JS))
    if rc != 0:
        evidence(args, 'read-prompt', 'read editor', err[-200:], 'ASIDE_CONTROL_ERROR')
        return 3
    st = json.loads(out)
    actual = str(st.pop('text', ''))
    st['actual_prompt_sha256'] = prompt_sha256(normalize_prompt(actual))
    if getattr(args, 'file', None):
        path = Path(args.file).expanduser().resolve()
        aside_bridge.require_project(prompt_file=path)
        expected = normalize_prompt(path.read_text(encoding='utf-8'))
        st['expected_prompt_sha256'] = prompt_sha256(expected)
        st['content_match'] = bool(st.get('ok')) and normalize_prompt(actual) == expected
        st['ok'] = st['content_match']
    evidence(args, 'read-prompt', 'read editor', json.dumps(st, ensure_ascii=False), 'OK' if st.get('ok') else 'FAIL')
    print(json.dumps(st, ensure_ascii=False))
    return 0 if st.get('ok') else 1



RESUME_CONTRACT_VERSION = 'seedance_foreground_wait_v4_20260819'
QUEUE_RUNTIME_VERSION = 'seedance_queue_runtime_v2_20260819'
QUEUE_TARGET_DEFAULT = 2
WAKE_DELAY_SECONDS = 900
WAIT_RETURN_INSTRUCTION_KO = '현재 Seedance 보드를 다시 읽고 queue-cycle --from-wake로 소비해.'
INFLIGHT_STATES = {'IN_QUEUE', 'GENERATING', 'PROCESSING', 'LOADING'}
SETTLED_STATES = {'COMPLETED', 'FAILED', 'CANCELLED', 'INVALID_INPUT'}
QUEUE_JOB_STATES = INFLIGHT_STATES | SETTLED_STATES
WAKE_REQUIRED_VERDICTS = {
    'QUEUE_FULL_WAKE_REQUIRED',
    'DRAIN_QUEUE_WAKE_REQUIRED',
}
ELAPSED_UNCONSUMED_RESULTS = {
    # v2 never calls elapsed time a fired wake. The legacy value is accepted
    # only as migration debt so an old task cannot silently overwrite it.
    'WAIT_ELAPSED_RECHECK_NOT_CONSUMED',
    'INTERRUPTED_RECHECK_REQUIRED',
    'ORPHANED_FOREGROUND_WAIT_RECHECK_REQUIRED',
    'WAKE_FIRED_RECHECK_BOARD_NOW',
}


def _json_file(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _write_json_atomic(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f'.{path.name}.{os.getpid()}.tmp')
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(temporary, path)


def _pid_running(pid: object) -> bool:
    try:
        candidate = int(pid)
    except (TypeError, ValueError):
        return False
    if candidate <= 0:
        return False
    try:
        os.kill(candidate, 0)
    except (OSError, ProcessLookupError):
        return False
    return True


def _wait_elapsed_unconsumed(wake: dict) -> bool:
    """Return whether a foreground wait elapsed without a board observation.

    A timer changing a JSON file cannot re-enter Codex reasoning. Only the
    subsequent visible-board observation consumes the wait. Treat the old
    WAKE_FIRED value as unconsumed migration debt because it proved only that
    sleep() returned, not that the model resumed.
    """
    if wake.get('elapsed_unconsumed') is True:
        return True
    if str(wake.get('last_result') or '') in ELAPSED_UNCONSUMED_RESULTS:
        return True
    return bool(wake.get('pending')) and not _pid_running(wake.get('wait_pid'))


def _project_seedance_sources(project: Path) -> dict:
    """Resolve v4 or legacy Seedance metadata without migrating either layout."""
    project = project.expanduser().resolve()
    manifest_path = project / 'manifest.json'
    state_path = project / 'state.json'
    if manifest_path.is_file() and state_path.is_file():
        return {
            'layout': 'runtime_v4',
            'state_path': state_path,
            'manifest_path': manifest_path,
            'metadata_dir': project / 'lanes' / 'seedance',
        }
    for status_path in (
        project / 'i2v' / 'seedance' / 'status.json',
        project / 'lanes' / 'seedance' / 'status.json',
        project / 'status.json',
    ):
        if status_path.is_file():
            return {
                'layout': 'legacy',
                'state_path': status_path,
                'manifest_path': None,
                'metadata_dir': status_path.parent,
            }
    raise ValueError(
        'INVALID_VIDEO_PROJECT: expected manifest.json + state.json or a legacy '
        f'Seedance status.json under {project}')


def queue_runtime_path(project: Path) -> Path:
    source = _project_seedance_sources(project)
    return Path(source['metadata_dir']) / 'queue_runtime.json'


def resume_contract_path(project: Path) -> Path:
    source = _project_seedance_sources(project)
    return Path(source['metadata_dir']) / 'resume_contract.json'


def settings_preflight_path(project: Path, block_id: str) -> Path:
    source = _project_seedance_sources(project)
    return (
        Path(source['metadata_dir']) / 'evidence'
        / f'{_safe_block_token(block_id)}_settings_preflight.json')


def inherited_edit_duration(project: Path, pack: dict, source_video: Path | None, expected: int) -> dict:
    """Edit inherits the verified input; never fabricate a visible duration label."""
    if not source_video or not pack.get('input_video_asset_id'):
        raise ValueError('SETTINGS_EDIT_INPUT_ASSET_REQUIRED')
    asset = media_registry.get_asset(project, pack['input_video_asset_id'])
    path = source_video.expanduser().resolve()
    if (asset.get('kind') != 'video' or asset.get('state') not in {'approved', 'selected', 'locked'}
            or not asset.get('active') or Path(asset['current_path']).resolve() != path
            or not path.is_file() or media_registry.sha256(path) != asset.get('sha256')):
        raise ValueError('SETTINGS_EDIT_SOURCE_NOT_APPROVED_OR_CHANGED')
    probe = subprocess.run(['ffprobe', '-v', 'error', '-show_format', '-show_streams',
                            '-of', 'json', str(path)], capture_output=True, text=True, timeout=30)
    if probe.returncode:
        raise ValueError('SETTINGS_EDIT_FFPROBE_FAILED')
    data = json.loads(probe.stdout)
    video = next((v for v in data.get('streams', []) if v.get('codec_type') == 'video'), None)
    if not video or not video.get('codec_name'):
        raise ValueError('SETTINGS_EDIT_VIDEO_STREAM_REQUIRED')
    from fractions import Fraction
    import math
    duration = float(data.get('format', {}).get('duration', 0))
    fps = float(Fraction(video.get('avg_frame_rate') or '0'))
    if not math.isfinite(duration) or not math.isfinite(fps) or duration <= 0 or fps <= 0:
        raise ValueError('SETTINGS_EDIT_SOURCE_DURATION_INVALID')
    # One input frame is metadata rounding tolerance, not a shorter-duration override.
    if abs(duration - expected) > 1 / fps + 1e-6:
        raise ValueError('SETTINGS_EDIT_INHERITED_DURATION_LOCK_MISMATCH')
    return {'input_video_asset_id': asset['asset_id'], 'input_video_sha256': asset['sha256'],
            'inherited_duration_sec': duration, 'duration_tolerance_sec': 1 / fps}


def verify_attested_generation_settings(
    project: Path,
    block_id: str,
    *,
    visible_model: str,
    duration_sec: float,
    duration_source: str = "visible",
    source_video: Path | None = None,
) -> dict:
    """Reject a non-2.0 model or duration drift before Generate."""
    project = project.expanduser().resolve()
    source = _project_seedance_sources(project)
    attestation_path = (
        Path(source['metadata_dir']) / 'prompts' / f'{block_id}_attestation.json')
    attestation = _json_file(attestation_path)
    if not attestation:
        raise ValueError(f'SETTINGS_ATTESTATION_MISSING: {attestation_path}')
    if attestation.get('verdict') != 'ATTESTED':
        raise ValueError(
            f'SETTINGS_ATTESTATION_NOT_PASS: verdict={attestation.get("verdict")}')
    if attestation.get('block_id') != block_id:
        raise ValueError(
            f'SETTINGS_ATTESTATION_BLOCK_MISMATCH: '
            f'{attestation.get("block_id")} != {block_id}')
    pack_path = Path(str(attestation.get('pack') or '')).expanduser().resolve()
    if not pack_path.is_file():
        raise ValueError(f'SETTINGS_ATTESTED_PACK_MISSING: {pack_path}')
    current_pack_hash = media_registry.sha256(pack_path)
    if current_pack_hash != attestation.get('pack_sha256'):
        raise ValueError('SETTINGS_ATTESTED_PACK_CHANGED_REATTEST_REQUIRED')
    duration_lock = attestation.get('duration_lock') or {}
    expected = duration_lock.get('expected_duration_sec')
    pack_duration = duration_lock.get('pack_duration_sec')
    if not isinstance(expected, int):
        raise ValueError('SETTINGS_DURATION_LOCK_NOT_ATTESTED')
    lock_path = Path(str(duration_lock.get('path') or '')).expanduser().resolve()
    if not lock_path.is_file():
        raise ValueError(f'SETTINGS_DURATION_LOCK_MISSING: {lock_path}')
    if media_registry.sha256(lock_path) != duration_lock.get('sha256'):
        raise ValueError('SETTINGS_DURATION_LOCK_CHANGED_REATTEST_REQUIRED')
    if pack_duration != expected:
        raise ValueError(
            f'SETTINGS_PACK_DURATION_LOCK_MISMATCH: expected={expected},pack={pack_duration}')
    verified_model = require_seedance_20(visible_model)
    # Historic ATTESTED receipts do not bypass the currently installed compiler.
    current_pack = _json_file(pack_path)
    pack_errors = validate_seedance(current_pack)
    if pack_errors:
        raise ValueError('SETTINGS_CURRENT_PACK_INVALID_REAUTHOR_REQUIRED: ' + ','.join(pack_errors))
    duration_errors, _current_duration = generation_settings.validate_pack_duration(current_pack, project)
    if duration_errors:
        raise ValueError('SETTINGS_CURRENT_DURATION_LOCK_INVALID: ' + ','.join(duration_errors))
    package_model = current_pack.get('provider_model', 'Seedance 2.0')
    if package_model != REQUIRED_GENERATION_MODEL:
        raise ValueError('SETTINGS_PACKAGE_MODEL_MISMATCH')
    mode = str(current_pack.get('provider_mode') or current_pack.get('creation_mode') or current_pack.get('mode') or '').lower()
    inherited = {}
    if mode == 'edit':
        if REQUIRED_GENERATION_MODEL != 'Seedance 2.5' or duration_source != 'input-video':
            raise ValueError('SETTINGS_EDIT_INHERITED_EVIDENCE_REQUIRED')
        inherited = inherited_edit_duration(project, current_pack, source_video, expected)
        if abs(duration_sec - inherited['inherited_duration_sec']) > inherited['duration_tolerance_sec']:
            raise ValueError('SETTINGS_EDIT_REPORTED_SOURCE_DURATION_MISMATCH')
    elif duration_source != 'visible' or source_video is not None:
        raise ValueError('SETTINGS_INHERITED_DURATION_ONLY_FOR_EDIT')
    elif duration_sec != expected:
        raise ValueError(
            f'SETTINGS_VISIBLE_DURATION_MISMATCH: expected={expected},visible={duration_sec}')
    result = {
        'ok': True,
        'contract_version': 'seedance_generation_settings_preflight_v3_20260906',
        'verified_at': dt.datetime.now().astimezone().isoformat(timespec='seconds'),
        'project': str(project),
        'layout': source['layout'],
        'block_id': block_id,
        'attestation': str(attestation_path),
        'attestation_sha256': media_registry.sha256(attestation_path),
        'duration_lock_path': str(lock_path),
        'duration_lock_sha256': duration_lock.get('sha256'),
        'expected_duration_sec': expected,
        'visible_duration_sec': None if inherited else duration_sec,
        'duration_source': duration_source,
        **inherited,
        'expected_model': REQUIRED_GENERATION_MODEL,
        'visible_model': verified_model,
        'verdict': 'PASS_SETTINGS_MATCH_SEEDANCE_2_0_AND_ATTESTED_DURATION',
    }
    _write_json_atomic(settings_preflight_path(project, block_id), result)
    return result


def _normalize_queue_state(value: str) -> str:
    normalized = re.sub(r'[^A-Za-z0-9]+', '_', value.strip()).strip('_').upper()
    aliases = {
        'INQUEUE': 'IN_QUEUE',
        'IN_QUEUE_VISIBLE': 'IN_QUEUE',
        'LOADING_SPINNER': 'LOADING',
        'COMPLETE': 'COMPLETED',
        'INVALID': 'INVALID_INPUT',
    }
    return aliases.get(normalized, normalized)


def parse_queue_job(value: str) -> dict:
    """Parse ``SCENE|OUTPUT|STATE`` from one visibly identified Runway card."""
    parts = [part.strip() for part in value.split('|')]
    if len(parts) != 3 or not parts[0] or not parts[2]:
        raise ValueError(
            f'QUEUE_JOB_FORMAT_REQUIRED: use SCENE|OUTPUT|STATE, got {value!r}')
    state = _normalize_queue_state(parts[2])
    if state not in QUEUE_JOB_STATES:
        raise ValueError(
            f'QUEUE_JOB_STATE_INVALID: {state}; allowed={sorted(QUEUE_JOB_STATES)}')
    output_index: int | str | None
    if not parts[1] or parts[1] == '-':
        output_index = None
    elif parts[1].isdigit():
        output_index = int(parts[1])
    else:
        output_index = parts[1]
    return {
        'scene_id': parts[0],
        'output_index': output_index,
        'visible_state': state,
    }


def parse_processed_job(value: str) -> dict:
    """Parse ``SCENE|OUTPUT`` for one downloaded/QC'd/registered settled card."""
    parts = [part.strip() for part in value.split('|')]
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError(
            f'QUEUE_PROCESSED_JOB_FORMAT_REQUIRED: use SCENE|OUTPUT, got {value!r}')
    output_index: int | str = int(parts[1]) if parts[1].isdigit() else parts[1]
    return {'scene_id': parts[0], 'output_index': output_index}


def _queue_job_key(row: dict) -> str:
    return f'{row.get("scene_id")}|{row.get("output_index")}'


def _queue_signature(jobs: list[dict]) -> str:
    rows = sorted(
        f'{row["scene_id"]}|{row.get("output_index")}|{row["visible_state"]}'
        for row in jobs if row['visible_state'] in INFLIGHT_STATES)
    return prompt_sha256('\n'.join(rows)) if rows else ''


def _queue_verdict(*, inflight: list[dict], settled: list[dict], armed: str | None,
                   shelf_state: str, stalled: bool,
                   queue_target: int = QUEUE_TARGET_DEFAULT) -> tuple[str, str, bool, bool]:
    """Return verdict, next action, wake-required, terminal/may-stop."""
    if stalled:
        return (
            'BLOCKED_RUNWAY_QUEUE_STALLED',
            'Stop rearming this external queue after three unchanged In queue wakes; resume on visible change.',
            False,
            True,
        )
    active_count = len(inflight)
    if shelf_state == 'AVAILABLE':
        if active_count < queue_target:
            action = (
                'Refill the free provider slot first: submit the already armed package now, '
                'then queue-cycle after the accepted card.'
                if armed else
                'Refill the free provider slot first: arm the next eligible package, submit it, '
                'then queue-cycle after the accepted card.'
            )
            return 'FILL_FREE_SLOT_NOW', action, False, False
        if settled:
            return (
                'PROCESS_SETTLED_CARD_NOW',
                'Both provider slots are active; now download/verify/QC/register settled cards '
                'and mark each with --processed-job before the next cycle.',
                False,
                False,
            )
        if not armed:
            return (
                'ARM_NEXT_BEFORE_WAIT',
                'Attach/verify the next eligible package before entering any wait.',
                False,
                False,
            )
        return (
            'QUEUE_FULL_WAKE_REQUIRED',
            'queue-cycle will hold this same foreground Codex task; after it returns, re-read the board.',
            True,
            False,
        )
    if settled:
        return (
            'PROCESS_SETTLED_CARD_NOW',
            'No eligible refill remains; download/verify/QC/register settled cards and mark '
            'each with --processed-job before the next cycle.',
            False,
            False,
        )
    if active_count:
        return (
            'DRAIN_QUEUE_WAKE_REQUIRED',
            'The generation shelf is closed but active cards remain; queue-cycle must keep draining them.',
            True,
            False,
        )
    if shelf_state == 'EXHAUSTED':
        return 'SHELF_EXHAUSTED', 'No active cards and no eligible package remain.', False, True
    return (
        'ALL_REMAINING_BLOCKED',
        'No active cards remain; report every blocked package and its reason.',
        False,
        True,
    )


def build_queue_runtime(
    project: Path,
    jobs: list[dict],
    *,
    armed: str | None,
    next_eligible: str | None,
    shelf_state: str,
    generate_state: str,
    from_wake: bool = False,
    processed_jobs: list[dict] | None = None,
    capacity_limit: int | None = None,
    capacity_evidence: str | None = None,
    now: dt.datetime | None = None,
) -> dict:
    """Build a deterministic queue decision from one visible-board observation."""
    project = project.expanduser().resolve()
    if shelf_state not in {'AVAILABLE', 'EXHAUSTED', 'ALL_BLOCKED'}:
        raise ValueError(f'QUEUE_SHELF_STATE_INVALID: {shelf_state}')
    scenes = [row['scene_id'] for row in jobs]
    if len(scenes) != len(set(scenes)):
        raise ValueError('QUEUE_DUPLICATE_SCENE: two active slots must contain different scenes')
    outputs = [str(row['output_index']) for row in jobs if row.get('output_index') is not None]
    if len(outputs) != len(set(outputs)):
        raise ValueError('QUEUE_DUPLICATE_OUTPUT_INDEX')
    inflight = [row for row in jobs if row['visible_state'] in INFLIGHT_STATES]
    if len(inflight) > QUEUE_TARGET_DEFAULT:
        raise ValueError(
            f'QUEUE_TARGET_EXCEEDED: observed={len(inflight)} target={QUEUE_TARGET_DEFAULT}')
    if armed and armed in {row['scene_id'] for row in inflight}:
        raise ValueError(f'QUEUE_ARMED_SCENE_ALREADY_INFLIGHT: {armed}')

    path = queue_runtime_path(project)
    previous = _json_file(path)
    previous_target = int(previous.get('queue_target') or QUEUE_TARGET_DEFAULT)
    if capacity_limit not in {None, 1, 2}:
        raise ValueError('QUEUE_CAPACITY_LIMIT_INVALID: expected 1 or 2')
    if capacity_limit == 1 and capacity_evidence != 'RUNWAY_QUEUE_CAPACITY_TOAST':
        raise ValueError(
            'QUEUE_CAPACITY_ONE_REQUIRES_TOAST_EVIDENCE: pass '
            '--capacity-evidence RUNWAY_QUEUE_CAPACITY_TOAST only after the exact visible toast')
    if len(inflight) >= 2:
        effective_target = 2
        effective_capacity_evidence = 'TWO_DISTINCT_CARDS_VISIBLE'
    elif capacity_limit == 1:
        effective_target = 1
        effective_capacity_evidence = capacity_evidence
    elif capacity_limit == 2:
        effective_target = 2
        effective_capacity_evidence = capacity_evidence or 'OPERATOR_CONFIRMED_TWO_SLOT_RETRY'
    elif not inflight and previous_target == 1:
        effective_target = 2
        effective_capacity_evidence = 'AUTO_RETRY_TWO_AFTER_QUEUE_EMPTY'
    else:
        effective_target = previous_target
        effective_capacity_evidence = previous.get('capacity_evidence')
    observed_history = {
        str(row.get('scene_id')): row
        for row in (previous.get('observed_job_history') or [])
        if isinstance(row, dict) and row.get('scene_id')
    }
    observation_time = (now or dt.datetime.now().astimezone()).isoformat(timespec='seconds')
    for row in jobs:
        scene = str(row['scene_id'])
        prior = observed_history.get(scene) or {}
        observed_history[scene] = {
            'scene_id': scene,
            'first_seen_at': prior.get('first_seen_at') or observation_time,
            'last_seen_at': observation_time,
            'last_output_index': row.get('output_index'),
            'last_visible_state': row.get('visible_state'),
        }
    previous_processed = {
        _queue_job_key(row): row
        for row in (previous.get('processed_settled_jobs') or [])
        if isinstance(row, dict)
    }
    visible_settled = [row for row in jobs if row['visible_state'] in SETTLED_STATES]
    current_visible_keys = {_queue_job_key(row) for row in visible_settled}
    for row in processed_jobs or []:
        key = _queue_job_key(row)
        if key not in current_visible_keys:
            raise ValueError(
                f'QUEUE_PROCESSED_JOB_NOT_VISIBLE_SETTLED: {key}; re-read the board and '
                'only acknowledge a currently visible settled card')
        previous_processed[key] = {
            **row,
            'processed_at': (now or dt.datetime.now().astimezone()).isoformat(timespec='seconds'),
        }
    processed_keys = set(previous_processed)
    settled = [row for row in visible_settled if _queue_job_key(row) not in processed_keys]

    status = _json_file(Path(_project_seedance_sources(project)['metadata_dir']) / 'status.json')
    status_attested = {
        str(block).strip() for block in (status.get('attested_blocks') or [])
        if str(block).strip()
    }
    status_blocked = {
        str(block).strip() for block in (status.get('blocked_attested_blocks') or [])
        if str(block).strip()
    }
    represented = set(observed_history)
    represented.update(filter(None, (armed, next_eligible)))
    unrepresented_attested = sorted(status_attested - status_blocked - represented)
    if unrepresented_attested and shelf_state != 'AVAILABLE':
        raise ValueError(
            'QUEUE_SHELF_CONTRADICTS_ATTESTED_STATUS: status.json declares eligible '
            f'attested blocks {unrepresented_attested}, so shelf_state={shelf_state} is invalid; '
            'pass AVAILABLE with --next-eligible/--armed or record each block under '
            'blocked_attested_blocks with evidence')
    signature = _queue_signature(inflight)
    prior_signature = str(previous.get('observation_signature') or '')
    previous_wake = previous.get('wake') if isinstance(previous.get('wake'), dict) else {}
    pending_wait_alive = (
        previous_wake.get('pending') is True
        and _pid_running(previous_wake.get('wait_pid'))
    )
    elapsed_unconsumed = _wait_elapsed_unconsumed(previous_wake)
    if pending_wait_alive:
        raise ValueError(
            'QUEUE_FOREGROUND_WAIT_STILL_RUNNING: do not observe or replace the '
            'queue from a second controller')
    if elapsed_unconsumed and not from_wake:
        raise ValueError(
            'QUEUE_WAIT_ELAPSED_UNCONSUMED: re-read the visible Runway board and '
            'run queue-cycle --from-wake before any new wait or ordinary sync')
    if from_wake and not elapsed_unconsumed:
        raise ValueError(
            'QUEUE_FROM_WAKE_REQUIRES_ELAPSED_WAIT: --from-wake may only consume '
            'a recorded elapsed/interrupted foreground wait')
    unchanged = int(previous.get('unchanged_in_queue_wakes') or 0)
    all_in_queue = bool(inflight) and all(row['visible_state'] == 'IN_QUEUE' for row in inflight)
    if signature != prior_signature:
        unchanged = 0
    elif from_wake:
        unchanged = unchanged + 1 if all_in_queue else 0
    stalled = unchanged >= 3 and not settled

    verdict, next_action, wake_required, may_stop = _queue_verdict(
        inflight=inflight,
        settled=settled,
        armed=armed,
        shelf_state=shelf_state,
        stalled=stalled,
        queue_target=effective_target,
    )
    if verdict == 'FILL_FREE_SLOT_NOW' and _normalize_queue_state(generate_state) != 'BLUE':
        next_action = (
            'A provider slot may be free but Generate is not visibly eligible. '
            'Inspect the armed reference/settings error or exact capacity toast; '
            'repair and re-run preflight. Do not click or infer queue full from gray alone.')
    now = now or dt.datetime.now().astimezone()
    wake = {
        'pending': False,
        'due_at': None,
        'registered_at': previous_wake.get('registered_at'),
        'wait_pid': None,
        'wait_started_at': previous_wake.get('wait_started_at'),
        'last_elapsed_at': previous_wake.get('last_elapsed_at'),
        'elapsed_count': int(previous_wake.get('elapsed_count') or 0),
        'elapsed_unconsumed': False,
        'last_consumed_at': previous_wake.get('last_consumed_at'),
        'consumed_count': int(previous_wake.get('consumed_count') or 0),
        'last_fired_at': previous_wake.get('last_fired_at'),
        'fired_count': int(previous_wake.get('fired_count') or 0),
        'last_result': previous_wake.get('last_result'),
    }
    if from_wake:
        wake.update({
            'last_consumed_at': now.isoformat(timespec='seconds'),
            'consumed_count': int(previous_wake.get('consumed_count') or 0) + 1,
            'last_fired_at': now.isoformat(timespec='seconds'),
            'last_result': 'WAIT_CONSUMED_BY_VISIBLE_BOARD_RECHECK',
        })
    return {
        'contract_version': QUEUE_RUNTIME_VERSION,
        'updated_at': now.isoformat(timespec='seconds'),
        'project': str(project),
        'queue_target': effective_target,
        'default_queue_target': QUEUE_TARGET_DEFAULT,
        'capacity_evidence': effective_capacity_evidence,
        'jobs': jobs,
        'inflight_jobs': inflight,
        'settled_jobs': settled,
        'visible_settled_jobs': visible_settled,
        'processed_settled_jobs': sorted(previous_processed.values(), key=_queue_job_key),
        'observed_job_history': sorted(observed_history.values(), key=lambda row: row['scene_id']),
        'settled_backlog_count': len(settled),
        'active_count': len(inflight),
        'armed_scene_id': armed,
        'next_eligible_package': next_eligible or armed,
        'shelf_state': shelf_state,
        'generate_state': _normalize_queue_state(generate_state),
        'observation_signature': signature,
        'observed_from_wake': bool(from_wake),
        'unchanged_in_queue_wakes': unchanged,
        'verdict': verdict,
        'next_action': next_action,
        'wake_required': wake_required,
        'may_stop': may_stop,
        'wake': wake,
    }


def sync_queue_runtime(
    project: Path,
    jobs: list[dict],
    **kwargs,
) -> dict:
    runtime = build_queue_runtime(project, jobs, **kwargs)
    _write_json_atomic(queue_runtime_path(project), runtime)
    return runtime


def _attested_prompts(metadata_dir: Path) -> list[dict]:
    attested = []
    prompt_dir = metadata_dir / 'prompts'
    for path in sorted(prompt_dir.glob('*_attestation.json')):
        row = _json_file(path)
        verdict = str(row.get('verdict') or row.get('status') or '').upper()
        if verdict not in {'ATTESTED', 'ATTESTED_READY', 'PASS'}:
            continue
        attested.append({
            'block_id': row.get('block_id'),
            'attestation': str(path),
            'pack_sha256': row.get('pack_sha256'),
            'prompt_sha256': row.get('prompt_sha256'),
        })
    return attested


def build_resume_contract(project: Path) -> dict:
    """Describe one foreground wait; never schedules or re-enters Codex."""
    project = project.expanduser().resolve()
    source = _project_seedance_sources(project)
    state_path = Path(source['state_path'])
    manifest_path = Path(source['manifest_path']) if source['manifest_path'] else None
    metadata_dir = Path(source['metadata_dir'])
    manifest = _json_file(manifest_path) if manifest_path else {}
    state = _json_file(state_path)
    attested = _attested_prompts(metadata_dir)
    runtime_path = queue_runtime_path(project)
    queue_runtime = _json_file(runtime_path)
    snapshot = {
        'layout': source['layout'],
        'state_path': str(state_path),
        'state_sha256': prompt_sha256(state_path.read_text(encoding='utf-8')),
        'manifest_path': str(manifest_path) if manifest_path else None,
        'manifest_sha256': (
            prompt_sha256(manifest_path.read_text(encoding='utf-8'))
            if manifest_path else None
        ),
        'queue_runtime_path': str(runtime_path),
        'queue_runtime_sha256': (
            prompt_sha256(runtime_path.read_text(encoding='utf-8'))
            if runtime_path.is_file() else None
        ),
        'queue_verdict': queue_runtime.get('verdict'),
        'active_count': queue_runtime.get('active_count'),
        'armed_scene_id': queue_runtime.get('armed_scene_id'),
        'seedance_lane_status': (
            ((state.get('lanes') or {}).get('seedance') or {}).get('status')
            if source['layout'] == 'runtime_v4'
            else state.get('terminal_state') or state.get('status')
        ),
        'media_schema_version': manifest.get('media_schema_version'),
        'attested_prompt_count': len(attested),
    }
    contract = {
        'contract_version': RESUME_CONTRACT_VERSION,
        'created_at': dt.datetime.now().astimezone().isoformat(timespec='seconds'),
        'project': str(project),
        'delay_seconds': WAKE_DELAY_SECONDS,
        'same_codex_task_only': True,
        'same_runway_browser_only': True,
        'continuation_mode': 'FOREGROUND_TOOL_LONG_POLL_ONLY',
        'automatic_model_reentry': False,
        'external_scheduler': False,
        'additional_agents': 0,
        'resident_processes': 0,
        'max_pending_wakeups': 1,
        'snapshot': snapshot,
        'queue_runtime': queue_runtime or None,
        'attested_prompts': attested,
        # This is output guidance after the foreground tool call returns. It is
        # not an automation prompt and writing this file schedules nothing.
        'wait_return_instruction_ko': WAIT_RETURN_INSTRUCTION_KO,
        'stop_conditions': [
            'QUEUE_EMPTY_AND_SHELF_EXHAUSTED',
            'QUEUE_EMPTY_AND_ALL_REMAINING_BLOCKED',
            'USER_ACTION_REQUIRED',
            'BLOCKED_RUNWAY_QUEUE_STALLED',
        ],
    }
    canonical = json.dumps(contract, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    contract['contract_sha256'] = prompt_sha256(canonical)
    return contract


def cmd_resume_contract(args) -> int:
    project = Path(args.project)
    try:
        contract = build_resume_contract(project)
    except ValueError as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}, ensure_ascii=False))
        return 1
    output = (Path(args.write).expanduser().resolve() if args.write else
              resume_contract_path(project))
    _write_json_atomic(output, contract)
    print(json.dumps({**contract, 'contract_path': str(output)}, ensure_ascii=False, indent=2))
    return 0


def run_bounded_queue_wake(
    project: Path,
    *,
    sleeper=time.sleep,
    delay_seconds: int = WAKE_DELAY_SECONDS,
    now: dt.datetime | None = None,
) -> dict:
    """Sleep once in one foreground tool session; never claim model re-entry.

    The function can prove that the process waited. It cannot prove that Codex
    consumed the tool result. Therefore elapsed time remains a continuation
    debt until queue-cycle --from-wake records a fresh visible-board observation.
    """
    project = project.expanduser().resolve()
    if read_queue_mode(project)['mode'] == 'scheduled':
        raise ValueError('SCHEDULED_MODE_FORBIDS_FOREGROUND_WAIT: use one native scheduled check, not sleep')
    path = queue_runtime_path(project)
    runtime = _json_file(path)
    if runtime.get('contract_version') != QUEUE_RUNTIME_VERSION:
        raise ValueError('QUEUE_SYNC_REQUIRED_BEFORE_WAIT')
    if runtime.get('verdict') not in WAKE_REQUIRED_VERDICTS:
        raise ValueError(
            f'QUEUE_WAIT_NOT_ALLOWED: verdict={runtime.get("verdict")} '
            '— fill/process/arm the board instead of waiting')
    if runtime.get('shelf_state') == 'AVAILABLE' and not runtime.get('armed_scene_id'):
        raise ValueError('QUEUE_WAIT_REQUIRES_ARMED_NEXT_PACKAGE')
    wake = runtime.get('wake') if isinstance(runtime.get('wake'), dict) else {}
    if _wait_elapsed_unconsumed(wake):
        raise ValueError(
            'QUEUE_WAIT_ELAPSED_UNCONSUMED: consume the previous wait with a '
            'visible board recheck and queue-cycle --from-wake')
    if wake.get('pending'):
        raise ValueError(f'QUEUE_WAKE_ALREADY_PENDING: due_at={wake.get("due_at")}')

    now = now or dt.datetime.now().astimezone()
    due = now + dt.timedelta(seconds=delay_seconds)
    runtime['wake'] = {
        **wake,
        'pending': True,
        'registered_at': now.isoformat(timespec='seconds'),
        'due_at': due.isoformat(timespec='seconds'),
        'wait_pid': os.getpid(),
        'wait_started_at': now.isoformat(timespec='seconds'),
        'elapsed_unconsumed': False,
        'last_result': 'WAITING_IN_FOREGROUND_TOOL_SESSION',
    }
    runtime['updated_at'] = now.isoformat(timespec='seconds')
    _write_json_atomic(path, runtime)
    contract = build_resume_contract(project)
    _write_json_atomic(resume_contract_path(project), contract)
    try:
        sleeper(delay_seconds)
    except BaseException:
        interrupted = _json_file(path) or runtime
        interrupted_wake = interrupted.get('wake') or {}
        interrupted['wake'] = {
            **interrupted_wake,
            'pending': False,
            'due_at': None,
            'wait_pid': None,
            'elapsed_unconsumed': True,
            'last_result': 'INTERRUPTED_RECHECK_REQUIRED',
        }
        _write_json_atomic(path, interrupted)
        raise

    elapsed_at = now + dt.timedelta(seconds=delay_seconds)
    elapsed = _json_file(path) or runtime
    elapsed_wake = elapsed.get('wake') if isinstance(elapsed.get('wake'), dict) else {}
    elapsed['wake'] = {
        **elapsed_wake,
        'pending': False,
        'due_at': None,
        'wait_pid': None,
        'last_elapsed_at': elapsed_at.isoformat(timespec='seconds'),
        'elapsed_count': int(elapsed_wake.get('elapsed_count') or 0) + 1,
        'elapsed_unconsumed': True,
        'last_result': 'WAIT_ELAPSED_RECHECK_NOT_CONSUMED',
    }
    elapsed['updated_at'] = elapsed_at.isoformat(timespec='seconds')
    _write_json_atomic(path, elapsed)
    return {
        'ok': True,
        'verdict': 'WAIT_ELAPSED_RECHECK_BOARD_NOW',
        'project': str(project),
        'queue_runtime_path': str(path),
        'resume_contract_path': str(resume_contract_path(project)),
        'delay_seconds': delay_seconds,
        'next_action': (
            'This timer did not schedule or wake Codex. The owning turn must now '
            're-read the visible Runway board, run queue-cycle --from-wake, and '
            'fill every free slot before another queue-wait.'
        ),
    }


def cmd_queue_sync(args) -> int:
    try:
        jobs = [parse_queue_job(value) for value in (args.job or [])]
        runtime = sync_queue_runtime(
            Path(args.project),
            jobs,
            armed=args.armed,
            next_eligible=args.next_eligible,
            shelf_state=args.shelf_state,
            generate_state=args.generate_state,
            from_wake=args.from_wake,
            processed_jobs=[parse_processed_job(value) for value in (args.processed_job or [])],
            capacity_limit=args.capacity_limit,
            capacity_evidence=args.capacity_evidence,
        )
    except ValueError as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps({
        'ok': True,
        **runtime,
        'queue_runtime_path': str(queue_runtime_path(Path(args.project))),
    }, ensure_ascii=False, indent=2))
    return 0


def run_queue_cycle(
    project: Path,
    jobs: list[dict],
    *,
    sleeper=time.sleep,
    delay_seconds: int = WAKE_DELAY_SECONDS,
    **sync_kwargs,
) -> dict:
    """Checkpoint one visible board using the persisted continuation choice.

    This removes the discretionary gap between ``queue-sync`` and
    ``queue-wait`` in foreground mode. Scheduled checks return without sleep;
    neither path creates a scheduler. An elapsed foreground wait still requires
    a fresh visible board read in the owning Codex turn.
    """
    mode = read_queue_mode(project)
    runtime = sync_queue_runtime(project, jobs, **sync_kwargs)
    if mode['mode'] == 'scheduled':
        return {
            'ok': True, 'verdict': 'SCHEDULED_CHECKPOINT_NO_WAIT',
            'wait_started': False, 'scheduler_created': False,
            'registration_verified': False, 'queue_runtime': runtime,
            'next_action': 'Inspect native app registration/run evidence; this call only checkpoints one observation. Never start a foreground wait.',
        }
    if not runtime.get('wake_required'):
        return {
            'ok': True,
            'verdict': runtime.get('verdict'),
            'wait_started': False,
            'queue_runtime': runtime,
        }
    wait_result = run_bounded_queue_wake(
        project, sleeper=sleeper, delay_seconds=delay_seconds)
    return {
        'ok': True,
        'verdict': wait_result['verdict'],
        'wait_started': True,
        'queue_verdict_before_wait': runtime.get('verdict'),
        'queue_runtime': runtime,
        'wait_result': wait_result,
    }


def queue_mode_path(project: Path) -> Path:
    return Path(_project_seedance_sources(project)['metadata_dir']) / 'continuation_mode.json'


def read_queue_mode(project: Path) -> dict:
    """A user-intent checkpoint, never an automation registration receipt."""
    path = queue_mode_path(project)
    if not path.exists():
        monitoring = _json_file(path.with_name('status.json')).get('monitoring') or {}
        if str(monitoring.get('mode', '')).startswith('SCHEDULED'):
            raise ValueError('QUEUE_SCHEDULED_REQUEST_REQUIRES_MODE_CHECKPOINT: do not fall back to foreground')
        return {'mode': 'foreground', 'interval_minutes': 15, 'source': 'legacy_default'}
    value = _json_file(path)
    if (value.get('mode') not in {'foreground', 'scheduled'}
            or value.get('project') != str(project.expanduser().resolve())
            or value.get('interval_minutes') not in {15, 20}):
        raise ValueError('QUEUE_MODE_INVALID: repair explicit selection; never fall back to sleep')
    evidence = Path(value.get('request_evidence') or '').resolve()
    if (not evidence.is_relative_to(project.expanduser().resolve())
            or not evidence.is_file() or not evidence.stat().st_size
            or media_registry.sha256(evidence) != value.get('request_evidence_sha256')):
        raise ValueError('QUEUE_MODE_EVIDENCE_CHANGED_OR_MISSING')
    return value


def select_queue_mode(project: Path, mode: str, evidence: Path, interval_minutes: int = 20) -> dict:
    project = project.expanduser().resolve()
    if mode not in {'foreground', 'scheduled'} or interval_minutes not in {15, 20}:
        raise ValueError('QUEUE_MODE_OR_INTERVAL_INVALID')
    evidence = evidence.expanduser().resolve()
    if not evidence.is_relative_to(project) or not evidence.is_file() or not evidence.stat().st_size:
        raise ValueError('QUEUE_MODE_PROJECT_USER_REQUEST_EVIDENCE_REQUIRED')
    wake = (_json_file(queue_runtime_path(project)).get('wake') or {})
    if wake.get('pending') and _pid_running(wake.get('wait_pid')):
        raise ValueError('QUEUE_FOREGROUND_WAIT_STILL_RUNNING: stop and consume the owning tool session first')
    value = {
        'project': str(project), 'mode': mode,
        'interval_minutes': interval_minutes if mode == 'scheduled' else 15,
        'request_evidence': str(evidence), 'request_evidence_sha256': media_registry.sha256(evidence),
        'selected_at': dt.datetime.now().astimezone().isoformat(timespec='seconds'),
        'scheduler_created': False, 'registration_verified': False,
    }
    _write_json_atomic(queue_mode_path(project), value)
    return value


def audit_production_state(project: Path) -> dict:
    """Read-only consistency check, not a replacement for GUI, ffprobe or playback QC."""
    project = project.expanduser().resolve()
    metadata = Path(_project_seedance_sources(project)['metadata_dir'])
    queue = _json_file(queue_runtime_path(project))
    documents = {name: _json_file(path) for name, path in {
        'state': project / 'state.json', 'manifest': project / 'manifest.json',
        'lane': metadata / 'status.json', 'qc': project / 'lanes/seedance_qc/status.json',
    }.items()}
    issues = []
    expected = {str(j['scene_id']): j['visible_state'] for j in queue.get('jobs', [])}
    for name in ('state', 'manifest', 'lane', 'qc'):
        doc = documents[name]
        reported = {str(j.get('block_id') or j.get('scene_id')): j.get('visible_state')
                    for j in doc.get('provider_jobs', [])}
        if name != 'qc' and expected and reported != expected:
            issues.append(f'QUEUE_JOB_STATE_MISMATCH:{name}')
        blocker = doc.get('blocker') or {}
        code = blocker.get('code', '') if isinstance(blocker, dict) else str(blocker)
        if (expected and queue.get('shelf_state') == 'EXHAUSTED'
                and ('NATIVE_FILE' in code or 'NATIVE_CONTROL' in code)):
            issues.append(f'STALE_PRE_GENERATION_BLOCKER:{name}')
    reported_statuses = [documents[n].get('lanes', {}).get('seedance', {}).get('status')
                         for n in ('state', 'manifest')] + [documents['lane'].get('status')]
    if len(set(filter(None, reported_statuses))) > 1:
        issues.append('LANE_STATUS_ROLLUP_MISMATCH')
    monitoring = documents['lane'].get('monitoring') or {}
    def has_evidence(field):
        value = monitoring.get(field)
        if not isinstance(value, str) or not value:
            return False
        file = Path(value).expanduser().resolve()
        return file.is_relative_to(project) and file.is_file() and file.stat().st_size > 0
    if monitoring.get('scheduled_run_verified') and not monitoring.get('automation_id'):
        issues.append('SCHEDULE_RUN_CLAIM_WITHOUT_AUTOMATION_ID')
    if monitoring.get('scheduled_run_verified') and not has_evidence('first_run_evidence'):
        issues.append('SCHEDULE_RUN_CLAIM_WITHOUT_RUN_EVIDENCE')
    if str(monitoring.get('registration_status', '')).upper() in {'ACTIVE', 'REGISTERED'}:
        if not monitoring.get('automation_id') or not has_evidence('registration_evidence'):
            issues.append('SCHEDULE_REGISTRATION_CLAIM_WITHOUT_RECEIPT')
    verified, approved = 0, 0
    registry = media_registry.db_path(project)
    if registry.is_file():
        try:
            with sqlite3.connect(registry.as_uri() + '?mode=ro', uri=True) as conn:
                rows = conn.execute("SELECT current_path, sha256, state FROM assets WHERE kind='video' AND active=1").fetchall()
            for filename, digest, state in rows:
                file = Path(filename).resolve()
                if (file.is_relative_to(project / 'media') and file.is_file()
                        and file.stat().st_size > 0 and media_registry.sha256(file) == digest):
                    verified += 1
                    approved += state == 'approved'
                else:
                    issues.append('REGISTERED_VIDEO_MISSING_OR_CHANGED')
        except sqlite3.Error:
            issues.append('REGISTRY_UNREADABLE')
    if 'DONE' in reported_statuses and not verified:
        issues.append('PRODUCTION_DONE_WITHOUT_REGISTERED_VIDEO')
    if documents['qc'].get('status') in {'DONE', 'PASS'} and not approved:
        issues.append('QC_DONE_WITHOUT_APPROVED_VIDEO')
    return {
        'read_only': True, 'issues': sorted(set(issues)),
        'ui_completed_cards': sum(j.get('visible_state') == 'COMPLETED' for j in queue.get('jobs', [])),
        'verified_local_video_files': verified, 'approved_local_video_files': approved,
        'reported_monitoring': monitoring, 'native_schedule_registration_verified_by_this_audit': False,
        'playback_qc_verified_by_this_audit': False,
    }


def cmd_queue_mode(args) -> int:
    try:
        result = select_queue_mode(Path(args.project), args.mode, Path(args.request_evidence), args.interval_minutes)
    except (OSError, ValueError) as exc:
        print(json.dumps({'ok': False, 'error': str(exc)})); return 1
    print(json.dumps({'ok': True, **result}, ensure_ascii=False, indent=2)); return 0


def cmd_queue_cycle(args) -> int:
    try:
        jobs = [parse_queue_job(value) for value in (args.job or [])]
        result = run_queue_cycle(
            Path(args.project),
            jobs,
            armed=args.armed,
            next_eligible=args.next_eligible,
            shelf_state=args.shelf_state,
            generate_state=args.generate_state,
            from_wake=args.from_wake,
            processed_jobs=[parse_processed_job(value) for value in (args.processed_job or [])],
            capacity_limit=args.capacity_limit,
            capacity_evidence=args.capacity_evidence,
        )
    except ValueError as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_settings_verify(args) -> int:
    try:
        aside_bridge.require_project(Path(args.project))
        rc, _out, err = browser_js('true')
        if rc:
            raise ValueError(err)
        result = verify_attested_generation_settings(
            Path(args.project), args.block,
            visible_model=args.visible_model,
            duration_sec=args.duration_sec,
            duration_source=args.duration_source,
            source_video=Path(args.source_video) if args.source_video else None)
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_queue_wait(args) -> int:
    try:
        result = run_bounded_queue_wake(Path(args.project))
    except ValueError as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def evaluate_queue_exit(project: Path) -> dict:
    """Return whether the owning Seedance turn may emit a final response.

    This is deliberately read-only.  It converts the existing ``may_stop``
    invariant into an explicit pre-final gate so a prose status such as
    "continue next turn" cannot disguise an abandoned active queue.
    """
    project = project.expanduser().resolve()
    runtime = _json_file(queue_runtime_path(project))
    if runtime.get('contract_version') != QUEUE_RUNTIME_VERSION:
        metadata = Path(_project_seedance_sources(project)['metadata_dir'])
        status = _json_file(metadata / 'status.json')
        blocked = status.get('preproduction_block') or {}
        attested = status.get('attested_blocks')
        held = status.get('blocked_attested_blocks')
        # This is not a queue observation. Permit only the narrow case before
        # any binding/transaction, never a lost or corrupt queue's replacement.
        production_evidence = (
            (metadata / 'aside_binding.json').exists()
            or (metadata / 'recovery_state.json').exists()
            or (metadata / 'recovery_events.jsonl').exists()
            or any((metadata / 'recovery').glob('*.json'))
            or any((metadata / 'evidence').glob('*settings_preflight.json'))
        )
        if (
            not queue_runtime_path(project).exists()
            and not production_evidence
            and status.get('status') == 'BLOCKED'
            and status.get('production_started') is False
            and status.get('provider_jobs') == []
            and isinstance(attested, list) and attested
            and isinstance(held, list) and sorted(attested) == sorted(held)
            and isinstance(blocked, dict)
            and blocked.get('code') == 'BLOCKED_RUNWAY_SESSION_SELECTION_REQUIRED'
            and str(blocked.get('evidence') or '').strip()
            and str(blocked.get('required_user_action') or '').strip()
        ):
            return {
                'ok': True,
                'verdict': 'QUEUE_EXIT_ALLOWED_PREPRODUCTION_BLOCK',
                'project': str(project),
                'may_stop': True,
                'active_count': 0,
                'queue_observation': False,
                'next_action': blocked['required_user_action'],
            }
        return {
            'ok': False,
            'verdict': 'QUEUE_EXIT_REFUSED_SYNC_REQUIRED',
            'project': str(project),
            'next_action': 'Re-read the visible Runway board and run queue-cycle.',
        }
    wake = runtime.get('wake') if isinstance(runtime.get('wake'), dict) else {}
    live_wait = wake.get('pending') and _pid_running(wake.get('wait_pid'))
    mode = read_queue_mode(project)
    if mode['mode'] == 'scheduled' and not live_wait and not _wait_elapsed_unconsumed(wake):
        return {
            'ok': True, 'verdict': 'QUEUE_EXIT_ALLOWED_SCHEDULED_CHECKPOINT',
            'project': str(project), 'active_count': int(runtime.get('active_count') or 0),
            'settled_backlog_count': int(runtime.get('settled_backlog_count') or 0),
            'production_complete': False, 'registration_verified': False,
            'next_action': 'Verify the native schedule separately; preserve outstanding download/QC work. This exit is not media completion.',
        }
    empty = not runtime.get('active_count') and not runtime.get('settled_backlog_count')
    terminal = empty and runtime.get('verdict') in {'SHELF_EXHAUSTED', 'ALL_REMAINING_BLOCKED'}
    stalled = (runtime.get('verdict') == 'BLOCKED_RUNWAY_QUEUE_STALLED'
               and int(runtime.get('unchanged_in_queue_wakes') or 0) >= 3
               and bool(runtime.get('inflight_jobs')) and not runtime.get('settled_backlog_count')
               and all(j.get('visible_state') == 'IN_QUEUE' for j in runtime['inflight_jobs']))
    interruption = runtime.get('interruption') or {}
    interrupted = (runtime.get('verdict') == 'BROKEN_FOREGROUND_CONTINUATION'
                   and interruption.get('code') == 'BROKEN_FOREGROUND_CONTINUATION'
                   and bool(interruption.get('evidence')) and bool(interruption.get('at')))
    if runtime.get('may_stop') is True and not live_wait and (terminal or stalled or interrupted):
        return {
            'ok': True,
            'verdict': 'QUEUE_EXIT_ALLOWED',
            'project': str(project),
            'queue_verdict': runtime.get('verdict'),
            'active_count': int(runtime.get('active_count') or 0),
        }
    if wake.get('pending') and _pid_running(wake.get('wait_pid')):
        next_action = (
            'Keep this same turn attached to the live queue-wait tool session; '
            'do not emit a final response.')
    elif _wait_elapsed_unconsumed(wake):
        next_action = (
            'Re-read the visible board now and consume the elapsed wait with '
            'queue-cycle --from-wake; do not emit a final response.')
    elif runtime.get('wake_required'):
        next_action = (
            'Run queue-cycle from the fresh visible board; it will enter the next '
            'sequential foreground wait. One pending wait at a time is the limit.')
    else:
        next_action = str(runtime.get('next_action') or 'Continue the queue controller cycle.')
    return {
        'ok': False,
        'verdict': 'QUEUE_EXIT_REFUSED_NONTERMINAL',
        'project': str(project),
        'queue_verdict': runtime.get('verdict'),
        'active_count': int(runtime.get('active_count') or 0),
        'unchanged_in_queue_wakes': int(runtime.get('unchanged_in_queue_wakes') or 0),
        'may_stop': False,
        'next_action': next_action,
    }


def cmd_queue_exit_check(args) -> int:
    try:
        result = evaluate_queue_exit(Path(args.project))
    except (OSError, ValueError) as exc:
        print(json.dumps({'ok': False, 'error': str(exc)})); return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['ok'] else 1


def diagnose_queue(project: Path) -> dict:
    """Model-independent observation of local continuation evidence, not a watcher.

    A live PID proves only a process, not attachment to an owning Codex tool
    session. No scheduler/tool/model availability is inferred from JSON text.
    """
    project = project.expanduser().resolve()
    path = queue_runtime_path(project)
    runtime = _json_file(path)
    wake = runtime.get('wake') if isinstance(runtime.get('wake'), dict) else {}
    exit_gate = evaluate_queue_exit(project)
    next_action = exit_gate.get('next_action') or 'No remaining queue action.'
    fresh_board = False
    if not path.exists():
        state = ('PREPRODUCTION_USER_ACTION_REQUIRED' if exit_gate.get('ok')
                 else 'NO_QUEUE_OBSERVATION')
        if state == 'NO_QUEUE_OBSERVATION':
            next_action = 'Verify intended session, read its visible board, then queue-cycle; a resume contract alone starts nothing.'
            fresh_board = True
    elif runtime.get('contract_version') != QUEUE_RUNTIME_VERSION:
        state = 'INVALID_QUEUE_RECORD'
        next_action = 'Preserve the invalid record and recover from the exact visible board; do not claim any watcher is running.'
        fresh_board = True
    elif wake.get('pending'):
        if _pid_running(wake.get('wait_pid')):
            state = 'WAIT_PROCESS_ALIVE'
            next_action = 'Keep the owning exec tool session attached with write_stdin until completion. wait_pid is NOT a tool session_id. Do not start a second wait or finish the turn.'
        else:
            state = 'BROKEN_FOREGROUND_CONTINUATION'
            next_action = 'Record the lost wait/tool session, re-read the exact board in the owning task and recover. A dead wait PID cannot wake a model.'
            fresh_board = True
    elif _wait_elapsed_unconsumed(wake):
        state = 'WAIT_ELAPSED_UNCONSUMED'
        next_action = 'Read the exact visible board now, then queue-cycle --from-wake with fresh jobs/shelf/settings. Do not sleep again first.'
        fresh_board = True
    elif exit_gate.get('ok'):
        state = 'TERMINAL_QUEUE'
    elif runtime.get('wake_required'):
        state = 'REQUIRED_WAIT_NOT_STARTED'
        next_action = 'Read the visible board and use queue-cycle, not separate queue-sync/queue-wait. Keep its yielded exec session attached.'
        fresh_board = True
    else:
        state = 'ACTION_REQUIRED_NOW'
        next_action = str(runtime.get('next_action') or next_action)
        fresh_board = True
    mode = read_queue_mode(project)
    if mode['mode'] == 'scheduled' and not (wake.get('pending') and _pid_running(wake.get('wait_pid'))):
        state = ('SCHEDULED_HANDOFF_RECHECK_REQUIRED' if _wait_elapsed_unconsumed(wake)
                 else 'SCHEDULED_CHECK_SELECTED')
        next_action = ('Read the exact board once and consume the interrupted wake with queue-cycle --from-wake; scheduled mode will not sleep.'
                       if _wait_elapsed_unconsumed(wake) else
                       'Inspect native app automation registration and last run. Local selection is not registration; do not restart foreground waiting.')
        fresh_board = True
    return {
        'ok': True, 'read_only': True, 'project': str(project),
        'diagnosis': state, 'continuation_mode': mode['mode'],
        'interval_seconds': mode.get('interval_minutes', 15) * 60,
        'scheduler_created': False, 'automatic_model_reentry': False,
        'model_specific_branch': False,
        'helper_path': str(Path(__file__).resolve()),
        'helper_sha256': media_registry.sha256(Path(__file__)),
        'queue_record_exists': path.exists(),
        'resume_contract_exists': resume_contract_path(project).exists(),
        'queue_verdict': runtime.get('verdict'),
        'active_count': runtime.get('active_count'),
        'settled_backlog_count': runtime.get('settled_backlog_count'),
        'wait_pid': wake.get('wait_pid'), 'due_at': wake.get('due_at'),
        'elapsed_count': wake.get('elapsed_count', 0),
        'consumed_count': wake.get('consumed_count', 0),
        'fresh_board_required': fresh_board,
        'exit_gate': exit_gate, 'next_action': next_action,
        'state_audit': audit_production_state(project),
        'limitations': [
            'Local evidence only; no current provider/UI observation.',
            'No proof of owning tool-session attachment from a PID alone.',
            'Native scheduled tasks require separate app-tool registration and actual run evidence.',
        ],
    }


def cmd_queue_doctor(args) -> int:
    try:
        result = diagnose_queue(Path(args.project))
    except (ValueError, OSError) as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_check_generate(args) -> int:
    st = read_generate_state()
    evidence(args, 'check-generate', 'read visible button color via CSS', json.dumps(st, ensure_ascii=False), st['verdict'])
    return 0 if st['verdict'] == 'BLUE_ENABLED' else 1


def cmd_recover(args) -> int:
    rc1 = cmd_escape(args)
    rc, out, _ = osa('tell application "System Events" to name of first application process whose frontmost is true')
    evidence(args, 'recover', 'ESC sent, frontmost reported', f'frontmost={out}', 'RECOVERY_STEP_DONE')
    print(json.dumps({'next': 'clean polluted field manually/by click+CmdA+Delete, re-screenshot, re-classify state before resuming'}))
    return rc1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--evidence', default=None)
    ap.add_argument('--state', default=None)
    ap.add_argument('--binding', help='project aside_binding.json; otherwise RUNWAY_ASIDE_BINDING')
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('frontmost').set_defaults(fn=cmd_frontmost)
    sub.add_parser('escape').set_defaults(fn=cmd_escape)
    p = sub.add_parser('prepare-upload-alias', help='create a temporary ASCII symlink for one approved registry asset')
    p.add_argument('--project', required=True)
    p.add_argument('--asset-id', required=True)
    p.add_argument('--block-id', required=True)
    p.add_argument('--slot', type=int, default=1)
    p.add_argument('--modality', choices=['Image', 'Video', 'Audio'], default='Image')
    p.set_defaults(fn=cmd_prepare_upload_alias)
    p = sub.add_parser('cleanup-upload-alias', help='remove a helper-owned temporary upload symlink')
    p.add_argument('--path', required=True)
    p.set_defaults(fn=cmd_cleanup_upload_alias)
    p = sub.add_parser('recovery-checkpoint', help='persist the exact same-session Seedance transaction before ATTACH')
    p.add_argument('--project', required=True)
    p.add_argument('--block-id', required=True)
    p.add_argument('--session-url', required=True)
    p.add_argument('--session-id')
    p.add_argument('--phase', default='ATTACH')
    p.add_argument('--prompt-sha256')
    p.add_argument('--reference-manifest-sha256')
    p.add_argument('--reference', action='append', help='repeat as ImageN|VideoN|AudioN=AST_...')
    p.add_argument('--verified-slot', action='append', help='repeat as ImageN, VideoN, or AudioN')
    p.add_argument('--settings-json', help='JSON object with model/mode/audio/ratio/resolution/duration')
    p.set_defaults(fn=cmd_recovery_checkpoint)
    p = sub.add_parser('recovery-record', help='record one incident and return the next fixed recovery rung')
    p.add_argument('--project', required=True)
    p.add_argument('--block-id', required=True)
    p.add_argument('--incident', required=True, choices=sorted(RECOVERY_INCIDENTS))
    p.add_argument('--slot', help='ImageN, VideoN, or AudioN for attachment incidents')
    p.add_argument('--detail')
    p.add_argument('--drag-approved', action='store_true', help='current-thread explicit approval already exists')
    p.set_defaults(fn=cmd_recovery_record)
    p = sub.add_parser('recovery-resolve', help='record recovery success and continue from the checkpoint')
    p.add_argument('--project', required=True)
    p.add_argument('--block-id', required=True)
    p.add_argument('--phase')
    p.add_argument('--verified-slot', help='ImageN, VideoN, or AudioN visibly verified after recovery')
    p.add_argument('--detail')
    p.set_defaults(fn=cmd_recovery_resolve)
    p = sub.add_parser('picker-go'); p.add_argument('--path', required=True); p.set_defaults(fn=cmd_picker_go)
    p = sub.add_parser('picker-select'); p.add_argument('--path', required=True); p.set_defaults(fn=cmd_picker_select)
    p = sub.add_parser('paste-prompt', help='insert prompt text into the Lexical editor via a dispatched paste event (no keystrokes, IME-safe)')
    p.add_argument('--file', required=True)
    p.add_argument('--replace', action='store_true', help='replace all existing text instead of appending')
    p.set_defaults(fn=cmd_paste_prompt)
    p = sub.add_parser('read-prompt'); p.add_argument('--file'); p.set_defaults(fn=cmd_read_prompt)
    sub.add_parser('ime-check', help='is the active input source safe for synthetic keystrokes?').set_defaults(fn=cmd_ime_check)
    def add_queue_observation_args(parser):
        parser.add_argument('--project', required=True)
        parser.add_argument(
            '--job', action='append',
            help='repeat one visible card as SCENE|OUTPUT|IN_QUEUE|GENERATING|PROCESSING|LOADING|COMPLETED|FAILED')
        parser.add_argument(
            '--processed-job', action='append',
            help='repeat one visible settled card already downloaded/QC/registered as SCENE|OUTPUT')
        parser.add_argument('--armed', help='next fully attached/prompted/settings-verified scene')
        parser.add_argument('--next-eligible', help='next eligible shelf package; defaults to --armed')
        parser.add_argument(
            '--shelf-state', required=True,
            choices=['AVAILABLE', 'EXHAUSTED', 'ALL_BLOCKED'])
        parser.add_argument(
            '--generate-state', required=True,
            choices=['BLUE', 'GRAY', 'WAIT', 'UNKNOWN'])
        parser.add_argument(
            '--from-wake', action='store_true',
            help='consume one elapsed foreground queue-wait with this visible-board observation')
        parser.add_argument(
            '--capacity-limit', type=int, choices=[1, 2],
            help='temporary effective provider capacity; 1 requires exact toast evidence')
        parser.add_argument(
            '--capacity-evidence',
            choices=['RUNWAY_QUEUE_CAPACITY_TOAST', 'OPERATOR_CONFIRMED_TWO_SLOT_RETRY'],
            help='visible evidence supporting a temporary capacity decision')

    p = sub.add_parser('queue-sync', help='persist one visible-board observation and compute the mandatory next action')
    add_queue_observation_args(p)
    p.set_defaults(fn=cmd_queue_sync)
    p = sub.add_parser(
        'queue-cycle',
        help='sync one visible board and immediately enter the foreground wait when required')
    add_queue_observation_args(p)
    p.set_defaults(fn=cmd_queue_cycle)

    p = sub.add_parser(
        'settings-verify',
        help='verify visible Seedance 2.0 and duration immediately before Generate')
    p.add_argument('--project', required=True)
    p.add_argument('--block', required=True)
    p.add_argument(
        '--visible-model', required=True,
        help='model label re-read from the visible closed Runway model control')
    p.add_argument('--duration-sec', required=True, type=float)
    p.add_argument('--duration-source', choices=['visible', 'input-video'], default='visible')
    p.add_argument('--source-video', help='registered approved input for Seedance 2.5 Edit only')
    p.set_defaults(fn=cmd_settings_verify)
    p = sub.add_parser(
        'queue-wait',
        help='hold one bounded 15-minute foreground tool session; this is not a scheduler')
    p.add_argument('--project', required=True)
    p.set_defaults(fn=cmd_queue_wait)
    p = sub.add_parser(
        'queue-exit-check',
        help='fail closed before a final response unless queue_runtime may_stop=true')
    p.add_argument('--project', required=True)
    p.set_defaults(fn=cmd_queue_exit_check)
    p = sub.add_parser('queue-doctor', help='read-only model-independent continuation diagnosis; creates no watcher')
    p.add_argument('--project', required=True)
    p.set_defaults(fn=cmd_queue_doctor)
    p = sub.add_parser('queue-mode', help='persist explicit user continuation intent; does not create or approve a scheduler')
    p.add_argument('--project', required=True)
    p.add_argument('--mode', choices=['foreground', 'scheduled'], required=True)
    p.add_argument('--request-evidence', required=True, help='nonempty project-local note of the actual user request')
    p.add_argument('--interval-minutes', choices=[15, 20], type=int, default=20)
    p.set_defaults(fn=cmd_queue_mode)
    p = sub.add_parser(
        'resume-contract',
        help='write state for one foreground wait; this does not schedule or wake Codex')
    p.add_argument('--project', required=True)
    p.add_argument('--write')
    p.set_defaults(fn=cmd_resume_contract)
    sub.add_parser('check-generate').set_defaults(fn=cmd_check_generate)
    sub.add_parser('recover').set_defaults(fn=cmd_recover)
    args = ap.parse_args()
    if args.binding:
        os.environ['RUNWAY_ASIDE_BINDING'] = str(Path(args.binding).expanduser().resolve())
    return args.fn(args)


if __name__ == '__main__':
    raise SystemExit(main())
