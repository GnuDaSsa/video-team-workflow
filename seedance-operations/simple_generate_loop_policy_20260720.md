# Simple Runway/Seedance generate loop policy — 2026-07-20 user correction

User correction: do not overcomplicate with stale click-nonce logic.

Loop:
1. Put the current/next scene images into Runway via Finder-frontmost direct drag/drop only.
2. Put the matching attested visual-only Terra/high prompt into Runway.
3. Verify visible UI: Image refs, prompt counter <=3500, Seedance 2.0, Multi-reference, Audio Off, 16:9, 720p, 15s, Unlimited.
4. If Generate is blue: click Generate once.
5. If Runway returns `Please wait` / Generate gray / no accepted generation state: this is NOT a completed submission and does NOT permanently consume the scene. Start/update a 15-minute scheduler to click the same prearmed scene when Generate becomes blue again after preflight.
6. If a visible queued/generating/processing/completed result appears, mark the scene submitted and advance to the next scene.
7. Do not click again only when the scene has a visible accepted job/result. Card/output evidence blocks duplicates; a failed wait-blocker click does not.
8. Never switch Credits/Max, never use Grok, never use picker/asset selector unless user explicitly says so.

Short rule: card/accepted-job exists -> advance; no accepted-job and blue -> click; gray/wait -> scheduler.

## Finder window placement rule — added 2026-07-20
Before any Runway/Seedance drag/drop, close unrelated Finder windows, open exactly one current upload_staging folder, immediately move Finder to a safe non-overlapping position, then inspect visible Runway UI. Drag one file at a time and verify each Image thumbnail before continuing. Use Codex Computer Use drag only. Do not let random Finder window placement cover reference slots, prompt/settings, or Generate.


## Finder placement correction — 2026-07-20
Staging Finder windows must be opened with `tools/position_seedance_finder_window_20260720.sh` and positioned at mid/slightly upper-right bounds `{780, 105, 1230, 505}`. They must not cover Runway refs/prompt/Generate. Close Finder immediately after uploads.
