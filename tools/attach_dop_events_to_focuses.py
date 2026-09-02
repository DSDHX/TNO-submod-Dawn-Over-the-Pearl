#!/usr/bin/env python3
"""Attach manually verified orphan events to their narrative focus owners."""

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path

from audit_dop_events import event_blocks, loc_values
from restore_dop_focus_layout import extract_field, focus_blocks, read_text, write_text


# Event-to-focus matches are deliberately explicit and manually reviewed.
# The only focus with two events stages the equipment promise and delivery.
ATTACHMENTS: dict[str, tuple[tuple[str, int], ...]] = {
    # Opening recovery and pre-war preparation.
    "DOP_GNG_year_of_the_rain": (("DOP_GNG_event.137", 0),),
    "DOP_GNG_res_from_oc": (("DOP_GNG_event.138", 0),),
    "DOP_GNG_regen_econ": (("DOP_GNG_event.142", 0),),
    "DOP_GNG_wrecking_world": (("DOP_GNG_event.139", 0),),
    "DOP_GNG_pan_thai_bay": (("DOP_GNG_event.140", 0),),
    "DOP_GNG_gd_mex_col": (("DOP_GNG_event.141", 0),),
    "DOP_GNG_expand_d": (("DOP_GNG_event.143", 0),),
    "DOP_GNG_lower_barrier": (("DOP_GNG_event.144", 0),),
    "DOP_GNG_rightous_def": (("DOP_GNG_event.65", 0),),

    # Ibuka ending technology and administration events.
    "GNG_focus_risk_clearance": (("DOP_GNG_event.4", 0),),
    "GNG_focus_industrial_nation": (("DOP_GNG_event.7", 0),),
    "GNG_focus_reform_inefficient_administration": (("DOP_GNG_event.6", 0),),
    "GNG_focus_never_stop": (("DOP_GNG_event.9", 0),),
    "GNG_focus_rise_of_silicon": (("DOP_GNG_event.10", 0),),
    "GNG_focus_supercomputer_center": (("DOP_GNG_event.5", 0),),
    "GNG_focus_academic_golden_age": (("DOP_GNG_event.11", 0),),
    "GNG_focus_laying_the_foundation_for_kouu": (("DOP_GNG_event.12", 0),),

    # Core diplomacy.
    "GNG_focus_be_in_the_Sphere": (("DOP_GNG_event.130", 0),),
    "GNG_focus_friend_in_Einheitspakt": (("DOP_GNG_event.131", 0),),

    # Police and security reform sequence.
    "GNG_focus_shield_of_the_Rising_Sun": (("DOP_GNG_event.38", 0),),
    "GNG_focus_level_up_equipment": (("DOP_GNG_event.39", 0), ("DOP_GNG_event.40", 5)),
    "GNG_focus_protect_your_own_life": (("DOP_GNG_event.41", 0),),
    "GNG_focus_and_the_lives_of_others": (("DOP_GNG_event.42", 0),),
    "GNG_focus_against_criminal_offences": (("DOP_GNG_event.43", 0),),
    "GNG_focus_expanding_Criminal_Department": (("DOP_GNG_event.44", 0),),
    "GNG_focus_century_of_science": (("DOP_GNG_event.45", 0),),
    "GNG_focus_into_the_community": (("DOP_GNG_event.46", 0),),
    "GNG_focus_harmonious_and_safe": (("DOP_GNG_event.47", 0),),
    "GNG_focus_reject_PGD": (("DOP_GNG_event.48", 0),),
    "GNG_focus_loyalty_and_courage": (("DOP_GNG_event.49", 0),),
    "GNG_focus_establishment_PRU": (("DOP_GNG_event.50", 0),),
    "GNG_focus_special_skills_units": (("DOP_GNG_event.52", 0),),
    "GNG_focus_territorial_support_force": (("DOP_GNG_event.51", 0),),
    "GNG_focus_watching_YOU": (("DOP_GNG_event.53", 0),),
    "GNG_focus_Secret_Force_May": (("DOP_GNG_event.54", 0),),
    "GNG_focus_force_major_terrorism": (("DOP_GNG_event.55", 0),),
    "GNG_focus_anti_black_department": (("DOP_GNG_event.56", 0),),
    "GNG_focus_police_tactics": (("DOP_GNG_event.58", 0),),
    "GNG_focus_Strike_hard_at_transnational_crime": (("DOP_GNG_event.57", 0),),
    "GNG_focus_gng_good_order": (("DOP_GNG_event.59", 0),),
}


CALL_RE = re.compile(r"country_event\s*=\s*\{\s*id\s*=\s*([^\s}]+)")


def replace_reward(block: str, reward: str) -> str:
    current = extract_field(block, "completion_reward")
    if current is None:
        raise ValueError("Focus lacks completion_reward")
    start = block.find(current)
    return block[:start] + reward + block[start + len(current) :]


def add_calls(reward: str, calls: tuple[tuple[str, int], ...], newline: str) -> str:
    existing = set(CALL_RE.findall(reward))
    if existing.intersection(event_id for event_id, _ in calls):
        raise ValueError(f"Attachment already present: {existing}")
    opening_end = reward.find("{") + 1
    line_end = reward.find("\n", opening_end)
    if line_end < 0:
        raise ValueError("Single-line completion_reward is unsupported")
    indent_match = re.search(r"(?m)^(?P<indent>[ \t]+)\S", reward[line_end + 1 :])
    indent = indent_match.group("indent") if indent_match else "\t\t"
    lines = [f"{indent}# DOP MANUALLY VERIFIED EVENT ATTACHMENT 260902B{newline}"]
    for event_id, days in calls:
        lines.append(
            f"{indent}country_event = {{ id = {event_id} days = {days} }}{newline}"
        )
    return reward[: line_end + 1] + "".join(lines) + reward[line_end + 1 :]


def event_ids(root: Path) -> set[str]:
    ids: set[str] = set()
    for path in (root / "events").glob("*.txt"):
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        ids.update(event_id for event_id, _, _ in event_blocks(text))
    return ids


def current_focus_event_owners(root: Path) -> dict[str, list[str]]:
    result: dict[str, list[str]] = defaultdict(list)
    for path in (root / "common" / "national_focus").glob("*.txt"):
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        for block in focus_blocks(text):
            for event_id in CALL_RE.findall(block.text):
                result[event_id].append(block.focus_id)
    return result


def write_ledger(root: Path, target: Path) -> None:
    loc = loc_values(root)
    lines = [
        "# DOP 国策事件挂载表",
        "",
        "本表只记录本轮经题名、正文与国策简介人工核实后新增的挂载；Git 基线原有挂载另按基线恢复。",
        "",
        "| 国策 ID | 国策名称 | 事件 ID | 事件名称 | 延迟 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for focus_id, calls in ATTACHMENTS.items():
        for event_id, days in calls:
            lines.append(
                f"| `{focus_id}` | {loc.get(focus_id, '')} | `{event_id}` | {loc.get(event_id + '.t', '')} | {days} 日 |"
            )
    path = target if target.is_absolute() else root / target
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--ledger", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()

    defined_events = event_ids(root)
    requested_events = {event_id for calls in ATTACHMENTS.values() for event_id, _ in calls}
    missing_events = sorted(requested_events - defined_events)
    if missing_events:
        raise ValueError(f"Undefined attached events: {missing_events}")
    if len(requested_events) != sum(len(calls) for calls in ATTACHMENTS.values()):
        raise ValueError("An event is assigned to more than one focus in ATTACHMENTS")

    owners = current_focus_event_owners(root)
    already_owned = {event_id: owners[event_id] for event_id in requested_events if owners[event_id]}
    if already_owned:
        raise ValueError(f"Requested orphan events already have focus owners: {already_owned}")

    focus_locations: dict[str, tuple[Path, object]] = {}
    file_text: dict[Path, tuple[str, bool]] = {}
    for path in (root / "common" / "national_focus").glob("*.txt"):
        text, bom = read_text(path)
        file_text[path] = (text, bom)
        for block in focus_blocks(text):
            if block.focus_id in ATTACHMENTS:
                if block.focus_id in focus_locations:
                    raise ValueError(f"Duplicate focus id: {block.focus_id}")
                focus_locations[block.focus_id] = (path, block)
    missing_focuses = sorted(set(ATTACHMENTS) - set(focus_locations))
    if missing_focuses:
        raise ValueError(f"Missing target focuses: {missing_focuses}")

    by_file: dict[Path, list[tuple[int, int, str]]] = defaultdict(list)
    for focus_id, calls in ATTACHMENTS.items():
        path, block = focus_locations[focus_id]
        reward = extract_field(block.text, "completion_reward")
        if reward is None:
            raise ValueError(f"Focus has no completion_reward: {focus_id}")
        text = file_text[path][0]
        newline = "\r\n" if "\r\n" in text else "\n"
        new_block = replace_reward(block.text, add_calls(reward, calls, newline))
        by_file[path].append((block.start, block.end, new_block))
        print(f"{focus_id} <- {', '.join(event_id for event_id, _ in calls)}")

    changes: list[tuple[Path, str, bool]] = []
    for path, replacements in by_file.items():
        current, bom = file_text[path]
        rebuilt = current
        for start, end, replacement in sorted(replacements, reverse=True):
            rebuilt = rebuilt[:start] + replacement + rebuilt[end:]
        changes.append((path, rebuilt, bom))

    print(f"verified attachments={len(requested_events)} events to {len(ATTACHMENTS)} focuses")
    if args.apply:
        for path, text, bom in changes:
            write_text(path, text, bom)
        if args.ledger:
            write_ledger(root, args.ledger)
        print("manual event attachments applied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
