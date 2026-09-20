# Jev QC 노트 분류기 (실행자 선택형 보조 도구)

Jev는 실행자 또는 사람이 작성한 QC 관찰 노트만 분류한다. Astra 저작·브라우저 실행·실제 미디어 QC는 변경하지 않는다. 한국어 합성 사례의 실제 API smoke test는 통과했지만 **실제 제작 데이터 정확도·확신도 임계값·시간 절감 효과는 미검증**이다. 모의 테스트는 계약·보안 검증이며 영상 QC 검증이 아니다.

## 영상팀의 기본 진입점

사용자가 적재적소 사용을 허용했으므로 아래 사유에 해당하면 별도 허락을 반복해서 묻지 않고 실행자가 선택한다. 매 컷 강제 호출은 하지 않는다.

| reason | 사용 상황 |
|---|---|
| `mixed_findings` | 한 QC 노트에 서로 다른 문제가 섞여 분류 정리가 필요함 |
| `repeated_failure` | 같은 문제가 반복되어 수정 요구를 정리하기 전에 보조 분류가 유용함 |
| `uncertain_category` | 실행자가 관찰한 문제의 종류가 모호함 |

```sh
node scripts/jev-video.mjs status
node scripts/jev-video.mjs classify --root /absolute/current-package --input /absolute/qc-note.json --reason mixed_findings
```

- 기본 인증 파일은 `<accountRoot>/secrets/typesafe-video-team.key`다. 비밀값을 출력하거나 package·프롬프트·로그에 복사하지 않는다. key-file과 디렉터리 권한은 각각 0600/0700으로 유지한다.
- 같은 작업에는 같은 root를 사용한다. `.jev` 안에 성공 응답 캐시·시도 원장을 보존한다. 같은 입력/모델/질문 버전의 검증된 성공 응답은 재사용한다. 작업 root당 최대 5회 시도이며 오류도 시도 수에 포함한다. 동시 실행은 잠금으로 거절한다. 자동 재시도·한도 우회·새 root로 재시도·작동 중인 lock 삭제는 금지한다.
- 정상 성공·명확한 단일 결함·해시·길이·숫자 검사에는 호출하지 않는다. 저작 전 브리프/프롬프트 검사까지 임의로 확장하지 않는다. 오류·키 없음·한도 초과는 기존 실행자의 검토로 돌아가며 Jev 통과로 표시하지 않는다.
- **주분류를 원본 관찰 노트와 대조한 후 참고**한다. 독립 noul 신호는 진단용 원자료일 뿐 자동 결함 태그·PASS·분기 조건으로 쓰지 않는다. 실제 시험에서 얼굴 변화만 명시한 노트에도 효과 결함 신호가 높게 나왔으므로, 여러 noul을 임계값으로 합쳐 새 결함을 추론하지 않는다.
- `NO_ISSUE_REPORTED`는 노트의 보고 범위에만 해당한다. 실제 미디어 검수 PASS가 아니다. `INSUFFICIENT_EVIDENCE`면 필요한 관찰을 먼저 하고, `MULTIPLE`이면 실행자가 실제로 확인된 항목을 나눈다. 이후 수정 문구는 Astra에만 맡긴다.
- wrapper는 provider 생성·프롬프트 쓰기·package 변경·계정 결제 변경을 하지 않는다. 유료 크레딧 구매·자동충전은 별도 요청 없이 하지 않는다.

## 저수준 도구 (개발·검증용)

일상 영상팀 작업은 위 wrapper만 사용한다. 아래 직접 호출은 연결 시험·개발 시에만 사용하며 작업별 캐시/횟수 제한을 대신하지 않는다.

## 사용

스킬 디렉터리에서 실행한다. 입력/출력 경로는 현재 작업 디렉터리 기준이다.

```sh
node scripts/jev-qc.mjs status
node scripts/jev-qc.mjs status --key-file /private/path/typesafe.key
node scripts/jev-qc.mjs classify --input qc-note.json --out shadow-dry.json --dry-run
node scripts/jev-qc.mjs classify --input qc-note.json --out shadow-result.json --key-file /private/path/typesafe.key
```

입력 예시:

```json
{"qc_note":"샘플 프레임에서 왼손 손가락이 하나 더 보인다.","observation_scope":"sampled_frames"}
```

- `qc_note`: 공백만은 불가, Unicode 코드 포인트 기준 최대 6000자. 입력 파일 최대 65536바이트.
- `observation_scope`: 생략하면 `text_only`; `sampled_frames`, `full_playback`, `audio_playback`도 허용. 이 값은 작성자의 관찰 범위 선언이지 재생·청취 증명이 아니다.
- 두 필드 이외는 엄격히 거절한다. package, 미디어, 첨부파일, 경로를 읽어 전송하는 기능은 없다. 노트에 비밀값·개인정보·미디어 인코딩을 넣지 않는다. 자유 텍스트의 비밀값 자동 탐지/삭제를 보장하지 않는다.
- 명시적 `--key-file`이 우선이고, 생략했을 때만 `TYPESAFE_API_KEY`를 사용한다. 잘못된 key-file에서 환경변수로 자동 전환하지 않는다. 실제 키를 CLI 인자에 직접 넣지 않는다.
- key-file은 현재 uid 소유의 일반 파일, 정확히 mode `0600`, 최대 8192바이트여야 한다. 심볼릭 링크는 거절하고 열린 파일의 소유자·권한·inode를 재검사한다. 읽기 전용 안전 확인에 실패하면 요청하지 않는다.
- `status`는 `key_present`만 출력한다. key-file은 내용 대신 메타데이터만 검사하므로 키 유효성/인증 성공을 의미하지 않는다.

## 결과와 경계

출력은 새 JSON 파일만 허용한다. `wx`로 **네트워크 호출 전에** 독점 생성하고 mode `0600`으로 저장한다. 기존 파일·링크를 덮어쓰지 않는다. 중단/디스크 오류 시 예약된 빈 파일이 남을 수 있으므로 다음 실행은 다른 새 경로를 사용한다. 불변은 이 도구가 재기록하지 않는다는 뜻이며 OS의 변경 불가 플래그는 아니다.

상태:

- `DRY_RUN`: 키 파일을 읽지 않고 네트워크도 호출하지 않는다. answers/usage/model_actual은 null이며 가짜 분류를 만들지 않는다.
- `CLASSIFIED`: 고정 모델과 엄격한 응답 스키마 검증에 통과한 advisory 응답이다. 시각/청각 QC PASS가 아니다.
- `UNAVAILABLE`: 키 없음, 안전하지 않은 키, HTTP/전송/타임아웃/응답 검증 오류. 정적 오류 코드만 기록하고 재시도하지 않는다.

정상/dry-run 종료코드 0, UNAVAILABLE 1, 입력·인자·출력 오류 2. 잘못된 입력에는 shadow 레코드를 만들지 않는다. 출력 실패 시 레코드 저장을 보장하지 않는다.

레코드에는 schema_version, question_version, UTC timestamp, 입력 SHA-256, 관찰 범위, 요청/실제 모델, 검증된 answers/usage/status와 다음 상수를 저장한다:

```json
{"advisory":true,"execution_authorized":false,"visual_qc":"NOT_ASSESSED_BY_JEV"}
```

원본 노트·키·HTTP 응답 본문·임의 오류 메시지는 저장하지 않는다. SHA는 원본 파일 바이트가 아니라 `JSON.stringify({qc_note,observation_scope})`의 UTF-8 바이트 기준이다. 생략된 범위는 `text_only`로 정규화한다. 검증 실패한 실제 모델명은 저장하지 않고 null로 둔다.

분류: `IDENTITY`, `ANATOMY`, `CONTACT_MOTION`, `CAMERA_SPACE`, `EFFECT`, `AUDIO`, `TIMING_ENDING`, `MULTIPLE`, `NO_ISSUE_REPORTED`, `INSUFFICIENT_EVIDENCE`. 단일 choice와 7개 독립 noul 신호를 받는다. 명시적으로 관찰된 문제만 대상이며 원인·보이지 않는 문제·PASS를 추론하지 않는다. 독립 신호와 choice가 의미적으로 일치하는지 자동 보증하지 않는다. `NO_ISSUE_REPORTED`도 해당 노트의 보고 내용일 뿐 승인/품질 증명이 아니다.

프롬프트 저작, 생성, 재시도, 승인, package 갱신은 절대 실행하지 않는다. 기존 시각·전체 재생·오디오 QC 및 Astra 저작 경계를 대체하지 않는다.

## 통신·검증

공식 계약: https://docs.typesafe.ai/api

- `POST https://api.typesafe.ai/v1/systemone`, Bearer 인증, 모델 `jev-1.13.0` 고정.
- 본문 `{model,state,questions}`만 전송. `state`는 허용된 두 필드만 복사한다.
- 호출 최대 1회, 전체 전송+본문 수신 제한 15초. redirect/retry/환경변수 endpoint override 없음. 별도 SDK·설치 없음(Node builtins만 사용).
- HTTP 본문 65536바이트 상한. 실제 모델 일치, 정확한 answer ID/type/enum, 모든 확률의 유한성·0~1·합계(오차 1e-6)·최빈 선택, confidence 범위, 안전한 비음수 정수 토큰 사용량을 검증한다. 알 수 없는 응답 필드도 거절한다.
- 제공자 응답 형식 변경은 UNAVAILABLE로 닫힌다. noul 확률과 choice는 advisory 신호이며 confidence를 QC 확실성으로 해석하지 않는다.

## 모의 테스트

```sh
JEV_QC_TEST_TMP=/absolute/session/tmp node --test scripts/jev-qc.test.mjs
```

테스트용 임시 디렉터리를 지정한다. 생략하면 OS tmp를 사용한다. 테스트는 합성 키와 모의 HTTP 전송만 사용하며 실제 API를 호출하지 않는다. CLI subprocess 테스트도 dry-run/키 없음 경로만 실행한다.
