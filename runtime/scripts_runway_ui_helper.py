#!/usr/bin/env python3
"""Deterministic Runway/Safari synthetic-input helper (doctrine §2b enforced in code).

Agents must NOT hand-roll osascript for clipboard/keystroke/picker work. Every
command here bundles activate + frontmost-verify + action ATOMICALLY in one
osascript, refuses to fire keys when focus is wrong, and appends evidence JSONL.

Commands:
  frontmost                              print frontmost app
  escape                                 send ESC to Safari (verified)
  paste-image  --png F                   Route C: clipboard=PNG data -> verified Cmd+V into Safari
  paste-text   --file F                  clipboard=text -> verified Cmd+V into Safari
  js-click-file-input [--index N]        Route B: do JavaScript click on real input[type=file]
  js-insert-prompt --file F [--clear]    prompt Route B: execCommand insertText (React-safe)
  picker-go    --path P                  verified file-picker sheet -> Cmd+Shift+G -> path -> Return
  recover                                focus-pollution ritual step: ESC + frontmost report

Common flags: --evidence <jsonl path> --state <label>  (evidence line per command)
Exit codes: 0 ok, 2 focus-abort, 3 applescript error.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path

def osa(script: str) -> tuple[int, str, str]:
    p = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, timeout=60)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


# --- browser targeting -------------------------------------------------------
# Written 2026-07-19 when Runway lived in Safari; the workflow moved to Chrome on
# 2026-07-21 and this was never ported, so the watcher polled a browser with no
# Runway tab, logged JS_ERROR, and exited 4 after five polls — the infinite
# generation loop died at the first wait. Chrome also does not accept Safari's
# `do JavaScript ... in current tab`; it uses `execute javascript ... in active tab`.
# Resolve the browser from where the Runway tab actually is. (2026-07-28)

RUNWAY_HOST = 'app.runwayml.com'
# The two browsers use different word order, not just different verbs:
#   Safari:  do JavaScript "<js>" in current tab of front window
#   Chrome:  execute active tab of front window javascript "<js>"
# Getting this wrong yields a -1723 "access not allowed" that *looks* like a
# permission problem and hides Chrome's real, actionable message.
_BROWSERS = {
    'Google Chrome': {'tmpl': 'execute active tab of front window javascript {js}'},
    'Safari':        {'tmpl': 'do JavaScript {js} in current tab of front window'},
}


def _has_runway_tab(app: str) -> bool:
    rc, out, _ = osa(f'tell application "{app}" to get URL of tabs of windows')
    return rc == 0 and RUNWAY_HOST in out


def resolve_target_app() -> str:
    """Pick the browser that actually holds the Runway board.

    Order: explicit env override -> browser with a visible Runway tab -> Chrome.
    """
    forced = os.environ.get('RUNWAY_BROWSER')
    if forced:
        if forced not in _BROWSERS:
            raise SystemExit(f'RUNWAY_BROWSER={forced!r} not supported; use one of {list(_BROWSERS)}')
        return forced
    for app in ('Google Chrome', 'Safari'):
        try:
            if _has_runway_tab(app):
                return app
        except Exception:
            continue
    return 'Google Chrome'


TARGET_APP = resolve_target_app()


def browser_js(js: str) -> tuple[int, str, str]:
    """Run JS in the Runway tab using the target browser's own AppleScript dialect."""
    tmpl = _BROWSERS[TARGET_APP]['tmpl']
    return osa(f'tell application "{TARGET_APP}" to ' + tmpl.format(js=json.dumps(js)))


def evidence(args, action: str, expected: str, observed: str, verdict: str) -> None:
    row = {'ts': dt.datetime.now().isoformat(timespec='seconds'), 'tool': 'runway_ui_helper',
           'state': getattr(args, 'state', None), 'action': action,
           'expected': expected, 'observed': observed, 'verdict': verdict}
    print(json.dumps(row, ensure_ascii=False))
    ev = getattr(args, 'evidence', None)
    if ev:
        p = Path(ev).expanduser()
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open('a', encoding='utf-8') as f:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')


VERIFY_BLOCK = f'''
tell application "{TARGET_APP}" to activate
delay 0.5
tell application "System Events"
    set fm to name of first application process whose frontmost is true
end tell
if fm is not "{TARGET_APP}" then error "ABORT_FOCUS_NOT_{TARGET_APP.upper()}: " & fm
'''


def run_verified(args, action: str, tail: str, pre: str = '') -> int:
    """pre (e.g. clipboard load) + activate + frontmost verify + tail action, ONE osascript."""
    rc, out, err = osa(pre + VERIFY_BLOCK + tail)
    if rc != 0:
        verdict = 'FOCUS_ABORT' if 'ABORT_FOCUS' in err else 'APPLESCRIPT_ERROR'
        evidence(args, action, f'frontmost={TARGET_APP} then action', err or out, verdict)
        return 2 if verdict == 'FOCUS_ABORT' else 3
    evidence(args, action, f'frontmost={TARGET_APP} then action', out or 'done', 'DONE_VERIFY_VISUALLY')
    return 0


def cmd_frontmost(args) -> int:
    rc, out, err = osa('tell application "System Events" to name of first application process whose frontmost is true')
    print(out or err)
    return rc


def cmd_escape(args) -> int:
    return run_verified(args, 'ESC', 'tell application "System Events" to key code 53')


def cmd_paste_image(args) -> int:
    png = Path(args.png).expanduser().resolve()
    if not png.exists() or png.stat().st_size == 0:
        evidence(args, 'paste-image', 'png exists', f'missing: {png}', 'FAIL')
        return 1
    pre = f'set the clipboard to (read (POSIX file "{png}") as «class PNGf»)\n'
    return run_verified(args, f'paste-image {png.name}', 'tell application "System Events" to keystroke "v" using {command down}', pre)


def cmd_paste_text(args) -> int:
    f = Path(args.file).expanduser().resolve()
    txt = f.read_text(encoding='utf-8')
    subprocess.run(['pbcopy'], input=txt.encode(), check=True)
    rc = run_verified(args, f'paste-text {f.name} ({len(txt)} chars)',
                      'tell application "System Events" to keystroke "v" using {command down}')
    if rc == 0:
        evidence(args, 'paste-text-verify-hint', 'visible counter must show char count',
                 f'expected counter ~{len(txt)} / 3500 — verify on screenshot, NOT via AX tree', 'VERIFY_BY_COUNTER')
    return rc


def do_js(args, action: str, js: str) -> int:
    osa(f'tell application "{TARGET_APP}" to activate')
    rc, out, err = browser_js(js)
    if rc != 0:
        low = err.lower()
        if TARGET_APP == 'Safari' and ('javascript' in low or 'not allowed' in low):
            hint = 'SAFARI_JS_FROM_APPLE_EVENTS_DISABLED — user action: Safari Develop menu > Allow JavaScript from Apple Events'
        elif TARGET_APP == 'Google Chrome' and ('not allowed' in low or '-1743' in err or 'privile' in low):
            hint = ('CHROME_JS_FROM_APPLE_EVENTS_DISABLED — user action: Chrome menu > View > Developer > '
                    'Allow JavaScript from Apple Events, and grant Terminal/Codex automation permission')
        else:
            hint = err
        evidence(args, action, f'{TARGET_APP} javascript ok', hint,
                 'BLOCKED' if 'DISABLED' in hint else 'APPLESCRIPT_ERROR')
        return 3
    evidence(args, action, f'{TARGET_APP} javascript ok', out or 'done', 'DONE_VERIFY_VISUALLY')
    return 0


def cmd_js_click_file_input(args) -> int:
    js = (f"var els=document.querySelectorAll('input[type=file]');"
          f"var el=els[{args.index}]; if(!el) 'NO_FILE_INPUT_AT_INDEX';"
          f"else {{ el.style.display='block'; el.click(); 'CLICKED_FILE_INPUT_'+{args.index}+'_of_'+els.length; }}")
    return do_js(args, f'js-click-file-input[{args.index}]', js)


def cmd_js_insert_prompt(args) -> int:
    txt = Path(args.file).expanduser().read_text(encoding='utf-8')
    clear = "document.execCommand('selectAll');" if args.clear else ''
    js = (f"var el=document.querySelector('textarea, [contenteditable=\"true\"]');"
          f"if(!el) 'NO_PROMPT_EDITOR'; else {{ el.focus(); {clear} "
          f"document.execCommand('insertText', false, {json.dumps(txt)}); 'INSERTED_'+{len(txt)}+'_CHARS'; }}")
    rc = do_js(args, f'js-insert-prompt ({len(txt)} chars)', js)
    if rc == 0:
        evidence(args, 'js-insert-verify-hint', 'visible counter', f'verify counter ~{len(txt)} / 3500 on screenshot', 'VERIFY_BY_COUNTER')
    return rc


def cmd_picker_go(args) -> int:
    path = str(Path(args.path).expanduser())
    pre = f'set the clipboard to {json.dumps(path)}\n'
    tail = f'''
tell application "System Events"
    tell process "{TARGET_APP}"
        if not (exists sheet 1 of window 1) then error "ABORT_NO_PICKER_SHEET"
        keystroke "g" using {{command down, shift down}}
        delay 0.5
        if not (exists sheet 1 of window 1) then error "ABORT_GO_SHEET_LOST"
        keystroke "a" using {{command down}}
        delay 0.1
        key code 51
        delay 0.1
        keystroke "v" using {{command down}}
        delay 0.3
        key code 36
    end tell
end tell
'''
    return run_verified(args, f'picker-go {path}', tail, pre=pre)


GEN_BTN_JS = r"""
(() => {
  const b = [...document.querySelectorAll('button')].find(x => /generate/i.test(x.textContent || ''));
  if (!b) return 'NO_GENERATE_BUTTON';
  const chain = [];
  let el = b;
  for (let i = 0; el && i < 4; i++, el = el.parentElement) {
    const cs = getComputedStyle(el);
    chain.push({
      tag: el.tagName,
      text: (el.textContent || '').trim().slice(0, 40),
      backgroundColor: cs.backgroundColor,
      color: cs.color,
      className: String(el.className || '').slice(0, 120)
    });
  }
  const rect = b.getBoundingClientRect();
  return JSON.stringify({
    text: (b.textContent || '').trim().slice(0, 40),
    rect: {x: Math.round(rect.x), y: Math.round(rect.y), w: Math.round(rect.width), h: Math.round(rect.height)},
    color_source: 'visible CSS button/ancestor background only; disabled/aria/data-soft-disabled ignored by user rule',
    chain
  });
})()
"""


def _rgb_triplet(value: str):
    import re
    m = re.search(r'rgba?\((\d+),\s*(\d+),\s*(\d+)', value or '')
    if not m:
        return None
    return tuple(map(int, m.groups()))


def _is_blue(rgb) -> bool:
    if not rgb:
        return False
    r, g, b = rgb
    return b >= 100 and b > r + 25 and b > g + 10


def _is_gray(rgb) -> bool:
    if not rgb:
        return False
    r, g, b = rgb
    return max(r, g, b) - min(r, g, b) <= 18


def read_generate_state() -> dict:
    """Read visible Generate button color. User rule: blue=clickable, gray=inactive; ignore AX/DOM disabled heuristics."""
    rc, out, err = browser_js(GEN_BTN_JS)
    if rc != 0:
        # -1723 / "not allowed" means the browser refuses Apple Events JS. That is a
        # standing permission blocker, not a transient read error: retrying cannot
        # clear it, so surface it distinctly and let the watcher stop at once
        # instead of burning five polls and exiting 4 with a vague JS_ERROR.
        low = err.lower()
        if '-1723' in err or 'not allowed' in low or '허용되지 않' in err:
            if TARGET_APP == 'Google Chrome':
                action = ('Chrome menu > View > Developer > "Allow JavaScript from Apple Events" (enable it), '
                          'then re-run. Also confirm Terminal/Codex has Automation permission for Chrome in '
                          'System Settings > Privacy & Security > Automation.')
            else:
                action = 'Safari menu > Develop > "Allow JavaScript from Apple Events" (enable it), then re-run.'
            return {'verdict': 'BLOCKED_BROWSER_JS_PERMISSION', 'browser': TARGET_APP,
                    'required_user_action': action, 'error': err[-200:]}
        return {'verdict': 'JS_ERROR', 'browser': TARGET_APP, 'error': err[-200:]}
    if out == 'NO_GENERATE_BUTTON':
        return {'verdict': 'NO_GENERATE_BUTTON'}
    try:
        st = json.loads(out)
    except Exception:
        return {'verdict': 'PARSE_ERROR', 'raw': out[:200]}
    rgbs = []
    for item in st.get('chain', []):
        rgb = _rgb_triplet(item.get('backgroundColor', ''))
        if rgb and rgb != (0, 0, 0):
            rgbs.append(rgb)
    st['sampled_background_rgbs'] = rgbs
    if any(_is_blue(rgb) for rgb in rgbs):
        st['verdict'] = 'BLUE_ENABLED'
    elif any(_is_gray(rgb) for rgb in rgbs):
        st['verdict'] = 'GRAY_INACTIVE'
    else:
        st['verdict'] = 'UNKNOWN_COLOR_TREAT_AS_INACTIVE'
    return st


def cmd_check_generate(args) -> int:
    st = read_generate_state()
    evidence(args, 'check-generate', 'read visible button color via CSS', json.dumps(st, ensure_ascii=False), st['verdict'])
    return 0 if st['verdict'] == 'BLUE_ENABLED' else 1


def cmd_watch_generate(args) -> int:
    """Self-judging slot watcher: polls the Generate button every --interval seconds.
    On GRAY->BLUE transition: appends SLOT_FREED event, posts a macOS notification,
    and EXITS 0 so the caller (agent or user) resumes work. No goal/resident agent needed.
    Exit codes: 0 slot freed, 3 timeout, 4 repeated color-read errors,
    5 standing blocker (browser JS permission / no Generate button)."""
    import time as _t
    deadline = _t.time() + args.max_hours * 3600
    was_disabled = False
    js_errors = 0
    warned_already_blue = False
    while _t.time() < deadline:
        st = read_generate_state()
        evidence(args, 'watch-generate poll', 'button state', json.dumps(st, ensure_ascii=False), st['verdict'])
        # Standing blockers: polling cannot clear these. Stop now with the exact
        # user action instead of looping until timeout.
        if st['verdict'] in ('BLOCKED_BROWSER_JS_PERMISSION', 'NO_GENERATE_BUTTON'):
            if st['verdict'] == 'NO_GENERATE_BUTTON':
                st['required_user_action'] = (
                    f'No Generate button in the front {TARGET_APP} tab. Bring the logged-in '
                    'app.runwayml.com Generate board to the front tab, then re-run.')
            osa(f'display notification "watcher stopped: {st["verdict"]}" with title "video-team watcher"')
            print(json.dumps({'result': st['verdict'], 'state': st}, ensure_ascii=False))
            return 5
        if st['verdict'] == 'BLUE_ENABLED':
            # Default semantics are "fire on gray -> blue". If the button is ALREADY
            # blue when the watcher starts, that transition never happens and the
            # watcher sits idle until --max-hours. Say so instead of looking alive.
            if not was_disabled and not args.immediate and not warned_already_blue:
                warned_already_blue = True
                evidence(args, 'watch-generate', 'gray->blue transition',
                         'button was ALREADY BLUE at watcher start — no transition will occur. '
                         'A slot is free right now: submit, or re-run with --immediate to fire on blue.',
                         'IDLE_ALREADY_BLUE')
                osa('display notification "Generate가 이미 파란색 — 지금 제출 가능 (워처는 전환 대기 중)" with title "video-team watcher"')
            if was_disabled or args.immediate:
                if args.event_queue:
                    q = Path(args.event_queue).expanduser()
                    q.parent.mkdir(parents=True, exist_ok=True)
                    with q.open('a', encoding='utf-8') as f:
                        f.write(json.dumps({'ts': dt.datetime.now().isoformat(timespec='seconds'),
                                            'event': 'SLOT_FREED_GENERATE_BLUE', 'source': 'watch-generate'}, ensure_ascii=False) + '\n')
                osa('display notification "Runway Generate 버튼 파란색 복귀 — 슬롯 해제, 백필 진행 가능" with title "video-team watcher"')
                print(json.dumps({'result': 'SLOT_FREED', 'state': st}, ensure_ascii=False))
                return 0
        elif st['verdict'] == 'GRAY_INACTIVE':
            was_disabled = True
            js_errors = 0
        else:
            js_errors += 1
            if js_errors >= 5:
                print(json.dumps({'result': 'JS_ERRORS_REPEATED', 'state': st}, ensure_ascii=False))
                return 4
        _t.sleep(args.interval)
    print(json.dumps({'result': 'TIMEOUT'}))
    return 3


def cmd_recover(args) -> int:
    rc1 = cmd_escape(args)
    rc, out, _ = osa('tell application "System Events" to name of first application process whose frontmost is true')
    evidence(args, 'recover', 'ESC sent, frontmost reported', f'frontmost={out}', 'RECOVERY_STEP_DONE')
    print(json.dumps({'next': 'clean polluted field manually/by click+CmdA+Delete, re-screenshot, re-classify state before resuming'}))
    return rc1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--evidence', default=None)
    ap.add_argument('--state', default=None)
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('frontmost').set_defaults(fn=cmd_frontmost)
    sub.add_parser('escape').set_defaults(fn=cmd_escape)
    p = sub.add_parser('paste-image'); p.add_argument('--png', required=True); p.set_defaults(fn=cmd_paste_image)
    p = sub.add_parser('paste-text'); p.add_argument('--file', required=True); p.set_defaults(fn=cmd_paste_text)
    p = sub.add_parser('js-click-file-input'); p.add_argument('--index', type=int, default=0); p.set_defaults(fn=cmd_js_click_file_input)
    p = sub.add_parser('js-insert-prompt'); p.add_argument('--file', required=True); p.add_argument('--clear', action='store_true'); p.set_defaults(fn=cmd_js_insert_prompt)
    p = sub.add_parser('picker-go'); p.add_argument('--path', required=True); p.set_defaults(fn=cmd_picker_go)
    sub.add_parser('check-generate').set_defaults(fn=cmd_check_generate)
    p = sub.add_parser('watch-generate'); p.add_argument('--interval', type=int, default=900); p.add_argument('--max-hours', type=float, default=6); p.add_argument('--event-queue', default=None); p.add_argument('--immediate', action='store_true', help='fire even if button is already blue at start'); p.set_defaults(fn=cmd_watch_generate)
    sub.add_parser('recover').set_defaults(fn=cmd_recover)
    args = ap.parse_args()
    return args.fn(args)


if __name__ == '__main__':
    raise SystemExit(main())
