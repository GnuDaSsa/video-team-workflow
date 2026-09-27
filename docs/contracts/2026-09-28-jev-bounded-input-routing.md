# Bounded input routing: code / JEV / current owner

## Request and scope
The user explicitly asked to apply the best version after analyzing JEV's
principles and replacing repetitive LLM decisions. Prior analysis is recorded
in the local wiki query `jev-video-workflow-fit-2026-09-27`; no private task,
account, provider URL, prompt body or key belongs in this repository.

Implement inside the existing owner, helpers and deployment path. No new agent,
browser, scheduler, daemon, production project or live generation. Preserve
unrelated dirty files in the old main checkout by working from origin/main in
an isolated worktree. Codex and native Aside keep their own author/language/UI
contracts; shared decision code must not import native author's Astra-only rule
into Codex's current-session default.

## Changes and acceptance
1. Extend the existing JEV dispatcher with a local-first `route` entry. Explicit
   known eligible actions bypass all key/network/ledger work. Creative/visual,
   ungrounded/stale, low-certainty, failed and unapproved semantic cases return
   to the same owner or re-observation, not a new agent or an automatic retry.
2. Semantic calls require current-scope explicit JEV approval, use only the
   existing bounded anonymized state and allowed actions, retain the existing
   three-attempt ledger/cache, and never return execution authorization. A
   high-confidence recommendation is not a safe-action or media-QC guarantee.
   No real HTTP classifier call is made during this implementation.
3. Make the existing Codex prompt paste a bounded idempotent transaction: same
   normalized accepted text returns success without mutation; differing text
   and a blocking visible dialog are preserved. Keep the single existing
   exact-session paste path, actual read-back, language/pack gates, and uncertain
   result recovery. No hidden file input or native Aside fill adapter transplant.
4. Update native and Codex stage entry instructions to prefer existing guarded
   helpers for known work, the bounded semantic router only where needed, and
   current-owner reasoning for new authoring, visual understanding and recovery.
   Do not add mandatory startup JEV calls or permanent approval.
5. Add offline positive/negative regression tests, run configured quick checks,
   scoped release preflight/deployment/hash checks, update harness records and
   push isolated source/evidence commits to GitHub main. Keep existing project
   holds and unrelated deployed drift intact.

## Verification limits
Mock network/browser tests prove control-flow and data boundaries only. No live
JEV Korean accuracy, provider/browser behavior, media quality or end-to-end
latency improvement is claimed. A future authorized production run should
compare input time and model calls, raw-prompt preservation and duplicate acts.

## State
Source implementation and 706 offline tests pass. Scoped deployment is pending;
see `docs/releases/2026-09-28-jev-input-routing.md`.
