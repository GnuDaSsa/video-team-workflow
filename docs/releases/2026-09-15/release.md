# Session executor / Astra author release

Source scope: runtime AGENTS §1.3; model_routing; native author_handoff request
builder and artifact hash verifier; runtime prompt/dispatch and image template;
Seedance dispatcher authority pointer. User-requested global workflow change.

Execution inherits the native session without model/thinking overrides; approved
legacy CLI production dispatch fails closed because it cannot inherit app thread
model. Planner and image/video authoring target Astra/xhigh; image production is
separate. Native spawn payload is bounded, file-scoped and permission-specific.
No native tool is invoked by this helper, no resident manager or scheduler added.
Parent keeps the selected model and records actual native author result evidence;
local receipt validation certifies only immutable bytes and block identity.

Verification: 188 regression tests, Python compile, shell syntax, diff whitespace;
release freeze/preflight/apply/check PASS, 69 managed files, 6 files changed.
Deployment backup: ~/.codex/archive/20260915_193328_015916_verified_video_release.

NOT verified: real Luna -> Astra native child -> parent roundtrip, actual tool
model provenance/creative QC, or prevention of an operator bypassing preflight.
No image/video generation, existing provider queue mutation, browser operation,
new agent or scheduler was performed for this workflow change.

Existing dirty harness/decisions/memory changes are preserved, not bundled in
this commit. A local recentCloseouts entry records this release without replacing
the unrelated blocked goal. Shared rule lives only in runtime AGENTS §1.3.
