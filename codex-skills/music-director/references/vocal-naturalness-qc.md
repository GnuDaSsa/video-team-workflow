# AI Vocal Naturalness QC

Use this checklist for every generated vocal candidate before calling it recommended, selected, locked, or ready for video editing.

## Statuses

- `PASS_VOCAL_NATURALNESS`: full-track playback completed and no conspicuous synthetic tell was heard.
- `HOLD_FOR_HUMAN_VOCAL_QC`: audio exists, but a qualified listener has not completed the playback gate.
- `REJECT_AI_VOCAL_ARTIFACT`: at least one obvious synthetic-vocal defect was heard.

Only the first status permits a recommendation. Composition, hook quality, intro duration, ASR accuracy, or mix polish cannot override a vocal rejection.

## User-rejected negative references

- `링크 업!`
- `리와인드 없는 오늘`

These names identify rejected generated performances, not genres to imitate. Never prompt toward, recommend, or reuse their vocal character. Use them only to calibrate the unacceptable level of AI-vocal obviousness.

## Pre-generation vocal contract

Put these requirements into every ordinary generated-vocal prompt before producing candidates:

- one stable native-Korean lead singer identity across the complete song;
- deliberate male or female lead selection, with neither treated as inherently more natural;
- clear conversational consonants, vowels, batchim, and phrase stress;
- natural phrase breathing and meaning-driven dynamic variation;
- restrained pitch correction, portamento, and vibrato;
- dry to moderately forward lead vocal that remains exposed enough to audit.

Default to one lead identity. Do not request mixed relay singers, persona/gender swaps, glossy choir stacks, whispered pickups, hums, sighs, chants, call-outs, or improvised ad-libs unless the creative brief truly needs them and each element will receive separate playback QC. Avoid overloading the prompt with “perfect,” “crystalline,” “ethereal,” “soaring,” or “ultra-polished” vocal adjectives and abrupt genre/persona changes. These commonly invite the exact synthetic gloss and identity drift this gate rejects.

Prompt prevention reduces risk; it cannot create a PASS. Generated audio must still complete the listening procedure below.

## Listening procedure

1. Play the complete song at normal speed through ordinary speakers or headphones. Do not decide from a contact sheet, waveform, transcript, or a few seconds of preview.
2. Recheck these points without effects masking when a dry vocal or separated stem is available:
   - intro and the moment before the first lyric;
   - first quiet verse line;
   - consonants and batchim in the densest Korean phrase;
   - verse/pre-chorus to chorus transition;
   - highest or longest held chorus note;
   - any harmony, chant, hum, sigh, or improvised ad-lib;
   - final chorus and last phrase/outro.
3. Compare all sections for the same singer identity: vocal weight, apparent age, gender presentation, resonance, accent, and mouth shape must not drift.
4. Record a status plus one short evidence note and timestamp. If a defect is obvious, stop scoring it as a recommendation and regenerate or replace it.

## Hard-fail defects

Reject when any of the following is conspicuous:

- metallic, buzzy, watery, hollow, phasey, or over-chorused formants;
- sudden changes in singer identity, apparent age, gender, accent, or vocal weight;
- Korean vowels melting together, consonants disappearing, broken batchim, invented syllables, or semantically correct lyrics pronounced as gibberish;
- syllable stress or duration that a fluent singer would not naturally choose;
- hard pitch snaps, identical repeated vibrato, robotic portamento, or a held note that changes throat/mouth identity mid-note;
- breaths copied like loops, impossible breath length, breath in the middle of a word, or no breath where the phrase requires one;
- every line delivered with the same pressure, volume, smile, anguish, or dramatic lift;
- synthetic sighs, whispers, hums, `ah` pickups, chants, call-outs, or ad-libs that were not compositionally required;
- lead and backing voices fusing into a glossy synthetic choir used to conceal an unstable lead;
- vocal fragments entering an explicitly instrumental intro.

## Natural target

- one stable singer identity across quiet and loud sections;
- intelligible, fluent Korean with believable consonant release and phrase stress;
- natural breathing and small dynamic changes tied to meaning;
- restrained tuning and vibrato rather than machine-perfect pitch motion;
- a clear lead vocal that remains credible when the arrangement becomes sparse;
- dry or moderately forward presentation by default, unless the brief specifically calls for a stylized effect.

Do not manufacture “humanity” by adding random breath noise, tape noise, distortion, lo-fi filtering, crowd layers, or excessive room reverb. Those are aesthetic choices, not proof of a natural performance.
