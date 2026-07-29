# Handoff schema

**The prompt is Korean and prompt-only.** Package fields (scene id, mode, reference roles, gates, expected settings, exit) live in `<BLOCK>_package.md` and never enter Runway; the prompt lives in `<BLOCK>_prompt.txt`.

The prompting team must emit this package before any production branch work.

## Required fields

| Field | Meaning |
|---|---|
| Scene ID | Stable scene/cut identifier |
| Look medium | `live-action` / `2D/stylized` / `mixed` |
| 2D reference architecture | If 2D/stylized: immutable `STYLE LOCK`, `CONTINUITY`, `DIRECTION`, plus one variable `SHOT`; otherwise `not applicable` |
| Naturalism / texture notes | Medium-aware material and anti-AI-texture guidance |
| Mode | `Creative` or `Standard` |
| Clip role | identity / reveal / speed / action / product proof / UGC hook / atmosphere / montage / transition |
| Camera family | One primary family name |
| Subject motion state | normal-speed / micro / static / frozen / vehicle-mounted (+ short detail) |
| Visual prompt | Final English visual-only prompt for Runway |
| Ordered references | Image1..N with exact path and visible role sentence |
| Character-sheet gate | `required` or `not applicable` |
| Physical motion layers | 2–4 bullets |
| Exit composition / next-scene handoff | Final frame + what the next scene receives |
| Expected duration/audio/settings | Default **15s multi-ref**; **Audio: ON**; prompt names the soundscape (`@Audio1` for dialogue) |
| Source root and exact file paths | Machine-usable paths |
| Critic verdict | `READY` or `REVISE` |
| Revision notes | Owning role + fix list when REVISE |

## Visual prompt pollution blacklist

Do **not** put these inside the Runway visual prompt:

- proper names of people/places when avoidable
- historical/political labels
- captions, narration, contest copy
- source-frame / provenance / folder / QC language
- Gongnyang / imagegen / model names
- artist or living-style imitation requests
- needless weapon/graphic wording
- generic negative walls

Facts and names belong in caption/narration packages outside Runway.

## Standing defaults for duration / audio / naturalism

Default every package to:

- **Duration:** 15s
- **References:** multi-reference (ordered `@ImageN`)
- **Creative room:** open after identity lock; refs are anchors, not cages
- **Audio:** toggle stays ON. The prompt names the soundscape for that shot — ambience, SFX, room tone, or music
- **Dialogue:** none unless a verified performed `@Audio1` speech guide is attached
- **Naturalism:** believable physics and imperfect micro-motion over glossy spectacle
- **Texture:**
  - live-action/photoreal → stable materials; reject plastic/waxy/crawling texture
  - 2D/stylized → medium-true material; do not force photoreal pores

For 2D/stylized source references, the prompt must preserve four blocks:

```text
STYLE LOCK   = medium, linework, fill/shading, palette, rendering rules
CONTINUITY   = character design, proportions, costume/props, geography, world rules
DIRECTION    = camera language, pacing, and sound/impact cue grammar
SHOT         = one unique variable beat for this cut
```

The first three blocks are immutable across the sequence. If any of them must change, start a new style-lock sequence instead of editing one shot in place.

Shorter duration, BGM, or dialogue is an explicit exception and must be written into the package.

Unless the package explicitly includes a verified performed `@Audio1` speech guide:

- visual + diegetic SFX / room tone only
- name the intended soundscape rather than leaving audio unstated; the toggle always stays ON
- no spoken dialogue generation request

If the user later attaches `@Audio1`, revise through Prompt Composer + Critic; production still verifies the visible audio asset.

## Acceptance vs production completion

| State | Meaning |
|---|---|
| Critic READY | Prompt package is authoring-complete |
| Production `submitted_ui` | Visible accepted Runway card exists |
| Production complete | Downloaded file + size + ffprobe duration/codec + QC verdict |

This skill can only declare Critic READY / REVISE.

## Example READY skeleton

```text
Scene ID: S03_NAM_TORCH_THREAT
Mode: Creative
Clip role: action
Camera family: handheld intimate track
Subject motion state: normal-speed run with micro shoulder checks
Visual prompt: |
  Use the forest danger reference and identity sheet as independent anchors...
Ordered references:
  Image1 = /path/forest_run.png — low forest path and torch light environment
  Image2 = /path/danger_silhouette.png — distant non-graphic threat viewpoint
  Image3 = /path/nam_identity_crop.png — approved face/hair/costume identity lock
Character-sheet gate: required
Physical motion layers:
  1. torch flame lean and ember scatter from running gait
  2. fabric and hair response to forward rush
  3. foreground branch occlusion and path parallax
  4. breath vapor / cold air in the ridge check
Exit composition / next-scene handoff: medium ridge check facing deeper forest; next scene receives his eyeline and torch as continuity anchors
Expected duration/audio/settings: 15s multi-ref; Audio: ON; soundscape directed in the prompt; 16:9; Seedance 2.0
Source root and exact file paths: /project/refs/...
Critic verdict: READY
Revision notes: none
```
