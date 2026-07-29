# Seedance production branch

This branch executes a complete, already-authored handoff package in visible Chrome Runway. It does not improvise or rewrite the visual prompt. If the package is incomplete, return to `seedance-prompting.md`.

## Keep producing until nothing is left to produce

This branch's job is **throughput**. A wake-up means: make as many valid submissions as the board allows, then stop — not "attempt one thing and report."

- **A blocker blocks that item, never the session.** Mark the item, move to the next eligible package, keep going. The session stops when *every* remaining item is blocked or the shelf is empty — not at the first one.
- **`exactly once` is per scene, not per session.** One click per scene prevents double-submitting that scene. After a scene's card is confirmed, immediately advance to the next scene while a slot is free.
- **A free slot is unfinished work.** If a card was accepted and the board still has capacity, the next package goes in during the same wake. Stopping with an open slot is a failure, not caution.
- **Exhaust the shelf before scheduling.** Schedule the next check only when nothing further can be submitted right now. Scheduling while work remains just adds 15 minutes of nothing.
- When you do stop, say which of the two it is: *shelf exhausted* or *every remaining item blocked, here is each reason*.

The block codes in this file exist to stop **bad submissions**, not to stop the run. Recording a blocker and continuing is the normal path; recording a blocker and halting is only correct when there is genuinely nothing else to submit.

The fixed ladders elsewhere restrict **which methods** you may use. They do not restrict **how long you keep working** — do not read "don't invent a new route" as "give up early".

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
10. **Role-map truth check:** each visible thumbnail must actually be what the role map claims. Three roles pointing at one picture, or a multi-panel sheet where a single-scene composition should be, means the map is fiction — stop and rebuild. The identity slot holds the `CHAR_<ID>_PROVIDER_REF_R<n>` file; a grid of panels in that slot is the wrong file.

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

- Click Generate exactly once **for that scene** after preflight — this prevents duplicate submissions of the same scene, and is not a limit on how many scenes you submit this session.
- Wait for a visible accepted card (`In queue`, `Generating`, `Processing`, or `Completed`) belonging to that scene.
- Record the accepted card and increment the in-flight count. Then advance the UI deck to the next prepared package; never re-click the accepted scene.
- Target two in-flight cards whenever two eligible packages exist. While cards render, pre-arm the next package and process completed cards; do not idle.
- The two in-flight slots must hold **two different scenes**. Filling both with the same scene, or with two decks that overlap by more than one reference, just buys two versions of one shot. Two slots is throughput, not redundancy — if only one scene is genuinely ready, run one slot and prepare the next.
- If the button is gray or shows a wait/Credits state, keep the current package staged and use the approved 15-minute observer. Do not click.
- If one click produces no accepted card, run the `ACTIVE_CLICK_NO_CARD` protocol below. Do not declare a blocker on a short look.
- The observer is allowed only while a queue is active. When the queue empties, **first fill it**: if a prepared block remains, pre-arm and submit it before anything else. Retire the observer only once the queue is empty and the shelf is exhausted, and say so explicitly.
- An observer watching a composer with 0 references is a staging failure. Generate cannot turn blue on an empty board, so pre-arm before observing.

## The recurring observer instruction — keep it scene-agnostic

A 15-minute observer is a **recurring** job. Anything scene-specific written into its instruction becomes permanent: the task re-reads that same text every wake, forever.

Observed failure: an observer was scheduled with `E24` in the text, the exact Korean line it had to see, E24's five-reference list, and the phrase *"keep waiting for user repair."* E24's prompt was missing its Korean sentence, so every wake found the same defect and waited again — eight cycles, no progress, no episode after E24 attempted. The instruction had made one broken scene into a permanent stop.

**Never put these in a recurring observer instruction:** a scene ID, prompt text to match, a reference list, per-scene settings, or any "wait for repair" wording. Those live in the staged package and the project state, which the observer reads at wake time. The instruction says *what to do*, the state says *what is current*.

The observer's whole job is: **is a submission possible right now, and if so, submit the next eligible one.**

```
Every interval:
  1. Read the visible board: queue depth, in-flight cards, Generate colour.
  2. Slot free?  no  -> record state, wait for next interval.
  3. Take the NEXT ELIGIBLE package from the shelf.
     eligible = staged, self-verified, not already marked blocked.
  4. Preflight -> Generate once -> confirm a matching card.
  5. Package fails its own verification?
     -> mark THAT package blocked with the reason and the repair needed
     -> SKIP it and take the next eligible package in the same wake
  6. No eligible package left? -> report shelf state and retire.
```

- **A blocked package is skipped, never waited on.** One bad scene must never hold the queue. Its repair is separate work, tracked in project state.
- **A blocker that needs a human is not a polling target.** Polling cannot type a missing line. Record it once with the exact repair action, escalate to the user, and stop re-checking that condition — re-polling an unchanged human-action blocker is a stall, not monitoring.
- The observer never authors prompts or attaches references. If the shelf is empty, that is a report ("shelf exhausted"), not something to wait out.

### Template

```
Seedance queue observer for <project>. Every 15 minutes, check the visible Chrome
Runway board and the project's staged shelf.

If Generate is gray or the queue is full, record the board state and wait.
If a slot is free, take the next eligible staged package — eligible means staged,
self-verified, and not already marked blocked — run the preflight, click Generate
once, and confirm a matching scene card.

If a package fails its own preflight, mark that package blocked with the reason
and the repair required, skip it, and try the next eligible package in the same
wake. Never wait on one scene.

If a blocker requires user action, record it once with the exact action needed,
report it, and stop monitoring that condition.

If no eligible package remains, report the shelf as exhausted and retire.
Do not open a second browser loop or create another observer. Never claim media
completion without a verified downloaded file.
```

No scene ID appears anywhere in it. That is the point.

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

## Repair vs blocked — check who can fix it

Most stops in this file were never stops. A defect in something **you produced and control** is a repair task with a budget; only a defect you **cannot fix from here** is a blocker.

Ask one question: *can I fix this myself, right now, with a documented method?*

| | Meaning | Action |
|---|---|---|
| **REPAIR** | the input is mine and the fix is known | fix it now, up to 2 attempts, then generate |
| **DEFER** | repair attempts used up | mark the item, take the next package, report at session end |
| **BLOCKED** | needs a person or an external system | record once with the exact action, escalate, skip the item, keep working |

Never poll a BLOCKED condition — polling cannot log in, cannot pay, cannot type. Never *wait* on a REPAIR — waiting cannot fix what your own hands broke.

### Repairs, not blockers

| Symptom | Repair |
|---|---|
| prompt text missing, truncated, or garbled — Korean especially | re-insert via the prompt route below, verify by the **visible character counter**, then generate |
| a required character sheet is not attached | attach it and verify the thumbnail |
| no `PROVIDER_REF` sheet exists | generate one from the approved master |
| a source frame fails as an I2V source (poster-like, wrong emotion) | regenerate that frame |
| the deck duplicates an image or overlaps the previous block | rebuild the deck from this shot's own material |

### Korean and other non-ASCII prompt text

Synthetic keystrokes drop CJK characters. That is a known input failure, not a reason to stop.

1. Load the prompt into the clipboard and paste it (`Chrome activate` → click the field → confirm caret → `Cmd+V`), then check the **visible counter** — never the AX tree, which misreports on this editor.
2. If the text is still wrong, focus the editor and use `document.execCommand('insertText', …)`, selecting all first to clear stale text.
3. Two failed attempts → DEFER this package with the exact text that would not go in, move to the next package, and report it at the end.

Generating with a prompt you know is incomplete is worse than deferring — it burns a slot and produces a clip that must be thrown away. But *waiting* on it while other packages are ready is worse still.

## Block and recovery codes

- `BLOCKED_CODEX_COMPUTER_USE_UNAVAILABLE`: visible Chrome/Computer Use route unavailable; record the exact user action needed.
- `REPAIR_CHARACTER_SHEET_NOT_ATTACHED`: attach the sheet and verify the thumbnail, then continue. Only after two failed attach attempts does it become `DEFER_CHARACTER_SHEET_UNRESOLVED` — mark the package and take the next one.
- `REPAIR_PROMPT_TEXT_INCOMPLETE`: prompt missing/truncated/garbled (typically CJK). Re-insert by clipboard, verify the visible counter. Two failures → `DEFER_PROMPT_TEXT_UNRESOLVED`, next package.
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
- Click Generate once per scene, then move on to the next scene while a slot is free. A click is not a submission — only a visible `In queue` / `Generating` / `Processing` / `Completed` card for that scene counts as accepted.
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
