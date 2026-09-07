# Hell Grind live-action routing release

## Result and ownership
The user explicitly requested reusable analysis and automatic application.
Public brief plus CINEDANCE V4, ACTING and LIRA previews were inspected. A
character triptych and an accompanying wide scene were visually inspected;
the feature film and all assets were not fully played or audited.

Creative content has one owner: `/Users/gnudas/wiki/concepts/video-prompting-live-action.md`.
`wiki-extract/video-prompting-live-action.md` is its version-controlled snapshot,
not a second maintained rulebook. The existing `medium-live-action` catalog row
already selects it; no new router, provider or competing skill was installed.
The compact body is 2,143 characters, below the 2,400-character selection cap.
Detailed Korean user report: `/Users/gnudas/Documents/영상작업/Hell_Grind_실사분석_2026-09-08.md`.
Source observation note: `/Users/gnudas/wiki/raw/articles/higgsfield-hell-grind-live-action-review-2026-09-08.md`.

## Narrow deployment
- `tools/deploy_one_skill_to_codex.sh --check videodirector` passed, then the
  same repository deployer applied the routing-only source change and archived
  the previous skill. Source/live bytes match.
- `image-prompt` is a third-party compiler, not a repository-owned fork.
  `image-prompt-routing.patch` owns only a pointer to the creative wiki page.
  Its original was archived, `patch --dry-run -p1` passed, then the same patch
  was applied in `~/.codex/skills/image-prompt`. Before/after hashes are recorded.
  The frontmatter and all compiler/generation behavior outside that paragraph
  remain unchanged. No external LIRA/CINEDANCE/ACTING file was installed.
- The wiki page was updated at its canonical path, the index entry refreshed,
  and a release snapshot saved. Existing Seedance adapters were not rewritten.
- Only the videodirector row hash was updated in the existing release manifest.
  A full release preflight reports pre-existing source drift in
  `seedance-prompt-en/scripts/runway_ui_helper.py` and `seedance-production.md`.
  Those are another active contract's pending deployment. They were not applied
  or included as changes in this release. No global deployment/parity PASS is claimed.

## Verification
- 7 local router scenarios: Korean photoreal portrait, dialogue, product,
  action, mixed 2D/live action, pure 2D and pure 3D. Positive routes preserve the
  complete profile; negative routes exclude it. Every packet is <=9,000 chars
  and <=6 selections. See `verification.json` and `verify-live-action.py`.
- 3 authored compiler examples: cafe still, object-only product still, narrow
  jacket edit. `check_prompt.mjs` returns `ok:true` for each, plus 14/14 built-in
  compiler fixtures. These are text smoke tests, not generated media.
- `quick_validate.py` passes videodirector. The same generic validator rejects
  image-prompt's pre-existing `version` frontmatter key; original and updated
  frontmatter are byte-identical. This metadata compatibility issue was not
  silently repaired as unrelated scope.
- Runtime Python compile, 143 unit tests, deployment shell syntax and diff
  checks pass. No runtime code changed.
- Wiki lint: 0 errors, 46 existing raw-hash warnings, 20 informational notices.
  The new source note hash and canonical/extract parity pass independently.

## Not verified / next use
No paid generation, full-film viewing, audio/lipsync evaluation, independent
agent evaluation, provider/UI interaction, active project mutation, new agent,
monitor or schedule. Next real photoreal request should use these routes, then
judge actual output for skin, contact, geography and performance continuity.
Automatic instruction/knowledge routing is verified, not a promise of image
or video quality on the first generation.

## Rollback / reapplication
See `local-backup-path.txt` for original local files. Check the current
image-prompt hash against `image-prompt-routing-hashes.json` before reversing
or reapplying the overlay; preserve later edits. Never overwrite an unrelated
updated compiler with the old backup. To reapply to a compatible clean version:

```sh
patch --dry-run -d "$HOME/.codex/skills/image-prompt" -p1 < image-prompt-routing.patch
patch -d "$HOME/.codex/skills/image-prompt" -p1 < image-prompt-routing.patch
```

The top-level active monitoring harness contract remains unchanged; this task
is recorded as an independent `recentCloseouts` entry.
