# Native video workflow lean pass

## Goal
Remove repetitive instructions and model-facing output bloat exposed by the recent five-person/five-drone production session.

## Scope
- Replace the long always-read entry with stage-scoped instructions, one source per rule.
- Remove per-turn full reference/status rereads and mandatory Jev choreography; keep Jev available only for real ambiguity.
- Default CLI output to compact machine-readable verification metadata; offer an explicit full/debug output and a bounded author-task view. Keep programmatic APIs and existing files/hashes compatible.
- Preserve Astra/English/knowledge/source/reference binding, live mode/session/modal gates, duplicate-submit prevention and honest QC.
- Preserve media, logs, raw wiki sources, old receipts, existing legacy projects and unrelated dirty changes.

## Acceptance
- Quantify source document characters and representative CLI stdout bytes before/after, not imaginary token or latency gains.
- Existing regression suites and legacy receipts still verify; malformed CLI options cannot bypass validation.
- Native source/install parity. No new provider generation or destructive data cleanup.

## Result

- Recent five-person/five-drone session was inspected with streamed aggregation: 2,150 records, 112 large media rows skipped, 43 inspected text outputs above 12k characters. These are overhead indicators, not a claim that every call was wasted. User corrections repeatedly concerned true Astra use, airborne flight and object/background consistency; corresponding protections remain.
- Instruction characters: 56,726 to 13795; entry alone 14,464 to 2,247; account-global video entry 2,161 to 615.
- Removed duplicate policy prose, per-turn whole-document/status rereads, mandatory Jev choreography, unrelated examples/experiment diaries, and stale release history from active repository state (history remains in Git).
- Compact CLI request stdout: synthetic fixture 9,808 to 1,256 bytes. Existing real payload verify stdout: image 3,444 to 1,770 and video 4,012 to 1,779 bytes. Full persisted evidence and JS returns are unchanged; --full remains diagnostic-only.
- 451 native/deployer and 188 legacy tests pass; native deployment parity and prior real Astra/English/knowledge bindings pass. No new media generation, end-to-end production speed or token gain was tested. Existing legacy deployment drift remains separate.
