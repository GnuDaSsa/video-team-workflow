---
name: jeongseon-video-typography
description: 정선 공모전/관광 MV에서 얻은 CapCut 타이포·전환·QC 운영 팁. Codex 영상팀이 관광/공모전/CapCut 편집을 할 때 적용.
---

# Jeongseon Video Typography & Edit Lessons

## 적용 상황

- 관광/지역/공공기관 공모전 영상
- CapCut 타임라인에서 장소명, 설명문, 챕터, 제목, 엔딩 문구를 다루는 작업
- 사용자가 “타이포가 별로”, “앱/스타트업 같다”, “겹친다”, “밋밋하다”, “CapCut에서 고쳐라”라고 지적한 경우

## 핵심 원칙

1. 타이포는 정보 디자인이다.
   - 예쁜 자막이 아니라, 관객이 지금 보는 장소/문화/감정/전환을 이해하게 해야 한다.
   - 관광지 이름만 던지지 말고, 한 줄 설명은 장면의 의미를 보태야 한다.

2. 관광/문화 라벨은 앱 UI처럼 보이면 실패다.
   - `AI 여행 루트`, `추천 코스`, `스팟` 같은 서비스/앱 느낌 카피를 피한다.
   - 오래된 문화/장소를 다룰 때는 locator feel, 오래된 지도/문화재 표지/기록물 같은 기운이 더 맞다.

3. 빠른 음악은 효과로만 해결하지 않는다.
   - 비트가 빠른데 화면이 느리면 플래시/글리치/자막 깜빡임을 늘리는 게 아니라, 목적 있는 새 컷과 액션을 추가한다.
   - 전환/타이포는 리듬 악센트일 뿐, 부족한 컷 설계를 숨기는 장식이 아니다.

4. 모든 컷에는 이유가 있어야 한다.
   - action, information, emotion, rhythm, transition, motif payoff 중 하나가 있어야 한다.
   - 비슷한 풍경/발/반사/손 클로즈업 반복은 파일이 달라도 시청 경험상 중복이면 실패다.

## CapCut 타이포 설계 규칙

### 레이어 구조

- 긴 `제목\n설명` 한 클립에 몰아넣지 않는다.
- 위험한 관광 locator는 제목 레이어와 설명 레이어를 분리한다.
  - Title track: 장소명/핵심명사
  - Description track: 짧은 설명/감정/맥락
- 분리하면 폰트, 크기, Y 위치, stroke, shadow, fade를 따로 제어할 수 있다.

### 위치

- 장면마다 피사체 얼굴/눈/핵심 동작/시선 흐름을 먼저 찾는다.
- 타이포는 남는 공간에 놓는다: 하늘, 벽, 바닥, 물결, 빈 도로, 어두운 영역.
- 인물 얼굴, 주 동작, 랜드마크 핵심부를 가리면 실패다.
- 왼쪽 정렬은 JSON 수치가 아니라 실제 CapCut 프리뷰에서 첫 글자 기준으로 검증한다.
- CapCut에서 alignment 값이 기대와 다르게 렌더될 수 있으므로 실제 UI/프리뷰가 기준이다.

### 폰트/톤

- 한국어 관광/문화 라벨은 기본 산세리프만 반복하면 현대 앱처럼 보일 수 있다.
- 필요 시 다음 계열을 검토한다:
  - 문화/유산/장소명: 명조/부리/바탕 계열, 경기천년제목, MaruBuri, Noto Serif CJK 등
  - 설명문: 더 차분한 고딕/본문체
  - 제목/챕터: 장면별 성격에 맞춘 굵기와 색
- 사용자가 추가한 폰트가 있으면 `~/Library/Fonts/CapCutCustom/`를 먼저 확인한다.

### 색/그림자/stroke

- 한 가지 노란/흰 자막 스타일을 모든 장면에 재사용하지 않는다.
- 장면군별 팔레트를 설계한다.
  - 설경/하늘/케이블: cool white, ice blue, navy shadow
  - 시장/음식/거리: warm cream, earth, umber shadow
  - 사찰/문화재: stone, bronze, charcoal
  - 동굴/야간: cool stone, amber, blue-black
  - 강/물/숲: blue-green, soft dark teal
- 그림자는 단순 검정 기본값이 아니라 장면의 빛 방향과 재질에 맞춘다.
- Shadow/stroke는 실제 프리뷰로 확인한다. JSON에 값이 있어도 렌더에서 안 보이거나 너무 지저분할 수 있다.

## 애니메이션/전환

- 타이포는 무작정 깜빡이지 않는다.
- 장소명은 컷 시작 또는 0.1초 뒤에 들어오게 한다.
- 읽을 수 있는 hold가 필요하다. 0.5초 키워드 점멸은 대체로 실패다.
- 빠른 비트에서는 2~4프레임 pop/echo/짧은 snap-off 정도가 좋고, 긴 generic fade/glitch는 피한다.
- CapCut keyframe/animation은 JSON만 보지 말고 실제 UI에서 확인한다.
  - `⌥K`로 키프레임 패널 확인
  - 선택한 orange text clip과 프리뷰/인스펙터가 같은 클립인지 확인
  - 흰 diamond keyframe이 실제 text lane에 있는지 확인

## 실제 QC 기준

타이포 PASS 전 반드시 확인:

1. 모든 글자가 보이는가?
   - 첫 글자 누락도 FAIL.
   - 긴 한글 장소명/설명문이 잘리거나 wrap되어 사라지면 FAIL.

2. 겹침이 없는가?
   - 피사체/핵심동작/시선흐름/랜드마크/배경 대비와 충돌하면 FAIL.
   - title-desc 사이 breathing room이 부족하면 FAIL.

3. CapCut 실제 프리뷰인가?
   - JSON 검사, ffmpeg/Pillow 시뮬레이션, 잘린 스크린샷만으로 PASS 금지.
   - CapCut UI에서 scrub하고 full preview proof를 남긴다.

4. 정보가 장면과 맞는가?
   - 라벨이 해당 컷보다 먼저 뜨면 FAIL.
   - 정보가 장면을 설명하지 못하고 장식처럼 보이면 FAIL.

5. CapCut 편집 가능성이 유지되는가?
   - 사용자가 CapCut 수정을 요구한 경우 baked PNG/MP4 overlay만으로 대체하지 않는다.
   - 가능한 한 editable text layer를 유지한다.

## 정선 프로젝트에서 얻은 운영 팁

- 음악 lock 전에는 최종 cut plan을 확정하지 않는다.
- Suno가 짧은 13~29초 조각만 내면, 짧은 곡을 더 요청하지 말고 full arrangement를 만든 뒤 40~60초 구간을 잘라 쓴다.
- Raw PNG/JPG source frame은 최종/리뷰 타임라인 filler가 아니다. 반드시 I2V를 거친 클립만 메인 타임라인에 사용한다.
- Grok `PASS_DOWNLOAD`는 다운로드/매핑 확인일 뿐 visual QC가 아니다.
- 다운로드된 영상은 cut→post/download mapping을 보존한다.
- 공모전 제출/공개 업로드/개인정보 폼 제출은 명시 확인 전 금지.

## Codex 영상팀 역할별 적용

- Director: 공식 요강/루브릭 → 창작 우선순위 → 컷 이유 → 역할 브리프까지 먼저 잠근다.
- Music: 실제 오디오 파일과 ffprobe로 duration/codec 검증 전에는 music lock이라고 말하지 않는다.
- Visual: ChatGPT Image 2는 한 컷 한 이미지. Grok는 QC 통과한 이미지로만 I2V.
- Editor: CapCut editable text layer, 실제 UI 프리뷰, export/ffprobe까지 책임진다.
- QC: 다운로드/JSON/경로가 아니라 실제 시각 품질, 글자, 겹침, 박자, 최종 패키지를 독립 판정한다.

## 금지 패턴

- “JSON상 문제 없음”만 보고 타이포 PASS
- 동일한 노란/흰 subtitle identity를 관광 locator에 재활용
- 문화재/관광 라벨을 스타트업 앱 UI처럼 디자인
- 글자 확인 없이 contact sheet만 보고 완료 주장
- 효과/글리치/플래시로 느린 컷 설계를 덮기
- CapCut 작업 요구에 ffmpeg-only baked preview만 제출
