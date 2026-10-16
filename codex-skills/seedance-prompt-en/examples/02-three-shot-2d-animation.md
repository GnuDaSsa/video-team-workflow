# Gold example 2 — three planned shots, 2D animation

Pattern: one character ref + one environment ref, three causally linked shots,
one dominant camera move per shot as declared in the storyboard.

## Locked inputs (excerpt)

```json
{
  "style_bible": {
    "style_block_en": "Hand-drawn 2D animation, clean variable-weight ink lines, flat cel colors with one hard shadow tone, painted watercolor backgrounds, warm dusk palette of coral, indigo and pale gold, limited animation on twos with crisp key poses.",
    "characters": [{"id": "CHAR_JUN", "sheet_ref_id": "REF_JUN_SHEET",
      "identity_block_en": "Jun: ten-year-old boy, round face, spiky black hair with one tall cowlick, oversized yellow raincoat, red rubber boots, a small blue paper kite in his right hand."}],
    "locations": [{"id": "LOC_HILL", "description_en": "A grassy hilltop with one bent pine tree and a small town of rooftops far below."}]
  },
  "refs": [
    {"ref_id": "REF_JUN_SHEET", "purpose": "identity", "role_en": "Jun character sheet"},
    {"ref_id": "REF_HILL", "purpose": "environment", "role_en": "dusk hilltop"}
  ],
  "storyboard_block": {
    "block_id": "B02", "order": 2, "purpose": "Jun reaches the hilltop and his kite finally flies",
    "duration_sec": 15, "audio_route": "native_diegetic_no_dialogue",
    "cast": ["CHAR_JUN"], "location_id": "LOC_HILL",
    "refs": ["REF_JUN_SHEET", "REF_HILL"],
    "end_frame": "Jun's face on the right third, eyes lifted to the kite, cowlick bending in the wind.",
    "shots": [
      {"shot_id": "B02_S1", "start_sec": 0, "end_sec": 4, "shot_size": "extreme wide shot",
       "angle": "high angle", "camera_move": "static",
       "composition": "hill diagonal from lower left, pine on the right, Jun small at lower left",
       "action": "Jun runs up the slope toward the pine", "must_include": ["bent pine tree"]},
      {"shot_id": "B02_S2", "start_sec": 4, "end_sec": 9, "shot_size": "medium shot",
       "angle": "low angle", "camera_move": "tracking",
       "composition": "Jun center, sky filling the upper two thirds",
       "action": "he runs, lets go, and the kite climbs", "must_include": ["blue paper kite"]},
      {"shot_id": "B02_S3", "start_sec": 9, "end_sec": 15, "shot_size": "close-up",
       "angle": "eye level", "camera_move": "slow push in",
       "composition": "face on the right third, kite string leading out of frame left",
       "action": "his worried mouth opens into a grin", "must_include": ["cowlick"]}
    ]
  }
}
```

## Shelf prompt (`preprod/04_shelf/B02/prompt.txt`)

```prompt
15 seconds, 3 shots:
Hand-drawn 2D animation, clean variable-weight ink lines, flat cel colors with one hard shadow tone, painted watercolor backgrounds, warm dusk palette of coral, indigo and pale gold, limited animation on twos with crisp key poses.
Jun: ten-year-old boy, round face, spiky black hair with one tall cowlick, oversized yellow raincoat, red rubber boots, a small blue paper kite in his right hand.
@Image1 is Jun's character sheet: take his face, hair, raincoat, boots and kite design only, never the sheet layout, panel borders or neutral backdrop.
@Image2 is the dusk hilltop: take its slope, pine silhouette, town below and sky colors only. Hard cuts between shots.
Shot 1 (0-4s): extreme wide shot, high angle, static camera. The hill runs diagonally from lower left; the bent pine tree stands on the right against a coral sky. Jun, small at lower left, runs up the slope with the kite held high, raincoat flapping behind him. Cut as he reaches the crest.
Shot 2 (4-9s): medium shot, low angle, tracking beside him at running speed. Jun sprints along the crest, glances back, and opens his hand; the blue paper kite dips once, catches the wind, and climbs out of the top of frame while the string snaps taut in his fist. His boots skid to a stop in the grass.
Shot 3 (9-15s): close-up, eye level, slow push in. Jun's face on the right third, string leading out of frame left. His mouth is a tight worried line; the string tugs, his eyes lift, and the line breaks into a wide grin as the cowlick bends in the wind. Hold the grin.
Sound: running footsteps in grass, raincoat flapping, wind gusts, the kite paper rattling, a short delighted gasp. No dialogue, no music.
End frame: Jun's face on the right third, eyes lifted to the kite, cowlick bending in the wind.
```

Why it passes: header count = shot count; each `Shot k (a-bs):` marker matches
the storyboard times; each section holds its own size/angle/move phrases and
MUST phrase; one move per shot; the emotion is shown as mouth/eye change, not
named.
