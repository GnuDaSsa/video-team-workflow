"""Offline tests: execute actual DOM callback JS against a synthetic Lexical DOM.
No real browser, provider, media or JEV request is made.
"""
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

PROMPT = '카메라는 골목을 천천히 따라가고 인물이 문을 여는 순간 따뜻한 빛이 바닥으로 번진다. 마지막 프레임은 인물의 안정된 중간 구도로 끝난다.'


class FakeDom:
    def __init__(self, text='', dialogs=0, editors=1, changes=None, reject_paste=False):
        self.text, self.dialogs, self.editors = text, dialogs, editors
        self.changes, self.reject_paste = changes or {}, reject_paste
        self.calls, self.events, self.scripts = 0, 0, []

    def browser(self, script):
        self.calls += 1
        self.scripts.append(script)
        for key, value in self.changes.get(self.calls, {}).items():
            setattr(self, key, value)
        payload = {'text': self.text, 'dialogs': self.dialogs, 'editors': self.editors,
                   'reject': self.reject_paste, 'script': script}
        js = '''const s=JSON.parse(process.argv[1]); let events=0;
const el={innerText:s.text, childNodes:[], getClientRects:()=>[{}], focus:()=>{},
 dispatchEvent:e=>{events++; if(!s.reject)el.innerText=e.clipboardData.getData('text/plain');}};
global.document={querySelectorAll:sel=>sel==='[contenteditable][data-lexical-editor]'
 ?Array(s.editors).fill(el):Array(s.dialogs).fill({getClientRects:()=>[{}]}),
 createRange:()=>({selectNodeContents:()=>{},collapse:()=>{}})};
global.window={getSelection:()=>({removeAllRanges:()=>{},addRange:()=>{}})};
global.DataTransfer=class {setData(k,v){this[k]=v} getData(k){return this[k]}};
global.ClipboardEvent=class {constructor(name,options){Object.assign(this,options)}};
const result=eval(s.script);
console.log(JSON.stringify({result,text:el.innerText,events}));'''
        run = subprocess.run([shutil.which('node'), '-e', js, json.dumps(payload)],
                             capture_output=True, text=True, timeout=10)
        if run.returncode:
            raise AssertionError(run.stderr)
        data = json.loads(run.stdout)
        self.text = data['text']
        self.events += data['events']
        return 0, data['result'], ''


class PromptInputTransactionTests(unittest.TestCase):
    def invoke(self, dom, text=PROMPT, replace=False, pack=None):
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / 'prompt.txt'
            f.write_text(text, encoding='utf-8')
            out = io.StringIO()
            with patch.object(helper, 'browser_js', side_effect=dom.browser), \
                 patch.object(helper.aside_bridge, 'require_project', return_value={'project': td}), \
                 patch.object(helper, 'evidence') as evidence, \
                 patch.object(helper.time, 'sleep'), contextlib.redirect_stdout(out):
                rc = helper.cmd_paste_prompt(argparse.Namespace(file=str(f), replace=replace, pack=pack))
            return rc, out.getvalue(), evidence.call_args_list

    def test_identical_accepted_text_is_success_without_paste(self):
        for replace in (False, True):
            dom = FakeDom(PROMPT)
            rc, out, _ = self.invoke(dom, replace=replace)
            data = json.loads(out)
            self.assertEqual(rc, 0)
            self.assertEqual(data['verdict'], 'PROMPT_ALREADY_MATCHED')
            self.assertFalse(data['write_dispatched'])
            self.assertEqual(dom.calls, 1)
            self.assertEqual(dom.events, 0)
            self.assertNotIn(PROMPT, out)

    def test_empty_editor_gets_one_paste_and_actual_readback(self):
        dom = FakeDom()
        rc, out, _ = self.invoke(dom)
        self.assertEqual(rc, 0)
        self.assertEqual(dom.events, 1)
        self.assertEqual(dom.calls, 3)
        self.assertEqual(dom.text, PROMPT)
        self.assertTrue(json.loads(out)['content_match'])

    def test_foreign_or_mutated_nonempty_text_is_preserved_even_with_replace(self):
        for text in ('다른 프로젝트의 미전송 문구', PROMPT + ' 변경', PROMPT.replace('골목', '복도')):
            for replace in (False, True):
                dom = FakeDom(text)
                rc, _, _ = self.invoke(dom, replace=replace)
                self.assertEqual(rc, 1)
                self.assertEqual(dom.text, text)
                self.assertEqual(dom.events, 0)

    def test_visible_dialog_blocks_empty_and_matching_editors(self):
        for text in ('', PROMPT):
            dom = FakeDom(text, dialogs=1)
            rc, _, evidence = self.invoke(dom)
            self.assertEqual(rc, 1)
            self.assertEqual(dom.events, 0)
            self.assertEqual(evidence[-1].args[-1], 'BLOCKING_DIALOG_CLOSE_AND_REOBSERVE')

    def test_dialog_opening_between_observation_and_paste_blocks_mutation(self):
        dom = FakeDom(changes={2: {'dialogs': 1}})
        rc, _, _ = self.invoke(dom)
        self.assertEqual(rc, 1)
        self.assertEqual(dom.events, 0)
        self.assertEqual(dom.calls, 2)

    def test_editor_changing_between_observation_and_paste_is_preserved(self):
        dom = FakeDom(changes={2: {'text': '다른 입력'}})
        rc, _, evidence = self.invoke(dom)
        self.assertEqual(rc, 1)
        self.assertEqual(dom.events, 0)
        self.assertEqual(dom.text, '다른 입력')
        self.assertEqual(evidence[-1].args[-1], 'PROMPT_CHANGED_BEFORE_PASTE')

    def test_dialog_opening_after_paste_never_produces_false_success_or_repaste(self):
        dom = FakeDom(changes={3: {'dialogs': 1}})
        rc, _, _ = self.invoke(dom)
        self.assertEqual(rc, 1)
        self.assertEqual(dom.events, 1)
        self.assertEqual(dom.calls, 3)

    def test_ambiguous_or_missing_editor_never_mutates(self):
        for editors in (0, 2):
            dom = FakeDom(editors=editors)
            self.assertEqual(self.invoke(dom)[0], 1)
            self.assertEqual(dom.events, 0)

    def test_rejected_paste_polls_reads_only_and_fails(self):
        dom = FakeDom(reject_paste=True)
        rc, out, _ = self.invoke(dom)
        self.assertEqual(rc, 1)
        self.assertEqual(dom.events, 1)
        self.assertEqual(dom.calls, 13)
        self.assertEqual(json.loads(out)['verdict'], 'CONTENT_MISMATCH_DO_NOT_GENERATE')
        self.assertFalse(json.loads(out)['ok'])

    def test_recovery_read_does_not_accept_text_behind_modal(self):
        dom = FakeDom(PROMPT, dialogs=1)
        out = io.StringIO()
        with patch.object(helper, 'browser_js', side_effect=dom.browser), \
             patch.object(helper, 'evidence'), contextlib.redirect_stdout(out):
            self.assertEqual(helper.cmd_read_prompt(argparse.Namespace(file=None)), 1)
        self.assertFalse(json.loads(out.getvalue())['ok'])
        self.assertEqual(dom.events, 0)

    def test_language_and_pack_failures_remain_before_browser(self):
        dom = FakeDom('English only.')
        self.assertEqual(self.invoke(dom, text='English only.')[0], 1)
        self.assertEqual(dom.calls, 0)
        with patch.object(helper, 'validate_paste_pack', side_effect=ValueError('Synthetic invalid pack')):
            self.assertEqual(self.invoke(dom, pack='/synthetic/pack.json')[0], 1)
        self.assertEqual(dom.calls, 0)

    def test_read_transport_failure_does_not_paste(self):
        dom = FakeDom()
        dom.browser = lambda _: (1, '', 'Synthetic transport failure')
        self.assertEqual(self.invoke(dom)[0], 3)
        self.assertEqual(dom.events, 0)

    def test_malformed_preflight_and_postread_return_recovery_not_repaste(self):
        for failure_call in (1, 2, 3):
            dom = FakeDom()
            real = dom.browser
            def call(script):
                if dom.calls + 1 == failure_call:
                    dom.calls += 1
                    return 0, '[]', ''
                return real(script)
            dom.browser = call
            self.assertEqual(self.invoke(dom)[0], 3)
            self.assertEqual(dom.events, 1 if failure_call == 3 else 0)


if __name__ == '__main__':
    unittest.main()
