#!/usr/bin/env python3
"""Select a small, attributable wiki packet for one video-generation block.

The router reads local files only. It never calls a model, Notion, a browser, or
an external search service. A curated catalog maps normalized production
attributes to exact wiki pages/sections. The resulting packet is bounded by a
character budget so the Seedance lane does not load the full wiki.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any, Final


ROUTER_VERSION: Final = "video-knowledge-router-v1"
DEFAULT_WIKI_ROOT: Final = Path("/Users/gnudas/wiki")
DEFAULT_CATALOG_REL: Final = Path("_meta/video-knowledge-catalog.json")
DEFAULT_BUDGET_CHARS: Final = 9000
DEFAULT_MAX_SELECTIONS: Final = 6

ATTRIBUTE_KEYS: Final = {
    "stages": ("stage", "stages"),
    "mediums": ("medium", "mediums", "visual_medium", "visual_mediums"),
    "project_types": ("project_type", "project_types", "project_mode", "project_modes"),
    "generation_modes": ("generation_mode", "generation_modes"),
    "shot_roles": ("shot_role", "shot_roles", "clip_role", "clip_roles"),
    "cameras": ("camera", "cameras", "camera_need", "camera_needs", "camera_family"),
    "risks": ("risk", "risks", "qc_risk", "qc_risks"),
    "methods": ("method", "methods", "generation_method", "generation_methods"),
    "audio": ("audio", "audio_route", "audio_routes"),
}

SCORE_WEIGHTS: Final = {
    "stages": 2,
    "mediums": 12,
    "project_types": 4,
    "generation_modes": 5,
    "shot_roles": 9,
    "cameras": 8,
    "risks": 10,
    "methods": 8,
    "audio": 7,
}


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid JSON: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _values(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [part.strip() for part in re.split(r"[,|]", value) if part.strip()]
    if isinstance(value, (list, tuple, set)):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()] if str(value).strip() else []


def _merge_attributes(target: dict[str, set[str]], source: Any) -> None:
    if not isinstance(source, dict):
        return
    for category, keys in ATTRIBUTE_KEYS.items():
        for key in keys:
            for value in _values(source.get(key)):
                target.setdefault(category, set()).add(value)


def _find_block(container: Any, block_id: str) -> dict[str, Any]:
    if isinstance(container, dict):
        value = container.get(block_id)
        return value if isinstance(value, dict) else {}
    if isinstance(container, list):
        for value in container:
            if isinstance(value, dict) and str(value.get("block_id")) == block_id:
                return value
    return {}


def _normalize_attributes(
    raw: dict[str, set[str]], aliases: dict[str, dict[str, str]],
) -> dict[str, list[str]]:
    normalized: dict[str, list[str]] = {}
    for category in ATTRIBUTE_KEYS:
        category_aliases = {
            str(key).casefold(): str(value)
            for key, value in (aliases.get(category) or {}).items()
        }
        values = set()
        for value in raw.get(category, set()):
            key = value.strip().casefold().replace(" ", "_").replace("-", "_")
            values.add(category_aliases.get(key, key))
        normalized[category] = sorted(values)
    return normalized


def collect_attributes(
    project: Path,
    block_id: str,
    catalog: dict[str, Any],
    attributes_path: Path | None = None,
) -> tuple[dict[str, list[str]], list[str], Path | None]:
    """Merge manifest, Planner attributes, and matching block metadata."""
    project = project.expanduser().resolve()
    raw: dict[str, set[str]] = {category: set() for category in ATTRIBUTE_KEYS}
    warnings: list[str] = []
    raw["stages"].add("seedance_prompting")

    manifest_path = project / "manifest.json"
    manifest = _read_json(manifest_path)
    _merge_attributes(raw, manifest)
    _merge_attributes(raw, manifest.get("global_rules"))
    _merge_attributes(raw, manifest.get("video_attributes"))
    _merge_attributes(raw, _find_block(manifest.get("blocks"), block_id))

    selected_attributes_path = attributes_path
    if selected_attributes_path is None:
        candidate = project / "lanes" / "planner" / "video_attributes.json"
        selected_attributes_path = candidate if candidate.exists() else None
    if selected_attributes_path is not None:
        selected_attributes_path = selected_attributes_path.expanduser().resolve()
        attrs = _read_json(selected_attributes_path)
        _merge_attributes(raw, attrs)
        _merge_attributes(raw, attrs.get("global"))
        _merge_attributes(raw, _find_block(attrs.get("blocks"), block_id))
    else:
        warnings.append("planner_video_attributes_missing")

    normalized = _normalize_attributes(raw, catalog.get("aliases") or {})
    if not normalized["mediums"]:
        warnings.append("visual_medium_unspecified_core_only")
    return normalized, warnings, selected_attributes_path


def _strip_frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---\n", 4)
    return text[end + 5:] if end >= 0 else text


def extract_section(text: str, heading: str | None) -> str:
    """Return one Markdown heading section, or the body when heading is absent."""
    body = _strip_frontmatter(text).strip()
    if not heading:
        return body
    lines = body.splitlines()
    target = heading.strip().casefold()
    start = None
    level = None
    for index, line in enumerate(lines):
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if match and match.group(2).strip().casefold() == target:
            start = index
            level = len(match.group(1))
            break
    if start is None or level is None:
        raise ValueError(f"heading not found: {heading}")
    end = len(lines)
    for index in range(start + 1, len(lines)):
        match = re.match(r"^(#{1,6})\s+", lines[index])
        if match and len(match.group(1)) <= level:
            end = index
            break
    return "\n".join(lines[start:end]).strip()


def _bounded_excerpt(text: str, limit: int) -> tuple[str, bool]:
    if len(text) <= limit:
        return text, False
    marker = "\n\n[선택 섹션이 문자 예산에 맞게 축약됨]"
    available = max(0, limit - len(marker))
    candidate = text[:available]
    paragraph = candidate.rfind("\n\n")
    if paragraph >= max(200, available // 2):
        candidate = candidate[:paragraph]
    return candidate.rstrip() + marker, True


def _inside(root: Path, path: Path) -> bool:
    try:
        return os.path.commonpath((str(root), str(path))) == str(root)
    except ValueError:
        return False


def validate_catalog(catalog_path: Path, wiki_root: Path) -> dict[str, Any]:
    catalog_path = catalog_path.expanduser().resolve()
    wiki_root = wiki_root.expanduser().resolve()
    catalog = _read_json(catalog_path)
    problems: list[str] = []
    ids: set[str] = set()
    for container_name in ("aliases", "no_route_required"):
        for category in (catalog.get(container_name) or {}):
            if category not in ATTRIBUTE_KEYS:
                problems.append(f"unknown_{container_name}_category:{category}")
    for entry in catalog.get("entries") or []:
        if not isinstance(entry, dict):
            problems.append("entry_not_object")
            continue
        entry_id = str(entry.get("id") or "")
        if not entry_id:
            problems.append("entry_missing_id")
        elif entry_id in ids:
            problems.append(f"duplicate_id:{entry_id}")
        ids.add(entry_id)
        path = (wiki_root / str(entry.get("path") or "")).resolve()
        if not _inside(wiki_root, path):
            problems.append(f"path_outside_wiki:{entry_id}:{path}")
            continue
        if not path.is_file():
            problems.append(f"missing_path:{entry_id}:{path}")
            continue
        try:
            extract_section(path.read_text(encoding="utf-8"), entry.get("section"))
        except (OSError, ValueError) as exc:
            problems.append(f"bad_section:{entry_id}:{exc}")
        for category in entry.get("require_match") or []:
            if category not in ATTRIBUTE_KEYS:
                problems.append(f"unknown_required_category:{entry_id}:{category}")
        for category in (entry.get("match") or {}):
            if category not in ATTRIBUTE_KEYS:
                problems.append(f"unknown_match_category:{entry_id}:{category}")
        for category in (entry.get("exclude") or {}):
            if category not in ATTRIBUTE_KEYS:
                problems.append(f"unknown_exclude_category:{entry_id}:{category}")
    return {
        "ok": not problems,
        "catalog": str(catalog_path),
        "wiki_root": str(wiki_root),
        "entry_count": len(catalog.get("entries") or []),
        "problems": problems,
    }


def _entry_score(
    entry: dict[str, Any], attributes: dict[str, list[str]],
) -> tuple[int, list[str]] | None:
    if entry.get("always"):
        return 1_000_000 + int(entry.get("priority") or 0), ["always"]

    match = entry.get("match") or {}
    exclude = entry.get("exclude") or {}
    for category, blocked in exclude.items():
        if set(_values(blocked)) & set(attributes.get(category) or []):
            return None

    reasons: list[str] = []
    score = int(entry.get("priority") or 0)
    for category in entry.get("require_match") or []:
        wanted = set(_values(match.get(category)))
        actual = set(attributes.get(category) or [])
        overlap = wanted & actual
        if not overlap:
            return None
        reasons.append(f"{category}=" + ",".join(sorted(overlap)))
        score += SCORE_WEIGHTS.get(category, 1) * len(overlap)

    for category, wanted_raw in match.items():
        wanted = set(_values(wanted_raw))
        overlap = wanted & set(attributes.get(category) or [])
        if overlap and not any(reason.startswith(f"{category}=") for reason in reasons):
            reasons.append(f"{category}=" + ",".join(sorted(overlap)))
            score += SCORE_WEIGHTS.get(category, 1) * len(overlap)

    return (score, reasons) if reasons else None


def select_knowledge(
    project: Path,
    block_id: str,
    *,
    wiki_root: Path = DEFAULT_WIKI_ROOT,
    catalog_path: Path | None = None,
    attributes_path: Path | None = None,
    budget_chars: int = DEFAULT_BUDGET_CHARS,
    max_selections: int = DEFAULT_MAX_SELECTIONS,
) -> dict[str, Any]:
    project = project.expanduser().resolve()
    wiki_root = wiki_root.expanduser().resolve()
    catalog_path = (catalog_path or wiki_root / DEFAULT_CATALOG_REL).expanduser().resolve()
    catalog_report = validate_catalog(catalog_path, wiki_root)
    if not catalog_report["ok"]:
        raise ValueError("invalid knowledge catalog: " + "; ".join(catalog_report["problems"]))
    catalog = _read_json(catalog_path)
    attributes, warnings, used_attributes_path = collect_attributes(
        project, block_id, catalog, attributes_path)

    routable: dict[str, set[str]] = {category: set() for category in ATTRIBUTE_KEYS}
    for entry in catalog.get("entries") or []:
        for category, values in (entry.get("match") or {}).items():
            if category in routable:
                routable[category].update(_values(values))
    no_route_required = {
        category: set(_values(values))
        for category, values in (catalog.get("no_route_required") or {}).items()
        if category in ATTRIBUTE_KEYS
    }
    unrouted_attributes: dict[str, list[str]] = {}
    for category, values in attributes.items():
        missing = sorted(
            set(values)
            - routable.get(category, set())
            - no_route_required.get(category, set()))
        if missing and category != "stages":
            unrouted_attributes[category] = missing
            warnings.extend(
                f"unrouted_attribute:{category}:{value}" for value in missing)

    ranked: list[tuple[int, str, dict[str, Any], list[str]]] = []
    for entry in catalog.get("entries") or []:
        scored = _entry_score(entry, attributes)
        if scored is None:
            continue
        score, reasons = scored
        ranked.append((score, str(entry.get("id")), entry, reasons))
    ranked.sort(key=lambda row: (-row[0], row[1]))

    output_dir = project / "lanes" / "seedance" / "knowledge"
    output_dir.mkdir(parents=True, exist_ok=True)
    context_path = output_dir / f"{block_id}_context.md"
    receipt_path = output_dir / f"{block_id}_selection.json"

    header = (
        f"# {block_id} 선택형 영상 지식 패킷\n\n"
        f"- Router: `{ROUTER_VERSION}`\n"
        f"- Attributes: `{json.dumps(attributes, ensure_ascii=False, sort_keys=True)}`\n"
        "- 이 파일만 읽고 전체 위키를 추가로 펼치지 않는다. 새로운 실패 유형이나 규칙 충돌이 있을 때만 targeted wiki lookup을 한다.\n"
    )
    pieces = [header]
    used_chars = len(header)
    selected: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    for score, entry_id, entry, reasons in ranked:
        key = (str(entry.get("path")), str(entry.get("section") or ""))
        if key in seen or len(selected) >= max_selections:
            continue
        seen.add(key)
        path = (wiki_root / str(entry["path"])).resolve()
        raw_section = extract_section(path.read_text(encoding="utf-8"), entry.get("section"))
        entry_limit = int(entry.get("max_chars") or 4000)
        remaining = budget_chars - used_chars
        if remaining < 320 and not entry.get("always"):
            continue
        excerpt, truncated = _bounded_excerpt(raw_section, min(entry_limit, max(320, remaining)))
        piece = (
            f"\n---\n\n## 지식 선택: {entry_id}\n\n"
            f"출처: `{path}`"
            + (f" · 섹션: `{entry.get('section')}`" if entry.get("section") else "")
            + f" · 선택 이유: `{', '.join(reasons)}`\n\n{excerpt}\n"
        )
        if used_chars + len(piece) > budget_chars:
            allowed = budget_chars - used_chars
            if allowed < 320 and not entry.get("always"):
                continue
            piece, extra_truncated = _bounded_excerpt(piece, max(0, allowed))
            truncated = truncated or extra_truncated
        pieces.append(piece)
        used_chars += len(piece)
        selected.append({
            "id": entry_id,
            "path": str(path),
            "section": entry.get("section"),
            "score": score,
            "reasons": reasons,
            "priority_class": entry.get("priority_class"),
            "provenance": entry.get("provenance"),
            "source_sha256": _sha256_file(path),
            "excerpt_chars": len(piece),
            "truncated": truncated,
        })

    context = "".join(pieces).rstrip() + "\n"
    if len(context) > budget_chars:
        context = context[:budget_chars].rstrip() + "\n"
        warnings.append("context_hard_truncated")
    context_path.write_text(context, encoding="utf-8")

    attributes_json = json.dumps(attributes, ensure_ascii=False, sort_keys=True).encode("utf-8")
    identity_payload = json.dumps({
        "router_version": ROUTER_VERSION,
        "block_id": block_id,
        "attributes": attributes,
        "selected": [(item["id"], item["source_sha256"]) for item in selected],
    }, ensure_ascii=False, sort_keys=True).encode("utf-8")
    receipt = {
        "router_version": ROUTER_VERSION,
        "selection_id": _sha256_bytes(identity_payload)[:20],
        "project": str(project),
        "block_id": block_id,
        "created_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "attributes": attributes,
        "attributes_sha256": _sha256_bytes(attributes_json),
        "attributes_source": str(used_attributes_path) if used_attributes_path else None,
        "attributes_source_sha256": (
            _sha256_file(used_attributes_path) if used_attributes_path else None),
        "catalog": str(catalog_path),
        "catalog_sha256": _sha256_file(catalog_path),
        "budget_chars": budget_chars,
        "context_chars": len(context),
        "context": str(context_path),
        "context_sha256": _sha256_bytes(context.encode("utf-8")),
        "selected": selected,
        "unrouted_attributes": unrouted_attributes,
        "warnings": warnings,
    }
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    receipt["receipt"] = str(receipt_path)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    check = sub.add_parser("catalog-check")
    check.add_argument("--wiki-root", default=str(DEFAULT_WIKI_ROOT))
    check.add_argument("--catalog")
    select = sub.add_parser("select")
    select.add_argument("--project", required=True)
    select.add_argument("--block", required=True)
    select.add_argument("--attributes")
    select.add_argument("--wiki-root", default=str(DEFAULT_WIKI_ROOT))
    select.add_argument("--catalog")
    select.add_argument("--budget-chars", type=int, default=DEFAULT_BUDGET_CHARS)
    select.add_argument("--max-selections", type=int, default=DEFAULT_MAX_SELECTIONS)
    args = parser.parse_args()

    wiki_root = Path(args.wiki_root)
    catalog_path = Path(args.catalog) if args.catalog else wiki_root / DEFAULT_CATALOG_REL
    if args.cmd == "catalog-check":
        report = validate_catalog(catalog_path, wiki_root)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["ok"] else 1

    receipt = select_knowledge(
        Path(args.project),
        args.block,
        wiki_root=wiki_root,
        catalog_path=catalog_path,
        attributes_path=Path(args.attributes) if args.attributes else None,
        budget_chars=max(1000, args.budget_chars),
        max_selections=max(1, args.max_selections),
    )
    print(json.dumps({
        "selection_id": receipt["selection_id"],
        "block_id": receipt["block_id"],
        "context": receipt["context"],
        "receipt": receipt["receipt"],
        "context_chars": receipt["context_chars"],
        "selected_ids": [item["id"] for item in receipt["selected"]],
        "warnings": receipt["warnings"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
