# Seedance prompting incidents (history only)

Not loaded by default. Each entry is the story behind an imperative rule that
now lives in its owner file. Read only when a rule's reason is disputed.

## E24 — operational text in the prompt box (34%)

E24's prompt was 3,207 characters. `Scene ID`, `REFERENCE ROLES`, gate
wording, `EXPECTED`, `EXIT` and a banned-cast list took 1,100 characters (34%);
only 2,107 described the shot. Seedance treats pasted text as something to
draw. → Rule: prompt file is prompt-only; metadata lives in the package/pack
(`seedance-shared-contract.md` → Handoff contract).

## Audio switched off by a "no BGM" setting

A diegetic-only preference was written into the settings/handoff field instead
of the prompt. An operator reconciling "settings match the package" read
`no BGM` as a UI value and switched Audio off, which also killed SFX and room
tone. A periodic observer was then told to re-verify "Audio Off settings", so
the silence was actively maintained. → Rule: sound intent lives in the prompt;
the settings line reports the real UI value (`seedance-shared-contract.md` →
Audio).

## Independence-activist project rules copy

A project-local rules file inside one of 68 session folders had grown its own
prompt corrections (GENERAL_REFERENCE_MODE, character-sheet scope, creative mode
without light-match glue, no negative wall) because the canonical documents
contradicted each other; most runs never saw it. The valid corrections were
promoted to `seedance-field-lessons.md` and the shared contract on 2026-07-28;
project-specific content (1907 costume research, filenames, sheet paths, block
cursor) was not promoted. Image-QC and Runway queue rules that had been mixed in
were moved to `image-qc-source-frame-standard.md` and `seedance-production.md`.
→ Rule: no local rules copies; exceptions go to `docs/project_overrides.md`.

## Sliding-window reference decks

`E19: E18·E19·E20`, then `E20: E19·E20·E21` made consecutive blocks share most
references and the model returned two clips that read as the same shot ("why
are you making the same video twice"). → Rule: build each deck from the shot's
own material; overlap check in the shared contract.

## Drone arena: ring passage and scoring (2026-08/09)

Context for `prompt-review.md` → repeated-failure diagnosis.

- A drone near the floor was judged "rolling" without frame evidence; low hover
  and ground contact are different defects with different fixes.
- An identity sheet's gray floor, contact shadow and display pose leaked into
  the scene; the fix was a minimal crop or a height-readable environment ref,
  not more negatives or dropping the required identity ref.
- Altitude was asserted in words; it only read when upper nets/stands, a
  dropped shadow and foreground/background parallax showed it. A camera tilting
  up does not make the craft fly higher.
- Craft paths were directed by the pilot's name; the fix was to identify each
  craft by its shape/color + token and give pilots separate shots.
- Contact/evasion failed when an opponent stopped for no reason, bodies passed
  through each other, or only a camera spin implied the dodge. Roles
  (attack/block/decoy/recover) had to be split per craft.
- Lightning trails and spiral/black/split-screen effects hid contact and
  scoring; they now go only where they do not cover the causal event.
- Ring scoring: one frame where the craft overlaps the ring is not proof of
  passage. Required: approach side → consistent occlusion at the fixed ring
  plane → silhouette fully exits the far side. A lateral move where both rims
  occlude the craft can be passing behind the ring. The ring's shape, count and
  position stay fixed from approach to exit; a one-score shot must not circle or
  re-enter. Score change/SFX only after a verifiable full exit; otherwise
  `HOLD_SPATIAL_EVENT_UNPROVEN`, and an insert candidate is not proof of the
  match result.

## Blender proxy leak

A sampled output kept low-poly proxy bodies and recolored scenery while
inserting isolated finished-object close-ups; source camera and trajectories
were largely preserved. The user then clarified the video was a motion guide,
not a source to edit. Prompts already submitted remain historical evidence,
not retroactively corrected submissions. → Rule: `blender-previs-prompting.md` MOTION_GUIDE vs
SOURCE_RESTYLE.

## 2026-08-24 user examples

The user supplied five Seedance examples (multi-character timed dialogue,
one-take sword action with physical effects, handheld intimate performance,
master-audio lipsync, exact on-screen Hangul). Per the wiki log, the original
texts were deliberately **not stored**; only their structure was distilled into
`hell-grind-production-prompting-adapter.md` and the executable checks in
`runtime/scripts/seedance_prompt_case_harness.py` (cases in
`runtime/tests/test_seedance_prompt_case_harness.py`).
