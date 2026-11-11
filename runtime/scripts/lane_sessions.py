"""Lane work runs in its own fresh Codex session; the main thread only directs.

Why: one long conversation re-sends its whole history on every tool step. After
nine days the door-test thread sent ~180k tokens per click (median 13.5 s of
model time per step, 57 compactions in four days). A lane session starts from
a short work order instead, writes its state to files, returns a few-line
`session_result.json` and exits; the director reads only that.

Rules kept: one lane session at a time (one Runway tab, one browser owner); no
daemons, schedulers or parallel browser loops; payment, public upload,
submission, login and deletion gates stay with the user via the director.
"""
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
import time

# Runway runs at most two active generations per account; a third Generate only
# gets the "wait for your last generation" toast. A production session therefore
# submits into the free slots and ends; a harvest session empties them.
RUNWAY_ACTIVE_SLOTS = 2
# Seedance 2.5 on Unlimited runs one job at a time (a second Generate only queues behind it);
# credits mode runs jobs in parallel again (new-lover 2026-11-10).
UNLIMITED_25_SLOTS = 1
# Machine-wide provider stop. The Runway helper writes it the moment an automation / account
# suspension warning is visible; every browser lane dispatch is refused until the user clears it
# (`video-codex-runtime hold --clear --approval-quote ...`). Retrying after a warning is what
# turned one warning into 34 sessions (2026-11-06) and a second warning (2026-11-10).
HOLD_PATH = Path(os.environ.get('VIDEO_TEAM_PROVIDER_HOLD',
                                '/Users/gnudas/Documents/Codex/video-team-runtime/PROVIDER_HOLD.json'))
REASON_CODES = ('SUBMITTED', 'HARVESTED', 'SLOT_BUSY', 'IN_QUEUE', 'ACCOUNT_WARNING',
                'PROMPT_CLEAR_FAILED', 'ASIDE_UNAVAILABLE', 'UI_STALE', 'ATTACH_FAILED',
                'NEEDS_USER', 'OTHER')
# Lanes whose session must reach the Aside CLI / native chooser (outside the
# workspace sandbox). Everything else runs in the workspace-write sandbox.
GUI_ROUTES = {'seedance:production', 'music', 'flow', 'image_creator_01:production', 'image_creator_02:production'}
RESULT_NAME = 'session_result.json'
CARD_CANDIDATES = (
    Path.home() / '.codex/skills/seedance-prompt-en/production-card.md',
    Path(__file__).resolve().parents[2] / 'codex-skills/seedance-prompt-en/production-card.md',
)


def policy_path(root: Path) -> Path:
    return Path(root) / 'session_policy.json'


def load_policy(root: Path) -> dict:
    try:
        data = json.loads(policy_path(root).read_text(encoding='utf-8'))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    return data if data.get('auto_lane_sessions') and data.get('approval_quote') else {}


def set_policy(root: Path, enable: bool, approval_quote: str = '') -> dict:
    path = policy_path(root)
    if enable:
        if not approval_quote.strip():
            raise SystemExit('SESSION_POLICY_REQUIRES_USER_QUOTE')
        data = {'auto_lane_sessions': True, 'approval_quote': approval_quote.strip(),
                'recorded_at': dt.datetime.now().astimezone().isoformat(timespec='seconds'),
                'scope': ('director may start one sequential lane session at a time via '
                          'video-codex-runtime dispatch; no daemons/schedulers/parallel browser loops; '
                          'payment, public upload, submission, login, deletion stay user-gated')}
    else:
        data = {'auto_lane_sessions': False,
                'recorded_at': dt.datetime.now().astimezone().isoformat(timespec='seconds')}
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return data


def sandbox_args(route_key: str) -> list[str]:
    if route_key in GUI_ROUTES:
        return ['-s', 'danger-full-access', '-c', 'approval_policy="never"']
    # codex 0.16x dropped --full-auto; workspace-write is what it meant for exec.
    return ['-s', 'workspace-write']


def _provider_jobs(project: Path) -> list[dict]:
    # state.json is the durable job ledger (record-generate and harvest write it); the lane's own
    # status.json is rewritten by every session, so it is only a fallback
    state_path = project / 'state.json'
    if state_path.is_file():
        try:
            json.loads(state_path.read_text(encoding='utf-8'))
        except json.JSONDecodeError as exc:
            raise SystemExit(f'LEDGER_CORRUPT: {state_path} is not valid JSON ({exc}); restore it before '
                             'any production/harvest dispatch, or jobs would be generated twice')
    for rel in ('state.json', 'lanes/seedance/status.json'):
        jobs = _json(project / rel).get('provider_jobs')
        if jobs:
            return jobs
    return []


def produced_blocks(project: Path) -> set[str]:
    return {str(j.get('block_id')) for j in _provider_jobs(project) if j.get('block_id')}


def production_batch(project: Path, released: list[str], requested: list[str] | None = None,
                     slots: int = RUNWAY_ACTIVE_SLOTS) -> tuple[list[str], list[str]]:
    """Released blocks without a provider job that fit the free Runway slots, and what remains.

    A generated-but-not-downloaded job still counts as holding a slot, so with two
    such jobs the batch is empty and dispatch runs a harvest session instead.
    """
    done = produced_blocks(project)
    pending = [b for b in released if b not in done]
    if requested:
        unknown = [b for b in requested if b not in released]
        if unknown:
            raise SystemExit(f'BLOCKS_NOT_RELEASED: {unknown}')
        # an explicit --blocks request is a retake: generate again even if a job exists
        pending = list(requested)
    free = max(0, slots - len(undownloaded_jobs(project)))
    return pending[:free], pending[free:]


def latest_handoff(project: Path) -> Path | None:
    docs = sorted((project / 'docs').glob('codex_handoff_*.md'))
    return docs[-1] if docs else None


def card_path() -> Path:
    for path in CARD_CANDIDATES:
        if path.is_file():
            return path
    raise SystemExit('PRODUCTION_CARD_MISSING')


def result_contract(project: Path, lane: str) -> str:
    path = project / 'lanes' / lane / RESULT_NAME
    return f"""
# SESSION RESULT CONTRACT (this session exits when done)

You are a lane session started by the director; the user is not reading this
session. Do only this lane's scope, then write `{path}`:
{{"status": "DONE|PARTIAL|STOPPED|NEEDS_USER", "reason_code": "<one of {'|'.join(REASON_CODES)}>",
  "summary": "<=5 short lines in Korean",
  "outputs": ["paths or asset IDs"], "remaining": ["what is left"],
  "question_for_user": null or "<one exact question>", "next": "<one line>"}}
Then end. Do not ask the user anything here. `NEEDS_USER` (with the exact question)
is only for payment, login/2FA/CAPTCHA, credit-spending (non-Unlimited) generation,
public upload/submission, or deletion. Anything else: decide and proceed, or return
`PARTIAL` saying exactly what the director must do (e.g. an `author run` with feedback).
Never start another session, agent, scheduler or watcher. If Runway shows any automation,
auto-click, suspension or CAPTCHA warning: touch nothing more, status STOPPED,
reason_code ACCOUNT_WARNING (the producer loop then holds every browser lane).
"""


def production_prompt(project: Path, blocks: list[str], remaining: list[str], route: dict) -> str:
    handoff = latest_handoff(project)
    return f"""# Seedance production session — released shelf blocks {', '.join(blocks)}

Model/effort: {route.get('model') or 'user default'} / {route.get('reasoning_effort') or 'user default'}.
Project: {project}
Handoff (session tab, scope, approvals): {handoff or 'none — use the bound tab in lanes/seedance/aside_binding.json'}
Blocks for THIS session, in order: {', '.join(blocks)}
Left for the next session (do not start them): {', '.join(remaining) or 'none'}

Read the handoff, then follow the production card below exactly. Read nothing
else unless a STOPPED code names it. After the last Generate of this batch,
write the session result (status PARTIAL if blocks remain for the next session,
DONE if none) and end; harvest/QC runs in its own later session.

---

{card_path().read_text(encoding='utf-8')}
{result_contract(project, 'seedance')}"""


def undownloaded_jobs(project: Path) -> list[str]:
    return [str(j.get('block_id')) for j in _provider_jobs(project)
            if j.get('block_id') and not j.get('downloaded')]


def harvest_prompt(project: Path, jobs: list[str], route: dict) -> str:
    return f"""# Seedance harvest session — {', '.join(jobs)}

Project: {project}
Generated jobs not yet downloaded: {', '.join(jobs)}
Do NOT click Generate or attach anything. On the bound tab
(`lanes/seedance/aside_binding.json`): if a job is still In queue / Generating after one
bounded wake (at most 10 minutes), stop there with status PARTIAL, reason_code IN_QUEUE — the
producer loop checks again later without a session. For each settled job: download the
matching output, ffprobe (≈15 s), ingest to `media/06_videos_candidates_영상후보/`, set the
job's `downloaded: true`. Procedure: `~/.codex/skills/seedance-prompt-en/seedance-production.md`
from "Post-Generate continuation gate" on (read only that part). Video QC is the next
session (`seedance_qc`), not this one. Write the session result and end.
{result_contract(project, 'seedance')}"""


def harvest_then_produce_prompt(project: Path, jobs: list[str], blocks: list[str], remaining: list[str],
                                route: dict) -> str:
    """One session for the common steady state: collect the finished job, then submit the next
    block into the slot it freed. Two sessions per clip became one; the references are attached
    once, right before Generate, never re-attached while a slot is busy."""
    harvest = harvest_prompt(project, jobs, route).split('# SESSION RESULT CONTRACT')[0]
    harvest = harvest.replace('Write the session result and end.', '')
    produce = production_prompt(project, blocks, remaining, route)
    return (f"{harvest}\nIf every job above is downloaded, continue in this same session with the "
            f"production part below. If any is still In queue / Generating, do not attach or "
            f"generate: write PARTIAL / IN_QUEUE and end.\n\n{produce}")


def provider_slots(project: Path, model: str | None = None, credits: bool = False) -> int:
    if credits:
        return RUNWAY_ACTIVE_SLOTS
    return UNLIMITED_25_SLOTS if (model or '').startswith('Seedance 2.5') else RUNWAY_ACTIVE_SLOTS


def hold_active() -> dict:
    """Fail closed: a hold file that exists but cannot be read still holds."""
    if not HOLD_PATH.exists():
        return {}
    data = _json(HOLD_PATH)
    return data or {'reason': 'UNREADABLE_HOLD_FILE', 'path': str(HOLD_PATH)}


def write_hold(reason: str, project: Path | None = None, evidence: str = '') -> dict:
    current = hold_active()
    if current:
        return current
    data = {'held_at': dt.datetime.now().astimezone().isoformat(timespec='seconds'), 'reason': reason,
            'project': str(project) if project else None, 'block': None, 'evidence': evidence[:400]}
    _write_json(HOLD_PATH, data)
    return data


def clear_hold(approval_quote: str) -> dict:
    if os.environ.get('VIDEO_TEAM_LANE'):
        raise SystemExit('HOLD_CLEAR_FROM_LANE_REFUSED: only the director, after the user handled the warning, clears it')
    if not approval_quote.strip():
        raise SystemExit('HOLD_CLEAR_REQUIRES_USER_QUOTE: the user must confirm the Runway warning was handled')
    current = hold_active()
    if HOLD_PATH.exists():
        archive = HOLD_PATH.with_name(HOLD_PATH.stem + '.cleared.jsonl')
        with archive.open('a', encoding='utf-8') as f:
            f.write(json.dumps({**current, 'cleared_at': dt.datetime.now().astimezone().isoformat(timespec='seconds'),
                                'approval_quote': approval_quote.strip()}, ensure_ascii=False) + '\n')
        HOLD_PATH.unlink()
    return {'cleared': bool(current), 'previous': current}


USER_APPROVAL_STAGES = {'concept', 'storyboard'}


def user_gate(project: Path, status: dict) -> dict | None:
    """A preprod point where the director must ask the user instead of starting a session."""
    p = str(project)
    for item in status.get('stages') or []:
        stage, state = item.get('stage'), item.get('state')
        if state == 'LOCKED':
            continue
        if state == 'DRAFT' and stage in USER_APPROVAL_STAGES:
            return {'action': 'ASK_USER', 'gate': f'{stage}_approval',
                    'show': f'preprod/{ {"concept": "00_concept/concept_options.md", "storyboard": "02_storyboard/storyboard.json"}[stage] }',
                    'commands': [f'video-codex-runtime preprod lock --project {p} --stage {stage} '
                                 '--approval-quote "<user words>"']}
        if state == 'DRAFT':
            return {'action': 'LOCK_STAGE', 'gate': stage,
                    'commands': [f'video-codex-runtime preprod lock --project {p} --stage {stage}']}
        return None
    rows = status.get('shelf') or []
    if rows and all(r.get('state') in {'LOCKED', 'RELEASED'} for r in rows) \
            and any(r.get('state') == 'LOCKED' for r in rows):
        return {'action': 'ASK_USER', 'gate': 'shelf_release',
                'show': [f"preprod/04_shelf/{r['block_id']}/prompt.txt" for r in rows if r.get('state') == 'LOCKED'],
                'commands': [f'video-codex-runtime preprod shelf-release --project {p} --blocks ALL_LOCKED '
                             '--approval-quote "<user words>"']}
    return None


def read_result(project: Path, lane: str) -> dict:
    return _json(project / 'lanes' / lane / RESULT_NAME)


def wait(project: Path, lane: str, pid_running, timeout_min: float = 10, poll_s: float = 15) -> dict:
    """Foreground wait for the one lane session; returns a compact result for the director."""
    lane_dir = project / 'lanes' / lane
    try:
        pid = int((lane_dir / 'pid').read_text().strip())
    except (OSError, ValueError):
        pid = None
    deadline = time.monotonic() + timeout_min * 60
    while pid and pid_running(pid) and time.monotonic() < deadline:
        time.sleep(poll_s)
    running = bool(pid and pid_running(pid))
    status = _json(lane_dir / 'status.json')
    out = {'lane': lane, 'pid': pid, 'running': running, 'lane_status': status.get('status')}
    if running:
        out['next'] = 'still running: wait again (no new session)'
        return out
    result = read_result(project, lane)
    if result:
        out['result'] = result
    else:
        out['result'] = {'status': 'NO_RESULT'}
        last = Path(status.get('result') or lane_dir / 'result.md')
        if last.is_file():
            out['last_message_tail'] = last.read_text(encoding='utf-8', errors='ignore')[-1200:]
    if status.get('status') in {'LAUNCHING', 'RUNNING'}:
        # the process is gone: record it so gates and the next dispatch stop seeing a live owner
        rs = (result or {}).get('status')
        status.update({'status': {'DONE': 'DONE', 'PARTIAL': 'PARTIAL_BLOCKED'}.get(rs, 'BLOCKED' if rs else 'FAILED'),
                       'result_status': rs or 'NO_RESULT',
                       'reason_code': (result or {}).get('reason_code') or ('DEAD_NO_RESULT' if not result else None),
                       'ended_at': dt.datetime.now().isoformat(timespec='seconds')})
        _write_json(lane_dir / 'status.json', status)
        out['lane_status'] = status['status']
    return out


def _write_json(path: Path, value: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f'.{path.name}.{os.getpid()}.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(tmp, path)


def _json(path: Path) -> dict:
    try:
        value = json.loads(Path(path).read_text(encoding='utf-8'))
        return value if isinstance(value, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}
