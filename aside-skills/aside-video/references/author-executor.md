# Aside 역할 하네스

## 단일 정책과 가시적 역할

`harness-policy.json`이 Aside 신규 제작의 역할 라우팅 원본이다. Codex 프로젝트의 별도 저작·attestation 계약을 소급 변경하지 않는다.

```text
[실행 · 현재 세션 유지] 브리프 / 기획 / 컷맵 / 참조 선택
           ↓ 필요한 프롬프트만 인계
[아스트라 프롬프팅] 노래(Suno) / 이미지 / Seedance
           ↓ 원문 + 파일 hash + 실제 응답 근거
[실행 · 현재 세션 유지]
  Suno 조작 / 웹 ChatGPT Images 2.5 / Runway
  업로드 / 컴퓨터 유즈 / 다운로드 / QC / 편집 / 납품
           ↓ QC 실패 시 수정 요구만 전달
[아스트라 프롬프팅] 해당 프롬프트만 수정 → 실행자 복귀
```

- 시작 시 위 구조를 짧은 표나 코드 블록으로 보여준다. 각 전환 직전에는 `[아스트라 프롬프팅 · 노래|이미지|Seedance]` 또는 `[실행 · 현재 세션 유지]`를 진행 메시지로 표시한다. 내부 파일에만 기록하지 않는다.
- Astra의 업무는 노래 프롬프트·가사/스타일·구조 지시, 이미지 생성/편집 프롬프트, Seedance 프롬프트와 그 의미 수정뿐이다. 일반 기획·컷맵·참조 선택·실물 QC는 실행자가 한다. 이미지 수정 문구도 Astra에 되돌린다.
- 실행자는 완성된 문구를 복사하고 UI 길이/hash를 검사한다. 줄임·번역·의미 보완을 몰래 하지 않는다. 실패 원인 분석과 QC 판단은 실행자의 업무다.
- 실행 모델은 항상 `inherit_session`. Luna, Astra 또는 다른 모델로 실행 세션을 바꾸지 않는다. 같은 Astra 모델이 실행할 때도 그것은 현재 세션이 Astra이기 때문이지 실행 모델 pin이 아니다.

## Jev 다음 단계 분배와 병렬 준비

- Seedance 입력 병목을 줄일 때 `jev-dispatch.md`의 분배기를 사용한다. Jev가 AUTHOR_ASTRA를 추천하면 아래 실제 request/native author/seal 경로로 연결한다. 추천만으로 저작 완료가 되거나 실행 모델이 바뀌지 않는다. Luna를 포함한 현재 실행자는 그대로 남는다.
- 별도 Astra author를 호출할 경우 가능한 독립 업무가 있으면 `run_in_background=true`로 시작한다. 현재 실행자는 그동안 확정된 에셋의 검색·참조 준비·설정 확인을 진행하고, 최종 문구 입력 시점에만 결과를 기다린다. author 결과에 의존하는 참조 변경은 병렬로 추측하지 않는다.
- 동일 저작 request/brief가 이미 진행 중이면 새 author를 호출하지 않는다. 캐시된 Jev 추천도 현재 request 상태와 실제 session context로 재검사한다. 완료된 문구는 `submission verify` 반환을 `runway-fastlane.js`로 원문 그대로 입력할 수 있다.
- 준비 단계의 Jev 행동 추천과 빠른 브라우저 함수는 기존 역할·인수증·provider 권한·비용 검증을 대체하지 않는다. CLI 자체가 native 모델을 실행하거나 브라우저를 가로채는 것은 아니다.

## 영어 기본 저작 계약

- 새 이미지·Seedance 및 음악 제작 지시의 기본은 영어(en-US)다. 한국어 대화/브리프를 영어 provider 원문으로 작성하는 것도 Astra 저작 범위다. 실제 가사·대사·화면 문자만 지정 원문 언어를 보존한다.
- `prompt-language.md`를 따라 request의 `language_contract`와 `author_task`를 실제 author에게 전달한다. 구형 Codex 원문의 한국어 기본 규칙을 복사하거나 별도 인계 메시지에서 Korean prompt를 요구하지 않는다. 명시적인 현재 작업 언어 예외만 `context.prompt_language_override`에 근거와 함께 기록한다.
- 언어 검증 실패는 새 Astra 수정 인계로 돌린다. 기존 인수증을 바꾸거나 실행자가 번역하지 않는다. 입력에는 `CURRENT_POLICY_VALIDATED` 결과만 사용하며, 언어 없는 legacy 검증은 보관 증거 확인일 뿐 신규 제출 허가가 아니다.

## 지식 패킷과 확인

이미지·Seedance는 `knowledge.md`를 적용한다. request가 생성한 bounded 지식 본문이 `author_task`에 포함되어야 하며, 실제 Astra가 같은 응답에 `Knowledge-SHA256: <request.knowledge.sha256>`를 남겨야 seal된다. 어떤 카드가 문구에 기여했는지도 원문 밖에서 설명한다. 이 확인은 내부 추론·시각 품질의 증명이 아니다. 전체 원본 스킬/위키를 재로드하여 옛 언어·owner·API 규칙을 섞지 않는다.

## 필수 실행 순서

1. `aside.sessions.current()`로 **현재 실행 세션 id**를 얻는다. `node scripts/session-context.mjs <id> --out <new-context.json>`로 실제 세션 설정과 category를 읽는다. 전역 default를 실행 모델로 추측하지 않는다.
2. 실행자가 brief·정확한 ordered reference와 변경/보존 범위를 정한다. 읽기 전용 session-context 사본에 실제 사용자 요청을 `user_instruction`으로 추가하고, 필요한 `preserved_literals` 및 명시적 언어 예외만 기록한다. 사용자가 요청을 다시 말하게 하거나 영어 기본값에 별도 승인을 요구하지 않는다. 현재 모델이 Astra가 아니면 아직 문구를 쓰지 않는다. `harness.mjs request <stage> --context <context.json> --root <package-dir> --prompt <new-prompt.txt> --out <new-request.json>`을 실행한다.
3. request의 `route.mode=functions.subagent`이면 **반드시 native `functions.subagent`를 실제 호출**한다. `subagent_profile=default`, `model_category=request.route.category`, 목적은 `Astra 이미지 프롬프트` 같은 구체적인 저작, prompt는 request의 `author_task` + 실제 root/출력 경로 + bounded brief/소스다. `inherit`는 현재 실행 모델이 Astra가 아닌 경우 사용하지 않는다. `visual`/`deep` 같은 이름 자체를 Astra 증거로 쓰지 않는다. 현재 설정이 바뀌면 category를 다시 확인한다.
4. 실행자 자체가 child라 native `functions.subagent`가 없으면 **`AWAITING_PARENT_ASTRA_AUTHOR`**로 request·brief·실행자 id를 기존 parent에 인계한다. parent가 실제 Astra author를 호출하고 seal/submission을 검증해 같은 실행자에게 payload를 돌려준다. 새 상주 관리자나 CLI를 만들지 않는다. 이때 package에 requester/executor id와 dispatcher id, actual author id를 분리하고 `author_dispatch_mode=parent_mediated`로 기록한다. parent 경로도 없으면 `HOLD_ASTRA_AUTHOR_REQUIRED`이며 실행자가 대필하지 않는다.
5. author 반환 뒤 실제 dispatcher의 `aside.sessions.childSessions(dispatcherId)`와 actual author `messages.jsonl`의 assistant model을 확인한다. author는 파일을 쓴 뒤 응답에 `Prompt-SHA256: <final hash>` 또는 최종 원문을 남긴다. 자산 이름/프로젝트에 Astra가 포함된 것은 모델 근거가 아니다.
6. `seal`은 그 **author child**의 대화 기록을 사용한다. 실제 Astra 직접 저작일 때만 현재 세션 기록을 사용한다. `submission.mjs prepare`로 image/music/Seedance 각각 provider 입력 payload를 만들고 **입력 직전 `submission.mjs verify`**를 통과시킨다. receipt와 payload의 독립 수락 hash를 package에 보존한다.
7. 현재 세션 실행자는 검증된 payload의 `prompt`를 파일에서 그대로 읽어 composer에 입력한다. UI의 수용된 문구와 대조한 뒤 단일 제출한다. 새 문자열 작성·번역·요약·내용 보완은 금지한다. 이미지 `inputImages` 배열 또는 웹 첨부가 prompt와 다른 문제는 실행자가 검사한다.
8. `[아스트라 프롬프팅 · 종류 / 실제 author session]`와 `[실행 · 현재 세션 유지 / payload 검증 완료]`를 표시한다. 미호출/검증 실패인데 Astra 완료를 표시하지 않는다.

Astra 호출 성공과 이미지 품질 성공은 별개다. 승인 자산을 썼다는 말로 shape/background identity QC를 대신하지 않으며, 웹 ChatGPT 대신 내장 `imagegen.generate`를 썼으면 웹 2.5 사용으로 보고하지 않는다.

## 실제 모델 선택

1. Aside builtin `aside` 스킬을 읽고 `aside.sessions.current()`와 `aside.settings.get('modelCategories')`를 확인한다. account default를 현재 호출 증거로 취급하지 않는다.
2. **세션 설정 변경은 실제 실행 모델 변경 증거가 아니다.** 기존 child의 `aside.sessions.update(model)` 이후 subagent 재개/heartbeat도 기존 실행 모델을 사용할 수 있으므로, 모델 지정/재개 실험에서는 첫 실제 assistant 응답이 의도한 모델인지 확인하기 전 저작·브라우저·생성을 시작하지 않는다. 현재 세션 모델은 API가 제공하면 명시 모델을 읽는다. 요약 API에 모델이 생략되면 account `state.db`의 `sessions`에서 **현재 id의 model만 읽기 전용 조회**한다. DB 직접 쓰기는 금지한다. 예: `sqlite3 -readonly '<accountRoot>/state.db' "select model from sessions where id='<verified-current-id>';"`. 실제 응답 모델은 해당 세션 `messages.jsonl`의 assistant `model`/`provider`로 별도 확인한다. 시스템 프롬프트나 credentials를 읽을 필요는 없다.
3. `{session_id, model, modelCategories}`를 작업 tmp의 `context.json`으로 저장해 `node scripts/harness.mjs route <stage> --context <context.json>`으로 분기한다. account 기본값은 route 후보의 보조 정보일 뿐이다.
4. 실제 현재 모델이 `gpt-6-astra`이면 동일 세션에서 저작한다. 그 외에는 현재 category 설정 중 정확히 Astra를 가리키는 category만 골라 `functions.subagent`의 bounded author에 넘긴다. `model_category=deep`이라는 이름만으로 Astra를 추정하지 않는다. author는 prompt 파일/텍스트만 반환하고 탭·외부 생성·추가 spawn·실행 설정을 만지지 않는다. 전체 대화를 fork하지 말고 brief/참조 설명/거절 사유만 전달한다.
5. 현재 도구가 정확한 Astra 경로를 제공하지 않으면 저작 단계만 `HOLD_ASTRA_AUTHOR_REQUIRED`. 다른 모델 대행, 일시적 전역 category 변경, child 시작 후 모델 변경, CLI sidecar 생성으로 우회하지 않는다. 이미 검증된 프롬프트의 실행 준비는 계속할 수 있다.
6. 신규 Aside 작업은 Astra 모델을 필수로 하고 effort는 선택된 author 세션 설정을 유지한다. `xhigh`는 선호값이며 그 값을 적용했다고 가장하지 않는다. 기존 Codex 프로젝트가 실제 Astra/xhigh attestation을 요구하면 그 gate를 그대로 유지한다. 계정 전체나 실행 세션 effort를 하네스가 강제로 변경하지 않는다.
7. 반환 task/session 식별자와 실제 assistant 응답 모델을 확인한다. 요청 route만 맞고 반환이 다른 모델이면 인수하지 않는다. 제공된 도구·플랫폼의 위임 권한을 따르되 동일 승인 범위를 반복 질문하지 않는다.

## 저작 전용 소스 계약

실행자가 원본에서 **현재 프롬프팅에 필요한 부분만** 선택해 author에게 준다. 원본 스킬의 운영 지시는 이 Aside 역할 분담을 덮어쓰지 않는다.

| Astra 작업 | 허용 읽기 범위 | 제외하는 일 |
|---|---|---|
| `music_prompt` | `~/.codex/skills/music-director/references/awesome-suno-prompts/INDEX.md`와 관련 prompt/example 1~3개, brief의 확정 음악 방향 | 전체 음악감독 세션, 재질문/선택 회의, Suno 조작, Music Lock, 청취 QC |
| `image_prompt` | request.knowledge의 검토된 image 카드·source-role·현재 brief, 필요하면 현재 웹 캐스팅의 인물 서술만 | 원본 `$imagegen`/API 호출, 캐스팅 선택/QC, 웹 조작·다운로드. gpt-image-2 전용 size/API/품질 토큰은 웹 2.5에 강제하지 않음 |
| `seedance_prompt` | request.knowledge의 현재 버전 video 카드·source-role·현재 brief. 추가 연구는 실행자가 검토한 새 카드로만 승격 | dispatcher의 production/queue/registry 단계, Runway 조작·첨부·Generate·QC |

Author brief에는 정확한 입력 파일 목록과 유일한 출력 prompt 경로를 적는다. allowed write는 그 파일뿐이다. 브라우저/컴퓨터 유즈, `imagegen.generate`, Suno/Runway/ChatGPT 조작, `openTab`, 외부 생성/업로드, CLI sidecar, 추가 subagent/spawn, 계정/모델 설정 변경을 금지한다. 로컬 파일 읽기와 저작 파일 쓰기/hash 검사는 가능하다. 이러한 도구 제한은 native author에게 전달하는 작업 계약이며 별도의 OS 샌드박스를 구현했다고 주장하지 않는다.

세부 작업의 정책 stage 매핑: 기획·연출·참조 선택·생성 설정 계획은 `planning`, 컷맵·콘티는 `storyboard`, 참조 업로드·UI/OS 조작은 `computer_use`, Music Lock/청취는 `audio_qc`, 캐스팅·시트 검수는 `image_qc`, 폴더링·납품은 `package`. 프롬프트 수정만 대응하는 세 author stage로 되돌린다.

## 파일 인계와 검증

하네스 CLI는 역할 계획·불변 인수증·파일 무결성을 담당한다. 실제 모델 호출은 현재 Aside native 도구가 수행한다. CLI가 모델이나 provider를 실행한 것처럼 보고하지 않는다.

```bash
node scripts/harness.mjs status
node scripts/harness.mjs route image_prompt --context '<context.json>'
node scripts/harness.mjs request image_prompt --context '<context.json>' --root '<package-directory>' --prompt 'image-prompt.txt' --out 'image-request.json'
# 실제 Astra가 원문 또는 Prompt-SHA256과 Knowledge-SHA256을 같은 실제 응답에 포함한다.
node scripts/harness.mjs seal --request '<package-directory>/image-request.json' --evidence '<actual-author-session>/messages.jsonl' --out 'image-receipt.json'
node scripts/harness.mjs verify '<package-directory>/image-receipt.json' --sha256 '<accepted-receipt-sha256>'
node scripts/submission.mjs prepare --stage image_prompt --receipt '<package-directory>/image-receipt.json' --sha256 '<accepted-receipt-sha256>' --out '<package-directory>/image-payload.json'
# 실제 참조가 있는 생성은 prepare에 --references <ordered-reference-files.json>도 전달한다.
node scripts/submission.mjs verify '<package-directory>/image-payload.json' --sha256 '<accepted-payload-sha256>'
```

- request는 아직 없는 prompt 경로도 허용한다. 존재하는 초기 파일을 입력으로 쓸 때는 비어 있지 않은 NFC UTF-8 prompt를 준비한다. author는 지정된 prompt 파일만 생성/수정한다. seal은 request 이후 실제 Astra assistant 응답이 최종 원문 또는 SHA256에 연결되는지 확인해야 한다. 단순 `model: astra` 자기 선언은 증거가 아니다.
- `seal`은 실제 대화 기록 중 연결된 assistant 응답 한 건을 package 안의 불변 evidence snapshot으로 보존한다. 원본 대화 파일이 package 밖에 있어도 읽을 수 있고, 이후 응답 추가는 허용하지만 선택된 응답의 변경/삭제는 실패한다. requester와 author session/task를 분리하며 확인되지 않은 author ID를 parent ID로 채우지 않는다.
- 인수증과 `seal` 반환의 `receipt_sha256`을 `package.json`의 `author_handoffs`에 `{ "receipt": "image-receipt.json", "sha256": "<accepted hash>" }` 형태로 넣는다. 노래/이미지/Seedance 각각 독립 인계하며 사용하지 않는 종류는 만들지 않는다. 웹 UI의 prompt 입력이 최종 원문과 일치하는지도 실행자가 확인한다.
- `verify` 성공은 파일·기록 연결 검사다. 의미 품질, 모델 내부 추론 effort, 실제 UI 첨부, 음악 청취, 영상 motion QC 성공을 뜻하지 않는다.
- `submission.mjs`는 이미지=`chatgpt_web`, 노래=`suno_web`, Seedance=`runway_web`의 정확한 stage·provider·저작 인수증·prompt·ordered reference 파일 hash를 검증한다. 이미지/노래를 Seedance preflight가 대신 검증한다고 간주하지 않는다. 참조 목록 각 항목은 `{path:<absolute file>,sha256:<file hash>,role:<실제 기여 범위>}`다.
- 인수 후 파일 수정·모델 불일치·원문 없는 반환은 제출하지 않는다. 프롬프트 수정은 새 request/receipt로 재인계한다. 기존 인수증을 덮어쓰지 않는다.
- 전체 역할 단계 중 `planning`, `image_generate`, `computer_use`, `image_qc`는 반드시 실행자 경로여야 한다. 정책에 없는 단계는 실행자로 추정하지 않고 명시적으로 매핑을 정리한다.

## 이미지 경로

모든 신규 이미지(캐릭터, 캐스팅, 시트, 장면, 제품, 편집)는 웹 ChatGPT Images 2.5를 기본 경로로 사용한다. 이미지 프롬프트는 Astra가 쓰고 실제 웹 조작은 현재 세션이 한다. `web-chatgpt-casting.md`의 웹 확인/다운로드 절차를 읽는다. 인물만 얼굴→몸→시트 규칙을 적용하며 제품/풍경에 캐스팅 절차를 강제하지 않는다.

웹 모델 세부 표기가 없으면 `requested_product=ChatGPT Images 2.5`, `observed_product=<actual label>`, `backend_variant=unverified`를 분리한다. 사용 불가 시 `BLOCKED_WEB_CHATGPT_IMAGE_ACCESS`로 두고 내장 imagegen/API/Grok still로 자동 대체하지 않는다. 사용자 명시 변경이 있을 때만 대체한다.
