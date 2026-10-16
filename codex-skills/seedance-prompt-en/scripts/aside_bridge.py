#!/usr/bin/env python3
"""Deterministic Aside CLI bridge. No browser agent, new tab, or active-tab fallback."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import hashlib
from urllib.parse import parse_qs, urlparse

MARKER = 'CODEX_ASIDE_RESULT:'
VERSION = 'aside_exact_session_v1'
CLI = '/Users/gnudas/.local/bin/aside'


def session_identity(url: str) -> tuple[str, str, str]:
    p = urlparse(url)
    ids = parse_qs(p.query, keep_blank_values=True).get('sessionId', [])
    if (p.scheme != 'https' or p.netloc != 'app.runwayml.com'
            or not p.path.endswith('/ai-tools/generate') or len(ids) != 1 or not ids[0]):
        raise ValueError('ASIDE_EXACT_GENERATE_SESSION_REQUIRED')
    return p.netloc, p.path, ids[0]


def repl(code: str, account: str | None = None):
    # Never use bare `aside`, `exec`, --model or a natural-language prompt.
    cmd = [CLI, 'repl']
    if account is not None:
        if not re.fullmatch(r'(?:u)?\d+', account):
            raise ValueError('ASIDE_ACCOUNT_ID_INVALID')
        cmd += ['--account', account]
    cmd.append(code)
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError('ASIDE_CLI_TRANSPORT_ERROR: retry same session; do not change browser') from exc
    if p.returncode:
        raise ValueError('ASIDE_CLI_CONTROL_FAILED: ' + p.stderr[-500:])
    matches = [line.split(MARKER, 1)[1] for line in p.stdout.splitlines() if line.startswith(MARKER)]
    if len(matches) != 1:
        raise ValueError('ASIDE_CLI_RESULT_MISSING_OR_AMBIGUOUS')
    try:
        value = json.loads(matches[0])
    except (ValueError, TypeError) as exc:
        raise ValueError('ASIDE_CLI_RESULT_INVALID_JSON') from exc
    if isinstance(value, dict) and '__aside_bridge_error' in value:
        raise ValueError('ASIDE_CLI_CONTROL_FAILED: ' + str(value['__aside_bridge_error']))
    return value


def binding_script(binding: dict, expression: str, *, require_active: bool = False,
                   require_focused: bool = True) -> str:
    target = str(binding.get('target_id') or '')
    if not re.fullmatch(r'[A-Za-z0-9_-]+', target):
        raise ValueError('ASIDE_TARGET_ID_INVALID')
    host, path, session = session_identity(str(binding.get('session_url') or ''))
    # Re-read identity before EVERY DOM operation. A user switching tabs is not
    # permission to operate whichever page happens to become foreground.
    return f'''await (async () => {{
const target = {json.dumps(target)};
const expectedPath = {json.dumps(path)};
const expectedSession = {json.dumps(session)};
// The Aside REPL sandbox has no global URL constructor. Parse only the exact
// allowlisted HTTPS base and query here; the page callback uses browser URL.
const same = raw => {{ try {{
  const address = String(raw).split('#')[0];
  const index = address.indexOf('?');
  if (index < 0 || address.slice(0,index) !== {json.dumps('https://' + host + path)}) return false;
  const ids = address.slice(index+1).split('&').map(pair => {{
    const i=pair.indexOf('='); return [decodeURIComponent(i<0 ? pair : pair.slice(0,i)),
      decodeURIComponent((i<0 ? '' : pair.slice(i+1)).replace(/\+/g,' '))];
  }}).filter(pair => pair[0] === 'sessionId');
  return ids.length === 1 && ids[0][1] === expectedSession;
}} catch {{ return false; }} }};
const tabs = await listBrowserTabs();
const matches = tabs.filter(t => same(t.url));
if (matches.length !== 1 || matches[0].targetId !== target)
  throw new Error('ASIDE_BOUND_SESSION_MISSING_OR_AMBIGUOUS');
if ({str(require_active).lower()} && (matches[0].active !== true ||
    ({str(require_focused).lower()} && matches[0].focusedWindow !== true)))
  throw new Error('ASIDE_NATIVE_BOUND_TAB_NOT_ACTIVE');
const page = await attachBrowserTab(target);
if (!same(await page.url())) throw new Error('ASIDE_BOUND_SESSION_CHANGED');
const value = {expression};
console.log({json.dumps(MARKER)} + JSON.stringify(value === undefined ? null : value));
}})().catch(error => console.log({json.dumps(MARKER)} + JSON.stringify({{__aside_bridge_error: String(error.message || error)}})))'''


def bind(project: Path, target_id: str, session_url: str, account: str | None = None) -> dict:
    session_identity(session_url)
    project = project.expanduser().resolve()
    if not (project / 'manifest.json').is_file():
        raise ValueError('ASIDE_PROJECT_MANIFEST_REQUIRED')
    binding = {'version': VERSION, 'project': str(project), 'target_id': target_id,
               'session_url': session_url, 'account': account,
               'bound_at': dt.datetime.now().astimezone().isoformat()}
    observation = repl(binding_script(binding, '({title: await page.title(), url: await page.url()})'), account)
    if session_identity(observation['url']) != session_identity(session_url):
        raise ValueError('ASIDE_BIND_OBSERVATION_MISMATCH')
    out = project / 'lanes/seedance/aside_binding.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix('.tmp')
    tmp.write_text(json.dumps(binding, ensure_ascii=False, indent=2) + '\n')
    tmp.replace(out)
    return {'ok': True, 'binding': str(out), 'target_id': target_id, 'title': observation['title']}


def require_project(project: Path | None = None, prompt_file: Path | None = None) -> dict:
    path = Path(os.environ.get('RUNWAY_ASIDE_BINDING', ''))
    if not path.is_file():
        raise ValueError('ASIDE_BINDING_REQUIRED')
    binding = json.loads(path.read_text())
    if not isinstance(binding, dict) or binding.get('version') != VERSION or not binding.get('project'):
        raise ValueError('ASIDE_BINDING_PROJECT_REQUIRED')
    bound = Path(binding['project']).expanduser().resolve()
    if project is not None and project.expanduser().resolve() != bound:
        raise ValueError('ASIDE_BINDING_PROJECT_MISMATCH')
    if prompt_file is not None and not prompt_file.resolve().is_relative_to(bound):
        raise ValueError('ASIDE_PROMPT_OUTSIDE_BOUND_PROJECT')
    return binding


def browser_js(js: str, binding_path: Path | None = None, *, require_active: bool = False,
               require_focused: bool = True) -> tuple[int, str, str]:
    try:
        path = binding_path or Path(os.environ.get('RUNWAY_ASIDE_BINDING', ''))
        if not path.is_file():
            raise ValueError('ASIDE_BINDING_REQUIRED: run aside_bridge.py bind for this project')
        binding = json.loads(path.read_text())
        if not isinstance(binding, dict) or binding.get('version') != VERSION:
            raise ValueError('ASIDE_BINDING_VERSION_MISMATCH')
        _host, path_part, session = session_identity(binding['session_url'])
        payload = {'code': js, 'path': path_part, 'session': session}
        expression = ('await page.evaluate(({code,path,session}) => {'
                      'const u=new URL(location.href); if(u.protocol!=="https:" || '
                      'u.host!=="app.runwayml.com" || u.pathname!==path || '
                      'u.searchParams.getAll("sessionId").length!==1 || '
                      'u.searchParams.get("sessionId")!==session) '
                      'throw new Error("ASIDE_SESSION_CHANGED_BEFORE_DOM"); '
                      'return (0,eval)(code);}, ' + json.dumps(payload, ensure_ascii=False) + ')')
        result = repl(binding_script(binding, expression, require_active=require_active,
                                     require_focused=require_focused), binding.get('account'))
        return 0, result if isinstance(result, str) else json.dumps(result, ensure_ascii=False), ''
    except (ValueError, OSError, KeyError, TypeError) as exc:
        return 3, '', str(exc)


# One read-only DOM transaction; no prompt text, media, account URLs or selectors
# leave the page. Native chooser visibility is outside the DOM's evidence scope.
OBSERVE_JS = r"""(() => {
 const visible = e => e.getClientRects().length > 0;
 const dialogs = [...document.querySelectorAll('[role="dialog"], [role="alertdialog"], dialog[open], [aria-modal="true"]')].filter(visible);
 const assetSelector = dialogs.some(e => e.getAttribute('aria-label') === 'Asset selector');
 const editors = [...document.querySelectorAll('[contenteditable][data-lexical-editor]')].filter(visible);
 const buttons = [...document.querySelectorAll('button')].filter(visible);
 const slots = buttons.map(e => (e.getAttribute('aria-label') || '').match(/^View (Image|Video|Audio) (\d+) larger$/)).filter(Boolean).map(m => ({modality:m[1], index:Number(m[2])}));
 const generate = buttons.filter(e => (e.getAttribute('aria-label') || e.innerText || '').trim() === 'Generate');
 return {schema:1, surface:assetSelector?'ASSET_SELECTOR':dialogs.length?'DIALOG':editors.length===1?'COMPOSER':'UNKNOWN',
  dialog_count:dialogs.length, editor_count:editors.length,
  prompt_characters:editors.length===1?(editors[0].textContent || '').length:null,
  references:slots.slice(0,32), references_truncated:slots.length>32,
  generate:{count:generate.length, enabled:generate.length===1?!generate[0].disabled && generate[0].getAttribute('aria-disabled')!=='true':null},
  native_chooser:'NOT_OBSERVED_BY_DOM'};
})()"""


def validate_observation(value):
    if not isinstance(value, dict) or value.get('schema') != 1:
        raise ValueError('ASIDE_OBSERVATION_INVALID')
    if value.get('surface') not in {'ASSET_SELECTOR','DIALOG','COMPOSER','UNKNOWN'}:
        raise ValueError('ASIDE_OBSERVATION_INVALID_SURFACE')
    for key in ('dialog_count','editor_count'):
        if type(value.get(key)) is not int or value[key] < 0:
            raise ValueError('ASIDE_OBSERVATION_INVALID_COUNT')
    chars=value.get('prompt_characters')
    if chars is not None and (type(chars) is not int or chars < 0):
        raise ValueError('ASIDE_OBSERVATION_INVALID_LENGTH')
    refs=value.get('references')
    if not isinstance(refs,list) or len(refs)>32 or type(value.get('references_truncated')) is not bool:
        raise ValueError('ASIDE_OBSERVATION_INVALID_REFERENCES')
    clean=[]
    for ref in refs:
        if not isinstance(ref,dict) or ref.get('modality') not in ('Image','Video','Audio') or type(ref.get('index')) is not int or ref['index']<1:
            raise ValueError('ASIDE_OBSERVATION_INVALID_REFERENCE')
        clean.append({'modality':ref['modality'],'index':ref['index']})
    generate=value.get('generate')
    if not isinstance(generate,dict) or type(generate.get('count')) is not int or generate['count']<0 or (generate.get('enabled') is not None and type(generate.get('enabled')) is not bool):
        raise ValueError('ASIDE_OBSERVATION_INVALID_GENERATE')
    # Allowlist only; never persist extra fields from a page/tool response.
    return {k:value[k] for k in ('surface','dialog_count','editor_count','prompt_characters','references_truncated')} | {
        'references':clean,'generate':{'count':generate['count'],'enabled':generate.get('enabled')},
        'native_chooser':'NOT_OBSERVED_BY_DOM'}


def observe(binding_path: Path, record: bool = False):
    binding_path=binding_path.expanduser().resolve()
    binding=json.loads(binding_path.read_text())
    if not isinstance(binding,dict) or binding.get('version')!=VERSION:
        raise ValueError('ASIDE_BINDING_VERSION_MISMATCH')
    project=Path(binding.get('project') or '').expanduser().resolve()
    if record and (binding_path != project/'lanes/seedance/aside_binding.json' or not (project/'manifest.json').is_file()):
        raise ValueError('ASIDE_OBSERVATION_RECORD_PROJECT_MISMATCH')
    # Exactly one existing guarded CLI call, without retries or cached identity.
    rc,out,err=browser_js(OBSERVE_JS,binding_path)
    if rc: raise ValueError(err or 'ASIDE_OBSERVATION_FAILED')
    value=validate_observation(json.loads(out))
    receipt={'schema':'aside_ui_observation_v1','ok':True,
        'observed_at':dt.datetime.now().astimezone().isoformat(),
        'binding_sha256':hashlib.sha256(binding_path.read_bytes()).hexdigest(),
        'read_only':True,'execution_authorized':False,'provider_acceptance_verified':False,
        **value}
    # Do not record against a binding switched while the observation ran.
    if json.loads(binding_path.read_text()) != binding:
        raise ValueError('ASIDE_BINDING_CHANGED_DURING_OBSERVATION')
    if record:
        destination=project/'lanes/seedance/ui_observation.json'
        temporary=None
        try:
            with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',dir=destination.parent,prefix='.ui_observation-',delete=False) as f:
                temporary=Path(f.name);f.write(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
            temporary.replace(destination)
        finally:
            if temporary is not None: temporary.unlink(missing_ok=True)
    return receipt


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='cmd', required=True)
    b = sub.add_parser('bind')
    b.add_argument('--project', type=Path, required=True)
    b.add_argument('--target-id', required=True)
    b.add_argument('--session-url', required=True)
    b.add_argument('--account')
    v = sub.add_parser('verify')
    v.add_argument('--binding', type=Path, required=True)
    o = sub.add_parser('observe', help='One guarded read of modal, references, editor and Generate; never authorizes execution')
    o.add_argument('--binding', type=Path, required=True)
    o.add_argument('--record', action='store_true', help='Save separate observation receipt; never modify lane status')
    args = p.parse_args()
    try:
        if args.cmd == 'observe':
            print(json.dumps(observe(args.binding,args.record),ensure_ascii=False))
            return 0
        if args.cmd == 'bind':
            print(json.dumps(bind(args.project, args.target_id, args.session_url, args.account), ensure_ascii=False))
            return 0
        rc, out, err = browser_js('JSON.stringify({title:document.title,url:location.href})', args.binding)
        print(out if rc == 0 else json.dumps({'ok': False, 'error': err}))
        return rc
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}))
        return 3


if __name__ == '__main__':
    raise SystemExit(main())
