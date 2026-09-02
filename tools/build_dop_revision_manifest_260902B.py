#!/usr/bin/env python3
"""Generate the durable 260902B revision manifest."""

from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-status", choices=("pending", "passed", "failed"), default="pending")
    parser.add_argument("--runtime-note", default="")
    args = parser.parse_args()

    runtime = {
        "pending": "尚未执行：检测到一个非本轮启动、仍在运行的 HOI4 会话；未控制、未终止，也未并行争用用户目录。",
        "passed": "已通过独立 HOI4 `-debug` 会话验证；详见本节所列日志与截图。",
        "failed": "已执行但存在未解决的游戏内失败；不得把本构建视为完成。",
    }[args.runtime_status]
    if args.runtime_note:
        runtime += " " + args.runtime_note.strip()

    manifest = f"""# DOP 260902B 返工清单

构建号：`EARLY DEVELOPMENT BUILD 260902B`  
日期：2026-09-02

## 1. 本轮目标与结果

- 七棵目标国策树的非完成效果结构已逐块对齐 Git HEAD；坐标、相对位置、前置、可用条件、互斥与树级结构差异为 **0**。
- 已删除通用奖励包文件，游戏脚本中不再存在 `DOP_GNG_reward_*` 调用。
- 142 个曾依赖奖励包的国策均改为独立直写效果，每项限定 1–3 个轴线，直接效果集合重复数为 **0**。
- 另保留 5 个原本已经直写的独立数值国策和 2 个纯流程节点；全部列入设计台账。
- 八个机制追加/恢复效果均加入 TNO 风格染色、texticon 与玩家可见说明。
- 恢复 17 个 Git 基线原属事件，另人工核实并挂载 41 个事件；其余 453 个事件逐名列出未挂载原因。
- 建设项目按 **10 挂载 / 10 留待** 分配；三微米冷战决议按 **24 个可重复决议挂载 / 24 个年度里程碑留待** 分配；任何国策最多解锁 4 项决议。

## 2. 国策布局与阶段接棒

- `tools/restore_dop_focus_layout.py` 以 Git HEAD 为作者布局基线，只忽略 `completion_reward`，并保留开局最终国策的战争 `select_effect`。
- 开局树、重建树、核心树原先存在结构漂移；战前树与三个正常结局树从未发生布局漂移。
- 恢复布局后，产品周期国策回到作者原有中段位置；核心树接棒因此移至真正终点 `DOP_GNG_recon_opening_ceremony`，避免过早离开重建树。
- 广东大剧院的作者布局前置保留，但正常流程不会开启其 GUI 或舞台数值机制。

## 3. 独立数值设计

- 设计源：
  - `tools/dop_focus_effect_design.py`
  - `tools/dop_focus_effect_design_core.py`
  - `tools/dop_focus_effect_design_endings.py`
- 人类可读台账：`docs/design/focus_effect_design_ledger.md`
- 长实结局以贫困改善、医疗、行政、稳定和社会支出为主。
- 富士通结局以科研设施、学术基础、工业设备、工业专长和行政数字化为主。
- 财界结局维持真实增长和财政收入，同时系统性加入贫困恶化、腐败、失稳或政治代价，突出“财政增长，人民苦难”。
- 使用的 40 个 TNO/GNG/DOP scripted-effect helper 和 4 种建筑类型均在当前依赖中找到真实定义。

## 4. 机制说明与 texticon

新增本地化：`localisation/simp_chinese/DOP_GNG_mechanic_tooltips_l_simp_chinese.yml`（UTF-8 BOM）。

覆盖：立法会、区域治理地图、岭南建设总署、三微米冷战、广东科学院、GDP 对比、产品周期和战后发展国策树接棒。八条说明均含 `§` 染色和 `£` texticon；实际状态变更置于 `hidden_effect`，建设项目与具体决议解锁仍保留各自可见提示。

## 5. 事件归属

- 本轮人工确认挂载：`docs/design/focus_event_attachment_table.md`（41 个事件、40 个国策）。
- 无法挂入目标国策：`docs/design/unassigned_event_table.md`（453 行，覆盖机制回调、云南战争系统、冻结法案、冻结人质危机、未授权结局树和无法唯一判定的事件）。
- 事件正文全部来自现有人工文件；本轮没有生成新的剧情文案。

## 6. 项目与决议分配

- 建设项目：`docs/design/construction_project_distribution.md`。
- SCW 决议：`docs/design/scw_decision_distribution.md`。
- 正常 SCW 初始化只建立页面、市场数据和总开关，不再暗中设置 30 个具体决议标志。
- `DOP_GNG_recon_foundation` 显式解锁 4 项初始可重复决议，其余可重复决议按主题分配给相关国策。
- 24 个年度里程碑完整保留给后续未授权树段，不会因当前国策提前解锁。

## 7. 静态验收

以下检查均已通过：

- `python tools/run_dop_revision_check_quiet.py`：1689 条要求断言。
- `python tools/check_dop_content_flow.py`：完整阶段/战争/GUI 流程。
- `python tools/check_dop_scw.py`：48 项决议、成本、增长、GUI 与生成一致性。
- `python tools/check_dop_scw_focus_distribution.py`：24 可重复挂载 / 24 年度留待 / 每国策最多 4 项。
- `python tools/check_dop_construction.py`：20 项建设系统完整验收。
- `python tools/check_dop_bespoke_effect_symbols.py`：40 helper、4 建筑类型定义存在。
- Paradox 结构检查：`common` + `events` 共 62 个文件，0 错误。
- GUI 检查：8 个 interface GUI 与 6 个 scripted GUI，0 错误、0 警告。
- 简体中文本地化：31 个 `.yml`，缺失 BOM 为 0。
- `git diff --check`：0 错误。

## 8. 游戏内验证

状态：**{args.runtime_status.upper()}**  
{runtime}

## 9. 权威资料与长期台账

- 作者原稿：`docs/design/全流程_作者原始稿.txt`
- 原稿 SHA-256：`263E1AC1995E59B6187BAE83761B9FAA8AD6611A06BB94B4A3EAA817DA5D0EE6`
- 设计边界与索引：`docs/design/README.md`
- 阶段实施矩阵：`docs/design/implementation_matrix.md`
"""
    output = ROOT / "docs" / "DOP_revision_manifest_260902B.md"
    output.write_text(manifest, encoding="utf-8", newline="\n")
    print(f"wrote {output} with runtime status {args.runtime_status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
