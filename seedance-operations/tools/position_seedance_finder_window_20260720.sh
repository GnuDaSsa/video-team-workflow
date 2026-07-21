#!/usr/bin/env bash
set -euo pipefail
folder="${1:?upload_staging folder required}"
osascript <<OSA
tell application "Finder"
  activate
  close every window
  open POSIX file "$folder"
  delay 0.8
  set current view of front window to icon view
  -- Finder can re-tile a newly opened window after the first bounds write.
  -- Apply the placement twice, with activation between writes, then verify.
  repeat 2 times
    activate
    set bounds of front window to {780, 105, 1230, 505}
    delay 0.35
  end repeat
  if (bounds of front window) is not {780, 105, 1230, 505} then
    set bounds of front window to {780, 105, 1230, 505}
  end if
end tell
OSA
