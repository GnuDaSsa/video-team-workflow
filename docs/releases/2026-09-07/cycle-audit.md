# 영상팀 실증 사이클 감사 및 개선

## 판정과 증거 범위

**운영 경로 개선 PASS / 영상 재생 품질과 예약 첫 실행 증거는 별도 미검증.**

두 작업은 같은 Runway 보드에서 생성 완료 및 Download 노출을 확인했다. 브라우저 메타데이터는 각각 15.069002초, 1280×720이다. 프로젝트 등록부에는 실제 영상 파일이 아직 없었다. UI 완료를 로컬 파일·ffprobe·재생 QC 완료로 확대 해석하지 않았다.

사용자는 예약 사이클 완료를 보고했지만 감사에서는 native 자동화 ID와 등록·첫 실행 receipt를 확보하지 못했다. 이는 **증거 인계 누락**이며 예약이 없다는 판정이 아니다. 중복 예약을 만들지 않았다. 보완 확인을 위해 Codex 앱의 예약 UI를 읽으려 했으나 Computer Use가 해당 앱 접근을 안전상 거부했다. 이를 다른 기술로 우회하지 않았다. native 예약 도구로 조회하려면 정확한 예약 ID가 필요하다.

## 발견 → 수정

| 우선순위 | 문제와 원인 | 반영 및 확인 |
|---|---|---|
| 높음 | 예약 요청에도 queue-cycle이 전경 sleep을 무조건 시작 | hash-bound continuation_mode 저장. 예약 선택 시 단발 기록 후 반환, 직접 queue-wait도 거부. 실제 프로젝트 NO_WAIT 검증 |
| 높음 | 제안 카드·등록·첫 실행을 모두 ‘감시 중’으로 부를 위험 | native 도구만 예약 생성. 특정 최초 승인, 기존 예약 확인, ID·주기·대상·등록 receipt·첫 실행 증거 분리. 근거 없는 ACTIVE/실행 주장 탐지 |
| 높음 | 완료 카드가 있어도 state/manifest/lane은 In queue, QC는 옛 native blocker | queue-doctor 교차 감사. 실제 불일치 4건 탐지 후 정정하여 0건 |
| 중간 | may_stop=true만 쓰면 활성 큐도 종료 가능 | 정상 terminal·증거 있는 interruption·예약 checkpoint를 구분. 살아 있는 전경 wait와 조작된 종료 플래그 반례 테스트 |
| 중간 | 짧은 locator timeout이나 image decode를 업로드·화면 완료로 오인 | 같은 슬롯 재관찰, 재업로드 금지, decode와 실제 overlay 표시 모두 확인하도록 operator 지침 보완 |
| 중간 | 동일 STYLE LOCK 접두사 파일명이 영상 식별자로 쓰일 위험 | 카드→block lineage/provider ID를 먼저 확보. 로컬 fingerprint를 provider UUID로 표시 금지 |

## 유지할 것과 정리한 것

- **2.0의 서로 다른 두 큐 유지·빈 슬롯 우선 보충은 유지.** 실제 두 카드 동시 접수를 확인했다. 1개 fallback은 명시적 capacity toast에만 허용한다.
- **Astra 프롬프트 / Luna 실행·QC 선호는 유지.** 모델 표는 현재 대화가 실제로 바뀌었다는 증거가 아니다. Luna/Terra/Astra 환경값에서 같은 큐 판정이 나오는 테스트는 실제 모델 UI A/B와 구분한다.
- **한 owner와 한 Aside 탭은 유지.** 웹은 exact-session aside repl, native chooser만 승인된 접근성 보조. bare aside/exec의 새 agent 생성 경계도 유지한다.
- entrypoint에 반복되던 상세 전경 대기 강제 문구를 줄이고 production 문서로 통합했다. 새 agent, daemon, scheduler backend는 추가하지 않았다.
- 활성 상태의 오래된 native blocker와 pre-character-lock 초안 표시를 정리했다. 이전 실패 증거와 사용자 미디어는 삭제하지 않았다.

## 프롬프팅 점검

두 블록은 각각 세 개의 인과 장면이다. 공유 scene/action 참조는 0개, 필요한 공통 identity 참조는 2개이며 최종 한글 prompt는 각각 1,333/1,356자였다. 다음은 보존했다.

- 인물시트의 얼굴·앞 의상·뒤 실루엣 역할 결속과 스튜디오 시트의 장면 유입 방지
- 손 근접 숏의 crop lock, 우산과 손의 좌우 위치, 접촉 뒤 반응
- 숏별 camera와 diegetic audio, 2D 선·색면의 일관성
- 같은 owner의 반례 검토와 attestation, 제출된 prompt의 불변성

발견된 문제는 창작 문장을 무조건 줄여야 한다는 것이 아니라 **최신 pack과 오래된 manifest의 장면 시작 상태 차이**였다. manifest를 현재 attested scene_plan에 맞췄다. 실제 출력의 손·우산 관통, identity drift, line boiling, 컷 타이밍을 검사하기 전에는 새로운 광범위 금지문을 추가하지 않았다.

후속 영상 QC에서는 손 접촉 전후, 우산 접기 구조, 얼굴·카디건 밑단 지속성, 세 숏의 실제 컷점, 첫/끝 불안정 프레임과 음향을 검사해야 한다. 브라우저 영상 길이 두 개의 합은 정확히 30.000초가 아니므로 최종 30초 편집은 오디오와 핸들에 맞춰 별도 검증한다. 음악의 fresh listening도 미확인 상태를 유지했다.

## 정상 경로

Astra 저작·검수 → 불변 pack → 같은 owner Aside 입력·fresh preflight → 두 큐 접수 → 예약 점검 선택 저장 → 최초 승인된 native 예약 하나 → 매 실행 단발 확인·무변화 종료 → 완료 조건 충족 시 해당 예약 중지·다음 작업 인계 → 실제 다운로드·registry·재생 QC → 편집·패키지.

전경 대기는 사용자가 고른 경우의 별도 경로다. 예약 선택·등록·첫 실행의 증거를 구분하며, 로컬 파일이 scheduler 역할을 하지 않는다.

## 검증과 남은 한계

- 전체 unit test 136개 PASS. 신규 scheduled·진단·종료 회귀 13개.
- Python compile, 배포 스크립트 문법, git diff check, strict 66-file source/live parity.
- 실제 프로젝트: 예약 선택 → 중단 wake 소비 → NO_WAIT → 직접 wait 거부 → 상태 불일치 정정.
- 이번 감사에서 새 agent·예약·브라우저 owner·Generate·계정 변경 없음. 기존 출력 보존.
- 미검증: native 예약 ID·첫 실행 receipt, 실제 모델별 브라우저 A/B, 다운로드 ffprobe, 전체 재생 QC, CapCut 30초 export.
