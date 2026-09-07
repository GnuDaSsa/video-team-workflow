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
- Primary controller is the exact-session CLI helper documented in `codex-skills/seedance-prompt-en/aside-operator.md`; do not retain a separate AppleScript DOM route.
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

## Lean workflow release

- Stage responsibility is not permission to instantiate another agent or change
  the current conversation's model. Explicitly approved legacy dispatch remains
  available; default execution stays inside the current owner.
- Prompt compile/review owner: `codex-skills/seedance-prompt-en/prompt-review.md`.
  Exact Aside transport owner: `codex-skills/seedance-prompt-en/aside-operator.md`.
- Deployment safety preflight and strict installed hash parity are distinct.
  Canonical release mechanism and evidence: `tools/video_release.py` and
  `docs/releases/2026-09-06/`. Never infer video quality from those checks.

## Astra creative prompt routing

- The user explicitly changed image and video prompt authorship from 5.6 Sol to Astra. The three creative routes now use `gpt-6-astra` at existing `xhigh`; flow/QC/edit and Seedance production routes retain Luna high.
- This is an authoring-model preference, not a change to image_gen/Seedance providers or permission to spawn another owner. The current conversation continues sequentially.
- Canonical routing: `runtime/scripts/model_routing.py`; acceptance: `docs/contracts/2026-09-06-astra-prompt-routing.md`.

## Role-aware reference overlap

- Live two-character cycle exposed a contradiction between mandatory per-generation identity sheets and the previous raw-image overlap limit. The canonical Seedance shared contract now counts scene/action duplication separately from required approved identity anchors; four same-owner good/bad review fixtures preserve attachment and anti-padding gates.
- No automatic agent, reduced identity test, provider action, or video-quality claim is introduced.

## Preproduction stop is not queue completion

- A newly attested project without an intended Runway session may stop for explicit human selection before binding. The queue checker now permits only a fully evidenced unstarted state with no queue/binding/recovery/preflight artifacts. Corrupt queue files and active or uncertain production still require normal recovery/continuation. The branch never invents a visible-board observation.
- Canonical code and four negative/positive test methods enforce this boundary; see docs/contracts/2026-09-06-preproduction-stop.md.

## Routine flow and truthful monitoring

- User corrected repeated production approvals and model-dependent monitoring claims. Runtime next now prefers the current owner, not optional new-owner dispatch. Routine role changes, safe same-tab fresh-session preparation and repeated foreground waits need no repeated confirmation; specific new surface and high-impact approvals remain.
- Canonical queue-doctor distinguishes absent queue, contract-only promises, live/dead wait processes and unconsumed wakes without creating any watcher. The old paused five-minute cron was not restarted; no 15-20 minute scheduled continuation is claimed. See docs/releases/2026-09-06/continuation-reliability.md.

## Scheduled-check continuation

When the user requests periodic scheduled checks, preserve that mode across model/turn changes through canonical queue-mode; do not silently substitute attached 15-minute waits. Never infer an active schedule from a proposal card or mode file, nor repeat initial approval at every run. Inspect existing native registration before creating another surface. queue-doctor also audits active rollups and unsupported DONE/schedule claims; its local file checks never certify scheduler access or playback QC. See the canonical Seedance production branch.

## Automatic photoreal knowledge

For 실사/포토리얼 stills and live-action video, the user need not repeat “Hell
Grind.” The existing live-action wiki profile is selected automatically via
image-prompt/videodirector/v4 knowledge routing. Apply only matching task/media
sections. Source contradictions and provider-specific recipes are not global
rules. Canonical content and verification: `docs/releases/2026-09-08-hell-grind/release.md`.
