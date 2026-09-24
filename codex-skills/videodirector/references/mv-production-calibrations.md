# Deferred video calibration — mv production calibrations

This file preserves the corresponding Codex global video guidance. Read only when the current task needs this phase. Runtime rails/safety and the selected Seedance skill remain authoritative in their scopes.

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
- Fast production may run up to three separate bounded Codex imagegen calls concurrently, one immutable one-cut prompt per worker, then fan in and QC the independent images. Additional cuts wait for the next batch; never combine cuts into one prompt or request a production grid/contact sheet.

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

<!-- End deferred guidance -->
