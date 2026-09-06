#!/bin/zsh
# Canonical deployment entrypoint. Strict parity and safe preflight are distinct.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
case "${1:-}" in
  --check) exec python3 "$ROOT/tools/video_release.py" check ;;
  --preflight) exec python3 "$ROOT/tools/video_release.py" preflight ;;
  "") exec python3 "$ROOT/tools/video_release.py" apply ;;
  *) echo 'Usage: deploy_skills_to_codex.sh [--preflight|--check]' >&2; exit 2 ;;
esac
