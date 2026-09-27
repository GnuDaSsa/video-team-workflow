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
- Source commit `f2835c3` pushed to canonical GitHub main before installation.
- Official native deploy applied the five expected changed/new files; complete
  managed native `--check` returned `PARITY OK`. No unrelated native drift.
- Official Codex `apply-scoped` deployed only the three listed files below.
  Independent source / release-manifest / installed SHA-256 comparisons PASS:

| Installed target (home-relative) | SHA-256 |
| --- | --- |
| `.codex/skills/seedance-prompt-en/aside-operator.md` | `56fbc36cff6a1292441bb5a90c846fab2b8387e71578ca2807743c9d55f4b8f3` |
| `.codex/skills/seedance-prompt-en/scripts/runway_ui_helper.py` | `5d4846e181075e77aa7f4f472262bb303b1ea1e97a46bb6c933657ad0ed3a95f` |
| `.codex/skills/videodirector/SKILL.md` | `d5491b732f342d5624e5bf976df127c9d6b0de55e742d5033ffca29a76e08939` |

- Installed CLI offline smoke: known FILL_PROMPT returned DIRECT; semantic input
  without current-scope approval returned OWNER/JEV_SCOPE_APPROVAL_REQUIRED.
  Neither created a classifier ledger; neither authorized execution.
- Reran the installed routing suite: 38/38 PASS (included in, not additional to,
  the 706 unique source tests). No live transport or UI in this check.
- Native backup (account-relative):
  `.workflow-backups/2026-09-27T15-22-34-424Z-e5acb1a1-ccaf-4bf1-9e19-c4da7322cdc9`.
- Codex backup (home-relative):
  `.codex/archive/20260928_002234_650744_scoped_video_release`.
- Full Codex parity was intentionally not run/claimed: unrelated live
  `model_routing.py` drift is outside the scoped release.

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
