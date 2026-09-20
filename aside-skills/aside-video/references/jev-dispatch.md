# Jev 분배기와 Seedance 빠른 입력

## 역할: 현재 실행자 + Jev 다음 단계 + Astra 저작

- 사용자가 Luna로 시작하면 Luna가 실행자로 남는다. 실행 모델은 항상 `inherit_session`; 전역 모델/category를 바꾸지 않는다.
- 노래·이미지·Seedance 프롬프트 작성과 의미 수정은 Astra만 한다. Jev는 저작 필요 단계를 분배하지만 문구를 쓰거나 프롬프트를 줄이지 않는다.
- Jev는 다음 행동의 **추천**만 반환한다. 현재 세션이 기존 도구와 승인 범위로 실행한다. `advisory:true`, `execution_authorized:false`는 유지하며 이것이 매 클릭마다 사용자 재승인을 요구한다는 뜻은 아니다.
- 빠른 경로는 역할 판단의 큰 모델 왕복과 불필요한 도구 왕복을 줄인다. Jev API 호출 시간, 브라우저 처리 시간, 전체 사용자 대기 시간을 구분한다. 매 snapshot에 Jev를 덧붙이면 오히려 느려질 수 있다.

## 실행 순서

1. `author-executor.md`에 따라 현재 session context를 한 번 읽는다. 브리프·ordered reference를 확정하고 재사용 가능한 bundle/공용 asset 기록을 조회한다. 동일 경로를 재탐색하지 않는다.
2. 저작이 필요하면 `stage=music_prompt|image_prompt|seedance_prompt`로 분배한다. 저작 request가 진행 중이면 같은 request를 다시 만들거나 author를 중복 호출하지 않는다. `AUTHOR_ASTRA` 결과는 `harness request → 실제 native author → seal → submission prepare/verify`로 연결한다. 반환 route의 category를 쓰며 이름만으로 Astra라고 추정하지 않는다. 실제 현재 모델이 Astra면 direct 저작, 아니면 bounded Astra author를 호출한다. native subagent가 없는 child는 기존 parent-mediated 인계를 사용한다.
3. **Astra가 별도 author로 작업 중이면 `run_in_background=true`로 두고, 현재 실행자는 독립적인 에셋 검색·참조 첨부·설정 확인을 진행한다.** 최종 문구가 필요한 입력 시점에만 결과를 기다린다. 프롬프트 결과에 따라 참조 선택이 바뀌는 작업은 독립으로 간주하지 않는다. author에게 브라우저 탭을 넘기지 않는다.
4. 입력 준비 중 복수의 다음 단계나 애매한 상태가 있으면 `computer_use` 상태를 Jev에 전달한다. 확정된 하나의 단순 작업은 바로 실행한다. `SEARCH_ASSET`은 해시로 결속된 실제 이름으로 검색, `SELECT_EXISTING`은 fresh UI의 유일하게 식별된 후보만, `UPLOAD_FIRST`는 검색/범위 재확인 후 기존 에셋이 없고 검증된 로컬 파일이 있을 때만 후보가 될 수 있다.
5. `FILL_PROMPT`는 `submission verify`가 통과한 payload와 정확한 reference 순서·mode가 준비된 경우에만 후보로 넣는다. 문구를 고쳐야 하면 computer_use 후보를 늘리지 말고 대응하는 author stage로 돌아간다. 입력된 원문이 이미 같으면 채우지 않는다.
6. Jev가 고른 행동에 해당하는 로컬 검증 인수만 아래 빠른 실행기에 넘긴다. Jev 응답에는 파일 경로·selector·ref·prompt가 없다. 셋 중 어느 것도 Jev에게 생성시키지 않는다. 행동을 마친 fresh snapshot에서 다음 상태를 갱신한다. 모호함/timeout은 먼저 재관찰하며 같은 업로드/클릭을 자동 재시도하지 않는다.
7. Generate는 분배기와 빠른 실행기 바깥에 있다. 기존 권한/비용/수량/모드/프롬프트/참조 gate와 단일 제출 기록을 그대로 적용한다.

## Jev 입력·출력

```sh
node scripts/jev-dispatch.mjs next --root <same-task-root> --input <state.json> --context <current-context.json>
```

입력은 정확히 세 필드다:

```json
{
  "stage": "computer_use",
  "blockers": "검증된 프롬프트가 있고 참조도 적용되었다. 영상 참조 모드이며 입력창만 아직 비어 있다.",
  "ready_actions": ["FILL_PROMPT", "VERIFY_INPUTS", "REVIEW"]
}
```

- blockers는 실행자가 실제 확인한 익명화 상태 요약 1500자 이하. 전체 snapshot·대화·대본·파일명·원본 이미지·고객명·계정·비밀을 전송하지 않는다. context는 로컬 라우팅에만 쓰며 API로 보내지 않는다.
- ready_actions는 로컬 근거로 **실행 가능성이 확인된 후보**만 포함하고 REVIEW는 항상 포함한다. Jev 추천 뒤에도 현재 조건을 재검사한다. 컴퓨터 단계에는 AUTHOR_ASTRA를 섞지 않는다. 저작 단계에는 AUTHOR_ASTRA와 WAIT/REOBSERVE/REVIEW만 허용한다.
- 허용값: AUTHOR_ASTRA, SEARCH_ASSET, SELECT_EXISTING, UPLOAD_FIRST, FILL_PROMPT, VERIFY_INPUTS, WAIT, REOBSERVE, REVIEW. Generate/제출/승인/결제/재생성/모델 변경은 없다.
- 같은 작업 root당 최대 3 API 시도. 같은 성공 입력은 캐시 재사용하며 캐시 결과의 역할 경로는 **현재** context로 다시 계산한다. 실패·타임아웃도 시도에 포함하며 자동 재시도하지 않는다. `.jev-dispatch`를 삭제하거나 root를 바꿔 한도를 우회하지 않는다.
- CLASSIFIED와 CACHED를 구분한다. latency_ms는 해당 API 시도의 시간이지 전체 제작 속도가 아니다. 한도/오류/미연결이면 현재 실행자의 정상 절차로 이어가며 업무 전체를 멈추거나 한도를 늘리지 않는다.
- 기존 `jev-seedance diagnose`와 같은 안내문을 이중 호출하지 않는다. dispatch의 상태 판단으로 해결된 안내문은 별도 분류를 생략한다. QC runner의 별도 범위는 유지한다.

## 짧은 브라우저 실행기

`scripts/runway-fastlane.js`는 현재 REPL에서 실행하는 로컬 함수다. 별도 브라우저/daemon/API 자동화가 아니며 모델과 native author를 직접 호출하지 않는다.

```js
const fastStep = new Function('return (' + await fs.readFile(
  '<accountRoot>/skills/user/aside-video/scripts/runway-fastlane.js', 'utf8'
) + ')')();
// job은 아래 gate를 통과한 실제 로컬 데이터로 구성한다. Jev 응답 전체를 job으로 쓰지 않는다.
console.log(await fastStep({page, snapshot, log:console.log}, job));
```

공통 `job.expected_url`은 **fresh snapshot 헤더**에서 실제 관측한 정확한 URL이다. `page.url()`은 Runway가 sessionId를 발급한 뒤에도 초기 newSession 주소를 캐시할 수 있으므로 단독 근거로 쓰지 않는다. helper도 fresh snapshot URL로 세션을 대조한다. 모든 행동은 fresh snapshot의 Video/Reference checked 상태와 관측된 ref로만 실행한다. snapshot 후 refs를 다시 얻으며 action마다 diff를 출력한다. 지원하지 않는 UI면 보수적으로 반환하고 기존 실행자가 관측 경로를 처리한다.

| action | 로컬 인수와 동작 |
|---|---|
| SEARCH_ASSET | asset_name. 관측된 Reference 버튼 열기 → 새 snapshot → 관측된 Search에 이름 fill → snapshot을 한 호출로 수행. SEARCH_OBSERVED는 검색어 수용이며 결과 로딩 완료/파일 부재 판정이 아니다. |
| SELECT_EXISTING | mode_gate, binding_confirmed, candidate:{role,name}, expected_count. 공용 hash/ID 기록과 live 후보를 대조한 뒤에만 binding_confirmed=true. 모호한 동명 후보는 금지. 정확한 한 후보 double-click 후 Image1.. 수용 확인. 이미 필요한 참조 수가 있으면 다시 toggle하지 않는다. |
| FILL_PROMPT | Asset selector 등 dialog가 열려 있으면 입력하지 않고 `BLOCKING_DIALOG_CLOSE_AND_REOBSERVE`로 반환한다. 관측된 닫기 control로 닫고 새 snapshot에서 해제된 것을 확인한다. mode_gate와 submission={file:<absolute payload path>,sha256:<독립 수락 hash>} 및 expected_previous_prompt=직전 관측 원문을 쓴다. 신뢰된 실행 환경의 verifySubmission(file,hash)가 실제 submission.mjs verify를 호출해야 하며 job.verified_submission은 무시한다. adapter가 없는 REPL에서는 이 fastlane 입력만 HOLD하고, 현재 실행자가 기존 submission CLI 재검증 후 원문 직접 입력 절차를 사용한다. 캐시 객체를 돌려주는 가짜 callback을 만들지 않는다. payload.prompt를 한 번 fill하고 DOM 수용 원문과 정확 비교한다. 참조 수 일치와 identity/순서 검수는 별개다. |
| UPLOAD_FIRST | mode_gate, search_absence_verified, files_verified, expected_existing_count, observed_file_input_selector, files. 같은 live UI에서 **직접 확인한** 유일한 input[type=file] selector와 검증된 upload-files.json 배열만 전달한다. 숨은 input을 추측하지 않는다. chooser-only UI이면 기존 절차로 처리한다. |
| VERIFY_INPUTS / REOBSERVE | 관측만. 전체 preflight 또는 최종 승인이 아니다. |

`mode_gate={passed:true,observed_at:<actual ISO>}`는 30초 이내의 실제 `check.mjs mode` 성공과 live 관측으로만 만든다. Jev 답변으로 만들지 않는다. helper의 mode 검사도 기존 `check.mjs` gate를 제거하지 않는다.

UPLOAD_FIRST에는 `claimUpload` 콜백이 추가로 필수다. **해당 작업·정확한 탭·ordered 파일 hash에 결속된 고정 경로**에 `fs.writeFile(...,{flag:'wx',mode:0o600})`으로 시도 기록을 독점 생성한 경우에만 true를 반환한다. 기존 기록이 있으면 false다. 호출마다 새 UUID/시간 파일을 만들어 우회하지 않는다. 기록은 실제 첨부 직전에 남기고 timeout/실패에도 자동 삭제하지 않는다. 이미 시도된 업로드는 fresh UI·공용 asset 기록을 확인한 뒤 실행자가 복구한다. `UPLOAD_DISPATCHED_UNCONFIRMED`는 전달 시도만 뜻하며 실제 업로드 성공·순서/identity 확인은 후속 snapshot으로 별도 기록한다.

정상 동작은 짧게 묶고, 다음 행동이 새 상태 판단에 달리면 반환한다. 무한 while/sleep loop나 숨은 자동 Generate를 붙이지 않는다.
