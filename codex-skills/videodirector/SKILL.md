---
name: "videodirector"
description: "Use when the user asks for video work such as video planning, shortform/reels/shorts/trailer concepts, storyboards, cut lists, scene breakdowns, ChatGPT Image 2 styleframe prompts, Grok image-to-video prompts, Suno BGM planning, narration sheets, subtitle sheets, or CapCut handoff packages. Trigger on Korean requests like 영상, 영상업무, 홍보영상, 숏폼, 콘티, 컷리스트, 장면 구성, 나레이션, BGM, Grok, Suno, CapCut. Kling only when explicitly requested."
---

# Video Director

Specialized workflow for planning and packaging AI-assisted video production work. Use this skill for concept development, scene structure, prompt packages, soundtrack planning, and edit-ready delivery sheets.

## First-line rule

- When this skill is active, start the response with `[videodirector]` on its own line.

## Hermes-global routing

For this user, Hermes is now the global entrypoint/orchestrator for external commands and long-memory MV/video-team direction.

- Treat Hermes standing memory and any brief supplied by Hermes as director context.
- Do **not** automatically invoke `~/.local/bin/hermes-mv` when the request already arrived through Hermes, Telegram-Hermes, or another Hermes-managed route. That creates a duplicate Hermes loop.
- Codex owns execution: local files, browser automation, ChatGPT Image 2 production, Grok I2V operation, edit/package commands, and verification.
- Invoke a separate Hermes sidecar only when the user explicitly asks for an extra Hermes critique/pass, or when Codex is being run standalone outside Hermes and the task truly needs long-memory director review.
- If explicitly needed, use:

```bash
~/.local/bin/hermes-mv -z "<compact Korean task brief + current project path + requested deliverables>"
```

- If the optional sidecar is unavailable, continue the video task using the standing rules and briefly report that the sidecar was unavailable.
- Do not send secrets, cookies, payment details, private tokens, or sensitive account data into Hermes prompts.

## Language rules

- Planning notes, explanations, narration, dialogue, and delivery guidance: Korean
- Image prompts, video prompts, and BGM prompts: English
- JSON keys: English

## When to use

- Video concept and structure planning
- Public-sector promo videos
- Shortform, reels, shorts, trailers
- Storyboards and cut lists
- Scene breakdowns
- Character reference prompt design
- ChatGPT Image 2 styleframe prompts
- Grok/I2V motion prompts
- Suno 5.5 BGM planning
- Narration, subtitle, and edit handoff sheets

## Start protocol

If the user has not already provided them, confirm these three items first:

1. Style: Makoto Shinkai / photoreal / ink wash / other
2. Length: 30s shortform / 60s trailer / 2-3 min full video
3. Characters: existing characters / no fixed character

If the request is underspecified but execution can still proceed, choose sensible defaults and say so briefly.

## Standard workflow

1. Confirm concept and goal
2. Break the project into scenes
3. Define character references if needed
4. Write start-frame prompts for each scene
5. Write Grok/I2V motion prompts
6. Plan Suno BGM tracks
7. Produce narration/subtitle/edit sheets

## Tool routing hard rule for this user

- Still images/styleframes/start frames/character sheets: **ChatGPT Image 2 only**.
- For a new project, ChatGPT Image 2 work must start in a **new ChatGPT tab/new chat** dedicated to that project.
- ChatGPT Image 2 production prompts must be **single-image prompts**: one cut only. Never ask for 2x2 grids, collages, multi-panel/contact sheets, or multiple separate images in one prompt for production styleframes.
- Fast ChatGPT Image 2 production may use **4-request microbatching**: submit up to four separate ChatGPT Image 2 messages/requests in sequence, each message for exactly one standalone 16:9 image for one cut, then download/QC the four independent outputs together. Never combine the four cuts into one prompt, 2x2 grid, collage, contact sheet, or multi-panel output.
- Grok: **I2V/videoization only**, from saved ChatGPT Image 2 frames.
- If ChatGPT Image 2 image production is blocked mid-project, do **not** switch Grok into still-image generation by default. Continue production by using Grok Imagine for I2V/videoization from any approved/saved existing frame, acceptable fallback frame, or other user-approved source frame so the edit can keep moving without a question.
- Do not use Grok to generate still images unless the user explicitly overrides for that job.
- Do not use Kling in the default workflow unless explicitly requested.
- If older wording says “Grok image prompt,” read it as “ChatGPT Image 2 styleframe prompt.”

## Core production rules

- Prefer image-first workflows over text-to-video for character consistency.
- If characters exist, define a fixed reference before scene generation.
- Keep hair, eyes, outfit, and body type fixed across scenes; change expression only.
- Do not put narration text inside Grok/I2V prompts.
- Output copy-paste-ready deliverables, not abstract advice.
- Do not tell the user to "refer to a preset below"; include required style locks directly inside each prompt.
- On revisions, update only the requested scene/track/character scope instead of regenerating everything.

## Default full-package order

When the user asks for a full package, output in this order:

1. Concept summary in 3 lines or less
2. Timeline or scene structure
3. Character JSON
4. Character sheet JSON
5. Scene start-frame JSON
6. Grok/I2V motion prompts
7. BGM JSON
8. Narration/dialogue sheet

## Output formats

### Cut list

Use a table with these columns:

| scene | timecode | visual | narration |
|------|----------|--------|-----------|

### Character reference JSON

```json
{
  "character": "[name]",
  "purpose": "reference sheet - front view",
  "prompt": "full character description with fixed hair, eyes, outfit, neutral pose, plain background, style lock included, 16:9 aspect ratio",
  "negative": "style drift, different character, deformed, extra accessories"
}
```

### Character sheet JSON

```json
{
  "character": "[name]",
  "purpose": "character expression and angle sheet",
  "attach_instruction": "attach [name] reference image as base character",
  "prompt": "same face same hair same outfit across all panels, front view, side profile, back view, close-up neutral, close-up emotion A, close-up emotion B, white background, high consistency",
  "negative": "different character, style change, costume change, chibi"
}
```

### Start-frame JSON

```json
{
  "cut": "C-01",
  "timecode": "00:00-00:05",
  "type": "start_frame",
  "attach": "[none / character / character + character]",
  "prompt": "scene description with camera angle, composition, facial expression, background, lighting, full style lock included, 16:9 aspect ratio"
}
```

### Grok/I2V motion prompts

Write one prompt per cut using concise camera language.

Available movement tags:

- `[SLOW_ZOOM_IN]`
- `[SLOW_ZOOM_OUT]`
- `[PAN_RIGHT]`
- `[TILT_UP]`
- `[TRACKING]`
- `[DOLLY_IN]`
- `[HANDHELD]`
- `[STATIC]`
- `[SLOW_MOTION]`

Example:

```text
[SLOW_ZOOM_IN] gentle forward camera movement, subject remains steady, emotional focus intensifies
```

### BGM JSON

```json
{
  "track": "BGM-01",
  "timecode": "00:00-00:12",
  "duration": "12s",
  "mood": "hopeful cinematic build",
  "suno_style_prompt": "instrumental cinematic ambient with soft piano and subtle strings, emotional but restrained, no vocals",
  "suno_tags": ["instrumental", "cinematic", "ambient", "piano"],
  "volume": "-4dB"
}
```

### Narration/dialogue sheet

```text
00:21 - 화자
"대사 또는 나레이션"
```

## Style locks

Embed the relevant style directly inside prompts:

- Makoto Shinkai: `makoto shinkai anime illustration, cinematic lighting, detailed background, soft atmospheric haze, 16:9 aspect ratio`
- Photoreal: `photorealistic, cinematic color grading, shallow depth of field, natural lighting, 16:9 aspect ratio`
- Ink wash: `traditional korean ink wash painting, sumi-e style, monochrome with subtle color, elegant brushwork, 16:9 aspect ratio`
- Pixar/3D: `pixar 3D animation style, soft subsurface scattering, expressive character design, warm studio lighting, 16:9 aspect ratio`

## Request routing

- "영상 기획" -> ask the 3 start questions if needed, then produce concept + structure
- "씬 나눠줘" -> produce a cut list
- "프롬프트 뽑아줘" -> produce character JSON + ChatGPT Image 2 start-frame JSON + Grok/I2V prompts
- "BGM 짜줘" -> determine track count and output BGM JSON
- "대사 정리해줘" -> output narration/dialogue sheet with timecodes
- "전체 패키지" -> follow the default full-package order exactly

## Revision rules

- "씬 3 바꿔줘" -> replace only scene 3
- "BGM 분위기 바꿔줘" -> update only the target track
- "캐릭터 수정" -> update the character JSON and only the affected scenes


## Typography dataset routing rule

When the task involves typography, subtitles, captions, chapter cards, title cards, lower thirds, keyword cards, final statements, or CapCut text-layer revisions, the editing/typography agent must not design from memory. It must first look for a local typography dataset and selection packet in the active project.

Mandatory order for projects that contain `production/typography_research/`:

1. Read `production/typography_research/TYPOGRAPHY_AGENT_PROTOCOL.md` if present.
2. Load `production/typography_research/typography_reference_dataset_v1.json` or the newest typography reference dataset.
3. Run the project selector if present, for example `python3 tools/select_typography_references.py --project kaia --top 14`, or read the latest file under `production/typography_research/selected/`.
4. State the selected pattern family before editing: opening/final, chapter labels, body captions, keywords, public clarity, motion/QC behavior.
5. Translate design logic from references; do not copy unrelated brand surfaces.
6. Apply in CapCut-first workflow, keeping editable text layers where practical.
7. QC in actual CapCut preview. JSON, contact sheets, or ffmpeg previews alone are not enough.

Hard fail: if a caption overlaps in-scene HUD/UI/text, warning icons, faces, key action, or wraps Korean badly, the typography pass is not complete. Move text timing to a cleaner cut instead of forcing another box onto the same frame.

## CapCut editable-timeline rule

For this user's serious MV/public-contest/institution video work, do not deliver a single flattened ffmpeg-assembled MP4 as the main editable result. ffmpeg is allowed for pre-CapCut QC, normalization checks, contact sheets, proxy previews, ffprobe/blackdetect/freezedetect, and temporary timing slates only. The actual edit must be built or mirrored in a CapCut draft so the user can adjust clips, timing, audio, and text inside CapCut. If a flattened reference render is useful, label it clearly as `QC/proxy/reference`, not as the editable final. Final handoff should include a CapCut project/draft with separate media/text/audio tracks where practical, plus manifests and QC artifacts.

Additional hard check: a CapCut draft is not valid merely because JSON inspection or the timeline view shows clip blocks. It must actually preview/play in CapCut's viewer. If a JSON-injected or externally generated draft shows a black viewer, stalled playback, missing media, or nonfunctional preview, mark it HOLD/DO_NOT_USE and rebuild through CapCut's own import/timeline workflow or another route that is verified by actual CapCut playback.

## Quality bar

- Lead with usable deliverables, not long theory.
- Keep outputs copy-paste ready.
- Be specific enough that the user can move directly into ChatGPT Image 2, Grok I2V, Suno, or CapCut.

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



## Editable CJK subtitle delivery rule

- For Japanese/Korean lyric subtitles, do not rely on a burned-in MP4 as the only deliverable.
- Always preserve editable subtitle sources: timed CSV/SRT/ASS and, when CapCut is part of the workflow, a CapCut draft/project folder with text clips on separate tracks.
- Use CJK-capable fonts for Japanese/Korean text, such as Hiragino, Apple SD Gothic Neo, Noto Sans CJK, or another verified Japanese/Korean font; avoid Latin-only default fonts that can produce tofu or broken glyphs.
- Preferred MV lyric layout for this user's bilingual subtitles: Japanese top line in yellow, Korean bottom line in white, both bottom-centered with black outline/stroke.
- If a subtitle render shows broken Japanese/Korean glyphs, treat it as a font failure, not as an acceptable export; switch to editable CapCut text or a verified CJK font before final delivery.

## Multi-panel sourceframe crop rule

- Do not use 2x2, contact-sheet, grid, collage, or multi-panel generated images as direct sourceframes for MV production.
- Prefer one complete 16:9 sourceframe per cut, generated as a single image, so no crop border, panel gutter, or white margin can enter I2V or final edits.
- If a multi-panel sheet is unavoidable for exploration, every cropped panel must pass a border/gutter QC step before I2V: crop past all white gutters, inspect all four edges at full resolution, and reject if any white frame, panel seam, or leftover background margin remains.
- A crop that contains a white border from the original 2x2 sheet is a failed source asset even if the character/scene looks good.
- Never send a bordered crop to Grok/I2V; regenerate or recrop first.

## I2V crop and identity lock

- For eye-only, partial-face, hand, object, reflection, silhouette, macro, and symbolic source frames, preserve the exact crop and composition. Do not invent a wider shot or reveal a full face/body unless explicitly requested.
- A generated clip that expands an eye close-up into a new full face is a failed asset, even if it is visually attractive. Reject/regenerate it.
- Check identity by face shape, nose bridge, jaw, eye spacing, age impression, hair mass, outfit, and scene role; eye color alone is not enough.
- Repair prompts for fragile close-ups must say: `preserve exact crop`, `do not reveal full face`, `no zoom out`, `no new facial structure`, `no new character`, and restrict motion to iris glint, eyelid micro-movement, hair-tip tremble, reflected light, or background shimmer.

## Calibrated subtitle taste for this user

For the user's MV subtitle orders, preserve the learned bilingual caption feel from the ORG79 project:

- Japanese/Korean lyric subtitles should look like one coherent two-line caption block, not a headline plus footnote.
- Preferred hierarchy: yellow Japanese upper line, white Korean lower line; Korean may be equal or slightly larger in perceived readability.
- Keep both lines compact in the lower safe area, but large enough to read at normal preview distance.
- When increasing size, also widen the vertical gap so black outlines never touch or visually merge.
- Avoid both extremes: no meme/title-sized captions, no tiny annotation captions.
- For CapCut-style normalized text transforms, a good starting ratio is JP size/scale around 8.4/0.69 and KR around 8.8/0.72, with JP y around -0.69 and KR y around -0.83 for 16:9 lower-third bilingual lyrics; tune from there by screenshot, not by abstract font numbers alone.

## Calibrated MV title taste for this user

For this user's MV title orders, prefer title impact that is musically motivated instead of long explanatory title cards. If the user suggests an audible accent, treat it as a serious edit point and verify against audio peaks when available. A strong pattern is a short 3-hit stamp on beat: concept part A / concept part B / full title, then exit before lyric subtitles compete. Keep typography cinematic and restrained: no meme-sized captions, no heavy generic glitch, no long center-card unless explicitly requested. Small motif accents such as a red signal dot, cat-eye/pupil point, ribbon slash, or weak flash are acceptable when tied to the song's visual motifs.

- Spatial title placement rule: before placing title text, identify the subject face/eyes and negative-space zone. For this user, do not let a title cover the character face unless it is intentionally a poster-style graphic frame. Prefer compact title blocks in windows, sky, walls, floor, or other motivated empty zones. If a title crosses the face because it is simply centered, treat that as a failure.
- Authorship rule for titles: do not merely restate the user's concept phrase. Preserve the concept, but coin a title with a point of view. Keep the premise legible while adding interpretation.
- Motif accents must be understandable. Remove decorative dots/slashes if the viewer cannot infer their relation to red signal, cat eye, laser, or rhythm.

- Title subline collision rule: when adding a Korean/translated title subline under a Japanese or English title, treat it like the calibrated bilingual subtitle system: separate vertically, lower its weight, and verify that outlines do not visually merge. Do not mistake a subline collision problem for a center/side placement problem.
- Trend application rule: borrow beat-synced kinetic text, compact high-contrast typography, and short micro-flashes from anime/CapCut/TikTok edits, but reject heavy default glitch/shake and unexplained ornaments.

- Title readability hold rule: a clever 3-hit title still needs a readable final/full-title hold. For this user's MV title work, keep the final title visible for about 1.5s minimum unless the user asks for a subliminal flash.
- Title beat alignment rule: for sharp pop-in/stamp typography, align the visible START/impact frame to the waveform peak, not the segment end. Use peak-as-arrival/end only when there is a deliberate pre-roll animation (fade/scale/swoop) whose motion is meant to resolve on the beat. When CapCut shows peaks near a timecode like 00:04:23, set the text clip/effect impact to that peak and verify against the timeline wave, not abstract timing guesses.
- CapCut timecode rule: CapCut timeline labels are `HH:MM:SS:FF` using the project fps. For a 24fps project, `00:04:23` means 4 + 23/24 = 4.958s, not decimal 4.23s. Always convert visible timecode frames before writing draft_info microsecond timings.
- Title exit rule: when this user asks for a title to disappear with impact, prefer a very short 2–4 frame CapCut text echo/pop/glitch-off at the end of a readable hold, not a long generic fade. The exit should feel like it snaps away on rhythm.
- Finalization rule: when this user accepts an MV version as final, lock the current CapCut draft, export the final MP4, preserve editable project files, and if uploading to YouTube without explicit visibility instruction, choose Unlisted/일부 공개 rather than Public.
- Account routing rule: for music/MV/AI-song uploads, use the Nuzic channel/account (`Nuzic(JiNu Style Ai muisic factory)` / `@Nuzic-m6r`), not the `누저씨ジヌおっさん` account. Verify the visible YouTube Studio channel before selecting a file or publishing.

- YouTube packaging rule: final MV upload is not complete until the title, description, thumbnail, channel/account, visibility, and copyright/processing status are checked. Never treat a bare uploaded MP4 with a filename title and auto-thumbnail as finished.
- YouTube CTR title rule: include the artistic title plus a Korean hook phrase when the audience is Korean/mixed. Prefer curiosity + concept phrasing such as `고양이 뇌지컬로 출근하는 현대인들` over literal file/title-only naming.
- YouTube thumbnail rule: for music/MV uploads, make or select a deliberate 16:9 thumbnail before finalizing. Prefer GPT/image-generation thumbnail or a designed composite, not a crude local text overlay unless it genuinely beats generated options. Thumbnail text must be mobile-readable, 2–4 Korean words max, with strong face/eye/motif contrast.
- Intro lyric timing rule: do not show the first lyric line across an instrumental intro just because the subtitle file starts early. Align the first lyric subtitle to the actual vocal onset/visible mouth or audible syllable.

- Title palette separation rule: title design must not reuse the lyric subtitle identity by default. If lyric subtitles are yellow/white, make titles feel special with a separate palette such as cyan/coral, magenta/cyan, or monochrome/red, tied to the MV motifs.
- Title color continuity rule: when a 3-hit title introduces part A in one color and part B in another color, the final/full title should either use a deliberately new third identity or, preferably for this user, split the typography so part A keeps color A and part B keeps color B. This reads as intentional composition rather than random recoloring.
- Lyric onset rule refinement: for repeated syllables such as `냐냐냐`, align to detected syllable onsets or the audible vocal pattern, not just the nearest big beat. A big instrumental hit can be a title cue but not automatically a lyric cue.


## YouTube / MV publishing packaging calibration for this user

When this user says to upload or finalize a music/MV work, treat the upload as a complete audience-facing package, not a file-transfer task.

Required publishing checklist:

1. **Account routing**
   - Music, Suno, AI song, MV, lyric video, or Nuzic-branded works must be uploaded to `Nuzic(JiNu Style Ai muisic factory)` / `@Nuzic-m6r`.
   - Do not upload these works to `누저씨ジヌおっさん` unless the user explicitly overrides it.
   - Before selecting files or saving, visually/DOM-confirm the active YouTube Studio channel.

2. **Title strategy**
   - Never leave a filename-like title such as `ORG79_final_v24` or only a bare art title if the user is thinking about views.
   - Use a two-layer title: artistic title + Korean hook phrase.
   - Good pattern: `作品タイトル｜한국어 후킹 문구`.
   - Example from accepted correction: `ネコの脳、ヒトの身体｜고양이 뇌지컬로 출근하는 현대인들`.
   - Korean hook should translate the concept into a clickable human situation, not merely explain it. Prefer phrases with everyday tension, curiosity, or identity: “출근하는 현대인들”, “고양이 뇌지컬”, “본능으로 버티는 하루” etc.

3. **Description strategy**
   - The first line should be Korean and hooky, not generic `AI Music Video`.
   - Include the concept in natural Korean, then compact credits.
   - Include searchable tags/keywords but avoid looking spammy.
   - Example structure:
     - Hook sentence in Korean.
     - One-sentence concept summary.
     - Title / Music / MV-Edit credits.
     - 4–6 relevant hashtags.

4. **Thumbnail strategy**
   - A video is not publish-ready without an intentional thumbnail.
   - Do not settle for YouTube auto-thumbnail or crude local text overlay if a GPT/image-generated thumbnail can be better.
   - For this user, when thumbnail quality matters, use GPT image generation as the default first-class thumbnail route.
   - Thumbnail goal is CTR: mobile-readable 2–4 Korean words, strong face/eye/motif, high contrast, clear emotional/concept hook.
   - Use generated-image thumbnails when they deliver a more polished design than frame compositing. Keep the original generated image and copy it into the project/youtube folder and upload staging folder.
   - Avoid “피지컬 낮은” local composite styles: unbalanced typography, boxy amateur overlays, weak spacing, or text that looks pasted on.

5. **Visual/CTR taste for thumbnails**
   - Strong motifs from the MV should drive the thumbnail: eye, red signal, cat brain, train/night rain, cat silhouette, neural circuit.
   - Text should behave like designed poster typography, not subtitle text.
   - Korean headline can be bold and click-oriented; Japanese title can be smaller as prestige/detail.
   - Keep it 16:9 YouTube standard and verify it reads at small size.

6. **Save/verification**
   - After updating title/description/thumbnail, wait until YouTube Studio shows saved state, e.g. `모든 변경사항이 저장되었습니다`.
   - Record final title, thumbnail path, visibility, video link, and account in project state.

Standing lesson from ORG79: the user values creative packaging and CTR thinking. Do not be passive or literal at the publishing stage.

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
