# Mode-specific rules

One workflow, different obligations depending on what is being made.

## MV mode

## User MV production standing rules

For the user's MV work, these override generic planning defaults:

- Default to no-question, one-block execution unless safety/login/payment/CAPTCHA/deletion/sensitive-upload requires stopping.
- Music comes first: beat, accent, phrase, lyric hook, energy curve, and cadence determine the cut map.
- Do not arbitrarily choose a length; choose the ending from musical resolution.
- Do not deliver raw PNG/JPG stillframes as clips. Stills are only image-to-video source frames.
- Do not use static zoompan/Ken Burns stills as MV filler.
- One generated video clip may be used exactly once in the delivered sequence.
- Each cut needs a unique startframe; motifs may return, identical image/video files may not.
- Every cut must advance action, information, emotion, rhythm, joke, or transition.
- For iterative skill improvement, prefer ~60s review prototypes before longer versions.
- Always create review contact sheets/keyframes and a self-contained package before claiming completion.

## MV cut-sense correction

For music videos, avoid false microcutting. A cut is justified only by beat/accent, lyric hook, action change, information reveal, emotional turn, or an intentional transition. If the audience cannot feel why the cut happened, the shot should usually be held longer. Near-identical scene repeats in different crops are a failure, not variation.

## Non-negotiable MV quality rules learned from user review

These rules are cumulative team memory and apply to every MV project unless explicitly overridden.

1. **Music-first, not table-first.** The block map starts from beat, accent, phrase, lyric hook, energy change, and natural ending cadence. Do not force visuals into a prewritten duration grid.
2. **No stills as clips.** PNG/JPG styleframes are only I2V source frames. Do not deliver raw stills or static zoompan filler. Missing video means regenerate video.
3. **One generated video = one use.** A generated clip may appear in the delivered sequence exactly once. No duplicate clip reuse.
4. **No image recycling.** Each cut needs a unique startframe. Returning motifs are allowed only with changed composition/action/lighting/story function.
5. **Every cut must advance something.** Each shot needs at least one: new action, new information, emotional shift, rhythmic hit, visual joke, or transition.
6. **Ending must be musical.** Choose the last block's `end_frame` from cadence/energy drop/phrase resolution, not arbitrary target length.
7. **1-minute review loop.** Improve team skill through ~60s prototypes: produce → review → update rules → rebuild.
8. **Self-contained delivery.** Package QC-approved clips in storyboard order, audio, manifest CSV+JSON, review contact sheet/keyframes, and notes. No edited master in the v5 rail.
9. **Contact-sheet QC before completion.** Review for duplicated impressions, weak beat fit, unclear story, missing anchors, unwanted motifs, and AI-looking repetition.
10. **Persistent feedback.** User criticism is promoted to standing production rules, not treated as a local one-off.

## Additional hard rule: no false microcutting

A cut must be felt. Do not split one visual moment into multiple cuts unless there is a real musical, narrative, action, or transition reason. If three seconds read better as one held shot, hold it. Different crops, small framing changes, or repeated I2V outputs are not valid cut structure.

If an I2V output visually collapses into the same scene as another cut, or does not match the intended source image, reject it and regenerate/merge; do not treat it as complete media.

## Lyrics handoff

For music videos, the Music lane should provide or request a lyric/section handoff whenever lyrics matter; the Planner uses it to place lyric moments in storyboard blocks (P2).

```csv
time_start,time_end,section,lyric,subtitle_priority,visual_note
00:00.000,00:08.000,intro,,none,show mood before words
00:08.000,00:16.000,verse,"lyric line",low,translate through image instead of full text
00:32.000,00:40.000,chorus,"hook line",high,use minimal kinetic subtitle
```

Generated clips stay text-free unless the storyboard explicitly requires on-screen text. Subtitle/caption authoring (SRT/ASS, kinetic captions) is post-production and is not part of the v5 rail; keep `subtitle_priority` as a note for a future editor. See `post-production-knowledge.md`.

## Public contest / institution mode

## Public contest delivery and submission lessons — 2026-05-06

For public-sector contest videos, deliver more than the final MP4. Prepare a complete submission package when relevant:
- YouTube title, description, hashtags, and visibility recommendation;
- AI-use disclosure describing tools/process;
- production intent explaining why the work was made and what value it communicates;
- synopsis summarizing the story sequence;
- link/password note and prior-contest history.

Submission safety:
- Verify the exact YouTube channel/account before upload. If visibility is not specified, save as private by default. Never public-publish without explicit final confirmation.
- For contest/government forms containing personal information, fill drafts only unless the user explicitly confirms final submission of that exact form. Do not click final Submit merely because routine fields are ready.
- In Safari/Google Forms/YouTube, Korean text may be lost through synthetic typing; prefer clipboard paste or direct JS value setting, then verify field labels and values. Especially audit `AI 활용 내역`, `제작 의도`, `시놉시스`, link, and password fields so they are not swapped.

Typography/caption work for contest masters is post-production (not in this rail); see `post-production-knowledge.md`.
