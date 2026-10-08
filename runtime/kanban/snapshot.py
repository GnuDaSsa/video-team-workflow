#!/usr/bin/env python3
"""Read-only bounded projection; never controls a lane, browser or scheduler."""
import argparse
import datetime as dt
import json
from pathlib import Path
import re

LANES = [('director','기획'),('music','음악'),('planner','컷 설계'),
 ('image_creator_01','이미지 1'),('image_creator_02','이미지 2'),('image_qc','이미지 검수'),
 ('seedance','영상 생성'),('seedance_qc','영상 검수'),('editor','편집'),('package','최종 패키지')]


def read(path, errors):
    if not path.exists(): return {}
    try:
        if path.stat().st_size > 2_000_000: raise ValueError('파일 크기 제한')
        value = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(value, dict): raise ValueError('JSON 객체 아님')
        return value
    except (OSError, ValueError) as exc:
        errors.append(path.name + ': 읽기 실패'); return {}


def text(value, limit=230):
    return value[:limit] if isinstance(value, str) else ''


def timestamp(value):
    try:
        parsed = dt.datetime.fromisoformat(value.replace('Z','+00:00'))
        return parsed.timestamp() if parsed.tzinfo else 0
    except (TypeError, ValueError, AttributeError): return 0


def bucket(status):
    s = str(status).upper()
    if any(x in s for x in ('BLOCK','FAIL','ERROR','REJECT','HOLD','REVIEW','USER_ACTION','REPAIR')): return 'attention'
    if s in ('DONE','COMPLETE','COMPLETED','PASS','WARN_PASS','APPROVED','DELIVERED'): return 'done'
    if any(x in s for x in ('RUNNING','ACTIVE','PROGRESS','WAITING','QUEUE','GENERATING','RECOVERING','STARTED')) and s != 'NOT_STARTED': return 'working'
    return 'ready'


def native_schedule(monitoring, automations):
    identity = monitoring.get('automation_id')
    if not isinstance(identity,str) or not re.fullmatch(r'[A-Za-z0-9_-]+',identity):
        return {'label':'예약 미등록', 'tone':'attention'}
    path = automations / identity / 'automation.toml'
    try:
        raw = path.read_text(encoding='utf-8')[:60000]
        match = re.search(r'^status\s*=\s*"([A-Z_]+)"',raw,re.M)
        state = match.group(1) if match else 'UNKNOWN'
    except OSError: state = 'UNKNOWN'
    labels = {'ACTIVE':'예약 활성 설정 · 실행 별도 확인','PAUSED':'예약 일시정지','UNKNOWN':'예약 설정 확인 불가'}
    return {'label':labels.get(state,'예약 상태 미확인'),'tone':'working' if state=='ACTIVE' else 'attention'}


def project_snapshot(path, automations, now):
    errors=[]; state=read(path/'state.json',errors); manifest=read(path/'manifest.json',errors)
    if not state and not manifest: return None
    stored=state.get('lanes') if isinstance(state.get('lanes'),dict) else {}
    cards=[]; latest=timestamp(state.get('updated_at')); seed={}
    for key,label in LANES:
        status_path=path/'lanes'/key/'status.json'
        lane=read(status_path,errors)
        fallback=stored.get(key) if isinstance(stored.get(key),dict) else {}
        conflict=bool(lane and fallback and lane.get('status') and fallback.get('status') and lane.get('status')!=fallback.get('status'))
        # Prefer the later explicitly timestamped record, not file modification time.
        if not lane or timestamp(fallback.get('updated_at')) > timestamp(lane.get('updated_at')):
            lane=fallback; source='state.json'
        else: source='lanes/'+key+'/status.json'
        if key=='seedance': seed=lane
        status=text(lane.get('status')) or 'PENDING'
        stamp=timestamp(lane.get('updated_at'));latest=max(latest,stamp)
        cards.append({'id':key,'title':label,'column':bucket(status),'status':status,
         'detail':text(lane.get('next_action') or lane.get('current_phase') or lane.get('phase')),
         'updated':text(lane.get('updated_at')),'stale':not stamp or now-stamp>1800,
         'conflict':conflict,'source':source})
    q=read(path/'lanes/seedance/queue_runtime.json',errors)
    monitoring=seed.get('monitoring') if isinstance(seed.get('monitoring'),dict) else {}
    schedule=native_schedule(monitoring,automations)
    if monitoring.get('consumer_task_id') and seed.get('owner_thread_id') and monitoring['consumer_task_id']!=seed['owner_thread_id']:
        schedule={'label':'예약 대상과 제작 담당 불일치','tone':'attention'}
    name=text(state.get('title') or manifest.get('title') or state.get('slug')) or path.name
    return {'id':path.name,'name':name,'path':str(path),'cards':cards,'schedule':schedule,
      'queue':{'active':q.get('active_count') if type(q.get('active_count')) is int else None,
               'backlog':q.get('settled_backlog_count') if type(q.get('settled_backlog_count')) is int else None,
               'updated':text(q.get('updated_at'))},
      'errors':errors,'updated_epoch':latest}


def snapshot(root,automations,now=None):
    now=now or dt.datetime.now(dt.timezone.utc).timestamp()
    projects=[]
    if root.is_dir():
        for p in sorted(root.iterdir())[:100]:
            if not p.is_dir() or p.is_symlink(): continue
            if not (p/'state.json').is_file() and not (p/'manifest.json').is_file(): continue
            item=project_snapshot(p,automations,now)
            if item:
                state=read(p/'state.json',[])
                if bucket(state.get('status',''))=='done': continue
                # Only recently updated, unfinished work; archived RUNNING records
                # must not masquerade as current production indefinitely.
                item['cards']=[c for c in item['cards']
                    if c['column'] in ('working','attention')
                    and 0 <= now-timestamp(c['updated']) <= 86400]
                if item['cards']: projects.append(item)
    projects.sort(key=lambda p:p['updated_epoch'],reverse=True)
    return {'schema':1,'observed_at':dt.datetime.now().astimezone().isoformat(),
      'projects':projects,'read_only':True,'provider_live_verified':False}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--automations',type=Path,default=Path.home()/'.codex/automations')
    args=parser.parse_args();print(json.dumps(snapshot(args.root,args.automations),ensure_ascii=False))
