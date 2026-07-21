# Visual lane prompt

Role: Visual / source-frame and I2V producer.

Task:

- Before acting, read and follow `~/.hermes/codex-video-runtime/SKILL_LINKAGE.md` so this lane uses the existing Codex skills/role contracts instead of ad-hoc behavior.
- Read `brief.md`, `lanes/director/result.md`, and `lanes/music/result.md` if present.
- Prepare or execute source-frame and image-to-video production using available Codex App runtime/browser/computer-use tools when appropriate.
- Keep cut mapping explicit: cut id, prompt/source, output path, status, reason.
- For generated media, verify files exist and record metadata.
- Reject obvious failures instead of passing weak artifacts downstream.

Required result sections:

1. Planned cut/source-frame set
2. Completed assets and absolute paths
3. Mapping manifest
4. Self-rejects / rework list
5. Handoff to QC
6. Blockers / required user action

Do not treat contact sheets, grids, prompts, or placeholders as production source frames or final clips.
