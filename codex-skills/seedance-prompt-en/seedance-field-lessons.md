# Seedance prompting — field lessons (review lens)

Prompt-authoring corrections proven in production. Apply them **inside** the
template in `seedance-prompting.md`; they add no section. Background stories:
`incidents.md`. Owners elsewhere: `GENERAL_REFERENCE_MODE`, the character-sheet
gate and Audio/dialogue live in `seedance-shared-contract.md`; image QC in
`image-qc-source-frame-standard.md`; Runway board/queue in
`seedance-production.md`.

## References are anchors

- Never write the prompt so `@Image1 → @ImageN` becomes a sequence, match-cut
  or replay order; one generation is one newly composed plan.
- When a background vs identity vs prop distinction protects the result, the
  binding sentences say it, e.g. `@Image1 defines the location, @Image2 anchors
  face and body identity, @Image3 anchors the prop; they are independent
  anchors, not a time order.`
- Two approved sheets for one character (turnaround/face + action/prop): bind
  each to its separate job; do not substitute a single portrait or treat them
  as duplicates.

### Five-image refresh (image batches)

During image batches, re-attach the approved sheet as a real file every fifth
image (5, 10, 15, …) and record `batch_id`, `image_batch_index`,
`character_sheet_refresh_at`, `attached_sheet_path`, `attachment_verified`. This
is on top of the per-generation gate, never a replacement.

## Creative mode without the light-match crutch

- Creative means inventing camera framing within the declared move, action,
  viewpoint and physical discovery — not decorating with transitions.
- Fire, torches, lamps are usable only as a real prop or action in that shot;
  never a cross-scene "light chain" or repeated warm-edge/through-aperture motif.
  Light matches between scenes only on an explicit character-transition beat.
- Transitions come from the scene's own causes: steam, cloth, footfall and
  dust, a door shadow, a hand on a prop, water, smoke, a change of direction.
- Vary camera grammar across blocks (low three-quarter, side track, overhead,
  macro, rear follow, long lens, POV, static-to-push) — in preprod this is
  chosen in the storyboard, one move per shot.
- Physical cues: only those the shot needs; no quota. Each needs a cause in
  frame.
- Do not force `calm → discovery → transformation` onto every scene. A repeated
  light device in adjacent scenes, or an effect that outweighs the real action,
  fails as `CREATIVE_MOTIF_OVERUSE_FAIL`.

## Compact prompts

When the user prefers short natural-language cards, keep the template lines
(header, verbatim locks, bindings, shot sections with their phrases, end frame)
and shorten only the action prose: one cohesive English paragraph per shot, no
label lists. Do not fake concision by dropping identity, contact, sound or the
end frame. Model, settings, QC and paths stay in the pack. Verify in media QC
before promoting it as a quality rule.

## No generic negative wall

Do not append boilerplate such as `no sudden cuts`, `no exaggerated camera
movement`, `no camera drift`. Keep only role-specific locks — face, crop,
hand/product contact, text/logo. General defects are caught in QC.
