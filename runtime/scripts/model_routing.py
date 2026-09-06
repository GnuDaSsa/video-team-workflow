#!/usr/bin/env python3
"""Deterministic model policy for the sequential video-team runtime.

This module selects the reasoning model for a foreground lane/phase.  It never
starts a process, opens a browser, or grants spawn approval.  Dispatch remains
an explicit runtime action and only one Codex owner may run at a time.
"""
from __future__ import annotations


POLICY_VERSION = 'video_team_model_routing_v1_20260829'

SOL_MODEL = 'gpt-5.6-sol'
SOL_EFFORT = 'xhigh'
LUNA_MODEL = 'gpt-5.6-luna'
LUNA_EFFORT = 'high'

ROUTES = {
    'director': (LUNA_MODEL, LUNA_EFFORT, 'workflow_direction'),
    'music': (LUNA_MODEL, LUNA_EFFORT, 'music_flow_and_lock'),
    'planner': (LUNA_MODEL, LUNA_EFFORT, 'planning_and_cut_map'),
    'image_creator_01': (SOL_MODEL, SOL_EFFORT, 'image_prompting_and_generation_owner'),
    'image_creator_02': (SOL_MODEL, SOL_EFFORT, 'image_prompting_and_generation_owner'),
    'image_qc': (LUNA_MODEL, LUNA_EFFORT, 'image_qc'),
    'seedance:prompting': (SOL_MODEL, SOL_EFFORT, 'video_prompt_authoring'),
    'seedance:production': (LUNA_MODEL, LUNA_EFFORT, 'aside_cli_and_computer_use'),
    'seedance_qc': (LUNA_MODEL, LUNA_EFFORT, 'video_qc'),
    'editor': (LUNA_MODEL, LUNA_EFFORT, 'capcut_and_edit_flow'),
    'package': (LUNA_MODEL, LUNA_EFFORT, 'package_and_delivery_flow'),
}


def route_key(lane: str, phase: str | None = None) -> str:
    if lane == 'seedance':
        if phase not in {'prompting', 'production'}:
            raise ValueError('seedance model routing requires phase=prompting|production')
        return f'seedance:{phase}'
    return lane


def resolve(lane: str, phase: str | None = None) -> dict:
    key = route_key(lane, phase)
    try:
        model, reasoning_effort, purpose = ROUTES[key]
    except KeyError as exc:
        raise ValueError(f'no model route for {key}') from exc
    return {
        'policy_version': POLICY_VERSION,
        'route_key': key,
        'lane': lane,
        'phase': phase if lane == 'seedance' else 'lane',
        'model': model,
        'reasoning_effort': reasoning_effort,
        'purpose': purpose,
        'parallel_owner_allowed': False,
        'dispatch_requires_explicit_action': True,
        'required_spawn_approval': f'{lane}:{phase if lane == "seedance" else "lane"}',
    }


def matrix() -> list[dict]:
    rows = []
    for key in ROUTES:
        lane, sep, phase = key.partition(':')
        rows.append(resolve(lane, phase if sep else None))
    return rows
