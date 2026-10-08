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
  for status,column in [('BLOCKED','attention'),('READY_FOR_USER_REVIEW','attention'),('WAITING_PROVIDER_QUEUE','waiting'),('DONE','done'),('NOT_STARTED','ready'),('UNKNOWN','ready')]:self.assertEqual(b.bucket(status),column)
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
  out=b.project_snapshot(self.project,self.auto,1);self.assertTrue(out['errors']);self.assertEqual(before,{str(f):f.read_bytes() for f in self.root.rglob('*') if f.is_file()})
 def test_completion_is_record_not_verified_media(self):
  self.write('state.json',{'slug':'x'});self.write('lanes/package/status.json',{'status':'DONE'})
  out=b.project_snapshot(self.project,self.auto,1);c=next(c for c in out['cards'] if c['id']=='package');self.assertEqual(c['column'],'done');self.assertEqual(b.snapshot(self.root,self.auto)['projects'],[])
 def test_private_prompt_fields_are_not_exported(self):
  self.write('state.json',{'slug':'x','prompt':'secret prompt','token':'secret key'})
  value=json.dumps(b.snapshot(self.root,self.auto));self.assertNotIn('secret',value)
 def test_current_only_hides_pending_done_and_old_work(self):
  now=b.timestamp('2026-10-08T20:00:00+09:00')
  self.write('state.json',{'lanes':{
   'seedance':{'status':'RUNNING','updated_at':'2026-10-08T19:00:00+09:00'},
   'music':{'status':'DONE','updated_at':'2026-10-08T19:00:00+09:00'},
   'editor':{'status':'PENDING','updated_at':'2026-10-08T19:00:00+09:00'},
   'planner':{'status':'RUNNING','updated_at':'2026-09-08T19:00:00+09:00'},
   'image_qc':{'status':'BLOCKED','updated_at':'2026-10-08T19:00:00+09:00'}}})
  out=b.snapshot(self.root,self.auto,now)
  self.assertEqual({c['id'] for c in out['projects'][0]['cards']},{'seedance','image_qc'})
  self.write('state.json',{'status':'DONE','lanes':{'seedance':{'status':'RUNNING','updated_at':'2026-10-08T19:00:00+09:00'}}})
  self.assertEqual(b.snapshot(self.root,self.auto,now)['projects'],[])
 def test_waiting_retained_after_24h_and_elapsed_is_honest(self):
  now=b.timestamp('2026-10-08T20:00:00+09:00')
  self.write('state.json',{'slug':'x'})
  self.write('lanes/seedance/status.json',{'status':'WAITING_PROVIDER_QUEUE','updated_at':'2026-10-06T20:00:00+09:00'})
  c=b.snapshot(self.root,self.auto,now)['projects'][0]['cards'][0]
  self.assertEqual(c['column'],'waiting');self.assertTrue(c['stale'])
  self.assertEqual(c['waiting']['basis'],'last_record');self.assertEqual(c['waiting']['elapsed_seconds'],172800)
  self.write('lanes/seedance/status.json',{'status':'RUNNING','updated_at':'2026-10-08T20:00:00+09:00'})
  c=b.snapshot(self.root,self.auto,now)['projects'][0]['cards'][0]
  self.assertEqual(c['column'],'working');self.assertIsNone(c['waiting'])
  self.write('lanes/seedance/status.json',{'status':'DONE','updated_at':'2026-10-08T20:00:00+09:00'})
  self.assertEqual(b.snapshot(self.root,self.auto,now)['projects'],[])
 def test_wait_start_unknown_future_and_attention_precedence(self):
  now=b.timestamp('2026-10-08T20:00:00+09:00')
  w=b.waiting_record({'waiting_since':'2026-10-08T19:00:00+09:00','wait_reason':'승인 대기'},'WAITING',now)
  self.assertEqual(w['basis'],'wait_start');self.assertEqual(w['elapsed_seconds'],3600)
  self.assertEqual(w['reason'],'승인 대기')
  w=b.waiting_record({'waiting_since':'2099-01-01T00:00:00Z'},'WAITING',now)
  self.assertIsNone(w['elapsed_seconds'])
  self.assertEqual(b.bucket('WAITING_USER_ACTION'),'attention')
  self.assertEqual(b.bucket('QUEUED'),'waiting')
  self.assertEqual(b.bucket('PENDING'),'ready')
 def test_week_old_waits_hidden_and_recent_wait_restored(self):
  now=b.timestamp('2026-10-08T20:00:00+09:00')
  self.write('state.json',{'slug':'x','updated_at':'2026-10-08T20:00:00+09:00'})
  for stamp in ['2026-10-01T20:00:00+09:00','2026-09-20T20:00:00+09:00',None,'2099-01-01T00:00:00Z']:
   self.write('lanes/seedance/status.json',{'status':'WAITING_PROVIDER_QUEUE','updated_at':stamp})
   self.assertEqual(b.snapshot(self.root,self.auto,now)['projects'],[],stamp)
  self.write('lanes/seedance/status.json',{'status':'WAITING_PROVIDER_QUEUE','updated_at':'2026-10-01T20:00:01+09:00'})
  self.assertEqual(len(b.snapshot(self.root,self.auto,now)['projects']),1)
 def test_legacy_runtime_local_timestamp_is_not_dropped(self):
  import datetime as dt
  local=dt.datetime.now().replace(microsecond=0)
  now=local.timestamp()+60
  self.write('state.json',{'slug':'x'})
  self.write('lanes/seedance/status.json',{'status':'RUNNING','updated_at':local.isoformat()})
  c=b.snapshot(self.root,self.auto,now)['projects'][0]['cards'][0]
  self.assertTrue(c['timezone_assumed']);self.assertFalse(c['stale'])
  self.assertEqual(b.timestamp(local.isoformat()),local.timestamp())
  self.assertEqual(b.timestamp('invalid'),0)
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
