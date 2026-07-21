---
title: Video Typography Operating Manual
created: 2026-05-12
updated: 2026-06-09
type: concept
tags: [video, multimodal, method]
sources: [video-typography/hourly/2026-05-12-09.md, video-typography/hourly/2026-05-12-20.md]
confidence: medium
contested: false
contradictions: []
---

# Video Typography Operating Manual

2026-05-12의 Hourly Video Typography Wiki Upgrade 회차들에서 나온 지식을 실제 제작 판단에 바로 쓰기 위한 운영 매뉴얼. 세부 규칙/사례/회차별 근거는 [[video-typography-dataset]]에 누적하고, 이 페이지는 **짧게 읽고 결정하는 표준 의사결정 레이어**로 쓴다.

## 핵심 교리

1. **음악/프레이즈가 먼저다.** 공공·관광 영상도 BGM 구조, 비트 악센트, 프레이즈 전환, 엔딩 호흡에 컷과 타이포 진입을 맞춘다.
2. **타이포는 장식이 아니라 편집 시스템이다.** 폰트/효과보다 먼저 타이밍, 정보 역할, 읽기 호흡을 결정한다.
3. **가독성은 모션으로 해결하지 않는다.** 문장을 줄이고, 위계를 나누고, 엔드포인트 홀드를 확보한 뒤에만 모션을 검토한다.
4. **CapCut preview/export가 source of truth다.** JSON 좌표·템플릿·타임라인 값은 보조일 뿐, 실제 미리보기와 샘플 export가 최종 판단 기준이다.
5. **공공과 MV의 차이는 주로 copy layer에서 생긴다.** 둘 다 음악-우선 편집이지만, 공공/기관은 설명과 역할 분리가 우선이고 MV는 더 시적·희소·리듬 중심일 수 있다.

## 모드별 선택 로직

| 모드 | 기본 텍스트 방식 | 모션 예산 | 가장 큰 위험 | 권장 해법 |
|---|---|---:|---|---|
| 공모전 / 관광 / 공공기관 | motif가 왜 필요한지 설명하되 title/place/body/disclosure/CTA 분리 | 문장당 0–1회 | 프레젠테이션 자막처럼 보임 | 챕터 카드·엔드 카드·절제된 본문 |
| 시네마틱 관광 캠페인 | 컷 내부 텍스트 최소화, 이미지와 음악을 주연으로 둠 | 핵심 태그라인만 | 미장센 위에 설명을 과하게 얹음 | 장소 라벨 + 정보 회수 카드 |
| MV / lyric / song-first | 희소하고 시적이며 훅 중심 | 훅/키워드만 | 모션 과잉으로 가사 읽힘 붕괴 | phrase-timed entry → hold → exit |
| Data / route / guide | 리스트·동선·단계형 정보 | 느린 스크롤 또는 정적 블록 | 한 컷에 정보 과밀 | 1컷 1정보 단위 |

## 재사용 제작 파이프라인

1. **Audio/brief pass** — BGM 프레이즈, 악센트, 훅, 내레이션 pause, 엔딩 cadence를 먼저 표시한다.
2. **Role map** — 모든 텍스트를 `TITLE`, `LOCATION`, `BODY/NARRATION`, `DISCLOSURE`, `CTA`로 분류한 뒤 스타일링한다.
3. **Caption spec lock** — 폰트 페어, safe-zone, 줄바꿈 규칙, 강조 우선순위, 금지 스타일을 선잠금한다.
4. **Motion budget lock** — 문장/컷마다 정지, fade-only, 1회 강조 모션 중 하나로 제한한다.
5. **CapCut implementation** — 가능하면 editable text layer를 유지한다. 한글 폰트 fidelity가 깨지면 의도적으로 외부 transparent overlay를 만들고 CapCut draft에 다시 정렬한다.
6. **Caption/STT isolation** — Auto Captions는 전용 격리 프로젝트에서 생성 → 정규화 → 메인 프로젝트 이식으로 처리한다.
7. **Sample export gate** — 새 템플릿·폰트·오토캡션 변경 후에는 캡션이 포함된 8–12초 샘플 export를 먼저 확인한다.
8. **Visual QC gate** — 실제 preview/export에서 overlap, jitter, 1-frame flash, export drift, line clipping, glyph-edge alignment를 본다.

### Typography Contract Gate — 실행 브리지

위키 규칙이 실제 편집에 안 붙는 경우, Editor에게 바로 “타이포 개선”을 맡기지 않는다. 먼저 Director가 프로젝트별 `Typography Contract`를 만든다. 이 계약은 각 텍스트 이벤트마다 `time range / copy / role / scene risk / placement / style token / motion budget / hold target / QC proof`를 고정한다. Editor는 이 계약을 CapCut editable text layer로 구현하고, QC는 계약 row별 PASS/FAIL/REWORK를 남긴다.

Contrast/size/shadow만 좋아진 export는 “증상 개선”일 수 있지만, role hierarchy·safe-zone·subject clearance·Korean line break·hold-time까지 통과해야 “위키 타이포 개념 적용”으로 인정한다. 재사용 시작점은 [[video-typography-contract-template]]이다.

## 타이포 역할 시스템

- **TITLE / CHAPTER:** 가장 크고 짧다. 프레이즈 시작/전환에 맞추며, generic presentation title처럼 보이면 실패다.
- **LOCATION NOTE:** 반복 가능한 장소 라벨. corner/side-safe이되, 휴대폰에서 보이지 않는 museum caption처럼 작아지면 안 된다.
- **BODY / NARRATION:** 차분하고 보통 unboxed/near-unboxed. 화면에 충분한 hold와 시각적 여백이 있을 때만 둔다.
- **DISCLOSURE / FOOTNOTE:** 작고 안정적이며 story와 경쟁하지 않는다.
- **CTA / FINAL STATEMENT:** optically centered. 본문과 역할·크기·위치를 분리하고 pill/box misalignment를 금지한다.

## 9:16 배치 규칙

- lower-center body subtitle은 기본 unsafe로 본다. player UI, 자막 UI, 발/손/차량/액션이 하단 1/3을 자주 점유한다.
- 프로젝트 기본 자산으로 **ALT position set**을 만든다: upper-left, upper-right, mid-left, mid-right, side-block.
- 위치는 습관이 아니라 cut geometry로 고른다. 피사체·동작·중요 prop이 하단에 있으면 본문은 위나 측면으로 보낸다.
- horizon line 위에는 텍스트를 직접 얹지 않는다. 위/아래로 살짝 이동하고, 필요한 경우 절제된 contrast support만 쓴다.

## Motion Budget 규칙

- 공공/관광 본문: 기본은 static 또는 fade-only.
- MV/lyric: 훅 단어/구절 1개만 움직이고, supporting text는 정지시킨다.
- 움직이는 텍스트는 반드시 **entry → readable hold → exit** 구조를 가진다.
- 읽히지 않으면 glow/shake/morph를 추가하지 말고, copy length, line break, size, timing을 먼저 고친다.
- 모션은 의미를 번역해야 한다: emphasis, tension, delay, release, route, transition 중 하나와 연결되지 않으면 쓰지 않는다.

## 한국어 가독성 규칙

- 강조 우선순위: weight → size → tracking/leading → subtle contrast support → color.
- 조사/어미를 의미 단위에서 떼지 않는다.
- 장문 내레이션은 font size를 줄이기보다 문장을 줄인다.
- phrase A가 phrase B로 교체될 때는 B도 A만큼 단독 reading breath를 가진 뒤 lower support line을 붙인다.

## CapCut 리스크 플레이북

- Auto Captions는 편의 기능이 아니라 **납기 리스크 subsystem**이다. recognition stall, template jump, export failure, preview/export mismatch가 반복될 수 있다.
- 표준 workflow: `Generate in isolation → Normalize typography → Transplant into main timeline`.
- recognition이 특정 progress에서 멈추면 language fixed mode, audio-only, shorter sample, cache/performance 점검, web/alternate STT route를 순서대로 고려한다.
- caption export 표준: ASCII-only path를 쓰고, 실패 시 TXT export → 외부 UTF-8 SRT 변환으로 우회한다.
- 새 caption template/font/auto-caption batch는 full delivery 전에 caption-included sample export를 통과해야 한다.

## 금지/실패 패턴

- lower-center narration을 큰 검은 rounded box에 넣는 방식.
- 하나의 굵은 발표용 폰트로 title/place/body/disclosure를 모두 처리하는 방식.
- color/glow를 정보 위계의 주수단으로 쓰는 방식.
- hold가 없는 빠른 rhythm cut에 설명 본문을 억지로 얹는 방식.
- CapCut JSON 좌표 equality를 실제 glyph alignment로 착각하는 방식.
- captions/templates 변경 후 preview만 보고 export를 생략하는 방식.
- 공공 제출 copy에서 제작 의도, 시놉시스, AI 활용 내역, 링크/password notes를 같은 문단으로 재사용하는 방식.

## 관련 페이지

- [[video-typography-dataset]] — append-only rule bank와 hourly additions.
- [[_mocs/video-production]] — video-production 지식 지도.
- [[llm-wiki-method]] — raw/working note를 durable wiki page로 컴파일하는 방식.

## Sources / provenance

- Hourly notes: [[video-typography/hourly/2026-05-12-09]] through [[video-typography/hourly/2026-05-12-20]].
- CapCut operational references captured in the hourly notes: Auto captions, recognition lagging/stuck, captions export failure, text-entry issue help pages.
- Typography/reference hubs captured in the hourly notes: CreativeBloq kinetic typography examples, Motionographer, Art of the Title, KTO/VisitKorea/VisitSeoul video examples.

## Update 2026-05-12 22:10KST — CapCut font-field fidelity gate / no baked-overlay final when user rejects it

- If the user explicitly says baked/videoized subtitle overlays are undesirable, **do not deliver a transparent/baked typography overlay as the main final**, even when it looks better. Keep CapCut editable text layers as the primary deliverable.
- For this user's CapCut font complaints, glyph appearance alone is not enough. The actual CapCut inspector font field must also be checked; if it still says `시스템`, treat the pass as not finished.
- macOS-installed custom Korean fonts can render different glyphs in CapCut while the inspector still displays `시스템`; that does not satisfy the user's font-fidelity requirement.
- Prefer a CapCut-recognized internal/free font when inspector-name fidelity matters. In the KAIA V33 pass, `경기천년제목B` was verified in the actual CapCut font field for both title and body; a body candidate (`고운한글돋움`) was rejected because it triggered a Pro/export blocker.
- QC artifact standard: save at least one actual CapCut UI proof screenshot showing the selected text layer and non-`시스템` font field, plus the exported contact sheet and draft JSON assertion that no baked overlay track is present.

## Update 2026-05-12 22:32KST — CapCut rich-text font patching order

- CapCut editable text can store font data twice: top-level text material fields (`font_name`, `font_path`, `font_resource_id`) and rich text runs inside `content.styles[].font`.
- If only the top-level fields are changed, the actual CapCut inspector may still show the old font. Patch both layers.
- Do not patch while CapCut has the draft open; on quit, CapCut can overwrite disk edits with its in-memory draft. Correct order: **quit CapCut → patch active JSON/template files including `template-2.tmp` and timeline copies → reopen → select title/body clips in the UI → confirm font fields → export**.
- KAIA V34 replaced the weak single-font `경기천년제목B` compromise with a more appropriate editable public-tech pairing: `Gothic A1 Black` for title/keyword/chapter and `Noto Sans KR` for explanatory body copy.

## Update 2026-05-12 22:45KST — Wiki-first editor mindset gate

- For this user's typography work, the editor must treat `~/wiki/video-typography/` as a required preflight knowledge source before making caption/font decisions.
- The editor's decision order is now: **read wiki → lock text roles → choose Display/Text pair → tune weight/size/leading/contrast → verify in CapCut preview/export**.
- A text layer that is too small to read at normal preview distance is not “subtle”; it is failed information design. Enlarge it, move it to a cleaner cut, or remove it.
- Micro labels such as chapter/status/kicker text must pass the same readability gate as main captions. Decorative labels are allowed only when they are intentionally non-semantic; public-contest explanatory labels are never decorative.
- If support/body text under a main headline is unreadable, do not keep it as texture. Shorten copy or give it a separate readable hold.

## KAIA V38 lesson — readability vs crowding balance — 2026-05-12
- When improving public-contest typography, do not only enlarge weak body text. A too-large body layer can become new overlap against the main title.
- Preferred fix order: remove meaningless micro labels → convert role labels to Korean → strengthen body contrast/stroke → increase size moderately → check contact sheet → reject if body crowds main title.
- For CapCut editable text, keep final typography editable unless explicitly approved otherwise. Use baked overlays only as a font-fidelity workaround, not as the default answer.
- If a larger iteration is more readable but visually crowded, roll back to the previous spacing and strengthen contrast instead of continuing to scale up.

## Failure lesson — KAIA typography regression, direct CapCut editing required — 2026-05-12
- Do not treat CapCut JSON coordinate edits as typography design. They can preserve data while destroying visual hierarchy, spacing, and legibility.
- If the user says the edit looks bad, stop JSON iteration immediately and switch to direct CapCut UI editing.
- For public-contest review masters, unreadable micro labels are worse than no labels. Remove them before trying to polish them.
- Minimum rescue rule: leave only one readable main text layer at a time, then rebuild supporting captions manually only where the preview proves they help.
- Actual CapCut preview/contact sheet is the pass/fail source. If a screenshot shows overlap, it is a fail regardless of internal text/material structure.

## Update 2026-06-08 KST — Shadow/legibility as scene lighting, not a checkbox
- New active reference: [[video-typography-shadow-legibility-playbook]].
- Correction from ACC: Pretendard GOV + weak stroke/shadow is not enough. If every caption uses the same white-fill/black-rim formula, it still reads as a pasted subtitle, not designed typography.
- Required decision before CapCut editing: choose contrast mode per event: dark-hero on bright architecture, ivory on dark/cool architecture, body over mixed image, or disclosure micro-copy.
- Shadow recipe is scene-specific: opacity, blur/smoothing, distance, rim width, and fill color must change according to background luminance and text role.
- QC now rejects “no visible design change” even if font field is non-system and export is technically valid.


## Update 2026-06-09 KST — Study-only correction after ACC typography rejection
- Active study page: [[acc-exhibition-typography-study-2026-06-09]].
- If the user says to study until a specified time, do not continue generating CapCut drafts/exports during that window.
- ACC lesson: public cultural video typography should be studied as moving exhibition signage/labels, not as subtitle decoration.
- Completion requires a study brief first; production comes after the study window or explicit user override.

## Update 2026-06-09 00:45KST — reduction before typography styling
- ACC study exposed a structural failure mode: if a public/cultural film carries many similar two-line BODY captions, changing the font or shadow does not create a new typography system.
- Required preflight for rejected typography: first classify every text event as `title / theme marker / object label / support`, then delete or demote lines that are merely narration. Only after this reduction may the editor choose fonts, shadows, and positions.
- Korean timed-text discipline is a useful floor even for non-dialogue captions: short lines, normally one line, max two lines, and redundant on-screen text should be removed rather than restyled.
- Shadow/stroke must be treated as luminance contrast engineering. Choose background zone and fill mode first; then tune stroke/shadow. Hue swaps are not a design pass.

## Update 2026-06-09 00:37KST — row-level contract before rejected typography revisions
- When a user rejects typography as unchanged, a general style brief is not enough. Create a row-level contract before editing: each existing text event must be marked `keep / shorten / delete / convert role / conditional`.
- Do not apply a new font pair to an old SRT if the old SRT was the source of the sameness. Copy reduction/reclassification precedes font implementation.
- For ACC, the row-level contract lives at `ACC_post0400_row_level_typography_contract_STUDY_ONLY_20260609.md` and is the required post-04 execution bridge.

## Update 2026-06-09 00:39KST — rejected typography execution order
- For a rejected public/cultural typography pass, the editor must follow this order: time/user gate → copy reduction → role map → font pair → contrast/placement → motion/timing → CapCut proof/export QC.
- A font patch is not an implementation start if the old copy map caused the sameness. The first implementation act is deleting/deactivating weak rows and confirming the reduced role contract.
- Keep a row-level QC table with font-field proof, placement proof, contrast proof, and hold proof for each remaining text event.

## Update 2026-06-09 00:41KST — reference study must become proof rules
- For future typography “study” windows, do not stop at source lists. Convert every reference into `source → principle → project rule → implementation implication → QC proof`.
- A reference that does not alter copy reduction, role hierarchy, font role, contrast mode, timing, or proof requirements has not yet affected the edit.
- ACC study artifact: `ACC_reference_to_rule_matrix_STUDY_ONLY_20260609.md`.

## Update 2026-06-09 00:43KST — study synthesis handoff before production resumes
- When a study-only window creates multiple notes, create a synthesis/index before production resumes. It must state: what failed, non-negotiable rules, reduced row map, font system, proof requirements, and the exact next resume point.
- For ACC, the synthesis index is `ACC_until0400_study_synthesis_index_STUDY_ONLY_20260609.md`.
- Accidental renders made during a study-only window are failure context, not completion evidence.

## Update 2026-06-09 00:45KST — contact-sheet architecture beats font audit
- A font audit can pass while the contact sheet still fails. If thumbnails still show repeated body-subtitle panels, typography has not changed enough.
- For ACC-like public/cultural films, next contact sheet must show information architecture: title/signage/final plus only sparse theme/object labels. More than two body-caption-looking frames after a rejection is a fail unless the user explicitly requests narration captions.
- Existing artifact: `ACC_visual_failure_audit_CONTACT_ONLY_STUDY_20260609.md`.

## Update 2026-06-09 00:51KST — submission fields should absorb explanation
- In public-contest/institution videos, do not force 제작 의도/시놉시스/AI 활용 내역 into on-screen captions. Use submission fields and descriptions for explanation; keep screen typography sparse.
- If deleting a body caption feels like losing meaning, first check whether that meaning already exists in submission copy. Do not re-add it to the screen unless the visual cannot stand without it.
- ACC artifact: `ACC_submission_display_copy_separation_STUDY_ONLY_20260609.md`.

## Update 2026-06-09 00:57KST — CapCut font-field proof must cover roles
- After a rejected font pass, do not verify only the opening title. Check representative rows across display/title, theme label, signage/final, and disclosure/support.
- For ACC, `ACC_post0400_capcut_font_field_verification_STUDY_ONLY_20260609.md` defines the post-04 proof protocol.
- `시스템` remains not accepted for this user's font-fidelity complaints unless an explicit workaround is documented and accepted.

## Update 2026-06-09 00:59KST — Korean line-break protocol for ACC
- Add W3C Hangul layout requirements as a reference for Korean text handling: https://www.w3.org/TR/klreq/.
- For ACC-style public/cultural captions, one short semantic phrase is the default. Two-line text is allowed only when it is a deliberate title/final/signage composition, not an explanatory body-caption habit.
- Do not shrink type to preserve a long Korean sentence; shorten, delete, or move it to submission copy.

## Update 2026-06-09 01:01KST — stable hold proof, not just visible text
- For ACC post-04 typography, contact/QC proof must include stable hold frames for title/theme/signage/final/disclosure. Fade-in/out frames are not enough.
- Removed rows must remain quiet; do not fill empty time with substitute explanatory captions.
- Final statement and disclosure must be sequenced as separate reading breaths.

## Update 2026-06-09 01:03KST — risk register before resuming rejected typography work
- After a long study window, create a risk register before production resumes. It should identify the ways the editor might revert to the old failure mode under time pressure.
- For ACC, active red-line risks are: pre-04 production, font-first patching, Pretendard/`시스템` fields, subtitle-like contact sheet, filler captions in deleted rows, generic shadow recipe, and premature completion claims.
- Artifact: `ACC_post0400_typography_risk_register_STUDY_ONLY_20260609.md`.


## Update 2026-06-09 01:10KST — invalidate stale handoff before editing
- If a rejected typography project has both an old delivery handoff and a newer study contract, the old handoff must be explicitly marked superseded before editing resumes.
- A handoff that still classifies many rows as `BODY` or keeps old font-family suggestions can silently pull the editor back into the rejected look, even when a new font file exists.
- For ACC, the post-04 editor must ignore the old Gothic/Noto/body-caption contract and start from row reduction + Gowun Batang / Wanted Sans / SUIT role pairing.

## Update 2026-06-09 01:12KST — skill assimilation gate for CapCut typography
- Before resuming a rejected CapCut typography pass, re-apply project skills as execution gates, not advice: layer separation, scene-first placement, cultural signage tone, scene-material shadow, and proof that effects are not hiding weak copy structure.
- For ACC, VideoDirector + Jeongseon typography rules were converted into `ACC_skill_assimilation_typography_rules_STUDY_ONLY_20260609.md`.
- Practical gate: no next export until visible proof distinguishes title/theme label/signage/final/disclosure roles; a readable but uniform subtitle system still fails.

## Update 2026-06-09 01:16KST — institutional palette is not color tweaking
- For public cultural/institution videos, a palette pass is valid only when tied to brand/institutional hierarchy and scene contrast. Random hue swaps remain a fail.
- For ACC, official CI + museum-label study produced palette tokens: dark charcoal, warm ivory, stone gray, soft gold rim, blue-black shadow.
- These tokens must support role separation: display/signage/final vs sparse theme/object labels vs disclosure. They cannot be applied globally to the old subtitle map.

## Update 2026-06-09 01:22KST — completion requires evidence matrix
- For rejected public/institution typography work, completion must be audited requirement-by-requirement, not inferred from an improved-looking export.
- A valid final claim needs: editable CapCut draft, actual preview/UI proof, final export path/size/ffprobe, stable-hold contact sheet, and row-level QC.
- Plans, dry-run specs, old accidental exports, and font audits alone are not completion evidence.

## Update 2026-06-09 01:25KST — placement maps must not preserve old subtitle geometry
- When reducing captions to sparse labels, do not simply keep the old transform coordinates. A one-line label still fails if it inherits subtitle geometry.
- For ACC, B03/B05 need fresh scene-anchor placement after row deletion; B01/B06/B08 need optical display/signage/final balance; B08D needs a separate subordinate breath.
- JSON transform values are only a locator; actual CapCut preview and visible glyph alignment are the proof.

## Update 2026-06-09 01:48KST — Study window discipline gate
When the user says to study until a specific time, do not produce new CapCut drafts, exports, ffmpeg renders, or media during that window unless explicitly overridden. The correct output during the window is research, failure analysis, wiki updates, and post-window execution contracts. Accidental renders made during a study window are evidence of process failure, not final completion.


## Update 2026-06-09 01:53KST — custom font metadata must be verified before CapCut patching
For rejected CapCut typography, verify local font file metadata before patching: family, subfamily, full name, PostScript name, and typographic family/style can disagree. Post-implementation proof must check representative role rows in CapCut and export; a single title proof or a readable glyph impression is not enough.
