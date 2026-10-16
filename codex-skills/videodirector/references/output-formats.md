# Output formats

Copy-paste-ready shapes for cut lists, character/scene JSON, BGM, and narration sheets.

## Output formats

### Cut list

Use a table with these columns:

| scene | timecode | visual | narration |
|------|----------|--------|-----------|

### Storyboard (P2) — `preprod/02_storyboard/storyboard.json`

The storyboard is now a validated JSON file owned by the planner and locked with the user's approval quote; schema and controlled vocabulary live in `runtime/scripts/preprod.py` (`validate_storyboard`), a skeleton in `runtime/templates/preprod/storyboard.json`. Blocking/geometry thinking: `/Users/gnudas/wiki/concepts/storyboard-production-blueprint-standard.md`. A rendered multi-panel board is optional planning reference only, never a production sourceframe.

Map from the former blueprint YAML:

| Former YAML field | Now lives in |
|---|---|
| `project.title/premise/mode/aspect_ratio/target_duration/hard_constraints` | `concept_lock.json`: `title`, `logline`, `mode`, `aspect_ratio`, `target_runtime_sec`, `must_avoid` |
| `project.palette`, `look_sound_cinematography.lighting/lens_movement_grammar` | `style_bible.json`: `palette_hex`, `lighting`, `lens_grammar`, `texture`, `style_block_en` |
| `identity_refs[]` | `style_bible.json` `characters[]` (`identity_block_en`, `sheet_ref_id`) + `image_plan.json` |
| `environment.set_ref/map` | `style_bible.json` `locations[]` (`description_en`) + block `location_id` / `refs` |
| `shots[].timecode` | block `order` + shot `start_sec`/`end_sec` inside a 15 s block |
| `shots[].frame_purpose` | block `purpose` + shot `action` |
| `shots[].distance_angle`, `camera_motion`, `lens` | shot `shot_size`, `angle`, `camera_move` (controlled lists), `lens` |
| `shots[].blocking_action` | shot `composition` + `action` + `must_include[]` |
| `shots[].dialogue_audio` | block `audio_route` |
| `shots[].transition_in_out` | block `end_frame` (+ optional shot `edit_out`) |

```json
{"blocks": [{"block_id": "B01", "order": 1, "purpose": "...", "duration_sec": 15,
  "audio_route": "native_diegetic_no_dialogue", "cast": ["HERO"], "location_id": "ROOFTOP",
  "refs": ["HERO_SHEET", "ROOFTOP_ENV"], "end_frame": "...", "risks": [],
  "shots": [{"shot_id": "B01_S1", "start_sec": 0, "end_sec": 6, "shot_size": "wide shot",
    "angle": "eye level", "camera_move": "slow push in", "lens": "35mm",
    "composition": "...", "action": "...", "must_include": ["..."]}]}]}
```

### Storyboard-to-Seedance handoff (P4)

The director/planner no longer hands over free metadata. `preprod.py shelf-brief --block <ID>` generates `preprod/04_shelf/<ID>/brief.md` from the locked concept/bible/storyboard/image plan; the Seedance prompting lane writes the English `prompt.txt` from it, `shelf-check` and `shelf-lock` verify it, and the user releases the shelf once. Production only copy-pastes the released shelf.

- One storyboard block = one generation (1–4 shots, 15 s). `STORYBOARD_SEQUENCE_PREVIS_MODE` (whole board in one generation) remains opt-in previs only and is `PREVIS_HOLD` until QC.

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
  "stress_gate": "three targeted attached-reference checks, recognizable identity 3/3; then clip-level QC",
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

Default provider is Seedance: one English shelf prompt per block via the P4 shelf (above). The bracket motion tags below are Grok-style and are used only if the user named Grok.

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

When the user asks for a full package, follow the fixed pre-production pipeline in `SKILL.md`:

1. P0 `concept_options.md` (3 options) → user choice → `concept_lock.json`
2. Verified audio spine (music lane) when applicable
3. P1 `style_bible.json` (palette, lighting, texture, lens grammar, forbidden looks, `style_block_en`, characters/locations)
4. Character triptych prompts and sheets (P3 refs named by `sheet_ref_id`)
5. P2 `storyboard.json` → user approval
6. P3 image prompts + `image_plan.json` with approved assets
7. P4 shelf prompts (English) → `shelf-lock` → user `shelf-release`
8. BGM JSON / narration sheet when in scope
