#!/usr/bin/env python3
"""File-backed image generation CLI for video-codex-runtime.

Non-GUI only. Never opens a browser. Writes image files directly to disk.
Provider order:
  1. OpenAI Images API via OPENAI_API_KEY

Usage:
  video-image-cli --check
  video-image-cli --prompt-file prompt.txt --out image.png --size 1024x1024
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import requests

HERMES_AGENT_ROOT = Path(os.environ.get("HERMES_AGENT_ROOT", str(Path.home() / ".hermes" / "hermes-agent")))
if str(HERMES_AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(HERMES_AGENT_ROOT))

OPENAI_IMAGES_URL = "https://api.openai.com/v1/images/generations"
DEFAULT_MODEL = os.environ.get("VIDEO_IMAGE_MODEL", "gpt-image-1")


def eprint(*args: object) -> None:
    print(*args, file=sys.stderr)


def provider_status() -> dict[str, Any]:
    hermes_available = False
    hermes_error = None
    try:
        from tools.image_generation_tool import check_image_generation_requirements, _resolve_fal_model
        hermes_available = bool(check_image_generation_requirements())
        try:
            hermes_model, _ = _resolve_fal_model()
        except Exception:
            hermes_model = None
    except Exception as exc:
        hermes_error = f"{type(exc).__name__}: {str(exc)[:200]}"
        hermes_model = None
    return {
        "providers": [
            {
                "provider": "openai-images",
                "model": DEFAULT_MODEL,
                "available": bool(os.environ.get("OPENAI_API_KEY")),
                "OPENAI_API_KEY": "SET" if os.environ.get("OPENAI_API_KEY") else "unset",
            },
            {
                "provider": "google-gemini-image",
                "model": os.environ.get("VIDEO_GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image-preview"),
                "available": bool(_get_secret("GEMINI_API_KEY") or _get_secret("GOOGLE_API_KEY")),
                "GEMINI_API_KEY": "SET" if (_get_secret("GEMINI_API_KEY") or _get_secret("GOOGLE_API_KEY")) else "unset",
            },
            {
                "provider": "hermes-image-gateway",
                "model": hermes_model,
                "available": hermes_available,
                "error": hermes_error,
            },
        ],
        "non_gui": True,
        "file_backed": True,
    }


def openai_generate(prompt: str, out: Path, *, size: str, model: str, quality: str | None, background: str | None) -> dict[str, Any]:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set; file-backed OpenAI image generation unavailable")

    payload: dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "size": size,
        "n": 1,
    }
    # gpt-image-1 supports quality/background in many deployments; omit when caller does not set.
    if quality:
        payload["quality"] = quality
    if background:
        payload["background"] = background

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    t0 = time.time()
    r = requests.post(OPENAI_IMAGES_URL, headers=headers, json=payload, timeout=300)
    if r.status_code >= 400:
        # Never print credentials; API body is safe enough but keep compact.
        raise RuntimeError(f"OpenAI Images API error HTTP {r.status_code}: {r.text[:1200]}")
    data = r.json()
    item = (data.get("data") or [{}])[0]
    b64 = item.get("b64_json")
    url = item.get("url")
    out.parent.mkdir(parents=True, exist_ok=True)
    if b64:
        out.write_bytes(base64.b64decode(b64))
    elif url:
        rr = requests.get(url, timeout=300)
        rr.raise_for_status()
        out.write_bytes(rr.content)
    else:
        raise RuntimeError(f"OpenAI Images API returned no b64_json/url: {json.dumps(data)[:1000]}")

    meta = {
        "provider": "openai-images",
        "model": model,
        "size": size,
        "quality": quality,
        "background": background,
        "out": str(out),
        "bytes": out.stat().st_size,
        "elapsed_sec": round(time.time() - t0, 2),
        "created": data.get("created"),
        "revised_prompt": item.get("revised_prompt"),
        "non_gui": True,
        "file_backed": True,
    }
    meta_path = out.with_suffix(out.suffix + ".provenance.json")
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return meta


def _secret_from_zshrc(name: str) -> str | None:
    """Read a local shell-exported key without printing it. Do not persist."""
    import re
    z = Path.home() / ".zshrc"
    if not z.exists():
        return None
    text = z.read_text(encoding="utf-8", errors="ignore")
    m = re.search(rf"export\s+{re.escape(name)}=(['\"])(.*?)\1", text)
    return m.group(2) if m else None


def _get_secret(name: str) -> str | None:
    return os.environ.get(name) or _secret_from_zshrc(name)


def gemini_generate(prompt: str, out: Path, *, model: str, aspect_ratio: str) -> dict[str, Any]:
    """Generate through Google Gemini image API without GUI/browser."""
    key = _get_secret("GEMINI_API_KEY") or _get_secret("GOOGLE_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY/GOOGLE_API_KEY is not set")
    t0 = time.time()
    size_hint = {
        "landscape": "Use a cinematic 16:9 landscape composition.",
        "portrait": "Use a vertical 9:16 portrait composition.",
        "square": "Use a square 1:1 composition.",
    }.get(aspect_ratio, "Use a square 1:1 composition.")
    payload = {
        "contents": [{"parts": [{"text": prompt.strip() + "\n\n" + size_hint}]}],
        "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    r = requests.post(url, json=payload, timeout=300)
    if r.status_code >= 400:
        raise RuntimeError(f"Gemini image API error HTTP {r.status_code}: {r.text[:1200]}")
    data = r.json()
    img_b64 = None
    mime = None
    for cand in data.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            inline = part.get("inlineData") or part.get("inline_data")
            if inline and inline.get("data"):
                img_b64 = inline["data"]
                mime = inline.get("mimeType") or inline.get("mime_type")
                break
        if img_b64:
            break
    if not img_b64:
        raise RuntimeError(f"Gemini returned no inline image data: {json.dumps(data)[:1200]}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(base64.b64decode(img_b64))
    meta = {
        "provider": "google-gemini-image",
        "model": model,
        "aspect_ratio": aspect_ratio,
        "mime_type": mime,
        "out": str(out),
        "bytes": out.stat().st_size,
        "elapsed_sec": round(time.time() - t0, 2),
        "non_gui": True,
        "file_backed": True,
    }
    out.with_suffix(out.suffix + ".provenance.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return meta


def hermes_generate(prompt: str, out: Path, *, aspect_ratio: str) -> dict[str, Any]:
    """Generate through Hermes' configured non-GUI image gateway/tool, then download to file."""
    from tools.image_generation_tool import image_generate_tool, _resolve_fal_model
    model_id, _meta = _resolve_fal_model()
    t0 = time.time()
    raw = image_generate_tool(prompt=prompt, aspect_ratio=aspect_ratio)
    data = json.loads(raw)
    if not data.get("success") or not data.get("image"):
        raise RuntimeError(f"Hermes image gateway failed: {json.dumps(data, ensure_ascii=False)[:1200]}")
    url = data["image"]
    out.parent.mkdir(parents=True, exist_ok=True)
    rr = requests.get(url, timeout=300)
    rr.raise_for_status()
    out.write_bytes(rr.content)
    meta = {
        "provider": "hermes-image-gateway",
        "model": model_id,
        "aspect_ratio": aspect_ratio,
        "source_url": url,
        "out": str(out),
        "bytes": out.stat().st_size,
        "elapsed_sec": round(time.time() - t0, 2),
        "non_gui": True,
        "file_backed": True,
    }
    out.with_suffix(out.suffix + ".provenance.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return meta


def main() -> int:
    ap = argparse.ArgumentParser(description="Non-GUI file-backed image generation for video-codex-runtime")
    ap.add_argument("--check", action="store_true", help="Print provider status and exit")
    ap.add_argument("--prompt", help="Prompt text")
    ap.add_argument("--prompt-file", help="Prompt file path")
    ap.add_argument("--out", help="Output image path, e.g. /path/ref.png")
    ap.add_argument("--size", default=os.environ.get("VIDEO_IMAGE_SIZE", "1024x1024"), help="Image size")
    ap.add_argument("--model", default=DEFAULT_MODEL, help="Image model")
    ap.add_argument("--quality", default=os.environ.get("VIDEO_IMAGE_QUALITY"), help="Provider quality option")
    ap.add_argument("--background", default=os.environ.get("VIDEO_IMAGE_BACKGROUND"), help="Provider background option")
    ap.add_argument("--aspect-ratio", default=os.environ.get("VIDEO_IMAGE_ASPECT_RATIO", "square"), choices=["landscape", "square", "portrait"], help="Image aspect ratio")
    ap.add_argument("--gemini-model", default=os.environ.get("VIDEO_GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image-preview"), help="Gemini image model")
    ap.add_argument("--dry-run", action="store_true", help="Validate inputs and print planned request without generating")
    args = ap.parse_args()

    if args.check:
        status = provider_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
        available = any(p.get("available") for p in status.get("providers", []))
        return 0 if available else 2

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
    out = Path(args.out).expanduser().resolve()

    if args.dry_run:
        print(json.dumps({
            "provider": "auto-file-backed",
            "openai_model": args.model,
            "hermes_aspect_ratio": args.aspect_ratio,
            "size": args.size,
            "out": str(out),
            "prompt_chars": len(prompt),
            "OPENAI_API_KEY": "SET" if os.environ.get("OPENAI_API_KEY") else "unset",
            "non_gui": True,
            "file_backed": True,
            "would_generate": bool(os.environ.get("OPENAI_API_KEY")) or any(p.get("available") for p in provider_status().get("providers", [])),
        }, ensure_ascii=False, indent=2))
        return 0

    try:
        if os.environ.get("OPENAI_API_KEY"):
            meta = openai_generate(prompt, out, size=args.size, model=args.model, quality=args.quality, background=args.background)
        elif _get_secret("GEMINI_API_KEY") or _get_secret("GOOGLE_API_KEY"):
            meta = gemini_generate(prompt, out, model=args.gemini_model, aspect_ratio=args.aspect_ratio)
        else:
            meta = hermes_generate(prompt, out, aspect_ratio=args.aspect_ratio)
    except Exception as exc:
        eprint(str(exc))
        return 1
    print(json.dumps(meta, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
