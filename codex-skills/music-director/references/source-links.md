# Source links and design notes

Updated: 2026-08-24.

## Primary Suno prompt corpus

- Repository: https://github.com/naqashmunir21/awesome-suno-prompts
- Bundled path: `awesome-suno-prompts/`
- Snapshot commit: `9d01635fe72ebb4a37ce29153f7bea026f1566fe`
- Upstream commit date: 2026-07-22
- License: CC0-1.0
- Role: first-choice retrieval corpus for Suno style prompts, genre/subgenre patterns, prompt debugging examples, use-case packs, and a dated trend-discovery list.
- Safety boundary: upstream may use artist/song names and marketing claims. Use names only to locate patterns, strip them from final prompts, and never repeat claims of guaranteed copyright bypass, virality, chart quality, or exact model behavior.
- Freshness boundary: bundled `TRENDING.md` is a snapshot, not live chart evidence. Browse upstream/current primary sources when the answer depends on what is current.

The bundled selection intentionally excludes repository promotion/community/web-image files. See `awesome-suno-prompts/SOURCE.md` for the exact included paths.

## Secondary composition-theory source

### Original discussion

- Source post: https://gall.dcinside.com/mgallery/board/view/?id=thesingularity&no=1149918&exception_mode=recommend
- Title: "에이전트가 작곡 전문적으로 잘 하게 만드는 스킬 만듬"
- Key takeaways, paraphrased:
  - Current LLMs may have strong general knowledge but need structured craft workflow and references, like good ingredients needing a recipe book.
  - The linked skill reports two author benchmarks where the skill-assisted agent outperformed the baseline: system-prompt injection blind comparison and native lazy-loading use.
  - Although framed as composition, the author expects it to improve AI help across broader music tasks.

Related DCInside chain:

- https://gall.dcinside.com/mgallery/board/view/?id=thesingularity&no=1149642 — points to the earlier test/demo chain.
- https://gall.dcinside.com/mgallery/board/view/?id=thesingularity&no=1148973 — initial note linking the same GitHub repository and describing it as a practical wiki/cheatsheet-like workflow aid.

### Older linked repository

- Repository: https://github.com/SJY051/music-composition
- Local install: `../music-composition-source/`
- Purpose: secondary modular composition reference covering harmony, melody, form, rhythm, arrangement, orchestration, critique, teaching, and reference-track workflows. It is no longer the default Suno prompt corpus.
- Current release seen on GitHub: v1.0, release date 2026-04-27.
- Theory workflow to preserve when that source is needed:
  1. Start from `SKILL.md`.
  2. Use `references/00-navigation.md`.
  3. Load only the relevant 1–3 reference files.
  4. Produce concrete musical decisions.
  5. Explain why they work.
  6. Offer a few next-step options.

### Other handoff references

- https://github.com/bitwize-music-studio/claude-ai-music-skills — full album / Suno-oriented music production pipeline with lyric, prompt, mastering, release-prep, research, and quality gates. Use as inspiration for staged workflow and QA gates, not as a dependency.
- https://github.com/tubone24/midi-agent-skill — text-to-MIDI generation skill with Python scripts, General MIDI instruments, and optional WAV conversion. Use as a potential handoff target when the user wants generated MIDI/audio files.
- https://github.com/mikecfisher/ableton-lom-skill — Ableton Live Object Model reference for Remote Script / Live automation work. Use as a handoff reference only for Ableton scripting/automation tasks.
- https://github.com/openclaw/skills/blob/main/skills/danbennettuk/voice-note-to-midi/SKILL.md — voice/humming audio to quantized MIDI workflow using pitch detection and cleanup. Use as a handoff concept when the user has humming/voice memo material.
