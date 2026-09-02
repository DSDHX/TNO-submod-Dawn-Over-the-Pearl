#!/usr/bin/env python3
"""Static acceptance for the numbered DOP flow debug decisions."""

from __future__ import annotations

import re
from pathlib import Path

from restore_dop_focus_layout import matching_brace


ROOT = Path(__file__).resolve().parents[1]
DECISIONS = ROOT / "common" / "decisions" / "DOP_GNG_flow_debug_decisions.txt"
LOCALISATION = ROOT / "localisation" / "simp_chinese" / "DOP_GNG_flow_debug_l_simp_chinese.yml"

EXPECTED = {
    "DOP_GNG_debug_flow_01_opening": "DOP_GNG_begin_post_tno_content = yes",
    "DOP_GNG_debug_flow_02a_yunnan_prewar": "DOP_YUN_prepare_southwest_war = yes",
    "DOP_GNG_debug_flow_02_southwest_crisis": "id = DOP_GNG_flow.1",
    "DOP_GNG_debug_flow_03_enter_war": "id = DOP_GNG_flow.2",
    "DOP_GNG_debug_flow_04_maoming_countdown": "DOP_GNG_maoming_survival_days = 14",
    "DOP_GNG_debug_flow_05_japanese_reinforcements": "DOP_GNG_spawn_japanese_reinforcements = yes",
    "DOP_GNG_debug_flow_06_postwar_settlement": "id = DOP_GNG_flow.3",
    "DOP_GNG_debug_flow_07_restore_legco": "DOP_GNG_restore_legco = yes",
    "DOP_GNG_debug_flow_08_restore_map": "DOP_GNG_restore_map_and_extra_regions = yes",
    "DOP_GNG_debug_flow_09_unlock_construction": "DOP_GNG_unlock_construction_stage = yes",
    "DOP_GNG_debug_flow_10_restore_product_cycle": "DOP_GNG_restore_product_cycle = yes",
    "DOP_GNG_debug_flow_11_unlock_scw": "DOP_GNG_unlock_scw_stage = yes",
    "DOP_GNG_debug_flow_12_unlock_gsa": "DOP_GNG_unlock_gsa_stage = yes",
    "DOP_GNG_debug_flow_13_restore_economy_compare": "DOP_GNG_restore_economy_compare = yes",
    "DOP_GNG_debug_flow_14_enter_core": "DOP_GNG_enter_core_stage = yes",
    "DOP_GNG_debug_flow_15_lee_ending": "load_focus_tree = dop_sonyjapan_ending1_lee_tree",
    "DOP_GNG_debug_flow_16_ibuka_ending": "load_focus_tree = dop_sonyjapan_ending2_ibuka_tree",
    "DOP_GNG_debug_flow_17_finance_ending": "load_focus_tree = dop_sonyjapan_ending3_hitachi_tree",
}


def decision_blocks(source: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for match in re.finditer(r"(?m)^\t(DOP_GNG_debug_flow_[A-Za-z0-9_]+) = \{", source):
        opening = source.find("{", match.start(), match.end())
        closing = matching_brace(source, opening)
        result[match.group(1)] = source[match.start() : closing + 1]
    return result


source = DECISIONS.read_text(encoding="utf-8-sig")
blocks = decision_blocks(source)
if blocks.keys() != EXPECTED.keys():
    raise SystemExit(
        f"debug decision ID mismatch: missing={sorted(EXPECTED.keys() - blocks.keys())} extra={sorted(blocks.keys() - EXPECTED.keys())}"
    )

for decision_id, required in EXPECTED.items():
    block = blocks[decision_id]
    for common in (
        "allowed = { original_tag = GNG }",
        "has_country_flag = GNG_show_debug_decisions",
        "is_debug = yes",
        "cost = 0",
        "ai_will_do = { factor = 0 }",
        "complete_effect = {",
        required,
    ):
        if common not in block:
            raise SystemExit(f"{decision_id}: missing {common}")

if "guang_dong_theater" in source or "DOP_theater_" in source:
    raise SystemExit("flow debug decisions must not touch the excluded Guangdong theatre")

loc_data = LOCALISATION.read_bytes()
if not loc_data.startswith(b"\xef\xbb\xbf"):
    raise SystemExit("flow debug localisation is missing UTF-8 BOM")
loc_source = loc_data.decode("utf-8-sig")
for decision_id in EXPECTED:
    if re.search(rf"(?m)^ {re.escape(decision_id)}:0 \"", loc_source) is None:
        raise SystemExit(f"missing localisation title: {decision_id}")
    if re.search(rf"(?m)^ {re.escape(decision_id)}_desc:0 \"", loc_source) is None:
        raise SystemExit(f"missing localisation description: {decision_id}")

flow_events = (ROOT / "events" / "DOP_GNG_flow.txt").read_text(encoding="utf-8-sig")
for event_id in ("DOP_GNG_flow.1", "DOP_GNG_flow.2", "DOP_GNG_flow.3"):
    if f"id = {event_id}" not in flow_events:
        raise SystemExit(f"undefined flow event used by debug decision: {event_id}")

print("DOP flow debug decisions: 18 nodes including 02A YUN prewar setup, debug-only visibility, localisation and production wiring PASS")
