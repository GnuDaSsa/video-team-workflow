---
title: Seedance Feature Playbook
created: 2026-05-23
updated: 2026-05-23
type: concept
tags: [multimodal, video-production, product, tool-use]
sources:
  - raw/articles/seedance-features-20260523/runway-seedance-help.md
  - raw/articles/seedance-features-20260523/seedance2-hk-image-to-video.md
  - raw/articles/seedance-features-20260523/seedance2-tech-image-input.md
  - raw/articles/seedance-features-20260523/first-last-frame-guide.md
  - raw/articles/seedance-features-20260523/seedance2pro-image-to-video.md
  - raw/articles/seedance-features-20260523/seedanceprompts-storyboard-grid.md
  - raw/articles/seedance-features-20260523/nemovideo-storyboard-workflow.md
  - raw/articles/seedance-features-20260523/picasso-camera-control.md
  - raw/articles/seedance-features-20260523/wmhub-motion-continuity.md
  - raw/articles/seedance-features-20260523/seedance-tv-tutorial.md
  - raw/articles/seedance-features-20260523/videoai-camera-prompts.md
  - raw/articles/seedance-features-20260523/seedance2-so-camera-guide.md
  - raw/articles/seedance-features-20260523/seedanceai-video-extension.md
  - raw/articles/seedance-features-20260523/promeai-edit-extend-repair.md
  - raw/articles/seedance-features-20260523/youtube-storyboard-feature.md
  - raw/articles/seedance-features-20260523/youtube-extension-process.md
confidence: medium
contested: false
contradictions: []
---

# Seedance Feature Playbook

## Scope

This page is a feature-selection layer for Seedance/Runway work. [[seedance-prompting-knowledge]] covers prompt structure; this page covers which Seedance-style capability to reach for: first/last frame control, storyboard/conti grids, multi-scene prompts, camera-control prompting, continuation/extension, and repair/replace workflows. It intentionally does not touch any live video project; it is wiki-only research compiled from 16 web/YouTube sources captured under `raw/articles/seedance-features-20260523/`.

Many sources are third-party product/SEO pages rather than official docs, so this page uses `confidence: medium`. Treat claims as prompt/workflow heuristics unless verified in the actual Runway UI.^[raw/articles/seedance-features-20260523/runway-seedance-help.md, raw/articles/seedance-features-20260523/seedance2-hk-image-to-video.md, raw/articles/seedance-features-20260523/youtube-storyboard-feature.md]

## Feature map

| Need | Feature / method | How to prompt or operate | When to avoid |
|---|---|---|---|
| Lock beginning and ending composition | First-frame / last-frame image-to-video | Provide a start image and an end image; say what must transform between them; specify continuity constraints. | Avoid if the middle action must introduce many unrelated locations/characters. |
| Plan multiple beats from a single concept | Storyboard / conti grid | Use a 3x3 or numbered storyboard grid as an input/reference; prompt ordered beat cells and camera/action per cell. | Avoid when identity consistency matters more than action staging unless each cell is visually consistent. |
| Build a 10–20s sequence | Multi-shot prompt / multi-scene storyboard | State duration, shot count, aspect, then enumerate `Shot 1..N` with camera/action verbs. | Avoid vague “cinematic montage” without ordered beats. |
| Add cinematic movement | Camera-control prompt | Use explicit dolly, tracking, orbit, handheld, pan, tilt, push-in, pull-back, rack-focus language. | Avoid stacking incompatible camera moves in a short shot. |
| Continue a good generated clip | Video extension / continuation | Use the previous clip or last frame as anchor; ask to extend forward/backward while preserving spatial/visual continuity. | Avoid if the prior clip already drifted off-identity; extension will anchor the drift. |
| Repair one section | Replace / repair / localized regeneration | Keep locked good sections, replace the defective beat/segment with a constrained prompt. | Avoid if the defect is global identity/reference mismatch; regenerate earlier. |
| Preserve product/character continuity | Multi-reference role assignment | Number references and give each one a single job: identity, setting, prop/motif, final target. | Avoid letting a background reference overwrite the character identity. |

## First/last-frame control

First/last frame methods are useful when the user needs a specific visual start and a specific visual destination. The prompt should not merely say “move from Image 1 to Image 2”; it should specify the causal transition: who moves, what changes, what stays locked, and what the camera does during the transformation. This helps avoid the model collapsing the entire clip into either the start or end frame.^[raw/articles/seedance-features-20260523/first-last-frame-guide.md, raw/articles/seedance-features-20260523/seedance2pro-image-to-video.md, raw/articles/seedance-features-20260523/seedance2-tech-image-input.md]

Recommended template:

```text
First/last-frame I2V. Image 1 is the opening frame; Image 2 is the final frame. Preserve [identity/costume/object]. Over {duration}s, [subject] performs [action] causing [visual transition]. Camera: [one primary movement]. Do not jump directly to Image 2; show intermediate motion and continuity.
```

For MV work, this is best for motif transformations, emotional reveal shots, or clear “leaves here → arrives there” transitions. It is less useful for dense action montages unless paired with a storyboard grid or explicit shots.

## Storyboard / conti grid

Storyboard workflows use a grid or ordered cells as visual beat anchors. The useful idea is not “one image becomes a video”; it is “each cell is a beat, and the prompt names the beat order.” The prompt should say whether the storyboard is a visual plan/reference rather than a literal split-screen output. The `seedanceprompts` and storyboard workflow sources emphasize cohesive 10–20 second sequences from storyboard-style references.^[raw/articles/seedance-features-20260523/seedanceprompts-storyboard-grid.md, raw/articles/seedance-features-20260523/nemovideo-storyboard-workflow.md, raw/articles/seedance-features-20260523/youtube-storyboard-feature.md]

Recommended template:

```text
Use the storyboard grid as a beat plan, not as an on-screen collage. Read cells left-to-right, top-to-bottom. Create a {duration}s cinematic sequence with {N} shots. Shot 1 uses cell 1: [action/camera]. Shot 2 uses cell 2: [action/camera] ... Maintain the same character identity and palette across all shots. Do not show grid borders or panels.
```

This maps well to Korean “콘티”: Planner/Geto can make a block-level conti grid or textual conti, then Toji can turn it into a Seedance prompt. It also gives Sukuna/Image a clearer target: generate reference images as storyboard beats, not random pretty stills.

## Camera-control prompting

Camera movement sources converge on explicit camera verbs: `slow dolly in`, `tracking shot`, `handheld follow`, `orbit`, `pan`, `tilt`, `push-in`, `pull-back`, `rack focus`, `low-angle reveal`, `top-down drift`. To exploit Seedance’s dynamic strength, every non-static block should have one primary camera move plus one subject/action verb. Too many camera moves in one short shot can fight each other.^[raw/articles/seedance-features-20260523/picasso-camera-control.md, raw/articles/seedance-features-20260523/videoai-camera-prompts.md, raw/articles/seedance-features-20260523/seedance2-so-camera-guide.md]

Use this decision table:

| Scene type | Camera verbs | Motion budget |
|---|---|---|
| Face/emotion close-up | locked close-up, slow dolly-in, rack focus, subtle handheld | micro-motion |
| Run/action | side tracking, rear tracking, handheld chase, whip-pan transition | kinetic |
| Motif/object macro | macro push-in, orbit, rack focus, particle drift | controlled macro |
| Environment reveal | pull-back, crane-up, orbit reveal, parallax pan | broad reveal |
| Impact/chorus | handheld surge, snap zoom only if stylized, fast orbit, motion streak | impact burst |

## Video extension / continuation

Video extension is best treated as a continuity tool. The previous clip’s last frame becomes the spatial anchor for the next clip. Prompt the continuation as “extend forward from the final frame” and specify what remains unchanged: character, camera direction, lighting, palette, location geometry. This is powerful for building longer sequences from successful clips, but dangerous if the previous clip has identity drift: extension will often inherit the drift.^[raw/articles/seedance-features-20260523/seedanceai-video-extension.md, raw/articles/seedance-features-20260523/promeai-edit-extend-repair.md, raw/articles/seedance-features-20260523/youtube-extension-process.md]

Recommended use in video-team workflow:

1. Seedance QC marks a clip as visually good but too short or ending before the beat resolves.
2. Toji uses the clip/last frame as an extension anchor.
3. Prompt: `Continue forward from the final frame of the provided clip. Preserve [identity, camera direction, lighting, location]. Over the next {seconds}, [new action]. Do not reset location or introduce a new face.`
4. QC must compare the extension seam, not only the new clip in isolation.

## Repair / replace

Repair/replace workflows are for local defects: a hand glitch, short wrong beat, bad transition, or a section that needs continuation. They are not a cure for bad source references or global identity mismatch. If the start identity is wrong, repair later segments will keep fighting the wrong anchor.^[raw/articles/seedance-features-20260523/promeai-edit-extend-repair.md, raw/articles/seedance-features-20260523/wmhub-motion-continuity.md]

Use:

```text
Keep the first [x] seconds unchanged. Replace only the [defective beat] with [corrected action]. Preserve the same character identity, camera direction, lighting, and background geometry. Do not reset to a new scene.
```

## Feature retrieval logic for video-team lanes

Planner/Geto and Toji should choose a Seedance method before writing the final prompt:

- `motif transforms into destination` → first/last-frame or multi-reference transition.
- `several beats in one music block` → storyboard/conti grid or numbered multi-shot prompt.
- `static images feel dead` → camera-control prompt with motion budget.
- `good clip but too short` → extension/continuation.
- `one beat broken, rest good` → repair/replace.
- `character consistency failing` → multi-reference identity anchor + fewer scene changes, not extension.
- `Runway asset contamination` → do not treat as prompt problem; fix upload route/project isolation first.

The selected method should be written into `prompt_rules_used` or the block prompt header, e.g.:

```text
Method: storyboard-conti multi-shot + camera-control. Not a static I2V hold.
```

## Related

- [[seedance-prompting-knowledge]]
- [[video-team-seed-system]]
- [[video-project-seed-template]]
