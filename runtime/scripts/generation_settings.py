#!/usr/bin/env python3
"""Workflow-owned immutable generation-duration decisions.

Planner/project state chooses duration. Prompting and Runway operation only
consume and verify the resulting lock.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
from pathlib import Path


DURATION_LOCK_VERSION = 'seedance_generation_duration_lock_v1_20260819'
MIN_DURATION_SEC = 5
MAX_DURATION_SEC = 15
SOURCE_PREFIXES = ('user:', 'brief:', 'planner_revision:', 'workflow_default:')
SHORTER_OVERRIDE_PREFIXES = ('user:', 'brief:')
DEFAULT_DURATION_SEC = 15
CHANGE_POLICY = 'default_15_shorter_requires_explicit_user_or_brief'


def _json(path: Path) -> dict:
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


def project_layout(project: Path) -> str:
    project = project.expanduser().resolve()
    if (project / 'manifest.json').is_file() and (project / 'state.json').is_file():
        return 'runtime_v4'
    for candidate in (
        project / 'i2v' / 'seedance' / 'status.json',
        project / 'lanes' / 'seedance' / 'status.json',
        project / 'status.json',
    ):
        if candidate.is_file():
            return 'legacy'
    raise ValueError(f'INVALID_VIDEO_PROJECT: {project}')


def duration_lock_path(project: Path) -> Path:
    project = project.expanduser().resolve()
    if project_layout(project) == 'runtime_v4':
        return project / 'lanes' / 'planner' / 'generation_duration_lock.json'
    if (project / 'i2v' / 'seedance' / 'status.json').is_file():
        return project / 'i2v' / 'seedance' / 'generation_duration_lock.json'
    if (project / 'lanes' / 'seedance' / 'status.json').is_file():
        return project / 'lanes' / 'seedance' / 'generation_duration_lock.json'
    return project / 'generation_duration_lock.json'


def seedance_prompt_dir(project: Path) -> Path:
    project = project.expanduser().resolve()
    if project_layout(project) == 'runtime_v4':
        return project / 'lanes' / 'seedance' / 'prompts'
    if (project / 'i2v' / 'seedance' / 'status.json').is_file():
        return project / 'i2v' / 'seedance' / 'prompts'
    if (project / 'lanes' / 'seedance' / 'status.json').is_file():
        return project / 'lanes' / 'seedance' / 'prompts'
    return project / 'prompts'


def initialize_duration_lock(project: Path) -> dict:
    path = duration_lock_path(project)
    if path.is_file():
        return _json(path)
    value = {
        'schema_version': DURATION_LOCK_VERSION,
        'status': 'LOCKED',
        'default_duration_sec': DEFAULT_DURATION_SEC,
        'block_overrides': {},
        'source': 'workflow_default:seedance_15s',
        'revision': 1,
        'revision_history': [],
        'updated_at': dt.datetime.now().astimezone().isoformat(timespec='seconds'),
        'change_policy': CHANGE_POLICY,
        'prompt_complexity_may_change_duration': False,
    }
    _write_json_atomic(path, value)
    return value


def _valid_duration(value: object) -> bool:
    return isinstance(value, int) and MIN_DURATION_SEC <= value <= MAX_DURATION_SEC


def _valid_source(value: object) -> bool:
    source = str(value or '').strip()
    return any(source.startswith(prefix) and len(source) > len(prefix)
               for prefix in SOURCE_PREFIXES)


def lock_duration(
    project: Path,
    duration_sec: int,
    source: str,
    *,
    block_id: str | None = None,
) -> dict:
    if not _valid_duration(duration_sec):
        raise ValueError(
            f'DURATION_OUT_OF_RANGE: integer {MIN_DURATION_SEC}..{MAX_DURATION_SEC} required')
    if not _valid_source(source):
        raise ValueError(
            'DURATION_LOCK_SOURCE_INVALID: use user:<evidence>, brief:<artifact>, '
            'or planner_revision:<named-revision>')
    normalized_source = source.strip()
    if duration_sec < DEFAULT_DURATION_SEC and not normalized_source.startswith(
            SHORTER_OVERRIDE_PREFIXES):
        raise ValueError(
            'SHORTER_DURATION_EXPLICIT_USER_OR_BRIEF_REQUIRED: 15s is the workflow '
            'default; 5-14s requires user:<evidence> or brief:<artifact>')
    if normalized_source.startswith('workflow_default:') and duration_sec != DEFAULT_DURATION_SEC:
        raise ValueError('WORKFLOW_DEFAULT_DURATION_MUST_BE_15')
    path = duration_lock_path(project)
    current = initialize_duration_lock(project)
    overrides = dict(current.get('block_overrides') or {})
    if block_id:
        overrides[block_id] = duration_sec
        default = current.get('default_duration_sec')
    else:
        default = duration_sec
    timestamp = dt.datetime.now().astimezone().isoformat(timespec='seconds')
    history = list(current.get('revision_history') or [])
    if current.get('status') == 'LOCKED':
        history.append({
            'revision': current.get('revision'),
            'default_duration_sec': current.get('default_duration_sec'),
            'block_overrides': current.get('block_overrides') or {},
            'source': current.get('source'),
            'updated_at': current.get('updated_at'),
        })
    value = {
        'schema_version': DURATION_LOCK_VERSION,
        'status': 'LOCKED',
        'default_duration_sec': default,
        'block_overrides': overrides,
        'source': normalized_source,
        'revision': int(current.get('revision') or 0) + 1,
        'revision_history': history,
        'updated_at': timestamp,
        'change_policy': CHANGE_POLICY,
        'prompt_complexity_may_change_duration': False,
    }
    _write_json_atomic(path, value)
    return {**value, 'path': str(path)}


def validate_duration_lock(project: Path) -> tuple[list[str], dict]:
    path = duration_lock_path(project)
    value = _json(path)
    errors: list[str] = []
    if not value:
        return [f'duration_lock_missing:{path}'], {}
    if value.get('schema_version') != DURATION_LOCK_VERSION:
        errors.append(f'duration_lock_wrong_schema:{value.get("schema_version")}')
    if value.get('status') != 'LOCKED':
        errors.append(f'duration_lock_not_locked:{value.get("status")}')
    default = value.get('default_duration_sec')
    overrides = value.get('block_overrides') or {}
    if default is not None and not _valid_duration(default):
        errors.append(f'duration_lock_invalid_default:{default}')
    if not isinstance(overrides, dict):
        errors.append('duration_lock_overrides_not_object')
        overrides = {}
    for block, seconds in overrides.items():
        if not block or not _valid_duration(seconds):
            errors.append(f'duration_lock_invalid_override:{block}={seconds}')
    shorter_values = (
        (isinstance(default, int) and default < DEFAULT_DURATION_SEC)
        or any(isinstance(seconds, int) and seconds < DEFAULT_DURATION_SEC
               for seconds in overrides.values())
    )
    source = str(value.get('source') or '').strip()
    if shorter_values and not source.startswith(SHORTER_OVERRIDE_PREFIXES):
        errors.append('duration_lock_shorter_without_explicit_user_or_brief')
    if default is None and not overrides:
        errors.append('duration_lock_has_no_default_or_overrides')
    if not _valid_source(value.get('source')):
        errors.append('duration_lock_source_invalid')
    if not isinstance(value.get('revision'), int) or value.get('revision') < 1:
        errors.append(f'duration_lock_revision_invalid:{value.get("revision")}')
    if value.get('change_policy') != CHANGE_POLICY:
        errors.append(f'duration_lock_change_policy_invalid:{value.get("change_policy")}')
    if value.get('prompt_complexity_may_change_duration') is not False:
        errors.append('duration_lock_prompt_complexity_override_not_false')
    try:
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        sha = None
    snapshot = {
        'schema_version': value.get('schema_version'),
        'path': str(path),
        'sha256': sha,
        'status': value.get('status'),
        'default_duration_sec': default,
        'block_overrides': overrides,
        'source': value.get('source'),
        'revision': value.get('revision'),
    }
    return errors, snapshot


def expected_duration(project: Path, block_id: str) -> tuple[list[str], dict]:
    errors, snapshot = validate_duration_lock(project)
    if errors:
        return errors, snapshot
    overrides = snapshot.get('block_overrides') or {}
    duration = overrides.get(block_id, snapshot.get('default_duration_sec'))
    if not _valid_duration(duration):
        errors.append(f'duration_lock_no_value_for_block:{block_id}')
    snapshot = {**snapshot, 'block_id': block_id, 'expected_duration_sec': duration}
    return errors, snapshot


def validate_pack_duration(pack: dict, project: Path) -> tuple[list[str], dict]:
    block = str(pack.get('block_id') or '')
    errors, snapshot = expected_duration(project, block)
    actual = pack.get('duration_sec')
    if not _valid_duration(actual):
        errors.append(f'pack_duration_invalid:{actual}')
    elif not errors and actual != snapshot.get('expected_duration_sec'):
        errors.append(
            f'pack_duration_lock_mismatch:expected={snapshot.get("expected_duration_sec")},actual={actual}')
    snapshot = {**snapshot, 'pack_duration_sec': actual}
    return errors, snapshot
