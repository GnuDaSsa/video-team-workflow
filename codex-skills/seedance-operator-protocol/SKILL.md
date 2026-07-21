---
name: seedance-operator-protocol
description: Single operational protocol for Runway Seedance UI work. Load only when actually operating Runway/Seedance, not when authoring a prompt or planning a video.
---

# Seedance Operator Protocol (single source of truth)

## Scope and precedence

This file is the sole authority for **Runway/Seedance UI operation**: window targeting, reference upload, prompt insertion, Generate, queue monitoring, downloads, and operator state.

It supersedes older operational passages in global instructions, `seedance-prompt-en`, `videodirector`, and `music-video-production-team`. Those files may define story, visual direction, or prompt content, but must not redefine UI steps.

Do not use this protocol for still-image creation. Still images use Codex imagegen and Gongnyang compilation.

## Non-negotiable boundaries

- Source of truth: visible `app.runwayml.com` UI only.
- Use **Codex Computer Use only** for Runway/Finder UI actions. Do not use connector/API, hidden file input, picker/asset selector, path typing, local mouse scripts, AppleScript drag, or cliclick.
- No Grok, Credits, or Max switch without explicit user approval for that action.
- A visible reference thumbnail is upload proof. A visible current-scene queue/generating/processing/completed card is submission proof. Local paths, DOM guesses, prompts, and button color alone are not proof.
- Never claim a downloaded/final clip without the file path plus verification.

## Tool availability gate — before any UI work

1. Confirm the Codex Computer Use tool can perform the required action (especially drag/drop).
2. If it is unavailable, set `BLOCKED_CODEX_COMPUTER_USE_UNAVAILABLE`; do not open Finder, do not rearrange references, do not inject the next prompt, and do not click Generate.
3. Record the exact unavailable action and required resume condition once. Do not create a scheduler for a missing tool.

## Scene transaction: exactly one current scene

Each scene moves through only these states:

`pending → prearming → refs_visible → prompt_verified → ready → submitted_ui → downloaded → qc_pass | qc_fail | blocked`

A scene cannot advance because of a click attempt, a blue button, or a scheduler tick. It advances only after its own visible accepted Runway card.

Maintain one current-cursor record with:

```json
{
  "scene_id": "...",
  "refs_visible": false,
  "prompt_verified": false,
  "settings_verified": false,
  "generate_color": "blue|gray",
  "accepted_card_visible": false,
  "status": "pending|..."
}
```

Do not maintain competing click-nonces, hard-coded scene monitors, or separate cursors for the same active queue.

## Minimal preflight: eight checks

Before Generate, confirm only:

1. Runway is the frontmost visible target.
2. Current cursor scene ID matches the scene package.
3. Correct visible reference thumbnails are present in order.
4. Current visual-only prompt is visible and at most 3500 characters.
5. Video + Seedance 2.0 + Multi-reference are visible.
6. Audio / ratio / resolution / duration / Unlimited match the scene package.
7. No visible `Please wait` or Credits blocker.
8. Exact Generate button is visibly blue.

Do not add stale DOM, hash, provenance, pixel-comparison, or unrelated historical checks to the live preflight. Store provenance locally before prearm, not as a UI blocker.

## Reference upload procedure

1. Open exactly one ordered staging folder in Finder and place it upper-right, leaving Runway references, prompt, and Generate visible.
2. Drag **one file at a time** from Finder into the currently empty Reference slot using Codex Computer Use.
3. Wait for the new thumbnail and verify count/order before the next file.
4. If a thumbnail is replaced, swapped, missing, or the drop targets another app: stop, clear/recover the tray, and restore the expected order. Do not Generate.
5. Never reuse a previous scene's deck for a new scene unless the current scene package explicitly declares it persistent.

## Prompt boundary

The final Seedance prompt is visual-only. It may state visible subjects, setting, motion, camera, timing, sound, and safety constraints.

It must not contain:

- proper names or historical/political labels unless visually essential and policy-safe;
- captions, narration, factual provenance, local folder names, model names, Gongnyang/imagegen, prompt-pack/QC language;
- artist/style imitation references;
- unnecessary weapon close-ups or policy-risk wording.

Names, facts, dates, and explanatory copy belong in the caption/narration package, not in the video prompt.

## Generate and queue loop

- Blue means **eligible after preflight**, never an instruction by itself.
- Click Generate exactly once after all eight checks pass.
- Wait briefly and seek a visible new current-scene accepted card.
- If accepted: mark `submitted_ui`, save evidence, advance cursor on the next transaction.
- If button turns gray, a wait/Credits blocker appears, or no card appears: keep the same current scene prearmed. Do not alter refs/prompt or duplicate-click.
- A scheduler may only observe the **current cursor** every 15 minutes. It must never hard-code a scene, alter refs/prompt, or click without the eight checks. Delete it when no current pending scene remains.

## Queue time

While a card is queued, use time only for independent offline work: next-scene image QC, prompt drafting, download/QC of completed clips, or package preparation. Do not create duplicate jobs or switch providers silently.

## Completion evidence

For every selected clip, record provider, exact downloaded path, size, duration/codec, source scene, and QC verdict. `UI_ONLY_NOT_DOWNLOADED` is not final media completion.
