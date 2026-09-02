#!/usr/bin/env python3
"""Restore authored focus layout from Git HEAD while preserving rewards.

The 260902A pass mixed layout edits with completion rewards in the same files.
This tool rebuilds each focus block from the Git HEAD version, then transplants
only the current ``completion_reward`` block.  The one intentional post-HEAD
``select_effect`` which starts the southwest-war transition is preserved.

The script is deliberately narrow: it refuses to run if focus IDs were added,
removed, or duplicated, so it cannot silently discard new focus content.
"""

from __future__ import annotations

import argparse
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


FILES = (
    "common/national_focus/dop_sony-opening.txt",
    "common/national_focus/dop_sony-japan_prewar.txt",
    "common/national_focus/dop_sony-japan_reconstruction.txt",
    "common/national_focus/dop_sony-japan_core.txt",
    "common/national_focus/dop_sony-japan_ending1_lee.txt",
    "common/national_focus/dop_sony-japan_ending2_ibuka.txt",
    "common/national_focus/dop_sony-japan_ending3_hitachi.txt",
)

PRESERVE_SELECT_EFFECT = {"DOP_GNG_faux_opening"}


@dataclass(frozen=True)
class FocusBlock:
    focus_id: str
    start: int
    end: int
    text: str


def matching_brace(text: str, opening: int) -> int:
    depth = 0
    quoted = False
    escaped = False
    comment = False
    for index in range(opening, len(text)):
        char = text[index]
        if comment:
            if char in "\r\n":
                comment = False
            continue
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
            continue
        if char == "#":
            comment = True
        elif char == '"':
            quoted = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index
    raise ValueError(f"Unmatched opening brace at offset {opening}")


def brace_depth_at(text: str, stop: int) -> int:
    depth = 0
    quoted = False
    escaped = False
    comment = False
    for char in text[:stop]:
        if comment:
            if char in "\r\n":
                comment = False
            continue
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
            continue
        if char == "#":
            comment = True
        elif char == '"':
            quoted = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
    return depth


def field_span(block: str, field: str) -> tuple[int, int] | None:
    pattern = re.compile(
        rf"(?m)^[ \t]*{re.escape(field)}[ \t]*=[ \t]*\{{"
    )
    for match in pattern.finditer(block):
        if brace_depth_at(block, match.start()) != 1:
            continue
        opening = block.find("{", match.start(), match.end())
        closing = matching_brace(block, opening)
        return match.start(), closing + 1
    return None


def focus_id(block: str) -> str:
    pattern = re.compile(r"(?m)^[ \t]*id[ \t]*=[ \t]*([^\s#}]+)")
    for match in pattern.finditer(block):
        if brace_depth_at(block, match.start()) == 1:
            return match.group(1)
    raise ValueError("Focus block has no top-level id")


def focus_blocks(text: str) -> list[FocusBlock]:
    pattern = re.compile(r"(?m)^[ \t]*(?:shared_focus|focus)[ \t]*=[ \t]*\{")
    blocks: list[FocusBlock] = []
    for match in pattern.finditer(text):
        opening = text.find("{", match.start(), match.end())
        closing = matching_brace(text, opening)
        block_text = text[match.start() : closing + 1]
        blocks.append(
            FocusBlock(
                focus_id=focus_id(block_text),
                start=match.start(),
                end=closing + 1,
                text=block_text,
            )
        )
    return blocks


def unique_map(blocks: list[FocusBlock], source: str) -> dict[str, FocusBlock]:
    result: dict[str, FocusBlock] = {}
    for block in blocks:
        if block.focus_id in result:
            raise ValueError(f"Duplicate focus id {block.focus_id} in {source}")
        result[block.focus_id] = block
    return result


def extract_field(block: str, field: str) -> str | None:
    span = field_span(block, field)
    return None if span is None else block[span[0] : span[1]]


def replace_field(block: str, field: str, replacement: str) -> str:
    span = field_span(block, field)
    if span is None:
        raise ValueError(f"Baseline block lacks {field}")
    return block[: span[0]] + replacement + block[span[1] :]


def insert_before_field(block: str, field: str, insertion: str) -> str:
    span = field_span(block, field)
    if span is None:
        raise ValueError(f"Baseline block lacks {field}")
    line_start = span[0]
    prefix = block[:line_start]
    if prefix and not prefix.endswith(("\n", "\r")):
        prefix += "\n"
    return prefix + insertion.rstrip("\r\n") + "\n" + block[line_start:]


def remove_field(block: str, field: str) -> str:
    span = field_span(block, field)
    if span is None:
        return block
    start, end = span
    while end < len(block) and block[end] in " \t":
        end += 1
    if end < len(block) and block[end] == "\r":
        end += 1
    if end < len(block) and block[end] == "\n":
        end += 1
    return block[:start] + block[end:]


def newline_style(text: str) -> str:
    return "\r\n" if "\r\n" in text else "\n"


def convert_newlines(text: str, newline: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n").replace("\n", newline)


def git_head_text(root: Path, relative: str) -> str:
    result = subprocess.run(
        ["git", "show", f"HEAD:{relative}"],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout.decode("utf-8-sig")


def read_text(path: Path) -> tuple[str, bool]:
    data = path.read_bytes()
    return data.decode("utf-8-sig"), data.startswith(b"\xef\xbb\xbf")


def write_text(path: Path, text: str, bom: bool) -> None:
    data = text.encode("utf-8")
    if bom:
        data = b"\xef\xbb\xbf" + data
    path.write_bytes(data)


def rebuild_file(root: Path, relative: str) -> tuple[str, str, bool]:
    path = root / relative
    current, bom = read_text(path)
    baseline = git_head_text(root, relative)
    newline = newline_style(current)
    baseline = convert_newlines(baseline, newline)

    current_blocks = unique_map(focus_blocks(current), f"current {relative}")
    baseline_list = focus_blocks(baseline)
    baseline_blocks = unique_map(baseline_list, f"HEAD {relative}")

    if set(current_blocks) != set(baseline_blocks):
        added = sorted(set(current_blocks) - set(baseline_blocks))
        removed = sorted(set(baseline_blocks) - set(current_blocks))
        raise ValueError(
            f"Focus ID set changed in {relative}; added={added}, removed={removed}"
        )

    rebuilt = baseline
    for base in reversed(baseline_list):
        current_block = current_blocks[base.focus_id].text
        reward = extract_field(current_block, "completion_reward")
        if reward is None:
            raise ValueError(f"Current focus {base.focus_id} lacks completion_reward")
        reward = convert_newlines(reward, newline)
        replacement = replace_field(base.text, "completion_reward", reward)

        if base.focus_id in PRESERVE_SELECT_EFFECT:
            select_effect = extract_field(current_block, "select_effect")
            if select_effect is None:
                raise ValueError(
                    f"Whitelisted focus {base.focus_id} lacks current select_effect"
                )
            replacement = insert_before_field(
                replacement,
                "completion_reward",
                convert_newlines(select_effect, newline),
            )

        projected = remove_field(replacement, "completion_reward")
        projected = remove_field(projected, "select_effect")
        expected = remove_field(base.text, "completion_reward")
        expected = remove_field(expected, "select_effect")
        if projected != expected:
            raise AssertionError(f"Non-reward layout drift remains in {base.focus_id}")

        rebuilt = rebuilt[: base.start] + replacement + rebuilt[base.end :]

    return current, rebuilt, bom


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()

    changed = 0
    for relative in FILES:
        current, rebuilt, bom = rebuild_file(root, relative)
        differs = current != rebuilt
        changed += int(differs)
        print(f"{relative}: {'needs restore' if differs else 'layout clean'}")
        if differs and args.apply:
            write_text(root / relative, rebuilt, bom)

    if args.apply:
        print(f"restored {changed} file(s)")
        return 0
    print(f"{changed} file(s) differ from authored layout")
    return 1 if changed else 0


if __name__ == "__main__":
    raise SystemExit(main())
