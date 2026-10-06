import copy
import datetime as dt
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'runtime/scripts'))
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('VIDEO_TEAM_RUNTIME_SCRIPTS', str(ROOT / 'runtime/scripts'))
import test_seedance_language_override as fixture
import prompt_packet_utils as packets
import media_registry
spec = importlib.util.spec_from_file_location('cloud_cua_preflight', ROOT / 'codex-skills/seedance-prompt-en/scripts/cloud_cua_preflight.py')
cloud = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cloud)


class CloudProfileTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixture.LanguageOverrideTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.tearDown)
        self.root = self.fixture.root
        (self.root / 'manifest.json').write_text(json.dumps({'media_schema_version':media_registry.MEDIA_SCHEMA_VERSION}))
        media_registry.init_registry(self.root)
        image = self.root / 'fixture.png'
        # Byte integrity fixture, not a claimed visual review.
        image.write_bytes(b'fixture-only-image-bytes')
        asset = media_registry.ingest(self.root,image,kind='image',state='approved',work_item_id='EN01',move=False)
        self.pack = self.fixture.pack
        self.pack.update(execution_profile=cloud.PROFILE,
            cloud_session_checkpoint={'tab_id':'fixture-tab','session_url':'https://app.runwayml.com/video-tools?sessionId=fixture'},
            cloud_reference_deck=[{'token':'@Image1','asset_id':asset['asset_id'],'sha256':asset['sha256']}],
            cloud_expected_settings={'model':'Seedance 2.0','mode':'Multi-reference','duration_sec':15,'ratio':'16:9','audio':'On'})
        packets.generation_settings.initialize_duration_lock(self.root)
        self.path=self.root/'pack.json'
        self.save()
        self.now=dt.datetime.now(dt.timezone.utc)
        self.obs={'execution_profile':cloud.PROFILE,'environment':'cloud','tool_surface':'supported_cloud_cua',
            'tool_capability_evidence':'fixture:capability','user_scope_evidence':'fixture:scope',
            'visible_ui_evidence':'fixture:ui','chip_binding_evidence':'fixture:chips',
            'denial_present':False,'dialog_present':False,'prior_submission':'none','block_id':'EN01',
            'observed_at':self.now.isoformat(),**self.pack['cloud_session_checkpoint'],
            'session_matches_checkpoint':True,'pack_sha256':hashlib.sha256(self.path.read_bytes()).hexdigest(),
            'visible_prompt_sha256':packets.prompt_sha256(self.pack['prompt']),
            'reference_deck':[{**self.pack['cloud_reference_deck'][0],'role':'arena','enlarged_image_verified':True,
                'asset_bound_chip_verified':True,'chip_evidence':'fixture:chip1'}],
            'settings':copy.deepcopy(self.pack['cloud_expected_settings']),'generate_eligible':True}

    def save(self):
        self.path.write_text(json.dumps(self.pack))
        result=packets.attest(self.path,self.root)
        self.assertEqual(result['verdict'],'ATTESTED',result)

    def check(self):
        return cloud.check(self.root,self.path,self.obs,now=self.now)

    def test_pass_is_offline_only_and_never_calls_browser_or_writes_aside_receipt(self):
        with patch.object(cloud.shared,'browser_js',side_effect=AssertionError('browser forbidden')):
            result=self.check()
        self.assertEqual(result['verdict'],'PASS_OFFLINE_CONSISTENCY_ONLY')
        self.assertFalse(result['execution_authorized_by_checker'])
        self.assertFalse(result['live_ui_verified_by_checker'])
        self.assertFalse(cloud.shared.settings_preflight_path(self.root,'EN01').exists())
        self.assertFalse((self.root/'lanes/seedance/aside_binding.json').exists())

    def test_denial_unknown_surface_dialog_and_uncertain_submit_fail(self):
        for key,value in [('execution_profile','local_aside'),('environment','local'),('tool_surface','Chrome'),
                          ('denial_present',True),('denial_present',None),('dialog_present',True),
                          ('prior_submission','uncertain'),('tool_capability_evidence',''),('generate_eligible',False)]:
            with self.subTest(key=key,value=value):
                saved=copy.deepcopy(self.obs);self.obs[key]=value
                with self.assertRaises(ValueError):self.check()
                self.obs=saved

    def test_stale_future_session_and_prompt_mismatch_fail(self):
        for key,value in [('observed_at',(self.now-dt.timedelta(seconds=121)).isoformat()),
                          ('observed_at',(self.now+dt.timedelta(seconds=1)).isoformat()),
                          ('tab_id','other'),('session_url','https://evil.example/?sessionId=fixture'),
                          ('pack_sha256','wrong'),('visible_prompt_sha256','wrong')]:
            with self.subTest(key=key):
                saved=copy.deepcopy(self.obs);self.obs[key]=value
                with self.assertRaises(ValueError):self.check()
                self.obs=saved

    def test_slot_chip_asset_and_role_mismatch_fail(self):
        for key,value in [('token','@Image2'),('asset_id','wrong'),('sha256','wrong'),
                          ('role','other'),('enlarged_image_verified',False),('asset_bound_chip_verified',False),('chip_evidence','')]:
            with self.subTest(key=key):
                saved=copy.deepcopy(self.obs);self.obs['reference_deck'][0][key]=value
                with self.assertRaises(ValueError):self.check()
                self.obs=saved
        asset=media_registry.get_asset(self.root,self.pack['cloud_reference_deck'][0]['asset_id'])
        Path(asset['current_path']).write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'ASSET_NOT_APPROVED_OR_CHANGED'):self.check()

    def test_unsupported_model_and_current_lock_remain_guarded(self):
        for key,value in [('model','Seedance 2.5'),('mode','Keyframe'),('audio','Off'),('duration_sec',10)]:
            with self.subTest(key=key):
                saved=copy.deepcopy(self.obs);self.obs['settings'][key]=value
                with self.assertRaises(ValueError):self.check()
                self.obs=saved
        path=packets.generation_settings.duration_lock_path(self.root)
        path.write_text(path.read_text()+' ')
        with self.assertRaisesRegex(ValueError,'LOCK_CHANGED'):self.check()

    def test_changed_pack_even_with_updated_observation_needs_reattest(self):
        self.path.write_text(json.dumps(self.pack,indent=2))
        self.obs['pack_sha256']=hashlib.sha256(self.path.read_bytes()).hexdigest()
        with self.assertRaisesRegex(ValueError,'ATTESTATION_STALE'):self.check()

    def test_required_knowledge_cannot_be_bypassed_by_old_attestation(self):
        manifest=json.loads((self.root/'manifest.json').read_text())
        manifest['knowledge_routing']={'enabled':True,'required_before_prompt_attestation':True}
        (self.root/'manifest.json').write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError,'CLOUD_KNOWLEDGE_INVALID'):self.check()

    def test_local_aside_guard_is_not_relaxed(self):
        with patch.dict(os.environ,{'RUNWAY_BROWSER':'cloud_cua'}):
            with self.assertRaisesRegex(SystemExit,'ASIDE_ONLY'):cloud.shared.resolve_target_app()


if __name__=='__main__':unittest.main()
