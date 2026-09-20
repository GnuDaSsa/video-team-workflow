# 저작 인계

역할·언어·provider 기본값은 SKILL.md가 원본이다. 이 문서는 새 문구/의미 수정 때만 읽는다.

request와 author-task는 가능하면 한 shell 호출에 묶는다. 저작 후 seal→prepare→verify도 로컬에서 연속 실행하고 최종 요약만 출력한다. 왕복을 줄이는 것이며 검사를 생략하는 뜻은 아니다.

1. 현재 session id와 실제 모델/category를 `session-context.mjs <id> --out <context.json>`로 한 번 확인한다. 설정값은 실제 응답 모델 증거가 아니다. context에 실제 `user_instruction`, 필요한 `preserved_literals`와 지식 태그/버전을 기록한다. 언어 예외가 있을 때만 prompt-language.md를 읽는다.
2. `harness.mjs request <stage> --context <context> --root <absolute package> --prompt <relative prompt.txt> --out <new request.json>`. stage는 image_prompt, seedance_prompt, music_prompt. request가 지식과 영어 계약을 함께 만든다. Seedance 원문은 현재 3,500자 한도 안에서 필요한 길이만 쓰며 분량을 채우지 않는다. 별도 route/status/knowledge-select를 매번 중복 호출하지 않는다.
3. `harness.mjs author-task <absolute request.json>`으로 저작 본문만 얻는다. 전체 request JSON을 덤프하지 않는다. 반환 author_task + 확정 brief·정확한 참조 역할 + 유일한 출력 경로를 실제 author에게 전달한다.
4. route가 direct면 현재 Astra가 저작한다. functions.subagent면 반환 category의 실제 Astra author를 호출한다. 별도 author는 문구 파일만 쓰며 브라우저/생성/QC/추가 spawn/설정 변경을 하지 않는다. child에 native 위임 도구가 없으면 기존 parent에 인계하고, parent도 없으면 저작만 HOLD한다. 같은 request의 author를 중복 호출하지 않는다.
5. 실제 author 응답의 모델이 gpt-6-astra인지 확인한다. 원문 또는 `Prompt-SHA256: <hash>`와, image/video는 같은 응답의 `Knowledge-SHA256: <request hash>`가 필요하다. xhigh는 선호이며 실제 미확인 effort를 주장하지 않는다.
6. `harness.mjs seal --request <absolute request> --evidence <actual author/messages.jsonl> --out <new receipt.json>` 후 `submission.mjs prepare --stage <stage> --receipt <receipt> --sha256 <accepted receipt hash> --out <new payload.json> [--references <ordered references.json>]`.
7. 입력 직전 `submission.mjs verify <payload> --sha256 <accepted payload hash>`. CLI 기본 요약의 current language/knowledge 상태를 확인하고 파일의 payload.prompt를 그대로 입력한다. JS verify()는 adapter용 전체 반환을 유지한다. 진단용 전체 CLI 출력은 `--full`일 때만 쓴다.

package에는 author_handoffs={receipt,sha256} 목록, provider_payload={path,sha256}, prompt_file/sha256, execution_model=inherit_session, harness_policy_version=1을 보존한다. 실제 author/requester ID는 구별한다. 참조는 path/hash/role의 ordered 배열이며 UI 첨부 확인은 별도로 한다.

실행자는 승인 문구를 번역·축약·보완하지 않는다. 수정은 새 request/receipt/payload로 인계한다. fixture·route·자기 선언은 실제 저작 증거가 아니며, 언어/지식 없는 옛 인수증은 보관 검증만 가능하다. CLI/해시는 의미 품질이나 미디어 QC, OS 수준 UI 차단을 증명하지 않는다.

음악이 필요할 때만 `~/.codex/skills/music-director/references/awesome-suno-prompts/INDEX.md`와 관련 1~3개 source를 저작에 전달한다. 전체 음악감독 절차를 새로 시작하지 않는다.
