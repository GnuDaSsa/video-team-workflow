import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SOURCE=Path(__file__).resolve().parents[2]/'codex-skills/seedance-prompt-en/scripts/aside_bridge.py'
spec=importlib.util.spec_from_file_location('observation_bridge',SOURCE)
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)

def fixture():
 return {'schema':1,'surface':'COMPOSER','dialog_count':0,'editor_count':1,'prompt_characters':10,'references':[],'references_truncated':False,'generate':{'count':1,'enabled':True}}

class ObservationTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);(self.root/'manifest.json').write_text('{}');self.path=self.root/'lanes/seedance/aside_binding.json';self.path.parent.mkdir(parents=True)
  self.path.write_text(json.dumps({'version':b.VERSION,'project':str(self.root),'target_id':'abc','session_url':'https://app.runwayml.com/video-tools/teams/test/ai-tools/generate?sessionId=test','account':'u1'}))
 def tearDown(self):self.tmp.cleanup()
 def test_one_call_read_only_default_and_no_status_write(self):
  with patch.object(b,'browser_js',return_value=(0,json.dumps(fixture()),'')) as call:
   result=b.observe(self.path);call.assert_called_once_with(b.OBSERVE_JS,self.path.resolve())
  self.assertFalse(result['execution_authorized']);self.assertFalse(result['provider_acceptance_verified']);self.assertEqual(list(self.path.parent.iterdir()),[self.path])
 def test_record_allowlist_and_preserve_status(self):
  status=self.path.parent/'status.json';status.write_text('{"status":"BLOCKED"}')
  data=fixture();data.update(prompt='secret',account_url='private')
  with patch.object(b,'browser_js',return_value=(0,json.dumps(data),'')):b.observe(self.path,True)
  value=(self.path.parent/'ui_observation.json').read_text();self.assertNotIn('secret',value);self.assertNotIn('private',value);self.assertEqual(status.read_text(),'{"status":"BLOCKED"}')
 def test_failure_no_retry_no_receipt(self):
  with patch.object(b,'browser_js',return_value=(3,'','SESSION_MISMATCH')) as call:
   with self.assertRaisesRegex(ValueError,'SESSION_MISMATCH'):b.observe(self.path,True)
   call.assert_called_once()
  self.assertFalse((self.path.parent/'ui_observation.json').exists())
 def test_binding_race_refuses_receipt(self):
  def changed(*args):
   v=json.loads(self.path.read_text());v['target_id']='changed';self.path.write_text(json.dumps(v));return 0,json.dumps(fixture()),''
  with patch.object(b,'browser_js',side_effect=changed):
   with self.assertRaisesRegex(ValueError,'BINDING_CHANGED'):b.observe(self.path,True)
 def test_invalid_payload_rejected(self):
  for change in ({'schema':2},{'references':'bad'},{'generate':{'count':1,'enabled':'yes'}},{'editor_count':True},{'surface':'READY_TO_GENERATE'}):
   value=fixture();value.update(change)
   with self.assertRaises(ValueError):b.validate_observation(value)
 def test_cli_zero_exit_missing_or_invalid_marker_is_failure(self):
  for stdout,code in [('Error: selector absent','MISSING_OR_AMBIGUOUS'),(b.MARKER+'{broken','INVALID_JSON'),(b.MARKER+'{}\n'+b.MARKER+'{}','MISSING_OR_AMBIGUOUS')]:
   with patch.object(b.subprocess,'run',return_value=subprocess.CompletedProcess([],0,stdout,'')):
    with self.assertRaisesRegex(ValueError,code):b.repl('read','u1')
 def test_wrong_record_path_refused_before_cli(self):
  p=self.root/'copy.json';p.write_bytes(self.path.read_bytes())
  with patch.object(b,'browser_js') as call:
   with self.assertRaisesRegex(ValueError,'PROJECT_MISMATCH'):b.observe(p,True)
   call.assert_not_called()
 def test_dom_stages_with_node_fixture(self):
  script='''const vm=require('vm');const code=JSON.parse(process.argv[1]);
const elem=(label,text='')=>({getClientRects:()=>[1],getAttribute:k=>k==='aria-label'?label:null,textContent:text,innerText:text,disabled:false});
for(const stage of ['ASSET_SELECTOR','DIALOG','COMPOSER','UNKNOWN']){
 const dialogs=stage==='ASSET_SELECTOR'?[elem('Asset selector')]:stage==='DIALOG'?[elem('Preview')]:[];
 const editors=stage==='UNKNOWN'?[]:[elem('', 'private prompt')];
 const buttons=[elem('View Image 1 larger'),elem('Generate')];
 const document={querySelectorAll:s=>s==='button'?buttons:s.startsWith('[contenteditable]')?editors:dialogs};
 const result=vm.runInNewContext(code,{document});
 if(result.surface!==stage)throw Error(stage);if(JSON.stringify(result).includes('private prompt'))throw Error('privacy');
 if(result.references[0].index!==1)throw Error('refs');
}console.log('4 DOM stages PASS');'''
  result=subprocess.run(['node','-e',script,json.dumps(b.OBSERVE_JS)],capture_output=True,text=True)
  self.assertEqual(result.returncode,0,result.stderr)
