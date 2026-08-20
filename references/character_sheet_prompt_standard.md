# Three-panel character identity standard for video-team image lanes

For live-action casting and anti-AI QC, also read `/Users/gnudas/wiki/concepts/live-action-character-authenticity-casting-standard.md`. This document owns the default recurring-character image asset; provider prompting and UI operation remain owned by the Seedance skill.

## Default asset: `CHAR_<ID>_TRIPTYCH_R<n>`

Every new recurring protagonist, pair member, guardian, mascot, performer, or repeated citizen starts with one **16:9 landscape, text-free, neutral three-panel identity triptych**:

1. **Left — headless front full body.** Show the complete body, shoes, proportions, outfit front, accessories, and relaxed hand position. Deliberately omit the head above a clean collar/neckline boundary so downstream wide shots cannot copy a tiny, blurry face from the full-body panel. The omission must look like a clean studio-reference crop, never injury, gore, a severed neck, or a mannequin display.
2. **Middle — back full body with head.** Show back silhouette, hair mass, outfit back, closures, footwear, and accessory placement on the same baseline and at the same scale as the front body.
3. **Right — large 3/4 head-and-shoulders portrait.** This is the only face source in the master. It must be large enough to resolve face silhouette, eye spacing, eyelids, nose, jaw, ears, hairline, skin response, age impression, and a natural catchlight.

The three panels depict the same identity, body, grooming state, outfit, materials, palette, and accessories. Use a neutral mid-gray seamless background, flat or softly one-directional studio light, neutral color response, and medium-true rendering. The sheet is deliberately plain: story lighting, rain, smoke, lens effects, dramatic camera language, film grain, LUTs, typography, UI, and worldbuilding belong in production frames and video prompts, not in the identity master.

### Why the face appears only once

Full-body faces are usually too small to be reliable identity evidence. Keeping one large portrait as the sole face source gives image/video models an unambiguous identity anchor, while the two full-body panels carry body and wardrobe construction. Do not regenerate the missing front head or treat the gray background/panel layout as scene content.

## Required lock before production

Before dependent styleframes or I2V:

1. write an immutable descriptor for face structure, hair mass, age, body proportions, outfit/materials, accessories, and forbidden changes;
2. generate the triptych with Codex `imagegen`, using the approved casting/identity image as an actual reference when one exists;
3. record prompt hash, reference paths/hashes, generation ID, dimensions, bytes, output SHA256, and revision;
4. run anatomical and identity QC at 100% crop;
5. stress-test the approved triptych in **10 varied generations** across pose, distance, lighting, action, and—when relevant—multi-character scenes. Lock only if the same person is recognizable in 10/10 without costume, age, role, or face drift.

If reference attachment cannot be verified, mark `BLOCKED_CHARACTER_SHEET_ATTACHMENT_NOT_VERIFIED`. If the triptych does not pass 10/10, revise one descriptor/layout variable at a time and repeat; do not compensate with a longer cinematic prompt.

## Deterministic derivatives

Provider or generator limits may require a simpler input. Crop only from the approved triptych without generative repainting:

- `CHAR_<ID>_TRIPTYCH_R<n>_FACE` — right portrait only;
- `CHAR_<ID>_TRIPTYCH_R<n>_FRONT_BODY` — left body panel only;
- `CHAR_<ID>_TRIPTYCH_R<n>_BACK_BODY` — middle body panel only.

Record the master SHA256 and exact crop coordinates. A derivative is not a new identity. Inspect all four edges and reject any surviving panel seam or gutter.

Use the full triptych for general multi-reference identity binding when the provider supports it. Prefer `_FACE` for fragile face close-ups; add `_FRONT_BODY` or `_BACK_BODY` only when body/wardrobe orientation is actually visible. Do not pad a reference deck with all derivatives.

## Model-facing role binding

When the full triptych is attached to a video model, the Korean prompt must state its roles explicitly:

```text
@ImageN의 오른쪽 큰 3/4 초상은 얼굴 정체성·피부·눈빛 기준, 왼쪽 머리 없는 정면 전신은 체형·의상 전면 기준, 가운데 후면 전신은 헤어 뒤 실루엣·의상 후면 기준으로만 사용한다. 회색 배경, 3분할 패널, 패널 경계, 앞 전신의 빈 머리 부분은 결과 화면에 재현하지 않는다. 실제 장면의 포즈·구도·조명은 아래 샷 지시를 따른다.
```

The identity reference never dictates scene composition, pose, camera angle, color grade, or starting frame. Those belong to the shot contract.

## State assets and optional supplements

Each materially different state is a separate derived asset: dry/wet hair, clean/wounded, coat on/off, damaged costume, age stage, disguise, or transformed form. Start from the last approved identity master, change **one state variable at a time**, and preserve provenance. Never pass a whole approved sheet through repeated global edits.

Create extra hand/prop, scale/chemistry, expression, or construction sheets only when the story proves they are necessary. They are task-specific QC assets, not the default seven-sheet package and not automatic provider inputs. Repeated supporting characters still receive their own triptych before shared-scene generation.

## Imagegen prompt template

```text
Create one text-free 16:9 landscape film-production character identity triptych for [CHARACTER], arranged as three neutral studio photographs side by side on the same seamless mid-gray background.

IDENTITY LOCK
[Immutable face, hair, age, body, outfit, material, accessory, and role descriptors.]

PANEL LAYOUT
Left: complete front full body on a level baseline, relaxed neutral stance, outfit front and both hands clearly readable; omit the head above a clean collar/neckline boundary so no small face appears, presented as a non-graphic studio-reference crop.
Middle: complete back full body with the head and rear hair silhouette visible, same scale and baseline, outfit back and accessory placement readable.
Right: one large natural 3/4 head-and-shoulders portrait of the same identity, neutral attentive expression, alive eyes with one coherent soft catchlight, face and skin details large and unretouched.

REFERENCE RENDERING
Flat or softly one-directional neutral studio light, true material and skin color, consistent lens perspective, plain mid-gray seamless background, equal visual treatment across panels. This is an intentionally plain identity asset, not key art. Preserve one person, one wardrobe state, and one coherent anatomy across all panels. No typography, labels, UI, palette chips, dramatic set, cinematic grade, film grain, beauty retouch, duplicate face, or extra figure.

AR 16:9
```

Compile high-value prompts through `/Users/gnudas/.codex/skills/image-prompt/` and require its checker to return `ok: true` before image generation.

## QC checklist

- [ ] Exactly three side-by-side roles in the required order.
- [ ] Left front body has no small face and the omission is clean, non-graphic, and visually unambiguous.
- [ ] Middle back view retains the head/hair rear silhouette.
- [ ] Right portrait is a large 3/4 face and the only face source.
- [ ] Face silhouette, eye spacing, nose/jaw, ears, hairline/mass, age and skin remain one identity.
- [ ] Front/back height, shoulders, torso, limb length, hands, footwear and outfit construction agree.
- [ ] Neutral gray, neutral light, true colors; no scene lighting, LUT, grain, text, logo, UI, or beauty campaign finish.
- [ ] Full triptych and any deterministic crops have recorded hashes/provenance.
- [ ] Ten varied stress generations recognize the same identity 10/10.

## Route boundary

- Production styleframes remain one cut = one prompt = one standalone scene image; this triptych exception is an identity-design asset, not a production grid or final frame.
- `standard_i2v`: attach the approved scene styleframe plus the minimum required triptych/crop identity anchor.
- `no_i2v_reference_native`: attach only the minimum approved identity/environment references; the prompt carries the omitted styleframe's blocking and scene design.
- Pre-lock frames remain `HOLD_LOOKDEV_ONLY` and must be regenerated from the approved triptych before I2V.
