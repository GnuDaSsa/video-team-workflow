import importlib.util
import json
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('export_cloud_source',ROOT/'tools/export_cloud_source.py')
exporter=importlib.util.module_from_spec(spec);spec.loader.exec_module(exporter)


class CloudSourceExportTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'repo';self.root.mkdir()
        self.git('init','-q')
        files={name:'# source\n' for name in ['AGENTS.md','AGENTS.harness.md','runtime/AGENTS.md','runtime/AGENTS.harness.md',
            'docs/video-feedback-promotion-protocol.md','docs/decisions.md','docs/project-memory.md','docs/contracts/current.md']}
        files['docs/harness-config.json']=json.dumps({'paths':{'stateFile':'docs/harness-state.json','decisionsFile':'docs/decisions.md','memoryFile':'docs/project-memory.md'}})
        files['docs/harness-state.json']=json.dumps({'currentContract':'docs/contracts/current.md'})
        for name,text in files.items():
            path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
        self.git('add','.');self.git('-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-qm','fixture')
        self.patch=patch.object(exporter,'ROOT',self.root);self.patch.start();self.addCleanup(self.patch.stop)
    def git(self,*args):
        return subprocess.check_output(['git','-C',str(self.root),*args],stderr=subprocess.STDOUT)
    def test_deterministic_committed_bytes_ignore_dirty_and_untracked(self):
        (self.root/'AGENTS.md').write_text('dirty must not export')
        (self.root/'private.txt').write_text('untracked must not export')
        a,b=Path(self.tmp.name)/'a',Path(self.tmp.name)/'b'
        one=exporter.export('HEAD',a);two=exporter.export('HEAD',b)
        self.assertEqual(one,two)
        self.assertEqual((a/'source.tar.gz').read_bytes(),(b/'source.tar.gz').read_bytes())
        with tarfile.open(a/'source.tar.gz') as archive:
            self.assertEqual(archive.extractfile('workflow/AGENTS.md').read(),b'# source\n')
            self.assertNotIn('workflow/private.txt',archive.getnames())
        with self.assertRaisesRegex(ValueError,'ALREADY_EXISTS'):exporter.export('HEAD',a)
    def test_missing_tracked_runtime_harness_is_rejected(self):
        self.git('rm','runtime/AGENTS.harness.md')
        self.git('-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-qm','missing')
        with self.assertRaisesRegex(ValueError,'MISSING_TRACKED_DEPENDENCY:runtime/AGENTS.harness.md'):exporter.inspect('HEAD')
    def test_missing_current_contract_is_rejected(self):
        self.git('rm','docs/contracts/current.md')
        self.git('-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-qm','missing')
        with self.assertRaisesRegex(ValueError,'MISSING_TRACKED_DEPENDENCY:docs/contracts/current.md'):exporter.inspect('HEAD')


if __name__=='__main__':unittest.main()
