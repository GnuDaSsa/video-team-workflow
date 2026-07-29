# Mode-specific rules

One workflow, different obligations depending on what is being made.

## MV mode

## User MV production standing rules

For the user's MV work, these override generic planning defaults:

- Default to no-question, one-block execution unless safety/login/payment/CAPTCHA/deletion/sensitive-upload requires stopping.
- Music comes first: beat, accent, phrase, lyric hook, energy curve, and cadence determine the cut map.
- Do not arbitrarily choose a length; choose the ending from musical resolution.
- Do not place raw PNG/JPG stillframes in final or review edits. Stills are only image-to-video source frames.
- Do not use static zoompan/Ken Burns stills as final MV filler.
- One generated video clip may be used exactly once in the timeline.
- Each cut needs a unique startframe; motifs may return, identical image/video files may not.
- Every cut must advance action, information, emotion, rhythm, joke, or transition.
- For iterative skill improvement, prefer ~60s review prototypes before longer versions.
- Always create review contact sheets/keyframes and a self-contained package before claiming completion.

## MV cut-sense correction

For music videos, avoid false microcutting. A cut is justified only by beat/accent, lyric hook, action change, information reveal, emotional turn, or an intentional transition. If the audience cannot feel why the cut happened, the shot should usually be held longer. Near-identical scene repeats in different crops are a failure, not variation.

## Non-negotiable MV quality rules learned from user review

These rules are cumulative team memory and apply to every MV project unless explicitly overridden.

1. **Music-first, not table-first.** The edit map starts from beat, accent, phrase, lyric hook, energy change, and natural ending cadence. Do not force visuals into a prewritten duration grid.
2. **No stills in final/review edit.** PNG/JPG styleframes are only I2V source frames. Do not place raw stills or static zoompan filler into the timeline. Missing video means regenerate video.
3. **One generated video = one use.** A generated clip may appear in the timeline exactly once. No duplicate clip reuse.
4. **No image recycling.** Each cut needs a unique startframe. Returning motifs are allowed only with changed composition/action/lighting/story function.
5. **Every cut must advance something.** Each shot needs at least one: new action, new information, emotional shift, rhythmic hit, visual joke, or transition.
6. **Ending must be musical.** Choose the cut point from cadence/energy drop/phrase resolution, not arbitrary target length.
7. **1-minute review loop.** Improve team skill through ~60s prototypes: produce → review → update rules → rebuild.
8. **Self-contained delivery.** Package final/review master, ordered clips, audio, EDL/manifest CSV+JSON, review contact sheet/keyframes, and notes.
9. **Contact-sheet QC before completion.** Review for duplicated impressions, weak beat fit, unclear story, missing anchors, unwanted motifs, and AI-looking repetition.
10. **CapCut remains the editable edit surface.** Do not use ffmpeg to flatten the whole edit into one unadjustable MP4 and present that as the main deliverable. ffmpeg may be used before CapCut for QC/proxy/timing/contact-sheet/ffprobe checks only. The working/final handoff must preserve CapCut editability as much as possible: separate clips, audio, text layers, manifests, and a CapCut draft the user can adjust. A draft is valid only after actual CapCut preview/playback is verified; JSON-created timelines that show blocks but produce a black viewer or stalled playback are HOLD/DO_NOT_USE and must be rebuilt through CapCut's own import/timeline route.
11. **Persistent feedback.** User criticism is promoted to standing production rules, not treated as a local one-off.

## Additional hard rule: no false microcutting

A cut must be felt. Do not split one visual moment into multiple cuts unless there is a real musical, narrative, action, or transition reason. If three seconds read better as one held shot, hold it. Different crops, small framing changes, or repeated I2V outputs are not valid cut structure.

If an I2V output visually collapses into the same scene as another cut, or does not match the intended source image, reject it and regenerate/merge; do not treat it as complete media.

## Lyrics and subtitle workflow

For music videos, the Music Director should provide or request a lyric/section handoff before final editing whenever lyrics matter. The Editor must consider subtitles as part of the edit, not an afterthought.

Required Music Director handoff when available:

```csv
time_start,time_end,section,lyric,subtitle_priority,visual_note
00:00.000,00:08.000,intro,,none,show mood before words
00:08.000,00:16.000,verse,"lyric line",low,translate through image instead of full text
00:32.000,00:40.000,chorus,"hook line",high,use minimal kinetic subtitle
```

Subtitle policy:

- Do **not** subtitle every lyric by default. Decide `none / low / medium / high` by section and emotional importance.
- Keep a clean master without subtitles and a subtitle master when subtitles are added.
- Avoid karaoke-style captions unless the user explicitly asks. Prefer selective kinetic subtitles that match the MV world.
- The Music Director owns lyric meaning and hook emphasis; the Planner maps lyric moments to scenes; the Editor/Post Supervisor creates SRT/ASS/CapCut text CSV and checks timing/readability.

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

Typography/CapCut workflow update:
- CapCut remains the edit-handoff environment when requested.
- If macOS CapCut font support makes typography look generic, design/render high-fidelity Korean typography externally as transparent overlays or a baked master, then import/align it back into the CapCut draft where practical.
- Treat external typography as a font-fidelity workaround, not an excuse to ignore CapCut.
