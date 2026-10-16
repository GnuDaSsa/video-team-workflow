#!/usr/bin/env python3
"""Authoring mode for the preprod stages: Claude writes, Codex runs the workflow.

Modes (manifest.authoring.mode):
  codex   Codex (current session) authors every preprod file itself, as before.
  claude  Codex calls `author` for each creative stage; Claude Code (headless
          `claude -p`) writes only that stage's files, the runtime validates them
          and feeds errors back. Codex keeps approvals, generation, Runway, QC,
          registry and folders. In this mode a stage locks only if its files are
          byte-identical to what Claude wrote (no silent Codex rewrite).
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import preprod  # noqa: E402

MODES = ('codex', 'claude')
CLAUDE_BIN = os.environ.get('CLAUDE_BIN', 'claude')
HOME = Path.home()
SKILLS = HOME / '.codex' / 'skills'
WIKI = HOME / 'wiki'
RUNTIME_ROOT = Path(__file__).resolve().parents[1]
MAX_ATTEMPTS = 3
TIMEOUT_SEC = int(os.environ.get('CLAUDE_AUTHOR_TIMEOUT_SEC', '1500'))

STAGES = ('concept-options', 'concept-lock', 'bible', 'storyboard', 'image-prompts', 'shelf')
LOCK_STAGE = {'concept-options': 'concept', 'concept-lock': 'concept', 'bible': 'bible',
              'storyboard': 'storyboard', 'image-prompts': 'images', 'shelf': 'shelf'}

READ_FIRST = {
    'concept-options': [SKILLS / 'videodirector/SKILL.md', RUNTIME_ROOT / 'templates/director.md'],
    'concept-lock': [RUNTIME_ROOT / 'templates/director.md'],
    'bible': [SKILLS / 'videodirector/SKILL.md', RUNTIME_ROOT / 'templates/director.md'],
    'storyboard': [RUNTIME_ROOT / 'templates/planner.md', SKILLS / 'videodirector/SKILL.md',
                   WIKI / 'concepts/storyboard-production-blueprint-standard.md',
                   WIKI / 'queries/composition-staging-references-2026-10-16.md'],
    'image-prompts': [RUNTIME_ROOT / 'templates/image_creator.md', SKILLS / 'image-prompt/SKILL.md',
                      RUNTIME_ROOT / 'references/character_sheet_prompt_standard.md'],
    'shelf': [RUNTIME_ROOT / 'templates/seedance.md', SKILLS / 'seedance-prompt-en/SKILL.md',
              SKILLS / 'seedance-prompt-en/seedance-prompting.md', SKILLS / 'seedance-prompt-en/examples'],
}

TASK = {
    'concept-options': ('Write preprod/00_concept/concept_options.md: exactly three `## Option A`, `## Option B`, '
                        '`## Option C` sections. Each: logline (one sentence), emotional arc hook -> build -> peak -> out, '
                        'what makes it different from the other two, signature image, must-avoid list, rough block count '
                        'at 15 seconds each. Make the three options genuinely different directions, all faithful to brief.md.'),
    'concept-lock': ('The user chose a direction (see USER INPUT). Fill preprod/00_concept/concept_lock.json from that '
                     'choice, merging any requested changes. Keep every key the template has; no `<...>` placeholders.'),
    'bible': ('Write preprod/01_bible/style_bible.json (image guide) for the locked concept: palette_hex, lighting, '
              'texture, lens_grammar, forbidden_looks, style_block_en (<=600 chars English, pasted verbatim into every '
              'video prompt, generic to the whole film), characters[] (id CHAR_*, identity_block_en <=350 chars, '
              'sheet_ref_id), locations[] (id LOC_*, description_en, anchor_objects).'),
    'storyboard': ('Write preprod/02_storyboard/storyboard.json (콘티): every 15-second block in story order with shots '
                   'that fully decide composition, camera and timing, using ONLY the controlled vocabulary in '
                   'runtime/scripts/preprod.py (SHOT_SIZES, ANGLES, CAMERA_MOVES). Contiguous shot times from 0 to '
                   'duration_sec, one dominant camera move per shot, end_frame that hands off to the next block.'),
    'image-prompts': ('Write one English prompt file preprod/03_image_prompts/<REF_ID>.prompt.txt for every reference the '
                      'storyboard refs[] and the bible sheet_ref_id values need, and preprod/03_image_prompts/'
                      'image_plan.json references[] with ref_id, purpose, role_en (short English role phrase used to bind '
                      '@ImageN) and asset_id null. Do not change asset_id values that are already filled.'),
    'shelf': ('Write preprod/04_shelf/{block}/prompt.txt, the final English Seedance prompt for block {block}, from '
              'preprod/04_shelf/{block}/brief.md and the single canonical template in seedance-prompting.md. Every '
              'requirement in the brief is mandatory. Target <=3200 characters, hard limit 3500.'),
}


def now() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec='seconds')


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# --- mode ------------------------------------------------------------------------

def get_mode(project: Path) -> str:
    manifest = preprod.read_json(project / 'manifest.json') or {}
    return str((manifest.get('authoring') or {}).get('mode') or '')


def set_mode(project: Path, mode: str, quote: str, model: str = '') -> dict:
    if mode not in MODES:
        raise ValueError(f'AUTHOR_MODE_UNKNOWN: {mode}; choose {MODES}')
    if not quote.strip():
        raise ValueError('USER_APPROVAL_REQUIRED: set the authoring mode with --approval-quote of the user choice')
    path = project / 'manifest.json'
    manifest = preprod.read_json(path) or {}
    manifest['authoring'] = {'mode': mode, 'model': model or None, 'set_at': now(),
                             'source': {'quote': quote.strip(), 'at': now()}}
    preprod.write_json(path, manifest)
    return manifest['authoring']


# --- targets / provenance ----------------------------------------------------------

def target_files(project: Path, stage: str, block: str = '') -> list[Path]:
    base = preprod.root(project)
    if stage == 'concept-options':
        return [base / '00_concept/concept_options.md']
    if stage == 'concept-lock':
        return [base / '00_concept/concept_lock.json']
    if stage == 'bible':
        return [base / '01_bible/style_bible.json']
    if stage == 'storyboard':
        return [base / '02_storyboard/storyboard.json']
    if stage == 'image-prompts':
        return sorted((base / '03_image_prompts').glob('*.prompt.txt'))
    if stage == 'shelf':
        return [base / '04_shelf' / block / 'prompt.txt']
    raise ValueError(f'AUTHOR_STAGE_UNKNOWN: {stage}')


def writable(project: Path, stage: str, block: str, path: Path) -> bool:
    base = preprod.root(project)
    if stage == 'image-prompts':
        return path.parent == base / '03_image_prompts' and (path.name.endswith('.prompt.txt') or path.name == 'image_plan.json')
    return path in target_files(project, stage, block)


def snapshot(project: Path) -> dict[str, str]:
    """Hash every non-media file Claude could reach inside the project."""
    out = {}
    for path in project.rglob('*'):
        if path.is_file() and 'media' not in path.relative_to(project).parts[:1] and path.suffix != '.sqlite':
            out[str(path)] = sha(path)
    return out


def authorship_path(project: Path) -> Path:
    return preprod.root(project) / 'authorship.jsonl'


def record_authorship(project: Path, stage: str, block: str, result: dict, files: list[Path]) -> dict:
    row = {'at': now(), 'stage': stage, 'block': block or None, 'author': 'claude',
           'model': ','.join(result.get('models') or []) or None, 'session_id': result.get('session_id'),
           'cost_usd': result.get('total_cost_usd'), 'files': {str(f.relative_to(project)): sha(f) for f in files if f.is_file()}}
    with authorship_path(project).open('a', encoding='utf-8') as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + '\n')
    return row


def claude_authored(project: Path, path: Path) -> bool:
    """True when the file's current bytes are exactly what Claude last wrote."""
    rel = str(path.relative_to(project))
    if not authorship_path(project).is_file() or not path.is_file():
        return False
    digest, last = sha(path), None
    for line in authorship_path(project).read_text(encoding='utf-8').splitlines():
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if rel in (row.get('files') or {}):
            last = row['files'][rel]
    return last == digest


def lock_authorship_errors(project: Path, lock_stage: str, block: str = '') -> list[str]:
    """In claude mode the locked creative files must be Claude's unchanged output."""
    if get_mode(project) != 'claude':
        return []
    base = preprod.root(project)
    paths = {
        'concept': [base / '00_concept/concept_options.md', base / '00_concept/concept_lock.json'],
        'bible': [base / '01_bible/style_bible.json'],
        'storyboard': [base / '02_storyboard/storyboard.json'],
        'images': sorted((base / '03_image_prompts').glob('*.prompt.txt')),
        'shelf': [base / '04_shelf' / block / 'prompt.txt'],
    }[lock_stage]
    return [f'claude_mode_file_not_claude_output:{p.relative_to(project)}' for p in paths if not claude_authored(project, p)]


# --- prompt + run --------------------------------------------------------------------

def stage_errors(project: Path, stage: str, block: str) -> list[str]:
    if stage == 'concept-options':
        return [e for e in preprod.VALIDATORS['concept'](project)
                if 'concept_options' in e or 'unfilled_placeholder:concept_options' in e]
    if stage == 'shelf':
        return preprod.validate_shelf_prompt(project, block)
    if stage == 'image-prompts':
        return [e for e in preprod.VALIDATORS['images'](project)
                if 'not_generated_or_not_approved' not in e and 'asset_not' not in e]
    return preprod.VALIDATORS[LOCK_STAGE[stage]](project)


def build_prompt(project: Path, stage: str, block: str, feedback: str, errors: list[str]) -> str:
    reads = [str(p) for p in READ_FIRST[stage] if p.exists()]
    files = [str(p.relative_to(project)) for p in target_files(project, stage, block)] or ['(see task)']
    lines = [
        'You are the creative author for one stage of a video pre-production pipeline. '
        'Codex runs the rest of the workflow; your only job is to write the files for this stage.',
        f'Project directory (your working directory): {project}',
        '', '## Task', TASK[stage].format(block=block),
        '', '## Read first',
        '- brief.md, changelog.jsonl (if present) and every existing file under preprod/ (locked upstream stages are binding).',
        f'- runtime/scripts/preprod.py at {RUNTIME_ROOT / "scripts/preprod.py"} for exact schemas, vocabulary and limits.',
        *[f'- {r}' for r in reads],
        '', '## Rules',
        '- Write or edit ONLY: ' + ', '.join(files) + (' and preprod/03_image_prompts/image_plan.json' if stage == 'image-prompts' else '') + '.',
        '- Do not modify any other file, do not run shell commands, do not touch media/, lanes/, locks or skills.',
        '- All model-facing text (style/identity blocks, image and video prompts) is English. Notes for humans may be Korean.',
        '- No file names, paths, tool names, gate words or process notes inside prompts.',
        '- When finished, reply with a 3-line summary of what you decided (Korean is fine).',
    ]
    if feedback.strip():
        lines += ['', '## USER INPUT (binding)', feedback.strip()]
    if errors:
        lines += ['', '## Validator errors from your previous attempt — fix all of them', *[f'- {e}' for e in errors]]
    return '\n'.join(lines)


def claude_cmd(project: Path, prompt: str, model: str, resume: str = '') -> list[str]:
    deny = []
    for root in (SKILLS, WIKI, RUNTIME_ROOT, HOME / '.codex'):
        for tool in ('Edit', 'Write', 'MultiEdit', 'NotebookEdit'):
            deny.append(f'{tool}(/{root}/**)')
    cmd = [CLAUDE_BIN, '-p', prompt, '--output-format', 'json', '--permission-mode', 'acceptEdits',
           '--allowedTools', 'Read', 'Glob', 'Grep', 'Edit', 'Write',
           '--disallowedTools', 'Bash', 'WebFetch', 'WebSearch', 'Task', *deny,
           '--add-dir', str(SKILLS), str(WIKI), str(RUNTIME_ROOT), '--max-turns', '60']
    if model:
        cmd += ['--model', model]
    if resume:
        cmd += ['--resume', resume]
    return cmd


def run_claude(project: Path, prompt: str, model: str, resume: str = '') -> dict:
    proc = subprocess.run(claude_cmd(project, prompt, model, resume), cwd=project, capture_output=True,
                          text=True, timeout=TIMEOUT_SEC)
    try:
        data = json.loads(proc.stdout)
    except ValueError:
        raise ValueError(f'CLAUDE_CLI_FAILED rc={proc.returncode}: {(proc.stderr or proc.stdout)[:400]}')
    if data.get('is_error'):
        raise ValueError(f'CLAUDE_CLI_ERROR: {str(data.get("result"))[:400]}')
    data['models'] = list((data.get('modelUsage') or {}).keys())
    return data


def author(project: Path, stage: str, block: str = '', feedback: str = '') -> dict:
    project = project.expanduser().resolve()
    if get_mode(project) != 'claude':
        raise ValueError('AUTHOR_MODE_NOT_CLAUDE: in codex mode the current session writes preprod files itself')
    if stage not in STAGES:
        raise ValueError(f'AUTHOR_STAGE_UNKNOWN: {stage}')
    if stage == 'concept-lock' and not feedback.strip():
        raise ValueError('USER_CHOICE_REQUIRED: pass the user choice with --feedback')
    if stage == 'shelf':
        if not block:
            raise ValueError('BLOCK_REQUIRED: --block for shelf')
        preprod.write_shelf_brief(project, block)
    model = str(((preprod.read_json(project / 'manifest.json') or {}).get('authoring') or {}).get('model') or '')
    before = snapshot(project)
    session, errors, attempts, result = '', [], 0, {}
    while attempts < MAX_ATTEMPTS:
        attempts += 1
        result = run_claude(project, build_prompt(project, stage, block, feedback, errors), model, session)
        session = result.get('session_id') or session
        after = snapshot(project)
        stray = sorted(p for p, digest in after.items()
                       if before.get(p) != digest and not writable(project, stage, block, Path(p)))
        if stray:
            raise ValueError('CLAUDE_WROTE_OUTSIDE_STAGE: ' + ', '.join(stray[:5]))
        errors = stage_errors(project, stage, block)
        if not errors:
            break
    files = target_files(project, stage, block)
    if stage == 'image-prompts':
        files = files + [preprod.root(project) / '03_image_prompts/image_plan.json']
    row = record_authorship(project, stage, block, result, files)
    return {'ok': not errors, 'stage': stage, 'block': block or None, 'attempts': attempts,
            'errors': errors, 'summary': str(result.get('result') or '')[:1200], 'authorship': row}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('set-mode'); p.add_argument('--project', required=True)
    p.add_argument('--mode', required=True, choices=MODES); p.add_argument('--approval-quote', required=True)
    p.add_argument('--model', default='')
    p = sub.add_parser('mode'); p.add_argument('--project', required=True)
    p = sub.add_parser('run'); p.add_argument('--project', required=True)
    p.add_argument('--stage', required=True, choices=STAGES); p.add_argument('--block', default='')
    p.add_argument('--feedback', default='', help='user choice or change request, quoted')
    args = parser.parse_args()
    project = Path(args.project).expanduser().resolve()
    try:
        if args.cmd == 'set-mode':
            out = {'ok': True, 'authoring': set_mode(project, args.mode, args.approval_quote, args.model)}
        elif args.cmd == 'mode':
            out = {'ok': True, 'mode': get_mode(project) or 'UNSET'}
        else:
            out = author(project, args.stage, args.block, args.feedback)
    except (ValueError, KeyError, subprocess.TimeoutExpired) as exc:
        out = {'ok': False, 'error': str(exc)}
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if out.get('ok') else 1


if __name__ == '__main__':
    raise SystemExit(main())
