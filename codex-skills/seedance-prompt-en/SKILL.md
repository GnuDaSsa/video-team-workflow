---
name: seedance-prompt-en
description: Author visual-only Seedance 2.0 video prompts. MUST load whenever Seedance, Runway Seedance, multi-reference video prompt, I2V prompt, or video-generation prompt writing is requested.
---

# Seedance 2.0 Prompt Authoring

## Scope

This skill writes the **video prompt only**. It does not operate Finder or Runway UI.

When a task includes actual Runway/Seedance UI work, first read `/Users/gnudas/.codex/skills/seedance-operator-protocol/SKILL.md`. That protocol is the single authority for uploads, Generate, queues, and downloads.

## Prompt contract

Write one compact visual contract, normally 700–1800 characters and never more than the visible 3500-character Runway limit.

Use this order:

1. **Shot premise** — a concrete visible situation and emotional temperature.
2. **Reference roles** — `@Image1` etc. describe only the visible job of each image.
3. **Motion arc** — 10–15 second timing, with a single dominant camera move and a physical action/change.
4. **Continuity locks** — only identity, crop, prop geometry, and essential safety constraints.
5. **Sound** — only when the scene package requests it.
6. **Short safety tail** — no readable text/logo/caption, no identity drift, no artifact category relevant to the shot.

## Reference roles

References are anchors, not cages. Describe a visual role, never local provenance.

Good:

```text
@Image1 anchors the lakeside campfire composition and warm foreground glow.
@Image2 controls a close flame texture used as a transition aperture.
@Image3 establishes the moonlit forest depth after the transition.
@Image4 anchors the distant lookout viewpoint and safe spatial tension.
```

Bad:

```text
@Image4 is the Gongnyang source frame from Bundang-ri.
@Image2 defines the historical person named ...
```

For continuity-critical character scenes, references may include the approved character sheet, current production frame, and adjacent continuity frame. Do not claim an unverified sheet attachment.

## Motion writing

A generated clip needs an event, not a still image with a zoom. Specify:

- one dominant camera grammar: creep, track, orbit, rack focus, reveal, handheld follow, or locked frame with actor movement;
- an observable subject action;
- an environmental layer: flame, smoke, wind, water, fabric, crowd flow, dust, light, or shadow;
- a transition only when the story needs one.

For 15 seconds, use four beats at most:

```text
0–3s establish physical action.
3–7s camera commits to one move.
7–11s the story change/reveal occurs.
11–15s land on a usable exit composition.
```

Avoid a four-shot slideshow unless the scene explicitly needs montage. A story-continuity bridge should normally be a single through-action/one-take.

## Visual-only boundary

Do not put into the final prompt:

- proper names, political/historical labels, captions, narration, contest names, place labels not visible in frame;
- artist names or imitation wording;
- Gongnyang, imagegen, model names, source-frame, prompt pack, provenance, QC, files, or folder names;
- needlessly policy-risky weapon close-ups or graphic harm.

Put facts, names, dates, and explanatory statements in the separate caption/narration package.

## Crop and identity locks

Use strict crop language only for fragile shots:

```text
preserve exact crop; do not zoom out; do not reveal a full face;
only eyelid, iris, reflection, and breath micro-motion.
```

For normal scenes, do not over-lock every camera and body part. Leave staging, blocking, and environmental rhythm to the model.

## Prompt quality check

Before handing off, verify:

- one scene, one motion goal, one exit composition;
- every reference has a visible role;
- the prompt asks for action, not a static pan/zoom;
- no hidden workflow/provenance terms;
- no unneeded facts, names, or policy-risk labels;
- no readable in-frame text requested;
- within 3500 characters.

## Output format

Return:

```text
Scene ID:
Visual prompt:
Reference roles:
Expected duration/audio:
Caption/narration notes (not for Runway prompt):
```

## Archived detail

The pre-consolidation guide, including older voice patches and research notes, is preserved at:
`/Users/gnudas/.codex/skills/seedance-prompt-en/archive/SKILL.pre-consolidation_20260721.md`.
It is reference material, not a live operational rule source.
