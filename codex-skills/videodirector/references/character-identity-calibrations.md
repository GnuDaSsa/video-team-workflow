# Deferred video calibration — character identity calibrations

This file preserves the corresponding Codex global video guidance. Read only when the current task needs this phase. Runtime rails/safety and the selected Seedance skill remain authoritative in their scopes.

## Three-panel character identity standard

Apply this to every new video-team/MV/public-contest/institution project with recurring people or characters. The canonical details live only in `runtime/references/character_sheet_prompt_standard.md`.

- Before production styleframes, create and QC one `CHAR_<ID>_TRIPTYCH_R<n>` per recurring identity: **left headless front full body, middle back full body with head, right large 3/4 portrait**, text-free on neutral mid-gray in neutral light.
- The front body's deliberate head omission prevents tiny full-body faces from competing with the large portrait. It must read as a clean, non-graphic studio-reference crop; never injury, gore, or a mannequin.
- If one focused edit still fails to make that crop clean, use the canonical standard's complete-front-head fallback with the right portrait as primary face authority. Do not spend a chain of image calls on the same layout defect.
- The sheet is intentionally plain. Do not bake cinematic lighting, rain, smoke, film grain, LUT, typography, scene background, or beauty retouch into the identity master.
- Identity is an immutable descriptor plus a verified image reference. Every materially different state—wet, wounded, transformed, coat on/off, damaged costume, age stage—is a separately registered derivative made one change at a time.
- Use the canonical `runtime/references/character_sheet_prompt_standard.md` for the current risk-targeted production preflight. Do not turn every recurring identity into an automatic ten-generation QC batch; actual video identity QC still applies.
- Deterministic `_FACE`, `_FRONT_BODY`, and `_BACK_BODY` crops may be made from the approved master with source hash and crop coordinates. They are not new generated identities.
- Attach the approved triptych or minimum required crop to every dependent image/video generation. Bind the right portrait as primary face authority, left panel for front body/wardrobe, middle for rear silhouette/wardrobe. Exclude gray background and seams; mention a missing front head only when that is the actual approved layout.
- Supporting recurring people receive their own triptych. Hand/prop, scale/chemistry, expression, or construction sheets are optional story-specific QC assets, not a mandatory seven-sheet package.
- Production styleframes remain one cut = one prompt = one standalone image. A triptych is an identity-design exception, never a production frame, final edit image, or storyboard sequence.
- Styleframes made before identity lock remain `HOLD_LOOKDEV_ONLY` / `INVALID_PRE_CHARACTER_LOCK_SOURCE` and must be regenerated from the approved triptych before I2V. If attachment cannot be verified, mark `BLOCKED_CHARACTER_SHEET_ATTACHMENT_NOT_VERIFIED`.

### Existing-project continuity — 오늘의 자동완성

- Existing approved MAIN / COUPLE / GUARDIANS sheets remain the required identity sources for the current project; do not invalidate completed assets retroactively.
- At the next major character-lock revision, migrate each recurring identity to the three-panel standard and register provenance from the last approved source.
- Seedance/Runway receives only post-lock, QC-passed styleframes plus the minimum approved identity reference. Never upload an unapproved design sheet or pretend an attachment was used.

<!-- End deferred guidance -->
