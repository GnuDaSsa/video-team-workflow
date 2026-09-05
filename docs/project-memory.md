# Project Memory

Use this file for durable context that should survive across threads.

## Product and Repo Context

- Canonical, version-controlled deployment package for the user's Codex video-team workflow.
- `codex-skills/seedance-prompt-en` is the sole live Seedance operator contract. The deployment script installs companion policies into `~/.codex/video-team-policies/`.

## Working Preferences

- Coding style choices that are stable over time.
- Review preferences or release expectations.
- Default recurring-character identity asset is `CHAR_<ID>_TRIPTYCH_R<n>`: left headless front body, middle back body with head, right large 3/4 portrait. Bind those roles explicitly in the model-facing prompt, use deterministic crops for fragile shots, keep state changes as separate assets, and require a 10/10 stress gate.
- Use the Hell Grind prompting adapter as a bounded shot-contract compiler: exact entity count, source roles, locked geography, complex-shot occupancy, timed physical beats, acting/audio, positive proof constraints, and one-clause revisions. It never overrides Korean prompts, duration/length limits, or Seedance UI authority.

## Known Pitfalls

- Never leave an archived `SKILL.md` under `~/.codex/skills`; it can remain discoverable as a live skill.
- A skill must not refer to a policy file that the deployment script does not install.
- Do not add a second Seedance UI instruction source to director, MV, AGENTS, lane, or scheduler files.

## Open Questions Worth Tracking

- Questions that are not blockers today but should not disappear.

## Runway Browser Owner

- Seedance production uses one visible, logged-in Aside `app.runwayml.com` tab only. Never fall back to Chrome, Safari, the Codex in-app browser, connector/API, or a second browser session.
- Primary controller is `aside repl` with `listBrowserTabs()` and `attachBrowserTab(exactTargetId)` on the existing tab. AppleScript is optional, not a prerequisite.
- If Aside control is unavailable, stop that UI route with `BLOCKED_ASIDE_CONTROL_UNAVAILABLE` and the exact required user action; do not reinterpret `어사이드` as `알아서`.

## Generated-vocal naturalness preference

- The user explicitly rejects the vocal sound of `링크 업!` and `리와인드 없는 오늘` as obvious AI output. Those performances are negative references only.
- Use `/Users/gnudas/.codex/skills/music-director/references/vocal-naturalness-qc.md` as the canonical listening gate. Male and female vocals are both allowed; stable human identity, fluent Korean diction, breathing, dynamics, tuning, and restrained vibrato determine acceptance.
- ASR, stems, onset timing, waveforms, and prompt quality cannot produce a PASS without full-track playback.

## Explicit Seedance 2.5 branch — 2026-09-05

- Natural-language `Seedance 2.5`/`씨댄스 2.5` requests route to `seedance25-prompt-en`; explicit 2.0 and unversioned Seedance remain on `seedance-prompt-en`. Never load both version branches for one block.
- Only prompting and production diverge. Runtime rails, media registry, safety and approval gates, duration lock, one existing Aside tab, and same-turn foreground queue handling remain shared.
- Every 2.5 package records `provider_model: Seedance 2.5` and `provider_skill: seedance25-prompt-en`. Production uses the 2.5 adapter to prove the freshly visible model and duration; the adapter imports the shared helper and may not grow separate browser/upload/queue/recovery code.
- For low-AI animation, prompts specify opening balance/contact, anticipation, one primary action, weight transfer, causal secondary motion, settle, one motivated camera path, and an editor-usable held end state. 2D prompts additionally specify key-pose timing, spacing, line/style stability, and restrained parallax/effects.
