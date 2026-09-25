from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class MusicGenerationBoundaryTests(unittest.TestCase):
    def test_music_skill_and_lane_stop_after_generation(self):
        skill = (ROOT / 'codex-skills/music-director/SKILL.md').read_text()
        template = (ROOT / 'runtime/templates/music.md').read_text()
        reference = (ROOT / 'codex-skills/music-director/references/vocal-naturalness-qc.md').read_text()
        self.assertIn('Suno generation boundary', skill)
        self.assertIn('user alone chooses and downloads', template)
        self.assertIn('PENDING_USER_AUDIO', template)
        self.assertIn('pre-generation only', reference)
        for obsolete in (
            'download via the visible card/list menu',
            'present TOP1–3',
            'after download, verify actual duration',
            'Only the first status permits a recommendation',
            'Listen to the full vocal performance',
        ):
            self.assertNotIn(obsolete, skill + template + reference)


if __name__ == '__main__':
    unittest.main()
