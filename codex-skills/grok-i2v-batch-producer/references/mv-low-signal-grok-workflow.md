# mv-low-signal Grok workflow retrospective

This reference captures practical lessons from completing `~/mv-low-signal` on 2026-05-02/03.

## What worked

- Expected outputs came from `video-prompts/i2v-prompts-v5.json` and final files went into `generated-videos`.
- Missing cuts were identified by comparing all JSON `cut` values against `{cut}_video.mp4` files.
- Suspicious small file threshold: about 2 MB. `C-12` was 1.0 MB and was regenerated.
- Safari was more reliable than in-app browser for Grok file uploads and real downloads because it had the user's logged-in session.
- Grok asset URLs may be visible in `<video>` tags but direct `curl` can fail with 403. Use the browser Download button.
- Final organization used hardlinks/copies into `final-ordered-cuts` and moved originals to `_raw-original-cuts`.

## Fragility notes

- AppleScript `do JavaScript` with `read POSIX file` corrupted Korean literals in JS. Button text checks like `includes('제출')` failed. Use `String.fromCharCode(51228,52636)` instead.
- Grok sometimes navigated from a post or tab to another Safari tab. Before every action, set Safari `current tab of front window to tab 1` or locate the Grok tab by URL.
- Face/lip/head animation prompts can hang at 0% or 99%. C-19 and C-25 initially stalled; safe no-face-motion prompt overrides completed.
- A generated image post can show a `동영상 만들기` button; clicking it starts a second video job.

## Safe protagonist prompt examples

C-19 style:

```text
[STATIC] locked-off portrait, only the earpiece cable sways very slightly and cold rim light flickers once. The face, eyes, mouth, and head remain completely stable with no facial motion. Preserve the input image identity, composition, lighting, and color palette. No text, subtitles, logos, watermarks, extra people, face morphing, lip sync, or camera overmovement. Photorealistic Korean live-action dark tech-noir / restrained alternative gugak music video style. Clip duration 2 seconds.
```

C-25 style:

```text
[SLOW_ZOOM_IN] very slow camera push on the side profile, tiny atmospheric haze moves in the background only. The face, eyes, mouth, shoulders, and head remain completely stable; no visible breathing animation, no face morphing. Preserve the input image identity, composition, lighting, and color palette. No text, subtitles, logos, watermarks, extra people, or camera overmovement. Photorealistic Korean live-action dark tech-noir / restrained alternative gugak music video style. Clip duration 3 seconds.
```

C-27 style:

```text
[SLOW_MOTION] restrained hand silhouette and coat edge move subtly while the head and face remain stable, controlled modern gugak presence without theatrical movement. Preserve the input image identity, composition, lighting, and color palette. No text, subtitles, logos, watermarks, extra people, face morphing, head tilt, lip sync, or camera overmovement. Photorealistic Korean live-action dark tech-noir / restrained alternative gugak music video style. Clip duration 2 seconds.
```

## Output structure used

```text
generated-videos/
  final-ordered-cuts/
  _raw-original-cuts/
  _logs/
  _backups/
  final-ordered-cuts_manifest.csv
  final-ordered-cuts_manifest.json
  lyrics-scene-application-guide.md
  lyrics-scene-application-guide.csv
```
