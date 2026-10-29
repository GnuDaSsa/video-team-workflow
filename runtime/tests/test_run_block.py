from __future__ import annotations
import os as _os, tempfile as _tempfile
_os.environ.setdefault('RUNWAY_UPLOAD_ALIAS_ROOT', _tempfile.mkdtemp(prefix='rwup-test-'))  # never the real ledger

import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
SKILL = Path(__file__).resolve().parents[2] / 'codex-skills/seedance-prompt-en/scripts'
os.environ.setdefault('VIDEO_TEAM_RUNTIME_SCRIPTS', str(SCRIPTS))
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(SKILL))

import runway_ui_helper  # noqa: E402,F401
import run_block  # noqa: E402

SETTINGS = {'model': 'Seedance 2.0', 'duration_sec': 15, 'aspect_ratio': '16:9', 'resolution': '720p',
            'audio': 'ON', 'mode': 'Multi-reference', 'generation_tier': 'Explore Mode'}
GOOD = {'model': 'Seedance 2.0', 'duration': '15s', 'ratio': '16:9', 'resolution': '720p',
        'multi_reference': True, 'audio': 'true', 'tier': 'Unlimited', 'refs': [1, 2],
        'prompt': '15 seconds, 3 shots: x', 'editors': 1, 'dialogs': [], 'generate': [{'disabled': False}]}


class FakePage:
    def __init__(self, state, rows=0):
        self.state, self.rows, self.calls = dict(state), rows, []
        self.binding = {}

    def js(self, code):
        self.calls.append(('js', code))
        if code == run_block.STATE_JS:
            return self.state
        if '"open"' in code:
            return 'open'
        if 'role=button' in code and 'split' in code:
            return self.rows or None
        if 'View Image' in code and 'larger"]\')?"ok"' in code:
            return 'ok'
        if 'naturalWidth' in code:
            return {'w': 1920, 'h': 1080}
        if 'Close' in code:
            return True
        return True

    def act(self, body):
        self.calls.append(('act', body))
        return True


class RunBlockTests(unittest.TestCase):
    def test_expected_settings_and_preflight(self):
        want = run_block.expected_settings(SETTINGS)
        self.assertEqual(run_block.preflight_errors(GOOD, want, '15 seconds, 3 shots:  x', 2), [])
        bad = dict(GOOD, duration='5s', refs=[1], generate=[{'disabled': True}], dialogs=['Asset selector'])
        fail = run_block.preflight_errors(bad, want, '15 seconds, 3 shots: x', 2)
        for code in ('SETTING_duration', 'REF_COUNT', 'GENERATE_NOT_READY', 'DIALOG_OPEN'):
            self.assertIn(code, fail)
        self.assertIn('PROMPT_MISMATCH', run_block.preflight_errors(GOOD, want, 'other', 2))
        with self.assertRaises(run_block.Stop):
            run_block.expected_settings(dict(SETTINGS, generation_tier='Credits'))

    def test_never_clicks_generate(self):
        source = (SKILL / 'run_block.py').read_text()
        self.assertNotRegex(source, r"Generate['\"]\)\S*\.click|\.click\(\).*Generate")
        self.assertNotIn("innerText.trim()==='Generate');b[0].click", source)

    def _ctx(self, root: Path):
        return {'project': root, 'block': 'B01', 'pack_path': root / 'pack.json', 'refs': [{}, {}],
                'settings': SETTINGS, 'binding_path': root / 'b.json', 'prompt_path': root / 'p.txt'}

    def _bundle(self, root: Path, attach: str):
        (root / 'bundle').mkdir(exist_ok=True)
        slots = []
        for k in (1, 2):
            name = f'RW_{k:012d}.png'
            (root / 'bundle' / name).write_bytes(b'x')
            slots.append({'reference_token': f'Image{k}', 'alias_name': name, 'asset_id': f'AST_{k}',
                          'sha256': f'{k}' * 64, 'attach': attach,
                          'search_names': [name] if attach.startswith('SELECT') else []})
        return {'bundle_dir': str(root / 'bundle'), 'slots': slots}

    def test_attach_selects_from_uploads_and_records_reuse(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            page = FakePage(dict(GOOD, refs=[1]), rows=1)
            log = []
            with mock.patch.object(runway_ui_helper, 'prepare_upload_bundle',
                                   return_value=self._bundle(root, 'SELECT_EXISTING_RUNWAY_UPLOAD')), \
                 mock.patch.object(runway_ui_helper, 'record_runway_attach') as record, \
                 mock.patch.object(run_block, '_image_dims', return_value=(1920, 1080)):
                run_block.phase_attach(self._ctx(root), page, log)
            self.assertEqual([c.args[2] for c in record.call_args_list], ['reused', 'reused'])
            self.assertEqual(log[0], {'step': 'clear_composer_refs', 'removed': [1]})
            self.assertEqual(sum(1 for s in log if s['step'] == 'attached_from_uploads'), 2)

    def test_attach_stops_for_native_upload_and_missing_names(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with mock.patch.object(runway_ui_helper, 'prepare_upload_bundle',
                                   return_value=self._bundle(root, 'UPLOAD_NEW_VIA_NATIVE_CHOOSER')):
                with self.assertRaises(run_block.Stop) as stop:
                    run_block.phase_attach(self._ctx(root), FakePage(dict(GOOD, refs=[])), [])
            self.assertEqual(stop.exception.code, 'SLOT_NEEDS_NATIVE_UPLOAD')
            self.assertIn('--from-slot 2', stop.exception.next_action)
            # Listed name absent in Uploads -> recorded missing, then stop for upload.
            with mock.patch.object(runway_ui_helper, 'prepare_upload_bundle',
                                   return_value=self._bundle(root, 'SELECT_EXISTING_RUNWAY_UPLOAD')), \
                 mock.patch.object(runway_ui_helper, 'record_runway_attach') as record:
                with self.assertRaises(run_block.Stop) as stop:
                    run_block.phase_attach(self._ctx(root), FakePage(dict(GOOD, refs=[]), rows=0), [])
            self.assertEqual(stop.exception.code, 'SLOT_NEEDS_NATIVE_UPLOAD')
            self.assertEqual(record.call_args.args[2], 'missing')

    def test_attach_searches_generation_names_under_recents(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            bundle = self._bundle(root, 'SELECT_EXISTING_RUNWAY_UPLOAD')
            gen = 'Seedream 5_0 Pro - # 1_ SceneX'
            bundle['slots'][1]['search_names'] = [gen]
            bundle['slots'][1]['search_pills'] = {gen: 'Recents'}
            page = FakePage(dict(GOOD, refs=[]), rows=1)
            log = []
            with mock.patch.object(runway_ui_helper, 'prepare_upload_bundle', return_value=bundle), \
                 mock.patch.object(runway_ui_helper, 'record_runway_attach') as record, \
                 mock.patch.object(run_block, '_image_dims', return_value=(1920, 1080)):
                run_block.phase_attach(self._ctx(root), page, log)
            pills = [c[1] for c in page.calls if c[0] == 'js' and 'FILTER_PILL' in c[1]]
            self.assertIn('==="Uploads"', pills[0])
            self.assertIn('==="Recents"', pills[1])
            self.assertEqual([c.args[1:3] for c in record.call_args_list],
                             [('RW_000000000001.png', 'reused'), (gen, 'reused')])

    def test_aspect_mismatch_stops(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with mock.patch.object(runway_ui_helper, 'prepare_upload_bundle',
                                   return_value=self._bundle(root, 'SELECT_EXISTING_RUNWAY_UPLOAD')), \
                 mock.patch.object(runway_ui_helper, 'record_runway_attach'), \
                 mock.patch.object(run_block, '_image_dims', return_value=(1000, 1000)):
                with self.assertRaises(run_block.Stop) as stop:
                    run_block.phase_attach(self._ctx(root), FakePage(dict(GOOD, refs=[]), rows=1), [])
            self.assertEqual(stop.exception.code, 'SLOT_IMAGE_ASPECT_MISMATCH')

    def test_record_generate_numbers_retakes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / 'lanes/seedance').mkdir(parents=True)
            for rel in ('state.json', 'manifest.json', 'lanes/seedance/status.json'):
                (root / rel).write_text('{}', encoding='utf-8')
            (root / 'pack.json').write_text(json.dumps({'prompt_sha256': 'h'}), encoding='utf-8')
            (root / 'b.json').write_text(json.dumps({'session_url': 'u'}), encoding='utf-8')
            ctx = dict(self._ctx(root), refs=[{'asset_id': 'AST_1'}])
            with mock.patch.object(run_block, 'load_context', return_value=ctx):
                out = run_block.record_generate(root, 'B01', 'IN_QUEUE')
                self.assertEqual(len(out['written']), 3)
                job = json.loads((root / 'lanes/seedance/status.json').read_text())['provider_jobs'][0]
                self.assertEqual((job['block_id'], job['downloaded']), ('B01', False))
                run_block.record_generate(root, 'B01', 'IN_QUEUE')
                jobs = json.loads((root / 'lanes/seedance/status.json').read_text())['provider_jobs']
                self.assertEqual([j['local_output_id'] for j in jobs], ['B01_output1', 'B01_output2'])

    def test_run_stops_cleanly_without_shelf(self):
        with tempfile.TemporaryDirectory() as td:
            result = run_block.run(Path(td), 'B01')
            self.assertFalse(result['ok'])
            self.assertEqual(result['stop'], 'NOT_A_SHELF_BLOCK')
            self.assertTrue((Path(td) / 'lanes/seedance/run_block/runs.jsonl').is_file())


if __name__ == '__main__':
    unittest.main()
