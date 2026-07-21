# Video Team Workflow

Reusable **Codex-native** video-team package: Seedance/Runway operating rules, image/I2V QC, typography, submission safety, and curated knowledge.

**Version line (2026-07-21 v2):** Chrome hybrid operator + dual in-flight queue + single Seedance contract + subagent approval gate + Hermes removed.

## Included

| Path | Purpose |
|---|---|
| `codex-skills/` | Deployable Codex skills |
| `references/` | Character sheet standards |
| `wiki-extract/` | QC / seed knowledge extracts |
| `seedance-operations/` | Ops helpers (Finder placement, continuity) |
| `team-policies/` | Subagent gate, Chrome hybrid operator |
| `docs/` | Session / version records |
| `tools/deploy_skills_to_codex.sh` | Deploy skills → `~/.codex/skills` (archives old) |
| `GLOBAL_AGENTS.md` | Package-side agents mirror (deploy separately if used) |

## Excluded

Project folders, generated media, CapCut drafts, browser/session state, credentials, tokens, `.env`, private personal-information forms.

## Authority map

| Topic | Live file |
|---|---|
| Seedance prompt + UI | `codex-skills/seedance-prompt-en/SKILL.md` **only** |
| Chrome hybrid + dual in-flight | `team-policies/chrome_hybrid_operator_20260721.md` |
| No subagent fan-out | `team-policies/subagent_approval_gate_20260721.md` |
| Cleanup history | `docs/2026-07-21-video-team-cleanup-session.md` |
| This version-up | `docs/2026-07-21-video-team-version-up.md` |

`videodirector` / `music-video-production-team` define story and image requirements only — **not** Seedance UI steps.

## Seedance operating model (v2)

```
Chrome tab = app.runwayml.com Generate board (only browser for Runway)
ATTACH  → Computer Use: Finder → Chrome Multi-ref, one drag at a time
VERIFY  → Chrome Codex plugin: thumbnail count/order = PASS
WEB     → Chrome Codex plugin: prompt, settings, Generate once, cards
QUEUE   → keep ~2 jobs in flight (~30 min each); fill next slot ASAP
WAIT    → poll / 15-min observer only; no second agent
```

- Default I2V: **Seedance**. Grok only if the user explicitly names Grok.
- No Runway API/connector, no picker/path/AppleScript method ladder, no Credits/Max without explicit approval.
- No Hermes / `~/.hermes` / external orchestrator.

## Operating principles

1. **Subagent spawn approval gate** — no delegated lanes, subagents, sidecars, or extra loops without per-spawn user approval (exception: Seedance 15-min queue observer while active).
2. **Latest-only** — active files hold only current rules; no stacked dated contradictions. History = git + `archive/`.
3. **Canonical source** — this GitHub repo; `~/.codex/skills` is a deploy target.

## Deploy

```bash
# from package root on the Mac video machine
./tools/deploy_skills_to_codex.sh
```

## Codex-native boundary

Codex is the single entrypoint and execution owner. Former Hermes supervisor/relay and `codex-video-runtime/` scaffold were removed (2026-07-21). Recover from git history only if ever needed.
