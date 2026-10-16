# Gold example 3 — two shots, product/object macro

Pattern: no cast (so no IDENTITY block), a prop ref + an environment ref, two
macro shots with exact contact and material physics.

## Locked inputs (excerpt)

```json
{
  "style_bible": {
    "style_block_en": "Premium product cinematography in live action macro, black walnut and brushed steel materials, one soft key light from upper left with a thin cool rim light, deep charcoal background, crisp micro-contrast, clean digital image without grain.",
    "characters": [],
    "locations": [{"id": "LOC_DESK", "description_en": "A dark walnut desk surface in a dim studio with a charcoal backdrop."}]
  },
  "refs": [
    {"ref_id": "REF_WATCH", "purpose": "prop", "role_en": "steel field watch"},
    {"ref_id": "REF_DESK", "purpose": "environment", "role_en": "walnut desk set"}
  ],
  "storyboard_block": {
    "block_id": "B03", "order": 3, "purpose": "The watch wakes up and shows its engraving",
    "duration_sec": 15, "audio_route": "native_diegetic_no_dialogue",
    "cast": [], "location_id": "LOC_DESK",
    "refs": ["REF_WATCH", "REF_DESK"],
    "end_frame": "The caseback fills the frame in sharp focus, the engraving catching a thin line of rim light.",
    "shots": [
      {"shot_id": "B03_S1", "start_sec": 0, "end_sec": 7, "shot_size": "extreme close-up",
       "angle": "low angle", "camera_move": "slow push in", "lens": "100mm macro",
       "composition": "dial fills the right two thirds, desk edge along the bottom",
       "action": "the crown is pushed in and the second hand starts", "must_include": ["second hand"]},
      {"shot_id": "B03_S2", "start_sec": 7, "end_sec": 15, "shot_size": "insert shot",
       "angle": "top-down", "camera_move": "rack focus",
       "composition": "watch face down, caseback centered",
       "action": "the watch is turned over, focus moves from strap to caseback", "must_include": ["engraved caseback"]}
    ]
  }
}
```

## Shelf prompt (`preprod/04_shelf/B03/prompt.txt`)

```prompt
15 seconds, 2 shots:
Premium product cinematography in live action macro, black walnut and brushed steel materials, one soft key light from upper left with a thin cool rim light, deep charcoal background, crisp micro-contrast, clean digital image without grain.
@Image1 is the steel field watch: keep its exact case shape, dial layout, hands, crown and strap stitching; do not invent extra text or logos.
@Image2 is the walnut desk set: take its wood grain, backdrop and light direction only. Hard cut between shots.
Shot 1 (0-7s): extreme close-up, low angle, 100mm macro lens, slow push in toward the dial. The dial fills the right two thirds, the desk edge along the bottom. A fingertip enters from frame left and presses the crown in with a small click; the second hand jumps, then sweeps smoothly as the push continues. Reflections slide across the domed crystal as the angle changes.
Shot 2 (7-15s): insert shot, top-down, static framing with a rack focus. Two fingers turn the watch face down onto the walnut; the steel settles with a soft knock and the strap folds to one side. Focus starts on the stitched strap in the foreground and racks to the engraved caseback, its lines catching the rim light.
Sound: the crown click, a quiet steady tick, steel touching wood, faint studio room tone. No music, no voice.
End frame: The caseback fills the frame in sharp focus, the engraving catching a thin line of rim light.
```

Why it passes: no cast, so no IDENTITY line is required; two tokens = two refs;
`insert shot` / `top-down` / `rack focus` appear inside Shot 2, not only in the
header; hand/product contact is the one shot-specific risk, so it is described
positively instead of listing negatives.
