# Generation duration lock contract — 2026-08-19

## Failure being corrected

The KiiiKiii Pop Off project had an explicit 15-second production correction,
but that decision existed only in prose. Later Seedance packs inferred 5 seconds
from their single-action beat budget, passed attestation, and were submitted at
5 seconds. The UI did not cause the drift: the wrong duration was already in
the prompt pack.

## Authority

- Planner/project workflow owns duration selection and changes.
- Seedance prompt authoring consumes the locked duration; it never infers or
  shortens it from prompt complexity.
- `prompt_packet_utils.py` attests that the pack duration matches the project
  lock.
- The Seedance-skill UI helper verifies that the visible Runway duration
  matches the attested duration immediately before Generate.

## Canonical artifacts

- Runtime v4: `lanes/planner/generation_duration_lock.json`
- Legacy: `i2v/seedance/generation_duration_lock.json`
- Schema: `seedance_generation_duration_lock_v1_20260819`

The lock has a 15-second workflow default and optional block overrides. A
5–14-second value requires `user:<evidence>` or `brief:<artifact>`; a
`planner_revision:<named-revision>` cannot shorten the default by itself.
Revisions retain prior values in the lock history. Prompt action budget and
final edit trim length are never duration sources.

## Required gates

1. New v4 projects start with a locked 15-second duration artifact.
2. Planner must verify that lock before Seedance and may shorten it only from an
   explicit user or brief source.
3. Every Seedance pack declares `duration_sec`.
4. Attestation without `--project`, without a locked duration artifact, or with
   a mismatching `duration_sec` returns `NOT_ATTESTED_DO_NOT_SUBMIT`.
5. Attestation records the lock path/hash and resolved expected duration.
6. Before every Generate, `runway_ui_helper.py settings-verify` verifies that
   neither the attested pack nor duration-lock file changed, requires a freshly
   read visible `Seedance 2.0` model label, compares the visible Runway duration
   to the attested duration, and writes combined model+duration evidence.
7. A mismatching prepared pack is `HOLD_DURATION_LOCK_MISMATCH`; it is
   re-authored rather than changing only JSON or clicking with the old prompt.
8. Submitted outputs are preserved as audited provider history. They do not
   authorize future use of the wrong duration.
9. A short/cut-dense final film normally keeps the 15-second source lock and
   groups 2–4 consecutive, causally related cuts into a Planner-authored
   `PLANNED_MULTI_SHOT_SOURCE`. Attestation verifies the contiguous scene
   timing, unique cut ownership, scene-specific references, and Korean shot
   markers; unrelated shots are never packed merely to consume duration.

## Acceptance criteria

- A 5-second pack under a 15-second project lock cannot attest.
- The same pack re-authored at 15 seconds can attest.
- A 5-second visible UI setting cannot pass a 15-second attestation.
- A visible Seedance 2.5, missing model label, or ambiguous 2.0/2.5 observation
  cannot pass the preflight even when duration is 15 seconds.
- Legacy and v4 projects resolve their respective lock and prompt paths.
- Queue continuation remains independent from duration selection.
