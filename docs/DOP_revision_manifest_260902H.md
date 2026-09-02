# DOP 260902H：实机援军与国策树修复

构建号：EARLY DEVELOPMENT BUILD 260902H

- 根据 error.log 的 Not allowed on enemy provinces，将六个 JAP 装甲师从广州改到 JAP 自有的高雄州生成。
- YUN 战前设置 YUN_long_yun_crusade flag，并载入 YUN_long_yun_crusade_tree。
- 在本地 TNO_Yunnan 覆盖中阻断 yun_wi.15，防止护国军树重新启动原版战争。
- 战后清除护国军 flag，并把 YUN 切回 YUN_post_xinan。
- GUX 获释后显式载入 TNO 自带空树 ZZZ_blank_focus，不再保留或继承 GNG 国策树。
