# Decisions

Record notable technical or product decisions here so they do not live only in chat history.

## Entry Template

### YYYY-MM-DD - Short Decision Title

- Context:
- Decision:
- Consequences:
- Follow-up:

### 2026-07-21 - Deploy Chrome-hybrid Seedance package with bundled policies

- Context: Fable/Grok updated the GitHub workflow to use one Chrome Runway board, phase-locked Codex tools, dual in-flight capacity, and explicit approval before agent/scheduler fan-out.
- Decision: Keep `seedance-prompt-en` as the single live Seedance contract; deploy the two referenced policies to `~/.codex/video-team-policies/` as part of `tools/deploy_skills_to_codex.sh`.
- Consequences: The local skill no longer has broken relative policy references, and an archived operator skill cannot be discovered as active.
- Follow-up: Use the Chrome hybrid route only when its actual Codex Computer Use/Chrome-plugin capability is available; do not pretend a missing capability succeeded.

### 2026-07-28 - Arbitrate the video-team rule set (7 user decisions)

- Context: generations were non-deterministic — Seedance silently disabled audio, uploads that worked one day failed the next, quality drifted. Diagnosis found five authority layers (~3,000 lines) each declaring itself final, with pairwise contradictions. Forensics on two live projects confirmed the cost: the independence-activist project had run 14 days across 68 seedance session folders (1.5 GB, 467 PNG, 36 MP4) with the rail's canonical asset folders still empty, and had grown its own project-local rules file — a sixth authority layer — because the canonical ones disagreed. The newest project stalled after the director lane with zero outputs.
- Decision: seven user rulings, applied across the repo.
  1. Audio toggle always ON; "no BGM" is prompt wording only. (Root cause: the preference was stored in the settings field, and the observer protocol literally said "verify Audio Off".)
  2. Character sheets are always attached when a recurring character appears; the runtime's INVALID_DIRECT_CHARACTER_SHEET_ROUTE ban is retired. Field practice was already doing this.
  3. + 6. Upload uses one fixed ladder: asset selector → one retry → drag only with explicit user approval → BLOCKED. Drag is demoted from canonical to last resort, and "get through it however works" is replaced by climbing predefined rungs.
  4. Runway runs in Chrome; the runtime file was the last Safari holdout.
  5. All prompt authoring is gpt-5.6-sol high, resolving a deadlock where §2.1 required terra but attestation required sol.
  7. I2V defaults to Seedance; Grok only when the user names it. music-video-production-team's role 5 was still Grok-first.
- Consequences: each contested behaviour now has exactly one owner, and an explicit authority order sits in both AGENTS.md files. Valid corrections from the project-local rules file were promoted to `seedance-field-lessons.md`; project-specific content stayed with the project. Local rules copies inside project folders are banned — exceptions go to `docs/project_overrides.md`.
- Follow-up: `runtime/AGENTS.md` is now tracked here but the live copy is still at `~/Documents/Codex/video-team-runtime/AGENTS.md`; deploying it is not yet automated. Nothing has been deployed to `~/.codex` — the fixes are on `fix/rule-arbitration-20260726` awaiting review. The deploy script now refuses to run while live is ahead of the repo.

### 2026-07-31 - Sequential media runtime v4 supersedes prompt bridges and scattered lane media

- Context: The user rejected the standing Sol prompt role, wanted Seedance prompts reviewable in Korean, allowed image generation concurrency up to three, and identified media spread across lane/session folders as an ongoing maintenance failure. A one-time Sol audit confirmed contradictory Sol/Terra/English rules, empty canonical asset folders, 151 exact duplicate copies (~509.7 MB), and a resident monitor that kept adding evidence files.
- Decision: Production prompts are lane-owned. Image Creator writes image prompts and may feed immutable prompts to at most three bounded non-agent workers; Seedance writes and attests Korean prompts and then operates Runway serially. Every other stage/provider/browser remains sequential. New projects use a numbered bilingual `media/` tree and `asset_registry.sqlite`; registry consistency is a non-bypassable hard gate. Eligible inactive intermediates move to macOS Trash after at least 24 hours during normal runtime commands, with a journal and no Trash emptying. Queue-full continuation is one same-turn 15-minute foreground tool wait, not a scheduler or resident observer/process.
- Consequences: `sol_prompt_bridge.py` and `seedance_inflight_monitor.py` are retired; existing projects are not migrated; new projects have stable asset IDs/revisions and media promotion paths. The deploy script now owns runtime scripts/templates and archives retired live files.
- Follow-up: Run v4 regression tests and deploy/source-live comparison on every workflow release. A future legacy migration needs a separate explicit user request and contract.

### 2026-08-01 - Seedance upload aliases and bounded foreground wait

- Context: The first live v4 cycle selected a wrong Runway asset during native-picker navigation, created a copied upload file in a chat work folder, returned a false prompt mismatch before Lexical committed, failed to apply duration through generic `set_value`, and embedded the entire resume procedure in the heartbeat prompt. Runway Unlimited also displayed a blue-looking Generate control but rejected the second job with a queue-capacity toast.
- Decision: Uploads now use a helper-owned ASCII symlink to an approved registry asset, exact chooser filename selection, enlarged-thumbnail comparison, and immediate alias cleanup. Queue continuation stays in one foreground tool session; `resume_contract.json` records state but schedules nothing. `paste-prompt` requires an empty editor and polls Lexical commit instead of replacing/appending blindly. Queue-capacity toast is `QUEUE_FULL_WAITING`, and two in-flight jobs are a target only when the account mode accepts them.
- Consequences: No upload copies belong in Downloads/chat workspaces; wrong slots are removed without `Reset settings`; duration requires visible closed-toolbar verification. The current external staging copy was moved into the project registry as inactive `staging` and remains eligible for the 24-hour Trash policy.

### 2026-08-01 - No-I2V is a generation-mode delta, not a separate workflow

- Context: A first correction incorrectly treated No-I2V as a standalone team/runtime with its own shortened execution policy. The user clarified that No-I2V exists to minimize references and new image generation and solve more of each shot through prompting; every other part of the video-team workflow remains the same.
- Decision: Add `generation_mode=no_i2v_reference_native` to the canonical v4 runtime. Standard and No-I2V projects share the complete lane chain, media registry, Korean prompt ownership, cleanup, QC, editing, packaging, spawn, provider, foreground wait, and safety contracts. No-I2V reuses the minimum approved identity/environment references, generates only genuinely missing reusable references, creates no per-cut source frames, and shifts shot composition/blocking/action/camera/atmosphere/timing into the Korean Seedance prompt.
- Consequences: A user request for No-I2V during production updates only future unsubmitted blocks in the same project; submitted provider jobs and all registered media/provenance remain preserved. The old `no-i2v-team-runtime` is compatibility/legacy provenance only and delegates new init to the canonical runtime.
- Follow-up: Review shared queue-continuation policy separately; it is not a No-I2V mode difference.

### 2026-08-01 - Split Seedance reference inputs by generation mode

- Context: The runtime correctly omitted per-cut frames in No-I2V, but the shared Seedance contract still contained one unconditional sentence requiring `styleframe(s) + PROVIDER_REF`. The Creative checklist also risked putting the ordered reference-role map into the visual prompt despite the prompt/package isolation rule.
- Decision: `standard_i2v` uses approved per-cut source frames plus mandatory recurring-character provider-safe identity sheets. `no_i2v_reference_native` uses no per-cut frame and only the minimum approved reusable identity/environment references, while its Korean prompt carries the missing composition and temporal direction. Ordered `@ImageN` roles remain in `<BLOCK>_package.md`, not as operational text in `<BLOCK>_prompt.txt`.
- Consequences: Both modes share the same character identity gate and Korean visual grammar without forcing extra images in No-I2V or contaminating the Runway prompt with attachment metadata.

### 2026-08-01 - Route video knowledge by declared production attributes

- Context: The user's accumulated Seedance creativity knowledge covered 2D, 3D, live action, camera grammar, feature methods, audio, and recurring failure modes, but active prompting either loaded only a small general skill or risked opening large wiki/history pages. The user wanted reusable knowledge without paying the context cost of the entire wiki.
- Decision: Store durable creative knowledge in curated wiki pages and a section-level catalog. Director/Planner declare normalized project/block attributes; a deterministic local router selects at most six matching sections within 9,000 characters. Seedance reads only that packet, writes its Korean prompt in the same lane, and records the selection receipt in the prompt package. This is retrieval context, not a new prompt agent or authority layer.
- Consequences: 2D, 3D, live-action, camera, risk, method, and audio guidance can evolve independently. Attestation hashes the attributes, catalog, selected sources, and context, so stale or tampered knowledge blocks Runway submission. Notion remains a work-log destination and is not auto-injected into prompting.
- Follow-up: Add new knowledge only after it becomes a durable rule, register an exact page/section in `_meta/video-knowledge-catalog.json`, and keep per-project incidents in project logs until promoted.

### 2026-08-01 - Prefer Higgsfield community grammar during Seedance authoring

- Context: The user explicitly requested that knowledge learned from the Higgsfield community lead Seedance video prompting. The existing Creative grammar already contained the study's camera families and motion patterns, but the new bounded wiki router did not guarantee that provenance a slot or rank it ahead of generic camera sections.
- Decision: Add a compact Higgsfield community concept sourced from the prior 126-prompt/100-motion/51-project study. Its compile core is always selected, and its matching camera-physics plus product/UGC sections receive the highest creative catalog priority. Hard authority remains unchanged: latest user instruction, project/style/identity/medium locks, approved references, and operational/safety gates rank above community knowledge.
- Consequences: Prompt receipts now expose `priority_class` and `provenance`; general camera knowledge becomes supplemental. Community wording, celebrity/IP cameos, and motion preset IDs are never copied literally.

### 2026-08-10 - Treat story progression as a pre-attestation gate

- Context: In the Fiji international-cooperation project, individually valid and visually consistent Seedance blocks filled the Runway queue, but the user correctly judged that the story itself was not advancing. Standalone shot quality, tropical art direction, and accepted-card throughput had been mistaken for narrative progress.
- Decision: Before attesting block N, the Seedance lane must compare it with the preceding story block and record `incoming_story_state`, `narrative_delta`, `causal_bridge`, and `outgoing_story_state`. A repeated location, prop, or mood without new information, changed action/relationship, complication, or resolution is repaired before submission.
- Consequences: Queue order, card count, visual polish, and a new background cannot satisfy the story gate. Each opening action must follow from the previous block, and each closing frame must hand off a concrete state to the next block.
- Follow-up: Add machine validation for the `story_progression` package fields when the prompt-pack schema next changes; until then, enforce them in the Seedance authoring/critic pass.

### 2026-08-10 - Enforce declared scene density with immutable cut ownership

- Context: The Fiji international-cooperation project has 46 picture cuts plus a CapCut-only final-title hold. The user requested roughly two planned scenes per 15-second Seedance clip, with editorial speed handled later, and explicitly prohibited regenerating scenes already covered by existing jobs.
- Decision: Treat a user-declared scenes-per-clip value as a prompt-complexity budget for all unsubmitted blocks. Maintain a cut-ownership ledger in which each cut ID belongs to exactly one queued, accepted, completed, or planned generation intent. Existing submitted jobs keep ownership; supplemental blocks use uncovered cuts only, and a retry requires `QC_FAILED_RETRY_ALLOWED`.
- Consequences: The 32 picture cuts already reserved by B01–B08 remain locked, while the 14 uncovered cuts are paired into seven supplemental 15-second clips, B09–B15. Editorial retiming no longer justifies overpacking prompts, and edit-only title beats remain in CapCut rather than becoming AI-rendered text scenes.
- Follow-up: Add schema validation for scene-density, `covered_cuts`, prior owner, duplicate-check verdict, and retry state when the prompt-pack schema next changes.

### 2026-08-18 - Make Seedance queue continuation observable and fail closed

- Context: The written workflow said to keep two Runway jobs active and resume the same task after 15 minutes, but the first implementation confused timer completion with model continuation. In the KiiiKiii run, `queue-wait` registered at 02:26 and wrote `WAKE_FIRED` at 02:41, yet no board recheck or queue update occurred for more than five hours; the operator resumed only after the user complained. `sleep()` had changed JSON but had not created a future Codex turn.
- Decision: Keep `queue-sync` as the canonical visible-board reducer and make `queue-wait` a bounded foreground tool long-poll, never a scheduler. Persist a live `wait_pid`; timer completion writes `WAIT_ELAPSED_RECHECK_NOT_CONSUMED`, and only a visible Runway observation plus `queue-sync --from-wake` records `WAIT_CONSUMED_BY_VISIBLE_BOARD_RECHECK`. Ordinary sync/new wait fail closed while debt remains. If the shell yields a session ID, the owning Codex turn must poll it until exit and may not emit a final answer. Support both v4 and legacy layouts; treat legacy `WAKE_FIRED` as unconsumed migration debt.
- Consequences: Queue-full remains intermediate. The lane gate accepts waiting only when a matching v4 contract and live foreground `wait_pid` exist. An elapsed timer is explicitly incomplete, not evidence of automation. Three unchanged in-queue observations after consumed waits become the explicit stalled-provider blocker.
- Follow-up: The already-running legacy CLI must adopt the controller at its next board observation; do not inject commands into or start a second browser loop alongside that owner.

### 2026-08-19 - Make generation duration a workflow-owned lock

- Context: The KiiiKiii project had an explicit 15-second correction in prose, but C13 onward prompt packs later inferred 5 seconds from one-action/final-edit complexity. Attestation approved those packs because it checked prompt form but not a project-owned duration decision; the Runway preflight then faithfully applied the already-wrong pack value.
- Decision: Planner/project workflow exclusively owns provider generation duration and records it in `generation_duration_lock.json`. The workflow initializes Seedance at 15 seconds; 5–14 seconds requires explicit `user:` or `brief:` evidence, and a `planner_revision:` alone cannot shorten it. Every Seedance pack declares `duration_sec`; attestation requires `--project` and rejects a mismatch. The canonical Seedance helper rechecks unchanged pack/lock hashes and the visible closed-toolbar duration immediately before Generate.
- Consequences: Prompt complexity, one-action shots, final edit trim length, and an existing Runway UI value can size action inside the lock but cannot choose 5/10/15 seconds. A lock revision invalidates old attestations. Unsubmitted mismatches are held and re-authored; submitted provider jobs remain immutable audit history.
- Source-yield refinement: For short or cut-dense final videos, Planner normally keeps the 15-second generation and groups 2–4 consecutive, causally related cuts into one final-production `PLANNED_MULTI_SHOT_SOURCE`. Each scene carries contiguous timing, unique cut ownership, scene-specific references, action, camera, and edit-out. This is distinct from unified-board PREVIS and never treats attachment order as story order.
- Stale-owner correction: A long-running legacy CLI was observed rewriting C18 from 5s to an unauthorized 10s pack 15 seconds after the new 15s lock was written. Live file deployment does not retroactively replace a running model's loaded context. The stale writer was reversibly paused; future contract changes require a fresh single CLI owner to reload runtime/skill/project state before it may write.
- Follow-up: Re-map and re-author the KiiiKiii C18+ shelf into justified 15-second single/multi-shot sources before any further Generate action. Keep queue continuation mechanically independent from duration selection.

### 2026-08-21 - Replace the default character-sheet bundle with a three-panel identity triptych

- Context: The user explicitly asked to adopt the public Hell Grind project's three-role character reference and its production prompting lessons. The previous workflow required a one-figure provider sheet plus a large mandatory turnaround/expression/pose/prop/scale package, while Seedance treated every multi-panel identity asset as contamination. That made the face authority ambiguous and the default lock unnecessarily heavy.
- Decision: New recurring identities use one text-free neutral 16:9 `CHAR_<ID>_TRIPTYCH_R<n>`: headless front body at left, back body with head at center, and one large 3/4 portrait at right. The front head omission prevents a tiny full-body face from competing with the portrait and must remain a clean non-graphic studio crop. Optional deterministic face/front/back crops inherit the master hash; story-specific hand/prop/scale sheets are created only when needed. Lock requires 10 varied identity tests at 10/10.
- Prompting consequence: Seedance receives the full triptych or the minimum crop with explicit Korean role binding and exclusion of the gray background, seams, and missing head from scene content. A bounded adapter adds exact entity counts, reusable GEO locks, complex-shot first-frame occupancy, timed physical beats, performance/audio blocks, positive proof constraints, and one-clause revision logs without replacing the Korean prompt, duration, length, or UI authority.
- Release boundary: Existing approved assets remain valid until their next major lock revision. The old vertical editorial-bible presets in the local Korean-women skill were moved to a dated archive rather than deleted.

## 2026-08-24 — User prompt cases compile into conditional semantic contracts

- Treat user-supplied successful prompts as case evidence, not verbatim templates.
- Keep the final Seedance model-facing prompt Korean and normalize all external source notation to canonical `@ImageN/@VideoN/@AudioN`.
- Apply semantic checks conditionally through `prompt_rules_used`; do not force lipsync, exact-text, effect, or one-take fields onto unrelated shots.
- Fail closed before ordinary attestation for entity/reference collisions, timed-beat gaps, one-take/cut conflicts, missing physical effect causality, master-audio vocal ownership errors, exact dialogue without a performed audio guide, and required/forbidden contradictions.
- UI/queue/production procedure remains owned by the existing Seedance production contract and is unchanged.

## 2026-08-24 — User Seedance examples outrank general prompting defaults

- Authority is current explicit user instruction/brief → the five user examples → project locks → general prompting defaults.
- Safety/rights, visible provider capability, verified attachment binding, and exact user settings remain non-bypassable mechanical boundaries.
- Older brevity, one-action, one-camera, and performed-audio defaults may fill gaps but cannot dilute the examples.
- Preserve “rapid-cut tempo” inside a one-take as rapid performance and reactive handheld reframing without edits when explicitly resolved.
- Native Seedance Korean dialogue is authorized by the examples without `@AudioN` when the literal line, speaker, delivery, and listening/lipsync QC route are recorded.

### 2026-08-24 - Make Aside the sole Runway production owner

- Context: The user explicitly corrected the Seedance browser route after the operator misread `어사이드` and opened Chrome. The old live contract still named Chrome as the source of truth.
- Decision: `codex-skills/seedance-prompt-en/` now assigns Runway production to one visible, logged-in Aside tab only. Chrome, Safari, the Codex in-app browser, connector/API, and any second browser route are prohibited fallbacks.
- Consequences: Prior 2026-08-22/23 daemon logs prove repeated successful `CliBinding`/`cli.replRun` use. Production therefore binds the exact existing Runway tab through `aside repl` first; a disabled Apple Events JavaScript toggle is not a blocker while that binding succeeds. Only after CLI and permitted same-tab fallbacks fail does it record `BLOCKED_ASIDE_CONTROL_UNAVAILABLE`.
- Follow-up: Keep browser-owner wording and enforcement only in the canonical Seedance skill; do not duplicate it in project rules or other role skills.

### 2026-08-28 - Make actual playback the AI-vocal recommendation gate

- Context: The user rejected the generated vocals in `링크 업!` and `리와인드 없는 오늘` as conspicuously artificial even though earlier intro/onset and technical checks had passed.
- Decision: The canonical owner is `codex-skills/music-director/SKILL.md` with the listening checklist at `references/vocal-naturalness-qc.md`. Automated analysis may screen but cannot certify vocal naturalness.
- Consequences: Prior recommendations for those performances are invalid. A candidate with obvious synthesis artifacts is rejected regardless of composition quality; unlistened vocal candidates remain on hold.
- Follow-up: Do not duplicate the checklist in project folders; keep only user-feedback evidence and a pointer to the canonical skill.

### 2026-08-29 - Route creative prompting to Sol xhigh and operations to Luna high

- Context: The runtime launched every lane with hard-coded `gpt-5.5`, while Seedance prompt authoring and Runway/Computer Use were fused into one owner. That prevented the requested quality/cost split and made browser operation inherit the creative-author model.
- Decision: `runtime/scripts/model_routing.py` now maps Image Creator and Seedance prompting to `gpt-5.6-sol` `xhigh`; Director/Music/Planner/QC/Editor/Package and Seedance Aside/Computer Use production to `gpt-5.6-luna` `high`. Seedance is two sequential phases inside the same lane, with a local attestation handoff between them.
- Safety: Production consumes only attested packs, uses the one existing Aside Runway tab through deterministic `aside repl`, and never auto-spawns from prompting. Each Codex owner requires an exact current-conversation `--approved-spawn` token, and an existing live owner blocks another dispatch.
- Release boundary: Fresh dispatches adopt the policy; already-running owners, current cards, media, and paused project states are not rewritten.

### 2026-08-29 - Make prompt insertion file-first and 15 seconds tamper-resistant

- Context: macOS Korean IME can silently consume synthetic typing, and a duration lock could be manually edited below 15 seconds even though the normal CLI rejected that change. The user also needed an observable answer to which model a CLI lane actually used.
- Decision: Seedance visual prompts are first written as UTF-8 NFC `*_prompt.txt`; production inserts that exact file with the keystroke-free `paste-prompt --file` route. The helper rejects wrong extension, invalid UTF-8, or non-NFC input before browser contact. Duration validation now rejects every 5–14 second default/override whose current source is not explicit `user:` or `brief:` evidence.
- Visibility: Each fresh dispatch writes `lanes/<lane>/model_route.json`; `status`, `report`, `next`, and the main-app `[model-route]` label expose model, reasoning, lane, and phase. Legacy runs without route evidence remain unknown rather than being guessed.

### 2026-08-30 - Fail closed on abandoned Seedance foreground continuation

- Context: In the Blue Orbit project, SF17 card 24 was submitted but the first wait initially tracked stale card 22 because the accepted card was not immediately committed through `queue-sync`. After card 24 was corrected and one foreground wake was consumed, the owner ended with `may_stop=false` and wrote that a future owner could continue. `cycle_status()` still returned `RUNNING` because it trusted the status string without a live lane PID.
- Decision: One wait means one pending wait at a time, not one wait total. Wake 1 or 2 immediately enters the next sequential same-turn wait while the reducer remains nonterminal. Add `queue-exit-check` as a binding pre-final gate. Runtime validation now rejects `status:RUNNING` without a live owner PID and rejects every nonterminal queue with no live owner/wait, regardless of prose status.
- Consequences: A contract file, consumed wake, stale RUNNING string, or “next owning turn” note cannot hide an abandoned queue. User interruption or lost tool attachment is recorded as `BROKEN_FOREGROUND_CONTINUATION`. A resident monitor/cron remains outside the normal route and is not the correction.
- Evidence: `20260828_000807_blue-orbit-promise-2d-mv/lanes/seedance/logs/20260830_foreground_continuation_audit.md`. Card 24 later became `COMPLETED`, but its download/QC/registry backlog still kept `may_stop=false`, correctly remaining `STOPPED_INCOMPLETE` without a live owner.

### 2026-08-30 - Refill Seedance 2.0 slots before settled-card QC

- Context: Blue Orbit cards 26 and 27 both completed, proving the current board accepts two concurrent jobs. Nevertheless the controller repeatedly ran one-at-a-time because it prioritized any settled card over a free provider slot, had no receipt for already processed Completed cards, and split queue checkpointing from the foreground wait. The project also declared seven attested blocks while queue state said `ALL_BLOCKED`.
- Decision: Make target 2 the evidence-backed default. Refill a freed slot before settled-card download/QC, then process backlog while the replacement pair generates. Add persistent `--processed-job SCENE|OUTPUT` receipts. Replace production's discretionary `queue-sync` → `queue-wait` pair with atomic `queue-cycle`. Reject shelf terminal/blocked claims that contradict status-declared attested work.
- Capacity fallback: Target 1 requires exact `RUNWAY_QUEUE_CAPACITY_TOAST` evidence from the second-submit attempt. An empty one-slot queue automatically retries target 2; two visible distinct cards restore target 2 immediately.
- Safety: `queue-cycle` is still one foreground Codex tool call and same Aside tab. It creates no resident monitor, cron, scheduler, second browser, or extra agent.
- Evidence: `20260828_000807_blue-orbit-promise-2d-mv/lanes/seedance/logs/20260830_two_slot_controller_audit.md`.

### 2026-08-30 - Verify Seedance 2.0 and duration together before every Generate

- Context: The user reported intermittent Seedance 2.5 submissions even though Seedance 2.0 is the production default. The machine preflight verified only duration, while the same-session recovery example incorrectly recorded `Seedance 2.5`; recovery could therefore preserve a wrong model as if it were valid.
- Decision: `settings-verify` now requires a freshly read visible model label plus duration. It accepts only one unambiguous `Seedance 2.0` observation, rejects 2.5 or unreadable/ambiguous text, and writes a combined model+duration receipt immediately before each Generate. Recovery checkpoints require 2.0, and old 2.5 checkpoints cannot resume until rebuilt from the same session with visibly corrected 2.0 settings.
- Consequences: The production owner must open/check the model control, select 2.0 if needed, close and re-read it, then run `settings-verify --visible-model ... --duration-sec ...`. Refresh, recovery, queue wake, or deck replacement invalidates reliance on remembered UI state; every block gets a fresh preflight.
- Evidence: `20260828_000807_blue-orbit-promise-2d-mv/lanes/seedance/logs/20260830_seedance_model_20_preflight_audit.md`.

### 2026-09-02 - Add an opt-in Toonkit snappy 2D animation grammar

- Context: A public Toonkit comparison showed that the useful differentiator was not its exact 10-second four-shot arrangement, but a prompt grammar that converts animation principles into timed pose beats: stillness, anticipation, fast action, overshoot, settle, and delayed follow-through.
- Decision: Register `toonkit_2d_snappy_v1` as an explicit user-only profile. `videodirector` recognizes “툰킷 문법을 적용해봐”; `seedance-prompt-en` owns the provider-facing Korean translation and package markers. Every enabled planned scene gets one readable pose-to-pose beat, a final hold, concrete contact/silhouette locks, restrained 2D accents, and one camera path independent from the character snap.
- Consequences: The profile preserves duration, identity, style, audio, and safety contracts; it cannot silently force a 10-second/four-shot layout or become a generic live-action/default motion preset. Operational profile names remain in the package, not the provider prompt.
- Follow-up: Judge its value through generated-clip QC before widening its scope beyond explicit 2D/stylized requests.

### 2026-09-05 - Route explicit Seedance 2.5 work through a separate skill

- Context: The user wants to request Seedance 2.5 deliberately without weakening the established 2.0 default, and wants only prompting and production to branch. The immediate quality target is animation that avoids generic AI motion, weightless contact, uniform whole-frame movement, identity drift, and line/texture crawl.
- Decision: Add `seedance25-prompt-en` as a narrow natural-language version route. Explicit 2.5 requests use its `prompting.md` and `production.md`; explicit 2.0 and unversioned Seedance requests remain on `seedance-prompt-en`. Runtime rails, media, safety, approvals, one Aside tab, and foreground queue waits stay shared. The 2.5 executable is a thin model-policy adapter over the existing Runway helper, not a second UI/queue implementation.
- Consequences: Every 2.5 package names `provider_model` and `provider_skill`, production freshly proves the visible 2.5 selector before Generate, and the prompt compiler chooses Reference/Keyframe/Edit/Extend from the actual continuity or repair problem. The 2.0 guard remains fail-closed against 2.5.
- Follow-up: Judge 2.5 against real generated animation QC. Promote only repeated, verified failures into the 2.5 prompting branch; do not widen generic Seedance routing from a single project.

## 2026-09-06 — Lean same-owner workflow and verified Aside release

- User explicitly requested applying the audit, removing unnecessary subordinate
  agents/old traces, improving Seedance prompting and concrete Aside operation.
- Retire the Creative prompt-team surface and installed skill archive; preserve
  useful directing review in the same owner's `prompt-review.md`. Historical
  browser/queue filenames become pointers, not competing procedures.
- Actual Aside execution now uses exact target/session/project CLI binding,
  explicit result/error transport, in-page URL recheck and unique empty Lexical
  guards. REPL lacks global URL; tested sandbox parsing is distinct from browser
  URL validation. No browser agent, hidden upload input or front-tab fallback.
- Current pack/duration checks run again at settings preflight. Scoped regressions
  reject undecided cameras and entity-motion contamination without banning
  intentional compound direction. 2.5 Edit records verified input duration instead
  of inventing a visible duration control.
- Strict source/live manifest parity replaces a misleading deploy-safe check.
  Only the reviewed v4 dependency closure is included; unknown live skill files
  block deployment and retired files move to archive. User media/submitted jobs
  remain untouched. Source files alone do not prove production quality.
- Evidence and remaining empirical QC: `docs/releases/2026-09-06/`.

- Staged-tree review also found a hidden App Server image-task launcher and automatic reference-image API fallback. Both are retired; image batching now creates an immutable current-owner handoff without starting an agent or provider CLI.

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

## Scheduled intent takes priority over legacy waiting

Explicit scheduled-check intent is persisted in the canonical Seedance helper before draining a queue. Scheduled queue-cycle checkpoints once and returns; direct foreground wait is rejected. This local selection is not an automation registration or spawn approval. Native app registration and first-run evidence remain separate. Exit now requires a justified terminal, evidenced interruption or scheduled checkpoint, not merely may_stop=true. Scope and verified limitations: docs/releases/2026-09-07/cycle-audit.md.

## Scoped Hell Grind live-action knowledge

The user requested automatic use for photoreal work. Keep the creative content
in the existing live-action wiki profile, route stills from image-prompt and
video planning from videodirector, and reuse v4 bounded knowledge selection.
Do not install the conflicting external skills, switch providers, hide age to
evade filters, or impose cinematic effects/timings on unrelated work. Single
stills do not inherit recurring-video identity or dialogue workflow overhead.
Evidence, scoped deployment and verification: `docs/releases/2026-09-08-hell-grind/release.md`.


## Scheduled continuation and bounded QC evidence

A successful native reservation is distinct from local cadence, actual execution, and media approval. Shared Seedance snapshot/cadence checks and runtime source-bound QC coverage now enforce those distinctions. Stable reservation prompts point to current state rather than freezing mutable counts. Resolved failure is a disposition, not a PASS; repeat input failures require a causal input/spatial correction instead of more negative prose. Canonical owners and live limits: docs/releases/2026-09-14/scheduled-production-qc.md.


## 정선 타이포 참조 폐기
사용자 실패작 지정에 따른 스킬·자동 참조 제거. 단일 소유 기록: `docs/contracts/2026-09-22-retire-jeongseon-typography.md`.

## Seedance production language
The shared Seedance Handoff contract owns the standing English direction
default; spoken Korean remains literal. Non-default Korean directions require
scoped explicit intent. See docs/contracts/2026-09-12-seedance-explicit-english.md
and docs/releases/2026-09-29-seedance-english-default.md.

### 2026-09-30 — Advanced shot prompting, scoped integration
- Strengthen existing Aside core/reference/edit cards; keep 17 cards, six-card/9,000-character limits, motion notes and provenance. Codex uses optional advanced_prompting through existing selector. No engine changes.
- Project tool/cost/20-minute queue and all-scenes 15-second generation lock stay in Seongnam overrides. Preserve R4 enteral-nutrition facts, No-I2V, source lock, prior receipts and unrelated blocked goal.
- 484 native + 199 Codex regressions passed; fixtures verify delivery, not actual authorship/media quality. Existing wiki motion-page format/raw warnings remain. No memory files edited.
- Hash-guarded backup/rollback: /Users/gnudas/Documents/Codex/2026-10-01/task/prompting-integration/manifest.json and apply.py --rollback.

### 2026-10-02 — Shared reference-production transfer
- Promoted the user's project transfer to canonical creative/production/QC owners; retain existing 20-minute scheduled preference and preserve explicit foreground/other cadence. No scheduler changes.
- Role-separated references and concise causal shot cards; first-party source distinction; account-local no-credit verification; exact-session/prompt reconciliation before retry; downloaded-file and playback QC.
- Reviewed patches deployed only production/QC, with a narrow Aside pointer. Existing project style/duration/music/dimension locks, dirty files and blocked main goal preserved.
- 199 tests, syntax/diff/harness, scoped deployment hashes and author/operator entry links PASS. No generation, live behavior claim, push or memory edits.
- Backup, checks and hash-guarded rollback: /Users/gnudas/Documents/Codex/2026-10-01/task-2/common-transfer-audit/ .

## Native picker target consistency
- September AXMain proof did not update action tails. Both picker actions now always prove and use the same main window, and AXSelected must be followed by one enabled OKButton. No permission diagnosis from disabled Open alone.
- Scoped patch preserves English/idempotent input and other live drift. See `docs/contracts/2026-10-08-native-picker-target.md`; native interaction remains unverified, current generating indicator is not resubmitted.

## Scheduled registration must precede pending-work handoff
- User clarified this is workflow repair, not permission to activate the current reservation. Native scheduling remains a same-owner tool operation under specific approval; the helper cannot create a scheduler or silently change a user pause.
- Remove scheduled-mode-only exit acceptance. Queue-cycle/doctor/exit consume the existing native snapshot audit and return a concrete registration/repair step. Stable instructions read current authorized scope, not revision labels. See `docs/contracts/2026-10-08-scheduled-registration-gate.md`.

## Flow request selects composite knowledge
User explicitly corrected the design: a FLOW video-generation request is the entry to Malfoy-style compositing, not a second general/composite choice. Shared motion craft belongs in videodirector/references/flow-malfoy-composite.md and is loaded by matching editor work across providers. Only instruction routing/knowledge is deployed; Seedance CLI/Runway helpers are not a Flow execution adapter. No current project/provider/schedule mutation. See docs/contracts/2026-10-08-flow-malfoy-knowledge.md.

## Aside bounded observation
Use one existing-bridge read for modal/reference/editor/Generate affordance instead of ad hoc repeated reads. A separate timestamped receipt is observation, not lane/provider/scheduler truth. Preserve live Runway helper drift; no new owner. See docs/contracts/2026-10-09-aside-bounded-observation.md.

## Opt-in disposable QC copies

Keep temporary download ownership and truthful bounded review separate from media quality approval. The installed disposable_video_qc tool requires exact new-download receipt, one-copy limit and source/report binding. Explicit project-scoped permanent-QC permission authorizes the exact journal-owned Trash copy to be unlinked after durable delete intent, without repeated per-file approval. No broad Trash cleanup, watcher, user-file deletion or physical free-space claim. See docs/contracts/2026-10-13-disposable-video-qc.md.
