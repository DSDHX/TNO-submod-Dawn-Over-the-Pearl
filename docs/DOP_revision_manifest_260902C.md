# DOP 260902C 流程调试决议增量清单

构建号：`EARLY DEVELOPMENT BUILD 260902C`  
日期：2026-09-02

## 新增内容

新增 `common/decisions/DOP_GNG_flow_debug_decisions.txt`，在既有 `GNG_debug_category` 中扩展 17 个顺序编号的主要流程调试节点：

1. 进入战后开局。
2. 触发西南危机开场事件。
3. 触发广东正式参战事件。
4. 启动茂名七日倒计时。
5. 使日本援军立即抵达。
6. 触发昆明胜利与战后结算事件。
7. 恢复立法会。
8. 恢复区域治理地图及新增地区。
9. 开启岭南建设总署。
10. 恢复产品周期。
11. 开启三微米冷战及4项初始可重复决议。
12. 开启广东科学院。
13. 恢复GDP对比。
14. 进入核心国策树。
15. 进入长实正面结局。
16. 进入富士通正面结局，并设置9点井深点数。
17. 进入财界结局，并设置0点井深点数。

前三个战争事件与战后结算继续调用现有 `DOP_GNG_flow` 事件；其余节点调用正式 scripted effect，没有复制生产流程逻辑。

## 可见性与安全边界

- 仅对 `original_tag = GNG` 生效。
- 必须同时满足 `GNG_show_debug_decisions` 与 `is_debug = yes`，正常游戏不会显示。
- 全部决议 `cost = 0`、AI 权重为 0，可由测试者主动选择。
- 战争、领土与附庸节点具有真实流程副作用；中文说明已明确标注。
- 不包含任何广东大剧院入口或效果。
- 新增本地化：`localisation/simp_chinese/DOP_GNG_flow_debug_l_simp_chinese.yml`，UTF-8 BOM。
- 作者手动修改的产品周期与核心接棒 tooltip 未被回滚；这两条文本从 C 版自动文本断言中排除。

## 验收

- `python tools/check_dop_flow_debug_decisions.py`：17 个节点 ID、调试可见性、AI、事件/effect 接线和本地化全部通过。
- `python tools/run_dop_revision_check_quiet.py`：1685 条综合断言通过。
- `python tools/check_dop_content_flow.py`：主流程回归通过。
- `python tools/check_dop_construction.py`：建设系统回归通过。
- Paradox 结构检查：`common` + `events` 共 63 个文件，0 错误。
- 简体中文本地化：32 个 `.yml`，缺失 BOM 为 0。
- `git diff --check`：0 错误。

游戏内操作与验证由作者自行进行。
