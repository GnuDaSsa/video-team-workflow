---
title: Video Typography Contract Template
created: 2026-05-20
updated: 2026-05-20
type: seed
tags: [video, video-production, typography, editing, qc, workflow, seed]
sources: [concepts/video-typography-operating-manual.md, concepts/video-typography-dataset.md, raw/transcripts/suncheon-v08-typography-correction-20260520.md]
confidence: medium
contested: false
contradictions: []
---

# Video Typography Contract Template

## Project Archetype

CapCut-first MV/public-contest/tourism projects where typography keeps regressing because rules exist in the wiki but are not being converted into a concrete edit contract. This seed bridges [[video-typography-operating-manual]], [[video-typography-dataset]], and project execution.

## Source Evidence

- [[video-typography-operating-manual]] — role-first typography, motion budget, CapCut preview/export as source of truth.
- [[video-typography-dataset]] — accumulated rules for Korean readability, safe zones, shadow/stroke, CapCut risks.
- raw/transcripts/suncheon-v08-typography-correction-20260520.md — V08 improved contrast/size but still exposed that concept-level typography rules were not enforced as a project contract.

## Winning Pattern

Before Editor touches CapCut, Director must issue a one-page **Typography Contract**. The contract is not a style essay; it is a checklist/table that binds each text layer to a role, scene geometry, style token, hold time, and QC proof.

## Non-goals / Anti-patterns

- Do not say "wiki 적용" after only increasing size, adding shadow, or removing boxes.
- Do not let AGENTS.md/global memory substitute for a project-specific typography contract.
- Do not accept a QC report that only says "readable" without checking role separation, subject clearance, safe margins, line breaks, and scene-specific contrast.
- Do not iterate by raw JSON coordinate nudging when the failure is design hierarchy.

## Production Seed

```text
Create a project typography contract before CapCut revision:
1. Read ~/wiki/concepts/video-typography-operating-manual.md and ~/wiki/concepts/video-typography-dataset.md.
2. Classify every on-screen text as TITLE, LOCATION, BODY/NARRATION, DISCLOSURE, CTA, or DECORATIVE/NON-SEMANTIC.
3. For each text event, specify copy, time range, scene risk, placement preset, font pair/weight, fill, stroke/shadow, line-break, motion budget, and minimum hold.
4. Editor implements only against this contract in editable CapCut text layers unless the user approves an exception.
5. QC checks actual CapCut preview/export frames against the contract; PASS requires every semantic text event to satisfy the role and scene-specific criteria.
```

## Role Handoff Map

- Director: turns wiki rules into the typography contract and marks V08/V09 target deltas.
- Editor: implements contract in CapCut; no ad-hoc style improvisation unless documented as a contract amendment.
- QC: audits contract compliance scene by scene; contrast-only PASS is insufficient.
- Package: copies only the contract-passing export into the submission package; upload/email remain approval-gated.

## Acceptance Criteria

- A `typography_contract_*.md` or equivalent exists before final typography revision.
- Every semantic text layer has role, time range, placement, style token, and QC proof requirement.
- Opening/final sky text uses dark charcoal/warm dark fill or otherwise proven contrast; white-outline-only is rejected.
- Body copy is short, readable, unboxed/near-unboxed, and clear of subject/action/important background.
- Rounded boxes are absent unless explicitly justified as last-resort accessibility support.
- CapCut editable text layers are preserved where required.
- QC report includes scene-by-scene contract result, not just global PASS prose.

## Verification Methods

- ffprobe/stat for exported master.
- CapCut preview/export stills for every risky text event.
- Contact sheet or sampled frames at text hold points, not only fade-in/out frames.
- Draft/layer proof that typography remains editable when required.
- Submission package readme confirming no upload/email/final submit without user approval.

## Next-use Prompt

```text
Use ~/wiki/seeds/video-typography-contract-template.md. Before revising the edit, produce a project typography contract from the wiki rules, then hand it to Editor and QC as the mandatory pass/fail surface. Treat contrast-only fixes as insufficient unless the contract also passes role hierarchy, safe-zone, hold-time, and scene clearance.
```

## Related pages

- [[video-typography-operating-manual]]
- [[video-typography-dataset]]
- [[video-team-seed-system]]
- [[tourism-mv-seed]]
