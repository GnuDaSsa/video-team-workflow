from pathlib import Path
import sys,json,tempfile,hashlib,subprocess
repo=Path('/Users/gnudas/Documents/Codex/video-team-workflow'); release=repo/'docs/releases/2026-09-08-hell-grind'
sys.path.insert(0,str(repo/'runtime/scripts'))
from video_knowledge_router import select_knowledge,validate_catalog,extract_section
wiki=Path('/Users/gnudas/wiki'); report={'catalog':validate_catalog(wiki/'_meta/video-knowledge-catalog.json',wiki),'routing_cases':[]}
assert report['catalog']['ok']
profile=extract_section((wiki/'concepts/video-prompting-live-action.md').read_text(),None)
assert len(profile)<=2400
cases=[('ko_portrait',{'medium':'실사','shot_roles':['close_up'],'cameras':['static'],'risks':['identity_drift']},True),('dialogue',{'medium':'live_action','shot_roles':['dialogue'],'cameras':['handheld'],'risks':['identity_drift','audio_naturalness'],'audio':['dialogue']},True),('product',{'medium':'live_action','project_type':'product','shot_roles':['product','object_macro'],'cameras':['macro'],'risks':['hand_object','text_logo']},True),('action',{'medium':'live_action','shot_roles':['action'],'cameras':['tracking'],'risks':['crop_drift','hand_object']},True),('mixed',{'mediums':['mixed','2d_animation','live_action'],'shot_roles':['montage'],'cameras':['static']},True),('pure_2d',{'medium':'2d_animation','shot_roles':['dialogue'],'cameras':['static'],'audio':['dialogue']},False),('pure_3d',{'medium':'3d_animation','shot_roles':['action'],'cameras':['tracking']},False)]
for name,attrs,expected in cases:
 with tempfile.TemporaryDirectory(prefix='hell-grind-route-') as td:
  p=Path(td);(p/'manifest.json').write_text(json.dumps(attrs));r=select_knowledge(p,'CHECK')
  selected=[x for x in r['selected'] if x['id']=='medium-live-action']; content=Path(r['context']).read_text()
  assert bool(selected)==expected,(name,r)
  assert len(content)<=9000 and len(r['selected'])<=6
  if expected:
   assert not selected[0]['truncated'],name
   assert profile in content,name
  report['routing_cases'].append({'case':name,'attributes':attrs,'expected_live_action':expected,'selected':[x['id'] for x in r['selected']],'profile_full_text_preserved':profile in content,'context_chars':r['context_chars'],'pass':True})
# Compiler examples are authored smoke tests, not generated media or independent LLM evaluation.
examples=[('cafe-still','Scene: 단독 성인 여성의 실사 스냅. 카페 창가에서 컵 손잡이에 엄지를 얹고 테이블 오른쪽 끝으로 시선이 내려간 한 순간. 어깨는 테이블을 향하고 얼굴은 자연스러운 비대칭을 유지한다. Camera: 앉은 사람의 눈높이 미디엄 클로즈업, 얼굴과 손이 화면 중심 60%를 차지하며 창문과 테이블 모서리는 부드럽게 읽힌다. Lighting: 왼쪽 창문의 넓고 부드러운 측광, 눈에 작고 자연스러운 창문 반사광. Color grading: 벽 #D7D2C9, 상의 #525E62, 테이블 #8A614A. Texture/Medium: 촬영 거리에서 읽히는 자연스러운 피부결과 면직물 주름, 잔잔한 명암 변화. AR 3:2'),('product-still','Scene: 평평한 석재 테이블 위에 투명한 유리병 한 개가 세워진 실사 제품 사진. 두꺼운 병 바닥이 테이블과 맞닿고 맑은 액체의 수평면이 병 아래쪽 3분의 1에 보인다. 표면은 매끈한 단색 마감. Camera: 병보다 조금 높은 3/4 시점, 병이 화면 높이 65%를 차지하며 배경 벽은 부드럽게 흐려진다. Lighting: 오른쪽 창문의 길고 넓은 반사가 유리 측면에 이어지고 접지 그림자는 왼쪽으로 짧게 놓인다. Color grading: 배경 #E8E4DD, 석재 #B4B0A7, 마개 #4C514D. Texture/Medium: 유리 두께에 따른 굴절과 미세한 석재 입도. AR 1:1'),('jacket-edit','Scene: 제공된 승인 인물 사진의 재킷 색만 차분한 회색으로 바꾼다. 원본 얼굴 정체성, 피부결, 머리, 손, 재킷의 재단과 접힘, 나머지 의상, 소품과 배경은 원본 그대로 보존한다. Camera: 원본의 촬영 거리, 시점, 크롭, 피사체 화면 크기를 그대로 유지한다. Lighting: 원본 광원 방향과 그림자 형태, 피부의 반사와 노출을 보존한다. Color grading: 재킷 #777873만 변경하며 원본 배경 #D7D2C9와 셔츠 #F4F1EB를 유지한다. Texture/Medium: 재킷 직물의 원본 질감과 봉제선을 유지한다. AR 3:2')]
report['compiler_examples']=[]
for name,prompt in examples:
 p=release/(name+'.txt');p.write_text(prompt+'\n')
 cmd=['node','/Users/gnudas/.codex/skills/image-prompt/scripts/check_prompt.mjs',str(p),'--tier','0'];r=subprocess.run(cmd,capture_output=True,text=True);data=json.loads(r.stdout);assert r.returncode==0 and data['ok'],(name,data,r.stderr)
 report['compiler_examples'].append({'file':p.name,'pass':True,'validator':data})
report['profile_chars']=len(profile)
assert (repo/'wiki-extract/video-prompting-live-action.md').read_bytes()==(wiki/'concepts/video-prompting-live-action.md').read_bytes()
report['wiki_snapshot_parity']=True
assert (repo/'codex-skills/videodirector/SKILL.md').read_bytes()==Path('/Users/gnudas/.codex/skills/videodirector/SKILL.md').read_bytes()
report['videodirector_parity']=True
hashes=json.loads((release/'image-prompt-routing-hashes.json').read_text());live=Path('/Users/gnudas/.codex/skills/image-prompt/SKILL.md').read_text();assert hashlib.sha256(live.encode()).hexdigest()==hashes['after_sha256']
backup=Path((release/'local-backup-path.txt').read_text().strip());old=(backup/'Users/gnudas/.codex/skills/image-prompt/SKILL.md').read_text();assert old.split('---',2)[1]==live.split('---',2)[1]
report['image_compiler_frontmatter_unchanged']=True
report['image_compiler_global_quick_validate']='PREEXISTING version frontmatter key unsupported by generic quick_validate; preserved. Actual compiler examples pass.'
raw=(wiki/'raw/articles/higgsfield-hell-grind-live-action-review-2026-09-08.md').read_text();fm,body=raw[4:].split('---\n',1);sha=[x.split(': ',1)[1] for x in fm.splitlines() if x.startswith('sha256:')][0];assert hashlib.sha256(body.encode()).hexdigest()==sha
report['source_notes_hash_verified']=True
report['limitations']=['No media generation or playback-quality claim','No independent model/agent behavioral evaluation','No provider/UI/queue changes','Global deployment is not claimed: unrelated preexisting SOURCE_MANIFEST_DRIFT']
(release/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
