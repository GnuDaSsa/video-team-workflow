---
name: seedance-prompt-en
description: Single live contract for Seedance 2.0 prompt writing and Runway UI operation. MUST load whenever Seedance, Runway Seedance, multi-reference video prompts, or Seedance generation is requested.
---

# Seedance: one authoring and operating contract

## Authority and scope

This is the **only live Seedance execution contract**. It owns prompt writing, Runway preflight, Finder reference upload, Generate, queue state, download evidence, and provider labeling.

- `videodirector` and `music-video-production-team` define story, scene purpose, and image requirements only.
- Global AGENTS defines universal safety only; it does not define Seedance UI steps.
- Historical Seedance patches are reference material only, never active instructions.
- Subagent spawn approval gate (2026-07-21): no delegated lanes, subagents, sidecars, or extra automation loops without explicit per-spawn user approval. The single 15-minute observer scheduler defined below is the only pre-approved background loop, and only while a queue is active. Full policy: `team-policies/subagent_approval_gate_20260721.md`.
- Still-image generation is Codex imagegen with Gongnyang. This skill covers Seedance video generation only.

## Hard route

- Runway source of truth: the visible logged-in `app.runwayml.com` UI.
- UI execution: **Codex Computer Use only**.
- Never use Runway connector/API, hidden input, picker/asset selector, path typing, AppleScript/local mouse/cliclick, Credits/Max, or Grok unless the user explicitly authorizes that exact exception.
- If the required Computer Use action is unavailable, set `BLOCKED_CODEX_COMPUTER_USE_UNAVAILABLE`. Do not open Finder, modify the deck, replace a prompt, click Generate, or create a scheduler.

## One scene, one state

Maintain one current cursor and one record:

```json
{
  "scene_id": "S01",
  "refs_visible": false,
  "prompt_verified": false,
  "settings_verified": false,
  "generate_color": "blue|gray",
  "accepted_card_visible": false,
  "status": "pending|prearming|ready|submitted_ui|downloaded|qc_pass|qc_fail|blocked"
}
```

A scene advances only when its own visible accepted card appears. A click, blue button, prompt text, local file, or scheduler event is not acceptance.

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

## Reference upload: visible one-by-one transaction

1. Confirm the visible Runway page is frontmost and the active scene is current cursor.
2. Open one ordered staging folder in Finder and keep it upper-right without covering Runway.
3. Use Codex Computer Use to drag one file to the **empty** Reference slot.
4. Wait for the thumbnail and verify its order/count before the next file.
5. If a file is swapped, missing, or dropped into another app, stop; clear/recover the tray before continuing. Do not Generate.
6. Never silently reuse a prior scene deck unless the scene package explicitly says it is persistent.

## Eight-check preflight

Immediately before Generate, verify only:

1. visible Runway is frontmost;
2. current cursor matches the scene package;
3. expected reference thumbnails/order are visible;
4. visual-only prompt is visible and ≤3500;
5. Video / Seedance 2.0 / Multi-reference are visible;
6. audio, ratio, resolution, duration, Unlimited match package;
7. no visible Please-wait/Credits blocker;
8. exact Generate button is visibly blue.

Blue means eligible **after** checks, never a command by itself.

## Generate, queue, scheduler

- Click exact Generate once after all checks.
- Wait and verify a visible new current-scene card (`In queue`, `Generating`, `Processing`, or `Completed`).
- If card exists: set `submitted_ui`, preserve evidence, advance cursor only for the next transaction.
- If gray, wait/Credits, or no card: keep the same scene prearmed; do not re-click, replace refs/prompt, or advance.
- A scheduler may only observe the current cursor every 15 minutes. It may never hard-code a scene, change refs/prompt, or click without all eight checks. Delete it after the queue ends.

## Provider and completion evidence

Provider is selected in the scene package, never silently switched. If a Grok file enters the edit, label it Grok; if a Seedance card has no downloaded file, label it `UI_ONLY_NOT_DOWNLOADED`.

For every selected clip record provider, exact downloaded file, size, duration/codec, scene ID, and QC verdict. A UI card, prompt, or thumbnail is never final media completion.

## Output format

```text
Scene ID:
Visual prompt:
Reference roles:
Expected duration/audio:
Caption/narration notes (not for Runway):
Operator state:
```

Older research and pre-consolidation notes are archived at `archive/` and are not live rules.
