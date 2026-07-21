# Codex App Runtime Video-Team Workflow

Updated: 2026-05-16
Source design: `~/Downloads/hermes_parallel_video_team_workflow_clean.md`

Purpose: run a fresh Codex-delegated video workflow where Hermes remains the user-facing supervisor/router, while Codex lane jobs execute production work. This is not a restoration of the purged legacy Hermes video-team runtime.

## Core model

Music and cut/block planning are serial. After Music Lock + Cut Map Lock + Multi-reference Block Map, production runs in block-parallel mode:

1. Director classifies the project and sets safety gates.
2. Music locks or blocks BGM/audio and writes the beat/section map.
3. Planner creates Cut List + Music Cue Map + Multi-reference Block Map.
4. Image Creator lanes generate/retry block references in parallel.
5. Image QC verifies individual images and block continuity.
6. Seedance Operator is the single Computer Use owner for Seedance 2.0 I2V and locks only the active block/stage.
7. Seedance QC verifies outputs and routes PASS/retry/delete/edit-trim.
8. Editor/CapCut uses only verified video clips, not raw stills, and performs actual preview/export verification when needed.
9. Package prepares final files and copy, but never submits/sends/publishes without user approval.

## Runtime paths

Project root:

`~/Documents/Codex/video-team-runtime/<timestamp>_<slug>/`

Supervisor script:

`~/.hermes/codex-video-runtime/scripts/video_codex_runtime.py`

User-facing launcher:

`~/.local/bin/video-codex-runtime`

## Lanes

- `director`
- `music`
- `planner`
- `image_creator_01`
- `image_creator_02`
- `image_qc`
- `seedance`
- `seedance_qc`
- `editor`
- `package`

Aliases:

- `image_pool` → image_creator_01 + image_creator_02
- `image` → image creators + image_qc
- `i2v` → seedance + seedance_qc
- `parallel` → image creators + image_qc + seedance + seedance_qc
- `visual` → backward-compatible alias for the full image/I2V group
- `qc` → image_qc + seedance_qc
- `all` → every lane

## Project contents

- `brief.md`
- `state.json`
- `manifest.json`
- `queues/*.jsonl`
- `locks/*.json`
- `assets/audio/`
- `assets/images_candidates/`
- `assets/images_approved/`
- `assets/i2v_clips/`
- `assets/contact_sheets/`
- `assets/keyframes/`
- `assets/edit/`
- `assets/package/`
- `lanes/<lane>/prompt.md`
- `lanes/<lane>/result.md`
- `lanes/<lane>/run.log`
- `lanes/<lane>/pid`
- `lanes/<lane>/status.json`

## Commands

Show workflow:

```bash
video-codex-runtime workflow
```

Create a project:

```bash
video-codex-runtime init --slug my-video --brief "45초 관광 홍보 영상"
```

Create the fixed Kanban rail for that project:

```bash
video-codex-runtime kanban-plan --project ~/Documents/Codex/video-team-runtime/<project>
```

This creates a board with fixed cards only. It does not invent ad-hoc subagents. Cards map to existing stable profiles:

- Director/planner/retry router → `director`
- Music → `music`
- Image creators + Seedance operator → `visual`
- Image QC + Seedance QC → `qc`
- Editor/package → `editor`

Each Kanban card instructs the worker to operate through the fixed runtime lanes with `video-codex-runtime dispatch/status`, not through `delegate_task` children or newly-created profiles.

Default dispatch order:

```bash
video-codex-runtime dispatch --project ~/Documents/Codex/video-team-runtime/<project> --lanes director
video-codex-runtime dispatch --project ~/Documents/Codex/video-team-runtime/<project> --lanes music
video-codex-runtime dispatch --project ~/Documents/Codex/video-team-runtime/<project> --lanes planner
video-codex-runtime dispatch --project ~/Documents/Codex/video-team-runtime/<project> --lanes image_pool image_qc seedance seedance_qc
video-codex-runtime dispatch --project ~/Documents/Codex/video-team-runtime/<project> --lanes editor package
```

Check status:

```bash
video-codex-runtime status --project ~/Documents/Codex/video-team-runtime/<project>
```

Stop lanes:

```bash
video-codex-runtime kill --project ~/Documents/Codex/video-team-runtime/<project> --lanes parallel
```

## Safety rules

- Codex may use its own App runtime and bundled computer-use plugins because this is the Codex-delegated workflow.
- Hermes CuaDriver and Codex Computer Use remain separate stacks; do not disable one to fix the other.
- Every lane must produce real artifacts or a concrete blocker; text-only claims are not generated-media completion.
- Seedance locks only the active block/stage, never the whole project.
- Keep public/final side effects gated: no YouTube public upload, contest/government submit, email send, form submit, payment, password/2FA automation, or irreversible deletion without explicit approval.
- If GUI permission/login/CAPTCHA blocks occur, the lane must write BLOCKED with the exact app/window/state and required user action.
- Hermes should report completion/failure/blocker, not internal Codex logs.

## Relation to old runtime

The old active Hermes video-team runtime was purged and backed up at:

`~/.hermes/backups/video-team-purge-20260516_102924.tar.gz`

This folder is a fresh Codex-delegated runtime scaffold, not a restoration of the old runtime.
