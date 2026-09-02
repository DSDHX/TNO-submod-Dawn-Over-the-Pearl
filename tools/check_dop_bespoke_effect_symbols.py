#!/usr/bin/env python3
"""Verify every scripted helper used by bespoke focus effects is defined."""

from __future__ import annotations

import re
from pathlib import Path

from dop_focus_effect_design import DESIGN_ROWS
from dop_focus_effect_design_core import CORE_DESIGN_ROWS
from dop_focus_effect_design_endings import ENDING_DESIGN_ROWS


ROOT = Path(__file__).resolve().parents[1]
TNO = Path(r"D:\Steam\steamapps\workshop\content\394360\2438003901")


def collect_definitions(base: Path) -> set[str]:
    result: set[str] = set()
    path = base / "common" / "scripted_effects"
    for file in path.glob("*.txt"):
        source = file.read_text(encoding="utf-8-sig", errors="replace")
        result.update(re.findall(r"(?m)^[ \t]*([A-Za-z0-9_]+)[ \t]*=[ \t]*\{", source))
    return result


definitions = collect_definitions(TNO) | collect_definitions(ROOT)
calls: set[str] = set()
for _focus_id, item in DESIGN_ROWS + CORE_DESIGN_ROWS + ENDING_DESIGN_ROWS:
    for snippet in item.effects:
        calls.update(re.findall(r"(?m)^([A-Za-z0-9_]+)[ \t]*=[ \t]*yes$", snippet))

missing = sorted(calls - definitions)
if missing:
    raise SystemExit(f"undefined bespoke scripted-effect helpers: {missing}")

building_types = set()
for _focus_id, item in DESIGN_ROWS + CORE_DESIGN_ROWS + ENDING_DESIGN_ROWS:
    for snippet in item.effects:
        building_types.update(re.findall(r"(?m)^[ \t]*type[ \t]*=[ \t]*([A-Za-z0-9_]+)$", snippet))
building_sources = "\n".join(
    file.read_text(encoding="utf-8-sig", errors="replace")
    for base in (TNO, ROOT)
    for file in (base / "common" / "buildings").glob("*.txt")
)
undefined_buildings = sorted(
    name
    for name in building_types
    if re.search(rf"(?m)^[ \t]*{re.escape(name)}[ \t]*=[ \t]*\{{", building_sources) is None
)
if undefined_buildings:
    raise SystemExit(f"undefined bespoke building types: {undefined_buildings}")

print(f"bespoke helper definitions verified={len(calls)}")
print(f"bespoke building types verified={len(building_types)}")
