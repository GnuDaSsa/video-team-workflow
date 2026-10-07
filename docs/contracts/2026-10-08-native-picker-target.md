# Native picker target consistency repair

## Goal
Repair the remaining mismatch between verified AXMain window and picker action target. Review GitHub history 4cdec9a and 71a06ba without merging divergent branches or overwriting unrelated live changes.

## Evidence and limits
The September main-window fix changed only the modal proof. Both picker action tails still use window 1. Modal proof is skipped when browser focus succeeds. Row AXSelected alone is not Open eligibility. Recent production turns failed at model capacity; saved attachment state predates a visible 3-reference composer and Generating video indicator. The exact current incident cause and actor are unconfirmed. No duplicate Generate or active-composer experiments.

## Scope
Always prove native picker ownership, use that nativeMainWindow in both action tails, require unique enabled AXIdentifier OKButton after row selection, document bounded native selection recovery. Preserve IME, exact-session, reference and permission gates. No new browser, agent or scheduler.

## Acceptance
Mocked regression tests cover focused and modal cases, failed proof sends no input, and both tails use the verified window. Full runtime test suite, compile, diff/shell checks. Scoped reviewed-patch deploy with backup/hash receipt; isolated remote commit. These do not prove native layout behavior or generated-media quality. Live picker test must not disturb an active/uncertain generation.
