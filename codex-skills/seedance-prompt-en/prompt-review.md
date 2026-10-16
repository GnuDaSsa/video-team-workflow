# Seedance prompt review (same-owner lens)

한 작업자가 아래를 순차 확인한다. 별도 Creative 팀/critic agent를 만들지 않는다.
이 문서는 **검토 렌즈**이며 템플릿이 아니다. 프롬프트는 항상
`seedance-prompting.md`의 단일 템플릿으로 작성하고, preprod 프로젝트에서는
`preprod.py shelf-check`가 형식(첫 줄·숏 마커·어휘·MUST·잠금 블록·토큰·길이·영어)을
기계 검사한다. 이 렌즈는 기계가 못 보는 의미만 본다. 체크리스트 문구는
model-facing prompt로 보내지 않는다. 모든 model-facing 예문은 영어다.

## 0. 저작 근거

모델/표시 라벨 정책 원본은 runtime AGENTS §1.3. attestation/shelf-lock은
형식·해시·길이·참조 계약 검사이지 창작 품질 보증이 아니다. 실제 작성 턴/모델
근거가 없으면 `HOLD_AUTHORSHIP_UNVERIFIED`; 문장이 바뀌면 새 revision으로
다시 검사·잠금한다. 새 승인 JSON이나 프로젝트별 규칙 파일을 만들지 않는다.

## 1. 장면 계약

- 사용자 원안에서 이 블록의 **화면적 보상 한 문장**을 적고, 최종 프롬프트에
  남았는지 확인한다. 사실·안전 사유로 바꿨다면 의도를 보존하는 대체 화면을 쓴다.
- `render_scope`(`human_only`, `drone_only`, `mixed`, `environment_only`,
  `object_only`)는 이번 출력에 실제 등장할 범위다. 범위 밖 entity의 반응을 쓰지 않는다.
- 첫 숏 구간만 읽어도 주체의 행동과 카메라가 그려져야 한다.
- 숏 수(예: 4숏)만으로 구성 PASS를 주지 않는다. 고정 카메라 vs 교차 편집 같은
  상충 요구를 해소한다. human/drone 분리는 표현 대상을 나누는 것이지 원인을 지우는 것이 아니다.
- 사용자 거부나 provider 정책 경고 뒤 자동 재생성하지 않는다. 경고 원인은 관측과
  추정을 분리한다.
- 블록 시간은 shared contract의 duration lock 그대로. 시간 표기는 연출 의도이지
  프레임 정확도 보장이 아니며, 실제 컷점은 출력 재생 검사로 확인한다.

## 2. 레퍼런스

인접 deck overlap 기준은 shared contract 소유. 검토 fixture:
- PASS: 서로 다른 장면 3장씩 + 동일한 승인 인물시트 2장 (공유 scene/action=0).
- REPAIR: 같은 장면 2장 공유 + 동일 시트 2장 (공유 scene/action=2).
- REPAIR: 중복 장면을 identity로 이름만 변경 (승인 identity 자산/hash 아님).
- BLOCKED: overlap을 줄이려고 필수 시트를 제거 (identity gate 실패).

각 token마다 `가져올 것 / 가져오지 않을 것 / 적용할 숏`을 정하고 바인딩 문장에
반영한다. 첨부 순서=사건 순서라는 가정, 파일명, 업로드 지시는 제거한다.

## 3. 카메라와 물리는 결정문

- 숏마다 **콘티에 선언된 지배적 카메라 무브 하나**. `3/4 tracking or locked-off
  front`처럼 미결정 문장은 FAIL; 하나를 고른다. 복합 경로가 필요하면 콘티에서 숏을 나눈다.
- 거리·각도·이동경로·시선/화면방향·끝 구도를 형용사 대신 명시한다.
- 물리 단서는 **그 숏에 필요한 것만, 개수 할당 없음**. 사람: 접지·체중 이동·지연되는
  의복. 드론: 관성·뱅크·안정화·parallax. 2D: 승인된 선/색면/음영 유지, 실사 모공/grain 주입 금지.
- 금지어 반복을 긍정적인 동작·공간 설계 대신 쓰지 않는다. 한 명 장면의 복수 인물
  문구 같은 템플릿 잔재를 지운다.

## 4. 컴파일 확인

템플릿 순서(헤더 → STYLE → IDENTITY → 바인딩 → Shot k → Sound → End frame)를
지켰는지 본다. 이미 결속한 identity 설명을 숏마다 반복하지 않는다. 길다는 이유만으로
고유한 인과·identity·공간·MUST 문구를 자르지 않는다; 제거 대상은 중복/모순/무관한
통제 문구다. 과거 프로젝트 금지 목록을 붙이지 않는다.

## 5. 반례 검토

| 검토 질문 | FAIL 예 |
|---|---|
| 이번 출력에 없는 entity가 행동하는가? | drone_only에 소매/머리카락 반응 |
| 제외하려다 오히려 등장시켰는가? | human_only에 "the drone stays in the air" |
| 카메라를 결정했는가? | "tracking or locked-off" |
| prompt와 pack이 같은 plan인가? | 참조/숏/시간/끝 상태 불일치 |
| 실행 메모가 누출됐는가? | `Mode:`, 업로드 경로, 파일명 |
| 행동이 실제 수행 가능한가? | 접촉 전 반응, 순간이동, 동시 다발 사건 |

`shot_semantics.py`는 관찰된 좁은 회귀만 검출한다. PASS가 의미 정합성이나 영상
품질을 보증하지 않는다. 새 오류는 재현 가능한 good/bad fixture로 만든 뒤 검출기로 승격한다.

## 6. 수정과 품질 측정

실패는 `identity / reference_scope / camera / physics / timing / texture /
operator / provider`로 분류하고 근거 있는 원인 한 가지만 고친다. 문장 문제면
그 문장(preprod에서는 콘티 또는 shelf prompt revision), 입력·공간 문제면 그 입력을
바꾼다. 원인이 reference인데 문장만 바꾸는 것은 단일 변수 실험이 아니다. 첫 생성
승인율, 재시도 수, 사용 가능 초/생성 초, identity FAIL, 채택 클립 수를 기록한다.
관찰치 없이 "프롬프트 개선 성공"이라 하지 않는다.

### 반복 실패 진단 (입력 → 공간 → 동작 → 효과)

같은 실패가 2회 이어지면 같은 입력으로 `faster`, `only in the air`, `never`를
늘리는 재시도를 멈춘다(다른 독립 블록 제작은 계속).

1. **관측과 추정 분리** — 연속 프레임의 접촉·회전축·그림자·공극으로 판정한다.
2. **참조 누출** — identity 시트의 바닥/그림자/전시 포즈가 장면으로 샜는지 본다.
   최소 crop이나 환경 참조로 해결하고, negative 추가나 필수 identity 제거로 풀지 않는다.
3. **공간 증거** — 고도·거리는 말이 아니라 구조물 대비 높이, 그림자, parallax로 읽히게.
4. **물체와 조종자 분리** — 물체는 형상/색 + token으로 식별, 조종자는 별도 숏.
5. **접촉과 회피의 인과** — 시작 위치 → 접근 → 접촉/여유 간격 → 양쪽 반동 → 회복.
6. **기본 사건이 읽힌 뒤 효과** — 잔상·분할 화면은 인과를 가리지 않는 순간에만.
7. **통과·득점 같은 공간 사건** — 한 프레임의 겹침은 증거가 아니다. 진입 → 고정
   평면에서의 일관된 가림 → 반대편 완전 이탈이 연속으로 읽혀야 하고, 부족하면
   `HOLD_SPATIAL_EVENT_UNPROVEN`.

드론 경기장 사례 상세: `incidents.md`. 수정안은 pack/QC report에 `관측한 실패 /
원인 가설 / 바꾼 입력 또는 문장 / 확인할 구간`을 남기고 다시 잠근다.

### 교정 예 — drone_only, 15초 단일 숏 (설명용)

잘못: `3/4 tracking or locked-off front. Sleeves and hair react to the wind.`

교정 (단일 숏 템플릿의 바인딩 + 본문 부분):

```text
@Image1 is the drone: keep its body shape and surface material only.
@Image2 gives only the city layout and the low sun direction.
Medium wide shot, eye level, tracking from the drone's rear-left three-quarter at matching speed. The drone flies straight, banks gently right, levels out and holds its heading to the end. Near rooftops and distant towers separate in parallax to show speed.
Sound: a steady motor hum and wind only.
```

이 예는 구성법이며 다른 작품에 복사할 기본 문장이 아니다.

## Blender / 3D previs 조건부 검토

Blender/프리비즈 입력은 `blender-previs-prompting.md`의 source-role, 프록시 외형,
수정 패스 분리와 출력 판정 항목을 함께 검토한다. 자동 attestation PASS로 대체하지 않는다.
