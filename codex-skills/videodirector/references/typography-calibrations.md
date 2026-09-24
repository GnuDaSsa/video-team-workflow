# Deferred video calibration — typography calibrations

This file preserves the corresponding Codex global video guidance. Read only when the current task needs this phase. Runtime rails/safety and the selected Seedance skill remain authoritative in their scopes.

## Typography and transition QC standing rule — 2026-05-06

Mode note: these typography/transition rules are shared, but public-contest videos require extra narrative clarity and compliance; MV videos require extra song/beat sensitivity.

The user strongly dislikes lower-center narration subtitles inside obvious rounded boxes. For MV/public-contest edits, avoid generic YouTube/presentation subtitle styling. Narration text should feel quiet, cinematic, and literary: usually unboxed or near-unboxed, with restrained shadow/gradient only when legibility requires it. Use a separate, calmer/static-feeling font for narration/body copy rather than the same bold public-presentation font used for chapter cards.

Typography QC must explicitly check:
- no subtitle/card overlap at any time;
- no `SCENE 03`-style mechanical labels unless the user asks;
- no direct contest-title wording such as “2026 영상 공모전” in the picture unless strategically required;
- lower-center narration must not cover too much image, must not sit in a big black rounded rectangle, and must feel integrated with the scene;
- chapter cards, location notes, and narration should be separated by role, font, size, opacity, and timing;
- tourism/MV location labels must not remain thin, bland, low-visibility museum captions. If rejected, redesign as a full title system: heavier Hangul, larger phone-readable scale, clear kicker/main hierarchy, warm ivory/gold palette, culturally specific motifs, and composition-aware placement;
- after readability is secured, remove obvious translucent boxes/plates unless absolutely required; rely on stroke/shadow/local vignette first;
- underline/route-line motifs must have finished craft: thinner tapered/feathered strokes, rounded caps/joins, soft glow/blur, eased opacity, and no crude rectangular endpoints;
- for right-aligned labels, ornaments/seals/bullets/route-line starts stay on the visual left of the text block. Do not let symbols jump to the far right just because the text is right-aligned.

Transition QC must explicitly check the first third of the edit for cut-to-cut frame jitter, micro stutters, duplicate/freezing frames, bad crossfade handles, optical-flow artifacts, and 1-frame flashes. If jitter is visible, fix with clean cut handles, short dip/dissolve only where motivated, re-encoding/normalization, or by trimming unstable first/last frames of generated clips before final export.


## CapCut Korean caption shadow/legibility rule — KAIA lesson — 2026-05-13

Apply this globally for the user's MV, public-contest, tourism, institution, and CapCut typography work.

Core lesson from the user's final KAIA CapCut export:
- Do **not** try to fix low-visibility Korean captions by randomly changing colors such as mint, bright yellow, or other flashy accents.
- First make the caption readable with fundamentals: **short copy, large type, actual shadow enabled, shadow opacity around 50–70% as the default starting point, subtle dark stroke, and enough hold time**.
- For bright sky, sunset, city-light, glass, HUD, and complex backgrounds, shadow must be treated as a required legibility layer, not an optional decoration. Start near 50% opacity, then raise/lower by actual CapCut preview/export.
- Prefer white or warm/cool off-white text with dark shadow/stroke for public-sector technology videos. Use accent color only when it has a clear narrative/information role and passes preview QC.
- Avoid ugly rounded subtitle boxes. Use shadow/stroke/local placement first; boxes or plates are last resort.
- Reduce or remove tiny helper labels if they compete with the main caption. Short, large, readable main phrases beat cluttered multi-layer information.
- QC must inspect CapCut actual preview and exported full-frame stills, because contact sheets can make fade-in/out frames look weaker than real playback. The hold section of every key caption must be clearly readable.

Default workflow for future CapCut captions:
1. Write the shortest usable Korean phrase.
2. Set readable size and safe placement away from faces, landmarks, HUD, and the brightest background band.
3. Enable shadow; start opacity about **50–70%**, with moderate blur/smoothing and a small distance.
4. Add a subtle dark stroke if needed; do not jump to random colors.
5. Verify in actual CapCut preview, then export/sample-frame QC before claiming PASS.

## CapCut-first typography revision rule — 2026-05-06

For this user's MV/public-contest edit revisions, if the user asks why CapCut is not being used or has previously required CapCut editing, do not keep presenting arbitrary baked local-render typography masters as the main answer. Build or update an editable CapCut draft first, keep typography as editable CapCut text layers where practical, and only render preview MP4s as secondary review aids. Preserve the previous draft before modifying it.

Typography-specific corrections from Sangju V26:
- Reject translucent rounded/oval cards if any text can escape the card boundary; prefer no box or guaranteed fixed-width safe layout.
- Do not let old lyric-subtitle color habits bias public video typography into yellow/white everywhere. Use a broader restrained palette such as ivory, stone, sage, muted clay, charcoal, and only minimal accent color.
- Opening title and final statement must be redesigned, not patched with the same box style.
- Final mnemonic/statement cards must be optically centered and aligned; no pill/box misalignment.

## CapCut font limitation / baked typography exception — 2026-05-06

CapCut remains the required edit-handoff environment when the user asks for CapCut, but macOS CapCut may flatten or fail to expose desirable Korean fonts. In that case, use this workflow instead of forcing bad generic typography:

1. Preserve/update a CapCut draft for timeline review and handoff.
2. Design high-fidelity typography externally with the intended Korean font, layout, timing, and alpha treatment.
3. Render the typography as transparent overlays or a baked master, import/align it back into the CapCut draft when practical, and clearly label it as an intentional font-fidelity workaround.
4. QC must compare the CapCut draft and final rendered master so the delivered video is not merely a local render detached from the user's CapCut workflow.

For public-sector contest films, typography must help explain the work without looking like a presentation template: bigger when needed, timed to reading rhythm, optically aligned, and role-separated into title/chapter/narration/final statement systems.

## MV typography/editing lesson — 교차 문구 편집 호흡 — 2026-05-10
- In Korean MV/public-contest typography, when transforming phrase A into phrase B in the same position, give B an equivalent solo reading breath to A before introducing any subordinate/lower explanatory line.
- Do not stack the lower line immediately on top of B; sequence as: A appears/holds/fades → B appears/holds in the same visual position → lower support line appears beneath B while preserving the established top/bottom layout.
- QC must inspect the actual CapCut preview for line order, hierarchy, scale, and overlap; JSON timing alone is not enough.

## CapCut editable text visual alignment lesson — 2026-05-10

For this user's CapCut typography work, **equal JSON/transform X values do not guarantee visual alignment**. CapCut editable text is effectively positioned by text-box center and rendered text width, so captions with different Korean line lengths can appear visually misaligned even when their transform coordinates are identical.

Required workflow for future CapCut typography alignment:
- Use the actual CapCut preview as the source of truth, not JSON equality.
- When the user asks to align caption positions, align by the **visible first glyph / left edge in the preview**, not by raw transform coordinates.
- If using draft JSON as a helper, calculate or adjust per-caption X offsets based on rendered text width, then reopen CapCut and visually QC.
- For important public-contest typography, select representative clips in CapCut, inspect the actual preview, and capture screenshots before claiming alignment is fixed.
- If one short line still feels visually off after formulaic correction, apply a direct screen-based manual nudge; visual balance beats numeric symmetry.
- Record this as a CapCut-first typography rule: editable text layer remains preferred, but CapCut UI/preview proof is mandatory for alignment claims.

<!-- End deferred guidance -->
