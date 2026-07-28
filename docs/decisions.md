# Decisions

Record notable technical or product decisions here so they do not live only in chat history.

## Entry Template

### YYYY-MM-DD - Short Decision Title

- Context:
- Decision:
- Consequences:
- Follow-up:

### 2026-07-21 - Deploy Chrome-hybrid Seedance package with bundled policies

- Context: Fable/Grok updated the GitHub workflow to use one Chrome Runway board, phase-locked Codex tools, dual in-flight capacity, and explicit approval before agent/scheduler fan-out.
- Decision: Keep `seedance-prompt-en` as the single live Seedance contract; deploy the two referenced policies to `~/.codex/video-team-policies/` as part of `tools/deploy_skills_to_codex.sh`.
- Consequences: The local skill no longer has broken relative policy references, and an archived operator skill cannot be discovered as active.
- Follow-up: Use the Chrome hybrid route only when its actual Codex Computer Use/Chrome-plugin capability is available; do not pretend a missing capability succeeded.

### 2026-07-28 - Arbitrate the video-team rule set (7 user decisions)

- Context: generations were non-deterministic — Seedance silently disabled audio, uploads that worked one day failed the next, quality drifted. Diagnosis found five authority layers (~3,000 lines) each declaring itself final, with pairwise contradictions. Forensics on two live projects confirmed the cost: the independence-activist project had run 14 days across 68 seedance session folders (1.5 GB, 467 PNG, 36 MP4) with the rail's canonical asset folders still empty, and had grown its own project-local rules file — a sixth authority layer — because the canonical ones disagreed. The newest project stalled after the director lane with zero outputs.
- Decision: seven user rulings, applied across the repo.
  1. Audio toggle always ON; "no BGM" is prompt wording only. (Root cause: the preference was stored in the settings field, and the observer protocol literally said "verify Audio Off".)
  2. Character sheets are always attached when a recurring character appears; the runtime's INVALID_DIRECT_CHARACTER_SHEET_ROUTE ban is retired. Field practice was already doing this.
  3. + 6. Upload uses one fixed ladder: asset selector → one retry → drag only with explicit user approval → BLOCKED. Drag is demoted from canonical to last resort, and "get through it however works" is replaced by climbing predefined rungs.
  4. Runway runs in Chrome; the runtime file was the last Safari holdout.
  5. All prompt authoring is gpt-5.6-sol high, resolving a deadlock where §2.1 required terra but attestation required sol.
  7. I2V defaults to Seedance; Grok only when the user names it. music-video-production-team's role 5 was still Grok-first.
- Consequences: each contested behaviour now has exactly one owner, and an explicit authority order sits in both AGENTS.md files. Valid corrections from the project-local rules file were promoted to `seedance-field-lessons.md`; project-specific content stayed with the project. Local rules copies inside project folders are banned — exceptions go to `docs/project_overrides.md`.
- Follow-up: `runtime/AGENTS.md` is now tracked here but the live copy is still at `~/Documents/Codex/video-team-runtime/AGENTS.md`; deploying it is not yet automated. Nothing has been deployed to `~/.codex` — the fixes are on `fix/rule-arbitration-20260726` awaiting review. The deploy script now refuses to run while live is ahead of the repo.
