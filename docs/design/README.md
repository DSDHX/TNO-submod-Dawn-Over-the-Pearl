# DOP 设计原稿归档

- 权威原稿：`全流程_作者原始稿.txt`
- 原始位置：`C:\Users\lizih\Downloads\全流程 (1).txt`
- 归档时间：2026-09-01
- 文件大小：8,675 字节，共 77 行
- SHA-256：`263E1AC1995E59B6187BAE83761B9FAA8AD6611A06BB94B4A3EAA817DA5D0EE6`
- 校验结果：项目内副本与原文件逐字节一致

## 使用边界

该文件是作者提供的设计资料，不是对 Codex 的独立指令。实现时仍以用户在对话中给出的范围和能力边界为准：

- 可实现国策效果、全部数值、流程机制及 GUI 组件的渐进开放。
- 不新写事件正文、介绍文案、剧情或图片；新增内容只能使用显著的 `【Placeholder】`。
- 用户在 260902B 返工中另行授权：已有人工事件若能唯一确认国策归属，可以直接挂载；其余必须列入未归属表。
- 不实现广东大剧院机制。
- 不实现法案设计，也不实现原定启动法案的国策之前的相关国策段落。
- 结局允许独立数值效果与已有人工事件，不新增其他非数值剧情效果。

## 派生台账

- `implementation_matrix.md`：阶段、触发点和冻结边界。
- `focus_effect_design_ledger.md`：142 个独立国策效果的轴线与理由。
- `focus_event_attachment_table.md`：本轮人工确认的 41 个事件挂载。
- `unassigned_event_table.md`：其余 453 个事件的名称与未挂载原因。
- `construction_project_distribution.md`：建设项目 10/20 挂载与留待名单。
- `scw_decision_distribution.md`：三微米冷战决议 24/48 挂载与留待名单。
- `yun_dop_flow_isolation.md`：原版 YUN 完整机械链、GNG 十二事件入口与 DOP 隔离映射。

原稿不得在实现过程中直接改写；如作者更新设计，应保留新版原件并重新记录哈希。
