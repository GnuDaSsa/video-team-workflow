# Seedance 2.0 multimodal prompting patterns

This is a **prompt-authoring reference** inside the canonical
`seedance-prompt-en` skill. It does not own Runway UI operation, queue handling,
downloads, or media completion.

## Provenance and verification

- User source: `/Users/gnudas/Downloads/seedance2-prompting.zip`
- Source SHA-256:
  `42612531d9c671cdfdbc61df88f8825c4745e48e8a897a2b2f36a7fbcf1b48f3`
- Integrated: `2026-08-14`
- First-party cross-checks:
  - [ByteDance Seedance 2.0 official launch](https://seed.bytedance.com/blog/seedance-2-0-official-launch)
  - [Runway: Creating with Seedance 2.0](https://help.runwayml.com/hc/en-us/articles/50488490233363-Creating-with-Seedance-2-0)

The ZIP is an input source, not a second authority. Rules below are reconciled
with `seedance-shared-contract.md`, `seedance-prompting.md`, current first-party
documentation, and the visible Runway UI.

### Current capability snapshot, not a permanent constant

As verified on `2026-08-14`, Runway documents:

- text, image, video, and audio inputs;
- `References`, `Start / End frames`, and `Text to video` creation modes;
- 5–15 second generations;
- up to 9 reference images;
- up to 3 reference videos, whose combined duration is under 15 seconds;
- up to 3 reference audio files, whose combined duration is under 15 seconds.

Before production, the visible provider UI and current first-party help page
win over this snapshot. Do not infer an undocumented combined-file maximum.

### Source claims deliberately not promoted as hard rules

- **Exactly three-second segments:** useful as a planning example, not a
  universal law. Segment by action complexity, music phrase, and shot purpose.
- **The phrase “completely reference” as a magic token:** use an explicit scoped
  role and preservation clause instead; no phrase guarantees literal copying.
- **All real-person image inputs are forbidden:** Runway describes moderation
  constraints and suggests Text to Video for realistic humans; it does not state
  the ZIP's absolute ban. Obey current provider moderation and never retry the
  same moderated input unchanged.
- **4-second minimum, 12-file combined limit, and broad image file extensions:**
  not copied into the live contract because they do not match or are not stated
  in the current Runway help page.
- **Backward extension:** use only if the active provider UI visibly exposes it.

## Method first

Choose the generation method before composing sentences.

| Need | Method | Prompt responsibility |
|---|---|---|
| Blend identity, environment, prop, motion, or sound references | `References` | Give every attached source a narrow role and describe the resulting scene |
| Exact first frame or exact first/last boundary | `Start / End frames` | Describe motion and continuity between the fixed boundaries |
| No source asset, or realistic human moderation makes image input unsuitable | `Text to video` | Own composition, identity description, blocking, light, action, camera, and sound |
| Preserve source-video motion but change subject/style/light | reference video / video edit | Name exactly what changes and what remains unchanged |
| Continue a successful clip | extension | Restate the observed boundary state, preserved invariants, new action, and new end state |
| Replace only one bad beat | repair/edit | Bound the changed interval or event and preserve everything outside it |
| Interpret one approved unified board | declared storyboard mode | Use its internal `shot_id`; never treat attachment order as story order |

The video-team generation mode still applies:

- `standard_i2v` uses the approved per-cut source frame plus required identity
  references.
- `no_i2v_reference_native` omits per-cut frames and makes the Korean prompt own
  the missing composition, blocking, action, camera, atmosphere, and timing.

## Five-block compile audit

Use these five questions to compile or review a prompt. They are an audit lens,
not a replacement for the live medium-specific structure. For 2D/stylized
sequences, `STYLE LOCK -> CONTINUITY -> DIRECTION -> SHOT` remains authoritative.

1. **Source binding** — What visible or audible job does every attached
   `@ImageN`, `@VideoN`, and `@AudioN` perform?
2. **Subject and space** — Who or what is present, where are they, and which
   identity, costume, prop, geometry, light, and material rules persist?
3. **Temporal action** — What physically happens, in what feasible order, and
   what visible state closes the clip?
4. **Camera and sound** — What is the one dominant camera family or per-beat
   setup, and what ambience, contact sound, music, or performed speech is heard?
5. **Style and constraints** — What medium/look is required, and what one or two
   shot-specific risks need a short positive lock?

If a block does not change what the viewer sees or hears, move it to the package.
File paths, asset IDs, gate wording, UI settings, retries, and provenance never
belong in the prompt.

## Multimodal source binding

### Core rule

Every attached source gets a scoped role **inside the model-facing prompt**.
The package separately records the exact asset ID, path, attachment order, and
verification evidence.

Good binding says both what to take and what not to overwrite:

```text
@Image1의 인물 얼굴 실루엣과 복식을 주인공의 정체성 기준으로 사용한다.
공간과 조명은 @Image2를 따르되 @Image1의 얼굴과 체형은 바꾸지 않는다.
@Video1에서는 카메라 이동 경로만 참고하고 등장인물 외형은 가져오지 않는다.
@Audio1은 대사의 발음 타이밍, 호흡, 멈춤만 이끌며 배경음악으로 쓰지 않는다.
```

Avoid unscoped instructions such as `@Video1을 참고한다`. Avoid assigning one
source several conflicting jobs. When one source truly contributes two roles,
state both separately and check that neither conflicts with another source.

### Image roles

- identity: face silhouette, hair mass, age impression, body proportion,
  costume, signature prop;
- environment: layout, architecture, terrain, palette, time of day, material;
- prop/product: exact geometry, surface, logo placement when readable text is
  safe and required;
- composition or boundary: starting composition, ending composition, or one
  declared storyboard `shot_id`;
- style: medium, line/fill/shading, texture, lighting response.

A recurring-character `TRIPTYCH` or deterministic identity crop is identity/body construction only. It is not a pose, scene,
camera, or narrative-order cue.

### Video roles

- camera path or mount only;
- subject action, choreography, timing, or body mechanics only;
- edit structure or rhythm only;
- visual effect or transition behavior only;
- source clip to relight, restyle, replace, repair, or extend;
- source-video audio, when that audible role is explicitly intended.

When transferring camera motion or choreography, identify the preserved lane:

```text
@Video1의 낮은 측면 트래킹 경로와 속도 변화만 적용한다.
장소는 @Image2, 주인공 정체성은 @Image1을 유지한다.
```

### Audio roles

- performed Korean speech guide: phoneme timing, cadence, breath, pause,
  hesitation, mic distance, and emotional curve;
- score or beat guide: tempo, accents, phrase changes, and energy curve;
- ambience/SFX guide: material contacts, room tone, weather, machinery, crowd;
- voice colour only when the provider and policy permit it.

The shared audio contract still wins: Audio stays ON; spoken dialogue requires
the verified performed `@Audio1` route unless the user explicitly requests the
candidate-only native voice branch.

## Temporal beat grammar

Use timed beats when the clip is longer than about eight seconds **and** contains
multiple phases, or whenever order has failed before. Do not split a single
continuous action merely to satisfy a timer.

Each beat should normally contain:

- one subject action or state change;
- one camera setup or continuation of the dominant camera move;
- one motivated environment/material response;
- one timing or rhythm cue;
- a state that the next beat can inherit.

The preferred chain is:

```text
start state -> action -> contact -> physical result -> camera beat -> end state
```

Convert emotion words into visible performance:

- not `긴장한다`;
- use `시선이 출구로 짧게 움직이고, 엄지가 컵 가장자리를 두 번 누르며,
  숨을 들이마신 뒤 어깨가 아주 조금 올라간다`.

Duration budget:

| Duration | Practical budget |
|---|---|
| 5–6s | one action or one camera discovery |
| 7–10s | setup -> one interaction -> reveal, usually no more than three major verbs |
| 11–15s | two or three causal phases with one dominant camera family and an explicit end frame |

If the action budget overflows, split the work into separate generations. Do not
solve overpacking by writing faster transitions.

## Single-shot, multi-shot, and storyboard wording

### Single continuous shot

State it positively and place the continuity instruction near the shot
description, not as a magic footer:

```text
15초 단일 연속 숏, 편집 컷 없이 같은 공간과 시간 안에서 이어진다.
카메라는 인물 앞의 낮은 미디엄 숏에서 시작해 한 번의 부드러운 측면
트래킹으로 모퉁이까지 따라가고, 인물이 프레임 오른쪽으로 빠져나가는
구도에서 끝난다.
```

### Multi-shot sequence

Declare the shot count and cut grammar. Every shot receives its own visible
action and camera setup. Hard cuts are usually clearer than unspecified morphs.

```text
15초 3숏 시퀀스, 각 숏은 명확한 하드 컷으로 연결한다.
0–4초, 숏 1: ...
4–10초, 숏 2: ...
10–15초, 숏 3: ...
```

In `GENERAL_REFERENCE_MODE`, never equate `@Image1 -> @Image2 -> @Image3` with
shot order. Ordered beats come only from the written shot plan or an approved
storyboard's internal IDs.

## Extension and repair

### Forward extension

Inspect the actual final frames first. Then compile four parts:

1. observed boundary state;
2. invariants to preserve;
3. new action and camera continuation;
4. new closing state and sound continuation.

```text
@Video1의 마지막 프레임에서 앞으로 이어진다. 현재 인물은 창가 왼쪽에
서서 오른손으로 커튼을 잡고 있고, 석양이 얼굴 왼쪽을 비춘다. 같은 인물
정체성, 의상, 카메라 진행 방향, 방의 구조, 석양 방향, 실내 잔향을 유지한다.
0–2초에는 커튼을 천천히 놓고 몸을 방 안쪽으로 돌린다. 2–5초에는 같은
카메라가 반걸음 뒤에서 따라가며 인물이 책상 위 편지를 집어 든다. 마지막은
편지를 든 손과 망설이는 시선이 함께 보이는 미디엄 클로즈업이다.
```

Do not extend a clip whose final frames already contain identity, anatomy, or
geometry drift; extension tends to inherit the defect.

### Local repair or edit

Name the bounded change and the preserved remainder:

```text
@Video1의 첫 6초와 마지막 구도는 유지한다. 6–9초 구간에서만 오른손이
컵 손잡이를 자연스럽게 잡고 들어 올리도록 수정한다. 얼굴, 왼손, 컵 형태,
카메라 경로, 조명, 배경 기하, 음향은 바꾸지 않는다.
```

If the source identity or scene anchor is globally wrong, regenerate from the
correct reference package instead of stacking repair instructions.

## Compact reusable patterns

### Reference composite

```text
@Image1의 주인공 정체성과 복식을 유지한다. 장면 구조와 시간대는
@Image2, 손에 든 제품 형상은 @Image3을 따른다. @Video1의 카메라 경로만
적용하고 그 영상의 인물과 장소는 가져오지 않는다. [행동과 시간 비트].
소리는 [앰비언스/접촉음/음악]. 마지막은 [명시적 종료 구도].
```

### Choreography transfer

```text
@Image1의 인물이 @Video1의 동작 순서와 체중 이동을 수행한다. 얼굴, 체형,
복식은 @Image1을 유지하고 @Video1의 배우 외형은 가져오지 않는다. 카메라는
[한 가지 경로]. 발 접촉, 옷감 관성, 호흡, 바닥 반응을 자연스럽게 보인다.
```

### Product edit

```text
@Video1의 편집 리듬과 카메라 구조를 유지하되 기존 제품만 @Image1의 제품으로
교체한다. 제품 비율, 모서리, 재질, 색, 로고 위치를 유지하고 손과 제품의
접촉을 물리적으로 정확하게 보인다. [시간별 제품 행동]. 마지막은 깨끗한
히어로 숏이다.
```

### Storyboard execution

```text
@Image1의 승인 스토리보드 중 내부 shot_id S03만 실제 영화 장면으로 구현한다.
보드의 패널, 테두리, 번호, 설명문, UI는 화면에 나타나지 않는다. 인물 정체성은
@Image2, 공간 재질은 @Image3을 따른다. [S03의 행동·카메라·사운드·종료 구도].
```

## Prompt critic checklist

- The method matches the intended control: References vs Start/End vs T2V vs
  edit/extension.
- Every attached image, video, and audio has a narrow model-facing role.
- A new reference-based pack declares `model_facing_multimodal_binding_v1` in
  `prompt_rules_used`; attestation can therefore reject package-only bindings.
- The same source is not silently responsible for identity, camera, action,
  background, and style at once.
- Reference attachment order has not been mistaken for narrative order.
- Subject, space, action, camera, sound, and end frame are all concrete.
- Emotion is expressed as visible body, face, breath, or contact behavior.
- Duration can physically contain the requested actions.
- Single-shot or multi-shot grammar is explicit when it matters.
- Extension starts from the observed boundary state and preserves continuity.
- The prompt contains no paths, asset IDs, UI settings, gates, status, or
  provenance.
- Constraints are short and shot-specific; no generic negative wall.
- The visible provider UI has been checked for current limits and controls before
  production handoff.
