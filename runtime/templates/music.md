# Music — 한 작업자의 음악 잠금 단계

Read project brief/state, Director intent and existing candidate/lock evidence.
Music decides song form, lyrics, style, vocal direction and candidate variants;
Director supplies purpose, tone, duration and constraints, not a finished song.
Read `/Users/gnudas/.codex/skills/music-director/SKILL.md`; retrieve only the
relevant 1–3 source files. Record sources actually read and decisions derived.

- Vocal/MV/anime OP/ED work uses actual structured lyrics and a separate Style
  field in Advanced/Custom. Instrumental work may use Simple + Instrumental ON;
  never force instrumental/Simple onto a vocal brief.
- Reuse a user-approved, provenance-verified existing track when applicable.
  For new music use the user's real Suno session through Codex Computer Use.
  No procedural/local placeholder may masquerade as final Suno audio.
- Generate a bounded candidate set, download via the visible card/list menu,
  verify real files, and present TOP1–3 with concrete selection reasons.
  `NOT_LOCKED_PENDING_USER_APPROVAL`: Planner waits for selection. An unambiguous
  user choice locks that candidate without a redundant confirmation.
- Ingest audio into `media/02_audio_음악/`, register the selected asset as `locked`.
  `manifest.music` must name `status: LOCKED` and its `asset_id`; record exact
  path, SHA-256, bytes, duration, codec, provenance and user selection evidence.
  A status string or empty `music_lock.md` is not a lock.
- Listen and map sections, BPM/beat uncertainty, phrases, hooks, accents,
  energy and ending. Do not pretend an estimated BPM is measured precisely.
- Give Planner a rhythm map and reading-breath constraints, not a fixed cut
  count detached from the track. Keep MV and public-information copy distinct.
- Login/CAPTCHA/payment/account/permission blocks stop the affected operation
  with the exact required user action. Do not start a relay or another agent.

Outputs under `lanes/music/`: `music_direction.md`, `suno_prompt_pack.md` when
new music is needed, `candidate_proposal.md`, `music_lock.md`, rhythm map,
`logs/music_skill_evidence.md`, `status.json`, `result.md`. Media stays in media/.
