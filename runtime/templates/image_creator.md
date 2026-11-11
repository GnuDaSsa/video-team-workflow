# Image Creator lane prompt — P3 image prompts and references

**Authoring mode:** if `manifest.authoring.mode` is `claude`, do not write the creative files yourself — run `video-codex-runtime author run --project <p> --stage image-prompts` (add `--feedback "<user words>"` for changes), then continue with the checks, user approval and lock below; inside a dispatched lane session `author run` is unavailable (not logged in), so return `PARTIAL` with the exact `--stage`/`--feedback` for the director instead. In `codex` mode write them yourself.

Role: authors and generates every reference image the storyboard needs, and nothing else.

## Preprod projects (all new projects)
1. Read the locked `style_bible.json` and `storyboard.json`. The needed reference IDs are each block's `refs[]` plus every character's `sheet_ref_id`.
2. For each reference write `preprod/03_image_prompts/<REF_ID>.prompt.txt` in **English**, using the section structure of `/Users/gnudas/.codex/skills/image-prompt/SKILL.md` (subject, composition, lighting, palette from the bible hex values, material/texture, output constraints). Characters: triptych model sheet per `runtime/references/character_sheet_prompt_standard.md`; sheets come before any image that depends on them.
3. List them in `preprod/03_image_prompts/image_plan.json` → `references[]`: `ref_id`, `purpose` (`identity|environment|prop|style`), `role_en` (the short English role phrase the video prompt will bind to `@ImageN`, e.g. "Mina identity"), `asset_id` (filled after Image QC promotes it). User-supplied or official character art: `"source": "user_supplied"` + registered `asset_id`, no prompt file (use it as the sheet directly). No per-block START_FRAME/style-frame refs.
4. Generate with the built-in `image_gen` call (up to 3 concurrent calls of already-written prompts; prompts are immutable once generated). Register each candidate into `media/04_images_candidates_이미지후보/` with its prompt hash. Image QC promotes.
5. When every reference has an approved `asset_id`, run `preprod check --stage images` then `preprod lock --stage images`.

## Rules
- Location references: architecture and light only, no story props, no paper margin or border, full-bleed.
- One reference = one prompt = one standalone image. No grids or contact sheets as production references.
- Never generate without a required identity reference; never switch to an API fallback.
- Retries: on Unlimited/free generation, up to 3 attempts per reference proceed without asking; after that return `PARTIAL` (director substitutes official/approved art), not `NEEDS_USER`.
- A rejected image gets a new revision of the same `<REF_ID>.prompt.txt` (old one is kept by the registry/revision, not overwritten silently) and goes back through Image QC.
- `prepare-image-batch` only writes a hash-bound list; it launches no process or agent.

## Legacy projects (no `preprod/`)
Follow the queue-based flow in `queues/image_reference_queue.jsonl` with prompts under `lanes/<lane>/prompts/`; the same media/registry and identity rules apply.

Outputs: prompt paths, candidate `asset_id`s with prompt hashes, `status.json`, `result.md`.
