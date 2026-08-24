# Production prompt contract adapter

Use this adapter during authoring after `seedance-shared-contract.md` and `seedance-prompting.md`, together with any verified live adapters selected by the dispatcher. It distills compatible lessons from the public Hell Grind production package into this user's Korean, bounded Seedance workflow. It does not replace provider rules, UI operation, duration locks, or the current prompt-length limits.

## Two-layer authoring

Maintain two artifacts:

1. **Shot contract package** — complete production logic for humans and validators.
2. **Korean model-facing prompt** — only the shot-critical subset, compiled to the current target length and visible hard limit.

Do not paste an encyclopedic contract into Runway. Immutable descriptors, spatial maps, reference provenance, revision logs, and omitted background facts remain in the package unless the model must see them for this shot.

## Shot contract package

Record these fields before compiling the provider prompt:

```yaml
shot_id:
intent:
duration_sec:
format_mode: SINGLE_CONTINUOUS_SHOT | PLANNED_MULTI_SHOT_SOURCE
exact_visible_entities:
reference_role_map:
semantic_contract:  # conditional ledger/timeline/axis/audio/text/effect data
character_state_assets:
geo_spatial_lock:
first_frame_occupancy:
lens_and_camera:
timed_action_beats:
physics_and_contact:
lighting_logic:
audio_and_dialogue:
performance_beats:
positive_proof_constraints:
exit_frame:
revision_ledger:
```

### Entity and reference lock

- State `exactly N` for each visible recurring role when count matters. Name every required character; do not use vague plural nouns.
- Give every `@ImageN/@VideoN/@AudioN` one narrow visible or audible role in both the package and Korean prompt.
- Treat a location reference as geometry/material/atmosphere evidence only. Unless explicitly required, it must not dictate the generated opening frame, camera angle, grade, or frozen composition.
- Treat identity descriptors and approved state assets as immutable. Wet, wounded, damaged-costume, age-stage, disguise, or transformation states are separate assets, not adjectives casually added to a clean master.

### Three-panel character reference binding

When `CHAR_<ID>_TRIPTYCH_R<n>` is attached, include a compact role binding equivalent to:

```text
@ImageN의 오른쪽 큰 3/4 초상은 얼굴 정체성·피부·눈빛 기준, 왼쪽 머리 없는 정면 전신은 체형·의상 전면 기준, 가운데 후면 전신은 헤어 뒤 실루엣·의상 후면 기준으로만 사용한다. 회색 배경·3분할·패널 경계·빈 머리 부분은 결과에 재현하지 않는다. 포즈와 장면은 현재 샷 지시를 따른다.
```

For a fragile face close-up, prefer the deterministic `_FACE` crop. For a body/wardrobe shot, use the full triptych or the one necessary body crop. Never ask the identity reference to supply composition, pose, or story lighting.

### Spatial continuity lock

For a multi-shot scene family, write one short `GEO_SPATIAL_LOCK` and reuse it unchanged until the geography changes. Include only discriminating facts:

- frame-left/right/center landmarks;
- character and prop positions or relative distance;
- camera side and 180-degree line;
- entrances, exits, and forbidden crossings.

Do not rewrite the map poetically between shots. In the model-facing prompt, include only the parts visible or causally necessary in the current shot.

### First-frame occupancy

For complex multi-character, combat, crowd, or spatial-continuity shots, use the first 0.8–1.0 seconds to prove occupancy: all required entities already visible, roles separated, location anchors readable, no duplicate character. This is not a universal empty establishing shot. Simple close-ups and inserts may start directly on their subject.

### Timed action and camera

- Write present-tense physical beats with observable verbs and contact results.
- Prefer one dominant camera move per shot. Name a second move only when it is a motivated continuation, not decorative stacking.
- Start difficult actions already in motion when approach time would consume the shot. Split setup and payoff into separate shots when the action cannot remain physically legible.
- In a 15-second planned multi-shot source, use 2–4 causal scenes with explicit time ranges; each scene gets no more than about three short sentences and ends on an edit-ready image.
- Specify mass, inertia, impact, grip, cloth/hair response, fluid behavior, and object contact only where they determine success.

### Acting and audio

Direct behavior under pressure rather than emotion adjectives alone:

- objective and obstacle;
- tactic change or visible beat shift;
- gaze arriving before the head/body turn;
- reaction beginning before a line fully ends when appropriate;
- small physical business, breathing, blinks, held muscular tension, and listening behavior.

Put exact spoken lines only in the audio/dialogue block. Name the speaker, keep non-speakers silent, and state the intended soundscape or mix. Do not confuse held tension with a frozen performer.

### Positive proof constraints

Prefer a short list of visible success conditions over a generic negative wall, for example:

- exactly two named characters remain visible and distinct;
- the left hand keeps continuous contact with the rail;
- the exit preserves an unobstructed face and clean motion handle;
- location reference contributes architecture and material only;
- no new character enters.

Use negatives only for shot-specific failure modes that positive wording cannot cover.

## Korean compile order

Compile the shot-critical subset in this order:

1. format and duration/shot grammar;
2. `@ImageN/@VideoN/@AudioN` role binding and exact entity count;
3. first frame plus current spatial lock;
4. timed action beats and dominant camera/lens;
5. physics/contact and light logic;
6. performance, dialogue, and audio;
7. exit frame and concise positive proof constraints.

Keep the prompt concrete, Korean-first, and within the live skill's current target and hard limit. Remove repeated adjectives before removing spatial, count, contact, timing, or source-role facts.

## User-reference case compiler — 2026-08-24

Five user-supplied examples established a useful high-detail grammar for
multi-character dialogue, single-take action, intimate handheld performance,
master-audio lipsync, and exact on-screen Hangul. Treat them as **case
evidence**, not paste-ready prompts. Keep the structure below, repair their
token, language, timing, and constraint defects, then compile the final prompt
in Korean.

### 1. Canonical reference and cast ledger

Before prose, assign every recurring visible person one immutable `entity_id`,
one exact count, a set of human-readable aliases, and the canonical provider
tokens that define the person. Then bind each reference by inclusion and
exclusion:

```text
@Image1은 CHAR_LEAD 한 명의 얼굴·헤어·체형·의상만 정의한다. 시트의 배경,
분할 레이아웃, 패널 경계와 텍스트는 장면에 사용하지 않는다.
```

- Model-facing tokens are exactly `@ImageN`, `@VideoN`, and `@AudioN` with no
  spaces. `{{Mixed N}}`, `@HARIN`, `@Image 1`, `(Audio1)`, file nicknames, and
  character names used as attachment tokens are unresolved source notation;
  normalize them before attestation.
- One alias cannot name two characters. One reference token cannot silently
  switch identity between sections. Repeated roles use the same `entity_id`
  throughout the reference block, timeline, dialogue, audio, and end state.
- State exact cardinality when it matters: for example one lead plus five named
  non-speaking dancers means six people throughout, not an open-ended crowd.
- Identity sheets define identity/wardrobe construction only. Their gray
  background, grid, text, pose, and studio lighting are excluded explicitly.

### 2. Premise, globals, then the right temporal grammar

Start with one sentence that contains subject, place, decisive action or comic
thesis, duration/format when relevant, and medium. Put shared world, lighting,
composition, performance tone, cast count, and sound above the timeline so they
are not rewritten inconsistently per beat.

Choose one of two structures:

- **Planned multi-shot:** contiguous `0–N초` shots. Every shot names the visible
  action, camera setup, physical acting, exact dialogue/audio event when any,
  and edit-ready exit. Global locks survive every cut.
- **Single continuous take:** contiguous **phases**, not shots. Lock camera side,
  subject off-center placement, lead room, screen direction, and forbidden axis
  crossing once, then describe setup → escalation → arrest → consequence → end
  state. A heading or time range does not imply a cut.

Never combine `원테이크/one-shot/一镜到底` with a positive direction such as
`빠른 컷 전환`, `하드 컷`, `rapid cuts`, or `快切`. If the desired energy is
handheld and fast but uncut, ask for quick performance beats, reactive
reframing, footwork, focus recovery, and natural handheld acceleration instead
of edit cuts.

### 3. Performance is observable

Translate the emotional curve into small physical evidence: gaze drops before
the head turns, a swallow moves the throat, the jaw sets, lips tremble, breath
changes the shoulders, hands hesitate, and a listener reacts after the line
lands. Preserve restraint unless one explicitly named climax owns the outburst.

For exact dialogue:

- record speaker `entity_id`, literal Korean string, time range, delivery,
  non-speakers, and the verified performed `@AudioN` guide;
- keep the literal Korean unchanged in the model-facing prompt;
- give one speaker each beat and keep reaction mouths silent;
- do not infer that a quoted line alone satisfies audio quality—the downloaded
  result still needs listening and lipsync QC.

### 4. Physical effect ontology

When an effect must not become generic light, name it by physics:

```text
cause -> material mechanism -> two nearby reactions -> travel -> impact -> aftermath
```

For example, a blade-driven pressure event can appear as transparent air
refraction; grass, cloth, dust, snow, or loose fragments prove the pressure
nearby; a groove proves travel; a non-explosive fracture and gravity-driven
debris prove impact and aftermath. If the prompt says the effect is not a beam,
glow, spark, or explosion, do not later request luminous streaks or a flare as
the payoff.

### 5. Master-audio performance and lipsync

When a finished `@AudioN` master owns the piece:

- declare it the only music/vocal source and forbid invented score or vocals;
- map instrumental and vocal intervals separately;
- name exactly one on-camera vocal owner and keep all other people from
  mouthing words;
- protect a sharp, unobstructed mouth through every vocal syllable and never cut
  mid-word;
- let choreography, camera distance, and circle/crowd blocking escalate around
  the vocal map rather than compete with it;
- record instrumental gaps explicitly in the broader performance timeline even
  when the lipsync map itself lists vocal intervals only.

### 6. Exact on-screen text

For generated writing or signage, record the literal string, language,
appearance action, completion point, and QC route. Keep the surface blank before
writing, show the writing action in a feasible close view, and speak only after
the writing is complete when that order matters. A list of several camera
angles without declared single/multi-shot grammar or time allocation is
overpacked and must be simplified or converted into a timed multi-shot plan.
Never claim text success from the prompt; inspect downloaded full-resolution
frames for spelling, glyph shape, stroke order impression, stability, and
legibility.

### 7. Constraint consistency pass

End with only shot-specific locks. Normalize required and forbidden concepts in
the package before compiling prose. A concept cannot appear in both sets. Check
the entire prompt, including the final frame: `렌즈 플레어 없음` cannot coexist
with a requested final sun/lens flare; `음악 없음` cannot coexist with an
invented score; `인물 한 명` cannot coexist with unnamed students, dancers, or
passersby.

### Conditional semantic harness

Activate only the rules needed by the current block in `prompt_rules_used`:

```text
reference_cast_ledger_v1
timed_performance_map_v1
one_take_axis_lock_v1
physical_effect_causality_v1
audio_lipsync_priority_v1
exact_text_dialogue_v1
constraint_consistency_v1
```

Put the machine-readable evidence under `semantic_contract`. Before ordinary
prompt attestation, run:

```yaml
semantic_contract:
  visible_entity_count_total: 0
  entities:
    - entity_id: CHAR_ID
      count: 1
      aliases: [프롬프트에서 쓸 유일한 별칭]
      reference_tokens: ["@Image1"]
  reference_bindings:
    - token: "@Image1"
      role: identity
      entity_id: CHAR_ID
      use: [face, hair, wardrobe]
      exclude: [sheet_background, layout, text]
  timed_beats:
    - {start_sec: 0, end_sec: 5, action: "...", camera: "..."}
  continuity:
    take_structure: single_take
    camera_axis: {side: "...", subject_placement: "...", lead_room: "..."}
  effects:
    - {effect_id: "...", cause: "...", material_mechanism: "...",
       nearby_reactions: ["...", "..."], travel: "...", impact: "...", aftermath: "..."}
  audio_contract:
    source_token: "@Audio1"
    exclusive_source: true
    performer_entity_id: CHAR_ID
    non_speaking_entity_ids: []
    face_visibility: "..."
    lip_sync_segments:
      - {start_sec: 0.5, end_sec: 2.8, content: "opening vocal"}
  dialogue: []
  on_screen_text: []
  constraints: {required: [], forbidden: []}
```

Omit an unused section and its rule together. When
`exact_text_dialogue_v1` is active, keep both `dialogue` and `on_screen_text` as
lists; one may be empty, but the other must contain at least one literal-string
contract.

Then run:

```bash
python3 /Users/gnudas/Documents/Codex/video-team-runtime/runtime/scripts/seedance_prompt_case_harness.py \
  --pack <BLOCK_prompt_pack.json>
```

`FAIL_DO_NOT_ATTEST` means return to authoring. Do not repair a token collision,
timeline gap, lipsync owner, exact string, or contradictory constraint during UI
execution.

## Revision discipline

After each generation, change one causal clause at a time and log:

```yaml
revision:
changed_clause:
observed_failure:
expected_correction:
verdict:
```

If the same failure survives repeated bounded attempts, simplify the action, split the shot, or change the camera angle rather than adding more prose. In edit/QC, inspect and normally trim unstable first/last handles (often about 0.5 seconds) instead of assuming the full generation is clean.

## Authoring audit

Before attestation, verify:

- [ ] exact visible entity count and named roles;
- [ ] all source notation is normalized to canonical `@ImageN/@VideoN/@AudioN` tokens;
- [ ] aliases and reference tokens map to one immutable entity each;
- [ ] every attached token has one model-facing role;
- [ ] triptych panels/crops are bound by function, not treated as a scene;
- [ ] current geography is explicit and consistent with the 180-degree line;
- [ ] complex first-frame occupancy proves all required entities;
- [ ] action is duration-feasible and physically observable;
- [ ] one dominant camera intent;
- [ ] acting contains objective, reaction, and micro-life;
- [ ] dialogue/audio are speaker-specific;
- [ ] single-take phase headings do not introduce cuts and preserve camera side/lead room;
- [ ] effect language has a physical cause, material proof, travel, impact, and aftermath;
- [ ] master-audio lipsync protects one vocal owner and silent non-performers;
- [ ] exact text/dialogue literals have language, owner/action, timing, and QC evidence;
- [ ] required and forbidden concepts do not conflict anywhere, including the final frame;
- [ ] exit frame is usable for editing;
- [ ] constraints are short, positive, and shot-specific;
- [ ] revision ledger changes one clause only.
