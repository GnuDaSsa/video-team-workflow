# Explicit visual-only production without audio

## Evidence and problem

The Seongnam foodtech project's Luna owner was told to make images and video, not music. Its project nevertheless remained at `music=PENDING` because the v4 Planner gate requires a verified locked audio file. The owner stopped after an unused local test and reported no way forward. The user now explicitly requests that this hard gate be handled. This is not a request to fabricate a silence file, relabel an unverified track `LOCKED`, or silently discard music-first defaults for other projects.

Project evidence: `/Users/gnudas/Documents/Codex/video-team-runtime/20260924_204417_seongnam-foodtech-one-table`; user message in the Luna task `msg_01a0d3a2-1cd3-72d3-90e2-b5803e232fee` (2026-09-24) and current root request (2026-09-25). The default music-first workflow remains unchanged elsewhere.

## Scope

- Add a **project-scoped, explicit-user, hash-bound** `visual_only_no_audio` audio plan with `delivery_scope=visual_assets_only` to the v4 runtime input gate.
- When valid, skip the music lane in `next` and let Planner prepare a **provisional time-based** visual block map from the brief, then run existing image/Seedance gates normally. Music and narration remain uncreated/unlocked; no timing or audio-completion claims.
- Refuse missing/malformed/tampered override evidence. Keep the default registered Music Lock hard gate for every other project.
- Permit only a clearly labeled `VISUAL_ASSETS_ONLY_NO_MUSIC` package from verified visual files; do not call it a finished voiced/musical film or fabricate a standalone audio asset.
- The internal mode name concerns the absence of a separate music/VO asset. It does not force Seedance video to be silent: causal knocks, room tone, or machine effects embedded in video follow the selected version skill's Audio setting. Label the package `VISUAL_ASSETS_ONLY_NO_MUSIC`.
- Record a concrete project exception in `docs/project_overrides.md` citing runtime §1.0 and §1.1. Preserve all existing assets/candidates and user holds.

## Acceptance

1. No override: status-only/empty music lock still blocks Planner and `--force` cannot bypass it.
2. Valid evidence: `next` skips music, exposes Planner as the next lane, leaves `manifest.music` unaltered, and Planner gate passes with no audio asset.
3. Wrong evidence path/hash/source/message ID/target length or changed file blocks Planner and fails validation.
4. Empty/non-unique Planner block map still blocks image lanes; existing Seedance duration/reference/attestation gates remain intact.
5. Package gate does not demand music for a verified visual-only project, but still requires editor completion, real video, and a registered export. Invalid override evidence blocks it.
6. Runtime unit tests, Python compile, release preflight, project `next`/`validate`, and selected live source/deployed hashes pass. Do not claim generated video or live Runway validation.

## Non-goals

No new agent, background process, audio generation, silent placeholder, I2V switch, shortening the 15-second Seedance lock, public upload, or reinterpretation of the user-approved ChatGPT web character candidates as identity-locked masters.
