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
    value = json.loads(matches[0])
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
    args = p.parse_args()
    try:
        if args.cmd == 'bind':
            print(json.dumps(bind(args.project, args.target_id, args.session_url, args.account), ensure_ascii=False))
            return 0
        rc, out, err = browser_js('JSON.stringify({title:document.title,url:location.href})', args.binding)
        print(out if rc == 0 else json.dumps({'ok': False, 'error': err}))
        return rc
    except ValueError as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}))
        return 3


if __name__ == '__main__':
    raise SystemExit(main())
