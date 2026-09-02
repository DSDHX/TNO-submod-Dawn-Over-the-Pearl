from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EFFECTS_PATH = ROOT / "common/scripted_effects/DOP_construction_effects.txt"
EVENTS_PATH = ROOT / "events/DOP_GNG_construction.txt"
LOC_PATH = ROOT / "localisation/simp_chinese/DOP_Construction_l_simp_chinese.yml"
TOKENS_PATH = ROOT / "common/synchronized_dynamic_tokens/DOP_construction_tokens.txt"
SCRIPTED_LOC_PATH = ROOT / "common/scripted_localisation/DOP_Construction_Scripted_loc.txt"
REWARDS_PATH = ROOT / "common/scripted_effects/DOP_construction_rewards.txt"
GFX_PATH = ROOT / "interface/GUI/DOP_construction.gfx"
AUDIT_PATH = ROOT / "docs/DOP_construction_reward_and_slider_audit.md"
IMAGE_MAP_PATH = ROOT / "docs/DOP_construction_image_map.md"

REGISTRY_BEGIN = "# BEGIN GENERATED CONSTRUCTION REGISTRY"
REGISTRY_END = "# END GENERATED CONSTRUCTION REGISTRY"
LOC_BEGIN = "# BEGIN GENERATED CONSTRUCTION LOCALISATION"
LOC_END = "# END GENERATED CONSTRUCTION LOCALISATION"
TOKENS_BEGIN = "# BEGIN GENERATED CONSTRUCTION TOKENS"
TOKENS_END = "# END GENERATED CONSTRUCTION TOKENS"
EVENT_DISPATCH_BEGIN = "# BEGIN GENERATED CONSTRUCTION EVENT DISPATCH"
EVENT_DISPATCH_END = "# END GENERATED CONSTRUCTION EVENT DISPATCH"
DIRECTORY_BEGIN = "# BEGIN GENERATED CONSTRUCTION DIRECTORY"
DIRECTORY_END = "# END GENERATED CONSTRUCTION DIRECTORY"
DIRECTORY_TOGGLE_BEGIN = "# BEGIN GENERATED CONSTRUCTION DIRECTORY TOGGLES"
DIRECTORY_TOGGLE_END = "# END GENERATED CONSTRUCTION DIRECTORY TOGGLES"
CLEAR_FLAGS_BEGIN = "# BEGIN GENERATED CONSTRUCTION CLEAR FLAGS"
CLEAR_FLAGS_END = "# END GENERATED CONSTRUCTION CLEAR FLAGS"
CLEAR_EXPANSION_BEGIN = "# BEGIN GENERATED CONSTRUCTION CLEAR EXPANSION FLAGS"
CLEAR_EXPANSION_END = "# END GENERATED CONSTRUCTION CLEAR EXPANSION FLAGS"
STATE_DISPATCH_BEGIN = "# BEGIN GENERATED CONSTRUCTION STATE DISPATCH"
STATE_DISPATCH_END = "# END GENERATED CONSTRUCTION STATE DISPATCH"
CLEAR_STATE_BEGIN = "# BEGIN GENERATED CONSTRUCTION CLEAR STATE FLAGS"
CLEAR_STATE_END = "# END GENERATED CONSTRUCTION CLEAR STATE FLAGS"
SELECT_FIRST_BEGIN = "# BEGIN GENERATED CONSTRUCTION SELECT FIRST SHOWN"
SELECT_FIRST_END = "# END GENERATED CONSTRUCTION SELECT FIRST SHOWN"
SCRIPTED_LOC_BEGIN = "# BEGIN GENERATED CONSTRUCTION DIRECTORY LOCALISATION"
SCRIPTED_LOC_END = "# END GENERATED CONSTRUCTION DIRECTORY LOCALISATION"
CALLBACK_END = "# END GENERATED COMPLETION CALLBACKS"
CALLBACK_BEGIN = "# BEGIN GENERATED COMPLETION CALLBACKS"
SLIDER_RUNTIME_BEGIN = "# BEGIN GENERATED CONSTRUCTION SLIDER RUNTIME"
SLIDER_RUNTIME_END = "# END GENERATED CONSTRUCTION SLIDER RUNTIME"
GFX_BEGIN = "# BEGIN GENERATED CONSTRUCTION PROJECT SPRITES"
GFX_END = "# END GENERATED CONSTRUCTION PROJECT SPRITES"


@dataclass(frozen=True)
class Region:
    id: int
    slug: str
    name: str


@dataclass(frozen=True)
class Project:
    id: int
    slug: str
    region: str
    total: int
    name: str
    desc: str
    source: str
    event_id: int | None = None

    @property
    def completion_event_id(self) -> int:
        return self.id if self.event_id is None else self.event_id

    @property
    def image(self) -> str:
        return f"DOP_construction_project_{self.id:02d}"


# IDs are save-game data. Append new IDs; never reuse or reorder released IDs.
REGIONS = (
    Region(1, "prd", "珠三角"),
    Region(2, "chaoshan", "粤东"),
    Region(3, "northern_guangdong", "粤北"),
    Region(4, "western_guangdong", "粤西"),
    Region(5, "jiaoyang", "交洋"),
    Region(6, "guangxi", "广西"),
)

PROJECTS = (
    Project(1, "sky_tower", "prd", 150000, "白鹅新区晴空塔", "广州是一座老城，老到最早的建筑在南海之畔建起时，如今人们耳熟能详的二沙岛，海珠区与番禺都尚且还是珠江上游的泥沙。它在几百年间都依水而建，顺江而修，迄今为止的所有城市规划都不过是在前人所留下的弊病上做小修小补罢了。\\n\\n如今，去做前无古人的大功业的责任就交到了我们的身上，我们在广佛交界的白鹅潭规划了一块名称待定的新区，在珠江北岸，一座新城将会拔地而起，国家博物馆，图书馆或是大剧院之类的文体设施将会簇拥着比东京所拥有的还要更加高大的晴空塔，让这座城市骄傲地屹立于三角洲的中心。", "01_sky_tower.jpg"),
    Project(2, "rose_garden", "prd", 100000, "玫瑰园计划", "香港的旧机场建得实在太早，以现代的视角审视处处都是弊病。选址太靠近市区，跑道太短，航站楼太小——要是让井深放开了骂，他能说上三天三夜。\\n\\n也正是因为如此，玫瑰园计划应运而生，我们拟在赤鱲角修建一个新的机场，并且配上所需要的交通设施，开通新的机场快线，跨海大桥，跨海隧道，诸如此类。这会是一项很大的建设工程，但我们相信，香港必须要延展它的边界才能得到一个崭新的未来。", "02_rose_garden.jpg"),
    Project(3, "alice_dream_factory", "prd", 30000, "粤海爱丽丝梦工厂", "澳门，创收之地，梦之地，它以小小几十平方米的面积为广东创造了无数活跃的现金流。在广港两地都在扩张的如今，作为珠三角的一份子，无数旅馆，红灯区以及滨海度假村沿着澳门半岛向北一路扩张，将曾经被称为香洲的地方也一并囊括入澳门，建设成了世界闻名的文旅城市。\\n\\n也正因如此，在这个人来人往，合贯东西的港口，我们有志于在淇澳岛上建成一座世界上最快乐的游乐园，它将欢迎世界上的所有人——与他们的假期和金钱。", "03_alice_dream_factory.jpg"),
    Project(4, "daya_bay_nuclear_plant", "prd", 45000, "大亚湾核电站", "珠三角的繁荣需要燃料浇筑，这里并不是指人才，金融资本，或者任何足以投机的风口。字面意思地，珠三角作为灯火通明的都市圈，每天所消耗的能源都是一个天文数字。而要是想要真正地走向独立自主，我们就必须有能力高效率地支撑起我们的能源缺口。\\n\\n在经过无数审批与灰色、黑色交易后，我们得到了在监督下建设商用核电站的机会。我们将核电基地选址于珠三角再向东几十公里的湾区内，使发电量的80%能方便地接入广港澳的高功率电网中。", "04_daya_bay_nuclear_plant.jpg"),
    Project(5, "guangdong_shinkansen", "prd", 90000, "广东新干线计划", "广东新干线将主要分为两段修建，旨在实现广东的沿岸地区与珠三角的快速互联。在最先修建的港汕线立项之初，以李嘉诚为首的诸多潮商的橄榄枝就伸了过来，表达出投资的意向，试图以此操纵新干线站点的选址，好实现自己的利益最大化。\\n\\n与之相比，连接粤西的澳湛线便稍微受人冷落了些，不过好在这一侧沿海平原比粤东更多些，修起来也不需要凿山开路，只需要与石油托拉斯做些适当的利益交换，路线规划就基本不会遇到什么难题。", "05_guangdong_shinkansen.jpg"),
    Project(6, "chaoshan_university", "chaoshan", 30000, "潮汕大学", "建设服务粤东地区的综合性大学。", "06_chaoshan_university.jpg"),
    Project(7, "xinfengjiang_reservoir", "northern_guangdong", 60000, "山区水库开发计划", "统筹粤北山区的水库、水利与水力发电设施。", "07_mountain_reservoirs.jpg"),
    Project(8, "luoding_granary", "western_guangdong", 40000, "粤西盆地储粮工程", "推动罗定盆地农业集中化、机械化与区域储粮体系建设。", "08_western_guangdong_granary.jpg"),
    Project(9, "pinglu_canal", "jiaoyang", 100000, "平陆运河", "贯通内河与北部湾航运体系的运河工程。", "09_pinglu_canal.jpg"),
    Project(10, "south_china_sea_drilling_platform", "jiaoyang", 30000, "南海油气开采", "建设面向南海油气资源的海上勘探与开采平台。", "10_south_china_sea_oil.jpg"),
    Project(11, "wenchang_space_center", "jiaoyang", 50000, "文昌卫星发射中心", "在文昌建设卫星发射场及配套测控设施。", "11_wenchang_space_center.jpg"),
    Project(12, "guangxi_industrial_institute", "guangxi", 60000, "重整广西实业院", "将桂柳一带的工业资源与机构逐步迁往南宁。", "12_guangxi_industrial_institute.jpg"),
    Project(13, "guangxi_expressway_network", "guangxi", 90000, "广西高速公路网", "广西被民族主义军阀占据太久，即使是在当下，层出不穷的军阀残部与山贼土匪仍然盘踞在包绕广西的群峦中。为了加快我们对广西的基层控制，便于广西的发展，新的路网规划迫在眉睫。 在这一计划中，最为关键的横纵两条干线分别为柳州-来宾-南宁-钦州以及南宁-贵港-梧州-肇庆一线，在确保了我们的人员与物资都能快速在桂中桂南的平原上流通之后，对于广西剩余地区的整合才能真正开始。", "13_guangxi_expressway.jpg"),
    Project(14, "nanyue_folk_memorial_park", "guangxi", 30000, "“南粤之心”民俗纪念园", "以南粤共同传统为主题建设民俗纪念园，缓和地方认同矛盾。", "14_nanyue_folk_park.jpg"),
    Project(15, "lijiang_waterway", "guangxi", 30000, "漓江航道开发工程", "改善漓江航道条件，加强桂柳与沿岸地区的沟通和商贸。", "15_lijiang_waterway.jpg"),
    Project(16, "honghe_fan_asia_friendship_pass", "guangxi", 30000, "红河泛亚友谊关", "强化友谊关面向红河—湄公河与印支半岛的交通和边贸联系。", "16_friendship_pass.jpg"),
    Project(17, "prd_maglev", "prd", 90000, "珠三角磁悬浮城轨", "随着珠三角三城及其中间地带的蓬勃发展，跨市通勤的事情越来越常见，有一些城区甚至成为了被住宅区所填满的“睡城”，为了实现更加便利的通勤，在井深大的建议下，我们实验性地搭建了两条磁悬浮轨道，贯通珠三角的东西两岸，一小时内从广州到达香港从此以后将不再是工作到半夜之后的一句牢骚。", "17_prd_maglev.jpg"),
    Project(18, "shantou_chaozhou_jieyang_integration", "chaoshan", 60000, "汕潮揭一体化方案", "以机场扩建和城际铁路推动汕头、潮州、揭阳一体化。", "18_shantou_integration.jpg"),
    Project(19, "granite_uranium_mining", "northern_guangdong", 60000, "开采花岗岩型铀矿", "勘探并开发粤北花岗岩型铀矿床。", "19_granite_uranium_mining.jpg"),
    Project(20, "shale_oil_refineries", "western_guangdong", 30000, "拓展页岩油化工厂", "扩建粤西页岩油炼化设施与配套输送流水线。", "20_shale_oil_refineries.jpg"),
)


@dataclass(frozen=True)
class Reward:
    regional: str
    social: str
    gng: str
    references: str
    targets: str
    strength: str
    risk: str
    effect: tuple[str, ...]

NON_PP_REWARD_MULTIPLIER = Decimal("2")
SOCIAL_DEVELOPMENT_EFFECT = re.compile(
    r"^(?P<indent>\s*)TNO_improve_(?P<area>academic_base|research_facilities|"
    r"agriculture|admin_efficiency|industrial_equipment|industrial_expertise|"
    r"poverty)_(?P<tier>really_low|low|med|high)\s*=\s*yes\s*$"
)
SCALED_TEMP_VALUE = re.compile(
    r"(set_temp_variable\s*=\s*\{\s*(?:GNG_corruption_temp_var|"
    r"chi_app_temp|zhu_app_temp|jap_app_temp)\s*=\s*)"
    r"(-?\d+(?:\.\d+)?)(\s*\})"
)
SCALED_REWARD_VARIABLE = re.compile(
    r"(add_to_variable\s*=\s*\{\s*(?:DOP_construction_reward_misc_income|"
    r"DOP_construction_reward_free_pu|DOP_construction_reward_research_speed|"
    r"DOP_construction_reward_trade_opinion|"
    r"DOP_construction_reward_resource_factor)\s*=\s*)"
    r"(-?\d+(?:\.\d+)?)(\s*\})"
)
SCALED_STATE_GDP = re.compile(
    r"(set_temp_variable\s*=\s*\{\s*state_value_multiplier_temp\s*=\s*)"
    r"(\d+(?:\.\d+)?)(\s*\})"
)
SCALED_RESOURCE = re.compile(
    r"(add_resource\s*=\s*\{\s*type\s*=\s*\w+\s+amount\s*=\s*)"
    r"(-?\d+(?:\.\d+)?)(\s*\})"
)
PERSISTENT_REWARD_EFFECT = re.compile(
    r"^(?P<indent>\s*)add_to_variable\s*=\s*\{\s*"
    r"(?P<variable>DOP_construction_reward_(?:misc_income|free_pu|"
    r"research_speed|trade_opinion|resource_factor))\s*=\s*"
    r"(?P<value>-?\d+(?:\.\d+)?)\s*\}\s*$"
)
PERSISTENT_REWARD_COMPONENTS = {
    "DOP_construction_reward_misc_income": (
        "misc_income_temp",
        "DOP_construction_add_misc_income_reward",
    ),
    "DOP_construction_reward_free_pu": (
        "pus_temp",
        "DOP_construction_add_free_pu_reward",
    ),
    "DOP_construction_reward_research_speed": (
        "DOP_construction_reward_component_value",
        "DOP_construction_add_research_speed_reward",
    ),
    "DOP_construction_reward_resource_factor": (
        "DOP_construction_reward_component_value",
        "DOP_construction_add_resource_factor_reward",
    ),
    "DOP_construction_reward_trade_opinion": (
        "DOP_construction_reward_component_value",
        "DOP_construction_add_trade_opinion_reward",
    ),
}


def scaled_number(raw: str) -> str:
    value = Decimal(raw) * NON_PP_REWARD_MULTIPLIER
    return format(value.normalize(), "f")


def scaled_state_gdp(raw: str) -> str:
    value = Decimal("1") + (
        Decimal(raw) - Decimal("1")
    ) * NON_PP_REWARD_MULTIPLIER
    return format(value.normalize(), "f")


def amplify_non_pp_reward_script(script: str) -> tuple[str, ...]:
    """Double safe numeric completion rewards while leaving PP untouched."""
    amplified: list[str] = []
    for raw_line in script.strip().splitlines():
        line = raw_line.rstrip()
        social_match = SOCIAL_DEVELOPMENT_EFFECT.fullmatch(line)
        if social_match:
            indent = social_match.group("indent")
            area = social_match.group("area")
            tier = social_match.group("tier")
            doubled_tiers = {
                "really_low": ("low",),
                "low": ("med",),
                "med": ("high", "low"),
                "high": ("high", "high"),
            }[tier]
            amplified.extend(
                f"{indent}TNO_improve_{area}_{doubled_tier} = yes"
                for doubled_tier in doubled_tiers
            )
            continue
        line = SCALED_TEMP_VALUE.sub(
            lambda match: match.group(1)
            + scaled_number(match.group(2))
            + match.group(3),
            line,
        )
        line = SCALED_REWARD_VARIABLE.sub(
            lambda match: match.group(1)
            + scaled_number(match.group(2))
            + match.group(3),
            line,
        )
        line = SCALED_STATE_GDP.sub(
            lambda match: match.group(1)
            + scaled_state_gdp(match.group(2))
            + match.group(3),
            line,
        )
        line = SCALED_RESOURCE.sub(
            lambda match: match.group(1)
            + scaled_number(match.group(2))
            + match.group(3),
            line,
        )
        amplified.append(line)
    return tuple(amplified)


def canonical_tno_cn(value: str) -> str:
    """Use the official TNO Chinese terms in generated audit prose."""
    replacements = (
        ("学术基础", "教育水平"),
        ("竹人", "珠人"),
        ("日本人", "日侨"),
        ("满意度", "政府支持率"),
        ("资源开采效率", "战略资源获取效率"),
        ("贸易关系评价", "贸易协定关系修正"),
        ("两次极小幅", "小幅"),
        ("两次小幅", "中等"),
        ("两次中等", "大幅与小幅"),
    )
    for old, new in replacements:
        value = value.replace(old, new)
    return value


def reward(
    regional: str,
    social: str,
    gng: str,
    references: str,
    targets: str,
    strength: str,
    risk: str,
    script: str,
) -> Reward:
    return Reward(
        canonical_tno_cn(regional),
        canonical_tno_cn(social),
        canonical_tno_cn(gng),
        canonical_tno_cn(references),
        canonical_tno_cn(targets),
        canonical_tno_cn(strength),
        canonical_tno_cn(risk),
        amplify_non_pp_reward_script(script),
    )


# Reward data lives beside the project registry. Scripts below remain expressed
# at TNO's native effect scale; reward() applies the explicit 2x non-PP policy
# before rendering. Physical buildings/rail levels are not multiplied because
# several already sit at engine caps. The displayed and paid effects still come
# from this one structure, so they cannot drift.
REWARDS: dict[int, Reward] = {}

# Four author-specified projects each contribute one point to the late-game
# Ibuka route score.  These flags are intentionally independent from the
# generic reward_claimed array so save inspection and regression tests can
# identify the exact source of every point.
IBUKA_POINT_FLAGS = {
    4: "DOP_construction_daya_bay_ibuka_scored",
    11: "DOP_construction_wenchang_ibuka_scored",
    17: "DOP_construction_prd_maglev_ibuka_scored",
    19: "DOP_construction_granite_uranium_ibuka_scored",
}

REWARDS.update({
    1: reward(
        "广州获得 2 级基础设施、3 个建筑槽位与 12% 州 GDP。",
        "行政效率获得两次中等改善。",
        "腐败降低 6；永久增加 2 个生产单位与 0.40B 杂项收入；广州华人/竹人满意度 +4/+2。",
        "TNO_SocDev_scripted_effects；TNO_Guangdong_scripted_effects；中国州开发接口",
        "广州（592）",
        "150k 旗舰项目；州收益高，全国收益中等",
        "生产单位与收入受全项目累计审计；腐败由 TNO clamp，好感由州级 helper 结算",
        """TNO_improve_admin_efficiency_med = yes
set_temp_variable = { GNG_corruption_temp_var = -3 }
GNG_Corruption_Change = yes
add_to_variable = { DOP_construction_reward_misc_income = 0.20 }
add_to_variable = { DOP_construction_reward_free_pu = 1 }
592 = {
\tadd_extra_state_shared_building_slots = 3
\tadd_building_construction = { type = infrastructure level = 2 instant_build = yes }
\tset_temp_variable = { state_value_multiplier_temp = 1.06 }
\tecon_state_value_change_multiply_specified_state = yes
\tset_temp_variable = { chi_app_temp = 2 }
\tGNG_chinese_app_change = yes
\tset_temp_variable = { zhu_app_temp = 1 }
\tGNG_zhujin_app_change = yes
}""",
    ),
    2: reward(
        "香港基础设施至少 8 级、空军基地至少 9 级、指定港口 10 级；增加海军补给枢纽、3 个槽位与 10% 州 GDP。",
        "行政效率获得两次小幅改善。",
        "永久增加 0.30B 杂项收入；香港日本人/竹人/华人满意度 +4/+4/+2。",
        "TNO_SocDev_scripted_effects；TNO_Guangdong_scripted_effects；TNO 建筑定义",
        "香港（326），港口省份 10062",
        "100k 大型综合交通项目",
        "建筑使用至少值避免超限；好感由州级 helper 结算",
        """TNO_improve_admin_efficiency_low = yes
add_to_variable = { DOP_construction_reward_misc_income = 0.15 }
326 = {
\tadd_extra_state_shared_building_slots = 3
\tif = { limit = { infrastructure < 8 } set_building_level = { type = infrastructure level = 8 instant_build = yes } }
\tif = { limit = { air_base < 9 } set_building_level = { type = air_base level = 9 instant_build = yes } }
\tif = { limit = { naval_base < 10 } set_building_level = { type = naval_base province = 10062 level = 10 instant_build = yes } }
\tadd_building_construction = { type = naval_supply_hub province = 10062 level = 1 instant_build = yes }
\tset_temp_variable = { state_value_multiplier_temp = 1.05 }
\tecon_state_value_change_multiply_specified_state = yes
\tset_temp_variable = { jap_app_temp = 2 }
\tGNG_japanese_app_change = yes
\tset_temp_variable = { zhu_app_temp = 2 }
\tGNG_zhujin_app_change = yes
\tset_temp_variable = { chi_app_temp = 1 }
\tGNG_chinese_app_change = yes
}""",
    ),
})

REWARDS.update({
    3: reward(
        "澳门获得 1 级空军基地、1 个建筑槽位与 6% 州 GDP。",
        "贫困获得两次小幅改善。",
        "永久增加 0.24B 杂项收入；澳门华人/竹人/日本人满意度 +6/+4/+2。",
        "TNO_economy_frontend_scripted_effects；TNO_Guangdong_scripted_effects",
        "澳门（729）",
        "30k 文化消费项目；州收益与小额长期收入并重",
        "好感限定单州并由 TNO helper 结算",
        """TNO_improve_poverty_low = yes
add_to_variable = { DOP_construction_reward_misc_income = 0.12 }
729 = {
\tadd_extra_state_shared_building_slots = 1
\tadd_building_construction = { type = air_base level = 1 instant_build = yes }
\tset_temp_variable = { state_value_multiplier_temp = 1.03 }
\tecon_state_value_change_multiply_specified_state = yes
\tset_temp_variable = { chi_app_temp = 3 }
\tGNG_chinese_app_change = yes
\tset_temp_variable = { zhu_app_temp = 2 }
\tGNG_zhujin_app_change = yes
\tset_temp_variable = { jap_app_temp = 1 }
\tGNG_japanese_app_change = yes
}""",
    ),
    4: reward(
        "惠州获得 1 座核反应堆与 1 级基础设施。",
        "研究设施、工业设备各获得两次小幅改善。",
        "惠州日本人/竹人满意度 +4/+2，体现技术资本与本地技术人员合作。",
        "TNO_SocDev_scripted_effects；TNO 00_buildings；TNO_Guangdong_scripted_effects",
        "惠州（959）",
        "45k 特殊能源设施；实体建筑为主体",
        "不额外堆全国 GDP；好感由州级 helper 结算",
        """TNO_improve_research_facilities_low = yes
TNO_improve_industrial_equipment_low = yes
959 = {
\tadd_building_construction = { type = nuclear_reactor level = 1 instant_build = yes }
\tadd_building_construction = { type = infrastructure level = 1 instant_build = yes }
\tset_temp_variable = { jap_app_temp = 2 }
\tGNG_japanese_app_change = yes
\tset_temp_variable = { zhu_app_temp = 1 }
\tGNG_zhujin_app_change = yes
}""",
    ),
})

REWARDS.update({
    5: reward(
        "建成 4 级港汕高铁与澳湛高铁；香港、潮州、澳门、茂名、湛江获得沿线基础设施与 4% 州 GDP 配套。",
        "行政效率、工业设备各获得两次小幅改善。",
        "香港日本人/竹人满意度 +2/+2，广州华人满意度 +4。",
        "TNO 巴西/伊比利亚 build_railway；TNO_SocDev；TNO_Guangdong",
        "326/592/593/729/1017/1464；铁路省份见三段 path",
        "90k 跨区域骨干铁路；真实 4 级铁路为主体",
        "三段路径须连续且不得跨越错误国家；社会发展按双倍 low 档结算",
        """TNO_improve_admin_efficiency_low = yes
TNO_improve_industrial_equipment_low = yes
build_railway = {
\tlevel = 4
\tpath = { 10062 7108 19574 4050 7067 9978 9938 }
\tstart_province = 10062
\ttarget_province = 9938
}
build_railway = {
\tlevel = 4
\tpath = { 4189 8802 1047 7152 }
\tstart_province = 4189
\ttarget_province = 7152
}
build_railway = {
\tlevel = 4
\tpath = { 7152 11938 9963 7039 10105 11981 }
\tstart_province = 7152
\ttarget_province = 11981
}
326 = {
\tset_temp_variable = { state_value_multiplier_temp = 1.02 }
\tecon_state_value_change_multiply_specified_state = yes
\tset_temp_variable = { jap_app_temp = 1 }
\tGNG_japanese_app_change = yes
\tset_temp_variable = { zhu_app_temp = 1 }
\tGNG_zhujin_app_change = yes
}
592 = {
\tset_temp_variable = { chi_app_temp = 2 }
\tGNG_chinese_app_change = yes
}
593 = {
\tadd_building_construction = { type = infrastructure level = 1 instant_build = yes }
\tset_temp_variable = { state_value_multiplier_temp = 1.02 }
\tecon_state_value_change_multiply_specified_state = yes
}
729 = { set_temp_variable = { state_value_multiplier_temp = 1.02 } econ_state_value_change_multiply_specified_state = yes }
1017 = { add_building_construction = { type = infrastructure level = 1 instant_build = yes } set_temp_variable = { state_value_multiplier_temp = 1.02 } econ_state_value_change_multiply_specified_state = yes }
1464 = { add_building_construction = { type = infrastructure level = 1 instant_build = yes } set_temp_variable = { state_value_multiplier_temp = 1.02 } econ_state_value_change_multiply_specified_state = yes }""",
    ),
    6: reward(
        "潮州获得 2 所学校、1 座办公室与 4% 州 GDP。",
        "学术基础获得两次大幅、研究设施获得两次中等、贫困获得两次小幅改善；永久研究速度 +3%。",
        "潮州华人/竹人满意度 +8/+4。",
        "TNO_SocDev；TNO_economy_frontend；TNO_Guangdong；TNO 学校/办公室",
        "潮州（593）",
        "30k 高教育密度项目；科研社会收益高于地区体量",
        "办公室最终不超过 TNO 上限 3；研究速度计入累计 7% 审计",
        """TNO_improve_academic_base_high = yes
TNO_improve_research_facilities_med = yes
TNO_improve_poverty_low = yes
add_to_variable = { DOP_construction_reward_research_speed = 0.015 }
593 = {
\tadd_building_construction = { type = schools level = 2 instant_build = yes }
\tadd_building_construction = { type = offices level = 1 instant_build = yes }
\tset_temp_variable = { state_value_multiplier_temp = 1.02 }
\tecon_state_value_change_multiply_specified_state = yes
\tset_temp_variable = { chi_app_temp = 4 }
\tGNG_chinese_app_change = yes
\tset_temp_variable = { zhu_app_temp = 2 }
\tGNG_zhujin_app_change = yes
}""",
    ),
})

REWARDS.update({
    7: reward(
        "韶关与清远各获得 1 座水电站、1 级基础设施与 4% 州 GDP。",
        "农业获得两次中等、贫困与行政效率各获得两次小幅改善。",
        "韶关、清远华人满意度各 +6。",
        "TNO 巴西 hydroelectric_plant；TNO_SocDev；TNO_economy_frontend；TNO_Guangdong",
        "韶关（1439）、清远（614）",
        "60k 双州水利项目；实体能源与民生并重",
        "直接作用于指定州；好感在各州单独结算",
        """TNO_improve_agriculture_med = yes
TNO_improve_poverty_low = yes
TNO_improve_admin_efficiency_really_low = yes
1439 = {
\tadd_building_construction = { type = hydroelectric_plant level = 1 instant_build = yes }
\tadd_building_construction = { type = infrastructure level = 1 instant_build = yes }
\tset_temp_variable = { state_value_multiplier_temp = 1.02 }
\tecon_state_value_change_multiply_specified_state = yes
\tset_temp_variable = { chi_app_temp = 3 }
\tGNG_chinese_app_change = yes
}
614 = {
\tadd_building_construction = { type = hydroelectric_plant level = 1 instant_build = yes }
\tadd_building_construction = { type = infrastructure level = 1 instant_build = yes }
\tset_temp_variable = { state_value_multiplier_temp = 1.02 }
\tecon_state_value_change_multiply_specified_state = yes
\tset_temp_variable = { chi_app_temp = 3 }
\tGNG_chinese_app_change = yes
}""",
    ),
    8: reward(
        "肇庆获得 2 级基础设施、1 座补给节点与 8% 州 GDP。",
        "农业获得两次大幅、工业设备获得两次中等、贫困获得两次小幅改善。",
        "肇庆华人/竹人满意度 +6/+4。",
        "TNO_SocDev；TNO_economy_frontend；TNO_Guangdong；补给建筑",
        "肇庆（1438），补给省份 11941",
        "40k 储粮与机械化项目；社会收益可感知",
        "不使用军工厂；SocDev 合计纳入全项目累计审计",
        """TNO_improve_agriculture_high = yes
TNO_improve_industrial_equipment_med = yes
TNO_improve_poverty_low = yes
1438 = {
\tadd_building_construction = { type = infrastructure level = 2 instant_build = yes }
\tadd_building_construction = { type = supply_node province = 11941 level = 1 instant_build = yes }
\tset_temp_variable = { state_value_multiplier_temp = 1.04 }
\tecon_state_value_change_multiply_specified_state = yes
\tset_temp_variable = { chi_app_temp = 3 }
\tGNG_chinese_app_change = yes
\tset_temp_variable = { zhu_app_temp = 2 }
\tGNG_zhujin_app_change = yes
}""",
    ),
})

REWARDS.update({
    9: reward(
        "南宁、钦州基础设施至少 5 级；钦州港至少 8 级并新增海军补给枢纽，南宁新增补给节点。",
        "行政效率、工业专业知识与贫困各获得两次小幅改善。",
        "永久增加 0.40B 杂项收入；钦州华人/竹人满意度 +4/+4。",
        "TNO 伊比利亚交通；TNO_SocDev；TNO_economy_frontend；TNO_Guangdong",
        "南宁（594）、钦州（2472），省份 7137/1018",
        "100k 运河枢纽；实体物流与长期航运收入并重",
        "基础设施和港口使用至少值，避免预建浪费或超限",
        """TNO_improve_admin_efficiency_low = yes
TNO_improve_industrial_expertise_low = yes
TNO_improve_poverty_low = yes
add_to_variable = { DOP_construction_reward_misc_income = 0.20 }
594 = {
\tif = { limit = { infrastructure < 5 } set_building_level = { type = infrastructure level = 5 instant_build = yes } }
\tadd_building_construction = { type = supply_node province = 7137 level = 1 instant_build = yes }
}
2472 = {
\tif = { limit = { infrastructure < 5 } set_building_level = { type = infrastructure level = 5 instant_build = yes } }
\tif = { limit = { naval_base < 8 } set_building_level = { type = naval_base province = 1018 level = 8 instant_build = yes } }
\tadd_building_construction = { type = naval_supply_hub province = 1018 level = 1 instant_build = yes }
\tset_temp_variable = { chi_app_temp = 2 }
\tGNG_chinese_app_change = yes
\tset_temp_variable = { zhu_app_temp = 2 }
\tGNG_zhujin_app_change = yes
}""",
    ),
    10: reward(
        "儋州近海新增 24 单位石油与 10% 州 GDP。",
        "工业专业知识获得两次中等、工业设备获得两次小幅改善。",
        "永久增加 2 个生产单位与 0.50B 杂项收入；儋州日本人/竹人满意度 +4/+2。",
        "TNO 资源开发；TNO_SocDev；TNO_Guangdong；经济动态修正",
        "儋州（2475）",
        "30k 高产资源项目；资源、PU、收入均可感知",
        "PU 与收入纳入 20 项累计上限审计",
        """TNO_improve_industrial_expertise_med = yes
TNO_improve_industrial_equipment_low = yes
add_to_variable = { DOP_construction_reward_misc_income = 0.25 }
add_to_variable = { DOP_construction_reward_free_pu = 1 }
2475 = {
\tadd_resource = { type = oil amount = 12 }
\tset_temp_variable = { state_value_multiplier_temp = 1.05 }
\tecon_state_value_change_multiply_specified_state = yes
\tset_temp_variable = { jap_app_temp = 2 }
\tGNG_japanese_app_change = yes
\tset_temp_variable = { zhu_app_temp = 1 }
\tGNG_zhujin_app_change = yes
}""",
    ),
})

REWARDS.update({
    11: reward(
        "琼东获得 1 座火箭基地、2 级空军基地、1 级基础设施与 6% 州 GDP。",
        "研究设施获得两次大幅、学术基础与工业专业知识各获得两次小幅改善；永久研究速度 +4%。",
        "琼东日本人/华人满意度 +4/+4。",
        "TNO_SocDev；TNO rocket_site；TNO_Guangdong；经济动态修正",
        "琼东（2474）",
        "50k 航天科研项目；特殊建筑和科研能力并重",
        "全国研究速度与大学合计 7%，未形成无限增长接口",
        """TNO_improve_research_facilities_high = yes
TNO_improve_academic_base_low = yes
TNO_improve_industrial_expertise_low = yes
add_to_variable = { DOP_construction_reward_research_speed = 0.02 }
2474 = {
\tadd_building_construction = { type = rocket_site level = 1 instant_build = yes }
\tadd_building_construction = { type = air_base level = 2 instant_build = yes }
\tadd_building_construction = { type = infrastructure level = 1 instant_build = yes }
\tset_temp_variable = { state_value_multiplier_temp = 1.03 }
\tecon_state_value_change_multiply_specified_state = yes
\tset_temp_variable = { jap_app_temp = 2 }
\tGNG_japanese_app_change = yes
\tset_temp_variable = { chi_app_temp = 2 }
\tGNG_chinese_app_change = yes
}""",
    ),
    12: reward(
        "南宁获得 2 座办公室、1 所学校与 10% 州 GDP。",
        "工业专业知识获得两次大幅、行政效率获得两次中等改善。",
        "腐败降低 8；永久增加 2 个生产单位；南宁华人/竹人/日本人满意度 +4/+6/+2。",
        "TNO_SocDev；TNO_Guangdong corruption/app helper；经济动态修正",
        "南宁（594）",
        "60k 制度与产业组织项目；行政/GNG 收益突出",
        "办公室达到但不越过上限 3；腐败由 helper clamp",
        """TNO_improve_industrial_expertise_high = yes
TNO_improve_admin_efficiency_med = yes
set_temp_variable = { GNG_corruption_temp_var = -4 }
GNG_Corruption_Change = yes
add_to_variable = { DOP_construction_reward_free_pu = 1 }
594 = {
\tadd_building_construction = { type = offices level = 2 instant_build = yes }
\tadd_building_construction = { type = schools level = 1 instant_build = yes }
\tset_temp_variable = { state_value_multiplier_temp = 1.05 }
\tecon_state_value_change_multiply_specified_state = yes
\tset_temp_variable = { chi_app_temp = 2 }
\tGNG_chinese_app_change = yes
\tset_temp_variable = { zhu_app_temp = 3 }
\tGNG_zhujin_app_change = yes
\tset_temp_variable = { jap_app_temp = 1 }
\tGNG_japanese_app_change = yes
}""",
    ),
})

REWARDS.update({
    13: reward(
        "南宁、钦州各获得 2 级基础设施与 4% 州 GDP；桂林、柳江、苍梧、肇庆各获得 1 级基础设施。",
        "行政效率获得两次中等、贫困获得两次小幅改善。",
        "腐败降低 6；南宁华人/竹人满意度 +6/+4，钦州华人满意度 +4。",
        "TNO 中国州开发；TNO_SocDev；TNO_Guangdong corruption/app helper",
        "594/2472/599/2390/2391/1438",
        "90k 六州高速网；地区整合和行政收益突出",
        "非铁路项目不调用 build_railway；腐败由 TNO clamp，好感由州级 helper 结算",
        """TNO_improve_admin_efficiency_med = yes
TNO_improve_poverty_low = yes
set_temp_variable = { GNG_corruption_temp_var = -3 }
GNG_Corruption_Change = yes
594 = {
\tadd_building_construction = { type = infrastructure level = 2 instant_build = yes }
\tset_temp_variable = { state_value_multiplier_temp = 1.02 }
\tecon_state_value_change_multiply_specified_state = yes
\tset_temp_variable = { chi_app_temp = 3 }
\tGNG_chinese_app_change = yes
\tset_temp_variable = { zhu_app_temp = 2 }
\tGNG_zhujin_app_change = yes
}
2472 = {
\tadd_building_construction = { type = infrastructure level = 2 instant_build = yes }
\tset_temp_variable = { state_value_multiplier_temp = 1.02 }
\tecon_state_value_change_multiply_specified_state = yes
\tset_temp_variable = { chi_app_temp = 2 }
\tGNG_chinese_app_change = yes
}
599 = { add_building_construction = { type = infrastructure level = 1 instant_build = yes } }
2390 = { add_building_construction = { type = infrastructure level = 1 instant_build = yes } }
2391 = { add_building_construction = { type = infrastructure level = 1 instant_build = yes } }
1438 = { add_building_construction = { type = infrastructure level = 1 instant_build = yes } }""",
    ),
    14: reward(
        "苍梧获得 1 所学校与 4% 州 GDP。",
        "学术基础与贫困各获得两次小幅改善。",
        "永久增加 0.16B 杂项收入；苍梧华人/竹人/日本人满意度 +8/+6/-2。",
        "TNO_SocDev；TNO_economy_frontend；TNO_Guangdong app helper",
        "苍梧（2391）",
        "30k 文化认同项目；差异化政治结果明显",
        "日本人 -2 是文化认同强化后的设计取舍；三群体均由州级 helper 结算",
        """TNO_improve_academic_base_low = yes
TNO_improve_poverty_low = yes
add_to_variable = { DOP_construction_reward_misc_income = 0.08 }
2391 = {
\tadd_building_construction = { type = schools level = 1 instant_build = yes }
\tset_temp_variable = { state_value_multiplier_temp = 1.02 }
\tecon_state_value_change_multiply_specified_state = yes
\tset_temp_variable = { chi_app_temp = 4 }
\tGNG_chinese_app_change = yes
\tset_temp_variable = { zhu_app_temp = 3 }
\tGNG_zhujin_app_change = yes
\tset_temp_variable = { jap_app_temp = -1 }
\tGNG_japanese_app_change = yes
}""",
    ),
})

REWARDS.update({
    15: reward(
        "桂林、柳江、苍梧各获得 1 级基础设施；桂林另获 4% 州 GDP。",
        "农业、贫困各获得两次小幅改善；行政效率获得两次极小幅改善。",
        "永久增加 0.20B 杂项收入；桂林华人/竹人满意度 +4/+2。",
        "TNO 伊比利亚航运；TNO_SocDev；TNO_economy_frontend；TNO_Guangdong",
        "桂林（599）、柳江（2390）、苍梧（2391）",
        "30k 内河航道；地区物流、民生和收入均有体现",
        "不误用海军基地；行政仅 really_low 档控制累计强度",
        """TNO_improve_agriculture_low = yes
TNO_improve_poverty_low = yes
TNO_improve_admin_efficiency_really_low = yes
add_to_variable = { DOP_construction_reward_misc_income = 0.10 }
599 = {
\tadd_building_construction = { type = infrastructure level = 1 instant_build = yes }
\tset_temp_variable = { state_value_multiplier_temp = 1.02 }
\tecon_state_value_change_multiply_specified_state = yes
\tset_temp_variable = { chi_app_temp = 2 }
\tGNG_chinese_app_change = yes
\tset_temp_variable = { zhu_app_temp = 1 }
\tGNG_zhujin_app_change = yes
}
2390 = { add_building_construction = { type = infrastructure level = 1 instant_build = yes } }
2391 = { add_building_construction = { type = infrastructure level = 1 instant_build = yes } }""",
    ),
    16: reward(
        "龙津获得 2 级基础设施、1 座边境补给节点与 8% 州 GDP。",
        "行政效率与贫困各获得两次小幅改善。",
        "永久增加 0.20B 杂项收入与 10% 贸易关系评价；龙津华人/竹人满意度 +4/+4。",
        "TNO 中国州开发/贸易修正；TNO_SocDev；TNO_Guangdong",
        "龙津（2394），补给省份 4121",
        "30k 边贸口岸；小幅长期外交和收入收益",
        "贸易评价为 10%，仍不形成大额全国乘区",
        """TNO_improve_admin_efficiency_low = yes
TNO_improve_poverty_low = yes
add_to_variable = { DOP_construction_reward_misc_income = 0.10 }
add_to_variable = { DOP_construction_reward_trade_opinion = 0.05 }
2394 = {
\tadd_building_construction = { type = infrastructure level = 2 instant_build = yes }
\tadd_building_construction = { type = supply_node province = 4121 level = 1 instant_build = yes }
\tset_temp_variable = { state_value_multiplier_temp = 1.04 }
\tecon_state_value_change_multiply_specified_state = yes
\tset_temp_variable = { chi_app_temp = 2 }
\tGNG_chinese_app_change = yes
\tset_temp_variable = { zhu_app_temp = 2 }
\tGNG_zhujin_app_change = yes
}""",
    ),
})

REWARDS.update({
    17: reward(
        "建成香港—广州—澳门 5 级磁悬浮城轨；三州各获得 1 级基础设施与 6% 州 GDP。",
        "行政效率获得两次小幅、工业设备获得两次中等改善。",
        "永久增加 0.20B 杂项收入；香港日本人/竹人 +4/+4，广州华人 +4，澳门华人/竹人 +2/+2。",
        "TNO 巴西/伊比利亚 build_railway；TNO_SocDev；TNO_Guangdong",
        "香港（326）、广州（592）、澳门（729）；省份 10062…4189",
        "90k 都市圈轨道；真实 5 级铁路和多州整合为主体",
        "单条连续路径；满意度分州，避免全国无限溢出",
        """TNO_improve_admin_efficiency_low = yes
TNO_improve_industrial_equipment_med = yes
add_to_variable = { DOP_construction_reward_misc_income = 0.10 }
build_railway = {
\tlevel = 5
\tpath = { 10062 7108 1047 8802 4189 }
\tstart_province = 10062
\ttarget_province = 4189
}
326 = {
\tadd_building_construction = { type = infrastructure level = 1 instant_build = yes }
\tset_temp_variable = { state_value_multiplier_temp = 1.03 }
\tecon_state_value_change_multiply_specified_state = yes
\tset_temp_variable = { jap_app_temp = 2 }
\tGNG_japanese_app_change = yes
\tset_temp_variable = { zhu_app_temp = 2 }
\tGNG_zhujin_app_change = yes
}
592 = {
\tadd_building_construction = { type = infrastructure level = 1 instant_build = yes }
\tset_temp_variable = { state_value_multiplier_temp = 1.03 }
\tecon_state_value_change_multiply_specified_state = yes
\tset_temp_variable = { chi_app_temp = 2 }
\tGNG_chinese_app_change = yes
}
729 = {
\tadd_building_construction = { type = infrastructure level = 1 instant_build = yes }
\tset_temp_variable = { state_value_multiplier_temp = 1.03 }
\tecon_state_value_change_multiply_specified_state = yes
\tset_temp_variable = { chi_app_temp = 1 }
\tGNG_chinese_app_change = yes
\tset_temp_variable = { zhu_app_temp = 1 }
\tGNG_zhujin_app_change = yes
}""",
    ),
    18: reward(
        "建成汕头—揭阳—潮州 3 级城际铁路；潮州获得 2 级基础设施、2 级空军基地与 8% 州 GDP。",
        "行政效率获得两次中等、学术基础与贫困各获得两次小幅改善。",
        "腐败降低 4；潮州华人/竹人满意度 +6/+4。",
        "TNO 伊比利亚 build_railway；TNO_SocDev；TNO_Guangdong corruption/app",
        "潮州（593）；省份 9938…7182",
        "60k 一体化工程；铁路、机场和行政整合同步生效",
        "单条连续铁路；腐败由 TNO clamp，好感由州级 helper 结算",
        """TNO_improve_admin_efficiency_med = yes
TNO_improve_academic_base_low = yes
TNO_improve_poverty_low = yes
set_temp_variable = { GNG_corruption_temp_var = -2 }
GNG_Corruption_Change = yes
build_railway = {
\tlevel = 3
\tpath = { 9938 9978 7067 4050 4207 4165 7182 }
\tstart_province = 9938
\ttarget_province = 7182
}
593 = {
\tadd_building_construction = { type = infrastructure level = 2 instant_build = yes }
\tadd_building_construction = { type = air_base level = 2 instant_build = yes }
\tset_temp_variable = { state_value_multiplier_temp = 1.04 }
\tecon_state_value_change_multiply_specified_state = yes
\tset_temp_variable = { chi_app_temp = 3 }
\tGNG_chinese_app_change = yes
\tset_temp_variable = { zhu_app_temp = 2 }
\tGNG_zhujin_app_change = yes
}""",
    ),
})

REWARDS.update({
    19: reward(
        "韶关新增 10 单位铀、1 级基础设施与 10% 州 GDP。",
        "工业专业知识获得两次中等、工业设备获得两次小幅改善。",
        "永久资源开采效率 +6%；韶关日本人/竹人满意度 +4/+2。",
        "TNO 伊比利亚资源开发；TNO_SocDev；TNO_Guangdong；资源动态修正",
        "韶关（1439）",
        "60k 战略资源项目；资源与产业能力并重",
        "铀提高至 10 单位；资源效率与项目 20 合计 12%",
        """TNO_improve_industrial_expertise_med = yes
TNO_improve_industrial_equipment_low = yes
add_to_variable = { DOP_construction_reward_resource_factor = 0.03 }
1439 = {
\tadd_resource = { type = uranium amount = 5 }
\tadd_building_construction = { type = infrastructure level = 1 instant_build = yes }
\tset_temp_variable = { state_value_multiplier_temp = 1.05 }
\tecon_state_value_change_multiply_specified_state = yes
\tset_temp_variable = { jap_app_temp = 2 }
\tGNG_japanese_app_change = yes
\tset_temp_variable = { zhu_app_temp = 1 }
\tGNG_zhujin_app_change = yes
}""",
    ),
    20: reward(
        "茂名与肇庆各获得 1 座合成炼油厂与 1 级基础设施。",
        "工业设备获得两次大幅、工业专业知识获得两次中等、贫困获得两次小幅改善。",
        "永久增加 2 个生产单位、0.30B 杂项收入与 6% 资源效率；茂名华人/竹人/日本人 +4/+4/+4，肇庆华人 +2。",
        "TNO synthetic_refinery；TNO_SocDev；TNO_economy_frontend；TNO_Guangdong",
        "茂名（1017）、肇庆（1438）",
        "30k 炼化扩建；实体工厂与 GNG 经济反馈明显",
        "全项目 PU 合计 8、收入 2.90B、资源效率 12%，不无限增长",
        """TNO_improve_industrial_equipment_high = yes
TNO_improve_industrial_expertise_med = yes
TNO_improve_poverty_low = yes
add_to_variable = { DOP_construction_reward_free_pu = 1 }
add_to_variable = { DOP_construction_reward_misc_income = 0.15 }
add_to_variable = { DOP_construction_reward_resource_factor = 0.03 }
1017 = {
\tadd_building_construction = { type = synthetic_refinery level = 1 instant_build = yes }
\tadd_building_construction = { type = infrastructure level = 1 instant_build = yes }
\tset_temp_variable = { chi_app_temp = 2 }
\tGNG_chinese_app_change = yes
\tset_temp_variable = { zhu_app_temp = 2 }
\tGNG_zhujin_app_change = yes
\tset_temp_variable = { jap_app_temp = 2 }
\tGNG_japanese_app_change = yes
}
1438 = {
\tadd_building_construction = { type = synthetic_refinery level = 1 instant_build = yes }
\tadd_building_construction = { type = infrastructure level = 1 instant_build = yes }
\tset_temp_variable = { chi_app_temp = 1 }
\tGNG_chinese_app_change = yes
}""",
    ),
})


def read_text(path: Path) -> tuple[str, str, bool]:
    has_bom = path.read_bytes().startswith(b"\xef\xbb\xbf")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        text = handle.read()
    newline = "\r\n" if "\r\n" in text else "\n"
    return text, newline, has_bom


def write_text(path: Path, text: str, has_bom: bool) -> None:
    encoding = "utf-8-sig" if has_bom else "utf-8"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding=encoding, newline="") as handle:
        handle.write(text)


def validate_data() -> None:
    region_ids = [region.id for region in REGIONS]
    project_ids = [project.id for project in PROJECTS]
    if region_ids != list(range(1, len(REGIONS) + 1)):
        raise ValueError("Region IDs must be consecutive and start at 1.")
    if project_ids != list(range(1, len(PROJECTS) + 1)):
        raise ValueError("Project IDs must be consecutive and start at 1.")
    if len({region.slug for region in REGIONS}) != len(REGIONS):
        raise ValueError("Region slugs must be unique.")
    if len({project.slug for project in PROJECTS}) != len(PROJECTS):
        raise ValueError("Project slugs must be unique.")
    region_slugs = {region.slug for region in REGIONS}
    unknown = sorted({project.region for project in PROJECTS} - region_slugs)
    if unknown:
        raise ValueError(f"Unknown project regions: {', '.join(unknown)}")
    event_ids = [project.completion_event_id for project in PROJECTS]
    if len(set(event_ids)) != len(event_ids):
        raise ValueError("Completion event IDs must be unique.")
    if any(project.total <= 0 for project in PROJECTS):
        raise ValueError("Project totals must be positive.")
    if len(REGIONS) != 6 or len(PROJECTS) != 20:
        raise ValueError("Construction v8 requires exactly 6 regions and 20 projects.")
    if set(REWARDS) != set(project_ids):
        raise ValueError("Every project must have exactly one reward definition.")
    if len({project.source for project in PROJECTS}) != len(PROJECTS):
        raise ValueError("Project source image names must be unique.")
    if len({project.image for project in PROJECTS}) != len(PROJECTS):
        raise ValueError("Project image tokens must be unique.")


def replace_marked(text: str, begin: str, end: str, body: list[str], newline: str) -> str:
    begin_at = text.index(begin)
    end_at = text.index(end, begin_at)
    begin_line = text.rfind("\n", 0, begin_at) + 1
    end_line = text.rfind("\n", 0, end_at) + 1
    end_line_end = text.find("\n", end_at)
    if end_line_end == -1:
        end_line_end = len(text)
    else:
        end_line_end += 1
    indent = text[begin_line:begin_at]
    body_text = newline.join((indent + line) if line else "" for line in body)
    replacement = indent + begin + newline + body_text + newline + indent + end
    # apply_patch may leave a generated marker line with a different newline
    # style from the surrounding file. Always separate a non-EOF marker from
    # the following declaration so repeated generation cannot fuse both lines.
    if end_line_end < len(text):
        replacement += newline
    return text[:begin_line] + replacement + text[end_line_end:]


def render_registry() -> list[str]:
    lines: list[str] = []
    region_id = {region.slug: region.id for region in REGIONS}
    for region in REGIONS:
        lines.append(f"add_to_array = {{ DOP_construction_region_ids = {region.id} }}")
    for region in REGIONS:
        lines.append(
            f"add_to_array = {{ DOP_construction_region_tokens = token:DOP_construction_region_{region.slug} }}"
        )
    lines.append("")
    for project in PROJECTS:
        lines.extend(
            [
                f"set_temp_variable = {{ DOP_construction_register_id = {project.id} }}",
                f"set_temp_variable = {{ DOP_construction_register_token = token:DOP_construction_{project.slug} }}",
                f"set_temp_variable = {{ DOP_construction_register_desc_token = token:DOP_construction_{project.slug}_desc }}",
                f"set_temp_variable = {{ DOP_construction_register_region = {region_id[project.region]} }}",
                f"set_temp_variable = {{ DOP_construction_register_image = token:{project.image} }}",
                f"set_temp_variable = {{ DOP_construction_register_event = {project.completion_event_id} }}",
                f"set_temp_variable = {{ DOP_construction_register_total = {project.total} }}",
                "DOP_construction_register_project = yes",
                "",
            ]
        )
    if lines and not lines[-1]:
        lines.pop()
    return lines


def loc_value(value: str) -> str:
    return value.replace('"', chr(92) + '"')


def render_tokens() -> list[str]:
    lines = ["DOP_construction_no_region", "DOP_construction_no_project", "DOP_construction_no_project_desc", ""]
    lines.extend(f"DOP_construction_region_{region.slug}" for region in REGIONS)
    lines.append("")
    for project in PROJECTS:
        lines.append(f"DOP_construction_{project.slug}")
        lines.append(f"DOP_construction_{project.slug}_desc")
    lines.append("")
    lines.extend(sorted({project.image for project in PROJECTS}))
    return lines


def render_event_dispatch() -> list[str]:
    lines: list[str] = []
    for project in PROJECTS:
        lines.extend(
            [
                "if = {",
                "\tlimit = { check_variable = { "
                f"DOP_construction_completed_event_id = {project.completion_event_id} }} }}",
                f"\tset_country_flag = DOP_construction_{project.slug}_completed",
                f"\tset_variable = {{ DOP_construction_completion_queued^{project.id} = 1 }}",
                "}",
            ]
        )
    return lines


def render_directory() -> list[str]:
    region_id = {region.slug: region.id for region in REGIONS}
    lines: list[str] = []
    for region in REGIONS:
        region_projects = [
            project for project in PROJECTS if region_id[project.region] == region.id
        ]
        lines.extend(
            [
                "if = {",
                "\tlimit = {",
                "\t\tOR = {",
            ]
        )
        for project in region_projects:
            lines.append(
                f"\t\t\tcheck_variable = {{ DOP_construction_shown^{project.id} > 0 }}"
            )
        lines.extend(
            [
                "\t\t}",
                "\t}",
                f"\tadd_to_array = {{ DOP_construction_directory_items = {100 + region.id} }}",
                "\tif = {",
                f"\t\tlimit = {{ has_country_flag = DOP_construction_region_{region.id}_expanded }}",
            ]
        )
        for project in region_projects:
            lines.extend(
                [
                    "\t\tif = {",
                    f"\t\t\tlimit = {{ check_variable = {{ DOP_construction_shown^{project.id} > 0 }} }}",
                    f"\t\t\tadd_to_array = {{ DOP_construction_directory_items = {project.id} }}",
                    "\t\t}",
                ]
            )
        lines.extend(["\t}", "}"])
    return lines


def render_directory_toggles() -> list[str]:
    region_id = {region.slug: region.id for region in REGIONS}
    lines: list[str] = []
    for region in REGIONS:
        region_projects = [
            project for project in PROJECTS if region_id[project.region] == region.id
        ]
        lines.extend(
            [
                "if = {",
                "\tlimit = { check_variable = { "
                f"DOP_construction_directory_item = {100 + region.id} }} }}",
                f"\tset_variable = {{ DOP_construction_selected_region = {region.id} }}",
            ]
        )
        for index, project in enumerate(region_projects):
            branch = "if" if index == 0 else "else_if"
            lines.extend(
                [
                    f"\t{branch} = {{",
                    f"\t\tlimit = {{ check_variable = {{ DOP_construction_shown^{project.id} > 0 }} }}",
                    f"\t\tset_variable = {{ DOP_construction_selected = {project.id} }}",
                    "\t}",
                ]
            )
        lines.extend(
            [
                "\tif = {",
                f"\t\tlimit = {{ has_country_flag = DOP_construction_region_{region.id}_expanded }}",
                f"\t\tclr_country_flag = DOP_construction_region_{region.id}_expanded",
                "\t}",
                f"\telse = {{ set_country_flag = DOP_construction_region_{region.id}_expanded }}",
                "}",
            ]
        )
    return lines


def render_select_first_shown() -> list[str]:
    region_id = {region.slug: region.id for region in REGIONS}
    lines: list[str] = []
    for index, project in enumerate(PROJECTS):
        branch = "if" if index == 0 else "else_if"
        lines.extend(
            [
                f"{branch} = {{",
                f"\tlimit = {{ check_variable = {{ DOP_construction_shown^{project.id} > 0 }} }}",
                f"\tset_variable = {{ DOP_construction_selected = {project.id} }}",
                f"\tset_variable = {{ DOP_construction_selected_region = {region_id[project.region]} }}",
                "}",
            ]
        )
    lines.extend(
        [
            "else = {",
            "\tset_variable = { DOP_construction_selected = 0 }",
            "\tset_variable = { DOP_construction_selected_region = 0 }",
            "}",
        ]
    )
    return lines


def render_state_dispatch() -> list[str]:
    lines = ["DOP_construction_mark_project_shown = {"]
    for project in PROJECTS:
        lines.extend(
            [
                "\tif = {",
                f"\t\tlimit = {{ check_variable = {{ DOP_construction_target_project = {project.id} }} }}",
                f"\t\tset_variable = {{ DOP_construction_shown^{project.id} = 1 }}",
                f"\t\tset_country_flag = DOP_construction_{project.slug}_shown",
                "\t}",
            ]
        )
    lines.extend(["}", "", "DOP_construction_mark_project_started = {"])
    for project in PROJECTS:
        lines.extend(
            [
                "\tif = {",
                f"\t\tlimit = {{ check_variable = {{ DOP_construction_target_project = {project.id} }} }}",
                f"\t\tset_variable = {{ DOP_construction_started^{project.id} = 1 }}",
                f"\t\tset_country_flag = DOP_construction_{project.slug}_started",
                "\t}",
            ]
        )
    lines.append("}")
    return lines


def render_clear_flags() -> list[str]:
    lines: list[str] = []
    for project in PROJECTS:
        lines.append(f"clr_country_flag = DOP_construction_{project.slug}_completed")
        lines.append(f"clr_country_flag = DOP_construction_{project.slug}_reward_claimed")
    return lines


def render_clear_expansion_flags() -> list[str]:
    return [
        f"clr_country_flag = DOP_construction_region_{region.id}_expanded"
        for region in REGIONS
    ]


def render_clear_state_flags() -> list[str]:
    lines: list[str] = []
    for project in PROJECTS:
        lines.append(f"clr_country_flag = DOP_construction_{project.slug}_shown")
        lines.append(f"clr_country_flag = DOP_construction_{project.slug}_started")
    return lines


def render_scripted_localisation() -> list[str]:
    lines = [
        "defined_text = {",
        "\tname = DOP_construction_GetDirectoryEntryContainer",
        "\ttext = {",
        "\t\ttrigger = { check_variable = { DOP_construction_directory_item > 100 } }",
        '\t\tlocalization_key = "DOP_construction_region_entry"',
        "\t}",
        '\ttext = { localization_key = "DOP_construction_project_entry" }',
        "}",
        "",
        "defined_text = {",
        "\tname = DOP_construction_GetDirectoryRegionName",
    ]
    for region in REGIONS:
        lines.extend(
            [
                "\ttext = {",
                "\t\ttrigger = { check_variable = { "
                f"DOP_construction_directory_item = {100 + region.id} }} }}",
                f"\t\tlocalization_key = DOP_construction_region_{region.slug}",
                "\t}",
            ]
        )
    lines.extend(["}", "", "defined_text = {", "\tname = DOP_construction_GetSelectedRegionName"])
    for region in REGIONS:
        lines.extend(
            [
                "\ttext = {",
                "\t\ttrigger = { check_variable = { "
                f"DOP_construction_selected_region = {region.id} }} }}",
                f"\t\tlocalization_key = DOP_construction_region_{region.slug}",
                "\t}",
            ]
        )
    lines.extend(
        [
            "\ttext = { localization_key = DOP_construction_no_region }",
            "}",
            "",
            "defined_text = {",
            "\tname = DOP_construction_GetTargetProjectName",
        ]
    )
    for project in PROJECTS:
        lines.extend(
            [
                "\ttext = {",
                f"\t\ttrigger = {{ check_variable = {{ DOP_construction_target_project = {project.id} }} }}",
                f"\t\tlocalization_key = DOP_construction_{project.slug}",
                "\t}",
            ]
        )
    lines.extend(
        [
            "\ttext = { localization_key = DOP_construction_no_project }",
            "}",
            "",
            "defined_text = {",
            "\tname = DOP_construction_GetDirectoryRegionMarker",
        ]
    )
    for region in REGIONS:
        lines.extend(
            [
                "\ttext = {",
                "\t\ttrigger = {",
                "\t\t\tcheck_variable = { "
                f"DOP_construction_directory_item = {100 + region.id} }}",
                f"\t\t\thas_country_flag = DOP_construction_region_{region.id}_expanded",
                "\t\t}",
                "\t\tlocalization_key = DOP_construction_directory_marker_open",
                "\t}",
            ]
        )
    lines.extend(
        [
            "\ttext = { localization_key = DOP_construction_directory_marker_closed }",
            "}",
        ]
    )
    return lines


def render_localisation() -> list[str]:
    lines = [
        "# Dynamic construction registry, GUI and completion-event localisation.",
        'DOP_construction_no_region:0 "暂无地区"',
        'DOP_construction_no_project:0 "暂无建设项目"',
        'DOP_construction_no_project_desc:0 "建设项目尚未添加到岭南建设总署。"',
        'DOP_construction_region_directory_title:0 "建设目录"',
        'DOP_construction_project_directory_title:0 "设施项目"',
        'DOP_construction_region_entry_name:0 "§B[DOP_construction_GetDirectoryRegionMarker] [DOP_construction_GetDirectoryRegionName]§!"',
        'DOP_construction_region_entry_tt:0 "展开或收起该地区；同时切换到该地区的第一个已显示建设项目。"',
        'DOP_construction_project_entry_name:0 "[?DOP_construction_project_tokens^DOP_construction_directory_item.GetTokenLocalizedKey]"',
        'DOP_construction_project_entry_tt:0 "[DOP_construction_GetEntryDesc]"',
        'DOP_construction_directory_marker_open:0 "−"',
        'DOP_construction_directory_marker_closed:0 "+"',
        'DOP_construction_show_project_tt:0 "£GFX_infrastructure §Y「[DOP_construction_GetTargetProjectName]」§!已在§B岭南建设总署§!§G立项§!。"',
        'DOP_construction_start_project_tt:0 "£GFX_infrastructure §B岭南建设总署§!的§Y「[DOP_construction_GetTargetProjectName]」§!已获准§G启动§!，一旦触发此效果，工程将§G即刻开始§!。"',
        'DOP_construction_show_and_start_project_tt:0 "£GFX_infrastructure §Y「[DOP_construction_GetTargetProjectName]」§!已在§B岭南建设总署§!§G立项§!，并获批§G立刻启动§!；一旦触发此效果，工程将§G即刻开始§!。"',
        'DOP_construction_economic_commitments:0 "岭南建设总署：建设经济承诺"',
        'DOP_construction_economic_commitments_desc:0 "正在施工的项目所产生的持续杂项支出与生产单位占用。"',
        'DOP_construction_social_mobilisation:0 "岭南建设总署：社会动员"',
        'DOP_construction_social_mobilisation_desc:0 "当前人力组织强度汇总产生的行政、社会发展与群体支持影响。"',
        'DOP_construction_completed_assets:0 "岭南建设总署：竣工资产"',
        'DOP_construction_completed_assets_desc:0 "已经验收的建设项目所提供的长期经济、科研与资源收益。"',
        'DOP_construction_selected_numbers:0 "目标工程量：[?DOP_construction_selected_total|0]\\n当前进度：[?DOP_construction_selected_progress|0]（[?DOP_construction_selected_percent|1]%）\\n基础速度：[?DOP_construction_base_speed|0]/周\\n实际速度：[?DOP_construction_selected_actual_speed|1]/周\\n资金倍率：[?DOP_construction_selected_funding_speed_factor|2]×\\n人力倍率：[?DOP_construction_selected_manpower_speed_factor|2]×\\n额外倍率：[?DOP_construction_selected_speed_factor|2]×"',
        'DOP_construction_funding_label:0 "资金投入：[?DOP_construction_selected_funding|0]%"',
        'DOP_construction_funding_effects:0 "本项目持续支出：[?DOP_construction_selected_misc_cost|3]B美元\\n本项目占用：£tt_prod_unit [?DOP_construction_selected_pu_cost|2]生产单位"',
        'DOP_construction_manpower_label:0 "人力组织：[?DOP_construction_selected_manpower|0]%"',
        'DOP_construction_manpower_effects:0 "全局统计：\\n全部施工持续支出：[?DOP_construction_total_misc_costs|3]B美元\\n全部施工占用：£tt_prod_unit [?DOP_construction_total_pu_occupied|0]生产单位\\n每日政治点数：[?DOP_construction_mobilisation_pp_gain|=+2]\\n每周稳定度：[?DOP_construction_mobilisation_stability_weekly_display|=+2]%\\n每月工业专业知识：[?DOP_construction_mobilisation_expertise_monthly|=+2]\\n每月贫困改善：[?DOP_construction_mobilisation_poverty_monthly|=+2]\\n每月行政效率：[?DOP_construction_mobilisation_admin_monthly|=+2]\\n每月£GNG_chinese_texticon §i华人§!政府支持率：[?DOP_construction_mobilisation_chinese_monthly|=+2]\\n每月£GNG_zhujin_texticon §E珠人§!政府支持率：[?DOP_construction_mobilisation_zhujin_monthly|=+2]\\n每月£GNG_expats_texticon §e日侨§!政府支持率：[?DOP_construction_mobilisation_japanese_monthly|=+2]"',
        'DOP_construction_description_click_tt:0 "§G点击§!项目简介以查看真实完工效果。"',
        'DOP_construction_effect_overlay_heading:0 "§Y项目完工效果§!"',
        'DOP_construction_effect_overlay_hint:0 "将光标停留在此页查看真实效果。\\n§G点击§!返回项目简介。"',
        'DOP_construction_selected_effect_tt:0 "[!construction_effect_overlay_button_click]"',
        'DOP_construction_preview_return_tt:0 "\\n§G点击§!返回项目简介。"',
        'DOP_GNG_construction.completed.desc:0 "岭南建设总署确认工程已达到计划目标。项目的地区设施、社会发展与广东特色收益，将在本事件确认后一次性发放。"',
        'DOP_GNG_construction.completed.a:0 "验收工程并落实全部收益"',
        'DOP_construction_research_speed_reward_tt:0 "$MODIFIER_RESEARCH_SPEED_FACTOR$：[?DOP_construction_reward_component_value|=+%2]\\n"',
        'DOP_construction_resource_factor_reward_tt:0 "$MODIFIER_LOCAL_RESOURCES_FACTOR$：[?DOP_construction_reward_component_value|=+%2]\\n"',
        'DOP_construction_trade_opinion_reward_tt:0 "$MODIFIER_TRADE_OPINION_FACTOR$：[?DOP_construction_reward_component_value|=+%2]\\n"',
        "",
    ]
    for region in REGIONS:
        lines.append(f'DOP_construction_region_{region.slug}:0 "{loc_value(region.name)}"')
    lines.append("")
    for project in PROJECTS:
        lines.append(f'DOP_construction_{project.slug}:0 "{loc_value(project.name)}"')
        lines.append(f'DOP_construction_{project.slug}_desc:0 "{loc_value(project.desc)}"')
        lines.append(
            f'DOP_GNG_construction.{project.completion_event_id}.t:0 "{loc_value(project.name)}建设完成"'
        )
    return lines


def render_persistent_reward_components() -> list[str]:
    components = (
        (
            "DOP_construction_add_misc_income_reward",
            "TNO_econ_misc_income_increase_tt",
            "DOP_construction_reward_misc_income",
            "misc_income_temp",
        ),
        (
            "DOP_construction_add_free_pu_reward",
            "TNO_econ_pus_increase_tt",
            "DOP_construction_reward_free_pu",
            "pus_temp",
        ),
        (
            "DOP_construction_add_research_speed_reward",
            "DOP_construction_research_speed_reward_tt",
            "DOP_construction_reward_research_speed",
            "DOP_construction_reward_component_value",
        ),
        (
            "DOP_construction_add_resource_factor_reward",
            "DOP_construction_resource_factor_reward_tt",
            "DOP_construction_reward_resource_factor",
            "DOP_construction_reward_component_value",
        ),
        (
            "DOP_construction_add_trade_opinion_reward",
            "DOP_construction_trade_opinion_reward_tt",
            "DOP_construction_reward_trade_opinion",
            "DOP_construction_reward_component_value",
        ),
    )
    lines: list[str] = []
    for effect, tooltip, variable, temp_variable in components:
        lines.extend(
            [
                f"{effect} = {{",
                f"\tcustom_effect_tooltip = {tooltip}",
                "\thidden_effect = {",
                f"\t\tadd_to_variable = {{ {variable} = {temp_variable} }}",
                "\t}",
                "}",
                "",
            ]
        )
    return lines


def render_componentised_reward(effect: tuple[str, ...]) -> list[str]:
    lines: list[str] = []
    for line in effect:
        match = PERSISTENT_REWARD_EFFECT.fullmatch(line)
        if not match:
            lines.append(line)
            continue
        temp_variable, component = PERSISTENT_REWARD_COMPONENTS[
            match.group("variable")
        ]
        indent = match.group("indent")
        lines.extend(
            [
                f"{indent}set_temp_variable = {{ {temp_variable} = {match.group('value')} }}",
                f"{indent}{component} = yes",
            ]
        )
    return lines


def render_rewards() -> str:
    lines = [
        "# Generated by tools/generate_dop_construction.py; do not edit by hand.",
        "# The event payout and effect_tooltip preview share these callbacks.",
        "",
    ]
    lines.extend(render_persistent_reward_components())
    for project in PROJECTS:
        lines.append(f"DOP_construction_{project.slug}_completion_effect = {{")
        lines.extend(
            "\t" + line if line else ""
            for line in render_componentised_reward(REWARDS[project.id].effect)
        )
        if project.id in IBUKA_POINT_FLAGS:
            flag = IBUKA_POINT_FLAGS[project.id]
            lines.extend(
                [
                    "\t# DOP CONTENT FLOW 260902A Ibuka score",
                    "\tif = {",
                    f"\t\tlimit = {{ NOT = {{ has_country_flag = {flag} }} }}",
                    f"\t\tset_country_flag = {flag}",
                    "\t\tDOP_GNG_add_ibuka_point = yes",
                    "\t}",
                ]
            )
        lines.extend(["}", ""])

    lines.append("DOP_construction_dispatch_reward_callback = {")
    for project in PROJECTS:
        lines.extend(
            [
                "\tif = {",
                f"\t\tlimit = {{ check_variable = {{ DOP_construction_target_project = {project.id} }} }}",
                f"\t\tDOP_construction_{project.slug}_completion_effect = yes",
                "\t}",
            ]
        )
    lines.extend(
        [
            "}",
            "",
            "DOP_construction_preview_selected_reward = {",
            "\tset_temp_variable = { DOP_construction_target_project = DOP_construction_selected }",
            "\teffect_tooltip = { DOP_construction_dispatch_reward_callback = yes }",
            "\tcustom_effect_tooltip = DOP_construction_preview_return_tt",
            "}",
            "",
            "DOP_construction_claim_project_reward = {",
            "\tif = {",
            "\t\tlimit = {",
            "\t\t\tcheck_variable = { DOP_construction_completed^DOP_construction_target_project > 0 }",
            "\t\t\tcheck_variable = { DOP_construction_reward_claimed^DOP_construction_target_project < 1 }",
            "\t\t}",
            "\t\tset_variable = { DOP_construction_reward_claimed^DOP_construction_target_project = 1 }",
            "\t\tDOP_construction_dispatch_reward_callback = yes",
        ]
    )
    for project in PROJECTS:
        lines.extend(
            [
                "\t\tif = {",
                f"\t\t\tlimit = {{ check_variable = {{ DOP_construction_target_project = {project.id} }} }}",
                f"\t\t\tset_country_flag = DOP_construction_{project.slug}_reward_claimed",
                "\t\t}",
            ]
        )
    lines.extend(
        [
            "\t\tforce_update_dynamic_modifier = yes",
            "\t\tupdate_economy_tab = yes",
            "\t\tDOP_construction_recalculate_all = yes",
            "\t\tDOP_construction_sync_selected = yes",
            "\t}",
            "}",
            "",
            "DOP_construction_process_completion_queue = {",
            "\tset_temp_variable = { DOP_construction_event_fired_today = 0 }",
        ]
    )
    for project in PROJECTS:
        lines.extend(
            [
                "\tif = {",
                "\t\tlimit = {",
                "\t\t\tcheck_variable = { DOP_construction_event_fired_today = 0 }",
                f"\t\t\tcheck_variable = {{ DOP_construction_completion_queued^{project.id} > 0 }}",
                f"\t\t\tcheck_variable = {{ DOP_construction_reward_claimed^{project.id} < 1 }}",
                "\t\t}",
                f"\t\tset_variable = {{ DOP_construction_completion_queued^{project.id} = 0 }}",
                "\t\tset_temp_variable = { DOP_construction_event_fired_today = 1 }",
                f"\t\tcountry_event = {{ id = DOP_GNG_construction.{project.completion_event_id} hours = 1 }}",
                "\t}",
            ]
        )
    lines.extend(["}", ""])
    return "\n".join(lines)


def render_events() -> str:
    lines = ["add_namespace = DOP_GNG_construction", ""]
    for project in PROJECTS:
        lines.extend(
            [
                "country_event = {",
                f"\tid = DOP_GNG_construction.{project.completion_event_id}",
                f"\ttitle = DOP_GNG_construction.{project.completion_event_id}.t",
                "\tdesc = DOP_GNG_construction.completed.desc",
                "\tpicture = GFX_report_event_IBR_road_work_1",
                "\tis_triggered_only = yes",
                "\toption = {",
                "\t\tname = DOP_GNG_construction.completed.a",
                f"\t\tset_temp_variable = {{ DOP_construction_target_project = {project.id} }}",
                "\t\tDOP_construction_claim_project_reward = yes",
                "\t}",
                "}",
                "",
            ]
        )
    return "\n".join(lines)


def render_slider_runtime() -> list[str]:
    return r"""
DOP_construction_recalculate_project = {
	set_variable = { DOP_construction_funding_speed_factor^DOP_construction_project_id = DOP_construction_funding^DOP_construction_project_id }
	divide_variable = { DOP_construction_funding_speed_factor^DOP_construction_project_id = 100 }
	add_to_variable = { DOP_construction_funding_speed_factor^DOP_construction_project_id = 0.5 }

	set_variable = { DOP_construction_manpower_speed_factor^DOP_construction_project_id = DOP_construction_manpower^DOP_construction_project_id }
	multiply_variable = { DOP_construction_manpower_speed_factor^DOP_construction_project_id = 0.006 }
	add_to_variable = { DOP_construction_manpower_speed_factor^DOP_construction_project_id = 0.7 }

	set_variable = { DOP_construction_input_factor^DOP_construction_project_id = DOP_construction_funding_speed_factor^DOP_construction_project_id }
	multiply_variable = { DOP_construction_input_factor^DOP_construction_project_id = DOP_construction_manpower_speed_factor^DOP_construction_project_id }
	set_variable = { DOP_construction_actual_speed^DOP_construction_project_id = DOP_construction_base_speed }
	add_to_variable = { DOP_construction_actual_speed^DOP_construction_project_id = DOP_construction_speed_add^DOP_construction_project_id }
	multiply_variable = { DOP_construction_actual_speed^DOP_construction_project_id = DOP_construction_input_factor^DOP_construction_project_id }
	multiply_variable = { DOP_construction_actual_speed^DOP_construction_project_id = DOP_construction_speed_factor^DOP_construction_project_id }
	clamp_variable = { var = DOP_construction_actual_speed^DOP_construction_project_id min = 0 }

	set_variable = { DOP_construction_project_misc_cost^DOP_construction_project_id = 0 }
	set_variable = { DOP_construction_project_pu_cost^DOP_construction_project_id = 0 }
	if = {
		limit = {
			check_variable = { DOP_construction_started^DOP_construction_project_id > 0 }
			check_variable = { DOP_construction_completed^DOP_construction_project_id < 1 }
		}
		set_variable = { DOP_construction_project_misc_cost^DOP_construction_project_id = DOP_construction_total^DOP_construction_project_id }
		divide_variable = { DOP_construction_project_misc_cost^DOP_construction_project_id = 1000000 }
		multiply_variable = { DOP_construction_project_misc_cost^DOP_construction_project_id = DOP_construction_funding^DOP_construction_project_id }
		divide_variable = { DOP_construction_project_misc_cost^DOP_construction_project_id = 50 }
		set_variable = { DOP_construction_project_pu_cost^DOP_construction_project_id = DOP_construction_total^DOP_construction_project_id }
		divide_variable = { DOP_construction_project_pu_cost^DOP_construction_project_id = 100000 }
		multiply_variable = { DOP_construction_project_pu_cost^DOP_construction_project_id = DOP_construction_funding^DOP_construction_project_id }
		divide_variable = { DOP_construction_project_pu_cost^DOP_construction_project_id = 50 }
	}

	set_variable = { DOP_construction_percent^DOP_construction_project_id = DOP_construction_progress^DOP_construction_project_id }
	if = {
		limit = { check_variable = { DOP_construction_total^DOP_construction_project_id > 0 } }
		divide_variable = { DOP_construction_percent^DOP_construction_project_id = DOP_construction_total^DOP_construction_project_id }
		multiply_variable = { DOP_construction_percent^DOP_construction_project_id = 100 }
	}
	else = { set_variable = { DOP_construction_percent^DOP_construction_project_id = 0 } }
	clamp_variable = { var = DOP_construction_percent^DOP_construction_project_id min = 0 max = 100 }
}

DOP_construction_recalculate_all = {
	for_each_loop = {
		array = DOP_construction_project_ids
		set_temp_variable = { DOP_construction_project_id = v }
		DOP_construction_recalculate_project = yes
	}
	DOP_construction_recalculate_aggregate_burden = yes
}

DOP_construction_recalculate_aggregate_burden = {
	set_temp_variable = { DOP_construction_previous_pu_occupied = DOP_construction_total_pu_occupied }
	set_variable = { DOP_construction_total_misc_costs = 0 }
	set_variable = { DOP_construction_total_pu_raw = 0 }
	set_variable = { DOP_construction_mobilisation_pp_gain = 0 }
	set_variable = { DOP_construction_mobilisation_stability_weekly = 0 }
	set_variable = { DOP_construction_mobilisation_expertise_monthly = 0 }
	set_variable = { DOP_construction_mobilisation_poverty_monthly = 0 }
	set_variable = { DOP_construction_mobilisation_admin_monthly = 0 }
	set_variable = { DOP_construction_mobilisation_chinese_monthly = 0 }
	set_variable = { DOP_construction_mobilisation_zhujin_monthly = 0 }
	set_variable = { DOP_construction_mobilisation_japanese_monthly = 0 }

	for_each_loop = {
		array = DOP_construction_project_ids
		set_temp_variable = { DOP_construction_project_id = v }
		if = {
			limit = {
				check_variable = { DOP_construction_started^DOP_construction_project_id > 0 }
				check_variable = { DOP_construction_completed^DOP_construction_project_id < 1 }
			}
			add_to_variable = { DOP_construction_total_misc_costs = DOP_construction_project_misc_cost^DOP_construction_project_id }
			add_to_variable = { DOP_construction_total_pu_raw = DOP_construction_project_pu_cost^DOP_construction_project_id }
			set_temp_variable = { DOP_construction_mobilisation_scale = DOP_construction_total^DOP_construction_project_id }
			divide_temp_variable = { DOP_construction_mobilisation_scale = 100000 }
			set_temp_variable = { DOP_construction_mobilisation_offset = DOP_construction_manpower^DOP_construction_project_id }
			subtract_from_temp_variable = { DOP_construction_mobilisation_offset = 50 }
			divide_temp_variable = { DOP_construction_mobilisation_offset = 50 }
			clamp_temp_variable = { var = DOP_construction_mobilisation_offset min = -0.8 max = 1 }
			set_temp_variable = { DOP_construction_mobilisation_scaled = DOP_construction_mobilisation_scale }
			multiply_temp_variable = { DOP_construction_mobilisation_scaled = DOP_construction_mobilisation_offset }

			set_temp_variable = { DOP_construction_contribution = DOP_construction_mobilisation_scaled }
			multiply_temp_variable = { DOP_construction_contribution = -0.04 }
			add_to_variable = { DOP_construction_mobilisation_pp_gain = DOP_construction_contribution }
			set_temp_variable = { DOP_construction_contribution = DOP_construction_mobilisation_scaled }
			multiply_temp_variable = { DOP_construction_contribution = -0.00016 }
			add_to_variable = { DOP_construction_mobilisation_stability_weekly = DOP_construction_contribution }
			set_temp_variable = { DOP_construction_contribution = DOP_construction_mobilisation_scaled }
			multiply_temp_variable = { DOP_construction_contribution = 1.6 }
			add_to_variable = { DOP_construction_mobilisation_expertise_monthly = DOP_construction_contribution }
			set_temp_variable = { DOP_construction_contribution = DOP_construction_mobilisation_scaled }
			multiply_temp_variable = { DOP_construction_contribution = -1 }
			add_to_variable = { DOP_construction_mobilisation_poverty_monthly = DOP_construction_contribution }
			set_temp_variable = { DOP_construction_contribution = DOP_construction_mobilisation_scaled }
			multiply_temp_variable = { DOP_construction_contribution = -0.8 }
			add_to_variable = { DOP_construction_mobilisation_admin_monthly = DOP_construction_contribution }
			set_temp_variable = { DOP_construction_contribution = DOP_construction_mobilisation_scaled }
			multiply_temp_variable = { DOP_construction_contribution = 0.24 }
			add_to_variable = { DOP_construction_mobilisation_chinese_monthly = DOP_construction_contribution }
			set_temp_variable = { DOP_construction_contribution = DOP_construction_mobilisation_scaled }
			multiply_temp_variable = { DOP_construction_contribution = -0.06 }
			add_to_variable = { DOP_construction_mobilisation_zhujin_monthly = DOP_construction_contribution }
			set_temp_variable = { DOP_construction_contribution = DOP_construction_mobilisation_scaled }
			multiply_temp_variable = { DOP_construction_contribution = -0.20 }
			add_to_variable = { DOP_construction_mobilisation_japanese_monthly = DOP_construction_contribution }
		}
	}

	set_variable = { DOP_construction_total_pu_occupied = DOP_construction_total_pu_raw }
	round_variable = DOP_construction_total_pu_occupied
	clamp_variable = { var = DOP_construction_mobilisation_pp_gain min = -0.5 max = 0.2 }
	clamp_variable = { var = DOP_construction_mobilisation_stability_weekly min = -0.003 max = 0.0008 }
	clamp_variable = { var = DOP_construction_mobilisation_expertise_monthly min = -6 max = 16 }
	clamp_variable = { var = DOP_construction_mobilisation_poverty_monthly min = -12 max = 8 }
	clamp_variable = { var = DOP_construction_mobilisation_admin_monthly min = -10 max = 6 }
	clamp_variable = { var = DOP_construction_mobilisation_chinese_monthly min = -3 max = 3 }
	clamp_variable = { var = DOP_construction_mobilisation_zhujin_monthly min = -3 max = 3 }
	clamp_variable = { var = DOP_construction_mobilisation_japanese_monthly min = -3 max = 3 }
	set_variable = { DOP_construction_mobilisation_stability_weekly_display = DOP_construction_mobilisation_stability_weekly }
	multiply_variable = { DOP_construction_mobilisation_stability_weekly_display = 100 }
	force_update_dynamic_modifier = yes
	if = {
		limit = {
			OR = {
				NOT = { has_country_flag = DOP_construction_special_pu_registered }
				check_variable = {
					var = DOP_construction_total_pu_occupied
					value = DOP_construction_previous_pu_occupied
					compare = not_equals
				}
			}
		}
		set_country_flag = DOP_construction_special_pu_registered
		recalculate_PUs_on_demand = yes
	}
	update_economy_tab = yes
}
    """.strip().splitlines()


def render_gfx() -> list[str]:
    lines: list[str] = []
    for project in PROJECTS:
        lines.extend(
            [
                "spriteType = {",
                f'\tname = "GFX_{project.image}"',
                f'\ttextureFile = "gfx/interface/bop/{project.image}.dds"',
                "}",
                "",
            ]
        )
    if lines and not lines[-1]:
        lines.pop()
    return lines


def md_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", "<br>")


def render_audit() -> str:
    lines = [
        "# 南粤建设系统：奖励与滑杆审计",
        "",
        "本文件由 tools/generate_dop_construction.py 生成。预览、本体奖励和审计表均来自同一份 REWARDS 数据，避免 GUI 文案与实际效果漂移。",
        "",
        "## 20 项奖励逐项表",
        "",
        "| ID | 项目 | 地区建设 | 社会发展 | GNG 特色 | 参考接口 | 目标州/省 | 强度依据 | 风险与上限 |",
        "|---:|---|---|---|---|---|---|---|---|",
    ]
    for project in PROJECTS:
        item = REWARDS[project.id]
        cells = (
            str(project.id),
            project.name,
            item.regional,
            item.social,
            item.gng,
            item.references,
            item.targets,
            item.strength,
            item.risk,
        )
        lines.append("| " + " | ".join(md_cell(cell) for cell in cells) + " |")

    lines.extend(
        [
            "",
            "## 滑杆口径与极值",
            "",
            "- 工程总量：1,205,000；基础速度：1,000/周。",
            "- 资金速度倍率 = 0.5 + 资金百分比 / 100；人力速度倍率 = 0.7 + 0.006 × 人力百分比；两者相乘后再乘项目额外倍率。",
            "- 资金持续支出 = 项目工程量 / 1,000,000 × 资金百分比 / 50；生产单位占用 = 项目工程量 / 100,000 × 资金百分比 / 50，所有在建项目汇总后四舍五入。",
            "- 全项目同时在建时：资金 10/50/100 分别为 0.241/1.205/2.410B 持续支出和约 2/12/24 个生产单位占用。",
            "- 资金/人力均为 10、50、100 时，基础周进度分别为 456、1,000、1,950。",
            "- 人力偏移 = (人力百分比 - 50) / 50，并按项目工程量 / 100,000 聚合。政治点维持原值，其余动员数值提高至 2 倍；最终修正有明确 clamp：每日政治点数 [-0.50, +0.20]；每周稳定度 [-0.30%, +0.08%]；每月工业专业知识 [-0.30, +0.80]；每月贫困改善 [-0.60, +0.40]；每月行政效率 [-0.50, +0.30]；三群体月度政府支持率各 [-3.00, +3.00]。",
            "- 20 项全开且人力 100 时，未 clamp 的聚合近似为每日政治点数 -0.482、每周稳定度 -0.193%、工业专业知识 +0.964、贫困 -0.603、行政 -0.482、华人 +2.892、珠人 -0.723、日侨 -2.410；超过上述边界的值由动态修正 clamp。",
            "- 20 项全开且人力 10 时，未 clamp 的聚合近似为每日政治点数 +0.386、每周稳定度 +0.154%、工业专业知识 -0.771、贫困 +0.482、行政 +0.386、华人 -2.314、珠人 +0.578、日侨 +1.928；同样由边界 clamp。",
            "- 滑杆只产生施工期间的聚合动态修正；项目完工、停工或尚未开工时不计入，不存在通过来回拖动获得永久收益的接口。",
            "",
            "## 完工累计上限",
            "",
            "- 永久全国经济修正：生产单位 +8、杂项收入 +2.90B、研究速度 +7%、战略资源获取效率 +12%、贸易协定关系修正 +10%。",
            "- 社会发展点数合计：教育水平 12、研究设施 12、农业 12、行政效率 28、工业设备 22、工业专业知识 22；贫困改善月度点数合计 0.66。",
            "- 腐败累计 -24；单一州单次最大政府支持率变化为华人 +8、珠人 +6、日侨 +4（民俗园日侨 -2）。相关 GNG helper 均在州作用域调用并由 TNO 接口结算。",
            "- 领奖路径为一次性 reward_claimed 数组保护；完成事件队列每日最多弹出一个事件。无 pending 奖励、无控制权检查、无 on_state_control_changed 发奖。",
            "",
            "## TNO 接口依据",
            "",
            "- 社会发展：common/scripted_effects/TNO_SocDev_scripted_effects.txt。",
            "- 贫困：common/scripted_effects/TNO_economy_frontend_scripted_effects.txt。",
            "- 腐败及三群体政府支持率：common/scripted_effects/TNO_Guangdong_scripted_effects.txt。",
            "- 永久全国经济收益只写入 DOP_construction_completed_assets 动态修正；施工负担只写入经济承诺和社会动员动态修正。",
            "",
        ]
    )
    return "\n".join(lines)


def render_image_map() -> str:
    lines = [
        "# 南粤建设系统：项目图像映射",
        "",
        "所有成品均由对应现实原图重新裁切至 285×551，最终 DDS 一图一文件并以原生尺寸铺满右侧栏；未使用旧版 20 帧条带、旧边框或旧成品。",
        "",
        "| ID | 项目 | 原图 | 最终 DDS | 动态 token | GFX sprite |",
        "|---:|---|---|---|---|---|",
    ]
    for project in PROJECTS:
        lines.append(
            f"| {project.id} | {project.name} | {project.source} | "
            f"gfx/interface/bop/{project.image}.dds | {project.image} | "
            f"GFX_{project.image} |"
        )
    lines.append("")
    return "\n".join(lines)


def build_outputs() -> dict[Path, tuple[str, bool]]:
    outputs: dict[Path, tuple[str, bool]] = {}

    effects, newline, bom = read_text(EFFECTS_PATH)
    effects = replace_marked(effects, REGISTRY_BEGIN, REGISTRY_END, render_registry(), newline)
    effects = replace_marked(
        effects,
        EVENT_DISPATCH_BEGIN,
        EVENT_DISPATCH_END,
        render_event_dispatch(),
        newline,
    )
    effects = replace_marked(
        effects,
        DIRECTORY_BEGIN,
        DIRECTORY_END,
        render_directory(),
        newline,
    )
    effects = replace_marked(
        effects,
        DIRECTORY_TOGGLE_BEGIN,
        DIRECTORY_TOGGLE_END,
        render_directory_toggles(),
        newline,
    )
    effects = replace_marked(
        effects,
        CLEAR_FLAGS_BEGIN,
        CLEAR_FLAGS_END,
        render_clear_flags(),
        newline,
    )
    effects = replace_marked(
        effects,
        CLEAR_EXPANSION_BEGIN,
        CLEAR_EXPANSION_END,
        render_clear_expansion_flags(),
        newline,
    )
    effects = replace_marked(
        effects,
        STATE_DISPATCH_BEGIN,
        STATE_DISPATCH_END,
        render_state_dispatch(),
        newline,
    )
    effects = replace_marked(
        effects,
        CLEAR_STATE_BEGIN,
        CLEAR_STATE_END,
        render_clear_state_flags(),
        newline,
    )
    effects = replace_marked(
        effects,
        SELECT_FIRST_BEGIN,
        SELECT_FIRST_END,
        render_select_first_shown(),
        newline,
    )
    effects = replace_marked(
        effects,
        SLIDER_RUNTIME_BEGIN,
        SLIDER_RUNTIME_END,
        render_slider_runtime(),
        newline,
    )
    effects = replace_marked(
        effects,
        CALLBACK_BEGIN,
        CALLBACK_END,
        ["# Completion callbacks are generated in DOP_construction_rewards.txt."],
        newline,
    )
    outputs[EFFECTS_PATH] = (effects, bom)

    localisation, newline, bom = read_text(LOC_PATH)
    prefix, generated = localisation.split(LOC_BEGIN, 1)
    legacy_key = re.compile(
        r"^\s*(?:DOP_construction_(?:selected_numbers|funding_label|"
        r"manpower_label|project_(?:name|desc|region)_\d+|catalog_\d+|"
        r"region_\d+)):"
    )
    prefix = newline.join(
        line.rstrip()
        for line in prefix.splitlines()
        if not legacy_key.match(line)
    )
    if prefix and not prefix.endswith(newline):
        prefix += newline
    localisation = prefix + LOC_BEGIN + generated
    localisation = replace_marked(
        localisation, LOC_BEGIN, LOC_END, render_localisation(), newline
    )
    outputs[LOC_PATH] = (localisation, bom)

    _, _, bom = read_text(EVENTS_PATH)
    outputs[EVENTS_PATH] = (render_events(), bom)
    outputs[REWARDS_PATH] = (render_rewards(), False)

    tokens, newline, bom = read_text(TOKENS_PATH)
    tokens = replace_marked(tokens, TOKENS_BEGIN, TOKENS_END, render_tokens(), newline)
    outputs[TOKENS_PATH] = (tokens, bom)

    scripted_loc, newline, bom = read_text(SCRIPTED_LOC_PATH)
    scripted_loc = replace_marked(
        scripted_loc,
        SCRIPTED_LOC_BEGIN,
        SCRIPTED_LOC_END,
        render_scripted_localisation(),
        newline,
    )
    outputs[SCRIPTED_LOC_PATH] = (scripted_loc, bom)

    gfx, newline, bom = read_text(GFX_PATH)
    gfx = replace_marked(gfx, GFX_BEGIN, GFX_END, render_gfx(), newline)
    outputs[GFX_PATH] = (gfx, bom)
    outputs[AUDIT_PATH] = (render_audit(), False)
    outputs[IMAGE_MAP_PATH] = (render_image_map(), False)
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Update the dynamic DOP construction registry and add missing stubs."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report generated drift without writing files.",
    )
    args = parser.parse_args()

    validate_data()
    outputs = build_outputs()
    changed = []
    for path, (new_text, has_bom) in outputs.items():
        old_text = read_text(path)[0] if path.exists() else ""
        if old_text == new_text:
            continue
        changed.append(path.relative_to(ROOT))
        if not args.check:
            write_text(path, new_text, has_bom)

    if changed:
        action = "would update" if args.check else "updated"
        print(f"{action}: " + ", ".join(str(path) for path in changed))
        return 1 if args.check else 0
    print("construction registry is up to date")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
