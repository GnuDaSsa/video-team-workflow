# Seedance Video QC lane prompt

Role: verification phase for registered Seedance video candidates, performed by
the current owner unless a separate verifier was specifically approved.

- Accept only registered videos in `media/06_videos_candidates_영상후보/` with prompt/reference provenance.
- Verify file existence, path, size, duration, codec, resolution, keyframes/contact sheet, and mapping.
- Judge identity, reference order, motion order, directionality, anatomy/hands/objects, crop drift, unwanted text/logo, jitter, freeze, micro-stutter, flash frames, and editability to the music slot.
- Verdict: PASS, SEEDANCE_RETRY, IMAGE_RETRY, PLANNING_RETRY, EDIT_TRIM_ONLY, or DELETE_CANDIDATE.
- Whole-asset PASS promotes the same `asset_id` to `media/07_videos_approved_영상승인/` and appends its new registered path to `queues/edit_queue.jsonl`.
- EDIT_TRIM_ONLY identifies a candidate interval, **not approval of its defective parent**. Keep the parent candidate/HOLD; create and register a trimmed derivative with parent lineage, then verify that derivative before promotion.
- Failed candidates become inactive work items with a reason and are eligible only for the 24-hour Trash policy; never delete them directly.

Required outputs: per-asset verdict/evidence, promoted path or retry route, approved count, manifest update, `status.json`, and `result.md`.

## Coverage and resumable checks

Extend the **existing per-asset QC report** with a `coverage` object. Do not add a
second ledger/queue or one reconciliation file per turn. Bind `version: 1`,
`asset_id`, `source_sha256`, and `checks`. Each check contains:

- stable `check_id`, `range_seconds: [start, end]`, and `method`:
  `samples`, `native_frames`, `full_speed_video`, `audio`, or `user_audio_approval`;
- `status`: `pending`, `resolved`, or `blocked` (blocked requires `reason`);
- after actual observation: `outcome: pass|fail|hold`, a concrete `finding`, and
  `evidence: [{path, sha256}]` referencing the viewed pages or actual playback /
  listening / exact user approval record. Record real observation time in that
  evidence. Extraction time, a late-written file, or ffprobe is not perception.

Before extraction/review or promotion, run the deployed read-only checker:

```bash
python3 <runtime>/runtime/scripts/video_qc_coverage.py --project <p> --report <existing-qc.json>
# Before repeating a suspected interval:
python3 <runtime>/runtime/scripts/video_qc_coverage.py --project <p> --report <existing-qc.json> \
  --check-id <stable-check-id> --start-sec <start> --end-sec <end> --method native_frames
```

- It verifies registry/source/evidence hashes, interval bounds and declared
  coverage; it does **not** automatically watch, listen, judge or promote.
  `declarations_sufficient_for_manual_gate` is not a creative PASS.
- `REUSE_EXISTING_REVIEW`: use the recorded finding instead of extracting the
  same source/check/range again. A new hypothesis or inadequate prior resolution
  can reopen it with `--reopen-reason`; record the reason in the existing report.
- Changed source hash requires new binding/review; do not copy old PASS. Missing
  evidence requires repair of that exact binding, not a fabricated observation.
- `next_check` is the next unresolved check or missing playback/audio interval.
  Complete several bounded useful checks per due run when capacity allows;
  persist findings **immediately after viewing**, then advance. Do not spread
  one already-downloaded clip over many reservations for bookkeeping alone.
- Samples and even every native frame of a short segment are **not full-speed
  video playback or audio listening**. Check whole-asset real playback and sound
  before whole-asset PASS. Exact user listening approval may satisfy only its
  declared audio scope. No audio stream means no invented listening requirement.
- `resolved` means the question was answered, including a confirmed FAIL/HOLD;
  it does not mean the asset passed. Record usable handles and route the repair.
  Once only external-action blockers remain, report that condition and end/pause
  the existing schedule per its authorized scope, not endless duplicate QC.
- Apply source binding when a legacy report is next used; do not retroactively
  invent reviewed intervals or invalidate previously approved assets wholesale.
