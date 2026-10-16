# Deferred video calibration — mode calibrations

This file preserves the corresponding Codex global video guidance. Read only when the current task needs this phase. Runtime rails/safety and the selected Seedance skill remain authoritative in their scopes.

## Video Agent Memory Routing — MV vs Public Contest — 2026-05-10

The user's video-agent history now has two distinct production contexts, but **music-first editing is a shared baseline**, not an MV-only feature. Do not blur project goals together, and separate mainly by typography/story-copy behavior and submission requirements.

### Shared baseline for all serious video work
Apply these rules to both MV and public-contest/institution videos unless the user explicitly overrides them.

Core priorities:
- Music comes first: analyze song/BGM structure, beat, phrase changes, hooks, accents, energy curve, cadence, and ending before final cut timing.
- Default cut density: use roughly **2.0–2.5 seconds per cut** unless the music or brief clearly calls for a different rhythm. Do not arbitrarily undercut the number of cuts for a 1-minute piece.
- Effects and transitions must be motivated by music, motion, story, or emotional emphasis; avoid random preset spectacle.
- Keep story physical and cinematic, but let rhythm drive cut timing and shot duration.
- For still-image production, use Codex `imagegen` / built-in `image_gen` by default; for I2V/videoization, use Grok/Runway/Seedance only after image QC; no raw stills delivered as clips.
- Imagegen production remains one cut = one standalone image; never request a production grid/contact sheet. Character/model sheets may be multi-panel design references only.
- QC must catch anatomical errors, disappearing limbs/people, repeated shots, bad crops, subtitle overlap, line clipping, weak narrative causality, jitter, freeze frames, and bad transition handles.
- (Post-production, not in this rail) CapCut JSON/coordinate edits are only helpers; actual CapCut preview is the source of truth for visual alignment, typography timing, and effect intensity.
- If a generated clip fails QC, regenerate or replace the block instead of presenting a weak final; there is no edit stage to hide it.

### Mode A: Music Video / MV typography and story memory
Use this mode when the user asks for 뮤직비디오, MV, 노래 기반 영상, 가사/비트/음악 중심 영상, review prototype, or a song-first project.

Typography/story behavior:
- Typography can be more lyrical, poetic, sparse, rhythmic, and emotionally timed; it does not always need to explain every visual literally.
- Text should support lyric hooks, repeated motifs, emotional turns, or chorus/bridge structure rather than becoming a public-information caption system.
- If a narrative exists, keep it cinematic and sensorial; let images, bodies, reflections, hands, shadows, and recurring motifs carry meaning.
- MV delivery (v5) includes QC-approved clips in storyboard order, audio, manifest, review contact sheet/keyframes, and notes. Masters/subtitled versions are post-production (not in this rail).

### Mode B: Public contest / tourism / institution typography and submission memory
Use this mode when the user asks for 공모전, 관광영상, 지자체/공공기관, 제출, 신청서, 유튜브 업로드, 메일 제출, 심사용 영상, or public-sector promotion.

Typography/story behavior:
- Story clarity beats pure mood: captions must explain why each motif exists and how it relates to the contest theme.
- Typography should be readable, restrained, culturally appropriate, and not a generic subtitle/presentation template.
- Do not assume a title/body structure from a prior project; design typography for the current story, footage, and contest brief.
- (Post-production, not in this rail) Caption/typography layers for contest masters; see `post-production-knowledge.md`.
- Public-sector copy must distinguish roles: title, chapter/location note, narration/body copy, final statement, AI-use disclosure, synopsis, and submission notes.
- Submission safety applies: verify official requirements and account/channel/recipient, prepare forms/copy packages carefully, and do not final-submit or publish without explicit user approval.
- Field-specific copy distinction is mandatory: 제작 의도, 시놉시스, AI 활용 내역, link/password notes, and prior-contest history must not be reused as the same paragraph.

### Memory routing rule
When the user approves a lesson during a project, save it under the appropriate bucket:
- music/cut/effect/QC basics → shared baseline;
- poetic lyric/title behavior → MV typography/story;
- explanatory public-sector captions, forms, upload, email, compliance → public contest/institution memory.

<!-- End deferred guidance -->
