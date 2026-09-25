# Vocal prompt guardrails (pre-generation only)

This retained reference informs Suno prompt writing before Generate. It is not a listening, download, candidate-ranking, selection, or Music Lock procedure. The music director stops after generation; the user chooses and downloads.

## User-rejected negative examples

The generated vocal performances in `링크 업!` and `리와인드 없는 오늘` were rejected as conspicuously artificial. Do not use their sound as a vocal target. Their names are not artist/style tags to put in a Suno prompt.

## Prompt contract

- Specify one stable native-Korean lead identity across the song. Choose male or female deliberately; neither is inherently more natural.
- Request conversational consonants and vowels, intelligible batchim, meaning-led phrase stress, believable breathing, and small dynamic changes.
- Request restrained pitch correction and vibrato; keep the lead dry to moderately forward so it is not hidden behind glossy choir layers.
- Avoid mixed relay singers, persona/gender switches, whispered pickups, hums, sighs, chants, call-outs, or improvised ad-libs unless the brief genuinely needs them.
- Avoid stacked “perfect,” “crystalline,” “ethereal,” “soaring,” or “ultra-polished” vocal adjectives and abrupt genre/persona changes.
- If the brief requires an instrumental intro, specify no vocal or non-lexical pickup before the first intended lyric.

These directions reduce known prompt risks but cannot prove the generated audio sounds natural. Do not assert a playback verdict from text, metadata, waveform, or UI settings. After generation, return the song IDs/links and stop for the user's own choice and download.
