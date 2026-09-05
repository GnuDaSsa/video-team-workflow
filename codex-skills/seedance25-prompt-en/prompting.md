# Seedance 2.5 prompting branch

Use this document only after the version gate in `SKILL.md` selects 2.5. This
branch authors and critiques the package; it never opens Runway.

## Capability envelope, not a promise

Current first-party documentation describes Reference, Keyframe, Edit, and
Extend workflows, 4–30 second generation, 480p/720p/1080p output, and a combined
multi-reference ceiling of up to 50 inputs. ByteDance describes that ceiling as
up to 30 images, 10 videos, and 10 audio files. Treat these numbers as provider
ceilings, not targets: the visible Runway surface and current account state are
the operational truth.

More inputs do not automatically improve consistency. Use the **minimum
sufficient deck** that proves identity, wardrobe, location, object, motion, or
audio roles without asking the model to reconcile competing authorities.

## Choose the mode from the actual problem

| Need | Preferred branch | Prompt consequence |
|---|---|---|
| identity/style/location continuity from several sources | **Reference** | bind each source to one narrow visible function |
| controlled start/end composition or transformation | **Keyframe** | describe the physical bridge and invariant elements between endpoints |
| localized repair of an otherwise useful clip | **Edit** | name the region/event to change and explicitly preserve everything else |
| continue motion, action, or camera beyond an approved clip | **Extend** | inherit the last state and describe only the next causal beat |

Do not use Reference as a universal default. If exact endpoints are the real
constraint, use Keyframe; if most of a clip already works, use Edit rather than
regenerating the whole shot.

## Reference-role compiler

For every attached source, write one role in both the package and the visible
Korean prompt:

```text
@Image1은 주인공 얼굴·머리 실루엣·연령 인상의 유일한 기준이다.
@Image2는 의상 앞·뒤 구조와 색 배치만 고정한다.
@Video1은 달리는 속도가 아니라 발 착지와 체중 이동의 리듬만 참고한다.
@Audio1은 대사의 발화 타이밍과 억양만 따른다.
```

- Attachment order is not story order.
- One source must not own two contradictory jobs.
- The approved triptych or minimum deterministic crop remains mandatory for a
  recurring character; scene memory and a previous card do not replace it.
- Do not import panel seams, gray identity-sheet backgrounds, absent front
  heads, watermarks, captions, UI, or source defects into the scene.
- When sources disagree, name the authority per attribute instead of saying
  “combine all references.”

## Anti-AI motion contract

The prompt must describe observable mechanics, not quality adjectives. Compile
each planned scene in this order:

1. **Readable opening state** — pose, balance, gaze, contact points, and what is
   already moving.
2. **Anticipation** — a small weight shift, breath, recoil, eye lead, hand set,
   or other visible preparation.
3. **Primary action** — one dominant action with direction, speed curve, body
   mechanics, and exact subject/object contact.
4. **Reaction and environment** — cloth, hair, dust, water, foliage, shadow, or
   another layer responds after the cause, not all at once.
5. **Settle and end state** — overshoot only when motivated, then a readable
   held state that an editor can cut on.
6. **Camera path** — one motivated route with speed and stop behavior; it
   supports the action instead of competing with it.

Avoid vague bundles such as “dynamic cinematic animation, dramatic camera,
high quality, smooth motion.” Replace each with a visible event. Preserve quiet
holds: constant whole-frame motion is a common source of synthetic drift.

## 2D and stylized animation

For animation that currently feels cheap or generically AI-made, specify the
animation timing itself:

- Name the opening key pose, anticipation pose, action key, contact pose,
  overshoot/settle, and final held pose when the beat needs them.
- Put speed in **spacing**: short hold → compressed anticipation → two or three
  fast action beats → settle. Do not demand uniform smoothness everywhere.
- Keep face proportions, hand count, costume shapes, line weight, shadow logic,
  and color regions stable across the shot.
- Use smear, speed lines, impact frames, camera shake, and debris only at a
  motivated accent; one accent family per beat is usually enough.
- Let background parallax follow the camera. Do not animate every background
  object independently.
- For a fragile close-up, lock the crop and permit only the necessary micro-
  movement. A full-face reveal from an eye or mouth crop is a failure.

If the user explicitly enables `toonkit_2d_snappy_v1`, apply its pose-to-pose
hold/anticipation/action/overshoot/settle/follow-through grammar from the 2.0
creative adapter, but keep this 2.5 mode/reference/timestamp contract.

## Timeline beats

Timestamps are pacing guidance, not frame-accurate promises. Use contiguous,
feasible intervals that match the project duration lock. Example structure for
a 15-second planned source:

```text
0.0–2.5초: 시작 자세와 시선 고정, 호흡만 보인다.
2.5–5.0초: 오른발에 체중을 싣고 손이 문고리를 잡는다.
5.0–9.0초: 몸통이 먼저 회전하며 문을 밀고, 소매는 한 박자 늦게 따라온다.
9.0–12.5초: 문이 벽에 닿기 직전 감속하고 먼지가 뒤늦게 흔들린다.
12.5–15.0초: 인물과 카메라가 멈춘 최종 구도를 유지한다.
```

Do not overfill a duration merely because 2.5 accepts longer generations.
Unrelated scenes stay separate. A planned multi-shot source may contain 2–4
causally connected cuts only when the project cut-ownership and duration locks
already authorize it.

## Korean model-facing prompt shape

Write natural Korean, not package keys. Use the smallest set of sections that
changes the model's behavior:

```text
[결과와 샷 의도]
[참조 역할]
[시작 상태와 물리 동작]
[시간대별 비트]
[카메라와 공간 반응]
[스타일·정체성·구도 불변 조건]
[현장음/대사/음악 역할]
[마지막 유지 구도]
```

Use positive proof constraints first. Add a short forbidden clause only for a
known high-risk failure that cannot be stated positively. Never paste workflow
terms, file paths, hashes, package keys, safety notes, or critic commentary into
the model-facing prompt.

## Package and critic gate

The handoff package must include at least:

```yaml
provider_model: Seedance 2.5
provider_skill: seedance25-prompt-en
provider_mode: Reference | Keyframe | Edit | Extend
duration_sec: <project-lock value>
resolution: 480p | 720p | 1080p
reference_roles: <ordered slot-to-role map>
prompt_rules_used: <only the rules actually applied>
revision_target: <one diagnosed variable, or null>
```

Before handoff, reject the package if any answer is “no”:

- Does each reference have one explicit, non-conflicting job?
- Is the primary action physically possible from the starting pose?
- Are anticipation, contact/causality, reaction, and settle visible where the
  action requires them?
- Is there one readable camera path and an editor-usable end state?
- For 2D/stylized work, are pose timing and line/style stability stated rather
  than replaced with “smooth/high quality” adjectives?
- Do all timestamp intervals fit the locked duration without overlap or gaps?
- Does the package explicitly name Seedance 2.5 and the selected mode?

On a failed generated clip, diagnose the failure class and change one primary
variable: source frame, reference role, mode, motion beat, camera path, or local
Edit instruction. Do not append a large negative list to the same prompt.
