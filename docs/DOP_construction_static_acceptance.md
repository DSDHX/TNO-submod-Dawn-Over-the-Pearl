# 南粤建设系统：静态验收报告

验收日期：2026-08-29
Git 基线：28df6f9b623f68e7c23610f36b2fa5adb38d3787
目标版本：260829A
TNO 静态参考：D:\Steam\steamapps\workshop\content\394360\2438003901

## 结论

静态验收通过。按要求未启动 Hearts of Iron IV；因此本报告证明生成一致性、脚本/GUI 结构、资源头、映射和当前 TNO 数据兼容性，不宣称完成游戏内点击或存档实测。

## 自动检查

| 检查 | 结果 |
|---|---|
| python -B tools/check_dop_construction.py | PASS：6 地区、20 项目、20 奖励、20 事件、20 sprite、20 DDS、20 套本地化、v8、队列和铁路全部通过 |
| python tools/generate_dop_construction.py --check | PASS：construction registry is up to date |
| hoi4-modding check_script.py（8 个建设脚本） | PASS：8 files, 0 errors |
| hoi4-gui-modding check_gui_script.py | PASS：2 files, 0 errors, 0 warnings |
| hoi4-gui-modding render_gui_layout.py | PASS：离线布局图已生成 |
| git diff --check | PASS |

## 功能链

- 项目数据只维护在生成器的一份 Project/Reward 表中，动态目录仍为单套 GUI、单个项目模板与六个可折叠地区。
- 简介区点击后切换到同一位置的效果页；效果页通过 effect_tooltip 调用真实完工 callback。事件领奖也经同一 callback 分发。
- 完工只设置 completed、国家完成 flag 和 completion_queued；每日队列最多安排一个可见事件。事件选项经 reward_claimed 数组保证一次性发奖。
- 发奖无 pending 状态、无控制权检查、无 on_state_control_changed、无强制 set_power_balance。
- 资金与人力影响实际周进度；所有在建项目的持续成本、生产单位占用和人力社会动员效果汇总到三个动态修正。未开工或已完工项目不计施工负担。
- v8 迁移保存旧存档的进度、资金、人力、完成、显示、开工、当前选择和周计数；旧的第 7–9 地区展开状态合并到新广西地区。

## 铁路静态核对

连续性以当前 TNO map/railways.txt 的相邻边为准；州归属以当前 TNO history/states 为准。

| 路径 | 省份序列 | 州/初始归属 | 结果 |
|---:|---|---|---|
| 1 | 10062–7108–19574–4050–7067–9978–9938 | 香港 GNG → 潮州 GNG | 连续 |
| 2 | 4189–8802–1047–7152 | 澳门/茂名/广州，均 GNG | 连续 |
| 3 | 7152–11938–9963–7039–10105–11981 | 茂名 GNG → 湛江 GUX | 连续；只进入项目目标湛江 |
| 4 | 10062–7108–1047–8802–4189 | 香港/潮州/广州/茂名/澳门，均 GNG | 连续 |
| 5 | 9938–9978–7067–4050–4207–4165–7182 | 潮州 GNG | 连续 |

## 图像验收

- 20 张指定 JPG 均存在且可用，因此没有调用生成式图像，也没有使用旧 frame 或旧最终 strip。
- 每张成品独立裁切至 182×423，采用低亮度、低饱和、高对比、明显冷蓝双色调与轻扫描线；描边严格沿用科学院既有项目图的 2px、RGB(89, 199, 194) 青绿色框体，无暗角、无左侧压暗、无投影。
- 20 个 DDS 均沿用科学院参考图的未压缩 32-bit RGBA 格式，header 为 182×423、depth 0、mipmap count 0；因此 2px 描边不会因 DXT 色块与画面混合而变色或断裂，并各自注册独立 GFX sprite。
- 逐项原图/成品/token/sprite 映射见 DOP_construction_image_map.md；目视联系表见 DOP_construction_contact_sheet.png。

## 平衡与剩余边界

- 除政治点外，施工动员和安全可放大的完工数值统一提高至原来的 2 倍；社会发展、腐败、州好感、州 GDP 与永久经济收益均由自动检查锁定新总量，铁路和建筑硬上限不做机械翻倍。
- 奖励逐项依据、目标州、累计永久收益、SocDev 合计、腐败/满意度边界及滑杆极值见 DOP_construction_reward_and_slider_audit.md。
- 离线布局图 DOP_construction_gui_layout.png 用于坐标和重叠检查；简介与效果页在图中重叠是互斥可见性的设计结果。
- 唯一未执行的验收层是游戏内交互和旧存档实载，因为任务明确要求不启动游戏。
