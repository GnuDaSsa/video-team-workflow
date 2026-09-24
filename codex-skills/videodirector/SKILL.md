---
name: "videodirector"
description: "Use for any video work: planning, MV/music video, promo and public-contest video, shortform/reels/shorts/trailers, storyboards, cut lists, scene breakdowns, character sheets, Codex imagegen styleframe prompts, Seedance/Grok image-to-video prompts, Suno music planning, narration and subtitle sheets, CapCut handoff. Trigger on Korean requests like 영상, 영상업무, 뮤직비디오, MV, 홍보영상, 공모전 영상, 숏폼, 콘티, 컷리스트, 장면 구성, 캐릭터시트, 나레이션, BGM, Suno, Seedance, CapCut. Kling only when explicitly requested."
---

# Video Director

Start the response with `[videodirector]` on its own line. This skill owns story, shot purpose, visual intent and delivery taste, **not** runtime execution procedure.

## Lean entry — classify before loading

1. Distinguish **advice/audit**, **one requested asset or revision**, and **new full production**. A question about the workflow is not a production job: do not initialize a project, open Runway, read all phase references, or create a new owner for it.
2. For an existing project, restore its `brief.md`, `state.json`, exact current blocker and `video-codex-runtime next --project <p>` before deciding the next action. Do not replay completed lanes or repeatedly dump the full state, transcript or wiki. For a new full project, initialize from the brief once, then follow `next` in the same owner.
3. Load only the reference for the **current** phase below. Reuse a document already read in this context unless its version or the phase changed. Read the selected Seedance version skill only when authoring or operating Seedance, not for every video question.
4. Give the first useful decision or artifact promptly. Briefly state chosen defaults when the request is workable but underspecified; ask about style, length or characters only when a missing answer truly blocks production. Never replace actual media/QC evidence with a plan.

JEV-style advisory classification is **not** a default startup step. Aside's JEV is optional for genuinely ambiguous next-action or mixed QC notes; importing an extra model call into every Codex step adds latency and does not authorize execution. Do not invoke an external agent/classifier without the applicable explicit approval, and never let advice bypass runtime gates.

## Mode and spine

| Mode | Timing source | Extra obligation |
|---|---|---|
| MV/music | Actual song and listening | Beat/phrase cut map, lyric hierarchy, no stills in the edit |
| Promo/public contest/institution | Requested narration/VO or approved visual-only scope | Story clarity, factual safety, AI-use and submission package |
| Shortform/reels/trailer | Hook and reading rhythm | Opening hook, vertical-safe composition |

Full production follows direction → applicable audio spine → cut map → character/style lock → production blueprint → images/QC → video/QC → CapCut edit → package. The runtime's explicit visual-only exception, not this skill, decides when audio may be deferred. A one-asset request still respects its dependent gates but does not silently enlarge into an entire film.

## Tool and authority boundaries

- Stills, start frames and character sheets: built-in Codex `image_gen` after the Gongnyang `image-prompt` compiler. Production is one cut = one prompt = one standalone image; character triptychs are identity-design exceptions. Never use Grok for stills by default.
- Video: Seedance by default; Grok only when named for that project, Kling only when explicitly requested. Follow exactly one selected Seedance version skill for prompt/UI/queue procedure.
- Edit: CapCut is the editable handoff; `ffmpeg` is for QC, normalization and previews, not a substitute final draft. Verify real CapCut playback and export.
- Runtime rails, lane order, duration, media registry and safety: `/Users/gnudas/Documents/Codex/video-team-runtime/AGENTS.md`. Spawn approval and browser operator policy: `~/.codex/video-team-policies/`. Default is one owner, sequential; no unapproved agent, sidecar, scheduler or second browser loop.
- A prompt, status string, attestation or provider card is not finished media. Confirm file/path/size/codec/duration and visual/audio QC appropriate to the deliverable.

## Read only when the phase needs it

| Work now | Reference |
|---|---|
| MV vs public contest details | `references/modes.md` |
| Accepted mode-specific video memory | `references/mode-calibrations.md` only for the relevant MV/public phase |
| Song-first MV production/QC | `references/mv-production-calibrations.md` |
| Recurring character identity lock | `references/character-identity-calibrations.md` |
| Typography, captions, CapCut alignment or transition QC | `references/typography-calibrations.md` |
| Production or revision hard rules | `references/production-rules.md` |
| Deliverable layout/manifest | `references/output-formats.md` |
| Accepted user typography and packaging taste | `references/user-calibrations.md` |
| Optional named-role split after approval | `references/role-split.md` |
| Shinkai/anime appearance or noisy stills | `/Users/gnudas/wiki/concepts/shinkai-style-anti-noise-image-prompting.md` |
| Storyboard, blocking, shot board | `/Users/gnudas/wiki/concepts/storyboard-production-blueprint-standard.md` |
| Camera distance/angle | `/Users/gnudas/wiki/concepts/ai-image-composition-distance-angle.md` |
| Phone/screen geometry | `/Users/gnudas/wiki/concepts/phone-screen-geometry-qc.md` |
| Character bible or photoreal casting | `/Users/gnudas/wiki/concepts/character-bible-page-prompt-standard.md`; for photoreal people also `live-action-character-authenticity-casting-standard.md` |
| Broken I2V motion/crop/style | `/Users/gnudas/wiki/concepts/video-image-qc-style-continuity.md` |

For live action, read matching sections of `/Users/gnudas/wiki/concepts/video-prompting-live-action.md` before planning/image authoring/QC, not the whole wiki. `툰킷 문법` activates `toonkit_2d_snappy_v1` only for the named 2D/stylized blocks; the selected Seedance skill owns the actual prompt grammar. Plan and explain in Korean; Seedance prompts are Korean unless an explicit project exception applies.

Default to no-question execution within the authorized scope. Stop for login, payment, CAPTCHA, account choice, sensitive upload/deletion, public publish/submission or an explicit review gate. Mark failed media honestly and repair it; never present a weak draft as final.
