# Video production throughput and user-intent recovery — 2026-09-26

## Evidence

The active Seongnam food-tech project has five character candidates and 23
reference-bound QC stills (10 guardian, 10 grandmother, 3 child), but zero
Seedance clips. Its initial 3m15s storyboard explicitly requested creative
non-I2V city/building shots and a scene where each subject eats. The accepted
Planner map holds 48 seconds of opening named-place footage for external
inserts and changes all three eating outcomes to preparation only. A later
`plan_recheck_20260925.md` identified those losses but did not revise the
production map. An appended unrelated character exception changed the hash of
the whole `docs/project_overrides.md`, invalidating the approved visual-only
audio exception; `next` misleadingly lists Music again.

The recent Blue Orbit project has 177 local Seedance prompt files; 47 exceed
3,000 characters and 15 exceed 3,400. Sample prompts combine up to seven
identity references and four timed shots. This is a complexity signal, not a
controlled claim that model quality changed. The latest single-owner fix has
already removed routine Astra-child approval; do not undo it.

## Objective

Shorten time-to-first-useful-video, preserve the user's creative intent and
recover safe, flexible shot authoring without weakening real media, attachment,
public-action or provider-account gates. This is a single-owner workflow
change, not permission to spawn more agents or browser loops.

## Changes

1. Use a dedicated immutable visual-only authorization receipt; editable
   project overrides no longer invalidate the evidence hash. Invalid audio-plan
   evidence must not silently route back to Music.
2. Replace mandatory 10/10 QC-only stills for every recurring identity with
   three varied reference-bound checks (face, body/action, and relationship if
   relevant) before dependent production. Keep native master crop QC, actual
   attachment, and clip-level identity QC. Any failure triggers targeted repair;
   a user-requested full 10-case study remains available but is not default.
3. Planner preserves each user-specified scene payoff and creative suggestion as
   KEEP, safety-scoped ADAPT, or HOLD with specific evidence and a functional
   alternative in its existing result. A review memo alone is not an adopted
   plan revision; affected block maps must change before claiming inclusion.
4. Seedance authoring starts with the user-intended image/action, then the
   minimal physical camera/reference contract. One coherent 15s source shot is
   valid; do not force 2–4 scenes to fill the duration. Load optional prompt
   adapters only for relevant risks. Avoid repeated generic controls.

## Acceptance

- Live Seongnam `validate` passes after moving the existing user authorization
  into a dedicated hash-bound receipt; `next` does not list Music for invalid or
  valid visual-only plans.
- Three-check identity policy is discoverable in the active video-team owners
  and reflected in the current project without fabricating missing tests.
- Prompt and Planner rules require user-intent trace plus conditional, lean
  authoring. Existing safety, duration, attachment and actual-media gates remain.
- Targeted tests, full configured quick verification, release preflight, scoped
  deployment, source/live hashes, isolated commits and Git sync pass.
- No real image/video quality or elapsed-time gain is claimed without a new
  comparable production run; untested limits and remaining holds are explicit.

## Verification so far

- Source tests: 451 Node tests and 204 Python runtime tests passed;
  Python compile, shell syntax and `git diff --check` passed.
- `video_release.py freeze` and source/live safety preflight passed for 73
  allowlisted files. This is not installed parity or generated-media proof.
- Native Aside's reviewed knowledge catalog hashes were refreshed for the
  current live wiki pages (including an already-edited typography page) after
  bounded content review; the creative corpus itself was not rewritten.

## Closeout and live limits

- GitHub `main` contains commits `3a0e27f` and `52c260a`. The 13 initial
  changed Codex files and one follow-up identity-standard file were deployed
  with `video_release.py apply-scoped`; each source/live hash matched. The
  native Aside reviewed knowledge catalog was frozen/deployed through
  `deploy_aside_workflow.mjs`; its installed parity check passed.
- Seongnam now uses a dedicated SHA-bound visual-only authorization receipt.
  `validate` returned `ok: true`, no problems, and `next` skipped Music with
  no user action required. Existing child T01–T03 image files and master were
  visually inspected and registry/hash/dimension verified; the child master
  is now the third approved identity (3/5 total), with a 3/3 preflight and
  explicit 4.47/5 scored crop rubric. Researcher and dog remain candidates.
- Project evidence and exact residual blockers are in
  `docs/throughput_intent_audit_20260926.md` inside the Seongnam project.
  Planner R2 still holds the user's creative city shot outside the generated
  block map, still omits actual eating, and binds outdated candidate IDs and
  stale source hashes. It must become a separately proven R3 before those
  blocks are submitted. This release does not claim that project-specific
  creative plan adoption or actual video quality is complete.
- Full Codex release parity is deliberately not claimed: the pre-existing
  unrelated live `model_routing.py` drift remains. Scoped changed-file hashes
  and native Aside parity were checked. No Seedance clip was generated for this
  workflow audit; no controlled GPT-5.5 comparison or wall-clock production
  speedup has yet been measured.
