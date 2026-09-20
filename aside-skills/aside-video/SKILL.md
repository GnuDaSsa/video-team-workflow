---
name: "aside-video"
description: "Aside 전용 영상팀 하네스. 영상팀, Jev/제브 작업 분배·Seedance 입력 속도 개선, 어사이드 최적화, Astra/아스트라 프롬프팅 전담, Luna/루나 강제 해제, 웹 ChatGPT Images 2.5, 노래·이미지·Seedance 제작, MV, No-I2V/noi2v에 사용한다. 아스트라는 세 종류의 프롬프팅만 담당하고 기획·실행·컴퓨터유즈·QC는 현재 세션 모델을 유지한다. 신규 Aside 제작은 기존 video-team 호환 스킬보다 우선한다."
---

# Aside Video

현재 Aside 세션이 제작 전체를 실행하고, **노래·이미지·Seedance 프롬프팅만 Astra**에 맡긴다. **Jev는 입력 준비의 다음 단계 분배**, 현재 세션은 짧게 묶은 브라우저 실행을 담당한다. Luna로 시작해도 실행자는 Luna 그대로이며 저작만 Astra에 넘긴다. **기존 대화의 후속 이미지/수정 요청도 매 턴** 이 스킬과 `references/author-executor.md`를 읽고 `node scripts/harness.mjs status`를 확인한다. Astra는 실제 `gpt-6-astra` 저작 모델이지 자산 이름·이미지 backend·고정 합성 기법이 아니다. 역할 전환을 사용자에게 실제 진행 메시지로 표시한다.

**매 신규 제작과 후속 수정에 영어 기본 언어 계약을 적용한다.** `harness request`가 만드는 language_contract를 Astra에 그대로 전달하고, `seal → submission prepare/verify`에서 현재 언어 계약까지 통과한 payload만 입력한다. 언어 없는 과거 인수증의 읽기 검증은 신규 영어 입력 승인이 아니다. 상세 규칙은 `references/prompt-language.md`를 따른다.

**이미지 생성/편집에도 영상과 별개로 필수 저작 게이트가 있다.** 현재 모델이 Astra가 아니면 prompt를 쓰기 전에 실제 Astra author child를 호출한다. `route`/`request` 출력은 호출 완료가 아니다. 모든 provider 입력은 `request → 실제 Astra 저작 → seal → submission.mjs prepare → verify`를 통과한 payload 원문만 사용한다. Luna 등 실행자가 `repl` 안에서 새 문자열을 만들고 바로 `imagegen.generate`/웹 composer에 보내는 패턴을 금지한다. provider UI 제어를 기술적으로 가로채는 OS 훅이 아니라, 이 스킬의 필수 실행 진입 계약과 payload 검증기다.

```text
[실행 · 현재 세션 유지] 브리프 / 기획 / 컷맵
  → [Jev 분배] 저작 인계 / 에셋 검색·선택 / 최초 첨부 / 입력 / 대기
  → [아스트라 프롬프팅] 노래 · 이미지 · Seedance 문구만
     동시에 [현재 실행자] 독립적인 에셋 준비·설정 확인
  → [현재 실행자 · 짧은 묶음 실행] 검증 원문 입력 / 생성 / 다운로드 / QC
```

영상팀의 연출·identity·물리·중복 제출 방지·실파일 검증 기준은 유지한다. 실행을 Luna로 고정하거나 저작 때문에 세션 전체를 Astra로 전환하지 않는다.

## 범위와 경량화

- 실행은 현재 사용자 세션의 모델/도구를 상속한다. 세 종류의 프롬프트 저작만 정확한 `gpt-6-astra`로 라우팅한다. 현재 모델이 Astra면 직접 저작하고, 아니면 실제 Astra category를 확인해 bounded author만 위임한다. 사용할 수 없으면 저작만 HOLD하며 다른 모델을 Astra로 가장하지 않는다. 전역 모델/category를 바꾸지 않는다. Codex CLI, 10개 lane, 전체 원본 검사, SQLite registry, 상주 watcher는 필수가 아니다.
- 독립 5~15초 클립은 단일 제작 패키지로 처리한다. 명시 길이가 우선이며 영상팀 기본은 15초다. UI가 5초로 열려도 그대로 생성하지 않는다.
- 단일 클립에 별도 음악/VO/편집 요구가 없으면 provider audio로 음악·환경음을 함께 생성할 수 있다. Suno/Music Lock/CapCut을 불필요하게 강제하지 않는다. 실제 곡에 맞추는 MV나 긴 편집물은 음악 파일을 먼저 확정하고 필요한 모듈만 추가한다.
- No-I2V는 per-cut 시작/종료 이미지 없이 prompt로 장면을 설계하는 모드다. **캐릭터 준비 생략이 아니다.** 인물이 주인공인 댄스·연기·패션 클립은 먼저 reusable 캐릭터 시트를 만들거나 기존 승인본을 재사용한다. 정면 몸·후면 전신·큰 얼굴 초상으로 얼굴/체형/의상 앞뒤를 잠그고 시각 QC 후 실제 첨부한다. 장면·소품의 일관성에 필요한 reference도 판단하되 무조건 늘리지는 않는다. 0 reference는 캐릭터 기준이 불필요한 장면 또는 사용자가 명시적으로 무참조 생성을 선택한 경우만 쓴다.
- 기본 provider는 Runway의 Seedance 2.0. 사용자가 다른 버전/provider를 명시하면 실제 지원을 확인한다. No-I2V를 Keyframe 또는 이미지 생성으로 바꾸지 않는다.
- 생성 수량은 현재 사용자의 명시 요청/승인된 source 계획이 우선이며, 불명시 단일 컷의 초기 생성은 1개다. 실패 시 실패 원인을 구체적으로 기록하고 한 원인만 수정한다. 유료 무한 재시도·추가 변형 생성은 하지 않는다.

## 1. 브리프와 패키지

사용자 요청에서 목적·길이·실사/애니·피사체·화면비·참조·오디오를 정한다. 빠진 사소한 항목은 합리적으로 선택하고 한 줄로 알린다. `references/directing.md`를 읽고 연출한다.

현재 작업 artifacts 또는 사용자 지정 프로젝트 안에 아래만 둔다.

- `prompt.txt`: NFC UTF-8, 모델에 넣을 영상/음향 설명만.
- `package.json`: brief, duration_sec, provider_model, aspect_ratio, resolution, audio, generation_mode, ordered references, prompt_file, prompt_sha256, browser session/target, observed settings, job/status와 QC. `harness_policy_version=1`, `execution_model=inherit_session`, 사용한 종류별 `author_handoffs`(receipt path + accepted SHA256), 이미지 요청/관측 product와 실제 웹 대화 URL을 추가한다.
- 사용한 프롬프트별 `route → request → 실제 Astra 저작 → seal → submission prepare → submission verify`: `scripts/harness.mjs`로 최종 원문·실제 응답 snapshot·인수증을 묶고 `scripts/submission.mjs`로 provider별 검증 payload를 만든다. 이미지/노래도 예외가 아니며 사용자가 거절한 이전 이미지의 인수증을 소급 작성하지 않는다. `seal`이 반환한 `receipt_sha256`을 package의 `author_handoffs[].sha256`에 저장한다. `submission prepare` 반환의 `payload_sha256`과 파일 경로는 `provider_payload={path,sha256}`로 저장하고 생성 직전 `submission verify`한다. Seedance `check.mjs preflight`도 이 payload와 현재 prompt/stage가 일치해야 통과한다. `harness_policy_version`은 policy의 `schema_version`을 복사한다. package 필드만 쓰고 seal/검증을 생략하지 않는다.
- 실제 다운로드 영상과 전달 파일. 폴더/파일을 추측하거나 다른 프로젝트 영상을 가져오지 않는다.

이미지 프롬프트는 Astra가 `references/author-executor.md`의 **저작 전용 소스 계약**에 따라 공냥의 문구 구성 규칙과 웹 2.5 캐스팅 서술만 참고해 작성한다. 원본 스킬의 이미지 호출·웹 조작·QC 절차를 저작 역할로 가져오지 않는다. **모든 이미지 생성/편집의 기본은 웹 ChatGPT Images 2.5**이며 현재 세션이 브라우저에서 실행한다. 내장 imagegen/API/Grok still로 자동 대체하지 않는다. 인물은 단독 캐스팅 초상 선택 후 승인 identity로 전신·후면·시트를 파생하고 거절된 시트는 재사용하지 않는다. 제품/풍경에는 인물 캐스팅 절차를 강제하지 않는다. 웹에서 실제 관측한 기능만 사용하고 API 모델/품질 옵션이나 미노출 2.5 backend를 확인했다고 가장하지 않는다. 프롬프트 checker와 실제 이미지 QC는 구분한다. 실행자가 패널·identity·의상·손발을 검사하며 참조 시트의 패널/배경이 최종 영상 구도가 아니라는 역할은 Astra가 영상 prompt에 명시한다.

노래가 필요한 경우 Astra는 `music-director/references/awesome-suno-prompts/INDEX.md`와 관련 corpus 1~3개만 참고해 실행자가 정한 음악 방향의 가사·스타일·구조 프롬프트를 작성한다. 전체 음악감독 세션·사용자 선택 워크플로우를 새로 시작하지 않는다. Suno 조작·오디오 다운로드·청취 QC·Music Lock은 현재 세션이 한다. Seedance는 Astra가 `seedance-prompt-en/seedance-prompting.md`와 `prompt-review.md`의 문구 검토를 적용하고 명시적 2.5는 `seedance25-prompt-en/prompting.md`만 사용한다. 이 경로들은 `~/.codex/skills/` 아래다. 전체 dispatcher나 production 문서의 Generate·queue·다운로드를 author가 실행하지 않는다. 같은 block에 버전 규칙을 섞지 않는다.

**신규 이미지·Seedance 생성용 프롬프트의 기본 언어는 영어(en-US)다.** 대화·브리프·진행 설명이 한국어라는 이유로 생성용 원문을 한국어로 쓰지 않는다. 음악의 스타일·제작 지시도 기본 영어이며 실제 가사·대사·화면에 표시할 문구는 사용자가 지정한 원문 언어를 보존한다. 특정 작업에서 다른 프롬프트 언어를 명시한 경우에만 근거 있는 `prompt_language_override`로 기록한다. 예전 Codex 문서의 Korean-default/block-only-English 규칙은 신규 Aside 작업의 언어 기본값을 덮어쓰지 않는다. 영어 저작과 번역·언어 수정도 Astra가 맡으며 실행자가 승인 문구를 번역하지 않는다. 보통 700~1500자이며 Seedance UI 한도 3500자 이하로 쓰되, 분량을 맞추려고 승인된 고유 인과·참조 결속·복합 연출을 삭제하지 않는다. 시각적 사실·시간별 동작·카메라 경로·물리적 반응·끝 구도·소리를 쓴다. 파일 경로, 내부 상태, QC/승인 지시, 스킬 이름을 prompt에 넣지 않는다. 메타데이터와 prompt는 분리한다.

## 2. 현재 브라우저와 프로젝트 격리

1. `listBrowserTabs()`로 시작하고 관련 탭을 attach한 뒤 `snapshot(page,{interactive:true})`로 읽는다. 이후 행동마다 fresh snapshot과 diff로 확인한다.
2. 같은 작업의 저장된 session이 있으면 정확한 URL/target으로 재개한다. Generate가 불확실하거나 queue가 있으면 관측부터 하고 재클릭하지 않는다.
3. 다른 프로젝트의 참조·prompt·jobs가 있으면 지우거나 재사용하지 않는다. 이전 URL/간단한 composer checkpoint를 tmp에 보존한다. 관측된 New Session 링크를 사용해 이 작업의 빈 세션을 만든다. 기존 작업이 진행 중이거나 unsaved composer가 있으면 기존 탭을 보존하고 해당 링크를 별도 탭으로 연다. 이것은 같은 실행자의 탭 분리이며 별도 agent가 아니다.
4. 새 세션에서 빈 prompt, reference 0개, 기존 생성 카드 없음, 올바른 계정을 확인한다. 생성 후 확정된 sessionId URL/target을 package에 기록한다.
5. 로컬 Aside CLI 인증 문제를 해결하려고 키체인·계정을 변경하지 않는다. 브라우저는 현재 `functions.repl`만 사용한다. CDP 연결 실패 시 같은 대상 재확인까지 1회, 계속 실패하면 정확한 오류와 필요한 복구만 보고한다.

## 3. 입력과 제출

### Jev 분배와 빠른 입력 경로

- `references/jev-dispatch.md`를 읽고 `scripts/jev-dispatch.mjs next`의 다음 단계 추천을 실제 Astra 인계 또는 현재 실행자의 브라우저 행동으로 연결한다. 복수 다음 단계/의미 판단에 Jev를 쓰고, 확정된 해시 비교·한 가지 단순 동작에는 추가 호출을 하지 않는다.
- Jev는 역할/행동 후보만 고른다. 저작은 정확한 Astra, 실행은 `inherit_session`, 실제 권한·참조·payload·모드 검증은 기존 코드와 live UI다. Jev가 selector·경로·프롬프트·Generate를 만들어 실행하는 구조가 아니다. `advisory:true`, `execution_authorized:false`를 유지한다.
- Astra가 별도 author로 저작하는 동안 현재 실행자는 독립적인 에셋 검색·첨부·설정 준비를 진행하고, 문구 입력 시점에만 저작 결과를 기다린다. 같은 request의 중복 author 호출은 금지한다.
- 관측된 안정적인 UI 동작은 `scripts/runway-fastlane.js`의 짧은 단계로 묶는다. 검색 열기+검색어 fill, 검증된 에셋 선택+관측, 검증 payload fill+원문 확인을 각각 한 REPL 호출에서 처리하며 모든 action 뒤 snapshot/diff를 유지한다. 업로드는 독점 시도 기록·검증 파일·실제 file input이 있는 최초 첨부만 처리한다. 지원하지 않는 UI는 기존 절차로 처리한다.
- dispatcher는 동일 작업 root당 최대 3 API 시도, 같은 성공 입력 캐시, 실패 자동 재시도 없음이다. 같은 상태를 별도 안내문 classifier에 다시 보내지 않는다. 한도/장애 시 현재 실행자로 이어가며 업무 전체를 멈추지 않는다. 준비 경로는 Generate/결제/최종 승인 권한을 주지 않는다.

### Seedance 참조 파일은 한 번 고정, 재탐색 금지

- 참조 준비·첨부·재개 전에 `references/seedance-upload.md`를 따른다. 현재 package/원본 manifest의 **절대경로·실제 hash·역할·순서**를 한 번 확정한다. 같은 basename의 원본·썸네일·구버전을 혼동하지 말고, 이미 확정된 경로를 매번 Finder/Recents에서 다시 찾지 않는다.
- 신규 참조 묶음은 `scripts/seedance-references.mjs prepare`로 만들고 반환된 plan hash를 `package.reference_bundle={path,sha256}`에 보존한다. 이후에는 같은 bundle을 `verify`해 재사용한다. exported `references.json`을 Astra의 Image1.. 매핑, submission payload, package.references에 공통 사용한다. 파일·순서 변경 시 새 bundle/인계로 처리하며 승인된 prompt를 실행자가 고치지 않는다.
- **기본은 재업로드가 아니라 기존 에셋 검색 재사용**이다. `scripts/runway-assets.mjs lookup --scope <현재 team slug> --file <검증된 파일>`로 워크스페이스+파일 SHA256 기록을 먼저 확인한다. 같은 이미지면 컷/session/Image 슬롯/staging 파일명이 바뀌어도 기존 asset_name/ID를 재사용한다. 레지스트리에 없어도 원본 이름으로 에셋 검색부터 하며 NOT_REGISTERED를 미업로드로 단정하지 않는다.
- 검색은 현재 UI의 `Reference → Asset selector → Search`를 우선하고, 필요하면 `References → Add Reference`로 연다. 확인된 실제 이름으로 검색해 유일한 정확한 에셋을 double-click하고 Image1.. 적용을 확인한다. 과거 업로드는 필요할 때 원본 Download와 로컬 hash를 한 번 대조해 공용 기록에 결속한다. 상세 절차는 `seedance-upload.md`를 따른다. 이 정확 조회에는 Jev를 쓰지 않는다.
- 검색/범위 확인 뒤에도 기존 에셋이 없을 때만 live file input/file chooser에 검증된 `upload-files.json` 경로를 직접 전달한다. 최초 업로드 수용 시 실제 이름/asset ID/hash를 공용 기록과 package.reference_uploads에 저장한다. batch 허용 여부와 실제 슬롯 순서는 별도로 확인한다. 이미 선택된 항목을 다시 toggle하거나, 이름이 비슷하다는 이유로 다른 파일을 대체하지 않는다.
- 명확한 상태는 규칙으로 처리한다. 다음 작업 판단은 위 Jev dispatcher를 우선하고, 분배가 아닌 안내문 종류만 필요한 경우 `scripts/jev-seedance.mjs diagnose`를 사용한다. 같은 상태에 두 runner를 이중 호출하지 않는다. Jev는 직접 클릭·업로드·Generate 권한이 없으며, 다음 단계 추천은 현재 실행자가 실제 근거를 확인해 수행한다. 같은 작업 root당 최대 3회, 성공한 같은 안내문은 캐시 재사용, 자동 재시도 없음. 기존 composer/queue를 보존한다.
- 파일 bundle 검증, 실제 browser 첨부 확인, Astra prompt 검증은 별개다. 한 항목의 성공으로 다른 항목을 PASS 처리하지 않는다.

### Video → Reference 고정 게이트

- Runway의 영상 composer는 **`Video → Reference`만** 사용한다. Keyframe, Start/End Frame, Image 작업공간으로 탐색하거나 모드를 추측하지 않는다. 참조가 0개/1개라는 이유로 Keyframe을 선택하지 않는다. 사용자가 향후 Keyframe/I2V를 명시하면 별도 작업 계약으로 분리하며 이 Reference 전용 gate를 무력화하지 않는다.
- 진입/재개, 새 세션, 새로고침, 모델 변경 직후와 **참조 첨부·prompt 입력·Generate 직전**에 fresh snapshot으로 Video와 Reference의 **선택 상태**를 확인한다. `Reference` 텍스트가 단지 존재하는 것과 선택된 것은 다르다. accessibility에 선택 상태가 없으면 screenshot으로 active tab과 composer를 판독한다. 시작/종료 프레임 슬롯이 보이거나 선택이 애매하면 실패다.
- package에 `video_workspace="Video"`, `video_input_mode="Reference"`를 고정한다. 실제 관측에서만 `observed_settings`의 `video_workspace`, `video_input_mode`, `mode_selection_verified=true`, `keyframe_slots_visible=false`, `observed_at`을 기록한다. **`node scripts/check.mjs mode <package.json>` 통과 전 첨부·prompt 입력 금지**, 최종 `preflight`도 동일 gate를 검사한다. 관측은 30초 이내여야 하며 모드에 영향을 주는 UI 변화 후에는 이전 PASS를 폐기한다. JSON 검사는 라이브 UI 확인을 대신하지 않는다.
- 잘못 Keyframe에 들어갔으면 `[실행 · Reference 모드 복구]`를 알리고 모든 첨부/입력/Generate를 멈춘다. 현재 session URL/기존 prompt/참조/queue를 보존한 뒤 **관측된 Video, Reference control만** 선택해 돌아온다. 각각의 클릭 뒤 snapshot으로 확인한다. 다른 작업의 미저장 입력을 지우거나 새 board로 도망가지 않는다. 생성 접수 여부가 불확실하면 먼저 기존 queue를 관측하며 재클릭하지 않는다.
- 복귀 후 참조 순서·prompt·모델·길이·비율·오디오까지 다시 대조하고 mode gate를 재실행한다. 동일 복구 경로는 최대 1회만 시도한다. 실패하면 `BLOCKED_REFERENCE_MODE_NOT_CONFIRMED`로 중단하며 Keyframe fallback/탭 왕복 탐색을 하지 않는다. UI 전환은 현재 세션 실행자만 맡는다.

- snapshot에서 확인한 Prompt textbox를 locator로 입력한다. 한 번 입력한 후 fresh snapshot으로 전체 내용과 실제 글자 수를 확인한다. `.fill`이 Lexical에서 정상 수용되면 추가 ClipboardEvent/IME 우회 코드를 만들지 않는다. 실패할 때만 actual editor를 확인해 bounded recovery를 적용한다. 불확실하면 먼저 읽고 중복 append하지 않는다.
- 실제 **Video → Reference 선택 유지**, model, duration, ratio, resolution, audio를 설정한 뒤 메뉴를 닫고 다시 읽는다. 참조 0개도 UI가 text-only를 지원하고 Generate를 허용할 때만 사용한다.
- 비용/Unlimited mode를 실제 UI로 확인한다. credit 구매, 유료 플랜 변경, 계정 변경, 공개 제출은 별도 승인 없이 하지 않는다. 사용자가 요청한 현재 수량과 비용 범위에서만 실행한다.
- `scripts/check.mjs preflight <package.json>`은 파일·명시 설정 일관성 검사다. 실제 UI 증거를 대신하지 않는다.
- 제출 직전 체크: 올바른 빈/현재 session, **Video → Reference 선택 확인 및 Keyframe 슬롯 없음**, 정확한 prompt, reference count/order, model, duration, ratio/resolution, audio, 단일 Generate 및 권한/비용 범위.
- package에 `SUBMITTING`을 기록한 뒤 Generate를 **한 번** 클릭한다. 신규 카드/queue 수락을 fresh snapshot에서 확인해야 `ACCEPTED`다. 클릭 timeout은 재클릭 허가가 아니다.

## 4. 대기와 다운로드

- provider가 진행 중임을 보여줄 때만 bounded wait 후 snapshot한다. 시작은 10~20초 단위, 긴 queue는 사용자에게 상태를 알린다. 1분을 넘는 지속 대기는 native notification/routine 정책을 따른다. 실제 routine 요청·승인 없이 timer 파일을 자동 재개로 가장하지 않는다.
- 불필요한 별도 observer, Codex CLI, 다른 browser, hidden API 생성은 사용하지 않는다. 재개 시 package와 실제 board를 먼저 대조한다.
- matching 새 카드의 Download를 사용한다. Playwright download event로 saveAs하거나 실제 관측한 다운로드 URL을 cookie-aware fetch로 저장한다. URL을 추측하지 않는다. 홈페이지 HTML을 MP4라고 저장하지 않는다.
- `node scripts/check.mjs media <downloaded.mp4>`로 실제 바이트, SHA256, duration, codec, size, audio 존재를 확인한다. ffprobe/ffmpeg가 PATH에 없으면 실제 설치된 `/opt/homebrew/bin`을 사용한다.

## 5. QC와 전달

- 15초 요청이면 실제 duration을 검사한다. 기대치 ±0.25초를 벗어나면 성공으로 처리하지 않는다. 원본은 보존한다.
- 실제 영상 재생에서 전체 움직임을 확인할 수 있으면 전 구간을 본다. 프레임 추출/contact sheet는 구도·identity·해부학·질감 확인에만 쓰며 full motion 또는 청취 PASS로 부풀리지 않는다.
- 댄스는 두 발의 접지와 체중 이동, 무릎/팔 관절, 손/발 증식, 얼굴/의상 유지, 음악 대비 움직임, 마지막 pose를 본다. 단일 약속된 클립이면 불필요한 CapCut 편집을 강제하지 않는다.
- 파일 검증, sampled-frame QC, playback QC, audio QC를 각각 별도 상태로 기록한다. 청취/전체 재생 능력이 없으면 해당 항목을 미검증으로 밝힌다. 실패 영상을 최종 승인본이라고 부르지 않는다.
- 최종에는 다운로드 MP4 링크, 실제 길이/해상도, 짧은 결과·미검증 항목을 제공한다. 가능하면 영상 대표 프레임 proof를 tmp에 저장해 함께 보여준다. user-requested video는 artifacts에 둔다.

## Jev 적재적소 사용: 작업 분배·QC·Seedance 안내문

- 영상팀에서는 사용자의 상시 허용에 따라 **Seedance 입력 준비의 다음 작업 분배, 필요한 QC 기록 및 애매한 첨부 안내문 분류**에 Jev를 호출한다. 매 컷·매 snapshot·정상 성공에 기계적으로 붙이지 않는다. Astra/현재 세션 역할과 기존 gate는 그대로 유지한다. 별도 생성자·브라우저 실행자·상주 에이전트가 아니다.
- QC 호출 조건은 관찰 기록에 서로 다른 문제가 섞인 `mixed_findings`, 같은 결함이 반복된 `repeated_failure`, 문제 종류가 모호한 `uncertain_category` 중 하나다. 단순 수치·해시·설정 비교, 이미 명확한 단일 결함, 프롬프트 저작에는 호출하지 않는다. 브리프/참조 선택/프롬프트 의미 검토는 아직 Jev 자동 적용 범위가 아니다.
- QC는 `references/jev-qc.md`를 읽고 **`scripts/jev-video.mjs` 경유**로 호출한다. Seedance 안내문은 위 첨부 절차의 별도 runner/최대 3회 한도를 따른다. `status`는 키 존재만 확인한다. 같은 작업은 동일 `--root`를 사용하며 `.jev` 캐시·시도 원장을 삭제하거나 다른 root로 한도를 우회하지 않는다. 작업 root당 최대 5회, 같은 성공 입력은 재사용한다. 장애·키 없음·한도 초과는 기존 실행자가 처리하고 자동 재시도하지 않는다.
- QC 입력은 실제 실행자가 관찰한 익명화 QC 노트와 관찰 범위뿐이다. Seedance 안내문 입력은 파일명·계정·경로·비밀을 제거한 실제 안내문뿐이며 전체 snapshot을 보내지 않는다. 고객명·비밀·불필요한 대본·원본 영상·이미지·전체 package·대화를 보내지 않는다. 관찰하지 않은 항목을 채워 넣지 않는다. 결과의 주분류만 검토 후보로 사용하고 원본 노트와 대조한다. 독립 noul 신호를 임계값으로 묶어 결함을 추가하거나, confidence를 정답률/승인 기준으로 해석하지 않는다.
- 결과·실제 모델·입력 hash는 `.jev` 파일로 보존하고 선택적으로 package에 결과 경로만 기록한다. `CLASSIFIED`만 실제 호출 성공이며 모의 시험·dry-run·캐시·미연결을 구분한다. `NO_ISSUE_REPORTED`도 실제 영상 PASS가 아니다. 실행자가 원인·수정 요구를 확정하고 수정 문구는 Astra로 보낸다.
- 분배 시 `[Jev 분배 · 다음 단계 → 담당]`, QC 시 `[Jev 보조 분류 · QC 기록 / 실행 권한 없음]`을 표시한다. 프롬프트 수정·유료 재생성·Generate·최종 QC 승인·모델 전환 권한은 없다. 유료 크레딧 구매·자동충전·한도 확대는 별도 사용자 요청 없이 하지 않는다.

## 스킬 개선

실제 실행에서 증명된 개선만 이 Aside 스킬에 반영한다. 계획을 성공 사례로 기록하지 않는다. 원본 Codex 영상팀·다른 프로젝트·전역 모델 설정은 수정하지 않는다. 재사용할 가치가 없는 task URL·계정·개별 job은 SKILL.md에 넣지 않고 해당 package에 보존한다.
