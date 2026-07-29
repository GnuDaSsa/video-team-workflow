# Optional role split

For bigger jobs the work can be walked as named roles. These are responsibilities, not agents to spawn — one agent plays them in sequence unless the user approves otherwise.

## Core idea

The MV workflow is split into these roles:

1. **Planner** — owns MV concept, story, scene structure, and production plan. Direction is settled before a track exists.
2. **Music Director** — already exists as `$music-director`; owns song generation, interpretation, and musical taste. Runs after direction, and the cut map is built from the locked result.
3. **Character Creator** — owns protagonists/recurring characters and character sheets.
4. **Image Creator** — owns GPT image prompts, still frames, and image QA.
5. **Image-to-Video Producer** — owns Seedance/I2V prompts, clip generation, motion QA, and edit handoff.

Use these roles for any MV project, not only the current project.

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
- For recurring-character projects, write the sheet usage into the cut prompt/manifest. If the generator route cannot verify attachment/reference use, stop that cut as `BLOCKED_CHARACTER_SHEET_ATTACHMENT_NOT_VERIFIED`; do not continue from memory-only descriptions.

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
- For the user's MV pipeline, generate images with Codex `imagegen` / built-in `image_gen` through the file-backed non-GUI route by default; Grok is not the image generator.
- Do not open or activate a browser for still-image generation. Save the returned image directly into the project artifact folder with an ordered, descriptive filename before handing it to I2V.
- Save Codex imagegen stills into the project image folder with ordered, descriptive filenames before handing them to I2V.
- Do not batch multiple cut images into one prompt. If a prompt says “generate exactly 4 separate images,” rewrite it into four separate one-cut prompts before generation.
- Fast Codex imagegen production may use up to four separate imagegen calls in sequence, each call for exactly one standalone image for one cut, then QC those four independent outputs together. This is batching of requests, not a single multi-image prompt.
- Produce image batches only after the Planner's cut logic is clear; avoid creating random cool frames disconnected from the story.
- Use character sheet attachment for scenes containing approved characters.
- Avoid text/logos/watermarks unless explicitly required.
- Preserve the Planner's visual style and the Music Director's taste guardrails.

#### GPT-5.6 Sol prompt-authoring routing — standing Image Creator rule

For work inside `/Users/gnudas/Documents/Codex/video-team-runtime`, non-character image prompts and Seedance final prompts are authored through the runtime-owned `gpt-5.6-sol` bridge defined in the canonical project `AGENTS.md` §2. Use reasoning effort `high`, structured block specs, and Sol prompt-pack provenance. Claude/browser prompt authorship is retired from the active route.

Character/model-sheet prompts remain owned by the Character Creator and character-sheet standard. They do not enter the Sol bridge. Codex imagegen remains the still-image executor after the prompt pack and required character references are ready.

The production route is: Planner beat + approved references + structured block spec -> GPT-5.6 Sol prompt pack -> Codex imagegen -> local save -> image QC -> provider-specific I2V handoff. If Sol cannot run because Codex is outdated, stop as `BLOCKED_SOL_CODEX_UPGRADE_REQUIRED`; do not fall back to Claude or an older model. If imagegen cannot verify an attached character sheet/reference, record `BLOCKED_CHARACTER_SHEET_ATTACHMENT_NOT_VERIFIED` or `BLOCKED_IMAGEGEN_EDIT_FAILED`.

Fable/modern fairy-tale animation prompts still require symbolic object logic, clear emotional action, foreground/midground/background story function, preserved character identity, strict no-text/no-logo/no-duplicate-person negatives, and one standalone image only.

### 5. Image-to-Video Producer

The Image-to-Video Producer turns selected stills into short clips. Default provider is **Seedance**; Grok only when the user names it.

Owns:
- image-to-video prompts
- camera motion
- motion intensity
- clip duration
- video QA
- edit handoff

Outputs:
- Seedance/I2V prompts in English
- camera tags or movement instructions
- per-clip duration
- failure criteria and regeneration notes
- final clip order / handoff timeline

Rules:
- For the user's MV pipeline, **default I2V is Seedance** via `seedance-prompt-en` (Chrome Runway board). Grok Imagine is used only when the user explicitly names Grok for that job. The input frame comes from the Image Creator's Codex imagegen stills.
- Do not let any I2V tool invent replacement images; if the wrong mode is active, switch to video/I2V and upload the correct still.
- Preserve the input image identity and composition.
- For music videos, motion should follow the beat and section energy.
- Do not over-morph characters or environments.
- Keep clips short if the song needs fast cutting.

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

## Approval gates

Use only the gates needed by the current project:

1. **Direction approval** — optional; use when concept is ambiguous.
2. **Character approval** — required if a recurring protagonist/character exists.
3. **Character sheet approval** — required before using a character across many scenes.
4. **Look approval** — required after representative generated stills.
5. **Final candidate approval** — required after video candidates are generated.

Do not ask before routine prompt edits, regeneration, candidate pruning, or small scene tweaks.

## Project brief template

```markdown

---

# Extended contracts (larger productions)

A finer split than the five core roles, for jobs that need one. Still responsibilities, not agents to spawn.

## Executive Producer / Showrunner
Owns concept, scope, continuity, and approval gates. Must keep a project brief and next-action status.

## Song Analyst
Owns music structure, beat density, lyric-image mapping, and section-specific cut speed.

## Research / Brand Context Agent
Owns factual context, cultural care, references-as-variables, and do-not-show lists.

## Character Director
Owns recurring-character identity, hero approval, character sheets, and attachment rules.

## Art Director / Image Prompt Agent
Owns GPT image prompts, global style locks, negative prompts, and still-frame batch planning.

Standing tool rule for the user's MV team:
- Generate MV stills, start frames, character references, and character sheets with Codex `imagegen` / built-in `image_gen` through the file-backed non-GUI route. Do not open or activate a browser for this step.
- Do not use Grok as the image generator in the default MV workflow.
- Save every approved image with an ordered, descriptive filename before handing it to Motion/I2V.

## Image QA Agent
Owns pass/fail selection, visual drift diagnosis, and regeneration deltas.

## Motion Director / I2V Prompt Agent
Owns Grok/Kling/Runway/Veo image-to-video prompts, camera motion, and clip failure criteria.

Standing tool rule for the user's MV team:
- Use Grok Imagine for image-to-video only, fed by the selected ChatGPT-generated still frame.
- If Grok opens in image mode or produces an image, switch/retry as video/I2V rather than accepting a Grok-generated replacement image.
- Keep version/cut production sequential when requested; do not parallelize versions without explicit instruction.

## Editor / Post Supervisor
Owns edit decision list, beat timing, subtitles, transitions, final timeline, and handoff.


## Persistent Feedback Memory
All roles must treat user feedback as durable production memory. If the user calls out a recurring failure, update future `must include`, `must avoid`, QA checks, and handoff requirements. The Executive Producer / Showrunner is responsible for carrying these notes into the next project brief.

Current non-negotiable routing memory:
- **Images = ChatGPT/GPT Images. Videos/I2V = Grok.**
- Apply this to the normal MV production team and image agent by default, not only to `mv-low-signal`.

## Music Director lyric/subtitle handoff
The Song Analyst / Music Director should provide a timed lyric and section map when lyrics are available, including subtitle priority (`none`, `low`, `medium`, `high`) and visual interpretation notes. The Editor / Post Supervisor must create both clean and subtitle-aware deliverables when subtitles are requested or useful.

## Editor / Post Supervisor additional contract
- Prevent missing media through self-contained packages and draft-local media references.
- Maintain an EDL and review contact sheet.
- Check for repeated visual impressions, missing user-approved anchor shots, unwanted motifs, and unclear story before handoff.
- If subtitles are part of the project, output SRT/ASS/CapCut text CSV plus a clean master and a subtitle master.

---

# MV Project Brief Template

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
- Current status:
- Next action:
```
