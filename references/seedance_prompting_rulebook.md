# Seedance Prompting Rulebook

Version: 2026-07-19
Source: distilled from `/Users/gnudas/wiki/concepts/seedance-prompting-knowledge.md` and `~/.codex/skills/seedance-prompt-en/SKILL.md`. Active production prompt authorship follows the current Codex model routing in AGENTS.md §2.

## How to reference this knowledge (retrieval protocol)

1. **Always load TIER 0 only** (~1 screen). Do not load the full wiki page during prompting.
2. Load the ONE matching TIER 1 block-type section for the current block. Not all of them.
3. Load TIER 2 only when the block contains dialogue/generated audio.
4. The wiki page is provenance/history, not a working reference. Consult it only when a rule here seems wrong or a new failure mode has no entry. The wiki's V07–V85 entries are a project log; everything durable from them is already in TIER 2.
5. After writing a prompt, always save `lanes/seedance/prompts/<BLOCK>_prompt_rules_used.md` listing: method, reference_role_map, shot_count, motion_budget, duration_reason, constraints, retry_if_failed, and which TIER sections were applied. QC compares the clip against this.

---

## TIER 0 — HOT CORE (always apply)


### Output language and scope — 2026-07-29

- Write the Seedance prompt in **Korean**, creative prompts included. The user reviews and approves it; an unreadable prompt cannot be corrected. Spoken lines stay verbatim Korean. Proper nouns, on-screen text and format tokens (`15s`, `9:16`) keep their original form.
- The prompt contains **only what is visible on screen**. Never write `Scene ID`, `Mode`, `Look medium`, `REFERENCE ROLES`, gate wording, `EXPECTED` settings, `EXIT` notes, file paths, project names, or provenance such as `generated styleframe for E23` — that describes how a still was made and renders as nothing.
- Measured contamination on a live prompt: 1,100 of 3,207 characters (34%) were operational. Target 700–1,500 characters; if you approach 3,500, suspect contamination before trimming description.
- State the cast by **who is present**, not by listing who is banned.


**2026-07-19 creative video high-lane**: For final Seedance video prompts, `gpt-5.6-terra` high acts as `video_prompt_director_high`. Use `prompt_style_version=creative_seedance_5_6terra_high_20260719`. References are anchors, not cages: lock only essential identity/symbol/safety details and allow Seedance to invent shot size, camera path, blocking, transition, parallax, and atmosphere inside the reference story roles. Avoid legacy template language: no repeated `preserve crop/composition`, `locked source frame`, `dignified slow push`, `tiny parallax`, or `stable hold` boilerplate.



Seedance final prompts must contain only video-relevant viewing instructions. Do not mention how a still was made (`Gongnyang`, imagegen, source frame, prompt pack, provenance, QC). Do not assign a reference to an invisible historical/admin label such as a village name unless that location is visually legible or necessary for motion. `@ImageN` roles should be framed as visible function: ember detail, ridge beacon, memory reflection, hands preparing cloth, market lane, crowd wave, aftermath hold.

**Formula**: `Shot structure + Subject + Environment + Action + Camera + Style + Reference mapping + Constraints`. Describe what the viewer sees; no adjective piles like "cinematic high quality".

**Method first**: choose T2V / I2V / multi-reference / first-last frame / extension / repair before writing. For I2V the image already owns composition/style/lighting — the prompt's job is motion, camera, temporal progression, preservation.

**Reference roles**: every upload gets one explicit role via `@ImageN/@VideoN/@AudioN` (`@Image1's character as the subject`, `scene references @Image2`). One primary job per reference. Never assume the model infers what to preserve. Identity reference → preserve hairstyle/clothing/face/proportions; environment reference must not overwrite identity.

**Structure upfront**: state total duration, aspect, resolution, shot/beat count BEFORE the action. >8s → time-segmented beats (`Beat 1 (0–3s): …`), each beat = one camera setup + one subject action + one environment motion layer + one timing cue. Single continuous shot → say so (`no cuts`). Montage → say `multi-shot montage, hard cuts, not one scene`.

**Motion budget** per beat: `micro` (eyes/breath/hair/rain/fabric) / `moderate` (walk/run/reach/turn) / `impact` (burst/transition, only where music demands). Close-ups get micro only + `no zoom out, keep crop`. A prompt that only maps Image1→Image2→Image3 with no camera/action verbs must be rewritten before Generate.

**Preservation tail** (adapt per project): For general cinematic blocks use `Preserve essential story motif, identity/symbol details, and palette; allow cinematic reframing within the same scene.` Use `Preserve exact crop` only for fragile face/hand/phone/text/macro/Taegeukgi or stability-first retries. Tail: `No text, logos, readable signs, lip-sync, new facial structure, new props, gore, malformed flags, watermarks, or location reset.`

**Length**: 700–1500 chars typical; Runway UI hard limit 3500. Trim order: style adjectives first → duration/aspect NEVER → identity/order constraints NEVER. Priority: ① reference order/roles ② identity/costume/crop ③ motion beats/camera ④ aspect/duration ⑤ style adjectives.

**Limits**: images ≤9, videos ≤3, audio ≤3, total ≤12. Duration 4–15s. Match duration to action count — a 5s clip cannot hold a whole scene.

**UI state ≠ prompt text**: duration/multi-reference are UI controls. Writing "12-second" in the prompt does nothing; the visible duration pill and ordered thumbnail strip must match the operator card before Generate. Reference attach one-by-one, verify `IMG_n` in strip each time.

**Project isolation**: only current-project files and block IDs. Stale Recents/old smoke tests contaminating the strip → defer the block, never generate with them.

---

## TIER 1 — BLOCK-TYPE RULES (load only the matching one)

**character close-up / identity**: identity lock + crop preservation + micro-motion (eye, breath, hair-tip, rack focus). Put `no zoom out, no new face, no facial structure change` near start AND tail.

**kinetic / run**: explicit tracking/side/back camera, parallax, footstep/cloth/hair motion, purposeful accel/decel, stable anatomy, ground/route continuity.

**memory / interior**: environment reference role, slow dolly / rack focus, light/rain/reflection motion; environment must not overwrite identity.

**object / motif macro**: prop reference role, macro push, state whether the object may glow/transform, no unrelated props, no readable text.

**transition / abstract**: declare metaphorical vs literal (`not a real bird / no animal anatomy`); morph/streak/flare/whip-pan allowed here only.

**multi-shot montage**: duration/aspect/shot-count first, enumerate Beat 1..N in exact reference order, add `do not collapse the sequence into only Image N` if a prior run ignored early refs.

**POV**: `single continuous POV, no cuts, no zoom`, state what hands/camera can and cannot see.

**final hold / climax**: restrained cinematic reveal/hold with living atmosphere (not frozen frame), fade-ready composition, no location reset.

**character/model-sheet intro** (Scenic pattern): the sheet is a shot library, not one flat image — `detail → identity → presence → full reveal`, active micro-expressions/gestures, controlled camera, consistent lighting.

**ad / product 15s** (Scenic pattern): timestamped arc `problem → contact → transformation → energetic demonstration → explicit hero shot`; product never a passive still.

**stability-first (approved stills that wobble/boil)**: `@Image1 is the exact source frame and composition anchor… Camera locked; only minimal natural motion (breathing, hair-tip, light shimmer). No texture crawling, line boiling, face flicker, hand warping, morphing.` Multi-ref stable shots → `hard cut / clean cut`, never `transition/morph`. Readable screens/UI → lock as CapCut overlay, or prompt `pure flat matte black rectangle`.

**anime**: never start from "anime style". Require: historical_layer(era) + era_materials/forbidden anachronisms + aesthetic family variables (describe variables, not living-director names) + layout contract + anime motion budget + 3–5 palette anchors. Retry diagnosis adds `era drift` and `style-family drift`.

---

## TIER 2 — DIALOGUE / GENERATED AUDIO CONTRACT (only for audio blocks)

Distillation of the entire V07–V85 Seongnam voice saga. The single durable lesson: **AI-like voice is a performance/cadence failure — never fixable by stacking adjectives.** `natural / professional voice actor / emotional / warm` as the main fix is banned.

**Audio route decision (write an `AUDIO ROUTE` line before story beats):**

1. Performed Korean `@Audio1` attached → assign it explicitly as speech-performance guide (phoneme timing, uneven syllables, breath, hesitation, swallowed endings, laugh leaks, room-mic distance, emotional curve) and state it is NOT BGM.
2. No `@Audio1`, final delivery → prompt visuals + room tone + diegetic SFX only, `no spoken dialogue`; replace speech externally (CapCut/VO). Prompt-only native speech = `AUDIO_FAIL_DEFAULT`.
3. User explicitly asks to improve native Seedance voice by prompting (V84 correction) → allowed as candidate route: generate S1 (story-readable) and S2 (anti-AI, under-acted) variants per block, select by listening QC, regenerate fails.

**Prompt mechanics for spoken lines:**

- Only spoken Korean inside quotes; acting/timing notes (`[0.35s silence]`) outside quotes, in English.
- One key line per 2.5–4s; 12s block ≤ 3 key lines. One speaker owns each beat; reactions/laughter only AFTER the line lands.
- Encode human imperfection directly: uneven syllable length, 0.2–0.6s thinking silence, breath before risky words, swallowed endings, uneven volume, false starts, room/phone mic distance.
- Private family speech, not campaign copy — public-message clarity goes to captions/editing.
- Relationship lock in positive form (`누나 teasing younger brother 민재`), plus English `wrong sibling title forbidden`. Never rely on negated Korean tokens.
- No-BGM hard rule when clean dialogue is required: any score/piano/strings/pad/jingle = audio hard fail. Allowed: room tone, phone buzz, gamepad, cloth, rattle, baby breath/coo, small laugh after key lines.

**Audio QC is independent of visual QC.** Visual PASS + audio FAIL → keep clip, mute, patch VO. Hard-fail signatures: metallic smoothing, equal-syllable rhythm, over-clean studio diction, announcer/campaign tone, fake hype, garbled Korean, wrong relationship, overlapped plot lines, any music bed.

---

## Failure-mode retry table

| Symptom | Diagnosis | Fix |
|---|---|---|
| Collapsed into one scene / only last ref used | ordering not enumerated | enumerate beats; add `do not collapse into only Image N` |
| Wobble/boil/rubber face on good stills | over-animation | stability-first pattern (TIER 1) |
| Wrong duration | UI pill, not prompt | fix duration control, verify pill before Generate |
| Stale/wrong assets in output | strip contamination | defer block, clean re-attach; not a prompt problem |
| AI-like voice | performance failure | TIER 2 route decision; never adjective retry |
| Era/style drift (anime) | style-family drift | back to style bible / image regeneration, not prompt patch |
| UI attach fails | operation problem | attach playbook; prompt is fine; do not rewrite prompt |
