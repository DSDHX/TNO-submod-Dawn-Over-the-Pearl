#!/usr/bin/env python3
"""Verify focus-owned SCW unlocks are exactly the 24 repeatable decisions."""

import re
from pathlib import Path

from rebalance_dop_unlocks import (
    DECISION_RE,
    FILES,
    FOCUS_DECISIONS,
    START_DECISIONS,
    effect_block,
)
from restore_dop_focus_layout import extract_field, focus_blocks, matching_brace


ROOT = Path(__file__).resolve().parents[1]
decision_source = (ROOT / "common" / "decisions" / "DOP_SCW_decisions.txt").read_text(
    encoding="utf-8-sig"
)
repeatable: set[str] = set()
annual: set[str] = set()
for match in re.finditer(r"(?m)^    (DOP_SCW_[A-Za-z0-9_]+) = \{", decision_source):
    opening = decision_source.find("{", match.start(), match.end())
    closing = matching_brace(decision_source, opening)
    block = decision_source[match.start() : closing + 1]
    if "days_remove = 30" in block:
        repeatable.add(match.group(1))
    elif "days_remove = 365" in block:
        annual.add(match.group(1))

actual_by_focus: dict[str, tuple[str, ...]] = {}
for relative in FILES:
    source = (ROOT / relative).read_text(encoding="utf-8-sig")
    for focus in focus_blocks(source):
        reward = extract_field(focus.text, "completion_reward") or ""
        calls = tuple(DECISION_RE.findall(reward))
        if calls:
            actual_by_focus[focus.focus_id] = calls

flow = (ROOT / "common" / "scripted_effects" / "DOP_GNG_flow_effects.txt").read_text(
    encoding="utf-8-sig"
)
_start, _end, wrapper = effect_block(flow, "DOP_GNG_unlock_scw_stage")
startup = tuple(DECISION_RE.findall(wrapper))

if actual_by_focus != FOCUS_DECISIONS:
    raise SystemExit("focus-owned decision mapping differs from curated mapping")
if startup != next(iter(START_DECISIONS.values())):
    raise SystemExit("startup decision mapping differs from curated mapping")
assigned = set(startup) | {decision for values in actual_by_focus.values() for decision in values}
if assigned != repeatable:
    raise SystemExit(f"assigned decisions are not exactly repeatables: {sorted(assigned ^ repeatable)}")
if len(repeatable) != 24 or len(annual) != 24:
    raise SystemExit(f"expected 24 repeatable / 24 annual, got {len(repeatable)} / {len(annual)}")
if max([len(startup), *(len(values) for values in actual_by_focus.values())]) > 4:
    raise SystemExit("a focus unlocks more than four decisions")

print("SCW focus distribution: 24 repeatables assigned, 24 annual milestones deferred, max 4 per focus")
