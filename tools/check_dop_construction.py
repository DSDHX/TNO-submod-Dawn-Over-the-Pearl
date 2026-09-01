from __future__ import annotations

import argparse
import importlib.util
import re
import struct
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TNO_ROOT = Path(
    r"D:\Steam\steamapps\workshop\content\394360\2438003901"
)
DEFAULT_TNO_CN_ROOT = Path(
    r"D:\Steam\steamapps\workshop\content\394360\2243912940"
)
DEFAULT_SOURCE_DIR = ROOT / "output/imagegen/construction_previews/sources"
ACADEMY_BORDER_COLOR = (89, 199, 194, 255)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)
    print(f"PASS  {message}")


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def generated_data() -> tuple[tuple, tuple, dict]:
    sys.dont_write_bytecode = True
    path = ROOT / "tools/generate_dop_construction.py"
    spec = importlib.util.spec_from_file_location(
        "dop_construction_generator_data", path
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
        return module.REGIONS, module.PROJECTS, module.REWARDS
    finally:
        sys.modules.pop(spec.name, None)


def parse_tno_rail_edges(path: Path) -> set[tuple[int, int]]:
    edges: set[tuple[int, int]] = set()
    bad_counts: list[str] = []
    for raw_line in text(path).splitlines():
        fields = raw_line.split("#", 1)[0].split()
        if len(fields) < 4:
            continue
        try:
            count = int(fields[1])
            provinces = [int(value) for value in fields[2:]]
        except ValueError:
            continue
        if count != len(provinces):
            bad_counts.append(raw_line[:96])
        edges.update(tuple(sorted(pair)) for pair in zip(provinces, provinces[1:]))
    require(not bad_counts, "all current TNO railway declaration counts match")
    return edges


def parse_tno_state_map(
    state_dir: Path,
) -> tuple[dict[int, int], dict[int, str], dict[int, str]]:
    province_to_state: dict[int, int] = {}
    state_name: dict[int, str] = {}
    state_owner: dict[int, str] = {}
    for path in state_dir.glob("*.txt"):
        source = text(path)
        id_match = re.search(r"\bid\s*=\s*(\d+)", source)
        province_match = re.search(
            r"\bprovinces\s*=\s*\{([^}]*)\}", source, re.DOTALL
        )
        if not id_match or not province_match:
            continue
        state_id = int(id_match.group(1))
        owner_match = re.search(r"\bowner\s*=\s*(\w+)", source)
        state_name[state_id] = path.stem
        state_owner[state_id] = owner_match.group(1) if owner_match else "UNKNOWN"
        for province in map(int, re.findall(r"\d+", province_match.group(1))):
            province_to_state[province] = state_id
    return province_to_state, state_name, state_owner


def validate_railways(
    rewards_source: str, tno_root: Path
) -> list[tuple[int, ...]]:
    paths = [
        tuple(map(int, re.findall(r"\d+", match.group(1))))
        for match in re.finditer(
            r"build_railway\s*=\s*\{.*?\bpath\s*=\s*\{([^}]*)\}",
            rewards_source,
            re.DOTALL,
        )
    ]
    require(len(paths) == 5, "five intended build_railway paths are defined")
    edges = parse_tno_rail_edges(tno_root / "map/railways.txt")
    province_to_state, state_name, state_owner = parse_tno_state_map(
        tno_root / "history/states"
    )
    for index, path in enumerate(paths, 1):
        missing = [
            pair
            for pair in zip(path, path[1:])
            if tuple(sorted(pair)) not in edges
        ]
        require(not missing, f"railway path {index} is continuous in current TNO")
        route = []
        for province in path:
            state_id = province_to_state.get(province)
            require(state_id is not None, f"province {province} belongs to a TNO state")
            owner = state_owner[state_id]
            require(
                owner in {"GNG", "GUX"},
                f"province {province} stays in intended GNG/GUX territory",
            )
            route.append(f"{province}:{state_name[state_id]}:{owner}")
        print(f"      route {index}: " + " -> ".join(route))
    return paths


def validate_dds(path: Path) -> None:
    payload = path.read_bytes()
    require(payload[:4] == b"DDS ", f"{path.name} has DDS magic")
    width = struct.unpack_from("<I", payload, 16)[0]
    height = struct.unpack_from("<I", payload, 12)[0]
    depth = struct.unpack_from("<I", payload, 24)[0]
    mipmaps = struct.unpack_from("<I", payload, 28)[0]
    require(
        (width, height, depth, mipmaps) == (285, 551, 0, 0),
        f"{path.name} is 285x551 with full-height right-panel metadata",
    )
    pixel_flags = struct.unpack_from("<I", payload, 80)[0]
    rgb_bits = struct.unpack_from("<I", payload, 88)[0]
    masks = tuple(
        struct.unpack_from("<I", payload, offset)[0]
        for offset in (92, 96, 100, 104)
    )
    require(
        (
            pixel_flags,
            payload[84:88],
            rgb_bits,
            masks,
        )
        == (
            0x41,
            b"\0\0\0\0",
            32,
            (0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000),
        ),
        f"{path.name} uses the Academy reference's uncompressed 32-bit RGBA format",
    )
    with Image.open(path) as image:
        image = image.convert("RGBA")
    for inset in (0, 1):
        ring = (
            [image.getpixel((x, inset)) for x in range(inset, width - inset)]
            + [image.getpixel((x, height - 1 - inset)) for x in range(inset, width - inset)]
            + [image.getpixel((inset, y)) for y in range(inset + 1, height - 1 - inset)]
            + [image.getpixel((width - 1 - inset, y)) for y in range(inset + 1, height - 1 - inset)]
        )
        require(
            set(ring) == {ACADEMY_BORDER_COLOR},
            f"{path.name} border inset {inset} is Academy cyan #59C7C2",
        )


def validate_gng_app_scopes(source: str) -> None:
    depth = 0
    state_depths: list[int] = []
    helper_count = 0
    failures: list[int] = []
    for line_number, line in enumerate(source.splitlines(), 1):
        state_open = re.match(r"^\s*\d+\s*=\s*\{", line)
        if state_open:
            state_depths.append(depth + 1)
        if re.search(
            r"\bGNG_(?:chinese|zhujin|japanese)_app_change\s*=\s*yes", line
        ):
            helper_count += 1
            if not state_depths:
                failures.append(line_number)
        depth += line.count("{") - line.count("}")
        state_depths = [state_depth for state_depth in state_depths if depth >= state_depth]
    require(helper_count > 0, "GNG satisfaction helpers are used by project rewards")
    require(
        not failures,
        "every GNG satisfaction helper call executes inside a numeric state scope",
    )


def validate_reward_geography(source: str, tno_root: Path) -> None:
    province_to_state, state_name, state_owner = parse_tno_state_map(
        tno_root / "history/states"
    )
    available_states = set(state_name)
    state_scopes = {
        int(value)
        for value in re.findall(r"(?m)^\s*(\d+)\s*=\s*\{", source)
    }
    require(
        state_scopes <= available_states,
        "every numeric reward state scope exists in current TNO",
    )
    province_targets = {
        int(value) for value in re.findall(r"\bprovince\s*=\s*(\d+)", source)
    }
    require(
        province_targets <= set(province_to_state),
        "every province-specific reward target exists in current TNO",
    )
    require(
        all(
            state_owner[province_to_state[province]] in {"GNG", "GUX"}
            for province in province_targets
        ),
        "every province-specific reward target stays in intended GNG/GUX territory",
    )


def validate_tno_component_localisation(tno_cn_root: Path) -> None:
    localisation_dir = tno_cn_root / "localisation/simp_chinese"
    sources = "\n".join(
        text(localisation_dir / name)
        for name in (
            "TNO_Guangdong_l_simp_chinese.yml",
            "TNO_societal_development_l_simp_chinese.yml",
            "TNO_economy_l_simp_chinese.yml",
            "modifiers_l_simp_chinese.yml",
        )
    )
    required = (
        "GNG_chi_app_temp_increase_tt:",
        "GNG_zhu_app_temp_increase_tt:",
        "GNG_jap_app_temp_increase_tt:",
        "GNG_Three_Evils_change_decrease_tt:",
        "TNO_econ_pus_increase_tt:",
        "TNO_econ_misc_income_increase_tt:",
        "improve_academic_base_small:",
        "improve_admin_efficiency_small:",
        "improve_industrial_expertise_small:",
        "improve_poverty_small:",
        "MODIFIER_RESEARCH_SPEED_FACTOR:",
        "MODIFIER_LOCAL_RESOURCES_FACTOR:",
        "MODIFIER_TRADE_OPINION_FACTOR:",
    )
    require(
        all(key in sources for key in required),
        "all referenced TNO Chinese effect components exist",
    )
    require(
        "§E珠人§!" in sources
        and "§e日侨§!" in sources
        and "§Y政府支持率§!" in sources
        and "§Y教育水平§!" in sources,
        "TNO Chinese component terminology is available and canonical",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Static acceptance checks for the DOP construction system."
    )
    parser.add_argument("--tno-root", type=Path, default=DEFAULT_TNO_ROOT)
    parser.add_argument(
        "--tno-cn-root", type=Path, default=DEFAULT_TNO_CN_ROOT
    )
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    args = parser.parse_args()

    regions, projects, rewards = generated_data()
    require(len(regions) == 6, "registry contains exactly six regions")
    require(len(projects) == 20, "registry contains exactly twenty projects")
    require(
        tuple((region.id, region.slug, region.name) for region in regions)
        == (
            (1, "prd", "珠三角"),
            (2, "chaoshan", "粤东"),
            (3, "northern_guangdong", "粤北"),
            (4, "western_guangdong", "粤西"),
            (5, "jiaoyang", "交洋"),
            (6, "guangxi", "广西"),
        ),
        "region IDs and names match the six-region specification",
    )
    expected_projects = {
        1: ("sky_tower", "prd", 150000, "白鹅新区晴空塔"),
        2: ("rose_garden", "prd", 100000, "玫瑰园计划"),
        3: ("alice_dream_factory", "prd", 30000, "粤海爱丽丝梦工厂"),
        4: ("daya_bay_nuclear_plant", "prd", 45000, "大亚湾核电站"),
        5: ("guangdong_shinkansen", "prd", 90000, "广东新干线计划"),
        6: ("chaoshan_university", "chaoshan", 30000, "潮汕大学"),
        7: ("xinfengjiang_reservoir", "northern_guangdong", 60000, "山区水库开发计划"),
        8: ("luoding_granary", "western_guangdong", 40000, "粤西盆地储粮工程"),
        9: ("pinglu_canal", "jiaoyang", 100000, "平陆运河"),
        10: ("south_china_sea_drilling_platform", "jiaoyang", 30000, "南海油气开采"),
        11: ("wenchang_space_center", "jiaoyang", 50000, "文昌卫星发射中心"),
        12: ("guangxi_industrial_institute", "guangxi", 60000, "重整广西实业院"),
        13: ("guangxi_expressway_network", "guangxi", 90000, "广西高速公路网"),
        14: ("nanyue_folk_memorial_park", "guangxi", 30000, "“南粤之心”民俗纪念园"),
        15: ("lijiang_waterway", "guangxi", 30000, "漓江航道开发工程"),
        16: ("honghe_fan_asia_friendship_pass", "guangxi", 30000, "红河泛亚友谊关"),
        17: ("prd_maglev", "prd", 90000, "珠三角磁悬浮城轨"),
        18: ("shantou_chaozhou_jieyang_integration", "chaoshan", 60000, "汕潮揭一体化方案"),
        19: ("granite_uranium_mining", "northern_guangdong", 60000, "开采花岗岩型铀矿"),
        20: ("shale_oil_refineries", "western_guangdong", 30000, "拓展页岩油化工厂"),
    }
    require(
        {
            project.id: (project.slug, project.region, project.total, project.name)
            for project in projects
        }
        == expected_projects,
        "all project IDs, regions, quantities and names match the specification",
    )
    description_fragments = {
        1: "广州是一座老城",
        2: "香港的旧机场建得实在太早",
        3: "澳门，创收之地，梦之地",
        4: "珠三角的繁荣需要燃料浇筑",
        5: "广东新干线将主要分为两段修建",
        13: "广西被民族主义军阀占据太久",
        17: "随着珠三角三城及其中间地带的蓬勃发展",
    }
    require(
        all(
            fragment in next(project.desc for project in projects if project.id == project_id)
            for project_id, fragment in description_fragments.items()
        ),
        "user-provided project descriptions stay attached to the intended IDs",
    )
    require(set(rewards) == set(range(1, 21)), "every project has one reward")
    require(
        len({project.source for project in projects}) == 20,
        "all twenty approved source names are unique",
    )
    require(
        all((args.source_dir / project.source).is_file() for project in projects),
        "all twenty approved source files exist",
    )
    reward_lines = [
        line for reward_data in rewards.values() for line in reward_data.effect
    ]

    def reward_total(variable: str, setter: str) -> Decimal:
        pattern = re.compile(
            rf"{setter}\s*=\s*\{{\s*{re.escape(variable)}\s*=\s*"
            r"(-?\d+(?:\.\d+)?)"
        )
        return sum(
            (
                Decimal(value)
                for line in reward_lines
                for value in pattern.findall(line)
            ),
            Decimal("0"),
        )

    require(
        not any("political_power" in line for line in reward_lines),
        "completion reward amplification leaves political power untouched",
    )
    social_values = {
        "really_low": Decimal("0.5"),
        "low": Decimal("1"),
        "med": Decimal("2"),
        "high": Decimal("3"),
    }
    poverty_values = {
        "low": Decimal("0.03"),
        "med": Decimal("0.06"),
        "high": Decimal("0.09"),
    }
    social_totals = {
        area: sum(
            (
                poverty_values[tier]
                if area == "poverty"
                else social_values[tier]
                for line in reward_lines
                for matched_area, tier in re.findall(
                    r"TNO_improve_(academic_base|research_facilities|"
                    r"agriculture|admin_efficiency|industrial_equipment|"
                    r"industrial_expertise|poverty)_"
                    r"(really_low|low|med|high)",
                    line,
                )
                if matched_area == area
            ),
            Decimal("0"),
        )
        for area in (
            "academic_base",
            "research_facilities",
            "agriculture",
            "admin_efficiency",
            "industrial_equipment",
            "industrial_expertise",
            "poverty",
        )
    }
    require(
        social_totals
        == {
            "academic_base": Decimal("12"),
            "research_facilities": Decimal("12"),
            "agriculture": Decimal("12"),
            "admin_efficiency": Decimal("28"),
            "industrial_equipment": Decimal("22"),
            "industrial_expertise": Decimal("22"),
            "poverty": Decimal("0.66"),
        },
        "completion rewards preserve the doubled social-development payload",
    )
    require(
        reward_total(
            "DOP_construction_reward_misc_income", "add_to_variable"
        )
        == Decimal("2.90")
        and reward_total(
            "DOP_construction_reward_free_pu", "add_to_variable"
        )
        == Decimal("8")
        and reward_total(
            "DOP_construction_reward_research_speed", "add_to_variable"
        )
        == Decimal("0.07")
        and reward_total(
            "DOP_construction_reward_resource_factor", "add_to_variable"
        )
        == Decimal("0.12"),
        "persistent non-PP reward totals are doubled",
    )
    require(
        reward_total("GNG_corruption_temp_var", "set_temp_variable")
        == Decimal("-24"),
        "total corruption improvement is doubled from 12 to 24",
    )
    approval_magnitude = sum(
        (
            abs(reward_total(variable, "set_temp_variable"))
            for variable in ("chi_app_temp", "zhu_app_temp", "jap_app_temp")
        ),
        Decimal("0"),
    )
    require(
        approval_magnitude == Decimal("196"),
        "net faction approval payload is doubled",
    )

    generator = subprocess.run(
        [sys.executable, str(ROOT / "tools/generate_dop_construction.py"), "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    require(
        generator.returncode == 0,
        "generated registry, rewards, events, GFX, localisation and docs are current",
    )

    effects = text(ROOT / "common/scripted_effects/DOP_construction_effects.txt")
    reconstruction_focus = text(
        ROOT / "common/national_focus/dop_sony-japan_reconstruction.txt"
    )
    scw_on_actions = text(ROOT / "common/on_actions/DOP_SCW_on_actions.txt")
    reward_effects = text(
        ROOT / "common/scripted_effects/DOP_construction_rewards.txt"
    )
    events = text(ROOT / "events/DOP_GNG_construction.txt")
    gfx = text(ROOT / "interface/GUI/DOP_construction.gfx")
    gui = text(ROOT / "interface/GUI/DOP_construction_interface.gui")
    scripted_gui = text(ROOT / "common/scripted_guis/DOP_Construction_GUI.txt")
    preview_builder = text(ROOT / "tools/build_dop_construction_previews.py")
    modifiers = text(
        ROOT / "common/dynamic_modifiers/DOP_construction_dynamic_modifiers.txt"
    )
    on_actions = text(ROOT / "common/on_actions/dop_bop_on_actions.txt")
    localisation = text(
        ROOT / "localisation/simp_chinese/DOP_Construction_l_simp_chinese.yml"
    )
    require(
        "multiply_temp_variable = { DOP_construction_contribution = -0.04 }"
        in effects
        and "clamp_variable = { var = DOP_construction_mobilisation_pp_gain min = -0.5 max = 0.2 }"
        in effects,
        "mobilisation political-power coefficient and clamp remain unchanged",
    )
    for variable, coefficient, minimum, maximum in (
        ("stability_weekly", "-0.00016", "-0.003", "0.0008"),
        ("expertise_monthly", "1.6", "-6", "16"),
        ("poverty_monthly", "-1", "-12", "8"),
        ("admin_monthly", "-0.8", "-10", "6"),
        ("chinese_monthly", "0.24", "-3", "3"),
        ("zhujin_monthly", "-0.06", "-3", "3"),
        ("japanese_monthly", "-0.20", "-3", "3"),
    ):
        require(
            f"multiply_temp_variable = {{ DOP_construction_contribution = {coefficient} }}"
            in effects
            and (
                f"clamp_variable = {{ var = DOP_construction_mobilisation_{variable} "
                f"min = {minimum} max = {maximum} }}"
            )
            in effects,
            f"mobilisation {variable} coefficient and clamp match the current balance",
        )

    require(
        "production_units_use = DOP_construction_total_pu_occupied" in modifiers
        and "free_production_units_modifier = DOP_construction_free_pu_modifier"
        not in modifiers
        and "free_production_units_modifier = DOP_construction_reward_free_pu"
        in modifiers
        and "DOP_construction_special_pu_registered" in effects
        and "recalculate_PUs_on_demand = yes" in effects,
        "construction burden uses TNO special-project PUs and refreshes on change",
    )
    for widget in ("construction_funding_effects", "construction_manpower_effects"):
        require(
            re.search(
                rf"name = {widget}\s+position = \{{[^}}]+\}}\s+"
                r"font = aldrich_16_outline",
                gui,
            )
            is not None,
            f"{widget} uses the enlarged 16-point font",
        )

    require(
        len(re.findall(r"^country_event\s*=\s*\{", events, re.MULTILINE)) == 20,
        "completion event file contains twenty visible triggered events",
    )
    require(
        len(re.findall(r"^\toption\s*=\s*\{", events, re.MULTILINE)) == 20,
        "each completion event has exactly one visible option",
    )
    require(
        len(
            re.findall(
                r"^DOP_construction_\w+_completion_effect\s*=\s*\{",
                reward_effects,
                re.MULTILINE,
            )
        )
        == 20,
        "reward file contains twenty project callbacks",
    )
    require(
        len(re.findall(r'name = "GFX_DOP_construction_project_\d\d"', gfx)) == 20,
        "GFX file contains twenty independent project sprites",
    )
    require(
        'image = "GFX_[?DOP_construction_selected_image.GetTokenKey]"'
        in scripted_gui,
        "project image is selected dynamically by token",
    )
    require(
        re.search(
            r"name = construction_project_image\s+"
            r"spriteType = GFX_DOP_construction_project_01\s+"
            r"position = \{ x = 755 y = 67 \}",
            gui,
        )
        is not None
        and "WIDTH = 285" in preview_builder
        and "HEIGHT = 551" in preview_builder,
        "project image occupies the full 285x551 right panel at native size",
    )
    require(
        "name = construction_description_scroll" in gui
        and 'verticalScrollbar = "right_vertical_slider"' in gui
        and "maxHeight = 10000" in gui
        and "name = construction_description_button" in gui,
        "long project descriptions use a dedicated scrollable viewport",
    )
    require(
        "name = construction_numbers" in gui
        and "text = DOP_construction_selected_numbers" in gui,
        "engineering quantities remain directly visible in the main GUI",
    )
    require(
        "array = DOP_construction_directory_items" in scripted_gui
        and "DOP_construction_toggle_directory_region = yes" in scripted_gui,
        "construction directory remains dynamic and region folders remain collapsible",
    )
    public_project_api = effects.split(
        "# Public project-state API for focuses, decisions and events.", 1
    )[1].split("# Bulk helpers deliberately omit", 1)[0]
    require(
        public_project_api.count("effect_tooltip = {") == 3
        and public_project_api.count("hidden_effect = {") == 3
        and all(
            f"custom_effect_tooltip = {tooltip}" in public_project_api
            for tooltip in (
                "DOP_construction_show_project_tt",
                "DOP_construction_start_project_tt",
                "DOP_construction_show_and_start_project_tt",
            )
        ),
        "three single-project APIs use LegCo-style effect tooltips and hidden execution",
    )
    construction_initializer = effects.split(
        "GNG_BOP_Construction_Initialize = {", 1
    )[1].split("DOP_construction_reset = {", 1)[0]
    require(
        "custom_effect_tooltip = TNO_BoP_AddTab_GNG_tt" in construction_initializer
        and construction_initializer.count("effect_tooltip = {") == 1
        and construction_initializer.count("hidden_effect = {") == 1
        and "DOP_construction_ensure_dynamic_modifiers = yes" in construction_initializer
        and "DOP_SCW" not in construction_initializer,
        "construction initializer exposes only the existing unlock tooltip",
    )
    scw_daily = scw_on_actions.split("on_daily = {", 1)[1].split(
        "on_yearly = {", 1
    )[0]
    require(
        "has_country_flag = DOP_SCW_enabled" in scw_daily
        and "DOP_SCW_activate_decision_system = yes" in scw_daily,
        "SCW daily activation requires its own explicit enabled flag",
    )
    ruins_focus = reconstruction_focus.split(
        "id = GNG_focus_leave_ruins_behind", 1
    )[1].split("id = GNG_focus_in_the_warm_sun", 1)[0]
    require(
        "add_building_construction" not in ruins_focus
        and "country_event = { id = DOP_GNG_event.152 days = 0 }" in ruins_focus
        and "GNG_BOP_Construction_Initialize = yes" in ruins_focus
        and "set_temp_variable = { DOP_construction_target_project = 13 }" in ruins_focus
        and "DOP_construction_show_and_start_project = yes" in ruins_focus,
        "leave-ruins focus fires its event, unlocks Construction and starts project 13",
    )
    require(
        gui.count("name = construction_description_button") == 1
        and gui.count("name = construction_effect_overlay_button") == 1,
        "GUI has one shared description/effect-preview area",
    )
    cleaned_sources = {
        6: "06_chaoshan_university.png",
        7: "07_mountain_reservoirs.png",
        8: "08_western_guangdong_granary.png",
        12: "12_guangxi_industrial_institute.png",
        17: "17_prd_maglev.png",
    }
    require(
        all(
            (
                ROOT
                / "output/imagegen/construction_previews/cleaned"
                / file_name
            ).is_file()
            for file_name in cleaned_sources.values()
        )
        and all(
            f'{project_id}: "{file_name}"' in preview_builder
            for project_id, file_name in cleaned_sources.items()
        ),
        "five text/logo-cleaned real-photo inputs exist and are wired to the builder",
    )
    require(
        (ROOT / "docs/DOP_construction_image_cleanup_prompts.md").is_file()
        and (ROOT / "docs/DOP_construction_image_sources.md").is_file(),
        "image sources, licences, cleanup methods and prompts are documented",
    )
    require(
        "DOP_construction_preview_selected_reward = yes" in scripted_gui
        and "effect_tooltip = { DOP_construction_dispatch_reward_callback = yes }"
        in reward_effects,
        "effect overlay previews the same real callback used by rewards",
    )
    require(
        not re.search(
            r"custom_effect_tooltip\s*=\s*"
            r"DOP_construction_\w+_effect_tt",
            reward_effects,
        )
        and all(
            f"DOP_construction_{project.slug}_effect_tt:" not in localisation
            for project in projects
        ),
        "project rewards no longer use hand-written aggregate effect text",
    )
    require(
        all(
            component in reward_effects
            for component in (
                "DOP_construction_add_misc_income_reward = yes",
                "DOP_construction_add_free_pu_reward = yes",
                "DOP_construction_add_research_speed_reward = yes",
                "DOP_construction_add_resource_factor_reward = yes",
                "DOP_construction_add_trade_opinion_reward = yes",
            )
        ),
        "DOP-only persistent rewards call reusable effect components",
    )
    require(
        all(
            not re.search(
                rf"DOP_construction_{re.escape(project.slug)}_completion_effect"
                r"\s*=\s*\{\s*(?:custom_effect_tooltip|hidden_effect)",
                reward_effects,
            )
            for project in projects
        ),
        "project callbacks expose their real TNO and engine effect components",
    )
    require(
        "DOP_construction_process_completion_queue = yes" in on_actions
        and "DOP_construction_event_fired_today" in reward_effects,
        "daily completion queue is wired for at most one event per day",
    )
    require(
        "DOP_construction_dynamic_v8_initialized" in effects
        and "DOP_construction_migrate_dynamic_v8" in effects,
        "v8 migration and version flag are present",
    )
    require(
        modifiers.count("enable = { always = yes }") == 3,
        "three scoped dynamic modifiers are defined",
    )
    require(
        re.search(
            r"\b(add_manpower|recruitable_population|conscription_factor|"
            r"mobilization_laws_cost_factor)\b",
            effects + "\n" + modifiers,
        )
        is None,
        "manpower slider never modifies recruitable or conscription population",
    )

    forbidden = {
        "pending reward/state": r"\bpending\b",
        "control-gated payout": r"is_owned_and_controlled|on_state_control_changed",
        "forced construction BOP": r"\bset_power_balance\b",
        "military-factory reward": r"\bindustrial_complex\b",
        "old multiframe strip": r"construction_project_previews|noOfFrames\s*=\s*20",
    }
    scoped = "\n".join(
        (effects, reward_effects, events, gfx, gui, scripted_gui, on_actions, modifiers)
    )
    for label, pattern in forbidden.items():
        require(
            not re.search(pattern, scoped, re.IGNORECASE),
            f"no {label} pattern appears in scoped runtime files",
        )

    dispatch = effects.split(
        "# BEGIN GENERATED CONSTRUCTION EVENT DISPATCH", 1
    )[1].split("# END GENERATED CONSTRUCTION EVENT DISPATCH", 1)[0]
    require(
        "country_event" not in dispatch and "_completion_effect" not in dispatch,
        "completion dispatch only marks complete and queues the event",
    )
    require(
        "DOP_construction_reward_claimed^DOP_construction_target_project < 1"
        in reward_effects,
        "reward claim uses once-only array protection",
    )
    validate_gng_app_scopes(reward_effects)
    validate_reward_geography(reward_effects, args.tno_root)
    validate_tno_component_localisation(args.tno_cn_root)

    require(
        "竹人" not in localisation
        and "满意度" not in localisation
        and "岭南开发总署" not in localisation,
        "construction localisation contains no obsolete Chinese terminology",
    )
    require(
        "§E珠人§!" in localisation
        and "§e日侨§!" in localisation
        and "政府支持率" in localisation,
        "construction localisation uses TNO's 珠人/日侨/政府支持率 terminology",
    )
    require(
        all(
            f"{key}:" in localisation
            for key in (
                "DOP_construction_economic_commitments",
                "DOP_construction_economic_commitments_desc",
                "DOP_construction_social_mobilisation",
                "DOP_construction_social_mobilisation_desc",
                "DOP_construction_completed_assets",
                "DOP_construction_completed_assets_desc",
            )
        ),
        "all three construction dynamic modifiers have Chinese names and descriptions",
    )
    project_api_tooltip_lines = "\n".join(
        line
        for line in localisation.splitlines()
        if "DOP_construction_" in line and "_project_tt:" in line
    )
    require(
        project_api_tooltip_lines.count("£GFX_infrastructure ") == 3
        and "£GFX_infrastructure_texticon" not in project_api_tooltip_lines
        and "£GFX_decision_icon_small" not in project_api_tooltip_lines,
        "single-project tooltips use GFX_infrastructure instead of decision/texticon variants",
    )

    for project in projects:
        for key in (
            f"DOP_construction_{project.slug}:",
            f"DOP_construction_{project.slug}_desc:",
            f"DOP_GNG_construction.{project.completion_event_id}.t:",
        ):
            require(key in localisation, f"localisation key exists: {key[:-1]}")
        validate_dds(
            ROOT / f"gfx/interface/bop/DOP_construction_project_{project.id:02d}.dds"
        )

    validate_railways(reward_effects, args.tno_root)
    require(
        "EARLY DEVELOPMENT BUILD 260901F"
        in text(ROOT / "localisation/simp_chinese/DOP_version_l_simp_chinese.yml"),
        "user-facing build version is 260901F",
    )
    print("STATIC ACCEPTANCE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
