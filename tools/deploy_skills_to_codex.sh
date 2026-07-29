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
# Only DESTRUCTIVE drift blocks: a file that exists live but not in the repo is
# deleted by --delete and is gone. Content differences are expected — deploying
# repo->live is the whole point, and the previous version is archived first.
preflight_drift_check() {
  destructive=0
  for live in "$DEST"/*/; do
    name="${$(basename "$live")}"
    case "$name" in
      seedance*|videodirector|music-video-production-team|music-director|grok-i2v-batch-producer|jeongseon-video-typography) ;;
      *) continue ;;
    esac
    if [ ! -d "$REPO_DIR/codex-skills/$name" ]; then
      echo "WOULD DELETE: skill '$name' exists live but not in the repo"
      destructive=1
      continue
    fi
    # files present live, absent in repo
    orphans="$(cd "$live" && find . -type f | while read -r f; do
        [ -e "$REPO_DIR/codex-skills/$name/$f" ] || echo "$f"; done)"
    if [ -n "$orphans" ]; then
      echo "WOULD DELETE: files in '$name' exist live but not in the repo:"
      echo "$orphans" | sed 's|^\./|       |'
      destructive=1
    fi
    if ! diff -rq "$REPO_DIR/codex-skills/$name" "$live" >/dev/null 2>&1; then
      echo "note: '$name' content differs (expected when deploying repo -> live)"
    fi
  done
  return $destructive
}

if [ "${1:-}" = "--check" ]; then
  if preflight_drift_check; then
    echo "safe to deploy: nothing live would be destroyed"
    exit 0
  fi
  exit 1
fi

if ! preflight_drift_check; then
  echo ""
  echo "REFUSING TO DEPLOY: the listed live files are not in the repo and"
  echo "'rsync --delete' would destroy them. Commit them first, then deploy."
  echo "Override only if you truly want them gone: DEPLOY_FORCE=1 $0"
  [ "${DEPLOY_FORCE:-0}" = "1" ] || exit 1
  echo "DEPLOY_FORCE=1 set — proceeding, live-only files will be deleted."
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

# The two rulebooks that decide behaviour were not deployed by this script, so
# "deploy" only ever synced half the rules and left the runtime contradicting
# the skills. Ship them too, archiving each first. (2026-07-28)
deploy_file() {
  src="$1"; dst="$2"
  [ -f "$src" ] || { echo "skip (missing in repo): $src"; return 0; }
  if [ -f "$dst" ]; then
    mkdir -p "$ARCHIVE"
    cp "$dst" "$ARCHIVE/$(basename "$dst").$(echo "$dst" | tr '/' '_')"
  fi
  mkdir -p "$(dirname "$dst")"
  cp "$src" "$dst"
  echo "deployed: $dst"
}

deploy_file "$REPO_DIR/GLOBAL_AGENTS.md" "$HOME/.codex/AGENTS.md"
deploy_file "$REPO_DIR/runtime/AGENTS.md" "$HOME/Documents/Codex/video-team-runtime/AGENTS.md"
deploy_file "$REPO_DIR/references/character_sheet_prompt_standard.md" \
            "$HOME/Documents/Codex/video-team-runtime/runtime/references/character_sheet_prompt_standard.md"
deploy_file "$REPO_DIR/wiki-extract/character-bible-page-prompt-standard.md" \
            "$HOME/wiki/concepts/character-bible-page-prompt-standard.md"

echo "archived previous versions to: $ARCHIVE"
