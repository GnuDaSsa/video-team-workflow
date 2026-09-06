#!/usr/bin/env python3
"""Allowlisted, hash-verified deployment. Never sweeps projects/media or unknown skills."""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'docs/releases/2026-09-06/manifest.json'
SKILLS = ('seedance-prompt-en', 'seedance25-prompt-en', 'videodirector')
RETIRED = [
    '.codex/skills/seedance-creative-prompt-team',
    '.codex/skills/seedance-prompt-en/archive',
    '.local/bin/video-image-cli',
    'Documents/Codex/video-team-runtime/runtime/scripts/codex_app_image_cli.py',
    *('Documents/Codex/video-team-runtime/runtime/scripts/' + n + '.py' for n in (
        'sol_prompt_bridge', 'seedance_inflight_monitor', 'image_qc_lane_runner', 'image_qc_queue')),
]


def digest(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def mappings(root: Path = ROOT) -> list[dict]:
    rows = []
    def add(src: Path, dst: str):
        rows.append({'source': str(src.relative_to(root)), 'target': dst, 'sha256': digest(src)})
    def tree(rel: str, target: str):
        for src in sorted((root / rel).rglob('*')):
            if src.is_file() and '__pycache__' not in src.parts and src.name != '.DS_Store':
                add(src, target + '/' + str(src.relative_to(root / rel)))
    for name in SKILLS:
        tree('codex-skills/' + name, '.codex/skills/' + name)
    for name in ('scripts', 'templates'):
        tree('runtime/' + name, 'Documents/Codex/video-team-runtime/runtime/' + name)
    for rel, target in (
        ('GLOBAL_AGENTS.md', '.codex/AGENTS.md'),
        ('runtime/AGENTS.md', 'Documents/Codex/video-team-runtime/AGENTS.md'),
    ):
        add(root / rel, target)
    for name in ('character_sheet_prompt_standard.md', 'seedance_prompting_rulebook.md'):
        add(root / 'references' / name, 'Documents/Codex/video-team-runtime/runtime/references/' + name)
    tree('team-policies', '.codex/video-team-policies')
    tree('seedance-operations', '.codex/video-team-policies/seedance-operations')
    return rows


def freeze(root: Path = ROOT) -> dict:
    return {'schema': 'video_release_v1', 'release': '2026-09-06-lean-aside',
            'files': mappings(root), 'retired': RETIRED}


def safe_path(root: Path, relative: str, *, allow_leaf_symlink: bool = False) -> Path:
    path = root / relative
    if Path(relative).is_absolute() or '..' in Path(relative).parts or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError('UNSAFE_RELEASE_PATH: ' + relative)
    if path.is_symlink() and not allow_leaf_symlink:
        raise ValueError('RELEASE_TARGET_SYMLINK: ' + relative)
    return path


def preflight(manifest: dict, root: Path, home: Path) -> list[str]:
    errors = []
    expected = {(r['source'], r['target'], r['sha256']) for r in mappings(root)}
    recorded = {(r['source'], r['target'], r['sha256']) for r in manifest['files']}
    if expected != recorded or manifest.get('retired') != RETIRED:
        errors.append('SOURCE_MANIFEST_DRIFT: freeze the reviewed release before deployment')
    for row in manifest['files']:
        safe_path(root, row['source']); safe_path(home, row['target'])
    for rel in RETIRED:
        safe_path(home, rel, allow_leaf_symlink=True)
    # Unknown live skill files must be reconciled, not silently left active or deleted.
    targets = {r['target'] for r in manifest['files']}
    for name in SKILLS:
        base = home / '.codex/skills' / name
        for p in base.rglob('*'):
            if not p.is_file() or '__pycache__' in p.parts or p.name == '.DS_Store':
                continue
            rel = str(p.relative_to(home))
            if rel not in targets and not any(rel == old or rel.startswith(old + '/') for old in RETIRED):
                errors.append('UNRECONCILED_LIVE_SKILL_FILE: ' + rel)
    return errors


def check(manifest: dict, root: Path, home: Path) -> dict:
    errors = preflight(manifest, root, home)
    for row in manifest['files']:
        p = safe_path(home, row['target'])
        if not p.is_file() or digest(p) != row['sha256']:
            errors.append('LIVE_HASH_MISMATCH: ' + row['target'])
    for rel in RETIRED:
        if (home / rel).exists() or (home / rel).is_symlink():
            errors.append('RETIRED_PATH_STILL_ACTIVE: ' + rel)
    return {'ok': not errors, 'managed_files': len(manifest['files']), 'errors': errors}


def apply(manifest: dict, root: Path, home: Path) -> dict:
    errors = preflight(manifest, root, home)
    if errors:
        raise ValueError('; '.join(errors))
    stamp = dt.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    archive = home / '.codex/archive' / (stamp + '_verified_video_release')
    archive.mkdir(parents=True, exist_ok=False)
    changed = []
    retired = []
    try:
        for row in manifest['files']:
            src, dst = safe_path(root, row['source']), safe_path(home, row['target'])
            if dst.is_file() and digest(dst) == row['sha256']:
                continue
            existed = dst.exists()
            if existed:
                old = archive / row['target']; old.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(dst, old)
            changed.append((dst, existed))
            dst.parent.mkdir(parents=True, exist_ok=True)
            tmp = dst.with_name(dst.name + '.release-tmp')
            shutil.copy2(src, tmp); tmp.replace(dst)
        for rel in RETIRED:
            p = home / rel
            if p.exists() or p.is_symlink():
                old = archive / rel; old.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(p), str(old)); retired.append(rel)
        result = check(manifest, root, home)
        if not result['ok']:
            raise ValueError('POST_DEPLOY_PARITY_FAILED')
    except Exception:
        for rel in reversed(retired):
            shutil.move(str(archive / rel), str(home / rel))
        for dst, existed in reversed(changed):
            if existed:
                shutil.copy2(archive / dst.relative_to(home), dst)
            elif dst.exists():
                dst.unlink()  # only this transaction's new file, never user media
        raise
    result.update({'changed_files': len(changed), 'retired_paths': retired, 'archive': str(archive)})
    (archive / 'receipt.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['freeze', 'preflight', 'check', 'apply'])
    p.add_argument('--home', type=Path, default=Path.home())
    p.add_argument('--manifest', type=Path, default=MANIFEST)
    args = p.parse_args()
    try:
        if args.action == 'freeze':
            data = freeze(); args.manifest.parent.mkdir(parents=True, exist_ok=True)
            args.manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
            result = {'ok': True, 'files': len(data['files'])}
        else:
            data = json.loads(args.manifest.read_text())
            if args.action == 'check':
                result = check(data, ROOT, args.home)
            elif args.action == 'preflight':
                errors = preflight(data, ROOT, args.home)
                result = {'ok': not errors, 'errors': errors, 'note': 'preflight is not live parity'}
            else:
                result = apply(data, ROOT, args.home)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result['ok'] else 1
    except (ValueError, OSError) as exc:
        print(json.dumps({'ok': False, 'error': str(exc)})); return 1


if __name__ == '__main__':
    raise SystemExit(main())
