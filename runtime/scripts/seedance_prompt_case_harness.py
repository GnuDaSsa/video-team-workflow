#!/usr/bin/env python3
"""Deterministic semantic checks distilled from user-supplied Seedance cases.

This checker complements, rather than replaces, prompt_packet_utils.py.  The
existing attestation owns Korean-language, duration-lock, reference-deck, and
provider handoff checks.  This module checks optional semantic contracts only
when their rule IDs are declared in ``prompt_rules_used``.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any


USER_REFERENCE_SUPERIOR_RULE = 'user_reference_superior_v1'
REFERENCE_CAST_LEDGER_RULE = 'reference_cast_ledger_v1'
TIMED_PERFORMANCE_RULE = 'timed_performance_map_v1'
ONE_TAKE_AXIS_RULE = 'one_take_axis_lock_v1'
PHYSICAL_EFFECT_RULE = 'physical_effect_causality_v1'
AUDIO_LIPSYNC_RULE = 'audio_lipsync_priority_v1'
EXACT_TEXT_DIALOGUE_RULE = 'exact_text_dialogue_v1'
CONSTRAINT_CONSISTENCY_RULE = 'constraint_consistency_v1'

CANONICAL_REFERENCE_RE = re.compile(r'@(Image|Video|Audio)\d+', re.IGNORECASE)
CANONICAL_REFERENCE_SEARCH_RE = re.compile(r'@(Image|Video|Audio)\d+(?!\d)', re.IGNORECASE)
SPACED_REFERENCE_RE = re.compile(r'@\s*(Image|Video|Audio)\s+\d+(?!\d)', re.IGNORECASE)
PAREN_REFERENCE_RE = re.compile(r'\((Image|Video|Audio)\d+\)', re.IGNORECASE)
MIXED_TEMPLATE_RE = re.compile(r'@?\s*\{\{\s*Mixed\s+\d+\s*\}\}', re.IGNORECASE)
AT_ALIAS_RE = re.compile(r'@[A-Za-z_][A-Za-z0-9_-]*')

SINGLE_SHOT_GRAMMARS = {'SINGLE_CONTINUOUS_SHOT', 'single_take'}
MULTI_SHOT_GRAMMARS = {'PLANNED_MULTI_SHOT_SOURCE', 'multi_shot'}


def _rules(pack: dict[str, Any]) -> set[str]:
    values = pack.get('prompt_rules_used') or []
    if isinstance(values, str):
        values = [values]
    return {str(value).strip() for value in values if str(value).strip()}


def _contract(pack: dict[str, Any]) -> dict[str, Any]:
    value = pack.get('semantic_contract') or {}
    return value if isinstance(value, dict) else {}


def _user_reference_superior(pack: dict[str, Any]) -> bool:
    return USER_REFERENCE_SUPERIOR_RULE in _rules(pack)


def _prompt_text(pack: dict[str, Any]) -> str:
    return '\n'.join(
        str(pack.get(field) or '') for field in ('prompt', 'prompt_s2')
        if pack.get(field)
    )


def _reference_entries(pack: dict[str, Any]) -> list[tuple[str, str]]:
    value = pack.get('reference_role_map') or []
    raw: list[tuple[Any, Any]] = []
    if isinstance(value, dict):
        raw.extend(value.items())
    elif isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                raw.append((
                    item.get('reference') or item.get('token') or '',
                    item.get('role') or '',
                ))
            else:
                raw.append(('', ''))
    return [(str(token).strip(), str(role).strip()) for token, role in raw]


def _canonical_token(value: Any) -> str:
    return str(value or '').strip()


def _validate_reference_token_forms(pack: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    prompt = _prompt_text(pack)
    for token, _role in _reference_entries(pack):
        if not CANONICAL_REFERENCE_RE.fullmatch(token):
            errors.append(f'invalid_reference_token:{token or "<empty>"}')

    for match in SPACED_REFERENCE_RE.finditer(prompt):
        errors.append(f'noncanonical_spaced_reference:{match.group(0)}')
    for match in PAREN_REFERENCE_RE.finditer(prompt):
        errors.append(f'noncanonical_parenthesized_reference:{match.group(0)}')
    for match in MIXED_TEMPLATE_RE.finditer(prompt):
        errors.append(f'unresolved_mixed_template:{match.group(0).strip()}')
    for match in AT_ALIAS_RE.finditer(prompt):
        token = match.group(0)
        if not CANONICAL_REFERENCE_RE.fullmatch(token):
            errors.append(f'unresolved_reference_alias:{token}')
    return errors


def _validate_user_reference_authority(pack: dict[str, Any]) -> list[str]:
    authority = _contract(pack).get('authority')
    if not isinstance(authority, dict):
        return ['semantic_contract.authority_required']
    errors: list[str] = []
    if authority.get('mode') != 'user_reference_superior':
        errors.append('authority.mode_must_be:user_reference_superior')
    if not str(authority.get('source') or '').strip():
        errors.append('authority.source_required')
    overrides = authority.get('overrides')
    if not isinstance(overrides, list) or not overrides:
        errors.append('authority.overrides_required')
    preserved = {
        str(value).strip() for value in (authority.get('mechanical_gates_preserved') or [])
        if str(value).strip()
    }
    required_preserved = {
        'safety', 'provider_capability', 'verified_attachment', 'user_settings'}
    missing = sorted(required_preserved - preserved)
    if missing:
        errors.append('authority.mechanical_gates_missing:' + ','.join(missing))
    return errors


def _validate_reference_cast_ledger(pack: dict[str, Any]) -> list[str]:
    contract = _contract(pack)
    errors: list[str] = []
    known_refs = {token.casefold() for token, _role in _reference_entries(pack)}
    entities = contract.get('entities')
    bindings = contract.get('reference_bindings')
    if not isinstance(entities, list) or not entities:
        return ['semantic_contract.entities_required']
    if not isinstance(bindings, list) or not bindings:
        errors.append('semantic_contract.reference_bindings_required')
        bindings = []

    entity_ids: set[str] = set()
    alias_owner: dict[str, str] = {}
    token_owner: dict[str, str] = {}
    total = 0
    for index, entity in enumerate(entities, 1):
        if not isinstance(entity, dict):
            errors.append(f'entity_{index}_not_object')
            continue
        entity_id = str(entity.get('entity_id') or '').strip()
        if not entity_id:
            errors.append(f'entity_{index}_missing:entity_id')
            continue
        if entity_id in entity_ids:
            errors.append(f'duplicate_entity_id:{entity_id}')
        entity_ids.add(entity_id)
        count = entity.get('count')
        if not isinstance(count, int) or count < 1:
            errors.append(f'entity_{entity_id}_count_must_be_positive_integer:{count}')
        else:
            total += count
        aliases = entity.get('aliases')
        if not isinstance(aliases, list) or not aliases:
            errors.append(f'entity_{entity_id}_aliases_required')
        else:
            for raw_alias in aliases:
                alias = str(raw_alias or '').strip().casefold()
                if not alias:
                    errors.append(f'entity_{entity_id}_empty_alias')
                    continue
                previous = alias_owner.get(alias)
                if previous and previous != entity_id:
                    errors.append(f'conflicting_entity_alias:{raw_alias}:{previous}!={entity_id}')
                alias_owner[alias] = entity_id
        tokens = entity.get('reference_tokens')
        if not isinstance(tokens, list) or not tokens:
            errors.append(f'entity_{entity_id}_reference_tokens_required')
        else:
            for raw_token in tokens:
                token = _canonical_token(raw_token)
                if not CANONICAL_REFERENCE_RE.fullmatch(token):
                    errors.append(f'entity_{entity_id}_invalid_reference_token:{token}')
                    continue
                if token.casefold() not in known_refs:
                    errors.append(f'entity_{entity_id}_unknown_reference_token:{token}')
                previous = token_owner.get(token.casefold())
                if previous and previous != entity_id:
                    errors.append(f'conflicting_reference_entity:{token}:{previous}!={entity_id}')
                token_owner[token.casefold()] = entity_id

    declared_total = contract.get('visible_entity_count_total')
    if not isinstance(declared_total, int) or declared_total < 1:
        errors.append('semantic_contract.visible_entity_count_total_required')
    elif declared_total != total:
        errors.append(f'visible_entity_count_total_mismatch:declared={declared_total},ledger={total}')

    for index, binding in enumerate(bindings, 1):
        if not isinstance(binding, dict):
            errors.append(f'reference_binding_{index}_not_object')
            continue
        token = _canonical_token(binding.get('token'))
        role = str(binding.get('role') or '').strip().casefold()
        use = binding.get('use')
        exclude = binding.get('exclude')
        if not CANONICAL_REFERENCE_RE.fullmatch(token):
            errors.append(f'reference_binding_{index}_invalid_token:{token}')
        elif token.casefold() not in known_refs:
            errors.append(f'reference_binding_{index}_unknown_token:{token}')
        if not role:
            errors.append(f'reference_binding_{index}_missing:role')
        if not isinstance(use, list) or not any(str(item).strip() for item in use):
            errors.append(f'reference_binding_{index}_use_required:{token}')
        if role in {'identity', 'character', 'character_identity'}:
            if not isinstance(exclude, list) or not any(str(item).strip() for item in exclude):
                errors.append(f'identity_binding_exclude_required:{token}')
            entity_id = str(binding.get('entity_id') or '').strip()
            if entity_id not in entity_ids:
                errors.append(f'identity_binding_unknown_entity:{token}:{entity_id or "<empty>"}')
    return errors


def _validate_timed_beats(pack: dict[str, Any]) -> list[str]:
    contract = _contract(pack)
    beats = contract.get('timed_beats')
    if not isinstance(beats, list) or not beats:
        return ['semantic_contract.timed_beats_required']
    errors: list[str] = []
    previous_end = 0.0
    for index, beat in enumerate(beats, 1):
        if not isinstance(beat, dict):
            errors.append(f'timed_beat_{index}_not_object')
            continue
        try:
            start = float(beat.get('start_sec'))
            end = float(beat.get('end_sec'))
        except (TypeError, ValueError):
            errors.append(f'timed_beat_{index}_invalid_time')
            continue
        if abs(start - previous_end) > 0.05:
            errors.append(
                f'timed_beat_{index}_gap_or_overlap:expected={previous_end},actual={start}')
        if end <= start:
            errors.append(f'timed_beat_{index}_reversed_or_empty:{start}-{end}')
        previous_end = end
        for field in ('action', 'camera'):
            if not str(beat.get(field) or '').strip():
                errors.append(f'timed_beat_{index}_missing:{field}')
    try:
        duration = float(pack.get('duration_sec'))
    except (TypeError, ValueError):
        errors.append('duration_sec_required_for_timed_beats')
    else:
        if abs(previous_end - duration) > 0.05:
            errors.append(
                f'timed_beats_do_not_fill_duration:end={previous_end},duration={duration}')
    return errors


def _contains_positive_cut_direction(prompt: str) -> str | None:
    patterns = (
        r'빠른\s*컷(?:\s*전환)?', r'하드\s*컷', r'rapid\s+cuts?',
        r'fast\s+cuts?', r'hard\s+cuts?', r'快速(?:剪辑|切镜)', r'快切',
    )
    for pattern in patterns:
        match = re.search(pattern, prompt, re.IGNORECASE)
        if match:
            return match.group(0)
    return None


def _validate_one_take_axis(pack: dict[str, Any]) -> list[str]:
    contract = _contract(pack)
    continuity = contract.get('continuity')
    if not isinstance(continuity, dict):
        return ['semantic_contract.continuity_required']
    errors: list[str] = []
    if continuity.get('take_structure') != 'single_take':
        errors.append('one_take_rule_requires_take_structure:single_take')
    grammar = str(pack.get('shot_grammar') or '')
    if grammar not in SINGLE_SHOT_GRAMMARS:
        errors.append(f'one_take_rule_wrong_shot_grammar:{grammar or "<empty>"}')
    camera_axis = continuity.get('camera_axis')
    if not isinstance(camera_axis, dict):
        errors.append('continuity.camera_axis_required')
    else:
        for field in ('side', 'subject_placement', 'lead_room'):
            if not str(camera_axis.get(field) or '').strip():
                errors.append(f'continuity.camera_axis_missing:{field}')
    cut_direction = _contains_positive_cut_direction(_prompt_text(pack))
    if cut_direction:
        interpretation = str(continuity.get('tempo_interpretation') or '').strip()
        if not (
            _user_reference_superior(pack)
            and interpretation == 'rapid_performance_handheld_no_edits'
        ):
            errors.append(f'one_take_conflicts_with_cut_direction:{cut_direction}')
    return errors


def _validate_physical_effect(pack: dict[str, Any]) -> list[str]:
    effects = _contract(pack).get('effects')
    if not isinstance(effects, list) or not effects:
        return ['semantic_contract.effects_required']
    errors: list[str] = []
    for index, effect in enumerate(effects, 1):
        if not isinstance(effect, dict):
            errors.append(f'effect_{index}_not_object')
            continue
        for field in ('effect_id', 'cause', 'material_mechanism', 'travel', 'impact', 'aftermath'):
            if not str(effect.get(field) or '').strip():
                errors.append(f'effect_{index}_missing:{field}')
        reactions = effect.get('nearby_reactions')
        if not isinstance(reactions, list) or len([item for item in reactions if str(item).strip()]) < 2:
            errors.append(f'effect_{index}_requires_two_nearby_reactions')
    return errors


def _validate_audio_lipsync(pack: dict[str, Any]) -> list[str]:
    contract = _contract(pack)
    audio = contract.get('audio_contract')
    if not isinstance(audio, dict):
        return ['semantic_contract.audio_contract_required']
    errors: list[str] = []
    token = _canonical_token(audio.get('source_token'))
    known_refs = {ref.casefold() for ref, _role in _reference_entries(pack)}
    if not re.fullmatch(r'@Audio\d+', token, re.IGNORECASE):
        errors.append(f'audio_contract_invalid_source_token:{token or "<empty>"}')
    elif token.casefold() not in known_refs:
        errors.append(f'audio_contract_unknown_source_token:{token}')
    if audio.get('exclusive_source') is not True:
        errors.append('audio_contract.exclusive_source_must_be_true')
    performer = str(audio.get('performer_entity_id') or '').strip()
    if not performer:
        errors.append('audio_contract.performer_entity_id_required')
    if not str(audio.get('face_visibility') or '').strip():
        errors.append('audio_contract.face_visibility_required')
    non_speakers = audio.get('non_speaking_entity_ids')
    if not isinstance(non_speakers, list):
        errors.append('audio_contract.non_speaking_entity_ids_required')
    elif performer and performer in {str(item) for item in non_speakers}:
        errors.append('audio_contract.performer_cannot_be_non_speaker')
    segments = audio.get('lip_sync_segments')
    if not isinstance(segments, list) or not segments:
        return errors + ['audio_contract.lip_sync_segments_required']
    previous_end = 0.0
    try:
        duration = float(pack.get('duration_sec'))
    except (TypeError, ValueError):
        duration = 0.0
    for index, segment in enumerate(segments, 1):
        if not isinstance(segment, dict):
            errors.append(f'lip_sync_segment_{index}_not_object')
            continue
        try:
            start = float(segment.get('start_sec'))
            end = float(segment.get('end_sec'))
        except (TypeError, ValueError):
            errors.append(f'lip_sync_segment_{index}_invalid_time')
            continue
        if start < previous_end - 0.05:
            errors.append(f'lip_sync_segment_{index}_overlap:{start}<{previous_end}')
        if end <= start or start < 0 or (duration and end > duration + 0.05):
            errors.append(f'lip_sync_segment_{index}_out_of_range:{start}-{end}')
        previous_end = max(previous_end, end)
        if not str(segment.get('content') or '').strip():
            errors.append(f'lip_sync_segment_{index}_missing:content')
    return errors


def _validate_exact_text_dialogue(pack: dict[str, Any]) -> list[str]:
    contract = _contract(pack)
    prompt = _prompt_text(pack)
    errors: list[str] = []
    dialogue = contract.get('dialogue')
    on_screen = contract.get('on_screen_text')
    if not isinstance(dialogue, list):
        errors.append('semantic_contract.dialogue_list_required')
        dialogue = []
    if not isinstance(on_screen, list):
        errors.append('semantic_contract.on_screen_text_list_required')
        on_screen = []
    if not dialogue and not on_screen:
        errors.append('exact_text_dialogue_rule_requires_text_or_dialogue')

    known_refs = {ref.casefold() for ref, _role in _reference_entries(pack)}
    for index, row in enumerate(dialogue, 1):
        if not isinstance(row, dict):
            errors.append(f'dialogue_{index}_not_object')
            continue
        for field in ('speaker_entity_id', 'exact_text', 'language', 'delivery'):
            if not str(row.get(field) or '').strip():
                errors.append(f'dialogue_{index}_missing:{field}')
        exact = str(row.get('exact_text') or '')
        if exact and exact not in prompt:
            errors.append(f'dialogue_{index}_literal_missing_from_prompt')
        audio_token = _canonical_token(row.get('audio_reference_token'))
        native_route = (
            _user_reference_superior(pack)
            and row.get('audio_route') == 'native_seedance_user_reference'
        )
        if native_route:
            if not str(row.get('qc_route') or '').strip():
                errors.append(f'dialogue_{index}_native_route_qc_required')
        elif not re.fullmatch(r'@Audio\d+', audio_token, re.IGNORECASE):
            errors.append(
                f'dialogue_{index}_audio_route_required:'
                'performed_@AudioN_or_native_seedance_user_reference')
        elif audio_token.casefold() not in known_refs:
            errors.append(f'dialogue_{index}_unknown_audio_reference:{audio_token}')

    for index, row in enumerate(on_screen, 1):
        if not isinstance(row, dict):
            errors.append(f'on_screen_text_{index}_not_object')
            continue
        for field in ('exact_text', 'language', 'appearance_action', 'qc_route'):
            if not str(row.get(field) or '').strip():
                errors.append(f'on_screen_text_{index}_missing:{field}')
        exact = str(row.get('exact_text') or '')
        if exact and exact not in prompt:
            errors.append(f'on_screen_text_{index}_literal_missing_from_prompt')
    return errors


def _validate_constraint_consistency(pack: dict[str, Any]) -> list[str]:
    constraints = _contract(pack).get('constraints')
    if not isinstance(constraints, dict):
        return ['semantic_contract.constraints_required']
    errors: list[str] = []
    required = {
        str(item).strip().casefold() for item in (constraints.get('required') or [])
        if str(item).strip()
    }
    forbidden = {
        str(item).strip().casefold() for item in (constraints.get('forbidden') or [])
        if str(item).strip()
    }
    for feature in sorted(required & forbidden):
        errors.append(f'constraint_required_and_forbidden:{feature}')

    prompt = _prompt_text(pack)
    without_no_lens_flare = re.sub(
        r'no\s+(?:lens\s+)?flares?', '', prompt, flags=re.IGNORECASE)
    if re.search(r'no\s+(?:lens\s+)?flares?', prompt, re.IGNORECASE) and re.search(
            r'(?:sun|lens)\s+flare', without_no_lens_flare, re.IGNORECASE):
        errors.append('prompt_requires_and_forbids_lens_flare')
    return errors


def validate_case_contract(pack: dict[str, Any]) -> list[str]:
    """Return deterministic semantic errors for the declared conditional rules."""
    errors = _validate_reference_token_forms(pack)
    rules = _rules(pack)
    validators = (
        (USER_REFERENCE_SUPERIOR_RULE, _validate_user_reference_authority),
        (REFERENCE_CAST_LEDGER_RULE, _validate_reference_cast_ledger),
        (TIMED_PERFORMANCE_RULE, _validate_timed_beats),
        (ONE_TAKE_AXIS_RULE, _validate_one_take_axis),
        (PHYSICAL_EFFECT_RULE, _validate_physical_effect),
        (AUDIO_LIPSYNC_RULE, _validate_audio_lipsync),
        (EXACT_TEXT_DIALOGUE_RULE, _validate_exact_text_dialogue),
        (CONSTRAINT_CONSISTENCY_RULE, _validate_constraint_consistency),
    )
    for rule, validator in validators:
        if rule in rules:
            errors.extend(validator(pack))
    return list(dict.fromkeys(errors))


def load_pack(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f'invalid prompt pack: {path}: {exc}') from exc
    if not isinstance(value, dict):
        raise ValueError('prompt pack must be one JSON object')
    return value


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Validate conditional Seedance semantic prompt contracts.')
    parser.add_argument('--pack', required=True, type=Path)
    args = parser.parse_args()
    try:
        pack = load_pack(args.pack.expanduser().resolve())
        errors = validate_case_contract(pack)
    except ValueError as exc:
        errors = [str(exc)]
    result = {
        'verdict': 'PASS' if not errors else 'FAIL_DO_NOT_ATTEST',
        'pack': str(args.pack.expanduser().resolve()),
        'errors': errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 2


if __name__ == '__main__':
    raise SystemExit(main())
