# Seedance explicit English request support

## Scope and decision
Fix the hard-coded Korean-only validator/paste path that contradicted the
existing rule that explicit user settings override defaults. Korean stays the
default. English is permitted only for named blocks with a hash-bound explicit
user-request record in that project's docs directory. This is input-language
support, not a policy-rejection workaround or a diagnosed provider fix.

## Acceptance
- Default Korean packs still reject English text.
- English requires project/block-scoped evidence, matching style/contract,
  unchanged attestation and prompt/file hash.
- Language change preserves reference binding, duration, shot timeline,
  character limit, semantic and live settings gates.
- Production uses the same existing Aside owner, no extra agent/scheduler.

## Verification and evidence boundary
- 167 unit tests PASS, including 8 English scope/paste/default/malformed/CLI tests.
- Python compilation, shell syntax and git diff whitespace checks PASS.
- Allowlisted release freeze/preflight/apply/check PASS; 67-file parity.
- Live: two English packs attested; exact Lexical hashes, seven enlarged
  references and Seedance 2.0 / 15s controls verified; two distinct new cards
  accepted in the same visible session. No additional Generate retries.
- New output files and temporal/creative QC are NOT verified. Acceptance is not
  completion, and English is not established as a fix for provider moderation.
- Initial test fixture errors (project identity and macOS resolved path) were
  corrected. First CLI invocation exposed a missing --pack parser declaration;
  it was fixed and regression-tested before the two actual submissions.

## State ownership
The pre-existing blocked harness goal belongs to a different production-resume
contract and is preserved. This bounded correction is a separate closeout.
