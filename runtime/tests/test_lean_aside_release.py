from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'runtime/scripts'))
sys.path.insert(0, str(ROOT / 'codex-skills/seedance-prompt-en/scripts'))
sys.path.insert(0, str(ROOT / 'tools'))
os.environ.setdefault('VIDEO_TEAM_RUNTIME_SCRIPTS', str(ROOT / 'runtime/scripts'))
import aside_bridge as bridge
import shot_semantics
import media_registry as registry
import lane_inputs
import lane_gates
import prompt_packet_utils as packets
import video_release
import video_codex_runtime as runtime

URL = 'https://app.runwayml.com/video-tools/teams/test/ai-tools/generate?sessionId=one'
BINDING = {'version': bridge.VERSION, 'target_id': 'TARGET', 'session_url': URL}


class AsideBridgeTests(unittest.TestCase):
    def test_exact_url_rejects_host_path_and_session_errors(self):
        for bad in ('https://evil.test/ai-tools/generate?sessionId=x',
                    URL.replace('https:', 'http:'), URL + '&sessionId=two',
                    URL.split('?')[0], 'https://app.runwayml.com/home?sessionId=x'):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                bridge.session_identity(bad)

    def test_cli_invokes_only_repl_and_parses_marker(self):
        with patch.object(bridge.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, bridge.MARKER + '{"ok":true}\n[ok]', '')) as run:
            self.assertEqual(bridge.repl('exact code'), {'ok': True})
            self.assertEqual(run.call_args.args[0], [bridge.CLI, 'repl', 'exact code'])
            self.assertEqual(run.call_args.kwargs['timeout'], 60)

    def test_ambiguous_or_missing_result_fails(self):
        for stdout in ('[ok]', bridge.MARKER+'1\n'+bridge.MARKER+'2'):
            with patch.object(bridge.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, stdout, '')):
                with self.assertRaises(ValueError): bridge.repl('code')

    def test_cli_error_has_no_fallback_or_retry(self):
        with patch.object(bridge.subprocess, 'run', side_effect=subprocess.TimeoutExpired('repl', 60)) as run:
            with self.assertRaisesRegex(ValueError, 'TRANSPORT_ERROR'): bridge.repl('code')
            self.assertEqual(run.call_count, 1)

    def test_binding_required_before_any_cli(self):
        with tempfile.TemporaryDirectory() as td, patch.object(bridge, 'repl') as run:
            self.assertEqual(bridge.browser_js('danger()', Path(td)/'absent')[0], 3)
            run.assert_not_called()

    def test_bound_project_and_prompt_path_cannot_be_crossed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);path=root/'binding.json'
            path.write_text(json.dumps({**BINDING,'project':str(root/'one')}))
            with patch.dict(os.environ,{'RUNWAY_ASIDE_BINDING':str(path)}):
                self.assertTrue(bridge.require_project(root/'one'))
                with self.assertRaisesRegex(ValueError,'PROJECT_MISMATCH'):
                    bridge.require_project(root/'two')
                with self.assertRaisesRegex(ValueError,'PROMPT_OUTSIDE'):
                    bridge.require_project(prompt_file=root/'two/prompt.txt')

    def test_malformed_binding_fails_closed(self):
        with tempfile.TemporaryDirectory() as td, patch.object(bridge, 'repl') as run:
            p=Path(td)/'b.json';p.write_text('[]')
            self.assertEqual(bridge.browser_js('danger()', p)[0], 3)
            run.assert_not_called()

    def test_generated_js_refuses_wrong_or_duplicate_target_before_action(self):
        # Execute the actual emitted script with a stub browser API, not a text assertion.
        node=shutil.which('node'); self.assertTrue(node)
        tab={'targetId':'TARGET','url':URL,'active':True,'focusedWindow':True}
        cases=[([tab],URL,True,False),
               ([{**tab,'targetId':'WRONG'}],URL,False,False),
               ([tab,tab],URL,False,False),
               ([tab],URL.replace('one','two'),False,False),
               ([{**tab,'active':False}],URL,False,True)]
        for tabs, page_url, accepted, active in cases:
            script=bridge.binding_script(BINDING,'(touches++, true)',require_active=active)
            code=('let touches=0;global.URL=undefined;global.listBrowserTabs=async()=>'+json.dumps(tabs)+';'
                  'global.attachBrowserTab=async()=>({url:async()=>'+json.dumps(page_url)+'});'
                  +'(async()=>{'+script+';console.log("TOUCHES="+touches);})().catch(e=>console.log("REFUSED="+touches));')
            result=subprocess.run([node,'-e',code],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIn('TOUCHES=1' if accepted else 'TOUCHES=0',result.stdout)
            if not accepted: self.assertIn('__aside_bridge_error',result.stdout)

    def test_dom_location_recheck_and_unique_editor_guard_exist(self):
        with tempfile.TemporaryDirectory() as td, patch.object(bridge, 'repl', return_value=True) as repl:
            p=Path(td)/'b.json';p.write_text(json.dumps(BINDING))
            self.assertEqual(bridge.browser_js('true',p)[0],0)
            self.assertIn('ASIDE_SESSION_CHANGED_BEFORE_DOM',repl.call_args.args[0])
        helper=(ROOT/'codex-skills/seedance-prompt-en/scripts/runway_ui_helper.py').read_text()
        self.assertIn('PROMPT_CHANGED_BEFORE_PASTE',helper)
        for name in ('def cmd_js_click_file_input','def cmd_paste_image'):
            self.assertNotIn(name,helper)
        # Native modal ownership may compare the front window to CLI-bound
        # identity; it must not become a front-tab DOM/control fallback.
        native_guard = helper.split('def native_picker_guard()', 1)[1].split('def run_verified(', 1)[0]
        self.assertIn('ABORT_NATIVE_WINDOW_CHANGED', native_guard)
        self.assertIn('ABORT_NATIVE_TAB_CHANGED', native_guard)
        self.assertNotIn('active tab of front window', helper.replace(native_guard, ''))


class SemanticRegressionTests(unittest.TestCase):
    def test_separated_drone_cannot_inherit_human_motion(self):
        pack={'block_id':'S01_DRONE','separated_identity_only':True,
              'prompt':'3/4 추적 또는 정면 고정. 소매와 머리카락이 바람에 반응한다.'}
        errors=shot_semantics.validate(pack)
        self.assertIn('prompt_unresolved_camera_choice',errors)
        self.assertIn('prompt_human_motion_in_drone_only',errors)

    def test_human_scope_cannot_activate_drone(self):
        self.assertIn('prompt_drone_motion_in_human_only',shot_semantics.validate(
            {'render_scope':'human_only','prompt':'드론은 공중에만 있고 기어가거나 굴러가지 않는다.'}))

    def test_compound_move_and_negative_exclusions_remain_valid(self):
        for scope,text in [('human_only','측면 추적 후 카메라를 고정한다. 드론이 가속하는 모습은 배제한다.'),
                           ('drone_only','드론을 측면 추적한다. 머리카락이나 소매 반응은 없다.')]:
            self.assertEqual(shot_semantics.validate({'render_scope':scope,'prompt':text}),[])

    def test_operator_and_filename_leak_rejected(self):
        e=shot_semantics.validate({'prompt':'입력 모드: 인물이 door.png을(를) 본다.'})
        self.assertIn('prompt_compiler_or_operator_text_leak',e)
        self.assertIn('prompt_media_filename_leak',e)

    def test_undecided_scene_camera_rejected(self):
        self.assertIn('scene_1_camera_choice_not_decided',shot_semantics.validate(
            {'scene_plan':[{'camera':'추적 또는 고정'}]}))


class InputEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.p=Path(self.temp.name)
        (self.p/'manifest.json').write_text(json.dumps({'media_schema_version':registry.MEDIA_SCHEMA_VERSION,
                                                      'music':{'status':'LOCKED'}}))
        registry.init_registry(self.p)
    def tearDown(self): self.temp.cleanup()

    def test_status_only_music_and_empty_plan_fail_hard(self):
        ok,reason=lane_gates.gate_check(self.p,'planner')
        self.assertFalse(ok);self.assertTrue(lane_gates.non_bypassable_reason(self.p,reason))
        plan=self.p/'lanes/planner/multi_reference_block_map.json'
        plan.parent.mkdir(parents=True);plan.write_text('{}')
        ok,reason=lane_gates.gate_check(self.p,'image_creator_01')
        self.assertFalse(ok);self.assertTrue(lane_gates.non_bypassable_reason(self.p,reason))

    def test_registered_lock_hash_and_probe_evidence_required(self):
        f=self.p/'source.wav';f.write_bytes(b'unit-test-audio-fixture')
        a=registry.ingest(self.p,f,work_item_id='MUSIC',kind='audio',state='locked',
                          metadata={'duration_sec':15,'codec':'pcm_s16le'})
        m={'music':{'status':'LOCKED','asset_id':a['asset_id']}}
        self.assertEqual(lane_inputs.music_error(self.p,m),'')
        Path(a['current_path']).write_bytes(b'changed')
        self.assertIn('changed',lane_inputs.music_error(self.p,m))

    def test_nonempty_unique_block_map_required(self):
        path=self.p/'lanes/planner/multi_reference_block_map.json';path.parent.mkdir(parents=True)
        b={'block_id':'B01','covered_cuts':['C01']}
        path.write_text(json.dumps({'blocks':[b]}));self.assertEqual(lane_inputs.planner_error(self.p),'')
        path.write_text(json.dumps({'blocks':[b,b]}));self.assertIn('unique',lane_inputs.planner_error(self.p))


class ReleaseTests(unittest.TestCase):
    def test_release_detects_drift_and_archives_retired_surfaces(self):
        with tempfile.TemporaryDirectory() as td:
            home=Path(td);m=video_release.freeze()
            retired=home/video_release.RETIRED[0];retired.mkdir(parents=True)
            (retired/'SKILL.md').write_text('old role')
            self.assertFalse(video_release.check(m,ROOT,home)['ok'])
            result=video_release.apply(m,ROOT,home)
            self.assertTrue(result['ok']);self.assertFalse(retired.exists())
            self.assertTrue((Path(result['archive'])/video_release.RETIRED[0]/'SKILL.md').is_file())
            dest=home/m['files'][0]['target'];dest.write_text(dest.read_text()+'drift')
            self.assertFalse(video_release.check(m,ROOT,home)['ok'])

    def test_unknown_live_skill_file_blocks_without_deletion(self):
        with tempfile.TemporaryDirectory() as td:
            home=Path(td);p=home/'.codex/skills/seedance-prompt-en/unknown.md'
            p.parent.mkdir(parents=True);p.write_text('keep')
            self.assertTrue(video_release.preflight(video_release.freeze(),ROOT,home))
            self.assertEqual(p.read_text(),'keep')

    def test_path_traversal_rejected(self):
        with self.assertRaises(ValueError): video_release.safe_path(ROOT,'../outside')

    def test_lane_templates_are_source_relative_and_lean(self):
        self.assertEqual(runtime.TEMPLATES,ROOT/'runtime/templates')
        for filename in ('music.md','seedance.md','editor.md','image_creator.md'):
            text=(runtime.TEMPLATES/filename).read_text()
            for obsolete in ('fable_prompt_bridge.py','ANIME_MV_MAHORAGA_MICROCUT','/music-video-production-team/references/'):
                self.assertNotIn(obsolete,text)
        self.assertFalse((ROOT/'codex-skills/seedance-creative-prompt-team').exists())


class AdditionalSafetyTests(unittest.TestCase):
    def test_status_read_does_not_call_cleanup(self):
        with patch.object(sys,'argv',['runtime','status','--project','/tmp/read-only-fixture']), \
                patch.object(runtime,'status'), patch.object(runtime,'run_due_cleanup') as cleanup:
            runtime.main()
            cleanup.assert_not_called()

    def test_rejected_dispatch_does_not_cleanup_before_approval(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);(p/'state.json').write_text('{}')
            with patch.object(sys,'argv',['runtime','dispatch','--project',td,'--lanes','director']), \
                    patch.object(runtime,'run_due_cleanup') as cleanup:
                with self.assertRaisesRegex(SystemExit,'SPAWN_APPROVAL_REQUIRED'):
                    runtime.main()
                cleanup.assert_not_called()

    def test_image_handoff_never_starts_codex_or_provider_cli(self):
        import contextlib, io
        from types import SimpleNamespace
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);d=p/'lanes/image_creator_01/prompts';d.mkdir(parents=True)
            (d/'C01.prompt.txt').write_text('One independent source frame.')
            with patch.object(runtime.lane_gates,'gate_check',return_value=(True,'OK')), \
                    patch.object(runtime.subprocess,'Popen') as spawn, contextlib.redirect_stdout(io.StringIO()) as out:
                runtime.image_shards_cmd(SimpleNamespace(project=td,lane='image_creator_01',max_parallel=3))
            spawn.assert_not_called();result=json.loads(out.getvalue())
            self.assertFalse(result['generation_started']);self.assertEqual(result['agents_spawned'],0)
            self.assertEqual(len(result['batches'][0]),1)
            self.assertFalse(result['batches'][0][0]['attachment_verified_by_generator'])

    def test_retired_image_runner_cannot_hide_api_fallback(self):
        s=(ROOT/'runtime/scripts/image_creator_lane_runner.py').read_text()
        self.assertNotIn('subprocess',s);self.assertNotIn('thread/start',s)
        self.assertIn('USE_CURRENT_OWNER_BUILTIN_IMAGEGEN',s)

    def test_release_retires_dangling_legacy_image_symlink(self):
        with tempfile.TemporaryDirectory() as td:
            home=Path(td);link=home/'.local/bin/video-image-cli';link.parent.mkdir(parents=True)
            link.symlink_to(home/'missing-legacy-cli.py')
            m=video_release.freeze();self.assertFalse(video_release.check(m,ROOT,home)['ok'])
            result=video_release.apply(m,ROOT,home)
            self.assertTrue(result['ok']);self.assertFalse(link.is_symlink())
            self.assertTrue((Path(result['archive'])/'.local/bin/video-image-cli').is_symlink())

    def test_edit_inherits_only_verified_registered_source(self):
        import runway_ui_helper as helper
        with tempfile.TemporaryDirectory() as td:
            project=Path(td);(project/'manifest.json').write_text(json.dumps({'media_schema_version':registry.MEDIA_SCHEMA_VERSION}));registry.init_registry(project)
            source=project/'clip.mp4';source.write_bytes(b'unit-test-video-fixture')
            asset=registry.ingest(project,source,work_item_id='SOURCE',kind='video',state='approved')
            pack={'input_video_asset_id':asset['asset_id']}
            probe={'format':{'duration':'15.02'},'streams':[{'codec_type':'video','codec_name':'h264','avg_frame_rate':'30/1'}]}
            with patch.object(helper.subprocess,'run',return_value=subprocess.CompletedProcess([],0,json.dumps(probe),'')):
                r=helper.inherited_edit_duration(project,pack,Path(asset['current_path']),15)
                self.assertEqual(r['inherited_duration_sec'],15.02)
                with self.assertRaisesRegex(ValueError,'LOCK_MISMATCH'):
                    helper.inherited_edit_duration(project,pack,Path(asset['current_path']),14)
            Path(asset['current_path']).write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'SOURCE_NOT_APPROVED_OR_CHANGED'):
                helper.inherited_edit_duration(project,pack,Path(asset['current_path']),15)

    def test_source_manifest_drift_fails_preflight(self):
        m=video_release.freeze();m['files'][0]['sha256']='0'*64
        with tempfile.TemporaryDirectory() as td:
            self.assertIn('SOURCE_MANIFEST_DRIFT',video_release.preflight(m,ROOT,Path(td))[0])

    def test_failed_release_rolls_back_existing_and_new_files(self):
        with tempfile.TemporaryDirectory() as td:
            home=Path(td);m=video_release.freeze();first=home/m['files'][0]['target']
            first.parent.mkdir(parents=True);first.write_text('original')
            original_copy=video_release.shutil.copy2
            def copy(src,dst,*args,**kwargs):
                if str(dst).endswith('.release-tmp') and str(src).endswith(m['files'][1]['source']):
                    raise OSError('injected copy failure')
                return original_copy(src,dst,*args,**kwargs)
            with patch.object(video_release.shutil,'copy2',side_effect=copy):
                with self.assertRaises(OSError): video_release.apply(m,ROOT,home)
            self.assertEqual(first.read_text(),'original')
            self.assertFalse((home/m['files'][1]['target']).exists())
