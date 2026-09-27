# 입력 실행 라우팅 — 코드 / JEV / 현재 실행자

## 정상 경로: 기존 guarded helper를 바로 사용

이미 행동·대상·승인 원문이 확정됐으면 JEV나 큰 모델의 추가 판단 없이 기존
입력 helper로 관측→한 번 조작→검증을 묶는다. 이 문서를 매 컷마다 재독하거나
알고 있는 행동을 확인받으려고 router를 호출하지 않는다. 컴퓨터유즈는 유지한다.

창작/문구 수정, screenshot의 시각 해석, 새로운 복합 복구는 현재 실행자가
소유 단계로 돌아간다. 별도 모델/agent/browser owner를 자동 생성하지 않는다.

## 의미 분기: 기존 JEV dispatcher의 route

복수의 **이미 관측하고 실행 적격을 확인한 행동** 중 선택만 필요할 때 사용한다.
입력 파일은 기존 `{stage,blockers,ready_actions}` 그대로다. stage=computer_use,
blockers는 직접 확인하고 익명화한 상태 1500자 이하, REVIEW는 항상 포함한다.
경로/selector/프롬프트/미디어/전체 snapshot/대화/계정/비밀은 보내지 않는다.
외부 전송 전 현재 실행자가 최소화·익명화를 확인한다; 자동 익명화 기능은 아니다.

```bash
node <installed skill>/scripts/jev-dispatch.mjs route \
  --root <same task root> --input <anonymized-state.json> \
  --kind semantic --observed-at <actual-observation-ISO-time> \
  --jev-approval <actual-current-scope-user-approval-reference>
```

`--jev-approval`은 현재 작업 범위의 실제 JEV 사용 승인을 가리킨다. 키가 있다는
사실, 스킬 설치, 포괄적 자동화 선호는 승인이 아니다. 승인 없는 경우 현재
실행자가 직접 처리하며 매 컷마다 승인을 재요청하지 않는다. 실제 승인은 같은
범위에서 재사용할 수 있지만 파일/CLI 문자열이 승인을 만들어주지는 않는다.

코드에서 이미 결정된 행동을 전달해야 할 때만 `--kind routine --known-action
FILL_PROMPT`처럼 쓸 수 있다. 이 경로는 키·네트워크·JEV 원장을 만지지 않는다.
후보 하나+REVIEW라고 정답을 자동 확정하지 않는다. `--kind creative|visual`은
호출 없이 현재 실행자로 돌려보낸다. `next`는 기존 진단/호환용 저수준 명령이다.

| routing | 처리 |
|---|---|
| DIRECT | 기존 helper로 해당 행동. REOBSERVE면 읽기만 하고 상태를 새로 확인 |
| JEV_ADVISORY | 적격 후보 추천. 현재 실제 상태와 아래 기존 helper gate를 재검증한 뒤에만 처리 |
| OWNER | 현재 실행자가 판단. 다른 agent 생성·일상 작업 중단·무조건 API 재시도 아님 |

모델은 selector·경로·문구·Generate·승인·결제를 만들거나 실행하지 않는다.
출력은 항상 advisory=true, execution_authorized=false다. `confidence`와 선택
확률의 초기 triage 기준은 코드 `ROUTING_POLICY` 한 곳이 소유하며, 한국어 정확도나
안전 승인을 입증한 수치가 아니다. 관측이 오래됐거나 호출 중 만료되면 재관측한다.
낮은 확신·키 없음·장애·손상·한도는 owner로 돌아온다. 같은 root의 기존 3회
원장·성공 캐시를 재사용하며 자동 retry/한도 우회/root 변경은 없다. 동일 상황을
jev-seedance로 이중 분류하지 않는다. 운영상 새 동작을 발명해야 하면 JEV가 아니라
현재 실행자가 맡는다. 의미 추천과 실제 UI/QC 성공은 별도 증거다.

## 짧은 UI 묶음

runway-fastlane.js는 기존 REPL 함수다. `new Function('return (' + await fs.readFile(<실제 helper 경로>,'utf8') + ')')()`로 읽어 현재 page/snapshot/log를 전달한다. env 코드는 실행자가 신뢰하는 코드이며 job은 실제 검증한 데이터다.

| action | 필수 데이터 |
|---|---|
| SEARCH_ASSET | 실제 asset_name |
| SELECT_EXISTING | binding_confirmed, 유일 candidate={role,name}, expected_count |
| UPLOAD_FIRST | files_verified/search_absence_verified, 실제 file input, 검증 경로, expected_existing_count, durable claimUpload callback |
| FILL_PROMPT | submission={file:absolute payload path,sha256:수락 hash}, expected_previous_prompt, 실제 submission.mjs verify를 호출하는 verifySubmission callback |
| VERIFY_INPUTS / REOBSERVE | 현재 상태 관측만 |

공통 expected_url은 fresh snapshot URL이다. 첨부/입력은 fresh mode_gate와 Video/Reference 선택이 필요하다. 모달·다른 session·잘못된 순서·불확실 상태는 중지한다. 액션 뒤 snapshot/diff와 수용 원문을 확인한다. Generate는 이 helper의 기능이 아니다.

**현재 REPL에 실제 verifier adapter가 없으면 FILL helper는 사용하지 않는다.** 기존 CLI 재검증 후 원문 직접 입력을 사용한다. PASS 객체/가짜 callback으로 연결을 흉내 내지 않는다. 이 한계를 매 컷마다 다시 실험하지 않는다. 검색·선택 helper는 독립적으로 사용할 수 있다.
