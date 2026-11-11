# Flow lane prompt — Google Flow production (explicit user request only)

Role: produce the simple, low-direction shots the director assigned to Google Flow, and nothing else.
Seedance stays the provider for every shot not listed here. Never run Flow and Runway at the same time.

## Inputs
- `lanes/flow/director_intent.md`: the user quote, the block list, and the credit budget.
- `lanes/flow/blocks/<BLOCK>/prompt.txt` and `inputs.json` (approved image asset_id + sha256, settings). Treat both as immutable: paste the prompt verbatim; do not shorten, translate or "improve" it. A wording problem goes back to the director as `PARTIAL` with the exact reason.

## Procedure per block
1. Verify the image file sha256 and the prompt sha256 against `inputs.json`.
2. Google Flow (labs.google/fx/tools/flow) in the existing Aside profile; GUI work goes through the Aside CLI. Use the settings in `inputs.json` (model, mode, aspect 16:9, duration, outputs). Read the displayed credit cost before Generate; if it exceeds the remaining budget in the intent, stop with `NEEDS_USER`.
3. Generate once. Wait in the same turn. A policy rejection or failure is recorded in `lanes/flow/blocks/<BLOCK>/result.json`; up to 1 retry only if the intent allows it.
4. Download the result, register it in `media/06_videos_candidates_영상후보/` with provider `google_flow`, the block id, the prompt hash and the image asset id. Copy the edit copy to the path given in the intent if one is given.
5. Record `lanes/flow/blocks/<BLOCK>/result.json`: model, mode, duration, credits shown, file path, asset_id, sha256.

## Rules
- Login, payment, plan upgrades and credit top-ups are user gates (`NEEDS_USER`).
- Do not record Flow output as Seedance output, and do not touch the Seedance shelf or its ledger.
- Finish with `status.json` (DONE / PARTIAL / NEEDS_USER), `result.md`, and `session_result.json` per the shared contract.
