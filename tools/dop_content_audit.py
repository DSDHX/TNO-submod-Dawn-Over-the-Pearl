#!/usr/bin/env python3
"""Audit the active KDocs design sheet against DOP focus/localisation files.

This is deliberately read-only.  It exists so the large design sheet can be
rechecked without copying its full contents into an assistant conversation.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ACTIVE_FOCUS_SECTIONS = {
    "战前（新）",
    "新战时",
    "（新）重建",
    "大国策树",
    "长实结尾",
    "富士通结尾",
    "（新）财界结局",
    "1962再现",
    "第二次坎通暴乱",
}

NON_FOCUS_ROWS = {
    "国策名",
    "可能可以复用",
    "说不定可以复用的↓",
    "年份",
    "产品名",
}


def normalize_name(value: str) -> str:
    table = str.maketrans(
        {
            "，": "",
            "。": "",
            "、": "",
            "！": "",
            "？": "",
            "…": "",
            "·": "",
            "《": "",
            "》": "",
            "“": "",
            "”": "",
            "‘": "",
            "’": "",
            "（": "",
            "）": "",
            "(": "",
            ")": "",
            " ": "",
            "\t": "",
        }
    )
    return value.strip().translate(table).lower()


def parse_sheet(path: Path) -> list[dict[str, object]]:
    section = ""
    rows: list[dict[str, object]] = []
    occurrence: Counter[str] = Counter()
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        heading = re.fullmatch(r"=====\s*(.*?)\s*=====", raw_line.strip())
        if heading:
            section = heading.group(1).strip()
            continue
        if section not in ACTIVE_FOCUS_SECTIONS:
            continue
        cells = [cell.strip() for cell in raw_line.split("\t")]
        if not cells:
            continue
        name = cells[0]
        if not name or name in NON_FOCUS_ROWS or name.isdigit():
            continue
        if name.startswith("可能可以复用") or name.startswith("说不定可以复用"):
            continue
        # Lines which merely contain a note/URL and no focus name are already
        # rejected by the empty first-cell check above.
        urls = re.findall(r"https?://[^\s⏎]+", raw_line)
        occurrence[name] += 1
        rows.append(
            {
                "section": section,
                "line": line_number,
                "name": name,
                "occurrence": occurrence[name],
                "urls": urls,
                "cells": cells,
            }
        )
    return rows


def parse_localisation(root: Path) -> tuple[dict[str, str], dict[str, list[str]]]:
    values: dict[str, str] = {}
    duplicates: dict[str, list[str]] = defaultdict(list)
    pattern = re.compile(r'^\s*([^\s:#]+):\d*\s+"(.*)"\s*$')
    for path in sorted((root / "localisation" / "simp_chinese").rglob("*.yml")):
        for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
            match = pattern.match(line)
            if not match:
                continue
            key, value = match.groups()
            if key in values:
                duplicates[key].append(str(path.relative_to(root)))
            values[key] = value
    return values, duplicates


def parse_focus_ids(root: Path) -> dict[str, str]:
    ids: dict[str, str] = {}
    pattern = re.compile(r"^\s*id\s*=\s*([^\s#}]+)")
    for path in sorted((root / "common" / "national_focus").glob("*.txt")):
        for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
            match = pattern.match(line)
            if match:
                ids[match.group(1)] = str(path.relative_to(root))
    return ids


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sheet", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    rows = parse_sheet(args.sheet)
    loc, duplicate_loc = parse_localisation(root)
    focus_ids = parse_focus_ids(root)
    current = {focus_id: loc.get(focus_id, "") for focus_id in focus_ids}

    current_names = [(focus_id, name) for focus_id, name in current.items() if name]
    exact_by_name: dict[str, list[str]] = defaultdict(list)
    norm_by_name: dict[str, list[str]] = defaultdict(list)
    for focus_id, name in current_names:
        exact_by_name[name].append(focus_id)
        norm_by_name[normalize_name(name)].append(focus_id)

    unique_rows: dict[str, dict[str, object]] = {}
    for row in rows:
        unique_rows.setdefault(str(row["name"]), row)

    matches: list[dict[str, object]] = []
    for name, row in unique_rows.items():
        if exact_by_name.get(name):
            kind = "exact"
            candidates = exact_by_name[name]
        elif norm_by_name.get(normalize_name(name)):
            kind = "normalized"
            candidates = norm_by_name[normalize_name(name)]
        else:
            kind = "fuzzy"
            ranked = sorted(
                (
                    (difflib.SequenceMatcher(None, normalize_name(name), normalize_name(current_name)).ratio(), focus_id, current_name)
                    for focus_id, current_name in current_names
                ),
                reverse=True,
            )[:5]
            candidates = [
                {"id": focus_id, "name": current_name, "score": round(score, 3)}
                for score, focus_id, current_name in ranked
            ]
        matches.append(
            {
                "section": row["section"],
                "line": row["line"],
                "name": name,
                "kind": kind,
                "candidates": candidates,
            }
        )

    result = {
        "sheet_rows": len(rows),
        "sheet_unique_names": len(unique_rows),
        "sheet_duplicate_names": dict(Counter(str(row["name"]) for row in rows) - Counter(unique_rows.keys())),
        "focus_ids": len(focus_ids),
        "localized_focus_ids": len(current_names),
        "match_counts": dict(Counter(item["kind"] for item in matches)),
        "matches": matches,
        "duplicate_localisation_keys": duplicate_loc,
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps({key: value for key, value in result.items() if key not in {"matches", "duplicate_localisation_keys"}}, ensure_ascii=False, indent=2))
        for item in matches:
            if item["kind"] == "fuzzy":
                print(f"{item['section']}\t{item['line']}\t{item['name']}\t{json.dumps(item['candidates'], ensure_ascii=False)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


