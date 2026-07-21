#!/usr/bin/env python3
"""Codex App image-generation CLI for video-codex-runtime.

Uses Codex App Server JSON-RPC `imageGeneration` items. No Safari, no browser,
no Computer Use, no Gemini/FAL/OpenAI Images wrapper. The generated PNG is
extracted from the Codex App runtime response and written to disk.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import select
import subprocess
import sys
import time
from pathlib import Path

CODEX = "/opt/homebrew/bin/codex"


def eprint(*args):
    print(*args, file=sys.stderr)


class CodexRpc:
    def __init__(self):
        env = os.environ.copy()
        env["HOME"] = os.environ.get("VIDEO_TEAM_HOME", str(Path.home()))
        self.p = subprocess.Popen(
            [CODEX, "app-server", "--listen", "stdio://"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            bufsize=1,
        )
        self.next_id = 1
        self.responses = {}
        self.notifications = []

    def close(self):
        if self.p.poll() is None:
            self.p.terminate()
            try:
                self.p.wait(timeout=5)
            except Exception:
                self.p.kill()

    def send(self, method: str, params=None) -> int:
        i = self.next_id
        self.next_id += 1
        obj = {"jsonrpc": "2.0", "id": i, "method": method}
        if params is not None:
            obj["params"] = params
        self.p.stdin.write(json.dumps(obj, ensure_ascii=False) + "\n")
        self.p.stdin.flush()
        return i

    def pump(self, timeout=0.5):
        end = time.time() + timeout
        while time.time() < end:
            r, _, _ = select.select([self.p.stdout, self.p.stderr], [], [], 0.1)
            for f in r:
                line = f.readline()
                if not line:
                    continue
                if f is self.stderr:
                    eprint(line.rstrip())
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                if "id" in obj:
                    self.responses[obj["id"]] = obj
                else:
                    self.notifications.append(obj)

    @property
    def stderr(self):
        return self.p.stderr

    def wait_id(self, i: int, timeout=60):
        end = time.time() + timeout
        while time.time() < end and i not in self.responses:
            self.pump(0.5)
        return self.responses.get(i)


def iter_image_items(thread_read: dict):
    thread = (thread_read.get("result") or {}).get("thread") or {}
    for turn in thread.get("turns") or []:
        for item in turn.get("items") or []:
            if item.get("type") == "imageGeneration":
                yield item


def generate(prompt: str, out: Path, *, aspect_ratio: str, model: str, timeout: int) -> dict:
    out = out.expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    cwd = str(out.parent)
    rpc = CodexRpc()
    try:
        rid = rpc.send("initialize", {
            "clientInfo": {"name": "video-codex-image-cli", "version": "1"},
            "capabilities": {"experimentalApi": True},
        })
        init = rpc.wait_id(rid, 20)
        if not init or "error" in init:
            raise RuntimeError(f"initialize failed: {init}")

        rid = rpc.send("thread/start", {
            "cwd": cwd,
            "model": model,
            "approvalPolicy": "never",
            "sandbox": "workspace-write",
            "threadSource": "user",
            "sessionStartSource": "startup",
            "ephemeral": False,
            "baseInstructions": "Use Codex App image generation when asked for an image. Do not use Safari, browser, Computer Use, or external image provider CLIs. ImageGeneration response data is acceptable.",
            "developerInstructions": "Return imageGeneration items only through Codex App runtime. The client will decode the returned imageGeneration result into a PNG file.",
        })
        resp = rpc.wait_id(rid, 30)
        if not resp or "error" in resp:
            raise RuntimeError(f"thread/start failed: {resp}")
        thread_id = resp["result"]["thread"]["id"]

        aspect_note = {
            "landscape": "16:9 landscape composition",
            "portrait": "9:16 portrait composition",
            "square": "1:1 square composition",
        }.get(aspect_ratio, "16:9 landscape composition")
        user_prompt = (
            "Generate exactly one image using Codex App image generation. "
            "Do not use browser/computer-use/Safari/external provider CLI. "
            f"Prompt: {prompt.strip()}\n"
            f"Composition: {aspect_note}.\n"
            "No text, no logo, no watermark unless the prompt explicitly requires text."
        )
        rid = rpc.send("turn/start", {
            "threadId": thread_id,
            "input": [{"type": "text", "text": user_prompt}],
            "cwd": cwd,
            "model": model,
        })
        turn = rpc.wait_id(rid, 30)
        if not turn or "error" in turn:
            raise RuntimeError(f"turn/start failed: {turn}")

        # Do not wait for a full turn/completed notification. In Codex App Server,
        # imageGeneration result data is often available via thread/read long before
        # the assistant turn is considered complete. Poll thread/read and return as
        # soon as a PNG result is present; this avoids a needless 420s wait per image.
        deadline = time.time() + timeout
        last_read = None
        while time.time() < deadline:
            rpc.pump(0.5)
            rid = rpc.send("thread/read", {"threadId": thread_id, "includeTurns": True})
            read = rpc.wait_id(rid, 12)
            if read and "error" not in read:
                last_read = read
                images = [it for it in iter_image_items(read) if it.get("result")]
                if images:
                    break
            time.sleep(2)
        else:
            read = last_read
            images = [it for it in iter_image_items(read or {}) if it.get("result")]

        if not read or "error" in read:
            raise RuntimeError(f"thread/read failed or timed out: {read}")
        (out.parent / (out.name + ".thread_read.json")).write_text(json.dumps(read, ensure_ascii=False, indent=2), encoding="utf-8")

        if not images:
            raise RuntimeError("Codex App returned no imageGeneration result before timeout")
        item = images[-1]
        out.write_bytes(base64.b64decode(item["result"]))
        meta = {
            "provider": "codex-app-server-imageGeneration",
            "model": model,
            "image_generation_id": item.get("id"),
            "status": item.get("status"),
            "savedPath": item.get("savedPath"),
            "revisedPrompt": item.get("revisedPrompt"),
            "out": str(out),
            "bytes": out.stat().st_size,
            "aspect_ratio": aspect_ratio,
            "non_gui_browser": True,
            "no_computer_use": True,
        }
        out.with_suffix(out.suffix + ".provenance.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        return meta
    finally:
        rpc.close()


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate an image through Codex App runtime imageGeneration and write PNG to disk")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--prompt")
    ap.add_argument("--prompt-file")
    ap.add_argument("--out")
    ap.add_argument("--aspect-ratio", choices=["landscape", "square", "portrait"], default="landscape")
    ap.add_argument("--model", default=os.environ.get("VIDEO_CODEX_IMAGE_MODEL", "gpt-5.5"))
    ap.add_argument("--timeout", type=int, default=420)
    if "--size" in sys.argv:
        # Backward-compatible no-op for older template commands.
        pass
    args, _unknown = ap.parse_known_args()
    if args.check:
        print(json.dumps({
            "provider": "codex-app-server-imageGeneration",
            "available": Path(CODEX).exists(),
            "codex": CODEX,
            "non_gui_browser": True,
            "no_computer_use": True,
        }, ensure_ascii=False, indent=2))
        return 0 if Path(CODEX).exists() else 2
    if args.prompt_file:
        prompt = Path(args.prompt_file).read_text(encoding="utf-8")
    elif args.prompt:
        prompt = args.prompt
    else:
        eprint("missing --prompt or --prompt-file")
        return 2
    if not args.out:
        eprint("missing --out")
        return 2
    try:
        meta = generate(prompt, Path(args.out), aspect_ratio=args.aspect_ratio, model=args.model, timeout=args.timeout)
    except Exception as exc:
        eprint(str(exc))
        return 1
    print(json.dumps(meta, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
