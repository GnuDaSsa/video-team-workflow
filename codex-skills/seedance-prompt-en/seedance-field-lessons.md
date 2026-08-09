# Seedance prompting — field lessons

Prompt-authoring corrections proven in production, promoted out of a rules copy that had grown inside the independence-activist project because the canonical documents contradicted each other. That file sat in one of 68 session folders, so most runs never saw them.

**Scope: prompt authoring only.** This file used to also carry image-QC verdicts, video-QC verdicts, and Runway board/queue procedure. Those were moved to their real owners on 2026-07-28 — a prompting document should not be where an image reviewer or a UI operator looks for their rules:

- image QC (source frame quality, emotion causality, duplicate protagonists) -> `image-qc-source-frame-standard.md` in this skill folder, owned by the `image_qc` lane
- Runway board, queue, stall and completion rules -> `seedance-production.md`

Project-specific content (1907 costume research, that project's filenames, sheet paths, block cursor) was not promoted at all.

## References are anchors, not a storyboard

`GENERAL_REFERENCE_MODE` — the single most load-bearing correction in that file.

- `@Image1 → @ImageN` are **independent reference images** showing look, palette, space, props, and plausible action. They are not consecutive frames.
- Never write the prompt so the numbering becomes a sequence to move through, a match-cut instruction, or an order to replay.
- One generation = **one coherent shot with one camera flow**, newly composed. The model must not copy several references in turn inside a single clip.
- Do not force interpolation between reference compositions that were never meant to connect.

## Character sheet as identity anchor

- Attach the approved sheet whenever a recurring character appears — always, in addition to the scene references.
- Order: scene references first, character sheet(s) after.
- The sheet fixes face silhouette, hair mass, costume, age impression, body proportion, and signature props. Nothing else.
- The sheet is **not** a scene-order cue, a transition cue, or a pose instruction. A character must never end up in a frontal poster stance merely because a sheet was attached — the shot's action, camera, and mid-motion state are specified separately.
- Verify by the visible `ImageN` thumbnail on **this** generation. Conversation context and previous decks are not verification.
- Stale thumbnails from an earlier deck: do not Generate until the strip is fully replaced.

### Five-image refresh

During image batches, index generations from 1 and re-attach the approved sheet as a real file reference every fifth image (5, 10, 15, …), confirming attachment before continuing. This is a drift-prevention habit layered **on top of** the per-generation attach rule, never a replacement for it.

Record in the manifest: `batch_id`, `image_batch_index`, `character_sheet_refresh_at`, `attached_sheet_path`, `attachment_verified`.

## Creative mode without the light-match crutch

- Creative means inventing **camera, action, viewpoint, and physical discovery** — not decorating with transitions.
- Fire, torches, lamps, and firelight are usable only when they are a real prop or action **in that shot**. Do not expand them into cross-scene glue, a "light chain", "answering lights", or a repeated warm-edge / through-aperture motif.
- Light matches between scenes are allowed only on an explicit character-transition beat.
- Other transitions come from the scene's own causes: steam off food, cloth movement, footfall and dust, a door shadow, a hand on a prop, water, smoke, a change of spatial direction.
- Distribute camera grammar across scenes — low three-quarter, side track, overhead, intimate macro, rear follow, long-lens observation, POV, static-to-push — one per shot, chosen to fit.
- Use 2–4 physical layers (steam, smoke, wind, fabric, reflection, foreground occlusion, parallax, focus breathing) and only where the cause actually exists in frame.
- Do not force `calm → discovery → transformation` or a through-aperture opening onto every scene.
- If the same light device repeats in adjacent scenes, or a transition effect outweighs the scene's real action, fail it as `CREATIVE_MOTIF_OVERUSE_FAIL`.

## User-directed compact natural-language prompts

When the user explicitly prefers their own short, natural-language Runway cards over an expanded template, that preference overrides the normal prompt-length target for the affected package.

- Write one cohesive Korean paragraph, not a label list or compressed schema.
- For one coherent 15-second beat, **about 180–450 Korean characters is valid** when it still names the visible setup, one action, one camera direction, only the motivated physical reactions, sound, and the final composition.
- Do not fake concision by dropping identity, contact physics, sound, or the ending frame. A genuinely complex or explicitly storyboarded sequence may stay longer.
- Keep reference roles, model choice, settings, attestation, and QC in the handoff package. They never enter the visual prompt.
- Treat this as a user-preference route, not a new provider, model, agent, or automation branch. Verify the result in media QC before promoting it as a broadly proven quality rule.

## No generic negative wall

Do not auto-append conservative boilerplate such as `no sudden cuts`, `no exaggerated camera movement`, `no camera drift`. Keep only the role-specific essential locks — face, crop, hand/product contact, text/logo. General defects are caught in QC afterwards, not by padding every prompt.
