# YUN 原版流程与 DOP 西南战争隔离审计

本文件记录 260902F 对 TNO YUN 流程的机械审计。原版来源均为本地 TNO 1.10.0b 文件；DOP 不修改这些 Workshop 文件。

## 原版完整链

1. YUN 与 GUZ 起初分别作为 CHI 附庸存在。统一流程会解除 GUZ 附庸、把 GUZ 州核心改给 YUN、合并军队，并切换为 YUN_southwest_united。
2. yun_unified.25 原本在四日后排入 .26 → .27 → .28。DOP 作者已在 events/TNO_Yunnan.txt 注释该入口，阻止本体自动继续。
3. .28 调用 YUN_Long_Yun_Coup_effects，完成龙云夺权、政府与经济切换、护国军模板、阵营和国策树切换，并排入 yun_wi.1、.4、.7 等事件。
4. yun_wi.1–14 组织原国军/中共成员、四川争夺与季节倒计时；.13 通过 YUN_volunteers 生成十个护国军师。
5. yun_wi.15 调用 WI_Start_effects，按本体方式重组 CHI 阵营、初始化省份 GUI、向 CHI 宣战并触发 GNG 原版响应。
6. 战争升级后 WI_GAW_Start_Effects 启动大东亚战争机制；战败时和平 on_action 调用 YUN_NPA_fails_effects 和 YUN_southwest_reconstruction_effects。

## GNG 原版响应

TNO_Guangdong.txt 定义 GNG_Western_Insurrection.1–12 共十二个事件。四类外部入口为：

- WI_Start_effects 排入 .1；
- WI_GAW_Start_Effects 排入 .8；
- 两个西部起义战败和平分支排入 .7；
- 大东亚战争战败和平分支排入 .12。

DOP 不调用前两个原版启动效果，并在自身开局与危机入口清除后三类 on_action 使用的原版全局 flag。十二个事件的内部链因没有任何首事件被排入而全部失活。

## DOP 专用映射

- 复用：YUN–GUZ 合并方式、护国军政府和经济初始化、YUN_long_yun_crusade_tree 护国军国策树、YUN_NPA_army 模板、YUN_volunteers 十个师、合法性/战力修正、YUN_southwest_reconstruction_effects。
- 替换：龙云改为龙绳武；角色在 YUN 历史阶段预先招募，运行时只提升党魁和切换执政党。
- 排除：YUN_Long_Yun_Coup_effects、WI_Start_effects、WI_GAW_Start_Effects、yun_wi.* 排程、本体危机 flag、本体 GNG 响应事件。
- 开战：仍由 DOP 危机先合并 GUX/海南并对 CHI 宣战，十四日后由 DOP 事件使 YUN 对 GNG 宣战。
- AI：仅在 YUN 已与 GNG 交战时启用 rush 前线、兵力集中、征服和“视为弱敌”策略；战后自动停用。
- 日本干预：茂名失守后完整等待十四日，JAP 先将 CHI 与 GNG 拉回共荣圈，再加入 GNG–YUN 战争；十二小时后在广州部署十二个使用专用模板的 JAP 装甲师，并启用对 YUN 的 rush 进攻计划。广州不可用时每十二小时重试，战后删除这些部队及模板。
- 战后树：YUN 清除护国军 flag 并切回 YUN_post_xinan；获释的 GUX 显式载入 TNO 空树 ZZZ_blank_focus。
- 地块：所有 GNG 州按本体珠三角触发器动态分配正面或负面修正；所有实际 YUN–CHI 接壤州的双方均获得 DOP 专用进攻锁。

## 测试要求

龙绳武由 history/countries/YUN - Yunnan.txt 招募，必须新开游戏验证；数据库热重载或旧存档不会补建角色。
