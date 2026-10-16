# Production prompt contract adapter (review lens)

Load for recurring-character identity, multi-entity blocking, difficult spatial
continuity, dialogue/lipsync, or exact on-screen text. Distilled from the public
Hell Grind production package. It adds checks and pack fields; the prompt is
still the single template in `seedance-prompting.md`. It does not change
provider rules, UI operation, duration locks or the 3,500-character limit.

## Two layers

1. **Shot contract** (pack / storyboard) — full logic for humans and validators.
2. **Model-facing prompt** — only the shot-critical subset, in the template.

Immutable descriptors, spatial maps, provenance and revision logs stay in the
pack unless the model must see them for this shot. In preprod projects most of
the contract already lives in `storyboard.json` and `style_bible.json`.

Legacy contract fields: `shot_id`, `intent`, `duration_sec`, `format_mode`,
`exact_visible_entities`, `reference_role_map`, `semantic_contract`,
`character_state_assets`, `geo_spatial_lock`, `first_frame_occupancy`,
`lens_and_camera`, `timed_action_beats`, `physics_and_contact`,
`lighting_logic`, `audio_and_dialogue`, `performance_beats`,
`positive_proof_constraints`, `exit_frame`, `revision_ledger`.

## Entity and reference lock

- State `exactly N` for each recurring visible role when count matters; name
  every required character, no vague plurals.
- One narrow role per `@ImageN/@VideoN/@AudioN`, in pack and prompt.
- A location reference is geometry/material/atmosphere evidence only; it does
  not dictate the opening frame, angle or grade unless required.
- Wet, wounded, damaged-costume, age-stage or transformed states are separate
  approved assets, not adjectives added to a clean master.

### Triptych binding sentence

```text
@ImageN is the character triptych: the large right 3/4 portrait is the primary face identity, the left front full body sets build and front wardrobe, the middle back view sets hair silhouette and rear wardrobe. Do not reproduce the gray background, three-panel layout or panel seams; if the left panel is headless, do not reproduce the missing head. Pose and scene follow this shot.
```

For a fragile face close-up prefer `_FACE`; for a body/wardrobe shot the
triptych or one body crop. Identity refs never supply composition, pose or
story lighting.

## Spatial continuity and first frame

- For a multi-shot scene family keep one short `GEO_SPATIAL_LOCK` in the pack
  (frame-left/right landmarks, positions/distances, camera side and 180-degree
  line, entrances/exits, forbidden crossings). In the prompt, include only what
  the current shot shows or needs.
- Complex multi-character, combat or crowd shots use the opening moment to
  prove occupancy: all required entities visible and distinct, location
  anchors readable. Simple close-ups start on their subject.

## Action, camera, acting

- Present-tense physical beats with observable verbs and contact results.
- **One dominant camera move per shot, as declared in the storyboard.** A
  single-take compound path (push-in → arc → rise) is not authored in preprod;
  the storyboard splits it into shots or picks the dominant move.
- Start difficult actions already in motion when approach time would consume
  the shot; split setup and payoff when it cannot stay legible.
- Mass, inertia, impact, grip, cloth/hair, fluid and contact only where they
  decide success (no quota).
- Direct behavior, not adjectives: objective and obstacle, a visible tactic
  change, gaze before head turn, reaction before the line ends, small business,
  breath, blinks, held tension (not a frozen performer).
- Dialogue: route and QC from the table in `seedance-shared-contract.md`. Name
  the speaker, keep the literal line in quotes in its spoken language, one
  speaker per beat, listeners silent.

## Positive proof constraints

Prefer a few visible success conditions over a negative wall: exactly two named
characters stay distinct; the left hand keeps contact with the rail; the end
frame keeps the face unobstructed; the location ref contributes architecture
only; no new character enters. Negatives only for failure modes positive
wording cannot cover.

## Where each part goes in the template

1. Format/duration → line 1.
2. Role binding and exact entity count → binding sentences (count may also sit
   in the first shot section).
3. First frame and spatial lock → the first `Shot k` section.
4. Action beats and the declared camera move → each `Shot k` section.
5. Physics/contact and light → inside the shot that needs them.
6. Performance, dialogue, audio → shot sections + `Sound:`.
7. End frame and proof constraints → the last shot section and `End frame:`.

Cut repeated adjectives before spatial, count, contact, timing or source-role
facts.

## Legacy: user-reference semantic harness (2026-08-24)

Five user examples (multi-character timed dialogue, one-take action with
physical effects, handheld intimate performance, master-audio lipsync, exact
on-screen Hangul) were distilled into the rules below. **The original example
texts were never stored**; the executable reference is
`runtime/scripts/seedance_prompt_case_harness.py` and its cases in
`runtime/tests/test_seedance_prompt_case_harness.py`.

`user_reference_superior_v1` is an opt-in for non-preprod packs. When declared,
its density, temporal specificity, performance detail and constraint precision
outrank generic brevity defaults. In a preprod project the locked storyboard
and the template rank above it; safety, provider capability, verified
attachment and user settings always remain mechanical gates.

What the cases enforce:

1. **Cast ledger** — each recurring person has one `entity_id`, exact count,
   aliases and canonical tokens. Tokens are exactly `@ImageN/@VideoN/@AudioN`;
   `{{Mixed N}}`, `@HARIN`, `@Image 1`, `(Audio1)` are unresolved notation. One
   alias never names two people; a token never switches identity.

   ```text
   @Image1 defines only the face, hair, build and costume of the single lead; do not use the sheet's background, layout, panel borders or text.
   ```
2. **Timeline** — contiguous beats with no gaps/overlaps covering the duration.
   A one-take request with "rapid-cut tempo" (`원테이크` + `빠른 컷 전환 템포`,
   `一镜到底` + `快切节奏`) is compiled as quick performance beats and reactive
   reframing without edits: `tempo_interpretation:
   rapid_performance_handheld_no_edits`.
3. **Performance** is observable (gaze, swallow, jaw, breath, hands, listener
   reaction).
4. **Physical effects** follow `cause → material mechanism → two nearby
   reactions → travel → impact → aftermath`; if it is "not a beam or glow", do
   not ask for streaks or a flare later.
5. **Master-audio lipsync** — the attached master is the only music/vocal
   source; one on-camera vocal owner; others do not mouth words; mouth
   unobstructed for every vocal interval; instrumental gaps recorded.
6. **Exact on-screen text** — literal string, language, appearance action,
   completion point and QC route; surface blank before writing; check
   downloaded full-resolution frames.
7. **Constraint consistency** — no concept both required and forbidden,
   including the end frame: "no lens flare" vs a requested sun flare; "no music"
   vs an invented score; "one person" vs unnamed passers-by.

Activate only the rules a block uses in `prompt_rules_used`:
`user_reference_superior_v1`, `reference_cast_ledger_v1`,
`timed_performance_map_v1`, `one_take_axis_lock_v1`,
`physical_effect_causality_v1`, `audio_lipsync_priority_v1`,
`exact_text_dialogue_v1`, `constraint_consistency_v1`. Evidence goes under
`semantic_contract`:

```yaml
semantic_contract:
  authority:
    mode: user_reference_superior
    source: user_examples_2026_08_24
    overrides: [brevity_default, one_action_default, one_camera_default, performed_audio_default]
    mechanical_gates_preserved: [safety, provider_capability, verified_attachment, user_settings]
  visible_entity_count_total: 0
  entities:
    - entity_id: CHAR_ID
      count: 1
      aliases: [the single alias used in the prompt]
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

Omit an unused section with its rule. With `exact_text_dialogue_v1`, keep both
`dialogue` and `on_screen_text` as lists (one may be empty). Then run:

```bash
python3 /Users/gnudas/Documents/Codex/video-team-runtime/runtime/scripts/seedance_prompt_case_harness.py \
  --pack <BLOCK_prompt_pack.json>
```

`FAIL_DO_NOT_ATTEST` returns to authoring; never repair during UI execution.

## Revision discipline

After each generation change one causal clause and log `revision`,
`changed_clause`, `observed_failure`, `expected_correction`, `verdict`. If the
same failure survives bounded attempts, simplify the action, split the shot or
change the angle in the storyboard rather than adding prose. In QC, check the
first/last handles (often about half a second) for instability instead of
assuming the whole generation is clean.

## Lens checklist

- [ ] exact visible entity count and named roles; one entity per alias/token
- [ ] canonical tokens only; every token has one binding sentence
- [ ] triptych panels bound by function, not as a scene
- [ ] geography consistent with the 180-degree line; complex first frame proves occupancy
- [ ] action duration-feasible; one declared camera move per shot
- [ ] acting has objective, reaction and micro-life; dialogue speaker-specific per the route table
- [ ] effects have cause, proof, travel, impact, aftermath
- [ ] lipsync protects one vocal owner; exact text has literal, timing and QC
- [ ] no required/forbidden conflict anywhere, including the end frame
- [ ] end frame usable for the next clip; constraints short and positive
