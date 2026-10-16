# Seedance queue continuation controller contract — 2026-08-18

## Objective

Keep the owning Codex Seedance turn attached without repeated user prompting:
keep up to two distinct Runway jobs active when capacity allows, arm the next
eligible package before waiting, hold exactly one bounded 15-minute foreground
tool session in the same turn/browser, and continue draining active jobs through
download/QC.

## Failure being corrected

The written workflow already required two-slot throughput and a same-turn wait,
but the helper only wrote `resume_contract.json`; it did not create a bounded
wait or prove that one was running. Legacy projects were rejected because the
helper required v4 `manifest.json` and `state.json`. Project status could then
remain stale while the browser advanced, so a later turn resumed from the wrong
scene and considered a previously consumed wake permanently exhausted.

## Decisions

1. `seedance-prompt-en` remains the only owner of Runway queue procedure.
2. Add a deterministic `queue-sync` checkpoint after every visible board
   change. Its canonical `queue_runtime.json` supersedes stale ad-hoc queue
   fields for continuation decisions without deleting legacy status history.
3. Add a foreground, bounded `queue-wait` command. It writes the wait contract,
   records one live `wait_pid`, and sleeps for exactly 900 seconds in the same
   Codex tool call. It is not a scheduler, daemon, recurring cron, agent, or
   second browser loop. If the shell tool yields a session ID, the owning Codex
   turn must poll that exact session until exit; a detached timer or log writer
   cannot re-enter model reasoning.
4. Timer completion records `WAIT_ELAPSED_RECHECK_NOT_CONSUMED`, not a fired
   wake. The debt clears only after the owning turn visibly reads Runway and
   runs `queue-sync --from-wake`.
5. `resume-contract` supports both runtime-v4 projects and legacy projects with
   `i2v/seedance/status.json` or `lanes/seedance/status.json`.
6. A contract file alone is not a scheduled wake. Stopping after only writing
   the contract is a workflow failure.
7. `SHELF_EXHAUSTED` and `ALL_REMAINING_BLOCKED` are terminal only after the
   active Runway queue and completion/download backlog are empty. Active jobs
   require a draining foreground wait.
8. Three unchanged `In queue` observations after consumed waits produce
   `BLOCKED_RUNWAY_QUEUE_STALLED`; any state/signature change resets the count.

## Acceptance criteria

1. One active job plus available shelf yields `FILL_FREE_SLOT_NOW` and cannot
   enter a wait.
2. Two active jobs plus an unarmed next package yields
   `ARM_NEXT_BEFORE_WAIT`.
3. Two active jobs plus an armed next package yields
   `QUEUE_FULL_WAKE_REQUIRED`.
4. `queue-wait` refuses to run for a free slot, unarmed available shelf, a
   completed card awaiting download, or an already pending wake.
5. An elapsed wait returns `WAIT_ELAPSED_RECHECK_BOARD_NOW`, remains unconsumed,
   and requires an immediate visible board read plus `queue-sync --from-wake`.
6. Active jobs with an exhausted/blocked shelf yield
   `DRAIN_QUEUE_WAKE_REQUIRED`; only an empty queue may become terminal.
7. Legacy and v4 wait contracts both include queue-runtime hashes, explicit
   `automatic_model_reentry=false`, one live wait maximum, zero additional
   agents, and zero resident processes.
8. Unit tests cover free-slot fill, arm-before-wait, bounded wait, unconsumed
   elapsed debt, live-PID validation, draining,
   legacy state, completed-card processing, and three-wake stall detection.
9. A yielded shell session is not a valid turn end: the owning turn keeps
   polling it and must consume the elapsed verdict through a board observation.
10. “One foreground wait” means at most one pending wait, not one wait for the
    whole turn. Wake 1 or 2 with `may_stop=false` immediately enters the next
    sequential wait in the same owner.
11. `queue-exit-check` fails before a final response unless the queue reducer
    has produced `may_stop=true`. A stale `status:"RUNNING"` without a live lane
    owner PID is `STOPPED_INCOMPLETE`, not evidence that the turn still exists.
12. Refill-first throughput: when a settled card frees a slot and an eligible
    package remains, restore two active distinct jobs before processing the
    settled-card backlog. Once both slots are active, download/QC/register the
    backlog while the replacement pair generates.
13. `--processed-job SCENE|OUTPUT` persists completion handling even when the
    provider card remains visibly Completed; the same card cannot cause an
    infinite settled-backlog loop.
14. Production uses `queue-cycle`, which atomically performs visible-board sync
    and the required foreground wait. `queue-sync` plus optional later
    `queue-wait` is no longer the production path.
15. A status-declared attested block cannot disappear behind
    `shelf_state=EXHAUSTED/ALL_BLOCKED` unless it is represented by the current,
    armed, or next package, or explicitly recorded under
    `blocked_attested_blocks` with evidence.

## Out of scope

- Creating a resident observer, cron, background daemon, second browser loop,
  or extra agent.
- Clicking Runway Generate without visible preflight.
- Changing Credits/Max mode.
- Migrating legacy project media into runtime v4.
- Public upload, publishing, payment, or submission.
