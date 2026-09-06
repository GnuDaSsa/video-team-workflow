#!/usr/bin/env python3
"""Read-only pack compatibility audit; never revises or re-attests a shelf."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--root', type=Path, required=True)
p.add_argument('--runtime-scripts', type=Path, default=Path(__file__).resolve().parents[1] / 'runtime/scripts')
p.add_argument('--pattern', default='*_package.json')
a = p.parse_args()
sys.path.insert(0, str(a.runtime_scripts))
from prompt_packet_utils import validate_seedance
rows = []; counts = Counter()
for path in sorted(a.root.rglob(a.pattern)):
    before = path.read_bytes()
    try:
        errors = validate_seedance(json.loads(before))
    except (ValueError, TypeError, KeyError) as exc:
        errors = ['invalid_pack_structure:' + type(exc).__name__]
    counts.update(errors)
    if path.read_bytes() != before:
        raise SystemExit('UNEXPECTED_PACK_CHANGE_DURING_READ_ONLY_AUDIT')
    rows.append({'pack': str(path.relative_to(a.root)), 'sha256': hashlib.sha256(before).hexdigest(),
                 'compatible': not errors, 'errors': errors})
print(json.dumps({'read_only': True, 'packs': len(rows), 'compatible': sum(r['compatible'] for r in rows),
                  'incompatible': sum(not r['compatible'] for r in rows),
                  'error_counts': dict(counts), 'results': rows}, ensure_ascii=False, indent=2))
