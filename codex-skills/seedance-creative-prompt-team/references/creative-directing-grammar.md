# Standing defaults for this project

- Default card: **multi-reference, 15 seconds**
- Creative room open after identity lock; refs are anchors, not cages
- **No BGM / score / music bed**; diegetic SFX + room tone only
- Naturalism over spectacle; medium-aware texture fidelity
  - live-action/photoreal: stable materials, no plastic/waxy/crawling texture
  - 2D/stylized: medium-true material (paper/ink/gouache/cel), not fake photoreal pores

# Creative directing grammar

Synthesized from the live Creative Seedance Mode and archived Higgsfield community pattern mining. Extract directing grammar only; never copy community prompts or real-person/IP cameos.

## Shot contract order

```text
[Shot size] + [camera position/mount] + [lens or framing] + [subject identity/action] +
[environment/light/depth] + [one dominant camera path] + [physical motion layers] +
[exit composition] + [role-specific safety tail]
```

If a draft says only `cinematic, beautiful, dynamic`, rewrite into camera physics.

## Camera family routing

| Clip role | Camera family | Obligation | Avoid |
|---|---|---|---|
| Identity/emotion close-up | static / slow push / macro-in | micro motion, crop lock, focus behavior | fast zoom, new face/body |
| Speed / vehicle / travel | mounted-object | camera fixed to object, parallax, vibration | floating independent camera |
| Reveal / transition | through-aperture / portal | entry geometry, edge, reveal target, final frame | vague “portal effect” |
| Action highlight | bullet-time / orbit / arc | motion state, orbit degrees, parallax, particles | generic normal-speed orbit |
| Fashion/group pose | dolly / pan / static | pose hierarchy, subtle gestures, depth | over-animated crowd |
| UGC/product proof | handheld phone / selfie | hook, tactile proof, imperfect realism | over-polished cinema look |
| Atmosphere / mood | slow dolly/pan or static active subject | one clear environmental motion proof | random effect pile |
| MV / music beat | beat-selected single family | rhythm cue, one dominant move | multi-trick chaos |
| Public / institution | restrained static/dolly/pan | dignified physical action, clarity | blockbuster spectacle |

## Primary camera families (detail)

### Through-aperture / reveal
Camera starts at an opening edge (keyhole, flame aperture, window, doorway, object gap) and pushes through to reveal the subject. State entry object, edge exit, reveal target, final composition.

### Mounted-object
Camera bolted to vehicle/object. Background streaks and vibrates; geometry of the mount stays stable.

### Handheld intimate track
Subtle operator tremble, focus breathing, forward track, human micro-actions.

### Dolly / pan / orbit
One precise path; shake-free unless handheld is intentional.

### Bullet-time
Subject frozen or ultra-slow; camera orbits with parallax, particles, and a clear final angle.

### Static-frame active subject
Locked frame; one simple subject/prop action; stable background.

### POV / FPV
Traversable continuous path with obstacles, altitude, acceleration, stabilization language.

### Deliberate montage
Only when explicitly needed; each beat still needs shot size and action; prefer split clips when possible.

## Subject motion states

Pick one per beat:

- normal-speed stillness with micro-expression
- steady walk / simple hand action
- frozen mid-action bullet-time
- vehicle-mounted rush
- static silhouette with environmental motion

For fragile faces/hands: prefer breath, eye movement, hair, smoke, fabric, tiny head turn.

## Physical motion layer menu

Choose **2–4** motivated layers:

- hair / fabric / breath / smoke / steam
- dust / debris / particles / grass / rubber
- wind / rain / train sway / car vibration
- reflections / neon slide / flicker / shadow travel / focus breathing
- foreground occluders / background parallax / aperture-edge exit
- water surface response / heat shimmer

## Naturalism and texture grammar

Naturalism is the default aesthetic goal even inside Creative Mode.

### Motion naturalism
- Prefer ordinary body weight, contact, recovery, and micro-hesitation over superhero smoothness.
- Keep one camera family; let physical layers prove the world instead of stacking tricks.
- For 15s cards: setup → discovery/interaction → aftermath/exit is enough. Do not overplot.

### Texture by medium
**Live-action / photoreal**
- Ask for stable material response already supported by the references: skin oil/pores only if present, fabric weave, metal scuff, wood grain, wet/dry ground, dust, grit, condensation.
- Reject / negative only when relevant: plastic skin, waxy face, crawling noise, boiling lines, synthetic grain soup, over-sharpen halos, morphing materials.
- Do not invent hyper-detail that fights the reference plates.

**2D / picture-book / stylized**
- Preserve the approved medium: paper tooth, ink contour, gouache body, cel flatness, watercolor bloom.
- Do not inject photoreal pore/skin rules into 2D.
- Avoid line boiling and texture crawl when those break the chosen medium; otherwise keep tactile material consistency.

### Audio naturalism
- No BGM.
- Prefer room tone and contact SFX that match the physical layers (footfall, cloth, fire crackle, wind, water) only when diegetic.
- Silence/near-silence is valid; do not pad with score.


## Creative priorities checklist

1. Visible premise and camera situation first
2. One primary camera family
3. Explicit subject motion state + one motivated evolution
4. 2–4 physical layers
5. Optional arc: calm → discovery → transformation/escalation → aftermath
6. Clear exit composition for next-scene handoff
7. Default duration is 15s multi-ref with a usable exit for the next card
8. No BGM; diegetic/room only
9. Naturalism/texture notes match the look medium

## Creative reference freedom

- References establish identity, environment, texture, or key prop
- Do not force incompatible refs into literal begin/middle/end frames
- Invent in-between motion and exit when Creative mode is on
- Preserve approved sheet: face silhouette, hair mass, age impression, costume, prop handling

## Anti-glue rule

Fire/torch/lamp/light matches are reserved for explicit character-transition beats or a cause that exists in the shot. Repeated light matches between unrelated scenes are a QC failure.

## Negative tail menu (role-specific only)

Pick only relevant risks:

- human close-up → no new facial structure, no face distortion, no bad hands if hands visible
- hand/product → no extra fingers, no product morphing, no logo/text corruption
- transition → no random object substitution, no location reset, preserve final target
- public/institution → no unintended logos/readable partisan symbols, no spectacle
- CapCut workflow → no generated subtitles/text unless intentionally diegetic

## Creative QA gate (Prompt Critic)

Before READY:

1. Clip role is named
2. Single dominant camera family (or explicit montage)
3. Duration defaults to 15s multi-ref unless explicitly overridden; action budget fits
4. Subject motion state is explicit
5. 2–4 physical layers are motivated
6. Ordered refs include every required sheet/crop
7. Character-sheet gate is correct
8. Exit composition is clear
9. Negative tail is short and role-specific
10. Prompt has no names/captions/provenance/model/folder pollution
11. Real-person/IP cameos from community examples are absent
12. Package schema fields are complete
13. Settings line says `Audio: ON`; the prompt requests diegetic SFX/room tone and no score, unless `@Audio1` is explicit
14. Look medium is declared; live-action texture naturalism or 2D medium-true material is addressed
15. Creative room is open (refs as anchors) unless Standard mode is justified

## Mini templates

### Through-aperture
```text
The camera starts close to [aperture edge], then moves forward through [opening].
As the foreground edges leave frame, it reveals [subject] in [environment].
[Subject] remains [motion state]; [physical layers] respond.
End on [clear final composition].
```

### Mounted-object
```text
The camera is fixed to [object position], [angle/lens].
[Object] moves [speed/direction]; background parallax and [vibration/wind] prove speed.
Keep [subject/object] geometry stable. End on [exit].
```

### Bullet-time
```text
[Subject] is frozen mid-[action].
Camera orbits [degrees] from [start] to [final] with [occluders/parallax/particles].
End on [final angle] with the action still suspended.
```

### Static active subject
```text
Static camera, [shot size], [framing]. [Subject] performs one action: [action].
Background stays stable; only [micro-motion layers] move.
No camera drift, no extra props.
```
