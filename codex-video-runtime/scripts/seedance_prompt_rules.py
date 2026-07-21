#!/usr/bin/env python3
"""Select Seedance prompting rules from the user's LLM Wiki.

Usage:
  python3 seedance_prompt_rules.py --project <project> --block B10

Reads:
- ~/.codex/skills/seedance-prompt-en/SKILL.md (mandatory)
- ~/wiki/concepts/seedance-prompting-knowledge.md
- project queues/seedance_block_queue.jsonl

Writes:
- lanes/seedance/prompts/<BLOCK>_prompt_rules_used.md

This is intentionally simple and deterministic: it does not generate the final prompt;
it retrieves the relevant production rules that Toji/Planner must apply.
"""
from __future__ import annotations
import argparse, json, re
from pathlib import Path
import os

WIKI = Path(os.environ.get("VIDEO_TEAM_SEEDANCE_WIKI", str(Path.home() / "wiki" / "concepts" / "seedance-prompting-knowledge.md")))
SEEDANCE_SKILL = Path(os.environ.get("VIDEO_TEAM_SEEDANCE_SKILL", str(Path.home() / ".codex" / "skills" / "seedance-prompt-en" / "SKILL.md")))

RULES = {
    'identity_closeup': ['close-up', 'eye', 'face', 'profile', 'identity', 'heroine'],
    'kinetic_tracking': ['run', 'running', 'stairs', 'sprint', 'kinetic', 'chase'],
    'memory_interior': ['memory', 'classroom', 'interior', 'room', 'reflection'],
    'object_motif': ['lantern', 'charm', 'wrist', 'compass', 'prop', 'motif', 'macro'],
    'transition_abstract': ['abstract', 'transformation', 'bird', 'streak', 'flare', 'transition'],
    'multi_shot': ['multi-reference', 'ordered', 'beats', 'sequence'],
    'final_hold': ['final', 'fade', 'hold', 'closure'],
    'scenic_character_sheet_intro': ['character sheet', 'model sheet', 'reference sheet', '소개', 'introduction', 'full reveal'],
    'scenic_product_ad_arc': ['ad', 'advertisement', 'commercial', 'product', 'hero shot', 'juice', 'brand'],
}

RULE_TEXT = {
    'identity_closeup': 'Identity/close-up: preserve face, hairstyle, costume, crop; micro-motion only; no zoom-out, no new facial structure.',
    'kinetic_tracking': 'Kinetic: use explicit tracking/side/back camera, moderate motion, stable body anatomy, preserve ground/location continuity.',
    'memory_interior': 'Memory/interior: assign environment reference role; slow dolly/rack focus; do not let room reference overwrite heroine identity.',
    'object_motif': 'Object/motif: assign prop reference role; specify whether the object may glow/transform; no new unrelated props.',
    'transition_abstract': 'Abstract/transition: state metaphorical vs literal; prevent unwanted substitutions such as real animals or new objects.',
    'multi_shot': 'Multi-shot: state duration/aspect/shot count upfront; enumerate Beat 1..N in exact reference order; do not collapse into one scene.',
    'final_hold': 'Final hold: use restrained motion, fade-ready composition, stable identity, no new location reset.',
    'scenic_character_sheet_intro': 'Scenic pattern — character/model sheet intro: treat the sheet as a shot library, not one flat image; structure detail -> identity -> presence -> full reveal; include active gestures, micro-expressions, gaze/body language, controlled camera, consistent lighting.',
    'scenic_product_ad_arc': 'Scenic pattern — 15s ad/product arc: timestamp problem/contact/transformation/demonstration/hero-shot beats; make the final product/brand hero shot explicit while preserving project-specific references.',
}

CANONICAL_TAIL = 'Preserve exact crop unless explicitly changed. Maintain heroine identity, costume, face, body proportions, paper-lantern motif, rainy blue/amber palette. No text, logos, readable signs, lip-sync, new facial structure, new props, gore, flags, watermarks, or location reset. Mute generated audio.'

DYNAMIC_RULE_TEXT = {
    'identity_closeup': 'Dynamic close-up: do not freeze the reference. Add micro eye movement, breathing, hair/rain movement, slow rack focus or gentle dolly; preserve crop and face; no zoom-out unless specified.',
    'kinetic_tracking': 'Dynamic kinetic: use tracking/side/back camera, parallax, footstep/cloth/hair motion, purposeful acceleration/deceleration; preserve anatomy and route direction.',
    'memory_interior': 'Dynamic memory: slow dolly/rack focus, light/rain/reflection movement, subtle hand/eye motion; environment reference must not overwrite heroine identity.',
    'object_motif': 'Dynamic motif: macro camera, glow/rotation/particles/rain interaction, clear causal transformation; no unrelated props or readable text.',
    'transition_abstract': 'Dynamic transition: energetic morph/streak/flare/whip-pan/impact beat, specify metaphorical vs literal; prevent real-animal/object substitution when abstract.',
    'multi_shot': 'Dynamic multi-shot: state duration/aspect/shot count upfront; enumerate Beat 1..N; each beat needs a camera verb and subject/action verb, not only a still-image description.',
    'final_hold': 'Dynamic final: restrained cinematic reveal/hold with living atmosphere, not static freeze; stabilize identity and fade-ready composition.',
    'scenic_character_sheet_intro': 'Dynamic Scenic character sheet: convert sheet elements into separate shots; character moves/reacts/interacts; include short natural gestures, micro-expressions, gaze/body language, and a controlled reveal rather than a frozen pan over the sheet.',
    'scenic_product_ad_arc': 'Dynamic Scenic product/ad: use timestamped beats from low-energy/problem state to product contact, transformation burst, energetic demonstration, and clean hero shot; do not leave the product as a passive still.'
}
PROJECT_ISOLATION_RULE = 'Project isolation: use only current project-root references and current block ids; reject old smoke-test/10s Runway Recent Generation assets or stale image2/IMG_2 thumbnails as contamination.'

def latest_block_event(project: Path, block: str) -> dict:
    q = project / 'queues' / 'seedance_block_queue.jsonl'
    found = {}
    if q.exists():
        for line in q.read_text(encoding='utf-8', errors='ignore').splitlines():
            try: e=json.loads(line)
            except Exception: continue
            if e.get('block_id') == block and e.get('event') in {'SEEDANCE_BLOCK_READY','SUKUNA_REFERENCE_BUNDLE_HANDOFF_TO_TOJI'}:
                found = e
    return found

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--project', required=True)
    ap.add_argument('--block', required=True)
    args=ap.parse_args()
    project=Path(args.project)
    event=latest_block_event(project,args.block)
    text=' '.join([str(event.get(k,'')) for k in ['seedance_prompt','covered_cuts','reference_order','ui_image_order']]).lower()
    selected=['multi_shot']
    for key, kws in RULES.items():
        if any(k in text for k in kws) and key not in selected:
            selected.append(key)
    wiki_status = 'available' if WIKI.exists() else 'missing'
    skill_status = 'available' if SEEDANCE_SKILL.exists() else 'missing'
    if not SEEDANCE_SKILL.exists():
        raise SystemExit(f'BLOCKED_REQUIRED_SEEDANCE_PROMPT_SKILL_MISSING: {SEEDANCE_SKILL}')
    out = project/'lanes/seedance/prompts'/f'{args.block}_prompt_rules_used.md'
    out.parent.mkdir(parents=True, exist_ok=True)
    lines=[f'# Seedance prompt rules used — {args.block}', '', f'Mandatory Seedance skill: `{SEEDANCE_SKILL}` ({skill_status})', f'Wiki source: `{WIKI}` ({wiki_status})', 'Pattern source: `raw/articles/scenic-sh-seedance-prompt-gallery-threads-20260525.md` (Scenic gallery; structure mining only, no verbatim copying)', '', '## Mandatory seedance-prompt-en checklist', '- Assign every upload a clear @ImageN/@VideoN/@AudioN role before writing the prompt.', '- Use time-segmented beats for >8s generations.', '- Include camera verbs, subject/action verbs, transitions/effects, and audio/rhythm direction.', '- Check file limits: images <=9, videos <=3, audio <=3, total files <=12, prompt <= provider UI limit.', '- Avoid vague references and conflicting camera instructions.', '', '## Selected rules']
    for key in selected:
        lines.append(f'- {RULE_TEXT[key]}')
    lines += ['', '## Dynamic Seedance motion rules']
    for key in selected:
        if key in DYNAMIC_RULE_TEXT:
            lines.append(f'- {DYNAMIC_RULE_TEXT[key]}')
    lines += ['', '## Project isolation', '', f'- {PROJECT_ISOLATION_RULE}', '', '## Canonical preservation tail', '', CANONICAL_TAIL, '', '## Event summary', '', '```json', json.dumps(event, ensure_ascii=False, indent=2)[:12000], '```']
    out.write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print(out)

if __name__ == '__main__':
    main()
