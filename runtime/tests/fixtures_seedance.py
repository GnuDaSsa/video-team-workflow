"""Explicit non-default language evidence for tests of unrelated semantics."""
import hashlib
import json
from pathlib import Path


def korean_request(pack, project):
    root = Path(project).resolve()
    evidence = root / 'docs' / ('language-' + pack['block_id'] + '.json')
    evidence.parent.mkdir(parents=True, exist_ok=True)
    evidence.write_text(json.dumps(dict(
        language='ko-KR', source='explicit_user_request',
        user_quote='이 테스트 블록의 제작 지시문은 한국어로 작성해 주세요.',
        turn_id='test-explicit-korean', block_ids=[pack['block_id']]), ensure_ascii=False))
    pack['prompt_language_override'] = dict(
        project=str(root), evidence_path=str(evidence),
        evidence_sha256=hashlib.sha256(evidence.read_bytes()).hexdigest())
    return pack
