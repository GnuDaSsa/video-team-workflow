---
title: Aside Image and Video Prompting Knowledge
created: 2026-09-20
updated: 2026-09-20
type: concept
tags: [video, video-production, multimodal, retrieval, qc]
sources: [raw/articles/aside-image-prompting-review-2026-09-20.md, raw/articles/aside-v20-prompting-review-2026-09-20.md, raw/articles/aside-v25-prompting-review-2026-09-20.md]
confidence: medium
contested: false
contradictions: []
---

# Aside Image and Video Prompting Knowledge

## CURRENT

Reviewed creative guidance, not execution authority. The native Aside selector loads only exact card sections below, at most six complete cards and 9,000 characters. Official recommendations and reviewed local heuristics are distinguished in the accompanying catalog; neither is a new media-quality test. Operational authority stays in the selected native skill or the existing Codex runtime, never an old wiki copy.

### image-core

- Specify the image's purpose, subject, composition, visible materials, light and constraints. Use concrete placement and framing instead of generic praise.
- Choose a readable structure appropriate to complexity. Paragraphs, labeled sections or concise lists are alternatives, not competing magic syntaxes.
- Describe intended optical appearance. Camera/lens wording is a cue, not a promise of physically exact simulation. Aspect ratio belongs to the visual brief; API-only parameters are not creative content.

### reference-roles

- Identify each supplied input by its actual order and specific contribution: identity, clothing, product, setting, palette, motion or sound.
- State what transfers and what must not transfer when ambiguity matters. A style reference does not authorize copying its subjects; an identity sheet does not dictate scene lighting or layout.
- Reference order alone is not shot order or a first-frame contract. Do not invent unavailable references or turn a sheet's panels, labels or neutral background into the final scene.

### image-edit

- Isolate the requested change and enumerate the surrounding invariants: identity, geometry, crop, viewpoint, light, labels or materials as relevant.
- Start from the approved input, not a regenerated approximation. Restate the important preserved details on later edits; change one causal variable when diagnosing a defect.
- Prompt preservation is not pixel locking. Flag exact unchanged-region requirements for compositing and compare the resulting pixels separately.

### image-identity

- Bind recognition to the approved reference and a concise stable signature of face shape, feature spacing, hair mass, proportions and wardrobe.
- Preserve distinguishing asymmetry and plausible skin texture at the intended distance; do not equate realism with exaggerated pores or beauty smoothing.
- Keep identity anchors separate from pose, crop, expression and scene lighting. When a sheet is actually requested, give each view one role. Do not impose a multi-view sheet or a fixed batch of stress generations on every portrait.

### image-product

- Prioritize silhouette, component topology, scale, material finish, label placement and contact with the supporting surface.
- Make the lighting explain shape without inventing glowing parts or altering color/finish. Preserve the approved geometry during a localized edit.
- If transparency is requested, distinguish an actual alpha channel from a depicted checkerboard; the output file must be checked separately.

### image-text

- Supply exact quoted copy, requested language, occurrence count, hierarchy, placement and readable surrounding space. Separate text content from visual style.
- Ask for only the required copy rather than allowing invented slogans or labels. Check spelling, punctuation and legibility in the delivered image.
- Treat charts and diagrams as factual specifications: supply verified labels, numbers and relationships. A polished visual is not a fact check.

### image-optics

- Decide distance, viewing angle, subject scale, foreground/midground/background and light direction before adding gear names.
- Keep the scene's fixed geography distinct from screen-left/right placement; a reverse angle is not a simple horizontal mirror.
- Use lighting, shadow direction and surface response consistently. Avoid automatically adding neon, fog, rim light, grain or a shallow-focus look to unrelated requests.

### image-animation

- Specify line economy, shape language, fill/shading, palette and material treatment separately from the depicted event.
- Preserve identity proportions, hair mass, costume and world geometry across images. Describe the desired visual variables rather than relying only on a studio or artist name.
- Favor readable silhouettes and broad controlled detail. Extra fine texture is not automatically higher quality and can undermine later video stability.

### video-core

- Write an observable scene contract: starting state, purposeful action or change, camera behavior, physical response and useful ending composition.
- Distinguish subject movement from camera movement. Preserve the approved complexity; simplify incompatible instructions, not the causal event the user requested.
- State whether the result is a continuous shot or an approved shot sequence. Timing phrases guide approximate pacing, not guaranteed frame-accurate cuts. Keep technical controls outside the creative prose.

### video-camera

- Select the shot purpose, distance, angle and spatial depth before specifying a dominant camera path. Describe start position, path, acceleration/deceleration and exit frame where relevant.
- Keep subject speed separate from camera speed. Use parallax or occlusion only when they clarify movement, not as decorative motion.
- Keep critical hands, feet, prop contact and reveals readable. Do not stack incompatible orbit, zoom, whip and tracking directions; do not remove a deliberately causal complex path merely to shorten prose.

### video-physics

- Make the causal chain visible: approach or stimulus, contact or force, reaction, and recovery or settled state. Describe only responses appropriate to the actual material and subject.
- For a human action, specify support, weight transfer, joint direction and prop grip when important. For rigid products, preserve topology and contact shadows; stationary objects need no invented breathing, cloth or particles.
- A camera-only move can be sufficient. End in a usable composition without pretending a freeze frame proves continuous motion quality.

### video-identity

- Anchor the character to approved identity references and keep face, body, hair and wardrobe stable through turns and changes of scale.
- Explain which sheet region governs which feature; exclude panel layout and reference background from the scene. Separate reference identity from current pose and camera instructions.
- Describe acting through visible gaze, breath, hand tasks and weight rather than emotion adjectives alone. Reference attachment and temporal identity quality require separate verification.

### video-audio

- Separate spoken content, ambience, diegetic actions and music intent. Preserve required dialogue exactly in its requested language.
- Tie an important sound cue to an observable action or beat, and name exclusions such as music or dialogue only when they are part of the brief.
- Prompted rhythm, synchronization and natural speech are goals, not measured results. Do not describe sound in an explicitly silent/audio-off deliverable; actual listening remains a separate check.

### video-storyboard

- Use the approved board as a plan for shot purpose, spatial layout, blocking, camera, action, sound and exit composition.
- Distinguish a reference deck from an explicitly sequential board. Only an approved board's shot IDs establish narrative order; input numbers alone do not.
- Render the intended scenes, not board borders, labels, camera diagrams or panel grids. A multi-shot preview is not automatically a final-production source or a replacement for identity references.

### video-text

- Keep required copy exact and sparse, with a clear title/body/label role, stable placement, subject clearance and enough reading time.
- Reduce density and improve contrast before adding motion. Do not import a former project's font, shadow percentage or caption position as a global default.
- Temporal text stability is a separate risk from a good first frame. If precision is essential, identify editable post-production typography as a delivery consideration rather than claiming the generative prompt guarantees it.

### video-edit

- Distinguish extracting a quality from a reference (motion, style, rhythm) from modifying the actual source video. State precisely which content changes and which structure remains.
- The creative transformation must match the executor's approved mode. Describing an edit or extension does not itself select or authorize that provider mode.
- Preserve identity, structure and timing constraints only to the extent requested, and describe the new visible result clearly instead of relying on an ambiguous verb such as improve.

### video-animation

- Keep medium, continuity and direction rules stable while changing the current event. Specify line/shading/palette response independently of action.
- Use readable pose-to-pose weight, anticipation and settle when appropriate; maintain contacts and anatomy rather than adding automatic smear, speed lines or overshoot.
- If line boil or texture crawl appears, favor broader clean planes and stable materials. Do not copy a reference grid or replace intentional stylization with live-action surface details.

## Sources and scope

Audit and exclusions: [[aside-prompt-knowledge-audit-2026-09-20]].

- Official sources reviewed 2026-09-20: https://developers.openai.com/api/docs/guides/image-prompting ; https://help.runwayml.com/hc/en-us/articles/50488490233363-Creating-with-Seedance-2-0 ; https://help.runwayml.com/hc/en-us/articles/53542207042323-Creating-with-Seedance-2-5. API capabilities do not establish web backend identity.
- Current creative source pages: [[video-prompting-live-action]], [[video-camera-composition-grammar]], [[character-bible-page-prompt-standard]], [[video-prompting-2d-animation]], [[storyboard-production-blueprint-standard]], [[video-typography-operating-manual]]. The selector records whole-file hashes and selected conceptual sections. This is reviewed synthesis, not verbatim extraction.
- Never auto-ingest raw articles, archived policies, context capsules, old project URLs, Claude routing, API-only parameters, or dated editor numeric recipes. Unknown explicit retrieval tags require a catalog review instead of a silent generic fallback.
- Model/version capacity, UI selection, paid retries and language ownership remain outside this corpus. Timestamps are pacing guidance; runtime settings and delivered media must be measured separately.

## CHANGELOG

- 2026-09-20: Added 17 scoped, source-backed cards for native Aside image/video authoring; separated creative knowledge from legacy operations. No generation-quality claim.
