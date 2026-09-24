# Global video guidance lazy-load — 2026-09-25

## Problem and evidence

Codex loads a 38,403-character global instruction file before a new request has been classified. Nine long video craft/QC sections are irrelevant to many general Codex tasks and to early video intake. The previous scoped `videodirector` lean entry reduced that skill but left this larger cost untouched. Aside's Jev is an optional ambiguity classifier, not a replacement for instruction-load reduction.

## Scope

Move the nine detailed craft/QC sections verbatim into four on-demand `videodirector/references/*-calibrations.md` files. Keep cross-project execution, spawn, public submission, ChatGPT send-button, Kim Gu email, authority, and Gongnyang safety/routing guidance in global AGENTS. Add a short trigger table to global AGENTS and the `videodirector` router. Runtime rails and versioned Seedance procedures are unchanged. No Jev call or extra agent is added.

## Acceptance

1. Every moved section is byte-for-byte present in a phase-specific reference, absent from global, and discoverable from both global and the skill.
2. Global instruction text falls below 20,000 characters without removing the named safety headings.
3. Quick tests, skill validation, source manifest preflight and six-file scoped deployment/hash parity pass.
4. No production token/latency improvement is claimed until a comparable new-task A/B is measured.

## Non-goals

No change to runtime gates, media, browser/provider action, JEV execution, global safety approvals, or user project state. Runtime AGENTS slimming requires its own authority audit.

## Verified result

- Commit `d928f3f` was pushed to `origin/main`. The reviewed manifest preflight passed; scoped deployment changed only global AGENTS, `videodirector/SKILL.md`, and four new calibration references. Six source/live SHA-256 pairs matched after deployment. Full release parity was not claimed because unrelated runtime drift remains.
- Global instructions: 38,403 → 17,661 Unicode characters, a 54.0% reduction. Nine moved sections were verified byte-for-byte in the new references. Global safety headings remained installed.
- 451 Aside/deployer tests (with realpath TMPDIR), 198 runtime tests, Python compile, skill validation, release preflight, shell syntax and diff check passed. The first Node test run used macOS `/tmp` and failed strict realpath fixtures; rerun with `/private/tmp` passed 451/451.
- No JEV API call, agent, provider/browser operation or media generation. Future model-token and production wall-clock benefit is not yet measured.
