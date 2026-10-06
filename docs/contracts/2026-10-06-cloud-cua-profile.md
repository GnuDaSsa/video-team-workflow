# Seedance 2.0 cloud CUA profile

Base: `1aaeccc71dddbbd7261c7d9650b3db25c4d61e93`, existing
`codex/workflow-change-provenance-20261006` branch. Request: make the supported
cloud CUA environment explicit without pretending it is local Aside.

## Findings and scope
The exact-session restriction prevents wrong-board mutation, ambiguous ownership,
blind retry, hidden upload and alternate-route bypass. `cmd_settings_verify`
requires Aside binding plus a live browser read; paste/native chooser/recovery
also depend on Aside/macOS. Documentation alone cannot satisfy those calls.
Keep those guards unchanged. Reuse the browser-free pack/duration consistency
function without writing an Aside settings receipt; add a separate cloud
observation checker, not a replacement browser or automatic Generate controller.
Only Seedance 2.0 Runway Multi-reference in a genuinely supported cloud CUA tool
is in scope. All other providers, local Chrome, APIs and version 2.5 remain out.

## Acceptance
- Explicit local versus cloud profile, no fallback after denial or local failure.
- Cloud checks current attestation/prompt/lock, fresh exact session observations,
  registered asset hashes, ordered slots, visible image review and actual chips,
  current model/mode/duration/ratio/audio, no uncertain prior submission or dialog.
- Observe/act once/verify with the supported tool only; tool policy and explicit
  denials outrank this document. A JSON boolean is never proof of authority/UI.
- Good/bad fixtures cover stale/tampered/missing and unsupported/denied evidence.
- Exact tracked-file export list includes root harness config/state/active contract,
  decisions/memory/protocol and required source. No local dirty/installed files.
- No live generation, deployment, account change, merge or PR.

## Limitations
Cloud tool availability, actual tool evidence, rendered chip semantics, upload,
submission/recovery and generated media are unverified in this local environment.
An offline consistency PASS is explicitly not authorization or live verification.
The local and cloud profiles cannot be mixed on an in-flight transaction.

## Verification and delivery limits

- 228 Python tests PASS, including 11 new profile/export tests. Tested current
  attestation/lock/knowledge changes, incorrect slots/assets/chips, stale/future
  observation, unsupported surface/settings, explicit denial and unknown states.
  Positive fixtures do not call a browser or write an Aside receipt.
- Python compile, shell syntax and `git diff --check` PASS.
- Configured verifyFull was invoked with real-path temporary directories and
  task-local Python cache. Node remains 407/489 PASS, 82 source-hash-drift failures;
  unchanged Node code and the prior direct base/head comparison establish the
  existing local-environment issue. Remaining Python/shell checks ran separately.
- Aside parity still fails on installed extras/changes. Codex parity now also
  reports SOURCE_MANIFEST_DRIFT caused by these intentional source edits, in
  addition to existing live mismatches. No release freeze or deployment is
  performed; this is not a deployable parity PASS.
- Root and runtime harness pointer files are now tracked. Export reads only an
  explicit commit, validates the configured harness closure, emits exact files
  and hashes, and rejects missing dependencies. Tests prove dirty/untracked
  files are excluded and repeated exports are byte-identical.
- Actual source archive hash and remote HEAD are reported after committing.
  Source bundle installation, cloud CUA availability/live UI, chip serialization,
  paid generation, recovery execution and video QC remain UNVERIFIED.

The initial cloud implementation intentionally accepts only image references and
Seedance 2.0 Multi-reference/Audio On/16:9 or 9:16. No general tool/provider grant.
If live chip serialization prevents exact attested-prompt equivalence, stop;
this implementation never blesses a string replacement as binding verification.
