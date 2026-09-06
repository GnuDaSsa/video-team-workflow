from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'runtime/scripts'))
sys.path.insert(0, str(ROOT / 'codex-skills/seedance-prompt-en/scripts'))
os.environ.setdefault('VIDEO_TEAM_RUNTIME_SCRIPTS', str(ROOT / 'runtime/scripts'))
import aside_bridge as bridge
import runway_ui_helper as helper

URL = 'https://app.runwayml.com/video-tools/teams/test/ai-tools/generate?sessionId=one'
BINDING = {'target_id': 'TARGET', 'session_url': URL}


class NativeFocusRecoveryTests(unittest.TestCase):
    def test_pre_activation_guard_allows_background_but_not_wrong_target(self):
        tab = {'targetId': 'TARGET', 'url': URL, 'active': True, 'focusedWindow': False}
        cases = [([tab], False, True), ([tab], True, False),
                 ([{**tab, 'active': False}], False, False),
                 ([{**tab, 'targetId': 'OTHER'}], False, False),
                 ([tab, tab], False, False), ([], False, False)]
        for tabs, focused, accepted in cases:
            with self.subTest(tabs=tabs, focused=focused):
                script = bridge.binding_script(BINDING, '(touches++, true)',
                                               require_active=True, require_focused=focused)
                code = ('let touches=0;global.URL=undefined;global.listBrowserTabs=async()=>'
                        + json.dumps(tabs) + ';global.attachBrowserTab=async()=>({url:async()=>'
                        + json.dumps(URL) + '});(async()=>{' + script
                        + ';console.log("TOUCHES="+touches);})()')
                result = subprocess.run([shutil.which('node'), '-e', code], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('TOUCHES=' + str(int(accepted)), result.stdout)

    def invoke(self, observations, *, activation=(0, 'Aside', ''), cjk=False):
        events = []
        def observe(*args, **kwargs):
            events.append(('observe', kwargs))
            return observations.pop(0)
        def osa(script):
            events.append(('native', script))
            return activation if script == helper.VERIFY_BLOCK else (0, 'done', '')
        with patch.object(helper.aside_bridge, 'browser_js', side_effect=observe), \
             patch.object(helper, 'osa', side_effect=osa), \
             patch.object(helper, 'ime_state', return_value={'cjk_active': cjk}), \
             patch.object(helper, 'evidence'):
            rc = helper.run_verified(argparse.Namespace(), 'test',
                                     'keystroke "g"', 'set the clipboard to "approved-path"\n')
        return rc, events

    def test_activation_precedes_strict_recheck_and_guarded_input_once(self):
        rc, events = self.invoke([(0, '', ''), (0, '', '')])
        self.assertEqual(rc, 0)
        self.assertEqual([x[0] for x in events], ['observe', 'native', 'observe', 'native'])
        self.assertEqual(events[0][1], {'require_active': True, 'require_focused': False})
        self.assertEqual(events[1][1], helper.VERIFY_BLOCK)
        self.assertEqual(events[2][1], {'require_active': True})
        self.assertTrue(events[3][1].startswith(helper.VERIFY_BLOCK))
        self.assertEqual(events[3][1].count('keystroke'), 1)

    def test_wrong_initial_tab_never_activates(self):
        rc, events = self.invoke([(3, '', 'wrong tab')])
        self.assertEqual(rc, 2)
        self.assertEqual([x[0] for x in events], ['observe'])

    def test_failed_activation_never_sends_input(self):
        rc, events = self.invoke([(0, '', '')], activation=(1, '', 'ABORT_FOCUS'))
        self.assertEqual(rc, 2)
        self.assertEqual([x[0] for x in events], ['observe', 'native'])
        self.assertNotIn('clipboard', events[-1][1])
        self.assertNotIn('keystroke', events[-1][1])

    def test_focus_or_session_change_after_activation_never_sends_input(self):
        for error in ('wrong tab', 'missing session', 'window not focused'):
            with self.subTest(error=error):
                rc, events = self.invoke([(0, '', ''), (3, '', error)])
                self.assertEqual(rc, 2)
                self.assertEqual([x[0] for x in events], ['observe', 'native', 'observe'])
                self.assertEqual(events[1][1], helper.VERIFY_BLOCK)

    def test_cjk_guard_prevents_clipboard_and_keys(self):
        rc, events = self.invoke([(0, '', ''), (0, '', '')], cjk=True)
        self.assertEqual(rc, 4)
        self.assertEqual([x[0] for x in events], ['observe', 'native', 'observe'])


if __name__ == '__main__':
    unittest.main()
