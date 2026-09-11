# Blender / 3D previs reference branch

Version-neutral authoring adapter; selected Seedance version still owns model,
UI, duration, reference limits and attestation. Load when Blender, 3D previs,
animatic, proxy animation, or a request to skin/restyle a rendered motion guide
is part of the input. No new agent, provider or execution route is authorized.

## 1. Choose what the reference owns

Choose the scope from the user's latest intent before writing the prompt:
- **MOTION_GUIDE**: borrow only named trajectories, timing or camera mechanics;
  the result is a new scene. Use this when the user asks for 동선 참고 / 동선용
  or a motion reference. Do not promise pixel/frame-exact tracking.
- **SOURCE_RESTYLE**: edit the source sequence, preserve its shot boundaries,
  camera, trajectories, occlusion order and contact events; replace appearance.
  Use only when editing/restyling the existing sequence is actually requested.
  “Blender 위에 입혀라” alone does not settle this distinction; the user's
  explicit clarification that the video is a motion guide takes precedence.

Record this distinction in the existing package's reference-role description.
For MOTION_GUIDE, the video supplies only the named movement cues: direction,
acceleration/braking, relative altitude/distance, event order, and optionally
camera mechanics. It does not own source pixels, proxy shape/material,
lighting, venue appearance, exact framing or cut boundaries. Images own the
named finished identities/design/style and environment attributes. The new
shot plan owns framing, cuts and effects, while respecting the selected motion
cues. If a camera mechanic is borrowed, do not give it a contradictory command.
For SOURCE_RESTYLE, the source owns only explicitly named invariants; avoid
independently re-directing those cameras in a second shot list. Resolve any
source/prompt conflict before submit. Existing user duration/count instructions
remain intact: 15s/6 shots can be a new shot plan, not a source-frame lock.

## 2. Inspect the source for its selected role

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

For SOURCE_RESTYLE, build visible environment structure in the source when
geometry continuity is important: enclosure, openings, columns and major light bands. A background
image describes appearance, not an automatic 3D reconstruction or flat plate.
Do not expect a sparse gray set to become a specific complex venue merely by
adding a color adjective. Intentional source stylization is allowed; neutral
proxies are not automatically invalid for MOTION_GUIDE. In that branch, check
whether the requested paths, event order and relative clearances are legible;
do not require a finished render or identical venue mesh merely to use a guide.

## 3. Compile the selected role, not both

### MOTION_GUIDE — create a new scene from movement cues

Example (adapt tokens, identities and borrowed cues to the actual deck):

> 새 2D 액션 애니메이션을 생성한다. @Video1은 두 기체의 동선 참고다.
> 왼쪽 뒤에서 접근 → 급제동 → 짧은 상승 페인트 → 수비 기체의 상승 반응
> → 열린 아래 진로로 돌파하는 이동 방향, 속도 변화, 상대 고도와 거리만
> 참고한다. 기체의 완성 외형과 작화는 @Image1의 흰청 공격 기체 한 대와
> @Image2의 흑금 수비 기체 한 대를 기준으로 처음부터 끝까지 일관되게
> 그린다. @Image3은 경기장 구조와 색채 기준이다. 영상의 모형 외형·재질·
> 조명·배경은 가져오지 않는다. 아래 새 6숏 구성에 따라 장면을 생성한다.

Do not add “원본 장면으로 편집”, “매 프레임 재작화”, object-replacement
commands, or an exact source-camera/cut lock to a MOTION_GUIDE prompt. Those
instructions change the requested task back into source editing. If camera
motion is needed, name just the useful mechanic (for example side tracking or
an orbit revealing the gap), rather than preserving the entire source camera.
Use unambiguous entity descriptions, not a pilot's name for an airborne craft.

### SOURCE_RESTYLE — edit an explicitly requested source sequence

Use a compact source-first edit contract only for this branch:

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
For MOTION_GUIDE, first check that no source-edit/repaint/frame-lock instruction
has leaked into the role binding or shot plan. Separate path readability from
identity/style fidelity; simplify ambiguous cues rather than changing the job
into SOURCE_RESTYLE. Keep the user's new shot plan and opening-style effects,
with contact and evasion still visible. A role correction is not proof of the
model-internal cause or proof that the next output will succeed.
For SOURCE_RESTYLE, first validate a restyle pass without newly invented cuts,
split screens or extra effects; then add requested opening effects over verified
action. This separates tests; it does not permanently remove the user's effects
or silently shorten the requested duration. Existing source effects may remain
when they do not obscure identity/contact verification.

## 5. Acceptance and evidence

- No unintended proxy body/appendage remains; no switching between proxy and
  final design, duplicate entity, or unrelated product insert.
- Shot-specific identities persist across distance, turns and occlusion.
- Inspect actual contact → rebound, depth order and complete passage through
  an opening; check after geometry changes as well as after generation.
- For MOTION_GUIDE, verify only the selected motion cues and new shot plan;
  changed framing is not itself a failure. For SOURCE_RESTYLE, verify the
  explicitly preserved camera/cut invariants. Check venue continuity and style
  separately in both branches. A good motion match is not appearance PASS,
  and an attractive still is not video QC.
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
The user subsequently clarified that this video's role is movement reference,
not source editing. Scope-specific examples prevent that request from being
silently redirected into restyling; prior submitted prompts remain historical
evidence, not retroactively corrected submissions.
Official reference-mode scope: [Runway Seedance 2.0 guide](https://help.runwayml.com/hc/en-us/articles/50488490233363-Creating-with-Seedance-2-0)
(supports motion/style transfer and object replacement; no exact-tracking guarantee).
