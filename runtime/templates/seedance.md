# Seedance — one owner, two sequential phases

Authority: explicit 2.5 → `/Users/gnudas/.codex/skills/seedance25-prompt-en/`;
2.0 or unversioned → `/Users/gnudas/.codex/skills/seedance-prompt-en/`.
Load only the selected version branch. Runtime owns rails/media/safety.

## Prompting (no browser)
1. Read the gate, current block map, music cue, generation-duration lock,
   generation mode, approved reference IDs/hashes and prior failure evidence.
2. Run `video-codex-runtime knowledge-select --project <p> --block <BLOCK>` when
   knowledge routing is enabled; read only the selected packet. Community
   grammar is inspiration below user intent, verified identity and project locks.
3. Apply the selected skill's prompting branch and shared `prompt-review.md`.
   Declare `render_scope`; remove irrelevant entities, undecided camera choices,
   operator prose and filenames. Bind each attached token to its narrow role.
4. Write a UTF-8 NFC `<BLOCK>_prompt.txt` containing only Korean visual/audible
   direction, plus the separate machine-readable package. Include
   `model_facing_multimodal_binding_v1`, `duration_sec`, `shot_grammar` and, for
   multi-shot sources, scene IDs/times/cut ownership/reference tokens/action/
   decided camera/edit-out. Include knowledge receipts when applicable.
5. Run `prompt_packet_utils.py attest --project <p> --pack <pack>` and require
   ATTESTED. A stale historical attestation is not current submission authority.

## Production (no prompt improvisation)
Continue in this same conversation by default; this phase change is not a spawn.
Use only the selected version's production branch and shared
`aside-operator.md` / executable helper. They own binding, native chooser,
settings verification, recovery, exactly-once submit and `queue-cycle`.
If the prompt needs a change, return to prompting and re-attest before Generate.

Download the matching output, verify bytes/duration/codec/resolution and ingest
into `media/06_videos_candidates_영상후보/`; queue the registered asset for QC.
Submitted cards and historical files are not rewritten to satisfy a new schema.

Outputs: pack + prompt + attestation, binding/checkpoint, deck/prompt/settings/
card evidence, downloaded asset IDs + ffprobe, `status.json`, `result.md`.
