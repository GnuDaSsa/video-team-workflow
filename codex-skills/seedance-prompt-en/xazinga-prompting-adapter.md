# XAZINGA prompting adapter

Source reviewed: `https://www.xazinga.com/apps` (2026-08-21), including its Seedance 2.0, Seedance 2.5, video-prompt-builder, guide, and director skill summaries/downloads.

This is an **adapter**, not a competing provider authority. It retains only provider-agnostic authoring patterns that are compatible with the Korean-prompt, visible-Runway, project-duration-lock, identity, and audio rules in this skill. Do not copy source claims about model limits, product features, or preferred languages as permanent facts.

## Compile additions

### 1. Every attachment has a scoped job

For each `@ImageN`, `@VideoN`, or `@AudioN`, the handoff map and the Korean prompt must declare:

- **use** — exactly which visible attributes are borrowed (identity silhouette, outfit, building geometry, camera motion, action rhythm, sound texture);
- **exclude** — which attributes must not transfer (for example, a character sheet's other panels/background; a building image's occupants; a camera reference's cast/look);
- **scope** — which planned scene(s) may use that anchor.

Attachments are independent anchors in `GENERAL_REFERENCE_MODE`; numbering does not create narrative order. A role-less attachment is a preflight failure. Never attach an identity sheet to a shot in which that character is absent. For two recurring characters, use their separate provider-safe crops/sheets, bind each to a screen role, and avoid a face-forward crowd around them.

### 2. Five visual blocks + package-only planning audit

Model-facing Korean text remains compact and visual:

1. **source binding** — attribute-scoped `@` roles;
2. **style/continuity** — medium, identity, costume, spatial and light locks;
3. **timed shot plan** — a visible action/state change per beat;
4. **camera and sound** — one dominant camera setup per planned scene and only motivated sound;
5. **constraints/end frame** — shot-specific risk plus an edit-ready closing frame.

Before attestation, keep the following **outside the pasted prompt** in the pack/ledger:

- effects/motion inventory (repeated device check),
- density map (quiet vs. eventful beats),
- energy arc (hook → development → release),
- a light contract (source, direction, colour temperature, contrast, exposure change, and final light state).

This planning audit must never become indiscriminate effect stuffing. Every effect, transition, and physical layer needs a visible cause and narrative purpose.

### 3. Time and camera grammar

For a 10s+ source, give each beat an explicit time window; normally use about three-second beats and one core action/state change per beat. A planned multi-shot source may contain 2–4 causal scenes only when the project plan grants those cut IDs. Each scene needs a named camera distance/angle/motion and stable edit-out.

Use concrete physical language rather than genre adjectives or preset names: state the start composition, action, physical response, camera beat, and end frame. Do not combine contradictory camera directions.

### 4. Transition, extension, and repair grammar

- **Transition:** trigger → camera behavior → visible transformation → arrival state.
- **Extension:** boundary-frame continuity → one new action/state → final anchor frame.
- **Repair/edit:** target goal → master elements to preserve → exact visible range → changed action/state → unchanged constraints.

These are prompt-authoring structures only. The actual provider mode and capabilities must be verified in the visible Runway UI and must obey the project duration lock.

### 5. Audio and language precedence

Korean is the final prompt language. Do not append English/Chinese merely because an external guide recommends it. User/project audio instructions outrank generic defaults. If the project requires effects-only, explicitly state: **no background music, song, narration, dialogue, or continuous ambience; only short effects caused by visible action.**

## Critic checklist additions

Before attestation, reject a package when any is true:

- an attachment has no use/exclude/scope declaration;
- a person not meant to be Kim has been given Kim's sheet/crop, or a crowd is likely to clone the identity;
- camera, light, start state, and end frame are not specified per scene;
- transition is a generic montage rather than a causal bridge;
- the model-facing text includes internal audit/ledger instructions;
- the audio clause conflicts with the current project lock.
