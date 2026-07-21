# 영상팀 워크플로우 버전업 — 2026-07-21 (v2)

기준 문서: `docs/2026-07-21-video-team-cleanup-session.md`  
적용 커밋 기반: `a94060b` (cleanup record) 이후 패키지 상태.

---

## 1. 클린업 세션에서 이어받은 것 (유지)

| 항목 | 상태 |
|---|---|
| 시댄스 규칙 단일 계약 (`seedance-prompt-en`) | 유지·확장 |
| 서브에이전트 건별 승인 게이트 | 유지 |
| latest-only (활성 파일에 현행만) | 유지 |
| Hermes / `codex-video-runtime` 제거 | 유지 |
| 정본 = GitHub, 배포 = `deploy_skills_to_codex.sh` | 유지 |
| 8체크 프리플라이트 / one-file drag / 썸네일=증거 | 유지 |

클린업 §2에 “크롬 전환은 미착수”로 남아 있던 항목을 **v2에서 착수·정식 규칙화**.

---

## 2. v2에서 바꾼 것

### 2.1 Chrome hybrid operator (신규 정책)

파일: `team-policies/chrome_hybrid_operator_20260721.md`

- Runway는 **Chrome 한 탭**에서만.
- **드래그(첨부)** = desktop Computer Use only.
- **확인·프롬프트·Generate·큐·다운로드 클릭** = Chrome Codex plugin preferred.
- 동시에 owner 도구 하나 (phase lock).
- 플러그인 불가 시 임시 폴백 = **같은 Chrome 탭** full CU (Safari 병행 금지).

클린업 진단의 “창 미스라우트 / 검증 폭발”에 대한 구조 대응:
- 웹 조작을 탭/플러그인 쪽으로 몰아 스크린샷 검증 부담 감소.
- 첨부의 비싼 OS 드래그만 CU에 남김.

### 2.2 Dual in-flight (큐 용량)

- 생성 ~30분/장 → **인플라이트 ~2 유지 필수**.
- A가 카드로 큐 진입하면 B를 바로 투입. “한 장 끝날 때까지 대기” 금지.
- “손(도구)은 순차, 큐 슬롯은 병렬”로 문장 고정.
- 잘못 읽히던 “직렬화 = 한 장만 돌린다” 해석 폐기.

### 2.3 seedance-prompt-en 계약 갱신

- Hard route를 Chrome hybrid + dual in-flight로 교체.
- state JSON에 `browser`, `phase`, `owner_tool`, `inflight_count` 추가.
- I2V default Seedance / Grok explicit-only 명시.
- 활성 파일 길이 유지 (단일 계약, archive는 참고만).

### 2.4 README / gate / ops 정합

- README에 authority map + v2 모델 다이어그램.
- subagent gate: 삭제된 `codex-video-runtime/templates` 참조 제거.
- `simple_generate_loop_policy`를 Chrome hybrid + dual fill에 맞춤.

---

## 3. 의도적으로 안 한 것

- Hermes 복원, 멀티 레인 스캐폴드 재도입.
- Playwright 자동화 코드 본문 (별도 PoC 과제).
- wiki `~/wiki` 헤르메스 죽은 인프라 8개 정리 (클린업 §6 미결 유지).
- 크롬 네이티브 호스트 설치 자동화 (로컬 맥 환경 작업).

---

## 4. 배포 체크리스트 (맥 영상 PC)

```bash
cd ~/Documents/Codex/video-team-workflow   # or clone of this repo
git pull
./tools/deploy_skills_to_codex.sh
# confirm:
#   ~/.codex/skills/seedance-prompt-en/SKILL.md  (Chrome hybrid text)
#   no parallel Safari Runway habit for this project
#   Chrome native host for Codex plugin if using plugin path
```

---

## 5. 롤백

```bash
git log --oneline -- docs team-policies codex-skills/seedance-prompt-en README.md
git checkout <pre-v2-commit> -- codex-skills/seedance-prompt-en/SKILL.md
# or full tree pin
```

Deploy archive: `~/.codex/archive/<timestamp>_skill_deploy/` after deploy script runs.
