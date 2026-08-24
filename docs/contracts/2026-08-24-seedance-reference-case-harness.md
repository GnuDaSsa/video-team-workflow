# Seedance reference-case prompting harness contract — 2026-08-24

## Goal

Make the five user-supplied Seedance examples the superior creative and
prompt-construction authority over pre-existing general prompting defaults.
Existing rules may fill an unspecified gap, but may not shorten, simplify,
reframe, or veto a directing choice established by the examples.

## Authority order

1. The user's current explicit instruction and project brief.
2. The user-supplied reference examples, activated as
   `user_reference_superior_v1`.
3. Project identity, story, music, continuity, and approved-asset locks.
4. General Seedance prompting defaults, adapters, target lengths, and house
   style.

Safety/rights gates, visible provider capability limits, verified attachment
binding, and exact user-selected settings are mechanical execution boundaries,
not competing creative rules. They remain non-bypassable. When an example uses
external placeholder syntax or exceeds a visible provider duration, preserve
its directing structure while translating the syntax or splitting the duration
at a causal boundary; do not downgrade the content to an older default.

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

## Mechanical normalization and internal resolution

- `{{Mixed N}}`, `@HARIN`, `@Image 1`, `(Audio1)`, or any other alias that is
  not compiled to the provider-visible canonical token (`@ImageN`, `@VideoN`,
  `@AudioN`).
- One token or alias naming different performers, or one performer silently
  changing token between sections.
- `one-shot` combined with rapid-cut tempo is interpreted as fast performance,
  reactive handheld reframing, and cut-like rhythmic acceleration without an
  edit when the authority contract records that resolution. It is not rejected
  merely because an older one-move default dislikes the density.
- A multi-phase or multi-shot timeline with gaps, overlaps, or no final-duration
  coverage.
- An attached master track plus invented music/vocals, or non-performers
  mouthing the lead vocal.
- Simultaneously requiring and forbidding the same normalized visual feature,
  including the observed lens-flare contradiction.
- Exact Hangul or spoken Korean requires a literal-string contract and
  result-specific QC. The examples authorize native Seedance Korean dialogue
  without `@AudioN` when `native_seedance_user_reference` is explicitly selected;
  a performed `@AudioN` guide remains the higher-fidelity optional route.
- External Chinese/English examples pasted directly into the provider. Their
  structure is distilled, but the final model-facing Seedance prompt remains
  Korean.

## Conditional semantic rules

The package activates only the applicable checks in `prompt_rules_used`:

- `user_reference_superior_v1`
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
- It rejects unresolved provider tokens, duplicate/conflicting cast aliases,
  timeline gaps, unresolved one-take/cut meaning, lipsync ownership failures,
  dialogue without either an authorized native route or performed guide,
  effect contracts without physical causality, and unresolved require/forbid
  contradictions.
- Repository quick verification passes, and deployed source/live hashes match
  for the files changed by this contract.
