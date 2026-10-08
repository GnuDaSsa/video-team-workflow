"""Instruction regression only; not a Flow browser/media integration test."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
REF = ROOT / 'codex-skills/videodirector/references/flow-malfoy-composite.md'


class FlowMalfoyKnowledgeTests(unittest.TestCase):
    def test_explicit_flow_entry(self):
        rail = (ROOT / 'runtime/AGENTS.md').read_text()
        self.assertIn('flow_malfoy_composite', rail)
        self.assertIn('추가 “말포이식” 호출', rail)
        self.assertIn('프로바이더 기본값은 Seedance', rail)

    def test_discoverable_from_director_and_editor(self):
        for path in ('codex-skills/videodirector/SKILL.md', 'runtime/templates/editor.md'):
            self.assertIn('flow-malfoy-composite.md', (ROOT / path).read_text())
        self.assertTrue(REF.is_file())

    def test_not_an_automatic_executor(self):
        rail = (ROOT / 'runtime/AGENTS.md').read_text()
        self.assertIn('Flow 실행\n  어댑터가 아니다', rail)
        self.assertIn('HOLD', rail)
        self.assertIn('TODO/stub', REF.read_text())

    def test_shared_craft_and_verification_boundaries(self):
        text = REF.read_text()
        for term in ('공통 모션그래픽 지식', 'BG', 'Subject', 'FG',
                     'frame = round(time_sec * fps)', '읽기 유지',
                     '실제 연기 검수', '기술 테스트 PASS', '전체 소스를 재생',
                     'ProRes 4444', '사용자에게 반려된 미감'):
            self.assertIn(term, text)

    def test_scope_and_provenance(self):
        text = REF.read_text()
        for term in ('clean footage', 'no-text', 'full_scene', '동시 워커',
                     '말포이 캐릭터', 'https://malfoy-meme-making.vercel.app/'):
            self.assertIn(term, text)


if __name__ == '__main__':
    unittest.main()
