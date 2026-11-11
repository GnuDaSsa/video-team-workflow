#!/usr/bin/env python3
"""User-rejected prompt patterns as data (one place). Warnings only; never blocks a lock.

Each rule: id, kinds (seedance_prompt|image_prompt|storyboard|concept), regex, reason (Korean),
hint (replacement wording), source (Claude memory file the correction came from), optional
`unless` (rule is skipped when this regex matches anywhere in the text) and `purpose`
(image_prompt only: apply when the reference purpose equals it; skipped if purpose unknown).
A match preceded within 4 words (same sentence) by no/without/never/not/avoid/금지 passes.
A block opts out of a rule with `lint_allow: [rule_id]`.
"""
from __future__ import annotations

import re

KINDS = ('seedance_prompt', 'image_prompt', 'storyboard', 'concept')
_NEG = re.compile(r"\b(no|without|never|not|avoid|avoids|don'?t|do not|nor|zero)\b|금지|없이|말고", re.I)
_KO = (r'korea|korean|seoul|seongnam|gyeonggi|busan|hwaseong|gwangyang|gyeongsan|pangyo|'
       r'hangul|한국|성남|서울|경산|광양|화성')

RULES = [
    dict(id='smooth_skin', kinds=['seedance_prompt', 'image_prompt'],
         regex=r'\b(smooth|flawless|perfect|porcelain|airbrushed|poreless)\s+(natural\s+)?skin\b|\bskin\s+(stays|remains|is)\s+(smooth|flawless)',
         reason='"매끈한 피부" 문구가 플라스틱 AI 티를 만든다',
         hint='true-to-life skin with fine pores and soft age lines, no beauty smoothing, 35mm lens, subtle film grain',
         source='seedance-avoid-smooth-skin.md'),
    dict(id='text_prop', kinds=['seedance_prompt', 'storyboard'],
         regex=r'\b(lab\s*coats?|beakers?|labels?|labell?ed|signage|(street|shop|road|neon|exit|name|door)\s*(signs?|plates?|tags?)|whiteboards?|blackboards?|'
               r'posters?|newspapers?|clipboards?|cartons?|banners?|ingredient cards?|flash ?cards?|price tags?|billboards?|control panels?)\b',
         reason='글자가 생기는 소품(Seedance가 가짜 한자·숫자를 그린다)',
         hint='plain white non-woven gown, blank chest; plain round glass jar with blank walls; or drop the prop; shoot equipment tight on the working part',
         source='seedance-no-text-props.md'),
    dict(id='garment_text', kinds=['seedance_prompt'],
         regex=r'\b(logos?|lettering|typography|embroider\w*|name\s*badges?|printed (shirt|jersey|text)|slogan)\b',
         reason='옷·물건 위 글자는 깨진 글자로 나온다',
         hint='plain unmarked clothing; face the back of the garment away or keep it out of frame',
         source='seedance-clip-qc-gaze-and-garment-text.md'),
    dict(id='screen_content', kinds=['seedance_prompt', 'storyboard'],
         regex=r'\b(screens?|monitors?|displays?|tablets?|laptops?|tvs?|lcd)\s+(shows?|showing|displays?|displaying|lights? up|glows?|flicker\w*)\b|'
               r'\b(diagram|circuit|graph|chart|ui|interface|dashboard|code)s?\s+(on|across)\s+(the\s+|a\s+)?(screens?|monitors?|display)\b|\bon-?screen\s+(graphic|ui|diagram)',
         reason='화면 내용을 묘사하면 화면이 불려 나오고 가짜 UI 글자가 생긴다',
         hint='frame so no screen is visible, or the screen is switched off / turned away; show hands, equipment, boards instead; diagrams only as code MG',
         source='seedance-screen-and-tube-wording.md'),
    dict(id='screen_summon', kinds=['seedance_prompt'],
         regex=r'\b(any|all|every)\s+(screens?|monitors?|displays?)\b|\bscreens?\s+(stay|stays|remain|remains|only|are)\s+(blank|dark|empty|color|soft)',
         reason='"화면은 비어 있다/색 도형만" 문구 자체가 화면을 부른다',
         hint='do not mention screens at all; describe the action without devices',
         source='seedance-screen-and-tube-wording.md'),
    dict(id='nasal_tube', kinds=['seedance_prompt', 'image_prompt'],
         regex=r'\b(nasal|feeding|ng|nostril)\s*(feeding\s*)?tube\b|\btube\s+(from|in|at)\s+(her|his|the)\s+nostril',
         unless=r'not (an? )?(oxygen )?cannula',
         reason='콧줄 묘사가 산소 캐뉼라로 오인된다',
         hint='"a single fine clear nasal feeding tube from the right nostril only, not an oxygen cannula"; fix one side; tube must be on the identity sheet',
         source='seedance-screen-and-tube-wording.md'),
    dict(id='foreign_office', kinds=['seedance_prompt', 'storyboard', 'concept'],
         regex=r'\b(glass[- ]walled\s+)?(corporate\s+)?(open[- ]plan\s+)?offices?\b|\bboardroom\b|\bmeeting room\b',
         unless=_KO,
         reason='한국 현장 단서 없는 사무실은 외국 회사풍 스톡 장면이 된다',
         hint='state Korean engineers and a Korean workplace detail (e.g. Korean office, Korean signage-free corridor), or use a real site/equipment',
         source='seedance-no-foreign-office-screen-diagrams.md'),
    dict(id='start_frame', kinds=['seedance_prompt', 'image_prompt', 'storyboard', 'concept'],
         regex=r'\bstart[ _-]?frames?\b|\bstyle[ _-]?frames?\b|\b[A-Z0-9]+_START_FRAME\b|\bkeyframe refs?\b',
         reason='사용자는 스타일프레임/시작프레임을 쓰지 않는다',
         hint='refs = character sheets + location/prop refs only; go straight to Seedance',
         source='no-start-frames.md'),
    dict(id='onscreen_text', kinds=['seedance_prompt', 'storyboard', 'concept'],
         regex=r'\b(title cards?|title text|opening titles?|place[- ]name (titles?|labels?)|captions?|subtitles?|lower[- ]thirds?|on-?screen text|text overlays?|watermarks?|burned-in)\b',
         reason='요청하지 않은 자막·지명 타이틀·라벨 삽입 금지',
         hint='default to a text-free version; offer on-screen text to the user as an option only',
         source='no-unrequested-onscreen-text.md'),
    dict(id='env_ref_props', kinds=['image_prompt'], purpose='environment',
         regex=r'\b(bowls? of|ribbons?|vases?|flowers? (on|in)|story props?|decorative props?|props?)\b',
         reason='장소 참조의 이야기 소품은 영상에 확률적으로 번진다',
         hint='location reference: architecture and light only; at most a glass and a candle; edge-to-edge full-bleed',
         source='location-ref-no-props-no-paper-margin.md'),
    dict(id='paper_margin', kinds=['image_prompt'],
         regex=r'\b(paper\s+(margins?|borders?|edges?|showing through)|cream paper|white (margins?|borders?)|deckled|(unpainted|blank) margins?|vignette border|picture frame border|torn edges?)\b',
         reason='종이 여백·테두리가 참조 이미지에서 영상으로 번진다',
         hint='full-bleed, edge-to-edge image with no margin or border',
         source='location-ref-no-props-no-paper-margin.md'),
    dict(id='restraint_action', kinds=['seedance_prompt', 'storyboard'],
         regex=r'\b(running|sprinting|leaping|chasing|grabbing)\b|elevator doors? (clos|shut)|ribbons? (vote|ballot)',
         reason='과한 액션·거절된 클리셰(엘베문, 리본투표)',
         hint='small acting: a head turn, a hand pause, a slow walk; show choices through objects placed or withheld',
         source='seedance-handdrawn-restraint-and-insert-shots.md'),
    dict(id='forced_metaphor', kinds=['storyboard', 'concept'],
         regex=r'\b(robot(ic)? arms?|robots?|ai|chips?|circuits?)\b[^.\n]{0,60}\b(ink|brush|calligraphy|geese|goose|crane|blossoms?|mountains?)\b|'
               r'\b(ink|brush|calligraphy|geese|goose|crane|blossoms?)\b[^.\n]{0,60}\b(robot(ic)? arms?|robots?|chips?|circuits?)\b',
         reason='자연×AI 억지 메타포는 거절됨; 장면은 대사 그대로',
         hint='show what the line literally says; keep AI scenes and nature scenes separate; ink style only when the line says draw/paint',
         source='scenes-follow-copy-literally.md'),
]
_BY_ID = {r['id']: r for r in RULES}


def _negated(text: str, start: int) -> bool:
    before = re.split(r'[.;\n]', text[max(0, start - 80):start])[-1]
    return bool(_NEG.search(' '.join(before.split()[-4:])))


def lint(text: str, kind: str, allow=(), purpose: str | None = None) -> list[dict]:
    """Rule hits for `text`. Negated mentions ("no lab coat") pass."""
    if kind not in KINDS:
        raise ValueError(f'LINT_KIND_UNKNOWN: {kind}')
    out = []
    for rule in RULES:
        if kind not in rule['kinds'] or rule['id'] in set(allow or ()):
            continue
        if rule.get('purpose') and rule['purpose'] != purpose:
            continue
        if rule.get('unless') and re.search(rule['unless'], text, re.I):
            continue
        for m in re.finditer(rule['regex'], text, re.I):
            if _negated(text, m.start()):
                continue
            out.append({'id': rule['id'], 'kind': kind, 'match': m.group(0), 'reason': rule['reason'],
                        'hint': rule['hint'], 'source': rule['source']})
            break
    return out


def rules_brief(kind: str) -> str:
    """Short list for authoring prompts (at most 15 lines)."""
    rows = [f'- {r["reason"]} [{r["id"]}] -> {r["hint"]}' for r in RULES if kind in r['kinds']]
    return '\n'.join((['Patterns the user already rejected (negated mentions like "no X" are fine):'] + rows)[:15])


def main() -> int:
    import json
    import sys
    kind = sys.argv[1] if len(sys.argv) > 1 else 'seedance_prompt'
    print(json.dumps(lint(sys.stdin.read(), kind), ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
