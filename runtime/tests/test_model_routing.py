from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock


SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))

import model_routing  # noqa: E402
import video_codex_runtime  # noqa: E402


class ModelRoutingTests(unittest.TestCase):
    def test_explicit_legacy_luna_owner_uses_gpt6(self) -> None:
        self.assertEqual(model_routing.LUNA_MODEL, 'gpt-6-luna')
        self.assertEqual(model_routing.LUNA_EFFORT, 'high')

    def test_creative_generation_routes_to_astra_xhigh(self) -> None:
        for lane, phase in (
                ('image_creator_01', None), ('image_creator_02', None),
                ('seedance', 'prompting')):
            route = model_routing.resolve(lane, phase)
            self.assertEqual(route['model'], 'gpt-6-astra')
            self.assertEqual(route['reasoning_effort'], 'xhigh')
            self.assertEqual(
                route['required_spawn_approval'],
                f'{lane}:{phase if lane == "seedance" else "lane"}')

    def test_flow_qc_and_computer_use_route_to_luna_high(self) -> None:
        for lane in ('director', 'music', 'image_qc',
                     'seedance_qc', 'package'):
            route = model_routing.resolve(lane)
            self.assertIsNone(route['model'])
            self.assertIsNone(route['reasoning_effort'])
        production = model_routing.resolve('seedance', 'production')
        self.assertIsNone(production['model'])
        self.assertIsNone(production['reasoning_effort'])
        self.assertEqual(production['purpose'], 'aside_cli_and_computer_use')

    def test_seedance_auto_phase_moves_only_after_ready_status(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            lane = project / 'lanes' / 'seedance'
            lane.mkdir(parents=True)
            (lane / 'status.json').write_text(
                json.dumps({'status': 'PENDING'}), encoding='utf-8')
            with mock.patch('video_codex_runtime.lane_gates._seedance_resume_needed', return_value=False):
                self.assertEqual(video_codex_runtime.seedance_phase(project), 'prompting')
                (lane / 'status.json').write_text(json.dumps({
                    'status': 'READY_FOR_PRODUCTION', 'phase': 'prompting_complete'}),
                    encoding='utf-8')
                self.assertEqual(video_codex_runtime.seedance_phase(project), 'production')

    def test_make_prompt_enforces_aside_repl_and_no_auto_spawn(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            old_templates = video_codex_runtime.TEMPLATES
            templates = project / 'templates'
            templates.mkdir()
            (templates / 'shared_lane_contract.md').write_text('shared', encoding='utf-8')
            (templates / 'seedance.md').write_text('seedance body', encoding='utf-8')
            video_codex_runtime.TEMPLATES = templates
            try:
                prompt = video_codex_runtime.make_prompt(project, 'seedance', 'production')
            finally:
                video_codex_runtime.TEMPLATES = old_templates
            self.assertIn('inherit_session', prompt)
            self.assertIn('aside repl', prompt)
            self.assertIn('attachBrowserTab(targetId)', prompt)
            self.assertIn('no second browser loop', prompt)
            self.assertNotIn('Sol prompting', prompt)

    def test_workflow_reports_model_matrix(self) -> None:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            video_codex_runtime.workflow(SimpleNamespace())
        data = json.loads(out.getvalue())
        self.assertEqual(
            data['model_routing']['policy_version'], model_routing.POLICY_VERSION)
        self.assertFalse(data['model_routing']['auto_spawn_next_phase'])
        self.assertNotIn('Sol', data['model_routing']['seedance_phase_handoff'])
        self.assertIn('Astra', data['model_routing']['seedance_phase_handoff'])

    def test_codex_command_carries_model_and_effort(self) -> None:
        args = (Path('/tmp/project'), Path('/tmp/prompt.md'), Path('/tmp/result.md'))
        # No routed model: the session uses the user's own Codex default model.
        production = video_codex_runtime.codex_exec_inner(*args, model_routing.resolve('seedance', 'production'))
        self.assertNotIn(' -m ', production)
        self.assertIn('danger-full-access', production)  # Aside CLI / native chooser lane
        authoring = video_codex_runtime.codex_exec_inner(*args, model_routing.resolve('seedance', 'prompting'))
        self.assertIn('-m gpt-6-astra', authoring)
        self.assertIn('-s workspace-write', authoring)
        self.assertNotIn('--full-auto', authoring)  # removed from codex exec
        self.assertIn('--json', authoring)
        self.assertNotIn('danger-full-access', authoring)

    def test_dispatch_refuses_without_exact_spawn_approval(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            (project / 'state.json').write_text('{}', encoding='utf-8')
            (project / 'lanes' / 'director').mkdir(parents=True)
            (project / 'lanes' / 'image_qc').mkdir(parents=True)
            with mock.patch('video_codex_runtime.lane_gates.gate_check', return_value=(True, 'OK')), \
                    mock.patch.object(video_codex_runtime.lane_sessions, 'load_policy', return_value={}):
                with self.assertRaisesRegex(SystemExit, 'SPAWN_APPROVAL_REQUIRED'):
                    video_codex_runtime.dispatch(SimpleNamespace(
                        project=str(project), lanes=['image_qc'], phase='auto',
                        approved_spawn=None, force=False))
                with self.assertRaisesRegex(SystemExit, 'DIRECTOR_STAYS_IN_MAIN_THREAD'):
                    video_codex_runtime.dispatch(SimpleNamespace(
                        project=str(project), lanes=['director'], phase='auto',
                        approved_spawn=None, force=False))

    def test_standing_policy_starts_one_lane_session_and_wait_reads_result(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            (project / 'state.json').write_text('{}', encoding='utf-8')
            (project / 'manifest.json').write_text('{}', encoding='utf-8')
            policy = {'auto_lane_sessions': True, 'approval_quote': 'q', 'recorded_at': 't'}
            proc = mock.Mock(pid=4242)
            out = io.StringIO()
            with mock.patch('video_codex_runtime.lane_gates.gate_check', return_value=(True, 'OK')), \
                    mock.patch.object(video_codex_runtime.lane_sessions, 'load_policy', return_value=policy), \
                    mock.patch.object(video_codex_runtime, 'run_due_cleanup'), \
                    mock.patch.object(video_codex_runtime.subprocess, 'Popen', return_value=proc) as popen, \
                    mock.patch.object(video_codex_runtime, 'CODEX', Path(sys.executable)), \
                    contextlib.redirect_stdout(out):
                video_codex_runtime.dispatch(SimpleNamespace(
                    project=str(project), lanes=['image_qc'], phase='auto', approved_spawn=None, force=False))
            popen.assert_called_once()
            prompt = (project / 'lanes/image_qc/prompt.md').read_text(encoding='utf-8')
            self.assertIn('SESSION RESULT CONTRACT', prompt)
            status = json.loads((project / 'lanes/image_qc/status.json').read_text())
            self.assertTrue(status['approved_spawn'].startswith('standing:'))
            (project / 'lanes/image_qc/session_result.json').write_text(
                json.dumps({'status': 'DONE', 'summary': 'ok'}), encoding='utf-8')
            waited = video_codex_runtime.lane_sessions.wait(project, 'image_qc', lambda pid: False, 0)
            self.assertEqual(waited['result']['status'], 'DONE')
            self.assertFalse(waited['running'])

    def test_production_batch_fills_only_free_runway_slots(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            (project / 'lanes/seedance').mkdir(parents=True)
            status = project / 'lanes/seedance/status.json'
            released = [f'B0{i}' for i in range(1, 8)]
            status.write_text(json.dumps({'provider_jobs': [{'block_id': 'B01', 'downloaded': True}]}), encoding='utf-8')
            batch, rest = video_codex_runtime.lane_sessions.production_batch(project, released)
            self.assertEqual(batch, ['B02', 'B03'])  # two active generations per Runway account
            self.assertEqual(rest, ['B04', 'B05', 'B06', 'B07'])
            status.write_text(json.dumps({'provider_jobs': [{'block_id': 'B01'}]}), encoding='utf-8')
            batch, _ = video_codex_runtime.lane_sessions.production_batch(project, released)
            self.assertEqual(batch, ['B02'])  # B01 still holds a slot
            status.write_text(json.dumps({'provider_jobs': [{'block_id': 'B01'}, {'block_id': 'B02'}]}), encoding='utf-8')
            batch, rest = video_codex_runtime.lane_sessions.production_batch(project, released)
            self.assertEqual(batch, [])  # both slots busy -> dispatch harvests instead
            self.assertEqual(rest[0], 'B03')
            with self.assertRaises(SystemExit):
                video_codex_runtime.lane_sessions.production_batch(project, released, ['B09'])

    def test_next_prefers_same_owner_without_automatic_model_switch(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            out = io.StringIO()
            with mock.patch.object(video_codex_runtime.lane_gates, 'next_actions',
                                   return_value={'next_lanes': ['seedance']}), \
                    mock.patch.object(video_codex_runtime, 'seedance_phase', return_value='production'), \
                    mock.patch.object(video_codex_runtime.lane_sessions, 'load_policy', return_value={}), \
                    contextlib.redirect_stdout(out):
                video_codex_runtime.next_cmd(SimpleNamespace(project=td))
            value = json.loads(out.getvalue())
            self.assertEqual(value['default_execution']['action'], 'CONTINUE_IN_CURRENT_CONVERSATION')
            self.assertFalse(value['default_execution']['new_approval_for_role_change'])
            self.assertFalse(value['default_execution']['automatic_model_switch'])
            self.assertTrue(value['next_dispatch'][0]['dispatch_requires_explicit_action'])
            self.assertEqual(value['next_dispatch'][0]['required_spawn_approval'], 'seedance:production')


if __name__ == '__main__':
    unittest.main()
