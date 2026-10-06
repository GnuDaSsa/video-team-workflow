import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
CLI=ROOT/'runtime/scripts/video_codex_runtime.py'
sys.path.insert(0,str(ROOT/'runtime/scripts'))
import video_codex_runtime as runtime


class InitProjectRootTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name).resolve()
        self.workspace=self.base/'workspace';self.workspace.mkdir()
    def init(self,root):
        return subprocess.run([sys.executable,str(CLI),'init','--project-root',str(root),
            '--slug','workspace-fixture','--brief','Fixture only','--mode','no_i2v_reference_native'],
            cwd=self.workspace,capture_output=True,text=True)
    def test_real_cli_builds_project_and_unchanged_gates(self):
        result=self.init('projects')
        self.assertEqual(result.returncode,0,result.stderr)
        project=Path(result.stdout.strip());self.assertTrue(project.is_relative_to(self.workspace/'projects'))
        manifest=json.loads((project/'manifest.json').read_text())
        state=json.loads((project/'state.json').read_text())
        self.assertEqual(manifest['project_root'],str(project))
        self.assertEqual(manifest['music']['status'],'NOT_LOCKED')
        self.assertTrue(manifest['knowledge_routing']['required_before_prompt_attestation'])
        self.assertTrue(manifest['safety']['public_upload_requires_user_approval'])
        self.assertTrue((project/'asset_registry.sqlite').is_file())
        self.assertTrue((project/'lanes/planner/generation_duration_lock.json').is_file())
        self.assertTrue(all(v['status']=='PENDING' for v in state['lanes'].values()))
    def test_absolute_inside_workspace_is_supported(self):
        result=self.init(self.workspace/'absolute')
        self.assertEqual(result.returncode,0,result.stderr)
    def test_relative_and_absolute_escape_reject_before_writes(self):
        for root in ('../outside',self.base/'outside'):
            with self.subTest(root=root):
                result=self.init(root);self.assertNotEqual(result.returncode,0)
                self.assertIn('OUTSIDE_WORKSPACE',result.stderr)
                self.assertFalse((self.base/'outside').exists())
    def test_symlink_escape_rejects_and_preserves_existing_files(self):
        outside=self.base/'outside';outside.mkdir();sentinel=outside/'preserve.txt';sentinel.write_text('keep')
        (self.workspace/'link').symlink_to(outside,target_is_directory=True)
        result=self.init('link/projects');self.assertNotEqual(result.returncode,0)
        self.assertIn('OUTSIDE_WORKSPACE',result.stderr)
        self.assertEqual(list(outside.iterdir()),[sentinel]);self.assertEqual(sentinel.read_text(),'keep')
    def test_default_path_is_unchanged_without_creating_it(self):
        self.assertEqual(runtime.init_project_root(None),Path('/Users/gnudas/Documents/Codex/video-team-runtime'))
    def test_existing_file_destination_not_overwritten(self):
        path=self.workspace/'occupied';path.write_text('preserve')
        result=self.init(path);self.assertNotEqual(result.returncode,0)
        self.assertEqual(path.read_text(),'preserve')


if __name__=='__main__':unittest.main()
