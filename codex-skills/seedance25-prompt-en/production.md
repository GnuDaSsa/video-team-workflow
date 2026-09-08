# Seedance 2.5 production branch

Use this document only for an attested package whose `provider_model` is exactly
`Seedance 2.5` and whose `provider_skill` is `seedance25-prompt-en`. Production
does not rewrite prompts.

Read `../seedance-prompt-en/aside-operator.md` for the shared exact-session binding and transaction procedure.

## One visible operator

- Use the one existing, logged-in Aside tab whose URL is the intended Runway
  session. Bind that exact tab; do not open a second Runway session.
- Do not route through Chrome, Safari, the Codex in-app browser, a connector,
  an API-credit path, a background browser loop, or another agent.
- Login, CAPTCHA, payment, account limit, or OS permission requires the exact
  user action and a blocked state. Do not work around it in another browser.

The shared implementation remains:

```text
~/.codex/skills/seedance-prompt-en/scripts/runway_ui_helper.py
```

Call it through this skill's thin 2.5 policy adapter:

```text
~/.codex/skills/seedance25-prompt-en/scripts/runway_ui_helper.py
```

The adapter changes only the required model from 2.0 to 2.5. Upload aliases,
prompt paste, same-session recovery, queue state, and foreground waits still run
inside the shared helper. If that shared helper is missing, stop with
`BLOCKED_SHARED_SEEDANCE_HELPER_MISSING`; do not invent a second procedure.

## Preflight before every Generate

1. Confirm the package and attestation are current and their hashes still match.
2. Confirm `provider_model: Seedance 2.5`; a generic or 2.0 package returns to
   its own skill.
3. Open the model selector, choose **Seedance 2.5**, close the selector, and
   freshly read the closed-control label. Memory and a previous card do not
   count.
4. Select the package mode: Reference, Keyframe, Edit, or Extend. Verify the
   visible mode rather than assuming the previous state survived refresh.
5. Attach only the ordered, approved, registry-backed sources. Verify each
   thumbnail by enlarged visible content, not filename or upload progress alone.
6. Paste the UTF-8 NFC Korean prompt file, then compare normalized visible text
   and hash with the attested prompt.
7. Reference/Keyframe/Extend: verify the exposed duration against the runtime
   lock. Edit: duration and ratio inherit the verified input video; there is no
   duration control. Record source hash + ffprobe duration as inherited evidence,
   not a fabricated visible label. If it conflicts with the runtime lock, return
   to planning for an explicit project override; do not silently change modes.
8. Reference/Keyframe expose resolution/ratio settings; Edit/Extend inherit ratio
   and do not expose the same resolution selector. Verify only controls that
   actually exist, plus source properties for inherited values.
9. Verify Audio, ratio, and other visible controls against the package.
10. Run the 2.5 settings guard immediately before Generate:

```bash
python3 ~/.codex/skills/seedance25-prompt-en/scripts/runway_ui_helper.py \
  settings-verify \
  --project <project> \
  --block <BLOCK> \
  --visible-model '<fresh closed-control label>' \
  --duration-sec <visible-seconds>
```

For Edit, the package also names the approved registered `input_video_asset_id`.
Use `--duration-source input-video --source-video <registered path>` and pass
its ffprobe duration via `--duration-sec`. The shared guard checks input hash,
video stream and inherited length against the lock (one input-frame metadata
rounding tolerance); it records `visible_duration_sec: null`. An unregistered
legacy source must be registered/approved before using this guard, not bypassed.

Any `Seedance 2.0`, missing/ambiguous model label, duration drift, stale pack,
or changed lock fails closed.

## Attachment and recovery transaction

Before `ATTACH`, checkpoint the exact current session and 2.5 settings through
the adapter:

```bash
python3 ~/.codex/skills/seedance25-prompt-en/scripts/runway_ui_helper.py \
  recovery-checkpoint \
  --project <project> \
  --block-id <BLOCK> \
  --session-url '<exact Runway session URL>' \
  --prompt-sha256 <hash> \
  --reference-manifest-sha256 <hash> \
  --reference Image1=<AST_ID> \
  --settings-json '{"model":"Seedance 2.5","mode":"Reference","audio":"ON","ratio":"16:9","resolution":"1080p","duration":"15s"}'
```

Use the actual package values; the example is not a default override. Transport
timeouts do not consume a semantic attachment retry. Use `recovery-record` and
`recovery-resolve` through the same adapter so the checkpoint cannot switch back
to 2.0 during recovery. Resume the same slot in the same session.

## Submit and queue

- One Generate click is one block transaction. Confirm the matching visible
  card before advancing.
- Do not assume 2.0 throughput merely because 2.5 is selected. Submit the next
  eligible package only while the visible board accepts it. Two distinct
  accepted cards are positive two-slot evidence; an exact capacity toast is
  one-slot evidence.
- After every accepted, changed, or completed card, use the adapter's
  `queue-cycle` with the visible board observation. It remains the shared atomic
  checkpoint controller. Continuation selection is shared with the 2.0 production
  document: persisted scheduled mode checkpoints once without sleeping; only
  selected foreground mode waits. Use the 2.5 adapter for the same commands.
- A foreground wait is not a scheduler. If the shell yields a session ID, keep
  that exact session attached until it exits, visibly re-read the board, and
  consume the wake in the same turn.
- Before any final response, run `queue-exit-check --project <project>` through
  the adapter and obey its exit code.

## Download, verify, and ingest

For every completed card:

1. Download the exact expected output from the same visible session.
2. Verify file existence and non-zero size.
3. Run `ffprobe` and record duration, container, video codec, dimensions, frame
   rate, and audio stream presence.
4. In a v4 project, ingest the actual file into the canonical numbered `media/`
   tree and registry. Lane directories remain metadata-only.
5. Map the provider card/output to the block and mark the card processed only
   after the file and registry evidence exist.

## Clip QC for reducing AI appearance

QC timing follows the shared production document’s Generation-first scheduling
priority: wait-time or post-batch review, not a per-clip prerequisite to the next
independent approved generation. The checks below gate creative approval/reuse
and delivery, not queue refilling.

Before creative PASS, compare every planned shot and the final one-second hold
against the actual video. Explicitly check subject permanence, face/body continuity,
contact/prop continuity, unintended transparency/disappearance, and required final
pose/crop. A sample showing an absent subject where one must remain is REJECT,
not PASS merely because a forbidden drone is absent. Do not claim inspected
sample times without viewing those frames. Technical file/hash/codec PASS and
creative/identity PASS are separate. Contact-sheet review cannot certify motion,
transition or audio quality; full playback remains required for those verdicts.
A user-rejected clip is HOLD for editing/reuse until the rejection is resolved;
retain the historical receipt but do not keep citing it as current approval.


Inspect full-speed playback, slow inspection around contact/transition frames,
and representative full-resolution frames. Reject or repair:

- identity drift, face substitution, extra/missing people, hand/object fusion;
- floating feet, sliding contact, weightless acceleration, impossible joint
  paths, or environmental motion that precedes its cause;
- uniform whole-frame motion, rubbery settling, texture crawl, line boiling,
  flickering shadows, or uncontrolled background warping;
- crop expansion, accidental zoom-out, camera reversals, spatial discontinuity,
  or a final frame that cannot be cut cleanly;
- duplicate/frozen frames, micro-stutter, 1-frame flashes, bad handles, or
  optical-flow artifacts;
- synthetic dialogue/lipsync, unwanted music, broken diegetic timing, or an
  absent audio stream when the package requires one.

Route a localized defect to **Edit**, a continuation need to **Extend**, an
endpoint problem to **Keyframe**, and a source/identity conflict back to
**Reference** prompting. Change one diagnosed variable per revision and keep a
revision receipt. Do not hide a failed source with random transitions or call a
technically polished identity change a pass.

## Capability evidence

Mode-specific inherited controls and approximate timing were checked against
[Runway's Seedance 2.5 guide](https://help.runwayml.com/hc/en-us/articles/53542207042323-Creating-with-Seedance-2-5)
on 2026-09-06. Edit takes source length/ratio; Extend outputs new footage only.
Prompt timestamps are not frame-accurate cut points. Gray can indicate invalid
references; inspect the reason before treating it as queue saturation.
