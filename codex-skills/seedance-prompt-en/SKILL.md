---
name: seedance-prompt-en
description: Seedance workflow dispatcher. Load the shared contract, then use the prompting branch for prompt/reference-package authoring and the production branch for visible Runway operation, queue monitoring, download, and media verification.
---

# Seedance workflow dispatcher

Seedance is intentionally split into two phases so prompt authoring does not block Runway production:

1. Read `seedance-shared-contract.md` first.
2. For prompt design, reference mapping, or CLI handoff, read `seedance-prompting.md`.
3. For Chrome/Runway attachment, Generate, queue monitoring, download, or `ffprobe`, read `seedance-production.md`.
4. When both are requested, finish the prompting package first, then hand it to the production branch. Do not rewrite prompts during UI execution; return to the prompting branch if the prompt needs revision.
5. Optional Creative authoring: `$seedance-creative-prompt-team` runs the six roles as one sequential authoring checklist (Director / Reference / Camera / Physics / Composer / Critic). Do not spawn or parallelize those roles by default; production UI still stays in this skill.

## Non-negotiable gates

- Every Seedance generation is multi-reference in this user's pipeline; no single-reference exception unless the user explicitly overrides the specific shot.
- Creative Seedance Mode is the default authoring branch unless fragile continuity or the user requests Standard mode.
- If an approved character/model/identity-sheet character appears, attach the relevant character sheet or identity crop **on every generation**, together with scene references. A previous card or conversational memory does not count.
- Missing, mismatched, or unverified character-sheet thumbnail means `BLOCKED_CHARACTER_SHEET_ATTACHMENT_NOT_VERIFIED`; never click Generate.
- Runway visible Chrome is the source of truth. Do not use connector/API, hidden input, AppleScript/local mouse, or a second browser route.
- A Generate click is exactly one transaction after preflight. Completion requires a downloaded file and verified duration/codec, not a card or thumbnail.

## Prompting isolation gate

- Prompt authoring is single-agent and sequential. Do not launch parallel prompt workers, background schedulers, queue observers, browser loops, or external sidecars while the prompt package is being written.
- The prompting branch is non-GUI: no Chrome/Safari/Runway activation, Computer Use, `osascript`, AppleScript, `open -a`, native file chooser, or browser automation. Write the local package and hand it to production only after the prompt critic passes.
- Production may use the separate visible Chrome route after handoff. A production observer must not be started from the prompting branch.

## Live branch documents

- `seedance-shared-contract.md` — invariants, handoff contract, and block codes.
- `seedance-prompting.md` — Creative/Standard prompt authoring and reference-role packages. No UI operation.
- `seedance-production.md` — Runway visible UI, queue, download, and verification. No prompt improvisation.
- Optional sibling: `../seedance-creative-prompt-team/SKILL.md` — multi-agent Creative prompt team. Authoring only; production remains here.

Older combined guidance is retained only in `archive/` and is not live.
