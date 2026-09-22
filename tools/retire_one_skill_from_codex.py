#!/usr/bin/env python3
"""Archive one explicitly retired skill without deploying unrelated source drift."""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
import re
import shutil

import video_release


def retire(name: str, root: Path, home: Path, *, check_only: bool = False) -> dict:
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', name):
        raise ValueError('INVALID_SKILL_NAME')
    relative = '.codex/skills/' + name
    if relative not in video_release.RETIRED:
        raise ValueError('SKILL_NOT_EXPLICITLY_RETIRED')
    if (root / 'codex-skills' / name).exists():
        raise ValueError('RETIRED_SKILL_SOURCE_STILL_PRESENT')
    target = video_release.safe_path(home, relative)
    if target.exists() and not target.is_dir():
        raise ValueError('SKILL_TARGET_NOT_DIRECTORY')
    result = {'ok': True, 'skill': name, 'active': target.exists(),
              'scope': 'one retired skill only', 'check_only': check_only}
    if check_only or not target.exists():
        return result
    stamp = dt.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    archive_rel = '.codex/archive/' + stamp + '_retired_skill/' + name
    archive = video_release.safe_path(home, archive_rel)
    archive.parent.mkdir(parents=True, exist_ok=False)
    shutil.move(str(target), str(archive))
    result.update(active=False, archive=str(archive))
    try:
        (archive.parent / 'receipt.json').write_text(json.dumps(result, indent=2) + '\n')
    except Exception:
        shutil.move(str(archive), str(target))
        raise
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('skill')
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--home', type=Path, default=Path.home())
    args = parser.parse_args()
    try:
        print(json.dumps(retire(args.skill, video_release.ROOT, args.home,
                                check_only=args.check), indent=2))
        return 0
    except (ValueError, OSError) as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
