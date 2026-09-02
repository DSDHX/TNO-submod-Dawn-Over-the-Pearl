# DOP 260902D 首页版本图标悬浮文本增量清单

构建号：`EARLY DEVELOPMENT BUILD 260902D`  
日期：2026-09-02

## 改动

- 替换右上角 `frontend_tno_logo` 版本图标的延迟悬浮文本：`TNO_dop_icon_tt_delayed`。
- 保留全部日文原句。
- 对应中文由繁体转换为简体，并保持日中逐行对照。
- 删除输入末尾的 `&#x20;` HTML 空格实体。
- 保留短提示 `TNO_dop_icon_tt`（“月台羁留”）。
- 未修改底部 `dop_current_version` 和 `dop_current_version_date` 的文本内容；其中仅构建号按规范更新为 260902D。
- 未修改 `interface/frontendmainview.gui` 的当前布局或版本图标位置。
- 未修改作者手动维护的产品周期与核心接棒 tooltip。

## 验收

- `python tools/check_dop_homepage_icon_poem.py`：图标绑定、目标隔离及批准文本完全匹配。
- `python tools/run_dop_revision_check_quiet.py`：1685 条综合断言通过。
- `python tools/check_dop_content_flow.py`：主流程回归通过。
- `python tools/check_dop_flow_debug_decisions.py`：17 个流程调试节点通过。

游戏内显示由作者自行验证。
