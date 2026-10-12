from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools'))
import deploy_reviewed_patch as deployer


class NewFileDeployTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'repo'; self.root.mkdir()
        self.home = Path(self.temp.name) / 'home'; self.home.mkdir()
        self.git('init', '-q'); self.git('config', 'user.name', 'Test')
        self.git('config', 'user.email', 'test@example.test')
        (self.root/'base').write_text('base'); self.git('add', 'base'); self.git('commit', '-qm', 'base')
        self.rel = 'runtime/scripts/new.py'
        p = self.root/self.rel; p.parent.mkdir(parents=True); p.write_text('new\n')
        self.git('add', '-N', self.rel)
        self.target = self.home/'managed/new.py'
        mock = patch.object(deployer.video_release, 'mappings', return_value=[{
            'source': self.rel, 'target': 'managed/new.py'}])
        mock.start(); self.addCleanup(mock.stop)

    def git(self, *args):
        return subprocess.run(['git', *args], cwd=self.root, check=True, capture_output=True)

    def test_new_requires_opt_in_and_dry_run_then_apply(self):
        with self.assertRaisesRegex(ValueError, 'LIVE_FILE_REQUIRED'):
            deployer.deploy(self.root, self.home, [self.rel])
        result = deployer.deploy(self.root, self.home, [self.rel], allow_new=True)
        self.assertIsNone(result['files'][0]['before_sha256']); self.assertFalse(self.target.exists())
        deployer.deploy(self.root, self.home, [self.rel], apply=True, allow_new=True)
        self.assertEqual(self.target.read_text(), 'new\n')

    def test_preexisting_target_never_overwritten(self):
        self.target.parent.mkdir(); self.target.write_text('user\n')
        with self.assertRaisesRegex(ValueError, 'CANNOT_OVERWRITE'):
            deployer.deploy(self.root, self.home, [self.rel], True, True)
        self.assertEqual(self.target.read_text(), 'user\n')

    def test_unmanaged_rejected(self):
        with self.assertRaisesRegex(ValueError, 'NOT_RELEASE_MANAGED'):
            deployer.deploy(self.root, self.home, ['other'], True, True)

    def test_missing_live_old_source_is_not_new(self):
        self.git('add', self.rel); self.git('commit', '-qm', 'tracked')
        (self.root/self.rel).write_text('changed\n')
        with self.assertRaisesRegex(ValueError, 'MUST_NOT_RESTORE'):
            deployer.deploy(self.root, self.home, [self.rel], True, True)

    def test_shared_existing_patch_is_context_and_unrelated_drift_is_retained(self):
        base = b'one\ntwo\nthree\nfour\nfive\nsix\n'
        live = b'ONE\ntwo\nthree\nfour\nFIVE\nsix\n'
        source = b'ONE\ntwo\nthree\nfour\nfive\nsix\nadded\n'
        common = deployer.shared_base(base, live, source)
        self.assertEqual(common, b'ONE\ntwo\nthree\nfour\nfive\nsix\n')
        after = deployer.merge_bytes(live, common, source)
        self.assertEqual(after, b'ONE\ntwo\nthree\nfour\nFIVE\nsix\nadded\n')
        self.assertEqual(deployer.merge_bytes(after, source, common), live)

    def test_conflicting_existing_edits_still_fail(self):
        base = b'one\ntwo\n'; live = b'X\ntwo\n'; source = b'Y\ntwo\n'
        with self.assertRaisesRegex(ValueError, 'CONFLICT'):
            deployer.merge_bytes(live, deployer.shared_base(base, live, source), source)


if __name__ == '__main__':
    unittest.main()
