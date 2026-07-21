# Chrome hybrid operator — 2026-07-21 (v2)

> **Naming:** “Hybrid” here means **tools** (CU drag + Chrome plugin clicks) on **Chrome only** — not Chrome+Safari.  
> Safari-only path: branch `operator/safari-computer-use` → `safari_computer_use_operator_20260721.md`.  
> This Chrome policy is live on `main`.

Live operating model for Runway/Seedance (Chrome mainline).

## Goal

- Keep **~2 Seedance jobs in flight** (generation is ~30 min each; idle slots are a production loss).
- Stop multi-file rule thrash and multi-agent fan-out (see cleanup session + subagent gate).
- Prefer **Chrome** for all Runway work so session/tab/DOM stay one surface.

## Browser

- **Runway lives in Chrome only** for this workflow: one logged-in `app.runwayml.com` Generate board tab.
- Do not open a parallel Safari Runway session for the same project.
- Finder is staging only (upper-right, not covering Multi-ref / prompt / Generate).

## Tool split (phase lock)

| Phase | Owner tool | Actions |
|---|---|---|
| `ATTACH` | Desktop **Computer Use** (drag only) | Finder → Chrome Multi-ref **one file drag** |
| `VERIFY_REFS` | **Chrome Codex plugin** | Count/order of visible Multi-ref thumbnails |
| `WEB` | **Chrome Codex plugin** | Prompt paste, settings, Generate once, queue/card read, download clicks |
| `WAIT` | Poll / observer (no VLM spam) | 15-min observer may re-check **current** gray→blue prearm only |
| `DOWNLOAD/QC` | Chrome plugin or local tools | Path, size, duration/codec evidence |

### Phase lock rules

1. Only one owner tool is active at a time.
2. During `ATTACH`, Chrome plugin must not click Runway.
3. During `WEB`, Computer Use must not move the mouse except explicit user recovery.
4. Attach **PASS** = Chrome-visible thumbnail count/order, not “drag returned OK”.
5. Generate is **Chrome plugin only** (never dual-click with Computer Use).

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
- No second agent to “watch the queue”. Same main agent or the single pre-approved 15-min observer only.

## Fallback

If Chrome Codex plugin is unavailable:

1. Prefer fixing the plugin/native host (preferred path).
2. Temporary fallback: full **Computer Use** on the **same Chrome** Runway tab (not Safari), still one-file drag + eight-check Generate.
3. Never invent a method ladder (picker → path type → AppleScript → coordinates).

If desktop drag is unavailable:

1. `BLOCKED_CODEX_COMPUTER_USE_UNAVAILABLE` once with exact missing capability.
2. Do not open Finder, do not Generate, do not spawn a helper.

## Relation to other files

- Prompt + eight-check + evidence: `codex-skills/seedance-prompt-en/SKILL.md` (implements this model).
- Subagent ban: `team-policies/subagent_approval_gate_20260721.md`.
- Cleanup history: `docs/2026-07-21-video-team-cleanup-session.md`.
