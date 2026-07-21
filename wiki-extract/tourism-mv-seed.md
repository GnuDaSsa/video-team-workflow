---
title: Tourism MV Seed
created: 2026-05-12
updated: 2026-05-25
type: seed
tags: [video, video-production, music-video, contest-film, workflow, seed]
sources: [concepts/video-team-seed-system.md, concepts/video-typography-operating-manual.md, raw/transcripts/hermes-session-capture-20260512-142448.md, raw/transcripts/video-workflow-lockdown-fixed-rail-20260525.md]
confidence: medium
contested: false
contradictions: []
---

# Tourism MV Seed

## Project Archetype

관광/지역/문화유산 소재를 음악 기반 MV 또는 공모전 광고로 만드는 seed. 목표는 장소 나열이 아니라, 음악·행동·공간 정보가 결합된 “가고 싶게 만드는 여정”이다. 이 seed는 [[video-project-seed-template]]의 관광/MV 특화 변형이며, 타이포그래피 판단은 [[video-typography-operating-manual]]을 따른다.

## Source Evidence

- [[video-team-seed-system]]
- [[video-typography-operating-manual]]
- [[video-typography-dataset]]
- [[video-typography-contract-template]]
- Prior Hermes video-team transcripts in `raw/transcripts/hermes-session-capture-*.md`

## Winning Pattern

1. Hook: 첫 3–5초 안에 장소/감정/리듬을 동시에 제시한다.
2. Journey Spine: 이동, 발견, 참여, 절정, 여운의 순서로 컷을 배치한다.
3. Place Meaning: 관광지는 배경이 아니라 행동의 무대다. 먹기, 걷기, 오르기, 만지기, 바라보기, 축제 참여처럼 시청자가 따라 할 수 있는 행동을 넣는다.
4. Music Fit: 빠른 음악은 단순 flash/glitch가 아니라 추가 action/information cuts로 해결한다.
5. Typography: 장소/event label은 정보 디자인이다. generic app/startup UI처럼 보이면 실패다.
6. Outro: 공식 슬로건/CTA/필수 로고는 숨 쉬는 엔드 카드로 회수한다.

## Non-goals / Anti-patterns

- 관광 명소의 예쁜 장면만 나열하지 않는다.
- 빠른 음악을 flash spam, 0.5초 micro-caption, glitch만으로 해결하지 않는다.
- raw still frame을 review/final timeline filler로 쓰지 않는다.
- 장소 라벨을 generic sans startup UI처럼 만들지 않는다.
- 음악 파일 없이 “music locked”라고 하지 않는다.
- CapCut 자막/그림자/페이드 PASS를 JSON-only로 선언하지 않는다.

## Production Seed

```text
Goal:
Create a music-driven tourism MV/contest film that turns [region/place/theme] into a concrete journey viewers want to follow.

Creative route:
Hook with a rhythm-action-place collision, move through 4-6 motivated location/action chapters, peak at a human/cultural participation moment, and close with a breathable slogan/CTA card.

Production constraints:
- Lock real BGM/audio before final cut timing.
- One cut must have one narrative/rhythm/information reason.
- Seedance 2.0 multi-reference blocks are the current video basis; Block Map sets `reference_count_required` and image/QC gates per block.
- Add purposeful new cuts if the edit feels slow; do not solve rhythm only with effects.
- Use place-aware typography: cultural locator feel, scene-specific palette, readable Korean, safe margins.
- Editor must keep CapCut text editable when typography is part of the deliverable.
```

## Role Handoff Map

- Director/Gojo: official rules/rubric → winning route → cut-level timeline → role handoffs.
- Music/Yuta: full-length usable BGM, verified duration/codec, beat map.
- Visual lane: reference images/character or location styleframes, Seedance multi-reference operation, image/Seedance queue evidence through fixed rail.
- Editor/Mahoraga: CapCut draft, cut rhythm, transitions, locator typography, export. Editor implements typography against a Director-issued contract, not loose style advice.
- QC/Yuji: duplicate impression check, motion/crop/identity, caption/typography clearance, final package PASS/FAIL. Typography QC must check the contract row-by-row.

## Acceptance Criteria

- Official runtime/aspect/file/submission constraints are satisfied.
- The first 10 seconds make the destination/theme understandable.
- Every cut has a reason: action, information, emotional shift, rhythmic accent, narrative transition, or motif payoff.
- BGM is a real file and checked; beat map informs cut timing.
- Typography identifies places/events without covering subject/action or looking like a generic app UI.
- A project-specific typography contract exists when typography is material to the deliverable; contrast-only fixes are not enough.
- CapCut preview/export verifies every character and safe margin if editable typography is required.
- Final public upload/submission waits for explicit user confirmation.

## Verification Methods

- ffprobe for BGM and final masters.
- Contact sheet/keyframes for source and I2V candidates.
- Seedance block → reference bundle → queue/download mapping.
- CapCut actual preview screenshots for typography risk points.
- QC PASS/FAIL checklist before final package.

## Next-use Prompt

```text
Use `~/wiki/seeds/tourism-mv-seed.md` as the seed. Adapt it to the current official rules/theme, create the runtime project plus fixed Kanban rail, produce a Director brief with 2-3 concept routes and one selected route, then route fixed-lane Music/Visual/QC/Editor deliverables with concrete gates and stop conditions.
```

## Related pages

- [[video-team-seed-system]]
- [[video-project-seed-template]]
- [[video-typography-operating-manual]]
- [[video-typography-dataset]]
