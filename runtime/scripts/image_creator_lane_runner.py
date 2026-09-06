#!/usr/bin/env python3
"""Retired compatibility entrypoint; never starts another Codex owner or Image API."""
import json

def main():
    print(json.dumps({"ok": False, "status": "USE_CURRENT_OWNER_BUILTIN_IMAGEGEN",
        "next_action": "Use video-codex-runtime prepare-image-batch, then current-owner built-in image_gen with verified references; no new task or automatic API fallback."}))
    return 2

if __name__ == '__main__':
    raise SystemExit(main())
