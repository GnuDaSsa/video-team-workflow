import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import test_seedance_queue_continuation as fixtures

h = fixtures.helper


class ScheduledQueueChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.project = Path(self.tmp.name)
        self.meta = self.project / 'i2v/seedance'
        self.meta.mkdir(parents=True)
        (self.meta / 'status.json').write_text('{}')
        self.evidence = self.meta / 'user-request.md'
        self.evidence.write_text('User requests one 20-minute scheduled check instead of attached waiting.')
        self.jobs = [h.parse_queue_job('B01|first|IN_QUEUE'), h.parse_queue_job('B02|second|IN_QUEUE')]
        self.kw = dict(armed=None, next_eligible=None, shelf_state='EXHAUSTED', generate_state='GRAY')

    def tearDown(self):
        self.tmp.cleanup()

    def select(self):
        return h.select_queue_mode(self.project, 'scheduled', self.evidence, 20)

    def test_two_slots_scheduled_cycle_never_sleeps_or_registers(self):
        receipt = self.select()
        with mock.patch.object(h, 'run_bounded_queue_wake', side_effect=AssertionError('must not wait')):
            for _ in range(2):
                result = h.run_queue_cycle(self.project, self.jobs, **self.kw)
                self.assertEqual(result['verdict'], 'SCHEDULED_CHECKPOINT_NO_WAIT')
                self.assertFalse(result['wait_started'])
                self.assertFalse(result['registration_verified'])
                self.assertEqual(result['queue_runtime']['queue_target'], 2)
                self.assertEqual(result['queue_runtime']['active_count'], 2)
        self.assertFalse(receipt['scheduler_created'])
        self.assertFalse(h.resume_contract_path(self.project).exists())

    def test_direct_wait_cannot_bypass_scheduled_selection(self):
        self.select()
        with self.assertRaisesRegex(ValueError, 'SCHEDULED_MODE_FORBIDS'):
            h.run_bounded_queue_wake(self.project, sleeper=lambda _: self.fail('slept'))

    def test_live_foreground_wait_blocks_mode_change(self):
        h.sync_queue_runtime(self.project, self.jobs, **self.kw)
        path = h.queue_runtime_path(self.project)
        data = json.loads(path.read_text()); data['wake'].update(pending=True, wait_pid=os.getpid())
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'STILL_RUNNING'):
            self.select()
        self.assertFalse(h.queue_mode_path(self.project).exists())

    def test_changed_or_corrupt_selection_never_falls_back_to_foreground(self):
        self.select(); self.evidence.write_text('changed')
        with self.assertRaisesRegex(ValueError, 'EVIDENCE_CHANGED'):
            h.run_queue_cycle(self.project, self.jobs, **self.kw)
        self.assertFalse(h.queue_runtime_path(self.project).exists())
        h.queue_mode_path(self.project).write_text('{}')
        with self.assertRaisesRegex(ValueError, 'QUEUE_MODE_INVALID'):
            h.run_bounded_queue_wake(self.project)

    def test_missing_or_outside_request_evidence_is_rejected(self):
        for path in [self.project / 'missing', Path(__file__)]:
            with self.assertRaisesRegex(ValueError, 'REQUEST_EVIDENCE_REQUIRED'):
                h.select_queue_mode(self.project, 'scheduled', path)

    def test_existing_scheduled_request_cannot_silently_use_legacy_default(self):
        (self.meta / 'status.json').write_text(json.dumps({'monitoring': {'mode': 'SCHEDULED_CHECK_REQUESTED'}}))
        with self.assertRaisesRegex(ValueError, 'SCHEDULED_REQUEST_REQUIRES'):
            h.run_queue_cycle(self.project, self.jobs, **self.kw)
        self.select()
        self.assertFalse(h.run_queue_cycle(self.project, self.jobs, **self.kw)['wait_started'])

    def test_scheduled_checkpoint_exit_is_not_production_completion(self):
        self.select(); h.run_queue_cycle(self.project, self.jobs, **self.kw)
        result = h.evaluate_queue_exit(self.project)
        self.assertTrue(result['ok'])
        self.assertFalse(result['production_complete'])
        self.assertFalse(result['registration_verified'])
        self.assertEqual(result['active_count'], 2)

    def test_completed_cards_remain_download_backlog(self):
        self.select()
        jobs = [{**j, 'visible_state': 'COMPLETED'} for j in self.jobs]
        result = h.run_queue_cycle(self.project, jobs, **self.kw)
        self.assertEqual(result['queue_runtime']['settled_backlog_count'], 2)
        audit = h.audit_production_state(self.project)
        self.assertEqual(audit['ui_completed_cards'], 2)
        self.assertEqual(audit['verified_local_video_files'], 0)
        self.assertFalse(audit['playback_qc_verified_by_this_audit'])

    def test_interrupted_wait_is_consumed_without_restarting(self):
        h.sync_queue_runtime(self.project, self.jobs, **self.kw)
        p = h.queue_runtime_path(self.project); data = json.loads(p.read_text())
        data['wake'].update(elapsed_unconsumed=True, last_result='INTERRUPTED_RECHECK_REQUIRED')
        p.write_text(json.dumps(data)); self.select()
        self.assertFalse(h.evaluate_queue_exit(self.project)['ok'])
        result = h.run_queue_cycle(self.project, self.jobs, from_wake=True, **self.kw)
        self.assertFalse(result['wait_started'])
        self.assertFalse(result['queue_runtime']['wake']['elapsed_unconsumed'])

    def test_arbitrary_may_stop_cannot_hide_active_foreground_queue(self):
        h.sync_queue_runtime(self.project, self.jobs, **self.kw)
        p = h.queue_runtime_path(self.project); data = json.loads(p.read_text()); data['may_stop'] = True
        p.write_text(json.dumps(data))
        self.assertFalse(h.evaluate_queue_exit(self.project)['ok'])

    def test_live_wait_prevents_even_scheduled_or_interrupted_exit(self):
        self.select(); h.run_queue_cycle(self.project, self.jobs, **self.kw)
        p = h.queue_runtime_path(self.project); data = json.loads(p.read_text())
        data.update(may_stop=True, verdict='BROKEN_FOREGROUND_CONTINUATION', interruption={
            'code': 'BROKEN_FOREGROUND_CONTINUATION', 'at': 'now', 'evidence': 'user request'})
        data['wake'].update(pending=True, wait_pid=os.getpid())
        p.write_text(json.dumps(data))
        self.assertFalse(h.evaluate_queue_exit(self.project)['ok'])

    def test_model_change_does_not_change_scheduled_doctor_or_write(self):
        self.select(); h.run_queue_cycle(self.project, self.jobs, **self.kw)
        before = {str(p): p.read_bytes() for p in self.project.rglob('*') if p.is_file()}
        results = []
        for model in ['gpt-5.6-luna', 'gpt-5.6-terra', 'gpt-6-astra']:
            with mock.patch.dict(os.environ, {'CODEX_MODEL': model}):
                results.append(h.diagnose_queue(self.project))
        self.assertEqual(results[0], results[1]); self.assertEqual(results[1], results[2])
        self.assertEqual(results[0]['diagnosis'], 'SCHEDULED_CHECK_SELECTED')
        self.assertEqual(results[0]['interval_seconds'], 1200)
        self.assertEqual(before, {str(p): p.read_bytes() for p in self.project.rglob('*') if p.is_file()})

    def test_audit_flags_stale_rollups_and_unsupported_schedule_claim(self):
        h.sync_queue_runtime(self.project, self.jobs, **self.kw)
        (self.project / 'state.json').write_text(json.dumps({'lanes': {'seedance': {'status': 'DONE'}}}))
        (self.meta / 'status.json').write_text(json.dumps({
            'status': 'IN_PROGRESS', 'blocker': {'code': 'BLOCKED_NATIVE_FILE_SELECTION'},
            'monitoring': {'registration_status': 'ACTIVE', 'scheduled_run_verified': True}}))
        issues = h.audit_production_state(self.project)['issues']
        for code in ['QUEUE_JOB_STATE_MISMATCH:lane', 'STALE_PRE_GENERATION_BLOCKER:lane',
                     'LANE_STATUS_ROLLUP_MISMATCH', 'PRODUCTION_DONE_WITHOUT_REGISTERED_VIDEO',
                     'SCHEDULE_RUN_CLAIM_WITHOUT_AUTOMATION_ID', 'SCHEDULE_REGISTRATION_CLAIM_WITHOUT_RECEIPT']:
            self.assertIn(code, issues)

    def test_native_heartbeat_shape_cannot_fall_back_to_sleep(self):
        (self.meta / 'status.json').write_text(json.dumps({'monitoring': {
            'kind': 'heartbeat', 'status': 'ACTIVE', 'automation_id': 'test-only'}}))
        before = (self.meta / 'status.json').read_bytes()
        with self.assertRaisesRegex(ValueError, 'SCHEDULED_REQUEST_REQUIRES'):
            h.run_queue_cycle(self.project, self.jobs, **self.kw,
                              sleeper=lambda _: self.fail('slept'))
        self.assertFalse(h.queue_runtime_path(self.project).exists())
        result = h.diagnose_queue(self.project)
        self.assertFalse(result['ok'])
        self.assertEqual(result['diagnosis'], 'CONTINUATION_SELECTION_REQUIRED')
        self.assertIn('SCHEDULE_INTENT_WITHOUT_MODE_CHECKPOINT', result['state_audit']['issues'])
        self.assertEqual(before, (self.meta / 'status.json').read_bytes())
        self.select()
        self.assertFalse(h.run_queue_cycle(self.project, self.jobs, **self.kw)['wait_started'])

    def test_native_claim_requires_receipt_even_with_status_alias(self):
        monitoring = {'kind': 'heartbeat', 'status': 'ACTIVE', 'automation_id': 'test-only'}
        (self.meta / 'status.json').write_text(json.dumps({'monitoring': monitoring}))
        self.assertIn('SCHEDULE_REGISTRATION_CLAIM_WITHOUT_RECEIPT',
                      h.audit_production_state(self.project)['issues'])
        monitoring['registration_evidence'] = str(self.evidence)
        (self.meta / 'status.json').write_text(json.dumps({'monitoring': monitoring}))
        audit = h.audit_production_state(self.project)
        self.assertNotIn('SCHEDULE_REGISTRATION_CLAIM_WITHOUT_RECEIPT', audit['issues'])
        self.assertFalse(audit['native_schedule_registration_verified_by_this_audit'])

    def test_inactive_or_non_scheduler_status_does_not_invent_active_schedule(self):
        for monitoring in [{'kind': 'heartbeat', 'status': 'PAUSED'},
                           {'kind': 'foreground', 'status': 'ACTIVE'}]:
            (self.meta / 'status.json').write_text(json.dumps({'monitoring': monitoring}))
            self.assertEqual(h.read_queue_mode(self.project)['source'], 'legacy_default')
            self.assertNotIn('SCHEDULE_REGISTRATION_CLAIM_WITHOUT_RECEIPT',
                             h.audit_production_state(self.project)['issues'])

    def test_explicit_mode_still_wins_over_old_native_status(self):
        (self.meta / 'status.json').write_text(json.dumps({'monitoring': {
            'kind': 'heartbeat', 'status': 'ACTIVE'}}))
        h.select_queue_mode(self.project, 'foreground', self.evidence)
        self.assertEqual(h.read_queue_mode(self.project)['mode'], 'foreground')

    def test_processed_cards_still_detect_nested_current_rollup_mapping(self):
        completed = [{**j, 'visible_state': 'COMPLETED'} for j in self.jobs]
        h.sync_queue_runtime(self.project, completed, **self.kw, processed_jobs=completed)
        h.sync_queue_runtime(self.project, [], **self.kw)
        stale = [{'scene_id': 'B01', 'output_index': 'second', 'visible_state': 'IN_QUEUE'},
                 {'scene_id': 'B02', 'output_index': 'first', 'visible_state': 'IN_QUEUE'}]
        root = {'lanes': {'seedance': {'current_test_queue_rollup': {'jobs': stale}}}}
        (self.project / 'state.json').write_text(json.dumps(root))
        code = 'CURRENT_QUEUE_ROLLUP_MISMATCH:state.lanes.seedance.current_test_queue_rollup'
        self.assertIn(code, h.audit_production_state(self.project)['issues'])
        root['lanes']['seedance']['current_test_queue_rollup']['jobs'] = completed
        (self.project / 'state.json').write_text(json.dumps(root))
        self.assertNotIn(code, h.audit_production_state(self.project)['issues'])

    def test_archive_and_unknown_scene_are_not_current_rollup_errors(self):
        h.sync_queue_runtime(self.project, self.jobs, **self.kw)
        (self.project / 'state.json').write_text(json.dumps({
            'history_queue_rollup': {'jobs': [{'scene_id': 'B01', 'output_index': 'wrong'}]},
            'current_test_queue_rollup': {'jobs': [{'scene_id': 'NEW', 'output_index': 'unseen'}]}}))
        self.assertFalse(any(x.startswith('CURRENT_QUEUE_ROLLUP_MISMATCH')
                             for x in h.audit_production_state(self.project)['issues']))

    def test_missing_mode_doctor_does_not_mutate_any_project_file(self):
        h.sync_queue_runtime(self.project, self.jobs, **self.kw)
        (self.meta / 'status.json').write_text(json.dumps({'monitoring': {
            'kind': 'heartbeat', 'status': 'ACTIVE', 'automation_id': 'test-only'}}))
        before = {str(p): p.read_bytes() for p in self.project.rglob('*') if p.is_file()}
        with mock.patch.object(h, 'run_bounded_queue_wake', side_effect=AssertionError('must not wait')):
            result = h.diagnose_queue(self.project)
        self.assertFalse(result['scheduler_created'])
        self.assertEqual(before, {str(p): p.read_bytes() for p in self.project.rglob('*') if p.is_file()})


if __name__ == '__main__':
    unittest.main()
