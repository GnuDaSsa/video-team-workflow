# Source links and design notes

Snapshot: 2026-05-01.

## Primary DCInside thread

- Source post: https://gall.dcinside.com/mgallery/board/view/?id=thesingularity&no=1149918&exception_mode=recommend
- Title: "에이전트가 작곡 전문적으로 잘 하게 만드는 스킬 만듬"
- Key takeaways, paraphrased:
  - Current LLMs may have strong general knowledge but need structured craft workflow and references, like good ingredients needing a recipe book.
  - The linked skill reports two author benchmarks where the skill-assisted agent outperformed the baseline: system-prompt injection blind comparison and native lazy-loading use.
  - Although framed as composition, the author expects it to improve AI help across broader music tasks.

Related DCInside chain:

- https://gall.dcinside.com/mgallery/board/view/?id=thesingularity&no=1149642 — points to the earlier test/demo chain.
- https://gall.dcinside.com/mgallery/board/view/?id=thesingularity&no=1148973 — initial note linking the same GitHub repository and describing it as a practical wiki/cheatsheet-like workflow aid.

## Main linked repository

- Repository: https://github.com/SJY051/music-composition
- Local install: `../music-composition-source/`
- Purpose: modular AI music-composition skill covering harmony, melody, form, rhythm, arrangement, orchestration, genre-aware writing, critique, teaching, research, and reference-track workflows.
- Current release seen on GitHub: v1.0, release date 2026-04-27.
- Core workflow to preserve:
  1. Start from `SKILL.md`.
  2. Use `references/00-navigation.md`.
  3. Load only the relevant 1–3 reference files.
  4. Produce concrete musical decisions.
  5. Explain why they work.
  6. Offer a few next-step options.

## Other internal/external links surfaced from the page/repo context

- https://github.com/bitwize-music-studio/claude-ai-music-skills — full album / Suno-oriented music production pipeline with lyric, prompt, mastering, release-prep, research, and quality gates. Use as inspiration for staged workflow and QA gates, not as a dependency.
- https://github.com/tubone24/midi-agent-skill — text-to-MIDI generation skill with Python scripts, General MIDI instruments, and optional WAV conversion. Use as a potential handoff target when the user wants generated MIDI/audio files.
- https://github.com/mikecfisher/ableton-lom-skill — Ableton Live Object Model reference for Remote Script / Live automation work. Use as a handoff reference only for Ableton scripting/automation tasks.
- https://github.com/openclaw/skills/blob/main/skills/danbennettuk/voice-note-to-midi/SKILL.md — voice/humming audio to quantized MIDI workflow using pitch detection and cleanup. Use as a handoff concept when the user has humming/voice memo material.
