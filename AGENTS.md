<!-- codex-harness-kit:start -->
# AGENTS

## Codex Harness Workflow

1. At the start of any thread, especially an old one, ignore stale chat context until the harness files below have been reread from the repository.
2. Before changing code, read `docs/harness-config.json` first.
3. Then use the configured paths from that file instead of assuming fixed `docs/...` locations:
   - read `paths.stateFile`
   - read the active contract referenced by `currentContract` inside the state file
   - read `paths.decisionsFile`
   - read `paths.memoryFile`
   - use `paths.contractsDir` for contract discovery
4. Use the configured validation commands from `commands.verifyQuick` and `commands.verifyFull` when they are set.
5. Restore state before editing. Do not jump straight into implementation.
6. Keep the contract current. If scope or acceptance changes, update the contract before more code changes.
7. After edits, run the smallest meaningful verification command and record the result in the file pointed to by `paths.stateFile`.
8. If the same class of failure reaches the configured repeated-failure limit in `rules.maxRepeatedFailures`, stop trial-and-error and write a short diagnosis with evidence, suspected root cause, and the safest next move.
9. Before ending any meaningful task, update the configured state file with the new status, blockers, next step, and verification result.
10. Capture durable context:
   - long-lived preferences and quirks go in `paths.memoryFile`
   - explicit trade-offs and architectural choices go in `paths.decisionsFile`
11. If the contract changed materially, update the active contract before ending the thread.
12. Final responses must always say:
   - what changed
   - what verification ran
   - what verification did not run
   - whether the harness state, decisions, or project memory were updated

## Restore Prompt

When a new Codex thread starts, begin by reading the harness files above. A good prompt is:

> Restore state and continue from the harness files before making changes.

When reopening an old thread, a good prompt is:

> Ignore old thread context, restore state from the harness files, then continue.

## Wrap-Up Prompt

Before ending a task, a good prompt is:

> Update harness-state, record any durable decisions or memory, then report verification and next steps.

## Guardrails

- Prefer the existing repo layout over inventing a new framework.
- Keep this harness lightweight; do not turn it into a platform.
- If validation is not configured yet, say so explicitly instead of claiming full verification.
<!-- codex-harness-kit:end -->
