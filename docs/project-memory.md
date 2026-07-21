# Project Memory

Use this file for durable context that should survive across threads.

## Product and Repo Context

- Canonical, version-controlled deployment package for the user's Codex video-team workflow.
- `codex-skills/seedance-prompt-en` is the sole live Seedance operator contract. The deployment script installs companion policies into `~/.codex/video-team-policies/`.

## Working Preferences

- Coding style choices that are stable over time.
- Review preferences or release expectations.

## Known Pitfalls

- Never leave an archived `SKILL.md` under `~/.codex/skills`; it can remain discoverable as a live skill.
- A skill must not refer to a policy file that the deployment script does not install.
- Do not add a second Seedance UI instruction source to director, MV, AGENTS, lane, or scheduler files.

## Open Questions Worth Tracking

- Questions that are not blockers today but should not disappear.
