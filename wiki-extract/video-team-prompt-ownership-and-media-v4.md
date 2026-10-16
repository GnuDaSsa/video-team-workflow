# Video-team prompt ownership and media v4

Canonical live page: `/Users/gnudas/wiki/concepts/video-team-prompt-ownership-and-media-v4.md`

## Durable decisions

- No dedicated Sol/Terra/model-specific prompt agent or runtime bridge.
- Image Creator owns image prompts; up to three bounded non-agent workers execute immutable prompts.
- Seedance lane owns final Korean prompts, local attestation, and serial Runway production.
- All stages except image generation are sequential; providers and browsers never run in parallel by default.
- New projects use one numbered bilingual `media/` tree plus `asset_registry.sqlite`; `lanes/` is metadata-only.
- Registry/media mismatches are non-bypassable hard gates.
- Inactive intermediate work moves to macOS Trash after at least 24 hours with a restoration journal; Trash is never emptied automatically.
- A full Runway queue uses one state-derived 15-minute wake in the same Codex task/browser, never a resident observer or extra agent.
- The scheduler prompt is only a short wake signal; state, scene data, references, and branching stay in `resume_contract.json` and the live workflow.
- Runway uploads use a helper-owned temporary ASCII symlink to an approved registry asset. Never create upload copies in Downloads or chat/session work folders; verify the exact chooser filename and enlarged Runway thumbnail, then remove the alias immediately.
- Existing projects remain untouched unless explicitly migrated.
- No-I2V is `generation_mode=no_i2v_reference_native` in this same runtime, not
  a separate team. The entire rail stays active; only reference/image strategy
  changes to minimum approved reusable references, minimum new image creation,
  and prompt-heavy Korean Seedance shot generation.
- A mid-project No-I2V request changes only future unsubmitted blocks in the
  same project. Submitted jobs and registered media/provenance are preserved.

Implementation contract: `docs/contracts/2026-07-31-sequential-media-runtime-v4.md`.
