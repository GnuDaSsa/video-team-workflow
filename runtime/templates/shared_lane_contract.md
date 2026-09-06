# Shared Codex lane contract

Primary rules: `/Users/gnudas/Documents/Codex/video-team-runtime/AGENTS.md`.

- Read project `brief.md`, `state.json`, `manifest.json`, relevant queues, and this lane's status.
- Continue routine authorized steps and role changes in the same owner without asking again. `next_dispatch` is optional new-owner routing, not a command to spawn. Runtime AGENTS.md owns the exact approval boundary.
- Only one production lane runs at a time. The sole concurrency exception is 1–3 bounded image-generation workers inside the active Image Creator lane.
- Write prompts, JSON/JSONL, logs, QC, `status.json`, and `result.md` under `lanes/<lane>/`.
- Write every actual media file under the canonical project `media/` tree and register it in `asset_registry.sqlite`. Never put media in `lanes/`.
- Run the lane gate before work. A `MEDIA_HARD_GATE` is non-bypassable.
- Prompts, plans, UI intentions, and placeholders are not media completion. Record actual paths, sizes, and duration/codec when relevant.
- Do not spawn a prompt agent, monitor agent, second browser loop, daemon, cron, or heartbeat.
- Public upload/publish/submission, email send, personal-info form submit, payment, password/2FA, and permanent deletion require explicit user approval.
- Login/CAPTCHA/payment/permission/account-limit blockers must name the exact required user action.
