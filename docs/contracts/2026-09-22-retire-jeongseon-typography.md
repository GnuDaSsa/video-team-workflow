# 정선 타이포 스킬 폐기

## 사용자 결정과 범위
사용자가 정선 결과를 실패작으로 지정하고 관련 스킬을 완전히 제거하도록 요청했다. 활성 스킬·추천·자동 참조에서 제외한다. 기존 영상/프로젝트와 사실 이력은 삭제하지 않는다. 비활성 rollback만 Git 이력과 ~/.codex/archive에 보존한다.

## 변경
- canonical codex-skills/jeongseon-video-typography 삭제
- canonical release RETIRED 목록에 등록
- repository-owned retire_one_skill_from_codex.py로 해당 경로만 preflight 후 아카이브 이동; 다른 live skill/source drift 배포하지 않음
- 위키 및 extract의 Jeongseon-derived assimilation 절 제거; 새 이름으로 재포장하지 않음
- 현재 MV 타이포 조사 추천 및 패키지 문서 수정; 영상 재제작은 수행하지 않음

## 검증
191 legacy unit tests + 451 native/deployer tests PASS (retirement regression 3개 포함), Python compile/shell syntax/diff check PASS. 활성 설치 경로 없음, source 폴더 없음, 단일 retirement preflight/apply/check PASS.

## 분리한 미검증/기존 상태
전체 release parity는 기존 source-manifest/live drift 때문에 PASS가 아니며 전체 hot deployment를 실행하지 않았다. 다른 제작 owner/예약/미디어와 기존 harness blocked 목표를 보존했다. 신규 앱 세션의 discovery UI 검증은 하지 않았으나 활성 경로 제거를 확인했다.
