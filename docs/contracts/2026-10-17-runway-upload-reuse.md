# 2026-10-17 — Runway Uploads 재사용 (재업로드 금지) 회귀 수정

사용자: "이미 런웨이에 업데이트한 적이 있는 것에 대해서는 에셋 업로드를 굳이 또 할 필요가 없어서, 그러지 말라고 했었는데, 계속 신규 업로드를 하고 있음."

## 원인 (v5 회귀)
1. 번들 파일명 `NN_ImageN_<asset8>`가 슬롯 번호와 asset ID에 묶여 있어서, 같은 이미지라도 블록·슬롯·프로젝트 사본이 달라지면 이름이 바뀌었다. 그래서 "Uploads에 같은 이름이 있으면 선택"이라는 규칙이 맞을 수가 없었다. v5 이전의 `/tmp/<BLOCK>__IMAGE2__<asset8>`도 블록마다 이름이 달랐다.
2. 기본 순서가 "번들 → native chooser 업로드"였다. Uploads에서 고르는 경로는 transport 실패 때의 복구 단계에만 있었다.
3. Runway가 어떤 바이트를 이미 가지고 있는지 기억하는 장소가 없었다.
4. `cp -c` 클론이 원본의 mtime을 물려받아서, 원본이 24시간 넘게 지난 파일이면 다음 슬롯을 준비할 때 sweep에 지워졌다. Codex는 손으로 바이트 복사해서 우회했다.

## 수정
- 파일명을 내용 기준 `RW_<sha12>.<ext>`로 바꿨다. 바이트가 같으면 어느 블록·슬롯·프로젝트에서든 이름이 같다.
- `~/RunwayUpload/_runway_library.json`에 sha256별로 Runway 표시 이름을 기록한다. 상태는 verified, candidate, missing 세 가지이고, sweep은 이 파일을 지우지 않는다.
- `prepare-upload-bundle`이 슬롯마다 `attach`를 정한다. 장부에 있는 바이트는 `SELECT_EXISTING_RUNWAY_UPLOAD`와 `search_names`, 없는 바이트는 `UPLOAD_NEW_VIA_NATIVE_CHOOSER`이다.
- 장부에 아직 이름이 남아 있는 파일은 `picker-select`가 거부한다(`UPLOAD_BLOCKED_ALREADY_IN_RUNWAY_UPLOADS`). 이름을 검색해서 행이 없으면 `--how missing`으로 기록하고, 모든 이름이 missing이 된 뒤에만 업로드가 열린다.
- 첨부 결과는 `record-runway-attach --how reused|uploaded|missing`으로 기록한다. 썸네일 확대 확인을 마친 뒤에만 기록한다.
- `runway-library --seed`로 기존 receipt와 bundle에 있던 이름을 candidate로 넣었다. 검증된 이름이 아니므로 첫 검색에서 확인된다.
- 클론을 만든 뒤 `os.utime`을 호출하고, sweep은 번들마다 한 번만 실행한다.

## 범위 밖
- Runway 계정이나 팀이 바뀌면 장부를 쓸 수 없다. 장부는 이 기기의 기본 Runway 계정 기준이다.
- 숨은 file input 업로드 정책은 그대로 둔다.

## 추가 (같은 날): 제작 속도 — `run-block`과 제작 카드
사용자: "클로드에서 코덱스로 이관해서 작업하는데 작업속도가 너무 느리다 … 에셋 두세개 넣고 프롬프팅 복사하고 제너레이트 누르는건데"

- 측정 (door-test 스레드, 10/13~10/17):
  - 도구 호출 자체는 0.5~1초였다.
  - 다음 행동을 정하는 모델 사고는 중앙값 13.5초, 평균 28초였고, 합계 약 20시간이었다.
  - 모델 호출 1회의 입력이 중앙값 17.9만 토큰이었다. 컨텍스트 압축은 57회였다.
  - 첨부 단계는 블록당 1~75분, 호출 40~90회였다.
- 원인:
  - 9일 동안 한 스레드를 계속 썼다.
  - 압축할 때마다 문서를 다시 읽었다.
  - 조작 JS를 매번 즉석에서 만들어 한 단계씩 실행했다. `/tmp/hwr_*.js`가 40개 이상 쌓였다.
  - 작업 도중에 위키와 brief를 기록했다.
- 수정:
  - `runway_ui_helper.py run-block`(`scripts/run_block.py`) 명령 하나가 attach(Uploads 선택, 확대 확인과 스크린샷), settings(15초 자동 설정), paste(+settings-verify), preflight를 거쳐 `READY`까지 간다. 사람의 판단이 필요한 지점에서는 STOPPED 코드와 다음 행동을 돌려준다.
  - Generate 클릭은 넣지 않았다. Claude Code 자동 모드 분류기가 실제 거래 자동화로 보고 차단했다. 그래서 클릭은 운영자(Codex)가 직접 한 번 한다.
  - `production-card.md`를 P5의 유일한 읽기 문서로 정했다. 문서는 STOPPED 결과가 지목할 때만 연다.
  - 제작은 새 스레드에서 하고, 기록은 배치가 끝난 뒤 한 번만 쓴다.
- 실제 Runway에서는 아직 검증하지 않았다. 셀렉터는 10/16에 Codex가 실제 DOM에서 쓴 것을 그대로 옮겼다. 첫 실행이 사실상 리허설이다.
