# Explicit Seedance 2.5 skill contract

## Objective

Add a dedicated Seedance 2.5 skill that is selected only when the user
explicitly names Seedance 2.5. Keep generic Seedance work and every explicit
Seedance 2.0 request on the existing `seedance-prompt-en` path.

## Architecture

1. `seedance25-prompt-en/SKILL.md` is a narrow version router.
2. Version-specific behavior is split only into:
   - `prompting.md` for prompt/reference/mode design;
   - `production.md` for visible Runway settings, submission, recovery, queue,
     download, and QC.
3. Runtime rails, media registry, safety gates, single-agent execution, one
   Aside tab, and the foreground-wait contract remain shared.
4. The 2.5 production helper is a thin version-policy adapter over the existing
   canonical Runway helper. It does not fork browser, upload, queue, or recovery
   implementation.
5. A 2.5 prompt package records `provider_model: Seedance 2.5` and
   `provider_skill: seedance25-prompt-en`; absent those fields, production falls
   back to the established 2.0 path rather than guessing.

## Prompt quality contract

- Prefer the minimum sufficient reference deck, with one narrow role per
  `@ImageN`, `@VideoN`, or `@AudioN`.
- Choose Reference, Keyframe, Edit, or Extend from the actual continuity or
  repair problem; do not treat Reference as the universal mode.
- Replace generic “cinematic/dynamic/high quality” wording with visible
  anticipation, weight transfer, contact, reaction, settle, camera path,
  environmental response, and a readable end state.
- For 2D/stylized animation, define key poses, spacing, held frames, controlled
  overshoot/follow-through, line stability, and restrained background parallax.
- Timestamps guide pacing and sequence but are not represented as frame-accurate
  guarantees.
- Failed clips return to prompting with one diagnosed variable changed; a large
  negative wall is not a repair strategy.

## Production contract

- Immediately before every Generate, visibly read the closed model control and
  require exactly `Seedance 2.5`; a remembered selection or prior card is not
  evidence.
- Duration remains project-lock-owned. Seedance 2.5's longer capability does
  not silently change the established 15-second workflow default.
- Resolution, mode, reference thumbnails, Korean prompt hash, and audio state
  must match the current package before Generate.
- Completion requires a downloaded, probed, registry-backed file plus visual
  and audio QC; a Runway card is not completion.

## Acceptance checks

1. Skill validation passes with no scaffold placeholders.
2. Natural requests that explicitly say `Seedance 2.5`/`씨댄스 2.5` match the
   new skill description; generic Seedance and explicit 2.0 are excluded.
3. The 2.5 adapter accepts a visible 2.5 label and rejects 2.0 while the original
   2.0 helper remains unchanged and rejects 2.5.
4. Prompting and production remain serial phases with no agent spawn, scheduler,
   second browser, or background observer.
5. Canonical source and deployed skill directories match byte-for-byte.

## First-party capability sources

- ByteDance Seed, “Introducing Seedance 2.5” (2026-07-31):
  <https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5>
- Runway, “Creating with Seedance 2.5”:
  <https://help.runwayml.com/hc/en-us/articles/53542207042323-Creating-with-Seedance-2-5>

## Release boundary

This adds an opt-in provider-version path. It does not change submitted jobs,
existing project locks, current queues, the generic Seedance default, or the
user's approval requirements for external actions.
