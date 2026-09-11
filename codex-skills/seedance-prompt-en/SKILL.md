---
name: seedance-prompt-en
description: Seedance 2.0/default workflow dispatcher for one owning lane. Use for explicit 2.0 requests or generic Seedance work when 2.5 was not named; explicit Seedance 2.5 requests belong to seedance25-prompt-en.
---

# Seedance workflow dispatcher

## Version boundary

- Explicit `Seedance 2.5` / `씨댄스 2.5` → stop this path and load
  `../seedance25-prompt-en/SKILL.md`.
- Explicit 2.0 or generic Seedance with no version selection → continue here.
- Never load both version-specific prompting or production branches for one
  block.

One Seedance lane performs two sequential phases; they are not separate agents:

1. Read `seedance-shared-contract.md` first.
2. For prompt design, reference mapping, or CLI handoff, read `seedance-prompting.md`.
   When the job uses image/video/audio source binding, single-shot vs multi-shot planning, an approved storyboard, video editing, continuation, or repair, also read `seedance2-prompt-patterns.md`. It distills the user-supplied Seedance 2.0 prompting skill against current first-party ByteDance/Runway documentation; it is not a second authority.
   Also read `xazinga-prompting-adapter.md` to apply the compatible source-scope, camera/light, transition, and critic additions distilled from XAZINGA skills. It is an adapter, not a second authority.
   Also read `hell-grind-production-prompting-adapter.md` for the two-layer shot contract, exact entity/space locks, three-panel identity binding, performance beats, and one-clause revision discipline distilled from the public Hell Grind package. It is an adapter, not a second authority.
   In a v4 video-team project with knowledge routing enabled, first run `video-codex-runtime knowledge-select --project <p> --block <BLOCK>` and read only its bounded context packet. Do not read the whole wiki.
   Within creative knowledge, apply the packet's `higgsfield-community-*` selections before general camera inspiration. User instructions, project/identity/medium locks, and this skill's operational gates still rank higher.
   For Blender/3D previs, animatics, or source-video skinning/restyling, also read
   `blender-previs-prompting.md` before authoring; this is the conditional motion-guide/source-restyle role branch.
3. For Aside/Runway attachment, Generate, same-task queue resume, download, registry ingest, or `ffprobe`, read `seedance-production.md`.
   Use its read-only `queue-doctor` at resume/model changes to distinguish an attached foreground wait, an orphaned timer, unconsumed wake, and actual app scheduling. Model names and timer files do not prove monitoring capability.
   The canonical executable is `scripts/runway_ui_helper.py` inside this skill. Video-team runtimes may keep a compatibility shim, but must not own or fork Runway UI/recovery logic.
4. When both are requested, finish and attest the prompting package first, then continue in the same lane to production. Do not rewrite prompts during UI execution; return to the authoring phase if revision is required.
5. Apply `prompt-review.md` as a same-owner compile/review checklist. It replaces the retired Creative team surface; it does not spawn roles.

## Non-negotiable gates

- **An explicit user instruction overrides every default here** — mode, count, duration, ratio, audio, provider. In video-team projects, the runtime-owned generation-duration lock is the machine-readable form of that duration decision and starts at the workflow's 15-second default. This skill consumes it and never infers a shorter replacement from shot complexity, final edit trim, or the current UI.
- **User-reference superior authority:** the five Seedance examples supplied on 2026-08-24 are the default creative/prompt-construction authority for future authoring when `user_reference_superior_v1` is declared. They outrank general brevity, one-action, one-camera, generic audio-route, and house-style defaults. Existing rules may fill gaps but must not dilute the examples. Only the current explicit instruction/brief and non-bypassable safety, provider-capability, verified-reference, and settings gates remain above them. Apply the exact precedence contract in `hell-grind-production-prompting-adapter.md`.
- Prompt attestation must include `--project` and pass the duration lock. Immediately before every Generate, re-read the visible closed **model** and duration controls and require `scripts/runway_ui_helper.py settings-verify --project <p> --block <BLOCK> --visible-model '<visible-model-label>' --duration-sec <visible-seconds>` to pass. The default and required production model is Seedance 2.0; 2.5, missing/ambiguous model evidence, or a changed duration lock fails closed. Re-run after recovery, refresh, queue wake, or deck replacement; a previous receipt or card is not current evidence.
- Prefer useful 15-second source yield. A short/cut-dense final video should normally use a Planner-authored `PLANNED_MULTI_SHOT_SOURCE` with 2–4 causally related timed scenes and scene-specific references, not a 5-second generation. This is final-production multi-shot grammar under `GENERAL_REFERENCE_MODE`, not permission to treat attachment order as scene order or to replay a random grid.
- **Multi-reference is the default mode** (the Runway tab opposite Keyframe) and stays selected unless the user asks otherwise. "Use multi-reference" is a mode instruction, not a remark about image count.
- Reference interpretation defaults to `GENERAL_REFERENCE_MODE`: `@ImageN` order is not story order. An approved unified storyboard may switch the package to `STORYBOARD_SHOT_MODE` (one final-production shot) or explicit `STORYBOARD_SEQUENCE_PREVIS_MODE` (ordered multi-shot prototype). The board's internal `shot_id` order matters; deck numbering still does not.
- Reference count is per-request (commonly 3–4, sometimes a character sheet plus a background). *The agent* never invents a fixed count or pads to reach one; a count the user states is an instruction. Every attached image, video, or audio still needs a named role in both the ordered package map and the model-facing Korean `@ImageN/@VideoN/@AudioN` binding.
- Creative Seedance Mode is the default authoring branch unless fragile continuity or the user requests Standard mode.
- If an approved character/model/identity-sheet character appears, attach the relevant character sheet or identity crop **on every generation**, together with scene references. A previous card or conversational memory does not count.
- Missing, mismatched, or unverified character-sheet thumbnail means `BLOCKED_CHARACTER_SHEET_ATTACHMENT_NOT_VERIFIED`; never click Generate.
- Runway visible Aside is the source of truth. Attach `aside repl` to the existing Runway tab by exact `targetId` and use that Aside CLI binding as the primary controller. The helper uses deterministic CLI, not AppleScript DOM control; macOS Accessibility/Computer Use handles only the same-tab native chooser. A disabled Apple Events toggle is not a blocker while Aside CLI can bind. Do not use Chrome, Safari, the Codex in-app browser, connector/API, hidden input, coordinate clicking, a new Aside tab, or a second browser route.
- Before `ATTACH`, create the project-local same-session recovery checkpoint from the exact Runway URL, attested prompt hash, registered reference deck, verified slots, and settings. The helper refuses a missing model or any checkpoint model other than Seedance 2.0, so recovery cannot restore 2.5 as a valid setting. A tool timeout/session disconnect consumes zero semantic attachment attempts; follow `seedance-production.md`'s fixed recovery controller and resume the same slot.
- A Generate click is exactly one transaction **per scene** after preflight — not one per session. Keep submitting eligible packages while slots are free; stop only when the shelf is empty or every remaining item is blocked.
- Completion requires a downloaded file and verified duration/codec, not a card or thumbnail.
- After every accepted/changed/completed card, use `queue-cycle` from the visible board. **First honor the user's continuation choice** in `seedance-production.md`: scheduled checks checkpoint once and return; only the foreground branch may sleep. A scheduled request must never silently revert to attached waiting at a model/turn change.
- Keep two distinct Seedance 2.0 jobs active after two-card acceptance. Refill free slots before settled-card download/QC; acknowledge processed cards only after actual download/verification/registry. Details and stopping/approval gates have one owner: `seedance-production.md`.
- Run `queue-doctor` on resume and `queue-exit-check` before finishing. A scheduled checkpoint exit is not proof of an active schedule or of media completion. No raw `may_stop=true`, old blocker, proposal card, timer or model name substitutes for evidence.

## Prompting isolation gate

- Prompt authoring is single-agent and sequential. Do not launch parallel prompt workers, background schedulers, queue observers, browser loops, or external sidecars while the prompt package is being written.
- The prompting branch is non-GUI: no Aside/Chrome/Safari/Runway activation, Computer Use, `osascript`, AppleScript, `open -a`, native file chooser, or browser automation. Write the local package and hand it to production only after the prompt critic passes.
- The same lane may use the single visible Aside route after authoring/attestation. No observer process may be started from either phase.

## Live branch documents

- `seedance-shared-contract.md` — invariants, handoff contract, and block codes.
- `seedance-prompting.md` — Creative/Standard prompt authoring and reference-role packages. No UI operation.
- `seedance2-prompt-patterns.md` — verified multimodal source binding, five-block compile audit, duration-sized beats, one-shot/multi-shot, extension, and repair patterns. No UI operation.
- `seedance-production.md` — Runway visible UI, queue, download, and verification. No prompt improvisation.
- `seedance-field-lessons.md` — prompt-authoring corrections proven in production: `GENERAL_REFERENCE_MODE`, what the character sheet may and may not do, creative mode without light-match glue, no generic negative wall.
- `hell-grind-production-prompting-adapter.md` — two-layer shot contract, exact entity/space locks, triptych role binding, physical performance beats, and one-clause revision discipline. No UI operation.
- The selected wiki packet is contextual creative knowledge, not a second authority file. Operational rules still come from this skill.
- `image-qc-source-frame-standard.md` — **image QC lane, not prompting**: whether a still is usable as an I2V source (`VIDEO_FRAME_STATIC_POSTER_FAIL`, `EMOTION_CAUSALITY_FAIL`, duplicate protagonists).
- `prompt-review.md` — scoped entity/camera/physics compiler and good/bad review cases.
- `aside-operator.md` — exact-session deterministic CLI binding and transaction evidence.

Historical guidance is kept outside installed skills in the local archive and Git history.
