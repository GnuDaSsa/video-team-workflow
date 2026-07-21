# Scene advancement policy — 2026-07-19

User correction: scheduler must not sit on one scene and repeatedly make near-identical videos. It must advance scene-by-scene with visible evidence.

## Immediate correction
- Deleted heartbeat automation `runway-b01-yuldong-generate-monitor`.
- Paused local/runtime queue files and disabled all `enabled=true` tasks.
- No Credits/Max/Grok fallback may be triggered by scheduler.

## Rule from now
1. One scene id = one prearm = one Generate click attempt.
2. After any Generate click, mark the scene `submitted_pending_visible_card` or `not_submitted_blocker`; do not click that same scene again automatically.
3. If Runway accepts it, verify visible new card, then move to the next scene package immediately while current one queues.
4. If Runway returns Please-wait/Credits blocker, leave that exact prearm alone and do **not** keep retrying every heartbeat. Prepare the next scene package offline or wait for user/operator decision.
5. QC is a separate pass after download/contact sheet. Scheduler should not pretend it is QC-ing if it is only clicking Generate.
6. Any future monitor must read a scene queue with cursor/lock and advance to `next_pending_scene`, never hard-code B01.
7. Duplicate guard: same `scene_id + prompt_sha + ref_manifest_sha` cannot be clicked twice by automation unless the previous attempt is explicitly marked `failed_no_card_retry_authorized_by_user`.

## Current B01 status
B01 Yuldong small-fire deck is prearmed in Runway but not submitted; repeated blue clicks returned Please-wait/Credits blocker and no new B01 card. No more automatic B01 clicks.


## 2026-07-19T20:11:19.610097 correction: blue is not a command
- Visible blue Generate means only `clickable`, not `click now`.
- Required Generate sequence is strict: (1) select next scene from queue, (2) clear/replace refs for that scene, (3) replace prompt and verify visible char counter/content, (4) verify settings, (5) if blue and no wait blocker, click exactly once, (6) mark scene click nonce consumed and move cursor.
- Never click Generate twice for the same `scene_id + prompt_sha + ref_manifest_sha`, even if the button stays blue or appears blue again after delay.
- If a first click has ambiguous effect, wait and inspect visible cards/AX for at least `In queue`/`Generating` before considering any retry; retry requires explicit operator note and a changed nonce, not automatic blue-button logic.
- The B02 duplicate happened because a delayed coordinate click was misread as a miss, then AX clicked again. Treat this as `DUPLICATE_SUBMISSION_INCIDENT_B02_20260719` and do not repeat.


## 2026-07-19 operator repair: transaction-first Seedance loop
- Treat each Seedance submit as an atomic transaction: PREPARE refs -> SET prompt -> VERIFY visible refs/prompt/settings -> CLICK ONCE -> VERIFY visible card -> ADVANCE cursor.
- Do not split a submit transaction across loose heartbeat reasoning unless all transaction state is read from the local queue/status and visible UI.
- Blue Generate means only clickable; it never means click by itself.
- If a click attempt makes state ambiguous (button gray but no visible card, or DOM/AX mismatch), mark `AMBIGUOUS_CLICK_NEEDS_OPERATOR_REVIEW`; do not retry automatically and do not advance as if submitted.
- Generate click method priority: (1) stable DOM/AX Generate button identity and visible button color cross-check; (2) calibrated screen coordinate from full-screen/native pixel mapping only; never use crop-relative coordinates.
- Heartbeat may monitor and prepare local next-scene assets, but must not overwrite current Runway prearm unless the current scene is visibly queued/submitted/completed or explicitly abandoned by operator decision.
- While Runway is gray/waiting, do useful non-UI work: next-scene prompt/ref QC, provider matrix update, download/QC completed cards. Do not burn cycles clicking.


## 2026-07-19 prompt-authoring correction: 5.6 Terra high creative video director
- Current failure mode: many Seedance prompts were 2,300–3,000 character template copies that over-used `preserve crop/composition`, `locked source frame`, `slow push`, and broad negative tails. This made Seedance behave like a cautious slideshow instead of a cinematic video generator.
- From now on, every Seedance video prompt must pass a `video_prompt_director_high` rewrite before UI submission: requested authoring route `gpt-5.6-terra`, reasoning effort `high`, prompt_style_version `creative_seedance_5_6terra_high_20260719`.
- The final UI prompt target is 700–1,500 characters when practical; Runway's 3,500 is the actual hard maximum, not an automatic failure before that.
- References are anchors, not cages. Lock essential identity/symbol/safety details; allow Seedance creative latitude for shot size, camera path, blocking, transitions, environmental motion, and visual rhythm.
- Do not repeat generic “dignified slow push / tiny parallax / settle into hold” on every image. Each 15s scene needs an arc: establish → approach/reveal → tactile/action detail → resolution/hold.
- Exact crop/composition locks are reserved for fragile shots: Taegeukgi/trigram geometry, faces, hands, phone/text screens, macro symbolic details, or explicit anti-boiling regeneration. Otherwise use “preserve story motif; allow cinematic reframing within the same scene.”
- The automation must not upload or click Generate for any scene whose local prompt metadata lacks this style version, unless the user explicitly orders a legacy retry.


## 2026-07-19 visual-semantics correction
- User correction: final Seedance prompts must not include production-origin language (`공냥`, Gongnyang, imagegen, source frame, prompt pack, provenance, QC). Those are local workflow facts, not video instructions.
- `@ImageN` roles must describe visible cinematic function, not arbitrary labels. Do not write `Image4 = Bundang-ri` or similar unless the image visibly establishes that place or the motion itself needs that label. Location/factual names belong in CapCut captions/narration copy, not necessarily in Seedance prompt text.
- Preferred roles: ember/prison light, ridge beacon, eye/glasses memory, hands preparing cloth, market lane, crowd wave, road spread, aftermath hold.

## Finder window placement rule — added 2026-07-20
Before any Runway/Seedance drag/drop, close unrelated Finder windows, open exactly one current upload_staging folder, immediately move Finder to a safe non-overlapping position, then inspect visible Runway UI. Drag one file at a time and verify each Image thumbnail before continuing. Use Codex Computer Use drag only; if it is unavailable, mark the lane blocked. Do not let random Finder window placement cover reference slots, prompt/settings, or Generate.


## Finder placement correction — 2026-07-20
Staging Finder windows must be opened with `tools/position_seedance_finder_window_20260720.sh` and positioned at mid/slightly upper-right bounds `{780, 105, 1230, 505}`. They must not cover Runway refs/prompt/Generate. Close Finder immediately after uploads.
