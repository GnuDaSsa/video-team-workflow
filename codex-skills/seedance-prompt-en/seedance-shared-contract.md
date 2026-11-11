# Seedance shared contract

Invariants both the prompting and production branches obey. It is not a UI
procedure and not a prompt template (the template is owned by
`seedance-prompting.md`). This file is the **single owner** of: the duration
lock, Audio, the dialogue route table, prompt language, the reference deck and
character-sheet gate, and reference interpretation modes. Other files point
here instead of restating them.

## Authority and routing

- **An explicit user instruction overrides every default** — mode, reference
  count, duration, ratio, audio, provider. Apply it and say which default it
  overrides. In a preprod project the user-approved storyboard and bible locks
  are that instruction in machine-readable form.
- `seedance-prompting.md` owns the prompt; `seedance-production.md` owns visible
  Runway operation, queue, download, registry ingest and media verification.
- Still images come from Codex imagegen/Gongnyang; this contract covers
  videoization only. Default provider is Seedance; Grok only when the user names
  it for the job.
- Authoring is single-agent, sequential, non-GUI and browser-free; production
  owns the visible browser. No resident observer, delegated prompt worker or
  sidecar in either phase. Queue continuation belongs only to production's
  `queue-cycle`.

## Duration lock

Use the workflow-owned, attested project/block duration exactly. The runtime
default is **15 seconds**; 5–14 seconds needs an explicit user/brief override
recorded in the lock. Never shorten it from prompt complexity, a planned final
trim, the current UI, or a board's existing value. Complexity is sized inside
the lock: a single sustained shot with edit handles is valid; 2–4 planned shots
only when causally related. Prompt line 1 and `duration_sec` name the same
value.

## Audio

The Runway audio control is one toggle for generated SFX and music together.

- Audio is **ON** for every block whose `audio_route` is not `silent`; the
  prompt's `Sound:` sentence decides the soundscape (ambience, contact SFX,
  room tone, or music when the block asks for it). There is no standing "no
  BGM" rule.
- Audio is OFF only when the locked block route is `silent` (preprod writes
  this into `settings.json`). The operator never toggles Audio to fix a
  soundscape; a wrong soundscape is a prompt revision.
- The settings line reports the real UI value only; sound intent never lives
  in a settings field.

### Dialogue and audio routes (the only table)

| Condition | Allowed route | QC |
|---|---|---|
| No speech in the block (default) | `native_diegetic_no_dialogue`: `Sound:` names on-screen causes; add "No dialogue." | listen: no speech or mumbling |
| Effects-only requested | same route; prompt says "No background music, song, narration, dialogue or continuous ambience; only short effects caused by visible action." | listen + waveform: any bed/score fails the route; regenerate (clip stays candidate) |
| Spoken line + verified performed `@AudioN` guide | `native_dialogue` with `@AudioN` bound to cadence/timing only; literal line in quotes; one speaker per beat, others silent | listening + lipsync |
| Spoken line, no guide, user explicitly asked for native voice (legacy: `native_seedance_user_reference` under `user_reference_superior_v1`) | `native_dialogue`, candidate-only | listening + lipsync before approval |
| A finished music master owns the piece | `music_reference`: `@AudioN` is the only music/vocal source; one on-camera vocal owner; no invented score | lipsync per vocal interval; mouth unobstructed |
| Block must be silent | `silent`: Audio OFF in settings; no `Sound:` sentence needed | none |

A quoted line alone never proves audio quality; the downloaded clip is QC'd.

## Prompt language

**Model-facing prompts are English** (en-US), including reference bindings,
scene/action/camera/light/physics/timing and voice-delivery descriptions. This
is the user's standing preference. User-facing planning, explanations and review
may stay Korean. A spoken line stays verbatim in its spoken language (normally
Korean) inside quotes; proper nouns, required on-screen text and format tokens
keep their intended form. The whole prompt must remain English-dominant.

Packs use `prompt_language: en-US`,
`prompt_style_version: creative_seedance_en_v4_20260912`,
`authoring_contract: seedance_lane_owned_en`. Preprod shelves accept English
only. Attestation, paste and settings checks use the same policy.

**Legacy override only:** an existing (non-preprod) project with an explicit,
recorded user request for Korean directions may keep `prompt_language: ko-KR`,
`creative_seedance_ko_v4_20260731`, `seedance_lane_owned_ko` with a
hash-bound `prompt_language_override` (absolute `project`, `evidence_path` under
that project's `docs/`, `evidence_sha256`; JSON with
`source: explicit_user_request`, `language`, verbatim `user_quote`, `turn_id`,
exact `block_ids`). A Korean conversation or Korean spoken line is not that
request. Never rewrite or resubmit accepted/uncertain transactions when
changing language; language change never bypasses moderation or other gates.

## Reference deck and character-sheet gate

- **Multi-reference is the mode** (the Runway tab opposite Keyframe) and the
  default. "Use multi-reference" is a mode instruction, not an image count. Do
  not ask whether to use it.
- **Count follows the request** (commonly 3–4; sometimes a sheet plus a
  background). The agent never invents a fixed count or pads to reach one; a
  count the user states is an instruction.
- Every attached image/video/audio has a named role both in the ordered pack
  map and as a binding sentence in the prompt
  (`model_facing_multimodal_binding_v1`); a package-only role is invisible to
  the provider.
- Build each deck from **this shot's own material**. A neighbouring frame is
  allowed only with a specific visible role for this shot. Compare against the
  previous block by registered hash and role: more than one shared scene/action
  image → rebuild before Generate. Required identity sheets/crops are excluded
  from that count; a scene frame relabelled as identity is not.
- If one usable frame exists, submit it plus the sheet; a smaller honest deck
  beats a padded one.
- **Character-sheet gate:** whenever an approved recurring character appears,
  attach that character's approved sheet or minimum identity crop **on every
  generation**, together with the scene refs (scene refs first, sheets after).
  Several characters → every relevant sheet. Verify the visible thumbnail on
  this generation; previous cards or memory are not verification. Missing,
  mismatched or unverifiable → `BLOCKED_CHARACTER_SHEET_ATTACHMENT_NOT_VERIFIED`,
  no Generate. This supersedes any rule against uploading sheets.
- The sheet fixes **face silhouette, hair mass, costume, age impression, body
  proportion and signature props** — nothing else. It is not a pose, scene
  order or transition cue and must never push the character into a frontal
  poster stance.
- Never attach an identity sheet to a shot without that character.

### Which identity asset

The canonical master is `CHAR_<ID>_TRIPTYCH_R<n>`: a text-free neutral 16:9
strip (default: left headless front full body, middle back full body, right one
large 3/4 portrait; a recorded complete-front-head fallback is allowed). Select
the approved layout by registered name/hash. Derivatives `_FACE`,
`_FRONT_BODY`, `_BACK_BODY` inherit it. Attach the minimum asset that proves the
shot: triptych for general identity/body, `_FACE` for fragile close-ups, a body
crop only when wardrobe/proportion is visible. A full triptych needs an English
binding sentence: primary face identity from the right portrait, front
body/wardrobe from the left panel, rear silhouette from the middle panel;
exclude gray background, panel seams and (for the headless default) the missing
head. No QC-passed triptych or derivative → `BLOCKED_NO_PROVIDER_SAFE_SHEET`.
Spec: `runtime/references/character_sheet_prompt_standard.md`.

- `standard_i2v` (only when the user explicitly requests it): attach
  styleframe(s) + the minimum identity asset; the styleframe carries the scene.
- `no_i2v_reference_native` (default): no per-cut frame; minimum reusable
  identity/environment refs; the prompt carries composition, blocking, action,
  camera, atmosphere and timing.

### Reference interpretation modes

- `GENERAL_REFERENCE_MODE` — **default and owner of the rule**: each `@ImageN`
  is an independent anchor for look, palette, space, props or plausible action.
  Deck order is attachment order only — never a sequence to interpolate,
  match-cut or replay. One generation is newly composed from the written shot
  plan. Say so once in the binding sentences when it matters.
- `STORYBOARD_SHOT_MODE` — one approved board `shot_id` per generation; other
  cells are context.
- `STORYBOARD_SEQUENCE_PREVIS_MODE` — opt-in prototype; status `PREVIS_HOLD`
  until order, identity, timing and board-artifact contamination pass QC.

Shot grammar is separate: `GENERAL_REFERENCE_MODE` may produce
`SINGLE_CONTINUOUS_SHOT` or `PLANNED_MULTI_SHOT_SOURCE` (2–4 shots ordered by
the written plan). A board never replaces the identity asset and never becomes
a `standard_i2v` per-cut frame. Without an approved board, `shot_id`s and the
mode declaration, fall back to `GENERAL_REFERENCE_MODE`. Board schema:
`/Users/gnudas/wiki/concepts/storyboard-production-blueprint-standard.md`.

## Creative mode

Creative Seedance Mode is the default authoring branch (Standard when
continuity is fragile or the user asks). It permits camera invention within
the declared move, motivated reveal, speed change and focus discovery after
identity is verified. It does not permit generic visual glue: light/fire matches
between unrelated scenes are a QC failure. Every clip still needs cause →
contact → response, a clear subject action and a usable end frame.

## Handoff contract

| File | Contents | Destination |
|---|---|---|
| `prompt.txt` / `<BLOCK>_prompt.txt` | the prompt only | pasted whole into Runway |
| `pack.json` / `<BLOCK>_package.md` | block id, mode, refs and paths, settings, knowledge receipt, gates | operator only; never enters Runway |

Write the prompt file as UTF-8 NFC; that file — not browser typing — is the
production prompt source of truth. Production may reject an incomplete pack but
never rewrites the prompt; it sends it back to prompting.

Legacy package fields: scene id; mode; look medium; reference interpretation
mode; shot grammar and scene count; `scene_plan` for multi-shot (scene_id,
start/end, covered_cuts, reference_tokens, action, camera, edit_out); knowledge
selection ID / context SHA-256 / selected IDs (must match
`lanes/seedance/knowledge/<BLOCK>_selection.json`); ordered references with
roles; storyboard asset; production status; character-sheet gate;
expected settings (duration, audio, ratio); end frame; source paths.

## Completion and blockers

- A UI card, prompt text, local image or Generate click is not completion.
  Completion needs the exact downloaded path, size, duration, codec/container,
  scene ID, provider and QC verdict.
- Aside CLI/repl binding to the exact existing Runway `targetId` is the primary
  production control. A disabled Apple Events JavaScript toggle alone is not a
  blocker. Only when Aside CLI binding and the permitted same-tab fallbacks
  cannot operate the visible Reference selector may production use
  `BLOCKED_ASIDE_CONTROL_UNAVAILABLE`; record the exact user action and
  do not switch to Chrome, Safari, the in-app browser, or connector/API.
- An upload stalled at 100%: cancel only that upload, keep the rest of the
  deck, record it in lane `status.json` and `result.md`.
- No duplicate Generate once the scene's accepted card is visible.

History behind these rules: `incidents.md` (not loaded by default).
