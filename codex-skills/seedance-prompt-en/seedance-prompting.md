# Seedance prompting branch

This branch authors the visual prompt and the ordered multi-reference package. It does not click Runway, monitor cards, download files, or claim production completion.
For multi-agent Creative authoring with explicit role separation, prefer `$seedance-creative-prompt-team` (`~/.codex/skills/seedance-creative-prompt-team/SKILL.md`). This file remains the single-agent Creative/Standard branch.
Standing defaults: **multi-reference × 15s**, Creative Mode open after identity lock, **no BGM** (diegetic/room only), naturalism-first, medium-aware texture. Shorter duration, BGM, or dialogue only with an explicit per-shot override.

## Prompt-authoring isolation gate — 2026-07-26

Prompt authoring is a single foreground, sequential operation. It may inspect approved local source files, write prompt packages, and call the runtime-owned prompt-authoring bridge, but it must not open or activate Chrome/Safari/Runway or use Computer Use, `osascript`, AppleScript, `open -a`, native file choosers, queue observers, launchd jobs, or browser automation. Do not run prompt authoring concurrently with production UI work or a background scheduler. A browser/queue handoff begins only after the prompt package and critic verdict are complete.

The six Creative roles are reasoning passes, not automatic parallel workers. If the user explicitly approves an extra worker, record the named role, purpose, and output first; never infer approval from a request to make a Creative prompt.

## Inputs and output

Read the story/scene brief, the approved source-image manifest, and the relevant character sheet(s). Before writing, choose `Creative` or `Standard` mode and record the choice.
Record look medium (`live-action` / `2D/stylized` / `mixed`) with the mode choice.

Produce a handoff package containing the shared-contract schema:

```text
Scene ID:
Mode: Creative | Standard
Look medium: live-action | 2D/stylized | mixed
Prompt file:
Visual prompt:
Ordered references:
  Image1 = ...
  Image2 = ...
  ImageN = character sheet/identity crop when a corresponding character appears
Character-sheet gate: required | not applicable
Naturalism / texture notes:
Expected duration/audio/settings: 15s multi-ref; no BGM; diegetic/room only; ...
Exit composition / next-scene handoff:
Source root and exact file paths:
```

The prompt must remain visual-only and within Runway's visible character limit. Do not include captions, narration, contest copy, hidden metadata, source provenance, folder/QC language, or image-generation model names.
Default settings line unless overridden: `15s multi-ref; no BGM; diegetic/room only`.

## Reference-role design

- All Seedance jobs use multi-reference. Scene references are anchors for environment, action, texture, or prop; they are not automatically forced into a literal beginning/middle/end interpolation.
- Put environment/action anchors first. Put the relevant approved character sheet or identity crop in the explicit role position required by the scene package, and name it in the role map.
- A character sheet is mandatory whenever that character appears, even if the scene image already contains the same character.
- For every new dependent prompt, re-check the actual sheet path and identity crop against the approved manifest. A remembered identity description is insufficient.
- After every five image/prompt packages, refresh the relevant sheet context as an auxiliary review step; the per-generation attachment gate remains mandatory.

### 2D/stylized reference architecture

When the source reference is 2D, anime, manga, picture-book, or cel-shaded, compile the prompt as four blocks:

```text
STYLE LOCK   = immutable medium, linework, fill/shading method, palette behavior, and rendering rules
CONTINUITY   = immutable character design, proportions, costume/props, palette, geography, and world rules
DIRECTION    = immutable camera language, pacing grammar, and sound/impact cue grammar
SHOT         = the only variable block: one unique physical beat for this shot
```

Keep `STYLE LOCK`, `CONTINUITY`, and `DIRECTION` stable across the block. Change only `SHOT` per image/clip. Do not let a new shot silently change the medium, character design, world geography, camera grammar, or sound language. If a shot needs a new direction or a different medium, open a new style-lock sequence rather than mutating one existing sequence.

## Standard mode

Use Standard when identity, crop, product geometry, spatial continuity, or a fragile close-up is the primary risk. Write in this order:

1. visible premise and mood;
2. ordered `@ImageN` roles;
3. one dominant camera move and subject action;
4. 15 second motion arc and usable exit (default; shorter only if overridden);
5. essential identity/crop/prop locks;
6. short role-specific safety tail.

Describe physical cause → contact → response. Do not fill the prompt with generic negative lists.

## Creative Seedance Mode

Use Creative when the user asks for creative, experimental, dreamlike, transformative, unexpected, or bold transitions, or when the scene benefits from discovery rather than literal interpolation. This mode is the preferred default for this project.

### Creative priorities

1. Start with a visible premise and a camera situation, not a stack of style adjectives.
2. Choose one primary camera family: through-aperture/reveal, mounted-object, handheld intimate track, dolly/pan/orbit, bullet-time, static-frame active subject, POV/FPV, or deliberate montage.
3. State the subject's motion state and allow one motivated camera evolution.
4. Add 2–4 physical motion layers such as smoke, steam, fabric, reflections, foreground occlusion, parallax, dust, particles, vibration, or focus breathing.
5. Build calm → discovery → transformation/escalation → aftermath only when the shot needs that arc.
6. End on a clear exit composition that hands off to the next scene.
7. Keep the card at 15s multi-ref with no BGM unless explicitly overridden.
8. Naturalism first; apply live-action texture stability or 2D medium-true material.

For 2D/stylized references, replace the generic creative assembly with the four-block architecture above and keep one unique beat in `SHOT`; use the fixed direction grammar for the camera and pacing.

### Creative reference freedom

References establish identity, environment, texture, or a key prop. They are anchors, not cages. Do not force incompatible references to become literal start/middle/end frames. Invent the in-between motion and exit when the brief calls for it, while preserving the approved character sheet's face silhouette, hair mass, age impression, costume, and prop handling.
For live-action/photoreal packages, also protect texture naturalness (stable materials; no plastic/waxy/crawling texture). For 2D/stylized, keep medium-true material and do not force photoreal pores.

### Creative handoff check

- concrete visual idea, not mood-only wording;
- all required scene and character-sheet refs listed in visible order;
- camera has room to discover or transform;
- action has a physical cause and visible response;
- 2–4 motivated motion layers;
- no generic negative wall;
- final composition and next-scene handoff are clear;
- default 15s multi-ref and no-BGM audio policy are recorded;
- naturalism/texture notes match the look medium.

## Current continuation package

The next prepared cursor after the approved S01 image 1–5 package is:

```text
Scene: S01-06_FIRE_TO_TORCH
Mode: Creative
Image1: modern campfire extreme close-up, flame dominant on screen-right
Image2: Nam torch-running source frame
Image3: Nam approved identity crop
Character-sheet gate: required and must be visibly verified
Prompt package: SEEDANCE_CREATIVE_MULTIREF_S01_06_FIRE_TO_TORCH_20250725.md
```

The scene package already exists in the project lane. The production branch must attach Image1 → Image2 → Image3 in that order, verify the visible thumbnails, paste the supplied prompt, and perform the normal preflight before one Generate.
