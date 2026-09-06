# 단계별 책임 — 역할은 에이전트 수가 아니다

기본은 현재 Codex 대화의 한 작업자가 순서대로 아래 책임을 수행한다.
별도 역할 인격, 별도 프롬프트 팀, 자동 모델 교대, 관찰자, relay를 만들지 않는다.
추가 owner를 실제 생성하려면 runtime의 해당 spawn 승인 규칙을 적용한다.

| 단계 | 결정/산출물 | 다음 단계로 넘기는 증거 |
|---|---|---|
| Director | 한 문장 전제, 인과·감정 spine, 목적/금기 | 승인된 brief와 제약 |
| Music | 곡/가사/오디오와 음악 구조 | 실파일·선택 근거·lock·리듬맵 |
| Planner | 음악 기반 컷/블록, 공간·동선·storyboard 설계 | shot 목적·타이밍·reference 범위·edit-out |
| Image Creator | 필요한 identity/reference/sourceframe | 공냥 컴파일 prompt + 생성 파일 |
| Image QC | identity·해부·구도·I2V 사용성 | 등록된 승인 자산과 근거 |
| Seedance prompting | 한국어 장면 연출·reference 결속 | prompt.txt + package + 현행 attestation |
| Seedance production | 정해진 pack만 실제 실행 | 매칭 card·다운로드·registry |
| Seedance QC | 시간적 연속성·동작·정체성·사용 구간 | 재생 검사와 approved interval |
| Editor | 음악/호흡 기반 편집·타이포 | 실제 CapCut preview와 export QC |
| Package | self-contained 전달물/제출 초안 | 검증 master·clean·audio·EDL·manifest·notes |

실행 레일·승인·모델/미디어 정책: canonical runtime AGENTS.md.
Seedance UI/큐/복구: 선택 버전 Seedance skill. 이 문서는 연출 책임만 설명한다.
