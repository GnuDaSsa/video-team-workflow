# Toonkit 2D snappy-animation grammar contract — 2026-09-02

## Goal

Make the user command `툰킷 문법을 적용해봐` a durable, opt-in prompt profile
for 2D/stylized Seedance animation. The profile must translate the analysed
Toonkit timing grammar into visible Korean direction without putting workflow
metadata into the provider prompt.

## Authority and scope

- `codex-skills/seedance-prompt-en/seedance-prompting.md` owns the prompt
  semantics and package marker.
- `codex-skills/videodirector/SKILL.md` owns recognition/routing of the user
  command and points to the Seedance owner instead of duplicating prompt rules.
- The profile is `toonkit_2d_snappy_v1`; it is opt-in and only applies to
  affected 2D/stylized blocks.
- It does not alter the existing duration lock, model routing, reference gates,
  UI procedure, safety gates, or audio ownership.

## Required prompt result

When enabled, each planned scene has one readable pose-to-pose beat:

`still hold → anticipation → sudden acceleration → controlled overshoot → sharp settle → delayed follow-through → final hold`.

The prompt must name start/final pose, physical contacts and one simple camera
path independent of the character motion. Cuts remain derived from the locked
cut/scene plan; the original comparison's 10-second four-shot layout is an
example, not a duration override.

## Package result

The package records:

```text
motion_grammar_profile: toonkit_2d_snappy_v1
prompt_rules_used: [..., toonkit_2d_snappy_v1]
```

Neither field may appear in the model-facing `*_prompt.txt`.

## Acceptance criteria

1. The exact Korean command activates the profile through `videodirector`.
2. The Seedance prompt guide defines timing, pose, mechanics, camera
   separation, and multi-scene cut behaviour.
3. The profile is explicitly opt-in, 2D/stylized-only, and preserves the
   workflow-owned duration lock.
4. Source and installed copies expose identical `toonkit_2d_snappy_v1` trigger,
   scope, and prompt-profile markers after a non-destructive, file-scoped
   deployment; unrelated pre-existing live-skill drift is preserved.
