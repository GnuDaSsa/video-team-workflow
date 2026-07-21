# Safari Computer Use branch — 2026-07-21

## Purpose

Provide a **Safari-only** Seedance operator parallel to `main`’s Chrome path.  
Name is **not** “hybrid with Chrome” — one browser per branch.

| Branch | Browser | Tools |
|---|---|---|
| `main` | Chrome only | CU drag + Chrome plugin for WEB clicks |
| `operator/safari-computer-use` | Safari only | Computer Use for drag **and** WEB clicks |

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
git checkout operator/safari-computer-use && ./tools/deploy_skills_to_codex.sh   # Safari machine path
git checkout main && ./tools/deploy_skills_to_codex.sh                   # Chrome machine path
```

## Files specific to this branch

- `team-policies/safari_computer_use_operator_20260721.md`
- `codex-skills/seedance-prompt-en/SKILL.md` (Safari hard route)
- README branch banner

`team-policies/chrome_hybrid_operator_20260721.md` may still exist historically from `main`; on this branch Safari policy is authoritative for Seedance UI.
