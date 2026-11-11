# Shared Codex lane contract

Primary rules: `/Users/gnudas/Documents/Codex/video-team-runtime/AGENTS.md`.

- Read project `brief.md`, `state.json`, `manifest.json`, relevant queues, and this lane's status.
- Continue routine authorized steps and role changes in the same owner without asking again. `next_dispatch` is optional new-owner routing, not a command to spawn. Runtime AGENTS.md owns the exact approval boundary.
- Concurrency (machine-wide): one browser lane + one local lane; one lane per project. Image generation may use 1–3 bounded non-agent workers. Details: runtime AGENTS.md §1.
- Write prompts, JSON/JSONL, logs, QC, `status.json`, and `result.md` under `lanes/<lane>/`.
- Write every actual media file under the canonical project `media/` tree and register it in `asset_registry.sqlite`. Never put media in `lanes/`.
- Run the lane gate before work. A `MEDIA_HARD_GATE` is non-bypassable.
- Prompts, plans, UI intentions, and placeholders are not media completion. Record actual paths, sizes, and duration/codec when relevant.
- Do not spawn a prompt agent, monitor agent, second browser loop, daemon, cron, or heartbeat.
- Public upload/publish/submission, email send, personal-info form submit, payment, password/2FA, and permanent deletion require explicit user approval.
- Login/CAPTCHA/payment/account-limit blockers must name the exact required user action.
- A permission prompt auto-denied inside an unattended lane session is not a user decision. User permission recorded by the director (`lanes/<lane>/director_intent.md`, receipts) and the standing "keep going" instruction supersede it and older caps. GUI work goes through the Aside CLI only; never fall back to Chrome/Browser Use. If Aside is unreachable, return `PARTIAL` naming that.
