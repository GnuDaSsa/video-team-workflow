# Runway → Seedance reference attach playbook

Purpose: make Codex Computer Use attach reference images into the active Runway Seedance 2.0 Multi-reference strip reliably. Use this for the `seedance` / 후시구로 토우지(video) lane only.

## Evidence from prior successful run

Successful smoke-test B02 evidence:

- Project: `~/Documents/Codex/video-team-runtime/20260523_102656_lyrical-2img-2video-smoke`
- UI route: Safari `app.runwayml.com` generation session, Video selected, Seedance 2.0, Multi-reference selected.
- Success evidence files:
  - `lanes/seedance/logs/B02_submission_ui.json`
  - `lanes/seedance/logs/provider_route_verification.json`
  - `lanes/seedance/run.log` around the B02 UI observation.
- Key observed success state:
  - `reference_attachment`: `IMG_1 visible in active Multi-reference strip`
  - `prompt_counter`: `1133 / 3500`
  - `duration`: `10 seconds`
  - `resolution`: `720p`
  - generation card visible/in queue after Generate.
- Key success method from the log:
  - Use a clean staged upload path, e.g. `~/Downloads/SEEDANCE_B02_UPLOAD_ONLY/B02_REF_UPLOAD_THIS.png`.
  - Existing Safari Runway Seedance Multi-reference session must be verified.
  - Upload/select that clean file, then verify the active Multi-reference strip shows `IMG_1` before Generate.

## Failure pattern in current Anime MV run

Current failed attempts show:

- Prompt can be inserted correctly into the custom board.
- Failure happens when pressing/using the reference control.
- CUA element IDs/coordinate clicks sometimes switch Runway between Generate / Apps / Assets or another Safari tab.
- Old thumbnail such as `image2` / `IMG_2` can remain in the active strip.
- Opening the asset selector or native picker is not enough; the uploaded/selected asset must become visible in the top active Multi-reference strip in the right order.

## Non-negotiable control rules

1. Do not click Generate unless the top active Multi-reference strip visibly shows every required reference thumbnail in exact order.
2. File picker selection alone is not proof. Blue native `업로드` alone is not proof. An asset visible in the library is not proof. Proof is thumbnail(s) attached in the active top Multi-reference strip.
3. Avoid multi-file selection until one-by-one attach is stable. Attach references one at a time in order: #1, verify `IMG_1`; #2, verify `IMG_2`; etc.
4. Prefer clean one-file staging folders under `~/Downloads/SEEDANCE_<BLOCK>_<ORDER>_UPLOAD_ONLY/` for each reference. Deep project paths confuse pickers/search and increase wrong-file risk.
5. Correct upload route is the native Finder file picker opened by Runway's drag-and-drop/upload file button. Use Cmd+Shift+G in that Finder picker and paste the staged folder/file path. Do not look for files in `/var/folders/.../TemporaryItems/NSIRD_screencaptureui...` or any screenshot temporary path, and do not use Runway asset filename search as the primary upload route.
6. Before attaching, clear any stale active strip thumbnails (`image2`, old `IMG_*`) if the UI provides an X/remove button. If stale thumbnails cannot be cleared, block rather than generate.
7. Do not use generic coordinate clicks from stale screenshots. Re-capture after every panel/view change and click only the current visible Add/Upload/Select controls.

## Recommended attach sequence

For each reference in `ui_image_order`:

1. Stage a single clean file:
   - Copy only that reference PNG into a dedicated simple folder:
     `~/Downloads/SEEDANCE_<BLOCK>_<ORDER>_UPLOAD_ONLY/<ORDER>_<REF_ID>.png`
   - Verify size/hash against original.
2. Return to the verified Runway generation board:
   - URL domain `app.runwayml.com`
   - tool/model visible: Seedance 2.0
   - input mode visible: Multi-reference
   - prompt text/counter still visible and <= 3500
3. Open the active Multi-reference reference area, not generic Recent Generations:
   - Use the button/control adjacent to the top Multi-reference strip / reference slot.
   - If the click opens a full Assets/Recent Generations page instead of the attach selector, go back to the Generate board and retry from the reference slot.
4. In the upload/asset selector:
   - Click Runway's drag-and-drop/upload file button so the native Finder file picker opens.
   - In the native Finder picker, use Cmd+Shift+G or the picker path field; paste the single staged file path or its simple `~/Downloads/SEEDANCE_<BLOCK>_<ORDER>_UPLOAD_ONLY/` folder.
   - Do not search Runway Assets/Recent by filename as the primary route.
   - Do not use `/var/folders/.../TemporaryItems/NSIRD_screencaptureui...` or any screenshot temporary path as an upload source.
   - Click blue `업로드` if shown.
   - Wait for upload toast/spinner to finish.
5. Attach the uploaded asset:
   - In the right References/Assets selector, click the just-uploaded thumbnail for that exact file, not an old `image2`/recent generation/video.
   - The thumbnail must appear in the active top Multi-reference strip as `IMG_<n>` or equivalent.
6. Verify after each file:
   - #1 → visible `IMG_1`
   - #2 → visible `IMG_1`, `IMG_2`
   - #3 → visible `IMG_1`, `IMG_2`, `IMG_3`
   - #4 → visible `IMG_1`, `IMG_2`, `IMG_3`, `IMG_4`
   - Record screenshot/visible state description in `lanes/seedance/logs/<BLOCK>_reference_attach_verification.json`.
7. Only after all attached thumbnails are visible in order:
   - verify prompt counter <= 3500;
   - verify settings 16:9 / 720p / target duration;
   - click Generate once.

## Recovery if stuck

- If a stale thumbnail remains and no remove/X is accessible: stop and write `BLOCKED_STALE_REFERENCE_STRIP_NOT_CLEARABLE`; do not Generate.
- If file picker upload succeeds but library selection does not attach to top strip: try drag/drop from Finder only if Codex Computer Use has Finder permissions; otherwise block.
- If the UI lands on Recent Generations/Assets page, do not select video cards; return to Generate board and re-open the reference slot.
- If a queued job already exists for that block, do not click Generate again; wait/download.
