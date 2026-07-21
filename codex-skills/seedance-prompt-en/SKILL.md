---
name: seedance-prompt-en
description: Single live contract for Seedance 2.0 prompt writing and Runway UI operation. MUST load whenever Seedance, Runway Seedance, multi-reference video prompts, or Seedance generation is requested.
---

# Seedance: one authoring and operating contract

## Authority and scope

This is the **only live Seedance execution contract**. It owns prompt writing, Chrome/Runway operation, reference attach, Generate, queue capacity, download evidence, and provider labeling.

- `videodirector` and `music-video-production-team` define story, scene purpose, and image requirements only.
- Global AGENTS defines universal safety only; it does not define Seedance UI steps.
- Hybrid operator policy: `~/.codex/video-team-policies/chrome_hybrid_operator_20260721.md`.
- Subagent spawn approval gate: `~/.codex/video-team-policies/subagent_approval_gate_20260721.md`. No extra agents/lanes/schedulers without per-spawn user approval. Only pre-approved loop: 15-minute Generate-queue observer while a queue is active.
- Still-image generation is Codex imagegen (Gongnyang). This skill covers Seedance video only.
- **I2V default = Seedance.** Grok only when the user explicitly names Grok for that job.

## Hard route (v2 — Chrome hybrid)

- Runway source of truth: visible logged-in **`app.runwayml.com` in Chrome** (one Generate board tab).
- Do **not** run a parallel Safari Runway session for the same project.
- **Tool split (phase lock):**
  - `ATTACH` → desktop **Computer Use drag only** (Finder → Chrome Multi-ref, one file).
  - `VERIFY` / `WEB` / queue card / download clicks → **Chrome Codex plugin** preferred.
  - Same moment: only one owner tool. Attach phase = no plugin clicks. Web phase = no CU mouse.
- Never use Runway connector/API, hidden input, picker/asset selector, path typing, AppleScript/local mouse/cliclick, Credits/Max, or Grok unless the user explicitly authorizes that exact exception.
- If desktop drag is unavailable: `BLOCKED_CODEX_COMPUTER_USE_UNAVAILABLE` once. Do not open Finder, modify the deck, click Generate, spawn a helper, or invent a method ladder.
- If Chrome plugin is unavailable: temporary fallback is full Computer Use on the **same Chrome** tab (not Safari), still one-file drag + eight-check Generate.

## Dual in-flight capacity (mandatory)

Seedance generation is ~30 minutes per card. **Empty second slot is a production loss.**

- Target **~2** cards in `In queue` / `Generating` / `Processing` whenever ≥2 eligible scenes exist.
- After scene A shows a **visible accepted card**, immediately run ATTACH→WEB for scene B if eligible.
- Do **not** wait for A’s full render before submitting B.
- Hands are sequential; **queue slots are not**.
- No second agent to watch the queue.

## One scene cursor + state

Maintain one current cursor and one record per active prearm:

```json
{
  "scene_id": "S01",
  "browser": "chrome",
  "phase": "attach|verify|web|inflight|download|blocked",
  "owner_tool": "cu_drag|chrome_plugin|none",
  "refs_visible": false,
  "prompt_verified": false,
  "settings_verified": false,
  "generate_color": "blue|gray",
  "accepted_card_visible": false,
  "inflight_count": 0,
  "status": "pending|prearming|ready|submitted_ui|downloaded|qc_pass|qc_fail|blocked"
}
```

A scene advances to `submitted_ui` only when **its own** visible accepted card appears. A click, blue button, prompt text, local file, or scheduler event is not acceptance.

## Visual prompt authoring

Write one visual-only prompt, normally 700–1800 characters and always within Runway's visible 3500-character limit.

Order:

1. visible premise and mood;
2. `@ImageN` visible roles;
3. one dominant camera move plus subject action;
4. 10–15 second motion arc and usable exit composition;
5. only essential identity/crop/prop locks;
6. short safety tail.

References are anchors, not cages. Describe their visible role, never provenance.

```text
@Image1 anchors the warm lakeside campfire composition.
@Image2 controls a close flame aperture transition.
@Image3 establishes moonlit forest depth after the reveal.
@Image4 anchors a distant, non-graphic danger viewpoint.
```

Do not include proper names, historical/political labels, captions, narration, contest names, invisible place labels, artist/style imitation, Gongnyang/imagegen/model names, source-frame/provenance/QC/folder language, or needless weapon/graphic wording. Facts and names belong in the caption/narration package.

For a fragile close-up, explicitly preserve crop; otherwise do not over-lock composition. The clip must contain physical action and environmental motion, not still-image zoom/pan filler.

## Reference upload: one-by-one (ATTACH + VERIFY)

1. Chrome Runway Generate board frontmost; cursor scene matches package.
2. Open one ordered staging folder in Finder (upper-right, not covering Multi-ref/prompt/Generate).
3. `owner_tool=cu_drag`: Computer Use drags **one** file into the empty Multi-ref slot on **Chrome**.
4. `owner_tool=chrome_plugin`: verify visible thumbnail count/order (this is PASS, not the drag log).
5. Repeat until all refs for the scene are visible in order.
6. If swap/missing/wrong app drop: stop; recover tray; do not Generate; do not switch to picker/path methods.
7. Never silently reuse a prior scene deck unless the package marks it persistent.

## Eight-check preflight (WEB, before Generate)

1. Chrome Runway is frontmost Generate board;
2. current cursor matches the scene package;
3. expected reference thumbnails/order are visible;
4. visual-only prompt is visible and ≤3500;
5. Video / Seedance 2.0 / Multi-reference are visible;
6. audio, ratio, resolution, duration, Unlimited match package;
7. no visible Please-wait/Credits blocker;
8. exact Generate button is visibly blue.

Blue means eligible **after** checks, never a command by itself.

## Generate, queue, dual fill

- `owner_tool=chrome_plugin`: click exact Generate **once** after all checks.
- Wait until a visible new current-scene card appears (`In queue` / `Generating` / `Processing` / `Completed`).
- If card exists: set `submitted_ui`, record evidence, `inflight_count++`.
- If `inflight_count < 2` and another scene is eligible: start that scene’s ATTACH→WEB immediately.
- If gray, wait/Credits, or no card: keep the **same** scene prearmed; do not re-click, replace refs/prompt, advance, or switch providers.
- 15-minute observer may only re-check the **current** prearmed gray→blue case with full eight checks. Delete observer when queue ends.
- While two jobs render: offline prep next prompts/refs, download completed cards — no idle 30-min babysitting of a single bar.

## Provider and completion evidence

Provider is selected in the scene package, never silently switched. Default provider is Seedance. Grok only with explicit user naming; label Grok files as Grok.

For every selected clip record provider, exact downloaded file, size, duration/codec, scene ID, and QC verdict. A UI card, prompt, or thumbnail is never final media completion. Missing download = `UI_ONLY_NOT_DOWNLOADED`.

## Output format

```text
Scene ID:
Browser: chrome
Visual prompt:
Reference roles:
Expected duration/audio:
Inflight count after submit:
Caption/narration notes (not for Runway):
Operator state:
Owner tool last used:
```

Older research and pre-consolidation notes are archived at `archive/` and are not live rules.
