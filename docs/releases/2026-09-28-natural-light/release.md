# 실사 조명·재질 기본값 — source release

## Evidence and owner
Source: [페이퍼로지 영상 5:50](https://www.youtube.com/watch?v=VvvzHA-xfAE&t=350).
Auto-caption review covers 5:47–6:36; the visible prompt at 5:59 confirms motivated
light/shadow, material grain and restrained image treatment. This is an adopted
creative preference, not proof of complete AI-artifact removal. See source-review.md.

Single creative owner: `/Users/gnudas/wiki/concepts/video-prompting-live-action.md`.
The repository `wiki-extract` is its snapshot. Native Aside's existing image-optics
and video-camera cards are reviewed derivatives, not a second independent policy.
Their upstream hashes and catalog source hash change together. Existing Codex
image-prompt/videodirector pointers require no skill/procedure rewrite.

## Scope
Natural variation without manufactured dirt, extreme pores, wrinkles or noise;
retain approved identity, genuine material gloss and clinical cleanliness.
Gongnyang keeps positive appearance instructions. Unwanted HDR/plastic/oversharp
looks are QC criteria. Video still requires actual playback, not frame-only PASS.
Mixed media uses this only on photoreal portions; explicit style/edit intent wins.
Provider, language, model, audio, timeline, reference mode and safety gates unchanged.

## Verification before deployment
- 7 Codex + 7 native selection/verification cases PASS; 2 positive image compiler
  examples PASS. Complete 2,376-character profile fits the 2,400 cap; packets fit
  six selections/9,000 characters. See verify.py and predeploy-verification.json.
- 55 targeted knowledge/deployer tests + 217 runtime tests PASS.
- The initial targeted run hit the existing macOS `/var` vs `/private/var` temp
  symlink guard. Re-running with realpath TMPDIR passes; guard/code unchanged.
- Native baseline parity PASS, freeze reports 46 source files. Preflight after
  the change shows only the two intended knowledge-file differences, not other
  live drift. Wiki patch dry-run and git diff --check PASS.
- Existing wiki September 26 removal of the obsolete fixed ten-test wording is
  preserved while refreshing the older repository snapshot.

## Deployment plan / safety
Apply `wiki.patch` only after matching wiki-preimage.json and successful dry-run;
originals archived in `~/.codex/archive/20260928_natural_light/wiki/`.
Then use `tools/deploy_aside_workflow.mjs --apply` and `--check`. Do not deploy
unrelated Codex/runtime files or rewrite submitted/historical knowledge receipts.
New unsubmitted author requests must reselect knowledge. Deployment result is
recorded separately after actual installed verification.

## Not verified
No new image/video generation, full-playback quality experiment, independent
model behavioral check or end-to-end improvement guarantee. No paid service,
new agent, browser owner, scheduler or source-video reuse. Project clinical/fact/
rights and identity holds stay in effect; male Fish narration remains deferred.
