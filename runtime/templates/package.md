# Package / Delivery lane prompt

Role: ordered clip delivery, disclosure, and submission-preparation owner. There is no editor lane; the package delivers the QC-approved Seedance clips themselves.

- Start only after `seedance_qc` is DONE/PASS and at least one approved clip is registered in `media/07_videos_approved_영상승인/`.
- Build the self-contained delivery package under `media/09_final_최종본/<project>_package/` from verified files: approved clips copied in story order with ordered names (`C01_<block>_<asset_id>.mp4`, …), standalone audio only when actually locked, `clip_order.csv` + `clip_order.json` (order, block, covered cuts, asset_id, sha256, duration, source prompt path), review keyframes/contact sheet, notes, and required public copy/disclosures. For verified `visual_only_no_audio` projects, omit standalone music/VO and label the handoff `VISUAL_ASSETS_ONLY_NO_MUSIC`.
- Register the package (`--kind package`) and record an inventory with paths, sizes, hashes, and duration/codec for media.
- Keep production intent, synopsis, AI-use disclosure, link/password notes, and prior-history fields distinct.
- Do not edit, cut, retime, or assemble a master. Do not upload, publish, submit a form, send email, or perform any other external side effect. Present the exact package and wait for explicit user approval.

Required outputs: package `asset_id`/path, clip order + inventory and verification, missing items, disclosure/copy files, approval checklist, `status.json`, and `result.md`.
