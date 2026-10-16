# BAD → GOOD — fixing a freestyle prompt

Same locked inputs as example 1 (`01-single-shot-live-action.md`: Hana, bakery,
`@Image1` identity, `@Image2` kitchen), but a two-shot storyboard block:

```json
{
  "storyboard_block": {
    "block_id": "B04", "order": 4, "purpose": "Hana tastes the first loaf",
    "duration_sec": 15, "audio_route": "native_diegetic_no_dialogue",
    "cast": ["CHAR_HANA"], "location_id": "LOC_BAKERY",
    "refs": ["REF_HANA_SHEET", "REF_BAKERY"],
    "end_frame": "Hana's eyes closed mid-chew, steam rising from the torn loaf in the foreground.",
    "shots": [
      {"shot_id": "B04_S1", "start_sec": 0, "end_sec": 6, "shot_size": "insert shot",
       "angle": "high angle", "camera_move": "static",
       "composition": "loaf centered on the rack, her hands entering from below",
       "action": "she tears the loaf open", "must_include": ["torn crust"]},
      {"shot_id": "B04_S2", "start_sec": 6, "end_sec": 15, "shot_size": "medium close-up",
       "angle": "eye level", "camera_move": "slow push in",
       "composition": "Hana on the left third, loaf soft in the foreground right",
       "action": "she takes a bite and her shoulders drop", "must_include": ["gold-rimmed glasses"]}
    ]
  }
}
```

## BAD (freestyle)

```text
Cinematic masterpiece, 8K, ultra detailed, epic emotional moment. Scene ID: B04. Mode: Creative.
REFERENCE ROLES: Image1 = CHAR_HANA sheet, Image2 = bakery styleframe for B04.
Hana is in her bakery and feels nostalgic and happy about her first bread. The camera orbits around her, then whip pans to the oven, then does a dolly zoom on her face. Lots of steam, flour, light rays, lens flares, hair blowing, dust, sparkles. 10 seconds of slow motion. She says "정말 맛있다" warmly.
No blur, no extra people, no deformed hands, no bad anatomy, no text, no watermark, no cartoon, no camera shake.
Audio ON in UI. EXIT: hands off to B05.
```

What `preprod.py shelf-check` and attestation report, and why:

| Problem | Validator / rule |
|---|---|
| first line is not `15 seconds, 2 shots:` | `shelf_first_line_must_be` |
| STYLE / IDENTITY paraphrased, not verbatim | `shelf_style_block_not_verbatim`, `shelf_identity_not_verbatim:CHAR_HANA` |
| `Image1` without `@`, no binding sentence | `shelf_tokens_[]_must_equal_['@Image1', '@Image2']` |
| no `Shot 1 (0-6s):` / `Shot 2 (6-15s):` sections | `shelf_shot_markers_missing_or_out_of_order` |
| `10 seconds` contradicts the lock | `shelf_conflicting_duration_mention:10` |
| `Scene ID:`, `Mode:`, `REFERENCE ROLES:`, `CHAR_`, `styleframe for`, `Audio ON`, `EXIT:` | attestation leak pattern |
| three camera moves, none from the storyboard | one dominant move per shot, as declared |
| ten physics/effect layers with no cause | physics only where the shot needs it |
| named emotion, quality adjectives, negative wall | show it; one or two shot-specific risks |
| dialogue in a `native_diegetic_no_dialogue` block | dialogue route table in `../seedance-shared-contract.md` |

## GOOD (passes shelf-check)

```prompt
15 seconds, 2 shots:
Grounded cinematic live action, early morning overcast light through a window, muted sage and warm brass palette, natural skin and fabric texture, 35mm lens look, shallow depth of field, fine film grain.
Hana: Korean woman in her early thirties, straight black hair tied in a low ponytail, oval face, thin gold-rimmed glasses, dark green canvas apron over a cream knit sweater, flour dust on her sleeves.
@Image1 is Hana's identity: take her face, hair, glasses and apron only, never its plain background or standing pose.
@Image2 is the bakery kitchen: take its rack, steel surfaces and window light only. Hard cut between shots.
Shot 1 (0-6s): insert shot, high angle, static camera. A round loaf sits centered on the cooling rack. Hana's floury hands enter from the bottom of frame, press into the crust and pull the loaf apart; the torn crust cracks, a ribbon of steam escapes, and crumbs drop through the rack.
Shot 2 (6-15s): medium close-up, eye level, slow push in. Hana on the left third, the torn loaf soft in the foreground right. She lifts a piece, blows on it once, and bites; her jaw slows, the gold-rimmed glasses slide a little down her nose, and her shoulders drop as she breathes out through her nose. Her eyes close.
Sound: crust cracking, crumbs on steel, one soft breath out, a low kitchen fan. No dialogue, no music.
End frame: Hana's eyes closed mid-chew, steam rising from the torn loaf in the foreground.
```

The fix is mechanical: start from `brief.md`, paste the locked blocks, write one
binding sentence per token, one section per storyboard shot with its exact
phrases, then cause → contact → response, sound, end frame. No invention outside
the storyboard.
