# 선택형 지식

request가 자동 선택한다. 일상 저작에서 이 문서나 전체 wiki를 추가로 읽지 않는다. 선택 오류/새 지식 검토 때만 사용한다.

- context의 knowledge_tags: reference, identity, edit, text, product, live_action, animation, action, camera, storyboard, audio. 명시 태그와 제한적 한·영 키워드 추론을 합친다. 완전한 의미 분류기는 아니다.
- knowledge_version: 이미지 chatgpt-web, 기본 영상 seedance-2.0, 명시적 2.5만 seedance-2.5. UI 지원/모드 증명과는 별개다. 음악은 기존 corpus를 사용한다.
- 최대 6개/9,000자의 완전한 카드만 author_task에 들어간다. 과예산/미지원 명시 태그는 검토한다. 전체 request/위키 덤프 또는 중복 knowledge-select로 해결하지 않는다.
- author-task 본문을 실제 Astra에게 전달하고 같은 저작 응답의 Knowledge-SHA256을 seal/payload까지 결속한다. 선택/전달/확인은 내부 추론·생성 품질의 보장이 아니다.
- catalog는 references/knowledge/catalog.json, canonical은 ~/wiki/concepts/aside-image-video-prompting.md. live corpus와 선택 upstream hash가 바뀌면 재검토한다. live가 없는 설치만 reviewed_snapshot/fallback을 명시하며, 기존 live request의 파일이 사라졌다고 snapshot으로 바꾸지 않는다.
- 공식 가이드와 로컬 경험칙의 URL·날짜·section/hash를 보존한다. 외부 URL을 매번 다시 확인한 것은 아니다. provider 변경/실제 반례가 있을 때만 targeted 연구한다.
- raw/archive/capsule/옛 프로젝트 운영 규칙은 자동 로드하지 않는다. 새 교훈은 근거를 검토해 CURRENT·catalog·mirror를 함께 갱신하고 테스트한다. 원본 raw·기존 인수증은 소급 수정하지 않는다.

진단이 필요할 때만 `knowledge.mjs select <stage> --context <json>`. 지식 자체는 파일에 남기되 모델에는 author-task 본문을 한 번만 전달한다.
