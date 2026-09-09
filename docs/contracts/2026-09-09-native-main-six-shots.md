# Native main-window proof and explicit six-shot request

User requests actual production and six 2.5-second scenes in 15 seconds.
Native read-only evidence showed window 1 was auxiliary and the unique AXMain
browser window owned the open panel. Preserve exact browser window ID/URL
proof, then require one AXMain window and its open-panel. No bypass of IME,
permission or session gates. Picker-select layout assumptions remain unchanged.

Allow six scenes only for Seedance 2.5 with recorded user_requested_scene_count=6;
this is manual user-intent metadata, not automatic authorization detection.
Default 2-4 and existing duration, min-shot, continuity, binding checks remain.
No guarantee of frame-accurate generation timing.

155 tests PASS; release freeze/preflight/apply/check PASS (66-file parity).
Live guard progressed beyond main-window error to IME stop; native CUA file-open
subsequently uploaded six refs and OP02 generation was accepted. No full playback
QC or general all-layout repair is claimed. No new operator/scheduler.
