# Aside workflow: persistent English authoring and bounded preparation

## User-requested scope

Make English the default language of new image and Seedance generation prompts,
keep the existing session as executor, delegate prompt authorship to actual Astra,
and persist the current Aside workflow in this canonical repository. Jev selects
bounded next-action recommendations; the current executor operates the browser.
User-facing explanations and literal lyrics/dialogue/on-screen text retain their
requested language. Explicit task-language overrides must be recorded, not inferred
from Korean conversation. Existing completed media and old signed/hashed handoffs
are not translated or rewritten.

## Acceptance

- New Astra requests carry an English-default language contract and explicit
  override/literal metadata; sealing and provider-input preparation validate it.
- Legacy evidence remains inspectable, but is not silently promoted into a fresh
  language-validated submission. A script check is not semantic proof of English.
- Account entry rules make new tasks and follow-up edits reload the current Aside
  skill. Native Astra evidence and unchanged payload gates remain mandatory.
- Version the current Aside skill, Jev bounded dispatcher/classifiers, reference
  bundle and reusable-asset registry tools, and guarded browser preparation helper.
- Include a scoped deployment/check mechanism for Aside without invoking legacy
  Codex deployment or changing model categories, credentials, project assets, or
  browser state. Source/live parity must be checkable.
- Commit no media, generated prompts/receipts, session transcripts, asset registry
  entries, credentials, or private task URLs. Preserve the original working tree's
  unrelated dirty files. Push only the reviewed commit, without force.
- Run Aside regression tests, applicable configured repo checks, source/live parity,
  and diff/secret-data inspection. Report checks not run or not passing accurately.

## Compatibility boundaries

`aside-skills/aside-video` is the entry for new native Aside work. Legacy Codex
runtime/attestation files retain their existing project-specific contracts and are
not used as an alternate Korean-language owner for new Aside prompts. Existing
Codex production owners and accepted media are untouched by this release.

## Not authorized by this change

No new image/video generation, no Generate click, no language-as-moderation-bypass
claim, no automatic translation by the executor, no claimed model-speed/quality
improvement, and no daemon-level interception of arbitrary tools.

## Verification result

- Native Aside regression: 368 passing tests; deployment tool: 5 passing tests.
- Frozen 35-file native source and installed skill/managed AGENTS block: PARITY OK.
- Existing configured legacy unit suite: 188 tests pass; Python compilation and shell syntax pass.
- Legacy full deployment parity is NOT clean: its pre-existing source manifest and five managed live files differ. No legacy source/production file was changed by this release.
- New provider generation/English prompt live submission was not run. Existing test assets and receipts were not rewritten. Native tool/model behavior is a separate live validation from these code gates.
