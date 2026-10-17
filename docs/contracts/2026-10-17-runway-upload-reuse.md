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
