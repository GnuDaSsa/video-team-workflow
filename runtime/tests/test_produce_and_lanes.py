"""produce loop, browser/local lane slots, provider hold, dead-session transition (2026-11-11)."""
import contextlib
import datetime as dt
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import lane_sessions  # noqa: E402
import video_codex_runtime as vcr  # noqa: E402


class FakeClock:
    def __init__(self):
        self.t = dt.datetime(2026, 11, 11, 10, 0, 0)
        self.slept = 0.0

    def now(self):
        return self.t

    def sleep(self, seconds):
        self.slept += seconds
        self.t += dt.timedelta(seconds=seconds)


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.project = self.root / 'p1'
        (self.project / 'lanes' / 'seedance').mkdir(parents=True)
        (self.project / 'queues').mkdir()
        self.state = {'provider_jobs': []}
        self.save_state()
        self.hold = self.root / 'PROVIDER_HOLD.json'
        patches = [mock.patch.object(lane_sessions, 'HOLD_PATH', self.hold),
                   mock.patch.object(vcr, 'DISPATCH_LOCK', self.root / '.dispatch.lock')]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

    def tearDown(self):
        self.tmp.cleanup()

    def save_state(self):
        (self.project / 'state.json').write_text(json.dumps(self.state), encoding='utf-8')


class LaneResourceTests(Base):
    def test_owner_resource_classes(self):
        self.assertEqual(vcr.owner_resource('seedance', 'production'), 'browser')
        self.assertEqual(vcr.owner_resource('seedance', 'prompting'), 'local')
        self.assertEqual(vcr.owner_resource('music', 'lane'), 'browser')
        self.assertEqual(vcr.owner_resource('image_qc', 'lane'), 'local')
        self.assertEqual(vcr.owner_resource('seedance_qc', None), 'local')

    def _dispatch(self, lane, phase, owners):
        codex = self.root / 'codex'
        codex.write_text('')
        other = self.root / 'p2'
        with mock.patch.object(vcr, 'CODEX', codex), \
                mock.patch.object(vcr, 'lane_phase', return_value=phase), \
                mock.patch.object(vcr.lane_sessions, 'load_policy', return_value={'recorded_at': 'x'}), \
                mock.patch.object(vcr, 'project_dirs', return_value=[other]), \
                mock.patch.object(vcr, 'active_lane_owners', side_effect=lambda p: owners if p == other else []), \
                mock.patch.object(vcr.lane_gates, 'gate_check', return_value=(False, 'TEST_STOP')), \
                mock.patch.object(vcr.lane_gates, 'non_bypassable_reason', return_value='TEST_STOP'):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                vcr.dispatch(SimpleNamespace(project=str(self.project), lanes=[lane], phase='auto'))
            return json.loads(out.getvalue())

    def test_second_browser_lane_is_refused_but_local_lane_runs(self):
        music = [{'lane': 'music', 'pid': 1, 'phase': 'lane'}]
        with self.assertRaises(SystemExit) as cm:
            self._dispatch('seedance', 'production', music)
        self.assertIn('SEQUENTIAL_OWNER_EXISTS', str(cm.exception))
        # a local lane passes the owner check (and stops at the stubbed gate)
        out = self._dispatch('image_qc', None, music)
        self.assertEqual(out['skipped'][0]['reason'], 'TEST_STOP')

    def test_second_local_lane_is_refused(self):
        qc = [{'lane': 'seedance_qc', 'pid': 1, 'phase': 'lane'}]
        with self.assertRaises(SystemExit) as cm:
            self._dispatch('image_qc', None, qc)
        self.assertIn('local lane owner', str(cm.exception))

    def test_hold_refuses_browser_lanes_only(self):
        lane_sessions.write_hold('ACCOUNT_WARNING', self.project, 'Are you using an autoclicker?')
        with self.assertRaises(SystemExit) as cm:
            self._dispatch('seedance', 'production', [])
        self.assertIn('PROVIDER_HOLD', str(cm.exception))
        self.assertEqual(self._dispatch('image_qc', None, [])['skipped'][0]['reason'], 'TEST_STOP')

    def test_unreadable_hold_still_holds_and_lane_cannot_clear(self):
        self.hold.write_text('{', encoding='utf-8')
        self.assertEqual(lane_sessions.hold_active()['reason'], 'UNREADABLE_HOLD_FILE')
        with mock.patch.dict('os.environ', {'VIDEO_TEAM_LANE': 'seedance'}):
            with self.assertRaises(SystemExit) as cm:
                lane_sessions.clear_hold('ok')
        self.assertIn('HOLD_CLEAR_FROM_LANE_REFUSED', str(cm.exception))

    def test_unknown_owner_phase_counts_as_browser(self):
        self.assertEqual(vcr.owner_resource('seedance', 'lane'), 'browser')
        self.assertEqual(vcr.owner_resource('image_creator_01', 'lane', 'image_creator_01:production'), 'browser')

    def test_hold_clear_needs_user_quote_and_archives(self):
        lane_sessions.write_hold('ACCOUNT_WARNING', self.project, 'warning text')
        with self.assertRaises(SystemExit):
            lane_sessions.clear_hold('')
        out = lane_sessions.clear_hold('경고 닫았어 다시 ㄱ')
        self.assertTrue(out['cleared'])
        self.assertFalse(self.hold.exists())
        self.assertIn('경고 닫았어', (self.root / 'PROVIDER_HOLD.cleared.jsonl').read_text(encoding='utf-8'))


class WaitAndLedgerTests(Base):
    def test_dead_session_without_result_is_marked_stopped(self):
        lane = self.project / 'lanes' / 'seedance'
        (lane / 'pid').write_text('424242\n')
        (lane / 'status.json').write_text(json.dumps(
            {'status': 'RUNNING', 'provider_jobs': [{'block_id': 'B01'}]}), encoding='utf-8')
        out = lane_sessions.wait(self.project, 'seedance', lambda pid: False, timeout_min=0)
        self.assertEqual(out['result']['status'], 'NO_RESULT')
        status = json.loads((lane / 'status.json').read_text(encoding='utf-8'))
        self.assertEqual(status['status'], 'FAILED')
        self.assertEqual(status['result_status'], 'NO_RESULT')
        self.assertEqual(status['reason_code'], 'DEAD_NO_RESULT')
        self.assertEqual(status['provider_jobs'], [{'block_id': 'B01'}])

    def test_corrupt_ledger_stops_instead_of_regenerating(self):
        (self.project / 'state.json').write_text('{"provider_jobs": [', encoding='utf-8')
        with self.assertRaises(SystemExit) as cm:
            lane_sessions.produced_blocks(self.project)
        self.assertIn('LEDGER_CORRUPT', str(cm.exception))

    def test_write_json_is_atomic_replace(self):
        target = self.project / 'x.json'
        vcr.write_json(target, {'a': 1})
        self.assertEqual(json.loads(target.read_text()), {'a': 1})
        self.assertEqual([p.name for p in target.parent.glob('.x.json.*')], [])

    def test_slots_follow_model(self):
        self.assertEqual(lane_sessions.provider_slots(self.project, 'Seedance 2.5'), 1)
        self.assertEqual(lane_sessions.provider_slots(self.project, 'Seedance 2.0'), 2)
        self.assertEqual(lane_sessions.provider_slots(self.project, 'Seedance 2.5', credits=True), 2)


class ProduceLoopTests(Base):
    """A fake Runway: each dispatch runs the session the producer asked for."""

    def run_produce(self, results, released=('B01', 'B02'), **kw):
        clock = FakeClock()
        calls = []
        results = list(results)

        def fake_run(cmd, capture_output, text):
            jobs = self.state['provider_jobs']
            waiting = [j for j in jobs if not j.get('downloaded')]
            produced = {j['block_id'] for j in jobs}
            need = [b for b in released if b not in produced]
            res = results.pop(0)
            if res.get('result') is None:
                (self.project / 'lanes' / 'seedance' / 'session_result.json').unlink(missing_ok=True)
            calls.append({'t': clock.t, 'need': need, 'waiting': [j['block_id'] for j in waiting], 'res': res})
            if res.get('harvest'):
                for j in waiting:
                    j['downloaded'] = True
            if res.get('submit') and need:
                jobs.append({'block_id': need[0], 'clicked_at': clock.t.isoformat(), 'downloaded': False})
            self.save_state()
            if res.get('result') is not None:
                (self.project / 'lanes' / 'seedance' / 'session_result.json').write_text(
                    json.dumps(res['result'], ensure_ascii=False), encoding='utf-8')
            clock.sleep(300)  # the session itself takes five minutes
            if res.get('skip'):
                return SimpleNamespace(returncode=0, stdout=json.dumps({'launched': [], 'skipped': [{}]}), stderr='')
            return SimpleNamespace(returncode=0, stdout=json.dumps({'launched': [{'blocks': need[:1], 'harvest': []}]}),
                                   stderr='')

        def fake_wait(project, lane, alive, timeout_min=5):
            return {'running': False, 'result': lane_sessions.read_result(project, lane) or {'status': 'NO_RESULT'}}

        rows = [{'block_id': b, 'state': 'RELEASED'} for b in released]
        args = SimpleNamespace(project=str(self.project), credits=False, first_check_min=None, recheck_min=None,
                               max_sessions=20, session_timeout_min=60, owner_wait_sec=180, **kw)
        with mock.patch.object(vcr, '_now', clock.now), mock.patch.object(vcr, '_sleep', clock.sleep), \
                mock.patch.object(vcr.preprod, 'is_preprod_project', return_value=True), \
                mock.patch.object(vcr.preprod, 'generation', return_value={'model': 'Seedance 2.5'}), \
                mock.patch.object(vcr.preprod, 'released_blocks', return_value=list(released)), \
                mock.patch.object(vcr.preprod, 'shelf_rows', return_value=rows), \
                mock.patch.object(vcr.subprocess, 'run', side_effect=fake_run), \
                mock.patch.object(vcr.lane_sessions, 'wait', side_effect=fake_wait), \
                contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as cm:
                vcr.produce(args)
        return cm.exception.code, calls, clock

    def test_steady_state_partial_submitted_is_success_three_blocks(self):
        sub = {'status': 'PARTIAL', 'reason_code': 'SUBMITTED', 'summary': 'B 제출. 자동클릭 경고 없음.'}
        code, calls, clock = self.run_produce([
            {'submit': True, 'result': sub},                                     # B01 Generate
            {'harvest': True, 'submit': True, 'result': sub},                    # B01 down + B02 Generate
            {'harvest': True, 'submit': True, 'result': {**sub, 'summary': 'prompt_lint 경고 2건, ffprobe 경고 1건'}},
            {'result': {'status': 'PARTIAL', 'reason_code': 'IN_QUEUE', 'summary': 'B03 In queue'}},
            {'harvest': True, 'result': {'status': 'DONE', 'reason_code': 'HARVESTED', 'summary': 'B03 다운로드'}},
        ], released=('B01', 'B02', 'B03'))
        self.assertEqual(code, 0)
        self.assertEqual(len(calls), 5)
        self.assertFalse(self.hold.exists())
        # no session starts until 65 min after the click (2.5 Unlimited), then rechecks every 20 min
        self.assertGreaterEqual(calls[1]['t'] - calls[0]['t'], dt.timedelta(minutes=65))
        self.assertGreaterEqual(calls[4]['t'] - calls[3]['t'], dt.timedelta(minutes=20))

    def test_warning_prose_without_reason_code_stops_without_hold(self):
        code, calls, _ = self.run_produce([
            {'submit': True, 'result': {'status': 'PARTIAL', 'summary': '화면에 autoclicker 경고 같은 창'}}])
        self.assertEqual((code, len(calls)), (2, 1))
        self.assertFalse(self.hold.exists())

    def test_gate_skip_is_refused_not_misread(self):
        stale = {'status': 'DONE', 'reason_code': 'SUBMITTED', 'summary': 'old'}
        (self.project / 'lanes' / 'seedance' / 'session_result.json').write_text(json.dumps(stale))
        code, calls, _ = self.run_produce([{'skip': True, 'result': stale}])
        self.assertEqual((code, len(calls)), (5, 1))

    def test_lost_session_is_not_resubmitted(self):
        code, calls, _ = self.run_produce([{'result': None}])
        self.assertEqual((code, len(calls)), (4, 1))

    def test_warning_in_session_holds_everything(self):
        code, calls, _ = self.run_produce([
            {'result': {'status': 'STOPPED', 'reason_code': 'ACCOUNT_WARNING', 'summary': 'Are you using an autoclicker?'}},
        ])
        self.assertEqual(code, 3)
        self.assertEqual(len(calls), 1)
        self.assertEqual(json.loads(self.hold.read_text())['reason'], 'ACCOUNT_WARNING')

    def test_existing_hold_starts_no_session(self):
        lane_sessions.write_hold('ACCOUNT_WARNING', self.project, 'x')
        code, calls, _ = self.run_produce([])
        self.assertEqual((code, calls), (3, []))

    def test_two_unexplained_failures_stop(self):
        bad = {'result': {'status': 'PARTIAL', 'reason_code': 'ATTACH_FAILED', 'summary': '첨부 실패'}}
        code, calls, _ = self.run_produce([bad, bad])
        self.assertEqual((code, len(calls)), (4, 2))

    def test_needs_user_stops(self):
        code, _, _ = self.run_produce([{'result': {'status': 'NEEDS_USER', 'reason_code': 'NEEDS_USER',
                                                   'summary': '로그인', 'question_for_user': 'Runway 로그인?'}}])
        self.assertEqual(code, 2)


if __name__ == '__main__':
    unittest.main()
