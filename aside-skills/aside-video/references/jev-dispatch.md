# 필요한 경우만 Jev / fastlane

## Jev

명확한 다음 행동은 실행자가 바로 한다. 복수 후보의 의미 판단이 실제로 막혔을 때만:

`jev-dispatch.mjs next --root <same task root> --input <state.json> --context <context.json>`

state는 `{stage,blockers,ready_actions}`만. blockers는 익명화한 실제 상태 1500자 이하, REVIEW는 항상 후보에 포함한다. stage=computer_use에는 AUTHOR_ASTRA를 섞지 않는다. 저작 stage 후보는 AUTHOR_ASTRA/WAIT/REOBSERVE/REVIEW만. 다른 허용 행동은 SEARCH_ASSET/SELECT_EXISTING/UPLOAD_FIRST/FILL_PROMPT/VERIFY_INPUTS다.

추천만 반환한다(advisory=true, execution_authorized=false). selector·경로·문구·Generate·승인·결제를 만들거나 실행하지 않는다. 동일 root당 3회 한도, 성공 캐시, 실패 자동 재시도 없음. 한도/장애는 현재 실행자가 처리하며 root/원장을 바꿔 우회하지 않는다. 같은 상태를 jev-seedance로 이중 분류하지 않는다. 전체 snapshot/대화/미디어/비밀은 보내지 않는다.

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
