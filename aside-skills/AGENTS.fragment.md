<!-- aside-video-workflow:start -->
## 영상팀 신규 제작 기본값과 재개

- 새 이미지·영상·Seedance 제작 및 후속 수정은 현재 `aside-video` 스킬과 `references/author-executor.md`, `references/prompt-language.md`부터 읽고 시작한다. 새 세션/모델에서도 오래된 대화의 절차를 재사용하지 않는다.
- **생성용 이미지·영상 프롬프트와 음악 제작 지시는 기본 영어(en-US)**다. 한국어 대화/진행 설명과 실제 가사·대사·화면 문자 원문은 별개다. 현재 작업의 명시적 다른 언어 요청만 근거 있는 override로 남긴다. 예전 Codex 문서의 한국어 기본값이 신규 Aside 영어 기본값을 덮어쓰지 않는다.
- 실행자는 현재 세션 유지(inherit_session), 저작·번역·의미 수정은 실제 Astra, 다음 작업 추천은 Jev다. 정상 UI 동작은 짧게 묶고 동일 에셋은 hash-bound 기록으로 검색 재사용한다. 새 업로드는 실행자 세션의 허용 경로에 둔 동일 바이트만 사용한다.
- Astra 언어 계약과 실제 응답·해시 검증을 통과한 `CURRENT_POLICY_VALIDATED` payload만 입력한다. 언어 없는 과거 인수증은 읽기 검증만 가능하고 새 입력으로 자동 승격하지 않는다. 팝업이 열려 있으면 prompt 입력을 멈추고 fresh snapshot의 실제 URL·모드로 다시 확인한다.
<!-- aside-video-workflow:end -->
