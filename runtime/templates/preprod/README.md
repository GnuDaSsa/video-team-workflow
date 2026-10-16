# Pre-production templates (preprod v5)

`preprod.py init` copies these skeletons into a new project's `preprod/` (this README is not copied).
They are shape examples with placeholders: field names match the validators in
`runtime/scripts/preprod.py` exactly, but the placeholder values will not pass `check` until edited.
Contract: `docs/contracts/2026-10-16-preprod-shelf-v5.md`. Authoring guidance: `videodirector/SKILL.md`
§ Fixed pre-production pipeline.

## Stage order

| Stage | Owner | File(s) | Lock |
|---|---|---|---|
| P0 concept | director | `00_concept/concept_options.md` (≥3 `## Option X`), `00_concept/concept_lock.json` | user choice quote |
| P1 style bible | director | `01_bible/style_bible.json` (`style_block_en` ≤600, `identity_block_en` ≤350) | lane self-check |
| P2 storyboard | planner | `02_storyboard/storyboard.json` (15 s blocks, 1–4 shots, contiguous time) | user approval quote |
| P3 image prompts | image_creator / image_qc | `03_image_prompts/<REF>.prompt.txt` (English), `image_plan.json` | all refs approved in registry |
| P4 shelf | seedance prompting | `04_shelf/<BLOCK>/{brief.md, prompt.txt, settings.json, refs.json, pack.json, SHELF_LOCK.json}` | `shelf-lock`, then one user `shelf-release` |
| P5 production | seedance production | consumes the released shelf only | `shelf-verify` |

Changing an upstream file makes its lock and every downstream lock STALE. Re-lock moves the old copy to
`preprod/_superseded/`. No new creative decisions at production time: edit the owning stage and re-lock.

Notes on fields:
- `concept_lock.json`: `mode` ∈ mv/contest/tourism/institution/shortform/other; `medium` ∈
  2d_animation/3d_animation/live_action/mixed (`mixed` needs ≥2 `medium_components`).
- `storyboard.json`: `shot_id` = `<BLOCK>_S<k>`; `shot_size`, `angle`, `camera_move` use the controlled
  lists `SHOT_SIZES`, `ANGLES`, `CAMERA_MOVES` in `preprod.py`; `duration_sec` must equal the project
  duration lock; `audio_route` ∈ native_diegetic_no_dialogue/native_dialogue/silent/music_reference.
- `image_plan.json`: `purpose` ∈ identity/environment/prop/style; set `"source": "user_supplied"` for a
  supplied image (no prompt file needed); `asset_id` is filled once the asset is approved.

## Commands

```bash
P=<absolute project path>
python3 runtime/scripts/preprod.py init   --project "$P"
python3 runtime/scripts/preprod.py status --project "$P"
python3 runtime/scripts/preprod.py check  --project "$P" --stage concept|bible|storyboard|images
python3 runtime/scripts/preprod.py lock   --project "$P" --stage concept    --approval-quote "<user words>"
python3 runtime/scripts/preprod.py lock   --project "$P" --stage bible
python3 runtime/scripts/preprod.py lock   --project "$P" --stage storyboard --approval-quote "<user words>"
python3 runtime/scripts/preprod.py lock   --project "$P" --stage images
python3 runtime/scripts/preprod.py shelf-brief   --project "$P" --block B01
python3 runtime/scripts/preprod.py shelf-check   --project "$P" --block B01
python3 runtime/scripts/preprod.py shelf-lock    --project "$P" --block B01
python3 runtime/scripts/preprod.py shelf-release --project "$P" --blocks ALL_LOCKED --approval-quote "<user words>"
python3 runtime/scripts/preprod.py shelf-verify  --project "$P" --block B01
```
