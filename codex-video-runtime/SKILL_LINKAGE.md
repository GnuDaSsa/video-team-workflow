# Codex video runtime skill linkage

Hermes is the brain/control plane only. Production work must run in Codex runtime lanes. Each Codex lane prompt must explicitly load/reuse the relevant Codex skills and role contracts below before acting.

Source design document:
- `~/Downloads/hermes_parallel_video_team_workflow_clean.md`

Codex skill roots:
- `~/.codex/skills/music-video-production-team/SKILL.md`
- `~/.codex/skills/music-video-production-team/references/role-prompts.md`
- `~/.codex/skills/music-video-production-team/references/agent-contracts.md`
- `~/.codex/skills/music-director/SKILL.md`
- `~/.codex/skills/music-composition-source/SKILL.md`
- `~/.codex/skills/music-composition-source/references/00-navigation.md`
- `~/.codex/skills/videodirector/SKILL.md`
- `~/.codex/skills/seedance-prompt-en/SKILL.md` — mandatory for every Seedance/Runway Seedance/Jimeng/即梦/I2V prompt drafting, revision, retry, QC diagnosis, or planning touchpoint.

Lane mapping:

| Runtime lane | Required Codex skill/contract | Notes |
|---|---|---|
| director | `music-video-production-team` Executive Producer / Showrunner + `videodirector` | project mode, scope, safety, manifest/queue setup |
| music | `music-director` + `music-composition-source` + MV team Music Director contract | Suno/BGM Music Lock; must use Codex Computer Use for Suno, never local placeholder as lock |
| planner | `music-video-production-team` Planner + Song Analyst contracts + `videodirector` | requires real Music Lock before final cut/block map |
| image_creator_01/02 | MV team Image Creator / Art Director contracts + imagegen skill when applicable | generate file-backed refs; no Hermes-side work |
| image_qc | MV team Image QA + design doc Image QC policy | individual + block continuity QC; route queues |
| seedance | Seedance Operator contract from design doc + `seedance-prompt-en` | single Computer Use owner for Seedance I2V; `seedance-prompt-en` is mandatory before any prompt draft/revision/retry/QC diagnosis |
| seedance_qc | Seedance Video QC contract | contact sheets/keyframes; route PASS/retry/delete/edit |
| editor | MV team Editor/Post Supervisor + CapCut user rules | approved clips only, no raw still final |
| package | Package/Submission Manager contract | no final publish/submit without user approval |

Hard rules:
- If any lane is touching Seedance/Runway Seedance/Jimeng/即梦/I2V prompting, retries, or prompt QC, it must first read `~/.codex/skills/seedance-prompt-en/SKILL.md`. If missing, stop as `BLOCKED_REQUIRED_SEEDANCE_PROMPT_SKILL_MISSING`.
- Do not let Hermes/Kanban generic workers execute visibility cards.
- Do not omit skill linkage in Codex lane prompts.
- If a required skill file is missing, the lane must stop as `BLOCKED_REQUIRED_CODEX_SKILL_MISSING` and name the path.
- Music lane must read `~/.codex/skills/music-director/SKILL.md` and `~/.codex/skills/music-composition-source/references/00-navigation.md` before proposing or generating Suno prompts.
- Music lane must use Codex Computer Use / SkyComputerUseClient to operate Suno when Suno is required.
