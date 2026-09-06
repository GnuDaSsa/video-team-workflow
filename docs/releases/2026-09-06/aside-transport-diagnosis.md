# Aside transport diagnosis and resolution

Read-only smoke: CLI returned exit 0 with no result marker. The initial async
await hypothesis was disproved: constant-only nested async logging succeeded.
The isolated probe found `typeof URL === "undefined"` in the Aside REPL sandbox;
the matcher caught that ReferenceError and classified every tab as unmatched.

Resolution: parse only the exact allowlisted HTTPS base and session query in
REPL (no URL global), retain full browser URL verification inside page.evaluate,
and serialize caught errors through the explicit result marker. Unit tests now
execute emitted JavaScript with `global.URL=undefined`, not a browser-like Node
default. A real same-tab bind + title/host read then passed. No provider mutation,
new tab, upload, Generate, or browser agent was used.

## Hidden image-agent route found during staged-tree review

The legacy image runner delegated its default backend to `codex_app_image_cli`,
whose implementation called App Server `thread/start` and `turn/start`. Its
reference-conditioned branch silently invoked the separate Image API script.
Neither is equivalent to a bounded built-in image-generation call in the current
owner. The runner is now a non-executing compatibility stop; `prepare-image-batch`
produces immutable prompt/reference hashes only. The old dedicated CLI and its
video-image symlink are explicitly archived/retired, not used as fallback.
