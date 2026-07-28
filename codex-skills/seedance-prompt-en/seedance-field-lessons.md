# Seedance field lessons

Rules promoted from `SEEDANCE_OPERATING_RULES_CURRENT.md`, a rules copy that grew inside the independence-activist project because the canonical documents contradicted each other. That file was the only place several working corrections existed, and it sat in one of 68 session folders — so runs starting elsewhere never got them.

Only the general rules are here. Project-specific content (1907 righteous-army costume research, that project's folder bans, filenames, character sheet paths, block cursor) stayed with the project and does not belong in a reusable skill.

Local rules copies inside project folders are not allowed going forward. Project exceptions belong in that project's `docs/project_overrides.md`, citing a clause number.

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

## One protagonist per frame

- A scene has exactly **one** of a given character. Never duplicate the same face/costume into the background.
- Supporting characters get distinct faces, builds, costume colours, and roles.
- "Slightly older" means a subtle age shift **on the same sheet**, not a new person.

## Source frames must be filmable

A still that reads as a poster is a bad I2V source even when it is a good picture. Reject with `VIDEO_FRAME_STATIC_POSTER_FAIL` when the frame lacks:

- a **mid-action moment** rather than a settled pose;
- asymmetric / off-centre framing;
- a diagonal axis of movement;
- foreground occlusion or parallax;
- near / mid / far depth;
- an exit the camera can continue into.

Typical failures: subject standing centred; subject on a summit merely looking at scenery; two sides squared up in a symmetrical stand-off.

## Emotion must have a cause

Each image states the preceding event, the body's reaction, the expression, and the gaze direction. If expression and event disagree, hold it as `EMOTION_CAUSALITY_FAIL`.

## Creative mode without the light-match crutch

- Creative means inventing **camera, action, viewpoint, and physical discovery** — not decorating with transitions.
- Fire, torches, lamps, and firelight are usable only when they are a real prop or action **in that shot**. Do not expand them into cross-scene glue, a "light chain", "answering lights", or a repeated warm-edge / through-aperture motif.
- Light matches between scenes are allowed only on an explicit character-transition beat.
- Other transitions come from the scene's own causes: steam off food, cloth movement, footfall and dust, a door shadow, a hand on a prop, water, smoke, a change of spatial direction.
- Distribute camera grammar across scenes — low three-quarter, side track, overhead, intimate macro, rear follow, long-lens observation, POV, static-to-push — one per shot, chosen to fit.
- Use 2–4 physical layers (steam, smoke, wind, fabric, reflection, foreground occlusion, parallax, focus breathing) and only where the cause actually exists in frame.
- Do not force `calm → discovery → transformation` or a through-aperture opening onto every scene.
- If the same light device repeats in adjacent scenes, or a transition effect outweighs the scene's real action, fail it as `CREATIVE_MOTIF_OVERUSE_FAIL`.

## No generic negative wall

Do not auto-append conservative boilerplate such as `no sudden cuts`, `no exaggerated camera movement`, `no camera drift`. Keep only the role-specific essential locks — face, crop, hand/product contact, text/logo. General defects are caught in QC afterwards, not by padding every prompt.

## Runway board specifics

- One logged-in Chrome `app.runwayml.com` Generate board per project.
- Attach one reference at a time through the native chooser, then confirm the visible `ImageN` thumbnail.
- **Reset is not the X.** It is the circular arrow at the image's top right — `button[aria-label="Reset settings"]`, icon `lucide-rotate-ccw`.
- Generate eligibility is decided by the **visible button colour**: blue = clickable, gray = wait. Never judge by button position, and do not let AX `disabled` / `aria-disabled` / DOM guesses override the colour — that override rule exists because DOM heuristics produced false negatives on a genuinely clickable button.
- Known trap: a `primaryBlue` button carrying `data-soft-disabled="true"` looks blue but does nothing. Colour still decides *eligibility*; if a single click on a blue button yields no accepted card, do not re-click — follow the `ACTIVE_CLICK_NO_CARD` protocol.
- Click Generate once per scene. A click is not a submission — only a visible `In queue` / `Generating` / `Processing` / `Completed` card for that scene counts as accepted.
- Every block: 15s, Creative, Multi-reference, 16:9, **Audio ON**.

## Two-slot queue

- Keep two jobs in flight. When the first card is accepted, immediately attach → verify → preflight the second.
- Once both are running, stop clicking Generate; prepare the next deck's references, prompt, and settings instead.
- Gray button means wait and keep preparing. When it returns to blue, redo the eight-check preflight before clicking.
- Never advance the cursor or re-click just because the button looks blue while no accepted card appeared.
- No extra agent, scheduler, or second browser loop. A single 15-minute status check, only while the queue is genuinely active.

## Queue stall stop rule

If the same submitted card reads `In queue` on **three consecutive** 15-minute checks, record `BLOCKED_RUNWAY_QUEUE_STALLED` and stop that monitor. Judge only on the third; checks one and two get a short status note. Any change — `Generating`, `Processing`, `Completed`, failure, error, card disappearance — resets the counter to zero.

This blocks that external queue, not the project. Resume when the card moves to `Generating`/`Completed` in the same session, or when the user clears the stall and says to resume.

## Completion evidence

- Completion is the **downloaded file**, never a card or thumbnail.
- Record `scene_id`, provider, absolute path, bytes, duration, codec, and QC verdict per file.
- A generated-but-undownloaded result is `UI_ONLY_NOT_DOWNLOADED` and is never reported as complete. Recover it from the session board before judging it missing.
- If a card vanishes, fails, shows a different deck, or a blocker appears: record `BLOCKED` and stop.
