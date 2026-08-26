from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EFFECTS_PATH = ROOT / "common/scripted_effects/DOP_construction_effects.txt"
EVENTS_PATH = ROOT / "events/DOP_GNG_construction.txt"
LOC_PATH = ROOT / "localisation/simp_chinese/DOP_Construction_l_simp_chinese.yml"
TOKENS_PATH = ROOT / "common/synchronized_dynamic_tokens/DOP_construction_tokens.txt"
SCRIPTED_LOC_PATH = ROOT / "common/scripted_localisation/DOP_Construction_Scripted_loc.txt"

REGISTRY_BEGIN = "# BEGIN GENERATED CONSTRUCTION REGISTRY"
REGISTRY_END = "# END GENERATED CONSTRUCTION REGISTRY"
LOC_BEGIN = "# BEGIN GENERATED CONSTRUCTION LOCALISATION"
LOC_END = "# END GENERATED CONSTRUCTION LOCALISATION"
TOKENS_BEGIN = "# BEGIN GENERATED CONSTRUCTION TOKENS"
TOKENS_END = "# END GENERATED CONSTRUCTION TOKENS"
EVENT_DISPATCH_BEGIN = "# BEGIN GENERATED CONSTRUCTION EVENT DISPATCH"
EVENT_DISPATCH_END = "# END GENERATED CONSTRUCTION EVENT DISPATCH"
DIRECTORY_BEGIN = "# BEGIN GENERATED CONSTRUCTION DIRECTORY"
DIRECTORY_END = "# END GENERATED CONSTRUCTION DIRECTORY"
DIRECTORY_TOGGLE_BEGIN = "# BEGIN GENERATED CONSTRUCTION DIRECTORY TOGGLES"
DIRECTORY_TOGGLE_END = "# END GENERATED CONSTRUCTION DIRECTORY TOGGLES"
CLEAR_FLAGS_BEGIN = "# BEGIN GENERATED CONSTRUCTION CLEAR FLAGS"
CLEAR_FLAGS_END = "# END GENERATED CONSTRUCTION CLEAR FLAGS"
CLEAR_EXPANSION_BEGIN = "# BEGIN GENERATED CONSTRUCTION CLEAR EXPANSION FLAGS"
CLEAR_EXPANSION_END = "# END GENERATED CONSTRUCTION CLEAR EXPANSION FLAGS"
STATE_DISPATCH_BEGIN = "# BEGIN GENERATED CONSTRUCTION STATE DISPATCH"
STATE_DISPATCH_END = "# END GENERATED CONSTRUCTION STATE DISPATCH"
CLEAR_STATE_BEGIN = "# BEGIN GENERATED CONSTRUCTION CLEAR STATE FLAGS"
CLEAR_STATE_END = "# END GENERATED CONSTRUCTION CLEAR STATE FLAGS"
SELECT_FIRST_BEGIN = "# BEGIN GENERATED CONSTRUCTION SELECT FIRST SHOWN"
SELECT_FIRST_END = "# END GENERATED CONSTRUCTION SELECT FIRST SHOWN"
SCRIPTED_LOC_BEGIN = "# BEGIN GENERATED CONSTRUCTION DIRECTORY LOCALISATION"
SCRIPTED_LOC_END = "# END GENERATED CONSTRUCTION DIRECTORY LOCALISATION"
CALLBACK_END = "# END GENERATED COMPLETION CALLBACKS"
PLACEHOLDER_IMAGE = "GSA_kanton_shenkansen_research"


@dataclass(frozen=True)
class Region:
    id: int
    slug: str
    name: str


@dataclass(frozen=True)
class Project:
    id: int
    slug: str
    region: str
    total: int
    name: str
    desc: str
    image: str = PLACEHOLDER_IMAGE
    event_id: int | None = None

    @property
    def completion_event_id(self) -> int:
        return self.id if self.event_id is None else self.event_id


# IDs are save-game data. Append new IDs; never reuse or reorder released IDs.
REGIONS = (
    Region(1, "prd", "珠三角"),
    Region(2, "chaoshan", "潮汕"),
    Region(3, "northern_guangdong", "粤北"),
    Region(4, "western_guangdong", "粤西"),
    Region(5, "jiaoyang", "交洋"),
    Region(6, "yongning", "邕宁"),
    Region(7, "cangwu", "苍梧"),
    Region(8, "guiliu", "桂柳"),
    Region(9, "tiannan", "田南"),
)

PROJECTS = (
    Project(1, "sky_tower", "prd", 150000, "白鹅新区晴空塔", "广佛同城之后的新核心区——这个世界的珠江新城与广州塔。"),
    Project(2, "rose_garden", "prd", 100000, "玫瑰园计划", "香港超级城建计划，包含新机场、海底隧道与填海工程。"),
    Project(3, "alice_dream_factory", "prd", 30000, "粤海爱丽丝梦工厂", "一座落在澳门的迪士尼式主题乐园。"),
    Project(4, "daya_bay_nuclear_plant", "prd", 45000, "大亚湾核电站", "在大亚湾建设大型核能发电设施。"),
    Project(5, "guangdong_shinkansen", "prd", 90000, "广东新干线", "澳湛高铁与港汕高铁组成的高速铁路骨架。"),
    Project(6, "chaoshan_university", "chaoshan", 8000, "潮汕大学", "服务潮汕地区的综合性大学。"),
    Project(7, "xinfengjiang_reservoir", "northern_guangdong", 20000, "新丰江水库", "新丰江流域的大型水利与供电工程。"),
    Project(8, "luoding_granary", "western_guangdong", 4000, "罗定粮仓", "推动罗定盆地农业集中化与机械化。"),
    Project(9, "pinglu_canal", "jiaoyang", 100000, "平陆运河", "贯通内河与北部湾航运体系的运河工程。"),
    Project(10, "south_china_sea_drilling_platform", "jiaoyang", 4000, "南海深水钻井平台", "面向南海深水油气资源的海上开采平台。"),
    Project(11, "wenchang_space_center", "jiaoyang", 12000, "文昌卫星发射中心", "面向未来航天计划的卫星发射场。"),
    Project(12, "guangxi_industrial_institute", "yongning", 50000, "重整广西实业院", "将桂柳一带的工业资源与机构逐步迁往南宁。"),
    Project(13, "guangxi_expressway_network", "yongning", 80000, "广西高速公路网新规划", "连接桂柳、南宁、钦廉与肇庆方向的高速公路网。"),
    Project(14, "nanyue_folk_memorial_park", "cangwu", 1000, "南粤民俗纪念公园", "纪念南粤民俗与乡土文化，以安抚本土认同。"),
    Project(15, "lijiang_waterway", "guiliu", 1000, "漓江航道开发工程", "加强桂柳同沿岸地区的交通、沟通与商贸。"),
    Project(16, "honghe_fan_asia_friendship_pass", "tiannan", 1000, "红河泛亚友谊关", "加强友谊关沿红河—湄公河方向与印支半岛的交通和商贸。"),
)


def read_text(path: Path) -> tuple[str, str, bool]:
    has_bom = path.read_bytes().startswith(b"\xef\xbb\xbf")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        text = handle.read()
    newline = "\r\n" if "\r\n" in text else "\n"
    return text, newline, has_bom


def write_text(path: Path, text: str, has_bom: bool) -> None:
    encoding = "utf-8-sig" if has_bom else "utf-8"
    with path.open("w", encoding=encoding, newline="") as handle:
        handle.write(text)


def validate_data() -> None:
    region_ids = [region.id for region in REGIONS]
    project_ids = [project.id for project in PROJECTS]
    if region_ids != list(range(1, len(REGIONS) + 1)):
        raise ValueError("Region IDs must be consecutive and start at 1.")
    if project_ids != list(range(1, len(PROJECTS) + 1)):
        raise ValueError("Project IDs must be consecutive and start at 1.")
    if len({region.slug for region in REGIONS}) != len(REGIONS):
        raise ValueError("Region slugs must be unique.")
    if len({project.slug for project in PROJECTS}) != len(PROJECTS):
        raise ValueError("Project slugs must be unique.")
    region_slugs = {region.slug for region in REGIONS}
    unknown = sorted({project.region for project in PROJECTS} - region_slugs)
    if unknown:
        raise ValueError(f"Unknown project regions: {', '.join(unknown)}")
    event_ids = [project.completion_event_id for project in PROJECTS]
    if len(set(event_ids)) != len(event_ids):
        raise ValueError("Completion event IDs must be unique.")
    if any(project.total <= 0 for project in PROJECTS):
        raise ValueError("Project totals must be positive.")


def replace_marked(text: str, begin: str, end: str, body: list[str], newline: str) -> str:
    begin_at = text.index(begin)
    end_at = text.index(end, begin_at)
    begin_line = text.rfind("\n", 0, begin_at) + 1
    end_line = text.rfind("\n", 0, end_at) + 1
    end_line_end = text.find("\n", end_at)
    if end_line_end == -1:
        end_line_end = len(text)
    else:
        end_line_end += 1
    indent = text[begin_line:begin_at]
    body_text = newline.join((indent + line) if line else "" for line in body)
    replacement = indent + begin + newline + body_text + newline + indent + end
    if end_line_end <= len(text) and text[end_line_end - len(newline):end_line_end] == newline:
        replacement += newline
    return text[:begin_line] + replacement + text[end_line_end:]


def render_registry() -> list[str]:
    lines: list[str] = []
    region_id = {region.slug: region.id for region in REGIONS}
    for region in REGIONS:
        lines.append(f"add_to_array = {{ DOP_construction_region_ids = {region.id} }}")
    for region in REGIONS:
        lines.append(
            f"add_to_array = {{ DOP_construction_region_tokens = token:DOP_construction_region_{region.slug} }}"
        )
    lines.append("")
    for project in PROJECTS:
        lines.extend(
            [
                f"set_temp_variable = {{ DOP_construction_register_id = {project.id} }}",
                f"set_temp_variable = {{ DOP_construction_register_token = token:DOP_construction_{project.slug} }}",
                f"set_temp_variable = {{ DOP_construction_register_desc_token = token:DOP_construction_{project.slug}_desc }}",
                f"set_temp_variable = {{ DOP_construction_register_region = {region_id[project.region]} }}",
                f"set_temp_variable = {{ DOP_construction_register_image = token:{project.image} }}",
                f"set_temp_variable = {{ DOP_construction_register_event = {project.completion_event_id} }}",
                f"set_temp_variable = {{ DOP_construction_register_total = {project.total} }}",
                "DOP_construction_register_project = yes",
                "",
            ]
        )
    if lines and not lines[-1]:
        lines.pop()
    return lines


def loc_value(value: str) -> str:
    return value.replace('"', chr(92) + '"')


def render_tokens() -> list[str]:
    lines = ["DOP_construction_no_region", "DOP_construction_no_project", "DOP_construction_no_project_desc", ""]
    lines.extend(f"DOP_construction_region_{region.slug}" for region in REGIONS)
    lines.append("")
    for project in PROJECTS:
        lines.append(f"DOP_construction_{project.slug}")
        lines.append(f"DOP_construction_{project.slug}_desc")
    lines.append("")
    lines.extend(sorted({project.image for project in PROJECTS}))
    return lines


def render_event_dispatch() -> list[str]:
    lines: list[str] = []
    for project in PROJECTS:
        lines.extend(
            [
                "if = {",
                "\tlimit = { check_variable = { "
                f"DOP_construction_completed_event_id = {project.completion_event_id} }} }}",
                f"\tset_country_flag = DOP_construction_{project.slug}_completed",
                f"\tDOP_construction_{project.slug}_completion_effect = yes",
                f"\tcountry_event = {{ id = DOP_GNG_construction.{project.completion_event_id} days = 1 }}",
                "}",
            ]
        )
    return lines


def render_directory() -> list[str]:
    region_id = {region.slug: region.id for region in REGIONS}
    lines: list[str] = []
    for region in REGIONS:
        region_projects = [
            project for project in PROJECTS if region_id[project.region] == region.id
        ]
        lines.extend(
            [
                "if = {",
                "\tlimit = {",
                "\t\tOR = {",
            ]
        )
        for project in region_projects:
            lines.append(
                f"\t\t\tcheck_variable = {{ DOP_construction_shown^{project.id} > 0 }}"
            )
        lines.extend(
            [
                "\t\t}",
                "\t}",
                f"\tadd_to_array = {{ DOP_construction_directory_items = {100 + region.id} }}",
                "\tif = {",
                f"\t\tlimit = {{ has_country_flag = DOP_construction_region_{region.id}_expanded }}",
            ]
        )
        for project in region_projects:
            lines.extend(
                [
                    "\t\tif = {",
                    f"\t\t\tlimit = {{ check_variable = {{ DOP_construction_shown^{project.id} > 0 }} }}",
                    f"\t\t\tadd_to_array = {{ DOP_construction_directory_items = {project.id} }}",
                    "\t\t}",
                ]
            )
        lines.extend(["\t}", "}"])
    return lines


def render_directory_toggles() -> list[str]:
    region_id = {region.slug: region.id for region in REGIONS}
    lines: list[str] = []
    for region in REGIONS:
        region_projects = [
            project for project in PROJECTS if region_id[project.region] == region.id
        ]
        lines.extend(
            [
                "if = {",
                "\tlimit = { check_variable = { "
                f"DOP_construction_directory_item = {100 + region.id} }} }}",
                f"\tset_variable = {{ DOP_construction_selected_region = {region.id} }}",
            ]
        )
        for index, project in enumerate(region_projects):
            branch = "if" if index == 0 else "else_if"
            lines.extend(
                [
                    f"\t{branch} = {{",
                    f"\t\tlimit = {{ check_variable = {{ DOP_construction_shown^{project.id} > 0 }} }}",
                    f"\t\tset_variable = {{ DOP_construction_selected = {project.id} }}",
                    "\t}",
                ]
            )
        lines.extend(
            [
                "\tif = {",
                f"\t\tlimit = {{ has_country_flag = DOP_construction_region_{region.id}_expanded }}",
                f"\t\tclr_country_flag = DOP_construction_region_{region.id}_expanded",
                "\t}",
                f"\telse = {{ set_country_flag = DOP_construction_region_{region.id}_expanded }}",
                "}",
            ]
        )
    return lines


def render_select_first_shown() -> list[str]:
    region_id = {region.slug: region.id for region in REGIONS}
    lines: list[str] = []
    for index, project in enumerate(PROJECTS):
        branch = "if" if index == 0 else "else_if"
        lines.extend(
            [
                f"{branch} = {{",
                f"\tlimit = {{ check_variable = {{ DOP_construction_shown^{project.id} > 0 }} }}",
                f"\tset_variable = {{ DOP_construction_selected = {project.id} }}",
                f"\tset_variable = {{ DOP_construction_selected_region = {region_id[project.region]} }}",
                "}",
            ]
        )
    lines.extend(
        [
            "else = {",
            "\tset_variable = { DOP_construction_selected = 0 }",
            "\tset_variable = { DOP_construction_selected_region = 0 }",
            "}",
        ]
    )
    return lines


def render_state_dispatch() -> list[str]:
    lines = ["DOP_construction_mark_project_shown = {"]
    for project in PROJECTS:
        lines.extend(
            [
                "\tif = {",
                f"\t\tlimit = {{ check_variable = {{ DOP_construction_target_project = {project.id} }} }}",
                f"\t\tset_variable = {{ DOP_construction_shown^{project.id} = 1 }}",
                f"\t\tset_country_flag = DOP_construction_{project.slug}_shown",
                "\t}",
            ]
        )
    lines.extend(["}", "", "DOP_construction_mark_project_started = {"])
    for project in PROJECTS:
        lines.extend(
            [
                "\tif = {",
                f"\t\tlimit = {{ check_variable = {{ DOP_construction_target_project = {project.id} }} }}",
                f"\t\tset_variable = {{ DOP_construction_started^{project.id} = 1 }}",
                f"\t\tset_country_flag = DOP_construction_{project.slug}_started",
                "\t}",
            ]
        )
    lines.append("}")
    return lines


def render_clear_flags() -> list[str]:
    return [
        f"clr_country_flag = DOP_construction_{project.slug}_completed"
        for project in PROJECTS
    ]


def render_clear_expansion_flags() -> list[str]:
    return [
        f"clr_country_flag = DOP_construction_region_{region.id}_expanded"
        for region in REGIONS
    ]


def render_clear_state_flags() -> list[str]:
    lines: list[str] = []
    for project in PROJECTS:
        lines.append(f"clr_country_flag = DOP_construction_{project.slug}_shown")
        lines.append(f"clr_country_flag = DOP_construction_{project.slug}_started")
    return lines


def render_scripted_localisation() -> list[str]:
    lines = [
        "defined_text = {",
        "\tname = DOP_construction_GetDirectoryEntryContainer",
        "\ttext = {",
        "\t\ttrigger = { check_variable = { DOP_construction_directory_item > 100 } }",
        '\t\tlocalization_key = "DOP_construction_region_entry"',
        "\t}",
        '\ttext = { localization_key = "DOP_construction_project_entry" }',
        "}",
        "",
        "defined_text = {",
        "\tname = DOP_construction_GetDirectoryRegionName",
    ]
    for region in REGIONS:
        lines.extend(
            [
                "\ttext = {",
                "\t\ttrigger = { check_variable = { "
                f"DOP_construction_directory_item = {100 + region.id} }} }}",
                f"\t\tlocalization_key = DOP_construction_region_{region.slug}",
                "\t}",
            ]
        )
    lines.extend(["}", "", "defined_text = {", "\tname = DOP_construction_GetSelectedRegionName"])
    for region in REGIONS:
        lines.extend(
            [
                "\ttext = {",
                "\t\ttrigger = { check_variable = { "
                f"DOP_construction_selected_region = {region.id} }} }}",
                f"\t\tlocalization_key = DOP_construction_region_{region.slug}",
                "\t}",
            ]
        )
    lines.extend(
        [
            "\ttext = { localization_key = DOP_construction_no_region }",
            "}",
            "",
            "defined_text = {",
            "\tname = DOP_construction_GetTargetProjectName",
        ]
    )
    for project in PROJECTS:
        lines.extend(
            [
                "\ttext = {",
                f"\t\ttrigger = {{ check_variable = {{ DOP_construction_target_project = {project.id} }} }}",
                f"\t\tlocalization_key = DOP_construction_{project.slug}",
                "\t}",
            ]
        )
    lines.extend(
        [
            "\ttext = { localization_key = DOP_construction_no_project }",
            "}",
            "",
            "defined_text = {",
            "\tname = DOP_construction_GetDirectoryRegionMarker",
        ]
    )
    for region in REGIONS:
        lines.extend(
            [
                "\ttext = {",
                "\t\ttrigger = {",
                "\t\t\tcheck_variable = { "
                f"DOP_construction_directory_item = {100 + region.id} }}",
                f"\t\t\thas_country_flag = DOP_construction_region_{region.id}_expanded",
                "\t\t}",
                "\t\tlocalization_key = DOP_construction_directory_marker_open",
                "\t}",
            ]
        )
    lines.extend(
        [
            "\ttext = { localization_key = DOP_construction_directory_marker_closed }",
            "}",
        ]
    )
    return lines


def render_localisation() -> list[str]:
    lines = [
        "# Dynamic directory and registry localisation.",
        'DOP_construction_no_region:0 "暂无地区"',
        'DOP_construction_no_project:0 "暂无建设项目"',
        'DOP_construction_no_project_desc:0 "建设项目尚未添加到岭南开发总署。"',
        'DOP_construction_region_directory_title:0 "建设目录"',
        'DOP_construction_project_directory_title:0 "设施项目"',
        'DOP_construction_region_entry_name:0 "§B[DOP_construction_GetDirectoryRegionMarker] [DOP_construction_GetDirectoryRegionName]§!"',
        'DOP_construction_region_entry_tt:0 "展开或收起该地区；同时切换到该地区的第一个已显示建设项目。"',
        'DOP_construction_project_entry_name:0 "[?DOP_construction_project_tokens^DOP_construction_directory_item.GetTokenLocalizedKey]"',
        'DOP_construction_project_entry_tt:0 "[DOP_construction_GetEntryDesc]"',
        'DOP_construction_directory_marker_open:0 "−"',
        'DOP_construction_directory_marker_closed:0 "+"',
        'DOP_construction_show_project_tt:0 "§Y[DOP_construction_GetTargetProjectName]§!将被添加到£decision_icon_small §W岭南开发总署§! GUI中。"',
        'DOP_construction_start_project_tt:0 "§Y[DOP_construction_GetTargetProjectName]§!将开始建设。"',
        'DOP_construction_show_and_start_project_tt:0 "§Y[DOP_construction_GetTargetProjectName]§!将被添加到£decision_icon_small §W岭南开发总署§! GUI中并开始建设。"',
        "",
    ]
    for region in REGIONS:
        lines.append(f'DOP_construction_region_{region.slug}:0 "{loc_value(region.name)}"')
    lines.append("")
    for project in PROJECTS:
        lines.append(f'DOP_construction_{project.slug}:0 "{loc_value(project.name)}"')
        lines.append(f'DOP_construction_{project.slug}_desc:0 "{loc_value(project.desc)}"')
    return lines


def ensure_callbacks(text: str, newline: str) -> str:
    missing = []
    for project in PROJECTS:
        name = f"DOP_construction_{project.slug}_completion_effect"
        if not re.search(rf"(?m)^\s*{re.escape(name)}\s*=", text):
            missing.append(f"{name} = {{ }}")
    if not missing:
        return text
    marker_at = text.index(CALLBACK_END)
    line_at = text.rfind("\n", 0, marker_at) + 1
    return text[:line_at] + newline.join(missing) + newline + text[line_at:]


def ensure_events(text: str, newline: str) -> str:
    existing = {
        int(match)
        for match in re.findall(r"(?m)^\s*id\s*=\s*DOP_GNG_construction\.(\d+)\s*$", text)
    }
    blocks = []
    for project in PROJECTS:
        event_id = project.completion_event_id
        if event_id in existing:
            continue
        blocks.append(
            newline.join(
                [
                    "country_event = {",
                    f"\tid = DOP_GNG_construction.{event_id}",
                    "\thidden = yes",
                    "\tis_triggered_only = yes",
                    "\timmediate = { }",
                    "}",
                ]
            )
        )
    if not blocks:
        return text
    return text.rstrip("\r\n") + newline * 2 + (newline * 2).join(blocks) + newline


def build_outputs() -> dict[Path, tuple[str, bool]]:
    outputs: dict[Path, tuple[str, bool]] = {}

    effects, newline, bom = read_text(EFFECTS_PATH)
    effects = replace_marked(effects, REGISTRY_BEGIN, REGISTRY_END, render_registry(), newline)
    effects = replace_marked(
        effects,
        EVENT_DISPATCH_BEGIN,
        EVENT_DISPATCH_END,
        render_event_dispatch(),
        newline,
    )
    effects = replace_marked(
        effects,
        DIRECTORY_BEGIN,
        DIRECTORY_END,
        render_directory(),
        newline,
    )
    effects = replace_marked(
        effects,
        DIRECTORY_TOGGLE_BEGIN,
        DIRECTORY_TOGGLE_END,
        render_directory_toggles(),
        newline,
    )
    effects = replace_marked(
        effects,
        CLEAR_FLAGS_BEGIN,
        CLEAR_FLAGS_END,
        render_clear_flags(),
        newline,
    )
    effects = replace_marked(
        effects,
        CLEAR_EXPANSION_BEGIN,
        CLEAR_EXPANSION_END,
        render_clear_expansion_flags(),
        newline,
    )
    effects = replace_marked(
        effects,
        STATE_DISPATCH_BEGIN,
        STATE_DISPATCH_END,
        render_state_dispatch(),
        newline,
    )
    effects = replace_marked(
        effects,
        CLEAR_STATE_BEGIN,
        CLEAR_STATE_END,
        render_clear_state_flags(),
        newline,
    )
    effects = replace_marked(
        effects,
        SELECT_FIRST_BEGIN,
        SELECT_FIRST_END,
        render_select_first_shown(),
        newline,
    )
    effects = ensure_callbacks(effects, newline)
    outputs[EFFECTS_PATH] = (effects, bom)

    localisation, newline, bom = read_text(LOC_PATH)
    localisation = replace_marked(
        localisation, LOC_BEGIN, LOC_END, render_localisation(), newline
    )
    outputs[LOC_PATH] = (localisation, bom)

    events, newline, bom = read_text(EVENTS_PATH)
    outputs[EVENTS_PATH] = (ensure_events(events, newline), bom)

    tokens, newline, bom = read_text(TOKENS_PATH)
    tokens = replace_marked(tokens, TOKENS_BEGIN, TOKENS_END, render_tokens(), newline)
    outputs[TOKENS_PATH] = (tokens, bom)

    scripted_loc, newline, bom = read_text(SCRIPTED_LOC_PATH)
    scripted_loc = replace_marked(
        scripted_loc,
        SCRIPTED_LOC_BEGIN,
        SCRIPTED_LOC_END,
        render_scripted_localisation(),
        newline,
    )
    outputs[SCRIPTED_LOC_PATH] = (scripted_loc, bom)
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Update the dynamic DOP construction registry and add missing stubs."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report generated drift without writing files.",
    )
    args = parser.parse_args()

    validate_data()
    outputs = build_outputs()
    changed = []
    for path, (new_text, has_bom) in outputs.items():
        old_text, _, _ = read_text(path)
        if old_text == new_text:
            continue
        changed.append(path.relative_to(ROOT))
        if not args.check:
            write_text(path, new_text, has_bom)

    if changed:
        action = "would update" if args.check else "updated"
        print(f"{action}: " + ", ".join(str(path) for path in changed))
        return 1 if args.check else 0
    print("construction registry is up to date")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
