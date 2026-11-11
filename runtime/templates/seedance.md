# Seedance — P4 shelf authoring, then P5 copy-paste production

**Authoring mode:** if `manifest.authoring.mode` is `claude`, do not write the creative files yourself — run `video-codex-runtime author run --project <p> --stage shelf --block <B>` (add `--feedback "<user words>"` for changes), then continue with the checks, user approval and lock below; inside a dispatched lane session `author run` is unavailable (not logged in), so return `PARTIAL` with the exact `--stage`/`--feedback` for the director instead. In `codex` mode write them yourself.

Authority: explicit 2.5 → `/Users/gnudas/.codex/skills/seedance25-prompt-en/`;
2.0 or unversioned → `/Users/gnudas/.codex/skills/seedance-prompt-en/`.
Load only the selected version. Runtime owns rails/media/safety. Prompts are English only.

## P4 — Author the shelf (no browser)
For every storyboard block, in order:
1. `video-codex-runtime preprod shelf-brief --project <p> --block <B>` → writes
   `preprod/04_shelf/<B>/brief.md`, `settings.json`, `refs.json` (and runs the bounded
   knowledge selection). The brief lists everything the prompt must contain.
2. Write `preprod/04_shelf/<B>/prompt.txt` following the skill's single canonical template:
   first line from the brief; STYLE and IDENTITY blocks verbatim; one binding sentence per
   `@ImageN`; `Shot k (a-bs):` sections with the exact shot size, angle, camera move and
   MUST phrases; end frame. No length target. No file names, gate words or notes.
3. `preprod shelf-check` until clean, then `preprod shelf-lock` (also runs attestation).
When all blocks are locked, show the user every `prompt.txt` (one per block) and ask once;
then `preprod shelf-release --blocks ALL_LOCKED --approval-quote "<user's words>"`.

## P5 — Production (copy-paste only)
The director normally launches this through `video-codex-runtime produce`; you are one of its sessions and handle the blocks it names.
Read `~/.codex/skills/seedance-prompt-en/production-card.md` and nothing else first: per block one
`runway_ui_helper.py run-block --project <p> --block-id <B>` (attach from Uploads, settings, paste,
preflight), then one Generate click. The numbered steps below are what run-block does.
Continue in this same conversation; the phase change is not a spawn. For each released block:
1. `preprod shelf-verify --block <B>` must be `ok`. Any failure → stop that block and return to P4.
2. `runway_ui_helper.py prepare-upload-bundle --project <p> --block-id <B> --pack preprod/04_shelf/<B>/pack.json`
   → `bundle.json` gives each slot its file (`RW_<sha12>.<ext>`, named by content) and an `attach` step.
   `SELECT_EXISTING_RUNWAY_UPLOAD`: pick it in Asset selector > Uploads (Recents per `search_pills`) by the listed `search_names`
   (never upload it again). `UPLOAD_NEW_VIA_NATIVE_CHOOSER`: upload that file. After the enlarged
   thumbnail is verified, `record-runway-attach --path <file> --name <name> --how reused|uploaded`;
   a searched name with no row → `--how missing`.
3. Settings from `settings.json`; `settings-verify` must pass (it also reads the visible duration/model).
4. `paste-prompt --file preprod/04_shelf/<B>/prompt.txt --pack preprod/04_shelf/<B>/pack.json`, verify, Generate once.
Never edit, shorten, translate or "improve" a released prompt during production. If it needs
a change, go back to P4 (or P2 for composition changes), re-lock and get it released again.
Attachment, recovery, exactly-once submit and queue handling are owned by the selected skill's
production doc and `aside-operator.md`.

Download the matching output, verify bytes/duration/codec/resolution and ingest into
`media/06_videos_candidates_영상후보/`; queue the registered asset for Seedance QC.

## Legacy projects (no `preprod/`)
Author a pack under `lanes/seedance/prompts/` and `prompt_packet_utils.py attest --project <p>` before any UI step; the same production rules apply.

Outputs: shelf files + SHELF_LOCK, settings/upload/card evidence, downloaded asset IDs + ffprobe, `status.json`, `result.md`.
