# DOP 260902A 完整修订清单

修订日期：2026-09-02  
构建号：`EARLY DEVELOPMENT BUILD 260902A`  
作者原稿：`docs/design/全流程_作者原始稿.txt`  
原稿 SHA-256：`263E1AC1995E59B6187BAE83761B9FAA8AD6611A06BB94B4A3EAA817DA5D0EE6`

## 1. 范围自审

本轮自由完成了数值设计、国策奖励装填、阶段状态机、战争骨架、现有 GUI/决议/项目的接线与渐进开放。以下内容没有擅自创作：

- 图片没有新增、修改或生成。
- 新增的四个可见剧情事件全部使用显著的 `【Placeholder】` 标题、描述和选项。
- 三田胜茂缺少文本头像时，界面使用 `【Placeholder：三田胜茂文本头像】`，没有制作或冒用图片。
- 广东大剧院没有被正常流程开启；其未完成指标已从芯片冷战运行时彻底脱钩。
- 法案及其前置国策段保持冻结，不可正常点选。
- 文官政变与第二次暴乱两棵大剧院失败树没有装填任何本轮内容。
- 正常结局树只加入数值奖励，已有 `country_event` 调用全部移除；没有加入领导人更换、剧情链、cosmetic tag 或政治体制变化。
- 第五阶段人质危机和第六阶段结局剧情没有创作。

## 2. 阶段流程

### 阶段一：本体盛田结局接棒

- 每日检测本体最终国策 `GNG_the_coming_storm`。
- 完成后只执行一次 `DOP_GNG_begin_post_tno_content`，载入 `DOP_GNG_opening_tree`。
- 保留本体既有 GUI 和国家精神，不在阶段入口重置本体经济/社会变量。
- 初始化 `DOP_GNG_content_stage = 1`、`DOP_GNG_ibuka_points = 0`。
- 日立 70 年代领袖显示改为作者指定的三田胜茂；文本头像保持 Placeholder。
- `DOP_GNG_faux_opening` 使用 `select_effect`，玩家点选而非完成国策时触发战争序幕 Placeholder 事件。

### 阶段二：大西南战争

- YUN 在起事时吞并 GUX 的九州，并接收海南三州 `591/2474/2475`。
- CHI 先把 YUN 的自治度设为 `autonomy_free`，随后 YUN 才对 CHI 宣战。
- CHI、YUN、GNG 由 JAP 作用域移出共荣圈。
- 14 日后的 Placeholder 事件让 YUN 对 GNG 宣战。
- 广东参战时删除现有 `Sensha Shidan - Armored Division` 单位，不删除模板，也不返还装备。
- 战时国家精神切换为第一次国难、举目所及风雨飘摇、全亚清廉和按债务率刷新的财政等级。
- 珠三角四州获得战时防御修正，外围三州获得防御惩罚。
- 云贵北部六州使用本体西班牙内战 `unplanned_offensive` 修正，南线孟自方向保持可突破。
- 茂名被 YUN 控制后启动 7 日计时；广东未投降时，在广州州作用域生成 6 个 85% 经验、满装备的装甲师。
- 援军同时获得 120 日反攻修正、5000 步兵装备、750 支援装备、500 摩托化装备、10% 战争支持和 50 指挥点。
- 胜利条件要求 GNG 同时控制昆明 `325` 与全部七个原始广东州。

### 战后结算

- GNG 与 CHI 分别同 YUN 停战。
- GNG 先接收 GUX 九州，再以 `autonomy_reliant` 放出 GUX。
- 广东从 GUX 收回湛江 `1464` 与钦州 `2472`。
- 广东从 YUN 接收海南 `591/2474/2475`。
- CHI 将 YUN 设为 `autonomy_military_government`，作为西南重建政府。
- 所有战时州修正与援军临时修正使用存在性检查后移除，不再刷缺失修正警告。
- 载入 `dop_sonyjapan_reconsturuction_tree`，阶段变量改为 3。

### 阶段三：重建与 GUI 顺序

1. `GNG_focus_temporary_relief` 恢复立法会。
2. `GNG_focus_foothold` 恢复地区 GUI，并把海口/湛江/钦州纳入人口、支持率和黑道数组。
3. `GNG_focus_leave_ruins_behind` 开启岭南建设总署，只展示项目 12 重整广西实业院和项目 13 广西高速公路网，不自动开工。
4. `DOP_GNG_recon_foundation` 开启芯片冷战 BoP 页与基础决议。
5. `DOP_GNG_recon_backwardness_disaster` 独立开启科学院 BoP 页。
6. 三个介绍国策分批放出 SCW 后续里程碑决议。
7. `DOP_GNG_recon_no_time_to_turn` 恢复珠江奇迹，并默认切换到 CHI 对比。
8. `DOP_GNG_recon_grand_wall_weak_foundation` 固定不可用，显示大剧院 Placeholder；后续国策绕过它。
9. `GNG_focus_new_products_old_friends` 移到重建树末尾，恢复产品周期并载入核心树。

### 阶段四及以后

- `GNG_focus_new_fate_choice_of_gng` 添加初始国族认同“南国乡愁”。
- 核心树中 98 个法案或法案前置国策要求未设置的 `DOP_GNG_law_content_ready`，正常游戏不可点选。
- 开局树中 5 个现有单国策法案及其直接前置同样冻结；最终开局国策改由非法律恢复节点与军务节点解锁。
- `GNG_focusambitions_of_tycoons` 只有在政治、现代化、国际与安保终点全部完成时可结算线路。
- 第五阶段只预留 `DOP_GNG_transition_stage_ready` 和阶段变量 5，不触发人质危机剧情。

## 3. 战争与国家精神数值

### 州修正

| 修正 | 数值 |
|---|---|
| 珠三角战时防御 | 陆军防御 +35%，当地组织恢复 +15%，损耗 -5% |
| 外围防线崩解 | 陆军防御 -25%，当地组织恢复 -15%，损耗 +10% |
| 日本援军反攻势头 | 陆军攻击 +20%，陆军防御 +10%，陆军组织 +10%，损耗 -10%，120 日 |
| 云贵北线僵持 | 复用 `unplanned_offensive`：进攻 -90%，速度 -75%，当地组织恢复 -50% |

### 14 个新增/续作国家精神数值

| 国家精神 | 数值设计 |
|---|---|
| 第一次国难 | 稳定 -15%，战争支持 +10%，每日政治点 -0.10，建造速度 -20%，工厂产出 -15%，GDP 增长修正 -2.00，实际 GDP 修正 -1.50 |
| 岭南之春 | 稳定 +5%，每日政治点 +0.05，建造速度 +10%，工厂产出 +5%，GDP 增长修正 +0.50 |
| 反认他乡是故乡 | 稳定 +10%，每日政治点 +0.10，建造速度 +10%，工厂产出 +10%，GDP 增长修正 +0.50 |
| 还有明天 | 稳定 +5%，每日政治点 +0.05，工厂产出 +15%，研究速度 +10%，广东研发修正 +10% |
| 狮子山日暮 | 稳定 -5%，每日政治点 +0.10，工厂产出 +15%，GDP 增长修正 +0.75，杂项收入 +10% |
| 重奏1962序曲 | 稳定 -25%，战争支持 +10%，每日政治点 -0.15，建造速度 -15%，工厂产出 -10% |
| 铅色年华 | 稳定 -35%，战争支持 +15%，每日政治点 -0.20，建造速度 -25%，工厂产出 -25%，损耗 +10% |
| 举目所及，风雨飘摇 | 稳定 -5%，每日政治点 -0.05，战争支持 +10%，陆军防御 +10%，可征募人口系数 +2% |
| 安保部门，方兴未艾 | 稳定 -2%，每日政治点 -0.03，驻军受抵抗损失 -10%，陆军防御 +5% |
| 国家的剑与盾 | 稳定 +7%，每日政治点 +0.05，驻军受抵抗损失 -20%，陆军防御 +5% |
| 南国乡愁 | 稳定 -3%，每日政治点 -0.03，中日态度上限各 -5 |
| 枯叶的漫漫归途 | 稳定 +8%，每日政治点 +0.05，华人/珠人月度政府支持各 +0.20 |
| 新生儿的啼哭 | 稳定 +5%，每日政治点 +0.05，华人向珠人转化 +5%，中国态度上限 -10，日本态度上限 +5 |
| 战火中的珠三角 | 稳定 -10%，战争支持 +15%，每日政治点 -0.10，建造速度 -30%，工厂产出 -20%，损耗 +5% |

安保层级同时同步本体广东安保动态修正：战争期 6，战后 4，改革完成 2。腐败在战争/战后入口统一刷新为本体等级 3“全亚清廉”。财政等级按债务/GDP 的 25%、50%、75%、100% 阈值刷新为本体五级财政状态。

## 4. 通用国策数值包

| 数值包 | 效果 |
|---|---|
| 恢复·小 | 政治点 +15，稳定 +1%，GDP 增长 +0.10，支出 0.10B |
| 恢复·中 | 政治点 +25，稳定 +2%，GDP 增长 +0.20，支出 0.25B |
| 经济·小 | 政治点 +15，GDP 增长 +0.10，支出 0.15B |
| 经济·中 | 政治点 +20，GDP 增长 +0.20，支出 0.30B，永久工厂产出 +1% |
| 经济·大 | 政治点 +30，稳定 +2%，GDP 增长 +0.35，支出 0.50B，永久工厂产出/建造速度各 +2% |
| 社会·小 | 政治点 +15，稳定 +1.5%，支出 0.10B，全部州华人/珠人支持各 +0.5 |
| 社会·中 | 政治点 +20，稳定 +3%，支出 0.25B，全部州华人/珠人支持各 +1 |
| 安保·小 | 政治点 +10，稳定 +1%，指挥点 +10，陆军经验 +5，腐败 -0.5 |
| 安保·中 | 政治点 +15，稳定 +2%，战争支持 +1%，指挥点 +15，陆军经验 +10，腐败 -1 |
| 安保·大 | 政治点 +25，稳定 +4%，战争支持 +2%，指挥点 +25，陆军经验 +15，腐败 -2 |
| 科研·小 | 政治点 +10，支出 0.20B，永久研究速度 +1%，广东研发修正 +2% |
| 科研·中 | 政治点 +15，稳定 +1%，支出 0.35B，永久研究速度 +1.5%，广东研发修正 +3% |
| 贸易·小 | 政治点 +15，GDP 增长 +0.10，中日态度各 +1 |
| 贸易·中 | 政治点 +20，稳定 +1%，GDP 增长 +0.20，永久杂项收入 +1%，中日态度各 +2 |
| 索长包 | 社会·小，加永久建造速度 +2% |
| 财界包 | 经济·小，加永久工厂产出 +2.5%、杂项收入 +2%、腐败 +0.5 |
| 索富包 | 科研·小，加永久工厂产出 +2% |

覆盖数量：

- 开局树 15 个非冻结国策。
- 战争树 7 个国策。
- 重建树 22 个国策。
- 核心树 69 个可独立设计的非冻结国策。
- 索长、索富、财界正常结局树各 12 个国策。
- 合计 149 个国策加入数值效果。

## 5. 井深点与线路判定

- 新变量 `DOP_GNG_ibuka_points`，范围钳制为 0–99。
- 芯片冷战结算一次：第五名 0、第四名 1、第三名 2、第二名 3、第一名 4；逐一比较 USA/ITA/GER/JAP 当前份额。
- 科学院当前已实现的项目 1 首次完成加 1，并有独立防重旗标。
- 建设项目 4 大亚湾核电站、11 文昌卫星发射中心、17 珠三角磁悬浮、19 花岗岩型铀矿首次验收各加 1。
- 四个建设计分钩子已写入建设生成器，重新生成不会丢失。
- 国族认同为枯叶归途时锁定索长线。
- 国族认同为新生儿啼哭且总点数不少于 9 时锁定索富线；低于 9 锁定财界线。
- 国族认同法案仍冻结时，线路明确记录为 unresolved，不擅自选线。

## 6. 芯片冷战与科学院

- 保留 48 个已有 SCW 决议和 5 个竞争者基线。
- 修复 `decision_tabs_id = 1` 的无效裸变量触发，改为 `check_variable`。
- 新增三个同步动态 token，消除多人 OOS 警告。
- 原生成器把本体变量包装为大剧院指标，本轮改为直接显示和调用：
  - 舞台完整度 → 腐败。
  - 监制态度 → 日本认可。
  - 观众耐心 → 中国意见。
- 数值倍率保持原生成器的 2 倍平衡不变；只移除未完成的大剧院包装、文本图标和 helper 调用。
- 科学院增加独立 BoP 定义和幂等初始化旗标 `DOP_GSA_enabled`，不会重复添加标签。

## 7. 修复的既有加载问题

- `DOP_SCW_effects.txt` 两处无效 `decision_tabs_id` 触发。
- 三个 BoP token 未同步导致的 OOS 警告。
- `DOP_GNG_zip.16` 把数值直接当 effect 的五个错误，改为本体临时变量 + helper。
- `max_organisation_factor` 改为当前 TNO 有效的 `army_org_factor`。
- `add_army_experience` 改为当前有效的 `army_experience`。
- 两处不兼容的 `>=/<=` 简写改为完整 `compare` 语法。
- 单行 `completion_reward = { }` 导致奖励落在块外的问题。
- 移除建设系统中两处大剧院完整度刷新调用。
- 移除不存在的 `GNG_focus_look_inland` 旧依赖。

## 8. 逐文件清单

### 新增正式游戏文件

- `common/dynamic_modifiers/DOP_GNG_flow_dynamic_modifiers.txt`：战争州修正和援军反攻修正。
- `common/on_actions/DOP_GNG_flow_on_actions.txt`：本体接棒、茂名七日计时、完整胜利检测。
- `common/scripted_effects/DOP_GNG_flow_effects.txt`：六阶段状态机、战争、领土、GUI、计分、路线。
- `common/scripted_effects/DOP_GNG_reward_packages.txt`：通用数值包。
- `common/synchronized_dynamic_tokens/DOP_bop_tokens.txt`：三个 BoP 同步 token。
- `events/DOP_GNG_flow.txt`：4 个可见 Placeholder 事件和 6 个隐藏 GUI 锁定事件。
- `localisation/simp_chinese/DOP_GNG_flow_l_simp_chinese.yml`：Placeholder、数值提示和路线提示，UTF-8 BOM。

### 修改游戏内容

- `common/bop/DOP_BoP_Defines.txt`：注册科学院标签。
- `common/decisions/DOP_SCW_decisions.txt`：生成器输出改用腐败/中日态度。
- `common/ideas/DOP_GNG_postwar_ideas.txt`：14 个国家精神数值。
- `common/national_focus/dop_sony-opening.txt`：15 个奖励、5 个法案冻结、select 转场与新前置。
- `common/national_focus/dop_sony-japan_prewar.txt`：7 个战争国策奖励。
- `common/national_focus/dop_sony-japan_reconstruction.txt`：重排顺序、22 个奖励、7 项 GUI 开放、大剧院旁路。
- `common/national_focus/dop_sony-japan_core.txt`：69 个奖励、98 个冻结门、路线锁、项目/SCW 解锁、旧依赖修复。
- `common/national_focus/dop_sony-japan_ending1_lee.txt`：12 个纯数值奖励，移除事件调用。
- `common/national_focus/dop_sony-japan_ending2_ibuka.txt`：12 个纯数值奖励，移除事件调用。
- `common/national_focus/dop_sony-japan_ending3_hitachi.txt`：12 个纯数值奖励。
- `common/on_actions/TNO_Guangdong_on_actions.txt`：移除启动/月度大剧院完整度刷新。
- `common/scripted_effects/DOP_GNG_postwar_effects.txt`：同步本体安保层级，移除未使用的大剧院完整度 effect。
- `common/scripted_effects/DOP_SCW_effects.txt`：SCW/GSA 幂等初始化、当前 GSA 计分、旧触发和剧院 helper 清理。
- `common/scripted_effects/DOP_construction_effects.txt`：移除两处大剧院完整度调用。
- `common/scripted_effects/DOP_construction_rewards.txt`：四项目井深点生成结果。
- `common/scripted_guis/TNO_GNG_Economy_GUI.txt`：CHI/MAN 切换按钮在正式解锁后可见，不再只限 debug。
- `events/DOP_GNG_zip.txt`：修复事件 16 的五个无效人口/支持率 effect。
- `localisation/simp_chinese/DOP_GNG_postwar_ideas_l_simp_chinese.yml`：使用作者原稿中的三个安保名称。
- `localisation/simp_chinese/DOP_SCW_decisions_l_simp_chinese.yml`：生成器输出改为本体腐败/中日态度图标与文本。
- `localisation/simp_chinese/DOP_version_l_simp_chinese.yml`：构建号 260902A。
- `localisation/simp_chinese/replace/TNO_Guangdong_l_simp_chinese.yml`：三田胜茂领袖显示与图片 Placeholder。

### 生成器、验收与文档

- `tools/generate_dop_construction.py`：四个建设项目井深点成为生成器单一事实来源。
- `tools/check_dop_construction.py`：验证项目 12/13 只开放不自动开工、四个计分防重钩子和 260902A。
- `tools/generate_dop_scw_decisions.py`：大剧院三指标改为本体腐败/中日态度。
- `tools/check_dop_scw.py`：验证 48 决议、规范 helper、剧院运行时 token 为零。
- `tools/check_dop_content_flow.py`：完整流程静态验收器。
- `docs/DOP_construction_static_acceptance.md`：目标版本同步为 260902A。
- `docs/design/README.md`：设计原稿索引、哈希与能力边界。
- `docs/design/implementation_matrix.md`：阶段、GUI、冻结区和井深点映射。
- `docs/design/全流程_作者原始稿.txt`：作者附件逐字节归档。
- `image_tools/Capture-Hoi4Window.ps1`：PrintWindow 测试捕获工具。
- `image_tools/Send-Hoi4ConsoleText.ps1`：控制台已打开时的无切换输入工具。
- `output/testing/dop_flow_playtest.log`：测试摘要。
- `output/testing/game_flow_chain_260902A.log`：端到端运行日志。
- `output/testing/error_flow_chain_260902A.log`：端到端错误日志。

## 9. 验证结果

- `check_script.py`：88 个 Paradox/GUI 脚本，0 个括号/引号错误。
- `check_gui_script.py`：14 个 GUI/GFX/scripted GUI 文件，0 错误、0 警告。
- 建设生成器 `--check`：current。
- SCW 生成器 `--check`：current。
- 建设静态验收：PASS。
- SCW 静态验收：48 决议 PASS。
- 完整流程静态验收：PASS。
- 所有简中 YML 均有 UTF-8 BOM。
- Git 状态中没有任何新增或修改的 PNG/JPG/DDS/TGA/PSD。
- 最终 HOI4 运行使用 TNO + TNO CN + DOP，`Active Mod Count: 3`。
- 最终干净加载抵达 `Start RestoreDeviceObjects`。
- 最终语义计数全部为 0：Unknown effect、Unknown trigger、Unknown modifier、gameitemdatabase、旧依赖、YUN subject 宣战、create_unit scope、缺失 modifier 清理、BoP token OOS。
- 端到端运行日志依次确认阶段一、危机、入战、援军、战后、七个 GUI、建设点、GSA 点、SCW 名次点、财界 6 点、索富 9 点、索长双元认同。
- DX11 在本机测试环境中于设备创建阶段崩溃；临时使用 OpenGL 完成测试。用户原始 DX11/2560×1440/8x MSAA 设置已按 SHA-256 原样恢复。

## 10. 已知 Placeholder 与未处理项

- 【Placeholder】四个战争/转场可见事件的全部剧情文本。
- 【Placeholder】三田胜茂文本头像。
- 【Placeholder】现有国策缺图与缺 shine 警告；按能力边界未制作图片。财界结局树仍有 6 个实际 Missing icon，其余多为 Missing icon shine。
- 【Placeholder】广东大剧院国策、机制、指标与两条失败线。
- 【Placeholder】法案及法案前置国策段，共冻结核心树 98 个、开局树 5 个。
- 【Placeholder】第五阶段人质危机事件链。
- 【Placeholder】三个正常结局的领导人、国家精神切换、事件链等非数值效果。
- 本体/其他模组仍有与本轮无关的音频缺失、frontend subscription 锚点、超大雾效纹理、旧 DDS mipmap 和本地化碰撞提示；最终 DOP 非图片错误为 0。

## 11. 建议明早重点审阅

1. 战争节奏：危机后 14 日参战、茂名后 7 日援军、6 个装甲师是否合适。
2. 战争强度：珠三角 +35% 与外围 -25%，北线 `unplanned_offensive` 是否过强。
3. 通用数值包：长期工厂/建造/研究修正是否需要再压低。
4. GUX/YUN 战后自治层级是否符合最终叙事设定。
5. 建设项目的开放映射，尤其项目 14–16 和路线专属项目。
6. SCW 初始排名在测试基线中给广东第一名并奖励 4 点，是否符合目标难度。
7. 井深阈值 9 与四个建设项目、科学院、SCW 三类来源的可达性。
8. 98 + 5 个冻结国策的边界是否过宽或过窄。
9. 是否保留三棵正常结局树的 36 个纯数值奖励。
