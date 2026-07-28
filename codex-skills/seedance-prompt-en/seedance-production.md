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
8. **Deck-overlap check:** compare the visible strip against the previous block's deck. More than one shared scene reference means two near-identical clips are about to be produced — rebuild the deck before Generate.
9. **Duplicate check:** no two thumbnails in the strip may be the same image. Identical thumbnails mean a file was attached repeatedly to fill a count — remove the duplicates and submit the honest deck.
10. **Role-map truth check:** each visible thumbnail must actually be what the role map claims. A character sheet sitting in a "current-scene composition" slot, or three roles pointing at one picture, means the map is fiction — stop and rebuild.

`ImageN` order is an attachment record, not a narrative sequence — the prompt must not treat the numbering as a storyboard to interpolate or replay (`GENERAL_REFERENCE_MODE`).

## Eight-check Generate preflight

Before one Generate, verify:

1. Chrome Runway is frontmost;
2. current cursor equals the handoff scene;
3. all expected reference thumbnails and order are visible;
4. the prompt box holds the **visual prompt only** — no `Scene ID`/`Mode`/`REFERENCE ROLES`/gate/`EXPECTED` field labels — and is within 3500 characters;
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
- The two in-flight slots must hold **two different scenes**. Filling both with the same scene, or with two decks that overlap by more than one reference, just buys two versions of one shot. Two slots is throughput, not redundancy — if only one scene is genuinely ready, run one slot and prepare the next.
- If the button is gray or shows a wait/Credits state, keep the current package staged and use the approved 15-minute observer. Do not click.
- If one click produces no accepted card, run the `ACTIVE_CLICK_NO_CARD` protocol below. Do not declare a blocker on a short look.
- The observer is allowed only while a queue is active. When the queue empties, **first fill it**: if a prepared block remains, pre-arm and submit it before anything else. Retire the observer only once the queue is empty and the shelf is exhausted, and say so explicitly.
- An observer watching a composer with 0 references is a staging failure. Generate cannot turn blue on an empty board, so pre-arm before observing.

## ACTIVE_CLICK_NO_CARD — clicked an eligible button, no card appeared

A card can lag well behind the button. Ported from the runtime contract 2026-07-28 because this file only said "hold the scene", with no observation window, so a 15-second look was being reported as `BLOCKED_GENERATE_ACCEPTANCE_NOT_VERIFIED` while the submission may have gone through.

1. **Keep watching.** Poll for the card every 5s for up to **60s**. The button briefly disabling and returning is not a verdict. Still nothing at 60s → classify `ACTIVE_CLICK_NO_CARD`.
2. **Check for a hidden success before re-clicking.** Refresh the same tab (Cmd+R, keep the verified session URL) and look in the session feed for a new job matching this block by time and reference count. If it is there, the submit succeeded — record the card evidence and never re-click.
3. **Re-preflight.** A refresh can reset the composer; re-verify the whole eight-check from the top and rebuild through the canonical route if anything was lost.
4. **One conditional second click**, only when all three hold: (a) refresh+feed confirmed no duplicate job, (b) every preflight item green, (c) 2 minutes since the first click. One second attempt per block per session — that is the cap.
5. **Still no card** → `BLOCKED_SUBMIT_NOT_REGISTERING`, defer that block, keep filling the queue and preparing the shelf, report to the user. No API/MCP detour, no Credits Mode, no extra clicks.
6. **Evidence** (`ui_evidence.jsonl`): `state`, `ts_click`, `button_pre` (visible colour), `card_poll` (interval/total/result), `refresh_done`, `feed_duplicate_check`, `preflight_after_refresh`, `second_click`, `final_classification`.

A deferred block never blocks the others: keep the remaining shelf moving.

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

---

# Board and queue specifics

Moved here 2026-07-28 from the prompting field-lessons file, where UI and queue procedure did not belong.

## Runway board specifics

- One logged-in Chrome `app.runwayml.com` Generate board per project.
- Attach one reference at a time through the native chooser, then confirm the visible `ImageN` thumbnail.
- **Reset is not the X.** It is the circular arrow at the image's top right — `button[aria-label="Reset settings"]`, icon `lucide-rotate-ccw`.
- Generate eligibility is decided by the **visible button colour**: blue = clickable, gray = wait. Never judge by button position, and do not let AX `disabled` / `aria-disabled` / DOM guesses override the colour — that override rule exists because DOM heuristics produced false negatives on a genuinely clickable button.
- Known trap: a `primaryBlue` button carrying `data-soft-disabled="true"` looks blue but does nothing. Colour still decides *eligibility*; if a single click on a blue button yields no accepted card, do not re-click — follow the `ACTIVE_CLICK_NO_CARD` protocol.
- Click Generate once per scene. A click is not a submission — only a visible `In queue` / `Generating` / `Processing` / `Completed` card for that scene counts as accepted.
- Every block: 15s, Creative, Multi-reference, 16:9, **Audio ON**.

## Two-slot queue

- Keep two jobs in flight. When the first card is accepted, immediately attach → verify → preflight the second.
- Once both are running, stop clicking Generate; prepare the next deck's references, prompt, and settings instead.
- Gray button means wait and keep preparing. When it returns to blue, redo the eight-check preflight before clicking.
- Never advance the cursor or re-click just because the button looks blue while no accepted card appeared.
- No extra agent, scheduler, or second browser loop. A single 15-minute status check, only while the queue is genuinely active.

## Queue stall stop rule

If the same submitted card reads `In queue` on **three consecutive** 15-minute checks, record `BLOCKED_RUNWAY_QUEUE_STALLED` and stop that monitor. Judge only on the third; checks one and two get a short status note. Any change — `Generating`, `Processing`, `Completed`, failure, error, card disappearance — resets the counter to zero.

This blocks that external queue, not the project. Resume when the card moves to `Generating`/`Completed` in the same session, or when the user clears the stall and says to resume.

## Completion evidence

- Completion is the **downloaded file**, never a card or thumbnail.
- Record `scene_id`, provider, absolute path, bytes, duration, codec, and QC verdict per file.
- A generated-but-undownloaded result is `UI_ONLY_NOT_DOWNLOADED` and is never reported as complete. Recover it from the session board before judging it missing.
- If a card vanishes, fails, shows a different deck, or a blocker appears: record `BLOCKED` and stop.
