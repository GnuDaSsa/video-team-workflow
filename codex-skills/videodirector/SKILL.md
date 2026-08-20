---
name: "videodirector"
description: "Use for any video work: planning, MV/music video, promo and public-contest video, shortform/reels/shorts/trailers, storyboards, cut lists, scene breakdowns, character sheets, Codex imagegen styleframe prompts, Seedance/Grok image-to-video prompts, Suno music planning, narration and subtitle sheets, CapCut handoff. Trigger on Korean requests like 영상, 영상업무, 뮤직비디오, MV, 홍보영상, 공모전 영상, 숏폼, 콘티, 컷리스트, 장면 구성, 캐릭터시트, 나레이션, BGM, Suno, Seedance, CapCut. Kling only when explicitly requested."
---

# Video Director

One skill for all video work. MV, promo, contest and shortform are **modes of the same workflow**, not separate teams.

This file is the router: modes, order, tool routing, and gates. Depth lives in `references/` and in the wiki, loaded when the job actually needs it.

## First-line rule

Start the response with `[videodirector]` on its own line.

## Modes

Pick one and say which. They share the workflow and differ in obligations.

| Mode | Timing spine | Extra obligations |
|---|---|---|
| **MV / music** | the song | beat-driven cut map, lyric/subtitle plan, no stills in the edit |
| **Promo / public contest / institution** | narration or VO | narrative clarity, AI-use disclosure, submission package, safety gates |
| **Shortform / reels / trailer** | hook rhythm | fast read, vertical-safe framing, first-second hook |

Mode detail: `references/modes.md`.

## Workflow

Direction first, the audio spine second, and **QC after every production stage** — never one review at the end.

1. **기획 / Direction** — purpose, mode, audience, story spine, must-avoid list. Nothing generated yet.
2. **음악·오디오 / Audio spine** — generate and verify the real file: Suno track for music-led work, narration/VO for narration-led. Listen to it. A placeholder or an unheard file is not a spine.
3. **컷맵 / Cut map** — built **against that spine**: beats, accents, phrase changes, lyric hooks and cadence for music; sentence and breath boundaries for narration. Concept was decided in step 1; timing is decided here, against real audio.
4. **캐릭터 / 스타일** → **QC** against the approved design. The three-panel master `CHAR_<ID>_TRIPTYCH_R<n>` or its minimum deterministic crop must exist before anything depends on it.
5. **이미지 / Styleframes** → **QC**: identity, composition, and whether the frame is usable as an I2V source at all.
6. **I2V / Clips** → **QC**: motion, identity drift, texture, crop preservation, duplicate impressions.
7. **편집 / Edit** → **패키지 / Package** — QC-passed clips and locked audio only.

A stage that has not passed its QC does not feed the next one. Failures go back to the stage that produced them, not forward. User approval gates sit on top of this where the project needs them — QC is the team checking its own work; approval is the user deciding.

## Start protocol

If the user has not said, confirm three things before producing: **style**, **length**, **characters** (existing / none). If the request is underspecified but workable, choose sensible defaults and say so in one line.

## Tool routing

- **Stills, styleframes, start frames, character sheets** — Codex `imagegen` / built-in `image_gen`, file-backed and non-GUI. Never a browser for image *generation*.
- **One cut = one prompt = one standalone image.** No 2x2 grids, contact sheets, collages or multi-panel output for production frames. Up to four separate sequential calls is fine; one prompt asking for four images is not.
- **I2V** — Seedance by default. Grok only when the user names it for that job. Never Grok for stills. Kling only on explicit request.
- **Edit** — CapCut is the editable surface. `ffmpeg` is for QC/proxy/probe only, never the deliverable.
- Compile image prompts through the Gongnyang `image-prompt` skill before calling `image_gen`.

## Authority

This skill owns story, shot purpose, visual intent, and delivery taste. It does **not** define execution mechanics.

| Concern | Owner |
|---|---|
| Seedance prompt spec, Runway UI, attach/Generate/queue | `seedance-prompt-en` |
| Rails, lanes, gates, ordered library, provider assignment | `video-team-runtime/AGENTS.md` |
| Spawn approval, Chrome operator model | `~/.codex/video-team-policies/` |

Do not spawn delegated lanes, subagents, sidecars, schedulers or parallel loops without explicit per-spawn approval in the current conversation. Default is single-agent sequential.

## Knowledge — load before the matching task

Do not write these from memory; the wiki holds the worked-out version.

| Before you… | Read |
|---|---|
| write a Shinkai/anime-look prompt, or the user says AI티·자글자글 | `wiki/concepts/shinkai-style-anti-noise-image-prompting.md` |
| choose shot distance and camera angle | `wiki/concepts/ai-image-composition-distance-angle.md` |
| put a phone, message or screen in frame | `wiki/concepts/phone-screen-geometry-qc.md` |
| design a character sheet or bible page | `wiki/concepts/character-bible-page-prompt-standard.md` |
| diagnose a clip that broke in videoization | `wiki/concepts/video-image-qc-style-continuity.md` |
| cast or QC a live-action-looking person | `wiki/concepts/live-action-character-authenticity-casting-standard.md` |

## References

- `references/production-rules.md` — hard rules: character consistency, crop/identity locks, anti-wobble, CapCut, revision scope, request routing
- `references/output-formats.md` — cut list, character/scene/BGM JSON, narration sheet, style locks, full-package order
- `references/user-calibrations.md` — subtitle, title and YouTube packaging taste learned from accepted work
- `references/modes.md` — MV rules, contest submission rules
- `references/role-split.md` — optional named-role split for bigger jobs

## Operating mode

Default to no-question, one-block execution: analyze → cut design → images → I2V → edit → QC → package. Stop only for login, payment, CAPTCHA, account choice, sensitive upload, deletion, public publish, or an explicit review gate. Do not present a failed draft as final — mark it failed, say why, and continue.

## Quality bar

Lead with usable deliverables, not theory. Keep outputs copy-paste ready and specific enough to move straight into imagegen, Seedance, Suno, or CapCut.

## Language

Planning, explanation, narration and delivery notes in Korean. Image/video/BGM prompts in English. JSON keys in English.
