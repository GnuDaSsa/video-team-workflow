# 언어 예외

기본은 SKILL.md의 영어 계약이다. 한국어 대화나 옛 예시는 override가 아니다.

- context.user_instruction에 실제 요청을 넣는다. 가사·대사·화면 문자는 preserved_literals 배열로 원문 보존한다. 설명 전체를 literal로 감싸 검사를 우회하지 않는다.
- 사용자가 다른 프롬프트 언어를 명시한 작업만 아래 override를 기록한다. 인용이나 승인 근거를 만들지 않는다.

`{"prompt_language_override":{"language":"ko-KR","reason":"Explicit task language choice","user_instruction":"이번 프롬프트는 한국어로 작성해 주세요."},"preserved_literals":[]}`

request→seal→payload는 같은 계약과 실제 원문을 검증한다. 실패하면 Astra가 수정하며 실행자는 번역하지 않는다. 신규 입력은 CURRENT_POLICY_VALIDATED만 사용한다. legacy 인수증은 읽기 검증만 허용하며 원본을 덮어쓰지 않는다.

문자 검사는 의미상 영어/번역 품질 검사가 아니다. 언어 변경은 provider 정책 우회나 품질/속도 향상의 증거가 아니다.
