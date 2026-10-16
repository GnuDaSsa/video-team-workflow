# Seedance 2.0 multimodal patterns (review lens)

Load when a block uses video/audio sources, extension, repair, or an unusual
method. Prompts are still written in the template in `seedance-prompting.md`;
the fragments below show only what goes **inside** its binding sentences and
shot sections. No UI operation here.

## Provenance

User source `/Users/gnudas/Downloads/seedance2-prompting.zip`
(SHA-256 `42612531d9c671cdfdbc61df88f8825c4745e48e8a897a2b2f36a7fbcf1b48f3`),
integrated 2026-08-14 and reconciled with
[ByteDance Seedance 2.0 launch](https://seed.bytedance.com/blog/seedance-2-0-official-launch)
and [Runway: Creating with Seedance 2.0](https://help.runwayml.com/hc/en-us/articles/50488490233363-Creating-with-Seedance-2-0).
It is an input, not a second authority.

Capability snapshot (2026-08-14, Runway): text/image/video/audio inputs;
`References`, `Start / End frames`, `Text to video`; 5–15 s; up to 9 images,
3 videos and 3 audio files (each media type's combined duration under 15 s). The
visible UI and current help page win over this snapshot.

Not promoted as rules: fixed three-second segments; "completely reference" as a
magic phrase; an absolute ban on real-person images (follow current moderation
and never retry a moderated input unchanged); a 4 s minimum / 12-file limit;
backward extension unless the UI exposes it.

## Method first

| Need | Method | Prompt responsibility |
|---|---|---|
| Blend identity, environment, prop, motion or sound refs | `References` | narrow role per source; describe the resulting scene |
| Exact first frame or first/last boundary | `Start / End frames` | motion and continuity between fixed boundaries |
| No source asset, or moderation blocks image input | `Text to video` | own composition, identity, blocking, light, action, camera, sound |
| Keep source-video motion, change subject/style/light | reference video / video edit | name exactly what changes and what stays |
| Continue a good clip | extension | observed boundary state, invariants, new action, new end state |
| Replace one bad beat | repair/edit | bound the changed interval, preserve the rest |
| One approved unified board | declared storyboard mode | use its internal `shot_id`, never attachment order |

`standard_i2v` uses the approved per-cut frame plus identity refs;
`no_i2v_reference_native` makes the prompt own the missing composition.

## Five-question lens

Check a finished prompt against these; they map onto template parts and are not
a separate layout: (1) source binding — every token has one job; (2) subject and
space — who/what/where and what persists (STYLE/IDENTITY); (3) temporal action —
feasible order and closing state (shot sections, end frame); (4) camera and
sound — the declared move per shot and the `Sound:` line; (5) constraints — one
or two shot-specific risks. Anything that changes nothing on screen moves to the
pack.

## Source binding

Each binding says what to take and what not to overwrite:

```text
@Image1 is the lead's identity: take face silhouette and costume only.
@Image2 sets the space and light; it never changes the face or build from @Image1.
@Video1 supplies the camera path only; do not take its people or their look.
@Audio1 guides the line's pronunciation timing, breath and pauses only; it is not background music.
```

Avoid unscoped lines such as `Use @Video1 as reference.` and one source with
conflicting jobs; if one source truly has two roles, state both.

- Image roles: identity (face silhouette, hair mass, age impression, build,
  costume, signature prop); environment (layout, architecture, palette, time of
  day, material); prop/product (geometry, surface, safe logo placement);
  boundary (start/end composition or one board `shot_id`); style (medium,
  line/fill/shading, texture, light response). A triptych or identity crop is
  identity/body only — never pose, scene, camera or order.
- Video roles: camera path/mount only; action, choreography or body mechanics
  only; edit rhythm only; effect/transition behavior only; a source to relight,
  restyle, repair or extend; its audio only when intended.
- Audio roles: performed speech guide (timing, cadence, breath, pause, mic
  distance); score/beat guide; ambience/SFX guide; voice colour only when policy
  permits. Routes and QC: dialogue table in `seedance-shared-contract.md`.

```text
@Video1 supplies only its low side-tracking path and speed changes. The location comes from @Image2 and the lead's identity from @Image1.
```

## Beats inside a shot

Within a shot section: `start state → action → contact → physical result → end
state`. Each beat holds one action or state change and inherits the previous
state. Convert emotion into evidence — not `she is nervous` but `her eyes flick
to the exit, her thumb presses the cup rim twice, she inhales and her shoulders
rise slightly`.

| Shot length | Practical budget |
|---|---|
| up to ~6 s | one action or one camera discovery |
| 7–10 s | setup → one interaction → reveal; about three major verbs |
| 11–15 s | two or three causal phases, the declared move, explicit end frame |

If the budget overflows, the storyboard needs another shot or block — never
faster transitions.

## Extension and repair

Forward extension — inspect the actual last frames, then write: observed
boundary state, invariants, new action, new end state.

```text
Continue forward from the last frame of @Video1. The woman stands at the left of the window holding the curtain in her right hand; low sunset light falls on the left side of her face. Keep the same identity, costume, camera direction, room layout, sun direction and room reverb. She slowly lets go of the curtain and turns into the room; the camera follows half a step behind as she picks up the letter on the desk. End on a medium close-up of the hand holding the letter and her hesitant gaze.
```

Do not extend a clip whose last frames already drift in identity, anatomy or
geometry.

Local repair — name the bounded change and the preserved remainder:

```text
Keep the opening and the final composition of @Video1. Only in the middle beat, the right hand takes the cup handle naturally and lifts it. Do not change the face, left hand, cup shape, camera path, lighting, background geometry or sound.
```

If the identity or scene anchor is globally wrong, regenerate from the correct
deck instead of stacking repair lines. (Repair/extension packs still follow the
template's header and the duration lock.)

## Reusable binding fragments

```text
Reference composite: @Image1 keeps the lead's identity and costume; @Image2 sets the scene layout and time of day; @Image3 fixes the shape of the product in her hand. Apply only the camera path of @Video1, not its people or location.
Choreography transfer: the person from @Image1 performs the move order and weight shifts of @Video1; face, build and costume stay from @Image1, never the dancer in @Video1. Foot contact, cloth inertia, breath and floor response stay natural.
Product swap: keep the edit rhythm and camera structure of @Video1 and replace only the product with the one in @Image1, keeping its proportions, edges, material, color and logo position; hand-to-product contact is physically exact.
Storyboard execution: render only internal shot S03 of the approved board in @Image1 as a real film scene; no panels, borders, numbers, captions or UI appear. Identity from @Image2, space and materials from @Image3.
```

## Lens checklist

- Method matches the control needed (References / Start-End / T2V / edit /
  extension).
- Every attached image, video and audio has one narrow binding; pack declares
  `model_facing_multimodal_binding_v1`.
- Attachment order is not narrative order.
- The duration can physically contain the actions.
- Extension starts from the observed boundary state.
- Constraints are short and shot-specific.
