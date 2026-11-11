#!/usr/bin/env python3
"""Fixed pre-production pipeline and production shelf (runtime v5, 2026-10-16).

Stages, each one file + one lock:
  P0 concept     preprod/00_concept/concept_lock.json     (user approval)
  P1 bible       preprod/01_bible/style_bible.json        (image guide)
  P2 storyboard  preprod/02_storyboard/storyboard.json    (콘티, user approval)
  P3 images      preprod/03_image_prompts/image_plan.json (all refs approved in registry)
  P4 shelf       preprod/04_shelf/<BLOCK>/                (prompt.txt + settings + refs, user release)
Production consumes only released shelf blocks; it never authors or edits prompts.
A changed upstream file makes its lock STALE and closes every downstream gate.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import unicodedata

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generation_settings  # noqa: E402
import media_registry  # noqa: E402
import prompt_packet_utils  # noqa: E402

SCHEMA = 'preprod_v1'
STAGES = ('concept', 'bible', 'storyboard', 'images', 'shelf')
STAGE_FILES = {
    'concept': '00_concept/concept_lock.json',
    'bible': '01_bible/style_bible.json',
    'storyboard': '02_storyboard/storyboard.json',
    'images': '03_image_prompts/image_plan.json',
}
USER_APPROVED_STAGES = {'concept', 'storyboard', 'shelf'}
PROMPT_LIMIT = prompt_packet_utils.SEEDANCE_PROMPT_CHAR_LIMIT
STYLE_BLOCK_LIMIT = 600
IDENTITY_BLOCK_LIMIT = 350
MAX_REFS = 7
MAX_SHOTS = 4
# Seedance 2.5 (Runway: up to 30 image refs, 4-30s takes): wider per-block envelope.
MAX_REFS_25 = 12
MAX_SHOTS_25 = 8
MODES = {'mv', 'contest', 'tourism', 'institution', 'shortform', 'other'}
MEDIUMS = {'2d_animation', '3d_animation', 'live_action', 'mixed'}
ASPECTS = {'16:9', '9:16', '1:1', '4:3', '3:4', '21:9'}
AUDIO_ROUTES = {'native_diegetic_no_dialogue', 'native_dialogue', 'silent', 'music_reference'}
REF_PURPOSES = {'identity', 'environment', 'prop', 'style'}
SHOT_SIZES = (
    'extreme wide shot', 'wide shot', 'full shot', 'medium wide shot', 'medium shot',
    'medium close-up', 'close-up', 'extreme close-up', 'insert shot',
)
ANGLES = ('eye level', 'low angle', 'high angle', 'overhead', 'top-down', 'dutch angle',
          'over-the-shoulder', 'worm\'s-eye', 'bird\'s-eye', 'pov')
# prompt-facing camera phrase -> knowledge-router camera category
CAMERA_MOVES = {
    'static': 'static', 'locked-off': 'static', 'slow push in': 'slow_push', 'push in': 'slow_push',
    'pull out': 'dolly', 'dolly in': 'dolly', 'dolly out': 'dolly',
    'truck left': 'tracking', 'truck right': 'tracking', 'tracking': 'tracking', 'follow': 'tracking',
    'pan left': 'pan', 'pan right': 'pan', 'tilt up': 'pan', 'tilt down': 'pan', 'whip pan': 'pan',
    'orbit': 'orbit', 'crane up': 'crane', 'crane down': 'crane', 'handheld': 'handheld',
    'fpv': 'fpv', 'rack focus': 'rack_focus', 'macro': 'macro', 'pov': 'pov',
}
SHOT_SIZE_ROLE = {'close-up': 'close_up', 'extreme close-up': 'close_up', 'medium close-up': 'close_up',
                  'insert shot': 'object_macro', 'extreme wide shot': 'environment', 'wide shot': 'environment'}
HEX = re.compile(r'#[0-9A-Fa-f]{6}')
ID = re.compile(r'[A-Z][A-Z0-9_]{1,40}')


# --- small helpers -----------------------------------------------------------

def now() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec='seconds')


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def root(project: Path) -> Path:
    return project / 'preprod'


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return None


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def is_preprod_project(project: Path) -> bool:
    return (root(project) / 'PREPROD_V1').is_file()


def english(text: str) -> bool:
    return prompt_packet_utils.language_stats(text)['english_dominant']


def nfc(text: str) -> str:
    return prompt_packet_utils.normalize_prompt(unicodedata.normalize('NFC', text))


def lock_path(project: Path, stage: str, block: str = '') -> Path:
    if stage == 'shelf':
        return root(project) / '04_shelf' / block / 'SHELF_LOCK.json'
    return root(project) / 'locks' / f'{stage}.json'


def stage_file(project: Path, stage: str) -> Path:
    return root(project) / STAGE_FILES[stage]


def _approval(quote: str, source: str) -> dict:
    return {'source': source, 'quote': quote.strip(), 'at': now()}


def _need(errors: list, cond: bool, code: str) -> None:
    if not cond:
        errors.append(code)


# --- stage validators ---------------------------------------------------------

def validate_concept(project: Path) -> list[str]:
    data = read_json(stage_file(project, 'concept'))
    if not isinstance(data, dict):
        return ['concept_missing_or_invalid_json']
    e: list[str] = []
    options = root(project) / '00_concept' / 'concept_options.md'
    count = len(re.findall(r'^##\s+Option\b', options.read_text(encoding='utf-8'), re.M)) if options.is_file() else 0
    _need(e, count >= 3, f'concept_options_need_3_options_found_{count}')
    for key in ('title', 'logline', 'audience', 'selected_option'):
        _need(e, bool(str(data.get(key) or '').strip()), f'concept_missing:{key}')
    _need(e, data.get('mode') in MODES, f'concept_bad_mode:{data.get("mode")}')
    _need(e, data.get('medium') in MEDIUMS, f'concept_bad_medium:{data.get("medium")}')
    if data.get('medium') == 'mixed':
        comps = set(data.get('medium_components') or [])
        _need(e, len(comps) >= 2 and comps <= MEDIUMS - {'mixed'}, 'concept_mixed_needs_components')
    _need(e, data.get('aspect_ratio') in ASPECTS, f'concept_bad_aspect:{data.get("aspect_ratio")}')
    _need(e, isinstance(data.get('target_runtime_sec'), (int, float)) and data['target_runtime_sec'] > 0,
          'concept_missing:target_runtime_sec')
    arc = data.get('emotional_arc') or {}
    for beat in ('hook', 'build', 'peak', 'out'):
        _need(e, bool(str(arc.get(beat) or '').strip()), f'concept_arc_missing:{beat}')
    _need(e, isinstance(data.get('must_avoid'), list), 'concept_missing:must_avoid')
    _need(e, data.get('music', 'track') in {'track', 'none'}, f'concept_bad_music:{data.get("music")}')
    _need(e, data.get('generation_tier', 'Explore Mode') in {'Explore Mode', 'Credits'},
          f'concept_bad_generation_tier:{data.get("generation_tier")}')
    return e


def concept_without_music(project: Path) -> bool:
    """A locked concept may decide `music: none`; the music lane is then skipped."""
    if not is_preprod_project(project) or lock_state(project, 'concept')['state'] != 'LOCKED':
        return False
    return (read_json(stage_file(project, 'concept')) or {}).get('music') == 'none'


def validate_bible(project: Path) -> list[str]:
    data = read_json(stage_file(project, 'bible'))
    if not isinstance(data, dict):
        return ['bible_missing_or_invalid_json']
    e: list[str] = []
    palette = data.get('palette_hex') or []
    _need(e, 3 <= len(palette) <= 7 and all(HEX.fullmatch(str(c)) for c in palette), 'bible_palette_hex_3_to_7')
    for key in ('lighting', 'texture', 'lens_grammar'):
        _need(e, bool(str(data.get(key) or '').strip()), f'bible_missing:{key}')
    _need(e, isinstance(data.get('forbidden_looks'), list) and data['forbidden_looks'], 'bible_missing:forbidden_looks')
    block = str(data.get('style_block_en') or '')
    _need(e, bool(block.strip()), 'bible_missing:style_block_en')
    _need(e, len(block) <= STYLE_BLOCK_LIMIT, f'bible_style_block_over_{STYLE_BLOCK_LIMIT}')
    if block:
        _need(e, english(block), 'bible_style_block_not_english')
    ids = set()
    for kind in ('characters', 'locations'):
        for item in data.get(kind) or []:
            iid = str(item.get('id') or '')
            _need(e, bool(ID.fullmatch(iid)) and iid not in ids, f'bible_{kind}_bad_or_duplicate_id:{iid}')
            ids.add(iid)
            text = str(item.get('identity_block_en' if kind == 'characters' else 'description_en') or '')
            _need(e, bool(text) and english(text), f'bible_{iid}_block_missing_or_not_english')
            if kind == 'characters':
                _need(e, len(text) <= IDENTITY_BLOCK_LIMIT, f'bible_{iid}_identity_over_{IDENTITY_BLOCK_LIMIT}')
                _need(e, bool(item.get('sheet_ref_id')), f'bible_{iid}_missing_sheet_ref_id')
    return e


def bible(project: Path) -> dict:
    return read_json(stage_file(project, 'bible')) or {}


def storyboard(project: Path) -> dict:
    return read_json(stage_file(project, 'storyboard')) or {}


def image_plan(project: Path) -> dict:
    return read_json(stage_file(project, 'images')) or {}


def validate_storyboard(project: Path) -> list[str]:
    data = read_json(stage_file(project, 'storyboard'))
    if not isinstance(data, dict):
        return ['storyboard_missing_or_invalid_json']
    e: list[str] = []
    b = bible(project)
    known = {str(i.get('id')) for k in ('characters', 'locations') for i in b.get(k) or []}
    blocks = data.get('blocks') or []
    _need(e, bool(blocks), 'storyboard_no_blocks')
    gen_model = (data.get('generation') or {}).get('model') or 'Seedance 2.0'
    _need(e, gen_model in generation_settings.MODEL_MAX_DURATION_SEC, f'storyboard_unknown_generation_model:{gen_model}')
    max_refs, max_shots = (MAX_REFS_25, MAX_SHOTS_25) if gen_model == 'Seedance 2.5' else (MAX_REFS, MAX_SHOTS)
    model_cap = generation_settings.MODEL_MAX_DURATION_SEC.get(gen_model, 15)
    seen_blocks, seen_shots = set(), set()
    for index, block in enumerate(blocks, 1):
        bid = str(block.get('block_id') or '')
        tag = bid or f'#{index}'
        _need(e, bool(ID.fullmatch(bid)) and bid not in seen_blocks, f'storyboard_bad_or_duplicate_block_id:{tag}')
        seen_blocks.add(bid)
        _need(e, block.get('order') == index, f'storyboard_{tag}_order_must_be_{index}')
        _need(e, bool(str(block.get('purpose') or '').strip()), f'storyboard_{tag}_missing_purpose')
        _need(e, block.get('audio_route') in AUDIO_ROUTES, f'storyboard_{tag}_bad_audio_route')
        duration = block.get('duration_sec')
        expected = generation_settings.expected_duration(project, bid)[1].get('expected_duration_sec')
        _need(e, duration == expected,
              f'storyboard_{tag}_duration_{duration}_must_match_lock_{expected}')
        _need(e, isinstance(duration, int) and duration <= model_cap,
              f'storyboard_{tag}_duration_{duration}_over_{gen_model}_cap_{model_cap}')
        sheets = {str(c.get('id')): str(c.get('sheet_ref_id')) for c in b.get('characters') or []}
        for ref in block.get('cast') or []:
            _need(e, ref in known, f'storyboard_{tag}_unknown_cast:{ref}')
            # Character-sheet gate: the cast member's sheet rides along on every generation.
            if ref in sheets:
                _need(e, sheets[ref] in (block.get('refs') or []),
                      f'storyboard_{tag}_refs_missing_sheet_of_{ref}:{sheets[ref]}')
        _need(e, block.get('location_id') in known, f'storyboard_{tag}_unknown_location:{block.get("location_id")}')
        refs = block.get('refs') or []
        _need(e, 1 <= len(refs) <= max_refs and len(set(refs)) == len(refs),
              f'storyboard_{tag}_refs_must_be_1_to_{max_refs}_unique')
        _need(e, bool(str(block.get('end_frame') or '').strip()), f'storyboard_{tag}_missing_end_frame')
        shots = block.get('shots') or []
        _need(e, 1 <= len(shots) <= max_shots, f'storyboard_{tag}_shots_must_be_1_to_{max_shots}')
        cursor = 0.0
        for s_index, shot in enumerate(shots, 1):
            sid = str(shot.get('shot_id') or '')
            stag = f'{tag}.{sid or s_index}'
            _need(e, sid == f'{bid}_S{s_index}' and sid not in seen_shots, f'storyboard_{stag}_shot_id_must_be_{bid}_S{s_index}')
            seen_shots.add(sid)
            start, end = shot.get('start_sec'), shot.get('end_sec')
            ok_time = isinstance(start, (int, float)) and isinstance(end, (int, float))
            _need(e, ok_time and abs(start - cursor) < 0.01 and end > start, f'storyboard_{stag}_time_not_contiguous')
            cursor = end if ok_time else cursor
            _need(e, shot.get('shot_size') in SHOT_SIZES, f'storyboard_{stag}_bad_shot_size:{shot.get("shot_size")}')
            _need(e, shot.get('angle') in ANGLES, f'storyboard_{stag}_bad_angle:{shot.get("angle")}')
            _need(e, shot.get('camera_move') in CAMERA_MOVES, f'storyboard_{stag}_bad_camera_move:{shot.get("camera_move")}')
            for key in ('composition', 'action'):
                _need(e, bool(str(shot.get(key) or '').strip()), f'storyboard_{stag}_missing:{key}')
            for phrase in shot.get('must_include') or []:
                _need(e, isinstance(phrase, str) and 2 <= len(phrase) <= 80, f'storyboard_{stag}_bad_must_include')
        _need(e, isinstance(duration, (int, float)) and abs(cursor - duration) < 0.01,
              f'storyboard_{tag}_shots_end_{cursor}_not_{duration}')
    return e


def validate_images(project: Path) -> list[str]:
    data = read_json(stage_file(project, 'images'))
    if not isinstance(data, dict):
        return ['image_plan_missing_or_invalid_json']
    e: list[str] = []
    refs = {}
    for item in data.get('references') or []:
        rid = str(item.get('ref_id') or '')
        _need(e, bool(ID.fullmatch(rid)) and rid not in refs, f'images_bad_or_duplicate_ref_id:{rid}')
        refs[rid] = item
        _need(e, item.get('purpose') in REF_PURPOSES, f'images_{rid}_bad_purpose')
        prompt = root(project) / '03_image_prompts' / f'{rid}.prompt.txt'
        if item.get('source') == 'user_supplied':
            pass
        elif not prompt.is_file():
            e.append(f'images_{rid}_prompt_file_missing')
        elif not english(prompt.read_text(encoding='utf-8')):
            e.append(f'images_{rid}_prompt_not_english')
        asset_id = item.get('asset_id')
        if not asset_id:
            e.append(f'images_{rid}_not_generated_or_not_approved')
            continue
        try:
            asset = media_registry.get_asset(project, asset_id)
        except (KeyError, ValueError, Exception):  # registry raises its own lookup errors
            e.append(f'images_{rid}_asset_not_registered:{asset_id}')
            continue
        _need(e, asset.get('state') in {'approved', 'selected', 'locked', 'source'},
              f'images_{rid}_asset_not_approved:{asset.get("state")}')
    needed = {r for blk in storyboard(project).get('blocks') or [] for r in blk.get('refs') or []}
    needed |= {str(c.get('sheet_ref_id')) for c in bible(project).get('characters') or []}
    for missing in sorted(needed - set(refs)):
        e.append(f'images_plan_missing_ref:{missing}')
    return e


PLACEHOLDER = re.compile(r'<[^<>\n]{2,120}>')


def _no_placeholders(stage: str, validator):
    """Template skeletons use `<...>`; an unfilled field must never be lockable."""
    def run(project: Path) -> list[str]:
        errors = validator(project)
        paths = [stage_file(project, stage)]
        if stage == 'concept':
            paths.append(root(project) / '00_concept' / 'concept_options.md')
        for path in paths:
            if path.is_file():
                found = PLACEHOLDER.findall(path.read_text(encoding='utf-8'))
                if found:
                    errors.append(f'{stage}_unfilled_placeholder:{path.name}:{found[0]}')
        return errors
    return run


VALIDATORS = {stage: _no_placeholders(stage, fn) for stage, fn in (
    ('concept', validate_concept), ('bible', validate_bible),
    ('storyboard', validate_storyboard), ('images', validate_images))}


# --- locks ---------------------------------------------------------------------

def lock_state(project: Path, stage: str) -> dict:
    """MISSING | INVALID | DRAFT | LOCKED | STALE for one upstream stage."""
    path = stage_file(project, stage)
    if not path.is_file():
        return {'stage': stage, 'state': 'MISSING', 'errors': [f'{stage}_file_missing:{path}']}
    errors = VALIDATORS[stage](project)
    lock = read_json(lock_path(project, stage)) or {}
    if errors:
        return {'stage': stage, 'state': 'INVALID', 'errors': errors}
    if not lock:
        return {'stage': stage, 'state': 'DRAFT', 'errors': []}
    if lock.get('sha256') != sha(path) or any(
            (lock_state(project, up)['state'] != 'LOCKED')
            or (read_json(lock_path(project, up)) or {}).get('sha256') != lock.get('upstream', {}).get(up)
            for up in STAGES[:STAGES.index(stage)]):
        return {'stage': stage, 'state': 'STALE', 'errors': [f'{stage}_changed_after_lock_or_upstream_relocked']}
    return {'stage': stage, 'state': 'LOCKED', 'errors': [], 'lock': lock}


def lock_stage(project: Path, stage: str, quote: str = '') -> dict:
    if stage not in VALIDATORS:
        raise ValueError(f'lock: unknown stage {stage}')
    for up in STAGES[:STAGES.index(stage)]:
        state = lock_state(project, up)['state']
        if state != 'LOCKED':
            raise ValueError(f'UPSTREAM_NOT_LOCKED: {up} is {state}; lock stages in order')
    errors = VALIDATORS[stage](project)
    if errors:
        raise ValueError(f'{stage.upper()}_INVALID: ' + '; '.join(errors[:12]))
    import claude_author
    if stage == 'concept' and claude_author.get_mode(project) not in claude_author.MODES:
        raise ValueError('AUTHOR_MODE_UNSET: ask the user once "Claude 프롬프팅 / Codex" and run '
                         'author set-mode --mode claude|codex --approval-quote "<user words>"')
    authorship = claude_author.lock_authorship_errors(project, stage)
    if authorship:
        raise ValueError('CLAUDE_MODE_AUTHORSHIP: ' + '; '.join(authorship)
                         + ' — rerun `author run` (with --feedback for changes); Codex must not edit these files')
    if stage in USER_APPROVED_STAGES and not quote.strip():
        raise ValueError(f'USER_APPROVAL_REQUIRED: lock {stage} only with --approval-quote of the user message')
    previous = read_json(lock_path(project, stage))
    if previous:
        _supersede(project, stage, previous)
    path = stage_file(project, stage)
    lock = {
        'schema': SCHEMA, 'stage': stage, 'file': str(path.relative_to(project)), 'sha256': sha(path),
        'revision': int((previous or {}).get('revision') or 0) + 1,
        'upstream': {up: (read_json(lock_path(project, up)) or {}).get('sha256') for up in STAGES[:STAGES.index(stage)]},
        'approval': _approval(quote, 'user') if quote.strip() else _approval('lane self-check', 'lane'),
    }
    write_json(lock_path(project, stage), lock)
    if stage == 'storyboard':
        derive_planner_files(project)
    return lock


def _supersede(project: Path, stage: str, previous: dict) -> None:
    """Keep exactly one current version in place; move the old locked copy aside."""
    dest = root(project) / '_superseded' / f'{stage}_R{previous.get("revision", 0)}'
    dest.mkdir(parents=True, exist_ok=True)
    write_json(dest / 'lock.json', previous)
    src = stage_file(project, stage)
    if src.is_file():
        shutil.copy2(src, dest / src.name)


# --- derived planner files (compatibility with lane gates / router) --------------

def derive_planner_files(project: Path) -> None:
    """Planner artifacts are generated from the storyboard, never hand-written."""
    board, concept = storyboard(project), read_json(stage_file(project, 'concept')) or {}
    mediums = concept.get('medium_components') or [concept.get('medium')]
    blocks, attrs = [], []
    for block in board.get('blocks') or []:
        shots = block.get('shots') or []
        blocks.append({
            'block_id': block['block_id'], 'order': block['order'],
            'covered_cuts': [s['shot_id'] for s in shots], 'refs': block.get('refs'),
            'duration_sec': block['duration_sec'], 'derived_from': 'preprod/02_storyboard/storyboard.json',
        })
        roles = {SHOT_SIZE_ROLE.get(s['shot_size'], 'action') for s in shots}
        attrs.append({
            'block_id': block['block_id'], 'mediums': [m for m in mediums if m],
            'shot_roles': sorted(roles | ({'identity'} if block.get('cast') else set())),
            'cameras': sorted({CAMERA_MOVES[s['camera_move']] for s in shots}),
            'risks': sorted(set(block.get('risks') or [])),
            'methods': ['storyboard'], 'audio': ['diegetic' if 'diegetic' in block['audio_route'] else 'dialogue'
                                                  if 'dialogue' in block['audio_route'] else 'no_dialogue'],
        })
    planner = project / 'lanes' / 'planner'
    write_json(planner / 'multi_reference_block_map.json', {'schema': 'derived_from_storyboard_v1', 'blocks': blocks})
    write_json(planner / 'video_attributes.json', {
        'global': {'project_type': concept.get('mode'), 'derived_from': 'preprod/02_storyboard/storyboard.json'},
        'blocks': attrs})


# --- shelf ----------------------------------------------------------------------

def shelf_dir(project: Path, block: str) -> Path:
    return root(project) / '04_shelf' / block


def _block(project: Path, block_id: str) -> dict:
    for block in storyboard(project).get('blocks') or []:
        if block.get('block_id') == block_id:
            return block
    raise ValueError(f'UNKNOWN_BLOCK: {block_id} is not in the locked storyboard')


def ref_rows(project: Path, block: dict) -> list[dict]:
    plan = {r['ref_id']: r for r in image_plan(project).get('references') or []}
    rows = []
    for index, rid in enumerate(block.get('refs') or [], 1):
        asset = media_registry.get_asset(project, plan[rid]['asset_id'])
        path = Path(asset['current_path'] if 'current_path' in asset else asset['path'])
        if not path.is_absolute():
            path = project / path
        rows.append({'token': f'@Image{index}', 'ref_id': rid, 'purpose': plan[rid]['purpose'],
                     'role': plan[rid].get('role_en') or plan[rid]['purpose'],
                     'asset_id': asset['asset_id'], 'path': str(path), 'sha256': asset['sha256']})
    return rows


def generation(project: Path) -> dict:
    """Provider model for the whole storyboard: `generation: {model, resolution}` in storyboard.json.
    Absent → Seedance 2.0 (the workflow default; 2.5 only on explicit user request)."""
    gen = (read_json(stage_file(project, 'storyboard')) or {}).get('generation') or {}
    model = gen.get('model') or 'Seedance 2.0'
    if model not in generation_settings.MODEL_MAX_DURATION_SEC:
        raise ValueError(f'UNKNOWN_PROVIDER_MODEL: {model}')
    return {'model': model, 'resolution': gen.get('resolution')}


def write_shelf_brief(project: Path, block_id: str) -> Path:
    """Deterministic authoring brief: everything the prompt must contain, nothing else."""
    for stage in ('concept', 'bible', 'storyboard', 'images'):
        state = lock_state(project, stage)['state']
        if state != 'LOCKED':
            raise ValueError(f'UPSTREAM_NOT_LOCKED: {stage} is {state}')
    block, b = _block(project, block_id), bible(project)
    concept = read_json(stage_file(project, 'concept')) or {}
    rows = ref_rows(project, block)
    out = shelf_dir(project, block_id)
    out.mkdir(parents=True, exist_ok=True)
    gen = generation(project)
    settings = {
        'model': gen['model'], 'duration_sec': block['duration_sec'], 'aspect_ratio': concept['aspect_ratio'],
        'resolution': gen['resolution'] or (b.get('resolution') or '720p'), 'audio': 'OFF' if block['audio_route'] == 'silent' else 'ON',
        'mode': 'Multi-reference', 'audio_route': block['audio_route'],
    }
    if concept.get('generation_tier'):
        settings['generation_tier'] = concept['generation_tier']
    write_json(out / 'settings.json', settings)
    write_json(out / 'refs.json', {'block_id': block_id, 'references': rows})
    chars = {c['id']: c for c in b.get('characters') or []}
    shots = block['shots']
    header = (f'{block["duration_sec"]} seconds, one continuous shot:' if len(shots) == 1
              else f'{block["duration_sec"]} seconds, {len(shots)} shots:')
    lines = [f'# Shelf brief {block_id} (generated; do not edit)', '',
             'Write `prompt.txt` in English. Production will paste it unchanged.', '',
             f'- No length target; Runway accepts up to {PROMPT_LIMIT} chars. No file names, paths, gate words or notes.',
             f'- First line exactly: `{header}`',
             '- Include the STYLE block verbatim, and each cast IDENTITY block verbatim.',
             '- Bind every token below to its role once; use no other @ tokens.']
    if len(shots) > 1:
        lines.append('- Start each shot with `Shot N (a-bs):` using the times below.')
    if gen['model'] == 'Seedance 2.5':
        lines += ['- Seedance 2.5 layout (Runway guide): after the header and STYLE/IDENTITY blocks, a REFERENCES list '
                  '(one line per token, one exclusive role each), then a one-sentence SUMMARY of subject, place, event, '
                  'style and camera feel, then the timed shots, then Sound, then a CONSISTENCY note restating the 2-3 '
                  'fixed traits per character and the paper/line look, then the End frame.',
                  '- Shot times are contiguous whole seconds. A shot longer than ~4s may chain two camera moves; '
                  'restate the lead\'s fixed traits at each major beat. Describe visuals positively; negatives only '
                  'for subtitles, music and text.']
    lines += ['- Inside each shot use the exact shot size, angle and camera move phrases, plus every MUST phrase.',
              '- End with the END FRAME.', '', '## STYLE (verbatim)', b['style_block_en'], '', '## IDENTITY (verbatim)']
    lines += [chars[c]['identity_block_en'] for c in block.get('cast') or []] or ['(no cast)']
    lines += ['', '## REFERENCES']
    lines += [f'- {r["token"]} = {r["role"]} ({r["purpose"]})' for r in rows]
    lines += ['', f'## SHOTS ({block["purpose"]})']
    for i, s in enumerate(shots, 1):
        lines.append(f'- Shot {i} ({_t(s["start_sec"])}-{_t(s["end_sec"])}s): {s["shot_size"]}, {s["angle"]}, '
                     f'{s["camera_move"]}{", " + s["lens"] if s.get("lens") else ""}. COMPOSITION: {s["composition"]}. '
                     f'ACTION: {s["action"]}.' + (f' MUST: {"; ".join(s["must_include"])}.' if s.get('must_include') else ''))
    lines += ['', '## END FRAME', block['end_frame'], '', '## AUDIO', block['audio_route'],
              '', '## AVOID', ', '.join(b.get('forbidden_looks') or [])]
    knowledge = _select_knowledge(project, block_id)
    if knowledge:
        lines += ['', '## CRAFT NOTES (selected wiki packet; apply, do not quote)', f'Read: {knowledge}']
    (out / 'brief.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return out / 'brief.md'


def _select_knowledge(project: Path, block_id: str) -> str:
    """Run the bounded wiki router when the project requires it; the pack picks up the receipt."""
    config = (read_json(project / 'manifest.json') or {}).get('knowledge_routing') or {}
    if not config.get('enabled'):
        return ''
    import video_knowledge_router as router
    receipt = router.select_knowledge(
        project, block_id,
        catalog_path=Path(config['catalog']) if config.get('catalog') else None,
        budget_chars=int(config.get('budget_chars') or router.DEFAULT_BUDGET_CHARS),
        max_selections=int(config.get('max_selections') or router.DEFAULT_MAX_SELECTIONS))
    return str(receipt['context'])


def _t(value: float) -> str:
    return str(int(value)) if float(value).is_integer() else str(value)


def _shot_sections(prompt: str, count: int) -> list[str]:
    if count == 1:
        return [prompt]
    marks = [re.search(rf'^Shot {i} \(', prompt, re.M) for i in range(1, count + 1)]
    if not all(marks):
        return []
    cuts = [m.start() for m in marks] + [len(prompt)]
    return [prompt[cuts[i]:cuts[i + 1]] for i in range(count)]


def validate_shelf_prompt(project: Path, block_id: str) -> list[str]:
    out = shelf_dir(project, block_id)
    path = out / 'prompt.txt'
    if not path.is_file():
        return ['shelf_prompt_missing']
    raw = path.read_text(encoding='utf-8')
    prompt = nfc(raw)
    e: list[str] = []
    _need(e, raw == unicodedata.normalize('NFC', raw), 'shelf_prompt_not_nfc')
    _need(e, len(prompt) <= PROMPT_LIMIT, f'shelf_prompt_over_{PROMPT_LIMIT}:{len(prompt)}')
    _need(e, english(prompt), 'shelf_prompt_not_english')
    block, b = _block(project, block_id), bible(project)
    shots = block['shots']
    header = (f'{block["duration_sec"]} seconds, one continuous shot:' if len(shots) == 1
              else f'{block["duration_sec"]} seconds, {len(shots)} shots:')
    _need(e, prompt.split('\n', 1)[0].strip() == header, f'shelf_first_line_must_be:{header}')
    _need(e, b['style_block_en'].strip() in prompt, 'shelf_style_block_not_verbatim')
    chars = {c['id']: c for c in b.get('characters') or []}
    for cid in block.get('cast') or []:
        _need(e, chars[cid]['identity_block_en'].strip() in prompt, f'shelf_identity_not_verbatim:{cid}')
    tokens = set(re.findall(r'@(?:Image|Video|Audio)\d+', prompt))
    expected = {f'@Image{i}' for i in range(1, len(block['refs']) + 1)}
    _need(e, tokens == expected, f'shelf_tokens_{sorted(tokens)}_must_equal_{sorted(expected)}')
    sections = _shot_sections(prompt, len(shots))
    if not sections:
        e.append('shelf_shot_markers_missing_or_out_of_order')
    for i, (shot, text) in enumerate(zip(shots, sections), 1):
        low = text.casefold()
        if len(shots) > 1:
            marker = f'Shot {i} ({_t(shot["start_sec"])}-{_t(shot["end_sec"])}s)'
            _need(e, text.startswith(marker), f'shelf_shot_{i}_marker_must_be:{marker}')
        for key in ('shot_size', 'angle', 'camera_move'):
            _need(e, shot[key].casefold() in low, f'shelf_shot_{i}_missing_{key}:{shot[key]}')
        for phrase in shot.get('must_include') or []:
            _need(e, phrase.casefold() in low, f'shelf_shot_{i}_missing_must:{phrase}')
    for found in re.findall(r'(?<![\d.])(\d{1,2})\s*(?:seconds?|sec)\b', prompt, re.I):
        _need(e, int(found) == block['duration_sec'], f'shelf_conflicting_duration_mention:{found}')
    return e


def build_pack(project: Path, block_id: str) -> Path:
    out = shelf_dir(project, block_id)
    block = _block(project, block_id)
    prompt = nfc((out / 'prompt.txt').read_text(encoding='utf-8'))
    refs = (read_json(out / 'refs.json') or {}).get('references') or []
    shots = block['shots']
    pack = {
        'block_id': block_id, 'production_status': 'READY_FOR_EXECUTION', 'duration_sec': block['duration_sec'],
        'prompt_language': 'en-US', 'prompt_style_version': prompt_packet_utils.ENGLISH_PROMPT_STYLE_VERSION,
        'authoring_contract': prompt_packet_utils.ENGLISH_AUTHORING_CONTRACT,
        'prompt': prompt, 'prompt_file': str(out / 'prompt.txt'), 'prompt_sha256': prompt_packet_utils.prompt_sha256(prompt),
        'settings': read_json(out / 'settings.json'),
        'provider_model': (read_json(out / 'settings.json') or {}).get('model') or 'Seedance 2.0',
        'reference_role_map': [{'token': r['token'], 'role': r['role'], 'asset_id': r['asset_id'],
                                'path': r['path'], 'sha256': r['sha256']} for r in refs],
        'shot_grammar': prompt_packet_utils.SINGLE_SHOT_GRAMMAR if len(shots) == 1 else prompt_packet_utils.MULTI_SHOT_GRAMMAR,
        'audio_route': block['audio_route'],
        'prompt_rules_used': ['anchors_not_cages', prompt_packet_utils.MULTIMODAL_BINDING_RULE, 'preprod_shelf_v1'],
        'covered_cuts': [s['shot_id'] for s in shots],
        'storyboard_lock_sha256': (read_json(lock_path(project, 'storyboard')) or {}).get('sha256'),
    }
    if len(shots) > 1:
        pack['planned_scene_count'] = len(shots)
        pack['scene_plan'] = [{
            'scene_id': s['shot_id'], 'start_sec': s['start_sec'], 'end_sec': s['end_sec'],
            'covered_cuts': [s['shot_id']], 'reference_tokens': [r['token'] for r in refs],
            'action': s['action'], 'camera': f'{s["shot_size"]}, {s["angle"]}, {s["camera_move"]}',
            'edit_out': s.get('edit_out') or block['end_frame'],
        } for s in shots]
    receipt = read_json(project / 'lanes' / 'seedance' / 'knowledge' / f'{block_id}_selection.json')
    if receipt:
        pack['knowledge_selection_id'] = receipt.get('selection_id')
        pack['knowledge_context_sha256'] = receipt.get('context_sha256')
        pack['knowledge_selected_ids'] = [str(i.get('id')) for i in receipt.get('selected') or []]
    write_json(out / 'pack.json', pack)
    return out / 'pack.json'


SHELF_FILES = ('prompt.txt', 'settings.json', 'refs.json', 'pack.json')


def lock_shelf(project: Path, block_id: str) -> dict:
    out = shelf_dir(project, block_id)
    if not (out / 'brief.md').is_file():
        raise ValueError('SHELF_BRIEF_MISSING: run shelf-brief first')
    errors = validate_shelf_prompt(project, block_id)
    if errors:
        raise ValueError('SHELF_PROMPT_INVALID: ' + '; '.join(errors))
    import claude_author
    authorship = claude_author.lock_authorship_errors(project, 'shelf', block_id)
    if authorship:
        raise ValueError('CLAUDE_MODE_AUTHORSHIP: ' + '; '.join(authorship))
    pack = build_pack(project, block_id)
    result = prompt_packet_utils.attest(pack, project)
    if result['verdict'] != 'ATTESTED':
        raise ValueError('SHELF_NOT_ATTESTED: ' + '; '.join(result['errors']))
    previous = read_json(out / 'SHELF_LOCK.json')
    lock = {
        'schema': SCHEMA, 'stage': 'shelf', 'block_id': block_id,
        'revision': int((previous or {}).get('revision') or 0) + 1,
        'files': {name: sha(out / name) for name in SHELF_FILES},
        'refs': {r['token']: r['sha256'] for r in (read_json(out / 'refs.json') or {})['references']},
        'storyboard_sha256': (read_json(lock_path(project, 'storyboard')) or {}).get('sha256'),
        'images_sha256': (read_json(lock_path(project, 'images')) or {}).get('sha256'),
        'attestation': result['attestation'], 'prompt_chars': len(nfc((out / 'prompt.txt').read_text(encoding='utf-8'))),
        'released': None, 'locked_at': now(),
    }
    if previous:
        dest = root(project) / '_superseded' / f'shelf_{block_id}_R{previous.get("revision", 0)}'
        dest.mkdir(parents=True, exist_ok=True)
        write_json(dest / 'SHELF_LOCK.json', previous)
    write_json(out / 'SHELF_LOCK.json', lock)
    return lock


def verify_shelf(project: Path, block_id: str, *, require_release: bool = True) -> list[str]:
    """Production preflight: every byte the operator will paste or attach is the locked one."""
    out = shelf_dir(project, block_id)
    lock = read_json(out / 'SHELF_LOCK.json')
    if not lock:
        return ['shelf_not_locked']
    e: list[str] = []
    for name, digest in (lock.get('files') or {}).items():
        path = out / name
        _need(e, path.is_file() and sha(path) == digest, f'shelf_file_changed:{name}')
    for row in (read_json(out / 'refs.json') or {}).get('references') or []:
        path = Path(row['path'])
        _need(e, path.is_file() and sha(path) == row['sha256'], f'shelf_ref_missing_or_changed:{row["token"]}')
    _need(e, lock.get('storyboard_sha256') == (read_json(lock_path(project, 'storyboard')) or {}).get('sha256'),
          'shelf_storyboard_relocked_since_shelf_lock')
    _need(e, lock_state(project, 'storyboard')['state'] == 'LOCKED', 'shelf_storyboard_not_locked')
    if require_release:
        _need(e, bool(lock.get('released')), 'shelf_not_released_by_user')
    return e


def release_shelf(project: Path, blocks: list[str], quote: str) -> list[str]:
    if not quote.strip():
        raise ValueError('USER_APPROVAL_REQUIRED: release the shelf only with --approval-quote')
    done = []
    for block_id in blocks:
        errors = verify_shelf(project, block_id, require_release=False)
        if errors:
            raise ValueError(f'SHELF_NOT_RELEASABLE {block_id}: ' + '; '.join(errors))
        path = shelf_dir(project, block_id) / 'SHELF_LOCK.json'
        lock = read_json(path)
        lock['released'] = _approval(quote, 'user')
        write_json(path, lock)
        done.append(block_id)
    return done


def shelf_rows(project: Path) -> list[dict]:
    rows = []
    for block in storyboard(project).get('blocks') or []:
        bid = block['block_id']
        out = shelf_dir(project, bid)
        lock = read_json(out / 'SHELF_LOCK.json')
        if not out.is_dir():
            state = 'NOT_STARTED'
        elif not lock:
            state = 'AUTHORING'
        else:
            errors = verify_shelf(project, bid, require_release=False)
            state = 'STALE' if errors else ('RELEASED' if lock.get('released') else 'LOCKED')
        rows.append({'block_id': bid, 'order': block['order'], 'state': state,
                     'prompt_chars': (lock or {}).get('prompt_chars')})
    return rows


def released_blocks(project: Path) -> list[str]:
    return [r['block_id'] for r in shelf_rows(project) if r['state'] == 'RELEASED']


def status(project: Path) -> dict:
    stages = [lock_state(project, s) for s in VALIDATORS]
    for item in stages:
        item.pop('lock', None)
    nxt = next((s['stage'] for s in stages if s['state'] != 'LOCKED'), 'shelf')
    shelf = shelf_rows(project) if nxt == 'shelf' else []
    import claude_author
    return {'project': str(project), 'authoring_mode': claude_author.get_mode(project) or 'UNSET',
            'stages': stages, 'next_stage': nxt, 'shelf': shelf}


# --- scaffold --------------------------------------------------------------------

def init(project: Path) -> Path:
    base = root(project)
    for name in ('00_concept', '01_bible', '02_storyboard', '03_image_prompts', '04_shelf', 'locks', '_superseded'):
        (base / name).mkdir(parents=True, exist_ok=True)
    (base / 'PREPROD_V1').write_text(now() + '\n', encoding='utf-8')
    templates = Path(__file__).resolve().parents[1] / 'templates' / 'preprod'
    for src in templates.glob('*'):
        target = {'concept_options.md': '00_concept', 'concept_lock.json': '00_concept',
                  'style_bible.json': '01_bible', 'storyboard.json': '02_storyboard',
                  'image_plan.json': '03_image_prompts'}.get(src.name)
        if target and not (base / target / src.name).exists():
            shutil.copy2(src, base / target / src.name)
    return base


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest='cmd', required=True)
    for name in ('init', 'status'):
        sub.add_parser(name).add_argument('--project', required=True)
    p = sub.add_parser('check'); p.add_argument('--project', required=True); p.add_argument('--stage', required=True, choices=list(VALIDATORS))
    p = sub.add_parser('lock'); p.add_argument('--project', required=True)
    p.add_argument('--stage', required=True, choices=list(VALIDATORS)); p.add_argument('--approval-quote', default='')
    for name in ('shelf-brief', 'shelf-check', 'shelf-lock', 'shelf-verify'):
        p = sub.add_parser(name); p.add_argument('--project', required=True); p.add_argument('--block', required=True)
    p = sub.add_parser('shelf-release'); p.add_argument('--project', required=True)
    p.add_argument('--blocks', required=True, help='comma list or ALL_LOCKED'); p.add_argument('--approval-quote', required=True)
    args = parser.parse_args()
    project = Path(args.project).expanduser().resolve()
    try:
        if args.cmd == 'init':
            out = {'ok': True, 'preprod': str(init(project))}
        elif args.cmd == 'status':
            out = {'ok': True, **status(project)}
        elif args.cmd == 'check':
            errors = VALIDATORS[args.stage](project)
            out = {'ok': not errors, 'stage': args.stage, 'errors': errors}
        elif args.cmd == 'lock':
            out = {'ok': True, 'lock': lock_stage(project, args.stage, args.approval_quote)}
        elif args.cmd == 'shelf-brief':
            out = {'ok': True, 'brief': str(write_shelf_brief(project, args.block))}
        elif args.cmd == 'shelf-check':
            errors = validate_shelf_prompt(project, args.block)
            out = {'ok': not errors, 'errors': errors}
        elif args.cmd == 'shelf-lock':
            out = {'ok': True, 'lock': lock_shelf(project, args.block)}
        elif args.cmd == 'shelf-verify':
            errors = verify_shelf(project, args.block)
            out = {'ok': not errors, 'errors': errors, 'shelf': str(shelf_dir(project, args.block))}
        else:
            blocks = ([r['block_id'] for r in shelf_rows(project) if r['state'] == 'LOCKED']
                      if args.blocks == 'ALL_LOCKED' else [b for b in args.blocks.split(',') if b])
            out = {'ok': True, 'released': release_shelf(project, blocks, args.approval_quote)}
    except (ValueError, KeyError) as exc:
        out = {'ok': False, 'error': str(exc)}
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if out.get('ok') else 1


if __name__ == '__main__':
    raise SystemExit(main())
