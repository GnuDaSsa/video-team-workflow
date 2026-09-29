#!/usr/bin/env python3
"""Deploy explicitly reviewed tracked-source patches, preserving unrelated live drift.

Use the full release path for clean bundle parity. This narrower route verifies
patch applicability and reverse applicability, never claims full-file parity.
"""
import argparse
import difflib
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess

import video_release


def merge_bytes(live, base, source):
    """Merge disjoint base-line edits only; adjacent edits need not conflict."""
    original = base.splitlines(keepends=True)
    changes = []
    for version in (live, source):
        lines = version.splitlines(keepends=True)
        for tag, start, end, a, b in difflib.SequenceMatcher(
                None, original, lines, autojunk=False).get_opcodes():
            if tag == 'equal':
                continue
            change = (start, end, lines[a:b])
            if change in changes:
                continue
            for old_start, old_end, _ in changes:
                overlap = max(start, old_start) < min(end, old_end)
                if start == end:
                    overlap |= old_start <= start <= old_end
                if old_start == old_end:
                    overlap |= start <= old_start <= end
                if overlap:
                    raise ValueError('PATCH_CONTEXT_CONFLICT')
            changes.append(change)
    result = list(original)
    for start, end, lines in sorted(changes, key=lambda row: row[:2], reverse=True):
        result[start:end] = lines
    return b''.join(result)


def deploy(root, home, sources, apply=False):
    if not sources or len(set(sources)) != len(sources):
        raise ValueError('EXPLICIT_UNIQUE_SOURCE_LIST_REQUIRED')
    allowed = {r['source']: r for r in video_release.mappings(root)}
    prepared = []
    for source in sources:
        if source not in allowed:
            raise ValueError('SOURCE_NOT_RELEASE_MANAGED: ' + source)
        row = allowed[source]
        live = video_release.safe_path(home, row['target'])
        if not live.is_file():
            raise ValueError('LIVE_FILE_REQUIRED: ' + source)
        patch = subprocess.check_output(
            ['git', 'diff', '--no-ext-diff', '--no-color', 'HEAD', '--', source], cwd=root)
        if not patch:
            raise ValueError('REVIEWED_TRACKED_PATCH_REQUIRED: ' + source)
        before = live.read_bytes()
        base = subprocess.check_output(['git', 'show', 'HEAD:' + source], cwd=root)
        proposed = video_release.safe_path(root, source).read_bytes()
        after = merge_bytes(before, base, proposed)
        if merge_bytes(after, proposed, base) != before:
            raise ValueError('PATCH_REVERSE_VERIFICATION_FAILED: ' + source)
        prepared.append((row, live, before, after, patch))
    receipt = dict(ok=True, scope='reviewed_patch_only', full_bundle_parity=False,
                   applied=apply, files=[])
    for row, live, before, after, patch in prepared:
        receipt['files'].append(dict(source=row['source'], target=row['target'],
            before_sha256=hashlib.sha256(before).hexdigest(),
            after_sha256=hashlib.sha256(after).hexdigest(),
            patch_sha256=hashlib.sha256(patch).hexdigest()))
    if not apply:
        return receipt
    archive = home / '.codex/archive' / (dt.datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '_reviewed_patch')
    # All patches passed before any live write. Recheck concurrent changes first.
    if any(live.read_bytes() != before for _, live, before, _, _ in prepared):
        raise ValueError('LIVE_CHANGED_AFTER_PREFLIGHT')
    changed = []
    try:
        for row, live, before, after, patch in prepared:
            saved = archive / row['target']
            saved.parent.mkdir(parents=True, exist_ok=True)
            saved.write_bytes(before)
            (saved.with_name(saved.name + '.patch')).write_bytes(patch)
            changed.append((live, before))
            live.write_bytes(after)
            if live.read_bytes() != after:
                raise ValueError('PATCH_DEPLOY_VERIFY_FAILED')
    except Exception:
        for live, before in reversed(changed):
            live.write_bytes(before)
        raise
    receipt['archive'] = str(archive)
    (archive/'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--source', action='append', required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(deploy(video_release.ROOT, Path.home(), args.source, args.apply), indent=2))
        return 0
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(json.dumps(dict(ok=False, error=str(exc))))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
