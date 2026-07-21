---
title: Video Image QC Style and Motion Continuity
created: 2026-05-26
updated: 2026-05-26
type: concept
tags: [video, workflow, multimodal]
sources: [raw/transcripts/video-team-image-qc-style-continuity-correction-20260526.md]
confidence: medium
contested: false
contradictions: []
---

# Video Image QC Style and Motion Continuity

This page turns a production failure in the 보훈 영상 rerun into reusable Image QC rules for [[video-team-seed-system]] and [[video-project-seed-template]].

## Core rule

Image QC is not only technical file QC. PASS requires three layers:

1. file/provider validity: path, dimensions, provenance, no text/logo/watermark;
2. art-direction fit: style, palette, medium, era, and planned visual contract;
3. block motion grammar: ordered references must read as clean sequential states for Seedance.

If any layer fails, the reference is not `APPROVED_FOR_I2V`.

## Style-lock gate

When Planner/Director specifies a section as sumi-e, ink-wash, hanji paper, monochrome memorial, brush-line, or restrained public-campaign style, Image QC must fail references that drift into photorealistic/live-action frames unless the Block Map explicitly marks a present-day color return.

Examples:

- 수묵화/한지 planned section + realistic city/actor/photo style → FAIL/REWORK.
- monochrome memorial section + saturated modern sports color before the planned color-return beat → FAIL/REWORK.
- present-day baseball return block explicitly marked color restoration → may PASS if logos/text are absent and transition timing is correct.

## Motion-state isolation gate

For action/transformation blocks, one reference equals one beat/state. QC must reject images that merge multiple temporal states into one composition.

Required examples:

- throwing sequence: pre-throw windup → release/post-throw pose → object in flight close-up → transformation state → landing/catch state.
- object transformation: source object alone → source object in motion → intermediate morph → destination object alone.
- style transition: old medium → transitional bridge → new medium, not both as an unmotivated collage.

Fail cases:

- lunchbox bomb and baseball visible together in the same reference before the intended morph beat;
- thrower, thrown object, destination ball, and final sports state all collapsed into one poster-like frame;
- multiple time states of the same object composited without a clear sequential purpose.

## 보훈 rerun lesson

The B08 lunchbox-bomb to baseball passage should read as:

1. historic silhouette winding up to throw;
2. throw release/post-throw body line;
3. lunchbox/object close-up traveling through air;
4. object morphs into a baseball-like sphere through white ink/air streak;
5. white flash/breath into modern baseball catch sequence.

If the generated images show the lunchbox and baseball together in one still frame, or if the pose sequence is unclear, QC must route to image rework, not Seedance.

## Runtime consequences

- Image Creator prompts must include style-lock language and explicit one-state-per-reference language.
- Image QC must inspect block continuity against `lanes/planner/block_map.json`, not only individual files.
- A complete block cannot be handed to Seedance until the block-level motion grammar passes.
- For contest/public films, planned visual style is part of compliance and message clarity; drifting into generic realism is a blocking issue.

## Related pages

- [[video-team-seed-system]]
- [[video-project-seed-template]]
- [[tourism-mv-seed]]
- [[seedance-prompting-knowledge]]
