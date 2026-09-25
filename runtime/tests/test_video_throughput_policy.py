from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class VideoThroughputPolicyTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding='utf-8')

    def test_default_identity_preflight_is_three_targeted_checks(self):
        standard = self.read('references/character_sheet_prompt_standard.md')
        self.assertIn('3/3 recognizable identity', standard)
        self.assertIn('actual generated clips', standard)
        self.assertIn('Fast fallback for failed headless edits', standard)
        self.assertIn('after one', standard)
        self.assertNotIn('Lock only if the same person is recognizable in 10/10', standard)
        self.assertNotIn('10/10 recognizable identity', self.read(
            'codex-skills/videodirector/references/character-identity-calibrations.md'))

    def test_prompting_keeps_user_intent_and_no_i2v_reference_roles(self):
        planner = self.read('runtime/templates/planner.md')
        prompting = self.read('codex-skills/seedance-prompt-en/seedance-prompting.md')
        review = self.read('codex-skills/seedance-prompt-en/prompt-review.md')
        self.assertIn('KEEP / ADAPT / HOLD', planner)
        self.assertIn('A review memo is not an adopted revision', planner)
        self.assertIn('One visually strong `SINGLE_CONTINUOUS_SHOT`', planner)
        self.assertIn('never copy its composition or treat it as an implicit start frame', prompting)
        self.assertIn('Zero extra layers is valid', prompting)
        self.assertIn('보류 메모 작성`은 기획 반영이 아니다', review)
        shared = self.read('codex-skills/seedance-prompt-en/seedance-shared-contract.md')
        self.assertIn('complete-front-head fallback', shared)


if __name__ == '__main__':
    unittest.main()
