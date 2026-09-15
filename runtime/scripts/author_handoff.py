#!/usr/bin/env python3
"""Build native Astra author requests and verify immutable handoffs. No dispatch/UI."""
import argparse
import hashlib
import json
from pathlib import Path


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def local(project, name):
    root = Path(project).resolve(strict=True)
    path = (root / name).resolve(strict=True)
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError('artifact_outside_project_or_not_file')
    return path


def request(project, block, kind, inputs, output, approval):
    if kind not in ('planning', 'image', 'video') or not block.strip():
        raise ValueError('invalid_author_scope')
    token = f'astra-author:{kind}:{block}'
    if approval != token:
        raise ValueError('SPECIFIC_SPAWN_APPROVAL_REQUIRED:' + token)
    if not inputs:
        raise ValueError('bounded_inputs_required')
    paths = [str(local(project, f)) for f in inputs]
    out = (Path(project).resolve() / output).resolve()
    if not out.is_relative_to(Path(project).resolve()) or out == Path(project).resolve():
        raise ValueError('invalid_output_scope')
    return dict(task_name='astra_author', model='gpt-6-astra',
                reasoning_effort='xhigh', fork_turns='none', message=(
        f'Own only {kind} authoring for block {block}. Output scope: {out}.\n'
        f'Project: {Path(project).resolve()}. Read canonical runtime AGENTS §1.3 and the relevant '
        'authoring skill, then these bounded source files:\n' + '\n'.join(paths) +
        '\nYou are not alone in the codebase. Preserve other edits. Do not use browser, '
        'Computer Use, image/video generation, scheduler, or spawn another agent. '
        'Do not change the block or substitute another scene. Author and review the local '
        'package; return prompt/ordered references/settings paths, hashes, and limitations. '
        'Use the relevant native attestation, not a self-declared PASS. Return to the parent; '
        'the original session executes. Parent records actual returned agent identity/model '
        'evidence separately; self-written metadata is not proof.'))


def verify(project, receipt, block):
    """Receipt hash must be retained by executor at acceptance; not author identity proof."""
    if receipt.get('block_id') != block:
        raise ValueError('block_mismatch')
    if receipt.get('status') != 'READY_FOR_EXECUTION':
        raise ValueError('handoff_not_ready')
    for key in ('prompt', 'settings', 'pack'):
        if key not in receipt:
            raise ValueError('missing_' + key)
    if not isinstance(receipt.get('references'), list):
        raise ValueError('ordered_references_required')
    for row in [receipt['prompt'], receipt['settings'], receipt['pack'], *receipt['references']]:
        if digest(local(project, row['path'])) != row['sha256']:
            raise ValueError('artifact_hash_mismatch:' + row['path'])
    return {'ok': True, 'block_id': block, 'checks': 'artifact_integrity_only',
            'author_identity_verified': False, 'provider_preflight_still_required': True}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    a = sub.add_parser('request')
    a.add_argument('--project', required=True); a.add_argument('--block', required=True)
    a.add_argument('--kind', required=True, choices=['planning','image','video'])
    a.add_argument('--input', dest='inputs', action='append', required=True)
    a.add_argument('--output', required=True); a.add_argument('--approval', required=True)
    v = sub.add_parser('verify')
    v.add_argument('--project', required=True); v.add_argument('--block', required=True)
    v.add_argument('--receipt', required=True); v.add_argument('--receipt-sha256', required=True)
    args = vars(p.parse_args()); command = args.pop('command')
    try:
        if command == 'request':
            result = request(**args)
        else:
            path = local(args['project'], args['receipt'])
            if digest(path) != args['receipt_sha256']:
                raise ValueError('receipt_changed_since_acceptance')
            result = verify(args['project'], json.loads(path.read_text()), args['block'])
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        p.exit(1, str(exc) + '\n')


if __name__ == '__main__':
    main()
