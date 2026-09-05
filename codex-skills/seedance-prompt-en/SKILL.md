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

Seedance is intentionally split into two phases so prompt authoring does not block Runway production:

1. Read `seedance-shared-contract.md` first.
2. For prompt design, reference mapping, or CLI handoff, read `seedance-prompting.md`.
   Also read `xazinga-prompting-adapter.md` to apply the compatible source-scope, camera/light, transition, and critic additions distilled from XAZINGA skills. It is an adapter, not a second authority.
   Also read `hell-grind-production-prompting-adapter.md` for the two-layer shot contract, exact entity/space locks, three-panel identity binding, performance beats, and one-clause revision discipline distilled from the public Hell Grind package. It is an adapter, not a second authority.
3. For Aside/Runway attachment, Generate, queue monitoring, download, or `ffprobe`, read `seedance-production.md`.
4. When both are requested, finish the prompting package first, then hand it to the production branch. Do not rewrite prompts during UI execution; return to the prompting branch if the prompt needs revision.
5. Optional Creative authoring: `$seedance-creative-prompt-team` runs the six roles as one sequential authoring checklist (Director / Reference / Camera / Physics / Composer / Critic). Do not spawn or parallelize those roles by default; production UI still stays in this skill.

## Non-negotiable gates

- **An explicit user instruction overrides every default here** — mode, count, duration, ratio, audio, provider.
- **User-reference superior authority:** the five Seedance examples supplied on 2026-08-24 are the default creative/prompt-construction authority for future authoring when `user_reference_superior_v1` is declared. They outrank general brevity, one-action, one-camera, generic audio-route, and house-style defaults. Existing rules may fill gaps but must not dilute the examples. Only the current explicit instruction/brief and non-bypassable safety, provider-capability, verified-reference, and settings gates remain above them. Apply the exact precedence contract in `hell-grind-production-prompting-adapter.md`.
- **Multi-reference is the default mode** (the Runway tab opposite Keyframe) and stays selected unless the user asks otherwise. "Use multi-reference" is a mode instruction, not a remark about image count.
- Reference count is per-request (commonly 3–4, sometimes a character sheet plus a background). *The agent* never invents a fixed count or pads to reach one; a count the user states is an instruction. Every reference still needs a named role in the ordered `@ImageN` map.
- Creative Seedance Mode is the default authoring branch unless fragile continuity or the user requests Standard mode.
- If an approved character/model/identity-sheet character appears, attach the relevant character sheet or identity crop **on every generation**, together with scene references. A previous card or conversational memory does not count.
- Missing, mismatched, or unverified character-sheet thumbnail means `BLOCKED_CHARACTER_SHEET_ATTACHMENT_NOT_VERIFIED`; never click Generate.
- Runway visible Aside is the source of truth. Attach `aside repl` to the existing Runway tab by exact `targetId` and use that Aside CLI binding as the primary controller. Aside AppleScript is optional only when Apple Events JavaScript is already enabled; macOS Accessibility/Computer Use is a same-tab fallback. A disabled Apple Events toggle is not a blocker while Aside CLI can bind. Do not use Chrome, Safari, the Codex in-app browser, connector/API, hidden input, coordinate clicking, a new Aside tab, or a second browser route.
- A Generate click is exactly one transaction **per scene** after preflight — not one per session. Keep submitting eligible packages while slots are free; stop only when the shelf is empty or every remaining item is blocked.
- Completion requires a downloaded file and verified duration/codec, not a card or thumbnail.

## Prompting isolation gate

- Prompt authoring is single-agent and sequential. Do not launch parallel prompt workers, background schedulers, queue observers, browser loops, or external sidecars while the prompt package is being written.
- The prompting branch is non-GUI: no Aside/Chrome/Safari/Runway activation, Computer Use, `osascript`, AppleScript, `open -a`, native file chooser, or browser automation. Write the local package and hand it to production only after the prompt critic passes.
- Production may use the one visible Aside route after handoff. A production observer must not be started from the prompting branch.

## Live branch documents

- `seedance-shared-contract.md` — invariants, handoff contract, and block codes.
- `seedance-prompting.md` — Creative/Standard prompt authoring and reference-role packages. No UI operation.
- `seedance-production.md` — Runway visible UI, queue, download, and verification. No prompt improvisation.
- `seedance-field-lessons.md` — prompt-authoring corrections proven in production: `GENERAL_REFERENCE_MODE`, what the character sheet may and may not do, creative mode without light-match glue, no generic negative wall.
- `hell-grind-production-prompting-adapter.md` — two-layer shot contract, exact entity/space locks, triptych role binding, physical performance beats, and one-clause revision discipline. No UI operation.
- `image-qc-source-frame-standard.md` — **image QC lane, not prompting**: whether a still is usable as an I2V source (`VIDEO_FRAME_STATIC_POSTER_FAIL`, `EMOTION_CAUSALITY_FAIL`, duplicate protagonists).
- Optional sibling: `../seedance-creative-prompt-team/SKILL.md` — multi-agent Creative prompt team. Authoring only; production remains here.

Older combined guidance is retained only in `archive/` and is not live.
