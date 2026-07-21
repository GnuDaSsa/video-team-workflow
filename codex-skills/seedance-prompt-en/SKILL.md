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

### Runway Web UI Reference Upload Lesson — 2026-06-12

When operating Runway/Seedance through Safari or Computer Use for the user's video-team pipeline, do **not** repeat the failed pattern of bulk file-picker upload or Finder drag/drop for order-critical multi-reference assets. On this Mac/session, those paths can silently register only one asset or fail to append new references.

Required default:
- Use Runway's visible asset selector / Reference button and add references **one by one** in the required order.
- **Never use the Search field inside the Reference / asset-selector modal** for this workflow. It is not a reliable attachment path, has no useful effect for local upload ordering, and can leave confusing filters/state. Leave Search untouched; if it was used, clear/reopen the modal before continuing.
- After each add, verify the visible `IMG_1`, `IMG_2`, ... thumbnail count/order before adding the next image.
- If only `IMG_1` appears after a multi-file or drag/drop attempt, stop and recover with the one-by-one asset selector flow; do not keep trying drag/drop/bulk upload.
- Do not click Generate until visible thumbnails match the required reference count and order.
- If an uploaded file appears in Recents (for example `01_seongnam...`) but not in the reference strip, select it from Recents as the next reference; do not assume upload alone attached it.


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
