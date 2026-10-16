---
name: "videodirector"
description: "Use for any video work: planning, MV/music video, promo and public-contest video, shortform/reels/shorts/trailers, storyboards, cut lists, scene breakdowns, character sheets, Codex imagegen styleframe prompts, Seedance/Grok image-to-video prompts, Suno music planning, narration sheets, and the fixed pre-production pipeline (concept options, style bible, storyboard, image prompts, production shelf). Trigger on Korean requests like 영상, 영상업무, 뮤직비디오, MV, 홍보영상, 공모전 영상, 숏폼, 콘티, 컷리스트, 장면 구성, 캐릭터시트, 나레이션, BGM, Suno, Seedance, 프리프로덕션, 스타일 바이블. Kling only when explicitly requested."
---

# Video Director

<!-- video-team-board:start -->
## Project kanban

Production `init`/`next` opens the upper-left Video Team Board. If bypassed, run
`~/.local/bin/video-team-board --project <absolute-runtime-project>` once.
Read-only records, not verified media, Hermes, an agent or scheduler.
No opening for advice/audits. To hide: `VIDEO_TEAM_BOARD_DISABLED=1`.
Closing stops refresh.
<!-- video-team-board:end -->

<!-- flow-malfoy-routing:start -->
## Flow / 공통 모션그래픽

명시적 FLOW/플로우 영상 생성은 runtime/AGENTS.md §1.4에 따라
`references/flow-malfoy-composite.md`로 연결한다. 일반/합성형을 다시 묻지 않는다.
분석 요청은 생성하지 않으며 기본 Seedance·진행 중 프로젝트는 자동 전환하지 않는다.

코드 모션그래픽·키네틱 타이포·쇼케이스 기획/QC에는 provider와 무관하게
같은 reference §3을 읽는다. 효과 목록 대신 레이어·음악 cue·모듈·수정 단위·재생
검수를 적용한다. no-text/clean footage 등 실제 요청 범위가 우선한다.
<!-- flow-malfoy-routing:end -->

Start the response with `[videodirector]` on its own line. This skill owns story, shot purpose, visual intent and delivery taste, **not** runtime execution procedure.

## Lean entry — classify before loading

1. Distinguish **advice/audit**, **one requested asset or revision**, and **new full production**. A question about the workflow is not a production job: do not initialize a project, open Runway, read all phase references, or create a new owner for it.
2. For an existing project, restore its `brief.md`, `state.json`, exact current blocker and `video-codex-runtime next --project <p>` before deciding the next action. Do not replay completed lanes or repeatedly dump the full state, transcript or wiki. For a new full project, initialize from the brief once, then follow `next` in the same owner.
3. Load only the reference for the **current** phase below. Reuse a document already read in this context unless its version or the phase changed. Read the selected Seedance version skill only when authoring or operating Seedance, not for every video question.
4. Give the first useful decision or artifact promptly. Briefly state chosen defaults when the request is workable but underspecified; ask about style, length or characters only when a missing answer truly blocks production. Never replace actual media/QC evidence with a plan.

JEV-style advisory classification is **not** a default startup step. Use code for established input steps, bounded JEV advice for semantic candidate selection, and the current owner for authoring, visual judgment and novel recovery. No new agent is created. Seedance's `aside-operator.md` owns the concrete integration; do not import native Aside author/language/UI rules into Codex. External classifier calls still require current-scope explicit approval, and advice never bypasses execution gates.

## Mode and spine

| Mode | Timing source | Extra obligation |
|---|---|---|
| MV/music | Actual song and listening | Beat/phrase block map, lyric hierarchy, no stills as clips |
| Promo/public contest/institution | Requested narration/VO or approved visual-only scope | Story clarity, factual safety, AI-use and submission package |
| Shortform/reels/trailer | Hook and reading rhythm | Opening hook, vertical-safe composition |

Rail (runtime v5): `director → music → planner → image_creator → image_qc → seedance → seedance_qc → package`. There is **no edit lane**: package delivers QC-approved clips in storyboard order (no edited master, no CapCut draft). The runtime's explicit visual-only exception, not this skill, decides when audio may be deferred. A one-asset request still respects its dependent gates but does not silently enlarge into an entire film.

## Fixed pre-production pipeline (preprod v5)

Every new project has `preprod/` (marker `preprod/PREPROD_V1`), scaffolded by `python3 runtime/scripts/preprod.py init --project <p>` from `runtime/templates/preprod/`. The script owns file schemas, locks and the shelf; field names below are exactly its validator names. Contract: `docs/contracts/2026-10-16-preprod-shelf-v5.md`.

| Stage | Owner | Files you produce | Lock / checkpoint |
|---|---|---|---|
| P0 concept | director | `preprod/00_concept/concept_options.md` (≥3 `## Option X`) → `concept_lock.json` | **user picks an option**; `lock --stage concept --approval-quote "<user words>"` |
| P1 style bible | director | `preprod/01_bible/style_bible.json` | lane self-check: `check` then `lock --stage bible` |
| P2 storyboard | planner | `preprod/02_storyboard/storyboard.json` | **user approves the storyboard**; lock with quote (planner block map / video attributes are then derived, never hand-written) |
| P3 image prompts | image_creator / image_qc | `preprod/03_image_prompts/<REF>.prompt.txt` (English) + `image_plan.json` (ref → approved `asset_id`) | every ref approved in the media registry |
| P4 shelf | seedance (prompting) | `preprod/04_shelf/<BLOCK>/prompt.txt` from the generated `brief.md` | `shelf-check` → `shelf-lock`; **user releases the shelf once** (`shelf-release --approval-quote`) |
| P5 production | seedance (production) | nothing new — copy-paste the released shelf | `shelf-verify` + `paste-prompt --pack <shelf>/pack.json` |

Hard rules:
- **No new creative decisions at production time.** A change request (story, look, shot, prompt wording, ref choice) goes back to the stage that owns it, is edited there and re-locked; every downstream lock goes STALE and is redone. The superseded copy moves to `preprod/_superseded/`; there is always exactly one current version.
- Model-facing text is **English only**: `style_block_en`, `identity_block_en`, `description_en`, image prompts and shelf prompts. Plan, explain and talk to the user in Korean.
- Do not write P4 prompts by hand from memory; `shelf-brief` generates the brief (style/identity verbatim, refs, shots, end frame) and `shelf-check` enforces ≤3500 chars (aim ≤3200), the `15 seconds, N shots:` header, `Shot k (a-bs):` markers, verbatim STYLE/IDENTITY, exact `@ImageN` tokens.

Commands: `python3 runtime/scripts/preprod.py init|status|check|lock|shelf-brief|shelf-check|shelf-lock|shelf-release|shelf-verify --project <p> ...` (see `runtime/templates/preprod/README.md`).

### P0 — writing a good `concept_options.md`

Write three genuinely different options (`## Option A`, `## Option B`, `## Option C`), not three wordings of one idea. Each option has:
1. **Logline** — one sentence: who, wants what, what stands in the way / what changes.
2. **Emotional arc** — `hook` (first 3 s reason to keep watching) → `build` → `peak` (the one image people remember) → `out` (musical or narrative resolution, not a fade).
3. **Differentiator** — why this is not the generic version of the brief (angle, device, visual idea).
4. **Must-avoid** — clichés, factual risks, rejected looks from user calibrations.
5. Medium / aspect / approximate runtime and the block count it implies (15 s blocks).

Present the three in Korean with a recommendation, then wait. `concept_lock.json` copies the chosen option: `title, logline, audience, selected_option, mode, medium(+medium_components if mixed), aspect_ratio, target_runtime_sec, emotional_arc{hook,build,peak,out}, must_avoid[]`. Lock only with the user's actual words as `--approval-quote`.

### P1 — the style bible (`style_bible.json`)

The bible is the single source of look; it is pasted, not paraphrased.
- `palette_hex`: 3–7 `#RRGGBB` values with a role in mind (key, shadow, accent).
- `lighting`: one recipe (key direction/quality, time of day, practicals, contrast).
- `texture`: grain, line quality, surface/material treatment, rendering style.
- `lens_grammar`: default focal families, depth of field, how camera moves are allowed to feel.
- `forbidden_looks[]`: concrete looks to reject (also feeds the shelf AVOID list).
- `style_block_en` (≤600 chars): one English paragraph that is pasted **verbatim into every video prompt**. Make it self-sufficient: medium, rendering, palette words, light, texture, lens feel. No shot-specific content.
- `characters[]`: `id` (UPPER_SNAKE), `identity_block_en` (≤350 chars, fixed face/hair/body/wardrobe/age impression, no expressions or actions), `sheet_ref_id` (the triptych ref in `image_plan.json`). Character sheets follow the triptych standard in `references/character_sheet_prompt_standard.md` (runtime: `runtime/references/`) and `references/production-rules.md` § Character-sheet-first gate.
- `locations[]`: `id`, `description_en` (geometry, materials, light sources).
- Optional `resolution` (default `720p`).

### P2 — the storyboard (planner, user-approved)

`storyboard.json` replaces the old free-form blueprint YAML. One block = one generation = 15 s (`duration_sec` must match the duration lock); `order` 1..n; `purpose`, `audio_route`, `cast[]`, `location_id`, `refs[]` (1–7 ref ids), `end_frame` (the hand-off image to the next block), optional `risks[]`, and 1–4 `shots[]` with contiguous `start_sec`/`end_sec`, `shot_id = <BLOCK>_S<k>`, controlled `shot_size`/`angle`/`camera_move` vocabulary (lists in `preprod.py`), optional `lens`, `composition`, `action`, `must_include[]` (short phrases that must survive into the prompt), optional `edit_out`. Use `/Users/gnudas/wiki/concepts/storyboard-production-blueprint-standard.md` for blocking/geometry thinking; `references/output-formats.md` maps the old YAML fields to these keys. Show the storyboard to the user in Korean (table per block) and lock only with their approval quote.

Continuity knowledge stays useful even without an edit lane: design each block's `end_frame` so the next block can start from it, give actions a clean beginning and end inside the 15 s (handles), and avoid cuts that only an editor could hide.

## Tool and authority boundaries

- Stills, start frames and character sheets: built-in Codex `image_gen` after the Gongnyang `image-prompt` compiler. Production is one cut = one prompt = one standalone image; character triptychs are identity-design exceptions. Never use Grok for stills by default.
- Video: Seedance by default; Grok only when named for that project, Kling only when explicitly requested. Follow exactly one selected Seedance version skill for prompt/UI/queue procedure.
- No edit/CapCut stage in this rail. `ffmpeg` is for QC, probes and contact sheets only. Post-production knowledge kept for a future editor rebuild: `references/post-production-knowledge.md` (not active).
- Runtime rails, lane order, duration, media registry and safety: `/Users/gnudas/Documents/Codex/video-team-runtime/AGENTS.md`. Spawn approval and browser operator policy: `~/.codex/video-team-policies/`. Default is one owner, sequential; no unapproved agent, sidecar, scheduler or second browser loop.
- A prompt, status string, attestation or provider card is not finished media. Confirm file/path/size/codec/duration and visual/audio QC appropriate to the deliverable.

## Read only when the phase needs it

| Work now | Reference |
|---|---|
| MV vs public contest details | `references/modes.md` |
| Accepted mode-specific video memory | `references/mode-calibrations.md` only for the relevant MV/public phase |
| Song-first MV production/QC | `references/mv-production-calibrations.md` |
| Recurring character identity lock | `references/character-identity-calibrations.md` |
| Production or revision hard rules | `references/production-rules.md` |
| Deliverable layout/manifest, old→new storyboard field map | `references/output-formats.md` |
| Accepted user packaging/thumbnail taste | `references/user-calibrations.md` |
| Optional named-role split after approval | `references/role-split.md` |
| Typography/caption/edit lessons (post-production, not in this rail) | `references/typography-calibrations.md`, `references/post-production-knowledge.md` |
| Shinkai/anime appearance or noisy stills | `/Users/gnudas/wiki/concepts/shinkai-style-anti-noise-image-prompting.md` |
| Storyboard, blocking, shot board | `/Users/gnudas/wiki/concepts/storyboard-production-blueprint-standard.md` |
| Camera distance/angle | `/Users/gnudas/wiki/concepts/ai-image-composition-distance-angle.md` |
| Phone/screen geometry | `/Users/gnudas/wiki/concepts/phone-screen-geometry-qc.md` |
| Character bible or photoreal casting | `/Users/gnudas/wiki/concepts/character-bible-page-prompt-standard.md`; for photoreal people also `live-action-character-authenticity-casting-standard.md` |
| Broken I2V motion/crop/style | `/Users/gnudas/wiki/concepts/video-image-qc-style-continuity.md` |

For live action, read matching sections of `/Users/gnudas/wiki/concepts/video-prompting-live-action.md` before planning/image authoring/QC, not the whole wiki. `툰킷 문법` activates `toonkit_2d_snappy_v1` only for the named 2D/stylized blocks; the selected Seedance skill owns the actual prompt grammar. Plan and explain in Korean; all model-facing prompts (image and Seedance) are English only. The legacy `prompt_language_override` exists only for pre-v5 projects.

Default to no-question execution within the authorized scope. Stop for login, payment, CAPTCHA, account choice, sensitive upload/deletion, public publish/submission or an explicit review gate (P0 concept choice, P2 storyboard, P4 shelf release). Mark failed media honestly and repair it; never present a weak draft as final.

구도·카메라·키네틱 타이포·비트 전환의 참고 선택은 `/Users/gnudas/wiki/concepts/awesome-ai-motion-video-reference.md`의 해당 목적만 읽는다. 2~3개 후보에서 선택 slug·고정 commit·선택 근거를 P1 bible 또는 P2 storyboard에 반영한다(제작 단계에서 새로 고르지 않는다). no-text 우선, 데모 수치·예시 사실은 일반 규칙이 아니다.

<!-- advanced-shot-contract:start -->
컷 작성 시 `/Users/gnudas/Documents/Codex/video-team-workflow/docs/advanced-shot-prompting.md`의 설계 카드로 목적·공간·시간·참조 역할과 인접 컷 연속성을 분리한다. Codex 영상 패킷에서는 해당 block의 planner/video_attributes.json methods에 `advanced_prompting`을 기존 값과 함께 선택한 뒤 기존 knowledge-select를 사용하고 `advanced-shot-contract` 선택을 확인한다. 지식 적용 기록과 실제 미디어 QC는 별도다. 현재 프로젝트 overrides의 도구·비용·대기 간격이 예시보다 우선한다.
<!-- advanced-shot-contract:end -->
