#!/bin/zsh
# Deploy one repository-owned skill without syncing unrelated in-flight skills.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$HOME/.codex/skills"
STAMP="$(date +%Y%m%d_%H%M%S)"
ARCHIVE="$HOME/.codex/archive/${STAMP}_single_skill_deploy"
MODE="deploy"

if [ "${1:-}" = "--check" ]; then
  MODE="check"
  shift
fi

if [ "$#" -ne 1 ]; then
  echo "usage: $0 [--check] <skill-name>" >&2
  exit 2
fi

name="$1"
if [[ ! "$name" =~ '^[a-z0-9][a-z0-9-]*$' ]]; then
  echo "invalid skill name: $name" >&2
  exit 2
fi

src="$REPO_DIR/codex-skills/$name"
live="$DEST/$name"
if [ ! -d "$src" ]; then
  echo "skill is not owned by this repository: $name" >&2
  exit 2
fi

destructive=0
if [ -d "$live" ]; then
  orphans="$(cd "$live" && find . \( -type f -o -type l \) | while read -r f; do
    [ -e "$src/$f" ] || echo "$f"
  done)"
  if [ -n "$orphans" ]; then
    echo "REFUSING TO DEPLOY: live-only files would be deleted from '$name':" >&2
    echo "$orphans" | sed 's|^\./|  |' >&2
    destructive=1
  fi
fi

[ "$destructive" -eq 0 ] || exit 1

if [ "$MODE" = "check" ]; then
  if [ -d "$live" ] && diff -rq "$src" "$live" >/dev/null 2>&1; then
    echo "safe to deploy: '$name' already matches the repository"
  else
    echo "safe to deploy: '$name' will be updated from the repository"
  fi
  exit 0
fi

if [ -d "$live" ]; then
  mkdir -p "$ARCHIVE"
  cp -R "$live" "$ARCHIVE/$name"
fi

mkdir -p "$live"
rsync -a --delete "$src/" "$live/"

if ! diff -rq "$src" "$live" >/dev/null 2>&1; then
  echo "deployment verification failed for '$name'" >&2
  exit 1
fi

echo "deployed: $name"
if [ -d "$ARCHIVE/$name" ]; then
  echo "archived previous version to: $ARCHIVE/$name"
fi
