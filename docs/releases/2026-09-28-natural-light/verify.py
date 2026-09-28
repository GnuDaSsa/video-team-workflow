"""Offline route/content checks, not image/video perception or provider evaluation."""
from pathlib import Path
import argparse,json,sys,tempfile,subprocess,hashlib
R=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(R/'runtime/scripts'))
from video_knowledge_router import select_knowledge,extract_section,validate_catalog
p=argparse.ArgumentParser();p.add_argument('--wiki-root',type=Path,default=Path('/Users/gnudas/wiki'));p.add_argument('--native-root',type=Path,default=R/'aside-skills/aside-video');p.add_argument('--output',type=Path);a=p.parse_args()
W=a.wiki_root;report={'scope':'offline routing/content/parity only','legacy':[],'native':[],'compiler':[]}
profile=extract_section((W/'concepts/video-prompting-live-action.md').read_text(),None)
assert len(profile)<=2400;report['profile_chars']=len(profile)
assert (R/'wiki-extract/video-prompting-live-action.md').read_bytes()==(W/'concepts/video-prompting-live-action.md').read_bytes()
assert (R/'aside-skills/aside-video/references/knowledge/aside-image-video-prompting.md').read_bytes()==(W/'concepts/aside-image-video-prompting.md').read_bytes()
assert validate_catalog(W/'_meta/video-knowledge-catalog.json',W)['ok']
for name,attrs,expected in [
 ('portrait',{'medium':'실사','shot_roles':['close_up'],'risks':['identity_drift']},True),
 ('object',{'medium':'photoreal','project_type':'product','shot_roles':['product','object_macro']},True),
 ('environment',{'medium':'live_action','shot_roles':['environment'],'cameras':['static']},True),
 ('no_i2v',{'medium':'live_action','generation_mode':'no_i2v_reference_native','shot_roles':['dialogue']},True),
 ('mixed',{'mediums':['mixed','live_action','2d_animation'],'shot_roles':['montage']},True),
 ('pure_2d',{'medium':'2d_animation','shot_roles':['dialogue']},False),
 ('pure_3d',{'medium':'3d_animation','shot_roles':['action']},False),
]:
 with tempfile.TemporaryDirectory() as td:
  d=Path(td);(d/'manifest.json').write_text(json.dumps(attrs));r=select_knowledge(d,name,wiki_root=W)
  hits=[x for x in r['selected'] if x['id']=='medium-live-action'];text=Path(r['context']).read_text()
  assert bool(hits)==expected;assert r['context_chars']<=9000 and len(r['selected'])<=6
  if expected:assert not hits[0]['truncated'] and profile in text
  report['legacy'].append({'name':name,'pass':True,'selected':[x['id'] for x in r['selected']]})
# Mandatory content and protected creative boundaries, including existing identity/edit/motion rules.
for marker in ['건축·배치·물체 형상','시간대·색온도·노출','실제 지지점·연결부','실사 기본값','접지 그림자','작은 밝기 편차','절제된 선명도','긍정형','과한 HDR','의료 공간의 청결','미검증이면 PASS하지 않는다','승인 참조','역숏은 단순 좌우 반전이 아니다','목적→방해/자극']:
 assert marker in profile,marker
module=(a.native_root/'scripts/knowledge.mjs').as_uri()
js=r'''import {selectKnowledge,verifyKnowledge} from '__MODULE__';
const cases=[['still','image_prompt',{user_instruction:'실사 제품 사진'},true],['edit','image_prompt',{user_instruction:'포토리얼 인물 참조 수정'},true],['video20','seedance_prompt',{user_instruction:'실사 영상'},true],['video25','seedance_prompt',{user_instruction:'실사 영상',knowledge_version:'seedance-2.5'},true],['mixed','seedance_prompt',{knowledge_tags:['live_action','animation'],user_instruction:'mixed'},true],['2d','seedance_prompt',{knowledge_tags:['animation']},false],['2dstill','image_prompt',{knowledge_tags:['animation']},false]];
const rows=[];for(const [name,stage,context,expected] of cases){const p=await selectKnowledge(stage,context,{wikiRoot:'__WIKI__'});await verifyKnowledge(p,{wikiRoot:'__WIKI__'});const has=p.text.includes('For photoreal/live-action portions');if(has!==expected)throw Error(name);if(p.text.length>9000||p.cards.length>6)throw Error('budget');if(expected&&!p.text.includes('not a quality guarantee'))throw Error('boundary');rows.push({name,pass:true,cards:p.selected_ids,chars:p.text.length,mode:p.source.mode});}console.log(JSON.stringify(rows));'''.replace('__MODULE__',module).replace('__WIKI__',str(W))
r=subprocess.run(['node','--input-type=module','-e',js],capture_output=True,text=True);assert r.returncode==0,r.stderr;report['native']=json.loads(r.stdout)
# Positive-only optical examples, with no model call.
examples={
'home':'Scene: 작은 식탁과 나무 의자가 놓인 실사 거실. Camera: 눈높이 미디엄 와이드, 창문과 식탁 다리가 함께 읽히는 3/4 시점. Lighting: 왼쪽 창의 부드러운 낮빛이 식탁 윗면을 밝히고 오른쪽 아래 접지 그림자가 이어진다. 밝은 면과 그늘의 작은 밝기 편차, 부드러운 하이라이트. Color grading: 벽 #E8E2D8, 나무 #A67E58. Texture/Medium: 촬영 거리에서 읽히는 나뭇결과 직물 결, 절제된 선명도와 매끈한 금속의 본래 반사. AR 16:9',
'lab':'Scene: 청결한 식품 연구실 작업대에 놓인 닫힌 식품 프린터의 외관. Camera: 눈높이 3/4 미디엄 숏, 본체의 실제 비율과 접지가 읽힌다. Lighting: 왼쪽 창과 천장 면광원의 반사가 금속과 유리의 표면 방향에 맞게 놓이며 넓은 하이라이트가 부드럽게 감쇠한다. Color grading: 본체 #E6E8E7, 작업대 #C4C8C8. Texture/Medium: 깨끗한 금속·유리 고유의 광택, 작은 국소 명암 편차와 절제된 선명도. AR 16:9'}
with tempfile.TemporaryDirectory() as td:
 for name,text in examples.items():
  f=Path(td)/(name+'.txt');f.write_text(text);r=subprocess.run(['node','/Users/gnudas/.codex/skills/image-prompt/scripts/check_prompt.mjs',str(f),'--tier','0'],capture_output=True,text=True);d=json.loads(r.stdout);assert r.returncode==0 and d['ok'],d
  report['compiler'].append({'name':name,'ok':d['ok'],'warnings':d.get('warnings',[])})
report['not_run']=['new media generation','full video playback QC','independent author behavioral evaluation','broad unrelated deployment']
report['ok']=True
if a.output:a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
