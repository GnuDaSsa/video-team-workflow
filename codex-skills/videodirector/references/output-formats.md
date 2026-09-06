# Output formats

Copy-paste-ready shapes for cut lists, character/scene JSON, BGM, and narration sheets.

## Output formats

### Cut list

Use a table with these columns:

| scene | timecode | visual | narration |
|------|----------|--------|-----------|

### Storyboard production blueprint

Planner drafts this after the real audio spine and cut map; recurring-character identity fields and any rendered board remain unlocked until the approved character/provider sheets exist. The rendered board may be multi-panel because it is a planning/reference artifact; it is never a production sourceframe. Canonical details: `/Users/gnudas/wiki/concepts/storyboard-production-blueprint-standard.md`.

```yaml
project:
  title: "[title]"
  premise: "[one sentence]"
  mode: "MV | public_contest | institution | shortform | trailer"
  aspect_ratio: "16:9"
  target_duration: "00:00.000"
  audio_spine: "[verified file / lock id]"
  hard_constraints: []
  palette: []

identity_refs:
  - character: "[ID]"
    identity_ref: "CHAR_<ID>_TRIPTYCH_R<n> or deterministic crop"
    wardrobe_props: []

environment:
  set_ref: "[asset id]"
  map: "[top-down actor/camera/action-path plan]"
  screen_direction: "[left-to-right / right-to-left / deliberate reversal]"

shots:
  - shot_id: "S01"
    timecode: "00:00.000-00:02.400"
    frame_purpose: "[new action / information / emotion / rhythm / transition]"
    distance_angle: "[distance + angle]"
    lens: "[lens family / focal length]"
    camera_position: "C1"
    camera_motion: "[one primary move]"
    blocking_action: "[start -> contact/action -> visible response]"
    dialogue_audio: "[dialogue/VO/room tone/SFX/music cue]"
    transition_in_out: "[motivated entry + stable exit composition]"
    identity_refs: ["CHAR_<ID>_TRIPTYCH_R<n> or deterministic crop"]

look_sound_cinematography:
  lighting: "[...]"
  colour_script: "[...]"
  acting: "[...]"
  sound: "[...]"
  lens_movement_grammar: "[...]"
```

For v4 projects, keep `storyboard_blueprint.md/json` and `storyboard_qc.md` under `lanes/planner/`. A rendered PNG is optional; if produced after identity/source approval, put and register it under `media/01_sources_원본자료/storyboards/`.

### Storyboard-to-Seedance handoff

The Seedance lane owns the final Korean prompt. The director/planner supplies metadata only:

```yaml
storyboard_mode: "STORYBOARD_SHOT_MODE | STORYBOARD_SEQUENCE_PREVIS_MODE"
storyboard_asset: "STORYBOARD_<PROJECT>_R<n>"
board_role: "production blueprint; never an on-screen graphic"
shot_range: ["S01"]
ordered_beats: []
character_identity_assets: ["CHAR_<ID>_TRIPTYCH_R<n> or deterministic crop"]
production_status: "FINAL_CANDIDATE | PREVIS_HOLD"
```

- `STORYBOARD_SHOT_MODE` is the final-production default: one board shot per generation, with the approved per-cut styleframe and minimum approved triptych/identity crop where required.
- `STORYBOARD_SEQUENCE_PREVIS_MODE` is an opt-in multi-shot prototype: restate feasible ordered beats and explicitly exclude the board sheet, panels, labels, diagrams and UI from the rendered video. The result remains `PREVIS_HOLD` until QC.

### Character reference JSON

```json
{
  "character": "[name]",
  "purpose": "reference sheet - front view",
  "prompt": "full character description with fixed hair, eyes, outfit, neutral pose, plain background, style lock included, 16:9 aspect ratio",
  "negative": "style drift, different character, deformed, extra accessories"
}
```

### Three-panel character identity JSON

```json
{
  "character": "[name]",
  "asset_id": "CHAR_<ID>_TRIPTYCH_R1",
  "purpose": "recurring-character identity and body/wardrobe construction lock",
  "attach_instruction": "attach the approved identity/casting source and verify its hash",
  "layout": ["left: headless front full body", "middle: back full body with head", "right: large 3/4 face portrait"],
  "rendering": "text-free neutral mid-gray, neutral studio light, true skin/material color, 16:9",
  "stress_gate": "10 varied generations, same recognizable identity 10/10",
  "derivatives": ["_FACE", "_FRONT_BODY", "_BACK_BODY"]
}
```

### Start-frame JSON

```json
{
  "cut": "C-01",
  "timecode": "00:00-00:05",
  "type": "start_frame",
  "attach": "[none / character / character + character]",
  "prompt": "scene description with camera angle, composition, facial expression, background, lighting, full style lock included, 16:9 aspect ratio"
}
```

### Seedance/I2V motion prompts (default)

Default provider is Seedance. Write one prompt per cut/block; use Grok-style motion tags only if the user named Grok.

Available movement tags:

- `[SLOW_ZOOM_IN]`
- `[SLOW_ZOOM_OUT]`
- `[PAN_RIGHT]`
- `[TILT_UP]`
- `[TRACKING]`
- `[DOLLY_IN]`
- `[HANDHELD]`
- `[STATIC]`
- `[SLOW_MOTION]`

Example:

```text
[SLOW_ZOOM_IN] gentle forward camera movement, subject remains steady, emotional focus intensifies
```

### BGM JSON

```json
{
  "track": "BGM-01",
  "timecode": "00:00-00:12",
  "duration": "12s",
  "mood": "hopeful cinematic build",
  "suno_style_prompt": "instrumental cinematic ambient with soft piano and subtle strings, emotional but restrained, no vocals",
  "suno_tags": ["instrumental", "cinematic", "ambient", "piano"],
  "volume": "-4dB"
}
```

### Narration/dialogue sheet

```text
00:21 - 화자
"대사 또는 나레이션"
```

## Style locks

Embed the relevant style directly inside prompts:

- Makoto Shinkai: `makoto shinkai anime illustration, cinematic lighting, detailed background, soft atmospheric haze, 16:9 aspect ratio`
- Photoreal: `photorealistic, cinematic color grading, shallow depth of field, natural lighting, 16:9 aspect ratio`
- Ink wash: `traditional korean ink wash painting, sumi-e style, monochrome with subtle color, elegant brushwork, 16:9 aspect ratio`
- Pixar/3D: `pixar 3D animation style, soft subsurface scattering, expressive character design, warm studio lighting, 16:9 aspect ratio`

## Default full-package order

When the user asks for a full package, output in this order:

1. Concept summary in 3 lines or less
2. Verified audio spine and timeline/cut map
3. Character JSON
4. Character sheet JSON
5. Storyboard production blueprint + QC
6. Scene start-frame JSON
7. Seedance/I2V motion prompts (or Grok only if user named Grok)
8. BGM JSON
9. Narration/dialogue sheet
