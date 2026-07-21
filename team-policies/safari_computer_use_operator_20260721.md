# Safari Computer Use operator — 2026-07-21

**Naming:** This is **Safari-only**, not Safari+Chrome.  
All Runway UI is Safari. Desktop Computer Use drives both drag and clicks.  
Branch: `operator/safari-computer-use`.  
Chrome mainline (different branch): `main` + `chrome_hybrid_operator` = Chrome-only with plugin for clicks.

## Goal

- Keep **~2 Seedance jobs in flight** (~30 min each; idle slots are a production loss).
- Single-agent sequential hands; no subagent fan-out without per-spawn approval.
- **Safari only** for Runway — one browser surface.

## Browser

- **Runway lives in Safari only**: one logged-in `app.runwayml.com` Generate board tab/window.
- Do not open Chrome Runway for the same project on this path.
- Finder is staging only (upper-right, not covering Multi-ref / prompt / Generate).

## Tool split (phase lock)

| Phase | Owner tool | Actions |
|---|---|---|
| `ATTACH` | Desktop **Computer Use** (drag only) | Finder → Safari Multi-ref **one file drag** |
| `VERIFY_REFS` | **Safari + Computer Use** (or Codex browser on Safari) | Count/order of visible Multi-ref thumbnails |
| `WEB` | **Safari + Computer Use** | Prompt paste, settings, Generate once, queue/card read, download clicks |
| `WAIT` | Poll / observer (no VLM spam) | 15-min observer may re-check **current** gray→blue prearm only |
| `DOWNLOAD/QC` | Safari CU or local tools | Path, size, duration/codec evidence |

### Phase lock rules

1. Only one owner tool/action stream is active at a time.
2. During `ATTACH`, do not Generate or change prompt.
3. During `WEB`, do not drag new refs unless recovering a failed tray.
4. Attach **PASS** = Safari-visible thumbnail count/order, not “drag returned OK”.
5. Generate is **one click** after eight checks — never dual-click recovery.
6. All steps stay in Safari Computer Use (no Chrome plugin on this branch).

## Dual in-flight (mandatory capacity)

```
A: ATTACH → VERIFY → WEB Generate once → card visible → inflight++
if inflight < 2 and next scene eligible:
  B: same pipeline immediately
while inflight == 2:
  WAIT / offline prep next prompts / download completed cards
when a slot frees:
  submit next eligible scene
```

- Do **not** wait for A’s full ~30 min render before starting B.
- Hands are sequential; **queue slots are not**.

## Fallback

If desktop drag is unavailable:

1. `BLOCKED_CODEX_COMPUTER_USE_UNAVAILABLE` once with exact missing capability.
2. Do not open Finder, do not Generate, do not spawn a helper, do not invent a method ladder (picker → path → AppleScript → coordinates).

If Safari focus is lost mid-transaction:

1. Restore Safari Runway Generate board frontmost.
2. Re-run verify for current phase; do not start a second browser.

## Relation to other files

- Prompt + eight-check + evidence: `codex-skills/seedance-prompt-en/SKILL.md` (Safari variant on this branch).
- Subagent ban: `team-policies/subagent_approval_gate_20260721.md`.
- Chrome mainline policy (other branch): `team-policies/chrome_hybrid_operator_20260721.md` on `main`.
