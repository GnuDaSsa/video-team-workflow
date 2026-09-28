---
title: Video Prompting — Live Action
created: 2026-08-01
updated: 2026-09-28
type: concept
tags: [video, video-production, qc]
sources: [concepts/live-action-character-authenticity-casting-standard.md, concepts/ai-photoreal-portrait-prompting-2026-05-30.md, concepts/seedance-prompting-knowledge.md, raw/articles/higgsfield-hell-grind-live-action-review-2026-09-08.md, raw/articles/paperloge-natural-light-review-2026-09-28.md, raw/articles/paperloge-prompt-screen-review-2026-09-28.md]
confidence: medium
contested: false
contradictions: []
retrieval_stages: [planner, image_prompting, image_qc, seedance_prompting, seedance_qc, editing]
retrieval_mediums: [live_action]
---

# Video Prompting — Live Action

## CURRENT

이 지식은 실사·포토리얼 요청의 기본 선택이다. 사용자 의도·승인 참조·프로젝트 lock이 우선한다. 정지 이미지에는 이미지 관련 항목만, 인물 없는 제품/공간에는 재질·공간·광학만 적용한다. 혼합 매체의 실사 구간에만 적용하며 애니메이션 작풍을 바꾸지 않는다.

### Identity

- 자연스러움을 완벽한 좌우대칭·V라인·도자기 피부로 번역하지 않는다. 승인 얼굴의 윤곽·눈 간격·코·턱·헤어·체형·의상과 고유 비대칭을 유지한다. 피부결·눈 반사광은 실제 광원과 촬영 거리에 맞춘다. 과장 모공·반짝임·입자를 추가하지 않는다.
- 반복 인물의 중립 triptych·상태별 파생·stress test는 기존 character-sheet 표준을 따른다. 단발 사진에 triptych/정체성 전용 stress test를 강제하지 않는다. 인물 시트 조명과 장면 룩을 구분한다.
- 수정은 승인 원본 기준으로 변경 대상과 보존할 얼굴·구도·광원·재질을 나눈다. 변경하지 않은 영역까지 반복 재생성하지 않는다. 픽셀 보존은 지시만으로 보장되지 않으므로 비교 QC한다.

### Optics

- 참조의 건축·배치·물체 형상을 보존한다. 고정 지도(문·창·거리·광원)와 컷별 blocking(카메라·좌우·몸 방향·시선·손)을 구분한다. 카메라가 바뀌면 좌우를 재계산한다. 역숏은 단순 좌우 반전이 아니다.
- 참조마다 얼굴/의상/공간/재질/구도 중 사용 역할을 구분한다. 지정 첫 프레임·크롭은 유지하되 장소 참조를 첫 프레임으로 오인하지 않는다.
- 장비명보다 거리·높이·화면 크기·원근·배경 선명도를 정한다. 얼굴 클로즈업에 전신 reveal을 섞지 않는다. 역광·연무·네온은 필요할 때만 쓴다.
- 실사 기본값: 인접 컷의 시간대·색온도·노출을 연결한다. 실제 해·창·조명을 정하고 밝은 면·그늘·접지 그림자의 방향을 맞춘다. 온기는 광원 색과 닿는 면에 국한한다. 작은 밝기 편차, 촬영 거리에서 읽히는 피부·나무·금속·유리의 결, 부드러운 하이라이트와 절제된 선명도를 유지한다. 재료 본래의 광택·의료 공간의 청결·승인 얼굴을 보존한다. 불균일함을 오염·과장 모공·주름·노이즈 추가로 번역하지 않는다. 이미지 프롬프트에는 해당 컴파일러의 긍정형으로 구체화한다.

### Performance — video only

- 목적→방해/자극→관찰 가능한 반응을 설계한다. 감정 형용사 대신 손의 작업과 멈춤, 시선 선행, 호흡·체중 이동을 쓴다. 단순 컷에는 한 변화면 충분하다. 클로즈업일수록 움직임을 절제한다.
- 반복 인물의 행동 핵심·습관 발동 조건·감추는 태도를 잠그고 현재 자세에 맞게 번역한다. 걷는 습관을 앉은 장면에 붙이지 않는다. 미세동작은 감정/자극에 연결하고 기계적 깜박임 주기를 강제하지 않는다.
- 상대의 핵심을 이해하는 시점에 듣는 반응을 배치한다. 군상 반응은 시차·강도를 달리하고, 앞 컷의 숨·손·피로·감정 잔여 상태를 다음 컷으로 넘긴다. 정지감은 살아 있는 긴장이지 프레임 동결이 아니다.
- 대사가 있을 때만 승인된 음색/말속도/억양과 정확한 대사를 오디오 규격에 반영한다. 비화자의 임의 발화·입모양을 검사한다. 연결용 앞 대사는 최종에서 중복 재생하지 않는다. 음성·립싱크는 실제 청취/재생 전까지 미검증이다.

### QC

- 다인물 공간 샷만 필요할 때 짧은 배치 확인을 둔다. 액션 중간 시작은 첫 프레임과 양립할 때만 사용한다. 공간 전환·크기는 문턱·비교물로 증명한다. 전체상 숏은 상하 여백, 부품은 실제 지지점·연결부를 확인한다.
- 과한 HDR·전면 주황빛·플라스틱 피부·과선명 테두리를 QC한다. 영상은 시작·중간·끝 표본과 실제 재생으로 광원 튐·질감 끓음을 확인한다. 미검증이면 PASS하지 않는다.
- 얼굴 교체·인물 복제·죽은 눈·과장 연기·손 접촉·피부/재질 끓음·광원/시선/스케일 오류를 QC한다. 한 원인씩 수정·기록하고 반복 실패는 동작 분할/구도 변경으로 푼다. 손·얼굴 결함 정리 후 인접 컷의 색과 현장 분위기음을 맞춘다. 불안정한 핸들만 검사 후 자른다.

### Boundaries

Hell Grind와 페이퍼로지(5:47–6:36)는 제작 경험이지 효능 보증이 아니다. 원문의 모델 교체, 영어 강제, 연령 숨김/필터 회피, 고정 1초 와이드·10–15회 재시도·0.5초 일괄 트림·8K/IMAX 문구는 수입하지 않는다. 음악 우선·한글 프롬프트·길이·참조·안전·제공자 규칙은 각 소유 문서 그대로다.

### Related

- [[live-action-character-authenticity-casting-standard]]
- [[video-camera-composition-grammar]]
- [[character-bible-page-prompt-standard]]
