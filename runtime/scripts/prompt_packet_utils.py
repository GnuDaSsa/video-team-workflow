#!/usr/bin/env python3
"""Validate and attest lane-authored Seedance prompt packages.

Runtime v4 has no dedicated prompt-authoring agent or model bridge. The
Seedance lane writes the Korean prompt and this module enforces the handoff
contract before visible Runway operation.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import unicodedata

import generation_settings
import seedance_prompt_case_harness
import shot_semantics


SEEDANCE_PROMPT_CHAR_LIMIT = 3500
SEEDANCE_PROMPT_STYLE_VERSION = 'creative_seedance_ko_v4_20260731'
SEEDANCE_AUTHORING_CONTRACT = 'seedance_lane_owned_ko'
PROMPT_LANGUAGE = 'ko-KR'
MULTIMODAL_BINDING_RULE = 'model_facing_multimodal_binding_v1'
SINGLE_SHOT_GRAMMAR = 'SINGLE_CONTINUOUS_SHOT'
MULTI_SHOT_GRAMMAR = 'PLANNED_MULTI_SHOT_SOURCE'
SHOT_GRAMMARS = {SINGLE_SHOT_GRAMMAR, MULTI_SHOT_GRAMMAR}

SEEDANCE_LEGACY_OVERLOCK_PATTERNS = [
    'locked new Gongnyang midclean source frame', 'Gongnyang', '공냥',
    'source frame', 'generated image', 'imagegen', 'prompt pack', 'provenance',
    'Preserve crop, composition', 'dignified slow push', 'tiny parallax',
    'settle into a stable edit-ready hold',
]

LEAK_PATTERN = re.compile(
    r'(/Users/|\.md\b|docs/|lanes/|Status:\s*(DONE|BLOCKED|RUNNING)|Key V\d+ docs|# Director Result'
    r'|\bScene ID\s*:|\bLook medium\s*:|\bMode\s*:\s*(Creative|Standard)\b|\bREFERENCE ROLES\s*:'
    r'|\bEXPECTED\s*:|\bEXIT\s*:|\bPrompt file\s*:|\bSource root\b|\bOrdered references\s*:'
    r'|\b[A-Z-]*GATE\s*:|\bvisibly verified\b|\bvisibly attached\b|\bmust be visibly\b'
    r'|\bcharacter[- ]sheet gate\b|\bscene[- ]reference gate\b'
    r'|\bin UI\b|\bAudio (ON|OFF)\b|\b\d+s full Seedance\b|\bSeedance generation\b'
    r'|\bgenerated styleframe\b|\bstyleframe for\b|\bapproved production sheet\b|\bCHAR_[A-Z0-9_]+)',
    re.IGNORECASE,
)

DURATION_DECLARATION_PATTERNS = (
    re.compile(r'(?<![\d.])(\d{1,2})\s*초\s*(?:동안\s*)?(?:단일|연속)'),
    re.compile(r'(?<![\d.])(\d{1,2})\s*초\s*동안'),
    re.compile(r'(?<![\d.])(\d{1,2})\s*초\s*\d+\s*숏'),
    re.compile(r'(?<![\d.])(\d{1,2})\s*(?:second|seconds|s)\s+(?:single|continuous)', re.I),
)


def normalize_prompt(text: str) -> str:
    text = unicodedata.normalize('NFC', text).replace('\r\n', '\n').replace('\r', '\n')
    lines = [line.rstrip() for line in text.strip().split('\n')]
    return '\n'.join(lines)


def prompt_sha256(text: str) -> str:
    return hashlib.sha256(normalize_prompt(text).encode('utf-8')).hexdigest()


def language_stats(text: str) -> dict:
    normalized = normalize_prompt(text)
    hangul = len(re.findall(r'[가-힣]', normalized))
    latin = len(re.findall(r'[A-Za-z]', normalized))
    letters = hangul + latin
    ratio = hangul / letters if letters else 0.0
    return {
        'chars': len(normalized),
        'hangul_chars': hangul,
        'latin_chars': latin,
        'hangul_letter_ratio': round(ratio, 4),
        'korean_dominant': hangul >= 30 and ratio >= 0.55,
    }


def _reference_role_entries(value: object) -> list[tuple[str, str]]:
    """Return canonical @ImageN/@VideoN/@AudioN tokens and declared roles."""
    raw: list[tuple[object, object]] = []
    if isinstance(value, dict):
        raw.extend(value.items())
    elif isinstance(value, list):
        for item in value:
            if not isinstance(item, dict):
                raw.append(('', ''))
                continue
            raw.append((item.get('reference') or item.get('token') or '', item.get('role') or ''))

    entries: list[tuple[str, str]] = []
    for token_value, role_value in raw:
        token = str(token_value or '').strip()
        if token and not token.startswith('@'):
            token = '@' + token
        entries.append((token, str(role_value or '').strip()))
    return entries


def _canonical_reference_token(value: object) -> str:
    token = str(value or '').strip()
    return token if token.startswith('@') else '@' + token


def validate_shot_grammar(pack: dict, binding_entries: list[tuple[str, str]]) -> list[str]:
    """Validate 15-second single-source yield design independently of UI settings."""
    errors: list[str] = []
    grammar = pack.get('shot_grammar')
    if not grammar:
        return errors
    if grammar not in SHOT_GRAMMARS:
        return [f'wrong_shot_grammar:{grammar}']
    if grammar == SINGLE_SHOT_GRAMMAR:
        count = pack.get('planned_scene_count')
        if count not in (None, 1):
            errors.append(f'single_shot_scene_count_must_be_1:{count}')
        return errors

    duration = pack.get('duration_sec')
    if duration != 15:
        errors.append(f'multi_shot_source_requires_15s:{duration}')
    count = pack.get('planned_scene_count')
    if not isinstance(count, int) or not 2 <= count <= 4:
        errors.append(f'multi_shot_scene_count_must_be_2_to_4:{count}')
        return errors
    scenes = pack.get('scene_plan')
    if not isinstance(scenes, list) or len(scenes) != count:
        errors.append(
            f'multi_shot_scene_plan_count_mismatch:expected={count},actual='
            f'{len(scenes) if isinstance(scenes, list) else "not_list"}')
        return errors

    known_tokens = {token.casefold() for token, _role in binding_entries}
    flattened_cuts: list[str] = []
    previous_end = 0.0
    for index, scene in enumerate(scenes, 1):
        if not isinstance(scene, dict):
            errors.append(f'multi_shot_scene_not_object:{index}')
            continue
        for key in ('scene_id', 'start_sec', 'end_sec', 'covered_cuts',
                    'reference_tokens', 'action', 'camera', 'edit_out'):
            if scene.get(key) in (None, '', []):
                errors.append(f'multi_shot_scene_{index}_missing:{key}')
        try:
            start = float(scene.get('start_sec'))
            end = float(scene.get('end_sec'))
        except (TypeError, ValueError):
            errors.append(f'multi_shot_scene_{index}_invalid_time')
        else:
            if abs(start - previous_end) > 0.05:
                errors.append(
                    f'multi_shot_scene_{index}_timeline_gap_or_overlap:'
                    f'expected_start={previous_end},actual={start}')
            if end <= start or end - start < 2.0:
                errors.append(f'multi_shot_scene_{index}_under_2s_or_reversed:{start}-{end}')
            previous_end = end
        cuts = scene.get('covered_cuts')
        if isinstance(cuts, list):
            flattened_cuts.extend(str(cut) for cut in cuts)
        tokens = scene.get('reference_tokens')
        if isinstance(tokens, list):
            for value in tokens:
                token = _canonical_reference_token(value)
                if token.casefold() not in known_tokens:
                    errors.append(
                        f'multi_shot_scene_{index}_unknown_reference_token:{token}')
    if abs(previous_end - float(duration or 0)) > 0.05:
        errors.append(
            f'multi_shot_timeline_does_not_fill_duration:end={previous_end},duration={duration}')
    if len(flattened_cuts) != len(set(flattened_cuts)):
        errors.append('multi_shot_duplicate_cut_ownership')
    pack_cuts = [str(cut) for cut in (pack.get('covered_cuts') or [])]
    if not pack_cuts:
        errors.append('multi_shot_pack_covered_cuts_missing')
    elif pack_cuts != flattened_cuts:
        errors.append(
            f'multi_shot_covered_cuts_mismatch:pack={pack_cuts},scenes={flattened_cuts}')
    return errors


def validate_seedance(pack: dict) -> list[str]:
    errors: list[str] = []
    required = (
        'block_id', 'prompt_language', 'prompt', 'reference_role_map',
        'duration_sec', 'shot_grammar', 'audio_route', 'prompt_rules_used', 'prompt_style_version',
        'authoring_contract',
    )
    for key in required:
        if not pack.get(key):
            errors.append(f'missing:{key}')
    if pack.get('prompt_language') != PROMPT_LANGUAGE:
        errors.append(f'wrong_prompt_language:{pack.get("prompt_language")}')
    if pack.get('prompt_style_version') != SEEDANCE_PROMPT_STYLE_VERSION:
        errors.append(f'wrong_prompt_style_version:{pack.get("prompt_style_version")}')
    if pack.get('authoring_contract') != SEEDANCE_AUTHORING_CONTRACT:
        errors.append(f'wrong_authoring_contract:{pack.get("authoring_contract")}')

    rules = ' '.join(str(value) for value in (pack.get('prompt_rules_used') or []))
    if 'anchor' not in rules.lower():
        errors.append('missing_anchor_not_cage_rule')

    binding_required = MULTIMODAL_BINDING_RULE.lower() in rules.lower()
    binding_entries = _reference_role_entries(pack.get('reference_role_map'))
    errors.extend(validate_shot_grammar(pack, binding_entries))
    if binding_required:
        if not binding_entries:
            errors.append('reference_role_map_empty_for_multimodal_binding')
        for token, role in binding_entries:
            if not re.fullmatch(r'@(Image|Video|Audio)\d+', token, re.IGNORECASE):
                errors.append(f'invalid_reference_token:{token or "<empty>"}')
            if not role:
                errors.append(f'missing_reference_role:{token or "<empty>"}')

    for field in ('prompt', 'prompt_s2'):
        prompt = normalize_prompt(str(pack.get(field) or ''))
        if not prompt:
            if field == 'prompt':
                errors.append('prompt_empty')
            continue
        if binding_required:
            prompt_folded = prompt.casefold()
            for token, _role in binding_entries:
                if re.fullmatch(r'@(Image|Video|Audio)\d+', token, re.IGNORECASE) and token.casefold() not in prompt_folded:
                    errors.append(f'{field}_missing_model_facing_binding:{token}')
        if pack.get('shot_grammar') == MULTI_SHOT_GRAMMAR:
            count = pack.get('planned_scene_count')
            duration = pack.get('duration_sec')
            if isinstance(count, int):
                if not re.search(rf'(?<![\d.]){duration}\s*초\s*{count}\s*숏', prompt):
                    errors.append(
                        f'{field}_missing_multi_shot_duration_count_declaration:'
                        f'{duration}s/{count}shots')
                for index in range(1, count + 1):
                    if not re.search(rf'숏\s*{index}(?!\d)', prompt):
                        errors.append(f'{field}_missing_shot_marker:{index}')
        declared_durations = {
            int(match.group(1))
            for pattern in DURATION_DECLARATION_PATTERNS
            for match in pattern.finditer(prompt)
        }
        pack_duration = pack.get('duration_sec')
        if declared_durations and declared_durations != {pack_duration}:
            errors.append(
                f'{field}_duration_declaration_mismatch:'
                f'pack={pack_duration},declared={sorted(declared_durations)}')
        if len(prompt) > SEEDANCE_PROMPT_CHAR_LIMIT:
            errors.append(f'{field}_over_{SEEDANCE_PROMPT_CHAR_LIMIT}')
        stats = language_stats(prompt)
        if not stats['korean_dominant']:
            errors.append(
                f'{field}_not_korean_dominant:'
                f'hangul={stats["hangul_chars"]},latin={stats["latin_chars"]},ratio={stats["hangul_letter_ratio"]}'
            )
        match = LEAK_PATTERN.search(prompt)
        if match:
            errors.append(f'{field}_contains_operational_leak:"{match.group(0)}"')
        legacy_hits = [pattern for pattern in SEEDANCE_LEGACY_OVERLOCK_PATTERNS if pattern.lower() in prompt.lower()]
        if legacy_hits:
            errors.append(f'{field}_legacy_overlock:' + ','.join(legacy_hits))
        if prompt.lower().count('preserve crop') + prompt.lower().count('preserve exact crop') > 2:
            errors.append(f'{field}_overused_crop_lock')
        if prompt.lower().count('slow push') > 1:
            errors.append(f'{field}_repeated_slow_push')
    errors.extend(seedance_prompt_case_harness.validate_case_contract(pack))
    errors.extend(shot_semantics.validate(pack))
    return errors


def load_pack(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f'invalid prompt pack: {path}: {exc}') from exc
    if not isinstance(value, dict):
        raise ValueError('Seedance prompt pack must be one JSON object')
    return value


def _inside(root: Path, path: Path) -> bool:
    try:
        return os.path.commonpath((str(root), str(path))) == str(root)
    except ValueError:
        return False


def validate_knowledge_selection(pack: dict, project: Path) -> tuple[list[str], dict]:
    """Verify the block's bounded wiki-selection receipt when v4 requires it."""
    project = project.expanduser().resolve()
    errors: list[str] = []
    try:
        manifest = json.loads((project / 'manifest.json').read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return ['knowledge_manifest_unreadable'], {}
    config = manifest.get('knowledge_routing') or {}
    if not config.get('enabled') or not config.get('required_before_prompt_attestation'):
        return [], {}

    block = str(pack.get('block_id') or '')
    required = ('knowledge_selection_id', 'knowledge_context_sha256', 'knowledge_selected_ids')
    for key in required:
        if not pack.get(key):
            errors.append(f'missing:{key}')
    receipt_path = project / 'lanes' / 'seedance' / 'knowledge' / f'{block}_selection.json'
    try:
        receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return errors + [f'knowledge_receipt_unreadable:{receipt_path}'], {}

    if receipt.get('block_id') != block:
        errors.append('knowledge_receipt_block_mismatch')
    if receipt.get('selection_id') != pack.get('knowledge_selection_id'):
        errors.append('knowledge_selection_id_mismatch')
    if receipt.get('context_sha256') != pack.get('knowledge_context_sha256'):
        errors.append('knowledge_context_hash_mismatch')
    selected_ids = [str(item.get('id')) for item in (receipt.get('selected') or [])]
    if selected_ids != [str(value) for value in (pack.get('knowledge_selected_ids') or [])]:
        errors.append('knowledge_selected_ids_mismatch')

    expected_context_path = (
        project / 'lanes' / 'seedance' / 'knowledge' / f'{block}_context.md').resolve()
    context_path = Path(str(receipt.get('context') or '')).expanduser().resolve()
    if context_path != expected_context_path:
        errors.append('knowledge_context_path_mismatch')
    try:
        context_hash = hashlib.sha256(context_path.read_bytes()).hexdigest()
    except OSError:
        errors.append(f'knowledge_context_unreadable:{context_path}')
    else:
        if context_hash != receipt.get('context_sha256'):
            errors.append('knowledge_context_file_hash_mismatch')

    catalog_path = Path(str(receipt.get('catalog') or '')).expanduser().resolve()
    expected_catalog = Path(str(config.get('catalog') or '')).expanduser().resolve()
    if catalog_path != expected_catalog:
        errors.append('knowledge_catalog_path_mismatch')
    try:
        catalog_hash = hashlib.sha256(catalog_path.read_bytes()).hexdigest()
    except OSError:
        errors.append(f'knowledge_catalog_unreadable:{catalog_path}')
    else:
        if catalog_hash != receipt.get('catalog_sha256'):
            errors.append('knowledge_catalog_changed_rerun_selection')

    wiki_root = catalog_path.parent.parent.resolve()
    for item in receipt.get('selected') or []:
        source = Path(str(item.get('path') or '')).expanduser().resolve()
        if not _inside(wiki_root, source):
            errors.append(f'knowledge_source_outside_wiki:{item.get("id")}')
            continue
        try:
            source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
        except OSError:
            errors.append(f'knowledge_source_unreadable:{source}')
            continue
        if source_hash != item.get('source_sha256'):
            errors.append(f'knowledge_source_changed_rerun_selection:{item.get("id")}')

    expected_attributes = (
        project / 'lanes' / 'planner' / 'video_attributes.json').resolve()
    attributes_source = Path(
        str(receipt.get('attributes_source') or '')).expanduser().resolve()
    if attributes_source != expected_attributes:
        errors.append('knowledge_attributes_path_mismatch')
    try:
        attributes_source_hash = hashlib.sha256(attributes_source.read_bytes()).hexdigest()
    except OSError:
        errors.append(f'knowledge_attributes_unreadable:{attributes_source}')
    else:
        if attributes_source_hash != receipt.get('attributes_source_sha256'):
            errors.append('knowledge_attributes_changed_rerun_selection')

    context_chars = int(receipt.get('context_chars') or 0)
    budget_chars = int(receipt.get('budget_chars') or 0)
    if context_chars > budget_chars:
        errors.append('knowledge_context_over_budget')
    if budget_chars > int(config.get('budget_chars') or 0):
        errors.append('knowledge_budget_exceeds_manifest')
    if len(selected_ids) > int(config.get('max_selections') or 0):
        errors.append('knowledge_selection_count_exceeds_manifest')
    if not selected_ids:
        errors.append('knowledge_selection_empty')
    return errors, {
        'selection_id': receipt.get('selection_id'),
        'receipt': str(receipt_path),
        'context': str(context_path),
        'context_sha256': receipt.get('context_sha256'),
        'selected_ids': selected_ids,
        'context_chars': context_chars,
        'budget_chars': budget_chars,
    }


def attest(pack_path: Path, project: Path | None = None) -> dict:
    pack_path = pack_path.expanduser().resolve()
    pack = load_pack(pack_path)
    errors = validate_seedance(pack)
    knowledge = {}
    duration_lock = {}
    if project is None:
        errors.append('project_required_for_duration_lock')
    else:
        project = project.expanduser().resolve()
        duration_errors, duration_lock = generation_settings.validate_pack_duration(
            pack, project)
        errors.extend(duration_errors)
        if generation_settings.project_layout(project) == 'runtime_v4':
            knowledge_errors, knowledge = validate_knowledge_selection(pack, project)
            errors.extend(knowledge_errors)
    prompt = normalize_prompt(str(pack.get('prompt') or ''))
    prompt_s2 = normalize_prompt(str(pack.get('prompt_s2') or ''))
    result = {
        'block_id': pack.get('block_id'),
        'pack': str(pack_path),
        'pack_sha256': hashlib.sha256(pack_path.read_bytes()).hexdigest(),
        'prompt_language': pack.get('prompt_language'),
        'prompt_style_version': pack.get('prompt_style_version'),
        'authoring_contract': pack.get('authoring_contract'),
        'prompt_sha256': prompt_sha256(prompt),
        'prompt_s2_sha256': prompt_sha256(prompt_s2) if prompt_s2 else None,
        'prompt_language_check': language_stats(prompt),
        'prompt_s2_language_check': language_stats(prompt_s2) if prompt_s2 else None,
        'duration_lock': duration_lock,
        'knowledge_selection': knowledge,
        'errors': errors,
        'verified_at': dt.datetime.now().astimezone().isoformat(timespec='seconds'),
        'verdict': 'ATTESTED' if not errors else 'NOT_ATTESTED_DO_NOT_SUBMIT',
    }
    out_dir = generation_settings.seedance_prompt_dir(project) if project else pack_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    block = str(pack.get('block_id') or pack_path.stem)
    out = out_dir / f'{block}_attestation.json'
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    result['attestation'] = str(out)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('validate'); p.add_argument('--pack', required=True)
    p = sub.add_parser('attest'); p.add_argument('--pack', required=True); p.add_argument('--project')
    args = parser.parse_args()
    pack_path = Path(args.pack)
    if args.cmd == 'validate':
        pack = load_pack(pack_path)
        errors = validate_seedance(pack)
        print(json.dumps({'pack': str(pack_path), 'ok': not errors, 'errors': errors}, ensure_ascii=False, indent=2))
        return 0 if not errors else 1
    project = Path(args.project).expanduser().resolve() if args.project else None
    result = attest(pack_path, project)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['verdict'] == 'ATTESTED' else 1


if __name__ == '__main__':
    raise SystemExit(main())
