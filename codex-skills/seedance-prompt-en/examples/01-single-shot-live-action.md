# Gold example 1 — one continuous shot, live action

Pattern: one character, one location, one dominant camera move for the whole
block. Read `../seedance-prompting.md` → Canonical template first; this file
only shows it filled in.

## Locked inputs (excerpt)

`style_bible.json` + `image_plan.json` refs + one `storyboard.json` block:

```json
{
  "style_bible": {
    "style_block_en": "Grounded cinematic live action, early morning overcast light through a window, muted sage and warm brass palette, natural skin and fabric texture, 35mm lens look, shallow depth of field, fine film grain.",
    "characters": [{"id": "CHAR_HANA", "sheet_ref_id": "REF_HANA_SHEET",
      "identity_block_en": "Hana: Korean woman in her early thirties, straight black hair tied in a low ponytail, oval face, thin gold-rimmed glasses, dark green canvas apron over a cream knit sweater, flour dust on her sleeves."}],
    "locations": [{"id": "LOC_BAKERY", "description_en": "A narrow neighborhood bakery kitchen with a steel worktable, a deck oven on the right wall and a fogged window at the back."}]
  },
  "refs": [
    {"ref_id": "REF_HANA_SHEET", "purpose": "identity", "role_en": "Hana identity"},
    {"ref_id": "REF_BAKERY", "purpose": "environment", "role_en": "bakery kitchen"}
  ],
  "storyboard_block": {
    "block_id": "B01", "order": 1, "purpose": "Hana takes the first batch out of the oven",
    "duration_sec": 15, "audio_route": "native_diegetic_no_dialogue",
    "cast": ["CHAR_HANA"], "location_id": "LOC_BAKERY",
    "refs": ["REF_HANA_SHEET", "REF_BAKERY"],
    "end_frame": "Hana in profile on the right third beside the open oven, steam drifting over the tray, camera at rest.",
    "shots": [
      {"shot_id": "B01_S1", "start_sec": 0, "end_sec": 15,
       "shot_size": "medium shot", "angle": "eye level", "camera_move": "truck right", "lens": "35mm",
       "composition": "Hana on the left third at the worktable, oven out of frame right",
       "action": "she presses dough, walks right to the oven and pulls out a tray of loaves",
       "must_include": ["steel worktable", "oven door"]}
    ]
  }
}
```

## Shelf prompt (`preprod/04_shelf/B01/prompt.txt`)

```prompt
15 seconds, one continuous shot:
Grounded cinematic live action, early morning overcast light through a window, muted sage and warm brass palette, natural skin and fabric texture, 35mm lens look, shallow depth of field, fine film grain.
Hana: Korean woman in her early thirties, straight black hair tied in a low ponytail, oval face, thin gold-rimmed glasses, dark green canvas apron over a cream knit sweater, flour dust on her sleeves.
@Image1 is Hana's identity: take her face, hair, glasses and apron only, never its plain background or standing pose.
@Image2 is the bakery kitchen: take its layout, steel surfaces, oven and window light only. The two images are independent anchors, not a time order.
Medium shot, eye level, 35mm, one slow truck right at walking pace for the whole shot. Hana stands at the steel worktable on the left third and presses a ball of dough flat with both palms; a puff of flour lifts at each press. She wipes her palms on the apron, turns and walks right while the camera keeps her the same size, the worktable sliding past in the foreground. She grips the oven door handle with a folded towel and pulls; the door swings down, heat haze ripples above the opening and the window behind her fogs a little more. She slides out a tray of round loaves, the crusts crackle as cooler air reaches them, and she sets the tray on the rack.
Sound: dough slapping the table, apron cloth, the oven hinge, crust crackle, a low kitchen fan. No dialogue, no music.
End frame: Hana in profile on the right third beside the open oven, steam drifting over the tray, camera at rest.
```

Why it passes: exact first line; STYLE and IDENTITY pasted verbatim; one
binding sentence per token; `medium shot` / `eye level` / `truck right` and both
MUST phrases appear; the only seconds mention is the header; physics only where
the action causes it (flour, heat haze, crust); end frame last.
