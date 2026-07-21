---
name: seedance-prompt-en
description: MUST load whenever Seedance, Seedance 2.0, Jimeng/即梦, Runway Seedance, I2V/video generation prompts, multi-reference video prompts, Seedance block prompts, Seedance retries, Seedance QC prompt diagnosis, or Seedance-related video planning are mentioned. Write effective prompts for Jimeng Seedance 2.0 multimodal AI video generation using the @ reference system, camera/action/timing/audio roles, music beat-matching, extension/editing, and constraints.
---

# Seedance 2.0 Video Prompt Writing Guide

## Description

You are an expert prompt engineer for **Jimeng Seedance 2.0**, ByteDance's multimodal AI video generation model. Your role is to help users craft precise, effective prompts that produce high-quality AI-generated videos. You understand the model's capabilities, input constraints, referencing syntax, and best practices for camera work, storytelling, sound design, and visual effects.


## Seedance2.ai Korean Guide Integration — added 2026-07-21

When writing **Seedance video prompts**, incorporate the following operating rules from the Korean guide at `https://seedance2.ai/ko/guide` (retrieved 2026-07-21). Treat this as an additional source-specific checklist layered on top of the existing user video-team rules.

### 1) Basic prompt formula from the guide
Every prompt must clearly cover the two mandatory logic anchors before style language:

```text
Subject + Motion + optional Environment + optional Aesthetic + optional Camera + optional Audio
```

- **Subject**: define who/what the video is about.
- **Motion**: define what the subject does; do not leave the clip as pure mood.
- **Environment / Aesthetic**: describe spatial background, lighting, visual style, and atmosphere only after subject and action are clear.
- **Camera / Audio**: add camera choreography and ambient sound/rhythm when they help immersion or timing.

Default compiler rule: if a draft prompt only says mood/style, rewrite it so `Subject` and `Motion` are explicit first.

### 2) Multimodal reference control
The guide emphasizes explicit reference targeting. For every uploaded reference, state exactly **which element** is being used and **what must remain consistent**. Use ordered names matching the UI upload order: `Image 1`, `Image 2`, `Video 1`, `Audio 1`, etc.

Required reference-role grammar:

```text
Reference / extract / combine / follow [Image N or Video N]'s [specific element],
generate [scene description], while maintaining consistent [feature/motion/camera/effect].
```

Examples of role types to encode:
- `Image N` for subject identity, product details, outfit, logo, scene/background, storyboard panel, first frame, last frame.
- `Video N` for action choreography, camera movement, visual effect, transition behavior, or original clip to edit/extend.
- `Audio N` for narration cadence, BGM, SFX, rhythm, or performed guide audio when applicable.

If multiple references are uploaded, write a visible role map at the top of the prompt/operator card. Never rely on the model to infer which file controls identity vs environment vs camera.

### 3) Video-in-video text control
Seedance supports text overlays in T2V/I2V/R2V/V2V, but the guide's prompt shape must be made explicit when text is required. Use ordinary characters; avoid rare symbols and special glyphs.

Prompt forms:

```text
Slogan/title: [exact text] + [display timing] + [screen position] + [reveal method], [text style/color/font].
Subtitle: subtitles reading "..." appear at the bottom in sync with the audio rhythm.
Speech bubble: [character] says "..."; a speech bubble containing the dialogue appears near the character.
```

User override for this workspace: because final Korean typography is usually CapCut-first, only generate Seedance text when intentionally testing native text, diegetic signage, speech bubbles, or temporary scratch captions. For final public-contest/MV captions, prefer editable CapCut/baked typography after video generation unless the user explicitly wants native Seedance text.

### 4) Image-reference modes
Use the guide's two image-reference categories explicitly:

#### Multi-angle subject reference
For products or characters, write:

```text
Extract/reference the [subject] from Image 1, Image 2, Image 3.
Generate [new scene/action], while keeping the subject's consistent features.
```

Use for recurring characters, products, mascot/body/face locks, and turnaround-like references. For this user's video workflow, this does **not** replace the stricter character-sheet-first rule; approved character/model sheets still must be attached/verified before dependent recurring-character shots.

#### Multi-image reference
For scenes with several controlled elements, write each role separately:

```text
Image 1 controls [character/product/logo].
Image 2 controls [outfit/prop].
Image 3 controls [environment/storyboard composition].
Generate [action] while maintaining consistent [named element] features.
```

For storyboards, state that panel compositions appear in the uploaded order. If using logo/text reference, specify persistent position and timing.

### 5) Video-reference modes
When a video is uploaded, do not just say `reference Video 1`. Use one of the guide's concrete control targets:

```text
Action reference: Follow Video 1's [action description], generate [new scene], maintain consistent action details.
Camera reference: Follow Video 1's [camera movement], generate [new scene], maintain the same camera path/feeling.
Effect reference: Follow Video 1's [effect description], generate [new scene], maintain the same effect trajectory/timing.
```

If a reference video controls multiple roles, list them separately: `Video 1 controls action choreography and camera movement; Image 2 controls left character; Image 1 controls right character.`

### 6) Video-editing / extension / track-completion prompt forms
For V2V or editing-style work, use the guide's precise edit verbs. Keep preservation requirements explicit.

```text
Add element: Add [desired element] at [time position] and [spatial position] in Video N.
Remove element: Remove [element] from Video N while keeping everything else unchanged.
Modify element: Replace [original element] in Video N with [desired element/reference], keeping motion and camera movement unchanged.
Extend backward/forward: Generate content before/after Video N: [extension content].
Track completion: Connect Video 1 to Video 2 to Video 3 using [transition description].
```

For track completion, remember the guide's practical constraint: up to 3 video inputs and total uploaded video duration must remain within the model limit; prompts should describe only the necessary bridge/transition rather than asking to duplicate the original segments.

### 7) Source-guide QA checklist
Before handing off a Seedance prompt/operator card, check:

- Subject and motion are explicit.
- Each reference file has a numbered role and a preservation target.
- Text overlay requests include exact content, timing, position, display method, and style; unnecessary native text is removed for CapCut-first projects.
- Image references distinguish subject, outfit/prop, scene, storyboard, and logo roles.
- Video references specify action vs camera vs effect vs edit/extension role.
- Editing prompts use add/remove/modify/extend/connect verbs and say what remains unchanged.
- Ordered references in the prompt match visible UI thumbnail order; if not verified, fix the UI before prompting.



## Higgsfield Community Video Pattern Mining — added 2026-07-21

Use this section when compiling **video generation prompts** after the user asks to learn from Higgsfield community examples. Source basis: public Higgsfield community pages (`https://higgsfield.ai/community`, `/community/generations`, `/community/projects`) and the public community-approved video feed discovered from the site JS on 2026-07-21. A local study sampled 50 approved `wan2_5_video` community generations and read at least 25; the following rules synthesize patterns from at least 15 examples. Do **not** copy community prompts verbatim; extract the directing grammar only.

### 1) Higgsfield-style shot contract
Community video prompts that read as controlled usually open with concrete cinematography, not broad style adjectives. Prefer this order:

```text
[Shot size] + [camera position/mount] + [lens or framing] + [subject identity/action] +
[environment/light/depth] + [one dominant camera path] + [physical motion layers] +
[sound/rhythm cues] + [mood/style] + [stability/preservation constraints]
```

If a draft says only `cinematic, beautiful, dynamic`, rewrite it into camera physics: where the camera is, whether it is mounted/handheld/static/orbiting/dollying, what moves, what stays stable, and what environmental details prove motion.

### 2) One dominant camera move per short clip
The sampled community examples often succeed by committing to a single legible camera grammar for 5–10 seconds:

- **Through-aperture / portal push**: camera moves fast forward through a circular frame, keyhole, gap, mouth, eye/pupil, window, doorway, or object opening. State the aperture edge, entry direction, revealed subject, and when the foreground edge leaves frame.
- **Mounted-camera drive**: camera is fixed to a car body, wheel, dashboard, passenger side, or other moving object. Lock the camera to the object; the background streaks, vibrates, and parallax-shifts instead.
- **Handheld intimate track**: slight tremble, small focus adjustments, forward tracking, and natural subject micro-actions such as smoking, phone interaction, walking, conversation, or glances.
- **Slow dolly-in / dolly-out**: one precise move toward a gaze/detail or away to reveal environment, with shake-free uniform speed.
- **Static camera, active subject**: keep the frame fixed while the actor/dancer/hand/hat/silhouette performs a simple clear action. Use when identity stability matters.
- **Bullet-time orbit**: subject is frozen mid-action while camera orbits 180–270 degrees; include foreground occluders, background parallax, floating particles/dust/grass, lens choice, and final three-quarter angle.
- **Pan reveal**: camera pans/rotates from subject to environment, usually revealing skyline, interior, group, or emotional context.

Default rule: for Seedance/Runway prompts, name the camera move in natural language even if the UI has a motion preset or Higgsfield-style `motion_id`. The preset is not a substitute for direction.

### 3) Normal-speed vs frozen-state must be explicit
Higgsfield examples repeatedly specify whether the subject remains at normal speed, moves subtly, or is frozen in suspended time. Add one of these states per beat:

```text
Subject motion state: normal-speed stillness with micro-expression / steady walk / simple hand action / frozen mid-air bullet-time / static silhouette dance / vehicle-mounted rush.
```

For close-ups and fragile faces/hands, prefer micro-action: breath, eye movement, hair, smoke, fabric, hand settling, tiny head turn. For high-energy action, add environmental motion instead of over-animating anatomy.

### 4) Physical motion layers beat generic mood
Add 2–4 concrete motion layers that make the generated video feel filmed:

- smoke inhaled/exhaled, dust clouds, rubber particles, grass blades, airborne particles;
- wind through hair/clothes, train sway, car vibration, tire rotation, streetlight flicker;
- reflections on metal/glass, neon signs sliding across windows, sunset color shift;
- foreground occluders passing camera, aperture edges exiting frame, background parallax;
- ambient sound bed: traffic, train rolling, engine hum, wind, distant city, murmurs.

Do not add many unrelated effects. Pick layers motivated by the camera move and subject action.

### 5) Prompt templates distilled from community examples

#### Through-aperture / reveal
```text
The camera starts close to [aperture/object edge], then moves fast straight forward through [opening].
As the foreground edges leave the frame, it reveals [subject] in [environment].
[Subject] remains [motion state]; [small physical elements] move naturally.
Lighting: [specific]. Camera: [lens/framing], smooth/handheld as needed.
End on [clear final composition].
```

#### Mounted vehicle/object camera
```text
The camera is fixed/mounted to [vehicle/object position], [angle/lens].
[Vehicle/object] moves [speed/direction]. The camera stays locked to the frame,
while [road/buildings/lights/background] streak/parallax past.
Add [vibration/wind/tire/engine/sound] cues. Keep subject/vehicle geometry stable.
```

#### Bullet-time orbit
```text
[Subject] is frozen mid-[action], suspended in time.
The camera orbits [180/270] degrees from [start angle] to [final angle] at [distance],
with [foreground occluders] and [background] creating parallax.
[Particles/dust/hair/cloth] hang in the air; [lens/depth] isolates the subject.
End on [three-quarter/profile/detail] with the action still frozen.
```

#### Static-frame subject action
```text
Static camera, [shot size], [lens/framing]. [Subject] performs one simple action: [action].
The background stays stable; only [body part/prop/environment micro-motion] moves.
Lighting and texture: [specific]. No camera drift, no extra action, no new props.
```

### 6) Safety/adaptation rule for community motifs
Some community examples use celebrity/real-person cameo dialogue or likeness. For this user's production prompts, do not reproduce real-person likeness, living-celebrity cameos, or branded/IP elements unless the user has explicit rights and requests it. Convert the pattern into a fictional archetype: `a famous tech-founder-like fictional entrepreneur`, `a glamorous fictional actor`, etc., or remove the cameo.

### 7) Higgsfield-pattern QA
Before handing off a prompt influenced by Higgsfield examples, verify:

- At least one exact shot size or camera position is stated.
- Exactly one dominant camera move controls the clip unless it is explicitly a multi-shot montage.
- Subject motion state is explicit: normal-speed / micro / static / frozen / vehicle-mounted.
- The prompt includes physical motion layers, not just mood.
- If an aperture/portal move is used, the entry object, reveal target, and final composition are clear.
- If mounted-camera is used, camera is locked to the object and background motion carries speed.
- If bullet-time is used, freeze state, orbit degrees, parallax, particles, and final angle are specified.
- Real-person/IP cameos from community examples are not copied into production prompts.


## Higgsfield Deep Community Research Upgrade — added 2026-07-21

Apply this after the first Higgsfield pattern section when a prompt needs richer video direction, especially for Seedance/Runway/I2V clips, ad/UGC videos, transition shots, vehicle/speed shots, or action/motion-control shots.

Research basis: deeper public Higgsfield community study on 2026-07-21: 126 deduplicated video-like community prompts (`wan2_5_video`, `kling3_0`, `marketing_studio_video`), 100 public motion preset names, 51 project publications, and selected motion samples. Do not copy prompts verbatim; use the directing grammar.

### 1) Camera grammar is a routing decision
Before writing style, choose the clip's **camera family**:

| Clip role | Camera family | Prompt obligation | Avoid |
|---|---|---|---|
| Identity/emotion close-up | static / slow push / macro-in | micro motion, crop lock, lens/focus behavior | fast zoom, new face/body |
| Speed / vehicle / travel | mounted-object / Car Grip | camera fixed to object, background parallax, vibration, wind/engine | camera floating independently |
| Reveal / transition | through-object / aperture / portal | entry geometry, object edge, reveal target, final composition | vague “portal effect” |
| Action highlight | bullet-time / orbit / arc | frozen or exact motion state, orbit degrees/path, parallax, particles | normal-speed generic orbit |
| Fashion/group pose | dolly/pan/static | pose hierarchy, subtle gestures, environment depth | over-animated crowd |
| UGC/product proof | handheld phone / selfie / jump cuts | hook, product handling, tactile proof, imperfect phone realism | over-polished cinema look |
| Public/institution | restrained static/dolly/pan | dignified physical action, clarity, no spectacle | blockbuster chaos |
| MV/music beat | beat-selected camera move | rhythm cue, one dominant move, motivated sensory layer | random effects |

### 2) Duration-to-complexity budget
Use duration as a hard complexity budget:

- **5–6s**: one action or one camera trick. No full story arc.
- **7–10s**: one continuous setup → action → reveal, or 2–3 clean beats.
- **11–15s**: UGC/ad sequences may use hook → proof → payoff or short montage. Every beat still needs shot size and action.

If the prompt contains more actions than the duration can hold, split the block or remove actions.

### 3) Translate motion/preset names into physical language
Higgsfield exposes names such as `Handheld`, `Static`, `Bullet Time`, `Dolly In/Out/Left/Right`, `Pan Left/Right`, `Car Grip`, `Through Object In/Out`, `Eyes In`, `Mouth In`, `FPV Drone`, `Arc Right`, `Face Punch`, `Building Explosion`, and transition families (`Raven/Splash/Flame/Melt/Smoke/Hand/Jump/Roll/Display Transition`).

Never rely on a preset name alone. Translate it into:

```text
Camera mount/position + direction/path + subject motion state + foreground/background relationship + physical motion layers + final frame.
```

Examples of translation, not copy targets:
- `Handheld` → subtle operator tremble, focus breathing, human inertia, not random shake.
- `Static` → locked frame, one simple action, stable background.
- `Car Grip` → camera bolted to car/wheel/object; environment streaks and vibrates around it.
- `Through Object In/Out` / `Mouth In` / `Eyes In` → aperture geometry, entry/exit edge, transition target, final composition.
- `Bullet Time` / `Arc Right` → frozen subject, orbit degree/path, parallax layers, particles, final angle.
- `FPV Drone` / `Flying Cam` → continuous traversable path, obstacles, altitude, acceleration, stabilization.
- VFX/action presets → cause → effect → aftermath, with debris/lighting/safety limits.

### 4) Physical motion layer menu
Community prompts repeatedly use small physical evidence to make a clip feel filmed. Add **2–4 motivated layers**, not a pile:

- hair/fabric/breath/smoke for human micro-motion;
- dust/debris/particles/grass/rubber for impact and sports;
- wind/rain/train sway/car vibration/engine hum for travel or speed;
- reflections/neon/flicker/shadows/lens flare for lighting movement;
- foreground occluders/background parallax/aperture-edge exit for camera motion;
- ambient sound bed: traffic, room tone, train, engine, murmurs, crowd, rain.

### 5) UGC / product / ad grammar
For product or creator-style videos, do **not** use the same grammar as cinematic MV shots. Use:

```text
Vertical 9:16, iPhone/front-camera or handheld phone POV, authentic amateur feel,
hook in 0–2s, product visible early, tactile proof action, short spoken line,
real room/daylight details, slight handheld imperfection.
```

Product proof actions: rotate product, tap, sip, crunch, open/tear wrapper, unbox, show handle/lid/logo/material, compare before/after, fit check, app screen tap, mirror try-on.

UGC negatives when relevant: no cinematic grading, no filters, no visible filming device in mirror, no over-polished studio look, no fake influencer smile, no unreadable app UI, no product morphing, no wrong logo/text.

### 6) Negative tail as a menu, not a wall
The sampled `wan2_5_video` examples often repeat: overexposed, blurred details, subtitles, jpeg artifacts, unnatural motion, extra fingers, bad hands, still image, cluttered background, duplicate limbs, random text, deformed face, asymmetrical eyes, bad anatomy, morphing, face distortion.

For this workflow, choose only the relevant risks:
- human close-up → no new facial structure, no face distortion, no asymmetrical eyes, no bad hands if hands visible;
- hand/product → no extra fingers, no product morphing, no logo/text corruption;
- transition → no random object substitution, no location reset, preserve final target;
- public/institution → no logos/readable signs/flags/partisan symbols unless intended, no spectacle;
- MV/CapCut workflow → no generated subtitles/text unless intentionally diegetic or scratch.

### 7) Deep Higgsfield QA gate
Before finalizing a prompt influenced by this research, answer:

1. What is the clip role? identity / reveal / speed / action / product proof / UGC hook / atmosphere / montage / transition.
2. What is the single dominant camera family?
3. Is the action budget plausible for the selected duration?
4. Is subject motion state explicit?
5. Are there 2–4 physical motion layers tied to the shot, not random effects?
6. If a motion preset name is used, has it been translated into camera physics?
7. Is the negative tail role-specific rather than a generic wall?
8. Are real-person/IP cameos removed or converted to fictional/authorized archetypes?


## System Constraints

### Input Limits
| Input Type | Limit | Format | Max Size |
|---|---|---|---|
| Images | ≤ 9 | jpeg, png, webp, bmp, tiff, gif | 30 MB each |
| Videos | ≤ 3 | mp4, mov | 50 MB each, total duration 2–15s |
| Audio | ≤ 3 | mp3, wav | 15 MB each, total duration ≤ 15s |
| Text | Natural language prompt | — | — |
| **Total files** | **≤ 12 combined** | — | — |

### Output
- Video duration: 4–15 seconds (user-selectable)
- Includes auto-generated sound effects / background music
- Resolution range: 480p (640×640) to 720p (834×1112)

### Restrictions
- **No realistic human faces** in uploaded images/videos (platform compliance). The system will block such uploads.
- When using reference videos, generation cost is slightly higher.
- Prioritize uploading materials that most influence visuals or rhythm.

---

## Core Syntax: The @ Reference System

Seedance 2.0 uses `@` to assign roles to each uploaded asset. This is the most critical part of prompt writing.

### How to Reference
```
@Image1    @Image2    @Image3   ...
@Video1    @Video2    @Video3
@Audio1    @Audio2    @Audio3
```

### Assigning Roles to References
Always explicitly state **what each reference is for**:

| Purpose | Example Syntax |
|---|---|
| First frame | `@Image1 as the first frame` |
| Last frame | `@Image2 as the last frame` |
| Character appearance | `@Image1's character as the subject` |
| Scene/background | `scene references @Image3` |
| Camera movement | `reference @Video1's camera movement` |
| Action/motion | `reference @Video1's action choreography` |
| Visual effects | `completely reference @Video1's effects and transitions` |
| Rhythm/tempo | `video rhythm references @Video1` |
| Voice/tone | `narration voice references @Video1` |
| Background music | `BGM references @Audio1` |
| Sound effects | `sound effects reference @Video3's audio` |
| Outfit/clothing | `wearing the outfit from @Image2` |
| Product appearance | `product details reference @Image3` |

### Multi-Reference Combinations
You can combine multiple references in a single prompt:
```
@Image1's character as the subject, reference @Video1's camera movement
and action choreography, BGM references @Audio1, scene references @Image2
```

---

## Prompt Structure Blueprint

### Formula
A well-structured Seedance 2.0 prompt follows this pattern:

```
[Subject/Character Setup] + [Scene/Environment] + [Action/Motion Description] +
[Camera Movement] + [Timing Breakdown] + [Transitions/Effects] +
[Audio/Sound Design] + [Style/Mood]
```

### Time-Segmented Prompts (Recommended for 10s+ videos)
For precise control, break your prompt into timed segments:

```
0–3s: [opening scene description, camera, action]
3–6s: [mid-section development]
6–10s: [climax or key action]
10–15s: [resolution, ending shot, final text/branding]
```

### Awesome-Seedance Practical Pattern Upgrade

Use these patterns when writing or diagnosing Seedance prompts, based on
structure mining from `ZeroLu/awesome-seedance` (README and prompt packs,
retrieved 2026-06-06). Do not copy prompt examples verbatim; extract the
operating pattern and adapt it to the current project.

#### Pattern A: Shot-header grammar beats plain description
For multi-shot prompts, each time segment should include:

```
[time range] Shot N: [shot size / camera position] ([dramatic function]).
Scene/subject: ...
Action/motion: ...
Camera: ...
Lighting/atmosphere: ...
Sound or rhythm cue: ...
```

Prefer concrete shot labels such as `Wide establishing shot`, `Interior
close-up`, `Low-angle wide shot`, `Slow push-in to medium shot`, `Hard cut
to detail`, `Final static hold` over generic "cinematic scene".

#### Pattern B: Escalation arc for 10–15s generations
Strong Seedance examples usually escalate across the whole duration:

1. **Establish** location, scale, object, or emotional premise.
2. **Approach / reveal** with a clear camera move or subject action.
3. **Detail / transformation / interaction** with tactile motion.
4. **Resolution / hold / cut-to-black** with a fade-ready frame.

For public-culture or documentary videos, make the escalation dignified
rather than spectacular: light grows, reflections move, hands repair,
silhouettes pause, space opens. Do not add action set-pieces just because
the source examples are dramatic.

#### Pattern C: Sensory physics improve motion
Every beat needs at least one physical driver, not only mood:

- rain hitting glass / floor reflections / ripples;
- dust, paper fibers, particles, smoke, mist, breath, fabric movement;
- light streaks, neon/LED flicker, projected light sliding across a wall;
- hand pressure, object rotation, walking cadence, small posture shift;
- sound-design cue even when final edit mutes model audio.

Use these to prevent "still image slideshow" outputs.

#### Pattern D: Music and sound are prompt controls
Even if generated audio will be muted in final edit, include sound/rhythm
direction because it helps the model time motion:

```
Rhythm: match the locked music phrase; first beat quiet, second beat reveal,
third beat tactile detail, final beat stable hold. Generated audio ignored
in final edit; if produced, keep only room tone / rain / paper rustle.
```

#### Pattern E: Reference roles must be stronger than style roles
For multi-reference blocks, state both sequence order and role:

```
@Image1 = Shot 1 first keyframe / composition anchor.
@Image2 = Shot 2 transition target / environment anchor.
@Image3 = Shot 3 tactile detail / motion anchor.
@Image4 = Shot 4 final hold / emotional resolution.
```

If a reference is abstract, state what it must **not** become (e.g. "paper
crane remains folded paper, not a living bird").

#### Pattern F: Public-contest safety tail
For institution/public-contest videos, append a compact negative tail:

```
No readable signs, no logos, no watermarks, no flags or partisan symbols,
no political rally spectacle, no gore, no violence, no new objects, no
identifiable realistic face close-up, preserve crop and reference order.
```

Do not use generic blockbuster prompt tails such as "8K disaster scale" for
public-sector pieces unless the brief explicitly requires spectacle.

#### Pattern G: Retry diagnosis
When a Seedance result fails, diagnose by failure mode and rewrite only the
needed part:

- **Collapsed into one scene** → repeat exact ordered `@ImageN -> @ImageN`
  sequence and use explicit shot headers.
- **Too static** → add sensory physics and camera verbs per beat.
- **Reference drift** → assign each reference a non-negotiable role and
  preserve crop/composition.
- **Unwanted literalization** → name metaphorical objects and forbid literal
  substitutions.
- **Over-animated hands/faces** → limit to micro-motion and add anatomy locks.
- **Wrong format/order** → stop prompting; fix UI thumbnails/settings first.

---

### Runway Web UI Reference Upload Lesson — corrected 2026-07-12

For the user's current no-I2V Runway/Seedance workflow, the verified first route is **Finder-frontmost direct drag/drop**, not the asset selector or file picker.

Required default:
- **HARD LOCK:** For this no-I2V team, the Finder-frontmost direct-drag state machine is mandatory. Do not improvise a Reference-tile, asset-selector, or file-picker route before completing the direct-drag preflight. If the current reference/background hashes already match, do not upload anything; use prompt/settings-only operation.
- Stage one exact file in a small Finder window and keep Finder frontmost, visibly above or beside Safari.
- Do **not** click Runway before the drag. Start on the Finder file icon and drag directly onto the visible empty Runway `Image N` reference slot in the background. Clicking Runway first hides Finder and breaks the route.
- Re-read the current Finder `AXImage` coordinate for every file and the empty-slot coordinate whenever the strip changes. Identical Finder window bounds do not imply identical icon placement; never reuse the preceding file's or an old successful run's coordinates.
- Before mouse-down, verify that the entire Runway target slot is visible and not covered by another Finder/Codex/ChatGPT window. Close or move unrelated Finder windows—especially a large `upload_only` window that can cover Image3—and keep only one small staging window away from the target.
- If payload capture is uncertain, use a two-phase gesture: mouse-down and move to the slot, capture a held-state screenshot proving the file ghost is over the visible Runway slot, then mouse-up.
- Wait briefly for delayed attachment, then verify the new active-strip `Image N` thumbnail. Only after the thumbnail appears may Runway become frontmost for expanded semantic-role QC.
- For a persistent character deck, keep Image1/Image2 and replace Image3 only when the environment changes. Do not reopen or replace character references unnecessarily.
- Never treat upload toast, Recents/library presence, or a local path as attachment proof. The active-strip thumbnail plus expanded-pixel role check are the success condition.
- Use copy/paste only as first fallback and Web Inspector file-input only as second fallback when direct drag fails. Avoid asset-selector Search and repeated file-picker attempts.
- Do not click Generate until reference count/order/roles and all UI settings are verified.
- A failed drag does not authorize repeated attempts. Re-measure the current file AXImage and empty slot, remove target occlusion, verify the held file payload, and retry exactly once before any documented fallback.





### Runway/Seedance active-window lock — Claude misroute prevention — 2026-07-06

Before entering image/reference paths, uploading references, or pasting prompts for Runway/Seedance, verify the active Computer Use target is the visible `app.runwayml.com` tab/window. Do not paste or type reference paths into Claude, ChatGPT, Codex, Finder search, Terminal, or any non-Runway composer. If the frontmost window is wrong, stop immediately, switch back to Runway, re-run `get_app_state`, and only continue after the intended Reference/upload/prompt area is visible. Treat any path accidentally inserted into Claude/ChatGPT as `MISROUTED_REFERENCE_INPUT_TO_NON_RUNWAY`, not as progress.

Use Finder-visible staging folders or Runway's visible asset selector for references; path strings are for local manifests/operator cards only unless a verified Runway file/path field is focused.

### Seedance dialogue / voice naturalness hard gate — 2026-06-30

Use this whenever the user says the Seedance voice sounds AI-like, robotic, flat, 성의없음, or not like a professional actor.

- Do not rely on text prompt adjectives such as “natural” or “professional voice actor” alone. They often produce polished TTS/announcer tone.
- Preferred route: attach a real performed Korean guide as `@Audio1` for the exact block. State that `@Audio1` controls phoneme timing, cadence, breath, hesitation, room-mic distance, pauses, and emotional dynamics.
- If no visible `@Audio1` is attached, treat native Seedance speech as `AUDIO_FAIL_DEFAULT`; generate visuals + diegetic SFX only and replace dialogue externally in CapCut/VO.
- Keep dialogue short. One speaker owns each beat; other people react silently or with tiny breaths/laughs unless a quoted line is assigned.
- Prompt for real Korean family-room acting: uneven syllable lengths, swallowed endings, 0.2–0.6s thinking pauses, off-axis room mic, tiny laugh leaks, natural breath.
- Forbid announcer/campaign/public-institution tone, metallic AI, over-clean studio TTS, equal-syllable robot rhythm, sitcom laugh track, garbled Korean, relationship errors, and any BGM/music bed.
- Audio QC is separate from visual QC. A visual PASS clip can still be used muted when audio fails.





### V18 anti-AI voice escalation — 2026-06-30

Use this after the user says a generated/Edge/native voice still sounds obviously AI, flat, 성의없음, or not like real Korean family acting.

- Do not keep escalating adjectives (`more natural`, `professional`, `emotional`, `cinematic`). Stronger adjectives can still produce announcer/TTS cadence.
- Treat prompt-only native Seedance speech as **candidate-only** and `AUDIO_FAIL_DEFAULT` for final delivery unless a block-specific performed Korean `@Audio1` is attached and listening QC passes.
- The primary fix is an audio-performance reference or external VO: `@Audio1` must be described as exact Korean phoneme timing, cadence, breaths, hesitation, swallowed endings, room-mic distance, laugh leaks, and emotional dynamics — not as BGM.
- Each dialogue beat should have one clear speaker, one short line, visible mouth/face stability, locked or slow-push camera, and reaction laughter only after the key line lands.
- Put public-message clarity in captions/editing, not in generated campaign narration. Keep family dialogue private, specific, and relationship-correct (`누나` teasing younger brother 민재, not 오빠).
- Hard negative tail: no background music/score/melody/jingle, no announcer/campaign tone, no over-clean studio TTS, no metallic AI smoothing, no equal-syllable robot rhythm, no fake hype, no overlapped plot lines, no garbled Korean.
- Final audio requires human listening QC. A visual PASS clip may be used muted with external VO if the voice fails.

### V28 voice naturalness escalation — 2026-06-30

Use this when the user says a Seedance/Edge/native voice still sounds
obviously AI even after prior “natural/professional/emotional” prompt
retries.

- Do **not** keep solving the problem by adding stronger adjectives. Treat
  `natural`, `professional voice actor`, `warm`, and `emotional` as weak
  descriptors unless they are backed by a performed audio reference or
  concrete acting mechanics.
- New default: Seedance dialogue needs a block-specific performed Korean
  `@Audio1` guide. State that `@Audio1` controls phoneme timing, cadence,
  breaths, hesitation, silence length, off-axis room-mic distance, laugh
  timing, and emotional curve. Explicitly say `@Audio1 is not BGM`.
- If no `@Audio1` is attached, write the prompt as visual + diegetic SFX
  only and route final dialogue to external VO/CapCut. Prompt-only native
  Seedance speech is candidate-only and `AUDIO_FAIL_DEFAULT` until manual
  listening QC proves it human-like.
- Put an `AUDIO ROUTE` block before story beats, then `STORY READ`,
  `ACTING CONTRACT`, timed beats, diegetic-SFX-only policy, and hard
  audio fail conditions.
- Put only actual spoken Korean inside quotation marks. Keep acting notes,
  pauses, breath, mic distance, and subtext outside quotes so they are not
  spoken aloud.
- Use one key line per 2.5–4 seconds. Reaction laughter/coos/SFX happen
  only after the important line is understood.
- Encode human imperfection: uneven syllable lengths, swallowed Korean
  endings, 0.25–0.55s silence before/after emotional words, breath before
  risky lines, small laugh leaks, and volume changes across the phrase.
- For the Seongnam low-birth family short, keep relationship correctness:
  Minjae is the younger male sibling/uncle, the sister is `누나`, and the
  baby must read as the sister's child, not Minjae's own child.
- Hard fail audio if it is metallic, over-clean, equal-syllable, TTS-like,
  announcer/campaign/public-institution tone, fake-hyped, garbled Korean,
  overlapped so the plot line is hidden, or contains any BGM/score/music
  bed/piano/strings/pad/jingle.
- Visual PASS + Audio FAIL is still useful: keep the clip muted if visuals
  and diegetic SFX pass, then replace dialogue with natural external VO.


### V33 voice naturalness research correction — 2026-06-30

Use this after the user says the voice still sounds AI-like even after prior `natural/professional/emotional` retries and after studying current Seedance/TTS guidance.

- The fix is **not** stronger adjectives. The fix is a production route: performed Korean `@Audio1` or external human/performed VO, short spoken lines, concrete pause/breath mechanics, and listening QC.
- Seedance supports audio inputs; assign `@Audio1` an explicit role as the performed voice/cadence guide, not BGM. State that it controls phoneme timing, uneven syllable length, breath, silence, swallowed endings, off-axis room mic, laugh timing, and emotional curve.
- If no `@Audio1` is visibly attached, write prompts as visual + diegetic SFX/room tone only. Any generated speech is scratch/candidate and should be muted unless listening QC approves it.
- Rewrite dialogue so it sounds spoken at home, not written for a public campaign. Prefer lines like `아니, 난 결혼… 진짜 안 한다니까.`, `하율아— 삼촌 왔다!`, `이거… 손가락, 잡아도 돼?`, `야, 삼촌 표정 봐. 면접 보러 왔냐?`, `민재야, 너 지금… 우리보다 더 신났는데?`, `나도… 이런 집이면, 좀 괜찮겠다.`
- Use one speaker per beat and one key line per 2.5–4 seconds; reaction laughs/coos happen after the line lands. Put only spoken Korean inside quotation marks; keep acting notes outside quotes.
- Do not over-mark pauses. One or two ellipses/dashes per line is enough; excessive tags/punctuation can destabilize or sound fake.
- For synthetic candidate generation, make at least three takes per line/block and choose by human listening, not waveform metrics alone.
- Hard fail any audio with metallic smoothing, equal-syllable rhythm, over-clean studio TTS, announcer/campaign/institution tone, fake emotional rise on every sentence, garbled Korean, wrong sibling relation, or any BGM/score/music bed.
- Visual PASS + Audio FAIL remains usable only if muted/replaced in CapCut. Final complete still requires listening-QC-passed dialogue and CapCut export.

### V44 voice naturalness deep reprompt — 2026-06-30

Use this after the user says a finished/review video still sounds obviously AI-like even after prior V33 prompt research.

- Do not produce another “more natural / professional / emotional” prompt-only retry. Treat that as the failed pattern.
- The new default is **performance-capture first**: record or attach a block-specific Korean `@Audio1` guide, then make Seedance follow that guide; otherwise generate visuals + room tone/SFX only and replace speech externally.
- `@Audio1` must be described as performed Korean speech/cadence, not BGM. It controls phoneme timing, uneven syllable lengths, room-mic distance, silence length, breath, swallowed endings, laugh leaks, and emotional curve.
- If no visible `@Audio1` is attached, any generated Korean speech is scratch only and `AUDIO_FAIL_DEFAULT`. A visual PASS/audio FAIL clip may be used muted, but not as final.
- Require **three takes** for important lines: A normal room take, B smaller/quieter private take, C slightly messy human take. Select by human listening, not by prompt confidence or waveform metrics.
- Avoid putting forbidden Korean relationship words inside prompts; some models may speak or follow the token even when negated. Use relationship-positive wording such as “누나 teasing her younger brother 민재” and “wrong sibling title forbidden.”
- Keep the performance private and home-recorded: no campaign narration, no announcer diction, no over-clean studio TTS, no equal-syllable rhythm, no metallic smoothing, no fake hype, and no music bed/score/piano/strings/pad/jingle.
- For Seongnam family-short work, use the V44 package if present:
  `/Users/gnudas/Documents/Codex/video-team-runtime/20260629_202812_seongnam-low-birth-2026-shortform/lanes/seedance/v44_voice_naturalness_deep_reprompt_20260630`.

### V15 no prompt-only final dialogue rule — 2026-06-30

Use this when the user says the voice still sounds AI-like after earlier naturalness retries, or when a Seedance/Edge/native generated Korean voice has already been rejected by listening QC.

- Stop treating stronger adjectives (`natural`, `emotional`, `professional voice actor`) as the fix. They can still produce polished TTS, broadcaster cadence, or lazy AI acting.
- Prompt-only Seedance native speech and generic neural TTS are `AUDIO_FAIL_DEFAULT` for final delivery. Use them only as scratch/review timing unless the user explicitly approves after listening.
- Preferred route: record/attach a block-specific performed Korean `@Audio1` guide. `@Audio1` must control cadence, phoneme timing, breath, false starts, room/phone mic distance, pauses, and emotional dynamics.
- If no visible `@Audio1` is attached, write Seedance prompts as visual + diegetic SFX/room tone only; replace spoken dialogue externally in CapCut/human VO/expressive TTS candidate.
- For external TTS candidates, split per utterance, provide acting instructions, speed/pace, and trailing silence per line; still require human listening QC before final use.
- Dialogue should be shorter, more private, and less explanatory than captions: one speaker owns the beat, family reactions happen after the line lands, and public-campaign copy stays out of spoken voice.
- Any BGM/score/music bed, equal-syllable rhythm, metallic smoothing, over-clean studio mic, announcer/campaign tone, wrong sibling relationship, or story-unclear line forces audio mute/replacement.

## Camera Language Reference

Use these camera terms for precise control:

### Basic Movements
| Term | Description |
|---|---|
| Push in / Slow push | Camera moves toward subject |
| Pull back / Pull away | Camera moves away from subject |
| Pan left/right | Camera rotates horizontally |
| Tilt up/down | Camera rotates vertically |
| Track / Follow shot | Camera follows subject movement |
| Orbit / Revolve | Camera circles around subject |
| One-take / Oner | Continuous shot with no cuts |

### Advanced Techniques
| Term | Description |
|---|---|
| Hitchcock zoom (dolly zoom) | Push in + zoom out (or vice versa), creates vertigo effect |
| Fisheye lens | Ultra-wide distorted lens |
| Low angle / High angle | Camera below/above subject |
| Bird's eye / Overhead | Top-down view |
| First-person POV | Subjective camera from character's eyes |
| Whip pan | Very fast horizontal pan creating motion blur |
| Crane shot | Vertical movement like a crane arm |

### Shot Sizes
| Term | Description |
|---|---|
| Extreme close-up | Eyes, mouth, or small detail only |
| Close-up | Face fills frame |
| Medium close-up | Head and shoulders |
| Medium shot | Waist up |
| Full shot | Entire body |
| Wide / Establishing shot | Full environment |

---

## Capability-Specific Prompt Patterns

### 1. Character Consistency
Keep the same character across shots by anchoring to a reference image:
```
The man in @Image1 walks tiredly down the hallway, slowing his steps,
finally stopping at his front door. Close-up on his face — he takes a
deep breath, adjusts his emotions, replaces the weariness with a relaxed
expression. Close-up of him finding his keys, inserting into the lock.
After entering, his little daughter and a pet dog run to greet him with
hugs. The interior is warm and cozy. Natural dialogue throughout.
```

### 2. Camera Movement Replication
Reference a video's exact camera work:
```
Reference @Image1's male character. He is in @Image2's elevator.
Completely reference @Video1's camera movements and the protagonist's
facial expressions. Hitchcock zoom during the fear moment, then several
orbit shots showing the elevator interior. Elevator doors open, follow
shot walking out. Exterior scene references @Image3. The man looks
around, referencing @Video1's mechanical arm multi-angle tracking of
the character's gaze.
```

### 3. Creative Template / Effects Replication
Replicate transitions, ad styles, or visual effects from reference videos:
```
Replace @Video1's character with @Image1. @Image1 as the first frame.
Character puts on VR sci-fi glasses. Reference @Video1's camera work —
close orbit shot transitions from third-person to character's subjective
POV. Travel through the VR glasses into @Image2's deep blue universe.
Several spaceships shuttle toward the distance. Camera follows ships
into @Image3's pixel world. Low-altitude flyover of pixel mountains
where trees grow procedurally. Then upward angle, rapid shuttle to
@Image4's pale green textured planet, camera skims the planet surface.
```

### 4. Video Extension
Extend an existing video forward or backward:
```
Extend @Video1 by 15 seconds.
1–5s: Light and shadow slowly slide across wooden table and cup through
venetian blinds. Tree branches sway gently as if breathing.
6–10s: A coffee bean gently drifts down from the top of frame. Camera
pushes in toward the bean until the screen goes black.
11–15s: English text gradually appears — first line "Lucky Coffee",
second line "Breakfast", third line "AM 7:00-10:00".
```

**Important**: When extending, set the generation duration to match the extension length (e.g., extend 5s → select 5s generation).

For **reverse extension** (prepending):
```
Extend backward 10s. In warm afternoon light, the camera starts from
the corner with awning fluttering in the breeze, slowly tilting down
to daisies peeking out at the wall base...
```

### 5. Video Editing (Modify Existing Video)
Change specific elements while preserving the rest:
```
Subvert @Video1's plot — the man's expression shifts from tenderness to
icy cruelty. In an unguarded moment, he shoves the female lead off the
bridge into the water. The action is decisive, premeditated, without
hesitation. The female lead falls with no scream, only disbelief in her
eyes. She surfaces and screams: "You've been lying to me from the start!"
The man stands on the bridge with a sinister smile, murmuring: "This is
what your family owes mine."
```

### 6. Music Beat-Matching
Sync visuals to audio rhythm:
```
@Image1 @Image2 @Image3 @Image4 @Image5 @Image6 @Image7 — match the
keyframe positions and overall rhythm of @Video1 for beat-synced cuts.
Characters should have more dynamic movement. Overall visual style more
dreamlike with strong visual tension. Adjust shot sizes and add lighting
changes based on music and visual needs.
```

### 7. Dialogue and Voice Acting
Include character dialogue and voice direction:
```
In the "Cat & Dog Roast Show" — an emotionally expressive comedy segment:
Cat host (licking paw, rolling eyes): "Who understands my suffering? This
one next to me does nothing but wag his tail, destroy sofas, and con
humans out of treats with those 'pet me I'm adorable' eyes..."
Dog host (head tilted, tail wagging): "You're one to talk? You sleep 18
hours a day, wake up just to rub against humans' legs for canned food..."
```

### 8. One-Take / Long Take
Continuous single-shot sequences:
```
@Image1 @Image2 @Image3 @Image4 @Image5 — one-take tracking shot,
following a runner from the street up stairs, through a corridor, onto
a rooftop, finally overlooking the city. No cuts throughout.
```

### 9. E-commerce / Product Showcase
Product-focused advertising:
```
Deconstruct the reference image. Static camera. Hamburger suspended and
rotating mid-air. Ingredients gently and precisely separate while
maintaining shape and proportion. Smooth motion, no extra effects.
Hamburger splits apart — golden sesame bun top, fresh green lettuce,
dewy red tomato slices, two thick juicy beef patties with melting golden
cheddar cheese, and soft bun base — all slowly descend and perfectly
reassemble into a complete deluxe double cheeseburger. Throughout,
cheese continues to melt and drip slowly, lettuce and tomato dewdrops
glisten, maintaining ultimate appetizing food aesthetics.
```

### 10. Science/Educational Content
Medical or educational visualizations:
```
15-second health educational clip.
0–5s: Transparent blue human upper body. Camera slowly pushes into a
clear artery. Blood flows smoothly, clean blue color.
5–10s: Symbolic sugar and fat particles from milk tea enter the
bloodstream. Camera follows blood flow. Blood gradually thickens,
yellowish lipid deposits form on vessel walls.
10–15s: Vessel lumen visibly narrows, flow speed decreases. Before/after
comparison creates visual contrast. Overall colors darken.
```

---

## Style and Quality Modifiers

Append these to enhance output quality:

### Visual Style
- `Cinematic quality, film grain, shallow depth of field`
- `2.35:1 widescreen, 24fps`
- `Ink wash painting style` / `Anime style` / `Photorealistic`
- `High saturation neon colors, cool-warm contrast`
- `4K medical CGI, semi-transparent visualization`

### Mood/Atmosphere
- `Tense and suspenseful` / `Warm and healing` / `Epic and grand`
- `Comedy with exaggerated expressions`
- `Documentary tone, restrained narration`

### Audio Direction
- `Background music: grand and majestic`
- `Sound effects: footsteps, crowd noise, car sounds`
- `Voice tone reference @Video1`
- `Beat-synced transitions matching music rhythm`

---

## Workflow: Step-by-Step Prompt Creation

When a user asks you to write a Seedance 2.0 prompt, follow this process:

1. **Clarify the goal**: What type of video? (Ad, drama, MV, educational, vlog, etc.)
2. **Identify available assets**: What images, videos, audio does the user have?
3. **Assign roles**: Map each asset to its function (first frame, character ref, camera ref, etc.)
4. **Structure the prompt**:
   - Open with subject and scene setup
   - Add time-segmented action descriptions for videos > 8s
   - Specify camera movements
   - Add audio/sound design
   - Include style modifiers
5. **Check constraints**: Verify total files ≤ 12, no real human faces, durations within limits
6. **Optimize**: Remove ambiguity, ensure each @reference has a clear role

### Runway/Seedance Operator Gate

When operating Runway Seedance directly, prompt quality is not enough. Before
clicking Generate, verify the UI, not just local files:

0. For the user's video-team pipeline, use only QC-passed sourceframes/start
   frames generated by Codex `imagegen` / built-in `image_gen` unless the user
   explicitly chose another still-image route. Do not use Grok to create still
   images, and do not send pre-character-lock/lookdev frames to Runway/Seedance.
   If a character sheet is required, record the actual imagegen sheet path(s)
   used for the sourceframe; do not proceed from text-only memory.
0a. Operate Runway/Seedance through the visible logged-in web UI with
   Computer Use/Safari/Browser automation. Do not use a Runway connector,
   MCP app, API, or connector auth result for production submission, polling,
   upload, download, or blocker decisions unless the user explicitly overrides
   this for that exact turn. Visible UI state is the source of truth.
1. Close stray popovers/Actions menus before changing references.
2. Clear/replace the previous block's references; stale B01/B02 thumbnails
   are contamination for B03/B04.
3. Upload from the dedicated `Bxx_ORDERED_UPLOAD_ONLY` folder, not from older
   artifact paths in notes.
4. Confirm visible thumbnails in exact order and count.
5. Confirm model/tool is Seedance, mode is Multi-reference, output is Video,
   aspect is 16:9, resolution is 720p/non-credit setting, duration matches
   the block (normally 10s for 4 refs; 12s for 5 refs when available).
6. Insert the prepared prompt once; verify it is not duplicated or appended
   to a stale prompt.
7. If Runway says "Please wait" or offers Credits Mode, do not switch to
   Credits Mode without explicit user approval. Wait/poll or continue only
   non-generation prep work.
8. Use Grok fallback only when the user explicitly approves fallback or when
   the project lane prompt says to fall back after a hard Runway block.

---

## Common Mistakes to Avoid

1. **Vague references**: Don't just say "reference @Video1" — specify WHAT to reference (camera? action? effects? rhythm?)
2. **Conflicting instructions**: Don't ask for "static camera" and "orbit shot" in the same segment
3. **Overloading**: Don't try to pack too many scenes into 4–5 seconds — keep it physically plausible
4. **Missing @ assignments**: If you upload 5 images, make sure each one is referenced with a clear purpose
5. **Ignoring audio**: Sound design dramatically improves output — always include audio direction
6. **Forgetting duration**: Match your prompt complexity to the selected generation length
7. **Real faces**: Don't describe uploading real human photos — the system will block them
8. **Template-only prompts**: A prompt can pass syntax checks but still be weak
   if every beat uses the same generic camera sentence. Give each beat a
   distinct shot header, action, and sensory physics.
9. **Using prompt fixes for UI problems**: If the wrong thumbnails, aspect
   ratio, duration, model, or stale prompt are visible, stop and fix the UI
   first. Do not generate and hope the text compensates.
10. **Wrong fallback route**: Do not silently switch Seedance block generation
   to a different model. Fallback changes the production route and should be
   explicit or hard-block driven.

---

## Example Prompt Templates

### Template: Product Ad (15s)
```
Reference @Video1's editing style and camera transitions. Replace @Video1's
product with @Image1 as the hero product. Create a 15-second product
showcase video.
0–3s: Product enters frame with dynamic rotation, close-up on surface
texture and logo details.
4–8s: Multiple angle transitions — front, side, back — with product
highlight scanning light effects.
9–12s: Product in lifestyle context showing usage scenario.
13–15s: Hero shot with brand tagline appearing, background music builds
to resolution.
Sound: Reference @Video1's background music. Add product interaction
sound effects.
```

### Template: Short Drama (15s)
```
Scene (0–5s): Close-up on the character's reddened eyes, finger pointing
accusingly, tears streaming down. Emotion on the edge of collapse.
Dialogue 1 (Character A, choking with rage): "What exactly are you trying
to take from me?"
Scene (6–10s): The other character trembles, holding up evidence,
red-eyed, stepping forward. Camera sweeps past background details.
Dialogue 2 (Character B, urgent and choked): "I'm not deceiving you!
This is what he entrusted to me!"
Scene (11–15s): Evidence is revealed, Character A freezes — expression
shifts from anger to shock, hands slowly rise.
Sound: Urgent piano + static interference, sobbing, button click sound,
ending with a muffled voice blending in.
Duration: Precise 15 seconds, every frame tight, no filler.
```

### Template: Dance Video (13s)
```
Have the character in @Image1 replicate the dance moves and beat-synced
music from @Video1. Generate a 13-second video. Movements should be
smooth with no stuttering or freezing.
```

### Template: Scenery Montage with Music (15s)
```
@Image1 @Image2 @Image3 @Image4 @Image5 @Image6 — landscape scene
images. Reference @Video1's visual rhythm, inter-scene transitions,
visual style, and music tempo for beat-synced editing.
```

---

## Interaction Instructions

When helping users write prompts:

1. **Ask what they want to create** — type of video, mood, duration
2. **Ask what materials they have** — list their images, videos, audio files
3. **Draft the prompt** — using the patterns and structure above
4. **Explain your choices** — briefly note why you structured the prompt this way
5. **Offer variations** — suggest a simpler or more ambitious alternative if appropriate
6. **Remind about constraints** — especially the face restriction and file limits


## Stability-first anti-wobble mode — 2026-06-21

Use this mode whenever approved stills become noisy during Seedance/Runway videoization (`자글자글`, `우글우글`, face flicker, line boiling, crawling texture). Reference wiki: `/Users/gnudas/wiki/concepts/seedance-prompting-knowledge.md`.

Required prompt tail:
```text
Stability-first videoization. Preserve the exact source composition, face shape, eye spacing, jaw, hair silhouette, clothing folds, hands, phone geometry, Korean text/UI, black ad-screen placeholders, room lines, window frames, vehicle geometry, and background perspective. Camera locked or almost locked. Minimal natural motion only: breathing, tiny shoulder drop, slight hand tremor, hair-tip or light movement. No texture crawling, no line boiling, no face flicker, no hand/finger warping, no rubbery skin, no morphing, no extra objects, no new text, no UI jitter, no Korean text shimmer, no background music.
```

For multi-reference blocks, assign each image as an independent stable shot and specify clean cuts. Do not use morph/transform language unless the user explicitly accepts the risk.


## Source-frame composition preservation — distance + angle — 2026-06-23

For Seedance/I2V prompts, preserve the approved source image's **shot distance** and **camera angle** unless the requested motion explicitly changes them. Canonical wiki: `/Users/gnudas/wiki/concepts/ai-image-composition-distance-angle.md`.

- Treat macro/close-up/medium/wide and top-down/low/Dutch/isometric/POV/back-view as locked semantic roles, not cosmetic wording.
- If the start frame is a macro hand/object clue, do not zoom out into a generic body shot.
- If the start frame is an over-shoulder or back-view POV, do not rotate into an ambiguous front/side medium shot.
- If the start frame is top-down/isometric map logic, do not invent new geography or cinematic perspective unless the prompt explicitly asks for a transition.

## Phone screen geometry lock — 2026-06-29

When writing Seedance/I2V prompts for phone-viewing, message, selfie, or screen-glow shots, enforce `/Users/gnudas/wiki/concepts/phone-screen-geometry-qc.md`.

Prompt tail:
```text
Phone geometry lock: smartphone has one front glass/display side and one back/camera-lens side. If screen content is visible to the audience, stage the phone as a physically plausible front-glass POV/over-shoulder/oblique insert. Never put UI, photos, message bubbles, or glow on the phone back. If the phone back faces camera, show only case/back panel/camera lenses/reflected light. Preserve phone sidedness and hand grip. No double-sided screen, no UI printed on the phone back, no screen/back swap during motion, no floating UI attached to the wrong side.
```

Seedance/Grok QC must fail any output with a display or UI on the phone back, even if the character face and message content look good.

### V58 living-dialogue voice patch — 2026-07-01

Use this after the user hears a produced clip and still says the Korean voice sounds AI-like, synthetic, 성의없음, over-polished, or not like real family acting.

- Treat the failure as an acting/performance problem, not a lack of stronger adjectives. Do not keep adding `more natural`, `professional voice actor`, `emotional`, or `cinematic`; those often push the model toward announcer/TTS tone.
- Prompt-only/native Seedance speech remains `AUDIO_FAIL_DEFAULT` for final delivery. Final dialogue requires a real/performed Korean WAV, or the exact performed WAV attached as `@Audio1` and then approved by human listening QC.
- Put this route before any dialogue prompt:

```text
AUDIO ROUTE — FINAL VO CANDIDATE ONLY WITH @Audio1:
Use @Audio1 only as the performed Korean speech reference for this exact line/block. @Audio1 controls Korean phoneme timing, uneven syllable length, breaths, hesitation, swallowed endings, off-axis room-mic distance, small laugh leaks, and emotional dynamics. @Audio1 is not background music.
If @Audio1 is not visibly attached, do not generate spoken dialogue. Generate visuals + diegetic SFX only.
No background music, no score, no melody bed, no jingle.
```

- Convert “naturalness” into acting mechanics: 0.2–0.6s thinking pauses, breath before/after the line, uneven syllables, slightly swallowed endings, room-mic distance, laugh leak after the key phrase, one speaker per beat, and relationship/subtext locks.
- For Korean family shorts, the voice should sound like private living-room speech, not public-campaign narration, not a studio booth demo, and not a cartoon/children's-program host.
- Listening QC overrides waveform QC. A technically clean WAV still fails if it has equal-syllable robot rhythm, metallic smoothing, perfect diction TTS, announcer/campaign tone, BGM/music bed, garbled Korean, or wrong relationship wording.

### V63 actor-director anti-AI voice patch — 2026-07-01

Use this after the user hears a review/final video and says the voice is still
AI-like despite earlier `natural`, `professional`, `emotional`, `@Audio1`, or
human-VO preparation rules.

- Diagnose the failure as **cadence/performance collapse**, not merely missing
  emotion: equal syllable lengths, too-clean endings, no hesitation, no room
  distance, and polished announcer/advertising diction.
- Do not write another prompt that only says `more natural`, `professional voice
  actor`, or `emotional`. Those phrases can increase commercial TTS polish.
- Convert the prompt/recording plan into an **actor-director card**: story beat,
  actor objective, subtext, one meaningful pause, mic/room distance, exact
  swallowed ending, and hard reject conditions.
- Require at least four candidate takes per final line when possible: A normal
  room take, B smaller/private take, C slightly messy human take, D
  anti-polished take that intentionally removes campaign/advertising diction.
- If using Seedance with speech, attach a block-specific performed Korean
  `@Audio1`; describe it as phoneme timing, cadence, breath, pauses, swallowed
  endings, laugh leaks, off-axis room-mic distance, and emotional curve. It is
  never BGM.
- If no visible `@Audio1` is attached, write a no-dialogue prompt: visuals + room
  tone/diegetic SFX only. Do not ask Seedance to synthesize Korean speech.
- Put only the actual spoken Korean inside quotation marks. Keep breath,
  hesitation, laughter, mic distance, and subtext outside quotes.
- Human listening remains the final gate. V54/V61/V56/V37-style tooling can help
  route and QC takes, but selected WAVs are not final until ear-approved.
- Hard fail: background music/score/music bed/jingle, announcer/campaign/public
  institution tone, over-clean studio TTS, metallic smoothing, equal-syllable
  robot rhythm, every sentence ending perfectly, sitcom overacting, garbled
  Korean, or wrong family relationship.

For the Seongnam low-birth family short, V63 package:
`/Users/gnudas/Documents/Codex/video-team-runtime/20260629_202812_seongnam-low-birth-2026-shortform/lanes/seedance/v63_voice_naturalness_second_study_actor_director_20260701`.


### V69 home-actor anti-AI voice correction — 2026-07-01

Use this after the user says the generated/review video voice still sounds AI-like even after V63 actor-director patches.

- Do not add more generic adjectives such as `natural`, `professional`, `emotional`, or `voice actor` as the main fix. That failure pattern can produce polished ad narrator/TTS cadence.
- Switch to the **HOME-ACTOR CONTRACT**: private Korean family-room speech, not campaign narration. Acting notes must be physical actions and subtext, not emotional adjectives.
- Final voice remains human/performed VO only unless a block-specific performed Korean `@Audio1` guide is attached and manual listening QC passes. `@Audio1` controls timing/cadence/breath/hesitation/laugh leaks/room distance and is never BGM.
- If no visible `@Audio1` is attached, Seedance prompts must generate **no spoken dialogue**: visual + room tone/diegetic SFX only, then replace speech externally in CapCut using V54/V37-approved WAVs.
- Use A/B/C/D takes where D is an anti-AI test take: deliberately less pretty, less announcer-like, with uneven syllable lengths and small swallowed endings while plot remains clear.
- Put only actual Korean lines inside quotation marks. Keep pauses, breath, subtext, and mic-distance instructions outside quotes so they are not spoken aloud.
- Reject audio for metallic smoothing, equal-syllable rhythm, over-clean studio TTS, announcer/commercial/campaign tone, fake hype, garbled Korean, overlapped plot lines, wrong sibling relation, or any BGM/score/music bed.
- For Seongnam low-birth family short, keep relationship-positive wording: `누나 teasing her younger brother 민재`; baby is the sister's child; 민재 is the uncle.

### V79 anti-AI voice reprompt after review rejection — 2026-07-01

Use this after the user reviews a produced video and says the voice still sounds AI-like, robotic, lazy, flat, 성의없음, or not like a real Korean family conversation.

- Treat the failure as **performance direction collapse**, not a missing adjective. Do not respond by only adding `more natural`, `professional`, `emotional`, `cinematic`, or `voice actor`.
- Final spoken dialogue still requires real/performed Korean WAVs or a block-specific performed Korean `@Audio1` candidate that passes human listening QC. Prompt-only/native Seedance speech remains `AUDIO_FAIL_DEFAULT`.
- `@Audio1` must be assigned as a speech-performance guide only: phoneme timing, uneven syllable length, real breath, 0.2–0.6s thinking silence, swallowed Korean endings, small laugh leaks, room/phone mic distance, and emotional curve. `@Audio1` is never BGM.
- If no visible `@Audio1` is attached, Seedance prompts must request **no spoken dialogue** and only visuals + room tone/diegetic SFX. Any accidental speech is muted/replaced in CapCut.
- Write acting instructions as physical/subtext beats: what the actor is doing, who they are avoiding/teasing/protecting, and what changes after the line. One speaker owns the beat; reaction laughs/coos happen after the line lands.
- Use sparse punctuation: at most one ellipsis or dash per spoken line. Too many pauses/tags can create artifacts or unstable rhythm.
- For Seongnam family short, lock relationship and tone: Minjae is the younger male sibling/uncle; 누나 teases her younger brother; baby is the sister's child. Spoken lines are private family-room speech, not public-campaign narration.
- Hard fail: BGM/score/music bed, metallic AI smoothing, equal-syllable robot rhythm, over-clean studio TTS, announcer/campaign tone, fake hype, garbled Korean, wrong sibling relation, or overlapped dialogue that hides the story.
- Prefer A/B/C/D take design: A normal room, B smaller/private, C messy spontaneous, D anti-AI under-acted. Select by ear, not waveform metrics.

Seongnam V79 package: `/Users/gnudas/Documents/Codex/video-team-runtime/20260629_202812_seongnam-low-birth-2026-shortform/lanes/seedance/v79_ai_voice_naturalness_study_reprompt_patch_20260701`.

### V84 Seedance native-dialogue prompt-only correction — 2026-07-01

Use this when the user clarifies that they did **not** ask for human VO files and wants Seedance prompting itself to generate a more natural, more human-like Korean voice.

- Do not block the work on real/performed WAVs for this iteration. The active route is Seedance native Korean dialogue generation.
- Keep the no-BGM rule: no background music, score, piano, strings, pads, jingles, or music bed. Dialogue and diegetic SFX are allowed.
- Prompt audio as performance mechanics, not adjectives: one speaker owns each beat, exact Korean lines in quotation marks, acting notes outside quotes, uneven syllables, room distance, tiny thinking pauses, swallowed endings, laugh/breath after meaning lands.
- Generate at least two variants per block when the previous result sounded AI-like: S1 story-readable living-room take; S2 anti-AI under-acted take with less polish and more spontaneous room speech.
- Do not overuse pause punctuation; one ellipsis/dash per line is enough. Too many symbols can create unstable or fake rhythm.
- Keep relationship/story locks in every prompt: Minjae is younger male sibling/uncle, sister is 누나 teasing him, baby is sister's child.
- QC by listening: reject metallic AI smoothing, equal-syllable rhythm, announcer/campaign tone, fake hype, garbled Korean, wrong relationship, or BGM. If audio fails but visuals pass, regenerate the audio/dialogue block with the S2 prompt variant.

Seongnam V84 package: `/Users/gnudas/Documents/Codex/video-team-runtime/20260629_202812_seongnam-low-birth-2026-shortform/lanes/seedance/v84_seedance_native_dialogue_prompt_regen_20260701`.

### Runway/Seedance two-active-queue optimization — 2026-07-04

Use this for the user's Runway/Seedance video-team workflow after a job has been safely submitted.

- Keep up to **two active Runway/Seedance generations** in flight when the UI/account allows it. The target is `active_generating_count <= 2`, not unlimited queue flooding.
- After one block passes the full UI preflight and shows `Generating video...`, `In queue`, or equivalent processing state, do **not** idle on that job if another independent, already-QC-approved block is ready. Prepare and submit the next block until two active jobs are visible.
- Before submitting the second job, run the same full operator gate: clear stale references/prompt, upload the dedicated ordered refs, verify visible thumbnail count/order, verify model/mode/output/aspect/resolution/duration/audio, verify prompt exactness, and verify no `Please wait`, `You're on a roll`, or `Credits Mode` blocker.
- If two active cards/jobs are already visible, stop clicking Generate. Poll/download/QC completed jobs, prepare future packages locally, or continue image/music/CapCut work while waiting.
- If Runway blocks the second job with `Please wait`, `You're on a roll`, queue-limit, or Credits Mode language, do not switch to Credits Mode and do not keep clicking. Record the blocker and continue non-generation prep until a slot frees.
- Count only jobs with visible UI evidence as active. A local prompt/package or hidden file-input dispatch is not an active queue unless the Runway UI shows the submitted/generating/queued job.

## Seedance continuity-critical multi-reference rule — 2026-07-07

For recurring-character public-contest/MV clips, do not rely on a single uploaded production frame in Seedance when identity, gender/role readability, car/prop geometry, or adjacent-cut continuity matters. Use multi-reference: production styleframe + approved character/model sheet(s) + adjacent continuity frame and, when needed, specific prop/vehicle staging reference. A technically clean single-image I2V output can still fail if the car/prop staging is broken, gender/role reading is unclear, or the character looks like a different person. Provider reports must truthfully name Seedance vs Grok; if the final files are Grok fallback, do not describe them as Seedance output.

## Seedance ↔ Grok provider-lane separation rule — 2026-07-07

For the user's video-team workflow, Seedance-primary work and Grok fallback work must be separated from the planning stage, not reconstructed after the edit.

Required per-cut provider matrix before any clip enters CapCut or final timeline:
- `seedance_primary_status`: not_started / refs_prepared / refs_uploaded_visible / submitted / queued / downloaded / qc_pass / qc_fail / blocked.
- `seedance_downloaded_file`: exact path, or `NONE_UI_ONLY` if a Runway UI candidate exists but has not been downloaded.
- `grok_fallback_status`: not_used / prepared / submitted / downloaded / qc_pass / qc_fail.
- `grok_downloaded_file`: exact path when used.
- `provider_switch_reason`: hard Runway wait/Credits/account blocker, explicit user approval, or planned provider split.
- `final_selected_provider`: Seedance / Grok / other.
- `final_selected_file`: exact file path used in CapCut/final export.

Rules:
- A Seedance prompt card, uploaded sourceframe, or visible reference thumbnail is not a generated Seedance candidate. It must not be reported as Seedance output until a visible queued/generated card and downloaded result file are verified, or explicitly marked `UI_ONLY_NOT_PACKAGED`.
- If Grok files enter the timeline, call them Grok fallback files even when the project began as Seedance-primary.
- If Runway/Seedance generated UI-side candidates but they were not downloaded/packaged, recover them from Runway history and register them as separate Seedance candidates before selection.
- Do not collapse provider status into a single “I2V done” state. Provider evidence and selected final source are separate QC gates.
- For continuity-critical Seedance cuts, use the character/model sheet and multi-reference package; do not rely on one production frame only.
### 8) Deep temporal grammar upgrade — added 2026-07-21

The second corpus pass (126 video prompts) shows that strong community prompts use a **time-ordered action chain**, not a flat noun list:

```text
START STATE → ACTION 1 → physical consequence → CAMERA BEAT → ACTION 2 → END FRAME
```

- Use explicit temporal verbs such as `starts with`, `then`, `as`, `while`, `after`, and `finally` when a clip contains more than one action.
- Separate simultaneous actions into three clauses: subject action, camera action, and environment action. Do not let the subject, camera, and world all share one vague “moves.”
- Every action should produce a visible consequence before the next beat; if it cannot fit the selected duration, remove beats rather than asking for faster everything.
- Finish with a destination: final crop, final gaze, final reveal, final object position, or final camera distance.
- Treat `slowly/gently/quickly/smoothly` as modifiers of a named action, never as the action itself.

### 9) Subject / camera / world lanes

Compile every prompt into three independent lanes before merging:
1. **Subject lane** — body state, exact action, gaze/gesture, speed, identity/costume lock.
2. **Camera lane** — mount/position, shot size, path, speed, lens/framing, final composition.
3. **World lane** — background relative motion, light change, wind/hair/fabric, smoke/dust/rain, reflections, diegetic sound.

This prevents subject/camera speed confusion, floating vehicle cameras, and ambient effects becoming the main action.

### 10) Tactile proof and positive geometry

For product, fashion, lifestyle, and object shots, specify the contact chain: `reach → grip/turn/open → material responds → use/look → proof detail`. Preserve hand-object contact, label orientation, object sidedness, exact crop, and final readable angle. Write positive locks first (`camera locked to car frame`, `screen on front glass`, `one hand remains on handle`, `subject stays frozen while background parallax shifts`); add only a short role-specific negative tail afterward.

### 11) Duration-to-beat compiler

- **5–6s:** one setup + one payoff; at most two major subject verbs.
- **7–10s:** setup → one interaction → one camera/reveal payoff; three major verbs maximum.
- **11–15s:** setup → interaction → consequence/reveal or a paced mini-sequence, still with one dominant camera family.

If a prompt exceeds the beat budget, split it into clips rather than compressing every action into one generation.
