"""Narrow deterministic regressions, not a substitute for visual/semantic review."""
from __future__ import annotations
import re

SCOPES = {'human_only', 'drone_only', 'mixed', 'environment_only', 'object_only'}


def render_scope(pack: dict) -> str:
    scope = str(pack.get('render_scope') or '')
    if not scope and pack.get('separated_identity_only') is True:
        block = str(pack.get('block_id') or '')
        if block.endswith('_HUMAN'):
            scope = 'human_only'
        elif block.endswith('_DRONE'):
            scope = 'drone_only'
    return scope


def validate(pack: dict) -> list[str]:
    errors = []
    scope = render_scope(pack)
    if scope and scope not in SCOPES:
        errors.append('semantic_unknown_render_scope:' + scope)
    fields = {key: str(pack.get(key) or '') for key in ('prompt', 'prompt_s2')}
    for field, text in fields.items():
        if re.search(r'(?:추적|트래킹|tracking)\s*(?:또는|or)\s*(?:정면\s*)?(?:고정|static)', text, re.I):
            errors.append(field + '_unresolved_camera_choice')
        if re.search(r'(?:입력\s*모드\s*:|첨부한?\s*순서.{0,30}토큰.{0,15}바꾸지|을\(를\)|이\(가\))', text):
            errors.append(field + '_compiler_or_operator_text_leak')
        if re.search(r'[`\w-]+\.(?:png|jpg|mp4|wav)(?![A-Za-z0-9])', text, re.I):
            errors.append(field + '_media_filename_leak')
        if scope == 'drone_only':
            for sentence in re.split(r'[.。!\n]', text):
                # Allow explicit exclusions; flag the proven affirmative boilerplate.
                if (re.search(r'소매|머리카락|sleeves?|hair', sentence, re.I)
                        and re.search(r'반응|흔들|따라온|react|sway|follow', sentence, re.I)
                        and not re.search(r'않|없|금지|배제|\bno\b|\bnever\b', sentence, re.I)):
                    errors.append(field + '_human_motion_in_drone_only')
                    break
        if scope == 'human_only':
            for sentence in re.split(r'[.。!\n]', text):
                affirmative_hover = re.search(r'드론은\s*공중에만\s*(?:있고|있다|있으며|머문|머무|존재)', sentence)
                if affirmative_hover or (re.search(r'드론이\s*(?:가속|상승|호버)', sentence)
                        and not re.search(r'않|없|금지|배제|말|\bno\b|\bnever\b', sentence, re.I)):
                    errors.append(field + '_drone_motion_in_human_only')
                    break
    for index, scene in enumerate(pack.get('scene_plan') or [], 1):
        if not isinstance(scene, dict):
            continue
        camera = str(scene.get('camera') or '')
        if re.search(r'또는|\bor\b', camera, re.I) and not re.search(r'\bno\b|\bnever\b|않|금지', camera, re.I):
            errors.append(f'scene_{index}_camera_choice_not_decided')
    return list(dict.fromkeys(errors))
