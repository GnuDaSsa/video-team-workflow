# Harness source pointer

The canonical source-checkout harness rules are in [AGENTS.md](AGENTS.md).
Resolve `docs/harness-config.json` and all configured paths from the repository
root. This pointer adds no second rule set. Installed runtime harness files are
separate deployment artifacts; exporting this repository does not install them.
