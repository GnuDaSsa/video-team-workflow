# Seedance shared contract

This document contains rules that both the prompting and production branches must obey. It is not a UI procedure and it is not a prompt template.

## Authority and routing

- `SKILL.md` dispatches the workflow; this file defines the shared invariants.
- `seedance-prompting.md` owns visual prompt and reference-package authoring.
- `seedance-production.md` owns visible Runway operation, queue monitoring, downloads, and media verification.
- `videodirector` and `music-video-production-team` may define story and shot purpose, but do not replace these Seedance rules.
- Still images are produced with Codex imagegen/Gongnyang. This contract covers Seedance videoization only.
- Default provider is Seedance. Grok is used only when the user explicitly names it for the specific job.

## Prompting/production isolation — 2026-07-26

- Prompt authoring is single-agent and sequential. The Creative six-role structure is a checklist, not a default parallel spawn.
- While authoring, do not start delegated prompt workers, background schedulers, queue observers, browser loops, or external sidecars.
- The prompting branch is non-GUI and browser-free: no Chrome/Safari/Runway activation, Computer Use, `osascript`, AppleScript, `open -a`, native file chooser, or browser automation. It writes the local handoff package and then stops.
- Visible browser operation, Generate, queue monitoring, and downloads belong only to the production branch after an explicit handoff. A production observer must not be launched by the prompting branch.
- A 15-minute Generate-queue observer scheduler is permitted only in the production branch, only after a prompt/reference package is fully staged and a queue is active or the staged Generate button is waiting for eligibility. It must be a single sequential observer, not a parallel browser loop, sidecar, cron, or second agent surface.

## Standing generation defaults — 2026-07-25

User standing preference for ordinary Seedance work:

- **Shape:** multi-reference × **15 seconds** by default. Do not ask whether to use multi-ref. Shorter only with an explicit override for that shot.
- **Creative room:** open after identity lock. References are anchors (identity/environment/texture/prop), not start/middle/end cages.
- **Audio:** the Runway **Audio setting stays ON**, always. The prompt names the soundscape for that shot — ambience, contact SFX, room tone, or music. Spoken dialogue only with a verified performed `@Audio1` guide. See "Audio: toggle always ON" below.
- **Naturalism:** believable body mechanics and ordinary contact physics over glossy AI spectacle.
- **Texture:** medium-aware. Live-action/photoreal requires stable materials and rejects plastic/waxy/crawling texture; 2D/stylized preserves medium-true material and does not force photoreal pores.

These defaults apply to both the single-agent prompting branch and `$seedance-creative-prompt-team`.

## Audio: toggle always ON, soundscape directed by the prompt — 2026-07-28

The Runway/Seedance audio control is **one binary toggle covering generated SFX and music together**. There is no "music off, SFX on" control.

- **The audio toggle is always ON.** It is not a per-shot decision and never gets switched off. `Audio: ON` is a settings-line value, checked once in the Generate preflight.
- **The prompt decides the soundscape** — that is the whole point of leaving audio on. Direct it explicitly per shot: ambient bed, specific SFX, room tone, or background music when the shot wants music. Naming the sound you want is normal prompt authoring, not a rule violation.
- There is **no standing "no BGM" rule**. Ask for score when the shot calls for it and ask for diegetic-only when it doesn't. Write what you want to hear.
- Spoken dialogue still needs a verified performed `@Audio1` guide.
- If a clip comes back with the wrong soundscape, that is a **prompt revision** — never a reason to touch the switch.

### How this went wrong

A preference for diegetic-only audio was written into the **settings/handoff field** instead of the prompt rules. An operator reconciling "settings match the package" read `no BGM` as a UI value and reached for the switch, which killed the SFX and room tone the same rules asked for. The corruption then hardened: the 15-minute observer was told to re-verify **"Audio Off settings"** on every wake, so the silence got actively maintained.

Audio intent belongs in the prompt text. The settings line reports the real UI value and nothing else.

## Universal multi-reference and character-sheet gate

- Every Seedance generation in this project uses visible multi-reference assets. The prompt package must contain an ordered `@ImageN` role map.
- When a visible person/character corresponds to an approved character/model/identity sheet, attach the scene reference(s) **and that character sheet or approved identity crop every time**.
- If multiple approved characters appear, attach every relevant sheet/crop. Scene image presence never replaces the sheet.
- Character sheets are identity anchors, not storyboard replacements. They do not authorize inventing a different costume, face, age, or role.
- Re-attach and visibly verify the sheet on every dependent generation. Previous cards, prior deck state, and conversation memory are not current verification.
- If a required sheet is missing, mismatched, or not visibly verifiable, stop with `BLOCKED_CHARACTER_SHEET_ATTACHMENT_NOT_VERIFIED` and do not Generate.
- The five-image refresh rule remains a secondary context-refresh habit; it never substitutes for the per-generation attachment gate.

### What the sheet is allowed to do — 2026-07-28

Promoted from the operating rules that were actually producing clips in the independence-activist project. Attaching the sheet is mandatory; misreading it is the failure mode.

- **Attachment order:** scene references first, approved character sheet(s) after. Record the order.
- The sheet fixes **face silhouette, hair mass, costume, age impression, body proportion, and signature props** — nothing else.
- The sheet is **not** a scene-order instruction, not a transition cue, and not a pose instruction. A sheet must never push the character into a frontal poster stance; the shot's action, camera, and mid-motion state are specified separately.
- `@ImageN` numbering is **not** a narrative sequence. Ordered references are independent anchors for look, palette, space, props, and plausible action — never a storyboard to interpolate, match-cut, or replay in order (`GENERAL_REFERENCE_MODE`).
- This gate **supersedes any rule that forbids uploading character sheets to Runway.** Sheets are required multi-reference inputs when a recurring character appears.

### Which sheet may be uploaded

The character-sheet standard produces two outputs, and only one of them is a Runway input.

| Output | Upload to Runway? |
|---|---|
| Dense AAA character **bible page** — hero pose, callouts, labels, lore, palette blocks | **Never.** Its text, labels, and panel grid corrupt the generation. Approval and design-lock only. |
| **Clean production sheet** — neutral/off-white background, flat lighting, no readable text, crop-safe | **Yes — this is what it was made for.** Attach it, or a deterministic crop of it, as the identity anchor. |

Same bar as the reference-native runtime's `PROVIDER_SAFE_REF` tier: no text, no labels, flat-lit, derived from the approved master.

The clean sheet **does not replace** the per-cut styleframe. Attach `styleframe(s) + clean sheet` together — the styleframe carries the scene, the sheet carries the identity.

## Generate-ready queue observer protocol

- After the prompt and all required references are visibly loaded, inspect the visible Generate control. If it is gray/disabled, do not click it and start one 15-minute observer schedule for that staged package.
- On each 15-minute wake, re-query the same visible Runway Generate board and verify that the staged prompt, ordered references, Multi-reference mode, 15s duration, and ratio are still present. Audio is a standing ON default and is checked once in the Generate preflight, not re-verified on every wake. Do not rely on a previous screenshot or stale element index.
- If Generate is still gray, leave the package untouched and schedule the next 15-minute wake. Do not spin-poll, re-upload, rewrite the prompt, open another browser route, or create a second observer.
- If Generate is blue, click it **exactly once**. Immediately verify the resulting scene card itself—`In queue`, `Generating`, `Processing`, or `Completed`—and match its scene ID/prompt before recording the queue submission. A blue button alone is not completion evidence.
- If one click does not produce a matching accepted card, stop automatic retries and record `BLOCKED_GENERATE_ACCEPTANCE_NOT_VERIFIED`; do not click again for that scene.
- After a matching card is visible, and only if the Generate control remains blue/eligible, advance to the next prepared prompt and reference package. Attach and visibly verify that next package first, then click Generate once. Repeat this staged-package → blue-button → one-click → matching-card cycle.
- Keep the observer alive only while at least one submitted card or a gray staged package remains active. Remove it when the queue is empty and no package is waiting. The observer never downloads, deletes, publishes, or submits external forms.

## Creative mode and continuity

- Creative Seedance Mode permits camera invention, motivated aperture/reveal, speed change, focus discovery, and atmospheric transformation after reference identity is verified.
- Creative mode does not permit generic visual glue. Fire/torch/lamp/light matches are reserved for explicit character-transition beats or a cause that exists in the shot; repeated light matches between unrelated scenes are a QC failure.
- References are anchors, not mandatory start/middle/end storyboard frames. The model may invent the in-between motion and exit composition when the prompt asks for creative freedom.
- Every clip still needs a physical cause → contact → response, a clear subject action, and a usable exit composition.
- Default package duration is 15s multi-ref with Audio ON; the prompt states the intended soundscape (ambience, SFX, room tone, or music) for that shot.

### 2D/stylized continuity architecture

- When source references are 2D/stylized, use four stable prompt blocks: `STYLE LOCK`, `CONTINUITY`, `DIRECTION`, `SHOT`.
- `STYLE LOCK`, `CONTINUITY`, and `DIRECTION` are immutable across the related sequence; `SHOT` is the only per-shot variable and contains one unique beat.
- A change to medium, character/world rules, camera grammar, or sound language starts a new style-lock sequence; it must not be smuggled into a single shot.

## Handoff contract

The prompting branch must hand the production branch:

```text
Scene ID:
Mode: Creative | Standard
Look medium: live-action | 2D/stylized | mixed
Prompt file:
Visual prompt:
Ordered references:
  Image1 = ...
  Image2 = ...
  ImageN = approved character sheet/identity crop when applicable
Character-sheet gate: required | not applicable
Naturalism / texture notes:
Expected duration/audio/settings: 15s multi-ref; Audio: ON; soundscape directed in the prompt; ...
Exit composition / next-scene handoff:
Source root and exact file paths:
```

The production branch may reject an incomplete package, but it must not silently rewrite the visual prompt. Return the package to prompting for revision.

## Completion and blockers

- UI card, prompt text, local source image, or a Generate click is not final media completion.
- Final completion requires an exact downloaded video path, file size, duration, codec/container evidence, scene ID, provider, and QC verdict.
- If Chrome Computer Use or the visible Reference selector is unavailable, use `BLOCKED_CODEX_COMPUTER_USE_UNAVAILABLE` and record the exact user action needed. Do not use connector/API as a fallback.
- If an upload stalls at 100%, cancel only that upload, preserve the rest of the deck, and record the event in lane `status.json` and `result.md`.
- No duplicate Generate: once the scene's accepted card is visible, do not click Generate again for that scene.
