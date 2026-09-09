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

## Continuation selection: scheduled means short scheduled checks

The user's standing video-team preference is **scheduled production continuation**,
not continuous foreground supervision. This common procedure applies to every
Seedance project (2.0/default and the 2.5 adapter), not just the project that
exposed the failure. Use 20-minute checks unless the user specifies 15 minutes
or another interval. An explicit foreground request overrides this preference.

Select scheduled mode before the first queue drain. Reuse an existing matching,
authorized native registration; a new scheduler surface still needs its specific
approval under the spawn policy. Do not ask again for routine checks on that
approved schedule, silently fall back to foreground, or claim registration when
only a local preference exists. If creation approval is missing, report that exact
missing step once rather than pretending continuation is armed.

The shared behavior follows the generation-first priority below, with the
post-Generate gate preserving follow-up rather than blocking on clip QC.
Keep only run data (project/task/job IDs, native receipt, last observation,
next due/action and completion scope) in existing project state. Never copy this
procedure into a project-specific reconciliation JSON or wrapper. Existing user
request/task evidence is sufficient; do not manufacture another evidence note
just to restate this standing preference. Persist mode using the existing helper:

```bash
python3 ~/.codex/skills/seedance-prompt-en/scripts/runway_ui_helper.py queue-mode \
  --project <p> --mode scheduled --interval-minutes 20 \
  --request-evidence <project-local-user-request-note>
```

This command creates **no scheduler and grants no spawn approval**. The
hash-bound selection survives model/turn changes. A live foreground wait must
first be stopped and its owning tool result consumed. The next fresh board
`queue-cycle --from-wake` clears any interrupted wake without sleeping.

In scheduled mode, `queue-cycle` records one board observation and immediately
returns `SCHEDULED_CHECKPOINT_NO_WAIT`. Direct `queue-wait` is rejected. Do not
hand-edit queue flags to escape the foreground branch. A corrupt/changed mode
receipt fails closed rather than falling back to a 15-minute sleep.
Existing native `kind: heartbeat/cron, status: ACTIVE` records also express
scheduled intent: repair a missing mode checkpoint from the original request,
not by restarting foreground waits or asking for the same approval again.

Use the native app automation tool after the **specific surface approval**;
inspect a matching existing automation before proposing/creating another.
Prefer one current-task heartbeat, 15–20 minutes as requested. Do not revive an
unrelated old cron, guess a task ID, write raw scheduler config, or run both
foreground and scheduled owners. If only a proposal card is returned, record
`PROPOSED`, not `ACTIVE`; do not repeatedly ask at each run after initial approval.

Capture registration ID, accepted cadence, destination, active/paused state and
native tool evidence separately from first-run evidence. Heartbeat model choice
may inherit task settings; do not claim Luna execution from a routing table.
A local mode file never proves registration, browser access or successful runs.

Declare the reservation's purpose: **observe-only** or **production continuation**.
An observe-only heartbeat on a review task cannot wake an idle production owner
and must never be presented as automatic production. Before ending with active
jobs, verify which exact existing task will consume the next scheduled check.
"Waiting" in a final answer is not a continuation mechanism.

When the user authorizes continuation through an existing review heartbeat, keep
the production task as the sole UI owner. The review heartbeat may send one
bounded resume message to that existing verified-idle task, never to an active
task or one held by the user or a verified safety blocker. Persist a pending
handoff before sending; receipt is delivery, not execution. Require a new owner
turn plus a fresh provider/artifact checkpoint before another handoff. Missing
consumption means pause and report once, not another identical message. After
three consumed checks without material progress, pause and report stalled
continuation without inventing a provider failure. A timestamp-only update is
not progress. Never add a second scheduler or take over the browser to repair it.
Verify actual native PAUSED state before claiming that monitoring stopped.

### Direct executor handoff, not instruction relay

For an authorized existing-owner check, use the shared runtime
`runtime/scripts/model_routing.py` existing-owner handoff builder. Provide
`--manager-id`, `--owner-id`, freshly observed `--owner-status idle`,
`--phase production|prompting`, and a bounded `--action`. It returns the native
send-message payload, never sends it. The manager calls the native tool once
with that payload after normal approval/HOLD checks; the builder itself grants
no authorization. Unknown/notLoaded is not proof of idle. For a fresh, explicit
user request to resume an existing unloaded task only, keep `--owner-status
notLoaded` and provide `--explicit-resume --latest-turn-status completed
--latest-turn-id <UUID>` from a fresh native read of the latest turn. Record the
user request and observation in existing pending state. This exception never
applies to automatic due checks, active/unknown states, old cached completion,
or unresolved HOLD/safety blocks. Completion proves a turn boundary, not media
progress; verify actual tools after delivery as usual.

The recipient is the executor; the sender remains manager. Execute the requested
board/file/prompt work in the receiving task. Do not send the instruction back,
ask the manager to operate the browser, or wait on the manager instead of doing
the work. Return actual results through existing lane state and the receiving
task's final answer. Routine result delivery does not need another cross-task
message or another monitor. This distinction survives model changes.

The manager retains the exact outgoing prompt in existing pending-handoff state.
An exact or whitespace-only echo (including the full request quoted in a reply)
is rejected using `model_routing.is_instruction_echo`; no reciprocal send and no
consumed acknowledgement. A non-echo is still NOT execution evidence: verify
fresh actual tools/artifacts. If execution is absent at the next scheduled check,
pause the same automation and report recipient-role inversion once. A completed
turn, self-written result, or claimed forwarding does not substitute for action.

### Generation-first scheduling priority

Unless the user explicitly requests a per-clip review gate, generate the planned
approved batch first. At each short scheduled check, read the board and refill
available capacity with the next eligible, attested package BEFORE lengthy QC.
Use the selected version's actual capacity rules; this is not agent concurrency.
Save completed media promptly to candidate storage and verify file identity so
it is not lost or misassigned. Candidate registration is not creative approval.

During provider waiting time, the same owner may QC downloaded candidates in
cut order. If QC cannot finish before generation work is due, checkpoint the
backlog and prioritize the next generation action. After initial generation is
finished, review all remaining candidates from the first unreviewed cut onward.
Do not pause a project because an unrelated previous clip is not yet QC-passed.
A failed clip goes on the repair list without blocking independent approved
shots. Do not trigger an endless repair loop before completing the initial batch.

Keep QC before approved-media promotion and final edit/delivery, not between
independent Generate submissions. Prompt/identity/reference/settings checks,
actual source dependencies (a later clip using an earlier video), safety failures,
and explicit user HOLD still gate the affected submission. This priority does
not bypass source-image QC or permit reuse of a rejected source. Never infer
project-wide HOLD from a single creative defect unless it affects shared inputs.
Project generation complete and QC complete are distinct states; the existing
schedule remains responsible for the QC backlog within its authorized scope.

### Post-Generate continuation gate

A successful Generate is not a safe terminal checkpoint. Before ending a
scheduled production turn, persist `scheduled_followup` with the exact job/scene,
acceptance evidence and observation time, `due_at`, existing automation ID,
consumer task ID, next action, and terminal condition. Verify native registration
covers that consumer and purpose. If the existing approved schedule is absent or
paused, repair that same registration through the native tool; never merely
promise to wait. A missing executable follow-up is `CONTINUATION_NOT_ARMED`, not
production running or complete. Do not click Generate again to repair scheduling.

For project-wide continuation already authorized by the user, the next action is
check accepted jobs -> submit the next eligible approved package when capacity
opens -> harvest completed candidates -> use waiting time for QC. Advance the
exact scene scope inside that same authorized project;
finishing one clip does not end the project schedule. For an explicitly
single-scene/observe-only schedule, stop at its declared terminal scope instead.
Do not pause at provider COMPLETED when download/QC is still in that scope.
No new scheduler or renewed routine approval is needed for an existing approved
project continuation schedule.

At each due check, consume one actual board observation, not a continuous watch.
Set the next due time from the real acceptance/pending observation plus the
approved 15-20 minute interval. Execution occurs on the first heartbeat at or
after due, not at a guaranteed exact second. An idle owner is woken once; an active
owner is never given competing UI commands. Require fresh execution evidence
within one check interval after delivery even if app metadata stays active;
otherwise pause the exact registration and report `EXECUTION_UNVERIFIED` once.

App active, a new turn ID, file mtime and a saved plan are not evidence of current
production. Compare embedded observation time with original tool/capture evidence
or an independently verified new artifact. Late-written old observations remain
historical; inconsistent times are `STALE_OR_INCONSISTENT_EVIDENCE`. Report app
state, last verified production observation, and media/QC status separately.
Never certify full playback QC from file hashes or owner text alone.

A live production owner or verified login/permission/CAPTCHA/account blocker means
no competing UI action. Codex usage-limit errors are observation execution
failures, not proof of Runway failure. No sleep, extra agent, second browser loop,
or resubmission of accepted jobs. Verify native PAUSED before reporting a stop.

`queue-doctor` also returns a read-only state audit: stale lane/queue rollups
(including nested current rollups after cards have been processed),
unsupported scheduling claims and DONE-without-local-video evidence. It does
not query the scheduler or certify playback. Fix active state in place from
fresh evidence; keep historical failures in logs, not active blocker fields.

## Foreground branch (only when selected)

Start/resume, a model change, or a disputed "monitor is running" claim first
uses `queue-doctor --project <p>`. This read-only command reports the canonical
helper hash, queue/timer/elapsed-consumption evidence and next action without
opening a browser, waiting, writing state or starting a scheduler. A live wait
PID is not proof that the owning exec tool session remains attached; never pass
that PID as a `write_stdin` session ID. The same state uses the same controller
under Luna, Terra or Astra. Record actual missing-tool/permission/version/session
evidence instead of diagnosing a model limitation from its name.

In this foreground branch, after every accepted/changed/completed card, use **`queue-cycle`**, not separate
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
  Repeating that authorized same-owner wait does not require another approval.
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

### Foreground is not scheduled

The foreground helper never registers a future task. Use the continuation
selection section above for actual app scheduling; do not substitute this loop
when the user requested scheduled checks.

## Download and completion

Download the exact matching output from the same board. Verify path, bytes,
SHA-256, duration, container/codec, dimensions, frame rate and audio presence.
Provider filenames may share the same style-lock prefix; do not map outputs by
filename alone. Preserve card-to-block evidence (provider asset ID when exposed,
or verified same-session card lineage) before renaming local files. Never call a
local prompt fingerprint a provider UUID.
V4 media is ingested into `media/06_videos_candidates_영상후보/` and registered
before processed acknowledgement and Seedance QC handoff. A card without a
verified file remains `UI_ONLY_NOT_DOWNLOADED`.

Playback QC is separate: identity/crop, anatomy, contact/weight/inertia,
texture/line stability, temporal seams, freeze/jitter, sound and usable handles.
Timestamps express intended pacing; approve actual cut intervals only after
playback. Technical file verification alone is not a creative PASS.
