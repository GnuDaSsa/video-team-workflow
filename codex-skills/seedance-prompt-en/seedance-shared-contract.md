# Seedance shared contract

This document contains rules that both the prompting and production branches must obey. It is not a UI procedure and it is not a prompt template.

## Authority and routing

- `SKILL.md` dispatches the workflow; this file defines the shared invariants.
- `seedance-prompting.md` owns visual prompt and reference-package authoring.
- `seedance-production.md` owns visible Runway operation, same-task queue resume, downloads, registry ingest, and media verification.
- `videodirector` may define story and shot purpose, but do not replace these Seedance rules.
- Still images are produced with Codex imagegen/Gongnyang. This contract covers Seedance videoization only.
- Default provider is Seedance. Grok is used only when the user explicitly names it for the specific job.

## Prompting/production isolation — 2026-07-26

- Prompt authoring is single-agent and sequential. Use `prompt-review.md`; no separate Creative team surface is loaded.
- While authoring, do not start delegated prompt workers, background schedulers, queue observers, browser loops, or external sidecars.
- The prompting phase is non-GUI and browser-free. It writes and attests the local handoff package; the same Seedance lane then enters the production phase.
- The production phase owns visible browser operation, Generate, download, registry ingest, and verification. No resident observer process is launched.
- Queue continuation belongs only to the selected production branch and `queue-cycle`; a contract file never schedules a future model turn.

## Standing generation defaults — 2026-07-25

User standing preference for ordinary Seedance work:

- **Shape:** use the workflow-owned, attested project/block duration exactly. The runtime starts at 15 seconds; 5–14 seconds requires an explicit user/brief override. This skill has no independent competing default and may not shorten the lock from prompt complexity, final edit trim, or the board's existing value. Reference count comes from the request, not a rule — see the reference/character-sheet gate below.
- **Creative room:** open after identity lock. References are anchors (identity/environment/texture/prop), not start/middle/end cages.
- **Audio:** the Runway **Audio setting stays ON**, always. The prompt names the soundscape for that shot — ambience, contact SFX, room tone, or music. Spoken dialogue only with a verified performed `@Audio1` guide. See "Audio: toggle always ON" below.
- **Naturalism:** believable body mechanics and ordinary contact physics over glossy AI spectacle.
- **Texture:** medium-aware. Live-action/photoreal requires stable materials and rejects plastic/waxy/crawling texture; 2D/stylized preserves medium-true material and does not force photoreal pores.

These defaults apply to the single-owner prompting branch and `prompt-review.md`.

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

## Reference deck and character-sheet gate

### What the user says wins

**An explicit instruction from the user overrides every default in this contract** — mode, reference count, duration, ratio, audio, provider. Apply it as stated, and if it conflicts with a default, say which default you are overriding rather than quietly splitting the difference.

Defaults exist for what the user did *not* specify. They are never a reason to ignore what they did.

### Mode and count are different things

- **Multi-reference is the mode**, the Runway tab opposite Keyframe. It is the **default mode** for this pipeline and stays selected unless the user asks for Keyframe. If the user says "multi-reference", that is a mode instruction — honour it exactly, do not treat it as a comment about how many images.
- **Reference count** is how many files go in that mode. It follows the request: typically 3–4, sometimes a character sheet plus a background, sometimes a larger deck.
- *The agent* must not invent a fixed count or pad a deck to reach a number. That restriction is on the agent, **not on the user** — a count the user asks for is an instruction, not a number to second-guess.
- Do not ask whether to use multi-reference; it is already the default. Asking is different from ignoring a stated one.
- Whatever the count or modality, the prompt package must contain an ordered
  `@ImageN` / `@VideoN` / `@AudioN` role map naming each attached source's
  visible or audible function. The Korean model-facing prompt must also bind
  every attached token to that narrow function; a package-only role is invisible
  to the provider.
- **Build each deck from that shot's own material.** Do not pad a deck with the previous or next scene's frames to reach a count. A sliding window like `E19: E18·E19·E20` then `E20: E19·E20·E21` makes consecutive blocks share most of their references, and the model returns two clips that read as the same shot — the exact "why are you making the same video twice" failure.
- If a block genuinely has only one usable frame of its own, submit it with that one frame plus the character sheet. **A smaller honest deck beats a padded one.**
- A neighbouring frame may be attached only when it carries a specific visible role for *this* shot (a prop that must match, a wall the camera crosses), and the role map must say what that role is. Continuity between shots comes from the exit-composition handoff in the prompt, not from recycling the neighbour's reference images.
- Before submitting, compare this deck against the previous block's deck by registered hash and declared role. If scene/action references overlap by more than one image, rebuild before Generate. Required immutable approved identity sheets/crops for recurring characters are excluded from that overlap count, not from attachment or visible-verification gates. A scene frame cannot be relabelled as identity to evade this check. Record both shared identity anchors and shared scene/action sources in the package; near-duplicate scene decks remain a duplicate-output defect.
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
- In `GENERAL_REFERENCE_MODE`, `@ImageN` numbering is **not** a narrative sequence. Ordered references are independent anchors for look, palette, space, props, and plausible action — never a storyboard to interpolate, match-cut, or replay in order.
- This gate **supersedes any rule that forbids uploading character sheets to Runway.** Sheets are required multi-reference inputs when a recurring character appears.

### Reference interpretation modes

The Runway tab remains Multi-reference; these names describe how the prompt package interprets an approved deck.

- `GENERAL_REFERENCE_MODE` — default. Each `@ImageN` has an independent role. Deck order is attachment order only.
- `STORYBOARD_SHOT_MODE` — final-production storyboard use. One generation executes one internal board `shot_id`. In `standard_i2v`, the approved per-cut styleframe carries the scene, the minimum `TRIPTYCH`/identity crop carries identity, and the unified board carries shot purpose, blocking, lens/camera intent, sound cue, and exit composition. Other board cells are context, not scenes to replay.
- `STORYBOARD_SEQUENCE_PREVIS_MODE` — opt-in prototype/previsualization only. One approved unified board carries internally numbered beats, and the Korean prompt restates a duration-feasible order. The output must be actual cinematic scenes, never the board sheet, panels, labels, diagrams, UI, or printed layout. The package status is `PREVIS_HOLD` until order, identity, timing, and board-artifact contamination pass QC.

Shot grammar is separate from reference interpretation. `GENERAL_REFERENCE_MODE` may produce either `SINGLE_CONTINUOUS_SHOT` or final-production `PLANNED_MULTI_SHOT_SOURCE`. In the latter, the Planner's written 0–15s scene plan—not `@ImageN` order—defines 2–4 scene order. Each scene binds only its relevant approved references and ends on an edit-ready frame. `STORYBOARD_SEQUENCE_PREVIS_MODE` remains reserved for a unified multi-panel board prototype.

Rules shared by both storyboard modes:

- A unified storyboard is one named reference role. `@Image1 → @ImageN` deck numbering never becomes the narrative sequence; only the board's internal `shot_id` order can be sequential.
- The board never replaces the approved `CHAR_<ID>_TRIPTYCH_R<n>` or minimum deterministic identity crop for a recurring character.
- The board never becomes a `standard_i2v` per-cut sourceframe. A multi-panel board or cropped panel is not an approved source image.
- If the package lacks an approved storyboard asset, internal shot IDs, or the matching storyboard mode declaration, fall back to `GENERAL_REFERENCE_MODE`; never infer storyboard semantics from a random collage or multi-panel sheet.
- Canonical directing schema and board QC: `/Users/gnudas/wiki/concepts/storyboard-production-blueprint-standard.md`.

### Which character identity asset to attach

The canonical master is **`CHAR_<ID>_TRIPTYCH_R<n>`**: a text-free neutral 16:9 strip whose left panel is a headless front full body, middle panel is a back full body with head, and right panel is one large 3/4 portrait. Select it by registered name/hash, not by eye. Its approved deterministic derivatives are `_FACE`, `_FRONT_BODY`, and `_BACK_BODY`; they inherit the master identity and record crop coordinates.

Attach the minimum asset that proves the current shot. Use the full triptych for general identity/body binding, `_FACE` for fragile close-ups, and a body crop only when wardrobe orientation or full-body proportion is visible. Never pad the deck with all derivatives. Every full-triptych attachment requires Korean model-facing role binding that assigns face identity to the right portrait, front body/wardrobe to the left panel, and rear silhouette/wardrobe to the middle panel, while explicitly excluding the gray background, panel seams, and missing front head from the generated scene.

If no QC-passed triptych or appropriate derivative exists, stop with `BLOCKED_NO_PROVIDER_SAFE_SHEET`. Do not improvise from a beauty key art, text-heavy bible, or unverified crop.

Spec and generation rules: `runtime/references/character_sheet_prompt_standard.md`. Compatible compile additions live in `hell-grind-production-prompting-adapter.md`.

Generation mode decides whether a per-cut styleframe exists; the identity gate itself does not change.

- `standard_i2v`: the identity asset **does not replace** the per-cut styleframe. Attach `styleframe(s) + minimum required TRIPTYCH/crop` — the styleframe carries the scene and the character asset carries identity/body construction.
- `no_i2v_reference_native`: a per-cut styleframe is intentionally absent. Attach only the minimum approved reusable identity/environment references needed by this shot family. The Korean prompt carries the omitted frame's composition, blocking, action, camera, atmosphere, and timing.

## Generate-ready queue resume protocol

The selected production branch and shared `aside-operator.md` own queue/recovery
procedures. Use atomic `queue-cycle`, not a discretionary sync-then-wait split.
This shared contract does not reproduce those procedures.

## Creative mode and continuity

- Creative Seedance Mode permits camera invention, motivated aperture/reveal, speed change, focus discovery, and atmospheric transformation after reference identity is verified.
- Creative mode does not permit generic visual glue. Fire/torch/lamp/light matches are reserved for explicit character-transition beats or a cause that exists in the shot; repeated light matches between unrelated scenes are a QC failure.
- In `GENERAL_REFERENCE_MODE`, references are anchors, not mandatory start/middle/end storyboard frames. In storyboard modes, only the declared internal `shot_id` or ordered PREVIS beats constrain sequence; creative freedom remains inside those bounds.
- Every clip still needs a physical cause → contact → response, a clear subject action, and a usable exit composition.
- Default package duration is 15s multi-ref with Audio ON; the prompt states the intended soundscape (ambience, SFX, room tone, or music) for that shot.

### 2D/stylized continuity architecture

- When source references are 2D/stylized, use four stable prompt blocks: `STYLE LOCK`, `CONTINUITY`, `DIRECTION`, `SHOT`.
- `STYLE LOCK`, `CONTINUITY`, and `DIRECTION` are immutable across the related sequence; `SHOT` is the only per-shot variable and contains one unique beat.
- A change to medium, character/world rules, camera grammar, or sound language starts a new style-lock sequence; it must not be smuggled into a single shot.

## Handoff contract

Two artifacts, and the split is the point:

| File | Contents | Destination |
|---|---|---|
| `<BLOCK>_prompt.txt` | **the prompt only** — what will be visible | pasted whole into Runway's prompt box |
| `<BLOCK>_package.md` | scene id, mode, routed-knowledge receipt IDs/hashes, reference roles and paths, gates, settings, handoff notes | read by the operator; **never enters Runway** |

Keeping metadata out of the prompt file makes the paste accident structurally impossible. Put both in one file and it eventually gets pasted whole — which is exactly how 1,100 of 3,207 characters (34%) ended up in a live prompt.

**Prompts are written in Korean** (2026-07-29), creative prompts included, so the user can read, approve and correct them. Spoken lines stay verbatim Korean; proper nouns, on-screen text and format tokens (`15s`, `9:16`) keep their original form.

### Package (`<BLOCK>_package.md`)

```text
Scene ID:
Mode: Creative | Standard
Look medium: live-action | 2D/stylized | mixed
Reference interpretation mode: GENERAL_REFERENCE_MODE | STORYBOARD_SHOT_MODE | STORYBOARD_SEQUENCE_PREVIS_MODE
Shot grammar: SINGLE_CONTINUOUS_SHOT | PLANNED_MULTI_SHOT_SOURCE
Planned scene count: 1 | 2 | 3 | 4
Scene plan: <for multi-shot: scene_id, start_sec, end_sec, covered_cuts, reference_tokens, action, camera, edit_out>
Knowledge selection ID:
Knowledge context SHA-256:
Knowledge selected IDs:
Prompt file: <BLOCK>_prompt.txt
Ordered references:
  Image1 = <asset_id/path> — <what it contributes to this shot>
  Video1 = <asset_id/path> — <camera/action/rhythm/edit role, if attached>
  Audio1 = <asset_id/path> — <performed speech/music/SFX role, if attached>
  ImageN = <asset_id/path> — approved CHAR_<ID>_TRIPTYCH_R<n> or minimum deterministic identity crop when that character appears
Storyboard asset / internal shot range: <none | STORYBOARD_<PROJECT>_R<n> / S01 | S01-S04>
Production status: FINAL_CANDIDATE | PREVIS_HOLD
Character-sheet gate: required | not applicable
Naturalism / texture notes:
Expected settings: 15s; Audio: ON; 9:16 | 16:9
Exit composition / next-scene handoff:
Source root and exact file paths:
```

For a v4 project with knowledge routing enabled, these three knowledge fields
must match `lanes/seedance/knowledge/<BLOCK>_selection.json`; attestation fails
when the Planner attribute file, catalog, selected source, or context packet has
changed. The production branch may reject an incomplete package, but it must
not silently rewrite the visual prompt. Send it back to prompting for revision.

New reference-based packs also declare
`prompt_rules_used += model_facing_multimodal_binding_v1`. Runtime attestation
then requires every ordered source token and role to be valid and non-empty, and
requires each non-empty prompt variant to contain every attached token. This is
the executable guard against a role existing only in package metadata.

### Never in the prompt file

`Scene ID` · `Mode` · `Look medium` · `REFERENCE ROLES` · gate wording · `EXPECTED` · `EXIT` · file paths · project names · status values · production provenance such as `generated styleframe for E23`.

That last one describes **how a still was produced**. There is nothing in it for a video model to render — it only consumes characters.

## Completion and blockers

- UI card, prompt text, local source image, or a Generate click is not final media completion.
- Final completion requires an exact downloaded video path, file size, duration, codec/container evidence, scene ID, provider, and QC verdict.
- Aside CLI/repl binding to the exact existing Runway `targetId` is the primary production control. A disabled Apple Events JavaScript toggle alone is not a blocker. Only when Aside CLI binding and the permitted same-tab fallbacks cannot operate the visible Reference selector may production use `BLOCKED_ASIDE_CONTROL_UNAVAILABLE`; record the exact user action and do not switch to Chrome, Safari, the in-app browser, or connector/API.
- If an upload stalls at 100%, cancel only that upload, preserve the rest of the deck, and record the event in lane `status.json` and `result.md`.
- No duplicate Generate: once the scene's accepted card is visible, do not click Generate again for that scene.
