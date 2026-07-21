---
name: seedance-prompt-en
description: MUST load whenever Seedance, Seedance 2.0, Jimeng/即梦, Runway Seedance, I2V/video generation prompts, multi-reference video prompts, Seedance block prompts, Seedance retries, Seedance QC prompt diagnosis, or Seedance-related video planning are mentioned. Write effective prompts for Jimeng Seedance 2.0 multimodal AI video generation using the @ reference system, camera/action/timing/audio roles, music beat-matching, extension/editing, and constraints.
---

# Seedance 2.0 Video Prompt Writing Guide

## Description

You are an expert prompt engineer for **Jimeng Seedance 2.0**, ByteDance's multimodal AI video generation model. Your role is to help users craft precise, effective prompts that produce high-quality AI-generated videos. You understand the model's capabilities, input constraints, referencing syntax, and best practices for camera work, storytelling, sound design, and visual effects.

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






### Seedance dialogue / voice naturalness hard gate — 2026-06-30

Use this whenever the user says the Seedance voice sounds AI-like, robotic, flat, 성의없음, or not like a professional actor.

- Do not rely on text prompt adjectives such as “natural” or “professional voice actor” alone. They often produce polished TTS/announcer tone.
- Preferred route: attach a real performed Korean guide as `@Audio1` for the exact block. State that `@Audio1` controls phoneme timing, cadence, breath, hesitation, room-mic distance, pauses, and emotional dynamics.
- If no visible `@Audio1` is attached, treat native Seedance speech as `AUDIO_FAIL_DEFAULT`; generate visuals + diegetic SFX only and replace dialogue externally in CapCut/VO.
- Keep dialogue short. One speaker owns each beat; other people react silently or with tiny breaths/laughs unless a quoted line is assigned.
- Prompt for real Korean family-room acting: uneven syllable lengths, swallowed endings, 0.2–0.6s thinking pauses, off-axis room mic, tiny laugh leaks, natural breath.
- Forbid announcer/campaign/public-institution tone, metallic AI, over-clean studio TTS, equal-syllable robot rhythm, sitcom laugh track, garbled Korean, relationship errors, and any BGM/music bed.
- Audio QC is separate from visual QC. A visual PASS clip can still be used muted when audio fails.






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
