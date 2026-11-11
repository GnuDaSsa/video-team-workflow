# 영상팀 런타임 규칙 — v5 단일 원본

## 0. 권위와 범위

| 순위 | 문서 | 소유 범위 |
|---|---|---|
| 1 | 이 파일 | 레일, lane 순서, 실행 예산, 미디어 구조, 게이트, 안전 |
| 2 | `~/.codex/skills/seedance-prompt-en/` (2.0/기본) 또는 `seedance25-prompt-en/` (사용자가 2.5 명시) | 선택된 한 버전의 Seedance 프롬프트 규격·Runway UI |
| 3 | `~/.codex/video-team-policies/` | 스폰 승인, 브라우저 오퍼레이터 정책 |
| 4 | `videodirector` | 이야기·연출·품질 기준 |

- 같은 규칙을 여러 문서에 복제하지 않는다. 본문은 소유 문서 한 곳에만 두고 나머지는 포인터다. 프로젝트 안에 규칙 사본을 만들지 않고, 예외는 `docs/project_overrides.md`에 조항 번호와 함께 적는다.
- 새로 init한 프로젝트에만 적용한다. 기존 프로젝트는 이관 요청 전까지 옮기지 않는다(`preprod/`가 없으면 legacy v4 흐름).
- No-I2V는 별도 팀이 아니라 같은 레일의 생성 모드다.
- Editor/CapCut lane은 퇴역했다. 레일은 승인 클립 납품까지다.
- 명령 목록은 `video-codex-runtime --help`와 `<cmd> --help`가 원본이다.

## 1. 실행 모델

레일: `director → music → planner → image_creator_01 → image_creator_02 → image_qc → seedance → seedance_qc → package`

1. **디렉터 = 메인 스레드**(Claude Code 또는 Codex 대화). 사용자 대화·승인·진행 판단만 하고 레인 작업·로그·프롬프트·미디어를 직접 열지 않는다.
2. 다음 레인은 `video-codex-runtime next --project <p>`의 `default_execution`을 따른다: `DISPATCH_LANE_SESSION`은 `commands[0]`(`dispatch` 후 `wait`)을 실행하고 `lanes/<lane>/session_result.json`만 읽는다. `ASK_USER`는 `show` 파일을 보여 주고 한 번 묻고 답을 `commands`로 기록한다. `LOCK_STAGE`는 그 명령으로 잠근다. `DIRECTOR_IN_MAIN_THREAD`는 P0/P1을 이 대화에서 진행한다.
3. 각 레인은 새 Codex 세션에서 돈다. 상시 승인은 `session_policy.json`(runtime 루트)이다(레인 세션만 해당, 승인 게이트는 풀지 않음). 세션 안에서 다른 세션·agent·scheduler·watcher를 만들지 않는다. 백그라운드 daemon·cron·heartbeat·두 번째 브라우저 루프 금지. 상시 승인이 없으면 `--approved-spawn <lane>:<phase>`가 정확히 일치할 때만 실행된다.
4. **동시 실행(머신 전체):** 브라우저 레인 1 + 로컬 레인 1. 브라우저 레인 = seedance production, music, flow, image_creator production. 로컬 레인 = planner, image_qc, seedance prompting, seedance_qc, package 등. 같은 프로젝트의 같은 레인은 하나. `--parallel-browserless`는 비활성이다. 이미지 생성 worker는 활성 Image Creator가 고정한 프롬프트를 1~3개 파일 생성 프로세스로 나눌 뿐이며(수정 금지, 4개 이상 `IMAGE_WORKER_CAP_EXCEEDED`) agent가 아니다.
5. 결과가 `NEEDS_USER`면 그 질문을 사용자에게 하고 승인 인용을 기록한 뒤 같은 레인을 다시 dispatch한다. `session_result.json`의 `reason_code`: SUBMITTED, HARVESTED, SLOT_BUSY, IN_QUEUE, ACCOUNT_WARNING, PROMPT_CLEAR_FAILED, ASIDE_UNAVAILABLE, UI_STALE, ATTACH_FAILED, NEEDS_USER, OTHER.
6. `wait`는 죽은 세션을 STOPPED/DEAD_NO_RESULT로 전이시키고 pid 재사용을 감지한다. 장부(`state.json`) 손상은 `LEDGER_CORRUPT`로 중단한다.
7. 프로바이더 기본값은 Seedance다. Flow는 사용자가 명시할 때만, Grok I2V는 해당 프로젝트에서 명시할 때만이며 병렬 금지다.
8. 사용자 요청마다 새 스킬이나 AGENTS 문서를 만들거나 늘리지 않는다. 규칙 변경은 기존 위치를 고친다(최신본만, 이력은 git).
9. 프로젝트 폴더는 SSD `/Volumes/gnudas-ssd/video-team/projects/`, 편집물은 SSD `edits/<slug>/`(프로젝트 `media/` 밖), 규칙·`session_policy.json`은 로컬 runtime 루트다. `PROJECTS_SSD_NOT_MOUNTED`면 SSD 연결을 요청하고 로컬에 만들지 않는다.

### 1.0s 새 프로젝트 시작 (매번 이 순서)

1. 새 영상 요청 = 새 대화 하나 = 그 프로젝트의 디렉터. 다른 프로젝트 대화에서 이어 시작하지 않는다.
2. `video-codex-runtime init --slug <영문-slug> --brief "<요청 원문>" [--mode ...] [--author claude|codex]`. 작성 모드를 말하지 않았으면 첫 질문은 “작성 모드: Claude 프롬프팅 / Codex” 하나뿐이다.
3. P0·P1은 디렉터가 이 대화에서 한다(`runtime/templates/director.md`): 컨셉 3안 → 사용자 선택 → 잠금, 스타일 바이블 → 잠금.
4. 이후 `next`의 `default_execution`을 반복한다.

### 1.1 사용자 확인 지점 (정확히 이것뿐)

작성 모드(미지정 시), P0 컨셉 선택, P2 콘티 승인(이미지 가이드 요약 포함), P4 선반 릴리스 1회, 그리고 세션이 돌려준 `NEEDS_USER`. 그 외 단계 전환·다음 컷마다 “진행할까요?”를 묻지 않는다. Suno 음악은 생성까지만 하고 다운로드·평가·선정은 하지 않는다(`music-director/SKILL.md`). 결제·로그인·공개 게시·외부 제출·개인정보·비가역 삭제 gate는 이 승인으로 풀리지 않는다.

### 1.2 입력 증거

음악 잠금·Planner 입력·블록맵 증거는 코드 게이트가 강제하며 `--force`로 우회할 수 없다. 사용자가 해당 프로젝트에서 음악 없이 이미지·영상 먼저를 명시했을 때만 `visual_only_no_audio` 예외(`docs/visual_only_authorization.md`)로 Planner에 진입하고 패키지는 `VISUAL_ASSETS_ONLY_NO_MUSIC`으로 표시한다. 무음 WAV·`LOCKED` 위조 금지. Suno 생성 직후는 `PENDING_USER_AUDIO`로 멈춘다.

### 1.3 생성 모드

- 기본 `no_i2v_reference_native`: 컷별 스타일프레임/시작프레임/키프레임을 만들거나 올리지 않는다. 재사용 identity/environment 참조만 최소로 쓰고(충분하면 신규 이미지 0개) 컷 구도·동작·시간 진행은 Seedance 프롬프트가 담당한다.
- `standard_i2v`는 사용자가 명시 요청할 때만: 컷마다 source/styleframe을 만들고 QC해 입력으로 쓴다.
- 진행 중 `No-I2V` 호출은 미제출 블록만 전환한다. 제출된 job·media는 보존한다.

### 1.4 생성 길이

길이는 Planner/프로젝트가 소유한다. 2.0은 5–15초, 2.5는 5–30초이고 **기본 lock은 15초**다. 프롬프트 복잡도·UI 값으로 추론하거나 줄이지 않는다. 15초 미만은 `lock-duration --source user:<evidence>|brief:<artifact>`로만 낮출 수 있다(`planner_revision:` 단독 불가). 모든 pack은 `duration_sec`을 선언하고 `prompt_packet_utils.py attest --project <p>`가 lock과 일치해야 한다. 잠금이 바뀌면 attestation이 무효이며 미제출 pack은 `HOLD_DURATION_LOCK_MISMATCH`로 두고 재저작한다. 한 장면이 좋으면 `SINGLE_CONTINUOUS_SHOT`, 인과가 맞을 때만 연속 컷 2–4개를 `PLANNED_MULTI_SHOT_SOURCE`로 묶는다.

### 1.5 모델과 Astra

창작 저작은 `gpt-6-astra`/`xhigh`를 선호하고 실행 레인은 모델을 지정하지 않는다(Astra가 아닌 결과를 Astra로 표시 금지). 승인형 Astra child와 `author_handoff.py`는 사용자가 spawn을 명시 승인한 경우의 호환 경로이며 `claude` 저작 모드가 대체한다. 일반 “영상팀 실행”은 spawn 승인이 아니다.

### 1.6 Flow

- 사용자가 FLOW/Flow/플로우 영상 생성을 요청하면 `flow_malfoy_composite` 분기를 선택하고 `~/.codex/skills/videodirector/references/flow-malfoy-composite.md`와 `runtime/templates/flow.md`를 따른다. 추가 “말포이식” 호출이나 일반/합성형 선택 질문은 필요 없다.
- 이 분기는 지침 기반 기획·저작 라우팅이다. `next`/`dispatch`/attest/Runway helper는 Seedance 전용이며 Flow 실행
  어댑터가 아니다. Flow를 Seedance로 허위 기록하거나 게이트 통과를 가장하지 않는다. 활성 Seedance 작업을 자동 전환하지 않고 기존 HOLD를 보존한다.

## 2. 프리프로덕션과 프롬프트 소유권

### 2.1 단계표 (`preprod/PREPROD_V1`, `video-codex-runtime preprod <cmd>`)

| 단계 | lane | 파일 | 잠금 |
|---|---|---|---|
| P0 컨셉 | director | `preprod/00_concept/` 3안 → `concept_lock.json` | 사용자 선택 인용 |
| P1 이미지 가이드 | director | `preprod/01_bible/style_bible.json` | lane 검증 |
| P2 콘티 | planner | `preprod/02_storyboard/storyboard.json` (숏마다 `copy_line` 근거 대사, 인서트는 "(insert)") | 사용자 승인 인용 |
| P3 이미지 | image_creator · image_qc | `preprod/03_image_prompts/<REF>.prompt.txt`, `image_plan.json` | 모든 ref 승인 등록 |
| P4 영상 프롬프트 | seedance(prompting) | `preprod/04_shelf/<BLOCK>/` | `shelf-lock` + 사용자 `shelf-release` 1회 |
| P5 제작 | seedance(production) | 선반만 소비 | `shelf-verify` 통과 |

- 모든 창작 결정은 `preprod/` 밖에 만들지 않는다. 개정은 같은 파일을 고쳐 재잠금하며 이전본은 `_superseded/`로 간다. 상류가 잠금 뒤 바뀌면 그 단계와 하류가 `STALE`이 되어 gate가 닫힌다. 제작 중 수정 요청은 소유 단계로 돌아가 재잠금·재릴리스한다. 제작 단계에서 프롬프트를 쓰거나 고치거나 줄이지 않는다.
- P2 잠금이 `multi_reference_block_map.json`, `video_attributes.json`을 생성한다. 손으로 쓰지 않는다.
- **shelf 잠금**은 블록이 실제로 쓰는 입력(해당 storyboard 블록, generation, 바이블 style/identity/forbidden, 콘셉트 화면비)에 묶인다. 다른 블록만 바뀐 storyboard 재잠금은 이 블록의 shelf를 무효화하지 않는다.

### 2.2 저작 모드 (프로젝트 시작 때 한 번)

- `claude`: Claude Code가 `video-codex-runtime author run --stage concept-options|concept-lock|bible|storyboard|image-prompts|shelf [--block B] [--feedback "<사용자 원문>"]`로 P0–P4 파일을 쓴다. Codex는 창작 파일을 직접 쓰지 않고 질문·승인·잠금·생성·QC·registry를 맡는다. 잠금은 파일이 Claude 출력과 바이트 단위로 같을 때만 통과한다.
- `codex`: 현재 Codex 세션이 직접 쓴다.
- 기록은 `author set-mode --project <p> --mode claude|codex --approval-quote "<답>"`(또는 `init --author`). 모드가 없으면 P0 잠금이 거부된다. 전환은 사용자가 요청할 때만이며 기존 잠금은 유지된다.
- **`author run`은 메인에서만** 돈다. 레인 세션 안에서는 `AUTHOR_RUN_IN_LANE`으로 거부되므로 레인은 `PARTIAL`로 피드백을 돌려준다. Claude 호출은 해당 단계 파일만 쓸 수 있다(`CLAUDE_WROTE_OUTSIDE_STAGE`).

### 2.3 이미지

Image Creator가 `image-prompt` 스킬 구조로 **영어** 프롬프트를 쓴다. 한 reference = 한 프롬프트 = 한 이미지(grid/contact sheet 금지). 반복 인물은 승인된 모델시트를 먼저 만들어 참조로 붙인다(`runtime/references/character_sheet_prompt_standard.md`). 참조 누락을 무참조 생성이나 API로 바꾸지 않는다. 장소 참조에는 소품·종이 여백을 넣지 않는다.

### 2.4 Seedance 프롬프트

- 모델 입력은 **영어만**. `preprod shelf-check`가 기계 검사한다(영어·NFC, Runway 입력 10000자 이하, 첫 줄 `N seconds, ...`, `Shot k (a-bs):`, 숏별 shot size·angle·camera move·must-include, STYLE·IDENTITY 원문, `@ImageN`이 refs와 일치). 이어서 `prompt_packet_utils.attest` 통과 시 잠긴다. 규격 본문은 선택된 버전 스킬이 소유한다. 한 블록에서 두 버전을 함께 읽지 않는다.
- `prompt_lint`가 사용자 거절 패턴(매끈 피부, 글자 생기는 소품, 화면 내용 묘사, 콧줄 문구, 외국 사무실, START_FRAME, 요청 없는 화면 글자, 장소 참조 소품·종이 여백, 과한 액션, 억지 메타포)을 `shelf-check`/`check`와 Claude 저작 프롬프트에서 경고한다. 의도된 예외는 블록 `lint_allow`로만 둔다. 장면은 `copy_line` 대사를 그대로 따른다.
- 선반 작성 전 `knowledge-select`가 속성 기반으로 위키 발췌를 고른다(전체 위키 읽기 금지, 상세는 `--help`).

### 2.5 P5 제작 — `produce`

- **표준 경로:** `video-codex-runtime produce --project <p> [--credits]`. 포그라운드 루프가 released 블록을 제출하고 수확한다. 디렉터는 이를 **백그라운드로 실행하고 종료코드만** 받는다: 0 완료/미릴리스, 2 NEEDS_USER·불명확한 경고 문구(화면 확인), 3 PROVIDER_HOLD, 4 연속 실패·세션 타임아웃·세션 유실(보드에서 제출 여부 확인 후 재개), 5 디스패치 거부(게이트 포함), 6 세션 상한(기본 30).
- 한 세션이 맡는 블록 수는 produce가 슬롯 수로 정한다. 수확과 다음 블록 제출은 같은 세션에서 한다. 슬롯이 찬 동안에는 세션을 띄우지 않고, 클릭 후 첫 확인은 2.5 Unlimited 65분 / 2.0 70분 / 크레딧 6분, 이후 20분(크레딧 5분) 간격이다. 프로젝트별 `drive_seedance.sh`는 퇴역했다.
- 제작 세션은 `production-card.md`만 읽고 블록마다 `runway_ui_helper.py run-block` 한 번 + Generate 한 번이다. `paste-prompt`는 릴리스·잠금된 선반만 받는다. 제작 중 이 문서·스킬 본문·헬퍼 소스를 다시 읽지 않는다. 큐 판정·재확인·다운로드·복구·exactly-once 제출은 선택된 버전 production 문서와 `aside-operator.md`가 소유한다. 새 Runway 참조는 먼저 올린 뒤 선택하며 이미 올린 바이트는 다시 올리지 않는다(Uploads에서 선택).
- 로그인·CAPTCHA·결제·권한·계정 제한은 자동 대기로 풀지 않는다. 정확한 사용자 행동을 적고 BLOCKED한다.
- **머신 HOLD:** Runway 자동화/autoclicker/정지 경고가 보이면 헬퍼가 `/Users/gnudas/Documents/Codex/video-team-runtime/PROVIDER_HOLD.json`을 기록하고 모든 브라우저 레인 dispatch를 거부한다. 해제는 사용자가 화면에서 처리한 뒤 `video-codex-runtime hold --clear --approval-quote "<사용자 원문>"`만 가능하다. 경고 우회·탐지 회피 금지.

## 3. 미디어 (요약)

- 실제 미디어는 프로젝트 `media/` 아래에만 둔다(`01_sources … 07_videos_approved … 09_final … 90_work … 99_archive`). `lanes/<lane>/`에는 메타데이터만 둔다.
- `asset_registry.sqlite`가 `asset_id`·hash·경로·provenance를 관리한다. 생성 직후 후보로 등록하고 QC PASS/WARN_PASS 뒤에만 `promote`한다.
- 이 규칙을 어긴 상태(`media/` 밖 미디어, 미등록, hash 불일치, 승인 자산이 후보에 잔존, 하류 입력 누락)는 consuming lane(image_qc, seedance, seedance_qc, package)을 `MEDIA_HARD_GATE`로 막으며 `--force`로 우회할 수 없다. `python3 runtime/scripts/media_registry.py audit --project <p>`가 통과해야 한다.
- 중간 파일(staging 복사, 실패·미선택 후보, 중복)은 registry로 확인된 경우에만 `90_work`로 옮기고 24시간 뒤 휴지통으로 보낸다. 원본·승인 자산·잠긴 음악·패키지·`preprod/` 잠금·QC 기록은 자동 정리하지 않는다. 영구 삭제 금지, 별도 정리 daemon 금지(허용된 dispatch가 동기적으로 처리).

## 4. 제작·QC 게이트

- 음악 우선: 구조·박·프레이즈를 분석한 뒤 컷 타이밍을 잠근다. 반복 인물은 모델시트가 승인·등록·첨부되기 전 production frame을 만들지 않는다.
- 원본 still·스틸 줌 대체 컷은 납품하지 않는다. 승인된 생성 클립만 쓴다.
- QC는 해부학, 손·물체, 인물 소실, 정체성, 시선, 옷 글자, crop drift, 반복 샷, jitter, freeze, 1-frame flash, 자막 겹침을 확인한다. 실패 클립은 재생성·교체한다(편집으로 숨기지 않음).
- 실제 파일 경로·크기와, 영상/음악이면 duration·codec을 확인하기 전 완료로 표시하지 않는다. 상태·프롬프트·계획만으로 완료를 주장하지 않는다.
- Package는 `seedance_qc` PASS 뒤 승인 클립을 이야기 순서대로 `media/09_final_최종본/<project>_package/`에 모으고(`clip_order.csv/json` 포함) registry에 `--kind package`로 등록한다. 자르기·리타이밍·master 조립은 하지 않는다.

## 5. 안전과 스폰 제한

- 공개 upload/publish, 공모전·정부 form 제출, email send, 개인정보 form submit, payment, password/2FA, 영구 삭제는 명시적 사용자 승인이 필요하다.
- 별도 agent/lane/subagent/browser loop를 만들려면 현재 대화에서 역할·목적·산출물을 명시해 승인받아야 한다(레인 세션 상시 승인 제외).
- 자동 복구 가능한 문제는 소유 문서의 복구 사다리를 끝까지 수행하고, 사람·외부 상태가 필요한 문제만 정확한 사용자 행동과 함께 BLOCKED한다.
- 사용자가 "지침 반영/워크플로우 개선"을 요청하면 프로젝트 한정 예외가 아닌 한 `video-team-workflow` 원본을 수정·검증·배포한다(`docs/video-feedback-promotion-protocol.md`).

<!-- codex-harness-kit:bridge:start -->
## Codex Harness Activation

This repository uses `codex-harness-kit`.

Keep the existing instructions in this file, and additionally treat `AGENTS.harness.md` as active instructions.

Before making code changes:

1. Read `docs/harness-config.json` first.
2. Use the file paths from the config `paths` object instead of assuming fixed `docs/...` paths.
3. Follow the harness workflow in `AGENTS.harness.md` together with the rest of this file.
<!-- codex-harness-kit:bridge:end -->
