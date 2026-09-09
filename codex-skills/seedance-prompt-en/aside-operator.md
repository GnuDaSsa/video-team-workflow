# Aside exact-session operator — shared by 2.0 and 2.5

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
| PROMPT | unique visible Lexical editor; empty immediately before one paste; NFC content/hash equality |
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

Use `paste-prompt --file <BLOCK>_prompt.txt` once, then `read-prompt --file <BLOCK>_prompt.txt` for a non-mutating exact content/hash comparison and visible
counter/hold inspection. Non-empty or ambiguous editor is a repair state, not
permission to append, use `--replace`, or inject text into another field.
An uncertain paste call is followed by a read, not another paste.

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
