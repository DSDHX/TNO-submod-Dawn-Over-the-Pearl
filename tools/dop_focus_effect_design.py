#!/usr/bin/env python3
"""Hand-authored, focus-specific numeric designs for the DOP content pass.

These helpers exist only at migration time.  Their rendered output is written
directly into each national focus; no reusable in-game reward package remains.
Every Design declares one to three gameplay axes and a short narrative reason.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Design:
    axes: tuple[str, ...]
    rationale: str
    effects: tuple[str, ...]

    def __post_init__(self) -> None:
        if not 1 <= len(self.axes) <= 3:
            raise ValueError(f"Design must use 1-3 axes: {self.axes}")


def design(axes: str, rationale: str, *effects: str) -> Design:
    return Design(tuple(part.strip() for part in axes.split("/") if part.strip()), rationale, effects)


def pp(value: int) -> str:
    return f"add_political_power = {value}"


def stability(value: str) -> str:
    return f"add_stability = {value}"


def war_support(value: str) -> str:
    return f"add_war_support = {value}"


def command_power(value: int) -> str:
    return f"add_command_power = {value}"


def army_xp(value: int) -> str:
    return f"army_experience = {value}"


def manpower(value: int) -> str:
    return f"add_manpower = {value}"


def stockpile(equipment: str, amount: int) -> str:
    return f"add_equipment_to_stockpile = {{ type = {equipment} amount = {amount} }}"


def gdp_growth(value: str) -> str:
    return (
        f"set_temp_variable = {{ gdp_growth_temp = {value} }}\n"
        "econ_gdp_growth_change = yes"
    )


def spend(value: str) -> str:
    return (
        f"set_temp_variable = {{ temp_econ_spending_amount = {value} }}\n"
        "econ_spend_money_once_effect_raw_money = yes"
    )


def misc_income(value: str) -> str:
    return (
        f"set_temp_variable = {{ GNG_misc_income_temp = {value} }}\n"
        "GNG_misc_income_change = yes"
    )


def misc_costs(value: str) -> str:
    return (
        f"set_temp_variable = {{ GNG_misc_costs_temp = {value} }}\n"
        "GNG_misc_costs_change = yes"
    )


def social_costs(value: str) -> str:
    return (
        f"set_temp_variable = {{ GNG_social_costs_temp = {value} }}\n"
        "GNG_social_costs_change = yes"
    )


def military_costs(value: str) -> str:
    return (
        f"set_temp_variable = {{ GNG_military_costs_temp = {value} }}\n"
        "GNG_military_costs_change = yes"
    )


def admin_costs(value: str) -> str:
    return (
        f"set_temp_variable = {{ GNG_admin_costs_temp = {value} }}\n"
        "GNG_admin_costs_change = yes"
    )


def corruption(value: str) -> str:
    return (
        f"set_temp_variable = {{ GNG_corruption_temp_var = {value} }}\n"
        "GNG_Corruption_Change = yes"
    )


def japan_approval(value: str) -> str:
    return (
        f"set_temp_variable = {{ GNG_approval_temp_var = {value} }}\n"
        "GNG_Japan_approval_change = yes"
    )


def china_opinion(value: str) -> str:
    return (
        f"set_temp_variable = {{ GNG_opinion_temp_var = {value} }}\n"
        "GNG_China_opinion_change = yes"
    )


def tax(kind: str, value: str) -> str:
    if kind not in {"income", "business", "sales"}:
        raise ValueError(f"Unsupported tax kind: {kind}")
    return (
        f"set_temp_variable = {{ {kind}_tax_temp = {value} }}\n"
        f"econ_{kind}_tax_rate_change = yes"
    )


def socdev(effect: str) -> str:
    return f"TNO_{effect} = yes"


def building(state: int, building_type: str, level: int = 1, slots: int = 0) -> str:
    lines = [
        f"{state} = {{",
        "\tadd_building_construction = {",
        f"\t\ttype = {building_type}",
        f"\t\tlevel = {level}",
        "\t\tinstant_build = yes",
        "\t}",
    ]
    if slots:
        lines.append(f"\tadd_extra_state_shared_building_slots = {slots}")
    lines.append("}")
    return "\n".join(lines)


def scw(production: str, competition: str) -> str:
    return (
        "set_temp_variable = { faction_id_t = 1 }\n"
        f"set_temp_variable = {{ DOP_SCW_production_scale_change = {production} }}\n"
        f"set_temp_variable = {{ DOP_SCW_competition_change = {competition} }}\n"
        "DOP_SCW_change_production_and_competition = yes"
    )


# A list, rather than a dict literal, lets the migration audit duplicate IDs.
DESIGN_ROWS: list[tuple[str, Design]] = [
    # Opening: recovery, overseas markets and quiet rearmament.
    ("DOP_GNG_year_of_the_rain", design("警觉/信心", "风暴预警提高戒备，却令社会略感不安", war_support("0.02"), stability("-0.005"))),
    ("DOP_GNG_res_from_oc", design("行政/财政", "恢复秩序需要一次性拨款并改善行政动员", socdev("improve_admin_efficiency_really_low"), spend("0.035"))),
    ("DOP_GNG_regen_econ", design("增长/财政", "重连商业网络直接带动增长与杂项收入", gdp_growth("0.18"), misc_income("0.025"))),
    ("DOP_GNG_wrecking_world", design("外贸/廉价商品", "抢占危机后市场带来收入，也以低价商品缓解贫困", misc_income("0.03"), socdev("improve_poverty_low"))),
    ("DOP_GNG_pan_thai_bay", design("增长/东京关系/投资", "环泰国湾投资扩大市场并符合共荣圈利益", gdp_growth("0.14"), japan_approval("1"), spend("0.04"))),
    ("DOP_GNG_gd_mex_col", design("外贸/东京关系", "墨西哥渠道打开北美市场，却会引起东京疑虑", misc_income("0.04"), japan_approval("-1"))),
    ("DOP_GNG_expand_d", design("科研/财政", "索尼以研发投入换取产品换代能力", socdev("improve_research_facilities_low"), spend("0.055"))),
    ("DOP_GNG_lower_barrier", design("增长/腐败/稳定", "翻热股市刺激资本流入，也放大投机和寻租", gdp_growth("0.10"), corruption("0.5"), stability("-0.01"))),
    ("DOP_GNG_rightous_def", design("备战/社会", "低调防卫提高战意，但战争传言侵蚀安定", war_support("0.03"), stability("-0.01"))),
    ("DOP_GNG_rearm_pol", design("警务专业化/军费", "警务处重新武装并承担持续装备费用", socdev("improve_army_professionalism_low"), military_costs("0.015"))),
    ("DOP_GNG_cps_info_co", design("情报/廉洁", "情报协作强化东京关系，也扩大灰色操作空间", corruption("0.35"))),
    ("DOP_GNG_fill_resp_troops", design("训练/军费", "对策部队在既有装备之外获得正规训练和预算", army_xp(8), military_costs("0.01"))),
    ("DOP_GNG_reiterate_our_pos", design("东京关系/南京关系", "重申地位协定安抚日本，却令中国更加不满", japan_approval("2"), china_opinion("-1"))),
    ("DOP_GNG_army_of_gadfly", design("作战经验/动员", "袭扰战术依赖小单位经验与临机指挥", army_xp(18), command_power(20))),

    # Pre-war: three focuses previously still called generic packages.
    ("beating_drums", design("军队专业化", "战鼓渐响促成一次战前训练整顿", socdev("improve_army_professionalism_low"))),
    ("collaborate_in_shadow", design("治安/民意/腐败", "警民合作改善秩序，但秘密协作留下寻租空间", stability("0.02"), corruption("0.25"), pp(10))),
    ("defend_the_great_gwongdung", design("本土防卫", "现有战意、经验与指挥力已完整体现守乡动员")),

    # Reconstruction: recovery and the staged return of Guangdong mechanics.
    ("GNG_focus_everlasting_peace", design("稳定/贫困/重建开支", "停战首先恢复社会信心并救济受灾者", stability("0.03"), socdev("improve_poverty_low"), spend("0.06"))),
    ("GNG_focus_temporary_relief", design("救济/社会预算", "临时喘息以更高社会支出换取贫困改善", socdev("improve_poverty_low"), social_costs("0.02"))),
    ("GNG_focus_foothold", design("行政/稳定", "重新掌握疆域资料后，地方行政和信心率先恢复", socdev("improve_admin_efficiency_really_low"), stability("0.01"))),
    ("GNG_focus_retrieve_the_cable", design("电力/财政", "修复电网需要直接建设与专项拨款", building(1438, "thermoelectric_plant", 1, 1), spend("0.045"))),
    ("GNG_focus_leave_ruins_behind", design("重建投资/增长", "建设总署启动即形成投资需求和复苏预期", spend("0.065"), gdp_growth("0.10"))),
    ("GNG_focus_in_the_warm_sun", design("外资/东京关系/增长", "日侨资本回流与珠人补贴共同托起复苏", misc_income("0.03"), japan_approval("2"), gdp_growth("0.08"))),
    ("GNG_focus_neon_signs_lit_up", design("工业设备/增长", "生产线复工改善设备利用并盘活内部市场", socdev("improve_industrial_equipment_low"), gdp_growth("0.14"))),
    ("GNG_focus_gazing_into_abyss", design("灰色收入/腐败/稳定", "极道资本带来现金，也让腐败和不安重返街头", misc_income("0.025"), corruption("0.75"), stability("-0.01"))),
    ("DOP_GNG_recon_economic_conference", design("声望/增长/东京关系", "主办经济大会提高政治声望并吸引共荣圈订单", pp(25), gdp_growth("0.12"), japan_approval("2"))),
    ("DOP_GNG_recon_status_agreement", design("主权/中日关系/军队", "保留自卫队改善广东筹码，却同时冒犯东京", japan_approval("-2"), china_opinion("1"), socdev("improve_army_professionalism_low"))),
    ("GNG_focus_new_products_old_friends", design("产品研发/增长", "重启产品周期使研发和旧市场同时恢复", socdev("improve_research_facilities_low"), gdp_growth("0.10"))),
    ("DOP_GNG_recon_foundation", design("芯片研发/财政", "芯片冷战开局必须用真实研发投入换取能力", socdev("improve_research_facilities_low"), spend("0.075"))),
    ("DOP_GNG_recon_backwardness_disaster", design("教育/科研/财政", "科学院以教育与研究设施的双重投入起步", socdev("improve_academic_base_low"), socdev("improve_research_facilities_low"), spend("0.08"))),
    ("DOP_GNG_recon_swarming_investors", design("资本流入/腐败", "蜂拥而至的投资者提高收入，也助长寻租", misc_income("0.04"), corruption("0.5"))),
    ("DOP_GNG_recon_leave_nothing_out", design("工业专长/科研", "细大无遗的产业盘点同时积累工艺与研究经验", socdev("improve_industrial_expertise_low"), socdev("improve_research_facilities_low"))),
    ("DOP_GNG_recon_first_trial", design("芯片竞赛/增长", "首轮产业试验形成可量化的芯片进展和新订单", scw("3", "0.015"), gdp_growth("0.08"))),
    ("DOP_GNG_recon_no_time_to_turn", design("经济治理/增长", "面对中国经济比较，行政体系开始按数据调度增长", socdev("improve_admin_efficiency_low"), gdp_growth("0.09"))),
    ("GNG_focus_corporate_voraciousness", design("增长/贫困/腐败", "企业吞食补贴换来增长，却把成本转嫁给劳动者", gdp_growth("0.18"), socdev("worsen_poverty_low"), corruption("0.5"))),
    ("GNG_focus_trade_union_highly_vigilant", design("贫困/稳定/社会预算", "工会监督迫使政府以预算换取工人生活改善", socdev("improve_poverty_low"), stability("0.02"), social_costs("0.02"))),
    ("DOP_GNG_recon_civilian_officials", design("行政/廉洁/财政", "文官体系恢复办事能力并压低腐败，但需重建经费", socdev("improve_admin_efficiency_low"), corruption("-0.5"), spend("0.04"))),
    ("DOP_GNG_recon_flying_geese", design("增长/工业专长/投资", "雁式转移扩大两广产能并积累产业组织经验", gdp_growth("0.22"), socdev("improve_industrial_expertise_low"), spend("0.07"))),
    ("DOP_GNG_recon_opening_ceremony", design("稳定/收入/行政", "揭幕式宣布重建收官并恢复政府与投资者信心", stability("0.03"), misc_income("0.03"), socdev("improve_admin_efficiency_really_low"))),
]

