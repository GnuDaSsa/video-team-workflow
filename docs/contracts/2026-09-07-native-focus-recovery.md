# Recover native focus without weakening exact-tab safety

## Goal
Fix the optional native helper preflight deadlock: focused-window validation precedes its own activation. Current Computer Use row/key failure remains a separate unproven cause; no media-completion claim.

## Contract
1. Before activation require exact session/target and active tab, but not an already focused app window. Reject missing/ambiguous/wrong/inactive target before any native action.
2. Activate the existing Aside app without keys, clipboard writes, navigation, new tabs or agents. Re-read the exact binding and require active + focused before input. For the native picker only, a modal may leave the browser focusedWindow flag false: permit an equivalent proof only by matching the CLI-bound browser window ID and exact current URL against native Aside front window/active tab, plus native main-window ownership of the open-panel sheet. Recheck that proof immediately before input; other commands retain strict focus refusal. Keep the OS frontmost and IME guards.
3. Fail closed on any intermediate error or focus loss; never replay mutating input. Existing UI technology/permission gates remain, including current Computer Use restrictions.
4. Add emitted-JS positive/negative tests and mock ordered native helper tests. Deploy only the canonical skill after tests/preflight; update release hashes, isolated commit/push.
5. Provide native ListView alias selection via AXSelected, no keystrokes/clipboard/IME changes. Validate helper alias, unique visible filename, guarded same-window ownership and actual selected state; changed layout fails closed.
6. Clearly separate tested code from unverified native upload and generation/QC.

## Verification
Configured quick checks, focused tests of background activation and wrong-tab/focus/IME failures, strict source/live release parity, git diff --check. User explicitly approved the limited same-Aside AppleScript route with “ㅇㅋ”. No new route or permission change is authorized.

## Result
120 unit tests, compile/syntax/diff checks and strict 66-file parity PASS. User approved the native helper route. Live same-window modal proof PASS; Korean IME remains unchanged. Keyboard-free native AXSelected row selection enabled Open, upload completed, and enlarged Image1 visually matched approved S01. Initial activation-only correction was insufficient; the modal/IME-safe correction is the verified path. Video generation/QC are separate and not yet run.
