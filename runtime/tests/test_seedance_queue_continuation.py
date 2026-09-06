from __future__ import annotations

import importlib.util
import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault('RUNWAY_BROWSER', 'Aside')
os.environ.setdefault('VIDEO_TEAM_RUNTIME_SCRIPTS', str(ROOT / 'runtime' / 'scripts'))
HELPER_PATH = (
    ROOT / 'codex-skills' / 'seedance-prompt-en' / 'scripts' / 'runway_ui_helper.py'
)
SPEC = importlib.util.spec_from_file_location('seedance_queue_helper_test', HELPER_PATH)
assert SPEC and SPEC.loader
helper = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(helper)
import prompt_packet_utils as packets


class SeedanceQueueContinuationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.project = Path(self.temporary.name) / 'legacy-video-project'
        metadata = self.project / 'i2v' / 'seedance'
        metadata.mkdir(parents=True)
        (metadata / 'status.json').write_text(json.dumps({
            'terminal_state': 'IN_PROGRESS',
            'active_queue': [],
            'prepared_shelf': [{'block': 'C01', 'status': 'ATTESTED_READY'}],
        }), encoding='utf-8')
        prompts = metadata / 'prompts'
        prompts.mkdir()
        duration_lock = metadata / 'generation_duration_lock.json'
        duration_lock.write_text(json.dumps({
            'schema_version': 'seedance_generation_duration_lock_v1_20260819',
            'status': 'LOCKED',
            'default_duration_sec': 15,
            'block_overrides': {},
            'source': 'planner_revision:test_fixture_15s_lock',
            'revision': 1,
            'change_policy': helper.generation_settings.CHANGE_POLICY,
            'prompt_complexity_may_change_duration': False,
        }), encoding='utf-8')
        pack = prompts / 'C01_pack.json'
        pack.write_text(json.dumps({
            'block_id': 'C01',
            'duration_sec': 15,
            'shot_grammar': packets.SINGLE_SHOT_GRAMMAR,
            'prompt_language': packets.PROMPT_LANGUAGE,
            'prompt_style_version': packets.SEEDANCE_PROMPT_STYLE_VERSION,
            'authoring_contract': packets.SEEDANCE_AUTHORING_CONTRACT,
            'prompt': '카메라는 골목을 천천히 따라가고 인물이 문을 여는 순간 따뜻한 빛이 바닥으로 번진다. 마지막 프레임은 인물의 안정된 중간 구도로 끝난다.',
            'reference_role_map': [{'reference': '@Image1', 'role': '인물과 공간 기준'}],
            'audio_route': 'Audio ON, 현장음 중심',
            'prompt_rules_used': ['references_are_anchor_not_cage'],
        }), encoding='utf-8')
        (prompts / 'C01_attestation.json').write_text(json.dumps({
            'verdict': 'ATTESTED',
            'block_id': 'C01',
            'prompt_sha256': 'a' * 64,
            'pack': str(pack.resolve()),
            'pack_sha256': hashlib.sha256(pack.read_bytes()).hexdigest(),
            'duration_lock': {
                'path': str(duration_lock.resolve()),
                'sha256': hashlib.sha256(duration_lock.read_bytes()).hexdigest(),
                'expected_duration_sec': 15,
                'pack_duration_sec': 15,
            },
        }), encoding='utf-8')

    def tearDown(self) -> None:
        self.temporary.cleanup()

    @staticmethod
    def jobs(state: str = 'IN_QUEUE') -> list[dict]:
        return [
            helper.parse_queue_job(f'C15|31|{state}'),
            helper.parse_queue_job(f'C16|32|{state}'),
        ]

    def sync(self, jobs: list[dict], **overrides) -> dict:
        values = {
            'armed': 'C17',
            'next_eligible': 'C17',
            'shelf_state': 'AVAILABLE',
            'generate_state': 'GRAY',
            'from_wake': False,
        }
        values.update(overrides)
        return helper.sync_queue_runtime(self.project, jobs, **values)

    def test_old_attested_label_does_not_bypass_current_compiler(self):
        pack=self.project/'i2v/seedance/prompts/C01_pack.json'
        data=json.loads(pack.read_text());data['prompt']='3/4 추적 또는 정면 고정. '+data['prompt']
        pack.write_text(json.dumps(data))
        receipt=pack.with_name('C01_attestation.json');r=json.loads(receipt.read_text())
        r['pack_sha256']=hashlib.sha256(pack.read_bytes()).hexdigest();receipt.write_text(json.dumps(r))
        with self.assertRaisesRegex(ValueError,'CURRENT_PACK_INVALID_REAUTHOR_REQUIRED'):
            helper.verify_attested_generation_settings(self.project,'C01',visible_model='Seedance 2.0',duration_sec=15)

    def test_gray_without_active_cards_does_not_trigger_capacity_wait(self):
        result=self.sync([])
        self.assertFalse(result['wake_required'])
        self.assertIn('Do not click',result['next_action'])

    def test_legacy_resume_contract_uses_legacy_metadata_directory(self) -> None:
        contract = helper.build_resume_contract(self.project)

        self.assertEqual(contract['snapshot']['layout'], 'legacy')
        self.assertEqual(contract['delay_seconds'], 900)
        self.assertEqual(contract['snapshot']['attested_prompt_count'], 1)
        self.assertEqual(
            helper.resume_contract_path(self.project),
            self.project.resolve() / 'i2v' / 'seedance' / 'resume_contract.json',
        )

    def test_visible_duration_must_match_unchanged_attested_lock(self) -> None:
        with self.assertRaisesRegex(ValueError, 'SETTINGS_VISIBLE_DURATION_MISMATCH'):
            helper.verify_attested_generation_settings(
                self.project, 'C01', visible_model='Seedance 2.0', duration_sec=5)

        passed = helper.verify_attested_generation_settings(
            self.project, 'C01', visible_model='Seedance 2.0', duration_sec=15)
        self.assertTrue(passed['ok'])
        self.assertEqual(passed['expected_duration_sec'], 15)
        self.assertEqual(passed['visible_model'], 'Seedance 2.0')
        self.assertEqual(
            passed['verdict'],
            'PASS_SETTINGS_MATCH_SEEDANCE_2_0_AND_ATTESTED_DURATION')
        self.assertTrue(helper.settings_preflight_path(self.project, 'C01').is_file())

        lock_path = self.project / 'i2v' / 'seedance' / 'generation_duration_lock.json'
        lock_path.write_text('{}', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'SETTINGS_DURATION_LOCK_CHANGED'):
            helper.verify_attested_generation_settings(
                self.project, 'C01', visible_model='Seedance 2.0', duration_sec=15)

    def test_visible_seedance_25_is_rejected_before_generate(self) -> None:
        with self.assertRaisesRegex(ValueError, 'SETTINGS_VISIBLE_MODEL_MISMATCH'):
            helper.verify_attested_generation_settings(
                self.project, 'C01',
                visible_model='Video / Seedance 2.5 / Multi-reference',
                duration_sec=15)

        self.assertFalse(helper.settings_preflight_path(self.project, 'C01').exists())

    def test_visible_model_must_be_read_unambiguously(self) -> None:
        for label in ('', 'Seedance', 'Seedance 2.0 / Seedance 2.5'):
            with self.subTest(label=label):
                with self.assertRaisesRegex(
                        ValueError, 'SETTINGS_VISIBLE_MODEL_UNREADABLE_OR_AMBIGUOUS'):
                    helper.verify_attested_generation_settings(
                        self.project, 'C01', visible_model=label, duration_sec=15)

    def test_recovery_checkpoint_refuses_seedance_25_settings(self) -> None:
        v4 = Path(self.temporary.name) / 'v4-project'
        v4.mkdir()
        (v4 / 'manifest.json').write_text(json.dumps({
            'media_schema_version': helper.media_registry.MEDIA_SCHEMA_VERSION,
        }), encoding='utf-8')
        (v4 / 'state.json').write_text('{}', encoding='utf-8')

        with self.assertRaisesRegex(
                ValueError, 'RECOVERY_SETTINGS_VISIBLE_MODEL_MISMATCH'):
            helper.create_recovery_checkpoint(
                v4, 'C01', 'https://app.runwayml.com/video-tools/session/test',
                'ATTACH', prompt_sha256_value='a' * 64,
                reference_manifest_sha256='b' * 64,
                settings={
                    'model': 'Seedance 2.5',
                    'mode': 'Multi-reference',
                    'audio': 'ON',
                    'ratio': '16:9',
                    'resolution': '720p',
                    'duration': '15s',
                })

    def test_existing_seedance_25_checkpoint_cannot_resume(self) -> None:
        v4 = Path(self.temporary.name) / 'v4-existing-project'
        v4.mkdir()
        (v4 / 'manifest.json').write_text(json.dumps({
            'media_schema_version': helper.media_registry.MEDIA_SCHEMA_VERSION,
        }), encoding='utf-8')
        (v4 / 'state.json').write_text('{}', encoding='utf-8')
        helper.create_recovery_checkpoint(
            v4, 'C01', 'https://app.runwayml.com/video-tools/session/test',
            'ATTACH', prompt_sha256_value='a' * 64,
            reference_manifest_sha256='b' * 64,
            settings={
                'model': 'Seedance 2.0',
                'mode': 'Multi-reference',
                'audio': 'ON',
                'ratio': '16:9',
                'resolution': '720p',
                'duration': '15s',
            })
        state_path = helper._recovery_state_path(v4)
        state = json.loads(state_path.read_text(encoding='utf-8'))
        checkpoint = state['checkpoint']
        checkpoint['settings']['model'] = 'Seedance 2.5'
        unsigned = {
            key: value for key, value in checkpoint.items()
            if key != 'checkpoint_sha256'
        }
        checkpoint['checkpoint_sha256'] = helper._hash_payload(unsigned)
        state_path.write_text(json.dumps(state), encoding='utf-8')

        with self.assertRaisesRegex(
                ValueError, 'RECOVERY_SETTINGS_VISIBLE_MODEL_MISMATCH'):
            helper._load_recovery_state(v4)

    def test_one_active_job_never_waits_while_shelf_is_available(self) -> None:
        runtime = self.sync([helper.parse_queue_job('C15|31|GENERATING')])

        self.assertEqual(runtime['verdict'], 'FILL_FREE_SLOT_NOW')
        self.assertFalse(runtime['wake_required'])
        self.assertFalse(runtime['may_stop'])
        with self.assertRaisesRegex(ValueError, 'QUEUE_WAIT_NOT_ALLOWED'):
            helper.run_bounded_queue_wake(self.project, sleeper=lambda _: None)

    def test_one_slot_fallback_requires_exact_toast_and_retries_two_when_empty(self) -> None:
        one = [helper.parse_queue_job('C15|31|GENERATING')]
        with self.assertRaisesRegex(ValueError, 'REQUIRES_TOAST_EVIDENCE'):
            self.sync(one, capacity_limit=1)

        runtime = self.sync(
            one,
            capacity_limit=1,
            capacity_evidence='RUNWAY_QUEUE_CAPACITY_TOAST',
        )
        self.assertEqual(runtime['queue_target'], 1)
        self.assertEqual(runtime['verdict'], 'QUEUE_FULL_WAKE_REQUIRED')

        runtime = self.sync(
            [], armed='C17', next_eligible='C17',
            shelf_state='AVAILABLE')
        self.assertEqual(runtime['queue_target'], 2)
        self.assertEqual(runtime['capacity_evidence'], 'AUTO_RETRY_TWO_AFTER_QUEUE_EMPTY')
        self.assertEqual(runtime['verdict'], 'FILL_FREE_SLOT_NOW')

    def test_two_active_jobs_require_arming_before_wait(self) -> None:
        runtime = self.sync(self.jobs(), armed=None, next_eligible='C17')
        self.assertEqual(runtime['verdict'], 'ARM_NEXT_BEFORE_WAIT')

        runtime = self.sync(self.jobs())
        self.assertEqual(runtime['verdict'], 'QUEUE_FULL_WAKE_REQUIRED')
        self.assertTrue(runtime['wake_required'])
        self.assertFalse(runtime['may_stop'])

    def test_bounded_wake_is_foreground_once_and_returns_recheck(self) -> None:
        self.sync(self.jobs())
        observed_delays: list[int] = []

        result = helper.run_bounded_queue_wake(
            self.project, sleeper=observed_delays.append)

        self.assertEqual(observed_delays, [900])
        self.assertEqual(result['verdict'], 'WAIT_ELAPSED_RECHECK_BOARD_NOW')
        runtime = json.loads(helper.queue_runtime_path(self.project).read_text())
        self.assertFalse(runtime['wake']['pending'])
        self.assertTrue(runtime['wake']['elapsed_unconsumed'])
        self.assertEqual(runtime['wake']['elapsed_count'], 1)
        self.assertEqual(runtime['wake']['consumed_count'], 0)
        self.assertTrue(helper.resume_contract_path(self.project).is_file())

        with self.assertRaisesRegex(ValueError, 'QUEUE_WAIT_ELAPSED_UNCONSUMED'):
            self.sync(self.jobs())
        with self.assertRaisesRegex(ValueError, 'QUEUE_WAIT_ELAPSED_UNCONSUMED'):
            helper.run_bounded_queue_wake(self.project, sleeper=lambda _: None)

        runtime = self.sync(self.jobs(), from_wake=True)
        self.assertFalse(runtime['wake']['elapsed_unconsumed'])
        self.assertEqual(runtime['wake']['consumed_count'], 1)
        self.assertEqual(
            runtime['wake']['last_result'],
            'WAIT_CONSUMED_BY_VISIBLE_BOARD_RECHECK')

    def test_legacy_fired_timer_is_migration_debt_not_automatic_resume(self) -> None:
        runtime = self.sync(self.jobs())
        runtime['wake'].update({
            'pending': False,
            'last_result': 'WAKE_FIRED_RECHECK_BOARD_NOW',
            'fired_count': 2,
        })
        helper._write_json_atomic(helper.queue_runtime_path(self.project), runtime)

        with self.assertRaisesRegex(ValueError, 'QUEUE_WAIT_ELAPSED_UNCONSUMED'):
            self.sync(self.jobs())
        consumed = self.sync(self.jobs(), from_wake=True)
        self.assertEqual(consumed['wake']['consumed_count'], 1)
        self.assertEqual(
            consumed['wake']['last_result'],
            'WAIT_CONSUMED_BY_VISIBLE_BOARD_RECHECK')

    def test_active_queue_drains_even_when_shelf_is_exhausted(self) -> None:
        runtime = self.sync(
            [helper.parse_queue_job('C78|71|PROCESSING')],
            armed=None,
            next_eligible=None,
            shelf_state='EXHAUSTED',
        )
        self.assertEqual(runtime['verdict'], 'DRAIN_QUEUE_WAKE_REQUIRED')
        self.assertTrue(runtime['wake_required'])
        self.assertFalse(runtime['may_stop'])

        runtime = self.sync(
            [], armed=None, next_eligible=None, shelf_state='EXHAUSTED')
        self.assertEqual(runtime['verdict'], 'SHELF_EXHAUSTED')
        self.assertTrue(runtime['may_stop'])

    def test_completed_card_refills_free_slot_before_backlog_processing(self) -> None:
        runtime = self.sync([
            helper.parse_queue_job('C15|31|GENERATING'),
            helper.parse_queue_job('C16|32|COMPLETED'),
        ])
        self.assertEqual(runtime['verdict'], 'FILL_FREE_SLOT_NOW')
        self.assertFalse(runtime['wake_required'])
        self.assertFalse(runtime['may_stop'])

        runtime = self.sync([
            helper.parse_queue_job('C15|31|GENERATING'),
            helper.parse_queue_job('C17|33|IN_QUEUE'),
            helper.parse_queue_job('C16|32|COMPLETED'),
        ], armed='C18', next_eligible='C18')
        self.assertEqual(runtime['verdict'], 'PROCESS_SETTLED_CARD_NOW')
        self.assertEqual(runtime['settled_backlog_count'], 1)

    def test_processed_settled_receipt_prevents_infinite_backlog_loop(self) -> None:
        jobs = [
            helper.parse_queue_job('C15|31|GENERATING'),
            helper.parse_queue_job('C17|33|IN_QUEUE'),
            helper.parse_queue_job('C16|32|COMPLETED'),
        ]
        runtime = self.sync(
            jobs,
            armed='C18', next_eligible='C18',
            processed_jobs=[helper.parse_processed_job('C16|32')],
        )
        self.assertEqual(runtime['settled_backlog_count'], 0)
        self.assertEqual(len(runtime['processed_settled_jobs']), 1)
        self.assertEqual(runtime['verdict'], 'QUEUE_FULL_WAKE_REQUIRED')

        runtime = self.sync(jobs, armed='C18', next_eligible='C18')
        self.assertEqual(runtime['settled_backlog_count'], 0)
        self.assertEqual(runtime['verdict'], 'QUEUE_FULL_WAKE_REQUIRED')

        with self.assertRaisesRegex(ValueError, 'NOT_VISIBLE_SETTLED'):
            self.sync(
                jobs,
                armed='C18', next_eligible='C18',
                processed_jobs=[helper.parse_processed_job('MISSING|99')],
            )

    def test_queue_cycle_atomically_enters_required_foreground_wait(self) -> None:
        observed_delays: list[int] = []
        result = helper.run_queue_cycle(
            self.project,
            self.jobs(),
            armed='C17',
            next_eligible='C17',
            shelf_state='AVAILABLE',
            generate_state='GRAY',
            from_wake=False,
            processed_jobs=[],
            sleeper=observed_delays.append,
        )
        self.assertTrue(result['wait_started'])
        self.assertEqual(observed_delays, [900])
        self.assertEqual(result['verdict'], 'WAIT_ELAPSED_RECHECK_BOARD_NOW')

        observed_delays.clear()
        result = helper.run_queue_cycle(
            self.project,
            self.jobs(),
            armed='C17',
            next_eligible='C17',
            shelf_state='AVAILABLE',
            generate_state='GRAY',
            from_wake=True,
            processed_jobs=[],
            sleeper=observed_delays.append,
        )
        self.assertTrue(result['wait_started'])
        self.assertEqual(observed_delays, [900])

    def test_status_attested_blocks_cannot_be_hidden_as_all_blocked(self) -> None:
        status_path = self.project / 'i2v' / 'seedance' / 'status.json'
        status = json.loads(status_path.read_text(encoding='utf-8'))
        status['attested_blocks'] = ['C17', 'C18']
        status_path.write_text(json.dumps(status), encoding='utf-8')

        with self.assertRaisesRegex(ValueError, 'QUEUE_SHELF_CONTRADICTS_ATTESTED_STATUS'):
            self.sync(
                [], armed=None, next_eligible=None,
                shelf_state='ALL_BLOCKED')

        runtime = self.sync(
            [], armed='C17', next_eligible='C17', shelf_state='AVAILABLE')
        self.assertEqual(runtime['verdict'], 'FILL_FREE_SLOT_NOW')

    def test_three_unchanged_in_queue_wakes_stop_rearming(self) -> None:
        runtime = self.sync(self.jobs())
        self.assertEqual(runtime['unchanged_in_queue_wakes'], 0)

        for expected in (1, 2, 3):
            helper.run_bounded_queue_wake(self.project, sleeper=lambda _: None)
            runtime = self.sync(self.jobs(), from_wake=True)
            self.assertEqual(runtime['unchanged_in_queue_wakes'], expected)

        self.assertEqual(runtime['verdict'], 'BLOCKED_RUNWAY_QUEUE_STALLED')
        self.assertTrue(runtime['may_stop'])
        with self.assertRaisesRegex(ValueError, 'QUEUE_WAIT_NOT_ALLOWED'):
            helper.run_bounded_queue_wake(self.project, sleeper=lambda _: None)

    def test_exit_check_refuses_after_first_consumed_wake(self) -> None:
        self.sync(self.jobs())
        helper.run_bounded_queue_wake(self.project, sleeper=lambda _: None)
        runtime = self.sync(self.jobs(), from_wake=True)
        self.assertEqual(runtime['unchanged_in_queue_wakes'], 1)
        result = helper.evaluate_queue_exit(self.project)
        self.assertFalse(result['ok'])
        self.assertEqual(result['verdict'], 'QUEUE_EXIT_REFUSED_NONTERMINAL')
        self.assertIn('queue-cycle', result['next_action'])

    def test_exit_check_allows_only_terminal_queue_state(self) -> None:
        self.sync(
            [], armed=None, next_eligible=None, shelf_state='EXHAUSTED')
        result = helper.evaluate_queue_exit(self.project)
        self.assertTrue(result['ok'])
        self.assertEqual(result['verdict'], 'QUEUE_EXIT_ALLOWED')

    def prebinding_block(self) -> Path:
        metadata = self.project / 'i2v' / 'seedance'
        (metadata / 'status.json').write_text(json.dumps({
            'status': 'BLOCKED', 'production_started': False, 'provider_jobs': [],
            'attested_blocks': ['C01'], 'blocked_attested_blocks': ['C01'],
            'preproduction_block': {
                'code': 'BLOCKED_RUNWAY_SESSION_SELECTION_REQUIRED',
                'evidence': 'New project; existing tab belongs to a different project; no binding or Generate.',
                'required_user_action': 'Identify the intended same-tab session.',
            },
        }))
        return metadata

    def test_prebinding_human_action_stop_is_not_fake_queue_observation(self) -> None:
        self.prebinding_block()
        result = helper.evaluate_queue_exit(self.project)
        self.assertTrue(result['ok'])
        self.assertFalse(result['queue_observation'])
        self.assertFalse(helper.queue_runtime_path(self.project).exists())

    def test_prebinding_stop_refuses_corrupt_queue_or_production_evidence(self) -> None:
        metadata = self.prebinding_block()
        paths = ['queue_runtime.json', 'aside_binding.json', 'recovery_state.json',
                 'recovery_events.jsonl', 'recovery/C01.json',
                 'evidence/C01_settings_preflight.json']
        for name in paths:
            with self.subTest(name=name):
                path = metadata / name; path.parent.mkdir(exist_ok=True)
                path.write_text('corrupt')
                self.assertFalse(helper.evaluate_queue_exit(self.project)['ok'])
                path.unlink()

    def test_prebinding_stop_requires_all_explicit_evidence(self) -> None:
        for field, value in [('production_started', True), ('provider_jobs', ['C01']),
                             ('blocked_attested_blocks', []), ('status', 'READY_FOR_PRODUCTION'),
                             ('preproduction_block', {})]:
            with self.subTest(field=field):
                metadata = self.prebinding_block(); path = metadata / 'status.json'
                status = json.loads(path.read_text()); status[field] = value
                path.write_text(json.dumps(status))
                self.assertFalse(helper.evaluate_queue_exit(self.project)['ok'])

    def test_prebinding_label_cannot_override_active_queue(self) -> None:
        self.sync(self.jobs())
        self.prebinding_block()
        self.assertFalse(helper.evaluate_queue_exit(self.project)['ok'])


if __name__ == '__main__':
    unittest.main()
