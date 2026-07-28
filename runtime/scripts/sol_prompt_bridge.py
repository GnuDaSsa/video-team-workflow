#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shlex
import shutil
import subprocess
import tempfile
from pathlib import Path

from prompt_packet_utils import (
    LEAK_PATTERN,
    RUNTIME,
    build_packet,
    extract_json,
    validate_image,
    validate_seedance,
)

SOL_BIN = os.environ.get("SOL_BIN") or shutil.which("codex") or "/opt/homebrew/bin/codex"
SOL_MODEL = os.environ.get("SOL_MODEL", "gpt-5.6-sol")
SEEDANCE_VIDEO_PROMPT_MODEL = os.environ.get("SEEDANCE_VIDEO_PROMPT_MODEL", "gpt-5.6-sol")
SOL_REASONING_EFFORT = os.environ.get("SOL_REASONING_EFFORT", "high")
SOL_STANDARD = RUNTIME / "references" / "sol_prompting_handoff_standard.md"
RULEBOOK = RUNTIME / "references" / "seedance_prompting_rulebook.md"
LAST_RUN: dict[str, str | int | dict[str, int] | list[str] | None] = {}


def read_cli_version() -> str:
    proc = subprocess.run([SOL_BIN, "--version"], text=True, capture_output=True, timeout=20)
    return proc.stdout.strip() if proc.returncode == 0 else "UNKNOWN"


def parse_events(raw: str) -> dict[str, str | dict[str, int] | list[str] | None]:
    event_types: list[str] = []
    thread_id: str | None = None
    usage: dict[str, int] = {}
    for line in raw.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        event_type = event.get("type")
        if isinstance(event_type, str):
            event_types.append(event_type)
        if event_type == "thread.started" and isinstance(event.get("thread_id"), str):
            thread_id = event["thread_id"]
        if event_type == "turn.completed" and isinstance(event.get("usage"), dict):
            usage = {str(k): int(v) for k, v in event["usage"].items() if isinstance(v, int)}
    return {"thread_id": thread_id, "usage": usage, "event_types": event_types}


def live_log_path(project: Path, task: str, block: str, lane: str = "image_creator_01") -> Path:
    root = project / "lanes" / ("seedance" if task == "seedance" else lane) / "live_prompt_runtime"
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{block}.live.jsonl"
    path.touch(exist_ok=True)
    return path


def live_status_path(live_log: Path) -> Path:
    return live_log.with_suffix(".status.txt")


def write_live_status(live_log: Path, model: str, task: str, block: str, phase: str, detail: str) -> None:
    status = live_status_path(live_log)
    prompt_state = "작성 완료" if phase == "DELIVERED" else (detail if phase == "PROMPTING" else "대기")
    status.write_text(
        "\n".join(
            [
                f"MODEL: {model}   REASONING: {SOL_REASONING_EFFORT}   TASK: {task}",
                f"BLOCK: {block}",
                "",
                "핸드오프 요약: 완료",
                f"프롬프팅 내용: {prompt_state}",
                f"본모델 전달: {'완료' if phase == 'DELIVERED' else '대기'}",
                "",
                f"현재 단계: {phase}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def call_sol(packet: str, live_log: Path | None = None) -> str:
    if not Path(SOL_BIN).exists():
        raise SystemExit(f"BLOCKED_SOL_CLI_UNAVAILABLE: {SOL_BIN} not found")
    with tempfile.TemporaryDirectory(prefix="video-sol-prompt-") as tmp:
        workdir = Path(tmp)
        final_path = workdir / "final.txt"
        cmd = [
            SOL_BIN,
            "exec",
            "--ephemeral",
            "--skip-git-repo-check",
            "--ignore-user-config",
            "--ignore-rules",
            "--sandbox",
            "read-only",
            "--cd",
            str(workdir),
            "--model",
            SOL_MODEL,
            "--config",
            f'model_reasoning_effort="{SOL_REASONING_EFFORT}"',
            "--json",
            "--output-last-message",
            str(final_path),
            "-",
        ]
        if live_log is not None:
            with live_log.open("a", encoding="utf-8") as stream:
                stream.write(
                    json.dumps(
                        {
                            "type": "prompt_authoring.process_started",
                            "ts": dt.datetime.now().astimezone().isoformat(),
                            "model": SOL_MODEL,
                            "reasoning_effort": SOL_REASONING_EFFORT,
                            "command": shlex.join(cmd),
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
                stream.flush()
                proc = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                )
                assert proc.stdin is not None
                assert proc.stdout is not None
                proc.stdin.write(packet)
                proc.stdin.close()
                output_lines: list[str] = []
                for line in proc.stdout:
                    output_lines.append(line)
                    stream.write(line)
                    stream.flush()
                proc.stdout.close()
                proc.wait(timeout=900)
                raw_output = "".join(output_lines)
                stream.write(
                    json.dumps(
                        {
                            "type": "prompt_authoring.process_finished",
                            "ts": dt.datetime.now().astimezone().isoformat(),
                            "returncode": proc.returncode,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
                stream.flush()
        else:
            proc = subprocess.run(cmd, input=packet, text=True, capture_output=True, timeout=900)
            raw_output = proc.stdout
        if proc.returncode != 0:
            blob = raw_output
            low = blob.lower()
            if "requires a newer version of codex" in low:
                raise SystemExit(
                    "BLOCKED_SOL_CODEX_UPGRADE_REQUIRED: gpt-5.6-sol requires a newer Codex CLI. "
                    "Finish the LazyCodex/Codex update, start a new Codex session, then retry."
                )
            if any(token in low for token in ("log in", "login", "not authenticated", "unauthorized")):
                raise SystemExit(
                    "BLOCKED_SOL_AUTH_REQUIRED: Codex CLI login is required. "
                    "Use the normal logged-in Codex session; do not add an API key fallback."
                )
            raise SystemExit(f"BLOCKED_SOL_CLI_ERROR rc={proc.returncode}: {blob[-1200:]}")
        if not final_path.exists():
            raise SystemExit("SOL_OUTPUT_MISSING: Codex CLI completed without a final message")
        LAST_RUN.clear()
        LAST_RUN.update(parse_events(raw_output))
        LAST_RUN.update(
            {
                "model": SOL_MODEL,
                "reasoning_effort": SOL_REASONING_EFFORT,
                "codex_version": read_cli_version(),
                "stderr_tail": "",
            }
        )
        return final_path.read_text(encoding="utf-8")


def announce(project: Path, task: str, block: str, phase: str) -> None:
    tag = f"[sol {task}]"
    print(f"{tag} GPT-5.6 Sol {phase} model={SOL_MODEL} effort={SOL_REASONING_EFFORT} block={block}", flush=True)
    queue = project / "queues" / "retry_router_queue.jsonl"
    queue.parent.mkdir(parents=True, exist_ok=True)
    with queue.open("a", encoding="utf-8") as stream:
        stream.write(
            json.dumps(
                {
                    "ts": dt.datetime.now().astimezone().isoformat(),
                    "event": f"GPT56_SOL_PROMPT_AUTHORING_{phase.upper()}",
                    "tag": tag,
                    "task": task,
                    "block": block,
                    "model": SOL_MODEL,
                    "reasoning_effort": SOL_REASONING_EFFORT,
                },
                ensure_ascii=False,
            )
            + "\n"
        )


def verify_provenance(path: Path) -> dict[str, str | bool]:
    provenance = json.loads(path.read_text(encoding="utf-8"))
    pack = Path(provenance.get("prompt_pack", ""))
    packet = Path(provenance.get("packet", ""))
    pack_ok = pack.is_file() and hashlib.sha256(pack.read_bytes()).hexdigest() == provenance.get("pack_sha256")
    packet_ok = packet.is_file() and hashlib.sha256(packet.read_bytes()).hexdigest() == provenance.get("packet_sha256")
    # User decision 2026-07-28: one authoring model for image and video prompts.
    expected_model = SEEDANCE_VIDEO_PROMPT_MODEL if provenance.get("task") == "seedance" else "gpt-5.6-sol"
    model_ok = provenance.get("model") == expected_model
    verdict = "VERIFIED" if pack_ok and packet_ok and model_ok else "NOT_VERIFIED"
    return {
        "provenance": str(path),
        "pack_hash_ok": pack_ok,
        "packet_hash_ok": packet_ok,
        "model_ok": model_ok,
        "verdict": verdict,
    }


def attest_block(project: Path, block: str) -> dict[str, str | int | bool]:
    prompt_dir = project / "lanes" / "seedance" / "prompts"
    pack_path = prompt_dir / f"{block}_sol_prompt_pack.json"
    provenance_path = prompt_dir / f"{block}_sol_prompt_pack.sol_provenance.json"
    result: dict[str, str | int | bool] = {"block": block, "pack": str(pack_path)}
    if not pack_path.exists() or not provenance_path.exists():
        result["verdict"] = "NO_SOL_PACK_OR_PROVENANCE"
        return result
    pack = json.loads(pack_path.read_text(encoding="utf-8"))
    prompt = pack.get("prompt", "")
    provenance = verify_provenance(provenance_path)
    result.update(
        {
            "prompt_chars": len(prompt),
            "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
            "prompt_style_version": pack.get("prompt_style_version"),
            "authoring_contract": pack.get("authoring_contract"),
            "leak_check": "FAIL" if LEAK_PATTERN.search(prompt) else "PASS",
            "provenance_check": provenance["verdict"],
        }
    )
    result["verdict"] = (
        "ATTESTED"
        if result["leak_check"] == "PASS" and result["provenance_check"] == "VERIFIED"
        else "NOT_ATTESTED_DO_NOT_SUBMIT"
    )
    (prompt_dir / f"{block}_attestation.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


def write_pack(
    project: Path,
    task: str,
    block: str,
    lane: str,
    packet: str,
    raw: str,
    live_log: Path | None = None,
) -> Path:
    out_dir = project / "lanes" / ("seedance" if task == "seedance" else lane) / "prompts"
    out_dir.mkdir(parents=True, exist_ok=True)
    pack = extract_json(raw)
    errors = validate_seedance(pack) if task == "seedance" else validate_image(pack)
    if errors:
        retry_raw = call_sol(packet + "\n\n## PREVIOUS ATTEMPT ERRORS\n" + "\n".join(errors), live_log)
        pack = extract_json(retry_raw)
        errors = validate_seedance(pack) if task == "seedance" else validate_image(pack)
        raw = retry_raw
    if errors:
        failure = out_dir / f"{block}_sol_output_invalid.txt"
        failure.write_text(raw, encoding="utf-8")
        raise SystemExit(f"SOL_OUTPUT_INVALID: {errors} raw={failure}")
    packet_path = out_dir / f"{block}_sol_packet.md"
    pack_path = out_dir / f"{block}_sol_prompt_pack.json"
    packet_path.write_text(packet, encoding="utf-8")
    pack_path.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if task == "image":
        for item in pack:
            (out_dir / f"{item['reference_id']}.prompt.txt").write_text(item["prompt"].rstrip() + "\n", encoding="utf-8")
    else:
        lines = [f"# [sol seedance] {block} Seedance prompt", "", "## Prompt", "", pack["prompt"]]
        if pack.get("prompt_s2"):
            lines.extend(["", "## S2", "", pack["prompt_s2"]])
        (out_dir / f"{block}_sol_prompt_pack.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    provenance = {
        "model": SOL_MODEL,
        "reasoning_effort": SOL_REASONING_EFFORT,
        "task": task,
        "block": block,
        "ts": dt.datetime.now().astimezone().isoformat(),
        "packet": str(packet_path),
        "prompt_pack": str(pack_path),
        "packet_sha256": hashlib.sha256(packet_path.read_bytes()).hexdigest(),
        "pack_sha256": hashlib.sha256(pack_path.read_bytes()).hexdigest(),
        "raw_output_sha256": hashlib.sha256(raw.encode()).hexdigest(),
        "codex_run": LAST_RUN,
        "prompt_style_version": pack.get("prompt_style_version") if task == "seedance" else None,
        "authoring_contract": pack.get("authoring_contract") if task == "seedance" else None,
        "handoff_standard": str(SOL_STANDARD),
        "rulebook": str(RULEBOOK),
    }
    (out_dir / f"{block}_sol_prompt_pack.sol_provenance.json").write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return pack_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify")
    parser.add_argument("--attest")
    parser.add_argument("--attest-project")
    parser.add_argument("--project")
    parser.add_argument("--task", choices=["seedance", "image"])
    parser.add_argument("--block")
    parser.add_argument("--lane", default="image_creator_01")
    parser.add_argument("--refs", nargs="*", default=[])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.verify:
        print(json.dumps(verify_provenance(Path(args.verify).expanduser()), ensure_ascii=False, indent=2))
        return 0
    if args.attest:
        if not args.attest_project:
            raise SystemExit("--attest requires --attest-project")
        result = attest_block(Path(args.attest_project).expanduser().resolve(), args.attest)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get("verdict") == "ATTESTED" else 1
    if not args.project or not args.task or not args.block:
        raise SystemExit("--project, --task, and --block are required")
    global SOL_MODEL
    if args.task == "seedance" and not os.environ.get("SOL_MODEL"):
        SOL_MODEL = SEEDANCE_VIDEO_PROMPT_MODEL
    if args.block.upper().startswith("CHAR") or any(ref.upper().startswith("CHAR") for ref in args.refs):
        raise SystemExit("REFUSED_CHARACTER_SHEET_TASK: use the character-sheet standard, not the Sol bridge")
    project = Path(args.project).expanduser().resolve()
    packet = build_packet(project, args.task, args.block, args.refs)
    if args.dry_run:
        output = project / "lanes" / ("seedance" if args.task == "seedance" else args.lane) / "prompts"
        output.mkdir(parents=True, exist_ok=True)
        packet_path = output / f"{args.block}_sol_packet.md"
        packet_path.write_text(packet, encoding="utf-8")
        print(json.dumps({"packet": str(packet_path), "dry_run": True}))
        return 0
    live_log = live_log_path(project, args.task, args.block, args.lane)
    write_live_status(live_log, SOL_MODEL, args.task, args.block, "HANDOFF", "대기")
    announce(project, args.task, args.block, "started")
    write_live_status(live_log, SOL_MODEL, args.task, args.block, "PROMPTING", "Terra high 작성 중")
    raw = call_sol(packet, live_log)
    pack_path = write_pack(project, args.task, args.block, args.lane, packet, raw, live_log)
    write_live_status(live_log, SOL_MODEL, args.task, args.block, "DELIVERED", "작성 완료")
    announce(project, args.task, args.block, "completed")
    print(json.dumps({"tag": f"[sol {args.task}]", "prompt_pack": str(pack_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
