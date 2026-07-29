#!/usr/bin/env python3
"""Keep one ordered image library per project, in place.

Why this exists
---------------
The naming convention was already fine — `NNN_<SCENE_ID>_<slug>.png`. What broke
was editing it. A mid-sequence image change meant renumbering everything after
it, and renumbering by hand silently breaks every manifest, queue and prompt pack
that names the old file. So agents avoided the problem: they left the old set
alone and made a sibling folder. That is where `ordered_images_v6_s01_restructured`
inside `redesign_20260724` inside `lanes/seedance` came from, and why one project
ended up with 68 folders and an empty assets/.

Renumbering is only safe if references move with the files, so that is what this
does, atomically and reversibly.

Commands
--------
  check    --project P [--lib DIR]                 report gaps, duplicates, disorder
  replace  --project P --slot N --file F           same slot, old revision superseded
  insert   --project P --at N --file F --slug S    shift the tail up, then place
  remove   --project P --slot N                    supersede and close the gap
  renumber --project P                             re-pack to a contiguous 001..NNN

Dry-run by default. Pass --apply to write. Every apply records a manifest under
`_superseded/<timestamp>/` so a bad edit can be reversed.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import sys
from pathlib import Path

DEFAULT_LIB = 'assets/images_approved'
# NNN_<rest>.<ext>
SEQ_RE = re.compile(r'^(?P<num>\d{3,4})_(?P<rest>.+)\.(?P<ext>[A-Za-z0-9]+)$')
# Files that may name an asset and therefore must be rewritten with it.
REF_SUFFIXES = {'.json', '.jsonl', '.md', '.txt', '.csv'}
SKIP_DIRS = {'_superseded', '_sweep_trash', '.git', '__pycache__', 'node_modules'}


def entries(lib: Path) -> list[dict]:
    out = []
    for p in sorted(lib.iterdir()) if lib.exists() else []:
        if not p.is_file():
            continue
        m = SEQ_RE.match(p.name)
        if m:
            out.append({'path': p, 'num': int(m.group('num')),
                        'rest': m.group('rest'), 'ext': m.group('ext')})
    return sorted(out, key=lambda e: (e['num'], e['path'].name))


def width(items: list[dict]) -> int:
    return max([len(str(e['num'])) for e in items] + [3])


def check(lib: Path) -> dict:
    items = entries(lib)
    nums = [e['num'] for e in items]
    dupes = sorted({n for n in nums if nums.count(n) > 1})
    gaps = [n for n in range(1, (max(nums) if nums else 0) + 1) if n not in nums]
    return {
        'library': str(lib),
        'count': len(items),
        'duplicate_slots': dupes,
        'missing_slots': gaps,
        'contiguous': not dupes and not gaps and (nums == list(range(1, len(nums) + 1))),
        'first': items[0]['path'].name if items else None,
        'last': items[-1]['path'].name if items else None,
    }


def find_refs(project: Path, names: list[str]) -> dict[str, list[str]]:
    """Text files that mention any of these filenames."""
    hits: dict[str, list[str]] = {}
    for p in project.rglob('*'):
        if not p.is_file() or p.suffix.lower() not in REF_SUFFIXES:
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        try:
            text = p.read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError):
            continue
        found = [n for n in names if n in text]
        if found:
            hits[str(p)] = found
    return hits


def apply_renames(project: Path, pairs: list[tuple[Path, Path]], apply: bool) -> dict:
    """Rename files and rewrite every text reference to their old names."""
    pairs = [(a, b) for a, b in pairs if a.name != b.name]
    if not pairs:
        return {'renamed': 0, 'reference_files_updated': 0}
    refs = find_refs(project, [a.name for a, _ in pairs])
    if apply:
        # two-phase so a swap never collides
        tmp = []
        for src, dst in pairs:
            t = src.with_name('.__seq_tmp__' + src.name)
            src.rename(t)
            tmp.append((t, dst))
        for t, dst in tmp:
            t.rename(dst)
        mapping = {a.name: b.name for a, b in pairs}
        for f in refs:
            p = Path(f)
            text = p.read_text(encoding='utf-8')
            for old, new in mapping.items():
                text = text.replace(old, new)
            p.write_text(text, encoding='utf-8')
    return {
        'renamed': len(pairs),
        'renames': [{'from': a.name, 'to': b.name} for a, b in pairs],
        'reference_files_updated': len(refs),
        'reference_files': sorted(refs),
    }


def supersede(lib: Path, path: Path, stamp: str, apply: bool) -> str:
    dest = lib / '_superseded' / stamp / path.name
    if apply:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(path), str(dest))
    return str(dest)


def renumber_plan(items: list[dict], w: int) -> list[tuple[Path, Path]]:
    plan = []
    for i, e in enumerate(items, start=1):
        new = e['path'].with_name(f"{i:0{w}d}_{e['rest']}.{e['ext']}")
        plan.append((e['path'], new))
    return plan


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('command', choices=['check', 'replace', 'insert', 'remove', 'renumber'])
    ap.add_argument('--project', required=True)
    ap.add_argument('--lib', default=DEFAULT_LIB, help=f'ordered library, default {DEFAULT_LIB}')
    ap.add_argument('--slot', type=int, help='slot number for replace/remove')
    ap.add_argument('--at', type=int, help='slot to insert at (existing entry shifts up)')
    ap.add_argument('--file', help='new image file')
    ap.add_argument('--slug', help='descriptive tail for an inserted file, e.g. S03-02_rifle_shadow')
    ap.add_argument('--apply', action='store_true', help='write changes (default: dry run)')
    a = ap.parse_args()

    project = Path(a.project).expanduser().resolve()
    lib = project / a.lib
    stamp = dt.datetime.now().strftime('%Y%m%d_%H%M%S')
    result: dict = {'command': a.command, 'project': str(project), 'library': str(lib),
                    'mode': 'APPLY' if a.apply else 'DRY_RUN'}

    if a.command == 'check':
        result.update(check(lib))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get('contiguous') else 1

    items = entries(lib)
    if not items and a.command != 'insert':
        print(json.dumps({**result, 'error': 'EMPTY_LIBRARY'}, ensure_ascii=False, indent=2))
        return 2
    w = width(items)

    if a.command == 'replace':
        if a.slot is None or not a.file:
            print(json.dumps({**result, 'error': 'replace needs --slot and --file'}), file=sys.stderr)
            return 2
        target = next((e for e in items if e['num'] == a.slot), None)
        if not target:
            print(json.dumps({**result, 'error': f'no entry at slot {a.slot}'}, ensure_ascii=False, indent=2))
            return 2
        src = Path(a.file).expanduser().resolve()
        dest = target['path'].with_suffix(src.suffix)
        result['superseded'] = supersede(lib, target['path'], stamp, a.apply)
        result['placed'] = str(dest)
        if a.apply:
            shutil.copy2(src, dest)
        # same slot, same name -> references keep pointing correctly
        result['note'] = 'slot and filename unchanged; existing references stay valid'

    elif a.command == 'insert':
        if a.at is None or not a.file or not a.slug:
            print(json.dumps({**result, 'error': 'insert needs --at, --file and --slug'}), file=sys.stderr)
            return 2
        src = Path(a.file).expanduser().resolve()
        tail = [e for e in items if e['num'] >= a.at]
        plan = [(e['path'], e['path'].with_name(f"{e['num'] + 1:0{w}d}_{e['rest']}.{e['ext']}"))
                for e in reversed(tail)]
        result['shift'] = apply_renames(project, plan, a.apply)
        dest = lib / f"{a.at:0{w}d}_{a.slug}{src.suffix}"
        result['placed'] = str(dest)
        if a.apply:
            shutil.copy2(src, dest)

    elif a.command == 'remove':
        if a.slot is None:
            print(json.dumps({**result, 'error': 'remove needs --slot'}), file=sys.stderr)
            return 2
        target = next((e for e in items if e['num'] == a.slot), None)
        if not target:
            print(json.dumps({**result, 'error': f'no entry at slot {a.slot}'}, ensure_ascii=False, indent=2))
            return 2
        result['superseded'] = supersede(lib, target['path'], stamp, a.apply)
        remaining = [e for e in entries(lib) if e['path'] != target['path']] if not a.apply else entries(lib)
        result['repack'] = apply_renames(project, renumber_plan(remaining, w), a.apply)

    elif a.command == 'renumber':
        result['repack'] = apply_renames(project, renumber_plan(items, w), a.apply)

    result['after'] = check(lib)
    if a.apply:
        log = lib / '_superseded' / stamp / 'operation.json'
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
