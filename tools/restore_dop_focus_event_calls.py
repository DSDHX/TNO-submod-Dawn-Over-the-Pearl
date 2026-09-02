#!/usr/bin/env python3
"""Restore authored top-level focus event calls from Git HEAD."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from restore_dop_focus_layout import (
    FILES,
    extract_field,
    focus_blocks,
    git_head_text,
    read_text,
    write_text,
)


EVENT_LINE_RE = re.compile(
    r"(?m)^[ \t]*country_event[ \t]*=[ \t]*\{[ \t]*id[ \t]*=[ \t]*([^\s}]+)[^\n}]*\}[ \t]*\r?$"
)


def block_map(text: str) -> dict[str, object]:
    return {block.focus_id: block for block in focus_blocks(text)}


def missing_event_lines(head_reward: str, current_reward: str) -> list[tuple[str, str]]:
    current_ids = set(EVENT_LINE_RE.findall(current_reward))
    result: list[tuple[str, str]] = []
    for match in EVENT_LINE_RE.finditer(head_reward):
        event_id = match.group(1)
        if event_id not in current_ids:
            result.append((event_id, match.group(0).lstrip(" \t")))
    return result


def add_event_lines(reward: str, lines: list[str], newline: str) -> str:
    opening_end = reward.find("{") + 1
    line_end = reward.find("\n", opening_end)
    if line_end < 0:
        raise ValueError("Single-line completion_reward is unsupported")
    indent_match = re.search(r"(?m)^(?P<indent>[ \t]+)\S", reward[line_end + 1 :])
    indent = indent_match.group("indent") if indent_match else "\t\t"
    insertion = "".join(f"{indent}{line}{newline}" for line in lines)
    return reward[: line_end + 1] + insertion + reward[line_end + 1 :]


def replace_reward(block: str, reward: str) -> str:
    current = extract_field(block, "completion_reward")
    if current is None:
        raise ValueError("Focus lacks completion_reward")
    start = block.find(current)
    return block[:start] + reward + block[start + len(current) :]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    changes: list[tuple[Path, str, bool]] = []
    restored = 0

    for relative in FILES:
        path = root / relative
        current, bom = read_text(path)
        head = git_head_text(root, relative)
        newline = "\r\n" if "\r\n" in current else "\n"
        current_map = block_map(current)
        replacements: list[tuple[int, int, str]] = []
        for head_block in focus_blocks(head):
            if head_block.focus_id == "DOP_GNG_recon_grand_wall_weak_foundation":
                continue  # Guangdong theatre remains explicitly out of scope.
            current_block = current_map[head_block.focus_id]
            head_reward = extract_field(head_block.text, "completion_reward") or ""
            current_reward = extract_field(current_block.text, "completion_reward") or ""
            missing = missing_event_lines(head_reward, current_reward)
            if not missing:
                continue
            ids = [event_id for event_id, _ in missing]
            print(f"{relative}:{head_block.focus_id} <- {', '.join(ids)}")
            restored += len(missing)
            new_reward = add_event_lines(current_reward, [line for _, line in missing], newline)
            new_block = replace_reward(current_block.text, new_reward)
            replacements.append((current_block.start, current_block.end, new_block))

        rebuilt = current
        for start, end, replacement in reversed(replacements):
            rebuilt = rebuilt[:start] + replacement + rebuilt[end:]
        if rebuilt != current:
            changes.append((path, rebuilt, bom))

    print(f"authored event calls to restore={restored}; files={len(changes)}")
    if args.apply:
        for path, text, bom in changes:
            write_text(path, text, bom)
        print("authored focus event calls restored")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
