# Bounded JEV input routing release

## Scope
- Existing native `jev-dispatch.mjs` gains local-first `route`; no new service,
  owner, browser loop or classifier SDK. Known actions avoid key/network/ledger
  access; semantic classification reuses the bounded original request and ledger.
- JEV output remains advice, not execution authority. Require actual current-scope
  approval before external classification. Missing approval/key, low certainty,
  malformed state, limited calls or service failure return to the current owner.
  Creative/visual decisions do not route to a native author agent.
- Existing Codex prompt paste now treats identical normalized text as no-write
  success, preserves other text, checks visible dialogs before/at/after mutation,
  and does not report a mismatched paste as `ok: true`. Recovery read also blocks
  an obscuring dialog. The original session/pack/language/Generate gates remain.
- Stage-specific native/Codex instructions consume this change without copying
  native author/language/upload policy into Codex.

## Verification
- 489 Node tests PASS, including 38 new routing cases. All classifier transport
  is synthetic; actual model quality is not tested.
- 217 Python tests PASS, including 13 input-transaction cases that execute the
  real callback JavaScript against a synthetic Lexical DOM. No real UI evidence.
- Configured quick checks: Python compilation, shell syntax, git diff check PASS.
- Three updated/affected skill entry validations PASS.
- Reviewed Codex 73-file manifest safety preflight PASS; native manifest frozen.
- First full Node run hit the pre-existing macOS symlinked TMPDIR fixture
  constraint; rerunning with canonical /private/tmp scratch passed. Python's
  historical exact-wording assertion was preserved, then full tests passed.
- No active production helper process was observed and the related recent Codex
  workflow task was idle before release. No other task was resumed or altered.

## Deployment
Pending scoped installation and independent installed checks. Do not read source
success as installed or live behavior success.

## Not tested / not changed
No live JEV request, key disclosure, browser operation, provider Generate, new
media, Korean classification accuracy, full-video/audio QC or end-to-end speed
measurement. No production project, existing hold, pending schedule or user
model setting was changed. Unrelated old-main worktree edits and live
model_routing.py drift remain outside this release. Full Codex parity is not
claimed; only the explicitly deployed source set will be checked.

Next real production run should compare input time/model hops and duplicate or
wrong-field events. A separately authorized JEV shadow sample can evaluate
Korean decisions before broadening its role. Confidence floors are initial
triage settings, not evidence of calibrated production accuracy.
