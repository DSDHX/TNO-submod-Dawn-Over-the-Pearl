#!/usr/bin/env python3
"""Build a compact ownership/reference inventory for every event in this mod."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

from restore_dop_focus_layout import FILES, focus_blocks, matching_brace


EVENT_START_RE = re.compile(r"(?m)^[ \t]*(country_event|news_event|state_event)[ \t]*=[ \t]*\{")
ID_RE = re.compile(r"(?m)^[ \t]*id[ \t]*=[ \t]*([^\s#}]+)")
TITLE_RE = re.compile(r"(?m)^[ \t]*title[ \t]*=[ \t]*([^\s#{}]+)")
CALL_RE = re.compile(r"(?:country_event|news_event|state_event)[ \t]*=[ \t]*\{[^{}\n]*?\bid[ \t]*=[ \t]*([^\s}]+)")
LOC_RE = re.compile(r'^\s*([^\s:#]+):\d*\s+"(.*)"\s*$')


def loc_values(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted((root / "localisation" / "simp_chinese").rglob("*.yml")):
        for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
            match = LOC_RE.match(line)
            if match:
                result[match.group(1)] = match.group(2)
    return result


def event_blocks(text: str) -> list[tuple[str, str, int]]:
    result: list[tuple[str, str, int]] = []
    for match in EVENT_START_RE.finditer(text):
        opening = text.find("{", match.start(), match.end())
        closing = matching_brace(text, opening)
        block = text[match.start() : closing + 1]
        id_match = ID_RE.search(block)
        if id_match:
            result.append((id_match.group(1), block, match.start()))
    return result


def compact(text: str, limit: int = 220) -> str:
    text = text.replace("\\n", " / ")
    text = re.sub(r"§.", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= limit else text[: limit - 1] + "…"


def focus_callers(root: Path) -> dict[str, list[dict[str, str]]]:
    result: dict[str, list[dict[str, str]]] = defaultdict(list)
    for relative in FILES:
        text = (root / relative).read_text(encoding="utf-8-sig")
        for block in focus_blocks(text):
            for event_id in CALL_RE.findall(block.text):
                result[event_id].append({"focus": block.focus_id, "file": relative})
    return result


def all_references(root: Path) -> dict[str, list[str]]:
    result: dict[str, set[str]] = defaultdict(set)
    roots = [root / "common", root / "events"]
    for source_root in roots:
        for path in sorted(source_root.rglob("*.txt")):
            relative = str(path.relative_to(root)).replace("\\", "/")
            text = path.read_text(encoding="utf-8-sig", errors="replace")
            for event_id in CALL_RE.findall(text):
                result[event_id].add(relative)
    return {key: sorted(value) for key, value in result.items()}


def inventory(root: Path) -> list[dict[str, object]]:
    loc = loc_values(root)
    focus_refs = focus_callers(root)
    refs = all_references(root)
    rows: list[dict[str, object]] = []
    occurrence: dict[str, int] = defaultdict(int)
    for path in sorted((root / "events").glob("*.txt")):
        relative = str(path.relative_to(root)).replace("\\", "/")
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        for event_id, block, offset in event_blocks(text):
            occurrence[event_id] += 1
            title_match = TITLE_RE.search(block)
            title_key = title_match.group(1) if title_match else f"{event_id}.t"
            title = loc.get(title_key, loc.get(f"{event_id}.t", ""))
            desc = loc.get(f"{event_id}.desc", "")
            rows.append(
                {
                    "id": event_id,
                    "occurrence": occurrence[event_id],
                    "file": relative,
                    "line": text.count("\n", 0, offset) + 1,
                    "title_key": title_key,
                    "title": title,
                    "description": compact(desc),
                    "triggered_only": bool(re.search(r"\bis_triggered_only\s*=\s*yes", block)),
                    "hidden": bool(re.search(r"(?m)^[ \t]*hidden\s*=\s*yes", block)),
                    "focus_callers": focus_refs.get(event_id, []),
                    "reference_files": refs.get(event_id, []),
                    "outgoing_events": sorted(set(CALL_RE.findall(block))),
                }
            )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    rows = inventory(root)
    payload = json.dumps(rows, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output = args.output if args.output.is_absolute() else root / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8", newline="\n")
        print(f"wrote {len(rows)} events to {output}")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
