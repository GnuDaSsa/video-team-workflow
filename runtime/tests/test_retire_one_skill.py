from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from retire_one_skill_from_codex import retire

NAME = 'jeongseon-video-typography'


class RetireOneSkillTests(unittest.TestCase):
    def test_preflight_and_archive_preserve_unrelated_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'repo'; home = Path(tmp) / 'home'
            live = home / '.codex/skills' / NAME
            live.mkdir(parents=True); (live / 'SKILL.md').write_text('retired content')
            other = home / '.codex/skills/keep.md'; other.write_text('keep')
            self.assertTrue(retire(NAME, root, home, check_only=True)['active'])
            self.assertTrue(live.exists())
            result = retire(NAME, root, home)
            self.assertFalse(live.exists())
            self.assertEqual((Path(result['archive']) / 'SKILL.md').read_text(), 'retired content')
            self.assertEqual(other.read_text(), 'keep')
            self.assertFalse(retire(NAME, root, home)['active'])

    def test_refuses_unlisted_invalid_or_still_owned_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); home = root / 'home'
            for name in ('videodirector', '../outside', ''):
                with self.assertRaises(ValueError): retire(name, root, home)
            source = root / 'codex-skills' / NAME; source.mkdir(parents=True)
            with self.assertRaisesRegex(ValueError, 'SOURCE_STILL_PRESENT'):
                retire(NAME, root, home)

    def test_canonical_source_is_removed_and_retirement_is_registered(self):
        self.assertFalse((ROOT / 'codex-skills' / NAME).exists())
        import json
        manifest = json.loads((ROOT / 'docs/releases/2026-09-06/manifest.json').read_text())
        self.assertIn('.codex/skills/' + NAME, manifest['retired'])


if __name__ == '__main__':
    unittest.main()
