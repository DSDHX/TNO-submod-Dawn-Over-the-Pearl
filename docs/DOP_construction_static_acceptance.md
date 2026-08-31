# 南粤建设系统：静态验收报告

验收日期：2026-08-31  
当前工作树基线：`6cd72a6c930b65ab173e1e4c21e95b4c16e3e8c0`  
目标版本：`260828C`  
TNO静态参考：`D:\Steam\steamapps\workshop\content\394360\2438003901`

## 结论

建设系统静态验收通过。本轮没有启动Hearts of Iron IV，也没有处理“三微米冷战”、SCW、科学院、dummy刷新或无关BOP生命周期。因此本报告证明当前文件的生成一致性、脚本结构、GUI结构、铁路路径、奖励接口、图片映射和资源格式，不宣称完成游戏内点击或旧存档实载测试。

## 自动检查

| 检查 | 结果 |
|---|---|
| `python -B tools/check_dop_construction.py` | PASS：6地区、20项目、奖励、滑条、20事件、v8、队列、铁路、20原图、5清理图、20独立DDS与GUI关键结构全部通过 |
| `python -B tools/generate_dop_construction.py --check` | PASS：生成注册表、本地化、事件、奖励、GFX和文档均为最新 |
| `hoi4-modding check_script.py` | PASS：8个建设脚本，0错误 |
| `hoi4-gui-modding check_gui_script.py` | PASS：2个GUI文件，0错误、0警告 |
| `hoi4-gui-modding render_gui_layout.py` | PASS：离线布局图已生成 |
| `git diff --check` | PASS；仅报告工作树既有CRLF提示，无空白错误 |

## 项目与GUI

- 项目数据由 `tools/generate_dop_construction.py` 中唯一一份 `PROJECTS`/`REWARDS` 注册表维护；ID 1–16保留，ID 17–20追加。
- 左侧目录继续由 `DOP_construction_directory_items` 动态生成，六个区域仍通过 `DOP_construction_toggle_directory_region` 展开和收起。
- 工程目标、当前进度、基础速度、实际速度和两个投入倍率继续通过 `DOP_construction_selected_numbers` 直接显示，不依赖悬浮提示。
- 用户提供的白鹅新区晴空塔、玫瑰园计划、粤海爱丽丝梦工厂、大亚湾核电站、广东新干线、珠三角磁悬浮及广西高速公路网正文均写入对应项目简介，没有进入完工事件或奖励文本。
- 简介区保持280×150可见窗口，并新增500px内容滚动区；最长简介为白鹅新区晴空塔239字符，可完整滚动阅读。
- 简介和效果没有两个并排切换按钮。点击简介后显示同位置效果覆盖页，`effect_tooltip`预览的正是完工事件调用的实际奖励回调；点击覆盖页返回简介。

## 奖励、滑条与事件

- 20个项目均同时具有按工程性质设计的地区设施、社会发展和GNG特色收益；完整逐项依据及累计强度见 `DOP_construction_reward_and_slider_audit.md`。
- 奖励中不存在 `industrial_complex`、未控制州pending、控制权补发、`on_state_control_changed`或强制 `set_power_balance`。
- 三个铁路项目共定义5条真实 `build_railway` 路径；所有相邻省份边均存在于当前TNO铁路图，并保持在GNG/GUX目标地区内。
- 资金滑条聚合杂项支出、TNO特殊项目生产单位占用和施工速度；项目停工或完成后不再计费。
- 人力滑条不触及适役人口、征兵人口、人口池或补员；其全国影响由统一动态修正聚合并带有上下限，不能靠反复切换刷永久收益。
- 项目达标只排入完成队列；每日最多弹出一个事件，唯一选项调用奖励回调，`reward_claimed`数组阻止重复领取。
- v8迁移保留进度、完成状态、选择、显示、开工状态、资金、人力与旧广西展开状态；不包含目标州控制权补发逻辑。

## 图片

- 20张现实原图已按最终视觉复核后的Commons来源恢复；来源页、作者和许可见 `DOP_construction_image_sources.md`。
- ID 6、7、8、12、17仅用内置imagegen清除院校名、水库题字、制造商logo、门牌和上海磁悬浮标识；原图与清理版分开保存，完整提示词见 `DOP_construction_image_cleanup_prompts.md`。
- 最终成品全部从现实原图或对应清理版重新等比裁切，不使用旧预览图、旧帧、旧条带或非等比拉伸。
- 20个DDS均为独立285×551、未压缩32-bit RGBA纹理；2px `#59C7C2`青色描边在最终尺寸后烧入。
- 图片左侧没有压暗、阴影、渐变或衔接色块。
- GUI图片锚点为局部坐标x=755、y=67，285×551纹理正好覆盖右分隔线之后至1040×618窗口边界。
- 20项项目ID、现实原图、DDS、动态token和sprite映射见 `DOP_construction_image_map.md`；最终视觉接触表为 `DOP_construction_contact_sheet.png`。

## 仍需用户游戏内验证

- 打开相应游戏页面后，六个目录的实际点击展开、滚轮和长简介滚动手感。
- 立法会式效果覆盖的点击切换和动态tooltip内容。
- 20张图片在实际缩放与两档分辨率下是否完全贴合右栏。
- 资金、人力持续修正的实时经济界面表现及项目完成后的释放。
- 多事件完成队列的每日弹出顺序、一次性领奖和v8旧存档实载。
- 补给地图中的5条铁路实际连线显示。

以上项目必须由用户按既定游戏内测试前提验证；本轮按要求没有启动游戏。
