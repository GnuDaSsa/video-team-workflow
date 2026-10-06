# Aside exact-session operator — shared by 2.0 and 2.5

This is the `local_aside` profile. Supported cloud CUA has a separate narrowly
scoped contract in `execution-profiles.md`; it must never impersonate this binding.

## A. One owner, one existing board

Aside CLI `repl` executes deterministic JavaScript. Bare `aside` and `aside exec`
start browser agents: do not use them. No `newTab`, alternate browser, hidden
upload input, API generation, extra owner or background observer.
The selected version helper consumes this contract; 2.5 does not fork it.

1. Read current project state, selected version, attested pack and current board.
2. List existing tabs with the read-only command below. For a resumed project,
   match the exact Runway session to its checkpoint; a missing/ambiguous match
   requires user selection, never a title/front-tab guess. For a genuinely new
   unsubmitted project, follow the bounded bootstrap below instead of asking
   routine permission to create a private session.
3. Bind the exact existing target. Binding stores only project-local metadata;
   it never opens a session or changes provider state.

```bash
aside repl "console.log(JSON.stringify((await listBrowserTabs()).filter(t=>t.url.includes('app.runwayml.com'))))"
python3 ~/.codex/skills/seedance-prompt-en/scripts/aside_bridge.py bind \
  --project '<absolute project>' --target-id '<verified existing targetId>' \
  --session-url '<exact https Generate URL with sessionId>'
export RUNWAY_ASIDE_BINDING='<project>/lanes/seedance/aside_binding.json'
python3 ~/.codex/skills/seedance-prompt-en/scripts/aside_bridge.py verify \
  --binding "$RUNWAY_ASIDE_BINDING"
```

`--binding <path>` may instead precede the selected helper's subcommand.
`--account` is an optional locally verified Aside account ID, not a new login.
Do not store account/session URLs in public repository evidence.

The bridge re-lists tabs, requires exactly one matching session and target,
attaches only that target, rechecks URL, and checks location again in the DOM
callback. A switched/missing/duplicated session fails closed. There is no
front-tab fallback and no Apple Events JavaScript requirement.

### New-project bootstrap is routine, not a new browser owner

Only before any binding, checkpoint, accepted/uncertain Generate or project queue:
- Use the sole existing authenticated Aside Runway tab by observed exact targetId.
  Multiple possible tabs/accounts or an unreadable UI still require selection.
- Inspect current board and composer. Do not navigate away from active jobs or
  unsaved/uncertain work. Preserve the previous exact session URL and a minimal
  composer/card checkpoint locally; do not erase, close or repurpose old media.
- If visibly idle and the prior session is safely retained, use the actual
  visible new-session control in that same tab for the requested new project.
  This needs no extra routine confirmation; it is not permission for a new tab,
  account switch, credit purchase, public upload or additional agent.
- Verify the new exact URL and empty session, register its project ownership,
  then bind/checkpoint normally before attaching anything. A failed or uncertain
  action is observed once before recovery, never blindly repeated.

## B. Observe → act once → verify, for each block

| Stage | Evidence required before advancing |
|---|---|
| BIND | exact project/target/session, one owner |
| CHECKPOINT | current attestation/prompt hash, registered deck, slots, settings |
| ATTACH | each expected modality/token mapped to approved asset; enlarged visible thumbnail verified |
| PROMPT | unique visible Lexical editor; matching text is a no-write success, otherwise empty before one paste; no visible dialog; NFC content/hash equality |
| SETTINGS | fresh closed model/mode/time/ratio/audio/resolution where exposed, matched to current pack |
| GENERATE | eight-check preflight; exactly one visible Generate control; one click |
| ACCEPT | matching newly accepted provider card/output; evidence distinguishes old cards |
| HARVEST | matching file, bytes/hash/ffprobe/registry before processed acknowledgement |

Use the selected helper's `recovery-checkpoint` before ATTACH, then its
`prepare-upload-alias` for the exact registered asset/modality. Use the visible
Reference selector to open the native chooser. Computer Use may operate only
that same Aside chooser; the helper's optional native `picker-go` first requires
the exact bound tab to be active, activates Aside without input, then rechecks
the exact active tab in the focused window before macOS frontmost and IME checks.
When the native picker makes the browser focus flag false, `picker-go` alone may
instead prove the CLI-bound window ID and exact current URL against native Aside's
front window/active tab, plus that main window's `open-panel` sheet. That proof is
repeated immediately before input; an unrelated dialog or changed tab fails closed.
`picker-select --path <helper-alias>` selects one uniquely named visible file row in the
verified native ListView without keys or clipboard input; it therefore does not depend
on an English IME. A changed layout, duplicate/missing row or unapplied selection fails
closed. Re-read the native Open button and actual uploaded thumbnail before proceeding.
A short locator timeout after Open is not an upload failure: observe the same
slot again without replaying Open/upload. Capture enlarged content only after
image decode **and visible overlay rendering** settle; a blank screenshot is not
verification even when the image reports loaded.
This does not override the current controller's UI-technology or permission gates.
Verify the actual chooser before/after native input: no software check can make
OS focus atomic with a user's simultaneous click. A focus change means stop the
input and re-observe, not send more keystrokes. Never upload through hidden DOM
file inputs, clipboard images, or unapproved drag fallback.

Use the existing `paste-prompt --file <BLOCK>_prompt.txt --pack <attested-pack>`
as one bounded input transaction: pre-read, no-write `PROMPT_ALREADY_MATCHED`
when normalized text already agrees, otherwise one paste into an empty editor
and actual committed-text/hash verification. A visible dialog blocks both
acceptance and mutation; it is checked again immediately before paste. Never
append/replace different existing text or guess another editor. A successful
transaction already includes a read-back; do not repeat it mechanically without
an intervening change. An uncertain call, resume or changed UI requires
`read-prompt --file <BLOCK>_prompt.txt`, never blind re-paste. Visible counter,
hold inspection and the fresh before-Generate preflight remain mandatory.

`settings-verify` rechecks the current pack with the current validator as well
as attestation/lock hashes. It is a consistency guard, not a screenshot sensor:
operator-supplied labels must come from a fresh visible inspection. Its PASS
alone does not prove deck, prompt or all other settings. Any refresh, recovery,
wake, deck/prompt/model change invalidates the prior visual preflight.

### Resume must reconcile the composer, not only the URL

On resume, compare the visible composer prompt hash, reference count/order and
settings against the intended attested block before clearing, attaching or
Generate. The same session URL can contain another project's unsent composer.
A saved armed block is not fresh proof. Preserve the unmatched composer locally
and identify its existing package/owner without editing that other project.
Do not submit it under the current project's block ID or erase it to restore a
stale checkpoint. An unresolved ownership conflict needs exact user selection;
verified completed cards from the bound project can still be harvested without
changing the composer. This is a manual visible preflight, not an automatic
ownership detector or permission to start another operator.

### Established input steps versus semantic decisions

Prefer the existing guarded CLI/Computer Use helpers for an established action;
do not ask the model or JEV to re-decide every known paste/search/verification.
Computer Use still performs the actual UI operation. The current owner retains
prompt authoring, screenshot/identity judgment, and novel multi-step recovery.

Only when a short observed text state requires a choice between locally eligible
input actions, reuse the installed Aside decision module (not its native UI or
Astra/language policy): `node ~/.aside/u/0/skills/user/aside-video/scripts/jev-dispatch.mjs
route --root <same project> --input <anonymized-state.json> --kind semantic
--observed-at <actual ISO observation> --jev-approval <current-scope approval ref>`.
Input/output/approval/triage details are owned by that module and its adjacent
`references/jev-dispatch.md`. If unavailable or unapproved, reason in this owner
without installing/starting a replacement agent. Do not pass author context.
The decision module never runs a browser, changes models, or authorizes execution.

Consume only its candidate action, then revalidate the existing exact-session,
reference, prompt and settings gates. Keep selectors, paths and immutable pack
text local. Never feed raw snapshots/media/private account data to JEV. Do not
use native `runway-fastlane.js` to bypass this Codex operator's paste/native
chooser restrictions. Generate, publication/payment, quality PASS and new owner
creation are outside this router; an existing runtime recovery rung takes
precedence over semantic advice. No second loop, automatic retry or scheduler.

## C. Uncertainty is not permission to repeat

- Missing marker, CLI timeout or tab mismatch: no alternate route and no blind
  replay of a mutating call. Reconnect to the same target, observe its state,
  then use the recovery controller's returned next action.
- A click without a matching new card is `ACTIVE_CLICK_NO_CARD`. Read cards and
  toast; keep block/cursor unchanged. Never click the same pending transaction
  twice merely because the first tool returned an error.
- Gray means not eligible *now*, not necessarily queue full. Inspect exposed
  error/tooltip and current active cards. Input/reference errors return to the
  affected attachment/settings step; active-card capacity uses `queue-cycle`.
  Record an actually observed queue-capacity toast as
  `RUNWAY_QUEUE_CAPACITY_TOAST`, or the Generate control's explicit capacity
  tooltip as `RUNWAY_QUEUE_CAPACITY_TOOLTIP`; never relabel one as the other.
  Keep the exact message and current active-card count in local evidence.
  Gray alone, an absent tooltip, or an input-error tooltip is not capacity proof.
  These operator-supplied labels are not automatic UI detection and never
  authorize Credits Mode. Empty queues retry the normal target instead of
  turning one temporary restriction into a permanent account limit.
- Login/CAPTCHA/payment/account/permission: record the exact human action and
  stop that control operation. Never try a bypass or another account/browser.
- Record outcome/evidence and next step in project `status.json` / `result.md`.
  Redact prompt bodies, account URLs and unrelated browser data from release logs.
- Before any binding or Generate, unresolved session ambiguity or unsafe bootstrap is a preproduction
  user-action block, not a queue. Record `production_started=false`, empty
  `provider_jobs`, all held `blocked_attested_blocks`, and `preproduction_block`
  with code `BLOCKED_RUNWAY_SESSION_SELECTION_REQUIRED`, evidence and the exact
  `required_user_action`. `queue-exit-check` accepts this only without any queue,
  binding, recovery or settings-preflight evidence. Never fabricate a board sync
  or use this state to abandon a started/uncertain transaction.

### Rendered image-chip readback (source-only update)

`read-prompt --file` serializes the observed noneditable Lexical image chip
structure to canonical `@ImageN`; it retains `raw_display_text`, `canonical_text`,
both hashes and observed provider IDs in local evidence. CSS line breaks inside
chips are not authored paragraph breaks. Plaintext tokens do not count as chips.
Unknown structure, duplicate slots/assets and missing/reordered tokens fail.
This version is intentionally conservative about repeated chip occurrences.

`content_match=true` only proves canonical text equality. Chip reads still return
nonzero `HOLD_ASSET_BINDING_UNVERIFIED` because an ID on the chip alone cannot
prove the approved file association. Do not interpret local registry IDs as
provider IDs or use the canonical hash as Generate approval. Review the existing
ordered upload/file-hash receipts, current loaded slots and enlarged images in
the exact session. The observed slot UI has no independent provider ID; report
that limit honestly. This source change does not automate association approval,
change paste, migrate a live transaction, or authorize another browser route.
See the repository contract `docs/contracts/2026-10-07-runway-chip-serialization.md`.

### Compose the existing visual association check with chip readback

The ATTACH row above and production preflight checks 3/4 already define the
operator's visual approved-reference verification. Independent provider ID equality
is not a requirement of that visual path. It must not be claimed when slot DOM
exposes no ID. The conservative reader's raw HOLD is retained; a separate operator
assessment may satisfy the reference association check, never tool authorization.

For the unchanged exact session and block, the sole authorized operator records
an append-only entry in `lanes/seedance/local_operator_evidence.jsonl` and links it
from project `status.json` / `result.md`. Use action
`reference-association-review`, verdict `PASS_OPERATOR_VISUAL_ASSOCIATION` only
when all following evidence has actually been inspected (otherwise `HOLD`):

- Operator identity, actual review time, project/block, exact target/session and
  current pack/prompt/reference-map hashes; no session/account substitution.
- Each ordered slot: token, approved registry ID, original file hash, actual
  upload receipt locator and upload order. Confirm that file is still approved
  and its bytes still match. Alias preparation alone is not completed-upload proof.
- For each slot: actual enlargement observation time and raw screenshot or tool
  observation locator, approved original comparison locator, concrete comparison
  result and reference role. A filename, loaded flag or unsupported recollection
  alone is insufficient. Do not manufacture missing image observations.
- Fresh current slot count/order/load state, observed chip order/provider IDs,
  structural readback's canonical content/occurrence match, plus raw readback
  path/hash. IDs must equal the IDs recorded at the reviewed deck checkpoint;
  changed/missing/duplicate IDs, slot changes or uncertain continuity require
  fresh visual review. Preserve raw display and canonical representations.
- `verification_method: ordered_upload_and_visual_comparison`,
  `independent_provider_id_match: false`, and
  `execution_authorized_by_receipt: false`. Keep the raw helper's
  `asset_binding_verified:false` and `HOLD_ASSET_BINDING_UNVERIFIED` unchanged.

This is an evidence record, not a software-authenticated visual verdict. Do not
manufacture a JSON boolean to replace the operator's actual review. Earlier
same-session enlargement evidence can be reused only with observed unchanged
composer/deck continuity; resume/refresh/recovery/wake or any uncertainty invalidates
it as described above. Review again when continuity cannot be established.

Existing checks remain the normal commands below; these are for the sole operator
to run in its permitted environment, not permission to start another controller:

```bash
python3 "$SOURCE/codex-skills/seedance-prompt-en/scripts/aside_bridge.py" verify \
  --binding "$PROJECT/lanes/seedance/aside_binding.json"
python3 "$SOURCE/codex-skills/seedance-prompt-en/scripts/runway_ui_helper.py" \
  --binding "$PROJECT/lanes/seedance/aside_binding.json" \
  --evidence "$PROJECT/lanes/seedance/local_operator_evidence.jsonl" \
  read-prompt --file "$PROMPT_FILE"
python3 "$SOURCE/codex-skills/seedance-prompt-en/scripts/runway_ui_helper.py" \
  --binding "$PROJECT/lanes/seedance/aside_binding.json" \
  --evidence "$PROJECT/lanes/seedance/local_operator_evidence.jsonl" \
  settings-verify --project "$PROJECT" --block "$BLOCK" \
  --visible-model 'Seedance 2.0' --duration-sec "$OBSERVED_DURATION"
```

`SOURCE` is the reviewed checkout and existing runtime dependencies must resolve;
these commands do not install it. Preserve each exit status and raw output.
Do not use `|| true`, change the raw HOLD to PASS, or chain Generate on exit zero.
Only the exact asset-association HOLD with both content/occurrence matches can be
paired with the separately evidenced operator association verdict. Any different
error still blocks. There is no new CLI command that performs visual judgment.
Do not use `recovery-resolve` merely to record this review or clear unrelated holds.
Complete all eight fresh production checks and the current continuation scope
before the existing one-click procedure; this record alone never permits Generate.
