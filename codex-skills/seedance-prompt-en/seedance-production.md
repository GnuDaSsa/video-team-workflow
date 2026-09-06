# Seedance 2.0 production branch

Execute an already-authored, currently attested package. No prompt improvisation.
Exact binding and stepwise operation live in `aside-operator.md`; read it first.
Aside is the only browser owner surface. One logged-in Aside `app.runwayml.com`
Generate board per project: bind the existing Generate board in Aside through
`attachBrowserTab(targetId)`. Apple Events JavaScript is not required.

## Preflight — eight checks before every Generate

1. Correct project/block/version, current pack and attestation/lock hashes.
2. No accepted or uncertain prior Generate transaction for this block.
3. Actual visible deck count, modality and slot order match the registered map.
4. Enlarged identity/reference content matches approved assets; a progress bar
   or filename alone is not proof. Reusable identity/environment anchors may be
   shared, but not an accidentally duplicated full scene deck in standard I2V.
5. Unique visible prompt editor equals the NFC file by normalized content/hash.
6. Closed model label is **Seedance 2.0** and duration matches the runtime lock.
   Run the selected helper's `settings-verify --project <p> --block <BLOCK>
   --visible-model '<fresh label>' --duration-sec <fresh visible seconds>`.
7. Visible mode, ratio, audio and exposed output settings match the package;
   default multi-reference / Audio ON unless user/brief explicitly overrides.
8. Exact visible Generate control is blue/eligible and no reference/setting error
   or capacity toast contradicts it. Do not infer eligibility by button position
   or solely by AX disabled; blue alone does not prove the other seven checks.

15s is the runtime default; only its authorized duration lock can change it.
A closed 2.5 label is a model mismatch on this branch, not implicit migration.
Generate is one click per block transaction. Confirm the matching new card
before advancing. A stale card, thumbnail or click is not submission evidence.

## Attachment and recovery

Use `recovery-checkpoint` with project/block, exact session URL, current prompt
hash, registered reference map/hash, verified slots and actual settings before
ATTACH. Use `prepare-upload-alias`, visible Reference selector and verified
native chooser as described in `aside-operator.md`; never hidden file inputs.

Classify incidents once via `recovery-record` and execute only the returned
same-session rung; after visible success use `recovery-resolve` and resume the
same slot. The executable `SAME_SESSION_RECOVERY_LADDER` owns rung details.
Transport timeout/session disconnect consumes zero semantic attachment attempts.
Wrong/missing/rejected media gets one clean slot-only retry; cancel only that
failed slot and preserve the rest of the deck. A 100% upload is stalled only
after 90 seconds unchanged with no resulting thumbnail. A final Finder drag
requires current-conversation approval and a controller-authorized rung.
Login/CAPTCHA/payment/account/OS permissions require an exact user action.
Do not repeatedly try a failed control or switch browser to escape the block.

## One queue controller, same-turn continuation

After every accepted/changed/completed card, use **`queue-cycle`**, not separate
discretionary `queue-sync` / `queue-wait` steps. Inputs must describe the current
visible board, not a stale status file. `queue_runtime.json` is its continuation
record. A `resume-contract` file does not schedule or wake Codex.

- After the board demonstrates two distinct accepted cards, refill a freed slot
  before downloading settled backlog. A one-slot fallback needs the exact
  `Please wait for your last generation to complete` capacity toast.
- Arm the next eligible package only after the previous transaction is known.
  Gray on an empty composer says nothing about capacity. Gray on an armed
  composer may mean invalid references/settings; inspect the reason, don't
  automatically waste a 15-minute wait when no active job exists.
- Pass visible jobs using `--job 'BLOCK|OUTPUT|IN_QUEUE'` (or actual visible
  state), current `--armed`, `--next-eligible`, `--shelf-state` and
  `--generate-state`. Use `--processed-job 'BLOCK|OUTPUT'` only after actual
  download/verification/registry, so settled cards cannot block refill forever.
- `queue-cycle` checkpoints and enters its bounded 900-second foreground wait
  when required. Only one pending wait, existing turn and existing board.
  If the shell yields `session_id`, keep that exact process attached with
  `write_stdin` until it returns `WAIT_ELAPSED_RECHECK_BOARD_NOW`.
- Re-read the visible board, then `queue-cycle --from-wake`; only this consumes
  `elapsed_unconsumed`. Continue sequentially while `may_stop=false`.
- Lost tool session/user interruption is `BROKEN_FOREGROUND_CONTINUATION`, never
  a claim that a scheduler is armed. No observer/cron/heartbeat/second loop.
- After three consumed wakes showing unchanged `In queue` cards, record
  `BLOCKED_RUNWAY_QUEUE_STALLED` and the exact resume condition. Any card-state
  change resets that stall counter.
- A blocked pack is removed from the eligible shelf, not allowed to hold other
  valid packages. An exhausted shelf is not terminal while active or settled
  download backlog remains. Human-action gates stop the affected operation.
- Before final response run `queue-exit-check --project <p>` and obey it.
  `SHELF_EXHAUSTED` / `ALL_REMAINING_BLOCKED` requires empty active/backlog;
  otherwise only explicit external stall/interruption can end continuation.

## Download and completion

Download the exact matching output from the same board. Verify path, bytes,
SHA-256, duration, container/codec, dimensions, frame rate and audio presence.
V4 media is ingested into `media/06_videos_candidates_영상후보/` and registered
before processed acknowledgement and Seedance QC handoff. A card without a
verified file remains `UI_ONLY_NOT_DOWNLOADED`.

Playback QC is separate: identity/crop, anatomy, contact/weight/inertia,
texture/line stability, temporal seams, freeze/jitter, sound and usable handles.
Timestamps express intended pacing; approve actual cut intervals only after
playback. Technical file verification alone is not a creative PASS.
