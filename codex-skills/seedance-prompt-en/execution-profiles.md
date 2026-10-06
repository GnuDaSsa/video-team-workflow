# Seedance 2.0 execution profiles

Select before production, after browser-free authoring. Default is
`local_aside`. The only additional profile is `cloud_cua_runway_20`: Runway
Seedance 2.0, Multi-reference, approved image references, Audio On, 16:9 or 9:16,
using the cloud environment's actually available and supported CUA browser tool.
An explicit request to operate in that supported cloud environment selects it;
Aside being absent/broken on a local machine does not. Seedance 2.5, video/audio
input, Edit/Extend, other providers/modes/settings have no cloud adapter here.
Unsupported cases stop; do not silently change the user's requested settings.

This changes execution transport, not permission. Tool/system restrictions,
explicit review denials and user scope remain authoritative. Never retry a
rejected action through a different tool, browser, API, direct network request,
login/account, hidden input or fabricated receipt. Local Chrome/Safari/in-app
fallback, headless browser, CDP/Playwright sidecar, private endpoint and proxy
routes remain prohibited. No new browser owner, observer, agent or scheduler.

## Local Aside (unchanged)

Use `aside-operator.md`, exact target/session binding, existing helper
`settings-verify`, paste, native chooser and recovery controller. All existing
Aside-only errors still fail closed. Never set `RUNWAY_BROWSER` to cloud or
manufacture `aside_binding.json` for cloud observations.

## Supported cloud CUA

Only the tool's documented visible-UI capture and element targeting/input
capabilities may operate the existing visible Runway tab. Follow that tool's
own interaction and upload documentation; this profile grants no additional API,
JavaScript evaluation, filesystem upload or coordinate capability. A visible
Reference selector/chooser and approved file-selection capability must exist.
If any required control cannot be reached within supported tool capabilities,
record `BLOCKED_CLOUD_CAPABILITY_UNAVAILABLE`; do not find a hidden alternative.

1. Verify actual tool availability and the user's project/action scope from
   trusted context. Read visible UI, bind its real tab/session handle to the exact
   Runway URL, preserve prior work. Ambiguous ownership or an in-flight local
   transaction requires reconciliation, not implicit profile migration.
2. Use the unchanged workflow pack/attestation and shot review. In that pack add
   `execution_profile=cloud_cua_runway_20`, `cloud_session_checkpoint` containing
   the observed `tab_id` and exact `session_url`, ordered `cloud_reference_deck`
   entries (`token`, registry `asset_id`, `sha256`), and
   `cloud_expected_settings` (`model`, `mode`, `duration_sec`, `ratio`, `audio`,
   plus actual exposed settings such as `resolution`). Keep this private in the
   project. Reattest after any pack change. Do not store session/account data in
   the GitHub source bundle. Profile fields cannot replace existing gates.
3. Before each attachment preserve a project-local checkpoint with the exact
   pack/prompt/lock hashes, approved registered deck and actual slot state. Use
   the visible Reference UI; inspect each enlarged rendered image against its
   approved asset, role and slot. Filenames/progress bars alone are insufficient.
4. Paste the attested NFC prompt only into the unique visible empty editor, or
   accept an already matching editor without a write. Preserve a foreign/different
   composer; no append/replace or blind re-paste. Bind references through the
   supported visible `@` selector and verify the actual asset-bound chips and
   their roles. Preserve literal UI serialization (e.g. `@Image 1`) as evidence;
   text normalization alone cannot prove chips. If exact prompt equivalence
   cannot be established alongside chip semantics, stop for a scoped adapter
   revision; this change does not implement an untested serializer.
5. Immediately before Generate, re-read the exact session, approved images,
   slots/chips, full prompt, closed Seedance 2.0 label, duration lock, mode,
   ratio, audio and every exposed output setting. Confirm no dialog/denial,
   prior accepted/uncertain transaction or reference error; exactly one visible
   eligible Generate control. Apply all eight production preflight checks.
6. Save one observation in existing local evidence with `execution_profile`,
   `environment=cloud`, `tool_surface=supported_cloud_cua`, `block_id`,
   timezone-aware `observed_at`, exact `tab_id`/`session_url`,
   `session_matches_checkpoint`, `pack_sha256`, `visible_prompt_sha256`,
   `denial_present`, `dialog_present`, `prior_submission=none`,
   `generate_eligible`, `settings`, and ordered `reference_deck` entries.
   Each deck entry has `token`, `asset_id`, `sha256`, `role`,
   `enlarged_image_verified`, `asset_bound_chip_verified`, `chip_evidence`.
   Include actual tool-result references in `tool_capability_evidence`,
   `user_scope_evidence`, `visible_ui_evidence`, `chip_binding_evidence`.
   These are pointers to evidence, not a substitute for reading it.
7. Run the cloud checker below. It reuses the current compiler/attestation/model/
   duration-lock validation and checks observation consistency/freshness. It
   does not observe UI, authenticate tool evidence, authorize a click or create
   an Aside receipt. An operator must separately verify the referenced actual
   tool results. Both the live checks and offline check are required; no boolean
   or `PASS_OFFLINE_CONSISTENCY_ONLY` is standalone permission to Generate.
8. Only within the already authorized production task, act once and verify the
   matching new card. On timeout/uncertainty, re-observe the same tab and record
   the unresolved transaction; never repeat Generate or migrate profiles. Resume
   requires fresh observations and composer ownership reconciliation. No automatic
   cloud recovery controller is implemented; unsupported recovery remains blocked.
   Queue/continuation intent, download/hash/codec/registry and full playback QC
   obligations remain. No local timer/file proves cloud scheduling or completion.

```bash
# Source-bundle root; exact paths, no installed-skill fallback needed.
export VIDEO_TEAM_RUNTIME_SCRIPTS="$PWD/runtime/scripts"
python3 codex-skills/seedance-prompt-en/scripts/cloud_cua_preflight.py \
  --project <project> --pack <current-attested-pack> --observation <local-evidence>
```

Every UI change, recovery, wake or tool reconnect invalidates old observations.
The checker accepts at most 120 seconds of age; even within that window any UI
change requires a new read. Reuse neither profile's receipts as the other's.
Capability absence, login/CAPTCHA/payment/account restrictions and explicit denial
stop the affected operation and identify the needed user action. Never click
Generate merely to test this profile. Local fixture PASS is not cloud live PASS.
