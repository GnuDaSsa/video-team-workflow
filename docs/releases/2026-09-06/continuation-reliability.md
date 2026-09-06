# Routine flow and continuation reliability

## Verified findings
- Runtime `next` emphasized optional new-owner dispatch despite the same-owner default. This encouraged needless per-phase approval/model handoff prompts.
- A local historical Luna Runway cron was paused and configured for five minutes. It was not an active 15–20 minute follow-up for the current project. It was inspected, not reactivated or migrated.
- The current canonical queue controller waits 900 seconds in an attached foreground tool session. It cannot schedule a new model turn. A contract file, live PID, elapsed timer, scheduler registration and successful scheduled run are different evidence.
- No paired Luna/Terra provider run establishes a model-caused failure. The diagnostic and controller have no model-specific branch; missing tools, permissions, session binding, stale code and actual scheduler status must be checked first.

## Changes
- `next.default_execution` explicitly selects current-conversation continuation and no extra role-change approval. Optional `next_dispatch` and its specific spawn gate remain intact.
- Same-owner authorized routine production and repeated foreground waits do not ask permission at each step. Safe fresh-session preparation in the one existing Aside tab is routine only after visible idle/preservation checks. Ambiguous accounts, unsaved work, active/uncertain transactions and protected external actions still stop.
- Read-only `queue-doctor` returns canonical helper hash, timer/consumption/orphan state and next action; it creates no monitoring, browser action or state record.
- Stale wiki Chrome/mandatory-dispatch narrative was replaced with canonical pointers.

## What real scheduling would require
Native scheduled tasks are separate from foreground waits. The app supports returning to an existing chat on minute-based intervals; local scheduled work requires the computer and app to remain running. [Official scheduled-task documentation](https://learn.chatgpt.com/docs/automations?surface=app).

The current tool route defaults recurring follow-ups to a current-task heartbeat. Creating an additional surface requires specific initial approval; an unrelated paused cron is not reusable authorization. Registration must be verified by task identity, destination, accepted cadence and active status; successful operation additionally needs first-run and fresh observation evidence. No new heartbeat, cron, agent, second browser loop, or scheduled production-continuation mode was installed in this release.

## Verification
- 110 unit tests; runtime/helper Python compile; deployment shell syntax.
- Identical diagnostic output under Luna/Terra/Astra model environment labels; this verifies deterministic code only, not comparative model performance.
- Real 2.012-second synthetic foreground test: exec yielded a tool session, the same owner consumed it through write_stdin, elapsed debt was present and a fixture recheck consumed it. No browser/provider was used. This is not a live 15-minute monitor test.
- Strict 66-file source/live parity and isolated release sync.
- Not run: real scheduled firing, model-specific browser A/B, Runway generation, media temporal QC or CapCut export.

Current-project smoke: next resolves Seedance production with no routine user-action request, after repairing omitted image-QC block-ready events from verified assets. Media registry audit is clean. Full project validation remains STOPPED_INCOMPLETE because two prepared video blocks have not been generated; no terminal/owner state was fabricated to make that audit pass.
