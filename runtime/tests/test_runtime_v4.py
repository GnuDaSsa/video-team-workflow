from __future__ import annotations

import contextlib
import datetime as dt
import io
import json
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock


SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
os.environ.setdefault('VIDEO_TEAM_RUNTIME_SCRIPTS', str(SCRIPTS))
sys.path.insert(0, str(SCRIPTS))

import lane_gates  # noqa: E402
import generation_settings  # noqa: E402
import media_registry  # noqa: E402
import prompt_packet_utils  # noqa: E402
import runway_ui_helper  # noqa: E402
import sequence_manager  # noqa: E402
import video_codex_runtime  # noqa: E402
import video_knowledge_router  # noqa: E402


VALID_KOREAN_PROMPT = (
    '승인된 인물과 골목 풍경을 서로 독립된 시각 기준으로 사용한다. '
    '카메라는 인물의 옆을 천천히 따라가다가 손이 문고리에 닿는 순간 멈춘다. '
    '바람에 옷자락과 간판 그림자가 자연스럽게 흔들리고, 문이 열리면 따뜻한 실내 빛이 '
    '바닥을 따라 번진다. 마지막에는 인물이 안쪽을 바라보는 안정된 중간 구도로 끝낸다.'
)


class RuntimeV4Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.wiki_root = self.root / 'wiki'
        concepts = self.wiki_root / 'concepts'
        concepts.mkdir(parents=True)
        (concepts / 'core.md').write_text(
            '# Core\n\n## Prompt\n\n\ud55c\uae00 \ud504\ub86c\ud504\ud2b8 \ud575\uc2ec \uaddc\uce59.\n', encoding='utf-8')
        (concepts / '2d.md').write_text(
            '# 2D\n\n2D STYLE LOCK CONTINUITY DIRECTION SHOT.\n', encoding='utf-8')
        (concepts / 'live.md').write_text(
            '# Live\n\n\uc2e4\uc0ac \ud53c\ubd80\uc640 \ub80c\uc988 \uc790\uc5f0주의.\n', encoding='utf-8')
        (concepts / 'higgs.md').write_text(
            '# Higgsfield\n\n## Priority\n\n카메라 패밀리를 먼저 고르고 물리적으로 번역한다.\n',
            encoding='utf-8')
        (concepts / 'camera.md').write_text(
            '# Camera\n\n## Composition\n\n\uc0f7 \uac70\ub9ac\uc640 \uac01\ub3c4.\n\n## Action\n\n\uc0ac\uc774\ub4dc \ud2b8\ub798\ud0b9\uacfc \uc561\uc158 \ubca1\ud130.\n',
            encoding='utf-8')
        meta = self.wiki_root / '_meta'
        meta.mkdir()
        self.catalog_path = meta / 'video-knowledge-catalog.json'
        self.catalog_path.write_text(json.dumps({
            'schema_version': 'test-v1',
            'aliases': {'mediums': {'2d': '2d_animation'}},
            'entries': [
                {'id': 'core', 'path': 'concepts/core.md', 'always': True,
                 'priority': 100, 'max_chars': 1000},
                {'id': 'higgsfield-core', 'path': 'concepts/higgs.md', 'section': 'Priority',
                 'always': True, 'priority': 98, 'max_chars': 1000,
                 'priority_class': 'preferred_higgsfield_community',
                 'provenance': 'test_higgsfield_community'},
                {'id': 'composition', 'path': 'concepts/camera.md', 'section': 'Composition',
                 'always': True, 'priority': 90, 'max_chars': 1000},
                {'id': 'medium-2d', 'path': 'concepts/2d.md', 'match': {
                    'mediums': ['2d_animation']}, 'require_match': ['mediums'], 'priority': 20},
                {'id': 'medium-live', 'path': 'concepts/live.md', 'match': {
                    'mediums': ['live_action']}, 'require_match': ['mediums'], 'priority': 20},
                {'id': 'camera-action', 'path': 'concepts/camera.md', 'section': 'Action',
                 'match': {'shot_roles': ['action']}, 'require_match': ['shot_roles'],
                 'priority': 10},
            ],
        }, ensure_ascii=False), encoding='utf-8')

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def init_with_runtime(
        self,
        slug: str = '테스트영상',
        mode: str = video_codex_runtime.STANDARD_I2V_MODE,
    ) -> Path:
        old_root = video_codex_runtime.PROJECT_ROOT
        video_codex_runtime.PROJECT_ROOT = self.root / 'projects'
        try:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                video_codex_runtime.init_project(SimpleNamespace(
                    slug=slug, brief='v4 테스트 프로젝트', mode=mode))
            return Path(output.getvalue().strip())
        finally:
            video_codex_runtime.PROJECT_ROOT = old_root

    def valid_pack(self, block: str = 'B01') -> dict:
        return {
            'block_id': block,
            'prompt_language': prompt_packet_utils.PROMPT_LANGUAGE,
            'prompt': VALID_KOREAN_PROMPT,
            'reference_role_map': [{'reference': '@Image1', 'role': '인물과 공간 기준'}],
            'duration_sec': 15,
            'shot_grammar': prompt_packet_utils.SINGLE_SHOT_GRAMMAR,
            'audio_route': 'Audio ON, 현장음 중심',
            'prompt_rules_used': ['references_are_anchor_not_cage'],
            'prompt_style_version': prompt_packet_utils.SEEDANCE_PROMPT_STYLE_VERSION,
            'authoring_contract': prompt_packet_utils.SEEDANCE_AUTHORING_CONTRACT,
        }

    def pack_with_knowledge(self, project: Path, block: str = 'B01') -> dict:
        generation_settings.lock_duration(
            project, 15, 'planner_revision:test_fixture_15s_lock')
        manifest_path = project / 'manifest.json'
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        manifest['knowledge_routing']['catalog'] = str(self.catalog_path)
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        attributes = project / 'lanes' / 'planner' / 'video_attributes.json'
        attributes.write_text(json.dumps({
            'schema_version': 'video-attributes-v1',
            'global': {'medium': '2d_animation'},
            'blocks': {block: {'shot_roles': ['action'], 'cameras': ['tracking']}},
        }, ensure_ascii=False), encoding='utf-8')
        receipt = video_knowledge_router.select_knowledge(
            project, block, wiki_root=self.wiki_root, catalog_path=self.catalog_path,
            attributes_path=attributes, budget_chars=4000, max_selections=5)
        pack = self.valid_pack(block)
        pack.update({
            'knowledge_selection_id': receipt['selection_id'],
            'knowledge_context_sha256': receipt['context_sha256'],
            'knowledge_selected_ids': [item['id'] for item in receipt['selected']],
        })
        return pack

    def test_init_creates_numbered_media_tree_and_registry(self) -> None:
        project = self.init_with_runtime()
        manifest = json.loads((project / 'manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(manifest['media_schema_version'], media_registry.MEDIA_SCHEMA_VERSION)
        self.assertEqual(manifest['execution_budget']['image_generation_workers_max'], 3)
        self.assertEqual(manifest['execution_budget']['detached_monitors_max'], 0)
        duration_lock = json.loads(
            generation_settings.duration_lock_path(project).read_text(encoding='utf-8'))
        self.assertEqual(duration_lock['status'], 'LOCKED')
        self.assertEqual(duration_lock['default_duration_sec'], 15)
        self.assertEqual(duration_lock['source'], 'workflow_default:seedance_15s')
        self.assertTrue((project / media_registry.REGISTRY_NAME).is_file())
        for folder_name in media_registry.FOLDERS.values():
            self.assertTrue((project / 'media' / folder_name).is_dir(), folder_name)
        self.assertFalse((project / 'assets').exists())

    def test_no_i2v_is_a_mode_on_the_same_v4_workflow(self) -> None:
        project = self.init_with_runtime(
            '노아이투브이', video_codex_runtime.NO_I2V_MODE)
        manifest = json.loads((project / 'manifest.json').read_text(encoding='utf-8'))

        self.assertEqual(manifest['generation_mode'], video_codex_runtime.NO_I2V_MODE)
        self.assertEqual(list(manifest['lanes']), video_codex_runtime.LANES)
        self.assertEqual(manifest['media_schema_version'], media_registry.MEDIA_SCHEMA_VERSION)
        self.assertTrue(manifest['visual_generation_strategy']['reference_minimal'])
        self.assertTrue(manifest['visual_generation_strategy']['prompt_heavy'])
        self.assertFalse(manifest['visual_generation_strategy']['per_cut_styleframes'])
        self.assertTrue((project / media_registry.REGISTRY_NAME).is_file())

    def test_mode_switch_changes_only_unsubmitted_blocks(self) -> None:
        project = self.init_with_runtime('모드전환')
        manifest_path = project / 'manifest.json'
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        manifest['blocks'] = [
            {'block_id': 'B01', 'status': 'SUBMITTED', 'provider_job_id': 'job-1'},
            {'block_id': 'B02', 'status': 'PLANNED', 'source_frame_file': '/tmp/B02.png'},
        ]
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding='utf-8')

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            video_codex_runtime.set_mode(SimpleNamespace(
                project=str(project), mode=video_codex_runtime.NO_I2V_MODE))
        result = json.loads(output.getvalue())
        updated = json.loads(manifest_path.read_text(encoding='utf-8'))

        self.assertEqual(result['preserved_submitted_blocks'], ['B01'])
        self.assertEqual(result['changed_unsubmitted_blocks'], ['B02'])
        self.assertNotIn('generation_mode', updated['blocks'][0])
        self.assertEqual(updated['blocks'][1]['generation_mode'], video_codex_runtime.NO_I2V_MODE)
        self.assertIsNone(updated['blocks'][1]['source_frame_file'])
        self.assertEqual(updated['blocks'][1]['keyframe_refs'], [])
        self.assertFalse(updated['mode_switch']['existing_media_deleted'])

    def test_no_i2v_image_qc_accepts_reused_approved_reference(self) -> None:
        project = self.init_with_runtime(
            '레퍼런스재사용', video_codex_runtime.NO_I2V_MODE)
        src = self.root / 'approved-reference.png'
        src.write_bytes(b'reusable-reference')
        asset = media_registry.ingest(
            project, src, kind='image', state='candidate', work_item_id='REF01')
        media_registry.promote(project, asset['asset_id'])

        ok, reason = lane_gates.gate_check(project, 'image_qc')

        self.assertTrue(ok, reason)

    def test_ingest_promote_and_revision_keep_stable_identity(self) -> None:
        project = self.init_with_runtime('자산테스트')
        src1 = self.root / 'first.png'; src1.write_bytes(b'first-image')
        first = media_registry.ingest(
            project, src1, kind='image', state='candidate', work_item_id='C001',
            origin_lane='image_creator_01', prompt_hash='p1')
        self.assertTrue(Path(first['current_path']).is_file())
        self.assertIn(media_registry.FOLDERS['images_candidates'], first['current_path'])
        again = media_registry.ingest(
            project, Path(first['current_path']), kind='image', state='candidate',
            work_item_id='C001')
        self.assertEqual(again['asset_id'], first['asset_id'])
        promoted = media_registry.promote(project, first['asset_id'])
        self.assertEqual(promoted['asset_id'], first['asset_id'])
        self.assertEqual(promoted['state'], 'approved')
        self.assertIn(media_registry.FOLDERS['images_approved'], promoted['current_path'])
        promoted_again = media_registry.promote(project, first['asset_id'])
        self.assertEqual(promoted_again['current_path'], promoted['current_path'])

        src2 = self.root / 'second.png'; src2.write_bytes(b'second-image')
        second = media_registry.ingest(
            project, src2, kind='image', state='candidate', work_item_id='C001',
            parent_asset_id=first['asset_id'], prompt_hash='p2')
        self.assertNotEqual(second['asset_id'], first['asset_id'])
        self.assertEqual(second['parent_asset_id'], first['asset_id'])
        self.assertEqual(second['revision'], 2)

    def test_media_scatter_and_unregistered_files_are_hard_gates(self) -> None:
        project = self.init_with_runtime('게이트테스트')
        stray = project / 'lanes' / 'director' / 'stray.mp4'
        stray.write_bytes(b'not-real-video')
        audit = media_registry.audit_project(project)
        self.assertTrue(any('MEDIA_OUTSIDE_CANONICAL_ROOT' in p for p in audit['problems']))
        ok, reason = lane_gates.gate_check(project, 'director')
        self.assertFalse(ok)
        self.assertTrue(reason.startswith('MEDIA_HARD_GATE:'))
        self.assertTrue(lane_gates.non_bypassable_reason(project, reason))

        stray.unlink()
        unregistered = media_registry.folder(project, 'images_candidates') / 'loose.png'
        unregistered.write_bytes(b'loose')
        audit = media_registry.audit_project(project)
        self.assertTrue(any('UNREGISTERED_MEDIA' in p for p in audit['problems']))

    def test_legacy_project_is_not_migrated_or_audited_as_v4(self) -> None:
        project = self.root / 'legacy'; project.mkdir()
        (project / 'manifest.json').write_text('{"project_id":"legacy"}\n', encoding='utf-8')
        before = sorted(project.iterdir())
        audit = media_registry.audit_project(project)
        self.assertFalse(audit['applicable'])
        self.assertEqual(before, sorted(project.iterdir()))
        self.assertFalse((project / 'media').exists())

    def test_legacy_sequence_manager_refuses_v4_project(self) -> None:
        project = self.init_with_runtime('순서도구테스트')
        argv = ['sequence_manager.py', 'check', '--project', str(project)]
        with mock.patch.object(sys, 'argv', argv):
            with self.assertRaisesRegex(SystemExit, 'V4_REGISTRY_OWNS_ORDER'):
                sequence_manager.main()

    def test_seedance_prompt_must_be_korean_dominant_and_attested(self) -> None:
        pack = self.valid_pack()
        self.assertEqual(prompt_packet_utils.validate_seedance(pack), [])
        bad = {**pack, 'prompt': 'A cinematic camera slowly moves through the street and ends on a face.'}
        self.assertTrue(any('not_korean_dominant' in e for e in prompt_packet_utils.validate_seedance(bad)))
        bad_s2 = {**pack, 'prompt_s2': 'Only English words are used for this alternate prompt.'}
        self.assertTrue(any('prompt_s2_not_korean_dominant' in e for e in prompt_packet_utils.validate_seedance(bad_s2)))

        project = self.init_with_runtime('프롬프트테스트')
        pack = self.pack_with_knowledge(project)
        pack_path = project / 'lanes' / 'seedance' / 'prompts' / 'B01_prompt_pack.json'
        pack_path.parent.mkdir(parents=True, exist_ok=True)
        pack_path.write_text(json.dumps(pack, ensure_ascii=False), encoding='utf-8')
        result = prompt_packet_utils.attest(pack_path, project)
        self.assertEqual(result['verdict'], 'ATTESTED')
        self.assertTrue(Path(result['attestation']).is_file())
        self.assertTrue(result['prompt_language_check']['korean_dominant'])
        self.assertEqual(
            result['knowledge_selection']['selection_id'],
            pack['knowledge_selection_id'])
        self.assertEqual(result['duration_lock']['expected_duration_sec'], 15)

    def test_duration_lock_rejects_drift_and_requires_project_attestation(self) -> None:
        project = self.init_with_runtime('시간잠금테스트')
        pack = self.pack_with_knowledge(project)
        pack_path = project / 'lanes' / 'seedance' / 'prompts' / 'B01_prompt_pack.json'
        pack_path.parent.mkdir(parents=True, exist_ok=True)

        drifted = {**pack, 'duration_sec': 5}
        pack_path.write_text(json.dumps(drifted, ensure_ascii=False), encoding='utf-8')
        rejected = prompt_packet_utils.attest(pack_path, project)
        self.assertEqual(rejected['verdict'], 'NOT_ATTESTED_DO_NOT_SUBMIT')
        self.assertIn(
            'pack_duration_lock_mismatch:expected=15,actual=5', rejected['errors'])

        no_project = prompt_packet_utils.attest(pack_path)
        self.assertEqual(no_project['verdict'], 'NOT_ATTESTED_DO_NOT_SUBMIT')
        self.assertIn('project_required_for_duration_lock', no_project['errors'])

        pack_path.write_text(json.dumps(pack, ensure_ascii=False), encoding='utf-8')
        passed = prompt_packet_utils.attest(pack_path, project)
        self.assertEqual(passed['verdict'], 'ATTESTED')
        self.assertEqual(passed['duration_lock']['pack_duration_sec'], 15)

    def test_planned_multi_shot_source_validates_scene_yield_and_reference_binding(self) -> None:
        pack = self.valid_pack('B_MULTI')
        pack.update({
            'prompt': (
                '@Image1은 인물과 첫 공간의 기준이고 @Image2는 두 번째와 세 번째 공간의 기준이다. '
                '15초 3숏 시퀀스이며 각 숏은 명확한 하드 컷으로 연결된다. '
                '0–5초, 숏 1: 인물이 문을 열고 골목으로 나가며 카메라는 옆으로 따라간다. '
                '5–10초, 숏 2: 시장 입구에서 손을 들어 신호하고 카메라는 낮은 위치에서 앞으로 이동한다. '
                '10–15초, 숏 3: 역 앞 표지판 아래 멈추고 뒤를 돌아보며 카메라는 안정된 중간 구도로 끝난다. '
                '각 장면의 바람과 옷자락, 발걸음 소리는 실제 접촉에 맞춰 자연스럽게 이어진다.'
            ),
            'reference_role_map': [
                {'reference': '@Image1', 'role': '첫 장면 인물과 골목 기준'},
                {'reference': '@Image2', 'role': '두 번째와 세 번째 공간 기준'},
            ],
            'shot_grammar': prompt_packet_utils.MULTI_SHOT_GRAMMAR,
            'planned_scene_count': 3,
            'covered_cuts': ['C01', 'C02', 'C03'],
            'scene_plan': [
                {'scene_id': 'S01', 'start_sec': 0, 'end_sec': 5,
                 'covered_cuts': ['C01'], 'reference_tokens': ['@Image1'],
                 'action': '문을 열고 골목으로 이동', 'camera': '측면 트래킹',
                 'edit_out': '골목 진입 와이드'},
                {'scene_id': 'S02', 'start_sec': 5, 'end_sec': 10,
                 'covered_cuts': ['C02'], 'reference_tokens': ['@Image2'],
                 'action': '시장 입구에서 손 신호', 'camera': '로우 전진',
                 'edit_out': '손 동작 정점'},
                {'scene_id': 'S03', 'start_sec': 10, 'end_sec': 15,
                 'covered_cuts': ['C03'], 'reference_tokens': ['@Image2'],
                 'action': '역 앞에서 뒤돌아봄', 'camera': '안정된 미디엄',
                 'edit_out': '역 표지와 인물 홀드'},
            ],
            'prompt_rules_used': [
                'references_are_anchor_not_cage',
                prompt_packet_utils.MULTIMODAL_BINDING_RULE,
            ],
        })
        self.assertEqual(prompt_packet_utils.validate_seedance(pack), [])

        planner_shortened = {**pack, 'duration_sec': 10}
        errors = prompt_packet_utils.validate_seedance(planner_shortened)
        self.assertTrue(any('multi_shot_source_requires_15s' in e for e in errors))

        bad_scene_plan = json.loads(json.dumps(pack))
        bad_scene_plan['scene_plan'][1]['covered_cuts'] = ['C01']
        bad_scene_plan['scene_plan'][1]['reference_tokens'] = ['@Image9']
        errors = prompt_packet_utils.validate_seedance(bad_scene_plan)
        self.assertIn('multi_shot_duplicate_cut_ownership', errors)
        self.assertTrue(any('unknown_reference_token:@Image9' in e for e in errors))

    def test_duration_lock_source_and_gate_are_non_bypassable(self) -> None:
        project = self.init_with_runtime('시간출처테스트')
        with self.assertRaisesRegex(ValueError, 'DURATION_LOCK_SOURCE_INVALID'):
            generation_settings.lock_duration(project, 15, 'inferred_from_prompt')
        with self.assertRaisesRegex(ValueError, 'SHORTER_DURATION_EXPLICIT_USER_OR_BRIEF_REQUIRED'):
            generation_settings.lock_duration(
                project, 10, 'planner_revision:complexity_inference_not_allowed')

        lock_path = generation_settings.duration_lock_path(project)
        broken = json.loads(lock_path.read_text(encoding='utf-8'))
        broken['status'] = 'NEEDS_LOCK'
        lock_path.write_text(json.dumps(broken), encoding='utf-8')
        allowed, reason = lane_gates.gate_check(project, 'seedance')
        self.assertFalse(allowed)
        self.assertIn('DURATION_LOCK_REQUIRED', reason)

        first = generation_settings.lock_duration(
            project, 15, 'brief:brief.md#provider-duration')
        second = generation_settings.lock_duration(
            project, 10, 'user:conversation_explicit_10s_override')
        self.assertEqual(first['revision'], 2)
        self.assertEqual(second['revision'], 3)
        self.assertEqual(second['revision_history'][-1]['default_duration_sec'], 15)

    def test_knowledge_router_selects_only_matching_bounded_packet(self) -> None:
        project = self.init_with_runtime('지식선별테스트')
        pack = self.pack_with_knowledge(project)
        receipt_path = (
            project / 'lanes' / 'seedance' / 'knowledge' / 'B01_selection.json')
        receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
        selected = [item['id'] for item in receipt['selected']]

        self.assertEqual(pack['knowledge_selected_ids'], selected)
        self.assertEqual(selected[:3], ['core', 'higgsfield-core', 'composition'])
        self.assertIn('core', selected)
        self.assertIn('higgsfield-core', selected)
        self.assertIn('composition', selected)
        self.assertIn('medium-2d', selected)
        self.assertIn('camera-action', selected)
        self.assertNotIn('medium-live', selected)
        self.assertLessEqual(receipt['context_chars'], receipt['budget_chars'])
        self.assertLessEqual(len(selected), 5)
        higgs = next(item for item in receipt['selected'] if item['id'] == 'higgsfield-core')
        self.assertEqual(higgs['priority_class'], 'preferred_higgsfield_community')
        self.assertEqual(higgs['provenance'], 'test_higgsfield_community')

    def test_knowledge_context_tampering_blocks_attestation(self) -> None:
        project = self.init_with_runtime('지식변조테스트')
        pack = self.pack_with_knowledge(project)
        pack_path = project / 'lanes' / 'seedance' / 'prompts' / 'B01_prompt_pack.json'
        pack_path.parent.mkdir(parents=True, exist_ok=True)
        pack_path.write_text(json.dumps(pack, ensure_ascii=False), encoding='utf-8')
        context_path = project / 'lanes' / 'seedance' / 'knowledge' / 'B01_context.md'
        context_path.write_text(
            context_path.read_text(encoding='utf-8') + '\n변조됨\n', encoding='utf-8')

        result = prompt_packet_utils.attest(pack_path, project)

        self.assertEqual(result['verdict'], 'NOT_ATTESTED_DO_NOT_SUBMIT')
        self.assertIn('knowledge_context_file_hash_mismatch', result['errors'])

    def test_image_parallelism_has_hard_cap_three(self) -> None:
        project = self.init_with_runtime('병렬테스트')
        prompt_dir = project / 'lanes' / 'image_creator_01' / 'prompts'
        prompt_dir.mkdir(parents=True, exist_ok=True)
        (prompt_dir / 'C001.prompt.txt').write_text('한 장면 프롬프트', encoding='utf-8')
        self.assertEqual(video_codex_runtime.IMAGE_MAX_PARALLEL, 3)
        with self.assertRaisesRegex(SystemExit, 'IMAGE_WORKER_CAP_EXCEEDED'):
            video_codex_runtime.image_shards_cmd(SimpleNamespace(
                project=str(project), lane='image_creator_01', max_parallel=4))

    def test_shard_fan_in_waits_for_every_expected_worker(self) -> None:
        project = self.init_with_runtime('팬인테스트')
        shards = project / 'lanes' / 'image_creator_01' / 'shards'
        shards.mkdir(parents=True, exist_ok=True)
        (shards / 'orchestrator.json').write_text(json.dumps({
            'shards': [{'shard': 'shard_01'}, {'shard': 'shard_02'}, {'shard': 'shard_03'}]
        }), encoding='utf-8')
        (shards / 'shard_01.status.json').write_text(json.dumps({
            'shard_id': 'shard_01', 'phase': 'complete', 'status': 'DONE',
            'generated_count': 1, 'failure_count': 0,
        }), encoding='utf-8')
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            video_codex_runtime.shards_status_cmd(SimpleNamespace(
                project=str(project), lane='image_creator_01'))
        result = json.loads(output.getvalue())
        self.assertFalse(result['all_done'])
        self.assertNotIn('finalized', result)
        self.assertEqual(len(result['shards']), 3)

    def test_wait_contract_is_state_derived_foreground_only(self) -> None:
        project = self.init_with_runtime('재개테스트')
        pack_path = project / 'lanes' / 'seedance' / 'prompts' / 'B01_prompt_pack.json'
        pack_path.parent.mkdir(parents=True, exist_ok=True)
        pack_path.write_text(
            json.dumps(self.pack_with_knowledge(project), ensure_ascii=False),
            encoding='utf-8')
        prompt_packet_utils.attest(pack_path, project)
        contract = runway_ui_helper.build_resume_contract(project)
        self.assertEqual(contract['delay_seconds'], 900)
        self.assertTrue(contract['same_codex_task_only'])
        self.assertTrue(contract['same_runway_browser_only'])
        self.assertEqual(contract['continuation_mode'], 'FOREGROUND_TOOL_LONG_POLL_ONLY')
        self.assertFalse(contract['automatic_model_reentry'])
        self.assertFalse(contract['external_scheduler'])
        self.assertEqual(contract['additional_agents'], 0)
        self.assertEqual(contract['resident_processes'], 0)
        wait_instruction = contract['wait_return_instruction_ko']
        self.assertLessEqual(len(wait_instruction), 100)
        self.assertNotIn(str(project), wait_instruction)
        self.assertNotIn('B01', wait_instruction)

        contract_path = project / 'lanes' / 'seedance' / 'resume_contract.json'
        contract_path.write_text(json.dumps(contract, ensure_ascii=False), encoding='utf-8')
        status_path = project / 'lanes' / 'seedance' / 'status.json'
        status_path.write_text(json.dumps({
            'status': 'PARTIAL_BLOCKED',
            'terminal_state': 'QUEUE_FULL_WAITING',
            'next_check_scheduled': True,
        }), encoding='utf-8')
        cycle = lane_gates.cycle_status(project)
        self.assertEqual(cycle['verdict'], 'STOPPED_INCOMPLETE')
        self.assertTrue(cycle['resume_contract_valid'])
        self.assertFalse(cycle['pending_wake_valid'])

        runtime = runway_ui_helper.sync_queue_runtime(
            project,
            [
                runway_ui_helper.parse_queue_job('B01|31|GENERATING'),
                runway_ui_helper.parse_queue_job('B02|32|IN_QUEUE'),
            ],
            armed='B03',
            next_eligible='B03',
            shelf_state='AVAILABLE',
            generate_state='GRAY',
        )
        runtime['wake'].update({
            'pending': True,
            'registered_at': '2026-08-18T21:00:00+09:00',
            'due_at': '2026-08-18T21:15:00+09:00',
            'wait_pid': os.getpid(),
            'elapsed_unconsumed': False,
            'last_result': 'WAITING_IN_FOREGROUND_TOOL_SESSION',
        })
        runway_ui_helper._write_json_atomic(
            runway_ui_helper.queue_runtime_path(project), runtime)
        contract = runway_ui_helper.build_resume_contract(project)
        contract_path.write_text(json.dumps(contract, ensure_ascii=False), encoding='utf-8')

        cycle = lane_gates.cycle_status(project)
        self.assertEqual(cycle['verdict'], 'WAITING_FOREGROUND_TOOL_SESSION')
        self.assertTrue(cycle['resume_contract_valid'])
        self.assertTrue(cycle['pending_wake_valid'])

    def test_running_seedance_without_live_owner_is_stopped_incomplete(self) -> None:
        project = self.init_with_runtime('죽은러닝상태테스트')
        runway_ui_helper.sync_queue_runtime(
            project,
            [runway_ui_helper.parse_queue_job('B01|31|IN_QUEUE')],
            armed=None,
            next_eligible=None,
            shelf_state='EXHAUSTED',
            generate_state='GRAY',
        )
        status_path = project / 'lanes' / 'seedance' / 'status.json'
        status_path.write_text(json.dumps({
            'lane': 'seedance',
            'status': 'RUNNING',
            'terminal_state': None,
        }), encoding='utf-8')

        cycle = lane_gates.cycle_status(project)

        self.assertEqual(cycle['verdict'], 'STOPPED_INCOMPLETE')
        self.assertFalse(cycle['owner_alive'])
        self.assertIn('may_stop=false', cycle['problem'])

        status_path.write_text(json.dumps({
            'lane': 'seedance',
            'status': 'PARTIAL_BLOCKED',
            'terminal_state': None,
            'detail': 'BROKEN_FOREGROUND_CONTINUATION',
        }), encoding='utf-8')
        cycle = lane_gates.cycle_status(project)
        self.assertEqual(cycle['verdict'], 'STOPPED_INCOMPLETE')
        self.assertIn('NONTERMINAL_QUEUE_WITHOUT_LIVE_OWNER', cycle['problem'])

    def test_upload_alias_is_ascii_symlink_and_cleanup_is_exact(self) -> None:
        project = self.init_with_runtime('업로드별칭테스트')
        src = self.root / '승인 이미지.png'; src.write_bytes(b'approved-image')
        candidate = media_registry.ingest(
            project, src, kind='image', state='candidate', work_item_id='C010')
        approved = media_registry.promote(project, candidate['asset_id'])
        alias_root = self.root / 'runway-upload'
        prepared = runway_ui_helper.prepare_upload_alias(
            project, approved['asset_id'], '장면 01', 1, alias_root)
        alias = Path(prepared['alias_path'])
        self.assertTrue(alias.is_symlink())
        self.assertEqual(alias.read_bytes(), b'approved-image')
        self.assertTrue(alias.name.isascii())
        self.assertEqual(prepared['canonical_path'], approved['current_path'])
        self.assertEqual(Path(approved['current_path']).read_bytes(), b'approved-image')
        removed = runway_ui_helper.cleanup_upload_alias(alias, alias_root)
        self.assertTrue(removed['removed'])
        self.assertFalse(alias.exists())
        self.assertTrue(Path(approved['current_path']).is_file())

    def test_inactive_work_moves_to_trash_only_after_24_hours(self) -> None:
        project = self.init_with_runtime('정리테스트')
        src = self.root / 'retry.png'; src.write_bytes(b'rejected-retry')
        asset = media_registry.ingest(
            project, src, kind='image', state='candidate', work_item_id='C009')
        rejected = media_registry.set_state(project, asset['asset_id'], 'rejected')
        self.assertIn(media_registry.FOLDERS['work'], rejected['current_path'])
        self.assertEqual(media_registry.cleanup_candidates(project, 24), [])

        old = (dt.datetime.now().astimezone() - dt.timedelta(hours=25)).isoformat(timespec='seconds')
        with sqlite3.connect(media_registry.db_path(project)) as conn:
            conn.execute('UPDATE assets SET updated_at=? WHERE asset_id=?', (old, asset['asset_id']))
        candidates = media_registry.cleanup_candidates(project, 1)
        self.assertEqual(len(candidates), 1)

        fake_trash = self.root / 'Trash'
        with mock.patch.dict(os.environ, {'VIDEO_TEAM_TRASH_ROOT': str(fake_trash)}):
            moved = media_registry.move_candidates_to_trash(project, candidates)
        self.assertEqual(len(moved), 1)
        self.assertTrue(Path(moved[0]['trashed_path']).is_file())
        self.assertFalse(Path(moved[0]['original_path']).exists())
        row = media_registry.get_asset(project, asset['asset_id'])
        self.assertEqual(row['state'], 'trashed')
        self.assertTrue((project / 'cleanup_journal.jsonl').is_file())

    def test_retired_monitor_and_prompt_bridge_are_not_runtime_commands(self) -> None:
        self.assertFalse((SCRIPTS / 'sol_prompt_bridge.py').exists())
        self.assertFalse((SCRIPTS / 'seedance_inflight_monitor.py').exists())
        self.assertFalse((SCRIPTS / 'image_qc_lane_runner.py').exists())
        runway_source = (SCRIPTS / 'runway_ui_helper.py').read_text(encoding='utf-8')
        runtime_source = (SCRIPTS / 'video_codex_runtime.py').read_text(encoding='utf-8')
        self.assertNotIn("sub.add_parser('watch-generate')", runway_source)
        self.assertNotIn("sub.add_parser('observer-instruction')", runway_source)
        self.assertNotIn('seedance-monitor-start', runtime_source)
        self.assertNotIn("if lane.startswith('image_creator_')", runtime_source)
        self.assertNotIn("if lane == 'image_qc'", runtime_source)
        self.assertIn("'image_prompts': 'owning image_creator lane", runtime_source)


if __name__ == '__main__':
    unittest.main()
