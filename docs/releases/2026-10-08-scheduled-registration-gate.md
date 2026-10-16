# Scheduled continuation registration gate

## Defect
The scheduled queue-cycle/exit path permitted a final response with active jobs and registration_verified=false. Prior c35340d/f6ad809 documented registration but did not enforce it. The old regression test explicitly accepted unarmed scheduled exit.

## Fix
Use the existing native snapshot audit in queue-cycle, queue-doctor and queue-exit-check. Missing/paused/proposed/stale/wrong cadence/wrong consumer/observe-only registration yields CONTINUATION_NOT_ARMED and a concrete automation_update action for the owning conversation. Native registration must actually occur under its specific approval; user HOLD/PAUSED is preserved. A terminal queue needs no new schedule; declared pending follow-up/QC still does. No Python scheduler, subprocess watcher, parallel owner or automatic model switch.

Production instructions now require discover/view, actual create/update where approved, read-back and snapshot validation instead of merely proposing scheduling. Stable prompts read current approved project scope, not revision/count literals. Snapshot compliance is neither authenticated tool provenance nor actual execution proof; the owner captures real native records and verifies the subsequent production run separately.

## Verification and limits
209 local tests, 227 isolated origin/main-plus-picker tests, 34 installed-helper scheduling tests PASS. Compile/shell/diff/harness and reviewed two-file deployment hash checks PASS. Read-only real-project doctor refuses unarmed continuation and identifies missing snapshot plus production-owner mismatch. All nine automation.toml records unchanged by hash. No native scheduler creation/update, task messaging, browser action, new Generate or live unattended end-to-end test. These tests do not establish future model compliance or provider success.

Release is scoped; unrelated dirty files and deployed differences retained. Current project's PAUSED automation was not resumed. GitHub sync outcome is recorded separately in the local release receipt/harness.
