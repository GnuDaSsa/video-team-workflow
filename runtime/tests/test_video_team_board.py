import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

path=Path(__file__).resolve().parents[1]/'kanban/snapshot.py'
spec=importlib.util.spec_from_file_location('board_snapshot',path);b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)

class BoardTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.project=self.root/'project';self.project.mkdir();(self.project/'manifest.json').write_text('{}');self.auto=self.root/'automations';self.auto.mkdir()
 def tearDown(self):self.temp.cleanup()
 def write(self,rel,data):
  p=self.project/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data));return p
 def test_columns_preserve_attention_and_not_started(self):
  for status,column in [('BLOCKED','attention'),('READY_FOR_USER_REVIEW','attention'),('WAITING_PROVIDER_QUEUE','working'),('DONE','done'),('NOT_STARTED','ready'),('UNKNOWN','ready')]:self.assertEqual(b.bucket(status),column)
 def test_newer_state_wins_but_disagreement_remains_visible(self):
  self.write('state.json',{'lanes':{'seedance':{'status':'RUNNING','updated_at':'2026-10-08T15:00:00+09:00'}}})
  self.write('lanes/seedance/status.json',{'status':'BLOCKED','updated_at':'2026-10-07T15:00:00+09:00'})
  p=b.project_snapshot(self.project,self.auto,9999999999);c=next(c for c in p['cards'] if c['id']=='seedance');self.assertEqual(c['column'],'working');self.assertTrue(c['conflict']);self.assertTrue(c['stale'])
 def test_native_paused_overrides_old_active_claim(self):
  p=self.auto/'a';p.mkdir();(p/'automation.toml').write_text('status = "PAUSED"\n')
  self.assertEqual(b.native_schedule({'automation_id':'a','status':'ACTIVE'},self.auto)['label'],'예약 일시정지')
 def test_unsafe_id_never_reads_external_file(self):
  self.assertEqual(b.native_schedule({'automation_id':'../../outside'},self.auto)['label'],'예약 미등록')
 def test_corrupt_json_is_visible_and_snapshot_read_only(self):
  self.write('state.json',{'slug':'test'});p=self.write('lanes/music/status.json',{});p.write_text('{broken')
  before={str(f):f.read_bytes() for f in self.root.rglob('*') if f.is_file()}
  out=b.snapshot(self.root,self.auto);self.assertTrue(out['projects'][0]['errors']);self.assertFalse(out['provider_live_verified']);self.assertEqual(before,{str(f):f.read_bytes() for f in self.root.rglob('*') if f.is_file()})
 def test_completion_is_record_not_verified_media(self):
  self.write('state.json',{'slug':'x'});self.write('lanes/package/status.json',{'status':'DONE'})
  out=b.snapshot(self.root,self.auto);c=next(c for c in out['projects'][0]['cards'] if c['id']=='package');self.assertEqual(c['column'],'done');self.assertFalse(out['provider_live_verified'])
 def test_private_prompt_fields_are_not_exported(self):
  self.write('state.json',{'slug':'x','prompt':'secret prompt','token':'secret key'})
  value=json.dumps(b.snapshot(self.root,self.auto));self.assertNotIn('secret',value)
 def test_owner_conflict_flag(self):
  self.write('state.json',{'slug':'x'});self.write('lanes/seedance/status.json',{'owner_thread_id':'new','monitoring':{'consumer_task_id':'old'}})
  self.assertIn('불일치',b.project_snapshot(self.project,self.auto,1)['schedule']['label'])

class BoardEntryTests(unittest.TestCase):
 def test_only_registered_runtime_project_launches_and_honors_disable(self):
  import sys,os
  from unittest.mock import patch
  sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
  import video_codex_runtime as runtime
  with tempfile.TemporaryDirectory() as td:
   home=Path(td);root=home/'projects';p=root/'p';p.mkdir(parents=True);(p/'manifest.json').write_text('{}');launcher=home/'.local/bin/video-team-board';launcher.parent.mkdir(parents=True);launcher.write_text('fixture')
   with patch.object(runtime,'HOME',home),patch.object(runtime,'PROJECT_ROOT',root),patch.object(runtime.subprocess,'run') as run,patch.dict(os.environ,{},clear=False):
    run.return_value.returncode=0
    with patch.dict(os.environ,{'VIDEO_TEAM_BOARD_DISABLED':'1'}):self.assertFalse(runtime.show_project_board(p));run.assert_not_called()
    with patch.dict(os.environ,{'VIDEO_TEAM_BOARD_DISABLED':'0'}):
     self.assertTrue(runtime.show_project_board(p));self.assertEqual(run.call_args.args[0],[str(launcher),'--project',str(p.resolve())])
     run.reset_mock();self.assertFalse(runtime.show_project_board(home/'foreign'));run.assert_not_called()

if __name__ == '__main__':
    unittest.main()
