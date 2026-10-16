# Native picker target repair

GitHub history: `4cdec9a` added modal ownership/AX selection; `71a06ba` fixed only the proof's main-window lookup and explicitly left picker layout assumptions unresolved. Source inspection finds both action tails still referenced window 1 and focused browser checks skipped modal proof.

Repair: always prove native picker ownership, use the proved nativeMainWindow in both tails, and reject missing/ambiguous/disabled Open after AXSelected. Exact-session, IME, alias and UI-technology gates remain. No automatic keyboard recovery, upload or Generate added.

Verification: 202 local unit tests and 220 tests on the isolated origin/main-based release tree, Python compile, shell syntax, diff check PASS. Two-file reviewed patch deployment and installed SHA checks PASS. Full bundle parity not asserted; unrelated drift and dirty changes preserved. Native AppleScript/CUA picker execution was NOT retested, because an existing Generating video indicator was visible. Prompt readback matched the intended local source. No new upload, Generate, scheduler or media QC.

The current incident's direct cause and generation actor remain unconfirmed. Model capacity errors and stale saved lane state are separate observations, not evidence that this patch fixes every submission failure.
