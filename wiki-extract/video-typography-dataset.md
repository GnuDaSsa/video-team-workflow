---
title: Video Typography Dataset (rules + heuristics)
created: 2026-05-12
updated: 2026-05-13
type: dataset
status: active
scope: CapCut-first typography + MV/public/tourism
tags: [video, typography, capcut, subtitles, motion]
sources: []
---

# Video Typography Dataset

## 0) Hard constraints (standing rules)
- **CapCut Preview/Export is source of truth.** JSON values do not guarantee visible alignment.
- Avoid “default system font” vibes. Prefer deliberate Korean type choices.
- **Pro/paid fonts:** do not ship final masters with paid fonts unless user explicitly approves licensing.
- **Public/contest/tourism:** clarity, readability, and role separation > mood.
- **MV + public:** cut timing must follow music/beat/phrase; default 2.0–2.5s per cut unless music dictates otherwise.

## 1) Typography role system (mandatory separation)
Define and keep these as distinct layers (font/size/opacity/timing):
1. **TITLE (opening / chapter card):** biggest; 1–2 lines; short hold.
2. **LOCATION NOTE:** place name; mid-size; often corner-safe; may repeat.
3. **NARRATION/BODY:** calm font; unboxed/near-unboxed; never cover key action.
4. **DISCLOSURE/FOOTNOTE (AI-use / sources):** smallest; avoid competing with story.

## 2) Caption placement heuristics (Korean-first)
- If subject/action occupies lower third (dancers, walking feet, vehicles): move narration to **upper-left/upper-right** or side-safe area.
- Avoid horizon lines: do not place type on the horizon; place slightly above/below with contrast aid.
- For travel montage: prefer **corner-safe** placement, but ensure it’s not “museum caption tiny.”

## 3) Readability thresholds (practical)
- Phone-first: set a minimum x-height equivalent; if you must reduce size, reduce words first.
- Korean line breaking: avoid breaking particles/auxiliaries (은/는, 이/가, 을/를, -고, -서, -지만).
- Motion: if text moves, either (a) **hold** at endpoints, or (b) keep movement slow enough for reading.

## 4) Motion typography patterns (when to use)
- **Fluid / morphing:** MV hooks or emotional turns; risky for public info unless restrained.
- **Scrolling:** lists, routes, schedules; best for public/tourism data.
- **Dynamic layout (responsive blocks):** good when multiple roles must coexist; use strict hierarchy.

## 5) CapCut implementation rules
- Alignment: align by **visible glyph edge in preview**, not by equal X transform.
- Timing: when A→B phrase replacement happens at same position, give **B the same reading breath** before adding lower support line.
- QC pass: check first third of edit for jitter, 1-frame flashes, duplicate frames; trim unstable clip heads/tails.

## 6) Font selection logic (non-pro default)
- Goal: “cinematic, quiet, Korean-legible” without looking like default UI.
- Choose a **pair** (Display + Text):
  - Display: heavier Hangul, wider tracking tolerance.
  - Text: calmer, higher legibility at small sizes.
- If only system fonts available, simulate “non-default” via: weight, tracking, line-height, subtle stroke/shadow, and layout (still avoid the obvious default look).

## 7) Dataset links
- Hourly research notes (latest): [[video-typography/hourly/2026-05-13-01]]

---

## Update 2026-05-13 01KST — kinetic typography 리듬 규칙 + CapCut 운영 게이트 강화
- Latest note: [[video-typography/hourly/2026-05-13-01]]

### A) “호흡(진입-홀드-퇴장)” 우선 규칙(모션 총량을 줄여도 완성도를 올리는 방법)
- 모션 타이포의 실패 원인 1순위는 “기법 부족”이 아니라 **읽을 시간이 없는 타이밍 설계**다.
- 기본값:
  1) 진입(0.25–0.6s)  
  2) 홀드(0.6–1.2s, 공공/장문이면 더 길게)  
  3) 퇴장(0.2–0.5s)  
- 엔드포인트 홀드가 확보되지 않으면 “모션으로 해결”하지 말고:
  - 문장 축약 → 줄바꿈 재설계 → 크기/행간 조정 → 마지막에 모션(최후 수단) 순서로 해결.

### B) 관광/공공(시네마틱) 텍스트 전략: 본편 장문 금지 → 챕터/엔드 카드 회수(역할 분리)
- 배우/공간/미장센이 주연인 캠페인형 영상에서 장문 본문 자막은 화면 신뢰감을 떨어뜨리기 쉽다.
- 운영 기본값:
  - 본편: 장소 라벨/짧은 문장(1–6단어) 중심
  - 설명/근거/메시지: 챕터 카드/엔드 카드에서 회수(= “설명은 설명 컷에서”)

### C) CapCut Auto Captions = 납기 리스크(프로젝트 손상/Export 실패 포함)로 재정의
- 기본값: **격리 프로젝트(생성) → 정규화 → 메인 이식**
- Export/업데이트/템플릿 적용 시에는 반드시:
  - **샘플 구간(10–20초) 적용 → Export 결과까지 확인**(Preview만으로 통과 금지)

### D) Export 안정성 규칙(프로젝트/팀 공통)
- Export 경로/파일명은 ASCII로 통일(한글/특수문자 회피).
- “캡션 겹침/중복”은 Export 폴더 문제가 아니라 타임라인 레이어 문제이므로, Export 직전 트랙/중복을 점검한다.

### E) 9:16 안전영역 대응: 하단 고정 1개가 아니라 **ALT 자막 위치 프리셋 자산**
- 하단 unsafe(UI 오버레이) 전제를 기본으로 두고, 최소 3개 이상을 자산화:
  - upper-left / upper-right / mid-left / mid-right / side-block

---

## Update 2026-05-12 10KST — 신규 규칙/로직
- Latest note: [[video-typography/hourly/2026-05-12-10]]

### A) “자막 목적” 기반 분기(선택 로직)
- **Accessibility/정보전달(공공/공모전):** 고정 규격(폰트/크기/행간/대비) + 문장 축약 + 역할 분리(장소/본문/고지).
- **Rhythm/정서(MV):** 훅 단어만 강조(색/스케일) + 엔드포인트 홀드 + 음악 프레이즈에 맞춘 등장/퇴장.
- **Data/가이드(관광 정보/동선):** 스크롤/리스트/아이콘 병행 가능하나, 1컷 1정보 원칙 유지.

### B) 모션 타이포 엔드포인트 홀드(필수)
- 텍스트가 이동/스케일 변형될 경우: **모션(0.3–0.6s) → 정지(0.6–1.2s)** 최소 패턴을 기본값으로 둔다.
- ‘계속 움직이는 텍스트’는 시청자가 **버벅임/프레임 드랍**으로 인지하기 쉬우므로 금지.

### C) Auto-caption “정규화 패스”를 파이프라인에 고정
- 오토캡션 생성 직후, 반드시 다음을 통일:
  - 폰트 페어(타이틀/본문 분리)
  - 크기/행간/자간
  - 줄바꿈 규칙(조사/어미 분리 금지)
  - 강조(색/굵기) 1개/문장 원칙

---

## Update 2026-05-12 11KST — CapCut 템플릿/오토캡션 안정성 규칙
- Latest note: [[video-typography/hourly/2026-05-12-11]]

### A) “샘플 Export 게이트” (업데이트/템플릿 적용 시 필수)
- CapCut 업데이트 직후 또는 새 caption template/프리셋을 적용할 때:
  1) 8–12초 샘플 구간에 적용
  2) **Preview에서 위치/겹침/점프 유무 확인**
  3) **Export 결과(압축/리사이즈 포함)까지 확인**
- 이유: 프리셋/템플릿 동작은 업데이트로 회귀할 수 있고, “Preview OK, Export FAIL”이 실무에서 치명적.

### B) 오토캡션 템플릿 = “점프 리스크” 기본값
- 오토캡션 템플릿에서 캡션이 산개/점프하는 경우가 반복됨(커뮤니티 사례 다수).
- 공공/관광/공모전 본문 내레이션은 기본값으로:
  - **블록형(한 덩어리) 텍스트 레이어**로 고정(수동 정규화)
  - ‘단어별 하이라이트/흔들림’ 프리셋은 금지 목록 우선

### C) 한국어 줄바꿈 하우스 룰(재강조)
- 조사/어미 분절 금지(은/는, 이/가, 을/를, -고, -서, -지만 등).
- 문장이 길어질수록 “글자 크기↓”가 아니라 “문장 축약↑”로 해결.

### D) 폰트/문자권/프리셋 호환성 테스트
- 비라틴 문자(키릴 등)에서 프리셋 애니메이션이 깨질 수 있다는 보고가 있음 → 한글도 예외가 생길 수 있으므로,
  - 폰트 교체 시 **프리셋 호환 샘플 테스트**
  - 깨지는 프리셋은 **금지 목록**으로 축적

### E) 공공/관광에서 MV식 키네틱을 “최소 단위”로 제한
- 강조는 **1개/문장**, 모션은 “짧게-멈추기(엔드포인트 홀드)”를 기본값으로.

---

## Update 2026-05-12 12KST — STT(오토캡션) 운영 규칙을 “파이프라인”으로 격상
- Latest note: [[video-typography/hourly/2026-05-12-12]]

### A) 캡션 생성 ‘격리 프로젝트’ (기본값)
- **메인 편집 프로젝트에서 바로 Auto Captions 생성 금지.**
- 절차(권장):
  1) 새 프로젝트(캡션 생성 전용) 생성
  2) 오디오/영상 1개만 넣고 Auto Captions 생성
  3) 생성된 캡션을 **정규화 패스(폰트 페어/행간/줄바꿈/강조 1개/문장)** 로 정리
  4) 메인 프로젝트로 가져오기(가능하면 SRT/자막 레이어 단위로)
- 목적: STT가 29/45/99%에서 멈추는 리스크를 메인 편집에서 분리(생산성 보호).

### B) STT 진행률 고착(29/45/99%) 대응 표준 순서
1) **언어 Auto-detect 해제 → 실제 음성 언어 명시 지정**
2) 오디오-only로 재시도(영상 디코딩/가속 영향 분리)
3) (데스크톱) 성능 옵션/하드웨어 가속/캐시 점검(환경별)
4) **CapCut Web 캡션 등 대체 경로로 생성 후 재가져오기**

### C) “세로 9:16 하단 unsafe”를 제도화(프리셋/템플릿으로)
- 쇼츠/관광/공공 모두 하단은 UI 침범 확률이 높으므로:
  - 본문 내레이션 기본 위치를 **ALT(상단/측면)** 으로 갖고,
  - 하단은 **단문/훅/효과음 정도**만 허용.

---

## Update 2026-05-12 13KST — “타이포가 주연”인 시스템화 + 캡션 Export 게이트
- Latest note: [[video-typography/hourly/2026-05-12-13]]

### A) Kinetic/모션 타이포 “한 순간 1주연” 규칙(정보 위계)
- 텍스트가 주연인 영상(키네틱/타이포 주도)에서 가장 흔한 실패는 **동시에 여러 레이어가 움직여 시선이 분산**되는 것.
- 기본값:
  - **한 순간에 ‘주연 텍스트 1개’만** 크게 이동/스케일/변형
  - 나머지는 정지(hold) 또는 매우 약한 패럴럭스 정도
- 공공/관광 적용:
  - (주연) 슬로건/키워드 1개 → (조연) 설명 1문장 → (고지) 작은 텍스트
  - “PPT 슬라이드처럼 한 프레임에 다 말하기” 금지

### B) “타이틀 시스템” 선잠금(시리즈/기관/관광)
- 에피소드/챕터가 늘어나는 구조에서는 **타이틀 시스템이 흔들리면 전체가 산만**해진다.
- 선잠금 항목:
  - 폰트 페어(타이틀/본문 분리)
  - 9:16 세이프존(하단 unsafe 기본)
  - 장소 라벨 위치(피사체 회피 포함)

### C) CapCut 캡션 Export 규칙(납기 보호)
- 캡션 Export 실패/깨짐을 줄이기 위한 “운영 게이트”:
  1) **캡션 Export 기본 폴더는 ASCII 경로**(영문/숫자)로 고정
  2) Export 실패 시: **TXT로 먼저 Export → 외부에서 SRT 변환**(표준 우회 루트)
  3) “샘플 Export 게이트”는 반드시 **캡션이 포함된 구간**으로 수행(캡션이 Export 멈춤 원인일 수 있음)

---

## Update 2026-05-12 14KST — Auto Captions를 ‘프로젝트 안정성’ 규칙으로 편입
- Latest note: [[video-typography/hourly/2026-05-12-14]]

### A) Auto Captions = “프로젝트 손상/Export 실패” 리스크로 취급
- Auto Captions는 결과 품질뿐 아니라 **Export 무한 로딩/캡션 Export 실패**를 유발할 수 있다는 보고가 있음.
- 기본값: **캡션 생성 전용(격리) 프로젝트**에서 먼저 성공시키고, 메인 편집으로 가져온다.

### B) 99% 고착(웹) 표준 대응
- 99%에서 멈춘다고 해서 곧바로 새로고침/이탈하면 작업이 취소될 수 있음.
- 표준: **리로드 금지 → 네트워크/브라우저 안정화 → 샘플(짧은 구간)로 재시도**.

### C) 캡션 Export “납기 루트” 고정
- Export path: **ASCII(영문/숫자)만**
- 실패 시: **TXT로 먼저 Export → 외부에서 SRT 변환(UTF-8 인코딩 확인)**
- 이유: Preview OK라도 Export 단계에서 깨지거나 실패하면 납기 손실.

### D) MV/가사 타이포 ‘하이라이트 최소 단위’
- 문장당 강조 단어 1개 + **엔드포인트 홀드**로 읽힘 보장.
- 모션으로 읽힘을 해결하지 말고, 먼저 **문장 축약/줄바꿈/간격**으로 해결.

---

## Update 2026-05-12 15KST — Safety-area 선잠금 + 캡션 납기 루트 + 의미-모션 매핑
- Latest note: [[video-typography/hourly/2026-05-12-15]]

### A) 9:16 “하단 unsafe”를 텍스트 시스템의 기본 전제로 둔다
- 본문 내레이션/설명 텍스트는 **하단 고정 금지(기본값)**.
- 디폴트 포지션(권장): lower-middle(중하단이되 UI 영역 위) 또는 side-block(좌/우 하단-중앙).
- 하단은 “단문 훅/효과음/짧은 키워드”만 제한적으로 사용(겹침 리스크 최소화).

### B) “캡션 Export 납기 루트” 표준(프로젝트/팀 공통 규칙)
- Export 경로는 **ASCII(영문/숫자/언더스코어)** 로만 구성된 폴더를 표준으로 둔다.
- 실패 시 우회 표준:
  1) CapCut에서 **TXT로 먼저 Export**
  2) 외부 변환으로 SRT 생성(UTF-8 인코딩 확인)
- 이유: Preview OK라도 Export 단계에서 깨지면 납기 손실이므로, “우회 루트”를 문서화해 **즉시 실행 가능한 절차**로 보유.

### C) “의미-모션 매핑 없는 모션 금지”(키네틱/자막 공통)
- 모션은 ‘멋’이 아니라 **의미를 번역**해야 한다.
- 체크리스트(둘 중 하나라도 Yes가 아니면 모션 금지):
  - 이 모션이 “강조/긴장/딜레이/해소/전환” 중 무엇을 표현하는가?
  - 음악/발화의 비트(악센트)와 모션의 피크가 같은가?
- 결과: 모션 수를 줄여도 완성도가 올라가며, 공공/관광에서 특히 “신뢰감”이 유지된다.

### D) Auto Captions는 “생성 단계부터 격리”를 기본값으로
- 메인 편집 프로젝트에서 바로 Auto Captions를 돌리지 않는다(리스크 분리).
- 캡션 생성 전용 프로젝트에서:
  1) 오디오/영상 최소 구성
  2) Auto Captions 생성 성공
  3) 정규화(폰트/행간/줄바꿈/강조 1개/문장)
  4) 메인 프로젝트로 가져오기

---

## Update 2026-05-12 16KST — 관광/공공 ‘시네마틱 캠페인’ 텍스트 절제 규칙 + 역할 3분리
- Latest note: [[video-typography/hourly/2026-05-12-16]]

### A) 관광/공공 캠페인형(시네마틱) 영상: “본문 자막을 얹는 비용”이 크다
- 시네마틱 관광 캠페인(스타/세계관/단편영화 톤)은 화면 미장센/배우/장소가 ‘주연’이라서, 본문 자막이 들어오면 신뢰감이 떨어지거나 과밀해지기 쉽다.
- 기본값:
  1) **컷 내부 본문 자막 최소화**
  2) 정보 회수는 **챕터 카드 / 엔드 카드**에서 처리(=설명은 설명 컷에서)

### B) 텍스트 역할 3분리(공공/관광 공통 규칙)
- 관광/공공 텍스트는 아래 3역할을 섞지 않는다:
  1) **타이틀/세계관 라벨(브랜드)**
  2) **장소 라벨(짧게, 반복 템플릿)**
  3) **본문 설명(공모전/기관 제출판에서만, 별도 스타일)**
- 실행 팁:
  - 1)과 2)는 화면 디자인을 존중(절제)
  - 3)은 가독성 최우선(역할 분리된 폰트/크기/위치)

### C) 리듬 강한 컷(추격/댄스/의식)은 “문장 자막”을 엔드포인트 홀드에서만 처리
- 이유: 리듬이 강한 컷은 자막이 ‘비트와 무관한 타이밍’으로 들어오는 순간 어색함이 커진다.
- 기본값:
  - 문장/설명 자막은 **엔드포인트 홀드가 확보된 컷**에서만 넣는다.
  - 나머지 컷은 키워드 1개 또는 무자막(필요 시 장소 라벨만).

---

## Update 2026-05-12 20KST — Motion Budget + ALT 위치 세트 + Auto captions 격리(운영 표준)
- Latest note: [[video-typography/hourly/2026-05-12-20]]

### A) Motion Budget(타이포 모션 예산) — “장문/공공은 훅만 움직인다”
- 컷/문장마다 모션 사용량을 먼저 제한한다(예: 1문장에 1회만 모션).
- 기본값:
  - **공공/공모전/관광 본문:** 모션 0(정지) + 페이드만 허용, 강조가 필요하면 “굵기/크기”로 해결.
  - **MV:** 훅/키워드 1개만 모션(진입-홀드-퇴장) + 나머지는 정지/미세 페이드.
- 이유: 모션으로 읽힘을 해결하려는 순간, 전체가 “버벅임/프레임 드랍”처럼 느껴지고 피로가 급증.

### B) 9:16 ALT 자막 위치 세트(기본 자산)
- 하단 중앙 본문 자막 고정은 실패 확률이 높으므로, 아래 프리셋을 프로젝트 자산으로 먼저 만든다:
  1) upper-left
  2) upper-right
  3) mid-left
  4) mid-right
  5) side-block(좌/우 세로 블록)
- 운용 규칙: “컷마다 새로 고민”하지 말고, **컷의 액션/피사체 위치에 따라 ALT 프리셋을 선택**한다.

### C) Auto captions 생성은 “격리 프로젝트”가 디폴트(납기 리스크 분리)
- 기본값: 메인 프로젝트에서 Auto captions를 바로 돌리지 않는다.
- 표준 절차:
  1) 캡션 생성 전용(격리) 프로젝트에서 생성 성공
  2) 정규화(폰트 페어/행간/줄바꿈/강조 1개/문장)
  3) 메인 프로젝트로 이식
- 근거: CapCut Help(99% 고착/Export fail 등)는 재발 가능성이 있으므로 “리스크 분리”가 납기 관점에서 안전.

### D) 타이포 설계 우선순위(재사용 로직)
1) 타이밍: 음악/발화의 악센트 + 진입/홀드/퇴장 호흡
2) 레이아웃: 역할 분리(타이틀/장소/본문/고지) + safe-zone
3) 스타일: 폰트/굵기/자간/행간/대비
4) 효과: 모션/글로우/노이즈는 마지막(“의미-모션 매핑”이 있을 때만)

### D) CapCut 운영 규칙은 ‘기능 팁’이 아니라 ‘납기 규정’으로 문서화
- 공식 근거:
  - Recognition stuck at 99%: https://www.capcut.com/help/recognition-of-subtitles-lagging
  - Captions fail to export: https://www.capcut.com/help/captions-fail-to-export
- 기본값:
  - Auto Captions는 **격리 프로젝트**에서 생성(메인 프로젝트 보호)
  - 캡션 Export는 **ASCII 경로 고정 + TXT→SRT 우회 루트**를 표준으로 보유

---

## Update 2026-05-12 17KST — “설명은 설명 컷에서” + 모션 텍스트 최소 조건 + STT 납기 Plan B
- Latest note: [[video-typography/hourly/2026-05-12-17]]

### A) 공공/관광(시네마틱) 기본값: “설명 자막”이 아니라 “설명 컷(카드)”을 만든다
- 캠페인형 시네마틱 컷 위에 본문 설명을 얹으면 과밀/저급해지는 경우가 많다.
- 기본 설계(권장):
  1) 본편(시네마틱 컷) = 무자막/키워드/장소 라벨 중심
  2) 정보 회수 = **챕터 카드 / 엔드 카드 / 설명 카드**에 집중
  3) 공모전 제출판 = “설명 카드”를 **의도적으로** 추가(역할 분리로 신뢰 확보)

### B) 모션 텍스트 최소 조건: “엔드포인트 홀드 없으면 모션 금지”
- 규칙:
  - 텍스트가 이동/스케일/회전/변형된다면, 반드시 “정지 구간(홀드)”이 있어야 한다.
  - 홀드가 없다면: (1) 문장 축약 (2) 글자 수 감소 (3) 크기 증가 (4) 위치 변경으로 해결.
- 적용 범위: MV 가사 타이포 + 공공 본문 자막(둘 다 동일 규칙).

### C) 한글 가독성/강조 우선순위(공공/관광/MV 공통)
- 강조를 만들 때 우선순위를 아래로 고정:
  1) 굵기(Weight)
  2) 크기(Size)
  3) 자간/행간(Tracking/Leading)
  4) 배경 대비(가벼운 그림자/로컬 비네트)
  5) 색(Color) — 마지막 단계
- 이유: 색/글로우/박스에 먼저 의존하면 “시스템 폰트 + 유튜브 자막” 느낌이 강화된다.

### D) STT/Auto captions = “품질 기능”이 아니라 “납기 리스크”: Plan B를 문서화
- 반복 실패 시그널: 29% / 45% / 99% 고착, Export 무한 로딩 등.
- Plan B(최소):
  1) 짧은 구간으로 분할하여 재시도(샘플 게이트)
  2) 캡션 생성은 격리 프로젝트에서(메인 프로젝트 보호)
  3) 캡션 Export는 ASCII 경로 + TXT→SRT 우회 루트 유지
  4) 최악의 경우: 외부 STT(SRT 생성)로 전환(도구는 별도 결정)

### E) CapCut 캡션 운영 표준(3단계)
- **Generate(격리)** → **Normalize(줄바꿈/강조/스타일 통일)** → **Transplant(메인 프로젝트 이식)**
- 이유: Auto captions 사용 이력이 프로젝트 Export에 영향 줄 수 있다는 현장 보고가 있으므로, 리스크를 분리해 관리한다.

---

## Update 2026-05-12 18KST — VisitKoreaYear 오마주형(게임/추격) 텍스트 규칙 + 야간 컷 자막 위치 금지구역 + ‘정답 watch-id’ 저장 규정
- Latest note: [[video-typography/hourly/2026-05-12-18]]

### A) 오마주/게임형 지역 바이럴(공공 캠페인) 텍스트 전략
- 전제: 이야기(룰/추격/행동)가 이미 화면에서 진행되는 경우, 본문 텍스트는 **과잉 정보**가 되기 쉽다.
- 기본값:
  1) 컷 내부 텍스트 = **룰/키워드 1줄** 또는 장소 라벨
  2) 본문 설명/CTA = **엔드 카드(또는 챕터 카드)에서 회수**
  3) 문장 텍스트가 필요하면 **엔드포인트 홀드가 있는 컷에서만**

### B) 야간/불꽃/네온 컷 “하단 중앙 본문 자막” 기본 금지
- 금지 이유:
  - 플레이어 UI/자막/안전영역과 충돌 가능성이 높고
  - 불꽃/반사/인물 실루엣 등 핵심 미장센이 하단에 몰리는 경우가 많아 ‘가림’이 잦다.
- 권장:
  - 상단/측면(단, 큰 둥근 박스/플레이트는 금지)
  - 필요 시 로컬 비네트/미세 그림자로 대비 확보(박스보다 우선)

### C) 공공/다큐형(미담/정책/기관) 모션 KPI 전환: “멋”보다 “신뢰”
- 규정:
  - 모션 텍스트(스케일/이동/회전/변형)는 최소화
  - 대신 **글자 크기↑ + 대비↑ + 홀드↑**로 읽힘/신뢰 확보

### D) 한글 본문 캡션 줄바꿈 잠금: “문자 수”가 아니라 “발화 단위”
- 금지 패턴(즉시 수정): 조사/어미가 다음 줄로 넘어가거나, 의미 단위가 깨지는 줄바꿈.
- 실행:
  - Auto captions 결과는 그대로 쓰지 않고, **Normalize 단계에서 발화 단위 줄바꿈**을 수동으로 고정.
  - CapCut JSON 좌표가 아니라 **CapCut preview에서 눈으로** 최종 판단.

### E) 레퍼런스 저장 규칙: embed/뉴스 링크가 아니라 “정답 watch-id”를 원본으로 보관
- 이유: 기사/VR 페이지는 iframe/스크립트로 영상 링크를 숨기는 경우가 많고, 장기 보존성이 낮다.
- 규정:
  - 위키에 저장할 때는 항상 **youtube.com/watch?v=...**를 1차 원본으로 기록한다.
  - 부가 근거(기사/보도자료)는 2차로 첨부.

---

## Update 2026-05-12 19KST — 장문 모션 총량 제한 + 합작 규격서 + 타이포=리듬(3박)
- Latest note: [[video-typography/hourly/2026-05-12-19]]

### A) 선택 로직(재사용 가능): “장문이면 모션을 줄이고, 규격을 잠근다”
- 입력 조건:
  - (1) 음성/내레이션이 길다(문장 단위)
  - (2) 화면 정보량이 많다(관광/도시/야간 미장센)
- 기본 선택:
  1) **본문은 홀드 중심**(읽힘/신뢰 KPI) + 훅/키워드만 모션
  2) 폰트는 1~2개로 제한(제목 1, 본문 1) + 팔레트는 2~3색
  3) 강조 우선순위는 고정: **굵기 → 크기 → 자간/행간 → 로컬 대비(그림자/비네트) → 색**

### B) 합작/다인 편집(키네틱 포함) 규격서 최소 템플릿
- 규격서에 반드시 명시(편집 시작 전):
  - 폰트(무료/비유료 후보만) + weight range(예: 600–800)
  - 팔레트(기본 2색 + 강조 1색) + 금지색(형광 노랑/과한 글로우 등)
  - Safe-zone(9:16 기준) + **하단 중앙 본문 금지 컷 타입(야간/네온/불꽃/인물 하단 중요 컷)**
  - 동시 단어 수 상한(예: 1–4단어) + 엔드포인트 홀드 최소치(프레임/초)

### C) 타이포=리듬: “진입-홀드-퇴장(3박)” 우선 설계
- 오프닝/챕터/슬로건에서 우선순위:
  1) 음악/컷에 맞춰 **진입 타이밍** 결정
  2) 읽기 호흡 확보를 위한 **홀드**(엔드포인트) 확보
  3) 다음 컷/비트로 넘어가기 위한 **퇴장**(또는 자연 소거) 설계
- 모양(박스/장식/모션 프리셋)은 마지막에 얹는다.

### D) CapCut 적용 규칙(공식 Help 근거 보강)
- STT/Auto captions는 “기능”이 아니라 **납기 리스크**(29/45/99% 고착, export 이슈 포함).
- 운영 표준(항상 유지):
  1) 캡션 생성은 격리 프로젝트에서(메인 프로젝트 보호)
  2) 캡션 export 경로는 **ASCII only**
  3) SRT가 막히면 **TXT export → 외부 변환** 우회 루트 유지
- 근거(공식):
  - https://www.capcut.com/help/recognition-of-subtitles-lagging
  - https://www.capcut.com/help/captions-fail-to-export

---

## Update 2026-05-12 21KST — STT 샘플 게이트 + 독해 속도 역설계 + 레이어 수 KPI
- Latest note: [[video-typography/hourly/2026-05-12-21]]

### A) STT/Auto-captions “샘플 구간 게이트” (납기 보호용 운영 규칙)
- 목적: 본편 전체를 STT 실패로 망가뜨리는 리스크를 줄인다.
- 규칙(기본값):
  1) 본편 전에 **10–20초 샘플 구간**(대사/내레이션이 있는 구간)을 잘라 **격리 프로젝트**에서 STT 생성 시도
  2) 성공하면: Normalize(줄바꿈/강조/스타일) 후 메인 프로젝트로 이식
  3) 실패하면: 본편 STT를 중단하고 Plan B로 전환(분할/웹/외부 STT 등)
- 핵심: “STT 기능”이 아니라 **납기 리스크**를 관리하는 게이트다.

### B) 독해 속도 역설계(타이포/카메라 공통)
- 전제: 기법(null/마스크/프리셋)보다 중요한 건 “읽힘”이다.
- 규칙:
  - 텍스트 이동/스케일/카메라 패닝 속도는 **독해 속도**에 맞춰 역설계한다.
  - 읽힘이 안 되면 모션을 늘리는 게 아니라 **문장 축약/분절/홀드**를 먼저 한다.

### C) “텍스트 레이어 수 KPI”(실패 패턴을 줄이는 정량 규칙)
- 기본 KPI:
  - 문장당 **주연 1개 + 보조 1개**를 기본 상한으로 둔다(그 이상은 기본적으로 실패 위험↑).
- 공공/관광 적용:
  - 한 화면에서 (타이틀/장소/본문/고지)를 동시에 말하려는 충동을 차단 → 역할 분리 컷(카드)로 회수.

### D) 한글 가독성 우선순위(강제 순서)
1) Weight/Size/Leading  
2) 로컬 대비(약한 그림자/비네트)  
3) 마지막에 색(Color)  
- 이유: 색/박스/글로우에 먼저 의존하면 “시스템 폰트+유튜브 자막” 인상이 강화된다.
---

## Synthesis 2026-05-12 22KST — Hourly runs → durable operating logic
- Canonical compact manual: [[video-typography-operating-manual]].
- Treat the hourly notes as evidence/rule mining logs; treat the manual as the production decision layer.
- Durable rules distilled from 09–20KST runs:
  1) **Text role comes before style**: TITLE / LOCATION / BODY / DISCLOSURE / CTA must be separated before font/effect work.
  2) **Motion is budgeted**: public/tourism body text is static or fade-only; MV hooks may move, but only with endpoint hold.
  3) **9:16 lower-center body captions are unsafe by default**: build ALT position presets before editing.
  4) **CapCut captions are a delivery-risk subsystem**: isolate Auto Captions, normalize, transplant, and sample-export with captions included.
  5) **Korean readability hierarchy**: weight/size/tracking/leading first, color/glow last; never solve long copy by only shrinking font.
  6) **Preview/export proof beats coordinates**: visible glyph alignment and exported caption behavior override JSON equality.

---

## Update 2026-05-12 22:10KST — Font-name proof as deliverable, not just visual font taste

### A) Inspector-name proof gate
- Public contest/CapCut typography revisions now require a proof step for selected text layers:
  - select title clip → confirm font field is not `시스템`;
  - select body/description clip → confirm font field is not `시스템`;
  - screenshot the actual CapCut UI proof.

### B) Editable-first constraint
- When the user rejects baked overlays, the typographic solution must stay editable in CapCut even if that narrows the font palette.
- Transparent overlay remains only a documented workaround when the user accepts it; it cannot be silently substituted as the main final.

### C) KAIA V33 empirical finding
- `경기천년제목B` worked as a CapCut-recognized editable Korean font and exported without observed Pro blocker.
- `고운한글돋움` showed a proper name but triggered Pro/export blocker, so reject for free-delivery finals unless the user approves Pro.
- macOS custom fonts that display as `시스템` are not acceptable for this user's font QC, even when the preview glyphs differ.

---

## Update 2026-05-12 22:25KST — Brand-film anchor rule + 9:16 safe-zone hardening + preset-first captions

### A) Brand-film anchor rule (공공/관광 레퍼런스 수집 표준)
- 문제: YouTube 검색/추천/채널 페이지는 변동성이 높고, embed 링크만 남으면 watch-id가 유실된다.
- 규칙(표준):
  1) 캠페인 영상은 **공식 보도자료/공식 기관 페이지의 outbound YouTube 링크**를 1차 앵커로 기록한다.
  2) hourly 노트에는 “보도자료 URL + watch URL”을 함께 저장한다.
- 근거 예시:
  - STB 보도자료에 “brand film here”로 YouTube outbound 링크 제공(공식 앵커): https://www.stb.gov.sg/about-stb/media-publications/media-centre/singapore-tourism-board-launches-made-in-singapore-global-campaign-to-inspire-travel-to-singapore/

### B) 관광/공공 본편 타이포 설계: “디스크립터(짧은 라벨) → 설명은 카드로 회수”
- 운영 로직:
  - 본편(시네마틱 컷): 장소/행동/감정 키워드(1–4단어)만.
  - 챕터/엔드 카드: 설명/근거/고지를 구조화해 회수(역할 분리).
- 이점: 영상이 ‘유튜브 자막’처럼 보이는 실패(하단 박스/장문)를 예방하고, 공공에서도 영화성을 유지.

### C) 9:16 safe-zone = “단일 하단 규칙”이 아니라 “가변 UI + 다중 프리셋” 문제
- 규칙:
  1) 하단 중앙 본문은 unsafe 기본값(플레이어 UI/설명/버튼 가변).
  2) **ALT 자막 위치 프리셋 3개 이상**을 프로젝트 자산으로 고정(예: 측면 블록 / 중단 / 상단).
  3) 최종 판단은 반드시 실제 앱 플레이어에서(=preview/export + 모바일 재생).
- 참고 근거:
  - YouTube Shorts safe-zone 가이드(가변성/중앙 safe 권고): https://tareno.co/tools/youtube-shorts-safe-zone-checker
  - Netflix title safe 권고치(“safe” 개념의 보수적 적용 근거): https://partnerhelp.netflixstudios.com/hc/en-us/articles/4406208331923-Title-Safe-and-Safe-Action-Best-Practices
  - Subtitle safe area/타이밍 규칙 요약: https://www.sukudostudios.com/srt-vtt-ttml-subtitle-specs/

### D) CapCut 자막은 “매번 디자인”이 아니라 “preset 재사용”이 기본
- 규칙:
  - subtitle system(폰트/크기/행간/강조/위치)을 preset으로 고정해 재사용한다.
  - 변형(모션/색/강조)은 훅/챕터에만 제한적으로 허용(공공/공모전은 신뢰 우선).
- 참고(공식/준공식):
  - subtitle formatting(프리셋/다중 비율 프리뷰 권장): https://www.capcut.com/ideas/ai-design/ai-design-for-subtitles-formatting

---

## Update 2026-05-13 00KST — CapCut auto-captions “납기 리스크” 운영 규칙(버그/고착/수정 미반영 대응)

### A) Auto-captions 단어 쪼개짐(줄바꿈) QC 규칙
- 증상: 단어가 줄바꿈으로 반쪽씩 분절(가독성 붕괴), 3줄 이상으로 자막이 비대해짐.  
  - 근거(커뮤니티): https://www.reddit.com/r/CapCut/comments/1t4eziv/autocaptions_breaks_up_words_into_separate_lines/  
  - 근거(커뮤니티): https://www.reddit.com/r/CapCut/comments/w8q0xl/how_can_edit_auto_captions_line_length/
- 규칙(운영):
  1) auto-captions 생성 직후, 본편에서 바로 고치지 말고 **격리 프로젝트에서 Batch Edit로 1–2줄 유지**를 먼저 달성한다.
  2) “단어 분절(예: congra / tulations)”은 발견 즉시 수정(=미루면 전체 정합성 붕괴).

### B) “수정했는데 export에 반영 안 됨” 우회 규칙(속성 이식)
- 증상: auto-caption 텍스트를 고쳐도 렌더 결과가 원문으로 남거나 일부 단어가 계속 잘림.  
  - 근거(커뮤니티): https://www.reddit.com/r/CapCut/comments/1bdil6w/auto_captions_not_working_properly/
- 규칙(우회):
  - 해당 캡션을 계속 붙잡지 말고, **새 텍스트 클립 생성 → Copy/Paste Attributes로 스타일만 이식**(텍스트는 새로).
  - 최종 확인은 preview가 아니라 **export(자막 포함) 결과로**.

### C) 99%/45% 고착 = “기술 이슈”가 아니라 “납기 이슈”
- 근거(커뮤니티):
  - 99% 고착: https://www.reddit.com/r/CapCut/comments/1r5ypbe/capcut_auto_captions_stuck_at_99/
  - 45% 고착: https://www.reddit.com/r/CapCut/comments/1nszlra/my_capcut_captions_are_stuck_at_45/
- 규칙(납기):
  1) auto-captions는 디폴트로 **10–20초 샘플 구간**에서 먼저 성공을 확인(“샘플 구간 게이트”).
  2) 실패하면 “본편에서 재시도 반복” 금지 → 격리 프로젝트/대체 STT 루트/수동 타이핑 등 Plan B로 즉시 전환.

### D) REF vs VERIFIED (레퍼런스 품질 라벨링)
- 이번 회차처럼 Behance 스틸/GIF/제작자 노트 기반 수집은 유용하지만, “컷 리듬/타이밍”은 오판 위험이 있다.
- 규칙:
  - hourly 노트에서 **REF(미시청)** / **VERIFIED(시청+타임코드)** 라벨을 강제하고,
  - 공공/관광/공모전 제출용 규칙은 가능하면 VERIFIED 근거를 우선 사용한다.

---

## Update 2026-05-13 02KST — Export-First Gate + Descriptor-Only(시네마틱 본편) + Autocaption Containment

### A) Export-First Gate (preview가 아니라 export가 첫 관문)
- 배경: CapCut/편집툴에서 “편집 화면(preview)에서는 정상인데 export에서 깨짐/누락/플래그”가 반복된다. (예: 필터 미반영, 캡션/효과 누락, Pro 플래그, 싱크 붕괴 등)
- 규칙(운영):
  1) 프로젝트 착수 직후(본편 편집 전에) **10–20초 샘플 구간을 선택**한다.
  2) 그 샘플에 적용될 예정인 핵심 리스크 요소(autocaption/필터/효과/폰트/템플릿)를 최소 1개씩 포함시킨다.
  3) **export 결과물로만** 통과/실패를 판정한다(“preview OK”는 통과 근거가 될 수 없다).
  4) 실패 시 본편에 계속 투자하지 말고 즉시 Plan B(격리 프로젝트, 대체 STT, 수동 캡션, 다른 툴)로 전환한다.
- 참고 근거:
  - r/CapCut (export에서 필터 미반영): https://www.reddit.com/r/CapCut/comments/1t32k2w/capcut_not_exporting_filters/

### B) Autocaption Containment (auto-captions는 “격리 생성→정규화→이식”이 기본)
- 배경: auto-captions는 ‘편의 기능’이 아니라 **프로젝트 오염/납기 리스크**가 될 수 있다(고착/수정 미반영/플래그/무한 로딩 등).
- 규칙(운영):
  1) auto-captions는 디폴트로 **격리 프로젝트**에서만 생성한다.
  2) 격리 프로젝트에서만 정규화(줄바꿈/강조/스타일 일괄) 후, 메인 프로젝트로 이식한다.
  3) “삭제했는데도 export가 무한로딩” 같은 상황을 예방하기 위해, 본편 프로젝트에서 auto-captions를 생성하지 않는다.
- 참고 근거(공식/준공식 + 커뮤니티):
  - CapCut help (캡션 export 실패/경로/형식 이슈): https://www.capcut.com/help/captions-fail-to-export
  - CapEditCut(비공식 커뮤니티지만 메타데이터/오염 가설이 반복): https://www.capeditcut.com/community/capcut/capcut-stuck-loading-after-clicking-export/
  - r/CapCut (autocaption 플래그/내보내기 제한): https://www.reddit.com/r/CapCut/comments/1t22nhb/capcut_not_letting_me_export_even_though_nothing/

### C) Descriptor-Only in Cinematic Cuts (관광/공공 본편 = 1–4단어 라벨만)
- 배경: 관광/공공 시네마틱 본편은 컷 리듬/미장센이 핵심이라, 장문 본문 자막을 얹는 순간 “설명 영상/유튜브 자막 영상”으로 장르가 붕괴하기 쉽다.
- 규칙:
  1) 본편(시네마틱 컷) 텍스트는 **장소/행동/감정 라벨(1–4단어)**만.
  2) 장문 설명/정책/고지/근거는 챕터/엔드 카드로 회수(역할 분리).
- 참고 근거(우수 사례 앵커):
  - Visit Dubai (캠페인 본편은 서사·액션 중심): https://www.youtube.com/watch?v=uKB2ZQD9hgA
  - STB(공식 릴리즈 outbound 앵커 + 브랜드 필름): https://www.stb.gov.sg/about-stb/media-publications/media-centre/singapore-tourism-board-launches-made-in-singapore-global-campaign-to-inspire-travel-to-singapore/

---

## Update 2026-05-13 03KST — Kinetic Typography ‘호흡(진입-홀드-퇴장)’ 최소 규격 + 캠페인형 모듈 시스템 근거

### A) Kinetic Typography Breath Spec (진입-홀드-퇴장) — “모션”보다 “읽기”를 KPI로
- 배경: kinetic typography 레퍼런스를 보면, 성공작은 공통적으로 **읽히는 시간(hold)** 을 먼저 확보하고, 모션은 그 다음에 배치한다.
- 근거(라운드업 + 사례 설명):
  - CreativeBloq kinetic typography 예시(2026 업데이트): https://www.creativebloq.com/typography/examples-kinetic-typography-11121304
  - 타이틀 합성/가독성 우선 튜토리얼: https://www.premiumbeat.com/blog/true-detectives-title-sequence-in-after-effects/
- 규칙(운영, 기본값):
  1) **진입(0.15–0.30s)**: “등장”은 빠르게. 의미 없는 튀는 트랜지션 금지.
  2) **홀드(읽기 시간)**: 한국어/공공은 보수적으로(=더 길게) 잡는다. 홀드가 없으면 모션 금지.
  3) **퇴장(0.15–0.30s)**: 다음 컷/다음 문장으로 넘겨주는 정리 모션만.
  4) “가독성 실패”가 가장 치명적인 실패 패턴이므로, 효과보다 **로컬 대비/마스킹/비네트**를 먼저 쓴다.
- CapCut 적용 규칙:
  - CapCut preview/export가 source of truth. 타이밍은 JSON이 아니라 **실제 preview에서 ‘읽는 데 걸리는 시간’으로 조정**.
  - 텍스트 모션은 기본적으로 **엔드포인트 홀드가 있는 컷**에만.

### B) Campaign Typography = 모듈/그리드(재사용성) 우선
- 근거(모듈형 캠페인 설계/여백/콘텐츠 시스템):
  - VIFF 2024 캠페인 시스템: https://wearezak.com/projects/vancouver-film-festival-2024/
- 규칙:
  - 공공/기관/관광(공모전 포함)은 “예쁜 자막”이 아니라 **모듈/그리드/여백 규칙**을 먼저 잠근다.
  - 폰트는 “기본 시스템 폰트 느낌 금지”. 단, **Pro/유료 폰트는 명시 승인 전 최종본 금지**.

### C) CapCut Caption Export 표준 루트(ASCII path + TXT→SRT 우회) 재강화
- 근거(공식 Help): https://www.capcut.com/help/captions-fail-to-export
- 규칙:
  1) 자막/캡션 관련 export는 기본적으로 **ASCII 경로**로 고정.
  2) SRT 실패 시 TXT로 export 후 외부 변환.
  3) 템플릿/전환과 결합 시, **Export-First Gate(10–20초 샘플)** 로 선검증.

---

## Update 2026-05-13 04KST — “분석 체크리스트(YouTube 30) + SRT 사이드카 + 캠페인 플레이리스트 앵커”

### A) YouTube 우수사례 분석 체크리스트(컷 리듬/자막 위치/폰트 감/전환/정보 위계)
- 목적: “예쁜 레퍼런스 수집”이 아니라 **재사용 가능한 관찰 포맷**을 고정한다.
- 체크리스트(기본 1회전):
  1) 컷 리듬: 평균 컷 길이(기본 2.0–2.5s/cut 대비), 훅 구간의 과밀/과소 여부
  2) 텍스트 호흡: 진입(짧게) → 홀드(읽기) → 퇴장(정리) 구조가 있는가?
  3) 자막 위치: 하단 고정만 쓰는가, 9:16 안전영역을 회피하는 **ALT 위치(상/중/측면)**가 있는가?
  4) 폰트 감: “기본 시스템 폰트 느낌”이 나는가? (난다면: 굵기/자간/행간/여백/대문자 비율로 해결 가능한가?)
  5) 정보 위계: 제목/장소/본문(설명)/고지/강조의 역할이 분리돼 있는가?
- 근거(여러 실제 영상 ID를 제공하는 리스트):
  - Thinkmedia.de kinetic typography list(YouTube embed ID 다수): https://thinkmedia.de/kinetic-typography-videos/

### B) Campaign anchor rule — “공식 캠페인 페이지의 YouTube 플레이리스트”를 1급 근거로 저장
- 배경: YouTube 검색 결과는 변동/중복이 많다. 반면 **공식 캠페인 페이지의 playlist 링크**는 보존성이 높다.
- 규칙:
  1) 캠페인형(관광/공공/기관) 레퍼런스는 “영상 1개 링크”보다 **플레이리스트/허브**를 먼저 저장한다.
  2) 플레이리스트를 앵커로 두고, 그 안에서 “자막/타이포” 관찰이 좋은 편을 골라 타임코드로 VERIFIED 승격한다.
- 근거:
  - Myrtle Moments 캠페인 페이지(YouTube playlist 링크 제공): https://www.myrtlebeachareacvb.com/myrtle-moments

### C) SRT sidecar deliverable — 공공/공모전/기관 제출에서 “번인 + SRT”를 표준으로
- 배경: 공공/공모전/기관 제출은 검수·수정이 잦고, 번인 자막만 있으면 수정 루프가 느리다.
- 규칙:
  1) 최종 번인(영상 내 자막) 외에, 가능하면 **SRT/TXT 캡션 파일을 함께 export**해 둔다.
  2) SRT는 전달용(검수/번역/재편집), 번인은 배포용(YouTube/쇼츠)으로 역할 분리한다.
  3) CapCut export 실패 리스크 때문에, SRT도 **Export-First Gate(샘플 10–20초)**에 포함해 선검증한다.
- 근거:
  - CapCut help(캡션 export 실패/ASCII path/TXT→SRT): https://www.capcut.com/help/captions-fail-to-export
  - YouTube(자막 파일 업로드 워크플로): https://help.youtube.com/support/youtube/bin/answer.py?answer=100079&topic=15328
  - YouTube 튜토리얼(직접 SRT export 목표): https://www.youtube.com/watch?v=Cjrj36cUsNM

---

## Update 2026-05-13 05KST — CapCut 실패 패턴(커뮤니티 근거) → 납기 운영 규칙 강화

### A) Auto Captions = 네트워크/서비스 의존 리스크(기능이 아니라 납기 변수)
- 근거(오프라인에서 auto captions 불가 보고): https://www.reddit.com/r/CapCut/comments/1k9gvln
- 규칙:
  1) auto captions가 들어가는 프로젝트는 시작 즉시 **샘플 10–20초 구간에서 ‘생성 성공’**을 먼저 확인한다.
  2) “생성 성공”이 확인되기 전까지는 메인 타임라인 편집을 과도하게 진행하지 않는다(낙관 금지).

### B) ‘단어 분절(한 단어가 2줄)’은 즉시 Reject(특히 한글/고유명사)
- 근거(Desktop Mac, 2026-05-05): https://www.reddit.com/r/CapCut/comments/1t4eziv/autocaptions_breaks_up_words_into_separate_lines/
- 실패 정의:
  - 한글/영문을 막론하고, **단어가 두 줄로 갈라지면(예: 한 글자씩 줄바꿈)** 가독성이 즉시 붕괴한다.
- 교정 우선순위(운영):
  1) 폰트 크기↓ 또는 박스 폭↑ (레이아웃)
  2) 자간/행간 조정 (줄바꿈 압력 완화)
  3) “문자수 기준”이 아니라 **발화 단위로 캡션을 재분할**(의미 단위 고정)

### C) Export 99~100% 프리즈/크래시: ‘라우트 우회’가 1차 대응일 수 있음
- 근거(99.9% 크래시, Space/Share 우회): https://www.reddit.com/r/CapCut/comments/1e38qnd
- 규칙:
  1) 로컬 export 실패 시, 전체 재시도 전에 **샘플 export(10–20초)**로 재현 여부를 먼저 확인.
  2) 재현되면 **Space/Share 라우트로 우회 export**를 플랜 B로 둔다.

### D) 서비스 다운/Pro 차단 동시 발생 가능성 → 제출/납품 플랜에 포함
- 근거(다운/차단 보고): https://www.reddit.com/r/CapCut/comments/1rk1ewn/capcut_bytedance_tiktoks_parent_company_seems/
- 규칙:
  - 공공/공모전/기관 납품은 “CapCut만 가능”을 전제로 하지 말고, 최소한의 **대체 렌더 파이프**(다른 기기/다른 편집기/번인+SRT 패키지)를 문서로 갖춘다.

### E) 캡션 줄바꿈(Enter) 후 싱크 붕괴 가능성 → 샘플 구간 게이트에 포함
- 근거: https://www.reddit.com/r/CapCut/comments/16ubkws
- 규칙:
  - 캡션 줄바꿈/대량 편집을 하기 전, 샘플 구간에서 **(1) 싱크 (2) 재생 안정성 (3) export 안정성**을 함께 통과시킨다.

---

## Update 2026-05-13 06KST — KTO 2024 4편 watch-id 확정 + CapCut Help(공식)로 운영 게이트 보강

### A) Campaign ingest rule v2 — “공식 채널 + 인덱서(Filmot)로 watch-id 고정”
- 문제: YouTube 검색은 변동/중복이 많고 music.youtube.com 등으로 샛길이 생김.
- 규칙(운영):
  1) 기관/캠페인 영상은 **공식 채널/공식 페이지**를 1급 근거로 둔다.
  2) ‘제목 검색’으로 못 찾으면, **Filmot(채널 인덱스)로 watch-id를 먼저 확정**하고 URL을 고정한다.
  3) URL이 고정되면, 다음 회차에서 타임코드(자막 위치/홀드/전환)로 VERIFIED 승격.
- 근거:
  - Filmot(Imagine Your Korea 채널 인덱스; 개별 영상의 youtube.com 링크 제공): https://filmot.com/channel/UChhOtjq-3QyyLmP2jv9amrg/0/Imagine%2BYour%2BKorea

### B) KTO 2024 ‘Feel the [ ] of KOREA’ 4편 (watch-id fixed)
- 공공/관광 “텍스트 절제 + 카드 회수”의 기준 샘플로 사용.
- URL:
  - Feel the Trail(gil) of KOREA #VisitKoreaYear: https://www.youtube.com/watch?v=4ihwjoM0pwg
  - Feel the Night(bam) of KOREA #VisitKoreaYear: https://www.youtube.com/watch?v=sng8h9f98Mo
  - Feel the Adventure(moheom) of KOREA #VisitKoreaYear: https://www.youtube.com/watch?v=HjGrwoSNWyw
  - Feel the Rest(shwim) of KOREA #VisitKoreaYear: https://www.youtube.com/watch?v=PPp7rub70HI
- 공식 앵커 페이지(추천지/캠페인 허브 역할):
  - https://english.visitkorea.or.kr/svc/contents/contentsView.do?vcontsId=214889

### C) CapCut 공식 Help 기반: Export/Auto-captions는 “기능”이 아니라 “납기 리스크”로 취급
- 규칙(운영):
  1) auto captions/텍스트가 들어가는 프로젝트는 시작 즉시 **10–20초 샘플 export-first gate**를 통과시켜야 한다.
  2) “편집 화면 OK”는 불충분. **export 파일을 다시 검수**(export-only 글리치/플래시가 존재).
  3) 에러코드가 있는 경우, 즉시 **에러코드 기반 분기**(compound clip 재생성/섹션 export 등)로 이동.
- 근거(공식 Help):
  - Auto captions troubleshooting: https://www.capcut.com/help/auto-captions
  - Export troubleshooting: https://www.capcut.com/help/export-video-on-capcut
  - Export stuck at 99%: https://www.capcut.com/help/export-stuck
  - Export error codes(Compound clip 등): https://www.capcut.com/help/how-to-fix-export-issues

### D) Typography placement hard defaults (관광/공공)
- 야간/네온/도시 조명 컷에서: **하단 중앙 장문 자막 기본 금지**(플레이어 UI + 미장센 충돌)
- 9:16 파생을 기본으로 고려: **bottom unsafe를 넓게 잡고**, ALT 위치(상/중/측면)를 사전 정의



---

## Update 2026-05-13 07KST — Campaign-series typography contract + lyric-video “text-as-shot” + CapCut Pro/Auto-caption risk

### A) Campaign-series Typography Contract — “본편 텍스트 절제 + 엔드/챕터에서 회수”
- 관찰: 서울관광재단(VisitSeoul)처럼 LOVE/INSPIRE/FUN 같은 **시리즈 구조**가 있는 경우, 본편에 설명 자막을 과다하게 넣지 않고, **엔드/챕터 카드에서 슬로건과 키 메시지를 회수**하는 편이 시네마틱 무드를 보존한다.
- 규칙(운영):
  1) 시리즈물은 먼저 **‘반드시 반복되는 문구 1개’(슬로건)**를 고정한다.
  2) 본편은 디스크립터 1줄 이하로 제한하고, 정보는 엔드/챕터 카드로 회수한다.
  3) 각 편의 차이는 “문구 변화”보다 **등장 빈도/위치/홀드 길이**로 만든다.
- 근거:
  - VisitSeoul TV complete edition: https://www.youtube.com/watch?v=V8zNmJVeYHM
  - PRNewswire(시리즈 공개 구조): https://www.prnewswire.com/news-releases/global-release-of-seoul-tourism-promotional-video-feel-soul-good-featuring-bts-jin-302232748.html

### B) Montage(장소 급변)형에서는 “장문 본문자막” 대신 “장르/테마 카드”만 허용
- 관찰: VisitBritain 같은 스케일 몬타주는 장소 전환이 빠르므로 장문 자막은 독해가 붕괴한다.
- 규칙(운영):
  1) 몬타주형은 텍스트를 **(a) 장르/테마 카드 (b) 엔드카드**로만 제한한다.
  2) 설명은 영상 밖 패키지(설명란/웹/고정댓글)로 회수한다.
- 근거(공식 보도자료에 YouTube 링크 포함): https://www.visitbritain.org/news-and-media/industry-news-and-press-releases/visitbritain-launches-global-screen-tourism

### C) Lyric/MV: Text-as-shot 규칙 — “문장 자막”이 아니라 “타이포 장면”
- 관찰: lyric video는 가독(독해)과 리듬(음악)이 동시에 KPI다. 문장 자막처럼 길게 쓰면 리듬이 죽는다.
- 규칙(운영):
  1) 가사는 문장 단위가 아니라 **구/훅 단위**로 분절한다.
  2) 모션은 항상 **도착(settle) → 홀드**를 확보한 뒤 퇴장한다(홀드 없으면 모션 금지).
  3) 공공/공모전 버전은 lyric 규칙을 그대로 쓰지 말고, **설명은 정보 컷(챕터/엔드)로 이동**한다.
- 근거:
  - MJ lyric video: https://www.youtube.com/watch?v=F1YD52Flsfw
  - TK lyric video: https://www.youtube.com/watch?v=hWXWC5ePyN0
  - Aimer lyric video: https://www.youtube.com/watch?v=bB7FfMXjjAM

### D) CapCut Pro/기능 변동 리스크 — “Pro 가정 금지”를 납기 규칙으로 격상
- 관찰: 캡션 관련 기능(예: auto-highlight)이 Pro로 이동/삭제될 수 있다는 사용자 경험 보고가 존재.
- 규칙(운영):
  1) 공공/공모전 납품은 **Pro 기능 의존 디자인 금지**(특히 승인 전 최종본).
  2) 강조는 Pro 효과 대신 **기본 타이포(굵기/크기/컬러 1포인트)**로도 재현 가능한 설계를 우선.
- 근거: https://www.capeditcut.com/community/capcut/auto-highlight-caption-features-is-gone/

---

## Update 2026-05-13 08KST — 관광/공공 “텍스트 최소 개입” + 9:16 ALT 위치 자산화 + STT 45/99 납기 분기 고정

### A) Minimal text intervention (관광/공공) — “화면 텍스트는 훅 1개만, 나머지는 밖으로 회수”
- 문제: 공공/관광에서 설명 자막을 본편에 과다하게 넣으면 화면이 ‘광고문/홍보문’처럼 보이며, 미장센·감정선이 붕괴한다.
- 규칙(운영):
  1) 본편 화면 텍스트는 **브랜드 개념 훅 1개(예: OutHorse / Icelandverse / Passion)**만 남기고, 디테일은 **설명란/웹/고정댓글/엔드카드**로 회수한다.
  2) 텍스트가 정보 전달이 아니라 **톤/개그/컨셉(펀치라인)** 역할일 때는 *짧고 굵게 + 홀드*가 기본(문장형 금지).
  3) “정보가 꼭 필요”하면 본편 위에 얹지 말고 **정보 컷(정지/홀드가 있는 카드)**을 따로 만든다.
- 근거:
  - OutHorse(텍스트 최소 개입 + 링크는 설명/웹): https://www.youtube.com/watch?v=kbfD_lX1Tog
  - Icelandverse(패러디 포맷): https://www.youtube.com/watch?v=enMwwQy_noI
  - VisitSingapore(스케일 몬타주형): https://www.youtube.com/watch?v=BJE3HIkQ4zU

### B) “라벨링(이름 붙이기)”을 문장 자막의 대체재로 사용
- 관찰: 환경/정책 메시지도 문장으로 길게 설명하기보다 **이름(라벨)로 오브젝트화**하면 설교 느낌이 줄고, 화면 타이포 개입량도 줄어든다.
- 규칙(운영):
  - “설명 자막”이 필요해질수록 먼저 **라벨링 가능한 단어/명사**로 바꿔서(예: Kranavatn) 화면 텍스트를 줄인다.
- 근거(YouTube URL을 기사에서 명시): https://www.contagious.com/en/article/news-and-views/inspired-by-iceland

### C) 9:16 Typography placement — ALT 위치 3종을 “템플릿 자산”으로 선잠금
- 규칙(운영):
  1) 9:16은 기본 하단 unsafe를 넓게 잡고, 텍스트 위치를 **ALT 3종(상/중/측면)**으로 표준화해 프로젝트 자산으로 저장한다.
  2) 본문(장문/내레이션)은 “하단 중앙 고정”이 아니라 **컷의 미장센/피사체/플레이어 UI 충돌 여부**로 ALT 위치를 선택한다.
  3) CapCut JSON 좌표는 보조 수단이고, 최종은 **CapCut preview/export**에서만 판정한다(standing rule 재확인).

### D) CapCut STT 45%/99% 고착 — 납기 분기(Decision gate)로 고정
- 규칙(운영):
  1) 99% 고착(웹): **새로고침/이탈 금지**(작업 취소 리스크) → 대기 + 네트워크 안정화 우선.
  2) 45% 고착(데스크톱): 캡션 생성은 **격리 프로젝트**에서만 시도(메인 손상 최소화).
  3) 어떤 경우든 “샘플 구간 10–20초 + 캡션 포함 export-first gate” 통과 전에는 본편 작업을 확대하지 않는다.
- 근거:
  - CapCut 공식 Help(99%): https://www.capcut.com/help/recognition-of-subtitles-lagging
  - CapCut 공식 Help(auto captions): https://www.capcut.com/help/auto-captions
  - Reddit(99%): https://www.reddit.com/r/CapCut/comments/1r5ypbe/capcut_auto_captions_stuck_at_99/
  - Reddit(45%): https://www.reddit.com/r/CapCut/comments/1nszlra/my_capcut_captions_are_stuck_at_45/

### E) Text layer budget KPI — “주연 1 + 보조 1”을 기본값으로
- 규칙(운영):
  - 공공/관광 본편은 텍스트 레이어 수를 **주연 1 + 보조 1**로 제한하고, 3개 이상이 필요해지면 해당 장면을 **정보 컷(카드/정지/홀드)**로 분리한다.

---

## Update 2026-05-13 09KST — 몽타주형(screen tourism) safe-zone 템플릿화 + “공식 타임코드(anchor)” 기반 리듬 근거 + CapCut 자막 템플릿 시스템

### A) Montage(screen tourism) typography contract v3 — “테마 카드만 허용”
- 문제: 장면 변화가 매우 빠른 몽타주형은 본편 설명 자막이 들어가는 순간 (1) 컷 리듬 붕괴 (2) UI safe-zone 충돌 (3) 캡션 운영 비용 폭증이 발생한다.
- 규칙(운영):
  1) 몽타주형(관광/공공/브랜드) 본편 텍스트는 **테마 카드(genre/키워드)만** 허용한다.
  2) “설명/근거/수치/신청/링크”는 **카드 컷(정지/홀드) + 엔드 + 설명란/웹**으로 회수한다.
  3) 본편 중간에서 텍스트가 꼭 필요하면: **0.6–1.2초 진입 + 0.6초 이상 settle/hold**(도착 호흡) 없으면 금지.
- 근거:
  - VisitBritain press release(YouTube 링크 명시): https://www.visitbritain.org/news-and-media/industry-news-and-press-releases/visitbritain-launches-global-screen-tourism
  - Campaign US(구성/크레딧): https://www.campaignlive.com/article/visit-britain-%E2%80%9Cstarring-great-britain%E2%80%9D-pablo/1904235

### B) Safe-zone 운영을 “문서”에서 “오버레이 템플릿 PNG”로 승격
- 원칙(standing rule 연계): CapCut preview/export가 SoT이므로, safe-zone도 글로 외우지 말고 **프리뷰에서 항상 켠 오버레이**로 관리해야 한다.
- 규칙(운영):
  1) 9:16(1080×1920) / 16:9(1920×1080) 각각 **safe-zone 오버레이 PNG**를 만든다.
  2) CapCut에서 해당 PNG를 “가이드 레이어”로 항상 상단에 두고(최종 export에서는 숨김), 텍스트 위치는 오버레이 안에서만 결정한다.
  3) 오버레이 값은 최초엔 REF로 시작하되, **앱 스크린샷 기반**으로 VERIFIED로 승격한다(플랫폼 UI는 수시로 변함).
- REF 근거(비공식: 반드시 앱에서 재검증):
  - YouTube Shorts safe area: https://www.overlaycheck.com/youtube-shorts-safe-area
  - TikTok safe zones: https://www.ezugc.ai/blog/tiktok-safe-zones

### C) “공식 타임코드 제공 페이지”를 typography rhythm의 VERIFIED anchor로 채택
- 규칙(운영):
  - 공공/브랜드가 공식 사이트에서 **텍스트 타임코드**(예: 00:00:02 …)를 제공하는 경우, 해당 타임코드를 “리듬 근거”로 인용 가능(VERIFIED).
- 근거:
  - Seoul 공식 브랜드 영상(MP4 + 타임코드 표기): https://english.seoul.go.kr/seoul-my-soul-2/

### D) CapCut captions = “템플릿 시스템”으로 운영(폰트/위치/강조/라인 길이)
- 문제: 자막을 매 프로젝트·매 장면마다 즉흥 디자인하면, 납기/일관성/검수 비용이 급증하고 export에서 깨질 확률도 올라간다.
- 규칙(운영):
  1) 자막 스타일은 **역할별 프리셋 3종**으로 고정: (a) 내레이션(조용/near-unboxed) (b) 훅(강조) (c) 데이터(날짜/장소/수치).
  2) 9:16은 기본 하단 unsafe가 크므로, 자막 기본 위치를 **center-mid + ALT 3종**으로 운영한다.
  3) export-first gate: “샘플 구간 10–20초 + 캡션 포함 export” 통과 전에는 스타일 확정 금지.
- 근거:
  - CapCut subtitles formatting guide: https://www.capcut.com/ideas/ai-design/ai-design-for-subtitles-formatting
  - CapCut 공식 Help(99%): https://www.capcut.com/help/recognition-of-subtitles-lagging
  - CapCut 공식 Help(auto captions): https://www.capcut.com/help/auto-captions

---

## Update 2026-05-13 10KST — 몽타주형(screen tourism) 테마카드-only 재확인 + STT 고착을 납기 리스크로 통합 + CapCut 모션 타이포 “hold KPI”

### A) Montage(Screen-tourism) = Theme-card-only (v4)
- 관찰: VisitBritain ‘Starring GREAT Britain’은 보도자료에서 “블록버스터 몽타주 필름”임을 명시하며, YouTube 링크(본편/15s/30s)를 공식적으로 제공한다. 이 타입은 컷 전환이 빠르므로 장문 자막을 얹는 순간 독해가 붕괴한다.
- 규칙(운영):
  1) 몽타주형(장소 급변) 본편 텍스트는 **테마 카드(1–3단어) + 엔드 카드**로 제한.
  2) 설명/근거/링크/신청/수치는 **엔드/설명란/웹**으로 회수.
- 근거:
  - VisitBritain press release(YouTube 링크 포함): https://www.visitbritain.org/news-and-media/industry-news-and-press-releases/visitbritain-launches-global-screen-tourism

### B) STT/Auto-captions 고착(29/45/99%) = “납기 리스크” (Cross-tool)
- 관찰: CapCut은 99% 고착에 대한 공식 트러블슈팅을 제공하며, 커뮤니티에서는 29/45% 고착이 반복 보고된다. 또한 Clipchamp에서도 99% 고착이 최근 보고되어(서비스/플랜/서버 이슈 의심), STT는 특정 앱 문제가 아니라 **클라우드 의존 작업의 공통 리스크**로 취급하는 편이 안전하다.
- 규칙(운영):
  1) **export-first gate**: 10–20초 샘플 구간에서 (a) 캡션 생성 (b) 캡션 포함 export 가 ‘성공’하기 전엔 본편 확장 금지.
  2) **autocaption containment**: 캡션 생성/정리는 격리 프로젝트에서 수행 후 메인에 이식.
  3) 99% 고착(웹)은 새로고침/이탈 금지(작업 취소 리스크) → 대기 + 네트워크 안정화 우선.
- 근거:
  - CapCut help(99%): https://www.capcut.com/help/recognition-of-subtitles-lagging
  - CapCut help(auto captions): https://www.capcut.com/help/auto-captions
  - CapCut community(45%): https://www.capeditcut.com/community/capcut/capcut-subtitles-stuck-at-45/
  - CapCut community(29%): https://www.capeditcut.com/community/capcut/auto-captions-not-working/
  - Clipchamp 99% report: https://techcommunity.microsoft.com/discussions/microsoft-clipchamp-discussions/auto-caption-not-working-stuck-at-99/4513590

### C) CapCut Motion Typography = “move”가 아니라 “hold(도착 호흡)”이 KPI
- 관찰: 2026년 CapCut 모션 타이포 튜토리얼은 키프레임/커브/easing을 강조한다. 그러나 실무 QC 관점에서 중요한 것은 ‘많이 움직이는 것’이 아니라 **도착 후 읽을 수 있게 정지하는 구간(hold)** 이다.
- 규칙(운영):
  1) 모션 타이포는 항상 **도착(settle) ≥ 0.6초**를 기본값으로 확보(공공은 더 길게).
  2) hold가 확보되지 않으면 모션 금지(standing rule의 endpoint-hold를 CapCut 구현 규칙으로 재고정).
- 근거:
  - Matt Loui CapCut motion typography(2026): https://www.youtube.com/watch?v=CBE1PkDRONc

---

## Update 2026-05-13 12KST — Kinetic typography “breath” 규칙 + CapCut Apply-to-all QA 규칙(공식 help 근거)

### 1) Kinetic Typography Breath Rule (재사용 로직)
- 문제: 많은 튜토리얼/레퍼런스는 “텍스트가 움직인다”를 보여주지만, 실무에서 실패는 대부분 **읽기 시간(hold) 부족**에서 발생한다.
- 규칙(로직):
  1) 모든 타이포 이벤트는 아래 3구간으로 분해해 설계/검수한다.
     - `IN`(진입): 등장 방식(페이드/슬라이드/스케일/마스크/트래킹)
     - `SETTLE+HOLD`(도착+정지): 읽기 호흡(공공/관광은 더 길게)
     - `OUT`(퇴장): 의미 있는 전환(컷/음악/스토리 변화)에서만
  2) 기본값(시작점):
     - 공공/관광 본문(내레이션/설명): `HOLD >= 0.9s` 권장
     - MV 훅/강조(짧은 구): `HOLD >= 0.6s` (단, 음악/비트가 더 빠르면 문장 길이를 줄여 해결)
  3) `SETTLE+HOLD`가 확보되지 않으면: 모션을 줄이고 **텍스트 길이를 줄이는 것**이 먼저다(모션으로 해결 금지).
- 근거(레퍼런스):
  - kinetic typography 큐레이션(사례 설명에서 timing/word reinforcement가 반복 강조됨): https://www.creativebloq.com/typography/examples-kinetic-typography-11121304

### 2) CapCut “Apply to all captions”는 QA가 아니다 (운영 규칙)
- 문제: auto-captions 워크플로에서 “Apply to all”을 누른 뒤도 일부 캡션이 스타일을 놓치거나 지연 반영될 수 있다.
- 규칙(운영):
  1) Apply-to-all 이후 **10–15초 export 샘플**을 반드시 만든다(Preview-only 판정 금지).
  2) 일부 캡션만 스타일이 어긋나면: (a) 수동 편집/분절로 그룹에서 이탈했는지 (b) 플랫폼 차이/지연인지 먼저 분리 진단.
  3) 장문/캡션 블록 수가 큰 프로젝트는: “격리 프로젝트(containment)”에서 먼저 캡션 정규화 후 본편에 이식한다.
- 근거(공식 help):
  - CapCut help — Apply to all captions 오류/지연 가이드: https://www.capcut.com/help/fix-apply-to-all-captions-error


---

## Update 2026-05-13 11KST — 레퍼런스 URL 정규화(watch?v=) + 플랫폼 정책-우선 + REF→VERIFIED 승격 게이트

### A) 레퍼런스 URL은 무조건 `watch?v=VIDEO_ID`로 정규화(playlist/music/shorts는 보조)
- 문제: YouTube 링크는 `playlist`, `music.youtube.com`, `youtu.be`, `shorts/ID`, 지역 리다이렉트 등으로 흩어져 **데이터셋 중복/누락/깨짐**이 빈번하다.
- 규칙(운영):
  1) 위키/데이터셋에 보관하는 기본 키는 항상 `https://www.youtube.com/watch?v=VIDEO_ID`.
  2) `playlist`, `music.youtube.com`, `shorts` 링크는 “보조 링크”로만 기록(선택).
  3) 영상 ID만 확보되면, 429/접속제한 상황에서도 데이터셋은 유지된다(시각 QC는 나중에).
- 근거/도구(REF):
  - Filmot(인덱서): https://filmot.com/ (URL에서 VIDEO_ID를 안정적으로 노출하는 경우가 많음)

### B) 플랫폼 정책이 컷/타이포에도 직접 영향(배포 규칙 선확정)
- 관찰: YouTube는 **업로드 날짜** 기준으로 “최대 3분 세로/정사각=Shorts 분류”를 안내하고, 1분 초과 Shorts의 Content ID claim 상황에서 **재생/추천/수익화가 제한**될 수 있음을 안내한다.
- 규칙(운영):
  1) MV/공모전 제출용은 편집 시작 전에 “배포 경로(Shorts/Long) + 음원 권리/클레임 리스크”를 먼저 결정한다.
  2) 길이/포맷이 확정되기 전에는 자막 스타일(특히 하단 unsafe 의존)을 확정하지 않는다.
- 근거(공식):
  - YouTube Help — 3-minute Shorts + claim 안내: https://support.google.com/youtube/answer/15424877?hl=en

### C) REF→VERIFIED 승격 게이트(인덱서/문서/실재생의 역할 분리)
- 규칙(운영):
  - REF(인덱서/기사/보도자료)로는 **URL 확보 + 맥락(캠페인 목적/구조)**까지만 기록한다.
  - VERIFIED(실제 적용 규칙)로 승격하려면 반드시:
    1) 실제 재생으로 컷/자막 충돌/전환/가독성 확인
    2) CapCut preview/export에서 “겹침/흔들림/폰트 대체/자막 점프” 없는지 확인(SoT)
  - 이 게이트 없이 “폰트 선택/자막 위치/모션 강도” 규칙을 확정하면, 반복 수정 비용이 폭증한다.

---

## Update 2026-05-13 13KST — Campaign format split(Teaser/Highlights/Main/Shorts) + Description-as-recovery + Semantics-first line breaks

### 1) Campaign Format Split Rule (Teaser/Highlights/Main/Shorts는 타이포 시스템을 공유하지 않는다)
- 관찰: 동일 캠페인이라도 Teaser/Highlights/Main Episode/Shorts로 배포 포맷이 갈리며, 특히 Shorts는 플레이어 UI 때문에 하단 unsafe가 확대되는 경우가 많다.
- 규칙(운영):
  1) **포맷별 타이포 계약서**를 분리해서 만든다: `TEASER`, `HIGHLIGHTS`, `MAIN`, `SHORTS`.
  2) 동일 영상 ID라도 `watch`와 `shorts`는 **safe-zone/QC 체크리스트를 분리**한다(Shorts는 기본 ALT 위치 프리셋을 더 위로).
- 근거(레퍼런스):
  - VisitSeoul TV — Absolutely in SEOUL teaser: https://www.youtube.com/watch?v=vzytRSgfn_0
  - VisitSeoul TV — Main Episode 2(Shorts): https://www.youtube.com/shorts/5s9hm3CC1Ww

### 2) Episode-title first (에피소드명이 강한 캠페인은 본편 설명 자막을 줄인다)
- 관찰: 에피소드명이 이미 “스토리/테마”를 전달하는 경우, 본편에서 장문 설명 자막을 얹을수록 미장센·리듬·가독성이 동시에 무너질 가능성이 크다.
- 규칙(운영):
  1) 본편은 **라벨/키워드-only**를 기본값으로 두고, 설명은 (a) 초반 타이틀 카드 (b) 엔드 카드에서 회수한다.
  2) 내레이션형 문장은 본편에 얹지 말고(특히 관광/시네마틱), 필요 시 별도 “인터뷰/설명” 포맷에서 처리한다.
- 근거(레퍼런스):
  - VisitSeoul TV — Main Episode 1. DALTOKKI: https://www.youtube.com/watch?v=JEEi6E8vt-4

### 3) Description-as-recovery (공공/관광은 설명력을 ‘설명란/웹’으로 회수하는 전략이 강력하다)
- 관찰: 본편 온스크린 타이포를 절제한 대신, YouTube 설명란에 체험/장소/링크를 상세히 기록하면 “설명력”을 영상 밖에서 회수할 수 있다.
- 규칙(운영):
  1) 공공/관광 본편은 **가독성·톤**을 위해 텍스트를 줄이고,
     설명력은 (a) YouTube 설명란 (b) 고정댓글 (c) 랜딩 페이지로 회수하는 것을 기본 전략으로 둔다.
  2) 제출/심사용 패키지는 영상 내 텍스트를 늘리는 대신, **설명란/패키지 문서(의도/시놉시스/AI 활용)**로 근거를 보강한다.
- 근거(레퍼런스):
  - Imagine Your Korea — Koreans’ Korea: K-Experience(설명란에 체험 리스트): https://www.youtube.com/watch?v=H_2_jPT_jus

### 4) Semantics-first line breaks (줄바꿈은 폭/글자수보다 ‘의미 단위’가 우선)
- 관찰: 자막/캡션의 줄바꿈 실패는 “글자가 많아서”가 아니라 “의미 단위가 깨져서” 발생하는 경우가 많다. 일반 캡션 가이드라인은 2줄 제한과 문장 단위 줄바꿈 원칙을 제공한다.
- 규칙(운영):
  1) 1차 분절은 **발화 단위/의미 단위**로 한다(문장/구/조사-의존명사 분리 금지).
  2) 2차로 폭(2줄/unsafe)과 읽기 시간에 맞춰 재배치한다.
  3) CapCut에서 입력/줄바꿈이 꼬이면(IME/키보드/문자 제한) “툴 문제”로 분류하고 우회(분절/박스 폭/입력 방식 변경)를 우선 적용한다.
- 근거:
  - Subtitle line length 가이드(2줄/42 chars/line, 의미 단위 줄바꿈 원칙): https://enhancingaudiodescription.com/assets/docs/subs/captioning-guide
  - CapCut help(줄바꿈/입력 문제): https://www.capcut.com/help/entre-text-issue

---

## Update 2026-05-13 14KST — CapCut “length/line-break” 운영 규칙(한글 중심) + Auto Captions 납기 리스크 강화

### 1) Auto Captions는 ‘생성’부터 납기 리스크다(29/45/99% 고착)
- 관찰: Auto Captions 생성이 **진행률 특정 지점에서 멈춘다**는 사례가 반복 보고된다(29%, 45%, 99%).  
- 규칙(운영):
  1) Auto Captions는 항상 **격리 프로젝트에서 생성 성공**을 먼저 만든다.
  2) 메인 프로젝트에는 “정리된 캡션(세그먼트/줄바꿈/강조)”만 이식한다.
  3) 샘플 export 게이트는 **캡션이 포함된 구간**으로 수행(“캡션 없는 구간 export 성공”은 무의미).
- 근거:
  - CapEditCut forum (29% 고착): https://www.capeditcut.com/community/capcut/auto-captions-not-working/
  - CapEditCut forum (45%/99% 고착): https://www.capeditcut.com/community/capcut/auto-caption-issue/

### 2) CapCut “텍스트 잘림/중간 단어 분할”은 ‘문장 축약/세그먼트’로 해결한다(폰트 축소 금지)
- 관찰: 자동 캡션은 사람의 읽기 단위를 고려하지 않아 “한 블록에 과도한 글자”가 들어가면 줄바꿈/잘림/중간 단어 분할이 생길 수 있다(특히 모바일).
- 규칙(운영):
  1) 해결 우선순위는 **문장 축약/세그먼트 분할 → 박스 폭/안전영역 조정 → (마지막) 폰트 크기**.
  2) 공공/관광/내레이션은 글자 크기 축소로 해결하지 말고, **정보를 카드/엔드로 회수**한다.
- 근거:
  - CapCut help(캡션 수정/재세그먼트/재인식): https://www.capcut.com/help/auto-captions-in-capcut
  - 서드파티 운영 힌트(숨은 길이/라인브레이크 경향): https://videowizardtools.com/capcut-captions-too-long-fix/

### 3) (Heuristic) “라인/블록 글자수”는 고정 규칙이 아니라 ‘사전 경보(threshold)’로만 쓴다
- 관찰(서드파티): 약 **~35–40 chars/line**, **~80–100 chars/block**에서 문제 패턴이 생긴다는 경험칙이 공유된다.
- 규칙(운영):
  - 위 수치는 “절대 기준”이 아니라 **경보 임계치**로만 사용한다.  
    실제 한글/폰트/자간/박스 폭/해상도에 따라 달라지므로 반드시 **CapCut preview + 샘플 export**로 검증한다.
- 근거:
  - https://videowizardtools.com/capcut-captions-too-long-fix/

### 4) 줄바꿈/입력 불가 문제는 “IME/키보드 Enter 동작/문자 제한”으로 분류하고 우회한다
- 관찰: Enter가 “Done”처럼 동작하거나 문자 제한에 걸리면 줄바꿈이 안 되거나 더 입력이 안 될 수 있다.
- 규칙(운영):
  1) (모바일) New Line/Return 키를 강제하거나 키보드 레이아웃을 바꾼다.
  2) 박스 폭/텍스트 크기를 조정해 “툴의 자동 줄바꿈”이 터지지 않게 만든다.
  3) IME 전환(한/영/다른 키보드)으로 재시도한다.
- 근거:
  - CapCut help(줄바꿈/문자 제한/IME): https://www.capcut.com/help/entre-text-issue

### 5) “YouTube 사례 풀(30개)”는 dataset에 바로 ‘규칙’로 가져오지 말고, VERIFIED 관찰로 승격한다
- 규칙(운영):
  - 레퍼런스 링크 풀은 `REF`로 저장하고, 실제 재생 관찰(타이포 출현 시점/좌표/전환/읽기 호흡)을 기록하면 `VERIFIED`로 승격한다.
- 근거(풀):
  - Imagine Your Korea Filmot 채널 리스트: https://filmot.com/channel/UChhOtjq-3QyyLmP2jv9amrg/3/Imagine%2BYour%2BKorea

---

## Update 2026-05-13 15KST — CapCut “99% 멈춤” 대응 표준화 + CC vs 영상 내 타이포 분리

### 1) CapCut Auto Captions “99% 멈춤” 대응은 3단계 표준(강제종료 금지)
- 관찰: CapCut 공식 help는 99%에서 멈춰 보이는 현상이 “완료 콜백/렌더/동기화 지연”일 수 있음을 전제하고, 플랫폼별로 ‘대기/환경 점검/재시도’를 권한다.
- 규칙(운영):
  1) **대기(5–10분)**: UI가 멈춰 보여도 처리 중일 수 있으므로 즉시 중단하지 않는다.
  2) **리소스 확인**(Desktop): Activity Monitor/작업관리자에서 CPU·RAM·디스크 활동이 있는지 본다.
  3) **진짜 동결이면 재시작(무저장)**: 5분 이상 활동이 없으면 강제종료→재실행(자동 저장/중간 결과 복구 기대).
- 근거:
  - CapCut help: https://www.capcut.com/help/recognition-of-subtitles-lagging

### 2) Auto captions “안 됨”은 원인 분류(오디오/언어/네트워크/버전) 체크리스트부터
- 규칙(운영):
  - 실패 시 바로 ‘템플릿/스타일’ 탓으로 돌리지 말고, (a) 음성 트랙 존재·볼륨 (b) 언어 설정 (c) 네트워크 (d) 앱 버전 순서로 원인 분해 후 재시도.
- 근거:
  - CapCut help: https://www.capcut.com/help/auto-captions

### 3) 플랫폼 CC(Closed captions)와 “영상 내 타이포”는 목적이 다르다 → 분리 운영
- 관찰: YouTube는 시청자 측에서 자막 폰트/크기/배경/edge 스타일을 변경할 수 있다.
- 규칙(운영):
  1) 접근성/다국어 확장은 **CC(플랫폼 자막 파일)** 로 해결한다.
  2) 브랜딩/정보 위계/리듬(음악-비트 기반)은 **영상 내 그래픽 타이포 레이어**로 해결한다.
  3) 공모전/공공은 “영상 내 타이포”를 역할 분리(타이틀/장소/본문/고지)로 설계하고, CC는 보조로 둔다.
- 근거:
  - YouTube Creator Academy: https://creatoracademy.youtube.com/page/lesson/community-contributions

### 4) 관광/공공 브랜드 필름 구조: “슬로건 반복+리듬” / 정보는 회수 컷으로
- 규칙(운영):
  - 본문 컷에 장문을 얹기 시작하면 (a) 하단 unsafe 침범 (b) 박스 자막(사용자 비선호) (c) 컷 리듬 붕괴로 이어지기 쉬움.
  - 기본값: **감정/정서(본문) ↔ 정보 회수(챕터/엔드/설명란/패키지 문서)** 분리.
- 근거(대표 레퍼런스):
  - Dubai Presents: https://www.youtube.com/watch?v=fuSpjxrdhTw
  - Saudi ‘This Land is Calling’(공식 배포/크레딧 근거): https://www.prnewswire.com/news-releases/saudi-tourism-launches-this-land-is-calling-campaign--an-enticing-invitation-to-discover-the-heart-of-arabia-302232955.html / https://www.betc.com/en/work/this-land-is-calling
  - STB ‘Made in Singapore’(공식 보도자료): https://www.stb.gov.sg/about-stb/media-publications/media-centre/singapore-tourism-board-launches-made-in-singapore-global-campaign-to-inspire-travel-to-singapore/

---

## Update 2026-05-13 16KST — “케이스 근거 레벨” + CC vs 영상 내 타이포 분리 운영

### 1) 레퍼런스 신뢰 레벨(REF→VERIFIED)을 ‘케이스 근거’까지 포함해 3단으로 나눈다
- 문제: YouTube 링크만 저장하면 “무슨 점이 좋은지”가 빠르게 소실되고, 중복이 늘어난다.
- 규칙(운영):
  - **L1 (REF-link):** YouTube URL만 확보(관찰 대기열)
  - **L2 (REF-case):** YouTube URL + 공식/케이스 페이지(제작 의도·크레딧·맥락) 링크를 함께 저장
  - **L3 (VERIFIED):** 실제 재생 관찰(타임스탬프/타이포 등장 타이밍/배치/읽기 호흡/컷 리듬)까지 기록
- 근거(예시):
  - Google Year in Search film: https://doodles.google/doodle/year-in-search-2025-film/
  - BUCK Childline First Step: https://buck.co/work/childline-first-step

### 2) CC(Closed captions)와 “영상 내 타이포”는 목적/제약이 다르다 → 역할 분리 표준
- 관찰: YouTube는 시청자 측에서 자막 폰트/크기/배경/edge 스타일을 변경할 수 있다.
- 규칙(운영):
  1) **접근성/다국어 확장 = CC(플랫폼 자막 파일)**
  2) **브랜딩/정보 위계/리듬(음악-비트 기반) = 영상 내 타이포 레이어**
  3) 공공/공모전은 영상 내 타이포를 **역할 분리(타이틀/장소/본문/고지)**로 설계하고, CC는 보조로 둔다.
- 근거:
  - YouTube Creator Academy: https://creatoracademy.youtube.com/page/lesson/community-contributions
  - YouTube Help(자막 파일/타이밍 개념): https://help.youtube.com/support/youtube/bin/answer.py?answer=100076

### 3) 템플릿/프리셋은 “기법 참고용”으로만 사용(특히 공공/관광)
- 문제: kinetic typography 템플릿은 그대로 쓰면 ‘프리셋 티’가 나서 공공/관광 톤을 해친다.
- 규칙(운영):
  - 템플릿은 (a) 이징/타이밍/레이어 구성 참고로만 사용하고
  - 최종본에서는 **폰트/리듬/여백/컬러/모션 총량을 프로젝트 톤에 맞춰 재설계**한다.
- 근거(템플릿 데모/가이드):
  - CapCut 리소스(키네틱 텍스트): https://www.capcut.com/resource/kinetic-typography-animations/

---

## Update 2026-05-13 17KST — 레퍼런스 정규화(YouTube) + 몽타주 텍스트 예산 + 사운드 드리븐(관광) 타이포 최소화

### 1) YouTube 사례 데이터 “정규화 규칙” (중복 제거의 핵심)
- 문제: 동일 영상이 `youtu.be/`, `watch?v=`, `&t=`, `&feature=share` 등으로 흩어지면 데이터셋이 쉽게 중복·오염되고, “관찰/검증 큐”가 깨진다.
- 규칙(재사용 로직):
  - 저장 키는 항상 `https://www.youtube.com/watch?v=VIDEO_ID`로 통일한다.
  - 파라미터(`&t=...`, `&feature=...`)는 **본문 레퍼런스**가 아니라 **관찰 노트(L3) 타임스탬프**에만 남긴다.
  - `youtu.be/VIDEO_ID`는 저장 시 `watch?v=`로 변환한다.
- 근거/테스트 케이스:
  - Year in Search 2025(원본): https://www.youtube.com/watch?v=Vv_sjpclsZ8 (파생 링크는 정규화 대상)

### 2) “공식 케이스/보도자료 링크(L2)” 동반 우선 규칙 (신뢰+재현력)
- 규칙(재사용 로직):
  - 가능하면 항상 “영상 링크 + 공식 케이스 페이지/보도자료/툴킷”을 한 묶음으로 저장한다.
  - 이유: (a) 제작 의도/제약 (b) 타깃/배포 맥락 (c) 크레딧/툴체인 (d) 버전(컷다운) 구조가 남는다.
- 예시:
  - JKR case + YouTube: https://www.jkrglobal.com/work/burger-king + https://www.youtube.com/watch?v=OBTn6ttQje0
  - Travel Switzerland 기사 + YouTube: https://www.travelswitzerland.com/20-million-views-for-swiss-sounds/ + https://www.youtube.com/watch?v=o1DUmOD9Nmw
  - VisitScotland toolkit(YouTube 명시) + 영상: https://toolkit.visitscotland.org/asset-page/111560-visitscotland-launches-responsible-tourism-campaign + https://www.youtube.com/watch?v=Q1HBKnnGr-g

### 3) 몽타주/리캡(초고밀도 컷)에서는 “장문 자막”이 리듬을 깨뜨린다 → 텍스트 예산 규칙
- 신호:
  - 컷 밀도가 높고(1초대 컷이 연속), 정보가 영상 자체에 과포화인 형태(연말 리캡/하이라이트/캠페인 몽타주).
- 규칙(공공/관광/브랜드 공통):
  - 본편: **라벨/훅(짧은 명사/동사)**만 허용
  - 정보 설명: **엔드카드/설명란/랜딩 페이지**로 회수
  - 접근성/다국어: **CC(SRT 등)**로 분리 운영
- 대표 레퍼런스:
  - Year in Search 2025: https://www.youtube.com/watch?v=Vv_sjpclsZ8
  - Year in Search 2024(원본 ID 확인): https://www.youtube.com/watch?v=61JHONRXhjs

### 4) “사운드 드리븐 관광 필름”은 타이포를 더 줄여야 톤이 산다 (음악이 이미 리듬/정보를 운반)
- 규칙(관광/공공 적용):
  - 음악/사운드가 메시지를 운반하는 경우(필드레코딩/뮤직비디오형 관광 필름), 본편 타이포를 늘리면 “프레젠테이션화”된다.
  - 필요한 정보는 챕터/엔드 슬레이트/설명란으로 회수한다.
- 근거:
  - THYLACINE - Swiss Sounds: https://www.youtube.com/watch?v=o1DUmOD9Nmw

### 5) CapCut auto-captions는 ‘기능’이 아니라 ‘납기 운영’으로 통제한다 (export-first gate)
- 규칙(재사용 로직):
  - 본편 전체 작업 전에 **60초 샘플 구간**에서 (a) 줄바꿈 (b) 위치 고정 (c) export 성공까지 통과시키는 “export-first gate”를 수행한다.
  - gate 실패 시: auto-captions 의존도를 낮추고, 수동 텍스트/CC(SRT)/외부 캡션 파이프라인으로 전환한다.
- 근거:
  - CapCut help (export stuck): https://www.capcut.com/help/export-stuck
  - CapCut forum (캡션 흩어짐/블록 이동 문제): https://www.capeditcut.com/community/capcut-pro/how-can-create-the-same-style-captions/
  - Reddit (캡션 위치/제어 불만): https://www.reddit.com/r/CapCut/comments/1rdl33g/capcut_captions_are_garbage/


---

## Update 2026-05-13 18KST — Kinetic 타이포 “속도↔문장길이” 규칙 + CapCut 폰트/Export 재현성 게이트 강화

### 1) Kinetic Typography 선택 로직: “속도 문제”는 타이밍보다 문장 길이로 해결한다
- 문제: 자막/타이포가 ‘너무 빨라서 못 읽힘’ → 타이밍을 늘리면 컷 리듬(특히 MV/Shorts)이 무너진다.
- 규칙(재사용 로직):
  - 텍스트가 빨라져야 한다면(컷/음악이 빠르다면) **문장을 줄여라.**
  - “빠른 타이포”에서 허용 가능한 단위는 (a) 1–3단어 키워드 (b) 숫자/지표 (c) 아주 짧은 절(<= ~8자 한글 기준) 중심.
- 근거(레퍼런스 풀):
  - thinkmedia kinetic typography list(Apple Don’t Blink 포함): https://thinkmedia.de/kinetic-typography-videos/

### 2) CapCut 폰트 재현성 규칙: ‘System’은 폰트가 아니라 환경 변수 → 레퍼런스/최종본 금지
- 문제: CapCut의 “System” 레이블은 OS/디바이스 UI 폰트에 종속되어 버전/환경에 따라 바뀔 수 있음.
- 규칙(운영):
  - **System 계열 폰트는 레퍼런스/최종본에서 금지**(협업/재수정/납기에서 재현 불가).
  - 폰트는 프로젝트 착수 시점에 “폰트 락(2~3종)”으로 고정하고, 60초 샘플 export에서 렌더 보존을 확인.
- 근거:
  - CapEditCut forum(“System font label confusion”): https://www.capeditcut.com/community/video-editing/need-help-identifying-a-missing-font-in-capcut/

### 3) 문자셋(언어) 호환성은 애니메이션 프리셋에도 영향을 준다 → 10초 샘플 게이트
- 문제: 비라틴(키릴 등)에서 프리셋/애니메이션이 깨질 수 있음. 한글도 동일 리스크 범주로 취급해야 안전.
- 규칙(운영):
  - **한글 자막/타이포는 “프리셋/모션”을 본편 전체 적용 전에 10초 샘플로 검증**한다.
- 근거:
  - CapEditCut forum(Cyrillic animation issue): https://www.capeditcut.com/community/capcut/adding-captions-in-cyrillic/

### 4) CapCut Mac 운영 전제: 템플릿이 없다고 가정하고(또는 제한적이라고 가정하고) 설계한다
- 규칙(운영):
  - 템플릿 의존 금지. 키프레임/가이드라인/자체 프리셋으로 재현 가능한 타이포 시스템을 만든다.
- 근거:
  - CapEditCut forum(Mac templates missing): https://www.capeditcut.com/community/templates/missing-templates-on-capcut-mac/

### 5) Export-First Gate 확장: 텍스트/폰트/애니메이션이 “export 후” 보존되는지까지 검증해야 한다
- 문제: 편집 화면에서 보이던 폰트/효과/애니메이션이 export에서 누락/변형될 수 있음.
- 규칙(운영):
  - 본편 제작 전 **60초 샘플 export**에서 (a) 텍스트 노출 (b) 폰트 유지 (c) 애니메이션/효과 유지까지 확인한다.
  - 실패 시: 프로젝트 복제본에서 재현 테스트 후, auto-captions/특정 프리셋/특정 폰트 의존도를 낮춘다.
- 근거:
  - CapEditCut(Effects/fonts missing after export): https://www.capeditcut.com/capcut-effects-not-working-fix-for-latest-version-fonts-animations-too/
  - CapCut help(text not appearing): https://www.capcut.com/help/text-not-appearing

---

## Update 2026-05-13 19KST — L3(VERIFIED) 승격 최소증거 + CapCut 캡션 Export 실패 진단 트리(공식 Help)

### 1) 레퍼런스 신뢰도 규칙: L3(VERIFIED) 승격은 “watch 링크 + 근거 페이지”가 최소 조건
- 문제: YouTube watch 링크만 저장하면 (a) 접근 불안정(429/임베드 편차) (b) 업로더 불명확 (c) 나중에 링크 사라짐/지역 제한 등으로 “검증 불가” 상태가 자주 발생한다.
- 규칙(운영):
  - L1(REF): watch 링크만 있어도 됨(단, 중복 제거는 `watch?v=` 정규화로 수행).
  - L2(REF+CONTEXT): watch 링크 + 설명/기사/제작사 페이지 중 1개 동반.
  - **L3(VERIFIED): watch 링크 + (어워드/제작사/공식 케이스 페이지) 동반 + (가능하면) 타임스탬프 기반 관찰 노트**.
- 실무 적용:
  - 공공/관광/기관 제출용 레퍼런스는 L2 이상만 사용(맥락/근거 없는 링크는 회의에서 설득력이 낮음).

### 2) CapCut 공식: “Captions fail to export” 진단 트리(납기 운영 규칙)
- 출처(공식 Help): https://www.capcut.com/help/captions-fail-to-export
- 핵심 요약(규칙 형태):
  1) **Auto Caption Recognition으로 생성된 캡션만 export 대상**일 수 있다(수동 텍스트를 ‘캡션 export’로 기대하지 않는다).
  2) Export에서 **Video Export가 아니라 Caption Export**를 선택해야 한다(형식 SRT/TXT).
  3) export 경로는 **ASCII만 사용**(특수문자/비라틴 경로 회피).
  4) 문제가 있으면 **TXT로 먼저 export → 외부 도구로 SRT 변환**(Plan B).
  5) 인코딩 이슈(예: UTF-8 BOM 등)가 있을 수 있으므로, 깨짐/미노출이면 인코딩을 점검한다.
  6) 버전 제한 가능 → 최신 버전 업데이트를 기본 전제로.
- standing rules 결합:
  - “CapCut preview/export가 source of truth”이므로, **샘플 export-first gate**에서 ‘캡션 export 성공’까지 포함해 통과시키고 본편 스타일을 확정한다.

---

## Update 2026-05-13 20KST — Kinetic Typography 15-case 규칙화 + Threads/Shorts 세로 안전영역 + CapCut 공식 캡션 Export/Import

### 1) 리캡/몽타주(Year-in-Search류) 타이포 기본값: “라벨 우선, 설명은 패키지로 분리”
- 문제: 몽타주 컷은 컷 밀도가 높아, 장문 자막은 읽히지 않고 미장센/UI와 충돌한다.
- 규칙(운영):
  - 본편 타이포는 **짧은 라벨(키워드)** 중심으로만.
  - 맥락/설명은 **엔드카드/챕터 카드/별도 문서(제작 의도/시놉시스/설명 캡션 패키지)** 로 회수.
- 근거(공식 컨텍스트):
  - Google Year in Search 2025 소개: https://blog.google/products/search/year-in-search-2025/

### 2) 민감/공공 주제 타이포 톤 규칙: “과장 모션/박스형 자막보다 홀드+위계”
- 규칙(운영):
  - 민감/신뢰형(공공/기관/상담/안전) 주제는 **팝업/바운스/과한 강조 박스**를 기본값으로 금지에 가깝게 운영.
  - 대신: **차분한 대비(화이트/오프화이트 + 다크 섀도/스트로크) + 충분한 홀드**로 신뢰 확보.
- 근거(공식 케이스):
  - BUCK — Childline: First Step: https://buck.co/work/childline-first-step

### 3) Threads/Shorts 세로 대응 규칙: “ALT 자막 위치 세트를 프리셋 자산으로 선제 구축”
- 문제: 세로 플랫폼 UI(오른쪽 레일/하단 메타)가 텍스트를 덮어 가독성이 무너진다.
- 규칙(운영):
  - 프로젝트 시작 시 **ALT placement set**(상/중/측면) 3종을 만든 뒤, 컷마다 안전영역에 맞게 선택.
  - 하단 중앙 본문 자막은 기본값으로 위험(플랫폼/미장센 충돌).
- 근거(Threads 맥락 + safe zone 도구):
  - Threads video guide: https://www.kapwing.com/resources/threads-video/
  - Shorts safe zone checker(예): https://tareno.co/tools/youtube-shorts-safe-zone-checker

### 4) CapCut 공식 캡션 export 운영 표준(다시 명문화)
- 규칙(운영):
  1) **Auto Caption Recognition으로 생성된 캡션만 export 대상**일 수 있다.
  2) Export에서 **Caption Export(SRT/TXT)** 를 선택해야 한다(= Video Export와 분리).
  3) export 경로는 **ASCII만 사용**.
  4) 실패 시 **TXT로 먼저 export → 외부에서 SRT 변환**.
  5) 인코딩/버전 문제를 점검.
- 근거(공식 Help):
  - Captions fail to export: https://www.capcut.com/help/captions-fail-to-export

### 5) CapCut 자막 import 제약을 파이프라인 전제에 포함
- 규칙(운영):
  - 외부 자막 파일 import는 **CapCut Desktop/Web 중심**으로 설계하고, Mobile은 제한을 기본 전제로 한다.
- 근거(공식 Help):
  - How to import subtitles: https://www.capcut.com/help/how-to-import-subtitles

## Update 2026-06-08 KST — ACC caption-sense failure: weak shadow is not design
- Trigger: User rejected ACC CapCut export because subtitles remained visually unchanged and generic despite wiki/font work.
- Lesson: Font proof and editable CapCut layers are necessary but not sufficient. Typography must show role/scene-specific contrast decisions.
- Add [[video-typography-shadow-legibility-playbook]] to preflight for every CapCut public-contest/tourism edit.
- New reject pattern: repeating the same white text, same stroke, same shadow, same corner alternation across scenes. This is “safe subtitle paste,” not public-film typography.
- New pass pattern: each text event declares contrast mode (dark-on-bright / ivory-on-dark / mixed-background body / disclosure), with explicit fill, rim stroke, shadow alpha/smoothing/distance, placement rationale, and phone-scale export proof.
