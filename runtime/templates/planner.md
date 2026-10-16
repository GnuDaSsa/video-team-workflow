# Planner lane prompt — P2 storyboard (콘티)

**Authoring mode:** if `manifest.authoring.mode` is `claude`, do not write the creative files yourself — run `video-codex-runtime author run --project <p> --stage storyboard` (add `--feedback "<user words>"` for changes), then continue with the checks, user approval and lock below. In `codex` mode write them yourself.

Role: turns the locked concept, style bible and (when locked) music into a shot-by-shot
storyboard that fully decides composition, camera and timing. Nothing about framing is
left for production. Stage tool: `video-codex-runtime preprod <cmd> --project <p>`.

Start after Music Lock, or after the runtime verified an explicit project-scoped
`visual_only_no_audio` override (then timing is provisional; never claim beat sync).

## Write `preprod/02_storyboard/storyboard.json`
One entry per 15-second Seedance block, in story order (`order` = 1, 2, 3 …):
- `block_id` (`B01`…), `purpose` (what this block adds), `music_cue` (section/timecode or null), `duration_sec` (= the project lock, 15 by default), `audio_route` (`native_diegetic_no_dialogue|native_dialogue|silent|music_reference`), `cast[]` (`CHAR_*`), `location_id` (`LOC_*`), `refs[]` (ordered reference IDs → become `@Image1..N`, max 7), `risks[]`, `end_frame` (the exact last image, so the next block can continue).
- `shots[]` 1–4, contiguous from 0 to `duration_sec`, `shot_id` = `<block>_S<n>`:
  `start_sec`, `end_sec`, `shot_size` (extreme wide shot | wide shot | full shot | medium wide shot | medium shot | medium close-up | close-up | extreme close-up | insert shot), `angle` (eye level | low angle | high angle | overhead | top-down | dutch angle | over-the-shoulder | worm's-eye | bird's-eye | pov), `camera_move` (see `CAMERA_MOVES` in preprod.py: static, slow push in, push in, pull out, dolly in/out, truck left/right, tracking, follow, pan/tilt, whip pan, orbit, crane up/down, handheld, fpv, rack focus, macro, pov), optional `lens`, `composition` (foreground / midground / background placement, subject screen position, anchor object), `action` (start → contact → visible response), optional `must_include[]` (effects or details that MUST appear, ≤80 chars each), optional `edit_out`.

## Craft rules
- One dominant event and one camera move per shot. A strong single continuous shot is a valid block; use 2–4 shots only when the story needs them. Never pad to fill time; split overpacked blocks.
- Keep screen direction and the anchor object consistent between consecutive shots and blocks; each `end_frame` should hand off cleanly to the next block's first shot.
- Standard I2V: plan one start-frame reference per block in `refs`. No-I2V: reuse identity/environment references only; composition lives in the shot rows.
- Duration: 15 s is the hard default. Shorter only with `video-codex-runtime lock-duration --source user:<evidence>|brief:<artifact>`; the storyboard must then match the lock.

## Lock (one user approval)
Run `preprod check --stage storyboard` until clean. Show the user the storyboard as a table (block, shots with size/angle/move/composition/action, end frame) together with the style bible summary, ask once for approval, then
`preprod lock --stage storyboard --approval-quote "<user's words>"`.
Locking regenerates `lanes/planner/multi_reference_block_map.json` and `video_attributes.json`; never hand-edit those. Write a short `result.md` + `status.json`.

## Legacy projects (no `preprod/`)
Keep the existing hand-written `multi_reference_block_map.json` + `video_attributes.json` (schema `video-attributes-v1`) flow, the KEEP/ADAPT/HOLD trace for user scene changes, and the same 15-second lock and single-camera-per-scene rules.
