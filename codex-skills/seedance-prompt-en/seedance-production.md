# Seedance production branch

This branch executes a complete, already-authored handoff package in visible Chrome Runway. It does not improvise or rewrite the visual prompt. If the package is incomplete, return to `seedance-prompting.md`.

## Approved route

- Source of truth: one visible, logged-in `app.runwayml.com` Generate board in Chrome.
- Attach through Runway's visible `Reference` asset selector: one staged file → native chooser → `Open` → verify the new visible `ImageN` thumbnail.
- Use one owner tool at a time: Computer Use for attachment; Chrome plugin/Computer Use for visible verification and web actions.
- Never use connector/API, hidden inputs, AppleScript coordinate clicking, clipboard image paste, Credits/Max, or a parallel Safari Runway session.
- When a step fails, follow the fixed ladder below. Do not invent a route that is not on it, and do not skip a rung.

## Attachment ladder — the only escalation path

| Rung | Method | Move on when |
|---|---|---|
| 1 | Visible `Reference` asset selector → native chooser → one staged file → `Open` | it fails |
| 2 | Retry rung 1 **once** (reopen the selector, re-read coordinates) | the retry fails |
| 3 | Finder-frontmost drag/drop — **requires explicit user approval in the current thread** | no approval, or it fails |
| 4 | Stop with `BLOCKED_REFERENCE_ATTACH_FAILED` and record the exact user action needed | — |

Drag is a last resort, not a default: it depends on coordinates, Retina scaling, window occlusion, and held-payload judgement, and that is where the repeat incidents came from. Never promote it automatically — rung 3 needs the user to say so in this conversation (or `DRAG_APPROVED_BY_USER_CURRENT_THREAD=true` in the project file).

If Computer Use itself is unavailable, stop with `BLOCKED_CODEX_COMPUTER_USE_UNAVAILABLE` and record the exact user action needed.

## Attach and verify

1. Bring the correct Chrome Runway Generate board frontmost and confirm the scene cursor matches the handoff.
2. Open the empty `Reference` slot.
3. In the native chooser, select exactly one staged file (rung 1 of the ladder).
4. Click `Open`, wait for the selector to close, and verify the newly visible `ImageN` thumbnail.
5. Repeat until every ordered reference is visible. Attach scene references first, approved character sheet(s) after.
6. For any character in an approved sheet, verify the sheet/identity crop thumbnail is present in the role position on **this** generation. Previous cards do not count.
7. If a file, slot, order, or character-sheet thumbnail is wrong, stop and recover the deck. Do not Generate.

`ImageN` order is an attachment record, not a narrative sequence — the prompt must not treat the numbering as a storyboard to interpolate or replay (`GENERAL_REFERENCE_MODE`).

## Eight-check Generate preflight

Before one Generate, verify:

1. Chrome Runway is frontmost;
2. current cursor equals the handoff scene;
3. all expected reference thumbnails and order are visible;
4. visual prompt is present and within 3500 characters;
5. Video / Seedance 2.0 / Multi-reference are visible;
6. **Audio is ON** (never disable it — it is one toggle for SFX and music together; unwanted score is fixed in the prompt, not with the switch), and ratio, resolution, duration, and Unlimited settings match the package;
7. no visible wait/Credits blocker;
8. the exact Generate button is blue.

The blue state means eligible after all eight checks; it is not permission to click repeatedly.

## Queue operation

- Click Generate exactly once for the current scene after preflight.
- Wait for a visible accepted card (`In queue`, `Generating`, `Processing`, or `Completed`) belonging to that scene.
- Record the accepted card and increment the in-flight count. Then advance the UI deck to the next prepared package; never re-click the accepted scene.
- Target two in-flight cards whenever two eligible packages exist. While cards render, pre-arm the next package and process completed cards; do not idle.
- If the button is gray or shows a wait/Credits state, keep the current package staged and use the approved 15-minute observer. Do not click.
- If one click produces no accepted card, hold the scene for review and do not automatically retry.
- The observer is allowed only while a queue is active and must be removed when the queue ends.

## Completion evidence

For every completed card:

1. download the actual video;
2. verify exact path and file size;
3. run `ffprobe` and record container, codec, duration, resolution, and frame evidence where relevant;
4. place/copy the verified file into the lane's canonical video library;
5. update the manifest, `status.json`, and `result.md` with scene ID, provider, path, and QC verdict.

A UI card, thumbnail, prompt, or source image is never final media completion. Missing download is `UI_ONLY_NOT_DOWNLOADED`.

## Block and recovery codes

- `BLOCKED_CODEX_COMPUTER_USE_UNAVAILABLE`: visible Chrome/Computer Use route unavailable; record the exact user action needed.
- `BLOCKED_CHARACTER_SHEET_ATTACHMENT_NOT_VERIFIED`: required character sheet/crop absent, mismatched, or not visibly verified; no Generate.
- `UPLOAD_100_PERCENT_STALLED`: cancel only the stalled upload, preserve the rest of the deck, and record it.
- `UI_ONLY_NOT_DOWNLOADED`: card exists but media file is not verified.
- `DUPLICATE_GENERATE_PREVENTED`: accepted card already exists; do not click again.
