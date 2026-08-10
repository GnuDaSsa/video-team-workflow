# Seedance prompting branch

This branch writes **only what will be visible on screen**. It does not click Runway, watch the queue, or claim completion.

Defaults: 15s, audio toggle always ON (the soundscape is directed in the prompt), naturalism first, medium-aware texture. Reference count follows the request.

## The prompt is written in Korean — 2026-07-29

**Seedance prompts are written in Korean**, creative prompts included.

The reason is review. A prompt the user cannot read is a prompt they cannot approve or correct, and the prompt is a directing decision, not a machine-only string.

- Spoken lines stay verbatim Korean.
- Proper nouns, on-screen text and brand names keep their original spelling.
- Format tokens (`16:9`, `9:16`, `15s`) stay as written.
- If a specific shot comes back badly, revise **that shot's prompt**. Do not roll the language back.

This governs Seedance video prompts only. Image (imagegen) prompt language is decided elsewhere.

## What goes in the prompt, and what never does

The prompt box takes **visible things**. Operational text put there gets rendered — Seedance treats it as something to draw.

Measured on E24 (3,207 chars): `Scene ID`, `REFERENCE ROLES`, gate wording, `EXPECTED`, `EXIT` and a banned-cast list accounted for **1,100 characters — 34% of the prompt** — none of which describes the picture. Only 2,107 characters actually described the shot.

**Never include:**

| Not this | Why |
|---|---|
| `Scene ID:` `Mode:` `Look medium:` | internal identifiers; nothing to draw |
| `REFERENCE ROLES:` role list | that is for whoever attaches the files. `generated styleframe for E23` describes **how a still was produced** — invisible to the camera |
| `CHARACTER-SHEET GATE`, `Scene-reference gate` | QC gates, not instructions to a model |
| `EXPECTED: … Audio ON in UI` | UI settings |
| `EXIT: hands off to next scene` | an edit note |
| file paths, project names, status values | operational |
| lists of banned characters | see Negatives below |

**Do include:** the visible scene, what the subject does and shows, one camera move, physical motion, sound, how the 15 seconds are spent, and the closing frame.

All the metadata lives in the **handoff package**, a separate file. Keep `*_prompt.txt` prompt-only so pasting the whole file is always safe.

## Structure

```
STYLE        medium, texture, lighting, colour        ┐
CONTINUITY   identity, costume, props, spatial rules  ├ shared across the sequence;
DIRECTION    camera grammar, pacing, sound character  ┘ do not rewrite per shot
SHOT         the one event that happens in this cut   ← the only block that changes
TIMING       how the 15 seconds are spent
SOUND        what should be heard
```

A change of medium, character rules or camera grammar starts a new sequence — it is not something to slip into one shot.

## Writing the SHOT block

- **One event.** Cause → contact → response, all visible.
- Start from the visible composition of `@Image1`.
- **One camera move.** Do not stack tricks into 15 seconds.
- 2–4 physical layers, and only where the cause is actually present in frame (steam, cloth, reflection, foreground occlusion, dust, vibration, focus breathing).
- Specify the closing frame — stable enough for the next cut to take over.
- Do not name emotions; show them. Not "he is sad" but "his gaze drops and his shoulders lower."

## Sequence progression gate

A valid standalone shot is not enough. Before attesting block N, compare it with
the immediately preceding story block and record a `story_progression` note in
the handoff package with four items: `incoming_story_state`,
`narrative_delta`, `causal_bridge`, and `outgoing_story_state`.

- The visible event must reveal new information, change an action or
  relationship, complicate a prior cause, or resolve it. A repeated location,
  prop, or mood without one of those changes is a prompt repair, not a new
  story block.
- The opening action must be understandable as a consequence of the previous
  block, and the closing frame must create a concrete handoff to the next one.
- Queue order, accepted-card count, visual polish, and a new background never
  substitute for narrative progress.
- If the causal bridge or narrative delta cannot be stated in one plain
  sentence, return to the block map and repair the prompt before attestation or
  Runway submission.

## Sound

Leave the audio toggle ON and **write the sound you want**: room tone, contact sounds, footsteps, cloth, wind. Ask for music when the shot wants music — it is not forbidden.

Write dialogue as verbatim Korean in quotes, with the delivery (breath, pauses, volume) beside it.

## Negatives — keep them short

Do not attach a habitual list of prohibitions.

- One or two risks **specific to this shot**: face identity, hand/product contact, on-screen text.
- Control the cast **by stating who is present**, not by listing who is banned: "only Minjae and Eunyu are in this room" is shorter and more precise than enumerating every unwanted relative.
- Everything else is caught by QC afterwards. Filling the prompt with defensive wording crowds out the description.

## References

- Count follows the request — commonly 3–4, sometimes a character sheet plus a background. There is no minimum, and a file is never attached twice to reach a number.
- `@ImageN` numbering is **not a narrative order**. Each reference is an independent anchor for look, space, props and plausible action, not a sequence to replay.
- Build the deck from **this shot's own material**. Padding with neighbouring cuts' frames makes adjacent clips look like the same shot.
- When a recurring character appears, attach the approved clean sheet (`CHAR_<ID>_PROVIDER_REF_R<n>`) alongside the scene references.

## Length

**Target 700–1,500 characters; 3,500 is the hard limit.** Stripping operational text usually lands you inside the target on its own. If you are approaching the ceiling, suspect operational contamination before assuming the description is too detailed. When the user explicitly selects compact natural-language cards, follow the user-directed exception in `seedance-field-lessons.md` rather than padding the visual prompt to this default.

## Authoring isolation

Prompt authoring is a single sequential foreground operation. It may read approved local files, write the package, and call the runtime prompt bridge. No browser, Computer Use, `osascript`, file chooser, queue observer or background job belongs in this branch. The six Creative roles are sequential review passes, not parallel workers.

## Before handing off

- no sentence that describes something invisible
- one event in the SHOT block
- one camera move
- every physical layer has a cause in frame
- the closing frame is specified
- spoken lines are verbatim Korean
- length is inside the target

Then hand the prompt file and the package to the production branch. UI operation is its job.
