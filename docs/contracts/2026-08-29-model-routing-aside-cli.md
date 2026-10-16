# Video-team model routing and Aside CLI phase contract

## Objective

Make high-value image/video prompt work use `gpt-5.6-sol` at `xhigh`, while
routine flow, QC, editing, packaging, Aside operation, and Computer Use use
`gpt-5.6-luna` at `high`, without reintroducing parallel prompt agents or a
second browser owner.

## Execution contract

1. The runtime chooses models from `runtime/scripts/model_routing.py`; lane
   prompts cannot override the mapping.
2. Image Creator lanes run under Sol xhigh. Their bounded image-generation
   processes remain non-agent immutable-prompt executors.
3. Seedance becomes two sequential phases inside the same lane directory:
   - `prompting`: Sol xhigh, local-only, ends after current attestation and
     writes `READY_FOR_PRODUCTION`;
   - `production`: Luna high, consumes attested packs, controls the one existing
     Aside Runway tab, and owns permitted native Computer Use.
4. Production uses deterministic `aside repl` tab binding first. It does not
   open a new Runway tab or route through Chrome, Safari, in-app browser,
   connector, or API.
5. The second phase is never auto-spawned. Every Codex owner dispatch requires
   an exact `--approved-spawn <lane>:<phase>` token corresponding to explicit
   current-conversation approval.
6. A live Codex lane owner blocks any other lane/phase owner. The existing
   bounded image process and foreground queue-wait exceptions do not create a
   second planning/browser owner.
7. Korean/non-ASCII Seedance prompts are file-first: UTF-8 NFC
   `<BLOCK>_prompt.txt` is the production source, and IME failure routes to the
   keystroke-free `paste-prompt --file` path rather than repeated typing.
8. Fifteen seconds is the hard generation default. Any shorter lock must carry
   current `user:` or `brief:` evidence; manual JSON edits and Planner-only
   reasoning fail validation.
9. Every fresh dispatch writes `model_route.json`, and runtime `status/report`
   exposes the selected model, reasoning effort, and phase.

## Acceptance checks

1. The model matrix maps only image creation and Seedance prompting to Sol
   xhigh; all other stages and Seedance production map to Luna high.
2. `codex exec` receives both the model ID and `model_reasoning_effort`.
3. Seedance auto-phase stays on prompting until the handoff/recovery/in-flight
   evidence selects production.
4. Production refuses to start without an attested pack, recovery checkpoint,
   or in-flight job.
5. Dispatch refuses a missing/mismatched spawn approval token and a second live
   Codex owner.
6. Prompt contracts explicitly bind the existing Aside tab via `aside repl`
   and prohibit a second browser loop.
7. Prompt paste preflight rejects non-`.txt`, non-UTF-8, and non-NFC inputs
   before touching the composer.
8. A manually shortened duration lock without user/brief authority is rejected.
9. Status output exposes model/effort/phase and the route evidence path.

## Release boundary

This policy applies to fresh dispatches after deployment. It does not mutate
an already-running model's loaded context, current Runway cards, project media,
or paused project state.
