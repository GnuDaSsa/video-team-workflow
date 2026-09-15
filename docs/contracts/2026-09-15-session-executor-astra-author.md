# Session executor / bounded Astra author

Scope: shared video workflow, not any project's creative assets. User selects the
session model. Planning/image/video authoring requires Astra; execution inherits
the session. A bounded native author child returns immutable local artifacts and
never touches browser/generator. Specific current-conversation spawn permission
remains required. No automatic self-turn model switch or resident manager.

Acceptance: routing and CLI do not pin execution to Luna; image authoring and
execution are separate; author payload pins actual tool model/effort, uses bounded
file context instead of full chat, and rejects missing approval; immutable handoff
verifier rejects changed prompt/reference/settings or mismatched block. Tests,
canonical deployment, isolated commit/push. Actual Luna-to-Astra native roundtrip
and generated media remain unverified unless independently exercised.
