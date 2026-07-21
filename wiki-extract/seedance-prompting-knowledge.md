---
title: Seedance Prompting Knowledge
created: 2026-05-23
updated: 2026-06-12
type: concept
tags: [video, video-production, workflow, multimodal]
sources:
  - raw/articles/seedance-prompting-20260523/seedance2-ai-guide.md
  - raw/articles/seedance-prompting-20260523/seedance2ai-io-prompt-guide.md
  - raw/articles/seedance-prompting-20260523/seedance-tv-prompt-guide.md
  - raw/articles/seedance-prompting-20260523/synclip-seedance-guide.md
  - raw/articles/seedance-prompting-20260523/invideo-seedance-guide.md
  - raw/articles/seedance-prompting-20260523/rundiffusion-seedance-guide.md
  - raw/articles/seedance-prompting-20260523/soprompts-seedance-guide.md
  - raw/articles/seedance-prompting-20260523/seedance2-tech-docs.md
  - raw/articles/seedance-prompting-20260523/seedance2-app-docs.md
  - raw/articles/seedance-prompting-20260523/heymarmot-seedance-guide.md
  - raw/articles/seedance-prompting-20260523/higgsfield-seedance-guide.md
  - raw/articles/seedance-prompting-20260523/runway-seedance-help.md
  - raw/articles/seedance-prompting-20260523/mattpaige-substack-seedance.md
  - raw/articles/seedance-prompting-20260523/youtube-elevenlabs-multishot.md
  - raw/articles/seedance-prompting-20260523/youtube-dan-kieft-course.md
  - raw/articles/seedance-prompting-20260523/youtube-tao-prompts-filmmaking.md
  - raw/articles/seedance-prompting-20260523/youtube-deepwhite-consistency.md
  - raw/articles/scenic-sh-seedance-prompt-gallery-threads-20260525.md
confidence: medium
contested: false
contradictions: []
---

# Seedance Prompting Knowledge

## Scope

This page compiles web articles, docs, threads/search results, and YouTube transcripts about Seedance 2.0 / Runway Seedance prompting into production rules for the Codex video-team workflow. It is an execution companion to [[video-team-seed-system]] and should be consulted before Planner/Toji write or revise `seedance_prompt` text.

The source set intentionally includes 10+ items: Seedance guide sites, Runway help, creator prompt libraries, a Substack prompt essay, and YouTube courses/tutorials. Some sources are unofficial and promotional, so this page treats repeated patterns as stronger than isolated claims.^[raw/articles/seedance-prompting-20260523/seedance2-ai-guide.md, raw/articles/seedance-prompting-20260523/seedance2ai-io-prompt-guide.md, raw/articles/seedance-prompting-20260523/seedance-tv-prompt-guide.md, raw/articles/seedance-prompting-20260523/synclip-seedance-guide.md, raw/articles/seedance-prompting-20260523/invideo-seedance-guide.md, raw/articles/seedance-prompting-20260523/rundiffusion-seedance-guide.md, raw/articles/seedance-prompting-20260523/soprompts-seedance-guide.md, raw/articles/seedance-prompting-20260523/seedance2-tech-docs.md, raw/articles/seedance-prompting-20260523/seedance2-app-docs.md, raw/articles/seedance-prompting-20260523/heymarmot-seedance-guide.md, raw/articles/seedance-prompting-20260523/higgsfield-seedance-guide.md, raw/articles/seedance-prompting-20260523/runway-seedance-help.md, raw/articles/seedance-prompting-20260523/mattpaige-substack-seedance.md, raw/articles/seedance-prompting-20260523/youtube-elevenlabs-multishot.md, raw/articles/seedance-prompting-20260523/youtube-dan-kieft-course.md, raw/articles/seedance-prompting-20260523/youtube-tao-prompts-filmmaking.md, raw/articles/seedance-prompting-20260523/youtube-deepwhite-consistency.md]

## Core formula

Strong Seedance prompts are concrete, not adjective piles. The recurring formula is:

`Shot structure + Subject + Environment + Action + Camera movement + Visual style + Reference mapping + Constraints`.

For simple shots, `subject + environment + action` is the minimum viable core; production prompts then add camera movement, lighting/style, reference roles, duration/aspect, and safety constraints. Avoid vague requests like “cinematic high quality video” without a visible action. Describe what the viewer sees.^[raw/articles/seedance-prompting-20260523/synclip-seedance-guide.md, raw/articles/seedance-prompting-20260523/seedance2-app-docs.md]

## Multi-reference rule

Multi-reference prompts must explicitly number images and assign each image a role. Use phrasing like:

- `Image 1 controls heroine identity and costume.`
- `Image 2 controls environment / room / vista.`
- `Image 3 controls object or motif.`
- `Use images in this exact visible order: Image 1 → Image 2 → Image 3.`

Do not upload references and assume the model infers what to preserve. A common pattern across guides is to say “maintain X from Image 1” and “reference image N for Y.” When an image controls character identity, preserve hairstyle, clothing, facial structure, proportions, and accessories; when it controls location, do not let it overwrite identity. Each reference should have one primary job where possible.^[raw/articles/seedance-prompting-20260523/synclip-seedance-guide.md, raw/articles/seedance-prompting-20260523/higgsfield-seedance-guide.md, raw/articles/seedance-prompting-20260523/youtube-deepwhite-consistency.md]

## Shot structure upfront

For multi-shot blocks, state the total duration, aspect ratio, and shot count before the detailed action. Higgsfield’s Seedance prompt library emphasizes specifying shot structure up front; creator videos similarly treat shot count / sequence order as the scaffold that keeps complex prompts from collapsing into one generic scene.^[raw/articles/seedance-prompting-20260523/higgsfield-seedance-guide.md, raw/articles/seedance-prompting-20260523/youtube-elevenlabs-multishot.md, raw/articles/seedance-prompting-20260523/youtube-dan-kieft-course.md]

Recommended block opening:

```text
Seedance 2.0 multi-reference I2V. Total 10s, 16:9, 720p. Four ordered visual beats, not one static scene. Use references in exact order: Image 1 -> Image 2 -> Image 3 -> Image 4.
```

Then write `Beat 1`, `Beat 2`, etc. If the block is a single continuous shot, say `single continuous shot, no cuts`; if it is montage, say `multi-shot montage, do not use one camera angle or a single cut`.

## Camera and motion language

The most useful camera tokens are explicit and bounded: `slow dolly in`, `medium tracking shot from behind`, `locked close-up with micro eye movement`, `side-profile track`, `gentle handheld micro-jitter`, `rack focus`, `orbit`, `pull back`, `low-angle wide`. For POV, specify what the camera is not doing: `no cuts, no zoom, natural head movement`, or the model may invent angle changes. For close-ups, explicitly say `no zoom out` and `keep the face/crop close`.

Use motion budgets. MV blocks should not all be hyper-chaotic. Split into:

- `micro-motion`: eyes, rain, hair, lantern glow, fabric, breathing.
- `moderate motion`: walking, running, reaching, turning.
- `impact motion`: burst/transition only where the music demands it.

This connects Seedance prompting with [[video-team-seed-system]] and avoids over-animating emotional close-ups.^[raw/articles/seedance-prompting-20260523/higgsfield-seedance-guide.md, raw/articles/seedance-prompting-20260523/seedance2-app-docs.md, raw/articles/seedance-prompting-20260523/youtube-tao-prompts-filmmaking.md]

## Negative / preservation constraints

Seedance prompts should include concise negative constraints, but they should be targeted rather than a giant Stable-Diffusion-style negative prompt. For this user’s MV workflow, the canonical tail is:

```text
Preserve exact crop unless explicitly changed. Maintain heroine identity, costume, face, body proportions, paper-lantern motif, rainy blue/amber palette. No text, logos, readable signs, lip-sync, new facial structure, new props, gore, flags, watermarks, or location reset. Mute generated audio.
```

Add block-specific constraints when needed, e.g. `not a real bird`, `do not turn the motif into a weapon`, `do not replace all beats with the destination vista`, `no single riverside scene replacing the ordered sequence`.

## Prompt length and density

Runway UI may enforce a 3500-character prompt counter in the user’s route. Keep block prompts compact: usually 700–1500 characters for 3–5 refs is enough. Dense action lists are useful only if they clarify shot order. If a prompt becomes long, remove generic film adjectives before removing identity/order constraints.

Priority order when trimming:
1. keep reference order / roles;
2. keep exact identity/costume/crop constraints;
3. keep motion beats and camera instructions;
4. keep aspect/duration;
5. trim generic style adjectives first.

## MV block template

```text
Seedance 2.0 multi-reference I2V. Total {duration}s, {aspect}, {resolution}. {beat_count} ordered visual beats, not one static scene. Use references in exact order: {Image 1 role} -> {Image 2 role} -> ...

Beat 1 ({time or musical cue}): using Image 1, {subject/action/environment}. Camera: {specific camera}. Motion budget: {micro/moderate/impact}.
Beat 2: using Image 2, {action/transition}. Camera: {specific camera}. Preserve continuity from Beat 1.
...

Style: {project palette/lighting/lens}, matching the locked music energy.
Preserve: {identity/costume/props/crop/order}.
Avoid: {block-specific failure modes}. No text/logos/watermarks/lip-sync/new face/new props/location reset. Mute audio.
```

## Scenic gallery pattern mining

Scenic (`scenic.sh`) is a Seedance 2.0 prompt gallery surfaced by the Threads post from `@scenic.sh`: it crawls/collects Seedance video prompts in a Pinterest-like browsing surface. Treat it as a pattern library for prompt structure, not as project truth. The useful features are filter tags (`Action`, `Ad`, `Anime`, `Close Up`, `Tracking`, `Slow Motion`, `First Person`, etc.), full prompt detail pages, creator/source links, and related-prompt exploration.^[raw/articles/scenic-sh-seedance-prompt-gallery-threads-20260525.md]

Rules for the prompting bot:

- Use Scenic-style examples to mine reusable structures: timestamped shot lists, hook → transformation → hero-shot arcs, reference-placeholder roles, camera/action verb density, and genre-specific pacing.
- Do not copy public gallery prompts verbatim into user projects. Extract the skeleton, then rewrite with the project’s Block Map, reference order, music timing, identity/costume/crop constraints, and avoid rules.
- For character/model sheets, Scenic examples reinforce a strong rule: do **not** treat the sheet as one flat image. Convert sheet elements into ordered shots such as `detail → identity → presence → full reveal`, with active acting, micro-expressions, gaze/body language, controlled camera movement, and consistent lighting.
- For ad/product/social blocks, use timestamped arcs: dull/problem state → product/contact/action → transformation → energetic demonstration → explicit hero shot.
- When a block maps to a gallery pattern, write the pattern name into `prompt_rules_used.md` so QC can verify that the final prompt used the intended structure.

## Retrieval / application logic

Before writing a Seedance prompt, Planner or Toji should first choose a Seedance method from [[seedance-feature-playbook]] (first/last frame, storyboard/conti grid, camera-control, extension/continuation, or repair/replace), then retrieve from this page and any relevant Scenic-style pattern by block type:

- `character close-up` → use identity lock, crop preservation, micro-motion, no zoom-out.
- `running / kinetic` → use tracking camera, moderate motion, ground continuity, no body deformation.
- `memory / interior` → use environment role, slow dolly/rack focus, no identity overwrite.
- `object/motif macro` → assign prop reference role, specify whether object may transform, no new object.
- `transition / abstract` → specify whether it is metaphorical or literal, prevent unwanted animal/object substitutions.
- `multi-shot montage` → state shot count/duration first and enumerate beats.
- `POV` → state single continuous POV, no cuts/no zoom, what hands/camera can see.
- `character/model sheet intro` → Scenic pattern: treat the sheet as a shot library, not one image; structure `detail → identity → presence → full reveal`; include micro-expressions, natural gestures, controlled camera, consistent lighting.
- `ad/product/social 15s` → Scenic pattern: timestamped conflict/problem → product/contact → transformation → energetic demonstration → explicit hero shot.

The retrieval output should be a short `prompt_rules_used` list saved beside the prompt, not a hidden thought. Production lanes should write `lanes/seedance/prompts/<BLOCK>_prompt_rules_used.md` or include the rules in the lock record so QC can compare the generated video to the intended prompt logic.

## Failure modes to encode

- If a block has 3–5 references, do not ask Seedance to infer ordering; enumerate beat-by-beat.
- If a prior generation ignored early references and used only the destination/background image, add `do not collapse the sequence into only Image N`.
- If old Runway assets contaminate upload, that is a UI/attach issue, not a prompt issue; defer the block and continue queue-fill rather than stopping all of Toji.
- If prompt says “bird-like” but the desired image is abstract, explicitly say `not a real bird / no animal anatomy`.
- If close-up identity matters, put `no zoom out, no new face, no facial structure change` near the start and tail.

## Related

- [[video-team-seed-system]]
- [[video-project-seed-template]]
- [[video-typography-operating-manual]]

## Dynamic MV motion enforcement

For this workflow, Seedance should not be used only to keep reference images static and cut between them. Every block prompt needs dynamic language matched to the block role:

- close-up / memory: micro eye movement, breathing, hair/rain/fabric motion, rack focus or gentle dolly; no face/crop drift.
- kinetic / run: tracking camera, parallax, footstep/cloth/hair motion, acceleration/deceleration, stable anatomy.
- object / motif: macro push, glow/rotation/particles/rain interaction, clear causal transformation.
- abstract / transition: morph/streak/flare/whip-pan/impact beat; specify metaphorical vs literal to avoid unwanted animals/objects.
- climax / final: living atmospheric motion or cinematic reveal/hold, not frozen frame.

A prompt that only maps Image 1 → Image 2 → Image 3 without camera/action verbs should be rewritten before Generate. This rule is an execution bridge for [[video-team-seed-system]].

## Runway web UI reference-upload operating lesson — superseded 2026-07-12

The 2026-06-12 asset-selector one-by-one route is **superseded**. Current verified route (2026-07-12 correction + 2026-07-20 loop policy):

- Finder-frontmost direct drag/drop only, one reference at a time, into the visible empty `Image N` slot.
- Never use the asset-selector Search field, picker modal, or hidden file inputs unless the user explicitly overrides.
- Success condition is the visible active-strip thumbnail per file, verified after each drop.
- Full state machine: `codex-skills/seedance-prompt-en/SKILL.md` → "Runway Web UI Reference Upload Lesson — corrected 2026-07-12", and `seedance-operations/simple_generate_loop_policy_20260720.md`.
