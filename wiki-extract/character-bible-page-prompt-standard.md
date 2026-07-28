---
title: Character Bible Page Prompt Standard
created: 2026-06-21
updated: 2026-07-22
type: concept
tags: [video-production, multimodal, qc]
sources: [raw/transcripts/character-bible-page-prompt-user-directive-2026-06-21.md, concepts/video-team-seed-system.md, raw/transcripts/hermes-session-capture-20260722-135635.md]
confidence: high
contested: false
contradictions: []
---

# Character Bible Page Prompt Standard

## Definition

사용자가 승인한 영상팀 캐릭터시트 기본값: 단순한 정면 모델시트만 만들지 말고, 필요할 때 **AAA 게임 아트북 / 애니메이션 캐릭터 바이블 / 프랜차이즈 visual development sheet**처럼 한 장 안에 hero pose, turnaround, expression sheet, outfit/accessory callout, weapons/tools/companions, color palette, lore identity가 모두 보이는 고밀도 캐릭터 디자인 바이블 페이지를 만든다.

이 페이지는 [[video-team-seed-system]]의 Character Creator 단계와 연결된다. 반복 캐릭터가 있는 MV/공모전/브랜드/애니 영상에서 캐릭터 승인·마케팅성·스타일락을 동시에 잡을 때 우선 적용한다.

## When to use

다음 요청에서는 이 표준을 기본으로 적용한다.

- “캐릭터시트”, “캐릭터 시트”, “character sheet”, “character bible”, “캐릭터 바이블”
- recurring protagonist / mascot / performer / fictional entity approval
- Seedance multi-reference block 전에 character identity를 고정해야 하는 경우
- 사용자가 “AAA”, “게임 아트북”, “공식 설정화”, “프랜차이즈 느낌”, “디자인 바이블”을 요구하는 경우

## Three-tier output and route boundary

기존 영상팀 규칙도 유지한다. 목적이 다르면 산출물도 분리한다.

1. **APPROVAL_BIBLE / Character Bible Page** — 사용자 승인/캐릭터 매력/마케팅성/세계관 제시용. 한 장 안에 hero action pose + callout panels + palette + identity notes를 허용한다. 단, AI가 글자를 깨뜨릴 수 있으므로 중요한 텍스트 정보는 별도 Markdown approval card에도 저장한다.
2. **PRODUCTION_MASTER / Clean Identity Model Sheet** — identity source of truth. Neutral/off-white background, flat lighting, aligned multi-angle/expressions/hands/costume/scale, no readable text/logos. 승인된 Bible/identity 이미지를 실제 image reference로 첨부해 만든다.
3. **PROVIDER_SAFE_REF** — locked master에서 파생한 무텍스트·무라벨 clean sheet 또는 deterministic angle/expression crop. Source master/hash/revision/provenance를 기록한다.

Route boundary (2026-07-28 정정): **두 팀 모두 clean production sheet를 Seedance Multi-reference에 올린다.** 차이는 styleframe 유무다 — 기존 I2V 팀은 `styleframe + clean sheet`를 함께 올리고, No-I2V Reference-Native 팀은 styleframe 없이 `clean sheet + 배경 시트`만 올린다. 어느 route든 업로드 가능한 것은 `PROVIDER_SAFE_REF` 등급(무텍스트·플랫조명·crop-safe)뿐이며, **고밀도 Bible 페이지는 어느 route에서도 provider reference가 아니다** — 텍스트·라벨·패널 격자가 생성물을 오염시킨다.

즉, 사용자가 “캐릭터시트”라고만 말하면 먼저 **Character Bible Page** 감각을 제안하되, 실제 영상 생성에는 production master와 route에 맞는 provider-safe 파생 자산을 함께 준비한다.

## Live-action casting override

실사 인물은 아래의 generic AAA/animation skeleton을 그대로 쓰지 않는다. 먼저 [[live-action-character-authenticity-casting-standard]]에 따라 casting brief와 identity signature 8–12개를 잠그고, **매력 = 완벽한 미용 얼굴**이 아니라 역할 적합성·기억점·카메라 생명력·표정 잠재력·상대와의 대비로 평가한다.

- Bible hero visual은 beauty campaign이 아니라 casting callback / wardrobe fitting의 살아 있는 순간으로 만든다.
- `perfect`, `flawless`, `idol visual`, `V-line`, `porcelain/glass skin`, 완전 대칭을 금지한다.
- 피부·눈·치아·귀·헤어라인·손과 자연스러운 미세 비대칭을 100% crop으로 QC한다.
- 승인된 Bible 이미지를 실제 reference input으로 사용해 clean production sheet를 생성한다. 텍스트 기억만으로 다시 만들지 않는다.
- Bible PASS 4.2/5, Clean Production PASS 4.3/5와 hard-fail 0을 통과하기 전 영상 reference로 쓰지 않는다.
- 기존 I2V 팀은 sheet-conditioned styleframe을 먼저 만든 뒤, Seedance에 그 styleframe과 clean sheet를 함께 올린다. Reference-Native 팀은 styleframe 단계 없이 clean sheet를 올린다.

## Canonical prompt skeleton

아래 구조를 ChatGPT Image 2 / gpt-image-2 캐릭터 생성 프롬프트의 기본 골격으로 쓴다. 프로젝트에 맞게 `[PLACEHOLDERS]`를 채운다.

```text
Create a highly detailed professional character design bible page for [CHARACTER].
The final image should look like an official AAA game artbook, animated series character bible, premium concept art sheet, or franchise visual development document.

MAIN HERO VISUAL
The character is the absolute focal point of the page. Display a large dynamic action pose occupying a significant portion of the layout. Use strong perspective distortion, dynamic foreshortening, energetic body language, dramatic silhouette, and cinematic movement. The pose should immediately communicate: [PERSONALITY]. The character should feel alive, charismatic, iconic, and highly marketable.

CHARACTER IDENTITY
Character Name: [CHARACTER NAME]
Alias: [TITLE OR NICKNAME]
Age: [AGE]
Height: [HEIGHT]
Faction: [FACTION]
Occupation: [ROLE]
Short lore description: [BACKGROUND STORY]

TURNAROUND SHEET
Include professional model sheet views: Front View, Side View, Back View. Maintain perfect design consistency. Show proportions, clothing construction, hairstyle structure, silhouette readability, and equipment placement.

EXPRESSION SHEET
Include multiple facial expressions: neutral, confident, smiling, angry, surprised, determined. Keep design consistency across all expressions. Show emotional range and personality.

OUTFIT BREAKDOWN
Create detailed outfit analysis panels. Label and visually highlight jacket, shirt, armor, accessories, gloves, belt, pants, boots, gadgets. Show material differences such as leather, fabric, metal, carbon fiber, futuristic materials, or magical materials.

ACCESSORY DETAILS
Include close-up detail windows for jewelry, insignias, tattoos, eyewear, weapon grips, device screens, badges, and emblems. Each detail should appear as a professional concept-art callout.

WEAPONS / TOOLS / COMPANIONS
Display supporting equipment separately, with multiple angles and detail views: [SWORD / RIFLE / HOVERBOARD / DRONE / MOTORCYCLE / MAGICAL STAFF / SUMMON CREATURE / ROBOT COMPANION / PROJECT-SPECIFIC PROP].

VISUAL DESIGN LANGUAGE
Style: [STYLE]. Extremely clean linework, readable shapes, strong visual hierarchy, professional production-art quality.

COLOR SYSTEM
Include a dedicated color palette section with primary color, secondary color, accent color, and neutral tones. Colors must reinforce character identity.

PAGE DESIGN
White concept-art background, professional layout grid, artbook presentation, graphic design elements, technical notes, character callouts, design annotations, studio-quality visual development sheet, high information density, AAA production quality, official franchise character bible aesthetic. No watermark, no UI, no cropped elements.
```

## Required Character Creator approval card

이미지 프롬프트와 별도로, Character Creator는 다음 정보를 한국어 approval card로 남긴다. AI 이미지 안의 텍스트가 깨져도 이 카드가 source of truth다.

```markdown
## Character Bible Approval Card
- Character name:
- Alias:
- Age / height:
- Faction / occupation:
- Personality in one phrase:
- Short lore:
- Core silhouette:
- Face/hair identity lock:
- Outfit/material lock:
- Props/weapons/companions:
- Palette:
- Must avoid:
- Downstream Seedance refs needed: hero crop / turnaround / expressions / hands-props / tool closeups
- Character ID / recurrence role:
- Route: standard_i2v / no_i2v_native
- Master sheet revision / identity lock SHA256:
- Provider-safe assets:
- Role separation / scale relation:
```

## QC checklist

- [ ] 큰 hero action pose가 즉시 성격을 말해준다.
- [ ] Front/Side/Back turnaround가 같은 인물·같은 의상·같은 비율로 보인다.
- [ ] 표정 6종이 동일 인물로 유지된다.
- [ ] 의상 구조와 소재 차이가 명확하다.
- [ ] 액세서리/무기/도구/동반자가 character identity와 연결된다.
- [ ] 컬러 팔레트가 캐릭터 성격과 faction을 강화한다.
- [ ] 페이지가 AAA artbook / franchise bible처럼 보이고, 단순 2x2 collage나 랜덤 contact sheet처럼 보이지 않는다.
- [ ] Seedance/I2V용으로 필요한 clean crop/reference를 추출할 수 있다.
- [ ] 실제 영상 reference로 쓸 때는 깨진 텍스트·작은 라벨·복잡한 callout을 제외하거나 clean sheet를 별도로 만든다.
- [ ] 실사 인물은 [[live-action-character-authenticity-casting-standard]]의 casting/authenticity 점수와 hard-fail을 통과한다.

## Episode pair / multi-case sheets — 2026-07-15

멀티 에피소드 숏폼(예: `오늘의 자동완성`)에서 에피소드마다 고정 페어가 있을 때는 Bible 고밀도 페이지와 별도로 **clean identity pair sheet**를 만든다.

- 한 후보 시트 = 한 고정 페어만. 다른 에피소드 캐스트/장면 소품/스토리 합성을 넣지 않는다.
- 기본 뷰: neutral turnaround + expression. action thumbnail은 최대 1개.
- 남성 헤어스타일은 후보 A/B/C에서 의도적으로 다르게 해 선택 축을 만든다.
- 에피소드 시트 승인 전에는 payoff styleframe/I2V를 시작하지 않는다.
- Gongnyang/image-prompt compile이 켜져 있어도 character-sheet-first와 pair lock이 우선한다 ([[gongnyang-image-prompt-codex-integration]]).

## Related pages

- [[video-team-seed-system]]
- [[video-project-seed-template]]
- [[anime-aesthetic-ai-production-playbook-2026-06-21]]
- [[seedance-prompting-knowledge]]
- [[live-action-character-authenticity-casting-standard]]
- [[ai-photoreal-portrait-prompting-2026-05-30]]
- [[gongnyang-image-prompt-codex-integration]]
