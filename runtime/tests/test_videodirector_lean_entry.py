from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / 'codex-skills/videodirector/SKILL.md'


class VideoDirectorLeanEntryTests(unittest.TestCase):
    def test_entry_is_bounded_and_phase_specific(self):
        text = SKILL.read_text(encoding='utf-8')
        self.assertLess(len(text), 7000)
        for marker in (
            'Lean entry — classify before loading',
            'advice/audit',
            'one requested asset or revision',
            'new full production',
            'video-codex-runtime next --project <p>',
            'Read the selected Seedance version skill only when',
            'JEV-style advisory classification is **not** a default startup step',
            'explicit approval',
            'visual-only exception',
            'actual media/QC evidence',
        ):
            self.assertIn(marker, text)

    def test_phase_references_and_core_gates_remain(self):
        text = SKILL.read_text(encoding='utf-8')
        for name in ('modes.md', 'production-rules.md', 'output-formats.md',
                     'user-calibrations.md', 'role-split.md'):
            self.assertTrue((SKILL.parent / 'references' / name).is_file())
            self.assertIn(name, text)
        for marker in ('Gongnyang', 'one cut = one prompt', 'Seedance by default',
                       'CapCut', 'no unapproved agent', 'Confirm file/path/size/codec/duration'):
            self.assertIn(marker, text)


if __name__ == '__main__':
    unittest.main()
