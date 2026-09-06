# Cycle audit: explicit scheduled checks before foreground waits

## Evidence
Romance-anime live cycle accepted two 15s Seedance2.0 jobs with ten enlarged verified attachments and exact prompt hashes. Owner repeatedly waited despite user scheduled-check intent. Native automation tool returned a proposal card only; active registration/run evidence was not captured. Completed UI now contradicts local In queue state, stale native blockers and zero registered videos.

## Contract
- Same owner, no new agents/automations/browser mutations during this audit. Preserve independent dirty work and provider jobs.
- Persist explicit project continuation selection with hash-bound local user-request evidence. Scheduled selection means queue-cycle checkpoints once and never sleeps; direct queue-wait also fails closed. Existing foreground mode remains compatibility, never substitutes for an explicit scheduled request. Mode changes refuse a live foreground wait.
- Native app tools alone create/inspect/pause real scheduled tasks after specific approval. Local selection/checkpoint is not registration. Report proposed/registered/first-run evidence independently; do not infer scheduler existence from a PID or model.
- Read-only consistency audit compares active state/manifest/lane/queue and actual registry video presence; retain UI_COMPLETE vs DOWNLOADED vs QC evidence. Do not auto-mark creative PASS.
- Exit requires a justified terminal/interruption/scheduled-checkpoint state, not an arbitrary may_stop=true. Same-owner two-slot refill, immutable prompt/identity gates and Astra/Luna routing remain unchanged.
- Add positive/negative scheduled/foreground tests, model-independence, no-side-effect checks, forged-exit regression, stale-state audit fixtures. Verify full existing test suite, strict deployment parity, isolated commit and push.

## Non-goals
No new scheduler backend, daemon, lane, account permission or provider generation. No retuning creative prompts from unreviewed video. No assertion that proposal means active schedule or that UI completion means local delivery/QC.

## Result
136 tests (13 new) and 66-file deployment parity PASS. Actual project scheduled checkpoint returned without waiting, direct wait rejected, interrupted wake consumed, four stale rollup/blocker issues reconciled to zero. Source changes limited to canonical helper/selected production routing; no new scheduler or agent. Detailed audit and unverified media/registration work: docs/releases/2026-09-07/cycle-audit.md.
