---
title: Video Project Seed Template
created: 2026-05-12
updated: 2026-05-25
type: seed
tags: [video, workflow, agents, seed]
sources: [concepts/video-team-seed-system.md, concepts/video-typography-operating-manual.md, raw/transcripts/video-workflow-lockdown-fixed-rail-20260525.md]
confidence: medium
contested: false
contradictions: []
---

# Video Project Seed Template

## Purpose

새 영상 작업을 시작할 때 이 페이지를 복사해 프로젝트별 seed로 변환한다. 이 seed는 계획 문서가 아니라, 다양한 영상작업을 fixed runtime/Kanban rail에서 실행 가능한 브리프, lane deliverable, QC gate로 전환하는 원천 단위다. 관련 운영 원칙은 [[video-team-seed-system]]과 [[video-typography-operating-manual]]을 따른다.

## 1. Project Archetype

- Type: contest film | tourism MV | brand film | public campaign | product ad | short-form | documentary | educational explainer | music video | other
- Runtime:
- Aspect ratio:
- Delivery platform:
- Required outputs:
- Public upload/submission gate: yes/no

## 2. Source Evidence

- Official rules:
- Required assets:
- Prior wiki seeds:
- Reference works:
- Raw transcripts:

## 3. Winning Pattern

Describe the reusable creative engine.

- Hook:
- Viewer transformation:
- Narrative/action spine:
- Visual motif:
- Music/rhythm logic:
- Typography role:
- CTA/outro:

## 4. Non-goals / Anti-patterns

- Do not use raw still frames as final/review timeline filler.
- Do not call music locked until a real audio file exists and duration/codec are verified.
- Do not assume the old Grok 4-cut microbatch or ChatGPT 4-output loop; current video generation is Seedance 2.0 multi-reference block-based unless explicitly overridden.
- Do not accept CapCut typography based on JSON/Pillow proof alone when editable CapCut work is required.
- Do not send final public upload/contest submission/personal info without explicit user confirmation.
- Project-specific anti-patterns:

## 5. Production Seed

Copy/paste-ready seed for a new run:

```text
Goal:
Create a [runtime/aspect] [project archetype] about [subject] for [audience/platform].

Success criteria:
- [official/spec criterion]
- [viewer effect]
- [quality gate]
- [delivery package]

Creative route:
[hook → body → peak → outro]

Production constraints:
- Create the project with `~/.local/bin/video-codex-runtime`, then create Kanban only with `video-codex-runtime kanban-plan --project <project>`.
- Use only fixed lanes: `director`, `music`, `visual`, `qc`, `editor`; do not create ad-hoc subagents/profiles.
- Music lane produces/locks real audio first when music-driven.
- Planner/Director writes Cut Map and Block Map; each Seedance block declares `reference_count_required`.
- Visual lane runs image creation plus Seedance 2.0 multi-reference operation through fixed rail gates; QC validates image and Seedance outputs separately.
- Editor builds an editable CapCut draft when typography/transitions are part of the brief.
- QC owns PASS/FAIL and checks actual artifacts.
```

## 6. Role Handoff Map

### Director / Gojo
- Extract official constraints, rubric, audience, non-goals.
- Choose concept route and cut-level reason for every cut.
- Produce project brief and fixed Kanban/runtime handoff evidence.
- Fan-in completion/blockers; do not create lane deliverables.

### Music / Yuta
- Generate or source actual audio.
- Save real MP3/WAV.
- Verify duration/codec with ffprobe.
- Write beat map and hand off LOCKED/NOT LOCKED.

### Visual / Sukuna
- Produce character sheets if recurring characters exist.
- Generate required reference images/styleframes for each block.
- Use Block Map `reference_count_required` to assemble Seedance 2.0 multi-reference bundles.
- Submit Seedance blocks only after required reference/QC gates are satisfied; defer dirty attach blocks without stopping clean blocks.

### Editor / Mahoraga
- Assemble accepted clips/audio/assets.
- Build editable CapCut draft when needed.
- Verify timeline, transitions, typography, render/export.
- Package review/final masters.

### QC / Yuji
- Check every gate independently.
- Verify identity, motion, crop, duplication, safe margins, captions, audio sync, final export.
- Report PASS/FAIL with exact blocker and required rework.

## 7. Acceptance Criteria

- AC1 Official compliance:
- AC2 Narrative/creative fit:
- AC3 Music/rhythm:
- AC4 Visual/I2V quality:
- AC5 Edit/typography:
- AC6 QC evidence:
- AC7 Delivery package:

## 8. Verification Methods

- ffprobe for audio/video duration/codec.
- Contact sheets/keyframes for visual review.
- CapCut UI/preview verification for editable text layers and real shadows/strokes/fades.
- File path + mtime + render/export proof.
- Final package checklist before user confirmation gate.

## 9. Next-use Prompt

```text
Use `~/wiki/seeds/video-project-seed-template.md` and related seed pages as the starting source. First read SCHEMA, index, `_mocs/video-production.md`, and `concepts/video-team-seed-system.md`. Then adapt the closest seed to the current project, create the runtime project and fixed Kanban rail, and route concrete fixed-lane deliverables without asking the user to repeat standing video-team rules.
```

## Related pages

- [[tourism-mv-seed]]
- [[video-team-seed-system]]
- [[video-typography-operating-manual]]
- [[video-typography-dataset]]
- [[hermes-agent]]
