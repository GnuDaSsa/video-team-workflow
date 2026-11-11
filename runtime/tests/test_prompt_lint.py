from __future__ import annotations
import os as _os, tempfile as _tempfile
_os.environ.setdefault('RUNWAY_UPLOAD_ALIAS_ROOT', _tempfile.mkdtemp(prefix='rwup-test-'))

import json
from pathlib import Path
import sys
import unittest

TESTS = Path(__file__).resolve().parent
sys.path.insert(0, str(TESTS))
sys.path.insert(0, str(TESTS.parent / 'scripts'))

import prompt_lint  # noqa: E402
import preprod  # noqa: E402
import test_preprod as tp  # noqa: E402
write = tp.write

POSITIVE = {
    'smooth_skin': ('seedance_prompt', 'Her skin stays smooth with soft highlights. Smooth skin, calm face.'),
    'text_prop': ('seedance_prompt', 'A researcher in a lab coat lifts a beaker.'),
    'garment_text': ('seedance_prompt', 'He wears a jacket with an embroidered logo.'),
    'screen_content': ('seedance_prompt', 'The monitor shows a circuit diagram.'),
    'screen_summon': ('seedance_prompt', 'Any screen shows only soft color shapes.'),
    'nasal_tube': ('seedance_prompt', 'A nasal feeding tube runs from her nostril.'),
    'foreign_office': ('seedance_prompt', 'Engineers talk in a glass-walled office.'),
    'start_frame': ('storyboard', 'refs: B01_START_FRAME'),
    'onscreen_text': ('seedance_prompt', 'A title card appears with the city name.'),
    'env_ref_props': ('image_prompt', 'A banquet hall with a bowl of ribbons.'),
    'paper_margin': ('image_prompt', 'Watercolor with cream paper showing through at the edges.'),
    'restraint_action': ('seedance_prompt', 'He is running down the corridor.'),
    'forced_metaphor': ('storyboard', 'A robot arm holds an ink brush.'),
}
NEGATIVE = {
    'smooth_skin': 'True-to-life skin with fine pores, no smooth skin.',
    'text_prop': 'No lab coat, no beaker; plain white gown.',
    'garment_text': 'Plain clothing without logos.',
    'screen_content': 'Hands move the board; no monitor shows anything.',
    'screen_summon': 'She walks the corridor.',
    'nasal_tube': 'A fine clear nasal feeding tube from the right nostril only, not an oxygen cannula.',
    'foreign_office': 'Korean engineers in a Korean office, utility poles outside.',
    'start_frame': 'Never add a START_FRAME ref.',
    'onscreen_text': 'No subtitles, no captions.',
    'env_ref_props': 'A banquet hall, glass and candle, edge-to-edge.',
    'paper_margin': 'Full-bleed, edge-to-edge image without margin.',
    'restraint_action': 'A slow walk and a head turn.',
    'forced_metaphor': 'The card is seated and the rack starts.',
}


class PromptLintTests(unittest.TestCase):
    def test_rule_data_complete(self):
        for rule in prompt_lint.RULES:
            for key in ('id', 'kinds', 'regex', 'reason', 'hint', 'source'):
                self.assertTrue(rule.get(key), (rule['id'], key))
        self.assertEqual(set(POSITIVE), {r['id'] for r in prompt_lint.RULES})

    def test_positive_and_negative_per_rule(self):
        for rid, (kind, text) in POSITIVE.items():
            purpose = 'environment' if rid == 'env_ref_props' else None
            ids = [h['id'] for h in prompt_lint.lint(text, kind, purpose=purpose)]
            self.assertIn(rid, ids, rid)
            self.assertNotIn(rid, [h['id'] for h in prompt_lint.lint(text, kind, [rid], purpose)])
        for rid, text in NEGATIVE.items():
            kind = POSITIVE[rid][0]
            purpose = 'environment' if rid == 'env_ref_props' else None
            self.assertNotIn(rid, [h['id'] for h in prompt_lint.lint(text, kind, purpose=purpose)], rid)

    def test_props_rule_needs_environment_purpose(self):
        self.assertEqual(prompt_lint.lint('a bowl of ribbons', 'image_prompt'), [])
        self.assertEqual(prompt_lint.lint('a bowl of ribbons', 'image_prompt', purpose='prop'), [])

    def test_brief_short(self):
        for kind in prompt_lint.KINDS:
            self.assertLessEqual(len(prompt_lint.rules_brief(kind).splitlines()), 15)
        with self.assertRaises(ValueError):
            prompt_lint.lint('x', 'bogus')


class LintInPipelineTests(tp.PreprodPipelineTests):
    def test_shelf_check_lint_warnings_and_allow(self) -> None:
        self.lock_all()
        preprod.write_shelf_brief(self.project, 'B01')
        path = preprod.shelf_dir(self.project, 'B01') / 'prompt.txt'
        write(path, self.prompt(**{'the brass handle': 'the brass handle in a lab coat'}))
        self.assertEqual(preprod.validate_shelf_prompt(self.project, 'B01'), [])
        warns = preprod.lint_warnings(self.project, 'shelf', 'B01')
        self.assertEqual([w['id'] for w in warns], ['text_prop'])
        sb = json.loads((self.pre / '02_storyboard/storyboard.json').read_text())
        sb['blocks'][0]['lint_allow'] = ['text_prop']
        write(self.pre / '02_storyboard/storyboard.json', sb)
        self.assertEqual(preprod.lint_warnings(self.project, 'shelf', 'B01'), [])

    def test_copy_line_warns_only(self) -> None:
        self.concept(); preprod.lock_stage(self.project, 'concept', '좋아 B안으로')
        self.bible(); preprod.lock_stage(self.project, 'bible')
        self.storyboard()
        self.assertEqual(preprod.VALIDATORS['storyboard'](self.project), [])
        ids = [w['id'] for w in preprod.lint_warnings(self.project, 'storyboard')]
        self.assertEqual(ids.count('missing_copy_line'), 2)
        sb = json.loads((self.pre / '02_storyboard/storyboard.json').read_text())
        sb['blocks'][0]['shots'][0]['copy_line'] = '문을 연다'
        sb['blocks'][0]['shots'][1]['copy_line'] = '(insert)'
        write(self.pre / '02_storyboard/storyboard.json', sb)
        self.assertEqual(preprod.lint_warnings(self.project, 'storyboard'), [])
        self.assertEqual(preprod.VALIDATORS['storyboard'](self.project), [])

    def test_image_prompt_lint(self) -> None:
        self.lock_all()
        write(self.pre / '03_image_prompts/REF_DOOR.prompt.txt',
              'Environment reference, a hall with a bowl of ribbons, cream paper showing through.')
        ids = {w['id'] for w in preprod.lint_warnings(self.project, 'images')}
        self.assertEqual(ids, {'env_ref_props', 'paper_margin'})


if __name__ == '__main__':
    unittest.main()
