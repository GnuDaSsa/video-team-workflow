# 영상팀 워크플로: native Aside + Codex 호환

Canonical source for the user's video workflow. Project/media data stays outside
this repository. Active rules are latest-only; history belongs to Git/archive.

## 신규 native Aside 제작의 진입점

**새 Aside 제작과 후속 수정은 `aside-skills/aside-video/SKILL.md`가 우선한다.**
이미지·Seedance 생성용 원문과 음악 제작 지시는 **영어(en-US) 기본**이다.
한국어 대화·브리프와 실제 가사·대사·화면 문자의 언어는 별개다. 작업별 명시
예외만 기록하며, 아래 legacy Codex의 한국어 기본값을 신규 Aside에 가져오지 않는다.

- 실행: 사용자가 연 현재 세션 유지(`inherit_session`, Luna로 시작하면 Luna).
- 저작·번역·의미 수정: 실제 Astra, 요청/응답/해시/언어 계약으로 인수.
- Jev: 제한된 다음 단계 추천만. 브라우저 실행·Generate·승인 권한 없음.
- 기존 에셋 hash-bound 검색 재사용, 최초 업로드만 실행자 허용 경로로 첨부.
- fresh snapshot URL/Reference 모드, 팝업 차단, 검증 원문 입력과 단일 제출 유지.
- legacy 인수증은 읽기 검증만 허용하며 새 입력 계약으로 자동 승격하지 않는다.

설치 및 같은 내용인지 확인:

```sh
node tools/deploy_aside_workflow.mjs --apply --account-root /absolute/aside/account
node tools/deploy_aside_workflow.mjs --check --account-root /absolute/aside/account
# source 변경을 검토하고 테스트한 뒤에만 manifest 갱신:
node tools/deploy_aside_workflow.mjs --freeze
```

이 설치는 해당 계정의 `skills/user/aside-video`와 AGENTS의 관리 블록만 다룬다.
기존 파일은 백업하며 키·설정·프로젝트/미디어·에셋 원장은 배포하지 않는다.
Codex 기술 문구/음악 소스가 필요한 경우 해당 로컬 스킬을 별도로 유지한다.
실제 모델 호출은 native Aside 도구가 수행하며 이 저장소가 상주 실행자를 만들지 않는다.

```sh
# 기존 scratch 폴더를 지정한다. 테스트는 합성 입력과 mock transport만 사용한다.
JEV_QC_TEST_TMP=/absolute/scratch TMPDIR=/absolute/scratch \
  node --test aside-skills/aside-video/scripts/*.test.mjs tools/deploy_aside_workflow.test.mjs
```

계약과 검증 범위: `docs/contracts/2026-09-20-aside-english-workflow.md`.

## 기존 Codex 프로젝트의 호환 실행 모델

기본은 **현재 대화의 한 작업자**가 아래 역할을 순차 수행한다. 역할 변경은
새 에이전트 생성이나 자동 모델 변경을 뜻하지 않는다.

`Director → Music Lock → Planner → Image → Image QC → Seedance prompting →
Seedance production → Seedance QC → Editor/CapCut → Package`

- `prepare-image-batch`는 내장 imagegen용 hash-bound 목록만 만들며 숨은 Codex 작업/API 전환은 없다.
- 별도 dispatch는 해당 spawn을 사용자가 명시 승인했을 때만 사용하는 호환 경로.
- 이미지 실행만 불변 1-cut prompt당 최대 3개의 bounded non-agent process 허용.
- No-I2V는 새 팀이 아니라 승인된 재사용 reference를 최소로 쓰는 생성 모드.
- 프로젝트별 media/registry와 승인/제출 안전은 runtime AGENTS.md가 소유한다.
- v4 조회 명령은 자동 정리를 실행하지 않는다. 승인 게이트를 통과한 lane dispatch 경로의 기존
  24시간 정리와 명시적 정리 명령만 해당 정책을 따른다. 미디어 이관은 별도 요청.

## 기존 Codex 호환 경로의 권위

| 범위 | 단일 소유자 |
|---|---|
| 레일·승인·미디어·입력 게이트 | `runtime/AGENTS.md` + runtime code |
| Seedance 2.0 / 기본 | `codex-skills/seedance-prompt-en/` |
| 사용자가 명시한 Seedance 2.5 | `codex-skills/seedance25-prompt-en/` |
| 공통 프롬프트 검토 | `seedance-prompt-en/prompt-review.md` |
| Aside exact-session 실행 | `seedance-prompt-en/aside-operator.md` + shared helper |
| 스폰 승인 | `team-policies/subagent_approval_gate_20260721.md` |
| 이야기·연출·편집 품질 | `codex-skills/videodirector/` |

## 기존 Codex 배포와 검증

```bash
python3 -m unittest discover -s runtime/tests -v
python3 tools/video_release.py freeze       # 검토 완료된 source hash 고정
./tools/deploy_skills_to_codex.sh --preflight # 안전한 적용 가능 여부; parity 아님
# 검토한 변경만 commit/push 후, 활성 제작 owner가 없을 때:
./tools/deploy_skills_to_codex.sh
./tools/deploy_skills_to_codex.sh --check     # source + live hash / 퇴역 경로 엄격 검사
```

이 릴리스는 명시된 세 skill(Seedance 2.0/2.5, videodirector), runtime scripts/
templates, 표준 reference, global/policy만 관리한다. 다른 음악/코딩 skill 및
무관한 사용자 파일은 동기화하지 않는다. 알 수 없는 live skill 파일은 삭제하지
않고 조정 필요로 중단한다. 기존 파일/퇴역 경로는 `~/.codex/archive/`에 먼저
보관한다. 덮어쓴 파일 hash가 다르면 성공으로 보고하지 않는다.

기존 pack 읽기 전용 감사:

```bash
python3 tools/shadow_prompt_audit.py --root '<prepared shelf>' > /tmp/shadow-audit.json
```

`ATTESTED` 과거 표시만으로 신규 제출하지 않는다. 현재 validator에서 FAIL이면
아직 제출하지 않은 pack을 저작 단계로 되돌린다. 제출된 job/media/history는
고치거나 자동 재승인하지 않는다.

## 검증의 한계

코드·해시·프롬프트 검사는 영상 품질 PASS가 아니다. 실제 생성 후 전 구간 재생,
identity/physics/temporal QC와 실제 CapCut preview/export 검사가 따로 필요하다.
릴리스 범위와 증거: `docs/releases/2026-09-06/`.

포함하지 않는 것: 프로젝트 폴더, 영상/음원, CapCut draft, 세션 URL/계정 상태,
비밀정보, 개인 제출 양식. 별도 에이전트/스케줄러/브라우저 루프는 만들지 않는다.

### Image/video prompting knowledge

Native Aside now binds a reviewed, task-scoped wiki packet into image and Seedance author requests and checks the actual Astra acknowledgement through provider input. See [knowledge contract](docs/contracts/2026-09-20-aside-knowledge.md) and [source/lifecycle guide](aside-skills/aside-video/references/knowledge.md). The portable snapshot is explicitly labeled when a live wiki is absent; live source drift never silently falls back. This is an authorship/data-flow gate, not a claim of generated-media quality.
