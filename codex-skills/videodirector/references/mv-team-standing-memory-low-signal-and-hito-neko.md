# MV Team Standing Memory — Low Signal + Hito Body / Neko Brain

This is shared memory for the user's MV agents. Apply by default to future MV work.

## Operating mode
- User prefers execution over questions.
- Proceed in one block: analysis → cut map → images → I2V → edit → QC → package.
- Ask only when safety/login/payment/CAPTCHA/account/deletion/sensitive upload blocks execution.

## Music-first rule
- Start from audio: beat, accents, phrase boundaries, lyric hooks, energy curve, cadence.
- Do not force a prewritten cut table onto the track.
- Ending must be justified by musical cadence, not arbitrary target length.

## No-still final rule
- ChatGPT/GPT Images outputs are startframes only.
- Final/review timeline must contain videoized clips only.
- No raw PNG/JPG, no still+zoompan filler, no pretending a slideshow is an MV.

## Unique media rule
- One generated video clip appears exactly once.
- One cut gets one unique source frame and one unique I2V output.
- Motifs may repeat; files/compositions should not.

## Story rule
- Every cut must advance action, information, emotion, rhythm, joke, or transition.
- Keep one-sentence premise and cause→discovery→turn/pursuit→resolution spine.
- User-liked shots become structural anchors.

## Low Signal carryover
- No arbitrary 35-cut cap; cut count follows song density.
- Self-contained package required: master, clean master if relevant, ordered clips, audio, EDL/manifest, contact sheet/keyframes, notes.
- Review contact sheet before claiming completion.
- Avoid rejected motifs permanently: no earpiece/earbuds/headset/cable-to-ear; no talking-mouth/lip-sync/dialogue-looking shots for that project.
- Prefer physical/infrastructural storytelling: body, hand, wall, floor, puddle, reflection, shadow, light/signal trace.

## Hito/Neko carryover
- Mika remains adult office worker and fully human; no real cat ears/tail/whiskers.
- Kuro is the only actual cat.
- Red laser, box, ribbon, rooftop, lamp, amber eyes are motifs, not reusable frames.
- 1-minute prototypes are preferred for iterative review before longer versions.
- Beat-fit failure and visual recycling are hard failures.

## 2026-05-05 Hito/Neko R60 cut-design correction

User feedback: the 3-second proof did not justify three separate cuts. It felt like the same scene was split into different framings without beat-fit, transition logic, or semantic change. For this team, this is a failure mode.

Standing rule added:
- Do not microcut a visually identical moment just because the cutlist has rows. If a moment reads as one scene and there is no clear beat accent, action change, information reveal, emotional turn, or transition device, hold it as one sustained shot.
- A cut is valid only when the viewer can feel why the cut happened. Cropping, aspect-ratio shift, or near-identical recomposition is not a valid cut reason by itself.
- If Grok output does not preserve the intended source image identity/composition, mark it REJECTED, not DONE. Do not trim it into the edit just because a video file exists.
- Before CapCut handoff, inspect generated clips for source-lineage mismatch and repeated-scene collapse. Repeated-scene collapse means multiple cuts visually become the same scene even if their prompts/images differ; these must be merged, regenerated, or rejected.
- For intro/low-energy openings, prefer one clean sustained shot over fake rhythmic cutting unless the music clearly demands cuts.

## 2026-05-17 Runway / Seedance file-picker upload correction

User feedback: this exact upload failure had happened before. In Runway, selecting a local file in the macOS file picker is **not** the upload. If the agent only clicks/selects the file or closes the picker, Runway does not register the asset/reference.

Standing rule added:
- When using Runway/Seedance file-picker upload, treat one upload as complete only after this full sequence: open picker → select the intended local project file → click the bottom-right `업로드` button → wait for the Runway upload/progress card (`Cancel`/progress state) to finish → verify the new visible asset thumbnail in Runway → only then double-click/select it as a reference.
- Do not count a local filepath, Finder selection, highlighted row, or closed picker as uploaded.
- If a search term or Recents view hides the new asset, clear/filter carefully and wait; do not switch to arbitrary existing Recents assets.
- For ordered multi-reference jobs, upload and verify references one at a time in story order unless the UI visibly preserves order. For the current BOHUN crisis sequence, the order is `C13 → C12 → C14`.
- Never use assets the agent did not create/prepare for the project just because they appear in Runway Recents. Use only verified local project upload files, or prove the visible thumbnail matches the intended local file before selecting.

## Runway / Seedance prompt insertion hard rule — 2026-05-17
- For Runway/Seedance prompt boxes, **never use slow literal typing / per-character `type_text` for long prompts**. Long prompts must be inserted by reliable paste or direct value set only.
- Default sequence for Runway prompt insertion: focus the Prompt field → select all existing prompt → paste the full prepared prompt from clipboard in one operation → verify the visible character count and beginning/end content → then click Generate.
- Do not repeatedly experiment with Safari Developer Tools, Web Inspector, DOM scripts, or keyboard shortcuts while the user is waiting to generate. If Web Inspector opens accidentally, close it immediately and return to the Runway page.
- If an accessibility `set_value`/DOM setter truncates at line breaks or only inserts the first line, stop using that method for Runway prompts; use clipboard paste into the focused prompt field instead.
- Do not open upload/reference pickers when the reference slots are already correct. For an already-prepared Runway generation, the job is simply: prompt in, Generate click, wait.
- Before clicking Generate, do only the minimum verification needed: correct reference thumbnails/order, prompt under 3500 chars, correct model/settings visible. Avoid extra UI churn.

## Runway asset-search prohibition for not-yet-uploaded local files — 2026-05-17
- Do **not** search the Runway Asset selector for a local project file that has not already been visibly uploaded and registered in Runway.
- Asset search is only for already-visible/previously-uploaded Runway assets. It is not an upload method.
- For new local references, use only: Asset selector drop zone / Add image reference → macOS file picker → select exact prepared local file → click bottom-right `업로드` → wait for upload/progress → verify a visible new thumbnail/reference slot.
- If the file is not visible after upload, do not pretend search will find it. Either wait for the upload to finish, retry the upload correctly once, or mark BLOCKED with the exact UI state.
- Never mix these two states: `local file exists` ≠ `Runway asset exists`. Treat them separately in notes and UI actions.

## Runway/Safari keyboard-shortcut safety — 2026-05-17
- In Safari Runway production, do not use ambiguous keyboard shortcuts such as Cmd+A/Delete/Cmd+Shift combinations when focus is uncertain; they have repeatedly opened Web Inspector or affected the wrong pane.
- If Web Inspector appears, close it immediately and do not continue with shortcut-based cleanup.
- Prefer explicit visible UI controls: close/cancel the modal, reopen the intended upload control, use the macOS file picker, click the visible Upload button, and verify thumbnails.
- For asset selector cleanup, do not rely on search-field keyboard clearing; close the selector and reopen cleanly if the UI is polluted by a wrong search.
