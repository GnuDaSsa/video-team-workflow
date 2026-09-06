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
    def test_creative_generation_routes_to_sol_xhigh(self) -> None:
        for lane, phase in (
                ('image_creator_01', None), ('image_creator_02', None),
                ('seedance', 'prompting')):
            route = model_routing.resolve(lane, phase)
            self.assertEqual(route['model'], 'gpt-5.6-sol')
            self.assertEqual(route['reasoning_effort'], 'xhigh')
            self.assertEqual(
                route['required_spawn_approval'],
                f'{lane}:{phase if lane == "seedance" else "lane"}')

    def test_flow_qc_and_computer_use_route_to_luna_high(self) -> None:
        for lane in ('director', 'music', 'planner', 'image_qc',
                     'seedance_qc', 'editor', 'package'):
            route = model_routing.resolve(lane)
            self.assertEqual(route['model'], 'gpt-5.6-luna')
            self.assertEqual(route['reasoning_effort'], 'high')
        production = model_routing.resolve('seedance', 'production')
        self.assertEqual(production['model'], 'gpt-5.6-luna')
        self.assertEqual(production['reasoning_effort'], 'high')
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
            self.assertIn('gpt-5.6-luna', prompt)
            self.assertIn('aside repl', prompt)
            self.assertIn('attachBrowserTab(targetId)', prompt)
            self.assertIn('no second browser loop', prompt)

    def test_workflow_reports_model_matrix(self) -> None:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            video_codex_runtime.workflow(SimpleNamespace())
        data = json.loads(out.getvalue())
        self.assertEqual(
            data['model_routing']['policy_version'], model_routing.POLICY_VERSION)
        self.assertFalse(data['model_routing']['auto_spawn_next_phase'])

    def test_codex_command_carries_model_and_effort(self) -> None:
        route = model_routing.resolve('seedance', 'production')
        command = video_codex_runtime.codex_exec_inner(
            Path('/tmp/project'), Path('/tmp/prompt.md'), Path('/tmp/result.md'), route)
        self.assertIn('-m gpt-5.6-luna', command)
        self.assertIn('model_reasoning_effort=', command)
        self.assertIn('high', command)

    def test_dispatch_refuses_without_exact_spawn_approval(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            (project / 'state.json').write_text('{}', encoding='utf-8')
            (project / 'lanes' / 'director').mkdir(parents=True)
            with mock.patch('video_codex_runtime.lane_gates.gate_check', return_value=(True, 'OK')):
                with self.assertRaisesRegex(SystemExit, 'SPAWN_APPROVAL_REQUIRED'):
                    video_codex_runtime.dispatch(SimpleNamespace(
                        project=str(project), lanes=['director'], phase='auto',
                        approved_spawn=None, force=False))


if __name__ == '__main__':
    unittest.main()
