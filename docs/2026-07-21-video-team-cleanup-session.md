# 영상팀 워크플로우 대정리 세션 기록 — 2026-07-21

Claude Code(Fable 5)와 진행한 시댄스 레인 진단 → 리포 동기화 → 게이트 도입 → 헤르메스 퇴역 전 과정 기록.

---

## 1. 최초 진단: 컴퓨터 유즈가 꼬이던 원인

증상: 코덱스 영상팀 시댄스 레인에서 잘 되던 컴퓨터 유즈가 꼬임. 원인은 스킬 하나가 아니라 **4개 파일에 같은 규칙이 겹겹이 쌓이며 모순 지시가 동시 로드되는 구조**였음.

### 동시 로드 규모 (당시 기준)

| 파일 | 줄 수 | Seedance 언급 |
|---|---|---|
| `~/.codex/AGENTS.md` | 475줄 | 35회 |
| `seedance-prompt-en/SKILL.md` | 1,028줄 (이후 1,155줄까지 증가) | 63회 |
| `videodirector/SKILL.md` | 494줄 | 22회 |
| `music-video-production-team/SKILL.md` | 464줄 | 19회 |

seedance-prompt-en의 트리거가 "Seedance 언급 시 MUST load"라 사실상 4개 전부 활성화. 동일 규칙(continuity multi-reference, provider-lane separation 등)이 4벌씩 verbatim 복사돼 있었음.

### 4대 고장 모드

1. **살아있는 모순 규칙**
   - 레퍼런스 업로드: 05-17 "빈 슬롯에 한 장씩" vs 05-18 "세트로 한꺼번에 드래그" — 둘 다 현역, 파일 내 배치도 날짜순 아님
   - MCP vs Computer Use: config.toml엔 Runway MCP 설정, 07-06 정정은 "MCP 금지"
   - 음성 라우트: V58~V79 "@Audio1 없으면 대사 생성 금지" vs V84 "네이티브 대사가 활성 루트" — 5겹 패치 전부 조건부 현역
2. **프리플라이트 폭발**: Generate 1클릭에 검증 지시 수십 개(창 잠금, 드롭별 썸네일 검증, 픽셀 비교, Lexical 상태, provider matrix 7필드…) → 컨텍스트가 검증 노트로 가득 차 실조작이 밀림
3. **패치-온리 성장**: 문제 생길 때마다 dated 섹션 append, 삭제·통합 없음 (백업 파일 십수 개가 증거)
4. **음성 패치 5겹**(V15→V84): 어떤 게 현행인지 파일만으론 판별 불가

## 2. 크롬 컴퓨터유즈(브라우저 DOM 제어) 방식 평가

결론: **구조적으로 적합** — 고장 모드와 1:1 대응 해결.

- 창 미스라우트 원천 소멸 (DOM은 탭/엘리먼트 지정 조작)
- Runway의 Lexical 에디터 프롬프트 주입이 네이티브로 가능 (`__lexicalEditor.setEditorState`)
- 검증이 스크린샷 → DOM/네트워크 텍스트로 전환되어 컨텍스트 절약

걸림돌: ① 크롬 플러그인 네이티브 호스트 미연결(`chrome-native-hosts-v2.json` entries 비어있음), ② config.toml("크롬 우선")과 AGENTS.md("Safari/CU")가 새 모순쌍이 되므로 07-06 라우팅 문구 개정 필요. 유지할 규칙: 썸네일 순서 = 성공 판정, 한 장씩 업로드, Generate 클릭 확인 정책. **현재는 Safari + Computer Use 경로가 현행이며 크롬 전환은 미착수.**

## 3. GitHub 리포(video-team-workflow) 대조·동기화

리포 구조(운용 정책 분리, 패치 레이어 제거)는 올바른 방향이었으나 `codex-skills/`가 7월 초 이전 스냅샷이라 **리포 내부 자기모순** 존재. 수정·푸시:

- **[31da96f]** 로컬 현행 진실로 동기화: 07-12 직접 드래그 정정본으로 교체(06-12 asset-selector 규칙 폐기), imagegen 기본 라우팅, Seedance-primary/Grok-fallback, 07-21 프롬프트 지식(Seedance2.ai 가이드·Higgsfield) 포팅, 통합 음성 게이트(06-30)+V84만 채택, provider/continuity 규칙 ops 파일화

### Codex 병렬 통합 (같은 날, Codex 세션이 독자 푸시)

- **[30d4586] / [3b303d5]** 시댄스 스킬을 1,155줄 → **117줄 단일 실행 계약**으로 붕괴 (8체크 프리플라이트, "one scene one state", 구버전은 `archive/`로), GLOBAL_AGENTS.md 추가, 로컬 AGENTS.md도 475→345줄 정리
- 리베이스로 통합, 충돌 해소 후 그 위에 게이트 반영

## 4. 서브에이전트 스폰 승인 게이트 + latest-only 원칙

- **[2d2cf42]** 게이트 도입: 레인/서브에이전트/사이드카/스케줄러·모니터·크론/병렬 자동화 루프 스폰 = **건별 사용자 승인 필수**. 승인 요청은 레인 id/역할·목적·산출물 명시. 기본 실행 모델 = 단일 에이전트 순차 진행. 유일한 사전 승인 예외 = 시댄스 계약의 15분 Generate-큐 옵저버(큐 활성 중에만)
- **latest-only 원칙**: 활성 규칙 파일엔 현행 규칙만. 정정은 제자리 수정/삭제, dated 레이어 append 금지. 히스토리·롤백 = git
- **[5a0cb27]** 게이트 반영된 GLOBAL_AGENTS.md 동기화
- 적용 위치: `team-policies/subagent_approval_gate_20260721.md`(정책 원문), 스킬 3종 상단 요약, `~/.codex/AGENTS.md`

### 배포·아카이브 체계

- 정본 = GitHub `GnuDaSsa/video-team-workflow`, 로컬 작업 사본 = `~/Documents/Codex/video-team-workflow`
- `~/.codex/skills` = 배포 대상 → `tools/deploy_skills_to_codex.sh` (교체본 자동 아카이브)
- 백업 잔해 24개(AGENTS.md.backup*, config.toml.bak*, 스킬 .backup*) → `~/.codex/archive/20260721_delayering/`로 이동, 스킬 폴더엔 현행 파일만

## 5. 헤르메스 레이어 완전 제거

### 리포/규칙 층 — **[3c82d9d]**

- `codex-video-runtime/` 통삭제 (헤르메스 관제 + 디스코드 페르소나 + `~/.hermes` 경로 전제의 위임 레인 스캐폴드; `references/character_sheet_prompt_standard.md`만 `references/`로 구출)
- videodirector "Hermes-global routing" → "**Codex-native routing**" (Codex가 유일한 진입점·실행 소유자, 외부 오케스트레이터/사이드카/릴레이 금지)
- `wiki-extract/video-team-seed-system.md` 삭제(순수 헤르메스/디스코드 운영), 나머지 seed 2개는 헤르메스 참조만 제거
- README에 Codex-native boundary 명문화

### 시스템 층 — `~/Archives/hermes-retired-20260721/` (8GB)

| 하위 | 내용 |
|---|---|
| `hermes/` | 구 `~/.hermes` 전체 (agent venv, MMRN 런타임, 프로젝트, 로그) |
| `launchagents/` | ai.hermes.gateway / gateway-director / mmrn-monitor plist + .bak |
| `bin/` | 구 `~/.local/bin` hermes 런처 8종 |

절차: LaunchAgent 언로드 → 프로세스 3개 종료(7/13부터 터미널에 떠있던 대화형 세션 포함) → 이동. 검증: `~/.hermes` 없음, launchd hermes 0건, bin 잔재 0건. 재부팅해도 되살아나지 않음.

## 6. 위키(~/wiki) 헤르메스 조사 — **미결**

총 175개 헤르메스 파일 발견:

- **기록(보존 대상)**: `raw/transcripts/hermes-session-capture-*.md` 167개 — "과거는 기록으로만" 원칙에 부합, 그대로 둠
- **죽은 인프라(청소 대상, 미처리)**: 활성 층 8개 — `scripts/hermes_session_capture.py`, `_meta/hermes-session-ingest-state.json`, `_meta/hermes-dataset-pipeline.md`, `_dashboards/hermes-operations-dashboard.md`, `concepts/hermes-usage-patterns.md`, `entities/hermes-agent.md`, `comparisons/hermes-interface-usage.md`, `queries/hermes-weekly-usage-*.md`
- `index.md`에 헤르메스 항목 6건 잔존(활성 표면 오염) — 위키 루트 AGENTS.md는 0건으로 깨끗

제안된 후속: 8개를 `~/wiki/_archive/`로 이동 + index 항목 제거 (승인 대기 상태).

## 7. 롤백 방법

- 규칙/스킬: 리포에서 `git log` → `git checkout <commit> -- <파일>`
- 로컬 스킬 배포 직전본: `~/.codex/archive/<타임스탬프>_skill_deploy/`
- 백업 잔해: `~/.codex/archive/20260721_delayering/`
- 헤르메스 복원: `~/Archives/hermes-retired-20260721/`의 세 폴더를 원위치 후 plist 재로드

## 커밋 이력 요약

| 커밋 | 내용 |
|---|---|
| c2e302f | 최초 패키지 생성 (세션 이전) |
| 31da96f | 로컬 현행 진실로 스킬 동기화 |
| 30d4586 / 3b303d5 | Codex 자체 통합: 시댄스 단일 계약 붕괴 |
| 2d2cf42 | 서브에이전트 승인 게이트 + latest-only + 배포 스크립트 |
| 5a0cb27 | GLOBAL_AGENTS.md 게이트 동기화 |
| 3c82d9d | 헤르메스 레이어 제거, Codex-native 단독 소유 |

---

## 8. Follow-up version-up (same day, v2)

See `docs/2026-07-21-video-team-version-up.md`.

Chrome hybrid operator + dual in-flight were formalized after this cleanup record. The "Chrome path not started" note in section 2 is superseded by that version-up.
