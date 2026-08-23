# Awesome Suno Prompts index

Read this file first. Search before opening source files; load only the most relevant
1–3 files for the current brief.

## Genre routes

| Need | File |
|---|---|
| pop, ballad, synth-pop, teen/adult contemporary | `prompts/pop.md` |
| rock, grunge, punk, metal-adjacent | `prompts/rock.md` |
| hip-hop, trap, boom bap, drill, melodic rap | `prompts/hip-hop.md` |
| R&B, soul, neo-soul, slow jam | `prompts/rnb-soul.md` |
| EDM, house, trance, techno, dubstep, DnB | `prompts/edm.md` |
| indie, bedroom pop, shoegaze, dream pop, folk | `prompts/indie.md` |
| jazz, blues, swing, fusion | `prompts/jazz-blues.md` |
| country, bluegrass, outlaw, country rock | `prompts/country.md` |
| K-pop, hyperpop, idol performance, dance structure | `prompts/k-pop.md` |
| Afrobeats, Amapiano, Afro-house, Afro-fusion | `prompts/afrobeats.md` |
| phonk, drift phonk, gym/edit structures | `prompts/phonk.md` |
| Jersey/Baltimore club and dance-loop structures | `prompts/jersey-club.md` |
| regional Mexican, corridos, sierreño, banda | `prompts/regional-mexican.md` |

## Workflow routes

| Need | File |
|---|---|
| improve a vague prompt | `examples/before-after.md` |
| diagnose weak/generic generations | `examples/common-mistakes.md` |
| prompt layering and controlled hybrids | `examples/advanced-techniques.md` |
| analyze short-form/viral construction patterns | `examples/viral-hits.md` |
| structured JSON retrieval by use case | `packs/*.json` |
| dated trend discovery only | `TRENDING.md` |
| provenance and safety boundary | `SOURCE.md` |

## Retrieval recipe

1. Translate the brief into concrete search terms: genre, subgenre, mood, use case,
   groove, instrument, vocal profile, energy, BPM, and form.
2. Search headings and prompt bodies with `rg -n -i`.
3. Read 2–5 nearby patterns across at most three files.
4. Extract a single coherent Song DNA; do not concatenate prompts blindly.
5. Strip artist/song names and unsupported marketing claims from the final prompt.
6. Record the filenames/headings used in the answer or project evidence.

Example:

```bash
rg -n -i 'anime|k-pop|anthem|female vocals|150 BPM' prompts examples packs
```

## Output variables

- genre / subgenre / era-aesthetic
- BPM / meter / key or mode
- groove / drums / bass
- harmonic density / lead / texture
- vocal type, register, delivery, language
- form / section transitions / energy arc
- mix-space / production character
- intended use / target duration
- avoid list

The corpus is evidence for prompt patterns, not proof that its musical theory,
trend claims, exact durations, or model-version labels are correct.
