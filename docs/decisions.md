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
