# Truthful stop before production binding

## Evidence
A newly created project has two attested packs but no intended Runway session yet, no binding, no checkpoint, and no Generate. The current queue-exit checker demands a board sync even when the operator is correctly waiting for the user to identify the intended session. Fabricating a board observation is not an acceptable workaround.

## Acceptance
Allow a narrowly evidenced pre-binding human-action stop only when queue_runtime.json never exists, status explicitly marks production unstarted and jobs empty, all attested blocks are held for the session-selection blocker, the exact required user action is recorded, and no binding/recovery/preflight evidence exists. Existing/corrupt queue files and any production evidence continue to fail closed. Active/elapsed waits retain the existing controller. Replace the stale queue-sync next-action pointer with queue-cycle. Add positive and negative regression tests and verify deployed parity. No provider completion claim.
