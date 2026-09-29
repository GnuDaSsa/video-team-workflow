# Seedance English-default correction

## Verified cause
The active shared contract and compiler retained Korean directions as the
default, with English requiring block-scoped exceptional authorization. Following
that stale default failed to implement the user's standing English instruction.
This was not a provider restriction or an inability to write English.
The fetched 2026-09-20 native Aside contract already set English by default,
but explicitly excluded existing Codex production contracts. The current project
used that older Codex path; the owner failed to reconcile the standing instruction.

## Change
- One language owner: the shared Seedance handoff contract.
- English production directions by default; spoken Korean remains verbatim.
- Korean directions require explicit project/block/hash-bound authorization.
- Attestation, paste and fresh settings verification consume that policy.
- Preserve already accepted jobs and media; never duplicate Generate to hide a
  language mistake. Version routing and other safety/semantic gates are unchanged.

## Evidence
- Full working-tree runtime suite: 199 tests passed.
- Isolated staged-tree suite excluding unrelated changes: 198 tests passed.
- Python compilation, shell syntax and git diff checks passed.
- 16 initial reviewed file patches plus 5 consumer-cleanup patches (17 unique
  deployed files) preflighted and applied through
  tools/deploy_reviewed_patch.py. The archive records before bytes and patches.
- Installed compiler rejects an old Korean pack without explicit Korean intent.
- A second, previously unsubmitted live block was reauthored in English with a
  literal Korean male narration line. Attestation, exact pasted prompt hash,
  current model/duration preflight, and one accepted matching provider card passed.
- The earlier accepted Korean block was retained, not regenerated.

## Scope limits
This is reviewed-patch deployment, not full-bundle parity. Existing installed
runtime/operator changes and local craft references were preserved. Unrelated
working-tree changes were not included. The approved original-voice audition
clips remain provider candidates: no download, audio audition, creative PASS or
selected voice asset is claimed by this release.

## Repository synchronization boundary
Commits 57f65df and 2b7c137 were pushed to
`codex/seedance-english-default`. Remote main had newer independent work and
rejected the fast-forward push. A read-only merge preview reported conflicts in
runtime/AGENTS.md, decisions, harness state, project memory, and the existing
typography retirement contract. No merge, force push, or conflict resolution was
performed. Main integration remains outstanding; deployed local correction and
branch publication are verified separately.
