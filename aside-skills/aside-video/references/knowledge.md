# 이미지·영상 지식 인계

## 매 작업의 연결

1. 현재 사용자 요청과 승인 brief를 기준으로 `context.user_instruction`을 기록한다. 필요하면 `knowledge_tags`로 `reference, identity, edit, text, product, live_action, animation, action, camera, storyboard, audio` 중 실제 속성을 지정한다. 현재 선택기는 명시 태그와 제한적인 한·영 키워드 추론을 합친다. 의미를 전부 이해하는 검색기로 가장하지 않는다.
2. 이미지 `knowledge_version=chatgpt-web`, Seedance 기본 `seedance-2.0`, 명시적으로 선택한 2.5만 `seedance-2.5`를 사용한다. 지식 버전은 실제 UI 지원·모드 확인을 대신하지 않는다. 음악은 이 corpus 범위 밖이며 기존 음악 소스를 쓴다.
3. `harness.mjs request`가 `knowledge.mjs`를 실제 호출한다. catalog의 검토된 17개 카드 중 해당 stage/version/태그에 맞는 최대 6개, 9,000자만 완전한 section 단위로 선택한다. 과예산이나 명시 태그 미매핑은 HOLD다. 핵심 규칙을 잘라내거나 전체 wiki를 대신 전달하지 않는다.
4. request의 **`author_task` 전체**를 실제 Astra에게 전달한다. 여기에는 선택된 지식 본문이 이미 들어 있다. 링크·선택 파일만 만들고 끝내지 않는다. 원본 wiki/구형 스킬 전체를 author에게 추가로 펼치지 않는다.
5. Astra는 prompt 원문 또는 `Prompt-SHA256: ...`와 함께 같은 실제 응답에 `Knowledge-SHA256: <request.knowledge.sha256>`를 남긴다. 어떤 카드가 구체적 문구 선택에 기여했는지도 provider 원문 밖에서 짧게 설명한다. 현재 실행자는 문구를 대필·번역하지 않는다.
6. `seal → submission prepare/verify → preflight/fastlane`이 지식 해시와 원문·실제 저작 응답을 연결한다. 지식 없는 구형 request/receipt는 보관 검증만 하며 새 입력을 허용하지 않는다. 지식은 provider 원문에 넣는 파일 경로·상태·QC 지시가 아니다.

선택기만 점검하려면 `node scripts/knowledge.mjs select image_prompt --context <context.json>`을 쓴다. request 전에 같은 선택을 중복 저장할 필요는 없다.

## 출처와 생명주기

- Catalog: `references/knowledge/catalog.json`. Canonical creative corpus: `~/wiki/concepts/aside-image-video-prompting.md`.
- live wiki가 있으면 canonical corpus와 선택된 upstream wiki 파일의 해시를 검사한다. 원본이 바뀌면 자동 수용·구버전 fallback하지 않고 검토를 요구한다. section은 검토 당시의 합성 범위를 나타내며 원문을 그대로 인용했다는 뜻은 아니다.
- wiki가 아예 없는 다른 설치에서는 동봉된 검토 snapshot만 사용하고 `source.mode=reviewed_snapshot`, `fallback=true`를 명시한다. 이를 live wiki 조회라고 보고하지 않는다. 이미 live로 결속된 request는 live 파일 삭제 후 snapshot으로 갈아탈 수 없다.
- 공식 문서와 검토한 로컬 경험칙은 `evidence`로 구분한다. URL·검토 날짜·wiki path/section/hash를 보존한다. 외부 URL 최신성은 매 요청마다 네트워크 검증한 것이 아니다. provider 변경이나 실제 결과의 반례가 있으면 targeted 재검토한다. 오래됐다는 이유만으로 유효한 구도·물리 원칙을 폐기하지 않는다.
- raw/아카이브/캡슐/옛 프로젝트 상태, 구형 Claude owner, Korean-default, `$imagegen` API 옵션, 숫자만 있는 CapCut 레시피를 자동 지식으로 승격하지 않는다. 검토되지 않은 규칙은 catalog에 넣지 않는다.
- 새 교훈은 실제 관찰과 실패 범위를 기록하고 재현/공식 근거를 검토한 뒤 CURRENT에 증류한다. 원문 raw는 수정하지 않는다. corpus·catalog revision/hash·동봉 mirror를 함께 갱신하고 회귀 검사와 배포 freeze/check를 통과시킨다. 진행 중인 인수증에 소급 반영하지 않는다.

## 확인 수준을 구별

`선택됨 → author_task에 전달됨 → 실제 Astra 응답에서 해시 확인됨 → 문구에 반영된 근거를 검토함 → 생성물 품질을 검증함`은 서로 다르다.

해시/acknowledgement는 파일과 응답의 결속 증거이지 내부 추론·모든 규칙의 의미 적용·시각 품질 증거가 아니다. 생성하지 않은 결과의 품질 개선을 주장하지 않는다. 로컬 파일은 수정 가능하므로 provider의 암호학적 attestation도 아니다.

## 브라우저 입력의 신뢰 경계

fastlane FILL은 job에 붙인 PASS 객체를 신뢰하지 않고 실제 `submission.mjs verify`에 연결된 환경 callback을 요구한다. 현재 REPL에서 그 adapter를 제공할 수 없으면 fastlane FILL만 HOLD하고 기존의 CLI 재검증 후 원문 직접 입력을 사용한다. 캐시 JSON을 반환하는 가짜 adapter로 통과시키지 않는다. 파일 게이트는 OS 수준 UI 차단기가 아니다.
