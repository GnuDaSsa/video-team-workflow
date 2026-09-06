# Recover native focus without weakening exact-tab safety

## Goal
Fix the optional native helper preflight deadlock: focused-window validation precedes its own activation. Current Computer Use row/key failure remains a separate unproven cause; no media-completion claim.

## Contract
1. Before activation require exact session/target and active tab, but not an already focused app window. Reject missing/ambiguous/wrong/inactive target before any native action.
2. Activate the existing Aside app without keys, clipboard writes, navigation, new tabs or agents. Re-read the exact binding and require active + focused before input. Keep the immediate OS frontmost check and IME guard.
3. Fail closed on any intermediate error or focus loss; never replay mutating input. Existing UI technology/permission gates remain, including current Computer Use restrictions.
4. Add emitted-JS positive/negative tests and mock ordered native helper tests. Deploy only the canonical skill after tests/preflight; update release hashes, isolated commit/push.
5. Clearly separate tested code from unverified native upload and generation/QC.

## Verification
Configured quick checks, focused tests of background activation and wrong-tab/focus/IME failures, strict source/live release parity, git diff --check. Live AppleScript route requires explicit user approval in this conversation before execution.

## Result
Implementation and deployment PASS: 116 tests, Python compile, shell syntax, strict 66-file parity (3 files changed), diff check. Real native-helper upload remains unverified pending one explicit technology exception; zero generated videos. Archive: `~/.codex/archive/20260907_054544_741299_verified_video_release`.
