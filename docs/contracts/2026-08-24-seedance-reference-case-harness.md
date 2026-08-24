# Seedance reference-case prompting harness contract — 2026-08-24

## Goal

Promote the reusable structure from five user-supplied Seedance examples without
copying their malformed reference aliases, language drift, timeline gaps, or
contradictory constraints into production prompts.

## Scope

- Canonical prompt-authoring guidance in
  `codex-skills/seedance-prompt-en/hell-grind-production-prompting-adapter.md`.
- A local, deterministic pre-attestation semantic checker in
  `runtime/scripts/seedance_prompt_case_harness.py`.
- Unit tests discovered by the repository harness.
- Selective deployment of the updated skill document and checker. Runway UI,
  queue, upload, and media-completion procedure are unchanged.

## Accepted patterns

1. Bind each reference to an exact visible/audible job and explicitly exclude
   sheet background, layout, labels, and other non-scene content.
2. Give every recurring performer one stable semantic ID, aliases, reference
   tokens, and an exact count before using prose names in the prompt.
3. For multi-shot work, keep global look/composition/performance locks above a
   contiguous timed shot plan. Each shot has action, camera, sound/dialogue, and
   an edit-ready exit.
4. For a single take, separate phase headings from cuts and lock camera side,
   subject placement, lead room, and screen direction across every phase.
5. Translate abstract emotion into gaze, breath, jaw, shoulders, hands, and
   listening reactions.
6. Define non-photonic effects by cause, material mechanism, nearby physical
   reactions, travel, impact, and aftermath.
7. For music performance, make the attached master audio exclusive, map vocal
   intervals, name one performer, keep non-performers silent, and protect face
   visibility through every vocal line.
8. For exact on-screen text or dialogue, record the literal string, language,
   owner, appearance/performance action, and dedicated QC route.

## Rejected or repaired patterns

- `{{Mixed N}}`, `@HARIN`, `@Image 1`, `(Audio1)`, or any other alias that is
  not compiled to the provider-visible canonical token (`@ImageN`, `@VideoN`,
  `@AudioN`).
- One token or alias naming different performers, or one performer silently
  changing token between sections.
- `one-shot` combined with positive rapid-cut/hard-cut direction.
- A multi-phase or multi-shot timeline with gaps, overlaps, or no final-duration
  coverage.
- An attached master track plus invented music/vocals, or non-performers
  mouthing the lead vocal.
- Simultaneously requiring and forbidding the same normalized visual feature,
  including the observed lens-flare contradiction.
- Exact Hangul or spoken Korean requested without a literal-string contract and
  result-specific QC. Spoken final dialogue still requires the shared contract's
  verified performed `@AudioN` route.
- External Chinese/English examples pasted directly into the provider. Their
  structure is distilled, but the final model-facing Seedance prompt remains
  Korean.

## Conditional semantic rules

The package activates only the applicable checks in `prompt_rules_used`:

- `reference_cast_ledger_v1`
- `timed_performance_map_v1`
- `one_take_axis_lock_v1`
- `physical_effect_causality_v1`
- `audio_lipsync_priority_v1`
- `exact_text_dialogue_v1`
- `constraint_consistency_v1`

The checker fails closed for a declared rule whose required semantic-contract
fields are missing. It does not silently rewrite the prompt or invent mappings.

## Acceptance

- The updated live Seedance skill tells the owning lane how to compile these
  patterns in Korean and how to run the semantic harness.
- The checker accepts representative corrected multi-shot, single-take,
  lipsync, and exact-text/dialogue packages.
- It rejects malformed reference tokens, duplicate/conflicting cast aliases,
  timeline gaps, one-take/cut conflicts, lipsync ownership failures, missing
  dialogue audio guides, effect contracts without physical causality, and
  require/forbid contradictions.
- Repository quick verification passes, and deployed source/live hashes match
  for the files changed by this contract.
