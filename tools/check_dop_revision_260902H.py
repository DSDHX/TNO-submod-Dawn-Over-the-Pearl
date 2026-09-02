#!/usr/bin/env python3
"""Requirement-level static acceptance for the 260902H DOP revision."""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

from attach_dop_events_to_focuses import ATTACHMENTS
from audit_dop_events import LOC_RE, inventory as event_inventory
from check_dop_content_flow import main as check_content_flow
from dop_focus_effect_design import DESIGN_ROWS, Design
from dop_focus_effect_design_core import CORE_DESIGN_ROWS
from dop_focus_effect_design_endings import ENDING_DESIGN_ROWS
from rebalance_dop_unlocks import (
    DECISION_RE,
    FOCUS_DECISIONS,
    FOCUS_PROJECTS,
    PROJECT_RE,
    START_DECISIONS,
    START_PROJECTS,
    decision_registry,
    effect_block,
    project_registry,
)
from restore_dop_focus_event_calls import missing_event_lines
from restore_dop_focus_layout import (
    FILES,
    extract_field,
    focus_blocks,
    git_head_text,
    rebuild_file,
)


ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)
    print(f"PASS  {message}")


def text(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8-sig", errors="strict")


def compact_script(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def focus_index() -> dict[str, tuple[str, object]]:
    result: dict[str, tuple[str, object]] = {}
    for relative in FILES:
        source = text(relative)
        for block in focus_blocks(source):
            require(block.focus_id not in result, f"focus ID unique in target trees: {block.focus_id}")
            result[block.focus_id] = (relative, block)
    return result


def design_index() -> dict[str, Design]:
    result: dict[str, Design] = {}
    for focus_id, item in DESIGN_ROWS + CORE_DESIGN_ROWS + ENDING_DESIGN_ROWS:
        require(focus_id not in result, f"bespoke design ID unique: {focus_id}")
        result[focus_id] = item
    return result


def check_layout() -> None:
    for relative in FILES:
        current, rebuilt, _bom = rebuild_file(ROOT, relative)
        require(current == rebuilt, f"authored non-reward focus layout matches Git HEAD: {Path(relative).name}")


def check_bespoke_effects(index: dict[str, tuple[str, object]], designs: dict[str, Design]) -> None:
    package_file = ROOT / "common" / "scripted_effects" / "DOP_GNG_reward_packages.txt"
    require(not package_file.exists(), "generic reward-package file is removed")
    game_script = "\n".join(
        path.read_text(encoding="utf-8-sig", errors="replace")
        for root in (ROOT / "common", ROOT / "events")
        for path in root.rglob("*.txt")
    )
    require("DOP_GNG_reward_" not in game_script, "no generic reward-package call remains in game script")
    require(len(designs) == 142, "142 focus-specific designs are declared")

    fingerprints: dict[tuple[str, ...], str] = {}
    for focus_id, item in designs.items():
        require(1 <= len(item.axes) <= 3, f"{focus_id} uses one to three gameplay axes")
        if item.effects:
            require(item.effects not in fingerprints, f"{focus_id} has a unique direct-effect set")
            fingerprints[item.effects] = focus_id
        require(focus_id in index, f"designed focus exists: {focus_id}")
        reward = extract_field(index[focus_id][1].text, "completion_reward") or ""
        require(reward.count("# DOP BESPOKE 260902B axes:") == 1, f"{focus_id} has one bespoke marker")
        normalized_reward = compact_script(reward)
        for snippet in item.effects:
            require(compact_script(snippet) in normalized_reward, f"{focus_id} contains its authored direct effect")

    ending_files = {
        "lee": "common/national_focus/dop_sony-japan_ending1_lee.txt",
        "ibuka": "common/national_focus/dop_sony-japan_ending2_ibuka.txt",
        "finance": "common/national_focus/dop_sony-japan_ending3_hitachi.txt",
    }
    route_designs = {
        route: [item for focus_id, item in designs.items() if index[focus_id][0] == relative]
        for route, relative in ending_files.items()
    }
    lee_positive = sum(
        any(token in "\n".join(item.effects) for token in ("TNO_improve_", "add_stability = 0", "gdp_growth_temp = 0", "GNG_misc_income_temp = 0"))
        for item in route_designs["lee"]
    )
    ibuka_technical = sum(
        any(token in "\n".join(item.effects) for token in ("improve_research", "improve_industrial", "improve_academic", "improve_admin"))
        for item in route_designs["ibuka"]
    )
    finance_fiscal = sum(
        any(token in "\n".join(item.effects) for token in ("gdp_growth_temp = 0", "GNG_misc_income_temp = 0", "business_tax_temp = -"))
        for item in route_designs["finance"]
    )
    finance_harm = sum(
        bool(
            re.search(
                r"TNO_worsen_|GNG_corruption_temp_var = (?!-)|add_stability = -|add_political_power = -|GNG_opinion_temp_var = -|GNG_misc_income_temp = -",
                "\n".join(item.effects),
            )
        )
        for item in route_designs["finance"]
    )
    require(lee_positive >= 11, "Lee ending is overwhelmingly positive and welfare-oriented")
    require(ibuka_technical >= 9, "Ibuka ending is overwhelmingly positive and technology-oriented")
    require(finance_fiscal >= 7 and finance_harm >= 10, "finance ending combines fiscal growth with broad human costs")


TOOLTIP_KEYS = (
    "DOP_GNG_restore_legco_tt",
    "DOP_GNG_restore_map_tt",
    "DOP_GNG_unlock_construction_tt",
    "DOP_GNG_unlock_scw_tt",
    "DOP_GNG_unlock_gsa_tt",
    "DOP_GNG_restore_economy_compare_tt",
    # Product-cycle and core-stage tooltip copy are author-managed in 260902H.
)


def check_mechanic_tooltips() -> None:
    effects = text("common/scripted_effects/DOP_GNG_flow_effects.txt")
    loc_path = ROOT / "localisation" / "simp_chinese" / "DOP_GNG_mechanic_tooltips_l_simp_chinese.yml"
    data = loc_path.read_bytes()
    require(data.startswith(b"\xef\xbb\xbf"), "mechanic-tooltip localisation keeps UTF-8 BOM")
    loc: dict[str, str] = {}
    for line in data.decode("utf-8-sig").splitlines():
        match = LOC_RE.match(line)
        if match:
            loc[match.group(1)] = match.group(2)
    require(set(TOOLTIP_KEYS) <= set(loc), "all eight staged mechanism tooltips are localised")
    for key in TOOLTIP_KEYS:
        require(f"custom_effect_tooltip = {key}" in effects, f"mechanism effect exposes {key}")
        require(all(token in loc[key] for token in ("§F", "§G", "£")), f"{key} uses TNO-style colour and texticon markup")
    reconstruction = text("common/national_focus/dop_sony-japan_reconstruction.txt")
    require("GNG_product_cycle_reactivation_focustt" not in reconstruction, "missing legacy product-cycle tooltip key is removed")
    reconstruction_blocks = {block.focus_id: block for block in focus_blocks(reconstruction)}
    require("DOP_GNG_enter_core_stage = yes" not in reconstruction_blocks["GNG_focus_new_products_old_friends"].text, "mid-tree product cycle does not leave reconstruction")
    require("DOP_GNG_enter_core_stage = yes" in reconstruction_blocks["DOP_GNG_recon_opening_ceremony"].text, "authored reconstruction endpoint enters the core stage")


def focus_event_owners() -> dict[str, list[str]]:
    owners: dict[str, list[str]] = defaultdict(list)
    pattern = re.compile(r"country_event\s*=\s*\{\s*id\s*=\s*([^\s}]+)")
    for relative in FILES:
        for block in focus_blocks(text(relative)):
            for event_id in pattern.findall(block.text):
                owners[event_id].append(block.focus_id)
    return owners


def check_events(index: dict[str, tuple[str, object]]) -> None:
    owners = focus_event_owners()
    for focus_id, calls in ATTACHMENTS.items():
        for event_id, _days in calls:
            require(owners[event_id] == [focus_id], f"manually verified event {event_id} belongs only to {focus_id}")
    for relative in FILES:
        current_map = {block.focus_id: block for block in focus_blocks(text(relative))}
        for head_block in focus_blocks(git_head_text(ROOT, relative)):
            if head_block.focus_id == "DOP_GNG_recon_grand_wall_weak_foundation":
                continue
            current_reward = extract_field(current_map[head_block.focus_id].text, "completion_reward") or ""
            head_reward = extract_field(head_block.text, "completion_reward") or ""
            require(
                not missing_event_lines(head_reward, current_reward),
                f"Git-authored focus events are restored for {head_block.focus_id}",
            )
    rows = event_inventory(ROOT)
    unassigned = [row for row in rows if not row["focus_callers"]]
    table = text("docs/design/unassigned_event_table.md")
    table_rows = len(re.findall(r"(?m)^\| `[^`]+` \|", table))
    require(len(rows) == 567, "all 567 mod events are covered by the event audit")
    require(len(unassigned) == 453 and table_rows == 453, "all 453 non-target-focus events have a named table row")


def current_unlock_maps(index: dict[str, tuple[str, object]]) -> tuple[dict[str, tuple[int, ...]], dict[str, tuple[str, ...]]]:
    projects: dict[str, tuple[int, ...]] = {}
    decisions: dict[str, tuple[str, ...]] = {}
    for focus_id, (_relative, block) in index.items():
        reward = extract_field(block.text, "completion_reward") or ""
        project_ids = tuple(int(value) for value in PROJECT_RE.findall(reward))
        decision_ids = tuple(DECISION_RE.findall(reward))
        if project_ids:
            projects[focus_id] = project_ids
        if decision_ids:
            decisions[focus_id] = decision_ids
    return projects, decisions


def check_unlock_distribution(index: dict[str, tuple[str, object]]) -> None:
    projects, decisions = current_unlock_maps(index)
    require(projects == FOCUS_PROJECTS, "focus-owned construction projects match the curated distribution")
    require(decisions == FOCUS_DECISIONS, "focus-owned SCW decisions match the curated distribution")

    flow = text("common/scripted_effects/DOP_GNG_flow_effects.txt")
    _s, _e, construction = effect_block(flow, "DOP_GNG_unlock_construction_stage")
    startup_projects = tuple(int(value) for value in re.findall(r"DOP_construction_target_project = (\d+)", construction))
    require(startup_projects == next(iter(START_PROJECTS.values())), "reconstruction starts with exactly projects 12 and 13")
    _s, _e, scw_stage = effect_block(flow, "DOP_GNG_unlock_scw_stage")
    startup_decisions = tuple(DECISION_RE.findall(scw_stage))
    require(startup_decisions == next(iter(START_DECISIONS.values())), "SCW starts with exactly four named decisions")

    unlock_text = text("common/scripted_effects/DOP_SCW_unlock_effects.txt")
    _s, _e, activation = effect_block(unlock_text, "DOP_SCW_activate_decision_system")
    concrete_flags = re.findall(r"set_country_flag = (DOP_SCW_[A-Za-z0-9_]+_unlocked)", activation)
    require(concrete_flags == ["DOP_SCW_decisions_unlocked"], "normal SCW activation sets no concrete decision flags")

    assigned_projects = set(startup_projects) | {value for values in projects.values() for value in values}
    assigned_decisions = set(startup_decisions) | {value for values in decisions.values() for value in values}
    require(len(project_registry(ROOT)) == 20 and len(assigned_projects) == 10, "construction distribution is 10 assigned / 10 deferred")
    require(len(decision_registry(ROOT)) == 48 and len(assigned_decisions) == 24, "SCW distribution is 24 assigned / 24 deferred")
    require(max(map(len, list(decisions.values()) + [startup_decisions])) <= 4, "no focus unlocks more than four SCW decisions")
    require((ROOT / "docs/design/construction_project_distribution.md").is_file(), "construction assigned/deferred ledger exists")
    require((ROOT / "docs/design/scw_decision_distribution.md").is_file(), "SCW decision assigned/deferred ledger exists")


def check_version_and_scope() -> None:
    version = text("localisation/simp_chinese/DOP_version_l_simp_chinese.yml")
    require("EARLY DEVELOPMENT BUILD 260902H" in version, "user-facing build is 260902H")
    yun_effects = text("common/scripted_effects/DOP_YUN_southwest_effects.txt")
    yun_characters = text("common/characters/DOP_YUN_characters.txt")
    yun_history = text("history/countries/YUN - Yunnan.txt")
    yun_ai = text("common/ai_strategy/DOP_YUN_southwest_war.txt")
    flow_effects = text("common/scripted_effects/DOP_GNG_flow_effects.txt")
    flow_debug = text("common/decisions/DOP_GNG_flow_debug_decisions.txt")
    native_yun_events = text("events/TNO_Yunnan.txt")
    require(
        "DOP_YUN_long_shengwu" in yun_characters
        and 'gfx/leaders/YUN/DOP_Long_Shengwu.png' in yun_characters
        and "country_leader = {" in yun_characters,
        "Long Shengwu character, portrait and leader role are wired before runtime",
    )
    require(
        yun_history.count("recruit_character = DOP_YUN_long_shengwu") == 1,
        "YUN history recruits Long Shengwu exactly once",
    )
    for token in (
        "promote_character = {",
        "retire_character = YUN_lu_han",
        "target = GUZ",
        'load_oob = "YUN_NPA_army"',
        'load_oob = "YUN_volunteers"',
        "set_country_flag = DOP_YUN_southwest_war_prepared",
    ):
        require(token in yun_effects, f"YUN prewar implementation contains {token}")
    yun_active = "\n".join(line.split("#", 1)[0] for line in yun_effects.splitlines())
    require(
        "recruit_character" not in yun_active
        and "add_country_leader_role" not in yun_active,
        "YUN runtime effect does not use game-start-only character recruitment",
    )
    for forbidden in (
        "YUN_Long_Yun_Coup_effects = yes",
        "WI_Start_effects = yes",
        "country_event = { id = yun_wi",
        "declare_war_on",
    ):
        require(forbidden not in yun_active, f"YUN prewar implementation excludes native start token {forbidden}")
    require(
        "has_war_with = GNG" in yun_ai
        and "type = conquer" in yun_ai
        and "type = front_control" in yun_ai
        and "execution_type = rush" in yun_ai,
        "YUN receives an at-war-only offensive AI plan against GNG",
    )
    require(
        "DOP_GNG_block_native_western_insurrection_responses = {" in flow_effects
        and "clr_global_flag = CHI_Western_Insurrection_Crisis" in flow_effects
        and "clr_global_flag = YUN_NPA_GAW_Crisis" in flow_effects,
        "DOP explicitly blocks native GNG Western Insurrection response gates",
    )
    require(
        "DOP_GNG_debug_flow_02a_yunnan_prewar" in flow_debug
        and "DOP_YUN_prepare_southwest_war = yes" in flow_debug,
        "02A debug decision advances only the isolated YUN preparation",
    )
    yun_25 = native_yun_events.split("id = yun_unified.25", 1)[1].split(
        "id = yun_unified.26", 1
    )[0]
    yun_25_active = "\n".join(line.split("#", 1)[0] for line in yun_25.splitlines())
    require(
        "country_event = { id = yun_unified.26" not in yun_25_active,
        "author-blocked native YUN trigger remains inactive",
    )
    combined = "\n".join(
        text(relative)
        for relative in (
            "common/scripted_effects/DOP_GNG_flow_effects.txt",
            "common/national_focus/dop_sony-japan_reconstruction.txt",
            "common/national_focus/dop_sony-japan_core.txt",
        )
    )
    require("set_country_flag = guang_dong_theater_visible" not in combined, "normal content still never opens the excluded Guangdong theatre")


def main() -> int:
    index = focus_index()
    designs = design_index()
    check_layout()
    check_bespoke_effects(index, designs)
    check_mechanic_tooltips()
    check_events(index)
    check_unlock_distribution(index)
    check_version_and_scope()
    check_content_flow()
    print("DOP 260902H REQUIREMENT ACCEPTANCE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
