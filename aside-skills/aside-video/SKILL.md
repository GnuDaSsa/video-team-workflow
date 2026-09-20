---
name: "aside-video"
description: "Aside 영상팀: 이미지·노래·Seedance/MV/No-I2V 제작과 후속 수정. 프롬프팅은 Astra, 실행·QC는 현재 세션. 신규 Aside 작업은 기존 Codex 호환 레일보다 우선한다."
---

# Aside 영상팀

## 유지할 계약

- 실행자는 현재 세션 그대로. 노래·이미지·Seedance 문구와 의미 수정만 실제 `gpt-6-astra`가 저작한다. 현재 모델이 Astra면 직접, 아니면 실제 Astra category의 bounded author로 위임한다. 모델/category 설정은 바꾸지 않는다.
- 생성용 문구는 영어 기본. 가사·대사·화면 문자 원문은 보존하며 명시적 언어 예외만 기록한다. 입력은 `request → 실제 Astra 응답 → seal → submission prepare/verify`를 통과한 원문 그대로다.
- 이미지 기본은 웹 ChatGPT Images 2.5, 영상은 Runway Seedance 2.0의 **Video → Reference**. 명시적으로 다른 provider/version/mode를 요청하면 별도 확인한다. 자동 API/imagegen/Keyframe fallback은 없다.
- 사용자 승인 수량·길이·참조·비용이 우선이다. 불명시 단일 컷은 15초·1개. 재생성·결제·공개·불확실한 Generate 재클릭으로 범위를 늘리지 않는다.
- 승인 identity/배경/기체를 실제 참조로 유지한다. 인물 중심 No-I2V는 필요한 캐릭터 시트를 생략하지 않는다. 제품·드론에는 인물 캐스팅을 강제하지 않는다.

## 필요한 단계만 읽기

| 지금 하는 일 | 읽을 문서 |
|---|---|
| 새 문구/의미 수정 | `references/author-executor.md` |
| 브리프·연출을 새로 결정 | `references/directing.md` |
| 이미지 웹 실행/인물 캐스팅 | `references/web-chatgpt-casting.md` |
| Runway 참조 준비·입력·생성 | `references/seedance-upload.md` |
| 지식 선택 오류/새 지식 검토 | `references/knowledge.md` |
| 명시적 언어 예외/언어 검사 실패 | `references/prompt-language.md` |
| 다음 행동이 정말 모호하여 Jev 보조가 필요 | `references/jev-dispatch.md` |
| 복합/반복/모호한 QC 노트 분류가 필요 | `references/jev-qc.md` |

같은 문맥에서 이미 읽었고 지침·단계가 바뀌지 않았으면 전체 문서를 재독하거나 status를 반복 호출하지 않는다. 새 세션·압축 후·규칙 변경 시 해당 단계만 복원한다. 정상 작업은 실행자가 바로 진행한다. Jev는 선택형이며 성공·숫자·해시 검사에 끼워 넣지 않는다. 역할은 실제 전환 때 한 줄로만 알린다.

## 최소 실행

1. 현재 package의 brief·최신 승인/HOLD·파일 경로·실제 browser session을 복원한다. 다른 프로젝트의 미저장 composer/queue는 보존한다.
2. 필요한 프롬프트만 인계한다. 지식 본문은 request가 자동 선택하므로 전체 wiki/구형 스킬을 추가 로드하지 않는다. 별도 author가 일하는 동안 독립적인 참조·설정 준비만 병행한다.
3. 참조는 workspace+SHA256으로 기존 에셋을 먼저 재사용한다. 동일 파일 재업로드·원본 재탐색·불필요한 reference 증식을 하지 않는다.
4. 실제 UI의 URL·Reference 선택·참조 순서·원문·길이·비율·오디오를 확인하고 preflight 뒤 한 번 제출한다. 브라우저는 플랫폼의 fresh snapshot/ref 규칙을 따른다. 모달이 열렸으면 prompt를 입력하지 않는다.
5. 다운로드의 실제 bytes/hash/codec/duration을 `check.mjs media`로 검사한다. 프레임 QC, 전 구간 motion, 청취는 별개다. 보지/듣지 않은 검사를 PASS라 하지 않는다. 15초 요청 허용 오차는 ±0.25초다.
6. 요청된 파일과 짧은 결과·미검증 항목만 전달한다. 별도 음악·편집 요구가 없으면 Suno/Music Lock/CapCut을 추가하지 않는다.

상세 인수증은 파일에 보존하고 CLI는 요약 출력만 쓴다. 막힌 원인 하나를 해결할 때만 해당 상세 자료를 연다. 이전 작업의 로그·미디어·인수증은 삭제하거나 소급 수정하지 않는다.
