#!/usr/bin/env python3
"""Seedance 2.5 model-policy adapter for the shared Runway helper.

This file deliberately contains no browser, upload, queue, or recovery
implementation. It imports the canonical ``seedance-prompt-en`` helper and
changes only its fail-closed model policy from Seedance 2.0 to Seedance 2.5.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


EXPECTED_MODEL = 'Seedance 2.5'
REPO_SHARED_HELPER = (
    Path(__file__).resolve().parents[2]
    / 'seedance-prompt-en' / 'scripts' / 'runway_ui_helper.py'
)
LIVE_SHARED_HELPER = Path(
    '/Users/gnudas/.codex/skills/seedance-prompt-en/scripts/runway_ui_helper.py'
)
SHARED_HELPER = (
    REPO_SHARED_HELPER if REPO_SHARED_HELPER.is_file() else LIVE_SHARED_HELPER
)

if not SHARED_HELPER.is_file():
    raise ImportError(f'BLOCKED_SHARED_SEEDANCE_HELPER_MISSING: {SHARED_HELPER}')

_spec = importlib.util.spec_from_file_location(
    '_shared_seedance_runway_ui_helper_for_25', SHARED_HELPER)
if _spec is None or _spec.loader is None:
    raise ImportError(f'SHARED_SEEDANCE_HELPER_LOAD_FAILED: {SHARED_HELPER}')
_shared = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _shared
_spec.loader.exec_module(_shared)


def _require_seedance_25(value: str, *, error_prefix: str = 'SETTINGS') -> str:
    visible_model = _shared.normalize_visible_seedance_model(value)
    if visible_model != EXPECTED_MODEL:
        raise ValueError(
            f'{error_prefix}_VISIBLE_MODEL_MISMATCH: '
            f'expected={EXPECTED_MODEL},visible={visible_model}; '
            'select Seedance 2.5, close the model menu, re-read the visible '
            'label, and rerun settings-verify before Generate')
    return visible_model


# The shared helper resolves these globals at call time. Patching only this
# policy preserves one implementation for every UI/recovery/queue operation.
_shared.REQUIRED_GENERATION_MODEL = EXPECTED_MODEL
_shared.require_seedance_20 = _require_seedance_25
_original_verify = _shared.verify_attested_generation_settings


def _verify_seedance_25_settings(*args, **kwargs) -> dict:
    result = _original_verify(*args, **kwargs)
    result['contract_version'] = 'seedance25_generation_settings_preflight_v1_20260905'
    result['expected_model'] = EXPECTED_MODEL
    result['visible_model'] = EXPECTED_MODEL
    result['verdict'] = 'PASS_SETTINGS_MATCH_SEEDANCE_2_5_AND_ATTESTED_DURATION'
    project = Path(result['project'])
    block_id = str(result['block_id'])
    _shared._write_json_atomic(
        _shared.settings_preflight_path(project, block_id), result)
    return result


_shared.verify_attested_generation_settings = _verify_seedance_25_settings

for _name in dir(_shared):
    if not _name.startswith('__'):
        globals()[_name] = getattr(_shared, _name)

# Expose a correctly named public guard while preserving the shared helper's
# legacy symbol for its internal dynamic lookups.
require_seedance_25 = _require_seedance_25
REQUIRED_GENERATION_MODEL = EXPECTED_MODEL
verify_attested_generation_settings = _verify_seedance_25_settings

__all__ = [name for name in globals() if not name.startswith('_')]


if __name__ == '__main__':
    raise SystemExit(_shared.main())
