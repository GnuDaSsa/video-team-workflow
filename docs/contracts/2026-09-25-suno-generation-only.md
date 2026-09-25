# Suno generation-only handoff — 2026-09-25

## User correction

Suno downloads are limited. The user alone chooses and downloads songs; the
assistant's Music Director role ends after generation. Remove instructions to
download, listen to/rank, recommend, select, or Music Lock generated candidates.

## Scope and source

The canonical creative owner is `codex-skills/music-director/SKILL.md`.
`runtime/templates/music.md` is its video-lane handoff; `runtime/AGENTS.md` and
`lane_gates.py` own rail gating. The official Suno help confirms downloads are
allowance-limited as of September 2026:
https://help.suno.com/en/articles/13876865

## Acceptance

1. A generated song returns only the verified Suno ID/link and settings.
2. Music lane enters `PENDING_USER_AUDIO`; `next` lists an explicit user action,
   not a rerun of Music or a Planner entry.
3. The video project's `manifest.music` stays `NOT_LOCKED`; Planner requires a
   separately provided, registered, measured audio file or an independently
   authorized visual-only project exception.
4. The music skill and reference contain pre-generation guidance only; no
   post-generation download/listening/ranking/selection procedure remains.
5. This change does not alter Seedance/video download rules, public submission
   gates, or a user's ability to request later editing using their own file.

## Verification boundary

Document and unit tests can verify routing and gates. No Suno session is used
in this instruction-change task, so live generation behavior remains to be
confirmed on the next authorized music request.

## Verified result

- Canonical source commit `11066fb` pushed to `origin/main`.
- Source skill validation, 451 Aside/deployer tests, 200 runtime tests, Python
  compile, shell syntax, manifest preflight, diff check and harness validation passed.
  The first Node run hit the known macOS symlinked `/tmp` fixture error; a
  realpath `TMPDIR=/private/tmp` rerun passed 451/451.
- `music-director` deployed through the targeted skill path. Runtime AGENTS,
  Music template and lane gate deployed by reviewed scoped release. All six
  changed live files matched source SHA-256 after deployment. Full bundle
  parity is not claimed because unrelated live drift remains.
- No Suno session, music generation, download, or production latency test was
  performed. The next authorized Suno request should verify the UI handoff.
