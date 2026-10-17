---
name: seedance-prompt-en
description: Seedance 2.0/default workflow dispatcher for one owning lane. Use for explicit 2.0 requests or generic Seedance work when 2.5 was not named; explicit Seedance 2.5 requests belong to seedance25-prompt-en.
---

# Seedance workflow dispatcher

Explicit `Seedance 2.5` / `씨댄스 2.5` → stop and load
`../seedance25-prompt-en/SKILL.md`. Explicit 2.0 or generic Seedance → continue
here. Never load both version branches for one block.

One Seedance lane runs two sequential phases. Runtime AGENTS §1.3 owns model
attribution and any approved optional author handoff.

## Read in this order

**Prompting phase** (preprod P4 shelf, or legacy authoring) — always:

1. `seedance-shared-contract.md` — invariants (duration lock, Audio + dialogue
   table, English, deck and character-sheet gate, `GENERAL_REFERENCE_MODE`).
2. `seedance-prompting.md` — **the one template** and the shelf workflow.
3. `examples/` — gold prompts that pass `preprod.py shelf-check`:
   `01-single-shot-live-action.md`, `02-three-shot-2d-animation.md`,
   `03-two-shot-product-macro.md`, `04-bad-to-good.md`.
4. The block's `brief.md` and, if listed there, its knowledge packet only.

Review lenses — load only when the block has that risk; none is a template:

- `prompt-review.md` — general same-owner review (camera/physics decisions,
  repeated-failure diagnosis).
- `seedance2-prompt-patterns.md` — method choice, video/audio source roles,
  extension and repair.
- `hell-grind-production-prompting-adapter.md` — multi-entity cast ledger,
  spatial lock, dialogue/lipsync, exact on-screen text, semantic harness.
- `xazinga-prompting-adapter.md` — use/exclude/scope per attachment.
- `seedance-field-lessons.md` — creative mode without light-match glue,
  compact prompts, no negative wall.
- `blender-previs-prompting.md` — Blender/3D previs, animatics, source restyle.

**Production phase, preprod shelf project:** `production-card.md` only — one
`run-block` call per block; open other docs only when a STOPPED result names them.

**Production phase, legacy project:** `seedance-production.md` and `aside-operator.md`. The
canonical executable is `scripts/runway_ui_helper.py`; runtimes may keep a
shim but must not fork Runway UI/recovery logic.

Not loaded by default: `incidents.md` (history), `image-qc-source-frame-standard.md`
(image QC lane).

## Non-negotiable gates

- Preprod projects: production pastes the released shelf `pack.json` and never
  writes or edits a prompt. The locked storyboard outranks
  `user_reference_superior_v1` (legacy opt-in; the 2026-08-24 example texts
  were never stored — see `runtime/scripts/seedance_prompt_case_harness.py` and
  its cases in `runtime/tests/test_seedance_prompt_case_harness.py`).
- Before every Generate: `scripts/runway_ui_helper.py settings-verify --project
  <p> --block <BLOCK> --visible-model '<label>' --duration-sec <seconds>`
  (Seedance 2.0 only); re-run after recovery, refresh, wake or deck change.
- Runway visible Aside is the source of truth: attach `aside repl` to the
  existing Runway tab by exact `targetId`; no other browser, API, hidden input
  or coordinate route. Checkpoint before `ATTACH`; recovery, queue
  (`queue-cycle`, `queue-doctor`, `queue-exit-check`, two active jobs) and
  completion evidence are owned by `seedance-production.md`.
- Character-sheet gate, duration lock, Audio: `seedance-shared-contract.md`.

Prompting is single-agent, sequential and non-GUI (no workers, schedulers,
observers, browser, Computer Use, `osascript`, file chooser). After the shelf is
locked (or a legacy pack attested) the same lane uses the
single visible Aside route.
