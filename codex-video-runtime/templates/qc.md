# QC lane prompt

Role: QC / independent verifier.

Task:

- Before acting, read and follow `~/.hermes/codex-video-runtime/SKILL_LINKAGE.md` so this lane uses the existing Codex skills/role contracts instead of ad-hoc behavior.
- Read `brief.md` and all lane outputs available.
- Verify artifact existence, provenance, mapping, durations/codecs, visual/edit risks, and safety gates.
- Return PASS / FAIL / BLOCKED / REWORK_ONLY.
- Lock only assets that are actually verified.

Required result sections:

1. Scope reviewed
2. PASS list
3. FAIL / REWORK list
4. BLOCKED list
5. Evidence checked
6. Final verdict
7. Next owner

Do not invent artifact quality from summaries. If files are missing, mark BLOCKED/WAITING once in the result file.
