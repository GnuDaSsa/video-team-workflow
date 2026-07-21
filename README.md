# Video Team Workflow

Reusable Codex-native video-team workflow package: Seedance/Runway operating rules, image/I2V QC, typography, submission safety, and reusable knowledge extracts.

## Included

- `codex-skills/` — reusable video-team skills.
- `references/` — production reference standards (character sheets).
- `wiki-extract/` — curated workflow and QC knowledge.
- `seedance-operations/` — current Seedance/Runway operation policies and Finder placement helper.
- `team-policies/` — team-wide operating gates (subagent spawn approval, latest-only principle).
- `tools/deploy_skills_to_codex.sh` — deploy packaged skills into `~/.codex/skills` (archives replaced versions).

## Excluded

Project folders, generated media, downloaded videos, CapCut drafts, browser/session state, credentials, tokens, `.env` files, and private personal-information forms are intentionally excluded.

## Seedance operating boundary

Use visible Runway UI as source of truth. Use Codex Computer Use for Finder-to-Runway drag/drop, one reference at a time, with visible thumbnail verification. Do not use hidden inputs, path typing, picker/asset-modal shortcuts, Runway API/connector, Grok for stills, Credits/Max, or Generate without current-scene preflight.

## Seedance operator authority

`codex-skills/seedance-prompt-en/SKILL.md` is the only live Seedance prompt-and-operation contract. It owns visual prompt writing, visible Runway UI operation, reference upload, Generate, queue state, and evidence. `GLOBAL_AGENTS.md`, `videodirector`, and `music-video-production-team` do not define Seedance UI steps. Older detailed material is retained under `codex-skills/seedance-prompt-en/archive/` as reference only.

## Operating principles

- **Subagent spawn approval gate:** no delegated lanes, subagents, sidecars, or scheduler loops without explicit per-spawn user approval (single pre-approved exception: the 15-minute Generate-queue observer in the Seedance contract). See `team-policies/subagent_approval_gate_20260721.md`.
- **Latest-only rule files:** active files carry only currently valid rules; corrections edit/delete in place instead of appending dated layers. History and rollback live in this repo's git history and `archive/` folders.
- **Canonical source:** this repo is the version-controlled source of truth for video-team skills; `~/.codex/skills` is a deployment target (`tools/deploy_skills_to_codex.sh`).

## Codex-native boundary — 2026-07-21

Codex is the single entrypoint and execution owner. The former Hermes supervisor/relay layer and its delegated lane scaffold (`codex-video-runtime/`) were removed; recover them from git history if ever needed. Nothing in this package may depend on `~/.hermes` paths, external orchestrator binaries, or relay personas.
