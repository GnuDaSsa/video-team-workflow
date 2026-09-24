# Global Codex Instructions

## 한국어 강의·발표자료 말투 기본 적용

로컬 Codex에서 프로젝트나 작업 폴더와 관계없이 한국어 강의·발표자료를 기획·작성·생성·수정할 때는 `/Users/gnudas/.codex/skills/korean-deck-voice/SKILL.md`를 먼저 읽고 적용한다. HTML 강의자료, 슬라이드/PPT, 제목·본문·캡션, 발표 대본의 장표화와 문구 검수에 적용하며 별도 스킬 호출을 요구하지 않는다.

세부 규칙의 원본은 위 스킬 한 곳으로 유지한다. 사용자의 원문·사실·요청 범위와 지정 템플릿·제작 방식을 보존하고, 결과 전달 전 스킬의 반영 후 확인을 수행한다. 사용자가 해당 작업에 다른 말투를 명시하면 그 지시를 따른다. 일반 보고서·블로그·일상 대화에는 확대 적용하지 않으며 기존 강의자료를 요청 없이 일괄 수정하지 않는다.

## 최우선 실행 책임 — 말뿐인 종료 금지

이 항목은 이 사용자 지침 안에서 일반적인 진행 보고·종료 관행보다 우선한다. 시스템/개발자 지침, 안전·권한·사용자의 중단 요청을 우회하는 권한은 아니다.

- 사용자가 실행·수정·제작·문제 해결을 요청하면, 사과·동의·계획·“하겠습니다”만으로 턴을 끝내지 않는다. 가능한 실제 작업을 같은 턴에서 수행하고 결과를 확인한다.
- “원인 확인”, “파일 작성”, “시도함”은 요청한 실제 결과의 완료가 아니다. 중간 진단은 진행 보고로만 사용하고, 안전한 수정·재시험·검증으로 이어간다.
- 통상적인 GUI 오류, 포커스 문제, 비활성 버튼, 타임아웃, 업로드 실패를 곧바로 사용자에게 떠넘기지 않는다. 관찰→원인 가설→승인 범위 내의 서로 다른 복구 방법→실제 결과 재확인을 수행한다. 같은 실패 조작의 맹목적 반복이나 안전장치 우회는 금지한다.
- 중단 보고는 사용자만 해결할 수 있는 권한·로그인·CAPTCHA·결제·명시적 선택이 필요하거나, 허용된 복구 방법을 근거 있게 소진해 외부 변화 없이는 진전할 수 없을 때만 한다. 확인된 사실, 이미 시도한 방법과 결과, 남은 정확한 차단 조건을 짧게 제시한다. 미확인 원인을 확정하거나 “불가능”으로 단정하지 않는다.
- 완료 보고는 파일·테스트·실제 GUI 결과 등 요청에 맞는 증거로 뒷받침한다. 해결되지 않았다면 완료로 포장하지 않는다. 지속 수행 도구가 실제로 활성화되어 있지 않으면 “계속 진행 중”이라고 말하고 턴을 종료하지 않는다.
- 요청이 순수 설명/기획이거나 사용자가 중단·검토 대기를 지시한 경우에는 그 범위를 지킨다. 새 에이전트·예약·브라우저 소유자, 유료 전환 및 고위험 동작의 별도 승인 의무는 그대로다.

## Codex App Runtime Video-Team Delegation Mode — 2026-05-16

When the current working directory is under `/Users/gnudas/Documents/Codex/video-team-runtime/`, follow the lane prompt and the local project `brief.md`/`state.json` first.

This is a Codex-native workflow. Codex is the single entrypoint and execution owner; no external orchestrator, sidecar, or relay layer is part of the route.

Lane rules:
- For v4 projects, write lane metadata under `lanes/<lane>/` and write/register all actual media under the project's canonical numbered `media/` tree. Legacy projects keep their existing layout until explicitly migrated.
- Update `status.json` and `result.md` for the lane.
- Real media completion requires verified files, paths, sizes, duration/codec where relevant, or verified GUI state. Prompts/plans/placeholders are not completion.
- Parallel lanes require explicit per-spawn user approval first. The v4 image stage may use up to three bounded non-agent generation processes over immutable prompts; this is not permission to spawn image agents or parallel lanes.
- Public upload, publish, contest/government submission, email send, personal-info form submit, payment, password/2FA, and irreversible deletion require explicit user approval.
- Login/CAPTCHA/payment/permission/account-limit gates require BLOCKED and the exact user action; ordinary recoverable GUI errors follow the execution-responsibility rule above before escalation.

## Subagent / lane spawn approval gate — 2026-07-21

After the video team (or any team workflow) is invoked, work must not fan out into extra agents on its own.

- Spawning any additional agent surface — Codex delegated lane, subagent/worker/explorer, external orchestrator sidecar, background monitor/scheduler/cron/heartbeat, or a second concurrent browser-automation loop — requires **explicit user approval for that specific spawn in the current conversation**. The approval request must name the lane/role, purpose, and expected output.
- Default execution model is single-agent, sequential, in the main conversation. Parallel lanes are an exception the user grants per project/turn, not the default. Role templates define responsibilities, not standing permission to instantiate agents.
- Single pre-approved exception: one 15-minute **foreground wait tool session** in the same Codex turn and existing Runway browser while an armed queue is active. It is not a scheduler and cannot create a future model turn; the owning turn must remain attached, consume the result, and re-read the board. It is not a resident observer/agent/process, and only one wait may be pending.
- Rule files operate latest-only: corrections edit/delete old text in place instead of appending dated layers. History and rollback live in the `GnuDaSsa/video-team-workflow` git repo and `~/.codex/archive/`. Deployed policy: `~/.codex/video-team-policies/subagent_approval_gate_20260721.md`.

## Codex Harness Auto Workflow

For most coding-related repository work, apply the local Codex harness workflow automatically.

Trigger for:

- feature implementation
- bug fixes
- refactors
- tests or CI work
- code review follow-up
- frontend/backend changes
- repo maintenance that changes code, docs, build config, or tests

Skip for:

- non-repository tasks
- quick terminal/status questions
- pure explanation or brainstorming
- user explicitly asks not to use the harness

Before coding in a repo:

1. Identify the repo root from cwd or the explicit target path.
2. Look for `AGENTS.md`, `AGENTS.harness.md`, `docs/harness-config.json`, and `docs/harness-state.json`.
3. If harness files are missing and the task is substantial repo coding work, run `/Users/gnudas/.local/bin/codex-harness-kit init`.
4. Run `/Users/gnudas/.local/bin/codex-harness-kit validate-harness`.
5. Run `/Users/gnudas/.local/bin/codex-harness-kit check-state` and use the recovered goal, contract, blockers, next step, and verification config to guide implementation.

Before finishing meaningful repo work:

- Run the smallest useful verification command.
- Update harness state, active contract, decisions, or project memory when applicable.
- Report what verification ran and what did not run.

## Visible Operation Labels

When a distinct role, agent, skill, tool phase, or workflow is active, make it visually obvious in the CLI transcript by prefixing short status updates with a bracketed label.

Use labels such as:

- `[reviewer]` for code-review mode or auto-review work
- `[explorer]` when an explorer subagent is active
- `[worker]` when a worker subagent is active
- `[harness]` for codex-harness-kit init, validation, state recovery, or wrap-up
- `[github]` for GitHub PR, issue, or CI work
- `[test]` for verification commands
- `[shell]` for local terminal investigation
- `[browser]` for browser automation

Emit a concise labeled update before starting a meaningful phase and when switching roles, so the user can see what is operating without reading tool internals.

## Global LLM Wiki + 90% Context Capture Loop — 2026-05-25

- For all non-trivial Codex work, treat `/Users/gnudas/wiki` as the standing LLM Wiki/knowledge hub. Before durable decisions, orient from `/Users/gnudas/wiki/SCHEMA.md`, `/Users/gnudas/wiki/index.md`, and relevant wiki pages; search the wiki when a task touches prior work, user conventions, workflows, reusable lessons, or project history.
- Do not wait for the user to explicitly say “wiki”. Use the wiki as background context for coding, research, media, operations, planning, and troubleshooting. Skip only truly trivial one-shot answers.
- When the active thread/context is roughly **90% full**, or before manual `/compress`, likely automatic context compression, handoff, session end, or a long pause, append a concise capsule to `/Users/gnudas/wiki/_hub/context-capsules/YYYY-MM-DD.md`. Follow `/Users/gnudas/wiki/_meta/context-recording-hub.md`.
- A capsule should capture: goal, current state, durable decisions/corrections, artifact paths, blockers, exact next resume point, and whether to promote the lesson into a wiki page, seed, skill, or memory.
- Capsules are staging records. Promote reusable lessons into canonical wiki pages/seeds/skills/memory; do not leave important knowledge only in chat or in the capsule.
- Never record secrets, passwords, tokens, payment info, personal form data, or unnecessary private message bodies. Summarize sensitive context by role/path only.

## Video-Team Workflow Default and Feedback Promotion

- Treat every non-trivial video request as a run of the user's canonical video-team workflow, not an ad-hoc media pipeline. Start from the current project state and the authority order in `/Users/gnudas/Documents/Codex/video-team-runtime/AGENTS.md`; use the repository source at `/Users/gnudas/Documents/Codex/video-team-workflow` for durable rule changes.
- Capture material process feedback as project evidence first. Promote it only when the user explicitly asks for a standing rule or when it is a repeated, verified cross-project failure; route it to the one canonical owner rather than copying rules into project folders.
- After a durable promotion, verify the smallest relevant checks, make an isolated Git commit that excludes unrelated working-tree changes, and sync it to `GnuDaSsa/video-team-workflow`. Do not create a background writer, scheduler, or extra agent to do this.
- Follow `/Users/gnudas/Documents/Codex/video-team-workflow/docs/video-feedback-promotion-protocol.md` for the evidence, routing, privacy, and release procedure.


## Video craft memory — load only the matching phase

The detailed video craft and QC calibrations are installed under `/Users/gnudas/.codex/skills/videodirector/references/`. They are **not** startup reading for every request. For a matching production phase, read only:

| Current work | Reference |
|---|---|
| MV vs public-contest story/caption mode | `mode-calibrations.md` |
| Song-first MV production, cut rhythm, I2V/identity continuity | `mv-production-calibrations.md` |
| Recurring character identity sheets | `character-identity-calibrations.md` |
| Typography, CapCut captions, alignment or transition QC | `typography-calibrations.md` |

The unchanged safety/approval clauses below and the runtime authority order still apply. A video-workflow question or unrelated Codex task does not require loading these references.

## Public contest upload/submission safety and copy workflow — 2026-05-06

This section is contest/submission memory, not generic MV memory. Apply it when the project involves public institutions, contest rules, forms, YouTube links, email/package submission, or personal-information workflows.

Lessons from the Sangju public video contest project:

- YouTube upload: before uploading, verify the exact channel/account visually and by URL/channel name. If the user names a specific channel, do not upload to another similarly named channel. If the user does not explicitly ask for public release, upload/save as **private** by default. Do not click public `Publish/게시` without explicit final confirmation.
- Contest/Government form submission: filling a draft with the user's known information is allowed when requested, but final `Submit/제출` for a contest, government, or personal-information form is a high-impact external action. Stop before final submit unless the user explicitly says to submit that exact form now after the filled fields are visible/ready.
- When the user says the final edit is good and asks for the application/submission link, open Finder on the final master/package, open the official contest page, identify the submission route (email vs form), download/open required application forms if available, and prepare a mailto/draft or copy package. Do not send the email or final-submit the form without explicit confirmation.
- Metadata/copy package: public-contest delivery should include or prepare title, YouTube description/hashtags, AI-use disclosure, production intent, synopsis, prior-contest history, and password/link notes. These should be written in a polished public-sector tone: clear, explanatory, not overly poetic, and within character limits.
- Korean browser form input: Safari/YouTube/Google Forms can drop Korean characters when using synthetic typing. Prefer clipboard paste or direct JavaScript setter for Korean text, then verify the field value. After every multi-field fill, audit labels and values so `제작 의도`, `시놉시스`, `AI 활용 내역`, and link/password fields are not swapped.
- Field-specific copy distinction: `AI 활용 내역` describes tools/process; `제작 의도` explains why the work was made and what value it communicates; `시놉시스` summarizes the story flow. Never reuse the same paragraph across these fields.


## ChatGPT web send-button safety rule — 2026-05-07

When automating ChatGPT web in Safari/Browser for image generation, prompt submission, or any composer workflow, avoid accidental activation of Voice mode. The user has observed repeated mistakes where the agent clicks the voice/받아쓰기/Voice button instead of the send button.

Required safeguards:
- Never click the last visible round composer button by position alone. Do not assume the rightmost button is send.
- Before sending, locate the exact send control by a stable selector/label such as `button[data-testid="send-button"]` or an accessible label containing `프롬프트 보내기` / `Send prompt`.
- Explicitly reject buttons whose accessible label or text contains `Voice`, `음성`, `받아쓰기`, `마이크`, `dictation`, or `voice mode`, even if they are near the composer.
- After inserting text, re-query the DOM and verify the send button is enabled and still has the send-specific selector/label before clicking.
- If only a voice/받아쓰기 button is visible, do not click it. Wait, refocus the composer, dispatch an input/change event, or use Enter only if it has already been verified not to trigger voice mode in that UI state.
- If Voice mode or “음성으로 연결 중” is accidentally opened, cancel/close it immediately and record the incident in the local run notes before retrying.
- For fallback ChatGPT web image production only, prefer this safe sequence: set composer text via direct DOM setter/computer-use `set_value`/direct typing → verify composer contains expected text → verify `send-button` identity → click once → verify a normal chat turn started. Do not use `pbcopy`, AppleScript clipboard, or clipboard paste for Codex GUI prompt insertion on this Mac; it can fail silently or return exit 1. Do not use coordinate clicks for ChatGPT submit unless there is no DOM alternative and the user has approved a manual fallback.

## Kim Gu contest submission email workflow — 2026-05-10

For the current Kim Gu / 백범 김구 public-contest video project and future follow-up turns in this project, when the user says to send the final video/package by email, use `sajw1994@korea.kr` as the default recipient.

Workflow:
1. Use the approved final master/package from the project as the attachment or link.
2. If the attachment is too large or the mail client rejects it, fall back to Naver Mail as the sending route.
3. Before any actual send, show the recipient, subject, body, attachment/link, and final file path to the user.
4. Sending is an externally visible action: do not click final Send/전송 until the user explicitly approves that exact prepared email.
5. If the user simply says “메일 보내라” after approving the final video in this project, interpret the recipient as `sajw1994@korea.kr` unless the user states another recipient.

## Video-team authority order — 2026-07-28

This block is the tie-breaker. Previously this file said "Seedance follows the skill" while `video-team-runtime/AGENTS.md` said "this file wins over everything" — circular authority, so behaviour depended on which file a session loaded first.

| Rank | Document | Owns |
|---|---|---|
| 1 | `~/Documents/Codex/video-team-runtime/AGENTS.md` | rails, lane order, gates, escalation ladders, provider assignment, prompt-authoring routing, safety gates |
| 2 | `~/.codex/skills/seedance-prompt-en/` (2.0/default) and `~/.codex/skills/seedance25-prompt-en/` (explicit 2.5) | Versioned Seedance prompt spec and Runway UI operation; the 2.5 adapter reuses the shared helper |
| 3 | `~/.codex/video-team-policies/` | spawn approval gate, Chrome operator model |
| 4 | `videodirector` | story, direction, quality bars — **never execution procedure** |

Within rank 2's scope (Seedance UI and prompt spec), rank 2 wins over rank 1. Within rank 1's scope (rails, gates, safety), rank 1 wins. Do not restate a rule in two places; leave a pointer instead.

Never write a rules copy inside a project folder. Project exceptions go in that project's `docs/project_overrides.md`, citing the clause number.

## Seedance execution authority

Seedance prompt authoring and Runway UI operation follow the selected version skill: explicit Seedance 2.5 requests use `/Users/gnudas/.codex/skills/seedance25-prompt-en/`; explicit 2.0 and unversioned Seedance requests use `/Users/gnudas/.codex/skills/seedance-prompt-en/`. Do not load both for one block or add UI upload/click/queue/scheduler rules here.

## Gongnyang image-prompt compiler default — 2026-07-12

For the user's raster-image work, load the installed Codex skill `/Users/gnudas/.codex/skills/image-prompt/SKILL.md` before calling built-in `image_gen`. Compile the rough request with the Gongnyang prompt rules, then pass only the compiled production prompt to `image_gen`.

- Apply by default to new still images, posters, key art, styleframes, character/model sheets, product images, card news, infographics, comics, and image prompt packages.
- The Gongnyang skill is the prompt-compilation layer; Codex built-in `image_gen` remains the actual still-image generator.
- For high-value prompts, run `/Users/gnudas/.codex/skills/image-prompt/scripts/check_prompt.mjs` and require `ok: true` before generation.
- Existing higher-priority video rules remain in force: recurring-character sheets precede dependent production frames; attach and verify approved references; one production cut equals one standalone image; no Grok still generation; no production grids/contact sheets.
- For edits of an existing image, preserve the user's requested edit and supplied reference as the primary constraint; use Gongnyang rules only where they do not distort that edit intent.
