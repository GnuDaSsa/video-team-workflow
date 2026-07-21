---
name: music-video-production-team
description: "Use this skill for a simple agentized music-video production workflow across any song or style. It divides the work into five roles: Music Director (existing `music-director` skill), Planner, Character Creator, Image Creator, and Image-to-Video Producer. Trigger on requests like 뮤직비디오 제작, MV 기획, 영상화, 에이전트화, 기획자, 캐릭터 생성가, 이미지 생성자, 이미지투비디오, GPT 이미지, Grok 영상화, 캐릭터시트, 주인공 검수, 컷리스트."
---

# Music Video Production Team

A general-purpose, reusable agent structure for making music videos. Keep the team simple: five roles, clear handoffs, minimal approval gates.

## First response rule

Start with `[music-video-production-team]` when this skill is active.

## Core idea

The MV workflow is split into these roles:

1. **Music Director** — already exists as `$music-director`; owns song interpretation and musical taste.
2. **Planner** — owns MV concept, story, scene structure, and production plan.
3. **Character Creator** — owns protagonists/recurring characters and character sheets.
4. **Image Creator** — owns GPT image prompts, still frames, and image QA.
5. **Image-to-Video Producer** — owns Grok/I2V prompts, clip generation, motion QA, and edit handoff.

Use these roles for any MV project, not only the current project.

## Non-negotiable tool routing rule

For the user's normal MV production team, this routing is a standing rule:

- **Images / styleframes / character sheets / start frames = ChatGPT image generation in the user's logged-in ChatGPT browser session.**
- **Video generation / image-to-video clips = Grok Imagine only, using the selected ChatGPT-generated image as the input frame.**
- **Do not use Grok for image generation in this workflow** unless the user explicitly overrides the rule for that specific job.
- **Do not start Grok video generation before the image is generated, saved, QA'd, and given an organized filename.**
- **For every new MV/video project, open a new ChatGPT tab/new chat for ChatGPT Image 2 generation.** Do not continue in an old unrelated image-generation thread.
- **Never request 2x2 grids, collages, contact sheets, multi-panel sheets, or multiple images in one ChatGPT Image 2 production prompt.** Generate each production styleframe as a single standalone 16:9 image: one cut, one prompt, one saved file.
- Work sequentially by version/cut when the user asks for sequential execution; do not silently parallelize versions.

## Operating rule

The user wants the agents to operate, not constant questions. For MV production, default to **no-question, one-block execution**: analyze → cut design → image generation → image-to-video → edit → QC → self-contained package. Ask only for login/payment/CAPTCHA/account/sensitive upload/deletion, or if the user explicitly requests a review gate. Otherwise proceed, iterate, prune weak outputs, and do not present failed drafts as final.

## Approval gates

Use only the gates needed by the current project:

1. **Direction approval** — optional; use when concept is ambiguous.
2. **Character approval** — required if a recurring protagonist/character exists.
3. **Character sheet approval** — required before using a character across many scenes.
4. **Look approval** — required after representative generated stills.
5. **Final candidate approval** — required after video candidates are generated.

Do not ask before routine prompt edits, regeneration, candidate pruning, or small scene tweaks.

## Role contracts

### 1. Music Director

Use existing `$music-director` skill when musical interpretation matters.

Owns:
- song mood, hook, rhythm, structure
- lyric-image interpretation
- genre/taste guardrails
- reference-track translation
- music-driven edit notes

Outputs:
- song structure map
- energy curve
- visual rhythm notes
- must-avoid musical/genre drift

### 2. Planner

The Planner is the main MV 기획자.

Owns:
- MV concept
- story or non-story structure
- scene/cut list
- visual motifs
- approval plan
- what each other role must produce

Outputs:
- project brief
- one-line concept
- story spine
- cut list
- scene goals
- production sequence

Planner must decide:
- protagonist or no protagonist
- live-action / 2D / 3D / mixed
- fast-cut / long-take / performance / narrative / montage
- image-first generation strategy

### 3. Character Creator

Use only when the MV has a recurring character, protagonist, mascot, performer, or fictional entity.

Owns:
- character concept candidates
- hero reference prompt
- character revision loop
- character sheet prompt
- consistency rules for scenes

Outputs:
- 2-3 character concepts
- GPT image prompt for first hero reference
- character approval card
- character sheet prompt after approval
- attachment instructions for future scenes

Rules:
- Do not make character-scene batches before the hero is approved.
- Once approved, keep face, hair, body, outfit, prop language, and mood fixed.
- Character scenes should attach the approved hero reference and/or character sheet.

### 4. Image Creator

The Image Creator produces still frames/styleframes, usually with GPT Images.

Owns:
- global visual style lock
- per-scene image prompts
- negative prompts
- image generation batches
- image QA and regeneration notes

Outputs:
- GPT image prompts in English
- negative prompt
- attachment instructions
- pass/fail table for generated stills
- selected stills for video production

Rules:
- 16:9 by default for MV frames.
- For the user's MV pipeline, generate images with ChatGPT/GPT Images in the logged-in ChatGPT browser session by default; Grok is not the image generator.
- For a new project, use a new dedicated ChatGPT tab/new chat for image generation so prompts, downloadable files, and context do not mix with older projects.
- Save ChatGPT-generated stills into the project image folder with ordered, descriptive filenames before handing them to I2V.
- Do not batch multiple cut images into one prompt. If a prompt says “generate exactly 4 separate images,” rewrite it into four separate one-cut prompts before generation.
- Fast ChatGPT Image 2 production may use **4-request microbatching**: submit up to four separate ChatGPT Image 2 messages/requests in sequence, each message for exactly one standalone 16:9 image for one cut, then download/QC those four independent outputs together. This is batching of requests, not a single multi-image prompt.
- Produce image batches only after the Planner's cut logic is clear; avoid creating random cool frames disconnected from the story.
- Use character sheet attachment for scenes containing approved characters.
- Avoid text/logos/watermarks unless explicitly required.
- Preserve the Planner's visual style and the Music Director's taste guardrails.

### 5. Image-to-Video Producer

The Image-to-Video Producer turns selected stills into short clips, usually with Grok or another I2V tool.

Owns:
- image-to-video prompts
- camera motion
- motion intensity
- clip duration
- video QA
- edit handoff

Outputs:
- Grok/I2V prompts in English
- camera tags or movement instructions
- per-clip duration
- failure criteria and regeneration notes
- final clip order / handoff timeline

Rules:
- For the user's MV pipeline, use **Grok Imagine for image-to-video only**. The input frame should come from the Image Creator's ChatGPT-generated stills.
- Do not use Grok to invent replacement images when the task is I2V; if the wrong mode is active, switch to video/I2V and upload the correct still.
- Preserve the input image identity and composition.
- For music videos, motion should follow the beat and section energy.
- Do not over-morph characters or environments.
- Keep clips short if the song needs fast cutting.




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

## Persistent user feedback rules

- Shared reference: `references/mv-team-standing-memory-low-signal-and-hito-neko.md`

The user's project feedback is cumulative team memory. When the user says a production mistake happened, promote it into future defaults for the MV team instead of treating it as a one-off note. In later MV projects, carry these rules unless the user explicitly overrides them.

Current standing rules learned from the `mv-low-signal` workflow:

0. **Tool routing is fixed for MV production.** Image/styleframe generation belongs to ChatGPT/GPT Images in the logged-in ChatGPT browser session. Grok is reserved for image-to-video generation from those saved stills. Do not let Grok become the image generator unless the user explicitly says so for that job.
1. **Prevent missing media by default.** Deliver self-contained packages: final master MP4, clean/no-subtitle master when relevant, `segments/`, `audio/`, `edit_decision_list.csv`, review contact sheet, key review frames, and notes. CapCut drafts should reference draft-local or package-local media, not temporary downloads/cache.
2. **Do not arbitrarily limit scene count.** Decide cut count from song length, beat density, lyric sections, and story needs. For a full ~100s MV, 35 cuts may be too few; prefer enough segments to make the edit feel dynamic, while preserving longer story-anchor shots where needed.
3. **Convert liked shots into structural anchors.** If the user identifies a shot as especially good, reuse its underlying creative principle as a story beat/chorus anchor/visual motif, not just a decorative insert.
4. **Avoid unwanted recurring motifs permanently.** If the user rejects a device or motif, add it to `must avoid` for future prompts and QA. Example from `mv-low-signal`: no earpiece, earbuds, headset, cable-to-ear device, needless lip-sync/talking-mouth shots.
5. **Story must be legible.** The Planner must state a one-sentence premise and cause→discovery→pursuit/turn→resolution spine before batch production. Avoid making a montage of disconnected cool shots.
6. **Reduce duplicate scenes.** Repeated source material must have a changed narrative role or visual treatment. Use contact sheets to catch repeated impressions before claiming completion.
7. **Review before handoff.** Always create a review contact sheet or equivalent, inspect it for missing anchors, repeated scenes, unwanted motifs, and unclear story, then write what passed/failed.

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

## Standard workflow

1. **Music Director** interprets the song and taste.
2. **Planner** creates the project brief and cut structure.
3. If needed, **Character Creator** creates protagonist candidates and gets approval.
4. **Character Creator** creates the character sheet and gets approval.
5. **Image Creator** creates styleframes/stills in batches.
6. User approves the overall look.
7. **Image-to-Video Producer** creates short clips from selected stills.
8. **Image-to-Video Producer** prepares final clip order and edit handoff.
9. User approves final candidates.

## Project brief template

```markdown
## MV Project Brief
- Song:
- Music Director notes:
- Timed lyrics / subtitle plan:
- Visual format:
- Target length:
- Cut rhythm:
- Protagonist strategy:
- Core story / non-story concept:
- Visual motifs:
- Must include:
- Must avoid:
- Persistent user feedback applied:
- Self-contained media/package plan:
- Tool chain:
- Approval gates:
- Review/contact sheet plan:
- Clean master / subtitle master plan:
```

## Handoff format between roles

### Planner → Character Creator

```markdown
Character need:
- Role in MV:
- Personality / aura:
- Visual constraints:
- Must avoid:
- Approval gate:
```

### Planner → Image Creator

```markdown
Scene package:
- Cut ID:
- Timecode:
- Scene purpose:
- Subject:
- Mood:
- Required attachments:
- Must avoid:
```

### Image Creator → Image-to-Video Producer

```markdown
Selected still:
- Cut ID:
- Image/link/file:
- Preserve:
- Animate:
- Avoid:
- Duration:
```

## Web operation policy

When browser control is available and the user has authorized automation:
- operate GPT Images, Grok, Gemini, or other tools directly;
- do not ask before routine generations;
- stop only for login, payment, captcha, file permissions, safety, or approval gates;
- summarize candidates with links/screenshots/file names.

## Language rules

- Planning and user-facing review: Korean.
- Image prompts: English.
- Image-to-video prompts: English.
- Tables may use Korean labels.

Current standing rules learned from the `hito body / neko brain` Suno MV review:

11. **Do not output slide-show proxies as final.** A local still-frame Ken Burns render is only an internal placeholder and must not be called an MV final.
12. **Final/review timeline must contain videoized clips only.** Raw ChatGPT images are I2V inputs, never edit assets.
13. **Beat fit is mandatory.** If cuts do not visibly hit the song pulse, the render fails QC.
14. **Avoid forced story-grid assembly.** The MV must feel composed around the song, not squeezed into a prebuilt template.
15. **Character/style consistency must not justify repeated frames.** Keep Mika/Kuro consistent through character sheets, but generate distinct scenes per cut.
16. **Default prototype duration is around 60 seconds for iterative review** before committing to longer 85–100s versions.


## Additional hard rule: no false microcutting

A cut must be felt. Do not split one visual moment into multiple cuts unless there is a real musical, narrative, action, or transition reason. If three seconds read better as one held shot, hold it. Different crops, small framing changes, or repeated Grok outputs are not valid cut structure.

If an I2V output visually collapses into the same scene as another cut, or does not match the intended source image, reject it and regenerate/merge; do not treat it as complete media.
