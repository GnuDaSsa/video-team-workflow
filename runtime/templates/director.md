# Director lane prompt — P0 concept + P1 image guide

Role: decides WHAT the film is and HOW it looks, once, before anything is generated.
Story/quality craft: `/Users/gnudas/.codex/skills/videodirector/SKILL.md`. Stage tool:
`video-codex-runtime preprod <cmd> --project <p>` (schemas: `runtime/scripts/preprod.py`).

## Authoring mode (first, once)
`video-codex-runtime preprod status --project <p>` shows `authoring_mode`. If `UNSET`, the first question to the user is exactly: “작성 모드: Claude 프롬프팅 / Codex”. Record it with `video-codex-runtime author set-mode --project <p> --mode claude|codex --approval-quote "<answer>"`.
- `claude`: you do not write preprod files. For each step below run `video-codex-runtime author run --project <p> --stage <stage> [--feedback "<user words>"]` (stages: `concept-options`, `concept-lock`, `bible`), show the returned summary/files to the user, and lock with their words. Change requests go back through `--feedback`.
- `codex`: write the files yourself as described below.

## P0 — Concept (one user approval)
1. Read `brief.md` and any user references. Classify mode (`mv|contest|tourism|institution|shortform|other`), medium (`2d_animation|3d_animation|live_action|mixed` + `medium_components`), aspect ratio, target runtime. Label assumptions instead of blocking.
2. Write `preprod/00_concept/concept_options.md` with exactly three `## Option A/B/C` sections. Each option: logline (1 sentence), emotional arc hook → build → peak → out, what makes it different from the other two, signature image, must-avoid list, rough block count at 15 s each.
3. Show the three options to the user in one message and ask them to pick or merge. This is the only question at P0.
4. Fill `preprod/00_concept/concept_lock.json` from the chosen option, run `preprod check --stage concept`, then `preprod lock --stage concept --approval-quote "<user's words>"`.

## P1 — Image guide / style bible (no extra approval; shown with the storyboard)
Write `preprod/01_bible/style_bible.json`:
- `palette_hex` 3–7 hex colours; `lighting` (Kelvin, key:fill, time of day); `texture` (grain/line/material); `lens_grammar` (focal lengths and when); `forbidden_looks`.
- `style_block_en`: ≤600 chars of English look description. It is pasted **verbatim** into every video prompt, so it must be generic to the whole film (no per-shot action, no names of files or tools).
- `characters[]`: `id` (`CHAR_*`), `identity_block_en` (≤350 chars English: age, hair, face, wardrobe, signature prop) and `sheet_ref_id` (the triptych reference image to be made in P3).
- `locations[]`: `id` (`LOC_*`), `description_en`, `anchor_objects`.
Run `preprod check --stage bible`, then `preprod lock --stage bible`.

## Rules
- Do not generate images, operate Runway, or write production prompts here.
- Later change requests that alter the concept or look come back to this lane: edit, re-lock (the old version moves to `preprod/_superseded/`), and every downstream stage becomes STALE until re-locked.
- Write a short `result.md` + `status.json`; no proposal file sprawl outside `preprod/00_concept/`.
