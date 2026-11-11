#!/usr/bin/env python3
"""One released shelf block -> composer armed and preflighted, in one command.

Production is copy-paste: the shelf already fixes prompt, refs and settings.
Doing it as 40-90 model-planned micro steps (each re-reading a huge context)
made a 2-minute task take 10-75 minutes. This runs the proven DOM sequence
deterministically and returns one JSON result. It never clicks Generate: the
operator does that one click itself after reading `READY`. It stops, without
guessing, whenever a step needs the operator: a slot that must be uploaded
through the native chooser, a setting it cannot set.

Phases (re-runnable with --start):
  attach    clear composer refs, select every slot by the ledger's names from
            Runway Uploads (or Recents, for images generated inside Runway),
            never re-uploading held bytes; verify each slot
  settings  observe model/mode/duration/ratio/resolution/audio/tier; set 15s
  paste     helper paste-prompt (all shelf/pack gates) + settings-verify
  preflight read-only eight-check preflight -> READY
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
import re
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
import aside_bridge  # noqa: E402

HELPER = Path(__file__).resolve().parent / 'runway_ui_helper.py'
HELPER_20 = HELPER
HELPER_25 = Path(__file__).resolve().parents[2] / 'seedance25-prompt-en' / 'scripts' / 'runway_ui_helper.py'
PHASES = ('attach', 'settings', 'paste', 'preflight')
# Visible credit label per shelf generation_tier.
TIER_LABEL = {'Explore Mode': 'Unlimited', 'Unlimited': 'Unlimited'}
SELECTOR = '[role=dialog][aria-label="Asset selector"]'


class Stop(Exception):
    def __init__(self, code: str, detail: object = None, next_action: str = ''):
        super().__init__(code)
        self.code, self.detail, self.next_action = code, detail, next_action


def _now() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec='seconds')


class Page:
    """Bound-tab DOM (evaluate) and Playwright (locator) calls; identity re-checked each call."""

    def __init__(self, binding_path: Path):
        self.binding_path = binding_path
        self.binding = json.loads(binding_path.read_text(encoding='utf-8'))

    def js(self, code: str):
        rc, out, err = aside_bridge.browser_js(code, self.binding_path)
        if rc:
            raise Stop('ASIDE_DOM_CALL_FAILED', err, 'recovery-record ASIDE_CONTROL_UNAVAILABLE')
        try:
            return json.loads(out)
        except (TypeError, ValueError):
            return out

    def act(self, body: str):
        script = aside_bridge.binding_script(self.binding, 'await (async()=>{' + body + '})()')
        try:
            return aside_bridge.repl(script, self.binding.get('account'))
        except ValueError as exc:
            raise Stop('ASIDE_ACTION_FAILED', str(exc), 'recovery-record ASIDE_CONTROL_UNAVAILABLE')


STATE_JS = r"""(() => {
 const vis=e=>e&&e.getClientRects().length;
 const q=s=>document.querySelector(s);
 const ed=[...document.querySelectorAll('[contenteditable][data-lexical-editor]')].filter(vis);
 const bs=[...document.querySelectorAll('button')].filter(vis);
 const gen=bs.filter(e=>e.innerText.trim()==='Generate');
 return {model:q('button[aria-label="Video models"]')?.innerText.trim()||null,
  duration:q('button[aria-label="Duration"]')?.innerText.trim()||null,
  ratio:q('button[aria-label="Aspect ratio"]')?.innerText.trim()||null,
  resolution:q('button[aria-label="Resolution"]')?.innerText.trim()||null,
  multi_reference:q('input[value="multi-reference"]')?.checked??null,
  audio:q('button[aria-label="Audio"]')?.getAttribute('aria-pressed')??null,
  tier:q('#credit-info-button')?.innerText.trim()||null,
  refs:bs.map(e=>(e.getAttribute('aria-label')||'').match(/^View Image (\d+) larger$/)).filter(Boolean).map(m=>Number(m[1])),
  prompt:ed.length===1?ed[0].innerText:null, editors:ed.length,
  dialogs:[...document.querySelectorAll('[role=dialog]')].filter(vis).map(e=>e.getAttribute('aria-label')||'dialog'),
  generate:gen.map(e=>({disabled:e.disabled||e.getAttribute('aria-disabled')==='true'})),
  alerts:[...document.querySelectorAll('[role=alert]')].filter(vis).map(e=>e.innerText).slice(0,4)};
})()"""


def _wait_js(condition: str, timeout_ms: int = 8000) -> str:
    return ('(async()=>{const t0=Date.now();while(Date.now()-t0<%d){const v=(()=>{%s})();'
            'if(v)return v;await new Promise(r=>setTimeout(r,250));}return null;})()'
            % (timeout_ms, condition))


def _image_dims(path: Path) -> tuple[int, int] | None:
    out = subprocess.run(['sips', '-g', 'pixelWidth', '-g', 'pixelHeight', str(path)],
                         capture_output=True, text=True).stdout
    w = re.search(r'pixelWidth:\s*(\d+)', out)
    h = re.search(r'pixelHeight:\s*(\d+)', out)
    return (int(w.group(1)), int(h.group(1))) if w and h else None


def _helper(binding: Path, *argv: str) -> dict:
    p = subprocess.run([sys.executable, str(HELPER), '--binding', str(binding), *argv],
                       capture_output=True, text=True, timeout=180)
    try:
        value = json.loads(p.stdout[p.stdout.find('{'):]) if '{' in p.stdout else {}
    except ValueError:
        value = {'raw': p.stdout[-800:]}
    value.setdefault('ok', p.returncode == 0)
    if p.returncode:
        value['ok'] = False
        value.setdefault('error', (p.stderr or p.stdout)[-800:])
    return value


# --- phases ----------------------------------------------------------------

def phase_attach(ctx: dict, page: Page, log: list, from_slot: int = 1) -> None:
    import runway_ui_helper as h
    bundle = h.prepare_upload_bundle(ctx['project'], ctx['block'], ctx['pack_path'])
    state = page.js(STATE_JS)
    refs = sorted(state.get('refs') or [])
    if from_slot > 1:
        if refs != list(range(1, from_slot)):
            raise Stop('FROM_SLOT_STATE_MISMATCH', {'refs': refs, 'from_slot': from_slot},
                       'composer must hold exactly the earlier slots; re-run from attach')
    elif refs:
        for k in reversed(refs):
            page.js('(()=>{const b=document.querySelector(\'button[aria-label="Remove Image %d"]\');'
                    'if(!b)throw Error("REMOVE_MISSING");b.click();return true})()' % k)
        log.append({'step': 'clear_composer_refs', 'removed': refs})
    for index, slot in enumerate(bundle['slots'], start=1):
        if int(re.sub(r'\D', '', slot['reference_token'])) != index:
            raise Stop('PACK_TOKENS_NOT_CONSECUTIVE', bundle['slots'])
        if index < from_slot:
            continue
        scan_for_warning(ctx, page, f'run-block before attach {slot["reference_token"]}')
        file_path = Path(bundle['bundle_dir']) / slot['alias_name']
        if slot['attach'] != 'SELECT_EXISTING_RUNWAY_UPLOAD':
            raise Stop('SLOT_NEEDS_NATIVE_UPLOAD',
                       {'slot': slot['reference_token'], 'file': str(file_path)}, _upload_next(file_path, index))
        _select_from_uploads(ctx, page, slot, index, file_path, log)


def _upload_next(file_path: Path, index: int) -> str:
    return (f'upload {file_path.name} into Image{index} via the native chooser (aside-operator.md), verify it, '
            f'record-runway-attach --path {file_path} --name {file_path.name} --how uploaded, '
            f'then run-block --start attach --from-slot {index + 1}')


def _select_from_uploads(ctx: dict, page: Page, slot: dict, index: int, file_path: Path, log: list) -> None:
    import runway_ui_helper as h
    opened = page.js(_wait_js(
        'if(document.querySelector(\'%s\'))return "open";'
        'const b=[...document.querySelectorAll("button")].filter(e=>e.getClientRects().length&&e.innerText.trim()==="Reference");'
        'if(b.length===1&&!window.__rbOpen){window.__rbOpen=1;b[0].click();}return null;' % SELECTOR, 8000))
    page.js('(()=>{window.__rbOpen=0;return true})()')
    if opened != 'open':
        raise Stop('ASSET_SELECTOR_NOT_OPENED', {'slot': slot['reference_token']})
    pills = slot.get('search_pills') or {}
    for name in slot['search_names']:
        # Uploads for RW_/uploaded names; Recents for images generated inside Runway.
        pill = pills.get(name) or 'Uploads'
        page.js('(()=>{const d=document.querySelector(\'%s\');const b=[...d.querySelectorAll("button")]'
                '.filter(e=>e.innerText.trim()===%s);if(b.length!==1)throw Error("FILTER_PILL");'
                'b[0].click();return true})()' % (SELECTOR, json.dumps(pill)))
        page.act('const i=page.locator(%s);await i.fill(%s);await i.press("Enter");return true;'
                 % (json.dumps(SELECTOR + ' input[type=search]'), json.dumps(name)))
        count = page.js(_wait_js(
            'const d=document.querySelector(\'%s\');if(!d)return null;'
            'const n=[...d.querySelectorAll("[role=button]")].filter(e=>e.innerText.split("\\n").some(l=>l.trim()===%s)).length;'
            'return n?n:null;' % (SELECTOR, json.dumps(name)), 6000)) or 0
        if not count:
            h.record_runway_attach(slot['sha256'], name, 'missing', project=str(ctx['project']),
                                   block_id=ctx['block'], asset_id=slot['asset_id'])
            log.append({'step': 'uploads_search', 'slot': slot['reference_token'], 'name': name, 'pill': pill,
                        'rows': 0})
            continue
        if count > 1 and not name.startswith('RW_'):
            raise Stop('LEGACY_NAME_AMBIGUOUS', {'slot': slot['reference_token'], 'name': name, 'pill': pill,
                                                 'rows': count},
                       'select the matching row by enlarged thumbnail, record-runway-attach --how reused, '
                       f'then run-block --start attach --from-slot {index + 1}')
        page.act('const r=page.locator(%s).filter({hasText:%s}).first();await r.dblclick();return true;'
                 % (json.dumps(SELECTOR + ' [role=button]'), json.dumps(name)))
        landed = page.js(_wait_js(
            'return document.querySelector(\'button[aria-label="View Image %d larger"]\')?"ok":null;' % index, 20000))
        if landed != 'ok':
            raise Stop('SLOT_NOT_FILLED_AFTER_SELECT', {'slot': slot['reference_token'], 'name': name})
        _verify_slot(page, index, file_path, slot, log)
        h.record_runway_attach(slot['sha256'], name, 'reused', project=str(ctx['project']),
                               block_id=ctx['block'], asset_id=slot['asset_id'])
        log.append({'step': 'attached_from_uploads', 'slot': slot['reference_token'], 'name': name, 'pill': pill,
                    'rows': count})
        return
    page.js('(()=>{const b=[...document.querySelectorAll(\'%s button[aria-label="Close"]\')];'
            'if(b[0])b[0].click();return true})()' % SELECTOR)
    raise Stop('SLOT_NEEDS_NATIVE_UPLOAD',
               {'slot': slot['reference_token'], 'file': str(file_path), 'searched': slot['search_names']},
               _upload_next(file_path, index))


def _verify_slot(page: Page, index: int, file_path: Path, slot: dict, log: list) -> None:
    """Enlarged overlay must show an image with the bundle file's aspect ratio."""
    seen = page.js(
        '(async()=>{const b=document.querySelector(\'button[aria-label="View Image %d larger"]\');b.click();'
        'const ok=i=>i.getClientRects().length&&i.clientWidth>300&&i.complete&&i.naturalWidth>0;'
        # the enlarged image lives in the modal; page cards behind it also pass the size test
        'const t0=Date.now();let im=null;while(Date.now()-t0<8000){im=[...document.querySelectorAll(\'[role="dialog"] img,[aria-modal="true"] img\')].find(ok);'
        'if(!im&&Date.now()-t0>4000)im=[...document.images].filter(ok).sort((a,b)=>b.clientWidth*b.clientHeight-a.clientWidth*a.clientHeight)[0];if(im)break;await new Promise(r=>setTimeout(r,250));}'
        'return im?{w:im.naturalWidth,h:im.naturalHeight}:null;})()' % index)
    shot = f'rb_{re.sub(r"[^A-Za-z0-9_-]", "_", slot.get("block", ""))}{slot["reference_token"]}_{int(time.time())}.png'
    try:
        page.act('await page.screenshot({path:%s});return true;' % json.dumps(shot))
        found = sorted(Path.home().glob(f'.aside/*/*/sessions/*/{shot}'))
        screenshot = str(found[-1]) if found else None
    except Stop:
        screenshot = None
    page.js('(()=>{const c=[...document.querySelectorAll(\'button[aria-label="Close"]\')]'
            '.filter(e=>e.getClientRects().length);if(c[0])c[0].click();return true})()')
    dims = _image_dims(file_path)
    if not seen or not dims:
        raise Stop('SLOT_IMAGE_NOT_VERIFIED', {'slot': slot['reference_token'], 'seen': seen, 'file': dims})
    if abs(seen['w'] / seen['h'] - dims[0] / dims[1]) > 0.02:
        raise Stop('SLOT_IMAGE_ASPECT_MISMATCH', {'slot': slot['reference_token'], 'seen': seen, 'file': dims},
                   'remove that slot; the Uploads row is not this file')
    log.append({'step': 'slot_verified', 'slot': slot['reference_token'], 'overlay': seen, 'file': dims,
                'enlarged_screenshot': screenshot})


def expected_settings(settings: dict) -> dict:
    tier = settings.get('generation_tier')
    if tier and tier not in TIER_LABEL:
        raise Stop('TIER_NOT_AUTOMATABLE', tier, 'set the tier by hand; run-block only arms free tiers')
    return {'model': settings.get('model', 'Seedance 2.0'), 'duration': f"{int(settings['duration_sec'])}s",
            'ratio': settings.get('aspect_ratio'), 'resolution': settings.get('resolution'),
            'multi_reference': (settings.get('mode') or '').lower() == 'multi-reference',
            'audio': 'true' if str(settings.get('audio', '')).upper() == 'ON' else 'false',
            'tier': TIER_LABEL.get(tier) if tier else None}


def settings_diff(state: dict, want: dict) -> dict:
    return {k: {'want': v, 'seen': state.get(k)} for k, v in want.items()
            if v is not None and state.get(k) != v}


def phase_settings(ctx: dict, page: Page, log: list) -> None:
    want = expected_settings(ctx['settings'])
    diff = settings_diff(page.js(STATE_JS), want)
    if 'duration' in diff:
        page.js('(()=>{const b=document.querySelector(\'button[aria-label="Duration"]\');'
                'if(!b)throw Error("DURATION");b.click();return true})()')
        page.act('const i=page.locator(\'input[aria-label="Duration in seconds"]\');await i.fill(%s);'
                 'await i.press("Enter");await page.keyboard.press("Escape");return true;'
                 % json.dumps(str(int(ctx['settings']['duration_sec']))))
        log.append({'step': 'set_duration', 'value': want['duration']})
        diff = settings_diff(page.js(STATE_JS), want)
    if diff:
        raise Stop('SETTINGS_NEED_OPERATOR', diff, 'set these visible controls by hand, then run-block --start settings')
    log.append({'step': 'settings_match'})


def clear_stale_prompt(page: Page, log: list) -> None:
    """Runway keeps the previous block's prompt after Generate; paste-prompt refuses a
    non-empty editor, so empty the one visible Lexical editor first and re-observe."""
    read = ("(()=>{const a=[...document.querySelectorAll('[contenteditable][data-lexical-editor]')]"
            ".filter(e=>e.getClientRects().length);return a.length===1?(a[0].innerText||'').trim().length:-1})()")
    before = page.js(read)
    if not before or before < 0:
        return
    page.js("(()=>{const e=[...document.querySelectorAll('[contenteditable][data-lexical-editor]')]"
            ".filter(x=>x.getClientRects().length)[0];e.focus();const r=document.createRange();"
            "r.selectNodeContents(e);const s=window.getSelection();s.removeAllRanges();s.addRange(r);return true})()")
    page.act("await page.keyboard.press('Backspace');return true;")
    after = page.js(read)
    if after:
        raise Stop('PROMPT_CLEAR_FAILED', {'before_chars': before, 'after_chars': after})
    log.append({'step': 'cleared_stale_prompt', 'before_chars': before})


def phase_paste(ctx: dict, page: Page, log: list) -> None:
    clear_stale_prompt(page, log)
    pasted = _helper(ctx['binding_path'], 'paste-prompt', '--replace', '--file', str(ctx['prompt_path']),
                     '--pack', str(ctx['pack_path']))
    if not pasted.get('ok'):
        raise Stop('PASTE_FAILED', pasted)
    verified = _helper(ctx['binding_path'], 'settings-verify', '--project', str(ctx['project']),
                       '--block', ctx['block'], '--visible-model', ctx['settings'].get('model', 'Seedance 2.0'),
                       '--duration-sec', str(int(ctx['settings']['duration_sec'])))
    if not verified.get('ok'):
        raise Stop('SETTINGS_VERIFY_FAILED', verified)
    log.append({'step': 'pasted_and_settings_verified'})


def preflight_errors(state: dict, want: dict, prompt: str, n_refs: int) -> list[str]:
    norm = lambda t: re.sub(r'\s+', '', t or '')  # noqa: E731
    fail = []
    if state.get('editors') != 1 or norm(state.get('prompt')) != norm(prompt):
        fail.append('PROMPT_MISMATCH')
    if state.get('dialogs'):
        fail.append('DIALOG_OPEN')
    fail += [f'SETTING_{k}' for k in settings_diff(state, want)]
    if sorted(state.get('refs') or []) != list(range(1, n_refs + 1)):
        fail.append('REF_COUNT')
    gen = state.get('generate') or []
    if len(gen) != 1 or gen[0].get('disabled'):
        fail.append('GENERATE_NOT_READY')
    return fail


def phase_preflight(ctx: dict, page: Page, log: list) -> None:
    scan_for_warning(ctx, page, 'run-block before Generate (preflight)')
    state = page.js(STATE_JS)
    fail = preflight_errors(state, expected_settings(ctx['settings']),
                            ctx['prompt_path'].read_text(encoding='utf-8'), len(ctx['refs']))
    if fail:
        raise Stop('PREFLIGHT_FAILED', fail)
    log.append({'step': 'preflight_ok'})


# --- driver ----------------------------------------------------------------

def load_context(project: Path, block: str) -> dict:
    project = project.expanduser().resolve()
    shelf = project / 'preprod/04_shelf' / block
    if not shelf.is_dir():
        raise Stop('NOT_A_SHELF_BLOCK', str(shelf), 'run-block only arms released preprod shelf blocks')
    import preprod
    errors = preprod.verify_shelf(project, block)
    if errors:
        raise Stop('SHELF_VERIFY_FAILED', errors, 'return to P4; never edit a released prompt')
    binding = project / 'lanes/seedance/aside_binding.json'
    if not binding.is_file():
        raise Stop('ASIDE_BINDING_REQUIRED', str(binding), 'bind this project to its own Runway session tab')
    pack = json.loads((shelf / 'pack.json').read_text(encoding='utf-8'))
    settings = json.loads((shelf / 'settings.json').read_text(encoding='utf-8'))
    global HELPER
    # Seedance 2.5 shelves go through the 2.5 model-policy adapter (same UI code, 2.5 model guard).
    HELPER = HELPER_25 if settings.get('model') == 'Seedance 2.5' else HELPER_20
    return {'project': project, 'block': block, 'binding_path': binding, 'pack_path': shelf / 'pack.json',
            'prompt_path': shelf / 'prompt.txt', 'refs': pack.get('reference_role_map') or [],
            'settings': settings}


def scan_for_warning(ctx: dict, page: Page, where: str) -> None:
    """Visible-text account-warning check; a hit writes the HOLD file and stops the run."""
    import runway_ui_helper as h
    found = h.detect_account_warning(*h.parse_warning_payload(page.js(h.WARNING_TEXT_JS)))
    if found:
        result = h.account_warning_result(found, ctx['project'], ctx['block'], where)
        raise Stop('ACCOUNT_WARNING', result, result['next_action'])


def run(project: Path, block: str, *, start: str = 'attach', from_slot: int = 1) -> dict:
    import runway_ui_helper as h
    hold = h.read_provider_hold()
    if hold is not None:  # touch nothing: no log file, no browser
        return {'block': block, 'ok': False, 'outcome': 'STOPPED', 'stop': 'PROVIDER_HOLD',
                'reason_code': 'PROVIDER_HOLD', 'hold': hold, 'hold_file': str(h.provider_hold_path()),
                'next_action': 'Ask the user; clear only with `video-codex-runtime hold --clear` after their confirmation.'}
    t0 = time.monotonic()
    log: list = []
    result = {'block': block, 'started_at': _now(), 'start': start}
    try:
        ctx = load_context(project, block)
        page = Page(ctx['binding_path'])
        scan_for_warning(ctx, page, 'run-block start')
        for phase in PHASES[PHASES.index(start):]:
            if phase == 'attach':
                phase_attach(ctx, page, log, from_slot)
            elif phase == 'settings':
                phase_settings(ctx, page, log)
            elif phase == 'paste':
                phase_paste(ctx, page, log)
            else:
                phase_preflight(ctx, page, log)
        result.update(ok=True, outcome='READY',
                      next_action='operator clicks Generate once (seedance-production exactly-once rules), '
                                  'confirms the matching card, then the next block')
    except Stop as stop:
        result.update(ok=False, outcome='STOPPED', stop=stop.code, detail=stop.detail, next_action=stop.next_action)
        if stop.code == 'ACCOUNT_WARNING':
            result['reason_code'] = 'ACCOUNT_WARNING'
    result['steps'] = log
    result['seconds'] = round(time.monotonic() - t0, 1)
    try:
        out = Path(project).expanduser().resolve() / 'lanes/seedance/run_block'
        out.mkdir(parents=True, exist_ok=True)
        with (out / 'runs.jsonl').open('a', encoding='utf-8') as handle:
            handle.write(json.dumps(result, ensure_ascii=False, default=str) + '\n')
    except OSError:
        pass
    return result


def record_generate(project: Path, block: str, state: str, clicked_at: str = '') -> dict:
    """Bookkeeping only (no browser): the operator clicked Generate once and saw the matching card."""
    if state not in {'IN_QUEUE', 'GENERATING'}:
        raise Stop('STATE_INVALID', state)
    ctx = load_context(project, block)
    pack = json.loads(ctx['pack_path'].read_text(encoding='utf-8'))
    binding = json.loads(ctx['binding_path'].read_text(encoding='utf-8'))
    now = _now()
    refs = [r.get('asset_id') for r in ctx['refs']]
    job = {'block_id': block, 'status': state, 'visible_state': state,
           'prompt_sha256': pack.get('prompt_sha256'), 'reference_asset_ids': refs, 'references': refs,
           'session_url': binding.get('session_url'), 'click_count': 1, 'clicked_at': clicked_at or now,
           'accepted_at': now, 'accepted_prompt_exact': True, 'downloaded': False,
           'quality_verdict': 'NOT_REVIEWED', 'settings': ctx['settings'],
           'local_output_id': block + '_output1', 'via': 'run-block'}
    written = []
    for rel in ('state.json', 'manifest.json', 'lanes/seedance/status.json'):
        path = ctx['project'] / rel
        if not path.is_file():
            continue
        doc = json.loads(path.read_text(encoding='utf-8'))
        jobs = doc.setdefault('provider_jobs', [])
        # a director-requested retake is a new job: number it after the block's earlier outputs
        take = sum(1 for j in jobs if j.get('block_id') == block) + 1
        jobs.append({**job, 'local_output_id': f'{block}_output{take}'})
        doc['provider_job_count'] = len(jobs)
        doc['updated_at'] = now
        tmp = path.with_suffix('.tmp')
        tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        tmp.replace(path)
        written.append(rel)
    return {'ok': True, 'block': block, 'state': state, 'written': written}
