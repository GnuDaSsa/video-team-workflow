# Safari hybrid branch — 2026-07-21

## Purpose

Provide a **Safari-surface** Seedance operator parallel to `main`’s Chrome hybrid, without mixing browsers in one deploy.

| Branch | Browser | Click path |
|---|---|---|
| `main` | Chrome | CU drag + Chrome Codex plugin for WEB |
| `operator/safari-hybrid` | Safari | CU drag + Safari CU for WEB |

Shared on both:

- Dual in-flight ~2
- One-file Finder drag
- Eight-check Generate
- Subagent approval gate
- Seedance default I2V; Grok only if named
- No Hermes

## Deploy rule

Only one branch should be deployed to `~/.codex/skills` at a time:

```bash
git checkout operator/safari-hybrid && ./tools/deploy_skills_to_codex.sh   # Safari machine path
git checkout main && ./tools/deploy_skills_to_codex.sh                   # Chrome machine path
```

## Files specific to this branch

- `team-policies/safari_hybrid_operator_20260721.md`
- `codex-skills/seedance-prompt-en/SKILL.md` (Safari hard route)
- README branch banner

`team-policies/chrome_hybrid_operator_20260721.md` may still exist historically from `main`; on this branch Safari policy is authoritative for Seedance UI.
