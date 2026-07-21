# Subagent / lane spawn approval gate — 2026-07-21

User correction: after the video team is invoked, work must not fan out into subagents, lanes, or background loops on its own.

## Hard rule

- Spawning any additional agent surface requires **explicit user approval for that specific spawn, in the current conversation**. This covers: Codex delegated lanes, subagent/worker/explorer agents, external sidecars, background monitors/schedulers/cron/heartbeat loops, and any second concurrent browser-automation loop.
- An approval request must name what is being spawned: lane id/role, purpose, and expected output. Blanket pre-approval does not exist; "the plan mentions lanes" or "the template defines roles" is **not** approval.
- Default execution model is **single-agent, sequential, in the main conversation**. Parallel lanes are an exception the user grants per project/turn, not the default.
- Wherever an older rule, template, or manifest says lanes "may run in parallel", read it as "may run in parallel **once the user approves that lane set**".
- Role names in skills (Planner, Image Creator, Seedance Operator, etc.) define **responsibilities**, not standing permission to instantiate agents. One agent may play multiple roles sequentially without approval; instantiating a separate agent per role requires approval.
- Schedulers/monitors additionally follow `seedance-operations/scene_advancement_policy_20260719.md`: never spawn a retry/heartbeat loop as a side effect of a blocker.
- If unsure whether something counts as a spawn: it does — ask first.

## Latest-only operating principle (same date)

- Active rule files carry **only the currently valid rules**. When a rule is corrected, edit or delete the old text in place — do not append another dated layer on top of it.
- History lives in git. Rollback = `git log` / `git checkout <commit> -- <file>`, not stacked "superseded" sections inside active files.
- Dated section titles remain fine as provenance, but two sections giving conflicting instructions for the same action may not coexist in an active file.
