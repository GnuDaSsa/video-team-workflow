---
title: Video Workflow Split Proposal — Contest vs MV
created: 2026-05-26
updated: 2026-05-26
type: query
tags: [video, workflow, agents]
sources: [concepts/video-team-seed-system.md, concepts/video-typography-operating-manual.md, concepts/video-typography-dataset.md, seeds/video-project-seed-template.md, seeds/tourism-mv-seed.md]
confidence: medium
contested: false
contradictions: []
---

# Video Workflow Split Proposal — Contest vs MV

## Problem

The current video-team runtime handles contest/public films and MV/song-first projects with one broad workflow. This causes mode confusion:

- Contest/public films need official requirements, message clarity, typographic role separation, package/submission gates, and restrained BGM.
- MV projects need music/lyrics/phrase-first editing, sparse poetic typography, stronger rhythm/microcut logic, and performance/visual hook evaluation.
- When these are not separated, lanes may over-monitor, over-explain, over-type, or trigger Seedance/editor stages at the wrong time.

## Proposal

Keep the same fixed runtime rails (`director`, `music`, `visual`, `qc`, `editor`) but add a required `project_mode` at initialization:

```json
{
  "project_mode": "contest_public" | "mv_songfirst",
  "typography_mode": "information_contract" | "lyric_hook_contract",
  "music_mode": "score_bgm" | "song_master"
}
```

The mode controls Director brief, Music lock, Planner cut/block map, Typography Contract, QC gates, and when Editor/Package can start.

## Mode A — Contest/Public Workflow

### Purpose

For contests, public campaigns, tourism/heritage, government-adjacent, brand explainers, institutional videos.

### Creative KPI

- Official compliance and judging rubric fit.
- Viewer understands the message/theme within the first 5–10 seconds.
- Typography clarifies information without looking like a presentation deck.
- Music supports trust/emotion and does not overpower message.

### Music policy

- `music_mode = score_bgm`.
- Music lane must lock a real BGM/score file before final cut/block map.
- Instrumental-first unless the brief explicitly requires lyrics.
- Beat map must include section changes, pauses, and ending cadence.
- Music is a support spine; it should not force unreadable kinetic captions.

### Typography policy

- `typography_mode = information_contract`.
- Required roles: `TITLE`, `LOCATION`, `BODY/NARRATION`, `DISCLOSURE`, `CTA/FINAL`.
- Body copy is allowed only on endpoint-hold or card cuts.
- Official info, AI-use notes, dates, slogans, CTA, required logos/assets get their own rows.
- Motion budget: static/fade-only by default; at most one restrained emphasis per sentence.
- Auto captions must be isolated: generate in caption-only project, normalize, then transplant.
- CapCut preview/export is source of truth.

### Planner output additions

- Official requirement map.
- Rubric-to-cut justification.
- Required text inventory before Editor.
- Card/label/body/CTA timing map.
- Submission/package checklist.

### Editor/QC gates

- Typography Contract must exist before CapCut work.
- QC must verify: readability, safe margins, no subject/action overlap, Korean line breaks, official required text, logo/CTA placement, caption-included sample export.
- Package cannot run until official runtime/aspect/file naming/submission assets are verified.

### Anti-patterns

- Treating contest film like a lyric MV.
- Long narration subtitles on fast rhythm cuts.
- Generic app/startup labels for heritage/tourism.
- Calling prompt/music snippet a Music Lock.
- Exporting based on JSON-only typography proof.

## Mode B — MV/Song-first Workflow

### Purpose

For anime MV, lyric/song video, song promotion, emotional montage, music-led visual story.

### Creative KPI

- Song/hook drives the edit.
- Cut timing follows phrase, snare/backbeat, drop, chorus, bridge, outro.
- Visual blocks are generation containers; final edit uses C-level microcuts when rhythm demands it.
- Typography is sparse, poetic, and hook-centered.

### Music policy

- `music_mode = song_master`.
- Music lane owns creative song design: lyrics, structure tags, vocal persona, style prompt, variations.
- Lyric/anime song uses Suno Advanced/Custom: Lyrics and Style separated.
- Instrumental MV can use Simple Mode + Instrumental, but still needs verified audio file and beat/phrase map.
- Planner cannot finalize cut/block map before real Music Lock.

### Typography policy

- `typography_mode = lyric_hook_contract`.
- Required roles are narrower: `TITLE`, `HOOK`, `LYRIC_MOTIF`, `FINAL_MOTIF/CTA`.
- Body/narration is usually forbidden unless deliberately part of the concept.
- Hook words/phrases may use one motion event, but must keep entry → readable hold → exit.
- Captions should not become karaoke unless the project is explicitly lyric-video mode.
- Scene risk focuses on face/eyes/hands/lantern/core action/subject clearance.

### Planner output additions

- Phrase map and microcut risk map.
- Chorus/drop/hook typography moments.
- B-block generation map plus C-cut editorial map.
- Seedance prompt starters must use `seedance-prompt-en` and music-aware motion budgets.

### Editor/QC gates

- Editor may split Seedance blocks into microcuts for rhythm recovery.
- Typography Contract rows are fewer but stricter: role, phrase timing, focal-object clearance, hold time, no rounded subtitle box.
- QC must verify actual CapCut preview/export sample frames at hook/title/outro points.
- Package should distinguish review proxy vs actual CapCut master.

### Anti-patterns

- Full-body informational subtitles in an MV.
- One 10–12s Seedance block used as a final cut when the song needs microcuts.
- Motion typography without readable hold.
- Treating MV title/hook as public explanation copy.

## Shared fixed lanes, mode-specific behavior

| Lane | Contest/Public | MV/Song-first |
|---|---|---|
| Director | official rules/rubric/source assets; compliance first | concept/song world/hook; emotional arc first |
| Music | score/BGM, instrumental, trust/emotion support | song/lyrics/vocal/hook/phrase map |
| Planner | cut map from requirements + beat map; text inventory | phrase/microcut map; B-block to C-cut relationship |
| Visual/Seedance | clear reference bundles, public-safe visuals, avoid signage/text | dynamic multi-reference motion, identity/motif continuity |
| QC | compliance, readability, official text/logo, package | rhythm, motion, identity, hook typography, microcut sync |
| Editor | editable CapCut text, cards, disclosures, final package | rhythm/microcut edit, sparse text hooks, final master |

## Runtime implementation plan

1. Add `project_mode` to new project manifest during `video-codex-runtime init` or immediately after Director intake.
2. Add two Director brief templates:
   - `templates/director_contest_public.md`
   - `templates/director_mv_songfirst.md`
3. Add two Music prompt modes:
   - `music_score_bgm`: instrumental/score, verified file, beat/cue guide.
   - `music_song_master`: lyrics/style split, song structure, vocal persona, phrase map.
4. Add two typography contract templates:
   - `TYPOGRAPHY_CONTRACT_INFORMATION.md`
   - `TYPOGRAPHY_CONTRACT_LYRIC_HOOK.md`
5. Add Planner validation:
   - Contest: official text inventory must exist before Editor.
   - MV: phrase map and C-cut/microcut policy must exist before Editor.
6. Add mode-specific QC checklists.
7. Add monitor rule: monitor must not reopen Seedance/editor/package unless the mode-specific gate is satisfied.

## Minimal manifest schema

```json
{
  "project_mode": "contest_public",
  "music_mode": "score_bgm",
  "typography_mode": "information_contract",
  "mode_gate_version": "2026-05-26",
  "mode_gates": {
    "music_lock_required_before_planner": true,
    "typography_contract_required_before_editor": true,
    "official_package_gate": true,
    "microcut_required_before_editor": false
  }
}
```

For MV:

```json
{
  "project_mode": "mv_songfirst",
  "music_mode": "song_master",
  "typography_mode": "lyric_hook_contract",
  "mode_gate_version": "2026-05-26",
  "mode_gates": {
    "music_lock_required_before_planner": true,
    "phrase_map_required": true,
    "microcut_policy_required": true,
    "official_package_gate": false
  }
}
```

## Recommended next change

Patch the runtime scaffold so Director must write `PROJECT_MODE_LOCK.json` before Music/Planner dispatch. If no mode is locked, default to `contest_public` only when official contest/rubric/submission words are present; default to `mv_songfirst` when the brief mentions MV, lyrics, chorus, anime OP/ED, song, hook, or music video.
