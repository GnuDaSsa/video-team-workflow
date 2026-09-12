import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import prompt_packet_utils as u

class LanguageOverrideTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name).resolve()
        (self.root/'manifest.json').write_text('{}'); (self.root/'state.json').write_text('{}')
        (self.root/'docs').mkdir(); self.ev=self.root/'docs/request.json'
        self.ev.write_text(json.dumps(dict(language='en-US',source='explicit_user_request',user_quote='영어로 진행해볼래?',turn_id='turn',block_ids=['EN01'])))
        self.pack=dict(block_id='EN01', prompt_language='en-US',prompt_style_version=u.ENGLISH_PROMPT_STYLE_VERSION,authoring_contract=u.ENGLISH_AUTHORING_CONTRACT,prompt='15 seconds, 2 shots. @Image1 supplies the empty arena. Shot 1: the camera tracks a hovering machine. Shot 2: a wide view follows the machine flying away.', reference_role_map={'@Image1':'arena'},duration_sec=15,shot_grammar=u.MULTI_SHOT_GRAMMAR, planned_scene_count=2,audio_route='diegetic',prompt_rules_used=['identity_anchor','model_facing_multimodal_binding_v1'], covered_cuts=['1','2'],scene_plan=[dict(scene_id=str(i),start_sec=(i-1)*7.5,end_sec=i*7.5,covered_cuts=[str(i)],reference_tokens=['@Image1'],action='hover then fly',camera='track',edit_out='machine exits') for i in (1,2)],prompt_language_override=dict(project=str(self.root),evidence_path=str(self.ev),evidence_sha256=hashlib.sha256(self.ev.read_bytes()).hexdigest()))
    def tearDown(self): self.tmp.cleanup()
    def test_explicit_english_valid(self): self.assertEqual(u.validate_seedance(self.pack),[])
    def test_default_rejects_english(self):
        self.pack.update(prompt_language='ko-KR',prompt_style_version=u.SEEDANCE_PROMPT_STYLE_VERSION,authoring_contract=u.SEEDANCE_AUTHORING_CONTRACT)
        self.assertTrue(any('not_korean' in e for e in u.validate_seedance(self.pack)))
    def test_request_required_and_scoped(self):
        saved=self.pack.pop('prompt_language_override'); self.assertIn('english_user_request_required',u.validate_seedance(self.pack))
        self.pack['prompt_language_override']=saved; self.pack['block_id']='OTHER';self.assertIn('language_request_scope_mismatch',u.validate_seedance(self.pack))
    def test_hash_and_project(self):
        self.assertEqual(u.validate_language_override(self.pack,self.root/'other'),['language_override_project_mismatch'])
        self.ev.write_text('{}');self.assertEqual(u.validate_language_override(self.pack),['language_request_evidence_changed'])
    def test_malformed_scope_fails_closed(self):
        for value in ([], {'block_ids': 'EN01'}):
            self.ev.write_text(json.dumps(value))
            self.pack['prompt_language_override']['evidence_sha256']=hashlib.sha256(self.ev.read_bytes()).hexdigest()
            self.assertEqual(u.validate_language_override(self.pack),['language_request_scope_mismatch'])
    def test_cli_exposes_attested_pack_argument(self):
        import subprocess, os
        root=Path(__file__).resolve().parents[2]
        result=subprocess.run([sys.executable,str(root/'codex-skills/seedance-prompt-en/scripts/runway_ui_helper.py'),'paste-prompt','--help'],capture_output=True,text=True,env={**os.environ,'VIDEO_TEAM_RUNTIME_SCRIPTS':str(root/'runtime/scripts')})
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('--pack',result.stdout)
    def test_other_gates_not_relaxed(self):
        self.pack['prompt'] += ' 12 seconds, 2 shots. '+ 'x'*3501
        errs=u.validate_seedance(self.pack)
        self.assertIn('prompt_over_3500',errs);self.assertTrue(any('duration_declaration_mismatch' in e for e in errs))
    def test_paste_attestation_and_hash(self):
        path=self.root/'pack.json';path.write_text(json.dumps(self.pack))
        with self.assertRaisesRegex(ValueError,'ATTESTATION_MISSING'):u.validate_paste_pack(path,self.pack['prompt'],self.root)
        out=u.generation_settings.seedance_prompt_dir(self.root);out.mkdir(parents=True,exist_ok=True)
        rec=dict(verdict='ATTESTED',block_id='EN01',pack=str(path),pack_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),prompt_sha256=u.prompt_sha256(self.pack['prompt']))
        (out/'EN01_attestation.json').write_text(json.dumps(rec))
        self.assertEqual(u.validate_paste_pack(path,self.pack['prompt'],self.root),'en-US')
        with self.assertRaisesRegex(ValueError,'PROMPT_PACK_MISMATCH'):u.validate_paste_pack(path,self.pack['prompt']+' changed',self.root)
        path.write_text(json.dumps(self.pack,indent=2))
        with self.assertRaisesRegex(ValueError,'ATTESTATION_STALE'):u.validate_paste_pack(path,self.pack['prompt'],self.root)

if __name__=='__main__':unittest.main()
