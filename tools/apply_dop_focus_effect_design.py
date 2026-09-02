#!/usr/bin/env python3
"""Replace every 260902A generic reward package with bespoke direct effects."""

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path

from dop_focus_effect_design import DESIGN_ROWS, Design
from dop_focus_effect_design_core import CORE_DESIGN_ROWS
from dop_focus_effect_design_endings import ENDING_DESIGN_ROWS
from restore_dop_focus_layout import (
    FILES,
    extract_field,
    focus_blocks,
    read_text,
    write_text,
)


PACKAGE_RE = re.compile(r"^(?P<indent>[ \t]*)DOP_GNG_reward_[A-Za-z0-9_]+\s*=\s*yes\s*$")
OLD_MARKER_RE = re.compile(
    r"^[ \t]*# DOP CONTENT FLOW 260902A (?:reward|numeric ending only)\s*$"
)
LOC_RE = re.compile(r'^\s*([^\s:#]+):\d*\s+"(.*)"\s*$')


def designs() -> dict[str, Design]:
    rows = DESIGN_ROWS + CORE_DESIGN_ROWS + ENDING_DESIGN_ROWS
    result: dict[str, Design] = {}
    for focus_id, item in rows:
        if focus_id in result:
            raise ValueError(f"Duplicate design id: {focus_id}")
        result[focus_id] = item
    return result


def package_focuses(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for relative in FILES:
        text = (root / relative).read_text(encoding="utf-8-sig")
        for block in focus_blocks(text):
            reward = extract_field(block.text, "completion_reward") or ""
            if re.search(r"(?m)^[ \t]*DOP_GNG_reward_[A-Za-z0-9_]+\s*=\s*yes\s*$", reward):
                if block.focus_id in result:
                    raise ValueError(f"Duplicate packaged focus: {block.focus_id}")
                result[block.focus_id] = relative
    return result


def render_lines(indent: str, item: Design, newline: str) -> list[str]:
    output = [
        f"{indent}# DOP BESPOKE 260902B axes: {' / '.join(item.axes)}{newline}",
        f"{indent}# {item.rationale}{newline}",
    ]
    for snippet in item.effects:
        for line in snippet.splitlines():
            output.append(f"{indent}{line}{newline}")
    return output


def transform_reward(reward: str, item: Design, newline: str) -> str:
    lines = reward.splitlines(keepends=True)
    transformed: list[str] = []
    inserted = False
    package_count = 0
    for raw in lines:
        logical = raw.rstrip("\r\n")
        if OLD_MARKER_RE.match(logical):
            continue
        match = PACKAGE_RE.match(logical)
        if match:
            package_count += 1
            if not inserted:
                transformed.extend(render_lines(match.group("indent"), item, newline))
                inserted = True
            continue
        transformed.append(raw)
    if package_count == 0 or not inserted:
        raise ValueError("Attempted to transform a reward without a package call")
    result = "".join(transformed)
    if "DOP_GNG_reward_" in result:
        raise AssertionError("Generic package call survived reward transformation")
    return result


def replace_reward(block: str, replacement: str) -> str:
    marker = re.search(r"(?m)^[ \t]*completion_reward[ \t]*=[ \t]*\{", block)
    if marker is None:
        raise ValueError("Focus block lacks completion_reward")
    current = extract_field(block, "completion_reward")
    if current is None:
        raise ValueError("Focus block lacks completion_reward span")
    start = block.find(current)
    return block[:start] + replacement + block[start + len(current) :]


def transform_file(root: Path, relative: str, mapping: dict[str, Design]) -> tuple[str, str, bool, int]:
    path = root / relative
    current, bom = read_text(path)
    newline = "\r\n" if "\r\n" in current else "\n"
    replacements: list[tuple[int, int, str]] = []
    count = 0
    for block in focus_blocks(current):
        reward = extract_field(block.text, "completion_reward") or ""
        if "DOP_GNG_reward_" not in reward:
            continue
        item = mapping[block.focus_id]
        new_reward = transform_reward(reward, item, newline)
        new_block = replace_reward(block.text, new_reward)
        replacements.append((block.start, block.end, new_block))
        count += 1
    rebuilt = current
    for start, end, replacement in reversed(replacements):
        rebuilt = rebuilt[:start] + replacement + rebuilt[end:]
    return current, rebuilt, bom, count


def localisation(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted((root / "localisation" / "simp_chinese").rglob("*.yml")):
        for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
            match = LOC_RE.match(line)
            if match:
                result[match.group(1)] = match.group(2)
    return result


def write_ledger(root: Path, path: Path, mapping: dict[str, Design], ownership: dict[str, str]) -> None:
    loc = localisation(root)
    lines = [
        "# DOP 国策独立效果设计台账",
        "",
        "本表由人工逐项设计数据生成。游戏文件内为直接效果，不调用通用奖励包；每项限定 1–3 个轴线。",
        "",
        "| 文件 | 国策 ID | 名称 | 轴线 | 设计理由 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for relative in FILES:
        ids = [focus_id for focus_id, owner in ownership.items() if owner == relative]
        for focus_id in ids:
            item = mapping[focus_id]
            title = loc.get(focus_id, "（无本地化名称）").replace("|", "\\|")
            reason = item.rationale.replace("|", "\\|")
            lines.append(
                f"| `{Path(relative).name}` | `{focus_id}` | {title} | {'、'.join(item.axes)} | {reason} |"
            )
    target = path if path.is_absolute() else root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--ledger", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    mapping = designs()
    ownership = package_focuses(root)

    missing = sorted(set(ownership) - set(mapping))
    extra = sorted(set(mapping) - set(ownership))
    if missing or extra:
        raise ValueError(f"Design coverage mismatch; missing={missing}, extra={extra}")

    fingerprints: dict[tuple[str, ...], list[str]] = defaultdict(list)
    for focus_id, item in mapping.items():
        if item.effects:
            fingerprints[item.effects].append(focus_id)
    duplicates = [ids for ids in fingerprints.values() if len(ids) > 1]
    if duplicates:
        raise ValueError(f"Identical bespoke effect sets remain: {duplicates}")

    total = 0
    changes: list[tuple[Path, str, bool]] = []
    for relative in FILES:
        current, rebuilt, bom, count = transform_file(root, relative, mapping)
        total += count
        print(f"{relative}: {count} bespoke focus design(s)")
        if current != rebuilt:
            changes.append((root / relative, rebuilt, bom))

    if total != len(mapping):
        raise AssertionError(f"Transformed {total} focuses but mapped {len(mapping)}")

    print(f"coverage={len(mapping)}; duplicate_effect_sets=0; files_to_change={len(changes)}")
    if args.apply:
        for path, text, bom in changes:
            write_text(path, text, bom)
        if args.ledger:
            write_ledger(root, args.ledger, mapping, ownership)
        print("bespoke effects applied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
