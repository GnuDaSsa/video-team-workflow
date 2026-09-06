"""Small read-only v4 input proofs. Status words and empty files are not assets."""
from __future__ import annotations
import json
from pathlib import Path
import sqlite3
import media_registry


def music_error(project: Path, manifest: dict) -> str:
    music = manifest.get('music') or {}
    if not isinstance(music, dict) or music.get('status') != 'LOCKED':
        return 'music status must be LOCKED with a registered selected audio'
    db = media_registry.db_path(project)
    if not db.is_file():
        return 'music registry is missing'
    asset_id = music.get('asset_id') or music.get('locked_asset_id')
    file = music.get('music_file') or music.get('path') or manifest.get('music_file')
    with sqlite3.connect(db.as_uri() + '?mode=ro', uri=True) as conn:
        conn.row_factory = sqlite3.Row
        if asset_id:
            row = conn.execute('SELECT * FROM assets WHERE asset_id=?', (asset_id,)).fetchone()
        elif file:
            path = Path(file)
            path = path if path.is_absolute() else project / path
            row = conn.execute('SELECT * FROM assets WHERE current_path=?', (str(path.resolve()),)).fetchone()
        else:
            return 'music lock must identify asset_id (or exact registered music_file)'
    if not row or row['kind'] != 'audio' or row['state'] != 'locked' or not row['active']:
        return 'selected music is not an active locked audio asset'
    path = Path(row['current_path']).resolve()
    if not path.is_relative_to((project / 'media').resolve()):
        return 'locked audio is outside canonical media'
    if not path.is_file() or path.stat().st_size <= 0 or media_registry.sha256(path) != row['sha256']:
        return 'locked audio file is missing/empty/changed'
    meta = json.loads(row['metadata_json'])
    probe = meta.get('ffprobe') or meta.get('probe') or meta
    fmt = probe.get('format') or probe
    duration = fmt.get('duration') or meta.get('duration_sec')
    streams = probe.get('streams') or []
    codec = meta.get('codec') or meta.get('codec_name') or next(
        (s.get('codec_name') for s in streams if s.get('codec_type') == 'audio'), None)
    try:
        if float(duration) <= 0 or not codec:
            return 'locked audio requires positive duration and audio codec evidence'
    except (TypeError, ValueError):
        return 'locked audio requires positive duration and audio codec evidence'
    return ''


def planner_error(project: Path) -> str:
    path = project / 'lanes/planner/multi_reference_block_map.json'
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        return 'planner block map is missing or invalid JSON'
    blocks = data.get('blocks') if isinstance(data, dict) else data
    if not isinstance(blocks, list) or not blocks:
        return 'planner block map must contain a non-empty blocks list'
    seen = set()
    for block in blocks:
        if not isinstance(block, dict):
            return 'planner block must be an object'
        block_id = block.get('block_id') or block.get('id')
        if not isinstance(block_id, str) or not block_id.strip() or block_id in seen:
            return 'planner block IDs must be non-empty and unique'
        seen.add(block_id)
        if not any(block.get(k) for k in ('covered_cuts', 'cuts', 'shot_roles', 'scene_plan')):
            return 'planner block requires cut ownership or planned shot structure'
    return ''
