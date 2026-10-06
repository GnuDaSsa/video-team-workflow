import argparse
import contextlib
import copy
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'codex-skills/seedance-prompt-en/scripts'))
import runway_ui_helper as helper
from runway_chip_serializer import PROMPT_CHIP_SERIALIZER_JS


def element(tag, children=None, **attrs):
    return dict(node_type='element', tag=tag, attributes=attrs, children=children or [])


def text(s):
    return dict(node_type='text', text=s)


def chip(n=1, identity='synthetic-asset-1'):
    return element('SPAN', [element('BUTTON', [element('IMG'), element('SPAN', [text(f'Image {n}')])],
                                  **{'aria-label': f'View Image {n} larger'})],
                   **{'data-reference': f'@Image {n}', 'data-asset-id': identity,
                      'data-reference-id': identity, 'data-lexical-decorator': 'true',
                      'contenteditable': 'false'})


def run_serializer(tree):
    # DOM adapter for recorded/synthetic public structure, no browser or URL access.
    code = '''const build = n => n.node_type === 'text'
      ? {nodeType:3,nodeValue:n.text}
      : {nodeType:1,tagName:n.tag,innerText:'CSS raw\\nImage 1',
         childNodes:n.children.map(build), getAttribute:k=>n.attributes[k]??null};
      console.log(JSON.stringify((''' + PROMPT_CHIP_SERIALIZER_JS + ') (build(' + json.dumps(tree) + '))));'
    p = subprocess.run(['node', '-e', code], capture_output=True, text=True, check=True)
    return json.loads(p.stdout)


class ChipSerializerTests(unittest.TestCase):
    def tree(self, nodes=None):
        return element('DIV', [element('P', nodes if nodes is not None else [chip(),
          element('SPAN', [text(' 두  칸')], **{'data-lexical-text':'true'})]),
          element('P', [element('BR')]), element('P', [text('끝'), element('BR'), text('다음')])])

    def test_canonical_and_raw_preserve_whitespace(self):
        r = run_serializer(self.tree())
        self.assertTrue(r['ok'])
        self.assertEqual(r['text'], '@Image1 두  칸\n\n끝\n다음')
        self.assertEqual(r['raw_display_text'], 'CSS raw\nImage 1')
        self.assertFalse(r['asset_binding_verified'])

    def test_unknown_and_malformed_fail_closed(self):
        for key, value in [('data-asset-id',''), ('data-reference-id','wrong'),
                           ('data-reference','@Image1'), ('contenteditable','true')]:
            c = chip(); c['attributes'][key] = value
            self.assertFalse(run_serializer(self.tree([c]))['ok'])
        c = chip(); c['children'][0]['children'].append(text('extra'))
        self.assertFalse(run_serializer(self.tree([c]))['ok'])
        self.assertFalse(run_serializer(self.tree([element('DIV')]))['ok'])

    def test_duplicate_slot_or_asset_rejected(self):
        for second in [chip(1,'other'), chip(2)]:
            self.assertFalse(run_serializer(self.tree([chip(),second]))['ok'])

    def read(self, result, expected):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)/'prompt.txt'; path.write_text(expected)
            output = io.StringIO()
            with patch.object(helper,'browser_js',return_value=(0,json.dumps(result),'')), \
                 patch.object(helper.aside_bridge,'require_project'), patch.object(helper,'evidence'), \
                 contextlib.redirect_stdout(output):
                rc = helper.cmd_read_prompt(argparse.Namespace(file=str(path)))
            return rc, json.loads(output.getvalue())

    def test_match_is_not_asset_binding_pass(self):
        r = run_serializer(self.tree([chip()]))
        rc, report = self.read(r,r['text'])
        self.assertEqual(rc,1)
        self.assertTrue(report['content_match'])
        self.assertTrue(report['chip_occurrences_match'])
        self.assertEqual(report['verdict'],'HOLD_ASSET_BINDING_UNVERIFIED')
        self.assertIn('canonical_text',report)
        self.assertIn('raw_display_sha256',report)

    def test_internally_consistent_wrong_asset_cannot_pass(self):
        r = run_serializer(self.tree([chip(identity='different-provider-id')]))
        rc, report = self.read(r, r['text'])
        self.assertEqual(rc, 1)
        self.assertFalse(report['asset_binding_verified'])
        self.assertTrue(report['content_match'])

    def test_plaintext_token_never_counts_as_chip(self):
        r = run_serializer(self.tree([text('@Image1')]))
        rc, report = self.read(r,r['text'])
        self.assertEqual(rc,1)
        self.assertFalse(report['chip_occurrences_match'])

    def test_missing_reordered_and_changed_text_fail(self):
        for nodes in [[chip(2,'other'),chip()], [chip()], [text('Image 1')]]:
            rc, report = self.read(run_serializer(self.tree(nodes)), '@Image1@Image2\n\n끝\n다음')
            self.assertEqual(rc,1)
            self.assertFalse(report['content_match'])

    def test_plain_prose_stays_read_only_pass(self):
        r = run_serializer(self.tree([text('일반 문장')]))
        self.assertEqual(self.read(r,r['text'])[0],0)


if __name__ == '__main__':
    unittest.main()
