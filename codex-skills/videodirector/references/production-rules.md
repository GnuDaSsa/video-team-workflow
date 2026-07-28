# Production hard rules

## Core production rules

- Prefer image-first workflows over text-to-video for character consistency.
- If characters exist, define a fixed reference before scene generation.
- Keep hair, eyes, outfit, and body type fixed across scenes; change expression only.
- Do not put narration text inside Grok/I2V prompts.
- Output copy-paste-ready deliverables, not abstract advice.
- Do not tell the user to "refer to a preset below"; include required style locks directly inside each prompt.
- On revisions, update only the requested scene/track/character scope instead of regenerating everything.

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

## I2V/Seedance anti-wobble videoization rule — 2026-06-21

When the user says a generated video became `자글자글`, `우글우글`, `비디오 과정에서 망가짐`, `얼굴이 끓음`, or similar, treat it as a videoization failure even if the still image was approved. Consult `/Users/gnudas/wiki/concepts/video-image-qc-style-continuity.md` and `/Users/gnudas/wiki/concepts/seedance-prompting-knowledge.md` before writing the next prompt.

Default response: use **stability-first videoization**. Lock the approved still's exact composition, face shape, hair silhouette, hands, phone/UI/text, black ad-screen placeholders, room/vehicle geometry, and background perspective. Prefer single-image 3.5–4s stable clips or multi-reference clean cuts; do not ask for morph transitions when stability matters. Allow only breathing, small shoulder/hand motion, hair-tip/curtain/light/ambience movement, short dialogue/SFX if needed. Keep the audio toggle ON and name the soundscape in the prompt as usual — a stability problem is a motion problem, not an audio one. Reject clips with texture crawling, line boiling, face flicker, hand/finger warp, Korean text shimmer, phone deformation, or unstable straight lines.

## CapCut editable-timeline rule

For this user's serious MV/public-contest/institution video work, do not deliver a single flattened ffmpeg-assembled MP4 as the main editable result. ffmpeg is allowed for pre-CapCut QC, normalization checks, contact sheets, proxy previews, ffprobe/blackdetect/freezedetect, and temporary timing slates only. The actual edit must be built or mirrored in a CapCut draft so the user can adjust clips, timing, audio, and text inside CapCut. If a flattened reference render is useful, label it clearly as `QC/proxy/reference`, not as the editable final. Final handoff should include a CapCut project/draft with separate media/text/audio tracks where practical, plus manifests and QC artifacts.

Additional hard check: a CapCut draft is not valid merely because JSON inspection or the timeline view shows clip blocks. It must actually preview/play in CapCut's viewer. If a JSON-injected or externally generated draft shows a black viewer, stalled playback, missing media, or nonfunctional preview, mark it HOLD/DO_NOT_USE and rebuild through CapCut's own import/timeline workflow or another route that is verified by actual CapCut playback.

## Revision rules

- "씬 3 바꿔줘" -> replace only scene 3
- "BGM 분위기 바꿔줘" -> update only the target track
- "캐릭터 수정" -> update the character JSON and only the affected scenes

## Request routing

- "영상 기획" -> ask the 3 start questions if needed, then produce concept + structure
- "씬 나눠줘" -> produce a cut list
- "프롬프트 뽑아줘" -> produce character JSON + Codex imagegen start-frame JSON + Grok/Seedance/I2V prompts
- "BGM 짜줘" -> determine track count and output BGM JSON
- "대사 정리해줘" -> output narration/dialogue sheet with timecodes
- "전체 패키지" -> follow the default full-package order exactly

## Character-sheet-first gate

For recurring people/characters the sheet stage is a hard gate, not a polish step.

- Before any production styleframe batch, create and QC the required sheets: the approval bible page where useful, the clean production sheet `CHAR_<ID>_PROVIDER_REF_R<n>` for identity lock, and mini-sheets for recurring supporting pairs/groups.
- Every dependent image prompt must attach or explicitly reference the approved sheet(s). A previous styleframe or a text-only memory is not an identity source.
- Styleframes generated **before** the sheet lock are `HOLD_LOOKDEV_ONLY`: composition/lookdev reference only, excluded from I2V handoff, and regenerated with the sheets attached before they can be used.
- If the generator cannot verify the attachment, record `BLOCKED_CHARACTER_SHEET_ATTACHMENT_NOT_VERIFIED` or `BLOCKED_IMAGEGEN_EDIT_FAILED` — never proceed from memory.
- QC compares regenerated frames to the sheets for face, hair mass, age impression, outfit/materials, hands/props, and role separation.
