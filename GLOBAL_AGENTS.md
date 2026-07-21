# Global Codex Instructions

## Codex App Runtime Video-Team Delegation Mode — 2026-05-16

When the current working directory is under `/Users/gnudas/Documents/Codex/video-team-runtime/`, follow the lane prompt and the local project `brief.md`/`state.json` first.

This is a fresh Codex-delegated workflow, not the old Hermes video-team runtime. The old active Hermes video-team files were purged and preserved only as backup.

Lane rules:
- Write only inside the assigned `lanes/<lane>/` directory unless the prompt explicitly names an output package path.
- Update `status.json` and `result.md` for the lane.
- Real media completion requires verified files, paths, sizes, duration/codec where relevant, or verified GUI state. Prompts/plans/placeholders are not completion.
- Parallel lanes require explicit per-spawn user approval first (see "Subagent / lane spawn approval gate — 2026-07-21"). Once a lane set is approved, do not wait on unrelated lanes unless the lane prompt states a dependency.
- Public upload, publish, contest/government submission, email send, personal-info form submit, payment, password/2FA, and irreversible deletion require explicit user approval.
- If GUI/login/CAPTCHA/payment/permission/account-limit blocks occur, stop and write BLOCKED with exact required user action.

## Subagent / lane spawn approval gate — 2026-07-21

After the video team (or any team workflow) is invoked, work must not fan out into extra agents on its own.

- Spawning any additional agent surface — Codex delegated lane, subagent/worker/explorer, Hermes sidecar, background monitor/scheduler/cron/heartbeat, or a second concurrent browser-automation loop — requires **explicit user approval for that specific spawn in the current conversation**. The approval request must name the lane/role, purpose, and expected output.
- Default execution model is single-agent, sequential, in the main conversation. Parallel lanes are an exception the user grants per project/turn, not the default. Role templates define responsibilities, not standing permission to instantiate agents.
- Single pre-approved exception: the 15-minute Generate-queue observer defined in the Seedance execution contract, only while a queue is active.
- Rule files operate latest-only: corrections edit/delete old text in place instead of appending dated layers. History and rollback live in the `GnuDaSsa/video-team-workflow` git repo and `~/.codex/archive/`. Full policy: `team-policies/subagent_approval_gate_20260721.md` in that repo.

## Codex Harness Auto Workflow

For most coding-related repository work, apply the local Codex harness workflow automatically.

Trigger for:

- feature implementation
- bug fixes
- refactors
- tests or CI work
- code review follow-up
- frontend/backend changes
- repo maintenance that changes code, docs, build config, or tests

Skip for:

- non-repository tasks
- quick terminal/status questions
- pure explanation or brainstorming
- user explicitly asks not to use the harness

Before coding in a repo:

1. Identify the repo root from cwd or the explicit target path.
2. Look for `AGENTS.md`, `AGENTS.harness.md`, `docs/harness-config.json`, and `docs/harness-state.json`.
3. If harness files are missing and the task is substantial repo coding work, run `/Users/gnudas/.local/bin/codex-harness-kit init`.
4. Run `/Users/gnudas/.local/bin/codex-harness-kit validate-harness`.
5. Run `/Users/gnudas/.local/bin/codex-harness-kit check-state` and use the recovered goal, contract, blockers, next step, and verification config to guide implementation.

Before finishing meaningful repo work:

- Run the smallest useful verification command.
- Update harness state, active contract, decisions, or project memory when applicable.
- Report what verification ran and what did not run.

## Visible Operation Labels

When a distinct role, agent, skill, tool phase, or workflow is active, make it visually obvious in the CLI transcript by prefixing short status updates with a bracketed label.

Use labels such as:

- `[reviewer]` for code-review mode or auto-review work
- `[explorer]` when an explorer subagent is active
- `[worker]` when a worker subagent is active
- `[harness]` for codex-harness-kit init, validation, state recovery, or wrap-up
- `[github]` for GitHub PR, issue, or CI work
- `[test]` for verification commands
- `[shell]` for local terminal investigation
- `[browser]` for browser automation

Emit a concise labeled update before starting a meaningful phase and when switching roles, so the user can see what is operating without reading tool internals.

## Global LLM Wiki + 90% Context Capture Loop — 2026-05-25

- For all non-trivial Codex work, treat `/Users/gnudas/wiki` as the standing LLM Wiki/knowledge hub. Before durable decisions, orient from `/Users/gnudas/wiki/SCHEMA.md`, `/Users/gnudas/wiki/index.md`, and relevant wiki pages; search the wiki when a task touches prior work, user conventions, workflows, reusable lessons, or project history.
- Do not wait for the user to explicitly say “wiki”. Use the wiki as background context for coding, research, media, operations, planning, and troubleshooting. Skip only truly trivial one-shot answers.
- When the active thread/context is roughly **90% full**, or before manual `/compress`, likely automatic context compression, handoff, session end, or a long pause, append a concise capsule to `/Users/gnudas/wiki/_hub/context-capsules/YYYY-MM-DD.md`. Follow `/Users/gnudas/wiki/_meta/context-recording-hub.md`.
- A capsule should capture: goal, current state, durable decisions/corrections, artifact paths, blockers, exact next resume point, and whether to promote the lesson into a wiki page, seed, skill, or memory.
- Capsules are staging records. Promote reusable lessons into canonical wiki pages/seeds/skills/memory; do not leave important knowledge only in chat or in the capsule.
- Never record secrets, passwords, tokens, payment info, personal form data, or unnecessary private message bodies. Summarize sensitive context by role/path only.


## Video Agent Memory Routing — MV vs Public Contest — 2026-05-10

The user's video-agent history now has two distinct production contexts, but **music-first editing is a shared baseline**, not an MV-only feature. Do not blur project goals together, and separate mainly by typography/story-copy behavior and submission requirements.

### Shared baseline for all serious video work
Apply these rules to both MV and public-contest/institution videos unless the user explicitly overrides them.

Core priorities:
- Music comes first: analyze song/BGM structure, beat, phrase changes, hooks, accents, energy curve, cadence, and ending before final cut timing.
- Default cut density: use roughly **2.0–2.5 seconds per cut** unless the music or brief clearly calls for a different rhythm. Do not arbitrarily undercut the number of cuts for a 1-minute piece.
- Effects and transitions must be motivated by music, motion, story, or emotional emphasis; avoid random preset spectacle.
- Keep story physical and cinematic, but let rhythm drive cut timing and shot duration.
- For still-image production, use Codex `imagegen` / built-in `image_gen` by default; for I2V/videoization, use Grok/Runway/Seedance only after image QC; no raw stills in final edit.
- Imagegen production remains one cut = one standalone image; never request a production grid/contact sheet. Character/model sheets may be multi-panel design references only.
- QC must catch anatomical errors, disappearing limbs/people, repeated shots, bad crops, subtitle overlap, line clipping, weak narrative causality, jitter, freeze frames, and bad transition handles.
- CapCut JSON/coordinate edits are only helpers; actual CapCut preview is the source of truth for visual alignment, typography timing, and effect intensity.
- If a generated clip fails QC and the edit cannot hide it cleanly, regenerate or replace the cut instead of presenting a weak final.

### Mode A: Music Video / MV typography and story memory
Use this mode when the user asks for 뮤직비디오, MV, 노래 기반 영상, 가사/비트/음악 중심 영상, review prototype, or a song-first project.

Typography/story behavior:
- Typography can be more lyrical, poetic, sparse, rhythmic, and emotionally timed; it does not always need to explain every visual literally.
- Text should support lyric hooks, repeated motifs, emotional turns, or chorus/bridge structure rather than becoming a public-information caption system.
- If a narrative exists, keep it cinematic and sensorial; let images, bodies, reflections, hands, shadows, and recurring motifs carry meaning.
- MV final delivery should include master, clean/no-subtitle master when relevant, ordered clips, audio, EDL/manifest, review contact sheet/keyframes, and notes.

### Mode B: Public contest / tourism / institution typography and submission memory
Use this mode when the user asks for 공모전, 관광영상, 지자체/공공기관, 제출, 신청서, 유튜브 업로드, 메일 제출, 심사용 영상, or public-sector promotion.

Typography/story behavior:
- Story clarity beats pure mood: captions must explain why each motif exists and how it relates to the contest theme.
- Typography should be readable, restrained, culturally appropriate, and not a generic subtitle/presentation template.
- Do not assume a title/body structure from a prior project; design typography for the current story, footage, and contest brief.
- CapCut-first handoff remains important; keep editable CapCut text layers where practical and verify in the actual preview.
- Public-sector copy must distinguish roles: title, chapter/location note, narration/body copy, final statement, AI-use disclosure, synopsis, and submission notes.
- Submission safety applies: verify official requirements and account/channel/recipient, prepare forms/copy packages carefully, and do not final-submit or publish without explicit user approval.
- Field-specific copy distinction is mandatory: 제작 의도, 시놉시스, AI 활용 내역, link/password notes, and prior-contest history must not be reused as the same paragraph.

### Memory routing rule
When the user approves a lesson during a project, save it under the appropriate bucket:
- music/cut/effect/QC basics → shared baseline;
- poetic lyric/title behavior → MV typography/story;
- explanatory public-sector captions, forms, upload, email, compliance → public contest/institution memory.

## Music Video Production Team Standing Rules

These rules apply to all future MV/video-agent work unless the user explicitly overrides them. They are global team memory, not one-project notes.

Mode boundary: this section is primarily for song-first MV production logistics and visual pipeline. Music-first cut timing is now a shared baseline for all serious video work; the main difference for public-contest/tourism/institution videos is typography, explanatory story copy, compliance, and submission workflow.

### Tool routing hard rule
- For the user's MV/video-agent pipeline, **all still images/styleframes/start frames/character sheets must be generated with Codex `imagegen` / built-in `image_gen` by default** when available.
- **Do not use Grok for still image generation** unless the user explicitly overrides this for that specific job.
- **Use Grok only for image-to-video/videoization** after a Codex imagegen frame already exists, has been saved, and has passed image QC.
- If Codex imagegen still-image production is blocked mid-project, do **not** switch Grok into still-image generation by default. Continue production by using Grok/Runway/Seedance only for I2V/videoization from any approved/saved existing frame, acceptable fallback frame, or other user-approved source frame so the edit can keep moving without a question.
- Do not use Kling in this user's default MV/video pipeline unless explicitly requested.
- If any local plan, prompt package, or older skill says `Grok image prompt`, `grok_image`, or “ChatGPT Image 2 browser generation”, reinterpret/update it as `Codex imagegen styleframe prompt` unless the user explicitly requests browser generation.
- For a **new project**, create/save character sheets and production styleframes through Codex imagegen first; ChatGPT web/new-tab generation is fallback/manual only when imagegen is unavailable or explicitly requested.
- Codex imagegen production must remain **one cut = one prompt = one standalone image**. Do not request 2x2 grids, contact sheets, collages, or multi-panel sheets for production styleframes.
- Fast production may batch up to four separate Codex imagegen calls conceptually, one cut prompt per call, then QC the resulting independent images together. This is allowed only if each request remains a standalone one-cut image; never combine four cuts into one prompt or ask for a 2x2/grid/contact sheet.

### Operating mode
- Default to **no-question, one-block execution** for MV production: analyze → cut design → image generation → image-to-video → edit → QC → package, without asking between routine steps.
- Ask only for login/payment/CAPTCHA/account/sensitive upload/deletion or when the user explicitly requests a review gate.
- Do not present a weak draft as final. If quality fails, mark it as failed, write the reason, and continue with the next production correction.

### Music-first editing
- Cut structure must come from the song: beat, accents, phrase changes, lyric hooks, energy curve, and natural cadence/ending.
- Do not force a prewritten visual table onto the music.
- For ~1 minute review prototypes, make reviewable MV cuts that test rhythm/story/look before longer versions.

### No stills in final edit
- Raw PNG/JPG styleframes are only source frames for I2V. They must never be placed directly in a final/review edit.
- No static-image zoompan filler in final/review masters. If a videoized clip is missing, generate/regenerate the clip.

### Unique media rule
- One generated video clip may appear in the timeline exactly once.
- Avoid image reuse. If the same location/motif returns, generate a new frame with changed composition, angle, action, lighting, or story function.
- Repeated motif is allowed; repeated image/video file is not.

### Story and scene sense
- Every cut needs a reason: new action, new information, emotional shift, rhythmic accent, or narrative transition.
- Keep a one-sentence premise and cause→discovery→turn/pursuit→resolution spine before batch production.
- Good user-approved shots become structural anchors, not decorative inserts.

### Low Signal lessons carried forward
- Do not cap MV cuts arbitrarily; cut count follows song density and story needs.
- Self-contained delivery is mandatory: final master, clean/no-subtitle master when relevant, ordered clips, audio, EDL/manifest CSV+JSON, review contact sheet/keyframes, notes.
- Review contact sheets are mandatory before claiming completion; inspect repeated impressions, missing anchors, unwanted motifs, and unclear story.
- Avoid unwanted motifs after rejection. For `mv-low-signal`: no earpiece/earbuds/headset/cable-to-ear, no talking-mouth/lip-sync/dialogue-looking shots.
- Prefer physical/visual storytelling through body, hands, eyes, silhouettes, reflections, walls, floors, puddles, shadows, light traces, and city layers.

### I2V crop and identity lock
- For partial-face, eye, hand, object, silhouette, reflection, macro, or symbolic source frames, the I2V model must preserve the original crop and composition. Do not allow zoom-out, reframing, or expansion into a full face/body unless the cut brief explicitly asks for that reveal.
- If a source frame only shows eyes or a facial fragment, the generated clip must remain an extreme close-up. A full-face hallucination is a character-consistency failure and must be rejected/regenerated.
- Character identity is judged by the whole face silhouette, nose, jaw, eye spacing, hair mass, age impression, and costume continuity, not only by eye color/hair color. If an I2V output “looks like another person,” reject it even when technically polished.
- For fragile close-ups, prompts must include explicit locks such as: `preserve exact crop`, `do not reveal full face`, `no zoom out`, `no new facial structure`, `only eyelid/iris/reflection micro-motion`.

## Typography and transition QC standing rule — 2026-05-06

Mode note: these typography/transition rules are shared, but public-contest videos require extra narrative clarity and compliance; MV videos require extra song/beat sensitivity.

The user strongly dislikes lower-center narration subtitles inside obvious rounded boxes. For MV/public-contest edits, avoid generic YouTube/presentation subtitle styling. Narration text should feel quiet, cinematic, and literary: usually unboxed or near-unboxed, with restrained shadow/gradient only when legibility requires it. Use a separate, calmer/static-feeling font for narration/body copy rather than the same bold public-presentation font used for chapter cards.

Typography QC must explicitly check:
- no subtitle/card overlap at any time;
- no `SCENE 03`-style mechanical labels unless the user asks;
- no direct contest-title wording such as “2026 영상 공모전” in the picture unless strategically required;
- lower-center narration must not cover too much image, must not sit in a big black rounded rectangle, and must feel integrated with the scene;
- chapter cards, location notes, and narration should be separated by role, font, size, opacity, and timing;
- tourism/MV location labels must not remain thin, bland, low-visibility museum captions. If rejected, redesign as a full title system: heavier Hangul, larger phone-readable scale, clear kicker/main hierarchy, warm ivory/gold palette, culturally specific motifs, and composition-aware placement;
- after readability is secured, remove obvious translucent boxes/plates unless absolutely required; rely on stroke/shadow/local vignette first;
- underline/route-line motifs must have finished craft: thinner tapered/feathered strokes, rounded caps/joins, soft glow/blur, eased opacity, and no crude rectangular endpoints;
- for right-aligned labels, ornaments/seals/bullets/route-line starts stay on the visual left of the text block. Do not let symbols jump to the far right just because the text is right-aligned.

Transition QC must explicitly check the first third of the edit for cut-to-cut frame jitter, micro stutters, duplicate/freezing frames, bad crossfade handles, optical-flow artifacts, and 1-frame flashes. If jitter is visible, fix with clean cut handles, short dip/dissolve only where motivated, re-encoding/normalization, or by trimming unstable first/last frames of generated clips before final export.


## CapCut Korean caption shadow/legibility rule — KAIA lesson — 2026-05-13

Apply this globally for the user's MV, public-contest, tourism, institution, and CapCut typography work.

Core lesson from the user's final KAIA CapCut export:
- Do **not** try to fix low-visibility Korean captions by randomly changing colors such as mint, bright yellow, or other flashy accents.
- First make the caption readable with fundamentals: **short copy, large type, actual shadow enabled, shadow opacity around 50–70% as the default starting point, subtle dark stroke, and enough hold time**.
- For bright sky, sunset, city-light, glass, HUD, and complex backgrounds, shadow must be treated as a required legibility layer, not an optional decoration. Start near 50% opacity, then raise/lower by actual CapCut preview/export.
- Prefer white or warm/cool off-white text with dark shadow/stroke for public-sector technology videos. Use accent color only when it has a clear narrative/information role and passes preview QC.
- Avoid ugly rounded subtitle boxes. Use shadow/stroke/local placement first; boxes or plates are last resort.
- Reduce or remove tiny helper labels if they compete with the main caption. Short, large, readable main phrases beat cluttered multi-layer information.
- QC must inspect CapCut actual preview and exported full-frame stills, because contact sheets can make fade-in/out frames look weaker than real playback. The hold section of every key caption must be clearly readable.

Default workflow for future CapCut captions:
1. Write the shortest usable Korean phrase.
2. Set readable size and safe placement away from faces, landmarks, HUD, and the brightest background band.
3. Enable shadow; start opacity about **50–70%**, with moderate blur/smoothing and a small distance.
4. Add a subtle dark stroke if needed; do not jump to random colors.
5. Verify in actual CapCut preview, then export/sample-frame QC before claiming PASS.

## CapCut-first typography revision rule — 2026-05-06

For this user's MV/public-contest edit revisions, if the user asks why CapCut is not being used or has previously required CapCut editing, do not keep presenting arbitrary baked local-render typography masters as the main answer. Build or update an editable CapCut draft first, keep typography as editable CapCut text layers where practical, and only render preview MP4s as secondary review aids. Preserve the previous draft before modifying it.

Typography-specific corrections from Sangju V26:
- Reject translucent rounded/oval cards if any text can escape the card boundary; prefer no box or guaranteed fixed-width safe layout.
- Do not let old lyric-subtitle color habits bias public video typography into yellow/white everywhere. Use a broader restrained palette such as ivory, stone, sage, muted clay, charcoal, and only minimal accent color.
- Opening title and final statement must be redesigned, not patched with the same box style.
- Final mnemonic/statement cards must be optically centered and aligned; no pill/box misalignment.

## CapCut font limitation / baked typography exception — 2026-05-06

CapCut remains the required edit-handoff environment when the user asks for CapCut, but macOS CapCut may flatten or fail to expose desirable Korean fonts. In that case, use this workflow instead of forcing bad generic typography:

1. Preserve/update a CapCut draft for timeline review and handoff.
2. Design high-fidelity typography externally with the intended Korean font, layout, timing, and alpha treatment.
3. Render the typography as transparent overlays or a baked master, import/align it back into the CapCut draft when practical, and clearly label it as an intentional font-fidelity workaround.
4. QC must compare the CapCut draft and final rendered master so the delivered video is not merely a local render detached from the user's CapCut workflow.

For public-sector contest films, typography must help explain the work without looking like a presentation template: bigger when needed, timed to reading rhythm, optically aligned, and role-separated into title/chapter/narration/final statement systems.

## Public contest upload/submission safety and copy workflow — 2026-05-06

This section is contest/submission memory, not generic MV memory. Apply it when the project involves public institutions, contest rules, forms, YouTube links, email/package submission, or personal-information workflows.

Lessons from the Sangju public video contest project:

- YouTube upload: before uploading, verify the exact channel/account visually and by URL/channel name. If the user names a specific channel, do not upload to another similarly named channel. If the user does not explicitly ask for public release, upload/save as **private** by default. Do not click public `Publish/게시` without explicit final confirmation.
- Contest/Government form submission: filling a draft with the user's known information is allowed when requested, but final `Submit/제출` for a contest, government, or personal-information form is a high-impact external action. Stop before final submit unless the user explicitly says to submit that exact form now after the filled fields are visible/ready.
- When the user says the final edit is good and asks for the application/submission link, open Finder on the final master/package, open the official contest page, identify the submission route (email vs form), download/open required application forms if available, and prepare a mailto/draft or copy package. Do not send the email or final-submit the form without explicit confirmation.
- Metadata/copy package: public-contest delivery should include or prepare title, YouTube description/hashtags, AI-use disclosure, production intent, synopsis, prior-contest history, and password/link notes. These should be written in a polished public-sector tone: clear, explanatory, not overly poetic, and within character limits.
- Korean browser form input: Safari/YouTube/Google Forms can drop Korean characters when using synthetic typing. Prefer clipboard paste or direct JavaScript setter for Korean text, then verify the field value. After every multi-field fill, audit labels and values so `제작 의도`, `시놉시스`, `AI 활용 내역`, and link/password fields are not swapped.
- Field-specific copy distinction: `AI 활용 내역` describes tools/process; `제작 의도` explains why the work was made and what value it communicates; `시놉시스` summarizes the story flow. Never reuse the same paragraph across these fields.


## ChatGPT web send-button safety rule — 2026-05-07

When automating ChatGPT web in Safari/Browser for image generation, prompt submission, or any composer workflow, avoid accidental activation of Voice mode. The user has observed repeated mistakes where the agent clicks the voice/받아쓰기/Voice button instead of the send button.

Required safeguards:
- Never click the last visible round composer button by position alone. Do not assume the rightmost button is send.
- Before sending, locate the exact send control by a stable selector/label such as `button[data-testid="send-button"]` or an accessible label containing `프롬프트 보내기` / `Send prompt`.
- Explicitly reject buttons whose accessible label or text contains `Voice`, `음성`, `받아쓰기`, `마이크`, `dictation`, or `voice mode`, even if they are near the composer.
- After inserting text, re-query the DOM and verify the send button is enabled and still has the send-specific selector/label before clicking.
- If only a voice/받아쓰기 button is visible, do not click it. Wait, refocus the composer, dispatch an input/change event, or use Enter only if it has already been verified not to trigger voice mode in that UI state.
- If Voice mode or “음성으로 연결 중” is accidentally opened, cancel/close it immediately and record the incident in the local run notes before retrying.
- For fallback ChatGPT web image production only, prefer this safe sequence: set composer text via direct DOM setter/computer-use `set_value`/direct typing → verify composer contains expected text → verify `send-button` identity → click once → verify a normal chat turn started. Do not use `pbcopy`, AppleScript clipboard, or clipboard paste for Codex GUI prompt insertion on this Mac; it can fail silently or return exit 1. Do not use coordinate clicks for ChatGPT submit unless there is no DOM alternative and the user has approved a manual fallback.

## MV character sheet standard — 2026-05-07

For future MV/video-agent projects with recurring characters, a single front-view character reference is not enough for production consistency. Do not retroactively apply this requirement to the already-progressed 2026-05-07 Seongnam Environment Day V4 project, but apply it to new projects and major new character-lock phases.

Research basis: animation/model-sheet references are used to keep proper proportions; industry-style model sheets function as blueprints for constructing consistent 2D/3D characters; production character teams provide sheets showing characters in varied attitudes and angles. References consulted: Concept Art Empire model-sheet gallery, Character Design References model-sheet/full-figure guidance, Character Design References visual library categories for turnarounds/poses, and AnimationResources notes on Disney model sheets from various attitudes and angles.

Minimum character-sheet package before batch styleframes/I2V:
1. **Turnaround sheet**: front, 3/4 front, side/profile, 3/4 back, back view; full body whenever the character appears as a full-body actor.
2. **Head/face sheet**: neutral front, 3/4, profile, mouth-open/speaking, smile, surprise, concern, blink/closed-eyes; keep muzzle/nose/jaw/eye spacing locked.
3. **Expression sheet**: 6-9 emotionally useful expressions matched to the script, not random emojis.
4. **Pose/action sheet**: 4-8 story-relevant poses such as holding a mic, pointing, walking/running, sitting/riding, bending, stamping, pedaling, drawing, carrying props.
5. **Hand/paw/prop interaction sheet**: close-ups for hands/paws gripping signature props, because I2V often drifts there.
6. **Costume/prop sheet**: front/back of core outfit and signature props, with color/material notes and forbidden changes.
7. **Scale sheet**: character height/volume relative to partner characters and common objects when multiple characters interact.

Production rule:
- Generate/approve these sheets with Codex imagegen before the main styleframe batch. One sheet can contain multiple reference panels because it is a design reference, but production styleframes remain one cut = one prompt = one standalone image.
- Attach/pass the relevant sheets as actual image references/inputs to every dependent Codex imagegen styleframe when supported. For fragile shots, attach only the most relevant angle/expression/prop sheets to avoid overloading references; if reference attachment cannot be verified, mark BLOCKED rather than proceeding from memory.
- QC must check identity across angle, silhouette, nose/muzzle/jaw, eye spacing, hair/fur mass, costume, body scale, hand/paw shape, and prop handling. If a later frame only matches color but not structure, reject/regenerate.
- Do not accept “front-view only” as a final character lock for a new recurring-character video unless the character appears in one static front-facing shot only.

## Character-sheet-first correction — 2026-07-06

Apply this to every video-team/MV/public-contest/institution animation project with recurring people or characters.

- Character/model sheets must be created, saved, QC'd, and treated as the identity source **before** production styleframes/start frames for any recurring protagonist, couple, guardian pair, mascot, performer, or repeated citizen character.
- The required minimum is still the full character-sheet standard: approval-oriented bible page when useful, plus clean production model sheet/crops for downstream identity lock. A single attractive hero/reference image is not enough for recurring-character production.
- Production Codex imagegen prompts for dependent cuts must explicitly use/reference the relevant approved sheet(s) and state the identity lock. Do not merely describe the character from memory.
- If styleframes were generated before the required sheets were attached, mark those frames `HOLD_LOOKDEV_ONLY` or `INVALID_PRE_CHARACTER_LOCK_SOURCE`; do not send them to Seedance/Runway/Grok as final I2V sources. Regenerate the affected styleframes from the approved sheets.
- Supporting recurring people such as a driving couple or guardian pair need mini model sheets before their linked cuts. One-off extras may use scene-specific locks, but repeated people must not drift cut to cut.
- QC must explicitly compare each regenerated styleframe against the sheet: face shape, eye spacing, nose/jaw, hair mass, age impression, outfit/materials, hand/prop handling, and role separation. If the output only matches “general style” but not identity, reject/regenerate.

### Current project hard gate — 오늘의 자동완성 / 3D animation — 2026-07-06

- For the current `오늘의 자동완성` shortform and any continuation of it, the saved MAIN / COUPLE / GUARDIANS character sheets are mandatory source references for all dependent styleframe regeneration. Do not treat first-pass styleframes as production sources.
- Each regenerated cut prompt/manifest must name which character sheet(s) were attached or explicitly referenced. If the sheet cannot be attached or verified in the active image-generation route, mark the cut `BLOCKED_CHARACTER_SHEET_ATTACHMENT_NOT_VERIFIED` instead of pretending the sheet was used.
- Pre-character-lock images remain `HOLD_LOOKDEV_ONLY`; they may guide composition/style only and must not be sent to Seedance/Runway/Grok as final I2V references.
- Seedance/Runway should receive only post-character-lock, QC-passed production styleframes/start/end frames. Do not upload raw character sheets to Seedance as the video reference strip unless the user explicitly orders that exception.

## MV typography/editing lesson — 교차 문구 편집 호흡 — 2026-05-10
- In Korean MV/public-contest typography, when transforming phrase A into phrase B in the same position, give B an equivalent solo reading breath to A before introducing any subordinate/lower explanatory line.
- Do not stack the lower line immediately on top of B; sequence as: A appears/holds/fades → B appears/holds in the same visual position → lower support line appears beneath B while preserving the established top/bottom layout.
- QC must inspect the actual CapCut preview for line order, hierarchy, scale, and overlap; JSON timing alone is not enough.

## CapCut editable text visual alignment lesson — 2026-05-10

For this user's CapCut typography work, **equal JSON/transform X values do not guarantee visual alignment**. CapCut editable text is effectively positioned by text-box center and rendered text width, so captions with different Korean line lengths can appear visually misaligned even when their transform coordinates are identical.

Required workflow for future CapCut typography alignment:
- Use the actual CapCut preview as the source of truth, not JSON equality.
- When the user asks to align caption positions, align by the **visible first glyph / left edge in the preview**, not by raw transform coordinates.
- If using draft JSON as a helper, calculate or adjust per-caption X offsets based on rendered text width, then reopen CapCut and visually QC.
- For important public-contest typography, select representative clips in CapCut, inspect the actual preview, and capture screenshots before claiming alignment is fixed.
- If one short line still feels visually off after formulaic correction, apply a direct screen-based manual nudge; visual balance beats numeric symmetry.
- Record this as a CapCut-first typography rule: editable text layer remains preferred, but CapCut UI/preview proof is mandatory for alignment claims.

## Kim Gu contest submission email workflow — 2026-05-10

For the current Kim Gu / 백범 김구 public-contest video project and future follow-up turns in this project, when the user says to send the final video/package by email, use `sajw1994@korea.kr` as the default recipient.

Workflow:
1. Use the approved final master/package from the project as the attachment or link.
2. If the attachment is too large or the mail client rejects it, fall back to Naver Mail as the sending route.
3. Before any actual send, show the recipient, subject, body, attachment/link, and final file path to the user.
4. Sending is an externally visible action: do not click final Send/전송 until the user explicitly approves that exact prepared email.
5. If the user simply says “메일 보내라” after approving the final video in this project, interpret the recipient as `sajw1994@korea.kr` unless the user states another recipient.

## Seedance execution authority

Seedance prompt authoring and all Runway UI operation follow only `/Users/gnudas/.codex/skills/seedance-prompt-en/SKILL.md`. Do not add UI upload/click/queue/scheduler rules here.

## Gongnyang image-prompt compiler default — 2026-07-12

For the user's raster-image work, load the installed Codex skill `/Users/gnudas/.codex/skills/image-prompt/SKILL.md` before calling built-in `image_gen`. Compile the rough request with the Gongnyang prompt rules, then pass only the compiled production prompt to `image_gen`.

- Apply by default to new still images, posters, key art, styleframes, character/model sheets, product images, card news, infographics, comics, and image prompt packages.
- The Gongnyang skill is the prompt-compilation layer; Codex built-in `image_gen` remains the actual still-image generator.
- For high-value prompts, run `/Users/gnudas/.codex/skills/image-prompt/scripts/check_prompt.mjs` and require `ok: true` before generation.
- Existing higher-priority video rules remain in force: recurring-character sheets precede dependent production frames; attach and verify approved references; one production cut equals one standalone image; no Grok still generation; no production grids/contact sheets.
- For edits of an existing image, preserve the user's requested edit and supplied reference as the primary constraint; use Gongnyang rules only where they do not distort that edit intent.
