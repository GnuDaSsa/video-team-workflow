# Character sheet prompt standard for video-team image lanes

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

### CHAR_TURNAROUND
Prompt should request:
- full-body turnaround sheet, 4 orthographic poses in a row: front view, 3/4 front view, profile side view, back view;
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

## Negative prompt block

Do not create: cinematic scene, rain background, street background, multiple different girls, alternate costumes, changed hairstyle, changed eye color, changed age, chibi version, glamour portrait only, random props, readable text, logos, watermarks, labels, speech bubbles, captions, cropped limbs, inconsistent scale, fisheye/perspective distortion, heavy shadows, colored lighting that changes palette, wet hair redesign, duplicate faces with different identities.

## Base template

Create exactly one 16:9 landscape production character model sheet for an anime music-video pipeline.

SHEET_TYPE: {sheet_type}
REFERENCE_ID: {reference_id}
ROLE: {role}

Purpose: lock the recurring heroine's identity for downstream reference-image generation and Seedance I2V continuity. This is a production design sheet, not cinematic key art.

Character identity lock:
- teenage Japanese anime heroine, consistent face shape, consistent eye shape/color, consistent hair silhouette, consistent body proportions;
- outfit: {outfit_details}; accessories: {accessory_details}; palette: {palette_details};
- mood motif may be rainy-night / warm paper-lantern amber, but the sheet itself must use neutral studio lighting and neutral background so colors and shapes are readable.

Sheet layout:
{layout_requirements}

Rendering:
- clean Japanese animation model-sheet style, crisp linework, production reference quality;
- flat/even studio lighting, neutral off-white background, clean whitespace between views;
- same single character repeated, same scale where applicable, no labels/text.

Negative constraints:
{negative_block}
