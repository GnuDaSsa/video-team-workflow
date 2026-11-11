from __future__ import annotations
import os as _os, tempfile as _tempfile
_TMP = _tempfile.mkdtemp(prefix='warnhold-test-')
_os.environ.setdefault('RUNWAY_UPLOAD_ALIAS_ROOT', _tempfile.mkdtemp(prefix='rwup-test-'))
_os.environ['VIDEO_TEAM_PROVIDER_HOLD'] = _os.path.join(_TMP, 'PROVIDER_HOLD.json')

import json
import os
import sys
import unittest
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
SKILL = Path(__file__).resolve().parents[2] / 'codex-skills/seedance-prompt-en/scripts'
SKILL25 = Path(__file__).resolve().parents[2] / 'codex-skills/seedance25-prompt-en/scripts'
os.environ.setdefault('VIDEO_TEAM_RUNTIME_SCRIPTS', str(SCRIPTS))
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(SKILL))

import runway_ui_helper as h  # noqa: E402
import run_block  # noqa: E402


class HoldCase(unittest.TestCase):
    def setUp(self):
        self.hold = Path(os.environ['VIDEO_TEAM_PROVIDER_HOLD'])
        self.hold.unlink(missing_ok=True)

    def tearDown(self):
        self.hold.unlink(missing_ok=True)


class PatternTests(unittest.TestCase):
    STRONG = [
        'Are you using an autoclicker?',
        'Using auto-click tools may result in your account being suspended.',
        '자동 클릭 도구를 사용하면 계정이 정지될 수 있습니다.',
        'We detected unusual activity on your account.',
        'Please complete the captcha to continue',
    ]
    WEAK = [
        'Automated tools violate our Terms of Service and may lead to suspension.',
        'Your account has been suspended.',
        '계정 이용 정지 안내',
        '자동화 도구 사용은 약관 위반입니다',
    ]
    PROMPT_LIKE = [
        'macro shot of a hand, restricted color palette',
        'automated factory, no banners',
        'the script terminates at the door',
        '로봇 팔이 멈추고 기계가 정지한다',
        'Terms of Use. Contact us. Browser scripts',
        'a robot arm in an automated factory, the machine stops',
        'Your account page. Settings ban none',
    ]

    def test_strong_anywhere(self):
        for text in self.STRONG:
            self.assertTrue(h.detect_account_warning(text), text)
            self.assertTrue(h.detect_account_warning('', text), text)

    def test_weak_only_in_dialog(self):
        for text in self.WEAK:
            self.assertIsNone(h.detect_account_warning(text), text)
            self.assertTrue(h.detect_account_warning('', text), text)

    def test_prompt_like_text_is_negative(self):
        for text in self.PROMPT_LIKE:
            self.assertIsNone(h.detect_account_warning(text), text)
            self.assertIsNone(h.detect_account_warning(text, ''), text)

    def test_payload_parsing(self):
        raw = json.dumps({'page_text': 'automated factory, restricted', 'dialog_text': 'Your account has been suspended.'})
        self.assertTrue(h.detect_account_warning(*h.parse_warning_payload(raw)))
        raw = json.dumps({'page_text': 'Your account has been suspended.', 'dialog_text': ''})
        self.assertIsNone(h.detect_account_warning(*h.parse_warning_payload(raw)))

    def test_negative_samples(self):
        for text in [
            'In queue', 'Generating 45%', 'Unlimited', 'Seedance 2.5  15s  16:9  720p',
            'Warning: this tooltip explains aspect ratio', 'Generate', 'Your generation is in the queue.',
            'Account settings', 'Upgrade your plan', 'Terms of Service', '', None,
        ]:
            self.assertIsNone(h.detect_account_warning(text, text), text)

    def test_evidence_is_bounded(self):
        found = h.detect_account_warning('x' * 500 + ' Are you using an autoclicker? ' + 'y' * 500)
        self.assertLessEqual(len(found), 200)
        self.assertIn('autoclicker', found)

    def test_25_adapter_inherits(self):
        sys.path.insert(0, str(SKILL25))
        import importlib.util
        spec = importlib.util.spec_from_file_location('h25_for_warning_test', SKILL25 / 'runway_ui_helper.py')
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.assertTrue(mod.detect_account_warning('Are you using an autoclicker?'))
        self.assertIn('ACCOUNT_WARNING', mod.HUMAN_ACTION_INCIDENTS)


class HoldFileTests(HoldCase):
    def test_atomic_write_and_keep_first(self):
        doc = h.write_provider_hold('evidence one', project='/p', block='B01')
        data = json.loads(self.hold.read_text(encoding='utf-8'))
        self.assertEqual(data['reason'], 'ACCOUNT_WARNING')
        self.assertEqual((data['project'], data['block'], data['evidence']), ('/p', 'B01', 'evidence one'))
        self.assertTrue(data['held_at'])
        self.assertEqual(doc, data)
        h.write_provider_hold('second')
        self.assertEqual(json.loads(self.hold.read_text(encoding='utf-8'))['evidence'], 'evidence one')
        self.assertEqual([p.name for p in self.hold.parent.glob('PROVIDER_HOLD.json.tmp*')], [])

    def test_incident_is_human_action(self):
        self.assertIn('ACCOUNT_WARNING', h.HUMAN_ACTION_INCIDENTS)
        self.assertIn('ACCOUNT_WARNING', h.RECOVERY_INCIDENTS)

    def test_scan_page_writes_hold(self):
        with mock.patch.object(h, 'browser_js', return_value=(0, 'Title\nAre you using an autoclicker?\nOK', '')):
            res = h.scan_page_for_warning(None, None, 'test')
        self.assertEqual(res['reason_code'], 'ACCOUNT_WARNING')
        self.assertTrue(self.hold.exists())

    def test_scan_page_clean(self):
        with mock.patch.object(h, 'browser_js', return_value=(0, 'In queue\nGenerating 45%', '')):
            self.assertIsNone(h.scan_page_for_warning(None, None, 'test'))
        self.assertFalse(self.hold.exists())

    def test_guard_page_exit_codes(self):
        out = StringIO()
        with mock.patch.object(h, 'browser_js', return_value=(0, 'autoclicker?', '')), mock.patch('sys.stdout', out):
            self.assertEqual(h.guard_page(SimpleNamespace(), 'x'), h.ACCOUNT_WARNING_EXIT)
        self.assertEqual(json.loads(out.getvalue())['reason_code'], 'ACCOUNT_WARNING')
        out = StringIO()
        with mock.patch.object(h, 'browser_js', side_effect=AssertionError('browser touched')), mock.patch('sys.stdout', out):
            self.assertEqual(h.guard_page(SimpleNamespace(), 'x'), h.PROVIDER_HOLD_EXIT)
        self.assertEqual(json.loads(out.getvalue())['reason_code'], 'PROVIDER_HOLD')


class RunBlockHoldTests(HoldCase):
    def test_run_returns_before_anything_when_held(self):
        h.write_provider_hold('held', project='/p', block='B01')
        with mock.patch.object(run_block, 'load_context', side_effect=AssertionError('touched project')):
            result = run_block.run(Path('/nonexistent-project'), 'B01')
        self.assertFalse(result['ok'])
        self.assertEqual(result['stop'], 'PROVIDER_HOLD')
        self.assertEqual(result['reason_code'], 'PROVIDER_HOLD')
        self.assertFalse(Path('/nonexistent-project').exists())

    def test_warning_during_run_passes_through(self):
        class Page:
            def js(self, code):
                return 'Are you using an autoclicker?'
        ctx = {'project': Path('/nonexistent-project'), 'block': 'B01'}
        with self.assertRaises(run_block.Stop) as cm:
            run_block.scan_for_warning(ctx, Page(), 'test')
        self.assertEqual(cm.exception.code, 'ACCOUNT_WARNING')
        self.assertTrue(self.hold.exists())


if __name__ == '__main__':
    unittest.main()
