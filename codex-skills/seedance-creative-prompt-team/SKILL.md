---
name: seedance-creative-prompt-team
description: "Sequential Creative Seedance prompt authoring team. Use when the user wants creative/experimental/dreamlike Seedance or Runway multi-reference video prompts, camera invention, bold transitions, reference-role packages, or a structured rewrite of the seedance-prompt-en Creative branch. The six roles are a single-agent checklist by default; prompt authoring only — never Runway UI, Generate, queue, or download. For production execution, hand off to seedance-prompt-en production branch."
---

# Seedance Creative Prompt Team

A cloned and restructured version of the Creative Seedance Mode from `seedance-prompt-en`. This skill owns **prompt and reference-package authoring only**. It does not click Runway, attach files, Generate, monitor queues, or claim media completion. The six named roles are a sequential reasoning checklist, not six automatically spawned agents.

## Relationship to the Sol prompt bridge — 2026-07-28

Inside the video-team runtime (`Documents/Codex/video-team-runtime`), the **final submitted Seedance prompt is authored by the `gpt-5.6-sol` bridge at reasoning effort `high`**, and the pre-submit attestation requires `model=gpt-5.6-sol`. A hand-written or chat-authored prompt has no Sol provenance and will fail attestation.

So this skill is a **pre-Sol thinking pass, not the final author**:

- run the six roles to decide premise, reference roles, camera family, physical layers, and exit composition;
- write that decision into the structured block spec (`lanes/seedance/prompts/<BLOCK>_block_spec.json`);
- let the Sol bridge compose the submitted prompt from it.

Outside the runtime — ad-hoc requests, exploration, a one-off clip with no lane — this skill may emit the final prompt directly. When in doubt, if the work lives in a runtime project, Sol writes the prompt.

Start responses with `[seedance-creative-prompt-team]` when this skill is active.

## Authority split

| Concern | Owner |
|---|---|
| Creative prompt + ordered multi-ref package | **this skill** |
| Shared Seedance invariants / block codes | `~/.codex/skills/seedance-prompt-en/seedance-shared-contract.md` |
| Visible Runway attach / Generate / download | `~/.codex/skills/seedance-prompt-en/seedance-production.md` |
| Story purpose / scene brief | `videodirector` |

Read the shared contract before authoring. If production execution is requested after the package is ready, hand off to `seedance-prompt-en` and do not improvise UI steps here.

## Execution isolation and spawn gate — 2026-07-26

Prompt authoring is one foreground, sequential operation. Do not fan out delegated lanes, subagents, external sidecars, schedulers/monitors, background jobs, or parallel automation loops by default. Multiple concurrent control surfaces can steal browser focus and trigger stale `osascript`/launchd helpers, so the prompt branch must remain browser-free and UI-free.

During prompt authoring, this skill may inspect approved local files, write the handoff package, and use the runtime-owned prompt-authoring bridge. It must not open or activate Chrome/Safari/Runway, use Computer Use, AppleScript, `osascript`, `open -a`, native file choosers, queue observers, launchd jobs, or browser automation. A prompt package is finished before production or any explicit CLI handoff begins.

Default is **single-agent sequential role-play**: one agent walks the six roles in order and emits one integrated package. Full policy: `~/.codex/video-team-policies/subagent_approval_gate_20260721.md`.

If the user explicitly approves one named extra role/worker, record its exact purpose and expected output before spawning it. That approval does not authorize a second worker, a scheduler, a monitor, or a browser loop. Keep one Showrunner as the only integrator, and do not combine the spawn with production UI work.

## Why this exists

The live Creative Seedance Mode works, but it is packed into one prompting branch. This skill makes the same grammar prettier and harder to skip by separating the reasoning into six sequential passes:

1. **Creative Director** — premise, mode, clip role, duration budget
2. **Reference Architect** — ordered `@ImageN` roles + character-sheet gate
3. **Camera Director** — camera family, one motivated evolution, subject motion state
4. **Motion Physicist** — 2–4 causal physical motion layers
5. **Prompt Composer** — visual-only English prompt assembly
6. **Prompt Critic** — creative QA gate and package completeness

No role may rewrite another role's ownership without an explicit conflict note from the Critic.

## Standing user defaults — 2026-07-25

These are project standing rules, not one-off notes. Apply on every package unless the user overrides that exact shot.

1. **Default card = Multi-reference mode, 15s.** Multi-reference is the Runway mode (opposite Keyframe) and stays selected unless the user asks for Keyframe. Duration shortens only when the user or a fragile shot requires it. **Reference count** is separate and comes from the request (commonly 3–4; a character sheet plus a background is a legitimate full deck) — the agent never pads a deck to hit a number, and a count the user states is an instruction, not a suggestion.
   **Anything the user states explicitly overrides these defaults.**
2. **Open creative room.** Creative Mode is default. References are anchors for identity, environment, texture, and key props — not start/middle/end cages. Invent in-between motion, camera discovery, and exit composition after identity is locked.
3. **Audio toggle always ON; the prompt directs the sound.** Name the soundscape for each shot — ambience, contact SFX, room tone, or music when the shot wants it. Diegetic-only is a sensible default, not a prohibition. Spoken dialogue only if a verified performed `@Audio1` guide is attached.
4. **Naturalism first.** Prefer believable body mechanics, ordinary contact physics, imperfect micro-motion, and lived-in environments over glossy AI spectacle. One dominant camera family; no multi-trick chaos in a single 15s card.
5. **Texture naturalness is medium-aware.**
   - **Live-action / photoreal / real-world plates:** texture fidelity is a first-class QC axis. Prefer stable material response (skin pores/oil only when already in refs, fabric weave, wood grain, wet/dry surfaces, dust, grit) and reject plastic skin, crawling noise, boiling lines, waxy faces, over-sharpened edges, and synthetic film-grain soup.
   - **2D / picture-book / stylized animation:** texture still should feel intentional and material (paper, ink, gouache, cel) but do not over-police photoreal texture rules. Keep medium consistency instead.
6. **Throughput mindset.** Author packages that can be generated back-to-back as multi-ref 15s cards. Prefer one coherent 15s beat with a usable exit over cramming a whole sequence into one prompt.

Package fields must record:
- `Duration: 15s` (or explicit override)
- `Audio: ON` (toggle never disabled); the prompt states the intended soundscape (`@Audio1` still required for spoken dialogue)
- `Look medium: live-action | 2D/stylized | mixed`
- `Naturalism/texture notes:` medium-appropriate

## Non-negotiable gates

- Creative Seedance Mode is the default unless the user requests Standard or the shot is fragile-continuity-first.
- When the source references are 2D/stylized, use the immutable `STYLE LOCK → CONTINUITY → DIRECTION` blocks and change only the per-shot `SHOT` block. Do not rewrite the medium, character/world rules, or camera language inside individual shot prompts.
- Default duration is **15 seconds**; no silent shorter duration unless the user overrides that exact shot. Reference count is whatever the request calls for — commonly 3–4, sometimes a character sheet plus a background.
- Open creative room after identity lock: invent transitions, camera discovery, and exit composition; do not cage the model to literal storyboard interpolation.
- **Audio toggle always ON.** The prompt names the soundscape; music is allowed when the shot calls for it. No spoken dialogue request unless a verified performed `@Audio1` is attached.
- Naturalism over spectacle. Believable cause → contact → response, ordinary micro-imperfections, lived-in motion.
- Texture naturalness is mandatory for live-action/photoreal packages; for 2D/stylized, preserve medium-true material instead of fake photoreal pores.
- If an approved character appears, the relevant character sheet / identity crop is mandatory on every generation and must appear in the ordered role map.
- Physical cause → contact → response is mandatory. No mood-only prompts.
- Exactly one dominant camera family per 15s card unless the package is an explicit montage.
- Negative tail is role-specific and short. No generic negative wall.
- **The prompt is written in Korean** (2026-07-29), creative prompts included, so the user can review and approve it. Spoken lines verbatim Korean; proper nouns, on-screen text and format tokens (`15s`, `9:16`) unchanged.
- Visual-only prompt. Never include `Scene ID`, `Mode`, `Look medium`, `REFERENCE ROLES`, gate wording, `EXPECTED` settings, `EXIT` notes, file paths, provenance such as `generated styleframe for E23`, captions, contest copy, or model names. Those belong to the package file, which never enters Runway — on E24 that contamination was 34% of the prompt.
- Stay within Runway's visible 3500-character limit; prefer 700–1800 characters.
- This skill never claims production completion. Completion requires the production branch's downloaded + ffprobe-verified file.


## Operating flow

Run as one integrated sequential pass. The role headings are review passes, not concurrent workers:

```text
1. Creative Director   → clip card (mode, premise, role, duration budget, exit intent)
2. Reference Architect → ordered Image1..N roles + character-sheet gate + exact paths
3. Camera Director     → camera family, mount/path, subject motion state, one evolution
4. Motion Physicist    → 2–4 motivated physical layers + cause→contact→response
5. Prompt Composer     → final visual-only English prompt + settings package
6. Prompt Critic       → pass/fail against creative QA; rewrite request or READY package
```

If Critic fails, return only to the owning role(s). Do not silently patch in Composer.

Do not start production, queue observation, browser automation, or an external worker between these passes. If a prompt revision is needed, return to the owning pass in the same sequential run.

## Role summary

### 1. Creative Director
Owns the shot's creative thesis. Decides Creative vs Standard. Declares look medium. Names the clip role: identity / reveal / speed / action / product proof / UGC hook / atmosphere / montage / transition. Defaults the budget to **15s multi-ref, Audio ON with the soundscape named**, naturalism-first. Sets the calm → discovery → transformation → aftermath need only when useful. Outputs a one-paragraph visible premise, not style adjectives.

### 2. Reference Architect
Owns the multi-reference deck for 15s throughput. Orders environment/action anchors first, then identity sheets. Labels each `@ImageN` with a visible role sentence. Enforces `Character-sheet gate: required | not applicable`. Re-checks approved sheet paths against the manifest; memory is not verification. After every five packages, refresh sheet context as an auxiliary review.

### 3. Camera Director
Owns camera grammar for one 15s card. Chooses one primary family:
through-aperture/reveal · mounted-object · handheld intimate track · dolly/pan/orbit · bullet-time · static-frame active subject · POV/FPV · deliberate montage.

States subject motion state (normal-speed / micro / static / frozen / vehicle-mounted) and one motivated camera evolution with a clear exit. Translates any preset name into camera physics. Never relies on a motion-id alone.

### 4. Motion Physicist
Owns physicality and medium-aware naturalism. Adds 2–4 layers motivated by camera + action: smoke/steam, fabric/hair, reflections, foreground occlusion, parallax, dust/particles, vibration, focus breathing, wind, water. For live-action, protect texture stability; for 2D, protect medium-true material. Forbids unmotivated spectacle and repeated generic light-match glue between unrelated scenes. Fire/torch/lamp matches only for explicit transition beats or a cause present in the shot.

### 5. Prompt Composer
Owns the final English visual prompt and production handoff fields. Assembles in this order:

For 2D/stylized sources:

1. immutable STYLE LOCK: medium, linework, fill/shading, palette, and rendering rules
2. immutable CONTINUITY: characters, proportions, costume/props, world, and geography
3. immutable DIRECTION: camera language, pacing, and sound/impact cue grammar
4. ordered `@ImageN` roles
5. one unique SHOT beat with physical cause→contact→response
6. 15s motion arc and clear exit composition
7. short role-specific safety tail + medium-true material note

For live-action/mixed sources, use the normal visible premise → reference roles → camera/action → physical layers → exit composition order.

Defaults settings to `15s multi-ref; Audio: ON; soundscape directed in the prompt`. Does not invent missing references or skip the character-sheet gate.

### 6. Prompt Critic
Owns READY / REVISE. Checks the creative QA list in `references/creative-directing-grammar.md` and package schema completeness. Rejects mood-only wording, missing sheet gates, multi-camera chaos, empty physics, storyboard-cage references, silent non-15s duration, an unstated soundscape, missing naturalism/texture attention on live-action, and prompt pollution (names, captions, provenance). Production-branch readiness is separate and not claimed here.

## Duration-to-complexity budget

Default duration is **15s multi-ref**. Use the 15s row unless overridden.

| Duration | Budget |
|---|---|
| 5–6s | exception only: one action or one camera trick |
| 7–10s | exception only: setup → one interaction → one reveal; ≤3 major verbs |
| **15s (default)** | setup → interaction/discovery → consequence or calm aftermath; still **one** dominant camera family; 2–4 physical layers; clear exit for the next card |

If the action budget overflows a single 15s card, split into multiple multi-ref 15s packages rather than compressing everything.


## Handoff package (required output)

```text
Scene ID:
Mode: Creative | Standard
Look medium: live-action | 2D/stylized | mixed
Clip role:
Camera family:
Subject motion state:
Visual prompt:
Ordered references:
  Image1 = <path> — <visible role>
  Image2 = <path> — <visible role>
  ImageN = <path> — approved character sheet/identity crop when applicable
Character-sheet gate: required | not applicable
Physical motion layers:
  1. ...
  2. ...
Naturalism / texture notes:
Exit composition / next-scene handoff:
Expected duration/audio/settings: 15s multi-ref; Audio: ON; soundscape directed in the prompt; ...
Source root and exact file paths:
Critic verdict: READY | REVISE
Revision notes (if any):
```

Template: `assets/package-template.md`.

## Standard mode (narrow exception)

Use Standard when identity, crop, product geometry, spatial continuity, or a fragile close-up is the primary risk. Keep the same six-role pipeline, but Camera Director prefers static/slow push/macro-in, Motion Physicist prefers micro-motion, and Composer strengthens identity/crop locks. Creative Director must record why Standard was chosen.

## Live branch documents

- `references/agent-contracts.md` — ownership and forbidden actions per role
- `references/role-prompts.md` — short role prompts for the sequential pass; spawning is exceptional and approval-gated
- `references/creative-directing-grammar.md` — camera families, physics menu, QA gate
- `references/handoff-schema.md` — field definitions and pollution blacklist
- `assets/package-template.md` — copy-ready package skeleton

## Relationship to original skill

This skill is a **clone/restructure of the Creative prompting branch**, not a replacement of production authority.

- Keep using `seedance-prompt-en` for shared contract + production UI.
- Prefer this skill when the user asks for creative prompting, role-separated sequential review, or experimental camera work.
- Do not fork conflicting Generate/attach rules here.

## First-action checklist

1. Read shared contract from `seedance-prompt-en`.
2. Collect scene brief, approved image manifest, and character sheets.
3. Run the six-role pass (sequential by default).
4. Emit one READY package or a REVISE note with owning role(s).
5. If the user wants Generate next, hand the READY package to `seedance-prompt-en` production.
