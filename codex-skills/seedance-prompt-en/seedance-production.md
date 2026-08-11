# Seedance production branch

## Continuing is the default. Stopping requires a named reason.

Read this before anything else in this file, and apply it to every rule here — including ones written later, and ones that forgot to say it.

**Silence means continue.** If a rule tells you not to do something, that is a restriction on *that action*, never permission to end the run. A rule that describes a failure without saying what happens next means: record it and keep going.

**A turn ends only by emitting one of these three states.** There is no fourth, and there is no ending by simply not continuing:

| Terminal state | Means | Must include |
|---|---|---|
| `QUEUE_FULL_WAITING` | slots are full, next package is armed | the scheduled next check |
| `SHELF_EXHAUSTED` | nothing left to arm | what was completed |
| `ALL_REMAINING_BLOCKED` | every remaining item is blocked | each item and its reason |

If you are about to stop and none of the three fits, **you are not finished** — go back to the cycle. Reaching the end of a rule, hitting a block code, finishing one generation, or running out of instructions are none of them.

Block codes exist to stop **a bad action**, not the run. `BLOCKED_*` on one item means that item leaves the loop; the loop continues with the next eligible package.

This inverts the usual failure. Rules accumulate prohibitions faster than permissions — every incident adds a "do not", and nothing adds a "keep going". Left alone, a rule set drifts toward halting by omission. This clause is the standing correction: an omission means continue, and any future rule that forgets to say so is covered by it.



This branch executes a complete, already-authored handoff package in visible Chrome Runway. It does not improvise or rewrite the visual prompt. If the package is incomplete, return to `seedance-prompting.md`.

## The production cycle

One loop, run until it genuinely cannot continue. **Arm first, then read the button** — an empty composer is always gray, so checking before arming reads "cannot generate" when the truth is "nothing loaded yet".

```
   ┌─────────────────────────────────────────────┐
   │  1. ARM      attach refs → paste prompt →    │
   │              settings (mode/duration/ratio/  │
   │              Audio ON)                       │
   │  2. READ     now look at Generate            │
   │        gray  → queue is full: this is the    │
   │                wait point. Stay armed,       │
   │                schedule the next check       │
   │        blue  → continue                      │
   │  3. PREFLIGHT  eight checks + deck overlap   │
   │                + duplicates + role-map truth │
   │  4. GENERATE   once, for this scene          │
   │  5. CONFIRM    matching card appears         │
   │                (no card → ACTIVE_CLICK_NO_CARD)│
   │  6. NEXT       take the next eligible        │
   │                package ─────────────────────┼──┐
   └─────────────────────────────────────────────┘  │
              ▲                                      │
              └──────────────────────────────────────┘
```

Exit only on one of these, and say which:

- **queue full** — armed and waiting; schedule the next check and stop for now
- **shelf exhausted** — nothing left to arm; report it
- **everything left is blocked** — list each item and its reason

### Scheduling the next check is mandatory, not optional

When the loop reaches **gray with a package armed**, scheduling the next check is a **required step of the cycle**, not a discretionary spawn. Do it without being asked. A run that stops at a full queue without a scheduled check has not paused — it has quietly ended, and the freed slot goes unused until a human notices.

Every mention of schedulers elsewhere is a prohibition (no second loop, no sidecar, no cron, no extra agent surface). That framing is about *proliferation*. It was never meant to discourage the one check this cycle depends on, and reading it that way is what leaves queues idle.

- **The queue-continuation check is not a new agent surface.** It is the same single operator resuming its own loop, and it is pre-approved by the spawn gate. It does not need per-run permission.
- **Arm first.** Never schedule against an unarmed board — gray then means "nothing loaded", and the check will be meaningless every time it fires.
- **One check only**, at the standing interval, while the queue is genuinely active. Not a second browser loop, not a parallel watcher, not a cron.
- **Scene-agnostic instruction.** No scene ID, no prompt text to verify, no reference list — those live in the staged package and project state, read at wake.
- **Retire it** when the shelf is exhausted or every remaining item is blocked, and say which.

If you are stopping and have not either scheduled a check or reported the shelf exhausted, the cycle is incomplete.

### Rules of the loop

- **Arm before reading the button, always.** Step 2 has no meaning before step 1. Watching an unarmed board is how a queue sits idle while packages wait.
- **A confirmed card is not the end of the turn.** It is the trigger for step 6. Advance immediately while a slot is free.
- **Gray is the only wait.** Every other stop is either exhaustion or a listed blocker. Gray with a package armed means the queue is genuinely full — that is the moment to schedule, not before.
- **A blocked package leaves the loop, the loop does not stop.** Mark it, take the next eligible package, keep cycling.
- **Never schedule with an unarmed shelf.** Arm the next package first, then let the schedule watch a meaningful gray.

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

### Do not compose the instruction — generate it

```
python3 runtime/scripts/runway_ui_helper.py observer-instruction --project <p>
```

Schedule that output verbatim. Hand-written observer text has failed twice for the same
reason: each rewrite re-introduces stop-early semantics the skill had already fixed.

- One instruction pinned `E24` and the exact Korean line it had to see, so eight
  consecutive wakes re-found the same defect and no later episode was ever attempted.
- Another defined its own failure semantics — *"조건이 하나라도 없으면 Generate하지 말고
  BLOCKED를 알린다"* — and the run stopped **8 seconds** after a Generate click instead of
  polling 60s, skipped the refresh-and-feed check entirely, paused the scheduler, and
  reported a code (`BLOCKED_ACTIVE_CLICK_NO_CARD`) that does not exist here.

A recurring instruction re-reads its own text every wake. Whatever stop condition it
contains becomes permanent, and it silently outranks this file because the agent is
following the task it was given. Generating the text is what keeps the two in sync.

If a run needs a constraint this instruction does not express, that belongs in the staged
package or the project state — not in the recurring text.

### Template (what the generator prints)

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

**Root cause, diagnosed 2026-07-29: the macOS input method eats synthetic keystrokes.**

If the active input source is a Korean IME (`com.apple.inputmethod.Korean.2SetKorean`), every `keystroke` from System Events is routed *through* it before reaching the page. Measured on the live board:

| Attempt | What actually happened |
|---|---|
| `keystroke "ZZTEST123"` | came out as Hangul fragments (`떻게`) |
| `keystroke "v" using {command down}` | modifier swallowed; a single character was typed instead of pasting |
| Korean text typed directly | jamo composition broken, characters lost |

That is how a 3,201-character prompt ended up with **zero** Hangul. It was never truncated — the IME consumed it. This is not a Runway bug and not a Lexical bug.

**The prompt field is a Lexical editor** (`data-lexical-editor="true"`, `[contenteditable].textbox-*`). Lexical renders from its own state model, so it ignores `execCommand('insertText')` and direct DOM mutation — both return success and change nothing. It *does* handle real `paste` events.

**Check the input source before any keystroke path:**

```
python3 runtime/scripts/runway_ui_helper.py ime-check
```

`CJK_IME_ACTIVE_KEYSTROKES_UNSAFE` means keystrokes will be mangled. The helper now refuses to fire keys in that state and returns `BLOCKED_IME_ACTIVE` rather than corrupting the field — `paste-image`, `paste-text` and `picker-go` all stop, since each one sends `Cmd+V` or `Cmd+Shift+G`. Either switch the input source to ABC/English for that operation, or use the keystroke-free route below.

Do not retry a keystroke path while a CJK IME is active. It will fail the same way every time, and it fails *silently* — every step reports success while the text never arrives.

**Working route — inject a paste event, use no keystrokes at all:**

```js
const el = document.querySelector('[contenteditable="true"][data-lexical-editor="true"]');
el.focus();
const sel = window.getSelection(), r = document.createRange();
r.selectNodeContents(el); r.collapse(false);      // caret to end; omit collapse to replace all
sel.removeAllRanges(); sel.addRange(r);
const dt = new DataTransfer();
dt.setData('text/plain', text);
el.dispatchEvent(new ClipboardEvent('paste', {clipboardData: dt, bubbles: true, cancelable: true}));
```

Verified: 3,201 → 3,229 characters with the Korean line present and correct. No keystroke is involved, so the IME cannot interfere and no window-focus race exists.

Helper: `runway_ui_helper.py paste-prompt --file F [--replace]`.

**Always verify by the visible character counter afterwards.** Two cautions learned the hard way on this editor:

- A select-all + paste **appended instead of replacing** in one observed run, leaving five copies of the same line and a 6,545-character prompt — well over the 3,500 limit. Re-read the counter after any replace; never assume it replaced.
- Requires Chrome's *Allow JavaScript from Apple Events* (View ▸ 개발자 정보). Without it this route fails with `-1723`, which reads like a permission error but is often the wrong AppleScript dialect — Chrome uses `execute <tab> javascript <text>`, not Safari's `do JavaScript … in <tab>`.

**One writer per board.** Two sessions editing the same composer will clobber each other; that is how the five-copy state above was produced. Before writing, confirm no other session is driving this board.

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

### Seedance QC normalization children

- Keep the downloaded provider file immutable as the raw candidate. Any freeze repair or audio removal becomes a parent-linked child asset; never overwrite the raw download.
- When an effects-only prompt still yields music or sustained ambience, remove the provider audio stream completely. Do not preserve it with a noise gate or partial mute; later rebuild only the approved BGM, real narration, and short visible-action foley in the editor.
- Run `freezedetect` on the raw candidate, remove each confirmed bad interval with explicit trim/concat edits, and run the same threshold again on the child. Record both the removed intervals and the zero-result recheck.
- A technical decode, anatomy, or geometry pass is never enough. Before `PASS` or edit-ready status, compare the clip/contact sheet with the assigned cut IDs, story action, causal bridge, location role, and medium/style lock. A polished but semantically unrelated output is `QC_FAIL_STORY_AND_STYLE_MISMATCH`: reject the raw parent and normalized child as inactive, reopen only the assigned cuts for regeneration, and never hide the mismatch with retiming, crop, or color grade.
- Prompt or storyboard wording is not camera evidence. When the assigned camera contract calls for movement or a composition change, inspect the actual downloaded playback at each scene's start, middle, and end: require a visible change in shot scale, angle, or subject/background geometry plus physical motion proof such as foreground occlusion, multi-plane parallax, changing perspective, or a completed reveal. In a two-scene clip, both scenes must preserve their assigned camera family and the cut must create legible composition contrast; an actor or prop moving inside the same locked framing is not a pass. Missing proof is `QC_FAIL_CAMERA_COMPOSITION_STATIC`: reject the raw parent and normalized child as inactive, reopen only the assigned cuts, and never fake the missing camera move with editorial zoom, crop, or speed change.
- Before calling the child edit-ready, verify SHA-256, `ffprobe`, zero audio streams, the freeze recheck, and a visual contact sheet, then register the child and contact sheet under the canonical numbered `media/` tree. Keep both in `candidate` state until full playback and edit-context QC pass; normalization alone is never approval.

### Completed-card download blocked by Chrome client

If a verified completed Runway card's **visible** Download opens its Runway CDN and Chrome shows `ERR_BLOCKED_BY_CLIENT`, classify the card as `BLOCKED_CHROME_CLIENT_CDN_DOWNLOAD` and `UI_ONLY_NOT_DOWNLOADED`. Keep the card's prompt/deck/settings evidence, but do **not** call it a video candidate or final media.

- Verify that no local non-empty media file appeared before declaring the block; the board's `Download all` control is not evidence by itself.
- Before asking the user to change Chrome, try one identity-safe recovery inside the **same visible Runway tab**: open `Assets` → `All Generations`, identify the exact completed asset by date/order, model, thumbnail and the already-recorded card evidence, open that asset's visible overflow menu, and choose the exact `Download` item. This is still the official Runway UI route; it is not a second session, raw CDN navigation or bypass.
- Capture the browser's real download event and verify its local path. Do not use an ambiguous player/media extractor such as `downloadMedia()` on a feed or viewer with multiple outputs; it can silently retrieve an older card. `Download all` is not identity-safe **by itself** and needs the bundle checks below.
- After the Assets download, prove identity before ingest: compare SHA-256 against earlier candidates/known duplicates, run `ffprobe`, and inspect a review contact sheet. Only then resolve `UI_ONLY_NOT_DOWNLOADED` and register the file under the canonical numbered `media/` tree.
- If the exact `All Generations` asset-menu download also reaches `ERR_BLOCKED_BY_CLIENT`, one final same-tab recovery is allowed: click the visible board-level `Download all` exactly once. Accept it only after Runway reports a completed file count and a non-empty local ZIP exists. Do not repeat the click while it is preparing.
- Treat the ZIP as an untrusted mixed-session bundle, not as ordered scene output. Match every ingest candidate to the current attested prompt fingerprint plus model/format evidence; verify bytes and SHA-256, register same-prompt variants as separate revisions, and send all variants through QC before selecting one. Exclude unmatched legacy or failed-generation members instead of assigning them by ZIP order or filename alone.
- If `Download all` also fails to create a verified local bundle, the safe UI ladder is exhausted and the Chrome client unblock below becomes the required human action.
- Do not bypass the block with the raw CDN URL, `curl`, API/MCP, Credits Mode, a second browser, or a re-generation.
- Tell the user to allow the Runway CDN only in their Chrome blocking/privacy client, then resume the **same session** and download the already-completed card. Do not re-submit it.
- A lost Chrome tab may be reopened to its exact verified Runway session URL only with the user's explicit instruction; that restores the board, not a new Runway session or a second browser loop.
