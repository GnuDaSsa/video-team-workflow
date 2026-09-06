import argparse
import contextlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'runtime/scripts'))
sys.path.insert(0, str(ROOT / 'codex-skills/seedance-prompt-en/scripts'))
import runway_ui_helper as helper


class LexicalVisibleTextTests(unittest.TestCase):
    def read_dom(self, paragraphs, fallback='CSS\n\nseparators'):
        nodes = [{'nodeType': 1, 'tagName': 'P', 'innerText': text,
                  'childNodes': [{'nodeName': 'BR' if text == '\n' else 'SPAN'}],
                  'firstChild': {'nodeName': 'BR' if text == '\n' else 'SPAN'}} for text in paragraphs]
        code = 'console.log(JSON.stringify((' + helper.PROMPT_DOM_TEXT_JS + ')(' + json.dumps(
            {'childNodes': nodes, 'innerText': fallback}) + ')))'
        run = subprocess.run([shutil.which('node'), '-e', code], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        return json.loads(run.stdout)

    def test_paragraph_boundaries_not_css_spacing(self):
        self.assertEqual(self.read_dom(['시작', '@Image1 인물', '마지막', '\n']),
                         '시작\n@Image1 인물\n마지막\n')

    def test_intentional_whitespace_blank_paragraphs_and_inline_br_preserved(self):
        self.assertEqual(self.read_dom(['두  칸', '\n', '위\n아래']), '두  칸\n\n위\n아래')
        self.assertEqual(self.read_dom([], 'plain text'), 'plain text')

    def test_read_only_verification_fails_real_mutations_without_repaste(self):
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / 'prompt.txt'; f.write_text('첫 줄\n둘  째\n')
            for actual, expected_rc in [('첫 줄\n둘  째\n', 0), ('첫 줄\n둘 째', 1),
                                        ('첫 줄\n변경', 1), ('첫 줄\n\n둘  째', 1)]:
                with self.subTest(actual=actual), \
                     patch.object(helper, 'browser_js', return_value=(0, json.dumps(
                         {'ok': True, 'text': actual, 'len': len(actual)}), '')) as browser, \
                     patch.object(helper.aside_bridge, 'require_project'), \
                     patch.object(helper, 'evidence'), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(helper.cmd_read_prompt(argparse.Namespace(file=str(f))), expected_rc)
                    self.assertEqual(browser.call_count, 1)
                    self.assertNotIn('dispatchEvent', browser.call_args.args[0])


if __name__ == '__main__':
    unittest.main()
