# Production card — released shelf blocks (P5)

This card is the whole procedure for producing released preprod shelf blocks.
It replaces reading `SKILL.md`, runtime `AGENTS.md`, `aside-operator.md`,
`seedance-production.md`, helper source or `--help`, and the wiki during P5.
Open one of those only when a STOPPED result names it. Every extra read is
re-sent with every later step; that, not Runway, is what made a block take 40 min.

P5 runs in its own **lane session** started by the director (`video-codex-runtime
dispatch --lanes seedance`), at most 2 blocks per session (Runway runs two active generations per
account; the session gets only the free slots); never in the long director thread. Write notes once, at the end of the batch, not between blocks.

`H` = `python3 ~/.codex/skills/seedance-prompt-en/scripts/runway_ui_helper.py`

## Once per batch
1. `video-codex-runtime next --project <p>` → `seedance`, `OK_PRODUCTION_COPY_PASTE_ONLY`.
2. Session tab exactly as the handoff doc says (existing bound tab, or the one
   new session it authorizes). Bind it once:
   `python3 ~/.codex/skills/seedance-prompt-en/scripts/aside_bridge.py bind --project <p> --target-id <tab> --session-url <exact url> --account <aside account, e.g. u1>`.

## Per block (B01, B02, … in order)
1. `H run-block --project <p> --block-id <B>` — one call does shelf-verify,
   upload bundle, attaches every slot from Runway **Uploads** by the ledger's
   names (never re-uploads bytes Runway holds), checks each enlarged slot,
   sets/checks settings, pastes the shelf prompt, settings-verify, preflight.
2. `READY` → view the `enlarged_screenshot` of each slot once (identity and
   environment are the approved refs). Then click the single visible Generate
   **once**, and confirm the matching new card (In queue / Generating). Then
   `H record-generate --project <p> --block-id <B> --state IN_QUEUE|GENERATING` (bookkeeping only).
   No card after a short look → `H recovery-record --project <p> --block-id <B> --incident RUNWAY_UI_STALE`; never click twice.
3. Next block. Do not re-read docs between blocks.

## STOPPED → do exactly this
| stop | action |
|---|---|
| `SLOT_NEEDS_NATIVE_UPLOAD` | Upload that one `RW_*` file into that slot via the native chooser (`aside-operator.md` § native chooser only), verify enlarged, `H record-runway-attach --path <file> --name <RW_ name> --how uploaded`, then the `next_action` command (`--from-slot N`). |
| `LEGACY_NAME_AMBIGUOUS` | Pick the row whose enlarged image is the ref, `record-runway-attach --how reused`, then `--from-slot N+1`. |
| `SLOT_IMAGE_*`, `SLOT_NOT_FILLED_AFTER_SELECT` | Remove that slot, re-run `run-block` once; twice → treat as `SLOT_NEEDS_NATIVE_UPLOAD`. |
| `SETTINGS_NEED_OPERATOR` | Set the listed controls by hand, then `run-block --start settings`. |
| `TIER_NOT_AUTOMATABLE`, credit/payment prompt | Stop the batch; ask the user. Never spend credits. |
| `SHELF_VERIFY_FAILED` | Stop that block; it goes back to P4. Never edit a released prompt. |
| `ASIDE_*`, `ASSET_SELECTOR_NOT_OPENED` | `H recovery-record --project <p> --block-id <B> --incident ASIDE_CONTROL_UNAVAILABLE` and follow its rung, then re-run. |
| `PREFLIGHT_FAILED` | Fix only the listed item, `run-block --start preflight`. |

Every run is appended to `lanes/seedance/run_block/runs.jsonl` (with seconds per run).

## After the last block of this session
Write the session result and end. Download/harvest, Seedance QC and package are
each their own later session, started by the director.
