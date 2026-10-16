# XAZINGA prompting adapter (review lens)

Source reviewed: `https://www.xazinga.com/apps` (2026-08-21) — its Seedance
2.0/2.5, video-prompt-builder, guide and director-skill material. Only
provider-agnostic checks are kept; the prompt is still the template in
`seedance-prompting.md`. Do not copy the source's claims about model limits,
features or preferred languages.

## Every attachment has use / exclude / scope

For each `@ImageN`, `@VideoN`, `@AudioN` the binding sentence (and pack map)
declares:

- **use** — exactly which visible attributes are borrowed (identity silhouette,
  outfit, building geometry, camera motion, action rhythm, sound texture);
- **exclude** — what must not transfer (a sheet's other panels/background, a
  building image's occupants, a camera reference's cast/look);
- **scope** — which shot(s) may use it.

A role-less attachment is a preflight failure. Never give an identity sheet to
a shot without that character or to a different person. Two recurring
characters: separate crops/sheets, each bound to a screen role; avoid a
face-forward crowd that could clone an identity.

## Planning audit (pack only, never pasted)

Before locking, keep in the pack/ledger: an effects/motion inventory (repeated
device check), a density map (quiet vs eventful beats), an energy arc (hook →
development → release), and a light contract (source, direction, colour
temperature, contrast, exposure change, final light state). This audit must
never turn into effect stuffing; every effect needs a visible cause.

## Transition, extension, repair shapes

Written inside the template's shot sections:

- **Transition:** trigger → camera behavior → visible transformation → arrival.
- **Extension:** boundary-frame continuity → one new action → final anchor.
- **Repair:** goal → elements to preserve → exact range → changed action →
  unchanged constraints.

Use concrete physical language, not genre adjectives or preset names. Audio and
language: `seedance-shared-contract.md` (effects-only wording is in its route
table).

## Lens checklist

Reject before locking when:

- an attachment lacks use/exclude/scope;
- a person other than the sheet's character receives that sheet/crop, or a
  crowd is likely to clone an identity;
- a shot lacks its declared camera, a light cue where light matters, a start
  state or the end frame;
- a transition is a generic montage instead of a causal bridge;
- the prompt contains internal audit/ledger text;
- the `Sound:` line conflicts with the block's audio route.
