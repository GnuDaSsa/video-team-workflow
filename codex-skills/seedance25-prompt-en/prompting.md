# Seedance 2.5 prompting branch

Use this document only after the version gate in `SKILL.md` selects 2.5. This
branch authors and critiques the package; it never opens Runway.

## Capability envelope, not a promise

Current first-party documentation describes Reference, Keyframe, Edit, and
Extend workflows, 4–30 second generation, 480p/720p/1080p output, and a combined
multi-reference ceiling of up to 50 inputs. ByteDance describes that ceiling as
up to 30 images, 10 videos, and 10 audio files. Treat these numbers as provider
ceilings, not targets: the visible Runway surface and current account state are
the operational truth.

More inputs do not automatically improve consistency. Use the **minimum
sufficient deck** that proves identity, wardrobe, location, object, motion, or
audio roles without asking the model to reconcile competing authorities.

## Choose the mode from the actual problem

| Need | Preferred branch | Prompt consequence |
|---|---|---|
| identity/style/location continuity from several sources | **Reference** | bind each source to one narrow visible function |
| controlled start/end composition or transformation | **Keyframe** | describe the physical bridge and invariant elements between endpoints |
| localized repair of an otherwise useful clip | **Edit** | name the region/event to change and explicitly preserve everything else |
| continue motion, action, or camera beyond an approved clip | **Extend** | inherit the last state and describe only the next causal beat |

Do not use Reference as a universal default. If exact endpoints are the real
constraint, use Keyframe; if most of a clip already works, use Edit rather than
regenerating the whole shot.

## Reference-role compiler

For every attached source, write one role in both the package and the visible
production prompt:

```text
@Image1 is the only reference for the lead's face, head silhouette and age impression.
@Image2 fixes only the front and back construction and color layout of the costume.
@Video1 supplies only the rhythm of foot strikes and weight shifts, not running speed.
@Audio1 guides only the timing and intonation of the spoken line.
```

- Attachment order is not story order.
- One source must not own two contradictory jobs.
- The approved triptych or minimum deterministic crop remains mandatory for a
  recurring character; scene memory and a previous card do not replace it.
- Do not import panel seams, gray identity-sheet backgrounds, absent front
  heads, watermarks, captions, UI, or source defects into the scene.
- When sources disagree, name the authority per attribute instead of saying
  “combine all references.”

## Anti-AI motion contract

The prompt must describe observable mechanics, not quality adjectives. Compile
each planned scene in this order:

1. **Readable opening state** — pose, balance, gaze, contact points, and what is
   already moving.
2. **Anticipation** — a small weight shift, breath, recoil, eye lead, hand set,
   or other visible preparation.
3. **Primary action** — one dominant action with direction, speed curve, body
   mechanics, and exact subject/object contact.
4. **Reaction and environment** — cloth, hair, dust, water, foliage, shadow, or
   another layer responds after the cause, not all at once.
5. **Settle and end state** — overshoot only when motivated, then a readable
   held state the next clip can start from.
6. **Camera path** — one motivated route with speed and stop behavior; it
   supports the action instead of competing with it.

Avoid vague bundles such as “dynamic cinematic animation, dramatic camera,
high quality, smooth motion.” Replace each with a visible event. Preserve quiet
holds: constant whole-frame motion is a common source of synthetic drift.

## 2D and stylized animation

For animation that currently feels cheap or generically AI-made, specify the
animation timing itself:

- Name the opening key pose, anticipation pose, action key, contact pose,
  overshoot/settle, and final held pose when the beat needs them.
- Put speed in **spacing**: short hold → compressed anticipation → two or three
  fast action beats → settle. Do not demand uniform smoothness everywhere.
- Keep face proportions, hand count, costume shapes, line weight, shadow logic,
  and color regions stable across the shot.
- Use smear, speed lines, impact frames, camera shake, and debris only at a
  motivated accent; one accent family per beat is usually enough.
- Let background parallax follow the camera. Do not animate every background
  object independently.
- For a fragile close-up, lock the crop and permit only the necessary micro-
  movement. A full-face reveal from an eye or mouth crop is a failure.

If the user explicitly enables `toonkit_2d_snappy_v1`, apply its pose-to-pose
hold/anticipation/action/overshoot/settle/follow-through grammar from the 2.0
creative adapter, but keep this 2.5 mode/reference/timestamp contract.

## Model-facing prompt layout (Runway Seedance 2.5 guide, 2026-11)

2.5 reads **structured labelled blocks**, not 2.0 flowing prose. Keep the
runtime header and the verbatim STYLE / IDENTITY blocks the shelf brief
requires, then compile in this order:

```text
<N> seconds, <k> shots:
<STYLE block verbatim>
<IDENTITY block(s) verbatim>
References: @Image1 is <one exclusive role>. @Image2 is <one exclusive role>. ...
Summary: <one sentence: who, where, what happens, genre/look, overall camera feel>.
Shot 1 (0-6s): <size>, <angle>, <declared move>. <opening state → anticipation → action → reaction → settle>. SFX: <diegetic sounds of this beat>.
Shot 2 (6-13s): ...
Sound: <whole-take bed>. No music. No subtitles.
Consistency: <2-3 fixed traits per lead restated>, <line/paper/palette invariants>, <prop states that carry across shots>.
End frame: <held, readable final composition>.
```

- **References first.** Every token gets one exclusive role (identity, wardrobe,
  location, object). A loose role such as "for style" leaks unintended traits.
  Do not re-describe a referenced object at length in prose; the model may read
  it as a second object.
- **Summary sentence** anchors all shots into one scene; write it before the
  timeline, never skip it.
- **Timeline.** Contiguous whole-second intervals, no gaps (gaps are ungoverned).
  Default beat 4–8 s; a closing hold 3–4 s. Timestamps are pacing, not frame-exact
  cuts. Say cuts explicitly ("Cut to …") when the shot changes.
- **Compound camera is allowed** inside a beat longer than ~4 s (e.g. locked-off
  hold, then a slow push in). The 2.0 one-move-per-shot rule is not a 2.5 rule,
  but every move still needs a motive and a stop.
- **Restate the primary traits** of each lead (2–3 visible features) at every
  major beat and again in Consistency; 2.5 drifts on long takes otherwise.
- **Positive visuals.** Describe the wanted result. Negatives only for audio,
  subtitles and on-screen text ("No subtitles. No background music,
  environmental sounds only.").
- **Per-beat SFX** lines plus one Sound bed. State whether music is present.
- **Detail density follows resolution.** At 1080p give texture/line facts
  (paper grain, brush-edge, wash bleed) once in STYLE and once in Consistency;
  do not repeat them in every shot.
- **Length.** No length target and no compression; Runway accepts 10,000
  characters. Spend words on staging, timing and causality, not adjectives.

### Runway Unlimited cap

On the Runway **Unlimited** (relaxed) tier, Seedance 2.5 generates at most
**15 s** (user-confirmed 2026-11-07) and **720p** (1080p is credit-mode only on the visible Runway control, 2026-11-07). Unless the user says the job runs on paid
credits, plan 2.5 blocks at 15 s and spend 2.5's strengths on structure,
reference depth and staging, not on length.

### Long-take planning (why 2.5)

Use the 30 s ceiling to keep one emotional scene in one source instead of
stitching 15 s fragments: one location, one light state, 3–5 beats with a
quiet hold between them. Do not fill 30 s just because it is allowed; unrelated
places stay in separate sources. A good 2.5 block reads as a short scene:
establish (often a no-person environment or object insert) → approach →
the one decisive gesture → reaction → held end frame.

## Package and critic gate

The handoff package must include at least:

```yaml
provider_model: Seedance 2.5
provider_skill: seedance25-prompt-en
provider_mode: Reference | Keyframe | Edit | Extend
duration_sec: <project-lock value>
resolution: 480p | 720p | 1080p
reference_roles: <ordered slot-to-role map>
prompt_rules_used: <only the rules actually applied>
revision_target: <one diagnosed variable, or null>
```

Before handoff, reject the package if any answer is “no”:

- Does each reference have one explicit, non-conflicting job?
- Is the primary action physically possible from the starting pose?
- Are anticipation, contact/causality, reaction, and settle visible where the
  action requires them?
- Is there one readable camera path and a usable end state?
- For 2D/stylized work, are pose timing and line/style stability stated rather
  than replaced with “smooth/high quality” adjectives?
- Do all timestamp intervals fit the locked duration without overlap or gaps?
- Are References, Summary, timed shots with SFX, Sound, Consistency and End frame all present, in that order?
- Does the block contain at least one no-person or object shot, and is the acting restrained?
- Does the package explicitly name Seedance 2.5 and the selected mode?

On a failed generated clip, diagnose the failure class and change one primary
variable: source frame, reference role, mode, motion beat, camera path, or local
Edit instruction. Do not append a large negative list to the same prompt.
