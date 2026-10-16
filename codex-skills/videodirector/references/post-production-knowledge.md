# Post-production knowledge — NOT part of the active rail

> **Status: inactive.** The editor/CapCut lane was retired on 2026-10-16 (runtime v5,
> `docs/contracts/2026-10-16-preprod-shelf-v5.md`). Package now delivers QC-approved clips in
> storyboard order. This file preserves paid-for editing, typography and caption lessons for a
> **future editor rebuild**. Do not load it for current production, and do not let it reintroduce
> an edit stage, CapCut draft or flattened master into a v5 project.

Related detailed lessons (also post-production): `typography-calibrations.md`, the marked sections of
`user-calibrations.md`, and `/Users/gnudas/wiki/queries/mv-typography-capcut-remotion-tests-2026-09-22.md`.

## 1. Editable-timeline principle (formerly "CapCut-first")

- For serious MV/public-contest/institution work, a single flattened ffmpeg-assembled MP4 is not an
  editable result. ffmpeg is for QC, normalization, contact sheets, proxy previews,
  ffprobe/blackdetect/freezedetect and timing slates only.
- The edit should live in an editor draft (CapCut was used) with separate media/text/audio tracks so
  the user can adjust clips, timing, audio and text. A flattened reference render is labelled
  `QC/proxy/reference`, not the editable final.
- A draft is valid only after **actual preview/playback** in the editor. A JSON-injected draft that
  shows clip blocks but a black viewer, stalled playback or missing media is HOLD/DO_NOT_USE; rebuild
  through the editor's own import/timeline route.
- Preserve the previous draft before modifying it; on user acceptance lock the draft, export the final
  MP4 and keep the editable project files.

## 2. Caption legibility — shadow first (KAIA lesson, 2026-05-13)

- Do not fix low-visibility Korean captions by random color changes (mint, bright yellow, flashy accents).
- Fundamentals first: **short copy, large type, real shadow enabled at ~50–70% opacity, subtle dark
  stroke, enough hold time.** On bright sky, sunset, city lights, glass, HUD or busy backgrounds, the
  shadow is a required legibility layer, not decoration.
- Prefer white / off-white text with dark shadow/stroke; accent color only with a narrative or
  information role. Avoid rounded subtitle boxes; plates are a last resort.
- Drop tiny helper labels that compete with the main caption.
- QC on the real preview and exported full-frame stills; contact sheets understate fade frames. The
  hold section of every key caption must be clearly readable.

## 3. Typography craft

- Narration/body text: quiet, cinematic, literary; usually unboxed; a calmer font than chapter cards.
- Phrase A → phrase B in the same position: give B an equivalent solo reading breath before any
  subordinate line appears.
- Equal transform X values do not guarantee visual alignment (text-box center vs rendered width);
  verify alignment in the actual preview with screenshots.
- Editor font limitations (e.g. macOS CapCut flattening Korean fonts): render high-fidelity typography
  externally as transparent overlays, align them back into the draft, label it as a font-fidelity
  workaround, and compare draft vs rendered master.
- Timecodes like `00:04:23` in a 24 fps project mean 4 + 23/24 s, not 4.23 s. Align a stamp's visible
  impact frame to the waveform peak unless a deliberate pre-roll resolves on the beat.
- Typography dataset routing: when a project has `production/typography_research/`, read its protocol
  and selected references before designing (see `user-calibrations.md`).

## 4. Subtitles and lyrics

- Do not subtitle every lyric; decide `none / low / medium / high` per section (the music lane's lyric
  handoff carries `subtitle_priority`).
- Keep a clean master and a subtitled master; avoid karaoke captions unless asked; prefer selective
  kinetic subtitles matching the MV world.
- Preserve editable sources (timed CSV/SRT/ASS, editor text tracks); use verified CJK fonts; broken
  glyphs are a font failure, not an acceptable export. Preferred bilingual layout: Japanese top line in
  yellow, Korean bottom line in white, bottom-centered with black outline.

## 5. Transitions and assembly QC

- Check the first third of the edit for cut-to-cut jitter, micro stutters, duplicate/frozen frames, bad
  crossfade handles, optical-flow artifacts and 1-frame flashes; fix with clean handles, motivated short
  dissolves, normalization, or trimming unstable first/last frames.
- Alpha deliverables: round-trip a small sample first (VP9 WebM once composited black; ProRes 4444
  passed in earlier local tests — re-verify on the current version).

## What still applies in v5 (upstream equivalents)

The useful parts of this knowledge now live upstream: design each storyboard block's `end_frame` for
the next block, keep actions inside the 15 s with clean start/settle (handles), keep generated clips
text-free unless the storyboard requires on-screen text, and regenerate a failed block rather than
expecting an edit to hide it.
