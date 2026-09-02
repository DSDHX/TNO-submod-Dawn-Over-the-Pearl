#!/usr/bin/env python3
"""Verify the bilingual poem is bound to the upper-right version-logo tooltip."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
GUI = ROOT / "interface" / "frontendmainview.gui"
MENU_LOC = ROOT / "localisation" / "simp_chinese" / "DOP_menu_tooltips_l_simp_chinese.yml"
VERSION_LOC = ROOT / "localisation" / "simp_chinese" / "DOP_version_l_simp_chinese.yml"

gui = GUI.read_text(encoding="utf-8-sig")
logo = re.search(
    r'iconType = \{\s*name ="frontend_tno_logo"(?P<body>.*?)\n\s*\}',
    gui,
    re.DOTALL,
)
if logo is None or "pdx_tooltip_delayed = TNO_dop_icon_tt_delayed" not in logo.group("body"):
    raise SystemExit("upper-right version logo is not bound to TNO_dop_icon_tt_delayed")

data = MENU_LOC.read_bytes()
if not data.startswith(b"\xef\xbb\xbf"):
    raise SystemExit("menu tooltip localisation is missing UTF-8 BOM")
source = data.decode("utf-8-sig")
match = re.search(r'^ TNO_dop_icon_tt_delayed: "(?P<value>.*)"$', source, re.MULTILINE)
if match is None:
    raise SystemExit("TNO_dop_icon_tt_delayed localisation is missing")

expected = "§F灯りともる 窓の中では 帰りびとが笑う\\n华灯初上的车窗里头净是　归人的笑语\\nふるさとは 走り続けた ホームの果て\\n故乡就在我不断追赶的月台那头\\n叩き続けた 窓ガラスの果て\\n就在我不断拍打的车窗那头\\nそして 手のひらに残るのは\\n然而此刻　留存在手心中的只有\\n白い煙と乗車券\\n白色的烟尘和一张车票\\n涙の数 ため息の数\\n泪水的数量　叹息的次数\\n溜ってゆく空色のキップ\\n等同那些始终没能搭上　愈积愈多的天蓝色车票\\nネオンライトでは 燃やせない\\n然而都会霓虹灯无法烧毁的\\nふるさと行きの乗車券\\n正是这张开往故乡的车票§!"
if match.group("value") != expected:
    raise SystemExit("version-logo delayed tooltip does not match the approved simplified bilingual text")
if "&#x20;" in source:
    raise SystemExit("HTML spacing entity remains in menu tooltip localisation")

version_source = VERSION_LOC.read_text(encoding="utf-8-sig")
if "灯りともる" in version_source:
    raise SystemExit("poem was incorrectly written into the bottom version/date tooltip")

print("homepage version-logo delayed tooltip: binding, simplified bilingual text and target isolation PASS")
