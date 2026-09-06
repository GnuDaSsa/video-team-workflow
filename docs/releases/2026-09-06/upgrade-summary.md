# 영상팀 경량화·Seedance·Aside 업그레이드

## 반영 범위

검토 결과를 규칙 문서뿐 아니라 실행 helper, 입력/프롬프트 검사, 테스트,
배포 검증에 반영했다. 이번 작업에서 추가 에이전트·스케줄러·Runway 생성은 없다.
기존 제작 미디어, 제출 job, 프로젝트 prompt/attestation은 수정하지 않았다.

## 1. 불필요한 구조 정리

- `seedance-creative-prompt-team`과 설치 skill 내부 구형 통합 규칙을 활성 경로에서
  퇴역시킨다. 필요한 연출 판단은 같은 owner의 `prompt-review.md`로 통합했다.
- `videodirector/references/role-split.md`: 286 → 21행. 역할별 별도 팀/agent 대신
  단계별 결정·출력·다음 단계의 증거만 남겼다.
- Seedance 2.0 production 문서: 481 → 97행. 중복 큐·입력·복구 설명을 줄이고,
  exact-session 조작은 버전 공통 `aside-operator.md` 한 곳에서 소유한다.
- 예전 Chrome operator/scene advancement/Generate loop/rulebook 경로는 삭제로
  링크를 깨뜨리지 않고 **실행 규칙 없는 호환 포인터**로 바꿨다.
- 기본은 현재 대화·모델의 한 작업자다. Sol/Luna 모델표는 사용자가 별도
  dispatch를 구체적으로 승인했을 때만 쓰는 호환 기능이며 자동 교대 지시가 아니다.
- 숨은 image CLI의 App Server 새 작업 생성/참조용 자동 API 전환을 제거했다.
  `prepare-image-batch`는 현재 owner 내장 imagegen용 immutable hash 목록만
  만들고 generation/agent를 시작하지 않는다. 구형 image runner는 안전한
  중단 포인터이며 전용 image CLI 및 symlink는 archive로 퇴역한다.
- 과거 Editor 특정 작품 강제, Image Creator 외부 Fable bridge, Music Simple
  강제와 같은 오래된 live template는 현재 source 계약으로 교체한다.
- approved storyboard 관련 live 추가사항은 먼저 source에 보존했다. 잘라낸
  storyboard panel을 production sourceframe으로 승인하는 예외는 제거했다.

삭제가 아니라 로컬 archive로 옮겨 역사와 복구 가능성을 보존한다. 무관한
코딩 에이전트/음악 skill/사용자 프로세스는 정리 대상이 아니다.

## 2. Seedance 프롬프트 업그레이드

`장면 목적/시작-원인-반응-끝 상태 → render_scope → reference 기여 범위 →
결정된 카메라/물리 → 한국어 model 문장 → 반례 검토 → 현행 attestation`

신규 검출:
- “3/4 추적 또는 정면 고정”처럼 결정하지 않은 카메라.
- drone_only의 소매/머리카락 반응, human_only의 긍정형 드론 행동.
- 입력 모드/첨부 지시/파일명/`을(를)` 같은 컴파일 찌꺼기.
- 기존 schema 검사와 결합해 scene ID, cut 소유권, scene별 token, camera,
  edit-out 및 명시된 multi-shot 구조를 검증한다.

의도적인 “추적하다 멈추며 고정”은 허용하고, 모든 장면을 단일 동작으로
획일화하지 않는다. 금지할 entity를 부정문으로 언급하는 것과 실제 등장시키는
것도 구분한다. 검출은 관찰된 회귀에 한정되며 의미 전체를 증명하는 AI critic은 아니다.

`settings-verify`는 과거 ATTESTED 문자열만 믿지 않고 **현재 pack validator +
현재 duration lock + hash + 선택 모델**을 다시 검사한다. 이번 source/live
불일치가 과거 attestation을 통해 우회되지 않게 했다.

## 3. Aside 구체적 실행

1. **동일 프로젝트의 기존 세션 확인** → 기존 targetId/Generate session URL을
   프로젝트 binding으로 고정. 없거나 애매하면 임의 탭을 고르지 않는다.
2. **매 DOM 작업 전에 재검사** → 탭 목록에서 exact session 1개, target 일치,
   attach 후 URL, 실제 DOM callback 안 location을 다시 확인한다.
3. **등록 reference만 순서대로 첨부** → visible selector + 같은 Aside native
   chooser. 확대 thumbnail로 identity/순서/기여 범위를 확인한다.
4. **prompt 한 번 삽입** → bound project 안의 UTF-8 NFC txt, 유일한 visible
   Lexical editor, 삽입 직전 빈 상태, 삽입 뒤 normalized content/hash 일치.
5. **설정·중복 제출 확인 후 한 번 Generate** → 새로운 matching card로만 접수
   확정. timeout이나 card 부재는 재클릭 사유가 아니다.
6. **queue-cycle** → 실제 board 상태를 기록하고 필요한 경우 같은 turn의
   foreground wait. 결과를 받고 board를 다시 읽어 wake를 소비한다.
7. **download→ffprobe→registry→QC** → card만 보고 완료라 하지 않는다.

`aside repl`만 사용한다. bare `aside` / `aside exec`는 browser agent를 시작하므로
사용하지 않는다. AppleScript front tab 기반 DOM 제어와 hidden file input/image
clipboard 명령을 없앴다. Native key helper는 exact bound active tab, focused
Aside window, macOS frontmost, IME를 확인한다. OS focus는 사용자 동시 조작과
원자적으로 잠글 수 없으므로 실제 chooser 전후 관찰도 필수다.

실제 CLI에서 REPL global `URL`이 없다는 점을 발견했다. REPL에서는 정확한
허용 base/query만 파싱하고 browser DOM 내부에서 다시 URL을 검사한다. 실제
same-tab bind/title/host 읽기가 통과했으며 상세 원인과 검증은 별도 evidence에 있다.

회색 Generate는 **누를 수 없음**이지 자동으로 **queue full**은 아니다. 참조/
설정 오류와 실제 active-card 포화를 구별하며, 빈 queue에서 무의미한 15분 대기를
걸지 않는다. 기존 색상 우선 판단은 유지하되 카드·오류·설정 검사를 생략하지 않는다.

### Seedance 2.5 모드 차이

Edit는 입력 영상의 길이·비율을 상속한다. 없는 시간 컨트롤을 찾지 않는다.
`--duration-source input-video --source-video <등록 승인 영상>`으로 source hash,
ffprobe, runtime lock을 검증하고 `visible_duration_sec: null`을 기록한다.
입력 1프레임 이내 metadata 반올림만 허용한다. Extend 출력은 새로 생성된 구간이다.
Reference/Keyframe의 설정 노출과 동일하다고 가정하지 않는다.
[공식 Runway 설명](https://help.runwayml.com/hc/en-us/articles/53542207042323-Creating-with-Seedance-2-5)을
2026-09-06 확인했다. 타임스탬프는 대략적 연출 시간이며 프레임 정확도는 편집에서 맞춘다.

## 4. 입력·배포 증거 강화

- Music LOCKED 문자열 대신 지정된 등록 locked audio, 실파일/hash,
  duration/codec 증거를 요구한다.
- Planner 빈 `{}`나 DONE 문자열 대신 비어 있지 않은 고유 block/cut 구조를 요구한다.
- v4 상태 조회로 media cleanup이 실행되지 않게 했다.
- `--preflight`는 적용 안전성, `--check`는 source/live 해시와 퇴역 경로의 엄격
  일치 검사다. 설치 파일 하나가 달라도 성공으로 보고하지 않는다.
- 이번 릴리스의 관리 파일은 66개다. 지정 범위만 교체하고, 알 수 없는 live
  skill 파일은 자동 삭제하지 않으며, 배포 중 실패하면 이전 파일을 복구한다.
- 기존 untracked v4 dependency들을 검토·검증한 범위에서 함께 버전 관리한다.
  관계없는 이전 계약/기억 변경은 별도로 남긴다.

## 5. 검증 결과와 한계

- 자동 테스트 101개 통과: emitted JS wrong-tab/duplicate/session drift, URL 없는
  REPL, transport 오류, project 교차, prompt good/bad, 입력 gate, queue,
  source/live drift, rollback 및 기존 2.0/2.5 회귀.
- 실제 Aside **읽기 전용** smoke 통과. Upload/Generate/유료 generation은 하지 않았다.
- 기존 shelf 28개 읽기 전용 감사: 28개 모두 현행 재작성 필요. 카메라 미결정 28,
  drone-only 인간 동작 혼입 14, human-only 드론 긍정 동작 혼입 14를 검출했다.
  원본은 변경하지 않았다. 자동 재승인/재제출하지 않는다.
- 실제 새 영상 A/B 생성·전체 재생·CapCut export QA는 미실시다. 생성 승인율이나
  사용 가능 영상 초수가 좋아졌다고 주장하지 않는다.

## 다음 제작에서 측정할 것

첫 생성 승인율, 원인별 재시도 수, 사용 가능 초/생성 초, identity FAIL,
실제 채택 cut 수를 작은 동조건 A/B로 기록한다. 현재 수정은 **운영 오류와
명백한 프롬프트 모순을 막는 업그레이드**이며 미디어 품질 개선의 실증은 다음 제작에서 한다.
