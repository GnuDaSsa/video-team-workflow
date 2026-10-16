# 단계별 책임 — 역할은 에이전트 수가 아니다

기본은 현재 Codex 대화의 한 작업자가 순서대로 아래 책임을 수행한다.
별도 역할 인격, 별도 프롬프트 팀, 자동 모델 교대, 관찰자, relay를 만들지 않는다.
추가 owner를 실제 생성하려면 runtime의 해당 spawn 승인 규칙을 적용한다.

| 단계 | 결정/산출물 | 다음 단계로 넘기는 증거 |
|---|---|---|
| Director | P0 컨셉 3안·P1 style bible | 사용자 선택 인용으로 잠근 concept_lock + 잠근 style_bible |
| Music | 곡/가사/오디오와 음악 구조 | 실파일·선택 근거·lock·리듬맵 |
| Planner | P2 음악 기반 15초 블록 storyboard | 사용자 승인으로 잠근 storyboard.json(파생 planner 파일) |
| Image Creator | P3 identity/reference/sourceframe | 영어 `<REF>.prompt.txt` + 생성 파일 + image_plan |
| Image QC | identity·해부·구도·I2V 사용성 | 등록된 승인 자산과 근거 |
| Seedance prompting | P4 영어 선반 프롬프트·reference 결속 | shelf-check/shelf-lock 통과 선반 + 사용자 release |
| Seedance production | P5 release된 선반만 복붙 실행(새 창작 결정 금지) | shelf-verify·매칭 card·다운로드·registry |
| Seedance QC | 시간적 연속성·동작·정체성·사용 구간 | 재생 검사와 approved interval |
| Package | QC 승인 클립을 storyboard 순서로 납품/제출 초안 | 순서 클립·audio·manifest·QC·notes (편집 master 없음) |

실행 레일·승인·모델/미디어 정책: canonical runtime AGENTS.md.
Seedance UI/큐/복구: 선택 버전 Seedance skill. 이 문서는 연출 책임만 설명한다.
