# Video team native kanban

User requests an independently built small window in the desktop upper-left, not Hermes. Implement a read-only AppKit panel over current runtime state. No agent, scheduler, provider control, public server or Hermes dependency. Closing the window stops refresh; no login item. Production intake opens the one app via the canonical director entry; repeated opens reuse it. Cards distinguish recorded status from live provider truth and stale/conflicting records. No drag-to-complete or fabricated progress. Verify parser tests, Swift compile, actual GUI placement/content, refresh and collapse. Deploy through a dedicated scoped installer without replacing unrelated workflow edits.

Acceptance complete: 236 isolated tests PASS; Swift build and native GUI verified. See docs/releases/2026-10-08-video-team-board.md.

Waiting tracking: separate WAITING/QUEUED column, explicit wait reason and timestamp provenance. Show elapsed from waiting_since/wait_started_at only when present; otherwise label time since latest record, never invent a start. Preserve unresolved waits beyond 24h with stale warning. Latest non-waiting/terminal record removes wait. Read-only; no new scheduling or provider requests.
