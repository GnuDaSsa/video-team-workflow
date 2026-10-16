# Scheduled registration execution gate

## Request
Repair workflow-owned automatic scheduling, not the current project's paused automation. No native schedule mutation, thread message, model change, browser loop or generation in this task.

## Root defect
run_queue_cycle returned a no-wait checkpoint and evaluate_queue_exit unconditionally allowed a scheduled turn to end with active jobs and registration_verified=false. A regression test explicitly expected this. Documentation alone required native registration. Prior fixes c35340d/f6ad809 did not close that executable exit.

## Scope
Connect existing queue cycle/doctor/exit to existing native snapshot audit. Pending work with missing, paused, proposed, stale, wrong-consumer or wrong-cadence registration cannot be reported as safely handed off. Provide concrete native tool action, not sleep or a new subprocess scheduler. Native registration is performed by the owning conversation through automation_update within specific approval; current-user pause/HOLD is never overridden. Verify records separately from first-run/action evidence. Stable production prompt reads current scope, never hardcodes V4.8 etc.

## Acceptance
Offline positive/negative tests for the actual helper path; no scheduler/tool side effects. Empty terminal queues remain stoppable. First-run proof is not required before the first scheduled handoff; snapshot compliance never claims a successful run. Scoped patch deploy preserves unrelated drift. Active automation configuration byte hashes unchanged before/after. Actual unattended production remains unverified without a later authorized live test.
