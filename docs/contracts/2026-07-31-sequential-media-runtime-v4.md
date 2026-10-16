# Sequential media runtime v4 contract — 2026-07-31

## Objective

Simplify the Codex video-team workflow so prompt ownership stays inside the
production lanes, only image generation may fan out (maximum three workers),
Seedance prompts are reliably Korean, and every new project's media is kept in
one human-readable project-local library instead of being scattered under
lane/session folders.

## User decisions

1. Remove the standing GPT-5.6 Sol prompt-authoring agent and runtime bridge.
   The one-time Sol workflow auditor used for this review is complete and is
   not part of production.
2. The owning lane writes its own prompts: Image Creator writes image prompts;
   Seedance writes Korean video prompts. Image workers execute immutable prompts
   and do not rewrite them.
3. Image generation may run up to three workers concurrently. Planning,
   prompting, Seedance operation, QC, editing and packaging stay sequential.
4. When the Runway queue is full, keep one 15-minute foreground tool wait in the
   same Codex turn and browser. It is not an automatic scheduler: the turn must
   remain attached, consume the tool result, and re-read the visible board. Do
   not create a detached daemon, second agent, cron, or second browser.
5. Apply the new media layout to newly initialized projects only. Existing
   projects remain legacy unless the user explicitly requests migration.
6. New projects use one project-local, Finder-friendly `media/` tree. `lanes/`
   contains status, prompt, manifest and QC text only; it is not a media store.
7. Eligible temporary files are moved to the macOS Trash within 24 hours after
   they are proven inactive and non-canonical. Trash is not emptied
   automatically.
8. Canonical registration/promotion is a hard gate for new projects; warnings
   alone are insufficient.
9. Runway upload selection uses a temporary helper-owned ASCII symlink to the
   approved registry asset. No upload copy may be scattered into Downloads,
   chat workspaces, or another project, and the alias is removed immediately
   after enlarged-thumbnail verification.
10. No-I2V is a generation mode inside this same full runtime, not a separate
    team, lane chain, or reduced workflow. It changes only the image/reference
    strategy and the amount of shot design carried by the Korean Seedance
    prompt.
11. In `no_i2v_reference_native`, reuse the minimum approved identity and
    environment references, generate only missing reusable references, and do
    not create per-cut styleframes/start/end/keyframes. Music lock, planning,
    prompt ownership, media registry, QC, editing, packaging, cleanup, spawn,
    provider, and safety contracts remain unchanged.
12. A mid-project No-I2V request changes only future unsubmitted blocks in the
    same project. Submitted provider jobs and all registered media/provenance
    remain intact.
13. Creative production knowledge is stored as tagged wiki pages rather than
    copied wholesale into every skill. Planner classifies each block by visual
    medium, project type, generation mode, shot role, camera, risk, method, and
    audio; a local deterministic router selects only the matching sections.
14. Ordinary Seedance authoring reads at most six selected sections and 9,000
    characters. The whole wiki, raw sources, archives, project logs, and Notion
    logs are not automatically injected. A targeted lookup is reserved for a
    catalog conflict or genuinely new failure class.
15. Within creative knowledge, the Higgsfield community synthesis is preferred
    after the latest user instruction, project/style/identity/medium locks,
    approved references, and operational/safety gates. It supplies camera-first
    routing, temporal action chains, physical motion translation, duration
    budgets, motivated layers, and explicit end frames; community wording,
    celebrity/IP cameos, and preset IDs are never copied literally.

## New-project media layout

```text
media/
  01_sources_원본자료/
  02_audio_음악/
  03_characters_캐릭터/
  04_images_candidates_이미지후보/
  05_images_approved_이미지승인/
  06_videos_candidates_영상후보/
  07_videos_approved_영상승인/
  08_edit_편집/
  09_final_최종본/
  90_work_작업중/
  99_archive_보관함/
```

`asset_registry.sqlite` is the machine source of truth for stable asset IDs,
hashes, revisions, state, provenance and current paths. Human-facing media
files remain in the numbered folders; filenames and sequence numbers are views,
not identity.

## Temporary-file eligibility

A file is eligible for 24-hour Trash cleanup only after all checks pass:

- it is an upload/import staging copy, rejected retry, unselected candidate,
  exact duplicate, proxy/test render, or redundant unchanged-state screenshot;
- it is not in an active generation, upload, QC or edit;
- an approved/canonical copy exists when one is required;
- no active manifest or queued job references the file;
- original path, SHA-256, reason and Trash time are journaled.

User-supplied sources, approved character sheets/images/videos, locked audio,
CapCut projects, final exports, delivery packages, prompts, manifests,
provenance and QC records are protected.

## Acceptance criteria

1. No active production rule requires a dedicated Sol prompt agent or
   `sol_prompt_bridge.py`.
2. Seedance prompt packages declare `prompt_language=ko-KR`; prompt and optional
   variants fail validation when Korean is absent or not dominant.
3. Seedance prompt authoring and visible Runway operation occur sequentially in
   the same Seedance lane, with prompt/package separation preserved.
4. Image worker concurrency defaults to three and cannot exceed three. No other
   production stage launches parallel agents, providers, browsers or detached
   monitors.
5. Seedance dispatch does not start `seedance_inflight_monitor.py`. A single
   15-minute foreground wait is allowed only for a prepared package while the
   visible queue is full. `resume_contract.json` is state only; valid waiting
   requires a live `wait_pid`, and elapsed time stays unconsumed until a visible
   board observation. The loop stops on completion, shelf exhaustion or a
   human-action blocker.
6. New project initialization creates the numbered `media/` tree and a valid
   asset registry, and records a schema/version marker distinguishing it from
   legacy projects.
7. New-project lane completion/QC PASS is rejected when media exists outside
   `media/` or when required canonical media is not registered in the correct
   approved folder.
8. A tested asset command can ingest, promote and revise media without using a
   filename as identity. Operations are transactional/idempotent where possible.
9. Cleanup performs a dry run by default, moves only eligible files to macOS
   Trash after 24 hours, journals every move, and never empties Trash.
10. Existing projects are not moved or rewritten by init, validate, deploy or
    cleanup unless an explicit migration command is later approved.
11. Canonical source files deploy cleanly to the live Codex skills, policies and
    video-team runtime, and deployed copies pass consistency checks.
12. An approved registry image can produce an ASCII upload symlink without
    copying media; cleanup removes only that symlink and preserves the canonical
    asset. Native chooser and Runway verification require exact alias identity
    plus enlarged visual match.
13. Project initialization accepts `standard_i2v` and
    `no_i2v_reference_native` while creating the identical lane chain, media
    schema, registry, cleanup, QC, editing, and packaging structure.
14. No-I2V image QC may reuse an already approved, registered provider-safe
    reference without forcing a new candidate. It still fails when a required
    reusable reference is missing or unsuitable.
15. Mode switching preserves submitted blocks and their provider/media state,
    and changes only unsubmitted blocks. Switching to No-I2V clears per-cut
    frame assignments for those future blocks without deleting any media.
16. Planner writes `lanes/planner/video_attributes.json`, and each routed
    Seedance block creates a bounded context file plus a selection receipt with
    attributes, reasons, source hashes, catalog hash, context hash, and budget.
17. Prompt attestation rejects missing, stale, tampered, over-budget, or
    out-of-scope knowledge packets before any visible Runway operation.
18. 2D, 3D, and live-action profiles select different medium knowledge while
    sharing a compact hot core and the matching camera/composition sections.
19. Every routed Seedance packet includes the compact Higgsfield community core,
    and blocks with shot/camera attributes select its camera-physics section
    ahead of general camera knowledge without exceeding the packet budget.

## Verification

- Python compile and unit tests for runtime scripts.
- Temporary-project init test for media tree and registry schema.
- Asset ingest/promote/revision and hard-gate tests.
- Korean prompt validation and attestation tests.
- Parallelism cap and no-detached-monitor tests.
- Foreground-wait/resume-contract integrity and stop-condition tests.
- Active-tree consistency grep excluding archive/history.
- Deployment dry run, deployment, then source-versus-live comparison.
- Wiki catalog lint plus profile-selection smoke tests for 2D, 3D, and
  live-action blocks.

## Out of scope

- Automatic migration or cleanup of existing video-team projects.
- Permanent deletion or automatic Trash emptying.
- Public upload, publish, email or contest submission.
- Replacing the approved image generation provider, Seedance or CapCut.
- Maintaining a second active No-I2V runtime or a No-I2V-specific lane,
  scheduler, QC, edit, package, or safety policy.
