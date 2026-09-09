"""Documentation routing regression, not a visual-fidelity validator."""
from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[2]
class BlenderPrevisBranch(unittest.TestCase):
    def test_both_versions_route_to_single_owner(self):
        for name in ('seedance-prompt-en', 'seedance25-prompt-en'):
            self.assertIn('blender-previs-prompting.md', (ROOT/'codex-skills'/name/'SKILL.md').read_text())
        self.assertFalse((ROOT/'codex-skills/seedance25-prompt-en/blender-previs-prompting.md').exists())
    def test_review_and_failure_contract(self):
        base=ROOT/'codex-skills/seedance-prompt-en'
        self.assertIn('blender-previs-prompting.md',(base/'prompt-review.md').read_text())
        text=(base/'blender-previs-prompting.md').read_text()
        for marker in ('MOTION_GUIDE','SOURCE_RESTYLE','FAIL_PROXY_APPEARANCE_LEAK','collision radii','lineage','full temporal/playback QC','not an implemented automatic'):
            self.assertIn(marker,text)
if __name__ == '__main__': unittest.main()
