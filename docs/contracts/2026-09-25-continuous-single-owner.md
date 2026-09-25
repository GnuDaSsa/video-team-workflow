# Continuous single-owner video production — 2026-09-25

## Evidence and problem

The Seongnam food-tech project is visual-only, No-I2V, Seedance 2.0. Its current
Codex session is `gpt-6-sol`. The runtime says both “continue in the current
conversation” and “Astra must author, otherwise request approval for a bounded
child.” The owner therefore stopped after one web character repair and asked
for an extra-agent approval that the user explicitly rejected. Image QC still
has three left-panel layout defects and five unlocked identities. A prompt
package or status string is not completed media.

## Decision

- Default: one owner keeps planning, prompting, browser execution and QC in the
  current conversation, using its actual session model. Astra xhigh remains the
  preferred *optional* creative dispatch route, not a prerequisite that creates
  a routine approval question or blocks an otherwise authorized production run.
- If a user explicitly requires Astra-only authorship for a particular asset,
  preserve that requirement and hold rather than silently authoring as another
  model. A separate author child still requires specific current-conversation
  approval; never infer it from “use the video team.”
- Record the actual author model where available; never label Sol-authored work
  as Astra. Keep existing prompt validation, reference attachment, identity
  stress QC, 15-second duration lock, registry, public-action and safety gates.
- `next` must make same-owner execution unambiguous and keep optional dispatch
  separate. Do not relax the media hard gate or auto-spawn/schedule anything.

## Acceptance

1. Runtime and Seedance/image lane text no longer say a child or approval is
   required merely because the current session model is not Astra.
2. `next.default_execution` advertises session-model same-owner authorship and
   the optional Astra preference; `next_dispatch` still requires exact spawn
   approval for an actual new owner.
3. Positive/negative tests cover single-owner prompting and protected optional
   dispatch; existing duration, identity, registry and public-action gates pass.
4. Isolated commit/push and scoped source-to-live deployment pass. Real ChatGPT
   image or Seedance generation is separate live verification, not implied by
   repository tests.
