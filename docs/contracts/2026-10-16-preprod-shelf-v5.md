# 2026-10-16 — 고정 프리프로덕션 + 제작 선반(v5), 편집 퇴역, 업로드 번들

## 요청 (사용자, 2026-10-16)
- 편집(Editor/CapCut) lane 제거 — 5개월 이상 미사용.
- 프롬프트 언어 영어 통일. 3500자 제한, 구도, 15초를 실제로 지키게.
- 업로드 문제 수정.
- 기획이 매번 프리스타일 → 단계별 틀: 아이디어 정리 → 이미지 가이드 → 콘티 → 이미지 프롬프트 → 영상 프롬프트(구도 포함)를 **미리 완성**하고, 제작은 복붙만.
- 폴더링을 정확히 해서 누락·중첩·병목 없게.

## 결정
1. Rail: `director → music → planner → image_creator_01/02 → image_qc → seedance → seedance_qc → package`. editor lane과 `editor.md`, `edit_queue`, `typography_queue`는 삭제. Package는 QC 승인 클립을 순서대로 납품(편집 master 없음).
2. 새 프로젝트는 `preprod/`(마커 `preprod/PREPROD_V1`)를 가진다. `runtime/scripts/preprod.py`가 단계 파일·잠금·선반을 소유한다.

| 단계 | lane | 파일 | 잠금 |
|---|---|---|---|
| P0 컨셉 | director | `preprod/00_concept/concept_options.md`(## Option ≥3) + `concept_lock.json` | 사용자 승인 인용 필수 |
| P1 이미지 가이드 | director | `preprod/01_bible/style_bible.json` (`style_block_en` ≤600자, 캐릭터 `identity_block_en` ≤350자) | lane self-check |
| P2 콘티 | planner | `preprod/02_storyboard/storyboard.json` (블록=15초, 숏 1–4개, 연속 시간, 통제 어휘 shot_size/angle/camera_move, composition, action, must_include, end_frame) | 사용자 승인 인용 필수 → planner 파일 자동 파생 |
| P3 이미지 | image_creator/image_qc | `preprod/03_image_prompts/<REF>.prompt.txt`(영어) + `image_plan.json`(ref→승인 asset_id) | 모든 ref가 registry 승인 상태 |
| P4 영상 프롬프트 | seedance(prompting) | `preprod/04_shelf/<BLOCK>/{brief.md, prompt.txt, settings.json, refs.json, pack.json, SHELF_LOCK.json}` | `shelf-lock`(검증+attest) 후 사용자 1회 `shelf-release` |
| P5 제작 | seedance(production) | 선반 소비만 | `shelf-verify` + `paste-prompt --pack <shelf>/pack.json` |

3. 선반 프롬프트 기계 검사(`preprod shelf-check`): 영어, NFC, ≤3500자(목표 ≤3200), 첫 줄 `15 seconds, N shots:` 또는 `15 seconds, one continuous shot:`, 멀티숏은 `Shot k (a-bs):`, 숏마다 shot_size/angle/camera_move/must_include 문구 포함, STYLE·IDENTITY 블록 원문 포함, `@ImageN` 토큰이 refs와 정확히 일치, 다른 초 수 언급 금지. 이후 기존 `prompt_packet_utils.attest`도 통과.
4. 상류 파일이 바뀌면 해당 잠금과 하류가 모두 STALE → gate 닫힘. 재잠금 시 이전본은 `preprod/_superseded/`로 이동, 현행은 항상 한 벌.
5. 업로드: `/tmp` symlink alias 폐기. `prepare-upload-bundle`이 pack의 토큰 순서대로 `~/RunwayUpload/<project>/<BLOCK>/NN_ImageN_<asset8>.png` APFS clone(0400, ASCII)을 만든다. 업로드 transport 실패는 세션 새로고침 없이 `ESCAPE_CHOOSER_REOPEN → REUSE_RUNWAY_UPLOADS_ENTRY_BY_EXACT_BUNDLE_NAME → PICKER_GO_TO_BUNDLE_FILE_PATH` 후 슬롯당 3회에서 사용자 행동. 세션 새로고침 rung 뒤에는 `settings-verify` 재통과 전 Generate 금지. `settings-verify`는 DOM에서 보이는 duration/model을 읽어 명백한 불일치를 거부.
6. 런타임 버그: status 부분문자열 추정 → 단어 단위; "not submitted"를 in-flight로 읽던 문제; 미디어 audit은 media 소비 lane(image_qc/seedance/seedance_qc/package)만 차단; inline 실행 RUNNING lane이 `next`에서 사라지던 문제.

## 보류 (사용자 결정 필요)
- 숨은 `input[type=file]`에 Aside `setInputFiles`로 번들 파일을 넣는 업로드 경로. 현재 정책("never hidden file inputs")은 유지.
- Korean override 코드 경로(`prompt_language_override`)는 기존 프로젝트 호환용으로 남김. 신규 선반은 영어만 허용.

## 검증
`python3 -m unittest discover -s runtime/tests` — 272 OK (2026-10-16).
