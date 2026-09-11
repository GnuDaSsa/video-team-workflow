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
    def test_motion_example_does_not_edit_source(self):
        text=(ROOT/'codex-skills/seedance-prompt-en/blender-previs-prompting.md').read_text()
        section=text.split('### MOTION_GUIDE —',1)[1].split('### SOURCE_RESTYLE —',1)[0]
        example='\n'.join(line for line in section.splitlines() if line.startswith('>'))
        self.assertIn('새 2D 액션 애니메이션을 생성한다',example)
        self.assertIn('@Video1은 두 기체의 동선 참고다',example)
        for token in ('@Image1','@Image2','@Image3'):
            self.assertIn(token,example)
        for editing_instruction in ('원본 장면으로 편집','매 프레임 재작화','교체한다'):
            self.assertNotIn(editing_instruction,example)
    def test_restyle_remains_explicit_and_reviews_are_scoped(self):
        text=(ROOT/'codex-skills/seedance-prompt-en/blender-previs-prompting.md').read_text()
        restyle=text.split('### SOURCE_RESTYLE —',1)[1].split('## 4.',1)[0]
        self.assertIn('@Video1을 원본 장면으로 편집한다',restyle)
        self.assertIn('Use only when editing/restyling the existing sequence is actually requested',text)
        self.assertIn('For MOTION_GUIDE, first check',text)
        self.assertIn('For SOURCE_RESTYLE, first validate',text)
        self.assertIn('changed framing is not itself a failure',text)
if __name__ == '__main__': unittest.main()
