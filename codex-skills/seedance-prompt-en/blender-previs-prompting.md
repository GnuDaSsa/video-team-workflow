# Blender / 3D previs reference branch

Version-neutral authoring adapter; selected Seedance version still owns model,
UI, duration, reference limits and attestation. Load when Blender, 3D previs,
animatic, proxy animation, or a request to skin/restyle a rendered motion guide
is part of the input. No new agent, provider or execution route is authorized.

## 1. Choose what the reference owns

Choose the scope from the user's latest intent before writing the prompt:
- **MOTION_GUIDE**: borrow only named trajectories, timing or camera mechanics;
  the result is a new scene. Use this when the user asks for 동선 참고 / 동선용
  (movement reference) or a motion reference. Do not promise pixel/frame-exact tracking.
- **SOURCE_RESTYLE**: edit the source sequence, preserve its shot boundaries,
  camera, trajectories, occlusion order and contact events; replace appearance.
  Use only when editing/restyling the existing sequence is actually requested.
  “Blender 위에 입혀라” (“skin it over the Blender”) alone does not settle this distinction; the user's
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

Example binding/opening text, placed inside the template in
`seedance-prompting.md` (adapt tokens, identities and borrowed cues to the deck):

> Create a new 2D action animation. @Video1 is a movement guide for the two
> craft: take only the travel direction, speed changes, relative altitude and
> distance of its approach from rear-left → hard brake → short rising feint →
> the defender rising in response → breaking through the open lower lane. Draw
> the finished look of the craft consistently from start to end from @Image1
> (one white-and-blue attacker) and @Image2 (one black-and-gold defender).
> @Image3 sets the arena structure and colors. Do not take the video's proxy
> shapes, materials, lighting or background. Follow the new shot plan below.

Do not add “edit the source scene”, “repaint every frame”, object-replacement
commands, or an exact source-camera/cut lock to a MOTION_GUIDE prompt. Those
instructions change the requested task back into source editing. If camera
motion is needed, name just the useful mechanic (for example side tracking or
an orbit revealing the gap), rather than preserving the entire source camera.
Use unambiguous entity descriptions, not a pilot's name for an airborne craft.

### SOURCE_RESTYLE — edit an explicitly requested source sequence

Use a compact source-first edit contract only for this branch:

> Edit @Video1 as the source scene. Keep its cut boundaries, camera path, each
> object's position and rotation, occlusion order and post-contact rebound.
> Replace the whole body and attachments of [distinct shape A] in the video
> with one [finished design A] from @Image1, and [shape B] with one
> [design B] from @Image2. The same designs continue from first appearance to
> the end; do not insert the images' product-shot framing as new cuts. @Image3
> sets [the environment's specific structure and materials]; repaint the space
> to match the source perspective. Render every shot consistently in [line /
> shading / material].

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

History of the proxy-leak observation: `incidents.md`. Official reference-mode
scope: [Runway Seedance 2.0 guide](https://help.runwayml.com/hc/en-us/articles/50488490233363-Creating-with-Seedance-2-0)
(supports motion/style transfer and object replacement; no exact-tracking guarantee).
