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

# --- drift guard (added 2026-07-28) ---------------------------------------
# This script uses `rsync --delete`: anything present in ~/.codex but absent
# from the repo is DESTROYED. On 2026-07-26 the live skills were ~5 days ahead
# of the repo (4-file seedance split + seedance-creative-prompt-team existed
# only live), so a deploy would have silently deleted them.
# Refuse to deploy while live is ahead of the repo. Run --check first.
preflight_drift_check() {
  drift=0
  for live in "$DEST"/*/; do
    name="${$(basename "$live")}"
    [ -d "$REPO_DIR/codex-skills/$name" ] || continue
    if ! diff -rq "$REPO_DIR/codex-skills/$name" "$live" >/dev/null 2>&1; then
      echo "DRIFT: $name differs between repo and live"
      diff -rq "$REPO_DIR/codex-skills/$name" "$live" 2>&1 | sed 's/^/       /'
      drift=1
    fi
  done
  # A video-team skill that exists live but not in the repo would be deleted.
  for live in "$DEST"/*/; do
    name="${$(basename "$live")}"
    case "$name" in seedance*|videodirector|music-video-production-team|music-director|grok-i2v-batch-producer|jeongseon-video-typography)
      [ -d "$REPO_DIR/codex-skills/$name" ] || { echo "DRIFT: $name exists live but NOT in repo — deploy would delete it"; drift=1; };;
    esac
  done
  return $drift
}

if [ "${1:-}" = "--check" ]; then
  preflight_drift_check && echo "no drift: repo and live match" || exit 1
  exit 0
fi

if ! preflight_drift_check; then
  echo ""
  echo "REFUSING TO DEPLOY: live ~/.codex is ahead of / diverged from the repo."
  echo "Commit the live state into the repo first, then deploy."
  echo "Override only if you are certain: DEPLOY_FORCE=1 $0"
  [ "${DEPLOY_FORCE:-0}" = "1" ] || exit 1
  echo "DEPLOY_FORCE=1 set — proceeding despite drift."
fi
# --------------------------------------------------------------------------

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

# seedance-operations was referenced by team-policies but never deployed, so
# `seedance-operations/scene_advancement_policy_20260719.md` was a dead link at
# the deploy target. Ship it next to the policies that cite it. (2026-07-28)
rsync -a --delete "$REPO_DIR/seedance-operations/" "$POLICY_DEST/seedance-operations/"
echo "deployed: video-team-policies/seedance-operations"

echo "archived previous versions to: $ARCHIVE"
