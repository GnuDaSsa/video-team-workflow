# Image QC — is this still usable as an I2V source?

Owner: the `image_qc` lane. These are **review verdicts**, not prompt instructions.

They were previously buried in the Seedance prompting file, so the lane that actually reviews stills never saw them and the verdict codes below existed only in a prompting document. A still can be a good picture and still be a bad I2V source; that judgement belongs here.

Verdict codes: `VIDEO_FRAME_STATIC_POSTER_FAIL`, `EMOTION_CAUSALITY_FAIL`.

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

## Relation to other rules

- Composition intent (shot distance, camera angle) is set at prompt time — see the global distance/angle contract.
- Identity comparison against the approved character sheet is the character-sheet gate, checked both here and again at Seedance attach time.
- Passing this review is what earns `BLOCK_READY_FOR_I2V`.
