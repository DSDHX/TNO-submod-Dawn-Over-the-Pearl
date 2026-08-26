#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import pathlib
import re

PROJECTS = [
    "sky_tower", "rose_garden", "alice_dream_factory", "daya_bay_nuclear_plant",
    "guangdong_shinkansen", "chaoshan_university", "xinfengjiang_reservoir",
    "luoding_granary", "pinglu_canal", "south_china_sea_drilling_platform",
    "wenchang_space_center", "guangxi_industrial_institute",
    "guangxi_expressway_network", "nanyue_folk_memorial_park",
    "lijiang_waterway", "honghe_fan_asia_friendship_pass",
]

def text(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="ignore")

def blocks(path: pathlib.Path, kinds: tuple[str, ...]):
    src = text(path)
    pattern = re.compile(r"(?m)^\s*(?:" + "|".join(map(re.escape, kinds)) + r")\s*=\s*\{")
    pos = 0
    while True:
        match = pattern.search(src, pos)
        if not match:
            break
        index = match.end()
        depth = 1
        while index < len(src) and depth:
            if src[index] == "{":
                depth += 1
            elif src[index] == "}":
                depth -= 1
            index += 1
        yield src[match.start():index]
        pos = index

def first_top_level_id(block: str) -> str | None:
    depth = 0
    for line in block.splitlines():
        if depth == 1:
            match = re.match(r"\s*id\s*=\s*([^\s#}]+)", line)
            if match:
                return match.group(1).strip('"')
        depth += line.count("{") - line.count("}")
    return None

def duplicate_map(entries):
    grouped = collections.defaultdict(list)
    for key, path in entries:
        grouped[key].append(path)
    return {key: paths for key, paths in grouped.items() if len(paths) > 1}

def loc_keys(roots):
    entries = []
    for root in roots:
        if not root or not root.exists():
            continue
        for path in root.rglob("*.yml"):
            for match in re.finditer(r"(?m)^[ \t]*([^#\s][^:]*?):\d*[ \t]+", text(path)):
                entries.append((match.group(1).strip(), path))
    return entries

def registered_gfx(roots):
    names = set()
    for root in roots:
        if not root or not root.exists():
            continue
        for path in root.rglob("*.gfx"):
            names.update(re.findall(r'\bname\s*=\s*"?([A-Za-z0-9_]+)', text(path)))
    return names

def report_duplicates(label, duplicate):
    print(f"{label}={len(duplicate)}")
    for key, paths in sorted(duplicate.items()):
        print(f"  {key}: " + ", ".join(str(p) for p in paths))

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path("."))
    parser.add_argument("--tno", type=pathlib.Path)
    parser.add_argument("--tno-cn", type=pathlib.Path)
    parser.add_argument("--base", type=pathlib.Path)
    args = parser.parse_args()
    root = args.root.resolve()

    focus_entries = []
    for path in (root / "common" / "national_focus").rglob("*.txt"):
        for block in blocks(path, ("shared_focus", "focus")):
            focus_id = first_top_level_id(block)
            if focus_id:
                focus_entries.append((focus_id, path.relative_to(root)))
    focus_dupes = duplicate_map(focus_entries)

    event_entries = []
    for path in (root / "events").rglob("*.txt"):
        for block in blocks(path, ("country_event", "news_event", "unit_leader_event", "state_event")):
            event_id = first_top_level_id(block)
            if event_id:
                event_entries.append((event_id, path.relative_to(root)))
    event_dupes = duplicate_map(event_entries)

    sub_loc_entries = loc_keys([root / "localisation"])
    sub_loc_dupes = duplicate_map((f"{path.relative_to(root / 'localisation').parts[0]}:{key}", path) for key, path in sub_loc_entries)
    all_loc_entries = list(sub_loc_entries)
    if args.tno_cn:
        all_loc_entries.extend(loc_keys([args.tno_cn / "localisation"]))
    if args.tno:
        all_loc_entries.extend(loc_keys([args.tno / "localisation"]))
    known_loc = {key for key, _ in all_loc_entries}
    focus_ids = {key for key, _ in focus_entries}
    missing_focus_loc = sorted(
        key for key in focus_ids
        if key not in known_loc or f"{key}_desc" not in known_loc
    )

    gfx_roots = [root / "interface"]
    if args.tno:
        gfx_roots.append(args.tno / "interface")
    if args.base:
        gfx_roots.append(args.base / "interface")
    gfx_defs = registered_gfx(gfx_roots)
    gfx_refs = set()
    for path in (root / "common" / "national_focus").rglob("*.txt"):
        gfx_refs.update(re.findall(r'\bicon\s*=\s*"?([A-Za-z0-9_]+)', text(path)))
    missing_focus_gfx = sorted(gfx_refs - gfx_defs)
    gui_gfx_refs = set()
    for path in (root / "interface").rglob("*.gui"):
        gui_gfx_refs.update(re.findall(r'\b(?:spriteType|quadTextureSprite)\s*=\s*"?([A-Za-z0-9_]+)', text(path)))
    missing_gui_gfx = sorted(gui_gfx_refs - gfx_defs)

    texture_refs = []
    texture_roots = [root]
    if args.tno:
        texture_roots.append(args.tno)
    if args.base:
        texture_roots.append(args.base)
    for path in (root / "interface").rglob("*.gfx"):
        for ref in re.findall(r'\btextureFile(?:1|2)?\s*=\s*"([^"]+)"', text(path)):
            normalized = pathlib.Path(ref.replace("\\", "/"))
            if not any((candidate / normalized).is_file() for candidate in texture_roots):
                texture_refs.append((ref, path.relative_to(root)))
    texture_refs = sorted(set(texture_refs))

    expected_files = {
        "effects": root / "common" / "scripted_effects" / "DOP_construction_effects.txt",
        "gui_script": root / "common" / "scripted_guis" / "DOP_Construction_GUI.txt",
        "events": root / "events" / "DOP_GNG_construction.txt",
        "localisation": root / "localisation" / "simp_chinese" / "DOP_Construction_l_simp_chinese.yml",
        "layout": root / "interface" / "GUI" / "DOP_construction_interface.gui",
    }
    construction_missing = []
    loaded = {name: text(path) if path.is_file() else "" for name, path in expected_files.items()}
    for index, slug in enumerate(PROJECTS, 1):
        requirements = [
            ("effects", f"DOP_construction_{slug}_total"),
            ("effects", f"DOP_construction_{slug}_tick"),
            ("effects", f"DOP_construction_{slug}_completed"),
            ("effects", f"DOP_GNG_construction.{index}"),
            ("gui_script", f"DOP_construction_select_{index}"),
            ("gui_script", f"DOP_construction_{slug}_percent"),
            ("events", f"id = DOP_GNG_construction.{index}"),
            ("localisation", f"DOP_construction_project_name_{index}:"),
            ("layout", f'name = "construction_project_{index}"'),
            ("layout", f'name = "construction_project_{index}_progress"'),
        ]
        for file_key, needle in requirements:
            if needle not in loaded[file_key]:
                construction_missing.append(f"{slug}: {file_key} lacks {needle}")

    product_cycle_missing = []
    product_cycle_files = {
        "effects": root / "common" / "scripted_effects" / "zz_DOP_GNG_product_cycle_override.txt",
        "event": root / "events" / "DOP_GNG_product_cycle.txt",
        "focus": root / "common" / "national_focus" / "dop_sony-japan_ending4_return1962.txt",
    }
    product_cycle_loaded = {
        name: text(path) if path.is_file() else ""
        for name, path in product_cycle_files.items()
    }
    product_cycle_requirements = [
        ("focus", "set_country_flag = DOP_GNG_open_product_cycle_investment"),
        ("effects", "GNG_product_cycle_event_initializer = {"),
        ("effects", "has_country_flag = DOP_GNG_open_product_cycle_investment"),
        ("effects", "country_event = DOP_GNG_product_cycle.1"),
        ("effects", "GNG_product_cycle_tracker = 13"),
        ("effects", "country_event = GNG_Product_Cycle.3"),
        ("event", "id = DOP_GNG_product_cycle.1"),
        ("event", "title = GNG_Product_Cycle.3.t"),
        ("event", "desc = GNG_Product_Cycle.3.desc"),
        ("event", "picture = GFX_report_event_GNG_generic_engineers_2"),
    ]
    for company, value, offset in [
        ("sony", 1, 8), ("matsushita", 2, 9),
        ("fujitsu", 3, 10), ("hitachi", 4, 11),
    ]:
        product_cycle_requirements.extend([
            ("effects", f"DOP_GNG_start_product_cycle_as_{company} = {{"),
            ("effects", f"set_temp_variable = {{ GNG_product_cycle_company_temp = {value} }}"),
            ("effects", f"add_to_temp_variable = {{ DOP_GNG_product_id_temp = {offset} }}"),
            ("event", f"DOP_GNG_start_product_cycle_as_{company} = yes"),
        ])
    for file_key, needle in product_cycle_requirements:
        if needle not in product_cycle_loaded[file_key]:
            product_cycle_missing.append(f"{file_key} lacks {needle}")
    if "GFX_report_event_GNG_generic_engineers_2" not in gfx_defs:
        product_cycle_missing.append("event picture GFX_report_event_GNG_generic_engineers_2 is not registered")
    for key in [
        "GNG_Product_Cycle.3.t", "GNG_Product_Cycle.3.desc",
        "GNG_Product_Cycle.3.a", "GNG_Product_Cycle.3.b",
        "GNG_Product_Cycle.3.c", "GNG_Product_Cycle.3.d",
    ]:
        if key not in known_loc:
            product_cycle_missing.append(f"localisation lacks {key}")

    print(f"focus_ids={len(focus_entries)} unique={len(focus_ids)}")
    report_duplicates("duplicate_focus_ids", focus_dupes)
    print(f"event_ids={len(event_entries)} unique={len({key for key, _ in event_entries})}")
    report_duplicates("duplicate_event_ids", event_dupes)
    report_duplicates("duplicate_submod_loc_keys", sub_loc_dupes)
    print(f"missing_focus_localisation={len(missing_focus_loc)}")
    for key in missing_focus_loc:
        print(f"  {key}")
    print(f"focus_gfx_refs={len(gfx_refs)} registered_gfx={len(gfx_defs)} missing_focus_gfx={len(missing_focus_gfx)}")
    for key in missing_focus_gfx:
        print(f"  {key}")
    print(f"gui_gfx_refs={len(gui_gfx_refs)} missing_gui_gfx={len(missing_gui_gfx)}")
    for key in missing_gui_gfx:
        print(f"  {key}")
    print(f"missing_texture_files={len(texture_refs)}")
    for ref, path in texture_refs:
        print(f"  {ref}: {path}")
    print(f"construction_projects={len(PROJECTS)} missing_bindings={len(construction_missing)}")
    for issue in construction_missing:
        print(f"  {issue}")
    print(f"product_cycle_missing_bindings={len(product_cycle_missing)}")
    for issue in product_cycle_missing:
        print(f"  {issue}")

    failures = (
        len(focus_dupes) + len(event_dupes) + len(sub_loc_dupes) + len(missing_focus_loc)
        + len(missing_focus_gfx) + len(missing_gui_gfx) + len(texture_refs)
        + len(construction_missing) + len(product_cycle_missing)
    )
    print(f"fatal_findings={failures}")
    return 1 if failures else 0

if __name__ == "__main__":
    raise SystemExit(main())
