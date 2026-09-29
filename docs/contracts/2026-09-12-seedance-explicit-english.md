# Seedance production prompt language contract

## Scope and correction
The user's standing video-team instruction is English production directions,
with spoken dialogue/narration preserved verbatim in its requested language.
The prior Korean default plus block-only English exception did not implement
that instruction. The shared Seedance handoff contract owns the corrected rule;
2.0/default and explicit 2.5 consume it. User-facing explanations stay Korean.

## Acceptance
- English packs need no per-block language permission record.
- Korean production directions require a current project/block/hash-bound
  explicit Korean request; do not synthesize one from Korean conversation.
- Attestation, prompt paste and fresh settings verification enforce the same
  policy. Existing accepted jobs/media are preserved, not resubmitted.
- Reference, duration, exact prompt hashes, semantic and character-limit checks
  remain unchanged. Language is never a moderation-bypass workaround.
- Remove conflicting active Korean-default prose, update tests, verify the deployed correction without overwriting unrelated live drift, isolate the commit from pre-existing working-tree changes.

## Live boundary
One current-project child clip was accepted under the old Korean contract before
this correction. The second clip was reauthored in English and accepted once after fresh checks. No duplicate
Generate, new owner, schedule, or claim of generated-quality PASS is authorized.

## State ownership
Preserve the unrelated blocked main harness goal; record this bounded correction
as a separate closeout. Actual verification is recorded in docs/releases/2026-09-29-seedance-english-default.md.
