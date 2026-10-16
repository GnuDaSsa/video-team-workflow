#!/usr/bin/env python3
"""Scoped instruction deployment. Preflight by default; --apply backs up changes.
Uses canonical release allowlist; never overwrites unrelated source/live drift.
"""
import hashlib
import json
from pathlib import Path
import sys
from datetime import datetime

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
from video_release import mappings, safe_path

HOME = Path.home()

def replace_once(text, before, after):
    if after in text:
        return text
    if text.count(before) != 1:
        raise ValueError('AMBIGUOUS_OR_MISSING_DEPLOY_ANCHOR')
    return text.replace(before, after, 1)


def proposals():
    allowed = {r['source']: r for r in mappings(ROOT)}
    sources = ['runtime/AGENTS.md', 'codex-skills/videodirector/SKILL.md',
               'runtime/templates/editor.md',
               'codex-skills/videodirector/references/flow-malfoy-composite.md']
    rows = []
    for src in sources:
        target = safe_path(HOME, allowed[src]['target'])
        before = target.read_bytes() if target.exists() else None
        canonical = (ROOT / src).read_text()
        if src.endswith('flow-malfoy-composite.md'):
            if before is not None and before != canonical.encode():
                raise ValueError('EXISTING_REFERENCE_DIFFERS')
            after = canonical
        else:
            if before is None:
                raise ValueError('EXISTING_LIVE_FILE_REQUIRED')
            after = before.decode()
            if src == 'runtime/AGENTS.md':
                old = '5. 프로바이더 기본값은 Seedance다. Grok I2V는 사용자가 해당 프로젝트에서 명시했을 때만 같은 직렬 레일 안에서 사용한다. 프로바이더 병렬은 금지한다.'
                new = next(x for x in canonical.splitlines() if x.startswith('5. 프로바이더 기본값'))
                after = replace_once(after, old, new)
                section = canonical.split('### 1.4 명시적 Flow 제작 분기\n', 1)[1].split('## 2. 프롬프트 소유권', 1)[0]
                addition = '### 1.4 명시적 Flow 제작 분기\n' + section
                after = replace_once(after, '## 2. 프롬프트 소유권', addition + '## 2. 프롬프트 소유권')
            elif src.endswith('SKILL.md'):
                start, end = '<!-- flow-malfoy-routing:start -->', '<!-- flow-malfoy-routing:end -->'
                addition = start + canonical.split(start, 1)[1].split(end, 1)[0] + end
                if start in after:
                    if after.count(start) != 1 or after.count(end) != 1:
                        raise ValueError('DUPLICATE_FLOW_SECTION')
                    old_block = start + after.split(start, 1)[1].split(end, 1)[0] + end
                    after = replace_once(after, old_block, addition)
                else:
                    after = replace_once(after, '# Video Director\n', '# Video Director\n\n' + addition + '\n')
            else:
                addition = '\n## Conditional code-motion knowledge\n' + canonical.split('\n## Conditional code-motion knowledge\n', 1)[1]
                if addition not in after:
                    if '## Conditional code-motion knowledge' in after:
                        raise ValueError('EDITOR_SECTION_CONFLICT')
                    after += addition
        rows.append((src, target, before, after.encode()))
    return rows


def main():
    rows = proposals()
    receipt = {'ok': True, 'scope': 'flow_instruction_and_knowledge_only',
               'full_bundle_parity': False, 'applied': '--apply' in sys.argv, 'files': []}
    archive = HOME / '.codex/archive' / (datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '_flow_knowledge')
    for src, dst, before, after in rows:
        receipt['files'].append({'source': src, 'target': str(dst),
          'before_sha256': hashlib.sha256(before).hexdigest() if before else None,
          'after_sha256': hashlib.sha256(after).hexdigest()})
    if '--apply' in sys.argv:
        # All anchors and allowlist checks pass before the first write.
        for _, dst, before, _ in rows:
            actual = dst.read_bytes() if dst.exists() else None
            if actual != before:
                raise ValueError('LIVE_CHANGED_AFTER_PREFLIGHT')
        archive.mkdir(parents=True)
        for _, dst, before, after in rows:
            saved = archive / dst.relative_to(HOME)
            if before is not None:
                saved.parent.mkdir(parents=True, exist_ok=True)
                saved.write_bytes(before)
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(after)
            assert dst.read_bytes() == after
        receipt['archive'] = str(archive)
        (archive / 'receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(receipt, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
