# Session monitoring: active state and scheduling intent

## Evidence and scope
The user explicitly requested ongoing diagnosis of an active planning/production
task. The owning review task registered one native 20-minute heartbeat; no
production browser or additional agent is started. Private observation evidence
is under `/Users/gnudas/Documents/영상작업/workflow-monitor/blue-orbit/`.

Repeated scheduling-intent loss is now reproduced with a second project's
`monitoring.kind=heartbeat,status=ACTIVE` shape. Its missing continuation mode
currently falls back to foreground. Nested current rollups retain swapped card
assignments and In queue states after corrected, processed outputs. A scoped
heartbeat also continued after those outputs were harvested; recent task failures
explicitly report Codex usage limits, not Runway failure or model intelligence.

## Acceptance
- Recognize active native-monitor metadata as scheduling intent, not registration
  proof. Without a hash-bound mode selection, fail closed before writes/sleep.
- Read-only audit detects nested current-rollup mismatches against known queue
  history, including state and card assignment. Missing/unrelated historical
  rows must not be treated as completed jobs or auto-reconciled.
- Check both registration_status and native status/kind claims for local receipt
  evidence; local files still do not prove native execution or playback QC.
- A short scheduled check examines its declared scope before accessing the board,
  distinguishes model-limit failures, and does not expand scope after completion.
- Add positive/negative regressions and run the existing suite. Preserve all
  unrelated dirty files. Commit/push a bounded canonical improvement.
- Do not mutate target production files or hot-deploy while its owner is active.
  A pending safe-boundary deployment is explicit, not called applied/live.

## Non-goals
No automatic prompt rewrite, global creative taste changes, model switching,
provider submission/download, independent browser loop, scheduler backend, or
claims that technical/assignment QC establishes full-motion quality.

## Verified result
143 tests (7 new), Python compile, shell syntax and diff checks pass. Read-only
source audit reproduces two nested current-rollup mismatches, missing schedule
mode/receipt linkage, and two candidate-video registry hash mismatches. Evidence
was sent once to the production owner; no project or browser mutation. Native
20-minute registration and actual native runs are verified. The later audit found
38 checks of a non-running owner: observe-only was mistaken for continuation.
The user requested repairing that gap. The existing heartbeat now permits bounded
resume of the same idle production owner, with pending-delivery deduplication,
actual checkpoint acknowledgement, and pause after missing consumption or three
no-progress consumed checks. No second scheduler or UI owner is introduced.
143 existing tests and syntax/diff checks pass; these do not establish live
continuation delivery/consumption. Canonical deployment at the observed idle boundary passed 66-file parity (2
changed files). One existing-owner resume was delivered and a new active turn
was verified. Fresh provider/artifact consumption remains pending; no further
resume may be sent while that handoff is outstanding.
