#!/usr/bin/env python3
"""Project-local media registry for video-team runtime v4.

New projects keep every media file under one Finder-friendly ``media/`` tree.
The SQLite registry gives files stable identity and revision lineage so a
filename or sequence number never has to double as an asset ID.

This module is deliberately legacy-safe: it does nothing to projects that do
not declare ``media_schema_version=2026-07-31-v4``.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import uuid


MEDIA_SCHEMA_VERSION = '2026-07-31-v4'
REGISTRY_NAME = 'asset_registry.sqlite'
MEDIA_EXT = {
    '.png', '.jpg', '.jpeg', '.webp', '.gif', '.tiff',
    '.mp4', '.mov', '.mkv', '.webm',
    '.wav', '.mp3', '.m4a', '.aac', '.flac', '.aiff',
    '.zip',
}

FOLDERS = {
    'sources': '01_sources_원본자료',
    'audio': '02_audio_음악',
    'characters': '03_characters_캐릭터',
    'images_candidates': '04_images_candidates_이미지후보',
    'images_approved': '05_images_approved_이미지승인',
    'videos_candidates': '06_videos_candidates_영상후보',
    'videos_approved': '07_videos_approved_영상승인',
    'edit': '08_edit_편집',
    'final': '09_final_최종본',
    'work': '90_work_작업중',
    'archive': '99_archive_보관함',
}

PROTECTED_STATES = {'source', 'locked', 'approved', 'selected', 'final', 'packaged'}
CLEANUP_STATES = {
    'staging', 'rejected', 'superseded', 'duplicate', 'proxy',
    'test_output', 'evidence_redundant',
}
ALLOWED_STATES = (
    {'source', 'locked', 'candidate', 'approved', 'selected', 'final', 'packaged', 'work', 'trashed'}
    | CLEANUP_STATES
)


def now_iso() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec='seconds')


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def project_manifest(project: Path) -> dict:
    try:
        value = json.loads((project / 'manifest.json').read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def is_v4_project(project: Path) -> bool:
    return project_manifest(Path(project)).get('media_schema_version') == MEDIA_SCHEMA_VERSION


def media_root(project: Path) -> Path:
    return Path(project) / 'media'


def folder(project: Path, key: str) -> Path:
    return media_root(project) / FOLDERS[key]


def db_path(project: Path) -> Path:
    return Path(project) / REGISTRY_NAME


def connect(project: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path(project))
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def init_registry(project: Path) -> Path:
    project = Path(project).expanduser().resolve()
    (project / 'media').mkdir(parents=True, exist_ok=True)
    for name in FOLDERS.values():
        (project / 'media' / name).mkdir(parents=True, exist_ok=True)
    with connect(project) as conn:
        conn.executescript(
            '''
            CREATE TABLE IF NOT EXISTS meta (
              key TEXT PRIMARY KEY,
              value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS assets (
              asset_id TEXT PRIMARY KEY,
              work_item_id TEXT NOT NULL,
              kind TEXT NOT NULL,
              state TEXT NOT NULL,
              revision INTEGER NOT NULL,
              attempt INTEGER NOT NULL DEFAULT 1,
              parent_asset_id TEXT,
              sha256 TEXT NOT NULL,
              size_bytes INTEGER NOT NULL,
              current_path TEXT NOT NULL UNIQUE,
              original_name TEXT NOT NULL,
              origin_lane TEXT,
              run_id TEXT,
              provider TEXT,
              prompt_hash TEXT,
              active INTEGER NOT NULL DEFAULT 1,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL,
              metadata_json TEXT NOT NULL DEFAULT '{}',
              FOREIGN KEY(parent_asset_id) REFERENCES assets(asset_id)
            );
            CREATE INDEX IF NOT EXISTS assets_work_item_idx
              ON assets(work_item_id, kind, revision);
            CREATE INDEX IF NOT EXISTS assets_hash_idx ON assets(sha256);
            CREATE INDEX IF NOT EXISTS assets_state_idx ON assets(state, active);
            CREATE TABLE IF NOT EXISTS cleanup_journal (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              asset_id TEXT NOT NULL,
              original_path TEXT NOT NULL,
              trashed_path TEXT NOT NULL,
              sha256 TEXT NOT NULL,
              reason TEXT NOT NULL,
              moved_at TEXT NOT NULL,
              FOREIGN KEY(asset_id) REFERENCES assets(asset_id)
            );
            '''
        )
        conn.execute('INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)',
                     ('media_schema_version', MEDIA_SCHEMA_VERSION))
        conn.execute('INSERT OR IGNORE INTO meta(key, value) VALUES (?, ?)',
                     ('created_at', now_iso()))
    return db_path(project)


def target_folder_key(kind: str, state: str) -> str:
    if state == 'work' or state in CLEANUP_STATES:
        return 'work'
    if kind == 'source':
        return 'sources'
    if kind == 'audio':
        return 'audio'
    if kind == 'character':
        return 'characters'
    if kind == 'image':
        return 'images_approved' if state in {'approved', 'selected'} else 'images_candidates'
    if kind == 'video':
        return 'videos_approved' if state in {'approved', 'selected'} else 'videos_candidates'
    if kind == 'edit':
        return 'edit'
    if kind in {'final', 'package'}:
        return 'final'
    raise ValueError(f'unsupported kind: {kind}')


def unique_destination(directory: Path, name: str, revision: int, asset_id: str) -> Path:
    destination = directory / name
    if not destination.exists():
        return destination
    stem, suffix = Path(name).stem, Path(name).suffix
    return directory / f'{stem}_r{revision}_{asset_id[-6:]}{suffix}'


def ingest(
    project: Path,
    source: Path,
    *,
    kind: str,
    state: str,
    work_item_id: str,
    origin_lane: str = '',
    provider: str = '',
    run_id: str = '',
    prompt_hash: str = '',
    parent_asset_id: str | None = None,
    move: bool = True,
    metadata: dict | None = None,
) -> dict:
    project = Path(project).expanduser().resolve()
    if not is_v4_project(project):
        raise ValueError('MEDIA_V4_REQUIRED: ingest is only for new v4 projects')
    source = Path(source).expanduser().resolve()
    if not source.is_file() or source.stat().st_size <= 0:
        raise FileNotFoundError(f'missing or empty media: {source}')
    if source.suffix.lower() not in MEDIA_EXT:
        raise ValueError(f'unsupported media extension: {source.suffix}')
    if state not in ALLOWED_STATES - {'trashed'}:
        raise ValueError(f'unsupported asset state: {state}')

    digest = sha256(source)
    existing = asset_for_path(project, source)
    if existing is not None:
        if existing['sha256'] != digest:
            raise ValueError(
                f'REGISTERED_PATH_CONTENT_CHANGED: {source}; create a new revision instead')
        return existing
    asset_id = f'AST_{uuid.uuid4().hex[:16].upper()}'
    created = now_iso()
    with connect(project) as conn:
        parent_revision = 0
        if parent_asset_id:
            parent = conn.execute('SELECT * FROM assets WHERE asset_id=?', (parent_asset_id,)).fetchone()
            if parent is None:
                raise ValueError(f'unknown parent asset: {parent_asset_id}')
            parent_revision = int(parent['revision'])
        row = conn.execute(
            'SELECT MAX(revision) AS n FROM assets WHERE work_item_id=? AND kind=?',
            (work_item_id, kind),
        ).fetchone()
        revision = max(parent_revision + 1, int(row['n'] or 0) + 1)
        destination_dir = folder(project, target_folder_key(kind, state))
        destination_dir.mkdir(parents=True, exist_ok=True)
        destination = (source if source.parent.resolve() == destination_dir.resolve()
                       else unique_destination(destination_dir, source.name, revision, asset_id))

        # Register and move as one recoverable operation. A filesystem error
        # rolls the DB transaction back; a DB error after moving restores source.
        moved = False
        try:
            if source != destination:
                if move:
                    shutil.move(str(source), str(destination))
                else:
                    shutil.copy2(source, destination)
                moved = True
            conn.execute(
                '''INSERT INTO assets(
                  asset_id, work_item_id, kind, state, revision, parent_asset_id,
                  sha256, size_bytes, current_path, original_name, origin_lane,
                  run_id, provider, prompt_hash, active, created_at, updated_at,
                  metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    asset_id, work_item_id, kind, state, revision, parent_asset_id,
                    digest, destination.stat().st_size, str(destination), source.name,
                    origin_lane or None, run_id or None, provider or None,
                    prompt_hash or None, 0 if state in CLEANUP_STATES else 1,
                    created, created, json.dumps(metadata or {}, ensure_ascii=False),
                ),
            )
        except Exception:
            if moved and move and destination.exists() and not source.exists():
                source.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(destination), str(source))
            elif moved and not move and destination.exists():
                destination.unlink()
            raise
    return get_asset(project, asset_id)


def get_asset(project: Path, asset_id: str) -> dict:
    with connect(project) as conn:
        row = conn.execute('SELECT * FROM assets WHERE asset_id=?', (asset_id,)).fetchone()
    if row is None:
        raise ValueError(f'unknown asset: {asset_id}')
    return dict(row)


def asset_for_path(project: Path, path: Path) -> dict | None:
    """Return the active registry row for an exact filesystem path, if any."""
    resolved = str(Path(path).expanduser().resolve())
    if not db_path(Path(project)).exists():
        return None
    with connect(Path(project)) as conn:
        row = conn.execute(
            'SELECT * FROM assets WHERE current_path=? AND state<>? ORDER BY updated_at DESC LIMIT 1',
            (resolved, 'trashed'),
        ).fetchone()
    return dict(row) if row is not None else None


def latest_asset(
    project: Path,
    work_item_id: str,
    *,
    kind: str = '',
    states: set[str] | None = None,
) -> dict | None:
    sql, args = 'SELECT * FROM assets WHERE work_item_id=?', [work_item_id]
    if kind:
        sql += ' AND kind=?'; args.append(kind)
    if states:
        marks = ','.join('?' for _ in states)
        sql += f' AND state IN ({marks})'; args.extend(sorted(states))
    sql += ' ORDER BY revision DESC, updated_at DESC LIMIT 1'
    with connect(Path(project)) as conn:
        row = conn.execute(sql, args).fetchone()
    return dict(row) if row is not None else None


def set_state(project: Path, asset_id: str, state: str, active: bool | None = None) -> dict:
    project = Path(project).expanduser().resolve()
    if state not in ALLOWED_STATES:
        raise ValueError(f'unsupported asset state: {state}')
    if state in PROTECTED_STATES and active is False:
        raise ValueError(f'protected state cannot be inactive: {state}')
    if active is None:
        active = state not in CLEANUP_STATES and state != 'trashed'
    asset = get_asset(project, asset_id)
    source = Path(asset['current_path'])
    destination = source
    if state in CLEANUP_STATES and source.is_file():
        destination = unique_destination(folder(project, 'work'), source.name, int(asset['revision']), asset_id)
    moved = False
    try:
        if source != destination:
            shutil.move(str(source), str(destination))
            moved = True
        with connect(project) as conn:
            conn.execute('UPDATE assets SET state=?, active=?, current_path=?, updated_at=? WHERE asset_id=?',
                         (state, 1 if active else 0, str(destination), now_iso(), asset_id))
    except Exception:
        if moved and destination.exists() and not source.exists():
            shutil.move(str(destination), str(source))
        raise
    return get_asset(project, asset_id)


def promote(project: Path, asset_id: str) -> dict:
    project = Path(project).expanduser().resolve()
    asset = get_asset(project, asset_id)
    if asset['kind'] not in {'image', 'video'}:
        raise ValueError('only image/video candidates can be promoted')
    source = Path(asset['current_path'])
    if not source.is_file() or sha256(source) != asset['sha256']:
        raise ValueError('source missing or hash mismatch; refusing promotion')
    destination_dir = folder(project, target_folder_key(asset['kind'], 'approved'))
    if asset['state'] in {'approved', 'selected'}:
        try:
            source.resolve().relative_to(destination_dir.resolve())
            return asset
        except ValueError:
            pass
    destination = unique_destination(destination_dir, source.name, int(asset['revision']), asset_id)
    moved = False
    try:
        if source != destination:
            shutil.move(str(source), str(destination))
            moved = True
        with connect(project) as conn:
            conn.execute(
                'UPDATE assets SET state=?, active=1, current_path=?, updated_at=? WHERE asset_id=?',
                ('approved', str(destination), now_iso(), asset_id),
            )
    except Exception:
        if moved and destination.exists() and not source.exists():
            shutil.move(str(destination), str(source))
        raise
    return get_asset(project, asset_id)


def list_assets(project: Path, *, kind: str = '', state: str = '') -> list[dict]:
    sql, args = 'SELECT * FROM assets WHERE 1=1', []
    if kind:
        sql += ' AND kind=?'; args.append(kind)
    if state:
        sql += ' AND state=?'; args.append(state)
    sql += ' ORDER BY kind, work_item_id, revision'
    with connect(project) as conn:
        return [dict(row) for row in conn.execute(sql, args)]


def registry_count(project: Path, *, kind: str = '', states: set[str] | None = None) -> int:
    if not is_v4_project(project) or not db_path(project).exists():
        return 0
    sql, args = 'SELECT COUNT(*) FROM assets WHERE 1=1', []
    if kind:
        sql += ' AND kind=?'; args.append(kind)
    if states:
        marks = ','.join('?' for _ in states)
        sql += f' AND state IN ({marks})'; args.extend(sorted(states))
    with connect(project) as conn:
        return int(conn.execute(sql, args).fetchone()[0])


def audit_project(project: Path) -> dict:
    project = Path(project).expanduser().resolve()
    if not is_v4_project(project):
        return {'applicable': False, 'problems': [], 'warnings': [], 'stats': {'media_schema': 'legacy'}}
    problems, warnings = [], []
    if not db_path(project).exists():
        return {
            'applicable': True,
            'problems': [f'MEDIA_REGISTRY_MISSING: {db_path(project)}'],
            'warnings': [],
            'stats': {'media_schema': MEDIA_SCHEMA_VERSION},
        }

    outside = []
    media = media_root(project).resolve()
    for path in project.rglob('*'):
        if not path.is_file() or path.suffix.lower() not in MEDIA_EXT:
            continue
        try:
            path.resolve().relative_to(media)
        except ValueError:
            outside.append(str(path.relative_to(project)))
    if outside:
        problems.append(
            f'MEDIA_OUTSIDE_CANONICAL_ROOT: {len(outside)} media file(s) outside media/; '
            f'first={outside[0]}'
        )

    rows = list_assets(project)
    by_path = {str(Path(row['current_path']).resolve()): row for row in rows if row['state'] != 'trashed'}
    missing, hash_mismatch = [], []
    for row in rows:
        if row['state'] == 'trashed':
            continue
        path = Path(row['current_path'])
        if not path.is_file():
            missing.append(row['asset_id'])
        elif sha256(path) != row['sha256']:
            hash_mismatch.append(row['asset_id'])
    if missing:
        problems.append(f'REGISTERED_MEDIA_MISSING: {missing[:10]}')
    if hash_mismatch:
        problems.append(f'REGISTERED_MEDIA_HASH_MISMATCH: {hash_mismatch[:10]}')

    unregistered = []
    for path in media.rglob('*'):
        if path.is_file() and path.suffix.lower() in MEDIA_EXT and str(path.resolve()) not in by_path:
            unregistered.append(str(path.relative_to(project)))
    if unregistered:
        problems.append(
            f'UNREGISTERED_MEDIA: {len(unregistered)} file(s) under media/ are absent from the registry; '
            f'first={unregistered[0]}'
        )

    wrong_approved = []
    for row in rows:
        if row['state'] not in {'approved', 'selected'}:
            continue
        expected = folder(project, target_folder_key(row['kind'], 'approved')).resolve()
        try:
            Path(row['current_path']).resolve().relative_to(expected)
        except ValueError:
            wrong_approved.append(row['asset_id'])
    if wrong_approved:
        problems.append(f'APPROVED_MEDIA_IN_WRONG_FOLDER: {wrong_approved[:10]}')

    stats = {
        'media_schema': MEDIA_SCHEMA_VERSION,
        'registered_assets': len(rows),
        'approved_images': registry_count(project, kind='image', states={'approved', 'selected'}),
        'approved_videos': registry_count(project, kind='video', states={'approved', 'selected'}),
        'outside_media': len(outside),
        'unregistered_media': len(unregistered),
        'missing_registered': len(missing),
    }
    return {'applicable': True, 'problems': problems, 'warnings': warnings, 'stats': stats}


def cleanup_candidates(project: Path, older_than_hours: int = 24) -> list[dict]:
    project = Path(project).expanduser().resolve()
    cutoff = dt.datetime.now().astimezone() - dt.timedelta(hours=max(24, older_than_hours))
    rows = list_assets(project)
    by_hash = {}
    for row in rows:
        by_hash.setdefault(row['sha256'], []).append(row)
    candidates = []
    for row in rows:
        if row['state'] not in CLEANUP_STATES or int(row['active']):
            continue
        try:
            updated = dt.datetime.fromisoformat(row['updated_at'])
        except ValueError:
            continue
        if updated > cutoff:
            continue
        path = Path(row['current_path'])
        if not path.is_file():
            continue
        try:
            path.resolve().relative_to(folder(project, 'work').resolve())
        except ValueError:
            # Cleanup candidates must remain in the explicit work area. This
            # protects user sources, approved folders, edits and finals.
            continue
        if row['state'] == 'duplicate':
            keep_exists = any(
                other['asset_id'] != row['asset_id']
                and other['state'] in PROTECTED_STATES
                and Path(other['current_path']).is_file()
                for other in by_hash.get(row['sha256'], [])
            )
            if not keep_exists:
                continue
        candidates.append({
            'asset_id': row['asset_id'],
            'path': str(path),
            'sha256': row['sha256'],
            'state': row['state'],
            'updated_at': row['updated_at'],
            'reason': f'{row["state"]}_inactive_over_{max(24, older_than_hours)}h',
        })
    return candidates


def move_candidates_to_trash(project: Path, candidates: list[dict]) -> list[dict]:
    project = Path(project).expanduser().resolve()
    # Tests may redirect this, but production always defaults to macOS Trash.
    # Nothing in this workflow empties Trash.
    trash_root = Path(os.environ.get('VIDEO_TEAM_TRASH_ROOT', str(Path.home() / '.Trash'))).expanduser().resolve()
    trash_root.mkdir(parents=True, exist_ok=True)
    moved = []
    for item in candidates:
        source = Path(item['path'])
        if not source.is_file() or sha256(source) != item['sha256']:
            continue
        destination = trash_root / f'{project.name}__{item["asset_id"]}__{source.name}'
        if destination.exists():
            destination = trash_root / f'{project.name}__{item["asset_id"]}__{uuid.uuid4().hex[:6]}__{source.name}'
        shutil.move(str(source), str(destination))
        moved_at = now_iso()
        try:
            with connect(project) as conn:
                conn.execute(
                    'INSERT INTO cleanup_journal(asset_id, original_path, trashed_path, sha256, reason, moved_at) '
                    'VALUES (?, ?, ?, ?, ?, ?)',
                    (item['asset_id'], str(source), str(destination), item['sha256'], item['reason'], moved_at),
                )
                conn.execute(
                    'UPDATE assets SET state=?, active=0, current_path=?, updated_at=? WHERE asset_id=?',
                    ('trashed', str(destination), moved_at, item['asset_id']),
                )
        except Exception:
            if destination.exists() and not source.exists():
                source.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(destination), str(source))
            raise
        event = {**item, 'original_path': str(source), 'trashed_path': str(destination), 'moved_at': moved_at}
        with (project / 'cleanup_journal.jsonl').open('a', encoding='utf-8') as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + '\n')
        moved.append(event)
    return moved


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('init'); p.add_argument('--project', required=True)
    p = sub.add_parser('ingest')
    p.add_argument('--project', required=True); p.add_argument('--file', required=True)
    p.add_argument('--kind', required=True, choices=['source', 'audio', 'character', 'image', 'video', 'edit', 'final', 'package'])
    p.add_argument('--state', default='candidate'); p.add_argument('--work-item-id', required=True)
    p.add_argument('--origin-lane', default=''); p.add_argument('--provider', default='')
    p.add_argument('--run-id', default=''); p.add_argument('--prompt-hash', default='')
    p.add_argument('--parent-asset-id'); p.add_argument('--copy', action='store_true')
    p = sub.add_parser('promote'); p.add_argument('--project', required=True); p.add_argument('--asset-id', required=True)
    p = sub.add_parser('set-state'); p.add_argument('--project', required=True); p.add_argument('--asset-id', required=True); p.add_argument('--state', required=True)
    p = sub.add_parser('list'); p.add_argument('--project', required=True); p.add_argument('--kind', default=''); p.add_argument('--state', default='')
    p = sub.add_parser('audit'); p.add_argument('--project', required=True)
    p = sub.add_parser('cleanup')
    p.add_argument('--project', required=True); p.add_argument('--older-than-hours', type=int, default=24)
    p.add_argument('--apply', action='store_true', help='move eligible files to macOS Trash; never empties Trash')
    args = parser.parse_args()
    project = Path(args.project).expanduser().resolve()
    if args.cmd == 'init':
        print(json.dumps({'registry': str(init_registry(project)), 'schema': MEDIA_SCHEMA_VERSION}, ensure_ascii=False, indent=2))
    elif args.cmd == 'ingest':
        result = ingest(
            project, Path(args.file), kind=args.kind, state=args.state,
            work_item_id=args.work_item_id, origin_lane=args.origin_lane,
            provider=args.provider, run_id=args.run_id, prompt_hash=args.prompt_hash,
            parent_asset_id=args.parent_asset_id, move=not args.copy,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.cmd == 'promote':
        print(json.dumps(promote(project, args.asset_id), ensure_ascii=False, indent=2))
    elif args.cmd == 'set-state':
        print(json.dumps(set_state(project, args.asset_id, args.state), ensure_ascii=False, indent=2))
    elif args.cmd == 'list':
        print(json.dumps(list_assets(project, kind=args.kind, state=args.state), ensure_ascii=False, indent=2))
    elif args.cmd == 'audit':
        result = audit_project(project); print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if not result['problems'] else 1
    elif args.cmd == 'cleanup':
        candidates = cleanup_candidates(project, args.older_than_hours)
        moved = move_candidates_to_trash(project, candidates) if args.apply else []
        print(json.dumps({
            'project': str(project), 'mode': 'apply' if args.apply else 'scan',
            'candidates': candidates, 'moved': moved,
            'trash_emptied': False,
        }, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
