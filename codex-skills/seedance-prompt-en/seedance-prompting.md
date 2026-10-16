# Seedance prompting branch — the one template

This branch writes **only what will be visible or audible**. It does not click
Runway, watch the queue, or claim completion. This file owns the single
model-facing template. Every other prompting document is a review lens that
checks a prompt written in this template; none is an alternative structure.

## Where the prompt is written

- **Preprod projects** (`preprod/PREPROD_V1` exists — all new projects): the
  prompt is written once, before production, in
  `preprod/04_shelf/<BLOCK>/`. Run
  `preprod.py shelf-brief --project <p> --block <BLOCK>`, write `prompt.txt`
  from the generated `brief.md`, then `shelf-check` (same flags) until clean and
  `shelf-lock` (validation + attestation). The user releases shelves once with
  `shelf-release`. Production only pastes
  `pack.json`; **no prompt is written or edited at production time.** If the
  storyboard is wrong, fix and re-lock the storyboard — never patch the prompt
  around it.
- **Legacy projects** (no preprod marker): use the same template, write
  `<BLOCK>_prompt.txt` + package, and attest (see "Pack fields" below).

## Canonical template

```text
15 seconds, N shots:                      <- or: 15 seconds, one continuous shot:
<STYLE block, verbatim from style_bible.style_block_en>
<IDENTITY block per cast member, verbatim from identity_block_en>
@Image1 is <role>: take <attributes> only, never <what must not transfer>.
@Image2 is <role>: ... (one binding sentence per token; say once that images are independent anchors, not a time order, or "Hard cuts between shots.")
Shot 1 (0-5s): <shot size>, <angle>, <camera move>[, <lens>]. <composition>. <action beats: start -> contact -> response>. <physics cue only if the shot needs it>.
Shot 2 (5-10s): ...
Shot 3 (10-15s): ...
Sound: <diegetic sounds caused on screen; music only if the block asks>. <dialogue per audio_route>.
End frame: <storyboard end_frame>.
```

Rules, each mechanically checked by `shelf-check` unless marked (review):

1. **Line 1** is exactly `<duration> seconds, N shots:` (N = storyboard shot
   count) or `<duration> seconds, one continuous shot:`. The duration is the
   locked block duration (default 15). No other "N seconds/sec" anywhere; shot
   times live only in the `Shot k (a-bs):` markers.
2. **STYLE** and **IDENTITY** are pasted verbatim. Do not paraphrase, shorten,
   or re-describe the character elsewhere.
3. **Bindings:** exactly the tokens `@Image1..@ImageN` for the block's refs, in
   `refs.json` order, each with one sentence naming its role, what to take and
   (review) what not to take. No `@Video`/`@Audio` unless the block owns one.
4. **Shots:** for 2–4 shots, each section starts with `Shot k (a-bs):` using
   the storyboard times, and contains that shot's exact `shot_size`, `angle` and
   `camera_move` phrases plus every `must_include` phrase **inside its own
   section**. A single shot carries the same phrases in its one body.
5. **Action** (review): present tense, visible verbs, start → contact →
   response. Show emotion through face, breath, hands, posture — never name it.
6. **Camera** (review): **one dominant camera move per shot, as declared in the
   storyboard.** Do not add a second move; a compound path means the storyboard
   needs another shot.
7. **Physics** (review): **only the physics cues the shot needs; no quota.**
   Zero is valid for a clean view. Every cue has a cause in frame.
8. **Sound** (review): one `Sound:` sentence following the block's
   `audio_route` and the dialogue table in `seedance-shared-contract.md`.
9. **End frame** last, from the storyboard `end_frame`.
10. **Length:** target ≤3,200 characters, hard limit 3,500. Over target means
    adjectives or repetition to cut — never a locked block or MUST phrase.
11. **English**, UTF-8 NFC. Only a spoken line may stay in its spoken language,
    in quotes; the prompt must still read as English-dominant.

Gold examples that pass `shelf-check` and `shelf-lock`: `examples/` (single
shot live action, 3-shot 2D, 2-shot product macro, BAD → GOOD).

## Never in the prompt

`Scene ID:` · `Mode:` · `Look medium:` · `REFERENCE ROLES:` · gate words ·
`EXPECTED:` · `Audio ON` / UI settings · `EXIT:` · file paths, asset IDs,
`CHAR_` IDs, project names, status values · provenance such as "generated
styleframe for E23" · lists of banned characters. Control the cast by stating
who is present. Attestation's leak pattern rejects most of these.

## Negatives

One or two risks specific to this shot (face identity, hand/product contact,
on-screen text), stated positively where possible. No habitual negative wall;
QC catches general defects.

## References

- `@ImageN` numbering is attachment order, never story order
  (`GENERAL_REFERENCE_MODE`, owned by the shared contract).
- In `no_i2v_reference_native`, references give only their named identity /
  environment / prop role; the prompt itself carries composition, blocking,
  action, camera and timing. Never copy a reference's composition as an
  implicit start frame. In `standard_i2v`, the approved per-cut frame may
  establish the opening composition.
- Deck, count and character-sheet rules: `seedance-shared-contract.md`.

## Story progression and cut ownership

In preprod projects the locked storyboard already owns order, purpose and
covered shots (`covered_cuts` are derived from it). For legacy projects, record
in the package before attesting: `story_progression` (incoming state,
narrative delta, causal bridge, outgoing state — each one plain sentence) and
a cut-ownership entry (`covered_cuts`, previous owner, duplicate verdict, retry
state). A cut may be regenerated only after `QC_FAILED_RETRY_ALLOWED`. Title
or typography beats are not Seedance text-rendering scenes.

## Opt-in: Toonkit 2D snappy grammar

Only when the user explicitly asks for **Toonkit 문법**, **12 laws** or the
equivalent snappy-animation grammar (2D/stylized only). Record
`motion_grammar_profile: toonkit_2d_snappy_v1` and add it to
`prompt_rules_used`; never paste the profile name into the prompt. Inside each
`Shot k` section write: a clear start pose → one short readable beat
(anticipation → sudden acceleration → controlled overshoot → sharp settle →
delayed follow-through of hair/sleeves) → a held final pose; planted limbs and
silhouette stated so it cannot become walking or a second action; modest
squash/stretch or one smear only where earned. The camera keeps its one
declared move, independent of the snap. The profile never changes the locked
duration, shot count, identity, style or audio.

## Wiki knowledge packet

When knowledge routing is enabled, `brief.md` lists the selected context packet
(`lanes/seedance/knowledge/<BLOCK>_context.md`); read only that, never the
whole wiki. Apply its craft (Higgsfield community grammar first among creative
knowledge) **inside this template** — it never adds a section, a second camera
move, or a physics quota, and it never outranks the user, the storyboard, or
locked blocks. Do not copy community wording, cameos or motion IDs. The pack
records selection ID, context SHA-256 and selected IDs automatically.

## Pack fields (legacy attest path)

Packs declare `prompt_language: en-US`,
`prompt_style_version: creative_seedance_en_v4_20260912`,
`authoring_contract: seedance_lane_owned_en`, `duration_sec` equal to the
workflow-owned lock, and `prompt_rules_used` including
`model_facing_multimodal_binding_v1`. Run
`prompt_packet_utils.py attest --project <p> --pack <pack>` and require
`ATTESTED` before UI work. Preprod `shelf-lock` writes these fields itself.

## Before handing off

- `shelf-check` is clean (or, legacy, attestation is `ATTESTED`).
- Read the first shot section aloud: the subject's action and the camera are
  obvious without the rest.
- No invisible sentence, no second camera move, no uncaused physics cue.
- Prompt-review lenses (`prompt-review.md`) applied for the risks this block
  actually has.

Authoring is single-agent, sequential and non-GUI: no browser, Computer Use,
`osascript`, file chooser, queue observer, background job or prompt agent.
