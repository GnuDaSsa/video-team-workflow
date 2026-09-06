#!/usr/bin/env python3
"""Disk sweep for video-team projects: keep finals, quarantine duplicates/staging.

Safety model (AGENTS.md 안전 게이트 준수):
- `scan`  : report only. No filesystem changes.
- `apply` : REVERSIBLE — moves candidates into <project>/_sweep_trash_<date>/
            preserving relative paths + writes sweep_manifest.json (restorable).
- `purge` : actually deletes a _sweep_trash folder. REQUIRES --user-approved
            (explicit user approval; agents must never pass this flag on their own).
- `restore`: undo an apply using its sweep_manifest.json.

Candidate policy (conservative v1):
1. EXACT duplicates: same sha256 among media files (>1MB). Keep ONE canonical
   copy (preference: assets/ > production/ > lanes/), quarantine the rest.
2. Staging folders: ~/Downloads/SEEDANCE_*_UPLOAD_ONLY and
   ~/Movies/CapCutImport/<project-slug>* older than --staging-days (default 3),
   IF every file inside also exists (by hash) somewhere in the project.
3. Superseded block retries: in the same directory, files matching the same
   block id where a strictly newer file exists AND the old one is not referenced
   in seedance_review_queue as PASS — REPORT ONLY in v1 (never auto-quarantined).

NEVER touched: queues/, *.json(l), *.md, evidence, locks/, music lock audio,
anything under assets/images_approved, final export files (*_FINAL*, package/).
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import shutil
import time
from collections import defaultdict
from pathlib import Path

import media_registry

MEDIA_EXT = {'.png', '.jpg', '.jpeg', '.webp', '.mp4', '.mov', '.wav', '.mp3', '.gif', '.tiff'}
MIN_SIZE = 1_000_000  # 1MB
PROTECT_PARTS = ('queues', 'locks', 'images_approved', 'package')
PROTECT_NAME = re.compile(r'(_FINAL|final_export|LOCKED)', re.IGNORECASE)


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def protected(p: Path) -> bool:
    if p.suffix.lower() not in MEDIA_EXT:
        return True
    if any(part in PROTECT_PARTS for part in p.parts):
        return True
    if PROTECT_NAME.search(p.name):
        return True
    return False


def canonical_rank(p: Path) -> tuple:
    s = str(p)
    return (0 if '/assets/' in s else 1 if '/production/' in s else 2, len(s))


def collect(project: Path):
    """Return (dupe_groups, big_files). dupe_groups: hash -> [paths sorted canonical-first]."""
    by_hash = defaultdict(list)
    big = []
    for p in project.rglob('*'):
        if not p.is_file() or p.stat().st_size < MIN_SIZE or protected(p):
            continue
        if '_sweep_trash_' in str(p):
            continue
        big.append(p)
    # hash only files whose (size) collides — cheap pre-filter
    by_size = defaultdict(list)
    for p in big:
        by_size[p.stat().st_size].append(p)
    for size, paths in by_size.items():
        if len(paths) < 2:
            continue
        for p in paths:
            by_hash[sha256(p)].append(p)
    dupes = {h: sorted(ps, key=canonical_rank) for h, ps in by_hash.items() if len(ps) > 1}
    return dupes, big


def staging_candidates(project: Path, days: int, project_hashes: set[str]):
    out = []
    cutoff = time.time() - days * 86400
    roots = list(Path.home().glob('Downloads/SEEDANCE_*_UPLOAD_ONLY*'))
    slug = project.name.split('_', 2)[-1][:20]
    roots += [d for d in Path.home().glob('Movies/CapCutImport/*') if slug and slug in d.name]
    for d in roots:
        try:
            if not d.is_dir() or d.stat().st_mtime > cutoff:
                continue
            files = [f for f in d.rglob('*') if f.is_file()]
            if files and all(sha256(f) in project_hashes for f in files if f.stat().st_size >= MIN_SIZE):
                out.append(d)
        except Exception:
            continue
    return out


def superseded_report(project: Path):
    """Report-only: same-dir files sharing a block id where newer versions exist."""
    rep = []
    pat = re.compile(r'(B\d{2}|C\d{2}|S\d{2})')
    by_key = defaultdict(list)
    for p in project.rglob('*.mp4'):
        if protected(p) or '_sweep_trash_' in str(p):
            continue
        m = pat.search(p.name)
        if m:
            by_key[(str(p.parent), m.group(1))].append(p)
    for (parent, block), ps in by_key.items():
        if len(ps) > 1:
            ps.sort(key=lambda x: x.stat().st_mtime)
            rep.append({'dir': parent, 'block': block,
                        'older_versions': [str(x) for x in ps[:-1]],
                        'newest': str(ps[-1]),
                        'reclaimable_mb': round(sum(x.stat().st_size for x in ps[:-1]) / 1e6, 1)})
    return rep


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=['scan', 'apply', 'purge', 'restore'])
    ap.add_argument('--project', required=True)
    ap.add_argument('--staging-days', type=int, default=1)
    ap.add_argument('--trash', help='trash folder for purge/restore')
    ap.add_argument('--user-approved', action='store_true', help='REQUIRED for purge; only the user grants this')
    args = ap.parse_args()
    project = Path(args.project).expanduser().resolve()

    # New projects use the registry-backed 24-hour policy and macOS Trash.
    # The legacy quarantine/purge implementation below remains available only
    # to old projects, which this upgrade intentionally does not migrate.
    if media_registry.is_v4_project(project):
        if args.mode in {'purge', 'restore'}:
            raise SystemExit(
                'V4_TRASH_MANAGED_EXTERNALLY: v4 never empties or restores macOS Trash; '
                'use Finder if the user wants to restore a journaled file.')
        candidates = media_registry.cleanup_candidates(
            project, older_than_hours=max(24, args.staging_days * 24))
        moved = media_registry.move_candidates_to_trash(project, candidates) if args.mode == 'apply' else []
        print(json.dumps({
            'project': str(project),
            'mode': args.mode,
            'media_schema_version': media_registry.MEDIA_SCHEMA_VERSION,
            'minimum_age_hours': max(24, args.staging_days * 24),
            'candidates': candidates,
            'moved': moved,
            'trash_emptied': False,
            'journal': str(project / 'cleanup_journal.jsonl'),
        }, ensure_ascii=False, indent=2))
        return 0

    if args.mode == 'purge':
        if not args.user_approved:
            raise SystemExit('BLOCKED_PERMANENT_DELETION_REQUIRES_USER_APPROVAL: purge needs --user-approved from the user.')
        trash = Path(args.trash).expanduser().resolve()
        assert '_sweep_trash_' in trash.name and trash.exists()
        size = sum(f.stat().st_size for f in trash.rglob('*') if f.is_file())
        shutil.rmtree(trash)
        print(json.dumps({'purged': str(trash), 'freed_mb': round(size / 1e6, 1)}))
        return 0

    if args.mode == 'restore':
        trash = Path(args.trash).expanduser().resolve()
        manifest = json.loads((trash / 'sweep_manifest.json').read_text())
        n = 0
        for item in manifest['moved']:
            src = trash / item['rel']
            dst = Path(item['original'])
            if src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dst))
                n += 1
        print(json.dumps({'restored': n}))
        return 0

    dupes, big = collect(project)
    project_hashes = set(dupes.keys()) | {sha256(p) for p in big if p.stat().st_size >= MIN_SIZE}
    staging = staging_candidates(project, args.staging_days, project_hashes)
    superseded = superseded_report(project)

    dupe_items = []
    for h, ps in dupes.items():
        keep, extras = ps[0], ps[1:]
        for e in extras:
            dupe_items.append({'keep': str(keep), 'candidate': str(e), 'mb': round(e.stat().st_size / 1e6, 1)})
    reclaim = round(sum(d['mb'] for d in dupe_items) + sum(sum(f.stat().st_size for f in d.rglob('*') if f.is_file()) / 1e6 for d in staging), 1)

    report = {
        'project': str(project), 'mode': args.mode,
        'duplicate_copies': dupe_items,
        'staging_folders': [str(s) for s in staging],
        'superseded_block_versions_REPORT_ONLY': superseded,
        'auto_reclaimable_mb': reclaim,
        'note': 'apply = reversible quarantine to _sweep_trash_<date>; purge requires user approval',
    }

    if args.mode == 'apply' and (dupe_items or staging):
        trash = project / f'_sweep_trash_{dt.datetime.now().strftime("%Y%m%d_%H%M%S")}'
        moved = []
        for d in dupe_items:
            src = Path(d['candidate'])
            rel = src.relative_to(project) if str(src).startswith(str(project)) else Path('external') / src.name
            dst = trash / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            moved.append({'original': str(src), 'rel': str(rel), 'reason': 'exact_duplicate', 'kept': d['keep']})
        for s in staging:
            rel = Path('staging') / s.name
            dst = trash / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(s), str(dst))
            moved.append({'original': str(s), 'rel': str(rel), 'reason': 'staging_folder_all_content_in_project'})
        (trash / 'sweep_manifest.json').write_text(json.dumps({'ts': dt.datetime.now().isoformat(), 'moved': moved}, ensure_ascii=False, indent=2))
        report['trash'] = str(trash)
        report['moved_count'] = len(moved)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
