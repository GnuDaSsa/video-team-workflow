from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
import unicodedata
from types import SimpleNamespace


SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
os.environ.setdefault('VIDEO_TEAM_RUNTIME_SCRIPTS', str(SCRIPTS))
sys.path.insert(0, str(SCRIPTS))

import generation_settings  # noqa: E402
import runway_ui_helper  # noqa: E402
import video_codex_runtime  # noqa: E402


KOREAN_PROMPT = (
    '카메라는 골목을 천천히 따라가고 인물이 문을 여는 순간 따뜻한 빛이 '
    '바닥으로 번진다. 마지막 프레임은 인물의 안정된 중간 구도로 끝난다.'
)


class OperatorVisibilityAndDurationTests(unittest.TestCase):
    def test_manual_short_duration_without_user_or_brief_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            (project / 'manifest.json').write_text('{}', encoding='utf-8')
            (project / 'state.json').write_text('{}', encoding='utf-8')
            lock = generation_settings.initialize_duration_lock(project)
            lock['default_duration_sec'] = 10
            lock['source'] = 'planner_revision:manual-json-edit'
            path = generation_settings.duration_lock_path(project)
            path.write_text(json.dumps(lock, ensure_ascii=False), encoding='utf-8')

            errors, _snapshot = generation_settings.validate_duration_lock(project)

            self.assertIn(
                'duration_lock_shorter_without_explicit_user_or_brief', errors)

    def test_paste_prompt_requires_txt_and_nfc(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            wrong_suffix = root / 'prompt.md'
            wrong_suffix.write_text(KOREAN_PROMPT, encoding='utf-8')
            nfd = root / 'prompt.txt'
            nfd.write_text(unicodedata.normalize('NFD', KOREAN_PROMPT), encoding='utf-8')

            for path, verdict in (
                    (wrong_suffix, 'PROMPT_FILE_MUST_BE_UTF8_NFC_TXT'),
                    (nfd, 'PROMPT_FILE_NOT_NFC')):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    rc = runway_ui_helper.cmd_paste_prompt(SimpleNamespace(
                        file=str(path), replace=False, evidence=None, state='TEST'))
                self.assertEqual(rc, 1)
                self.assertIn(verdict, output.getvalue())

    def test_status_exposes_model_effort_and_phase(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            (project / 'manifest.json').write_text(
                json.dumps({'project_phase': 'test', 'blocks': []}), encoding='utf-8')
            lane = project / 'lanes' / 'seedance'
            lane.mkdir(parents=True)
            (lane / 'status.json').write_text(json.dumps({
                'status': 'READY_FOR_PRODUCTION',
                'dispatch_phase': 'prompting',
                'model': 'gpt-5.6-sol',
                'reasoning_effort': 'xhigh',
                'model_policy_version': 'test-policy',
            }), encoding='utf-8')

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                video_codex_runtime.status(SimpleNamespace(project=str(project)))
            data = json.loads(output.getvalue())
            seedance = next(row for row in data['lanes'] if row['lane'] == 'seedance')
            self.assertEqual(seedance['model'], 'gpt-5.6-sol')
            self.assertEqual(seedance['reasoning_effort'], 'xhigh')
            self.assertEqual(seedance['phase'], 'prompting')


if __name__ == '__main__':
    unittest.main()
