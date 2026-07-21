# Workflow deployment contract — 2026-07-21

## Objective

Deploy the remote Fable/Grok workflow update into Codex without restoring duplicate
Seedance operator instructions.

## Acceptance criteria

1. `seedance-prompt-en` remains the single live Seedance operating contract.
2. The deployed contract can resolve both Chrome-hybrid and subagent-gate policy paths.
3. Archived Seedance contracts are outside `~/.codex/skills` and cannot be loaded as active skills.
4. Deployment has a rollback archive and passes the package verification command.
