#!/usr/bin/env python3
"""Export one exact committed source tree, never the working tree or installed files.

A complete tracked source tree is retained because configured regression commands
load both runtime and Aside suites. The adjacent export document lists the minimum
harness closure; files.txt is the exact exhaustive list for this commit.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])


def inspect(commit):
    sha = git('rev-parse', '--verify', commit + '^{commit}').decode().strip()
    rows = git('ls-tree', '-rz', '--full-tree', sha).split(b'\0')
    files = []
    for row in rows:
        if not row:
            continue
        meta, name = row.split(b'\t', 1)
        mode, kind, _oid = meta.decode().split()
        path = name.decode()
        if mode not in {'100644', '100755'} or kind != 'blob':
            raise ValueError('NON_REGULAR_TRACKED_ENTRY:' + path)
        if PurePosixPath(path).suffix.lower() in {'.mp4','.mov','.wav','.mp3','.png','.jpg','.jpeg','.sqlite','.zip'}:
            raise ValueError('MEDIA_OR_ARCHIVE_NOT_SOURCE:' + path)
        if PurePosixPath(path).name.lower() in {'.env','credentials','id_rsa','id_ed25519'}:
            raise ValueError('SENSITIVE_FILENAME:' + path)
        files.append(path)
    def read(path):
        if path not in files:
            raise ValueError('MISSING_TRACKED_DEPENDENCY:' + path)
        return git('show', sha + ':' + path)
    required = ['AGENTS.md','AGENTS.harness.md','runtime/AGENTS.md','runtime/AGENTS.harness.md',
                'docs/harness-config.json','docs/video-feedback-promotion-protocol.md']
    config = json.loads(read('docs/harness-config.json'))
    for key in ('stateFile','decisionsFile','memoryFile'):
        required.append(config['paths'][key])
    state = json.loads(read(config['paths']['stateFile']))
    required.append(state['currentContract'])
    for path in required:
        read(path)
    return sha, sorted(files), sorted(set(required))


def export(commit, output):
    sha, files, required = inspect(commit)
    output.mkdir(parents=True, exist_ok=True)
    targets = [output/name for name in ('source.tar.gz','files.txt','manifest.json')]
    if any(path.exists() for path in targets):
        raise ValueError('EXPORT_DESTINATION_ALREADY_EXISTS')
    archive = gzip.compress(git('archive','--format=tar','--prefix=workflow/',sha),mtime=0)
    targets[0].write_bytes(archive)
    targets[1].write_text('\n'.join(files)+'\n')
    manifest = {'source_commit':sha,'archive_sha256':hashlib.sha256(archive).hexdigest(),
                'files_sha256':hashlib.sha256(targets[1].read_bytes()).hexdigest(),
                'tracked_file_count':len(files),'required_harness_files':required,
                'scope':'Committed source only; not installation, permission or live validation.'}
    targets[2].write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--commit',required=True)
    p.add_argument('--output',type=Path,required=True)
    args = p.parse_args()
    print(json.dumps(export(args.commit,args.output),ensure_ascii=False,indent=2))
