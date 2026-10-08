# Video Team Board

Independent, read-only macOS AppKit floating panel. No Hermes, server, agent,
provider control, login item, or scheduler. Initial frame: upper-left of main
screen; draggable/resizable, collapsible, close to terminate refresh.

## Install / open

From this repository: `python3 tools/install_video_board.py`.
Open: `~/.local/bin/video-team-board --project <absolute-runtime-project>`.
Registered production runtime `init` and `next` open/reuse it automatically.
Set `VIDEO_TEAM_BOARD_DISABLED=1` on runtime calls to suppress the panel.
Advice/audits do not open it. Existing app/launcher are archived before replacement.

## Data contract

Every five seconds, bounded local reads project ten production lanes into four
columns. Newer embedded timestamps win; conflicts and stale/missing timestamps
remain visible. Queue counts are saved records, not a live Runway observation.
Native automation configuration is read-only; ACTIVE is not execution proof.
No credentials, prompts, or private account URLs are exported to the panel.
No drag-to-complete: status changes belong to the workflow's existing evidence
writers. This panel neither fixes nor independently executes production.

## Verification

`VIDEO_TEAM_BOARD_DISABLED=1 python3 -m unittest discover -s runtime/tests -v`
The installer compiles Swift and signs the local app. Native GUI acceptance:
project selection, automatic refresh, details, collapse/expand, close, and reopen.
