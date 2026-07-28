# Character sheet prompt standard for video-team image lanes

For live-action casting and anti-AI QC, also read `/Users/gnudas/wiki/concepts/live-action-character-authenticity-casting-standard.md`. This stable I2V runtime uses these sheets to generate and verify sheet-conditioned production styleframes, and also attaches the clean production sheet to Seedance alongside those styleframes whenever the character appears. Dense Bible/master pages are never Runway inputs.

Research basis:
- A model sheet / character sheet is used in animation, comics, and games to standardize a character's appearance, poses, and gestures across multiple artists and scenes; it prevents off-model drift and supports continuity.
- Production character sheets are not beauty key art or narrative scene frames. They are neutral design references: repeated same character, same proportions, same costume, clean background, orthographic/controlled views, and detail callouts.

Sources checked via web search:
- Wikipedia, "Model sheet": defines model sheets as character boards/sheets/studies used to standardize appearance, poses, and gestures; required for multi-artist continuity and avoiding off-model characters.
- Web search terms used: "AI image generation character sheet prompt front side back turnaround model sheet anime", "character model sheet turnaround front side back expressions art guide", "Stable Diffusion character turnaround sheet prompt front view side view back view".

## Non-negotiable standard

Character sheets for this workflow must be design-lock references, not cinematic frames.

Every character sheet prompt must specify:
1. white/off-white or neutral gray studio background, no scene background;
2. clean production model sheet / animation turnaround / character reference sheet language;
3. the same single character repeated in all panels, not multiple different characters;
4. identical face structure, hair silhouette, body proportions, outfit, color palette, accessories across all views;
5. flat/even studio lighting, no dramatic rain/night/cinematic color cast that changes perceived colors;
6. aligned ground line and same scale for full-body views;
7. no text labels unless explicitly requested, because AI text artifacts hurt QC;
8. no logos, watermarks, signatures, UI panels, speech bubbles, subtitles, random notes.

## Required sheet types

### CHAR_PROVIDER_REF — the one sheet cleared for provider upload

**Mandatory. A character sheet set is incomplete without it**, and it is the only asset from this standard that may be attached to Seedance/Runway.

Every other sheet here is a multi-panel design document with labels, callouts and panel gutters. Those are for approval and for conditioning imagegen; a video model reads their text and grid as things to draw. Rather than asking downstream to judge which file is safe, this standard emits one that provably is.

Prompt should request:
- **one figure, one view** — a clean full-body or 3/4 identity shot of the approved design (a matching head-and-shoulders crop may be produced as `_R<n>_HEAD`);
- neutral or off-white seamless background, flat even lighting, no set, no props beyond the character's signature items;
- **zero text**: no name plates, labels, callouts, arrows, palette chips, measurement lines, logos, watermarks, panel borders or gutters;
- full bleed with generous margins so any crop stays clean; nothing touching an edge;
- identical face silhouette, eye spacing, hair mass, costume colours, body scale and signature props as the approved turnaround.

Reject and regenerate if the output contains any readable glyph, panel seam, multi-figure layout, or a white gutter that would survive a crop.

If this sheet does not exist for a character that downstream needs, stop with `BLOCKED_NO_PROVIDER_SAFE_SHEET` and generate it. Do not substitute a turnaround, bible page, or a crop taken out of a multi-panel sheet.


### CHAR_TURNAROUND
Prompt should request:
- full-body turnaround sheet: front, 3/4 front, profile, 3/4 back, back;
- neutral standing pose or relaxed A-pose, arms visible, legs visible, feet on same baseline;
- same head size, same height, same outfit, same accessories in every view;
- no perspective exaggeration, no action pose, no cropped limbs, no background scene.

### CHAR_EXPRESSIONS
Prompt should request:
- bust/head expression sheet with the same head angle grid;
- neutral, worried, determined, subtle smile, closed-eyes/quiet resolve;
- mouth mostly closed or minimally open unless dialogue is required;
- identical hair silhouette, eye shape, face shape, skin tone, accessories;
- neutral background and even lighting.

### CHAR_HEAD_FACE
Prompt should request neutral front, 3/4, profile, mouth-open/speaking, smile, surprise, concern and blink/closed-eyes close-ups while preserving face silhouette, eye spacing, nose/jaw, ears, hairline and age impression.

### CHAR_POSE_ACTION
Prompt should request:
- action/pose sheet after identity is locked;
- 4–6 readable full-body poses using the same character design: holding lantern, running, reaching, tying charm, back-view overlook;
- poses separated with clean whitespace, same costume/accessories, no environment.

### CHAR_PROP_COSTUME
Prompt should request:
- detail sheet for hands, lantern/charm, scarf/cuffs, shoes, fabric layers, color swatches;
- close-up callouts on neutral background;
- hands must be anatomically plausible and consistent with the heroine's age/style.

### CHAR_HAND_PROP
Prompt should request relaxed hands plus story-specific grips from useful angles. Preserve five fingers, thumb direction, knuckles, wrist connection, nail shape, hand scale and prop contact.

### CHAR_COSTUME_FRONT_BACK
Prompt should request front/back construction, silhouette, fit, seams, closures, fabric behavior, accessories and forbidden changes under neutral light.

### CHAR_SCALE_ROLE
Prompt should request recurring characters at a common baseline next to relevant objects, preserving height, body volume and role separation. Each identity must already be locked independently.

## Negative prompt block

Do not create: cinematic scene, rain background, street background, multiple different girls, alternate costumes, changed hairstyle, changed eye color, changed age, chibi version, glamour portrait only, random props, readable text, logos, watermarks, labels, speech bubbles, captions, cropped limbs, inconsistent scale, fisheye/perspective distortion, heavy shadows, colored lighting that changes palette, wet hair redesign, duplicate faces with different identities.

## Base template

Create exactly one landscape production character model sheet for a video-production pipeline.

SHEET_TYPE: {sheet_type}
REFERENCE_ID: {reference_id}
ROLE: {role}

Purpose: lock the recurring character's identity for downstream reference-conditioned production image generation, continuity QC, **and direct attachment to Seedance as the identity anchor**. This is a production design sheet, not cinematic key art. Being text-free and flat-lit is what makes it safe to upload.

Character identity lock:
- {character_identity}, consistent face shape, eye spacing/shape/color, nose/jaw, ear placement, hairline/mass, age impression and body proportions;
- outfit: {outfit_details}; accessories: {accessory_details}; palette: {palette_details};
- project style: {project_style}; the sheet itself must use neutral studio lighting and neutral background so colors and shapes remain readable.

Sheet layout:
{layout_requirements}

Rendering:
- {rendering_style}, production reference quality;
- flat/even studio lighting, neutral off-white background, clean whitespace between views;
- same single character repeated, same scale where applicable, no labels/text.

Negative constraints:
{negative_block}

## Naming and provenance

Use `CHAR_<ID>_<SHEET_TYPE>_R<n>`. The provider-safe sheet is `CHAR_<ID>_PROVIDER_REF_R<n>` — **downstream selects by that name, never by eye**. Anything without `PROVIDER_REF` in its filename is internal-only. Record imagegen generation ID, prompt hash, attached source reference paths/hashes, dimensions, bytes and output SHA256. If the approved identity reference attachment cannot be verified, mark `BLOCKED_CHARACTER_SHEET_ATTACHMENT_NOT_VERIFIED`.

## Route boundary

- Stable I2V runtime: these assets are identity sources for Codex imagegen styleframes, and `CHAR_<ID>_PROVIDER_REF_R<n>` is additionally attached to Seedance alongside the styleframes when the character appears (2026-07-28). Downstream attaches the `PROVIDER_REF` file by name; the other sheet types never leave this stage.
- No-I2V Reference-Native runtime: governed separately by `/Users/gnudas/Documents/Codex/no-i2v-team-runtime/runtime/references/character_reference_standard.md`; only its locked `PROVIDER_SAFE_REF` tier may be uploaded directly.
