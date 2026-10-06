#!/usr/bin/env python3
"""Offline consistency check, never a browser controller or execution permission.

Operator evidence is supplied, not authenticated by this program. See
execution-profiles.md for the mandatory supported-tool visual review.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import urlparse, parse_qs

REPO = Path(__file__).resolve().parents[3]
if (REPO / 'runtime/scripts').is_dir():
    os.environ.setdefault('VIDEO_TEAM_RUNTIME_SCRIPTS', str(REPO / 'runtime/scripts'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import runway_ui_helper as shared
from prompt_packet_utils import (validate_paste_pack, validate_knowledge_selection,
                                 prompt_sha256, _reference_role_entries)

PROFILE = 'cloud_cua_runway_20'


def require(condition, code):
    if not condition:
        raise ValueError(code)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def check(project: Path, pack_path: Path, observation: dict, *, now=None) -> dict:
    project, pack_path = project.resolve(), pack_path.resolve()
    require(pack_path.is_relative_to(project), 'CLOUD_PACK_OUTSIDE_PROJECT')
    pack = json.loads(pack_path.read_text())
    require(isinstance(pack, dict) and isinstance(observation, dict), 'CLOUD_OBJECT_REQUIRED')
    require(re.fullmatch(r'[A-Za-z0-9_-]+', str(pack.get('block_id', ''))), 'CLOUD_BLOCK_INVALID')
    require(pack.get('execution_profile') == PROFILE and observation.get('execution_profile') == PROFILE,
            'CLOUD_PROFILE_REQUIRED')
    require(observation.get('environment') == 'cloud' and observation.get('tool_surface') == 'supported_cloud_cua',
            'CLOUD_SUPPORTED_SURFACE_REQUIRED')
    for key in ('tool_capability_evidence', 'user_scope_evidence', 'visible_ui_evidence', 'chip_binding_evidence'):
        require(nonempty(observation.get(key)), 'CLOUD_EVIDENCE_REQUIRED:' + key)
    require(observation.get('denial_present') is False, 'CLOUD_DENIAL_OR_UNKNOWN')
    require(observation.get('dialog_present') is False, 'CLOUD_DIALOG_OR_UNKNOWN')
    require(observation.get('prior_submission') == 'none', 'CLOUD_PRIOR_SUBMISSION_UNCERTAIN')
    require(observation.get('block_id') == pack['block_id'], 'CLOUD_BLOCK_MISMATCH')
    stamp = dt.datetime.fromisoformat(str(observation.get('observed_at', '')))
    require(stamp.tzinfo is not None, 'CLOUD_TIMEZONE_REQUIRED')
    age = ((now or dt.datetime.now(dt.timezone.utc)) - stamp).total_seconds()
    require(0 <= age <= 120, 'CLOUD_STALE_OBSERVATION')
    url = str(observation.get('session_url', ''))
    parsed = urlparse(url)
    require(parsed.scheme == 'https' and parsed.netloc == 'app.runwayml.com'
            and bool(parse_qs(parsed.query).get('sessionId')), 'CLOUD_SESSION_INVALID')
    require(nonempty(observation.get('tab_id')) and observation.get('session_matches_checkpoint') is True,
            'CLOUD_SESSION_NOT_VERIFIED')
    # The checkpoint is immutable input to the attested pack, not invented here.
    checkpoint = pack.get('cloud_session_checkpoint', {})
    require(isinstance(checkpoint, dict), 'CLOUD_CHECKPOINT_REQUIRED')
    require(checkpoint.get('session_url') == url and checkpoint.get('tab_id') == observation['tab_id'],
            'CLOUD_CHECKPOINT_MISMATCH')
    require(observation.get('pack_sha256') == hashlib.sha256(pack_path.read_bytes()).hexdigest(),
            'CLOUD_PACK_HASH_MISMATCH')
    validate_paste_pack(pack_path, str(pack.get('prompt', '')), project)
    if shared.generation_settings.project_layout(project) == 'runtime_v4':
        knowledge_errors, _ = validate_knowledge_selection(pack, project)
        require(not knowledge_errors, 'CLOUD_KNOWLEDGE_INVALID:' + ','.join(knowledge_errors))
    require(observation.get('visible_prompt_sha256') == prompt_sha256(pack['prompt']), 'CLOUD_PROMPT_MISMATCH')
    # No whitespace token replacement is performed. Chip identity has separate evidence.
    expected = pack.get('cloud_reference_deck')
    actual = observation.get('reference_deck')
    require(isinstance(expected, list) and bool(expected) and isinstance(actual, list)
            and len(expected) == len(actual), 'CLOUD_DECK_COUNT')
    roles = dict(_reference_role_entries(pack['reference_role_map']))
    require(len(roles) == len(expected), 'CLOUD_DECK_ROLE_COUNT')
    for index, (want, seen) in enumerate(zip(expected, actual), 1):
        require(isinstance(want, dict) and isinstance(seen, dict), 'CLOUD_DECK_ENTRY_REQUIRED')
        token = '@Image' + str(index)
        require(want.get('token') == token and token in roles and seen.get('token') == token,
                'CLOUD_SLOT_MISMATCH')
        asset = shared.media_registry.get_asset(project, want.get('asset_id', ''))
        path = Path(asset['current_path'])
        require(asset.get('kind') == 'image' and asset.get('active')
                and asset.get('state') in {'approved', 'selected', 'locked'}
                and path.is_file() and shared.media_registry.sha256(path) == asset.get('sha256'),
                'CLOUD_ASSET_NOT_APPROVED_OR_CHANGED')
        require(want.get('sha256') == asset['sha256'] and seen.get('asset_id') == asset['asset_id']
                and seen.get('sha256') == asset['sha256'], 'CLOUD_ASSET_MISMATCH')
        require(seen.get('enlarged_image_verified') is True and seen.get('asset_bound_chip_verified') is True
                and nonempty(seen.get('chip_evidence')) and seen.get('role') == roles[token],
                'CLOUD_IMAGE_OR_CHIP_UNVERIFIED')
    settings = observation.get('settings', {})
    wanted_settings = pack.get('cloud_expected_settings', {})
    require(isinstance(settings, dict) and isinstance(wanted_settings, dict), 'CLOUD_SETTINGS_REQUIRED')
    require(wanted_settings.get('mode') == 'Multi-reference' and wanted_settings.get('audio') == 'On'
            and wanted_settings.get('ratio') in {'16:9', '9:16'}, 'CLOUD_UNSUPPORTED_SETTINGS')
    require(settings == wanted_settings, 'CLOUD_SETTINGS_MISMATCH')
    require(settings.get('model') == 'Seedance 2.0', 'CLOUD_UNSUPPORTED_MODEL')
    require(observation.get('generate_eligible') is True, 'CLOUD_GENERATE_NOT_ELIGIBLE')
    # Reuse current compiler/lock/model validation; do not mint an Aside receipt.
    result = shared.verify_attested_generation_settings(project, pack['block_id'],
        visible_model=settings['model'], duration_sec=settings.get('duration_sec'), write_receipt=False)
    return {'ok': True, 'execution_profile': PROFILE, 'block_id': pack['block_id'],
            'verdict': 'PASS_OFFLINE_CONSISTENCY_ONLY', 'live_ui_verified_by_checker': False,
            'execution_authorized_by_checker': False, 'settings_consistency': result,
            'observation_sha256': hashlib.sha256(json.dumps(observation, sort_keys=True).encode()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--pack', type=Path, required=True)
    parser.add_argument('--observation', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = check(args.project, args.pack, json.loads(args.observation.read_text()))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({'ok': False, 'verdict': 'BLOCKED_CLOUD_PREFLIGHT', 'error': str(exc)}))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
