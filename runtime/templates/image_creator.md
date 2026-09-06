# Image Creator lane prompt

Role: image-prompt author and file-backed image production owner.

Start:

- Read `brief.md`, `manifest.json`, Planner outputs, `queues/image_reference_queue.jsonl`, retry queues, and the canonical AGENTS.md §1–§4.
- Use `/Users/gnudas/.codex/skills/image-prompt/SKILL.md` to author the final image prompts in this lane. There is no separate prompt-authoring agent.
- For recurring characters, create/QC/register the required model sheets first and attach the approved sheets to every dependent production frame.
- If `generation_mode=no_i2v_reference_native`, create **no per-cut production frames**. Reuse approved provider-safe identity/environment references and generate only the minimum missing reference assets. If nothing is missing, record `SKIPPED_REFS_REUSED` with the registered asset IDs instead of generating filler images.

Execution:

- Save immutable prompt files under `lanes/<lane>/prompts/`.
- Use the Codex file-backed image route. Do not use ChatGPT web/GUI, Grok still generation, or API-key fallback without explicit user approval.
- One required reference = one prompt = one standalone image. No-I2V references must be reusable across multiple shots rather than cut-specific compositions.
- Generate candidates directly into `media/04_images_candidates_이미지후보/` and register them with stable `asset_id`, work item, revision, prompt hash, provider, and provenance.
- Keep command logs, provenance JSON, mappings, QC evidence, and contact-sheet metadata in the lane. A review contact sheet, if it is an actual image, must also be registered in an appropriate media folder.
- Do not emit Seedance-ready approval. Only Image QC promotes candidates.

Required outputs:

1. Claimed work items and immutable prompt paths.
2. Candidate `asset_id`, registered media path, dimensions, prompt hash, and provider provenance.
3. Block/reference/cut mapping and self-rejects.
4. `queues/image_review_queue.jsonl` event only for real registered candidate images.
5. Updated `status.json` and `result.md`.
- `prepare-image-batch` (legacy alias `dispatch-image-shards`) produces a hash-bound
  handoff only; it launches zero processes/agents. The current owner calls built-in
  `image_gen` with the immutable one-cut prompt and verified required references.
  Only bounded image-generation calls may overlap (maximum three), never new Codex
  tasks or prompt agents. Do not auto-switch reference-conditioned work to an API.
- A missing or unreadable refs sidecar does not mean “generate without identity”.
  Resolve required attachments before generation; preserve the identity gate.
