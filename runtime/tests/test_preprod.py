from __future__ import annotations
import os as _os, tempfile as _tempfile
_os.environ.setdefault('RUNWAY_UPLOAD_ALIAS_ROOT', _tempfile.mkdtemp(prefix='rwup-test-'))  # never the real ledger

import contextlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from types import SimpleNamespace

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
os.environ.setdefault('VIDEO_TEAM_RUNTIME_SCRIPTS', str(SCRIPTS))
sys.path.insert(0, str(SCRIPTS))

import claude_author  # noqa: E402
import lane_gates  # noqa: E402
from unittest import mock  # noqa: E402
import media_registry  # noqa: E402
import preprod  # noqa: E402
import runway_ui_helper  # noqa: E402
import video_codex_runtime  # noqa: E402

STYLE = ('Grounded cinematic live action, soft overcast daylight, teal and warm amber palette, '
         'natural skin texture, shallow depth of field, gentle film grain.')
IDENTITY = ('Mina: woman in her late twenties, shoulder-length black bob, cream trench coat, '
            'small silver hoop earrings, calm attentive expression.')


def write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) if not isinstance(value, str) else value,
                    encoding='utf-8')


class PreprodPipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        old = video_codex_runtime.PROJECT_ROOT
        video_codex_runtime.PROJECT_ROOT = self.root / 'projects'
        try:
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                video_codex_runtime.init_project(SimpleNamespace(slug='preprod-test', brief='test', mode='standard_i2v'))
            self.project = Path(out.getvalue().strip())
        finally:
            video_codex_runtime.PROJECT_ROOT = old
        manifest = json.loads((self.project / 'manifest.json').read_text())
        manifest['knowledge_routing']['enabled'] = False
        write(self.project / 'manifest.json', manifest)
        self.pre = preprod.init(self.project)
        if self.mode:
            claude_author.set_mode(self.project, self.mode, 'test')

    mode = 'codex'

    def tearDown(self) -> None:
        self.tmp.cleanup()

    # -- fixtures --------------------------------------------------------------
    def concept(self) -> None:
        write(self.pre / '00_concept/concept_options.md',
              '# Options\n\n## Option A\nx\n\n## Option B\ny\n\n## Option C\nz\n')
        write(self.pre / '00_concept/concept_lock.json', {
            'title': 'Door', 'logline': 'A woman steps through a door into her past.', 'audience': 'public',
            'mode': 'contest', 'medium': 'live_action', 'aspect_ratio': '16:9', 'target_runtime_sec': 30,
            'emotional_arc': {'hook': 'door', 'build': 'walk', 'peak': 'reveal', 'out': 'smile'},
            'must_avoid': ['text on screen'], 'selected_option': 'B'})

    def bible(self) -> None:
        write(self.pre / '01_bible/style_bible.json', {
            'palette_hex': ['#1F4E5F', '#E8A54B', '#F2EDE4'], 'lighting': 'overcast 5600K, key:fill 2:1',
            'texture': 'fine grain', 'lens_grammar': '35mm and 85mm', 'forbidden_looks': ['neon glow'],
            'style_block_en': STYLE,
            'characters': [{'id': 'CHAR_MINA', 'identity_block_en': IDENTITY, 'sheet_ref_id': 'REF_MINA_SHEET'}],
            'locations': [{'id': 'LOC_DOOR', 'description_en': 'A weathered blue wooden door in a brick alley.'}]})

    def storyboard(self, end: float = 15) -> None:
        write(self.pre / '02_storyboard/storyboard.json', {'blocks': [{
            'block_id': 'B01', 'order': 1, 'purpose': 'Mina opens the door', 'duration_sec': 15,
            'audio_route': 'native_diegetic_no_dialogue', 'cast': ['CHAR_MINA'], 'location_id': 'LOC_DOOR',
            'refs': ['REF_MINA_SHEET', 'REF_DOOR'], 'end_frame': 'Mina framed in the open doorway, warm light behind.',
            'shots': [
                {'shot_id': 'B01_S1', 'start_sec': 0, 'end_sec': 6, 'shot_size': 'wide shot', 'angle': 'eye level',
                 'camera_move': 'slow push in', 'composition': 'door centered, Mina left third',
                 'action': 'Mina walks to the door', 'must_include': ['brass handle']},
                {'shot_id': 'B01_S2', 'start_sec': 6, 'end_sec': end, 'shot_size': 'close-up', 'angle': 'low angle',
                 'camera_move': 'static', 'composition': 'face right third', 'action': 'she opens it and smiles'}]}]})

    def image_plan(self) -> None:
        refs = []
        for rid, purpose in (('REF_MINA_SHEET', 'identity'), ('REF_DOOR', 'environment')):
            write(self.pre / f'03_image_prompts/{rid}.prompt.txt',
                  f'Photorealistic reference image for {rid.lower()}, neutral studio light, full detail.')
            src = self.root / f'{rid}.png'; src.write_bytes(rid.encode())
            asset = media_registry.ingest(self.project, src, kind='image', state='candidate', work_item_id=rid)
            asset = media_registry.promote(self.project, asset['asset_id'])
            refs.append({'ref_id': rid, 'purpose': purpose, 'asset_id': asset['asset_id'],
                         'role_en': 'Mina identity' if purpose == 'identity' else 'blue door alley'})
        write(self.pre / '03_image_prompts/image_plan.json', {'references': refs})

    def prompt(self, **edits) -> str:
        text = (f'15 seconds, 2 shots:\n{STYLE}\n{IDENTITY}\n'
                '@Image1 is Mina. @Image2 is the blue door alley.\n'
                'Shot 1 (0-6s): wide shot, eye level, slow push in as Mina walks to the door and reaches the brass handle.\n'
                'Shot 2 (6-15s): close-up, low angle, static; she opens the door and a quiet smile forms.\n'
                'End on Mina framed in the open doorway, warm light behind.')
        for old, new in edits.items():
            text = text.replace(old, new)
        return text

    def lock_all(self) -> None:
        self.concept(); preprod.lock_stage(self.project, 'concept', '좋아 B안으로')
        self.bible(); preprod.lock_stage(self.project, 'bible')
        self.storyboard(); preprod.lock_stage(self.project, 'storyboard', '콘티 확정')
        self.image_plan(); preprod.lock_stage(self.project, 'images')

    # -- tests -----------------------------------------------------------------
    def test_concept_lock_requires_authoring_mode(self) -> None:
        manifest = json.loads((self.project / 'manifest.json').read_text())
        manifest.pop('authoring'); write(self.project / 'manifest.json', manifest)
        self.concept()
        with self.assertRaisesRegex(ValueError, 'AUTHOR_MODE_UNSET'):
            preprod.lock_stage(self.project, 'concept', 'B안')
        with self.assertRaisesRegex(ValueError, 'USER_APPROVAL_REQUIRED'):
            claude_author.set_mode(self.project, 'claude', '')

    def test_stages_lock_in_order_and_require_user_approval(self) -> None:
        self.concept()
        with self.assertRaisesRegex(ValueError, 'USER_APPROVAL_REQUIRED'):
            preprod.lock_stage(self.project, 'concept')
        self.bible()
        with self.assertRaisesRegex(ValueError, 'UPSTREAM_NOT_LOCKED'):
            preprod.lock_stage(self.project, 'bible')
        preprod.lock_stage(self.project, 'concept', 'B안')
        self.assertEqual(preprod.lock_state(self.project, 'concept')['state'], 'LOCKED')
        self.assertEqual(preprod.status(self.project)['next_stage'], 'bible')

    def test_unfilled_template_cannot_be_locked(self) -> None:
        errors = preprod.VALIDATORS['concept'](self.project)
        self.assertTrue(any('unfilled_placeholder' in e for e in errors), errors)
        with self.assertRaisesRegex(ValueError, 'CONCEPT_INVALID'):
            preprod.lock_stage(self.project, 'concept', 'ok')

    def test_storyboard_rejects_gaps_vocab_and_duration(self) -> None:
        self.concept(); preprod.lock_stage(self.project, 'concept', 'ok')
        self.bible(); preprod.lock_stage(self.project, 'bible')
        self.storyboard(end=12)
        errors = preprod.validate_storyboard(self.project)
        self.assertTrue(any('shots_end_12' in e for e in errors))
        board = json.loads((self.pre / '02_storyboard/storyboard.json').read_text())
        board['blocks'][0]['refs'] = ['REF_DOOR']
        write(self.pre / '02_storyboard/storyboard.json', board)
        self.assertTrue(any('refs_missing_sheet_of_CHAR_MINA' in e for e in preprod.validate_storyboard(self.project)))
        board['blocks'][0]['refs'] = ['REF_MINA_SHEET', 'REF_DOOR']
        board['blocks'][0]['shots'][0]['camera_move'] = 'cinematic swoop'
        write(self.pre / '02_storyboard/storyboard.json', board)
        self.assertTrue(any('bad_camera_move' in e for e in preprod.validate_storyboard(self.project)))

    def test_concept_music_none_skips_music_lane(self) -> None:
        self.concept()
        lock = json.loads((self.pre / '00_concept/concept_lock.json').read_text()); lock['music'] = 'none'
        write(self.pre / '00_concept/concept_lock.json', lock)
        preprod.lock_stage(self.project, 'concept', '음악 없이')
        ok, reason = lane_gates.gate_check(self.project, 'music')
        self.assertFalse(ok); self.assertIn('SKIPPED_BY_CONCEPT_LOCK', reason)
        self.assertNotIn('music', lane_gates.next_actions(self.project)['next_lanes'])
        self.bible(); preprod.lock_stage(self.project, 'bible')
        self.storyboard(); preprod.lock_stage(self.project, 'storyboard', 'ok')
        lanes = lane_gates.next_actions(self.project)
        self.assertEqual(lanes['lanes']['director']['status'], 'DONE')
        self.assertEqual(lanes['lanes']['planner']['status'], 'DONE')
        self.assertEqual(lanes['next_lanes'][:1], ['image_creator_01'])

    def test_storyboard_lock_derives_planner_files(self) -> None:
        self.lock_all()
        block_map = json.loads((self.project / 'lanes/planner/multi_reference_block_map.json').read_text())
        self.assertEqual(block_map['blocks'][0]['covered_cuts'], ['B01_S1', 'B01_S2'])
        attrs = json.loads((self.project / 'lanes/planner/video_attributes.json').read_text())
        self.assertEqual(attrs['blocks'][0]['cameras'], ['slow_push', 'static'])

    def test_image_lane_auto_phase_is_production_once_prompts_exist(self) -> None:
        self.concept(); preprod.lock_stage(self.project, 'concept', '좋아 B안으로')
        self.bible(); preprod.lock_stage(self.project, 'bible')
        self.storyboard(); preprod.lock_stage(self.project, 'storyboard', '콘티 확정')
        phase = video_codex_runtime.lane_phase
        self.assertIsNone(phase(self.project, 'image_creator_02'))  # no prompts yet: authoring route
        write(self.pre / '03_image_prompts/REF_MINA_SHEET.prompt.txt', 'Photorealistic Mina identity sheet, studio light.')
        write(self.pre / '03_image_prompts/REF_DOOR.prompt.txt', 'Photorealistic blue door alley, overcast light.')
        write(self.pre / '03_image_prompts/image_plan.json', {'references': [
            {'ref_id': 'REF_MINA_SHEET', 'purpose': 'identity', 'role_en': 'Mina identity', 'asset_id': None},
            {'ref_id': 'REF_DOOR', 'purpose': 'environment', 'role_en': 'blue door alley', 'asset_id': None}]})
        self.assertEqual(phase(self.project, 'image_creator_02'), 'production')
        self.assertEqual(video_codex_runtime.model_routing.resolve('image_creator_02', 'production')['route_key'],
                         'image_creator_02:production')
        self.assertIsNone(phase(self.project, 'image_creator_02', 'prompting'))
        with self.assertRaises(SystemExit):
            phase(self.project, 'planner', 'production')

    def test_upstream_edit_makes_lock_stale(self) -> None:
        self.lock_all()
        board = json.loads((self.pre / '02_storyboard/storyboard.json').read_text())
        board['blocks'][0]['purpose'] = 'changed'
        write(self.pre / '02_storyboard/storyboard.json', board)
        self.assertEqual(preprod.lock_state(self.project, 'storyboard')['state'], 'STALE')
        self.assertEqual(preprod.lock_state(self.project, 'images')['state'], 'STALE')

    def test_shelf_prompt_enforces_language_limit_composition_and_tokens(self) -> None:
        self.lock_all()
        preprod.write_shelf_brief(self.project, 'B01')
        shelf = self.pre / '04_shelf/B01'
        cases = {
            'shelf_shot_1_missing_camera_move': self.prompt(**{'slow push in': 'drift'}),
            'shelf_shot_1_missing_must': self.prompt(**{'brass handle': 'knob'}),
            'shelf_style_block_not_verbatim': self.prompt(**{'gentle film grain': 'grain'}),
            'shelf_tokens_': self.prompt(**{'@Image2 is': '@Image3 is'}),
            'shelf_first_line_must_be': self.prompt(**{'15 seconds, 2 shots:': '10 seconds, 2 shots:'}),
            'shelf_prompt_over_3500': self.prompt() + ' x' * 1800,
            'shelf_prompt_not_english': self.prompt() + '\n' + '한국어 설명 문장입니다 ' * 60,
        }
        for code, text in cases.items():
            (shelf / 'prompt.txt').write_text(text, encoding='utf-8')
            errors = preprod.validate_shelf_prompt(self.project, 'B01')
            self.assertTrue(any(code in e for e in errors), (code, errors))
        (shelf / 'prompt.txt').write_text(self.prompt(), encoding='utf-8')
        self.assertEqual(preprod.validate_shelf_prompt(self.project, 'B01'), [])

    def test_shelf_lock_release_verify_and_production_gates(self) -> None:
        self.lock_all()
        preprod.write_shelf_brief(self.project, 'B01')
        shelf = self.pre / '04_shelf/B01'
        (shelf / 'prompt.txt').write_text(self.prompt(), encoding='utf-8')
        lock = preprod.lock_shelf(self.project, 'B01')
        self.assertIsNone(lock['released'])
        self.assertIn('shelf_not_released_by_user', preprod.verify_shelf(self.project, 'B01'))
        ok, reason = lane_gates.gate_check(self.project, 'seedance')
        self.assertTrue(ok); self.assertIn('SHELF_NOT_RELEASED', reason)
        with self.assertRaisesRegex(ValueError, 'USER_APPROVAL_REQUIRED'):
            preprod.release_shelf(self.project, ['B01'], '')
        preprod.release_shelf(self.project, ['B01'], '프롬프트 다 좋아, 제작 시작')
        self.assertEqual(preprod.verify_shelf(self.project, 'B01'), [])
        self.assertEqual(preprod.released_blocks(self.project), ['B01'])
        self.assertIn('COPY_PASTE_ONLY', lane_gates.gate_check(self.project, 'seedance')[1])
        # Production may paste only the shelf prompt with its pack.
        self.assertIn('PRODUCTION_PASTES_ONLY', runway_ui_helper.shelf_paste_error(
            self.project / 'lanes/seedance/prompts/x_prompt.txt', None))
        self.assertIn('PRODUCTION_REQUIRES_SHELF_PACK', runway_ui_helper.shelf_paste_error(shelf / 'prompt.txt', None))
        self.assertEqual(runway_ui_helper.shelf_paste_error(shelf / 'prompt.txt', str(shelf / 'pack.json')), '')
        # Any edit after release closes production again.
        (shelf / 'prompt.txt').write_text(self.prompt() + ' Extra.', encoding='utf-8')
        self.assertIn('shelf_file_changed:prompt.txt', preprod.verify_shelf(self.project, 'B01'))
        self.assertTrue(runway_ui_helper.shelf_paste_error(shelf / 'prompt.txt', str(shelf / 'pack.json')))

    def _next(self) -> dict:
        out = io.StringIO()
        with mock.patch.object(video_codex_runtime.lane_sessions, 'load_policy',
                               return_value={'auto_lane_sessions': True, 'approval_quote': 'q'}), \
             contextlib.redirect_stdout(out):
            video_codex_runtime.next_cmd(SimpleNamespace(project=str(self.project)))
        return json.loads(out.getvalue())['default_execution']

    def test_new_project_director_flow_asks_user_only_at_the_three_gates(self) -> None:
        self.assertEqual(self._next()['action'], 'DIRECTOR_IN_MAIN_THREAD')        # P0 in the main thread
        self.concept()
        gate = self._next()
        self.assertEqual((gate['action'], gate['gate']), ('ASK_USER', 'concept_approval'))
        preprod.lock_stage(self.project, 'concept', 'B안')
        self.bible(); self.assertEqual(self._next()['action'], 'LOCK_STAGE')
        preprod.lock_stage(self.project, 'bible')
        nxt = self._next()                                                         # music session (concept has music)
        self.assertEqual(nxt['action'], 'DISPATCH_LANE_SESSION')
        self.assertIn('--lanes music', nxt['commands'][0])
        no_music = mock.patch.object(lane_gates.preprod, 'concept_without_music', return_value=True)
        no_music.start(); self.addCleanup(no_music.stop)                           # rest of the flow: no-music concept
        self.assertIn('--lanes planner', self._next()['commands'][0])
        self.storyboard()
        gate = self._next()
        self.assertEqual((gate['action'], gate['gate']), ('ASK_USER', 'storyboard_approval'))
        preprod.lock_stage(self.project, 'storyboard', '콘티 확정')
        self.image_plan(); preprod.lock_stage(self.project, 'images')
        nxt = self._next()
        self.assertEqual(nxt['action'], 'DISPATCH_LANE_SESSION')
        self.assertIn('--phase prompting', nxt['commands'][0])                    # P4 shelf session
        preprod.write_shelf_brief(self.project, 'B01')
        (self.pre / '04_shelf/B01/prompt.txt').write_text(self.prompt(), encoding='utf-8')
        preprod.lock_shelf(self.project, 'B01')
        gate = self._next()
        self.assertEqual((gate['action'], gate['gate']), ('ASK_USER', 'shelf_release'))
        preprod.release_shelf(self.project, ['B01'], '릴리스')
        nxt = self._next()
        self.assertIn('--phase production', nxt['commands'][0])                   # P5 production session

    def test_upload_bundle_from_shelf_pack_is_ordered_ascii_clones(self) -> None:
        self.lock_all()
        preprod.write_shelf_brief(self.project, 'B01')
        shelf = self.pre / '04_shelf/B01'
        (shelf / 'prompt.txt').write_text(self.prompt(), encoding='utf-8')
        preprod.lock_shelf(self.project, 'B01')
        bundle = runway_ui_helper.prepare_upload_bundle(
            self.project, 'B01', shelf / 'pack.json', self.root / 'RunwayUpload')
        names = [s['alias_name'] for s in bundle['slots']]
        self.assertEqual([s['reference_token'] for s in bundle['slots']], ['Image1', 'Image2'])
        for slot, name in zip(bundle['slots'], names):
            path = Path(bundle['bundle_dir']) / name
            self.assertTrue(path.is_file() and not path.is_symlink() and name.isascii())
            # Content-addressed: same bytes, same name in every block/project.
            self.assertEqual(name, runway_ui_helper.runway_upload_name(slot['sha256'], path.suffix))
            self.assertEqual(slot['attach'], 'UPLOAD_NEW_VIA_NATIVE_CHOOSER')

    def test_runway_uploads_ledger_reuses_before_any_upload(self) -> None:
        self.lock_all()
        preprod.write_shelf_brief(self.project, 'B01')
        shelf = self.pre / '04_shelf/B01'
        (shelf / 'prompt.txt').write_text(self.prompt(), encoding='utf-8')
        preprod.lock_shelf(self.project, 'B01')
        root = self.root / 'RunwayUpload'
        first = runway_ui_helper.prepare_upload_bundle(self.project, 'B01', shelf / 'pack.json', root)
        slot = first['slots'][0]
        bundle_file = Path(first['bundle_dir']) / slot['alias_name']
        canonical = getattr(runway_ui_helper, '_canonical', runway_ui_helper)
        with mock.patch.dict(os.environ, {'RUNWAY_UPLOAD_ALIAS_ROOT': str(root)}), \
             mock.patch.object(canonical, 'UPLOAD_ALIAS_ROOT', root), \
             mock.patch.object(canonical, 'run_verified', return_value=0) as run:
            # Nothing in Runway yet: the native chooser may upload it.
            self.assertEqual(runway_ui_helper.upload_block_reason(bundle_file), '')
            runway_ui_helper.record_runway_attach(slot['sha256'], slot['alias_name'], 'uploaded',
                                                  project='p', asset_id=slot['asset_id'])
            # Runway holds the bytes now: the chooser refuses and names the entry to select.
            reason = runway_ui_helper.upload_block_reason(bundle_file)
            self.assertIn('UPLOAD_BLOCKED_ALREADY_IN_RUNWAY_UPLOADS', reason)
            self.assertIn(slot['alias_name'], reason)
            with self.assertRaises(ValueError):
                runway_ui_helper.cmd_picker_select(SimpleNamespace(path=str(bundle_file)))
            run.assert_not_called()
            # The next block (or a project holding a copy) is told to select, not upload.
            again = runway_ui_helper.prepare_upload_bundle(self.project, 'B01', shelf / 'pack.json', root)
            self.assertEqual(again['slots'][0]['attach'], 'SELECT_EXISTING_RUNWAY_UPLOAD')
            self.assertEqual(again['slots'][0]['search_names'], [slot['alias_name']])
            # A name searched and absent is dropped; then uploading is allowed again.
            runway_ui_helper.record_runway_attach(slot['sha256'], slot['alias_name'], 'missing')
            self.assertEqual(runway_ui_helper.upload_block_reason(bundle_file), '')

    def test_bundle_clone_of_old_source_survives_next_slot_sweep(self) -> None:
        self.lock_all()
        preprod.write_shelf_brief(self.project, 'B01')
        shelf = self.pre / '04_shelf/B01'
        (shelf / 'prompt.txt').write_text(self.prompt(), encoding='utf-8')
        preprod.lock_shelf(self.project, 'B01')
        for asset in media_registry.list_assets(self.project):
            if Path(asset['current_path']).is_file():
                os.utime(asset['current_path'], (0, 0))
        bundle = runway_ui_helper.prepare_upload_bundle(
            self.project, 'B01', shelf / 'pack.json', self.root / 'RunwayUpload')
        for slot in bundle['slots']:
            self.assertTrue((Path(bundle['bundle_dir']) / slot['alias_name']).is_file())

    def test_seed_runway_library_from_old_receipts_as_candidates(self) -> None:
        root = self.root / 'RunwayUpload'
        receipt = self.root / 'rt/proj1/lanes/seedance/upload_alias_receipts.jsonl'
        sha = 'a' * 64
        write(receipt, json.dumps({'ts': '2026-10-01T00:00:00+09:00', 'sha256': sha,
                                   'alias_name': 'B01__IMAGE1__ABCD.png'}) + '\n')
        result = runway_ui_helper.seed_runway_library(self.root / 'rt', root)
        self.assertEqual(result['names_added'], 1)
        library = runway_ui_helper.load_runway_library(root)
        self.assertEqual(runway_ui_helper.runway_search_names(library, sha), ['B01__IMAGE1__ABCD.png'])
        self.assertEqual(library['entries'][sha]['names']['B01__IMAGE1__ABCD.png']['status'], 'candidate')
        # The ledger at the root is never swept.
        os.utime(runway_ui_helper.runway_library_path(root), (0, 0))
        runway_ui_helper.sweep_stale_upload_aliases(root)
        self.assertTrue(runway_ui_helper.runway_library_path(root).is_file())


class ClaudeModeTests(unittest.TestCase):
    mode = 'claude'
    setUp = PreprodPipelineTests.setUp
    tearDown = PreprodPipelineTests.tearDown
    concept = PreprodPipelineTests.concept
    bible = PreprodPipelineTests.bible

    def options_only(self):
        write(self.pre / '00_concept/concept_options.md', '# Options\n\n## Option A\nx\n\n## Option B\ny\n\n## Option C\nz\n')

    def lock_only(self):
        backup = (self.pre / '00_concept/concept_options.md').read_text()
        self.concept()
        write(self.pre / '00_concept/concept_options.md', backup)

    def fake_claude(self, writer):
        def run(project, prompt, model, resume=''):
            writer(prompt)
            return {'session_id': 'S1', 'result': '요약', 'models': ['claude-opus-5-5'], 'total_cost_usd': 0.1}
        return mock.patch.object(claude_author, 'run_claude', side_effect=run)

    def test_codex_edit_of_claude_file_cannot_lock(self) -> None:
        with self.fake_claude(lambda prompt: self.options_only()):
            claude_author.author(self.project, 'concept-options')
        with self.fake_claude(lambda prompt: self.lock_only()):
            out = claude_author.author(self.project, 'concept-lock', feedback='B안으로, 밤 장면 추가')
        self.assertTrue(out['ok'], out)
        preprod.lock_stage(self.project, 'concept', 'B안')
        self.bible()  # Codex wrote the bible itself in claude mode
        with self.assertRaisesRegex(ValueError, 'CLAUDE_MODE_AUTHORSHIP'):
            preprod.lock_stage(self.project, 'bible')
        with self.fake_claude(lambda prompt: self.bible()):
            claude_author.author(self.project, 'bible')
        preprod.lock_stage(self.project, 'bible')
        self.assertEqual(preprod.lock_state(self.project, 'bible')['state'], 'LOCKED')

    def test_validator_errors_are_fed_back_until_clean(self) -> None:
        prompts = []
        def writer(prompt):
            prompts.append(prompt)
            if len(prompts) == 1:
                write(self.pre / '00_concept/concept_options.md', '## Option A\nonly one\n')
            else:
                self.options_only()
        with self.fake_claude(writer):
            out = claude_author.author(self.project, 'concept-options')
        self.assertTrue(out['ok']); self.assertEqual(out['attempts'], 2)
        self.assertIn('concept_options_need_3_options', prompts[1])

    def test_write_outside_stage_is_rejected(self) -> None:
        def writer(prompt):
            self.options_only(); write(self.project / 'brief.md', 'rewritten by author')
        with self.fake_claude(writer), self.assertRaisesRegex(ValueError, 'CLAUDE_WROTE_OUTSIDE_STAGE'):
            claude_author.author(self.project, 'concept-options')

    def test_concurrent_lane_and_docs_writes_do_not_fail_author_run(self) -> None:
        def writer(prompt):
            self.options_only()
            write(self.project / 'lanes/seedance/run.production.log', 'lane log')
            write(self.project / 'lanes/seedance/status.json', {'status': 'RUNNING'})
            write(self.project / 'docs/codex_handoff_20261029.md', 'director handoff')
        with self.fake_claude(writer):
            self.assertTrue(claude_author.author(self.project, 'concept-options')['ok'])

    def test_author_run_inside_lane_session_is_refused(self) -> None:
        with mock.patch.dict(os.environ, {'VIDEO_TEAM_LANE': 'image_creator_02'}), \
                self.assertRaisesRegex(ValueError, 'AUTHOR_RUN_IN_LANE'):
            claude_author.author(self.project, 'concept-options')

    def test_codex_mode_refuses_author_run(self) -> None:
        claude_author.set_mode(self.project, 'codex', '코덱스로')
        with self.assertRaisesRegex(ValueError, 'AUTHOR_MODE_NOT_CLAUDE'):
            claude_author.author(self.project, 'concept-options')

    def test_cli_denies_writes_to_skills_wiki_and_runtime(self) -> None:
        cmd = claude_author.claude_cmd(self.project, 'x', '')
        self.assertIn('Bash', cmd)
        self.assertIn(f'Write(/{claude_author.SKILLS}/**)', cmd)
        self.assertIn(f'Edit(/{claude_author.WIKI}/**)', cmd)


class LegacyStatusGuessTests(unittest.TestCase):
    def test_whole_word_status_guess(self) -> None:
        guess = lane_gates._guess_legacy_status
        self.assertEqual(guess('UNLOCKED'), 'UNKNOWN')
        self.assertEqual(guess('NOT_READY'), 'UNKNOWN')
        self.assertEqual(guess('BYPASS'), 'UNKNOWN')
        self.assertEqual(guess('HOLD_EXPLICIT_AUTHOR_MODEL'), 'BLOCKED')
        self.assertEqual(guess('QC_PASS_PARTIAL'), 'PARTIAL_DONE')
        self.assertEqual(guess('GENERATING_B03'), 'RUNNING')

    def test_negated_inflight_marker_is_not_inflight(self) -> None:
        markers = ('submitted', 'generating')
        self.assertFalse(lane_gates._has_affirmed_marker('prompt not submitted yet', markers))
        self.assertFalse(lane_gates._has_affirmed_marker('nothing generating', markers))
        self.assertTrue(lane_gates._has_affirmed_marker('b03 submitted; card generating', markers))


if __name__ == '__main__':
    unittest.main()
