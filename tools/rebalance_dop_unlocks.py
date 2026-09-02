#!/usr/bin/env python3
"""Rebalance construction projects and SCW decisions across relevant focuses."""

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path

from audit_dop_events import loc_values
from restore_dop_focus_layout import (
    FILES,
    extract_field,
    focus_blocks,
    matching_brace,
    read_text,
    write_text,
)


# Two mandatory reconstruction-start projects are wired through
# DOP_GNG_unlock_construction_stage; eight further projects are focus-owned.
START_PROJECTS = {"GNG_focus_leave_ruins_behind": (12, 13)}
FOCUS_PROJECTS: dict[str, tuple[int, ...]] = {
    "GNG_focus_gng_chemical_industry": (20,),
    "GNG_focus_sub_center_in_gng": (18,),
    "GNG_focus_eliminate_backward": (4,),
    "GNG_focus_pull_down_slums": (1,),
    "GNG_focus_plan_to_build_SZ": (17,),
    "GNG_focus_the_first_port": (9,),
    "GNG_focus_bridge_of_Sphere": (16,),
    "GNG_focus_expand_eduation_system": (6,),
}

# Four initial decisions are exposed by DOP_GNG_unlock_scw_stage.  Every other
# focus remains at or below four unlocks.
START_DECISIONS = {
    "DOP_GNG_recon_foundation": (
        "DOP_SCW_race_commercial_attaches",
        "DOP_SCW_materials_buy_crude_silicon",
        "DOP_SCW_wafer_replenish_consumables",
        "DOP_SCW_lithography_optical_calibration",
    )
}
FOCUS_DECISIONS: dict[str, tuple[str, ...]] = {
    "DOP_GNG_recon_swarming_investors": (
        "DOP_SCW_race_tariff_lobby",
        "DOP_SCW_race_court_dissidents",
        "DOP_SCW_packaging_recruit_assembly_labor",
        "DOP_SCW_logistics_liner_subsidies",
    ),
    "DOP_GNG_recon_leave_nothing_out": (
        "DOP_SCW_materials_smelter_overtime",
        "DOP_SCW_wafer_spc_control",
        "DOP_SCW_lithography_import_photoresist",
        "DOP_SCW_packaging_bonding_consumables",
    ),
    "DOP_GNG_recon_first_trial": (
        "DOP_SCW_materials_power_subsidy",
        "DOP_SCW_wafer_paramilitary_shifts",
        "DOP_SCW_lithography_buy_pellicles",
        "DOP_SCW_logistics_esd_packaging_standard",
    ),
    "GNG_focus_jackals_of_Central_Europe": (
        "DOP_SCW_race_friendly_expositions",
        "DOP_SCW_lithography_expert_allowances",
    ),
    "GNG_focus_vultures_in_NA": (
        "DOP_SCW_packaging_consumer_oem_orders",
        "DOP_SCW_logistics_overland_transshipment",
    ),
    "GNG_focus_trade_with_ibuka": (
        "DOP_SCW_packaging_lower_piece_rates",
        "DOP_SCW_logistics_direct_distribution",
    ),
    "GNG_focus_chip_bases_in_SZ": (
        "DOP_SCW_materials_export_low_grade_products",
        "DOP_SCW_wafer_japanese_military_orders",
    ),
}


PROJECT_RE = re.compile(
    r"(?m)^[ \t]*set_temp_variable[ \t]*=[ \t]*\{[ \t]*DOP_construction_target_project[ \t]*=[ \t]*(\d+)[ \t]*\}[ \t]*\r?\n"
    r"[ \t]*DOP_construction_show_project[ \t]*=[ \t]*yes[ \t]*(?:\r?\n)?"
)
DECISION_RE = re.compile(
    r"(?m)^[ \t]*(DOP_SCW_[A-Za-z0-9_]+)_unlock[ \t]*=[ \t]*yes[ \t]*(?:\r?\n)?"
)


def effect_block(text: str, name: str) -> tuple[int, int, str]:
    match = re.search(rf"(?m)^[ \t]*{re.escape(name)}[ \t]*=[ \t]*\{{", text)
    if match is None:
        raise ValueError(f"Missing scripted effect: {name}")
    opening = text.find("{", match.start(), match.end())
    closing = matching_brace(text, opening)
    return match.start(), closing + 1, text[match.start() : closing + 1]


def append_to_reward(reward: str, lines: list[str], newline: str) -> str:
    closing = reward.rfind("}")
    if closing < 0:
        raise ValueError("completion_reward lacks closing brace")
    line_start = reward.rfind("\n", 0, closing) + 1
    closing_indent = re.match(r"[ \t]*", reward[line_start:closing]).group(0)
    indent = closing_indent + "\t"
    insertion = "".join(f"{indent}{line}{newline}" for line in lines)
    return reward[:line_start] + insertion + reward[line_start:]


def replace_reward(block: str, reward: str) -> str:
    old = extract_field(block, "completion_reward")
    if old is None:
        raise ValueError("Focus lacks completion_reward")
    start = block.find(old)
    return block[:start] + reward + block[start + len(old) :]


def transform_focus_files(root: Path) -> list[tuple[Path, str, bool]]:
    changes: list[tuple[Path, str, bool]] = []
    for relative in FILES:
        path = root / relative
        current, bom = read_text(path)
        newline = "\r\n" if "\r\n" in current else "\n"
        replacements: list[tuple[int, int, str]] = []
        for block in focus_blocks(current):
            reward = extract_field(block.text, "completion_reward")
            if reward is None:
                continue
            cleaned = PROJECT_RE.sub("", reward)
            cleaned = DECISION_RE.sub("", cleaned)
            additions: list[str] = []
            projects = FOCUS_PROJECTS.get(block.focus_id, ())
            if projects:
                additions.append("# DOP RELEVANT CONSTRUCTION PROJECTS 260902B")
                for project_id in projects:
                    additions.append(
                        f"set_temp_variable = {{ DOP_construction_target_project = {project_id} }}"
                    )
                    additions.append("DOP_construction_show_project = yes")
            decisions = FOCUS_DECISIONS.get(block.focus_id, ())
            if decisions:
                additions.append("# DOP RELEVANT SCW DECISIONS 260902B")
                additions.extend(f"{decision}_unlock = yes" for decision in decisions)
            if additions:
                cleaned = append_to_reward(cleaned, additions, newline)
            if cleaned != reward:
                replacements.append(
                    (block.start, block.end, replace_reward(block.text, cleaned))
                )
        rebuilt = current
        for start, end, replacement in reversed(replacements):
            rebuilt = rebuilt[:start] + replacement + rebuilt[end:]
        if rebuilt != current:
            changes.append((path, rebuilt, bom))
    return changes


def transform_activation(root: Path) -> tuple[Path, str, bool, int]:
    path = root / "common" / "scripted_effects" / "DOP_SCW_unlock_effects.txt"
    current, bom = read_text(path)
    start, end, block = effect_block(current, "DOP_SCW_activate_decision_system")
    output: list[str] = []
    removed = 0
    flag_re = re.compile(
        r"^[ \t]*set_country_flag[ \t]*=[ \t]*(DOP_SCW_[A-Za-z0-9_]+_unlocked)[ \t]*$"
    )
    for raw in block.splitlines(keepends=True):
        match = flag_re.match(raw.rstrip("\r\n"))
        if match and match.group(1) != "DOP_SCW_decisions_unlocked":
            removed += 1
            continue
        output.append(raw)
    rebuilt_block = "".join(output)
    rebuilt = current[:start] + rebuilt_block + current[end:]
    return path, rebuilt, bom, removed


def transform_stage_wrapper(root: Path) -> tuple[Path, str, bool]:
    path = root / "common" / "scripted_effects" / "DOP_GNG_flow_effects.txt"
    current, bom = read_text(path)
    start, end, block = effect_block(current, "DOP_GNG_unlock_scw_stage")
    newline = "\r\n" if "\r\n" in current else "\n"
    closing = block.rfind("}")
    initial = next(iter(START_DECISIONS.values()))
    lines = ["\t# DOP INITIAL SCW DECISIONS 260902B"]
    lines.extend(f"\t{decision}_unlock = yes" for decision in initial)
    insertion = newline.join(lines) + newline
    rebuilt_block = block[:closing] + insertion + block[closing:]
    rebuilt = current[:start] + rebuilt_block + current[end:]
    return path, rebuilt, bom


def project_registry(root: Path) -> dict[int, str]:
    text = (root / "common" / "scripted_effects" / "DOP_construction_effects.txt").read_text(
        encoding="utf-8-sig"
    )
    pattern = re.compile(
        r"DOP_construction_register_id\s*=\s*(\d+).*?"
        r"DOP_construction_register_token\s*=\s*token:([^\s}]+)",
        re.S,
    )
    return {int(project_id): token for project_id, token in pattern.findall(text)}


def decision_registry(root: Path) -> set[str]:
    text = (root / "common" / "scripted_effects" / "DOP_SCW_unlock_effects.txt").read_text(
        encoding="utf-8-sig"
    )
    return set(re.findall(r"(?m)^(DOP_SCW_[A-Za-z0-9_]+)_unlock\s*=\s*\{", text))


def all_focus_ids(root: Path) -> set[str]:
    result: set[str] = set()
    for path in (root / "common" / "national_focus").glob("*.txt"):
        result.update(block.focus_id for block in focus_blocks(path.read_text(encoding="utf-8-sig")))
    return result


def validate(root: Path) -> tuple[dict[int, str], set[str], set[int], set[str]]:
    projects = project_registry(root)
    decisions = decision_registry(root)
    assigned_projects = {
        project_id
        for mapping in (START_PROJECTS, FOCUS_PROJECTS)
        for values in mapping.values()
        for project_id in values
    }
    assigned_decisions = {
        decision
        for mapping in (START_DECISIONS, FOCUS_DECISIONS)
        for values in mapping.values()
        for decision in values
    }
    if set(projects) != set(range(1, 21)):
        raise ValueError(f"Construction registry is not exactly 1..20: {sorted(projects)}")
    if len(assigned_projects) != 10:
        raise ValueError(f"Expected 10 unique assigned projects, got {sorted(assigned_projects)}")
    if len(decisions) != 48 or len(assigned_decisions) != 24:
        raise ValueError(
            f"Expected 24/48 assigned decisions, got {len(assigned_decisions)}/{len(decisions)}"
        )
    if not assigned_decisions <= decisions:
        raise ValueError(f"Undefined assigned decisions: {sorted(assigned_decisions - decisions)}")
    focus_ids = all_focus_ids(root)
    target_ids = set(START_PROJECTS) | set(FOCUS_PROJECTS) | set(START_DECISIONS) | set(FOCUS_DECISIONS)
    if not target_ids <= focus_ids:
        raise ValueError(f"Missing target focuses: {sorted(target_ids - focus_ids)}")
    per_focus = {**START_DECISIONS, **FOCUS_DECISIONS}
    over_cap = {focus_id: values for focus_id, values in per_focus.items() if len(values) > 4}
    if over_cap:
        raise ValueError(f"Decision cap exceeded: {over_cap}")
    return projects, decisions, assigned_projects, assigned_decisions


PROJECT_BACKLOG_HINTS = {
    2: "未来城市住房与景观更新树段",
    3: "未来文化娱乐或消费制造树段",
    5: "未来全省交通现代化树段",
    7: "未来粤北水利与电力树段",
    8: "未来农业与粮食安全树段",
    10: "未来南海能源开发树段",
    11: "未来航天与大型科研树段",
    14: "未来民族认同与公共文化树段",
    15: "未来广西水运与旅游树段",
    19: "未来粤北资源与核能树段",
}


def decision_hint(decision: str) -> str:
    if "race_" in decision:
        return "未来国际外交/技术竞赛树段"
    if "materials_" in decision:
        return "未来原料、矿业与重化工业树段"
    if "wafer_" in decision:
        return "未来晶圆制造或军工订单树段"
    if "lithography_" in decision:
        return "未来专门光刻研发树段"
    if "packaging_" in decision:
        return "未来劳动、住房与封装制造树段"
    return "未来港口、运输与全球贸易树段"


def write_ledgers(
    root: Path,
    project_path: Path,
    decision_path: Path,
    projects: dict[int, str],
    decisions: set[str],
    assigned_projects: set[int],
    assigned_decisions: set[str],
) -> None:
    loc = loc_values(root)
    project_owner = {
        project_id: focus_id
        for mapping in (START_PROJECTS, FOCUS_PROJECTS)
        for focus_id, values in mapping.items()
        for project_id in values
    }
    project_lines = [
        "# 建设项目分配表",
        "",
        "当前授权树挂载 10/20 项；其余 10 项保留给未授权修改的后续树段。",
        "",
        "## 当前挂载",
        "",
        "| ID | 项目 | 国策 |",
        "| ---: | --- | --- |",
    ]
    for project_id in sorted(assigned_projects):
        token = projects[project_id]
        owner = project_owner[project_id]
        project_lines.append(
            f"| {project_id} | {loc.get(token, token)} | `{owner}`（{loc.get(owner, '')}） |"
        )
    project_lines.extend(
        [
            "",
            "## 留待未授权树段",
            "",
            "| ID | 项目 | 建议未来树段 |",
            "| ---: | --- | --- |",
        ]
    )
    for project_id in sorted(set(projects) - assigned_projects):
        token = projects[project_id]
        project_lines.append(
            f"| {project_id} | {loc.get(token, token)} | {PROJECT_BACKLOG_HINTS[project_id]} |"
        )

    decision_owner = {
        decision: focus_id
        for mapping in (START_DECISIONS, FOCUS_DECISIONS)
        for focus_id, values in mapping.items()
        for decision in values
    }
    decision_lines = [
        "# 三微米冷战决议分配表",
        "",
        "当前授权树挂载 24/48 项；任何单一国策最多解锁 4 项。其余 24 项留待未授权修改的后续树段。",
        "",
        "## 当前挂载",
        "",
        "| 决议 | 国策 |",
        "| --- | --- |",
    ]
    for decision in sorted(assigned_decisions):
        owner = decision_owner[decision]
        decision_lines.append(
            f"| {loc.get(decision, decision)} (`{decision}`) | `{owner}`（{loc.get(owner, '')}） |"
        )
    decision_lines.extend(
        [
            "",
            "## 留待未授权树段",
            "",
            "| 决议 | 建议未来树段 |",
            "| --- | --- |",
        ]
    )
    for decision in sorted(decisions - assigned_decisions):
        decision_lines.append(
            f"| {loc.get(decision, decision)} (`{decision}`) | {decision_hint(decision)} |"
        )

    ppath = project_path if project_path.is_absolute() else root / project_path
    dpath = decision_path if decision_path.is_absolute() else root / decision_path
    ppath.parent.mkdir(parents=True, exist_ok=True)
    dpath.parent.mkdir(parents=True, exist_ok=True)
    ppath.write_text("\n".join(project_lines) + "\n", encoding="utf-8", newline="\n")
    dpath.write_text("\n".join(decision_lines) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--project-ledger", type=Path)
    parser.add_argument("--decision-ledger", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    projects, decisions, assigned_projects, assigned_decisions = validate(root)
    focus_changes = transform_focus_files(root)
    activation_path, activation_text, activation_bom, removed_flags = transform_activation(root)
    wrapper_path, wrapper_text, wrapper_bom = transform_stage_wrapper(root)
    if removed_flags != 30:
        raise ValueError(f"Expected to remove 30 startup decision flags, found {removed_flags}")

    print(f"projects assigned/deferred={len(assigned_projects)}/{len(projects) - len(assigned_projects)}")
    print(f"decisions assigned/deferred={len(assigned_decisions)}/{len(decisions) - len(assigned_decisions)}")
    print(f"startup hidden decision flags removed={removed_flags}; max per focus=4")
    print(f"focus files to rewrite={len(focus_changes)}")

    if args.apply:
        for path, text, bom in focus_changes:
            write_text(path, text, bom)
        write_text(activation_path, activation_text, activation_bom)
        write_text(wrapper_path, wrapper_text, wrapper_bom)
        if args.project_ledger and args.decision_ledger:
            write_ledgers(
                root,
                args.project_ledger,
                args.decision_ledger,
                projects,
                decisions,
                assigned_projects,
                assigned_decisions,
            )
        print("unlock distribution rebalanced")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
