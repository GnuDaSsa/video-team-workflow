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
- [ ] every attached token has one model-facing role;
- [ ] triptych panels/crops are bound by function, not treated as a scene;
- [ ] current geography is explicit and consistent with the 180-degree line;
- [ ] complex first-frame occupancy proves all required entities;
- [ ] action is duration-feasible and physically observable;
- [ ] one dominant camera intent;
- [ ] acting contains objective, reaction, and micro-life;
- [ ] dialogue/audio are speaker-specific;
- [ ] exit frame is usable for editing;
- [ ] constraints are short, positive, and shot-specific;
- [ ] revision ledger changes one clause only.
