# Seedance provider-lane and continuity rules — 2026-07-07

Ported from the operator standing rules (`~/.codex/AGENTS.md`) so the reusable package carries the provider-truth and multi-reference continuity gates.

# Seedance continuity-critical multi-reference rule — 2026-07-07

For recurring-character public-contest/MV clips, do not rely on a single uploaded production frame in Seedance when identity, gender/role readability, car/prop geometry, or adjacent-cut continuity matters. Use multi-reference: production styleframe + approved character/model sheet(s) + adjacent continuity frame and, when needed, specific prop/vehicle staging reference. A technically clean single-image I2V output can still fail if the car/prop staging is broken, gender/role reading is unclear, or the character looks like a different person. Provider reports must truthfully name Seedance vs Grok; if the final files are Grok fallback, do not describe them as Seedance output.

# Seedance ↔ Grok provider-lane separation rule — 2026-07-07

For the user's video-team workflow, Seedance-primary work and Grok fallback work must be separated from the planning stage, not reconstructed after the edit.

Required per-cut provider matrix before any clip enters CapCut or final timeline:
- `seedance_primary_status`: not_started / refs_prepared / refs_uploaded_visible / submitted / queued / downloaded / qc_pass / qc_fail / blocked.
- `seedance_downloaded_file`: exact path, or `NONE_UI_ONLY` if a Runway UI candidate exists but has not been downloaded.
- `grok_fallback_status`: not_used / prepared / submitted / downloaded / qc_pass / qc_fail.
- `grok_downloaded_file`: exact path when used.
- `provider_switch_reason`: hard Runway wait/Credits/account blocker, explicit user approval, or planned provider split.
- `final_selected_provider`: Seedance / Grok / other.
- `final_selected_file`: exact file path used in CapCut/final export.

Rules:
- A Seedance prompt card, uploaded sourceframe, or visible reference thumbnail is not a generated Seedance candidate. It must not be reported as Seedance output until a visible queued/generated card and downloaded result file are verified, or explicitly marked `UI_ONLY_NOT_PACKAGED`.
- If Grok files enter the timeline, call them Grok fallback files even when the project began as Seedance-primary.
- If Runway/Seedance generated UI-side candidates but they were not downloaded/packaged, recover them from Runway history and register them as separate Seedance candidates before selection.
- Do not collapse provider status into a single “I2V done” state. Provider evidence and selected final source are separate QC gates.
- For continuity-critical Seedance cuts, use the character/model sheet and multi-reference package; do not rely on one production frame only.

