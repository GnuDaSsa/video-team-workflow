# Output formats

Copy-paste-ready shapes for cut lists, character/scene JSON, BGM, and narration sheets.

## Output formats

### Cut list

Use a table with these columns:

| scene | timecode | visual | narration |
|------|----------|--------|-----------|

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
2. Timeline or scene structure
3. Character JSON
4. Character sheet JSON
5. Scene start-frame JSON
6. Seedance/I2V motion prompts (or Grok only if user named Grok)
7. BGM JSON
8. Narration/dialogue sheet
