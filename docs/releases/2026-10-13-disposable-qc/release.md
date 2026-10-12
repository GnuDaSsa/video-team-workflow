# Opt-in disposable QC copies

- Added deterministic exact-file register/review/Trash lifecycle, no downloader, watcher, permanent deletion or auto-PASS.
- Installed script and QC template via reviewed scoped preflight/apply. Deployment helper supports explicit new managed files only when live target is absent, and treats already-identical live/source edits as common context. Unrelated live edits remain untouched; conflict and reverse checks remain fail-closed.
- Verification: 253 local unit tests PASS (10 lifecycle, 6 scoped-deploy cases); runtime Python compile, shell syntax, diff and harness validation PASS. Two installed file hashes match reviewed source. Full bundle parity/deploy not run.
- Actual local behavior: one 23,912,941-byte current QC copy registered, source-bound native-frame failure report persisted, dry run then Trash move verified by hash/path and registry. Repeat call returned ALREADY_TRASHED. No user downloads, source images or cloud video changed. Working candidate folder has no MP4 afterwards. Trash does not free disk until separately emptied; no permanent deletion occurred.
- Full-speed video and audio perception were not claimed. New 2D source jobs were accepted separately and remain pending; unit tests do not certify their quality.
- Existing local main and origin/main are divergent (4 local / 23 remote commits at inspection). Sync this isolated change on a named branch without force-push or merging unrelated edits.
