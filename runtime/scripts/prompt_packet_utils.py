#!/usr/bin/env python3
"""Shared packet assembly and validation for the active Codex image/Seedance route."""
from __future__ import annotations

import json
import re
from pathlib import Path

RUNTIME = Path('/Users/gnudas/Documents/Codex/video-team-runtime/runtime')
RULEBOOK = RUNTIME / 'references' / 'seedance_prompting_rulebook.md'
MAX_PACKET_CHARS = 32000
SEEDANCE_PROMPT_CHAR_LIMIT = 3500
IMAGE_PROMPT_CHAR_LIMIT = 2600
SEEDANCE_CREATIVE_PROMPT_STYLE_VERSION = 'creative_seedance_sol_high_20260728'
SEEDANCE_LEGACY_OVERLOCK_PATTERNS = [
    'locked new Gongnyang midclean source frame', 'Gongnyang', '공냥',
    'source frame', 'generated image', 'imagegen', 'prompt pack', 'provenance',
    'Preserve crop, composition', 'dignified slow push', 'tiny parallax',
    'settle into a stable edit-ready hold',
]
TIER1_KEYS = {
    'closeup': ['close-up', 'identity', 'face', 'eye'],
    'kinetic': ['run', 'kinetic', 'chase', 'sprint', 'stairs'],
    'memory': ['memory', 'interior', 'room', 'classroom'],
    'object': ['prop', 'motif', 'macro', 'object'],
    'transition': ['abstract', 'transition', 'morph', 'streak'],
    'montage': ['montage', 'multi-shot', 'beats'],
    'pov': ['pov', 'first person'],
    'final': ['final', 'hold', 'fade', 'closure'],
    'sheet': ['character sheet', 'model sheet', 'reveal'],
    'ad': ['ad', 'product', 'commercial', 'hero shot'],
    'anime': ['anime', '2d', 'cel'],
}
LEAK_PATTERN = re.compile(r'(/Users/|\.md\b|docs/|lanes/|Status:\s*(DONE|BLOCKED|RUNNING)|Key V\d+ docs|# Director Result)', re.IGNORECASE)


def read(path: Path, limit: int = 6000) -> str:
    try:
        return path.read_text(encoding='utf-8', errors='ignore')[:limit]
    except Exception:
        return ''


def load_json(path: Path, default=None):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return default


def read_queue(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding='utf-8', errors='ignore').splitlines():
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return rows


def rulebook_sections(block_text: str, dialogue: bool) -> str:
    full = read(RULEBOOK, 60000)
    if not full:
        return 'RULEBOOK MISSING — apply seedance-prompt-en skill rules.'
    parts = re.split(r'\n(?=## )', full)
    tier0 = next((p for p in parts if p.startswith('## TIER 0')), '')
    tier1 = next((p for p in parts if p.startswith('## TIER 1')), '')
    tier2 = next((p for p in parts if p.startswith('## TIER 2')), '')
    low = block_text.lower()
    hits = [k for k, kws in TIER1_KEYS.items() if any(w in low for w in kws)]
    selected = []
    if tier1:
        for para in tier1.split('\n\n'):
            if any(k in para.lower() for k in hits) or para.startswith('## '):
                selected.append(para)
    out = [tier0, '\n\n'.join(selected)]
    if dialogue:
        out.append(tier2)
    return '\n\n'.join(x for x in out if x)


def identity_lock(project: Path) -> tuple[str, bool]:
    for candidate in (
        project / 'production' / 'visual' / 'character_identity_lock.md',
        project / 'docs' / 'identity_lock.md',
        project / 'lanes' / 'director' / 'identity_lock.md',
    ):
        if candidate.exists():
            return read(candidate, 3000), True
    return read(project / 'lanes' / 'director' / 'result.md', 3000), False


def block_spec(project: Path, block: str) -> tuple[str, dict]:
    block_map = load_json(project / 'lanes' / 'planner' / 'multi_reference_block_map.json', {}) or {}
    for entry in block_map.get('blocks', []) or []:
        if entry.get('block_id') == block:
            return json.dumps(entry, ensure_ascii=False, indent=2), entry
    for candidate in (
        project / 'lanes' / 'seedance' / 'prompts' / f'{block}_block_spec.json',
        project / 'lanes' / 'planner' / 'block_specs' / f'{block}.json',
    ):
        spec = load_json(candidate)
        if spec:
            return json.dumps(spec, ensure_ascii=False, indent=2), spec
    manifest = load_json(project / 'manifest.json', {}) or {}
    for entry in manifest.get('blocks') or []:
        if isinstance(entry, dict) and entry.get('block_id') == block:
            return json.dumps(entry, ensure_ascii=False, indent=2), entry
    return '', {}


def spec_completeness_error(spec: dict) -> str:
    if not isinstance(spec, dict):
        return 'spec is not a JSON object'
    missing = []
    for key in ('duration_s', 'aspect', 'story_beat'):
        if not spec.get(key):
            missing.append(key)
    refs = spec.get('references')
    if not isinstance(refs, list) or not refs:
        missing.append('references[]')
    elif not all(isinstance(ref, dict) and (ref.get('role') or ref.get('covered_cut')) for ref in refs):
        missing.append('references[].role/covered_cut')
    return 'missing required structured fields: ' + ', '.join(missing) + '.' if missing else ''


def neighbor_prompts(project: Path, block: str) -> str:
    prompt_dir = project / 'lanes' / 'seedance' / 'prompts'
    if not prompt_dir.exists():
        return ''
    packs = sorted(prompt_dir.glob('*_sol_prompt_pack.json'))
    keep = [path for path in packs if not path.name.startswith(f'{block}_')][-2:]
    chunks = []
    for path in keep:
        data = load_json(path, {}) or {}
        chunks.append(f"[{data.get('block_id')}]\n{data.get('prompt', '')[:1800]}")
    return '\n\n'.join(chunks)


def fail_history(project: Path, block: str) -> str:
    rows = []
    for name in ('seedance_retry_queue', 'image_retry_queue', 'retry_router_queue'):
        for row in read_queue(project / 'queues' / f'{name}.jsonl'):
            if block and block in json.dumps(row, ensure_ascii=False):
                rows.append(row)
    return '\n'.join(json.dumps(row, ensure_ascii=False)[:500] for row in rows[-6:])


SEEDANCE_SCHEMA = '''{
  "block_id": "...", "method": "...", "duration_s": 0, "aspect": "...",
  "prompt_style_version": "creative_seedance_sol_high_20260728",
  "authoring_contract": "video_prompt_director_high",
  "reference_role_map": {"@Image1": "anchor role; essential lock; creative latitude"}, "shot_count": 0,
  "motion_budget": ["..."],
  "audio_route": "NO_AUDIO1_SFX_ONLY | AUDIO1_GUIDE | NATIVE_CANDIDATE_S1_S2",
  "prompt": "700-1400 chars preferred, <=3500 Runway hard limit; references are anchors, not cages; cinematic reframing allowed except fragile details",
  "prompt_s2": "only when NATIVE_CANDIDATE_S1_S2, else omit",
  "constraints_tail": "short essential safety tail only", "prompt_rules_used": ["creative_seedance_sol_high_20260728", "anchor_not_cage"],
  "retry_if_failed": "..."
}'''
IMAGE_SCHEMA = '''[{
  "reference_id": "...", "role": "identity | environment | prop | action",
  "prompt": "identity lock; MUST end with: No text, no logo, no watermark.",
  "palette_anchors": ["..."], "avoid": ["..."]
}]'''


def build_packet(project: Path, task: str, block: str, refs: list[str]) -> str:
    spec_text, spec = block_spec(project, block)
    if not spec_text:
        raise SystemExit(f'BLOCKED_MISSING_BLOCK_SPEC: no structured block spec for {block}')
    spec_error = spec_completeness_error(spec)
    if spec_error:
        raise SystemExit(f'BLOCKED_INCOMPLETE_BLOCK_SPEC: {block}: {spec_error}')
    dialogue = any(word in spec_text.lower() for word in ('dialogue', 'voice', 'speech', 'audio1', '대사'))
    schema = SEEDANCE_SCHEMA if task == 'seedance' else IMAGE_SCHEMA
    deliverable = ('Seedance multi-reference block prompt' if task == 'seedance'
                   else f'image prompts for references: {", ".join(refs) or "per BLOCK SPEC reference_order"}')
    identity_text, identity_locked = identity_lock(project)
    identity_header = ('IDENTITY LOCK (reuse this text verbatim in every prompt, do not paraphrase)'
                       if identity_locked else
                       'IDENTITY CONTEXT (distill a clean character/style identity line; never copy operational text)')
    prompt_limit = SEEDANCE_PROMPT_CHAR_LIMIT if task == 'seedance' else IMAGE_PROMPT_CHAR_LIMIT
    task_rules = (
        f'{deliverable}. block_id={block}. Runway hard limit: {prompt_limit}; recommended target 700-1500. '
        'The generation prompt is for the video/image model only: no file paths, statuses, or project-management text. '
    )
    if task == 'seedance':
        task_rules += ('Author as video_prompt_director_high at reasoning effort high; use the creative Seedance style version; '
                       'references are visible story anchors, not production artifacts; allow cinematic reframing/camera/blocking/transitions '
                       'except fragile symbol/face/hand/crop locks.')
    sections = [
        ('TASK', task_rules),
        (identity_header, identity_text),
        ('PROJECT DIRECTION', read(project / 'brief.md', 2500)),
        ('MUSIC LOCK', read(project / 'lanes' / 'music' / 'result.md', 2500)),
        ('BLOCK SPEC', spec_text),
        ('APPROVED NEIGHBOR PROMPTS', neighbor_prompts(project, block)),
        ('QC FAIL HISTORY', fail_history(project, block)),
        ('RULES', rulebook_sections(spec_text + ' ' + read(project / 'brief.md', 1500), dialogue)),
        ('OUTPUT CONTRACT', 'Return ONLY one fenced ```json block matching this schema. No prose.\n' + schema),
    ]
    return '\n\n'.join(f'## {heading}\n\n{body}' for heading, body in sections if body is not None)[:MAX_PACKET_CHARS]


def extract_json(text: str):
    match = re.search(r'```json\s*(.+?)```', text, re.DOTALL)
    raw = match.group(1) if match else text
    starts = [idx for idx in (raw.find('{'), raw.find('[')) if idx >= 0]
    if not starts:
        raise ValueError('no JSON found in model output')
    start = min(starts)
    return json.loads(raw[start:raw.rfind('}') + 1] if raw.lstrip().startswith('{') else raw[start:raw.rfind(']') + 1])


def validate_seedance(pack: dict) -> list[str]:
    errors = []
    for key in ('block_id', 'prompt', 'reference_role_map', 'audio_route', 'prompt_rules_used', 'prompt_style_version'):
        if not pack.get(key):
            errors.append(f'missing:{key}')
    if pack.get('prompt_style_version') != SEEDANCE_CREATIVE_PROMPT_STYLE_VERSION:
        errors.append(f'wrong_prompt_style_version:{pack.get("prompt_style_version")}')
    rules = ' '.join(str(x) for x in (pack.get('prompt_rules_used') or []))
    if 'anchor' not in rules.lower() and 'anchor' not in (pack.get('authoring_contract') or '').lower():
        errors.append('missing_anchor_not_cage_rule')
    if (pack.get('authoring_contract') or '') not in {'video_prompt_director_high', 'video_prompt_director_high_anchor_not_cage'}:
        errors.append('missing_video_prompt_director_high_contract')
    prompt = pack.get('prompt', '') or ''
    if len(prompt) > SEEDANCE_PROMPT_CHAR_LIMIT:
        errors.append(f'prompt_over_{SEEDANCE_PROMPT_CHAR_LIMIT}')
    legacy_hits = [pattern for pattern in SEEDANCE_LEGACY_OVERLOCK_PATTERNS if pattern.lower() in prompt.lower()]
    if legacy_hits:
        errors.append('legacy_overlocked_seedance_prompt:' + ','.join(legacy_hits))
    if prompt.lower().count('preserve crop') + prompt.lower().count('preserve exact crop') > 2:
        errors.append('overused_crop_lock_refs_are_cages_not_anchors')
    if prompt.lower().count('slow push') > 1:
        errors.append('repeated_slow_push_template_language')
    for field in ('prompt', 'prompt_s2'):
        match = LEAK_PATTERN.search(pack.get(field) or '')
        if match:
            errors.append(f'{field}_contains_operational_leak:"{match.group(0)}"')
    return errors


def validate_image(pack) -> list[str]:
    errors = []
    if not isinstance(pack, list) or not pack:
        return ['not_a_list']
    for item in pack:
        reference_id = item.get('reference_id', '?')
        prompt = item.get('prompt', '')
        if not prompt:
            errors.append(f'{reference_id}:missing_prompt')
        low = prompt.lower()
        if not all(token in low for token in ('no text', 'no logo', 'no watermark')):
            errors.append(f'{reference_id}:missing_no_text_logo_watermark_policy')
        match = LEAK_PATTERN.search(prompt)
        if match:
            errors.append(f'{reference_id}:prompt_contains_operational_leak:"{match.group(0)}"')
    return errors
