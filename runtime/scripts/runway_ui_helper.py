#!/usr/bin/env python3
"""Compatibility shim for the canonical Seedance/Runway helper.

Runway UI operation and same-session recovery are owned by the global
``seedance-prompt-en`` skill. Keep this module only so older runtime commands and
tests continue to work; no Seedance procedure may be implemented or forked here.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


REPO_CANONICAL_HELPER = (
    Path(__file__).resolve().parents[2]
    / 'codex-skills' / 'seedance-prompt-en' / 'scripts' / 'runway_ui_helper.py'
)
LIVE_CANONICAL_HELPER = Path(
    '/Users/gnudas/.codex/skills/seedance-prompt-en/scripts/runway_ui_helper.py'
)
CANONICAL_HELPER = (
    REPO_CANONICAL_HELPER if REPO_CANONICAL_HELPER.is_file()
    else LIVE_CANONICAL_HELPER
)

if not CANONICAL_HELPER.is_file():
    raise ImportError(f'CANONICAL_SEEDANCE_HELPER_MISSING: {CANONICAL_HELPER}')

_spec = importlib.util.spec_from_file_location(
    '_canonical_seedance_runway_ui_helper', CANONICAL_HELPER)
if _spec is None or _spec.loader is None:
    raise ImportError(f'CANONICAL_SEEDANCE_HELPER_LOAD_FAILED: {CANONICAL_HELPER}')
_canonical = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _canonical
_spec.loader.exec_module(_canonical)

for _name in dir(_canonical):
    if not _name.startswith('__'):
        globals()[_name] = getattr(_canonical, _name)

__all__ = [name for name in dir(_canonical) if not name.startswith('_')]


if __name__ == '__main__':
    raise SystemExit(_canonical.main())
