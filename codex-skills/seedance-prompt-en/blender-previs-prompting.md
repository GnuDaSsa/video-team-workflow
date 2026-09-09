# Blender / 3D previs reference branch

Version-neutral authoring adapter; selected Seedance version still owns model,
UI, duration, reference limits and attestation. Load when Blender, 3D previs,
animatic, proxy animation, or a request to skin/restyle a rendered motion guide
is part of the input. No new agent, provider or execution route is authorized.

## 1. Choose what the reference owns

Before writing, distinguish:
- **MOTION_GUIDE**: borrow only named trajectories, timing or camera mechanics;
  the result is a new scene. Do not promise pixel/frame-exact tracking.
- **SOURCE_RESTYLE**: edit the source sequence, preserve its shot boundaries,
  camera, trajectories, occlusion order and contact events; replace appearance.
  This is the branch for “Blender 위에 입혀라”, not generic visual inspiration.

Record this distinction in the existing package's reference-role description.
The video owns motion/camera/cut order; images own named identity/design/style
and environment attributes. Do not independently re-direct those same cameras
in a second prose shot list. Resolve any source/prompt conflict before submit.
Existing user duration/count instructions remain intact (including 15s/6 shots).

## 2. Inspect the source before asking for a replacement

Compare source and approved targets at establishment, contact, occlusion,
recovery and ending. Confirm entity count, persistent one-to-one identity,
contact geometry, scale, crop, and readable foreground/background separation.
A filename, attachment, attestation or render completion is not visual QC.

For SOURCE_RESTYLE, use proxies aligned with target silhouette, proportions,
major appendages and palette whenever feasible. Three identical toy bodies
identified only by different colors are a poor input for three radically
different finished objects. If replacement has already failed, rebuild those
proxies before repeating the same full-scene request. Recheck collision radii
and passage clearance after changing geometry; preserve paths only where safe.

Build visible environment structure in the source when geometry continuity is
important: enclosure, openings, columns and major light bands. A background
image describes appearance, not an automatic 3D reconstruction or flat plate.
Do not expect a sparse gray set to become a specific complex venue merely by
adding a color adjective. Intentional source stylization is allowed; neutral
proxies are not automatically invalid for every MOTION_GUIDE task.

## 3. Compile an explicit edit, not a vague recolor

Use a compact source-first contract. Example (adapt tokens to the actual deck):

> @Video1을 원본 장면으로 편집한다. 컷 경계·카메라 경로·각 대상의 위치와
> 회전·가림 순서·접촉 후 반동은 유지한다. 영상 속 [구별 가능한 형태 A]는
> @Image1의 [완성 디자인 A] 한 대로 본체와 부속 구조 전체를 교체한다.
> [형태 B]는 @Image2의 [디자인 B] 한 대로 교체한다. 첫 등장부터 마지막까지
> 같은 디자인이 이어지며 이미지의 제품 촬영 구도를 새 컷으로 삽입하지 않는다.
> @Image3은 [환경의 구체적인 구조·재질] 기준이다. 원본의 원근에 맞춰 공간을
> 재작화한다. 모든 숏을 [선/명암/재질]로 일관되게 표현한다.

“Keep everything” conflicts with complete shape/background replacement. Name
only the invariants. “Ignore gray material” alone does not require full-body
replacement. Names/colors alone do not establish identity across occlusion.
Do not paste this checklist, paths or internal branch labels into the prompt.

## 4. Repair by separating variables

If output preserves proxies, recolors the set, or alternates between toy and
finished identities, classify **FAIL_PROXY_APPEARANCE_LEAK** rather than simply
“video reference ignored”. Compare motion preservation separately from design
replacement and venue reconstruction. Model-internal causes remain hypotheses.

Do not keep stacking stronger adjectives or feed the failed mixed-identity
output into another repair. Return to the clean source and fix its ambiguity.
First validate a restyle pass without newly invented cuts, split screens or
extra effects; then add the requested opening effects over verified action.
This separates tests; it does not permanently remove the user's effects or
silently shorten the requested duration. Existing source effects may remain
when they do not obscure identity/contact verification.

## 5. Acceptance and evidence

- No unintended proxy body/appendage remains; no switching between proxy and
  final design, duplicate entity, or unrelated product insert.
- Shot-specific identities persist across distance, turns and occlusion.
- Inspect actual contact → rebound, depth order and complete passage through
  an opening; check after geometry changes as well as after generation.
- Verify camera/cut fidelity, venue continuity and style separately. A good
  motion match is not appearance PASS, and an attractive still is not video QC.
- Match downloaded output to its provider transaction. “Most recently saved”
  does not prove “most recently submitted”. If lineage is unknown, say so and
  retain visual source matching as an inference, not a provider ID.
- Sample sheets support diagnosis; full temporal/playback QC is still needed
  before approval. Generated media must pass before claiming the fix works.

These are same-owner authoring/review checks, not an implemented automatic
vision validator. Prompt edits do not guarantee deterministic skinning.

## Basis

User-approved promotion after a sampled output retained low-poly proxy bodies
and recolored scenery while inserting isolated finished-object closeups;
source camera and trajectories were substantially preserved. This observation
does not establish a universal provider defect or a deterministic root cause.
Official reference-mode scope: [Runway Seedance 2.0 guide](https://help.runwayml.com/hc/en-us/articles/50488490233363-Creating-with-Seedance-2-0)
(supports motion/style transfer and object replacement; no exact-tracking guarantee).
