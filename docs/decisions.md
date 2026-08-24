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

### 2026-08-21 - Replace the default character-sheet bundle with a three-panel identity triptych

- Context: The user explicitly asked to adopt the public Hell Grind project's three-role character reference and its production prompting lessons. The previous workflow required a one-figure provider sheet plus a large mandatory turnaround/expression/pose/prop/scale package, while Seedance treated every multi-panel identity asset as contamination. That made the face authority ambiguous and the default lock unnecessarily heavy.
- Decision: New recurring identities use one text-free neutral 16:9 `CHAR_<ID>_TRIPTYCH_R<n>`: headless front body at left, back body with head at center, and one large 3/4 portrait at right. The front head omission prevents a tiny full-body face from competing with the portrait and must remain a clean non-graphic studio crop. Optional deterministic face/front/back crops inherit the master hash; story-specific hand/prop/scale sheets are created only when needed. Lock requires 10 varied identity tests at 10/10.
- Prompting consequence: Seedance receives the full triptych or the minimum crop with explicit Korean role binding and exclusion of the gray background, seams, and missing head from scene content. A bounded adapter adds exact entity counts, reusable GEO locks, complex-shot first-frame occupancy, timed physical beats, performance/audio blocks, positive proof constraints, and one-clause revision logs without replacing the Korean prompt, duration, length, or UI authority.
- Release boundary: Existing approved assets remain valid until their next major lock revision. The old vertical editorial-bible presets in the local Korean-women skill were moved to a dated archive rather than deleted.

### 2026-08-24 - Make Aside the sole Runway production owner

- Context: The user explicitly corrected the Seedance browser route after the operator misread `어사이드` and opened Chrome. The old live contract still named Chrome as the source of truth.
- Decision: `codex-skills/seedance-prompt-en/` now assigns Runway production to one visible, logged-in Aside tab only. Chrome, Safari, the Codex in-app browser, connector/API, and any second browser route are prohibited fallbacks.
- Consequences: If Aside control or its visible Reference selector is unavailable, production records `BLOCKED_ASIDE_CONTROL_UNAVAILABLE` with one exact user action instead of silently changing browsers.
- Follow-up: Keep browser-owner wording and enforcement only in the canonical Seedance skill; do not duplicate it in project rules or other role skills.
