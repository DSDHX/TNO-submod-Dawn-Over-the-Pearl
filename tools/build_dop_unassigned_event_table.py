#!/usr/bin/env python3
"""Generate the required named table for events not attached to target focuses."""

from __future__ import annotations

import argparse
import re
from collections import Counter, defaultdict
from pathlib import Path

from audit_dop_events import LOC_RE, inventory


TNO_CN = Path(r"D:\Steam\steamapps\workshop\content\394360\2243912940")


def merged_localisation(root: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    roots = [TNO_CN / "localisation" / "simp_chinese", root / "localisation" / "simp_chinese"]
    for loc_root in roots:
        if not loc_root.is_dir():
            continue
        for path in sorted(loc_root.rglob("*.yml")):
            for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
                match = LOC_RE.match(line)
                if match:
                    values[match.group(1)] = match.group(2)
    return values


def numeric_suffix(event_id: str) -> int | None:
    match = re.search(r"\.(\d+)$", event_id)
    return int(match.group(1)) if match else None


def classify(row: dict[str, object]) -> tuple[str, str]:
    file = str(row["file"])
    event_id = str(row["id"])
    refs = [str(value) for value in row["reference_files"]]
    number = numeric_suffix(event_id)

    if file == "events/DOP_GNG_construction.txt":
        return "机制回调", "由对应建设项目完成回调触发，不应重复挂入国策"
    if file == "events/DOP_GNG_econ_compare.txt":
        return "机制回调", "经济对比机制的内部刷新事件"
    if file == "events/DOP_GNG_product_cycle.txt":
        return "机制回调", "产品周期机制事件，按周期状态触发"
    if file == "events/DOP_GNG_flow.txt":
        return "战争流程", "西南战争阶段事件，已由选择国策、on_action 或事件链触发"
    if file == "events/GNG_bop_event.txt":
        return "机制回调", "BoP/决议页内部事件"
    if file == "events/GNG_ending_event.txt":
        return "冻结阶段", "属于结局或人质危机过渡，当前阶段明确不实施"
    if file == "events/TNO_Yunnan.txt":
        return "云南战争系统", "云南/西南战争既有系统事件；由触发、决议或事件链管理，不属于广东国策奖励"
    if file == "events/DOP_GNG_focus_stubs.txt":
        if event_id == "DOP_GNG_focus_stub.12":
            return "冻结内容", "对应明确排除的广东大剧院国策"
        return "无可判定内容", "占位事件没有题名和正文，无法判定唯一国策归属"
    if file == "events/DOP_GNG_zip.txt":
        if number is not None and 1 <= number <= 4:
            return "待作者整合", "战后领土外交备选链，与当前确定性战后结算并存，不能直接叠加"
        if number is not None and 5 <= number <= 10:
            return "冻结法案", "民族条例/主体民族法案链属于明确排除的法案段"
        if number is not None and 11 <= number <= 22:
            return "战争流程备选", "另一套西南战争叙事链，与现行战争生命周期重复"
        if number is not None and 23 <= number <= 38:
            return "冻结阶段", "人质危机及结局过渡剧情，当前阶段明确不实施"
        return "战争流程备选", "战云/西南战争备选叙事，不能与现行触发重复挂载"
    if file == "events/DOP_GNG_event.txt":
        if any("ending4_return1962" in ref for ref in refs):
            return "已有外部归属", "已由未授权修改的“重返1962”结局树调用，不重复挂载"
        if any("ending5_second_riot" in ref for ref in refs):
            return "已有外部归属", "已由未授权修改的“第二次暴乱”结局树调用，不重复挂载"
        title = str(row.get("title", ""))
        if any(token in title for token in ("法案", "条例")):
            return "冻结法案", "题名明确属于法案通过/失败或条例实施事件"
        if refs:
            return "已有非国策链", "已有事件、决议或其他系统调用；没有重复挂入国策"
        if number is not None and number in {16, 17, 18, 19, 20, 132, 133, 174, 186, 188, 193, 200, 205, 206, 207, 208}:
            return "冻结阶段", "内容涉及路线/政权/结局过渡，当前阶段不能安全挂载"
        return "待作者指定", "题名与正文不足以唯一确定一个国策，未强行匹配"
    return "待作者指定", "未找到唯一且安全的国策归属"


def display_title(row: dict[str, object], loc: dict[str, str]) -> str:
    event_id = str(row["id"])
    title = str(row.get("title", ""))
    if not title:
        title_key = str(row.get("title_key", ""))
        title = loc.get(title_key, loc.get(f"{event_id}.t", ""))
    title = title.replace("|", "\\|")
    return title or "（无题名）"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    loc = merged_localisation(root)
    rows = [row for row in inventory(root) if not row["focus_callers"]]
    classified: list[tuple[dict[str, object], str, str]] = []
    counts: Counter[str] = Counter()
    by_file: dict[str, list[tuple[dict[str, object], str, str]]] = defaultdict(list)
    for row in rows:
        category, reason = classify(row)
        counts[category] += 1
        classified.append((row, category, reason))
        by_file[str(row["file"])].append((row, category, reason))

    lines = [
        "# 无法挂入目标国策的事件名称表",
        "",
        "本表覆盖模组 `events/` 下全部事件。已挂入本轮目标国策的事件不重复列出；其余事件逐项注明为何不能安全挂载。",
        "",
        "## 分类汇总",
        "",
        "| 分类 | 数量 |",
        "| --- | ---: |",
    ]
    for category, count in sorted(counts.items()):
        lines.append(f"| {category} | {count} |")

    for file, entries in sorted(by_file.items()):
        lines.extend(
            [
                "",
                f"## `{file}`",
                "",
                "| 事件 ID | 事件名称 | 分类 | 未挂载原因 | 既有引用 |",
                "| --- | --- | --- | --- | --- |",
            ]
        )
        for row, category, reason in entries:
            refs = "、".join(f"`{value}`" for value in row["reference_files"]) or "—"
            lines.append(
                f"| `{row['id']}` | {display_title(row, loc)} | {category} | {reason} | {refs} |"
            )

    output = args.output if args.output.is_absolute() else root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {len(rows)} named unassigned/system event rows to {output}")
    for category, count in sorted(counts.items()):
        print(f"{category}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
