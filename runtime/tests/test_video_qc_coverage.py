import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import video_qc_coverage as q


class VideoQcCoverageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name)
        self.evidence = self.project / 'observed.txt'
        self.evidence.write_text('Test-only operator observation, not real playback proof.')
        self.source = dict(asset_id='TEST', sha256='a' * 64, duration_seconds=15, has_audio=True)
        self.report = {'verdict': 'HOLD', 'coverage': {'version': 1,
                       'asset_id': 'TEST', 'source_sha256': 'a' * 64,
                       'checks': [self.row('geometry', 'native_frames', [11, 13])]}}

    def row(self, key, method, span, outcome='pass'):
        return dict(check_id=key, method=method, range_seconds=span, status='resolved',
                    outcome=outcome, finding='Observed fixture finding.', evidence=[{
                        'path': str(self.evidence), 'sha256': q.media_registry.sha256(self.evidence)}])

    def audit(self, **kw):
        return q.audit_coverage(self.report, self.source, self.project, **kw)

    def test_native_all_frames_never_counts_as_playback_or_audio(self):
        self.report['coverage']['checks'][0]['range_seconds'] = [0, 15]
        self.report['verdict'] = 'PASS'
        result = self.audit()
        self.assertTrue(result['ok'])
        self.assertFalse(result['declarations_sufficient_for_manual_gate'])
        self.assertIn('QC_FULL_SPEED_VIDEO_REVIEW_MISSING', result['promotion_blockers'])
        self.assertIn('QC_AUDIO_REVIEW_MISSING', result['promotion_blockers'])
        self.assertFalse(result['perception_verified_by_this_check'])
        self.assertFalse(result['media_promoted'])

    def test_resolved_interval_reuses_evidence_unless_explicit_reopen(self):
        request = dict(check_id='geometry', method='native_frames', range_seconds=[11.5, 12.5])
        self.assertEqual(self.audit(request=request)['action'], 'REUSE_EXISTING_REVIEW')
        request['reopen_reason'] = 'New depth-plane hypothesis, inspect near/far rim.'
        self.assertEqual(self.audit(request=request)['action'], 'REOPEN_WITH_EXPLICIT_REASON')
        request.pop('reopen_reason')
        request['method'] = 'full_speed_video'
        self.assertNotEqual(self.audit(request=request)['action'], 'REUSE_EXISTING_REVIEW')

    def test_changed_source_or_evidence_cannot_reuse_review(self):
        source = {**self.source, 'sha256': 'b' * 64}
        with self.assertRaisesRegex(ValueError, 'SOURCE_CHANGED'):
            q.audit_coverage(self.report, source, self.project)
        self.evidence.write_text('Changed observation')
        result = self.audit(request=dict(check_id='geometry', method='native_frames', range_seconds=[11, 13]))
        self.assertFalse(result['ok'])
        self.assertEqual(result['action'], 'REPAIR_EVIDENCE_BINDING')

    def test_pending_and_blocked_checks_select_actual_remaining_work(self):
        rows = self.report['coverage']['checks']
        rows.extend([
            dict(check_id='sound', method='audio', range_seconds=[0, 15],
                 status='blocked', reason='Audio-capable listening unavailable'),
            dict(check_id='hands', method='native_frames', range_seconds=[4, 6], status='pending')])
        self.assertEqual(self.audit()['next_check']['check_id'], 'hands')
        rows[-1] = self.row('hands', 'native_frames', [4, 6], outcome='fail')
        rows.append(self.row('playback', 'full_speed_video', [0, 15]))
        result = self.audit()
        self.assertEqual(result['action'], 'BLOCKED_REQUIRES_EXTERNAL_ACTION')
        self.assertIsNone(result['next_check'])
        self.assertIn('QC_CREATIVE_FAIL_OR_HOLD', result['promotion_blockers'])

    def test_mandatory_review_returns_only_uncovered_interval(self):
        self.report['coverage']['checks'].extend([
            self.row('playback-start', 'full_speed_video', [0, 5]),
            self.row('playback-end', 'full_speed_video', [10, 15])])
        self.assertEqual(self.audit()['next_check']['range_seconds'], [5, 10])
        self.report['coverage']['checks'].append(self.row('playback-mid', 'full_speed_video', [5, 10]))
        self.assertEqual(self.audit()['next_check']['method'], 'audio')

    def test_complete_declarations_are_not_automatic_approval(self):
        self.report['coverage']['checks'].extend([
            self.row('playback', 'full_speed_video', [0, 15]),
            self.row('listening', 'user_audio_approval', [0, 15])])
        self.report['verdict'] = 'PASS'
        result = self.audit()
        self.assertTrue(result['declarations_sufficient_for_manual_gate'])
        self.assertFalse(result['perception_verified_by_this_check'])
        self.assertFalse(result['media_promoted'])
        self.report['verdict'] = 'EDIT_TRIM_ONLY'
        self.assertFalse(self.audit()['declarations_sufficient_for_manual_gate'])

    def test_invalid_or_legacy_coverage_never_invents_review(self):
        with self.assertRaisesRegex(ValueError, 'BINDING_REQUIRED'):
            q.audit_coverage({'final_pass': True}, self.source, self.project)
        for span in ([4, 4], [-1, 2], [0, 16], [True, 2], [0, float('nan')]):
            with self.assertRaises(ValueError):
                q.interval(span, 15)
        self.report['coverage']['checks'].append(copy.deepcopy(self.report['coverage']['checks'][0]))
        with self.assertRaisesRegex(ValueError, 'DUPLICATE'):
            self.audit()

    def test_no_audio_stream_and_read_only_audit(self):
        self.source['has_audio'] = False
        before = json.dumps(self.report, sort_keys=True)
        files = {str(p): p.read_bytes() for p in self.project.rglob('*') if p.is_file()}
        result = self.audit()
        self.assertTrue(result['audio_coverage_declared'])
        self.assertEqual(json.dumps(self.report, sort_keys=True), before)
        self.assertEqual(files, {str(p): p.read_bytes() for p in self.project.rglob('*') if p.is_file()})

    def test_missing_registry_does_not_create_database(self):
        with self.assertRaisesRegex(ValueError, 'QC_REGISTRY_MISSING'):
            q.registered_source(self.project, 'TEST')
        self.assertFalse(q.media_registry.db_path(self.project).exists())

    def test_external_or_missing_evidence_never_qualifies(self):
        row = self.report['coverage']['checks'][0]
        row['evidence'][0]['path'] = str(Path(__file__).resolve())
        row['evidence'][0]['sha256'] = q.media_registry.sha256(Path(__file__))
        self.assertFalse(self.audit()['ok'])
        row['evidence'][0]['path'] = str(self.project / 'missing.jpg')
        self.assertFalse(self.audit()['ok'])

    def test_complete_fail_disposition_is_not_endless_reinspection(self):
        self.report['coverage']['checks'][0]['outcome'] = 'fail'
        self.report['coverage']['checks'].extend([
            self.row('playback', 'full_speed_video', [0, 15]),
            self.row('sound', 'audio', [0, 15])])
        result = self.audit()
        self.assertEqual(result['action'], 'DISPOSITION_COMPLETE')
        self.assertIsNone(result['next_check'])
        self.assertFalse(result['declarations_sufficient_for_manual_gate'])


if __name__ == '__main__':
    unittest.main()
