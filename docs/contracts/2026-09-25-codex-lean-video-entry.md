# Codex lean video entry — 2026-09-25

## Evidence

- Aside's current video skill treats Jev as an optional advisory classifier, not a routine startup step. Its documented instruction reduction is 56,726 to 13,669 Unicode characters; production token/latency gains were not measured.
- The Codex global AGENTS file is 40,527 bytes and deployed runtime AGENTS is 31,042 bytes. The last observed production case used 45,908 input tokens on its first response. These are context-size indicators, not causal latency measurements.
- Local read-only timings: `video-codex-runtime next` 0.30 s, `validate` 0.06 s, codex-harness-kit validation 0.20 s. CLI execution is not the dominant measured delay.

## Scope and decision

Shrink only the Codex `videodirector` entry skill and enforce task/phase classification before optional reference reads. Advice/audit and one-asset revisions must not automatically invoke the full production path. Existing runtime rails, Astra authorship, image/character/QC, versioned Seedance UI, spawn approval, public-submission and media-evidence gates remain authoritative. Do not copy Aside's English-prompt or web-image defaults into Codex. Do not add Jev to every step; Jev advisory use requires a separate scoped decision and cannot authorize execution.

## Acceptance

1. Entry skill under 7,000 characters, with task classes and stage-specific references.
2. Core routing, media, approval and safety boundaries remain visible.
3. Skill validator and targeted/full runtime tests pass; source/live skill parity verified after targeted deployment.
4. Report that model-token and production wall-clock improvement remain unverified until a future A/B production run.

## Non-goals

No provider submission, media generation, agent spawn, Jev API call, global AGENTS rewrite, runtime lane bypass or quality-gate relaxation.
