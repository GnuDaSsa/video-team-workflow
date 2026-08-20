---
title: Three-Panel Character Identity Triptych Standard
created: 2026-06-21
updated: 2026-08-21
type: concept
tags: [video-production, multimodal, character-design, qc]
sources: [raw/articles/higgsfield-hell-grind-production-brief-2026-08-21.md, concepts/video-team-seed-system.md, concepts/live-action-character-authenticity-casting-standard.md]
confidence: high
contested: false
contradictions: []
---

# Three-Panel Character Identity Triptych Standard

## Definition

영상팀의 기본 캐릭터시트는 **16:9 가로형 3분할 정체성 마스터**다. 한 장 안에서 동일 인물의 역할을 분리한다.

1. 왼쪽: 머리를 의도적으로 생략한 정면 전신 — 체형, 비율, 손, 신발, 의상 전면.
2. 가운데: 머리를 포함한 후면 전신 — 헤어 뒤 실루엣, 의상 후면, 액세서리 위치.
3. 오른쪽: 크게 배치한 자연스러운 3/4 얼굴·어깨 초상 — 유일한 얼굴 정체성 기준.

정면 전신의 작은 얼굴을 없애는 이유는 영상/이미지 모델이 흐릿한 소형 얼굴을 정체성 기준으로 복제하지 못하게 하기 위해서다. 머리 생략은 깨끗한 칼라/목선 경계의 비폭력적 스튜디오 레퍼런스 크롭이어야 하며, 부상·절단·마네킹처럼 보이면 실패다.

## Default route

- 파일명: `CHAR_<ID>_TRIPTYCH_R<n>`.
- 배경: 중성 중간 회색, 무텍스트, 무UI, 무로고.
- 광원: 플랫하거나 한 방향의 큰 소프트 라이트. 실제 피부·소재 색을 판독할 수 있어야 한다.
- 금지: 시네마틱 LUT, 영화 그레인, 비·연기·야간광, 드라마틱 세트, 뷰티 리터칭. 캐릭터시트는 의도적으로 평범해야 한다.
- 동일 상태: 얼굴 구조, 헤어 질량, 나이 인상, 체형, 의상, 소재, 액세서리를 세 패널에서 고정한다.
- 반복 캐릭터마다 독립 triptych가 필요하다. 반복 조연/커플/보호자도 예외가 아니다.

사용자가 명시적으로 AAA 바이블/설정화/마케팅 페이지를 요구하면 별도의 `APPROVAL_ART`를 만들 수 있다. 그러나 이는 정체성 source of truth나 provider 입력이 아니다. 기본 “캐릭터시트” 요청은 triptych를 뜻한다.

## Immutable identity and state assets

정체성은 **불변 descriptor + 승인 이미지 + provenance**다. 젖음, 상처, 변신, 의상 손상, 코트 착탈, 연령대, 위장처럼 화면에 영향을 주는 상태는 별도 파생 자산으로 등록한다. 마지막 승인본에서 한 변수만 바꾸며, 전체 시트를 거듭 재생성하지 않는다.

기록 항목:

- character ID / role;
- immutable face·hair·body·wardrobe descriptor;
- source reference path/hash;
- imagegen generation ID와 prompt hash;
- dimensions / bytes / output SHA256 / revision;
- state change와 forbidden changes.

## Deterministic derivatives

Provider/샷 특성에 따라 승인 마스터를 비생성형으로 크롭한다.

- `_FACE`: 오른쪽 큰 초상;
- `_FRONT_BODY`: 왼쪽 정면 전신;
- `_BACK_BODY`: 가운데 후면 전신.

마스터 SHA256과 정확한 크롭 좌표를 기록하고, 패널 경계·거터가 남으면 실패다. 클로즈업은 `_FACE`, 전신/의상 방향이 중요한 샷은 triptych 또는 필요한 body crop만 쓴다. 세 크롭을 습관적으로 모두 올리지 않는다.

## Provider binding

Triptych 자체를 Multi-reference에 넣을 수 있지만, 모델 프롬프트에 패널 역할을 명시해야 한다.

```text
@ImageN의 오른쪽 큰 3/4 초상은 얼굴 정체성·피부·눈빛 기준, 왼쪽 머리 없는 정면 전신은 체형·의상 전면 기준, 가운데 후면 전신은 헤어 뒤 실루엣·의상 후면 기준으로만 사용한다. 회색 배경·3분할·패널 경계·빈 머리 부분은 결과에 재현하지 않는다. 포즈·구도·조명은 현재 샷 지시를 따른다.
```

정체성 레퍼런스는 구도, 포즈, 시작 프레임, 장면광을 지시하지 않는다. 그것은 샷 계약의 역할이다.

## Stress gate

승인 후보를 서로 다른 포즈·거리·조명·행동으로 10회 생성한다. 관계 장면이 있으면 다른 인물과 함께 있는 테스트도 포함한다. 얼굴 실루엣, 눈 간격, 코/턱, 헤어 질량, 나이, 체형, 의상과 역할이 10/10 동일하게 인식되어야 production lock이다.

실패 시 긴 프롬프트를 덧붙이지 않는다. descriptor 또는 한 레이아웃 변수만 바꾸고 재검증한다.

## Minimal prompt skeleton

```text
Create one text-free 16:9 landscape film-production character identity triptych for [CHARACTER], arranged as three neutral studio photographs side by side on one seamless mid-gray background.

IDENTITY LOCK
[Immutable face, hair, age, body, outfit, material, accessory, and role descriptors.]

PANEL LAYOUT
Left: complete front full body on a level baseline; omit the head above a clean collar/neckline boundary so no small face appears, presented as a non-graphic studio-reference crop.
Middle: complete back full body with the head and rear hair silhouette visible, same scale and baseline.
Right: one large natural 3/4 head-and-shoulders portrait of the same identity, neutral attentive expression and one coherent soft catchlight.

REFERENCE RENDERING
Flat or softly one-directional neutral studio light, true skin/material color, consistent perspective, plain mid-gray seamless background. Preserve one person, one wardrobe state, and one coherent anatomy. No text, UI, dramatic set, cinematic grade, grain, beauty retouch, duplicate face, or extra figure.

AR 16:9
```

고가치 프롬프트는 [[gongnyang-image-prompt-codex-integration]]으로 컴파일하고 checker `ok: true`를 통과한 뒤 Codex imagegen을 호출한다.

## QC

- [ ] 정확히 왼쪽 정면 전신(머리 없음) / 가운데 후면 전신(머리 있음) / 오른쪽 큰 3/4 얼굴 순서다.
- [ ] 오른쪽 초상이 유일한 얼굴 source이고 100% crop에서 정체성을 판독할 수 있다.
- [ ] 세 패널의 비율·의상·소재·액세서리가 동일하다.
- [ ] 중성 회색·중성광·실제 색이며 텍스트/그레인/LUT/장면 배경이 없다.
- [ ] provenance와 결정적 크롭 좌표가 기록됐다.
- [ ] 10회 스트레스 테스트가 10/10이다.
- [ ] 실사 인물은 [[live-action-character-authenticity-casting-standard]]의 피부·눈·헤어·해부 hard fail도 통과한다.

## Route boundary

- production styleframe은 계속 한 컷 = 한 독립 이미지다. triptych는 정체성 디자인 예외이며 final frame/storyboard가 아니다.
- `standard_i2v`: styleframe + 최소 triptych/crop.
- `no_i2v_reference_native`: 최소 identity/environment ref만 사용하고 샷 프롬프트가 구도·블로킹을 담당한다.
- pre-lock frame은 `HOLD_LOOKDEV_ONLY`이며 승인 triptych를 실제 첨부해 재생성해야 한다.

## Related pages

- [[video-team-seed-system]]
- [[live-action-character-authenticity-casting-standard]]
- [[seedance-prompting-knowledge]]
- [[gongnyang-image-prompt-codex-integration]]
