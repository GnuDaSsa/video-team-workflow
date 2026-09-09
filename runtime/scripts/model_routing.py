#!/usr/bin/env python3
"""Deterministic model policy for the sequential video-team runtime.

This module selects the reasoning model for a foreground lane/phase.  It never
starts a process, opens a browser, or grants spawn approval.  Dispatch remains
an explicit runtime action and only one Codex owner may run at a time.
"""
from __future__ import annotations


POLICY_VERSION = 'video_team_model_routing_v2_20260906'

ASTRA_MODEL = 'gpt-6-astra'
ASTRA_EFFORT = 'xhigh'
LUNA_MODEL = 'gpt-5.6-luna'
LUNA_EFFORT = 'high'

ROUTES = {
    'director': (LUNA_MODEL, LUNA_EFFORT, 'workflow_direction'),
    'music': (LUNA_MODEL, LUNA_EFFORT, 'music_flow_and_lock'),
    'planner': (LUNA_MODEL, LUNA_EFFORT, 'planning_and_cut_map'),
    'image_creator_01': (ASTRA_MODEL, ASTRA_EFFORT, 'image_prompting_and_generation_owner'),
    'image_creator_02': (ASTRA_MODEL, ASTRA_EFFORT, 'image_prompting_and_generation_owner'),
    'image_qc': (LUNA_MODEL, LUNA_EFFORT, 'image_qc'),
    'seedance:prompting': (ASTRA_MODEL, ASTRA_EFFORT, 'video_prompt_authoring'),
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


def existing_owner_handoff(*, manager_id: str, owner_id: str,
                           owner_status: str, phase: str, action: str) -> dict:
    """Build a native follow-up payload; never dispatch or certify execution."""
    import uuid
    for value in (manager_id, owner_id):
        uuid.UUID(value)
    if manager_id == owner_id:
        raise ValueError('manager_and_executor_must_differ')
    if owner_status != 'idle':
        raise ValueError('existing_owner_must_be_observed_idle')
    if not action.strip():
        raise ValueError('bounded_action_required')
    route = resolve('seedance', phase)
    prompt = (
        '[기존 작업 직접 실행 요청]\n'
        f'실행 담당 작업: {owner_id}\n'
        f'관리·결과 수신 작업: {manager_id}\n'
        f'현재 단계: {phase}\n'
        '이 메시지를 받은 작업이 실행 담당입니다. 관리 작업에 이 지시를 '
        '재전송하거나 실행을 맡기지 마세요. 관리 작업을 wait_threads로 '
        '기다리는 것도 실행이 아닙니다.\n\n'
        f'직접 수행할 범위:\n{action.strip()}\n\n'
        '반환할 것은 새 결과입니다: 실제 수행 동작, 관측 시각, 기존 산출물 '
        '경로/검증 근거, 미완료 또는 차단 사유, 다음 확인 대상·시각. '
        '기존 lane status/result에 기록하고 이 작업의 final로 보고하세요. '
        '관리자는 그 결과를 읽습니다. 원문 지시나 접수 확인만 반환하면 '
        '미실행으로 처리됩니다. 새 작업/agent/예약은 만들지 마세요. '
        '최신 사용자 HOLD와 안전 게이트를 유지하세요.'
    )
    return {'threadId': owner_id, 'model': route['model'],
            'thinking': route['reasoning_effort'], 'prompt': prompt}


def is_instruction_echo(request: str, reply: str) -> bool:
    """Reject exact/whitespace echoes, including an unchanged quoted request.

    False means only 'not an exact echo', NEVER verified execution.
    """
    import unicodedata
    def compact(value):
        return ''.join(unicodedata.normalize('NFC', value).split())
    original, returned = compact(request), compact(reply)
    return bool(original) and original in returned


if __name__ == '__main__':
    import argparse
    import json
    parser = argparse.ArgumentParser(description='Build an existing-owner handoff; no dispatch')
    parser.add_argument('--manager-id', required=True)
    parser.add_argument('--owner-id', required=True)
    parser.add_argument('--owner-status', required=True)
    parser.add_argument('--phase', choices=['prompting', 'production'], required=True)
    parser.add_argument('--action', required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(existing_owner_handoff(**vars(args)), ensure_ascii=False))
    except ValueError as exc:
        parser.error(str(exc))
