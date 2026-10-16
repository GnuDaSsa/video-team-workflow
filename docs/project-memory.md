# Project Memory

Use this file for durable context that should survive across threads.

## Product and Repo Context

- Canonical, version-controlled deployment package for the user's Codex video-team workflow.
- `codex-skills/seedance-prompt-en` is the sole live Seedance operator contract. The deployment script installs companion policies into `~/.codex/video-team-policies/`.
- Runtime v4 (`2026-07-31-sequential-media-v4`) applies only to newly initialized projects. Actual media lives in the numbered bilingual project `media/` tree and is tracked by `asset_registry.sqlite`; lane folders are metadata-only.
- Prompt ownership is lane-local and model routing is phase-local, not a prompt bridge: Image Creator and Seedance prompting use Sol xhigh; other flow/QC/edit/package and Seedance Aside/Computer Use production use Luna high.
- No-I2V is a `generation_mode` of this same runtime, not another team. It keeps the full rail and changes only image/reference strategy: minimum reusable references, minimum new image generation, no per-cut source frames, and more shot design in the Korean Seedance prompt.
- Video prompting knowledge is attribute-routed from `/Users/gnudas/wiki/_meta/video-knowledge-catalog.json`. Planner declares block attributes, the local router emits a bounded context/receipt, and Seedance reads that packet instead of the full wiki.
- Inside Seedance creative knowledge, Higgsfield community synthesis is preferred after user/project/style/identity/medium locks and operational gates. The always-selected core and matching camera/product sections translate community patterns into camera physics rather than copying prompts or cameos.

## Working Preferences

- Only image generation may use bounded concurrency, with a hard maximum of three immutable-prompt worker processes. Everything else is serial.
- Seedance prompting and production are separate sequential owners inside one lane. Prompting stops at `READY_FOR_PRODUCTION`; production consumes only current attested packs. Never auto-spawn the second phase.
- Every Codex lane/phase dispatch needs the exact current-conversation `--approved-spawn <lane>:<phase>` token, and a live Codex owner blocks another dispatch.
- Seedance prompt insertion is file-first: UTF-8 NFC `*_prompt.txt` → canonical `paste-prompt --file` → visible counter + normalized hash. Never retry Korean synthetic typing after an IME failure.
- Fifteen seconds is a hard default. Any shorter project/block lock must carry current `user:` or `brief:` evidence and still pass attestation plus visible `settings-verify`; manual lock edits fail closed. Immediately before every Generate, the same preflight also requires one unambiguous visible `Seedance 2.0` label. Seedance 2.5, missing/ambiguous model text, and stale recovery settings fail closed; re-read after refresh, recovery, queue wake, or deck replacement.
- For model visibility, use the main-app `[model-route]` label and project `model_route.json`/`status`/`report`. Do not infer a model from prose quality or an old log without route evidence.
- Eligible inactive intermediate files go to macOS Trash after 24 hours with a journal; never empty Trash automatically.
- When Runway is full, use at most one **pending** same-turn 15-minute foreground tool wait, never a resident monitor, scheduler, or additional agent/browser. This is not a one-wait-total limit: after each consumed wake, continue sequentially in the same turn while `may_stop=false`. `resume_contract.json` is state only and cannot re-enter Codex.
- Treat `queue_runtime.json`, not prose or `resume_contract.json` alone, as the continuation source of truth. Production runs `queue-cycle` after every visible card change; it atomically checkpoints and enters the required foreground wait. Keep two distinct jobs active: when a card settles, refill its provider slot before download/QC, then process settled backlog while the replacement pair generates. Mark handled visible cards with `--processed-job SCENE|OUTPUT`.
- A long-running foreground `queue-wait` may make the shell tool yield a session ID. The same Codex turn must keep polling that exact session until exit, visibly re-read Runway, and consume it with `queue-sync --from-wake`; never substitute a detached `sleep`, log writer, background process, or a claim that the timer woke the model.
- Shelf exhaustion ends submission only. Existing active cards must still be rechecked through consumed foreground waits, downloaded, verified, and registered before the Seedance lane may stop.
- Before any Seedance production final response, run canonical `queue-exit-check --project <p>`. Exit code 1 is binding. `status:"RUNNING"` without a live lane owner PID and any nonterminal `queue_runtime.may_stop=false` without a live owner/wait are `STOPPED_INCOMPLETE`; “continue on the next owning turn” is valid only as an explicitly recorded `BROKEN_FOREGROUND_CONTINUATION` after user interruption or a lost tool session.
- Provider generation duration is a Planner/project decision recorded in `generation_duration_lock.json`, not a Seedance prompt-complexity inference. Seedance starts from a 15-second workflow lock; only explicit user/brief evidence may select 5–14 seconds. Prompt packs must match the lock under project-scoped attestation, and the visible Runway duration must pass `settings-verify` against unchanged pack/lock hashes immediately before Generate.
- Optimize 15-second source yield: when a short/cut-dense final needs several shots, Planner should group 2–4 consecutive cuts from one music phrase and causal continuity family into `PLANNED_MULTI_SHOT_SOURCE`. The pack owns a contiguous scene plan with unique cuts, scene-specific references, action/camera/edit-out, and explicit Korean `15초 N숏` markers. Do not pack unrelated shots or use attachment order as chronology.
- Do not create or describe a CLI scheduler prompt. The foreground wait contract records state only; project paths, scene IDs, reference lists, prompt checks, safety rules, and branching stay in `resume_contract.json` and the live workflow.
- Runway upload handles are temporary ASCII symlinks created from approved registry assets; never scatter upload copies into Downloads or chat workspaces. Verify exact chooser name plus enlarged Runway content, then delete the alias immediately.
- When No-I2V is requested mid-project, switch only future unsubmitted blocks. Preserve submitted jobs and all registered media/provenance; do not create a No-I2V-specific scheduler, QC, edit, or package branch.
- Seedance reference input is mode-specific: `standard_i2v` uses the approved per-cut source frame plus the minimum recurring-character `TRIPTYCH`/deterministic crop; `no_i2v_reference_native` intentionally omits per-cut frames and uses only the minimum approved reusable identity/environment references. Keep operational paths/settings in the handoff package, but place a concise natural-language visible-function `@ImageN` sentence in the visual prompt whenever it disambiguates background, identity, action, or prop anchors; explicitly say those anchors are not a time sequence.
- Keep ordinary knowledge selection to six sections/9,000 characters. The packet may include 2D, 3D, live-action, camera, risk, method, and audio guidance selected by the Planner; full wiki/raw/archive and Notion work logs are not default prompt context.
- Preserve the Higgsfield preference as a knowledge ranking, not a new agent/model/provider: camera-first routing, temporal chain, one dominant movement, motivated physical layers, duration budget, explicit end frame, and product/UGC tactile proof take precedence over generic camera inspiration.
- Default recurring-character identity asset is `CHAR_<ID>_TRIPTYCH_R<n>`: left headless front body, middle back body with head, right large 3/4 portrait. Bind those roles explicitly in the model-facing prompt, use deterministic crops for fragile shots, keep state changes as separate assets, and require a 10/10 stress gate.
- Use the Hell Grind prompting adapter as a bounded shot-contract compiler: exact entity count, source roles, locked geography, complex-shot occupancy, timed physical beats, acting/audio, positive proof constraints, and one-clause revisions. It never overrides Korean prompts, duration/length limits, or Seedance UI authority.

## Known Pitfalls

- Never leave an archived `SKILL.md` under `~/.codex/skills`; it can remain discoverable as a live skill.
- A skill must not refer to a policy file that the deployment script does not install.
- Do not add a second Seedance UI instruction source to director, MV, AGENTS, lane, or scheduler files.
- Do not turn wiki retrieval into a prompt agent, RAG service, scheduler, or background indexer. It is a local deterministic catalog lookup inside the existing sequential Seedance lane.
- Do not reinterpret deterministic Sol/Luna phase routing as a model-specific prompt bridge, prompt worker, or parallel agent. The owning lane still writes its own prompt and the handoff is file-backed attestation.
- Do not store real media under `lanes/` in v4 or soften `MEDIA_HARD_GATE` into a warning/force bypass.
- The local `codex-harness-kit` wrapper may point to a missing `~/.codex/tmp/codex-harness-kit/dist/src/cli.js`; record the blocker and recover harness state from repo files instead of repeatedly guessing paths.
- Lexical paste dispatch may return before React commits. Poll the normalized editor content and hash; never trust the immediate DOM length. Refuse non-empty editor replacement because it can append a duplicate prompt.
- Runway Unlimited can show a blue-looking Generate button while enforcing one active job. A `Please wait for your last generation to complete` toast means queue full; do not re-click or switch to Credits Mode.
- Two-card acceptance is positive capacity evidence and makes queue target 2. Temporary target 1 requires the exact visible queue-capacity toast from the second-submit attempt; gray/empty UI and operator inference are invalid. When that one-slot queue empties, automatically retry target 2 on the next batch.
- `status.json.attested_blocks` is positive shelf evidence. Do not claim `EXHAUSTED` or `ALL_BLOCKED` while an attested block is absent from current/armed/next/history unless it is explicitly listed in `blocked_attested_blocks` with evidence.
- A written resume contract is not executable automation. `QUEUE_FULL_WAITING` is valid only while `queue_runtime.json` records a live foreground `wait_pid`; once elapsed it becomes unconsumed continuation debt until a visible `queue-sync --from-wake`. Legacy projects may store this state under `i2v/seedance/`; do not require a v4 manifest just to continue their queue.
- Do not treat “single action,” short final edit use, or a 5s/10s board default as duration authority. Shortening the 15s workflow default needs explicit `user:` or `brief:` evidence; a named Planner revision alone is not enough. Changing the lock requires re-attestation before UI operation.
- Do not trust Runway's remembered model selector or a prior card/checkpoint. The production default is Seedance 2.0, and the combined model+duration receipt must be fresh for the current block. A recovery example or checkpoint naming 2.5 is invalid and must be rebuilt from visibly corrected 2.0 state before submission.
- A running CLI does not hot-reload newly deployed skills/contracts. If its writes contradict a newer project lock, pause/terminate that stale owner before correcting files and restart one fresh owner from current status. Otherwise the old context can overwrite the fixed workflow after deployment.

## Open Questions Worth Tracking

- Questions that are not blockers today but should not disappear.

## Seedance user-example handling — 2026-08-24

When the user supplies good Seedance examples, preserve their directing structure but actively repair token aliases, cast identity collisions, language drift, timeline gaps, and contradictory constraints. The user expects durable updates to both the canonical prompting skill and executable harness, with regression tests—not a prose-only note. Do not retain full raw example text when a privacy-safe distilled rule and fixture are sufficient.

## Seedance example authority correction — 2026-08-24

The user explicitly corrected the hierarchy: the five supplied Seedance examples are not merely evidence to be filtered through older rules. They outrank general prompting defaults. Preserve their density, compound camera paths, temporal acting detail, native dialogue, audio ownership, and specific constraints. Normalize only what provider mechanics require; never describe the examples as subordinate inspiration again.

## Runway Browser Owner

- Seedance production uses one visible, logged-in Aside `app.runwayml.com` tab only. Never fall back to Chrome, Safari, the Codex in-app browser, connector/API, or a second browser session.
- Primary controller is the exact-session CLI helper documented in `codex-skills/seedance-prompt-en/aside-operator.md`; do not retain a separate AppleScript DOM route.
- If Aside control is unavailable, stop that UI route with `BLOCKED_ASIDE_CONTROL_UNAVAILABLE` and the exact required user action; do not reinterpret `어사이드` as `알아서`.

## Generated-vocal naturalness preference

- The user explicitly rejects the vocal sound of `링크 업!` and `리와인드 없는 오늘` as obvious AI output. Those performances are negative references only.
- Use `/Users/gnudas/.codex/skills/music-director/references/vocal-naturalness-qc.md` as the canonical listening gate. Male and female vocals are both allowed; stable human identity, fluent Korean diction, breathing, dynamics, tuning, and restrained vibrato determine acceptance.
- ASR, stems, onset timing, waveforms, and prompt quality cannot produce a PASS without full-track playback.

## Opt-in Toonkit 2D animation grammar — 2026-09-02

- Exact user trigger: `툰킷 문법을 적용해봐` (or explicit Toonkit/12-laws equivalent) enables `toonkit_2d_snappy_v1` only for affected 2D/stylized animation blocks.
- Write a visible Korean pose-to-pose beat: hold → anticipation → short acceleration/action → controlled overshoot → sharp settle → delayed hair/sleeve follow-through → final hold. Lock start/end pose, contact limbs, silhouette, one independent simple camera path, and one action per planned scene.
- Put `motion_grammar_profile` and `prompt_rules_used` only in the package; never paste profile/process wording into the model-facing prompt. Keep the project duration lock and scene/cut plan authoritative.

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


## Scheduled/QC closeout reliability

Use the canonical Seedance production branch for native schedule state and runtime seedance_qc template for coverage. The 2026-09-14 release fixes local/native cadence drift and current-scope history false positives, reuses source-bound reviewed intervals, and keeps frame samples separate from playback/audio. It does not automate perception or prove the next due run. See docs/releases/2026-09-14/scheduled-production-qc.md; do not clone the rules into project folders.


## 퇴역한 타이포 참조
정선 타이포 스킬 폐기 기록과 검증은 `docs/contracts/2026-09-22-retire-jeongseon-typography.md`에 있다.

## Seedance production language
The shared Seedance Handoff contract owns the standing English direction
default; spoken Korean remains literal. Non-default Korean directions require
scoped explicit intent. See docs/contracts/2026-09-12-seedance-explicit-english.md
and docs/releases/2026-09-29-seedance-english-default.md.

## Disposable QC retention

When explicitly requested, register and review new QC copies, then remove the exact owned copy from Trash as well under recorded permanent-QC permission. Reuse valid scoped approval rather than reasking per file or routine production phase. User-selected files, original assets, other Trash entries and cloud outputs remain protected. Preserve delete intent, source/report hashes and truthful unverified checks; no full-video/audio PASS from frame samples. Installed lifecycle and verification: docs/releases/2026-10-13-disposable-qc/release.md.
