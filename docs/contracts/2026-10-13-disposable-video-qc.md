# Disposable video QC (explicit opt-in)

## Scope
Provide a deterministic, single-owner local lifecycle for newly downloaded QC copies: receipt/authorization → registry ingest → bounded review report → verified Trash move; with recorded explicit permanent-QC authorization, delete only that journal-owned Trash copy. No downloader, watcher, automatic perception, cloud mutation or broad Downloads/Trash cleanup.

## Acceptance
- Only an explicitly authorized, newly downloaded file already isolated under the project candidate `_qc_temp` directory can be adopted. Require a pre-download baseline, exact source match, hash and UI mapping receipt.
- At most one registered disposable copy remains pending. Existing user files and approved assets are never adopted or trashed.
- Cleanup requires a persisted source/hash-bound report specifying review method, findings, unverified checks and disposal approval. A failed bounded review may end early; this is not whole-video PASS.
- Dry run by default. Apply rechecks ownership, file hash, report and authorization before calling the existing registry Trash journal. Repeat calls are idempotent; no empty-Trash action. Permanent cleanup requires independent project-scoped approval, exact Trash journal/path/hash/report binding, single-link regular file, and persisted delete intent before unlink. Recovery never deletes an unrecognized or changed path. Preserve metadata and do not claim physical disk-space recovery from file deletion.
- Extend the existing reviewed deployment tool only for explicitly named new managed files; reject existing live targets and preserve unrelated live/source drift.

- A valid approval for this narrow class is reused without per-file confirmation; routine approved production uses the existing execution owner. New surfaces and unrelated irreversible actions retain their gates.

## Verification
Targeted negative/positive unit tests, actual one-clip lifecycle, syntax and diff checks, scoped deployment preflight/apply/hash check. Full production playback/audio and full bundle deployment are separate and not implied.
