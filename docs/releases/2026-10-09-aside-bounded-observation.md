# Aside CLI bounded observation — 2026-10-09

Added `aside_bridge.py observe --binding ... [--record]` to the existing exact-session bridge. A single guarded REPL read returns modal surface, reference slot labels, editor count/length and Generate affordance. No new bridge, browser owner, observer, agent or schedule. No mutations or retries. Phase-specific identity/prompt/settings checks remain mandatory.

Optional recording writes a separate allowlisted observation receipt atomically, with observed_at and binding hash. It never overwrites lane status, claims provider acceptance or connects a scheduler automatically. Stale or switched binding rejects recording; native chooser status remains unknown to DOM. No raw prompts/account URLs persisted.

Verified: 237 local tests PASS (8 new tests including 4 DOM-stage fixtures, one-call assertion, malformed/zero-exit CLI failure, privacy, changed binding, recording safety), Python compile, shell syntax, reviewed two-file deployment and unchanged live Runway helper SHA. Existing installed prompt guards preserved. No production browser was operated; real latency, attachment/Generate throughput, future wake and media completion not benchmarked or verified. This is the observation stage optimization, not full end-to-end workflow repair.
