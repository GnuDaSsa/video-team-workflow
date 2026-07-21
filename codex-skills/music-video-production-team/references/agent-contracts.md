# Agent contracts

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
- Generate MV stills, start frames, character references, and character sheets with ChatGPT/GPT Images in the user's logged-in ChatGPT browser session.
- Do not use Grok as the image generator in the default MV workflow.
- Save every approved ChatGPT image with an ordered, descriptive filename before handing it to Motion/I2V.

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
