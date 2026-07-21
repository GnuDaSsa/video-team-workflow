---
title: Video Team Seed System
created: 2026-05-12
updated: 2026-05-26
type: concept
tags: [video, workflow, agents, dataset, seed]
sources: [raw/transcripts/hermes-session-capture-20260512-142448.md, raw/transcripts/video-team-project-thread-routing-20260523.md, raw/transcripts/video-team-anime-song-mode-routing-20260523.md, raw/transcripts/video-team-suno-list-download-rule-20260523.md, raw/transcripts/video-workflow-lockdown-fixed-rail-20260525.md, raw/transcripts/hermes-session-capture-20260525-200049.md]
confidence: medium
contested: false
contradictions: []
---

# Video Team Seed System

## Definition

`Video Team Seed System`은 사용자의 영상/MV/공모전 작업 경험을 LLM Wiki 안에서 재사용 가능한 제작 시드로 컴파일하는 운영 방식이다. raw transcript는 작업 흔적이고, seed page는 다음 영상 작업을 시작할 때 fixed runtime/Kanban rail에서 브리프·컷 구조·lane handoff·QC 기준으로 변환할 수 있는 실행 원천이다.

이 시스템은 [[hermes-agent]], [[hermes-usage-patterns]], [[video-typography-operating-manual]]을 연결해, 단순한 회고 저장소가 아니라 새로운 영상 프로젝트의 발아점(seed bank)이 되도록 한다.

## Why it matters

영상팀 작업은 공모요강, 음악, 스타일프레임, I2V, CapCut 편집, 타이포그래피, QC, 제출 패키징이 얽혀 있어 매번 처음부터 설명하면 품질이 흔들린다. Wiki seed는 반복되는 판단을 다음과 같이 압축한다.

- 어떤 종류의 영상인지: 관광/공공/브랜드/MV/숏폼/제품/행사/교육
- 성공 기준이 무엇인지: 공식 규격, 심사 기준, 시청자 효과, 최종 제출 형식
- 어떤 제작 레일을 써야 하는지: fixed Kanban rail, Suno/Music Lock, Seedance 2.0 multi-reference block, CapCut, QC
- 어떤 실패를 피해야 하는지: raw still timeline filler, music not locked, headless login loss, JSON-only CapCut proof, caption clipping
- 어떤 역할에게 무엇을 handoff해야 하는지: Director, Music, Visual, Editor, QC

## Seed page contract

새 seed page는 `seeds/` 아래에 저장하고 다음 항목을 포함한다.

1. Project Archetype
   - contest film, tourism MV, brand film, public campaign, product ad, short-form, documentary, educational explainer 등.
2. Source Evidence
   - raw transcripts, official rules, reference pages, prior project pages.
3. Winning Pattern
   - 어떤 콘셉트 구조가 먹히는지, 왜 그런지.
4. Non-goals / Anti-patterns
   - 반복 실패, 금지된 우회, 품질 저하 패턴.
5. Production Seed
   - 다음 작업의 초기 prompt/brief로 복사 가능한 짧은 seed.
6. Role Handoff Map
   - 어떤 fixed lane(`director`, `music`, `visual`, `qc`, `editor`)이 어떤 gate와 queue evidence로 다음 lane에 넘길지.
7. Acceptance Criteria
   - 산출물 PASS 기준과 검증 방법.
8. Next-use Prompt
   - “이 seed를 기반으로 새 프로젝트를 시작하라”는 한 문단 지시문.


## Discord-native audio review handoff

유타(Music)는 Suno 후보를 다운로드/검증한 뒤 로컬 경로만 보고하면 안 된다. 사용자가 Discord 안에서 바로 들어볼 수 있도록 TOP 후보 오디오를 native attachment로 업로드하고, TOP1/TOP2/TOP3·제목·길이·BPM·추천 이유·`사용자 선택 전 NOT_LOCKED / Planner 대기`를 함께 남긴다. Hermes relay에서는 `MEDIA:<absolute_audio_path>`를 사용한다. Music lane이 직접 업로드하지 못하면 `lanes/music/discord_candidate_proposal.md`에 정확한 메시지와 업로드 파일 목록을 써서 Director/Hermes relay가 반드시 올리게 한다.^[raw/transcripts/video-team-discord-audio-attachment-review-20260523.md]

## Suno list-first download rule

유타(Music)의 Suno 운영은 batch generation 후 list/grid 다운로드를 기본으로 한다. 후보를 쭉 생성한 뒤 Create/Library 목록에서 각 row/card 맨 오른쪽 끝에 떠 있는 둥근 `...` 메뉴로 오디오를 다운로드하고, 그 다음 ffprobe/청감 피드백을 한다. Codex Computer Use가 곡 제목/커버를 눌러 상세 페이지로 들어가 헤매는 것은 anti-pattern이며, 상세 페이지는 카드 `...` 다운로드가 실제로 막혔을 때만 fallback으로 사용한다.^[raw/transcripts/video-team-suno-list-download-rule-20260523.md]

## Music mode ownership and anime-song routing

Director/고죠는 Music lane에 최종 Suno prompt나 가사를 넘기지 않는다. Director는 컨셉, 목표, 러닝타임, 톤, 금지사항만 전달하고, 유타(Music)가 곡 형식, 가사, 보컬 페르소나, 스타일 프롬프트, variation plan을 직접 만든다.^[raw/transcripts/video-team-anime-song-mode-routing-20260523.md, raw/transcripts/video-team-suno-list-download-rule-20260523.md]

Suno mode routing is a production gate: instrumental BGM/score는 Simple Mode + Instrumental ON + arrangement-only description이고, 일본 애니 OP/ED·MV song·vocal song·character song·hook/chorus 요청은 Advanced/Custom Mode이다. Advanced/Custom에서는 Lyrics에 실제 가사와 `[Intro]`, `[Verse]`, `[Pre-Chorus]`, `[Chorus]`, `[Bridge]`, `[Outro]` 같은 structure tag를 넣고, Style에는 anime OP/ED sound, BPM, vocal persona, instrumentation, production, energy arc를 별도로 작성한다. scene description이나 cut list를 Lyrics에 넣으면 안 된다.^[raw/transcripts/video-team-anime-song-mode-routing-20260523.md, raw/transcripts/video-team-suno-list-download-rule-20260523.md]

## Current fixed-rail runtime contract

새 영상/MV/공모전 미션에서 `#헤르메스-메인`은 일반 command/router이며 영상 제작 실행 창구가 아니다. 영상 전용 명령 표면은 `#영상팀`의 `영상워크플로-관제` thread(`1505047707864006776`)이다. 새 프로젝트는 `~/.local/bin/video-codex-runtime`으로 만들고, 생성 직후 `video-codex-runtime kanban-plan --project <project>`가 만든 fixed Kanban rail만 사용한다. Discord 대화 누적이 아니라 project `manifest.json`, `queues/*.jsonl`, lane `status.json/result.md`, fixed Kanban cards가 source of truth다.^[raw/transcripts/video-workflow-lockdown-fixed-rail-20260525.md]

Kanban은 임의 subagent, `delegate_task`, 새 profile을 만들지 않는다. 역할은 고정 lane으로만 매핑한다: Director/Planner/Retry Router → `director`; Music → `music`; Image Creator/Seedance Operator → `visual`; Image QC/Seedance QC → `qc`; Editor/Package → `editor`. 오래된 Gojo role-mention 직접 handoff는 중지되었고, 정상 handoff 표면은 fixed Kanban card + runtime manifest/queue event다.^[raw/transcripts/video-workflow-lockdown-fixed-rail-20260525.md]

역할 순서는 `Music Lock → Planner Cut Map/Block Map → block별 Image/QC/Seedance/QC 병렬 → Editor → Package`이다. Music Lock은 실제 오디오 파일·duration/codec·Suno provenance·beat/cut guide로 확정되어야 하며, 그 뒤 Planner가 cut map/block map을 만든다. 과거 Grok 4-cut microbatch/ChatGPT 4-output 고정 루프는 폐기되었고, 현재 기준은 Seedance 2.0 multi-reference block이다. 각 block의 reference 수는 Block Map의 `reference_count_required`가 결정한다.^[raw/transcripts/video-workflow-lockdown-fixed-rail-20260525.md]

Music lane 실패는 프로젝트 blocker일 뿐 아니라 재사용 규칙의 입력이다. 유타가 Suno 음악을 만들지 못했거나 stale/local 파일을 잘못 lock한 원인을 해결하면, `lanes/music/logs/music_failure_learning.md`와 result 요약에 해결 원인을 남겨 다음 LLM Wiki compile이 Music profile/runtime template에 반영할 수 있어야 한다.^[raw/transcripts/video-team-project-thread-routing-20260523.md, raw/transcripts/video-team-anime-song-mode-routing-20260523.md, raw/transcripts/video-team-suno-list-download-rule-20260523.md]

## Compilation policy

Daily llm-wiki compile job은 video/MV 세션에서 다음만 seed로 승격한다.

- 재사용 가능한 제작 패턴
- 명확한 실패모드와 예방책
- 공모전/관광/브랜드/CapCut/I2V 같은 반복 도메인의 의사결정
- 사용자가 명시적으로 만족/불만을 표현한 품질 기준
- 역할별 handoff 또는 QC 기준으로 일반화 가능한 내용

다음은 seed로 승격하지 않는다.

- 일회성 파일 경로만 있는 완료 로그
- 곧 낡을 PR/이슈/메시지 ID
- 아직 검증되지 않은 계획
- 특정 웹 세션의 임시 로그인/권한 상태
- 사용자의 개인정보 또는 제출 양식 세부 개인정보

## Seed to production flow

1. Read `SCHEMA.md`, `index.md`, `_mocs/video-production.md`, and this page.
2. Search `seeds/` for a matching archetype.
3. Use `~/.local/bin/video-codex-runtime` to create the project and `video-codex-runtime kanban-plan --project <project>` to create the fixed rail.
4. Map work only to fixed lanes: `director`, `music`, `visual`, `qc`, `editor`; do not invent subagents/profiles.
5. Lock actual audio before final cut/block design when music-driven.
6. Planner writes Cut Map/Block Map, including `reference_count_required` per Seedance multi-reference block.
7. Run block-level image/QC/Seedance/QC in parallel where gates are satisfied; defer dirty/failed attach blocks without stopping clean blocks.
8. Editor builds an editable CapCut draft when typography/transitions matter.
9. QC performs PASS/FAIL using actual artifacts, not prompts or JSON alone.
10. Public upload/submission/email/form/payment/password/2FA/irreversible deletion remain explicit user-approval gates.


## Active seed pages

- [[video-project-seed-template]] — generic starter for video/MV/contest work.
- [[tourism-mv-seed]] — tourism/regional/culture MV and public contest starter.
- [[video-typography-contract-template]] — turns typography wiki rules into a project execution contract.
- [[zhemnixhwangsa_bangi_food_alley_seed]] — Bangi Food Alley/DDP AI film festival starter.

## Related pages

- [[video-typography-operating-manual]]
- [[video-typography-dataset]]
- [[hermes-agent]]
- [[hermes-usage-patterns]]
- [[_meta/hermes-dataset-pipeline]]


## Fixed command-surface communication

영상 운영에서 Hermes-main/일반 relay가 후보 제안·파일 업로드·진행 보고를 대신 올리는 것은 정상 경로가 아니다. 현재 기준에서 `#헤르메스-메인`은 command/router이고, 영상 명령 표면은 `#영상팀/영상워크플로-관제`다. 후보/파일/진행 보고는 fixed lane 산출물과 queue/card evidence로 남겨야 하며, Hermes-main은 긴급 수동 보정이나 명시적 디버깅 때만 개입한다.^[raw/transcripts/video-team-no-hermes-main-in-project-threads-20260523.md, raw/transcripts/video-workflow-lockdown-fixed-rail-20260525.md]


## Music selection auto-transition

Music 후보를 리뷰한 뒤 사용자가 `1번/2번/3번`, `TOP1/TOP2/TOP3`, `이걸로`, 후보 제목 등으로 명확히 선택하면 추가 확인 없이 해당 파일을 Music Lock으로 승격하고 Planner로 자동 전환한다. `music_lock.md`, lane status, manifest/state에 ffprobe/sha256/선택 정보를 기록하고 fixed Kanban/runtime queue에 다음 owner를 반영한다. 선택 후 `NOT_LOCKED`로 멈추는 것은 워크플로 실패다.^[raw/transcripts/video-team-music-selection-auto-transition-20260523.md, raw/transcripts/video-workflow-lockdown-fixed-rail-20260525.md]


## Planner visible report after Music Lock

Director fan-in 요약은 lane evidence를 대체하지 않는다. Planner는 Music Lock 전에는 cut/block planning을 확정하지 않고, Music Lock 이후 cut_map/cue_map/block_map을 완성하면 fixed Kanban/runtime에 Music Lock 기준, planning revision, cut count, block count, `reference_count_required`, 주요 output path, next owner를 남긴다. 내부 로그/PID를 외부 보고로 노출하지 않는다.^[raw/transcripts/video-team-planner-visible-report-20260523.md, raw/transcripts/video-workflow-lockdown-fixed-rail-20260525.md]


## Fixed Kanban handoff, not Gojo-centralized or ad-hoc role mentions

영상팀은 고죠(Director)가 모든 정상 전환을 role mention으로 직접 깨우는 구조도, Hermes-main이 숨은 subagent를 임의 생성하는 구조도 아니다. 현재 handoff 표면은 fixed Kanban cards + runtime manifest/queues다. 고죠/Director는 intake, safety gate, retry routing, 예외 fan-in을 맡고, 정상 전환은 fixed lane status와 queue event로 증명한다. `이어가/계속/진행해` 같은 generic continuation은 현재 owner lane의 다음 fixed card/queue state를 진행하는 신호로 해석하며, 새 profile이나 `delegate_task`를 만들 근거가 아니다.^[raw/transcripts/video-workflow-lockdown-fixed-rail-20260525.md]


## Strict image/video lane separation and downstream gates

스쿠나(image)는 `image_reference_queue`/`image_retry_queue`만 소비해 reference image를 만들고 Image QC로 넘긴다. 스쿠나가 Runway/Seedance/영상 생성/편집/패키징을 하면 안 된다. 토우지(Seedance/video)는 Image QC가 특정 block의 required references를 `APPROVED_FOR_I2V`로 채워 `SEEDANCE_BLOCK_READY` handoff를 만든 뒤에만 시작한다. Planner 완료, parallel phase open, 또는 사용자의 generic `이어가/계속`만으로 Seedance·Editor·Package가 발동하면 실패다. Runtime dispatch는 upstream gate 미충족 시 seedance/editor/package를 hard-skip해야 한다.^[raw/transcripts/video-team-role-separation-no-premature-seedance-20260523.md]

## Image QC style and motion-continuity gate

Image QC는 “예쁜 한 장”이 아니라 Planner의 작풍·Block Map의 reference order·Seedance motion beat를 동시에 검수해야 한다. 수묵화/한지/먹선으로 계획된 과거·기억 파트가 일반 실사 재연처럼 보이면 FAIL이고, 현재·야구·컬러 회복 같은 실사/컬러 파트는 Block Map이 지정한 구간에서만 허용한다. QC PASS에는 최소한 `style_lock_match`, `reference_index_role_match`, `block_motion_order_support`, `forbidden_object_overlap_absent`, `no_realism_drift_for_sumi_e_blocks` 증거가 필요하다.

특히 사물 전환/던지기/투사체 sequence는 이미지 한 장 안에 서로 다른 시간 상태를 합쳐 넣으면 안 된다. 윤봉길 도시락 폭탄→야구공 전환 같은 block은 `던지기 전 자세 → 던진 후 자세 → 던져지는 중의 도시락/사물 클로즈업 → 야구공으로 자연 변환`이 별도 reference와 motion handle로 읽혀야 한다. 도시락과 야구공이 같은 비전환 still에 함께 있거나, pre-throw/release/trajectory/aftermath가 한 장에 합쳐지면 Image QC FAIL이며 Seedance handoff 금지다. 이미 downstream으로 넘어간 출력이라도 이 기준을 위반하면 process-invalid로 격리하고 이미지 작업부터 재시작한다.


## Discord image review and visible video handoff gate

스쿠나(image)가 백그라운드에서 reference image를 만들더라도 사용자는 Discord에서 진행 이미지를 확인할 수 있어야 한다. 캐릭터 preflight, block별 refs, 4–16장 단위 등 의미 있는 묶음이 생기면 스쿠나(image)가 contact sheet 또는 대표 이미지를 native attachment로 올리고 generated/pass/retry 상태와 Seedance gate 상태를 짧게 붙인다. 고죠/Hermes-main이 대신 올리는 정상 경로가 아니다.

Seedance는 이미지 파일이 존재하거나 Planner가 끝났다는 이유만으로 시작하지 않는다. 특정 block의 Image QC readiness, Block Map `reference_count_required` 충족, fixed rail의 Seedance-ready card/queue event가 필요하다. gate 증거는 `SEEDANCE_BLOCK_READY`, approved reference bundle, and runtime/Kanban lane status다. gate 전 생성된 Seedance 출력은 사용자가 명시 재사용 승인하기 전까지 process-invalid/quarantine이다.^[raw/transcripts/video-team-discord-image-review-and-visible-video-handoff-20260523.md, raw/transcripts/video-workflow-lockdown-fixed-rail-20260525.md]


## Character sheet prompt standard

캐릭터 시트는 cinematic MV scene frame이 아니라 production model sheet/design-lock reference다. 웹검색 기준으로 model sheet는 애니메이션/만화/게임에서 캐릭터의 appearance, poses, gestures를 표준화해 여러 작업자와 여러 장면 사이의 continuity를 유지하고 off-model drift를 막는 문서다. 따라서 영상팀의 `CHAR_*`/`CHAR_PREP` 프롬프트는 neutral/off-white studio background, flat/even lighting, same single character repeated, consistent proportions/outfit/palette/accessories, aligned views/details, no readable labels/text를 요구해야 한다. rainy-night/cinematic motif는 palette/prop에만 반영하고 배경/조명으로 쓰지 않는다. 이 기준을 못 맞춘 기존 캐릭터 시트는 QC FAIL/RETRY이며 downstream Seedance reference의 identity lock으로 쓰지 않는다.^[raw/transcripts/video-team-character-sheet-standard-upgrade-20260523.md]


## Sukuna image-only reference bundle handoff

료멘 스쿠나(image)는 이미지 전용 worker다. 스쿠나는 `image_reference_queue`/`image_retry_queue`를 소비해 하나의 block/reference bundle에 해당하는 이미지들을 만들고, Image QC 통과 후 Discord에 contact sheet/대표 이미지와 reference order/paths를 브리핑한 뒤 `SUKUNA_REFERENCE_BUNDLE_HANDOFF_TO_TOJI`로 후시구로 토우지(video)에게 넘긴다. 스쿠나는 Seedance/Runway/영상화 작업을 조작하거나 진행한다고 말하지 않는다. Image QC는 직접 Seedance queue를 여는 대신 reference-bundle readiness를 만들고, runtime은 Sukuna bundle handoff + Toji visible handoff 없이는 Seedance를 hard-skip한다. 사용자가 추가로 막지 않으면 이미지 생성/QC/스쿠나 브리핑/handoff는 계속 진행된다.^[raw/transcripts/video-team-sukuna-image-only-reference-bundle-handoff-20260523.md]


## Toji immediate Seedance and reference attach recovery

토우지(video)는 스쿠나(image)에게 complete approved reference bundle 하나를 받는 즉시 해당 block의 Seedance를 시작한다. Seedance 큐/렌더 시간이 길기 때문에, 그 사이 image generation과 Image QC는 다른 block에 대해 계속 병렬 진행한다. Runway→Seedance에서 프롬프트 입력은 성공하지만 reference button/image add가 실패하는 경우, 과거 성공 사례처럼 clean staged single-file path를 사용하고 active top Multi-reference strip의 reference slot에서 한 장씩 upload/select한다. 각 장마다 `IMG_1`, `IMG_2`…가 active strip에 붙었는지 확인해야 하며, file picker selection/blue `업로드`/asset library visibility만으로는 부족하다. stale `image2/IMG_2`가 제거되지 않으면 Generate 금지.^[raw/transcripts/video-team-toji-immediate-seedance-reference-attach-recovery-20260523.md]

If Seedance lane status/result reports a route-level blocker such as `global_reference_upload_permission`, ready queue entries do not override the block. Director/fan-in cron should not repeatedly re-dispatch Seedance, Seedance QC, editor, or package while only a subset of blocks has QC PASS. The correct state is `BLOCKED` with a user-action requirement: enable Computer Use/Finder visible drag-drop or manually attach current-project staged PNG references to the Runway Seedance Multi-reference strip in exact `IMG_1`, `IMG_2`, … order. Once the permission/manual attach issue is fixed, re-run runtime status and continue from remaining `SEEDANCE_BLOCK_READY` events; do not fabricate progress from queue counts alone.^[raw/transcripts/hermes-session-capture-20260525-200049.md]

## Toji Seedance compact queue-fill policy

Seedance/Runway queue time is long, so 토우지(video)는 one-job-wait 방식으로 일하지 않는다. 스쿠나(image)가 승인된 reference bundle을 넘기면 해당 block을 즉시 제출하고, Runway card가 queued/generating으로 확인되면 `SEEDANCE_JOB_SUBMITTED_IN_QUEUE`를 기록한 뒤 active block lock을 submitted 상태로 전환/해제한다. 이후 최소 3개 Seedance jobs가 in-flight 상태가 될 때까지 다음 eligible bundle을 계속 제출한다. 실제 MP4 다운로드/검증 전에는 DONE 또는 Seedance QC handoff를 하지 않는다.^[raw/transcripts/video-team-toji-seedance-three-inflight-queue-policy-20260523.md]

## Seedance prompt knowledge retrieval and non-stopping queue-fill

토우지(video)는 특정 bundle의 reference attach/order/old asset contamination 실패를 lane 전체 BLOCKED로 만들지 않는다. Runway route/account가 살아 있으면 해당 block만 `DEFERRED_ATTACH_BLOCKED`로 `deferred_blocks.json`에 미루고, 다음 eligible Sukuna bundle로 이동해 최소 3개 in-flight Seedance jobs를 채운다. 전역 blocker(login/CAPTCHA/payment/account limit/provider route lost/permission prompt)만 lane 전체를 멈춘다.

Seedance prompt는 매번 처음부터 감으로 쓰지 않고 [[seedance-prompting-knowledge]]를 검색/적용한다. Planner/Toji는 block type(캐릭터 close-up, kinetic run, memory interior, object motif, abstract transition, final hold)에 맞는 reference-role, shot-count, camera/motion budget, identity/crop preservation, avoid rules를 `lanes/seedance/prompts/<BLOCK>_prompt_rules_used.md`에 남긴 뒤 prompt에 반영한다.^[raw/articles/seedance-prompting-20260523/synclip-seedance-guide.md, raw/articles/seedance-prompting-20260523/higgsfield-seedance-guide.md, raw/articles/seedance-prompting-20260523/youtube-elevenlabs-multishot.md, raw/articles/seedance-prompting-20260523/youtube-dan-kieft-course.md, raw/transcripts/video-team-toji-seedance-three-inflight-queue-policy-20260523.md]

## Hermes no-CUA production boundary and Seedance dynamic/project isolation

For #영상팀 video production, Hermes is only the control-plane. Hermes CUA must not capture/click/probe/move a visible pointer in production GUIs; GUI work belongs to Codex Computer Use lanes only. This is now a hard safety boundary, not an optimization preference.^[raw/transcripts/video-team-hermes-cua-ban-seedance-dynamic-project-isolation-20260523.md]

Seedance/Toji also needs project isolation and dynamic-prompt enforcement. A Runway asset/card is valid only if it is tied to the current project root and current block reference IDs. Old smoke-test outputs, old 10-second B02 clips, generic Recent Generation cards, and stale `image2/IMG_2` thumbnails are contamination. The correct response is to defer that block and continue queue-fill, not to generate with mixed assets.^[raw/transcripts/video-team-hermes-cua-ban-seedance-dynamic-project-isolation-20260523.md]

Seedance prompts should exploit Seedance's motion strengths. Static image-hold prompts are insufficient. Each block prompt must include a motion mode, camera verbs, subject/action verbs, music-aware motion budget, and dynamic atmospheric/VFX cue while preserving identity/crop/reference order. See [[seedance-prompting-knowledge]].^[raw/transcripts/video-team-hermes-cua-ban-seedance-dynamic-project-isolation-20260523.md]
## Seedance feature method selection

Before Toji writes a Seedance prompt, the lane should choose a method from [[seedance-feature-playbook]] rather than treating every block as static image-to-video. Use first/last-frame control for defined visual destinations, storyboard/콘티 grids for multi-beat sequences, camera-control prompting for dynamic motion, extension/continuation for good clips that need to continue, and repair/replace for localized defects. The selected method should be visible in `prompt_rules_used` so QC can judge whether the right Seedance feature was used.

## Image QC style-lock and motion-state continuity — 2026-05-26

Image QC must not approve references only because files exist, aspect ratio is correct, anatomy is passable, and no text/logo appears. For planned sumi-e/ink-wash/hanji/monochrome memorial sections, photorealistic/live-action drift is a blocking style failure unless the Block Map explicitly says present-day color returns. For action/transformation blocks, each reference must isolate one temporal state; merged-state/collage images such as a lunchbox bomb and baseball appearing together before the intended morph fail block continuity. See [[video-image-qc-style-continuity]].^[raw/transcripts/video-team-image-qc-style-continuity-correction-20260526.md]
