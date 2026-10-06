# Runway rendered chip serialization

Base: `7c67b505e1a0e594c4ae65e7e3a506184cc9a515`, same isolated branch.
Observed rendered DOM (2026-10-06 17:42 UTC) exposes reference/asset IDs on
noneditable Lexical chip spans, but not on uploaded slot DOM. The old innerText
reader inserts CSS line breaks and loses canonical @ tokens. Local evidence
remains private; public tests use synthetic text and IDs.

Scope: read-prompt only, strict structural canonicalization of observed image
chips. Preserve raw display, canonical text and separate hashes; reject malformed,
missing, duplicate, reordered or plaintext references. Never rewrite input or
use expected text to construct actual text. Existing paste/binding/dialog guards
and all generation gates remain unchanged. No browser execution or installation.

Content equivalence is not asset verification. Chip provider IDs are reported,
not compared with unrelated registry IDs. Without independent approved-asset
binding evidence this reader returns HOLD even on canonical content match.
Existing ordered upload receipts (approved local file hashes), current slot
load/order checks and visual enlargement review can establish a documented
operator association; this change does not automatically certify that association
or create a new bypass flag. Independent provider ID equality remains unverified.

Acceptance: synthetic regressions plus offline replay of saved DOM; configured
checks, unchanged baseline failures reported; commit/push separate branch only.

## Verification

Eight new synthetic tests PASS, 242 total Python tests PASS. Actual saved DOM
replay yields three chips and exact canonical prompt hash
`a2abe57056f45069e174a45a58ee8a5cf38c12cfd33dd130b877f9479b14bc31`.
Input evidence SHA256:
`3f461ecf1cdab2ca8a94a585157a2f79d13e2ae5832933c3ecf064f53e409920`.
The DOM adapter exercises the same serializer offline; it is not a fresh browser
observation. No provider-ID association PASS or Generate readiness is claimed.
Wrong but internally consistent chip IDs still HOLD, never authorize generation.
Repeated references currently fail closed as duplicate chips; broader semantics
need separate observed evidence and contract review.

Configured verifyFull rerun with TMPDIR/JEV_QC_TEST_TMP=/private/tmp: 489 Node
tests, 407 PASS / 82 existing Knowledge source-hash failures. An initial run
with default TMPDIR also hit existing symlink fixture restrictions. Python ran
separately; changed Python syntax, shell syntax and diff checks PASS. Downstream
parity commands did not run after Node failure; prior source/live drift remains.
No fresh browser read, live installation, cloud validation or generation ran.
