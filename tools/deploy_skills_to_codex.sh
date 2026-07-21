#!/bin/zsh
# Deploy the packaged video-team skills into ~/.codex/skills.
# The git repo is the canonical, version-controlled source; ~/.codex/skills is a deployment target.
# Replaced files are archived under ~/.codex/archive/<timestamp>_skill_deploy/ for quick local rollback;
# full history rollback is via git in this repo.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$HOME/.codex/skills"
POLICY_DEST="$HOME/.codex/video-team-policies"
STAMP="$(date +%Y%m%d_%H%M%S)"
ARCHIVE="$HOME/.codex/archive/${STAMP}_skill_deploy"

for skill in "$REPO_DIR"/codex-skills/*/; do
  name="$(basename "$skill")"
  if [ -d "$DEST/$name" ]; then
    mkdir -p "$ARCHIVE"
    cp -R "$DEST/$name" "$ARCHIVE/$name"
  fi
  rsync -a --delete "$skill" "$DEST/$name/"
  echo "deployed: $name"
done

if [ -d "$POLICY_DEST" ]; then
  mkdir -p "$ARCHIVE"
  cp -R "$POLICY_DEST" "$ARCHIVE/video-team-policies"
fi
rsync -a --delete "$REPO_DIR/team-policies/" "$POLICY_DEST/"
echo "deployed: video-team-policies"

echo "archived previous versions to: $ARCHIVE"
