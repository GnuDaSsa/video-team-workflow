# Runway 참조·입력

## 파일은 한 번 확정

- package/승인 manifest의 절대경로·SHA256·역할·순서를 사용한다. 이미 아는 원본을 Finder/Recents에서 다시 찾지 않는다. 같은 이름의 preview/구버전으로 대체하지 않는다.
- 새 묶음만 `seedance-references.mjs prepare --references <ordered.json> --out-dir <new bundle dir>`로 만들고 반환 plan 경로/hash를 package.reference_bundle에 보존한다. 재개는 `verify <plan.json> --sha256 <accepted hash>`. references.json을 author·payload·package에 공통 사용한다. 파일/순서 변경은 새 bundle/저작 인계다.
- 원본 파일 검사와 시각 승인, 실제 UI 첨부는 별개다. 코드의 100개 구조 상한은 provider 허용 수량이 아니다.

## 기존 에셋 우선

1. `runway-assets.mjs lookup --scope <observed team> --file <verified file>`. workspace+hash가 같으면 컷/session/staging 이름이 달라도 기존 이름/ID로 재사용한다.
2. 기록이 없어도 원본 이름으로 Asset selector 검색부터 한다. fresh UI에서 유일한 정확한 에셋을 double-click하고 슬롯을 확인한다. 이미 선택된 항목을 다시 toggle하지 않는다.
3. 과거 업로드의 바이트 결속이 없을 때만 원본 Download와 hash를 한 번 비교한다. thumbnail은 근거가 아니다. 기록은 `runway-assets.mjs record --scope <team> --file <source> --asset-name <observed name> [--asset-id <observed id>] --evidence <json> [--downloaded-file <original>]`.
4. evidence 필드: `{kind,observed_at,source_url,sha256,asset_name,asset_id}`. kind=upload_binding 또는 download_hash; 미노출 ID는 null. download_hash는 독립 다운로드 파일이 필요하다. 충돌/손상은 업로드 허가가 아니며 registry/root를 바꿔 우회하지 않는다.
5. 실제 없는 에셋만 직접 업로드한다. child 실행자는 자신의 허용 세션 폴더에 원본과 동일 hash/크기의 비심볼릭 복사본을 staging한다. provider 전달 전 경로 거절만 실패 기록을 남겨 1회 교정한다. 수용 불확실 timeout은 먼저 관측한다.
6. 관측한 file input/chooser에 검증 경로를 전달한다. multiple 지원 시에만 batch를 쓰고 실제 Image1.. 순서를 다시 확인한다. package.reference_uploads에 slot/hash/실제 이름·ID/관측 시간을 남긴다.

## UI와 한 번 제출

- 현재 작업의 정확한 snapshot URL/target을 사용한다. page.url()의 cached newSession 주소를 믿지 않는다. 다른 composer/queue를 보존한다.
- 진입·모델/모드 변경 후와 첨부/입력/Generate 직전에 **Video와 Reference의 실제 선택 상태**를 확인한다. Keyframe/Start-End 슬롯이면 중지. 애매하면 screenshot으로 판독한다.
- package: video_workspace=Video, video_input_mode=Reference. 실제 관측의 observed_settings에 mode_selection_verified=true, keyframe_slots_visible=false, observed_at을 기록하고 `check.mjs mode <package>`를 통과한다. 30초를 넘거나 UI가 바뀌면 다시 관측한다.
- 잘못된 모드는 기존 상태를 보존하고 관측된 Video/Reference control로 1회만 복구한다. 계속 실패하면 HOLD. 새 board/다른 모드로 도망가지 않는다.
- 모달이 열렸으면 닫고 재관측한다. prompt는 검증 payload 원문만 fill하고 수용 원문을 대조한다. 이미 같으면 재입력하지 않는다. 실패한 뒤 관측 없이 append/재시도하지 않는다.
- 모델·길이·비율·해상도·오디오·참조 순서·비용 범위를 대조하고 `check.mjs preflight <package>`. 통과 후 SUBMITTING을 기록해 Generate를 한 번 클릭하고 새 job의 수용을 확인한다. timeout은 재클릭 허가가 아니다.
- 실제 진행 중일 때만 bounded wait한다. 장기 대기는 플랫폼의 notification/routine 정책을 따른다. 해당 job의 원본 Download만 저장하고 media 검사를 한다.

정상 검색/선택/입력은 실행자가 직접 한다. 짧은 묶음 helper가 필요할 때만 jev-dispatch.md의 fastlane 절을 읽는다. 애매한 업로드 안내문만 `jev-seedance.mjs diagnose --root <same task root> --input <notice.json>`: 입력은 익명화한 실제 notice 한 필드(1500자 이하), 3회 한도·캐시·자동 재시도 없음. dispatch와 이중 호출하지 않으며 추천은 실행 권한이 아니다.
