# DOP 260902E：YUN 战前状态与西南战争接线

构建号：`EARLY DEVELOPMENT BUILD 260902E`

## 结论

- 卢汉未被替换属于 DOP 实现缺漏，不是等待 YUN 自行推进。
- 作者在 `events/TNO_Yunnan.txt` 中对 `yun_unified.25 → yun_unified.26` 的阻断保持不变。
- DOP 不调用 `YUN_Long_Yun_Coup_effects` 或 `WI_Start_effects`，以免恢复本体的龙云线路、日期、事件排程、阵营重组和开战方式。

## 实现

- 新增龙绳武角色，使用既有 `gfx/leaders/YUN/DOP_Long_Shengwu.png`。
- 新增幂等效果 `DOP_YUN_prepare_southwest_war`，选择性复用本体的护国军政府、军队模板、经济与合法性机制。
- 新增调试决议 `DOP_GNG_debug_flow_02a_yunnan_prewar`；只推进 YUN 至战前状态，不宣战。
- DOP 正式危机效果会自动执行同一战前准备，再按原有 DOP 方式吞并广西/海南、脱离阵营并宣战。
- 战后退役龙绳武并调用本体 `YUN_southwest_reconstruction_effects`，随后沿用 DOP 的南京军事政府安排。

## 验收重点

- 本体触发阻断仍为非活动脚本。
- 战前准备中不存在 `YUN_Long_Yun_Coup_effects`、`WI_Start_effects`、`yun_wi.*` 排程或 `declare_war_on`。
- 02A、正式危机和战后重建均指向同一套明确作用域。
