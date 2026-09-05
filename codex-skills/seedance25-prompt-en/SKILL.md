---
name: seedance25-prompt-en
description: Use only when the user explicitly requests Seedance 2.5 or 씨댄스 2.5. Author Korean 2.5 prompts and run the matching visible Runway production path; do not activate for generic Seedance or Seedance 2.0 work.
---

# Seedance 2.5 prompt and production router

This is the opt-in Seedance 2.5 branch. A natural-language request that clearly
names **2.5** is sufficient; `$seedance25-prompt-en` is also explicit. Never
silently migrate a generic Seedance or 2.0 job to this skill.

## Version gate

- Explicit `Seedance 2.5` / `씨댄스 2.5` → use this skill.
- Explicit `Seedance 2.0` / `씨댄스 2.0`, or generic `Seedance` with no version
  selection → use `../seedance-prompt-en/SKILL.md`.
- Do not load both version-specific prompting or production documents for one
  block.
- Before handoff, write `provider_model: Seedance 2.5` and
  `provider_skill: seedance25-prompt-en` in the prompt package. Missing or
  conflicting values block 2.5 production; do not infer the version from prose.

## Shared authority

The current video-team runtime `AGENTS.md` continues to own rails, lane order,
media registry, duration locks, safety, approvals, and spawn policy. This skill
owns only the version-specific prompt and Runway production decisions. Keep one
agent, one sequential lane, and one existing visible Aside Runway tab.

Do not copy the 2.0 shared contract wholesale: it includes deliberate 2.0 model
and queue assumptions. Reuse only the version-neutral creative adapters when
they apply:

- `../seedance-prompt-en/seedance-field-lessons.md`
- `../seedance-prompt-en/hell-grind-production-prompting-adapter.md`
- `../seedance-prompt-en/xazinga-prompting-adapter.md`
- the project's bounded `knowledge-select` packet, when present

Current user instructions, project locks, approved identity/style references,
and provider-visible capabilities outrank those adapters.

## Two serial branches

1. For mode choice, reference roles, Korean prompt compilation, timeline beats,
   or prompt repair, read `prompting.md`.
2. After the package is current and attested, for visible Runway operation,
   model/settings verification, attachment, Generate, recovery, queue handling,
   download, registry ingest, or clip QC, read `production.md`.
3. Production consumes the attested prompt. If the prompt must change, return to
   prompting, create a new revision, and re-attest before touching Generate.

## Isolation and completion

- Prompting is local and non-GUI. It must not activate Aside, Runway, Computer
  Use, a browser loop, a scheduler, or another agent.
- Production is the sole GUI owner and may not improvise a new prompt inside the
  composer.
- The existing Runway helper implementation remains canonical. The script in
  this skill is only a 2.5 model-policy adapter; it must not grow a second copy
  of upload, queue, or recovery logic.
- A prompt, Runway card, or thumbnail is not completion. Completion requires a
  downloaded file, duration/codec verification, registry evidence where the
  runtime requires it, and clip QC.

## First-party references

- [ByteDance Seed: Introducing Seedance 2.5](https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5)
- [Runway: Creating with Seedance 2.5](https://help.runwayml.com/hc/en-us/articles/53542207042323-Creating-with-Seedance-2-5)
