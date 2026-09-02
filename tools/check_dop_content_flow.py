from __future__ import annotations

import hashlib
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TNO_ROOT = Path(r"D:\Steam\steamapps\workshop\content\394360\2438003901")


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8-sig")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)
    print(f"PASS  {message}")


def matching_brace(text: str, open_pos: int) -> int:
    depth = 0
    quoted = False
    escaped = False
    comment = False
    for idx in range(open_pos, len(text)):
        char = text[idx]
        if comment:
            if char == "\n":
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
                return idx
    raise AssertionError(f"unmatched brace at {open_pos}")


def focus(text: str, focus_id: str) -> str:
    found: list[str] = []
    for match in re.finditer(r"(?m)^[ \t]*(?:shared_focus|focus)[ \t]*=[ \t]*\{", text):
        open_pos = text.find("{", match.start(), match.end())
        end = matching_brace(text, open_pos) + 1
        block = text[match.start():end]
        id_match = re.search(r"(?m)^[ \t]*id[ \t]*=[ \t]*([^\s#]+)", block)
        if id_match and id_match.group(1) == focus_id:
            found.append(block)
    require(len(found) == 1, f"focus exists exactly once: {focus_id}")
    return found[0]


def event(text: str, event_id: str) -> str:
    found: list[str] = []
    for match in re.finditer(r"(?m)^[ \t]*(?:country_event|news_event)[ \t]*=[ \t]*\{", text):
        open_pos = text.find("{", match.start(), match.end())
        end = matching_brace(text, open_pos) + 1
        block = text[match.start():end]
        id_match = re.search(r"(?m)^[ \t]*id[ \t]*=[ \t]*([^\s#]+)", block)
        if id_match and id_match.group(1) == event_id:
            found.append(block)
    require(len(found) == 1, f"event exists exactly once: {event_id}")
    return found[0]


def main() -> int:
    design = ROOT / "docs/design/全流程_作者原始稿.txt"
    require(design.is_file(), "author design is archived inside the project")
    require(
        hashlib.sha256(design.read_bytes()).hexdigest().upper()
        == "263E1AC1995E59B6187BAE83761B9FAA8AD6611A06BB94B4A3EAA817DA5D0EE6",
        "archived author design retains the verified SHA-256",
    )
    require((ROOT / "docs/design/README.md").is_file(), "design archive has a durable index and scope note")
    require((ROOT / "docs/design/implementation_matrix.md").is_file(), "implementation/frozen-scope matrix exists")

    version = read("localisation/simp_chinese/DOP_version_l_simp_chinese.yml")
    require("EARLY DEVELOPMENT BUILD 260902I" in version, "user-facing build is 260902I")

    flow_effects = read("common/scripted_effects/DOP_GNG_flow_effects.txt")
    yun_effects = read("common/scripted_effects/DOP_YUN_southwest_effects.txt")
    yun_characters = read("common/characters/DOP_YUN_characters.txt")
    yun_history = read("history/countries/YUN - Yunnan.txt")
    yun_ai = read("common/ai_strategy/DOP_YUN_southwest_war.txt")
    jap_ai = read("common/ai_strategy/DOP_JAP_southwest_war.txt")
    jap_reinforcement_oob = read("history/units/DOP_JAP_southwest_reinforcements.txt")
    flow_modifiers = read("common/dynamic_modifiers/DOP_GNG_flow_dynamic_modifiers.txt")
    yun_events = read("events/TNO_Yunnan.txt")
    flow_actions = read("common/on_actions/DOP_GNG_flow_on_actions.txt")
    flow_events = read("events/DOP_GNG_flow.txt")
    flow_loc_path = ROOT / "localisation/simp_chinese/DOP_GNG_flow_l_simp_chinese.yml"
    flow_loc = flow_loc_path.read_text(encoding="utf-8-sig")
    require(flow_loc_path.read_bytes().startswith(b"\xef\xbb\xbf"), "flow localisation has a UTF-8 BOM")
    for event_id in range(1, 5):
        require(f"id = DOP_GNG_flow.{event_id}" in flow_events, f"placeholder flow event {event_id} exists")
        for suffix in ("t", "desc", "a"):
            line = next(
                (item for item in flow_loc.splitlines() if item.startswith(f" DOP_GNG_flow.{event_id}.{suffix}:")),
                "",
            )
            require("【Placeholder】" in line, f"flow event {event_id}.{suffix} is conspicuously placeholder-labelled")
    for event_id in range(10, 16):
        block = event(flow_events, f"DOP_GNG_flow.{event_id}")
        require("hidden = yes" in block, f"hidden GUI-lock event {event_id} exists")

    require(
        'civilian = { large = "gfx/leaders/YUN/DOP_Long_Shengwu.png" }' in yun_characters
        and (ROOT / "gfx/leaders/YUN/DOP_Long_Shengwu.png").is_file(),
        "Long Shengwu character uses the existing DOP portrait",
    )
    require(
        "country_leader = {" in yun_characters
        and "ideology = ultranationalism_stratocracy_subtype" in yun_characters,
        "Long Shengwu owns his country-leader role before runtime",
    )
    require(
        yun_history.count("recruit_character = DOP_YUN_long_shengwu") == 1,
        "YUN history recruits Long Shengwu exactly once at game start",
    )
    native_yun_history = (
        TNO_ROOT / "history/countries/YUN - Yunnan.txt"
    ).read_text(encoding="utf-8-sig")
    require(
        yun_history.replace("recruit_character = DOP_YUN_long_shengwu\n", "", 1)
        == native_yun_history,
        "YUN history override differs from TNO only by Long Shengwu recruitment",
    )
    for token in (
        "promote_character = {",
        "character = DOP_YUN_long_shengwu",
        "retire_character = YUN_lu_han",
        "target = GUZ",
        "add_core_of = YUN",
        'load_oob = "YUN_NPA_army"',
        'load_oob = "YUN_volunteers"',
        "set_cosmetic_tag = YUN_NPA_Long_Yun",
        "set_country_flag = DOP_YUN_southwest_war_prepared",
    ):
        require(token in yun_effects, f"YUN prewar setup contains {token}")
    yun_active = "\n".join(line.split("#", 1)[0] for line in yun_effects.splitlines())
    require(
        "recruit_character" not in yun_active
        and "add_country_leader_role" not in yun_active,
        "YUN runtime effect never attempts to recruit or construct the leader role",
    )
    require(
        "set_country_flag = YUN_long_yun_crusade" in yun_active
        and "tree = YUN_long_yun_crusade_tree" in yun_active
        and "keep_completed = no" in yun_active,
        "YUN prewar setup loads the visible National Protection Army focus tree",
    )
    for forbidden in (
        "YUN_Long_Yun_Coup_effects = yes",
        "WI_Start_effects = yes",
        "country_event = { id = yun_wi",
        "declare_war_on",
    ):
        require(forbidden not in yun_active, f"DOP YUN preparation excludes native timing/war token: {forbidden}")
    for token in (
        "type = conquer",
        "id = GNG",
        "type = consider_weak",
        "type = front_unit_request",
        "type = front_control",
        "execution_type = rush",
        "has_war_with = GNG",
        "abort_when_not_enabled = yes",
    ):
        require(token in yun_ai, f"YUN wartime AI plan contains {token}")
    yun_25_active = "\n".join(
        line.split("#", 1)[0] for line in event(yun_events, "yun_unified.25").splitlines()
    )
    require(
        "country_event = { id = yun_unified.26" not in yun_25_active,
        "author-blocked native yun_unified.25 to .26 trigger remains inactive",
    )
    yun_15 = event(yun_events, "yun_wi.15")
    require(
        "NOT = { has_country_flag = DOP_YUN_native_wi_runtime_blocked }" in yun_15
        and "WI_Start_effects = yes" in yun_15,
        "native yun_wi.15 remains available outside DOP but is blocked during DOP runtime",
    )
    native_yun_effects = (
        TNO_ROOT / "common/scripted_effects/TNO_YUN_scripted_effects.txt"
    ).read_text(encoding="utf-8-sig")
    native_peace_actions = (
        TNO_ROOT / "common/on_actions/TNO_peace_on_actions.txt"
    ).read_text(encoding="utf-8-sig")
    native_gng_events = (
        TNO_ROOT / "events/TNO_Guangdong.txt"
    ).read_text(encoding="utf-8-sig")
    native_response_ids = {
        int(match)
        for match in re.findall(
            r"(?m)^\s*id = GNG_Western_Insurrection\.([0-9]+)\s*$",
            native_gng_events,
        )
    }
    require(
        native_response_ids == set(range(1, 13)),
        "TNO's complete twelve-event GNG Western Insurrection response set is inventoried",
    )
    require(
        len(re.findall(r"id = GNG_Western_Insurrection\.1\b", native_yun_effects)) == 1
        and len(re.findall(r"id = GNG_Western_Insurrection\.8\b", native_yun_effects)) == 1
        and len(re.findall(r"id = GNG_Western_Insurrection\.7\b", native_peace_actions)) == 2
        and len(re.findall(r"id = GNG_Western_Insurrection\.12\b", native_peace_actions)) == 1,
        "all four native external GNG response entrypoint classes are inventoried",
    )
    flow_active = "\n".join(line.split("#", 1)[0] for line in flow_effects.splitlines())
    require(
        "country_event = { id = GNG_Western_Insurrection." not in flow_active
        and "WI_Start_effects = yes" not in flow_active
        and "WI_GAW_Start_Effects = yes" not in flow_active,
        "DOP runtime never calls native GNG response events or their two start effects",
    )
    for flag in (
        "CHI_Western_Insurrection_Crisis",
        "CHI_Yunnan_War",
        "YUN_NPA_GAW_Crisis",
        "JAP_Western_Insurrection_Intervention",
        "CHI_Western_Insurection_RoC_defeated",
    ):
        require(f"clr_global_flag = {flag}" in flow_effects, f"DOP clears native GNG-response gate {flag}")
    require(
        "YUN = { DOP_YUN_prepare_southwest_war = yes }" in flow_effects,
        "DOP crisis guarantees the isolated YUN prewar setup",
    )
    require(
        "retire_character = DOP_YUN_long_shengwu" in flow_effects
        and "YUN_southwest_reconstruction_effects = yes" in flow_effects,
        "DOP victory retires Long Shengwu and reuses TNO reconstruction mechanics",
    )
    for key in (
        "DOP_YUN_long_shengwu:0",
        "POLITICS_DOP_YUN_LONG_SHENGWU_DESC:0",
        "DOP_YUN_prepare_southwest_war_tt:0",
    ):
        require(key in flow_loc, f"YUN flow localisation exists: {key}")

    require("has_completed_focus = GNG_the_coming_storm" in flow_actions, "DOP automatically follows TNO's final Morita focus")
    require("load_focus_tree = DOP_GNG_opening_tree" in flow_effects, "stage 1 loads the opening tree")
    require("set_country_flag = DOP_GNG_mita_hitachi_leader" in flow_effects, "stage 1 records the Mita leadership handoff")
    replace_loc = read("localisation/simp_chinese/replace/TNO_Guangdong_l_simp_chinese.yml")
    require(
        "GNG_legco_hitachi_leader_70s" in replace_loc
        and "三田胜茂" in replace_loc
        and "【Placeholder：三田胜茂文本头像】" in replace_loc,
        "Hitachi's 1970s leader is Mita with an explicit missing-image placeholder",
    )

    for tag in ("CHI", "GNG", "YUN"):
        require(f"remove_from_faction = {tag}" in flow_effects, f"{tag} exits the CPS during the crisis")
    require("annex_country = { target = GUX transfer_troops = yes }" in flow_effects, "YUN absorbs the Guangxi warlord")
    require("target = YUN" in flow_effects and "autonomy_state = autonomy_free" in flow_effects, "YUN is freed from CHI before declaring war")
    for state in (591, 2474, 2475):
        require(f"transfer_state = {state}" in flow_effects, f"Hainan state {state} participates in the revolt/settlement")
    require("declare_war_on = { target = CHI type = annex_everything }" in flow_effects, "YUN begins the RGOC war")
    require("declare_war_on = { target = GNG type = annex_everything }" in flow_effects, "YUN later brings Guangdong into the war")
    require(
        'division_template = "Sensha Shidan - Armored Division"' in flow_effects
        and "delete_units = {" in flow_effects,
        "Guangdong's existing armoured formation is removed on entry",
    )
    war_modifier_apply = flow_effects.split(
        "DOP_GNG_apply_southwest_war_state_modifiers = {", 1
    )[1].split("DOP_GNG_remove_southwest_war_state_modifiers = {", 1)[0]
    require(
        "every_owned_state = {" in war_modifier_apply
        and "GNG_is_pearl_river_delta_state = yes" in war_modifier_apply,
        "every GNG-owned state is classified by TNO's canonical Pearl River Delta trigger",
    )
    require(
        war_modifier_apply.count("add_dynamic_modifier = { modifier = DOP_GNG_prd_wartime_defence }") == 1
        and war_modifier_apply.count("add_dynamic_modifier = { modifier = DOP_GNG_outer_wartime_defence }") == 1,
        "all GNG states receive exactly one core-or-outer wartime modifier branch",
    )
    require(
        war_modifier_apply.count("any_neighbor_state = { is_controlled_by = CHI }") == 1
        and war_modifier_apply.count("any_neighbor_state = { is_controlled_by = YUN }") == 1
        and war_modifier_apply.count("add_dynamic_modifier = { modifier = DOP_GNG_southwest_stalemate }") == 1,
        "both sides of every actual YUN-CHI border receive the DOP stalemate modifier",
    )
    require(
        "attacker_modifier = yes" in flow_modifiers
        and "army_speed_factor = -0.75" in flow_modifiers
        and "army_attack_factor = -0.90" in flow_modifiers
        and "local_org_regain = -0.50" in flow_modifiers,
        "DOP stalemate modifier mirrors TNO's Spanish-style offensive lock",
    )
    war_modifier_remove = flow_effects.split(
        "DOP_GNG_remove_southwest_war_state_modifiers = {", 1
    )[1].split("DOP_GNG_begin_southwest_crisis = {", 1)[0]
    require(
        "every_state = {" in war_modifier_remove
        and "remove_dynamic_modifier = { modifier = DOP_GNG_southwest_stalemate }" in war_modifier_remove,
        "all dynamically selected wartime states are cleaned after victory",
    )
    require(
        war_modifier_remove.count("remove_dynamic_modifier = { modifier = unplanned_offensive }") == 6,
        "six legacy hardcoded stalemate modifiers have migration cleanup",
    )
    require("1017 = { is_controlled_by = YUN }" in flow_actions, "Maoming loss is the reinforcement trigger")
    require(
        "DOP_GNG_maoming_survival_days = 14" in flow_actions
        and "fourteen-day survival clock" in flow_actions
        and "else_if = {" in flow_actions,
        "Maoming starts a full fourteen-day survival clock without same-tick decrement",
    )
    reinforcement = flow_effects.split(
        "DOP_GNG_spawn_japanese_reinforcements = {", 1
    )[1].split("DOP_GNG_complete_southwest_war = {", 1)[0]
    for token in (
        "add_to_faction = CHI",
        "add_to_faction = GNG",
        "targeted_alliance = GNG",
        "enemy = YUN",
        "single_target_only = yes",
        "country_event = { id = DOP_GNG_flow.16 hours = 12 }",
    ):
        require(token in reinforcement, f"Japanese intervention contains {token}")
    require(
        "create_unit = {" not in reinforcement and "1853 = {" not in reinforcement,
        "same-tick intervention performs no unit creation and never uses Takao",
    )
    deployment = event(flow_events, "DOP_GNG_flow.16")
    for token in (
        "hidden = yes",
        "has_war_with = YUN",
        'load_oob = "DOP_JAP_southwest_reinforcements"',
        "592 = {",
        'division_template = \\"DOP Nanshin Sensha Shidan\\"',
        "owner = JAP",
        "count = 12",
        "set_country_flag = DOP_JAP_southwest_reinforcements_deployed",
        "country_event = { id = DOP_GNG_flow.16 hours = 12 }",
        "GNG = { country_event = { id = DOP_GNG_flow.4 hours = 1 } }",
    ):
        require(token in deployment, f"delayed Guangzhou deployment contains {token}")
    require(
        'name = "DOP Nanshin Sensha Shidan"' in jap_reinforcement_oob
        and "MBT = {" in jap_reinforcement_oob
        and "motorized = {" in jap_reinforcement_oob,
        "JAP reinforcements use a unique armoured OOB template",
    )
    require(
        'division_template = "DOP Nanshin Sensha Shidan"' in flow_effects
        and "delete_unit_template_and_units = {" in flow_effects,
        "postwar cleanup deletes only the dedicated JAP reinforcement template and units",
    )
    for token in (
        "has_war_with = YUN",
        "type = conquer",
        "id = YUN",
        "type = front_unit_request",
        "type = front_control",
        "execution_type = rush",
        "abort_when_not_enabled = yes",
    ):
        require(token in jap_ai, f"JAP wartime AI plan contains {token}")

    victory_states = (326, 592, 593, 729, 1017, 1438, 1439)
    require(
        all(f"controls_state = {state}" in flow_actions for state in victory_states),
        "victory still requires every original Guangdong state",
    )
    kunming_trigger = flow_actions.split("325 = {", 1)[1].split("}", 2)[0]
    require(
        all(f"is_controlled_by = {tag}" in kunming_trigger for tag in ("GNG", "JAP", "CHI")),
        "Kunming may be occupied by GNG, JAP or CHI for DOP victory",
    )
    for state in (1464, 2472, 591, 2474, 2475):
        require(f"transfer_state = {state}" in flow_effects, f"postwar Guangdong receives state {state}")
    require("target = GUX" in flow_effects and "autonomy_state = autonomy_reliant" in flow_effects, "GUX becomes a Guangdong client")
    require(
        "tree = ZZZ_blank_focus" in flow_effects
        and "keep_completed = no" in flow_effects,
        "released GUX is explicitly assigned TNO's empty focus tree",
    )
    require("target = YUN" in flow_effects and "autonomy_state = autonomy_military_government" in flow_effects, "YUN becomes the southwest reconstruction government under CHI")
    require(
        "clr_country_flag = YUN_long_yun_crusade" in flow_effects
        and "tree = YUN_post_xinan" in flow_effects,
        "postwar YUN leaves the NPA tree and returns to its reconstruction tree",
    )
    require("load_focus_tree = dop_sonyjapan_reconsturuction_tree" in flow_effects, "victory loads the reconstruction tree")

    for flag in (
        "GNG_IJA_Disable_LegCo",
        "GNG_Google_Maps_Show",
        "GNG_Three_Evils_Show",
        "GNG_PTRG_deccat_visible",
        "GNG_Product_Decisions_GUI_show",
        "GNG_Economic_Graphs_Show",
    ):
        require(flag in flow_effects, f"GUI flow controls {flag}")
    for current, following in zip(range(10, 15), range(11, 16)):
        require(
            f"id = DOP_GNG_flow.{following} days = 1" in flow_events.split(f"id = DOP_GNG_flow.{current}", 1)[1],
            f"GUI lock event {current} advances to {following}",
        )

    reconstruction = read("common/national_focus/dop_sony-japan_reconstruction.txt")
    unlocks = {
        "GNG_focus_temporary_relief": "DOP_GNG_restore_legco = yes",
        "GNG_focus_foothold": "DOP_GNG_restore_map_and_extra_regions = yes",
        "GNG_focus_leave_ruins_behind": "DOP_GNG_unlock_construction_stage = yes",
        "DOP_GNG_recon_foundation": "DOP_GNG_unlock_scw_stage = yes",
        "DOP_GNG_recon_backwardness_disaster": "DOP_GNG_unlock_gsa_stage = yes",
        "DOP_GNG_recon_no_time_to_turn": "DOP_GNG_restore_economy_compare = yes",
        "GNG_focus_new_products_old_friends": "DOP_GNG_restore_product_cycle = yes",
    }
    for focus_id, effect in unlocks.items():
        require(effect in focus(reconstruction, focus_id), f"{focus_id} owns its specified GUI unlock")
    product_focus = focus(reconstruction, "GNG_focus_new_products_old_friends")
    require("focus = DOP_GNG_recon_status_agreement" in product_focus, "product cycle keeps its authored predecessor")
    require("DOP_GNG_enter_core_stage = yes" not in product_focus, "mid-tree product cycle does not leave reconstruction")
    require("DOP_GNG_enter_core_stage = yes" in focus(reconstruction, "DOP_GNG_recon_opening_ceremony"), "authored reconstruction endpoint enters stage 4")
    require(
        "focus = GNG_focus_new_products_old_friends" in focus(reconstruction, "DOP_GNG_recon_foundation"),
        "SCW foundation keeps the authored layout dependency",
    )

    construction_unlock = flow_effects.split("DOP_GNG_unlock_construction_stage = {", 1)[1].split("DOP_GNG_unlock_scw_stage = {", 1)[0]
    require("DOP_construction_target_project = 12" in construction_unlock, "construction initially opens Guangxi Industrial Institute")
    require("DOP_construction_target_project = 13" in construction_unlock, "construction initially opens Guangxi expressways")
    require(construction_unlock.count("DOP_construction_show_project = yes") == 2, "initial construction projects are only shown")
    require("DOP_construction_start_project" not in construction_unlock and "show_and_start" not in construction_unlock, "initial construction projects do not auto-start")

    bop = read("common/bop/DOP_BoP_Defines.txt")
    require("BoP_Tab_DOPSiliconCW_GNG" in bop, "SCW BoP tab is registered")
    require("BoP_Tab_DOPScienceAcademy_GNG" in bop, "Science Academy BoP tab is registered separately")
    require("BoP_Tab_DOPConstruction_GNG" in bop, "Construction BoP tab is registered")
    scw_effects = read("common/scripted_effects/DOP_SCW_effects.txt")
    require("has_country_flag = DOP_GSA_enabled" in scw_effects, "Science Academy initialization is idempotent")
    require("DOP_GSA_research_1_ibuka_scored" in scw_effects and "DOP_GNG_add_ibuka_point = yes" in scw_effects, "current Science Academy project awards one protected Ibuka point")

    construction_rewards = read("common/scripted_effects/DOP_construction_rewards.txt")
    require(construction_rewards.count("DOP_GNG_add_ibuka_point = yes") == 4, "four construction projects award Ibuka points")
    require(construction_rewards.count("Ibuka score") == 4, "four construction Ibuka sources carry generator markers")
    require(flow_effects.count("compare = less_than") == 4, "SCW rank compares Guangdong with all four opponents")
    require("DOP_GNG_scw_rank_points_awarded = 4" in flow_effects, "SCW rank starts from four points")
    require("has_country_flag = DOP_SCW_initialized" in flow_effects.split("DOP_GNG_score_scw_rank_once = {", 1)[1], "SCW rank cannot score before initialization")
    require("var = DOP_GNG_ibuka_points value = 9 compare = greater_than_or_equals" in flow_effects, "Ibuka route threshold is nine points")

    core = read("common/national_focus/dop_sony-japan_core.txt")
    opening = read("common/national_focus/dop_sony-opening.txt")
    require("select_effect = {" in focus(opening, "DOP_GNG_faux_opening"), "opening transition fires on focus selection")
    require(
        sum(read(relative).count("# DOP BESPOKE 260902B axes:") for relative in (
            "common/national_focus/dop_sony-opening.txt",
            "common/national_focus/dop_sony-japan_prewar.txt",
            "common/national_focus/dop_sony-japan_reconstruction.txt",
            "common/national_focus/dop_sony-japan_core.txt",
            "common/national_focus/dop_sony-japan_ending1_lee.txt",
            "common/national_focus/dop_sony-japan_ending2_ibuka.txt",
            "common/national_focus/dop_sony-japan_ending3_hitachi.txt",
        )) == 142,
        "142 focuses carry bespoke 260902B effects",
    )
    require("DOP_GNG_reward_" not in opening + reconstruction + core, "generic reward-package calls are absent")

    normal_runtime = "\n".join(
        read(relative)
        for relative in (
            "common/decisions/DOP_SCW_decisions.txt",
            "common/scripted_effects/DOP_SCW_effects.txt",
            "common/on_actions/TNO_Guangdong_on_actions.txt",
            "common/on_actions/DOP_GNG_flow_on_actions.txt",
            "localisation/simp_chinese/DOP_SCW_decisions_l_simp_chinese.yml",
        )
    )
    for token in (
        "DOP_SCW_stage_integrity_change",
        "DOP_SCW_supervisor_attitude_change",
        "DOP_SCW_audience_patience_change",
        "DOP_SCW_sync_theater_stage_integrity",
        "舞台完整度",
        "监制的态度",
        "观众的耐心",
    ):
        require(token not in normal_runtime, f"unfinished theatre token absent from normal runtime: {token}")
    require("set_country_flag = guang_dong_theater_visible" not in flow_effects + reconstruction + core, "normal flow never opens the Guangdong theatre")

    postwar_loc = read("localisation/simp_chinese/DOP_GNG_postwar_ideas_l_simp_chinese.yml")
    for authored_name in ("举目所及，风雨飘摇", "安保部门，方兴未艾", "国家的剑与盾"):
        require(authored_name in postwar_loc, f"author-supplied security spirit name is used: {authored_name}")

    print("DOP CONTENT FLOW STATIC ACCEPTANCE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
