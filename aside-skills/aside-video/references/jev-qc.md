# 선택형 Jev QC 노트 분류

실제 관찰 노트가 mixed_findings, repeated_failure, uncertain_category일 때만 보조로 쓴다. 정상 성공·수치·해시·명확한 단일 결함은 직접 처리한다.

`jev-video.mjs classify --root <same task root> --input <qc-note.json> --reason <reason>`

입력은 `{"qc_note":"실제 관찰만","observation_scope":"sampled_frames"}`. qc_note는 6000자 이하이며 observation_scope는 text_only/sampled_frames/full_playback/audio_playback 중 실제 범위다. 전체 package·대화·원본 미디어·고객명·계정·비밀·경로를 보내지 않는다. 키는 출력/복사하지 않는다.

- 같은 root의 .jev 원장을 유지한다. 작업당 최대 5회, 오류도 포함, 같은 성공 입력은 캐시 재사용. 자동 retry/한도 우회/lock 삭제는 없다. 실패·키 없음이면 현재 실행자가 처리한다.
- 주분류를 원본 노트와 대조한다. 독립 noul/confidence는 PASS 기준이나 보이지 않는 결함을 만드는 근거가 아니다. NO_ISSUE_REPORTED도 실제 영상 PASS가 아니다.
- advisory=true, execution_authorized=false. 저작·Generate·재생성·승인·설정 변경 권한은 없으며 문구 수정은 Astra에 돌린다.
- 실제 호출 CLASSIFIED, 캐시, dry-run, 미연결은 구별한다. 속도/정확도 개선은 미입증이다.

저수준 jev-qc.mjs는 개발 시험용이다. 일상 제작에서는 wrapper만 사용한다. 입력 스키마/보안/HTTP 세부사항은 코드와 테스트가 원본이며 작업마다 다시 읽지 않는다.
