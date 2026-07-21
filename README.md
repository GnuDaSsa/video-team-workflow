# Video Team Workflow — Safari hybrid branch

Reusable **Codex-native** video-team package.  
**This branch:** `operator/safari-hybrid` — Runway/Seedance on **Safari**.

| Branch | Browser surface |
|---|---|
| `main` | Chrome hybrid (plugin + CU drag) |
| `operator/safari-hybrid` (this) | Safari hybrid (CU drag + CU web on Safari) |

## Included

| Path | Purpose |
|---|---|
| `codex-skills/` | Deployable Codex skills |
| `references/` | Character sheet standards |
| `wiki-extract/` | QC / seed knowledge extracts |
| `seedance-operations/` | Ops helpers (Finder placement, continuity) |
| `team-policies/` | Subagent gate, **Safari** hybrid operator |
| `docs/` | Session / version records |
| `tools/deploy_skills_to_codex.sh` | Deploy skills → `~/.codex/skills` |

## Authority map (this branch)

| Topic | Live file |
|---|---|
| Seedance prompt + UI | `codex-skills/seedance-prompt-en/SKILL.md` |
| Safari hybrid + dual in-flight | `team-policies/safari_hybrid_operator_20260721.md` |
| No subagent fan-out | `team-policies/subagent_approval_gate_20260721.md` |
| Cleanup history | `docs/2026-07-21-video-team-cleanup-session.md` |
| Chrome mainline notes | see `main` branch `team-policies/chrome_hybrid_operator_20260721.md` |

## Seedance operating model (Safari hybrid)

```
Safari window = app.runwayml.com Generate board (only browser for Runway on this branch)
ATTACH  → Computer Use: Finder → Safari Multi-ref, one drag at a time
VERIFY  → Safari visible thumbnail count/order = PASS
WEB     → Safari Computer Use: prompt, settings, Generate once, cards
QUEUE   → keep ~2 jobs in flight (~30 min each); fill next slot ASAP
WAIT    → poll / 15-min observer only; no second agent
```

- Default I2V: **Seedance**. Grok only if the user explicitly names Grok.
- Do **not** mix Safari + Chrome Runway sessions in one project.
- No Runway API/connector, no picker/path/AppleScript method ladder, no Credits/Max without explicit approval.
- No Hermes / external orchestrator.

## Deploy (Safari machine)

```bash
git checkout operator/safari-hybrid
git pull
./tools/deploy_skills_to_codex.sh
```

To return to Chrome mainline skills:

```bash
git checkout main
./tools/deploy_skills_to_codex.sh
```

## Operating principles

1. **Subagent spawn approval gate** — no extra agents without per-spawn user approval.
2. **Latest-only** — active files hold only current rules.
3. **Canonical source** — this GitHub repo; `~/.codex/skills` is a deploy target.
