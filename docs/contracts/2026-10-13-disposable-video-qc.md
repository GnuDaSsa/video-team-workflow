# Disposable video QC (explicit opt-in)

## Scope
Provide a deterministic, single-owner local lifecycle for newly downloaded QC copies: receipt/authorization → registry ingest → bounded review report → verified Trash move. No downloader, watcher, scheduler, automatic perception, permanent deletion, cloud mutation or broad Downloads cleanup.

## Acceptance
- Only an explicitly authorized, newly downloaded file already isolated under the project candidate `_qc_temp` directory can be adopted. Require a pre-download baseline, exact source match, hash and UI mapping receipt.
- At most one registered disposable copy remains pending. Existing user files and approved assets are never adopted or trashed.
- Cleanup requires a persisted source/hash-bound report specifying review method, findings, unverified checks and disposal approval. A failed bounded review may end early; this is not whole-video PASS.
- Dry run by default. Apply rechecks ownership, file hash, report and authorization before calling the existing registry Trash journal. Repeat calls are idempotent; no empty-Trash action.
- Extend the existing reviewed deployment tool only for explicitly named new managed files; reject existing live targets and preserve unrelated live/source drift.

## Verification
Targeted negative/positive unit tests, actual one-clip lifecycle, syntax and diff checks, scoped deployment preflight/apply/hash check. Full production playback/audio and full bundle deployment are separate and not implied.
