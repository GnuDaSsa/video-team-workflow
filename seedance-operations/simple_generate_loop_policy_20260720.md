# Simple Runway/Seedance generate loop policy

Live companion to `codex-skills/seedance-prompt-en/SKILL.md` and `team-policies/chrome_hybrid_operator_20260721.md`.

Loop (Chrome Generate board):
1. ATTACH: Finder → Chrome Multi-ref, **Computer Use drag one file at a time**.
2. VERIFY: Chrome plugin confirms thumbnail count/order.
3. WEB: paste visual-only prompt; confirm Image refs, counter ≤3500, Seedance 2.0, Multi-reference, Audio Off, 16:9, 720p, duration, Unlimited.
4. If Generate is blue **and** eight checks pass: Chrome plugin clicks Generate **once**.
5. Gray / Please wait / no card: keep same prearm; 15-min observer may retry **same** scene after full preflight only.
6. Visible accepted card → `submitted_ui`. If in-flight &lt; 2 and next scene eligible → **immediately** start next scene (do not wait ~30 min).
7. Never double-click a scene that already has an accepted card. Never Credits/Max/Grok/picker unless user explicitly authorizes that exception.

Short rule: card exists → fill toward **~2 in-flight**; no card + blue+preflight → click once; gray/wait → wait same prearm; never idle a free slot for 30 min.

## Finder window placement rule — added 2026-07-20
Before any Runway/Seedance drag/drop, close unrelated Finder windows, open exactly one current upload_staging folder, immediately move Finder to a safe non-overlapping position, then inspect visible Runway UI. Drag one file at a time and verify each Image thumbnail before continuing. Use Codex Computer Use drag only. Do not let random Finder window placement cover reference slots, prompt/settings, or Generate.


## Finder placement correction — 2026-07-20
Staging Finder windows must be opened with `tools/position_seedance_finder_window_20260720.sh` and positioned at mid/slightly upper-right bounds `{780, 105, 1230, 505}`. They must not cover Runway refs/prompt/Generate. Close Finder immediately after uploads.
