from __future__ import annotations

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / 'codex-skills' / 'seedance25-prompt-en'


class Seedance25SkillContractTests(unittest.TestCase):
    def test_router_is_explicit_and_keeps_generic_work_on_20(self) -> None:
        text = (SKILL / 'SKILL.md').read_text(encoding='utf-8')

        self.assertIn('Use only when the user explicitly requests Seedance 2.5', text)
        self.assertIn('generic `Seedance` with no version', text)
        self.assertIn('../seedance-prompt-en/SKILL.md', text)
        self.assertIn('Do not load both version-specific', text)

    def test_only_prompting_and_production_are_version_branches(self) -> None:
        self.assertTrue((SKILL / 'prompting.md').is_file())
        self.assertTrue((SKILL / 'production.md').is_file())
        router = (SKILL / 'SKILL.md').read_text(encoding='utf-8')

        self.assertIn('runtime `AGENTS.md` continues to own rails', router)
        self.assertIn('only the version-specific prompt and Runway production', router)

    def test_prompting_encodes_25_modes_and_physical_animation(self) -> None:
        text = (SKILL / 'prompting.md').read_text(encoding='utf-8')

        for marker in ('Reference', 'Keyframe', 'Edit', 'Extend'):
            self.assertIn(marker, text)
        for marker in ('Anticipation', 'Primary action', 'Settle and end state',
                       '2D and stylized animation', 'line weight'):
            self.assertIn(marker, text)
        self.assertIn('provider_model: Seedance 2.5', text)
        self.assertIn('provider_skill: seedance25-prompt-en', text)

    def test_production_fails_closed_on_model_mismatch(self) -> None:
        text = (SKILL / 'production.md').read_text(encoding='utf-8')

        self.assertIn('choose **Seedance 2.5**', text)
        self.assertIn('Any `Seedance 2.0`', text)
        self.assertIn('settings-verify', text)
        self.assertIn('queue-exit-check', text)

    def test_adapter_contains_no_second_ui_or_queue_implementation(self) -> None:
        path = SKILL / 'scripts' / 'runway_ui_helper.py'
        tree = ast.parse(path.read_text(encoding='utf-8'))
        functions = {
            node.name for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }

        self.assertFalse(functions & {
            'browser_js', 'sync_queue_runtime', 'create_recovery_checkpoint',
            'run_bounded_queue_wake', 'prepare_upload_alias',
        })
        self.assertIn('_require_seedance_25', functions)
        self.assertIn('_verify_seedance_25_settings', functions)


if __name__ == '__main__':
    unittest.main()
