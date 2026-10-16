"""Small read-only v4 input proofs. Status words and empty files are not assets."""
from __future__ import annotations
import json
import hashlib
from pathlib import Path
import sqlite3
import media_registry


VISUAL_FIRST_MODE = 'visual_only_no_audio'
VISUAL_FIRST_EVIDENCE_PATHS = {
    'docs/project_overrides.md',  # legacy projects
    'docs/visual_only_authorization.md',  # immutable authorization receipt
}


def visual_first_error(project: Path, manifest: dict) -> str | None:
    """None: not requested; empty: verified explicit-user exception; text: invalid."""
    plan = manifest.get('audio_plan')
    if plan is None:
        return None
    if not isinstance(plan, dict) or plan.get('mode') != VISUAL_FIRST_MODE:
        return 'audio_plan mode must be visual_only_no_audio'
    if plan.get('source') != 'explicit_user_request':
        return 'visual-first requires an explicit user request'
    if not str(plan.get('source_thread_id') or '').strip():
        return 'visual-first source thread is missing'
    message_id = str(plan.get('source_message_id') or '')
    if not message_id.startswith('msg_') or len(message_id) < 20:
        return 'visual-first source message ID is missing'
    if plan.get('timing_status') != 'PROVISIONAL':
        return 'visual-first timing must remain PROVISIONAL'
    if plan.get('delivery_scope') != 'visual_assets_only':
        return 'visual-only delivery scope must be visual_assets_only'
    seconds = plan.get('target_duration_sec')
    if not isinstance(seconds, int) or isinstance(seconds, bool) or seconds <= 0:
        return 'visual-first target duration must be positive seconds'
    if plan.get('evidence_path') not in VISUAL_FIRST_EVIDENCE_PATHS:
        return 'visual-first evidence path is not an approved project receipt'
    evidence = Path(project) / plan['evidence_path']
    if not evidence.is_file():
        return 'visual-first evidence file is missing'
    expected_hash = str(plan.get('evidence_sha256') or '')
    if len(expected_hash) != 64 or any(c not in '0123456789abcdef' for c in expected_hash):
        return 'visual-first evidence hash is invalid'
    content = evidence.read_bytes()
    if hashlib.sha256(content).hexdigest() != expected_hash:
        return 'visual-first evidence file changed'
    try:
        proof = content.decode('utf-8')
    except UnicodeDecodeError:
        return 'visual-first evidence is not UTF-8'
    if VISUAL_FIRST_MODE not in proof or message_id not in proof:
        return 'visual-first evidence lacks mode or source message'
    return ''


def visual_first_active(project: Path, manifest: dict) -> bool:
    return visual_first_error(project, manifest) == ''


def music_error(project: Path, manifest: dict) -> str:
    override_error = visual_first_error(project, manifest)
    if override_error is not None:
        return 'visual-first override invalid: ' + override_error if override_error else ''
    return locked_music_error(project, manifest)


def locked_music_error(project: Path, manifest: dict) -> str:
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
