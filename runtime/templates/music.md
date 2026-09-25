# Music — Suno generation boundary

Read the project brief/state and Director intent. Music owns the pre-generation
song form, lyrics, Style, vocal direction, and a bounded generation set. Director
supplies purpose, tone, duration, and constraints, not a finished song.
Read `/Users/gnudas/.codex/skills/music-director/SKILL.md`; retrieve only the
relevant 1–3 source files and record the decisions derived from them.

- Vocal/MV/anime OP/ED work uses actual structured lyrics and a separate Style
  field in Advanced/Custom. Instrumental work may use Simple + Instrumental ON;
  never force instrumental/Simple onto a vocal brief.
- If the user already supplies an approved track, skip Suno generation and
  route that file to the separately requested video audio handoff. For new
  music, use the user's real Suno session through Codex Computer Use; no
  procedural/local placeholder may masquerade as Suno audio.
- Generate only the bounded set requested or justified by the brief. Record
  each generated song ID/link, prompt/settings, and visible completion state.
  Stop here. The user alone chooses and downloads. Do not open Download,
  export files, buy download credits, listen to/rank/recommend generated songs,
  select TOP candidates, ingest audio, or claim Music Lock from generation.
- Set `lanes/music/status.json` to `PENDING_USER_AUDIO` with a concise handoff
  detail, keep `manifest.music.status=NOT_LOCKED`, and write `result.md` with
  generation evidence and the exact user action: choose/download a song and
  provide the file in a separate follow-up if video work should continue.
  Do not mark the Music lane DONE or advance Planner on a generated link.
- The existing registered-audio Music Lock gate still applies to subsequent
  video work. A separately requested downstream handoff may use a file the
  user supplies; it does not retroactively authorize Music Director to
  download, evaluate, recommend, or select Suno candidates.
- Login/CAPTCHA/payment/account/permission blocks stop the affected operation
  with the exact required user action. Do not start a relay or another agent.

Outputs under `lanes/music/`: `music_direction.md`, `suno_prompt_pack.md` when
new music is needed, `generation_receipt.md` (IDs/links/settings, no fabricated
file metadata), `status.json`, and `result.md`. No audio asset or Music Lock is
claimed at this stage.
