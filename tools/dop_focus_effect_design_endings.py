#!/usr/bin/env python3
"""Hand-authored focus effects for the three normal DOP endings."""

from dop_focus_effect_design import (
    Design,
    admin_costs,
    building,
    china_opinion,
    corruption,
    design,
    gdp_growth,
    japan_approval,
    misc_income,
    pp,
    scw,
    social_costs,
    socdev,
    spend,
    stability,
    tax,
)


ENDING_DESIGN_ROWS: list[tuple[str, Design]] = [
    # Lee / Cheung Kong ending: a deliberately positive social-democratic arc.
    ("GNG_focus_the_wind_is_gentle", design("稳定/贫困/行政", "惠风和畅意味着安定、民生与常态治理同步回归", stability("0.05"), socdev("improve_poverty_low"), socdev("improve_admin_efficiency_low"))),
    ("GNG_focus_the_forgotten", design("贫困/社会预算/稳定", "把被遗忘者纳入保障，需以长期预算换取团结", socdev("improve_poverty_med"), social_costs("0.028"), stability("0.025"))),
    ("GNG_focus_disaster_response_department", design("行政/医疗/财政", "灾害部门结合应急行政、医疗能力与一次性建设", socdev("improve_admin_efficiency_low"), socdev("improve_healthcare_low"), spend("0.055"))),
    ("GNG_focus_policy_report_system", design("行政/廉洁/政治资本", "施政报告提高透明度、执行力和政府公信力", socdev("improve_admin_efficiency_med"), corruption("-1"), pp(30))),
    ("GNG_focus_chinese_chief_secretary", design("南京关系/行政支出/稳定", "华人布政司改善基层服从并减轻管理摩擦", china_opinion("3"), admin_costs("-0.015"), stability("0.02"))),
    ("GNG_focus_feed_back_china", design("南京关系/增长/贫困", "华南复苏让难民返乡、市场重开并改善生计", china_opinion("4"), gdp_growth("0.14"), socdev("improve_poverty_low"))),
    ("GNG_focus_all_eyes_on", design("稳定/廉洁/政治资本", "万众瞩目转化为信任，也迫使政府保持克制", stability("0.04"), corruption("-0.5"), pp(35))),
    ("GNG_focus_cultural_affairs_bureau", design("稳定/社会预算/教育", "公共文化服务增加认同与学习机会，也需要经常预算", stability("0.03"), social_costs("0.014"), socdev("improve_academic_base_low"))),
    ("GNG_focus_guangdong_stocks_rejuvenation", design("财政收入/东京关系/腐败", "广股援助东京带来金融收益和政治善意，也滋生内幕空间", misc_income("0.055"), japan_approval("2"), corruption("0.35"))),
    ("GNG_focus_fill_with_laughter", design("贫困/稳定/增长", "廉价索尼产品把消费繁荣真正送入普通家庭", socdev("improve_poverty_low"), stability("0.045"), gdp_growth("0.10"))),
    ("GNG_focus_equal_competition", design("廉洁/工业专长/增长", "反垄断提高长期产业质量，却牺牲短期扩张", corruption("-2"), socdev("improve_industrial_expertise_low"), gdp_growth("-0.035"))),
    ("GNG_focus_a_place_for_all", design("稳定/贫困/南京关系", "容身之地以强力社会团结和民生改善收束长实结局", stability("0.08"), socdev("improve_poverty_med"), china_opinion("4"))),

    # Ibuka / Fujitsu ending: a positive research and industrial modernisation arc.
    ("GNG_focus_the_ultimate_enemy", design("科研/增长/东京关系", "以日本为最终标杆推动科研和增长，也公开挑战宗主", socdev("improve_research_facilities_med"), gdp_growth("0.15"), japan_approval("-2"))),
    ("GNG_focus_never_look_back", design("行政/廉洁/政治资本", "风险复盘清理低效环节并集中改革授权", socdev("improve_admin_efficiency_med"), corruption("-0.75"), pp(25))),
    ("GNG_focus_risk_clearance", design("廉洁/财政收入/稳定", "金融风险出清增强稳定，却压低一部分投机收入", corruption("-1.25"), misc_income("-0.018"), stability("0.025"))),
    ("GNG_focus_industrial_nation", design("工业设备/工业专长/增长", "实业之国同时更新设备、知识与实体产出", socdev("improve_industrial_equipment_high"), socdev("improve_industrial_expertise_med"), gdp_growth("0.20"))),
    ("GNG_focus_reform_inefficient_administration", design("行政/行政支出/稳定", "全面电子政务显著提高效率并削减经常支出", socdev("improve_admin_efficiency_high"), admin_costs("-0.03"), stability("0.015"))),
    ("GNG_focus_end_of_poverty", design("贫困/社会预算/增长", "最低生活保障强力减贫，成本由繁荣经济承担", socdev("improve_poverty_high"), social_costs("0.04"), gdp_growth("0.06"))),
    ("GNG_focus_never_stop", design("教育/科研/财政", "永不停歇的创新需要最好的学术基础和持续投入", socdev("improve_academic_base_med"), socdev("improve_research_facilities_high"), spend("0.11"))),
    ("GNG_focus_rise_of_silicon", design("芯片竞赛/工业专长/增长", "硅市成为广东高科技增长的核心发动机", scw("10", "0.035"), socdev("improve_industrial_expertise_med"), gdp_growth("0.21"))),
    ("GNG_focus_supercomputer_center", design("科研/行政/财政", "超级电脑同时服务科研与危机治理，建设代价高昂", socdev("improve_research_facilities_high"), socdev("improve_admin_efficiency_med"), spend("0.14"))),
    ("GNG_focus_academic_golden_age", design("教育/科研/财政", "学术黄金时代以高等教育和研究经费共同维系", socdev("improve_academic_base_high"), socdev("improve_research_facilities_med"), spend("0.095"))),
    ("GNG_focus_laying_the_foundation_for_kouu", design("科研/行政/增长", "网络番组链接科研、政府与企业通信", socdev("improve_research_facilities_med"), socdev("improve_admin_efficiency_low"), gdp_growth("0.11"))),
    ("GNG_focus_onward_to_Tomorrow", design("稳定/增长/贫困", "致明日以科技繁荣、社会信心和共享成果收束结局", stability("0.065"), gdp_growth("0.25"), socdev("improve_poverty_med"))),

    # Finance ending: growth and cash remain real, but ordinary people pay.
    ("GNG_focus_weak_up_from_dream", design("增长/腐败/贫困", "从繁荣幻梦醒来时，账面增长仍由腐败和贫困支撑", gdp_growth("0.19"), corruption("1"), socdev("worsen_poverty_low"))),
    ("GNG_focus_falling_pices", design("增长/稳定/政治资本", "派系分裂中仍强撑增长，但政府威信迅速流失", gdp_growth("0.09"), stability("-0.04"), pp(-25))),
    ("GNG_focus_fool_cheung_kong", design("南京关系/财政收入/稳定", "向长实和富士通让步略缓矛盾，却损失部分财政收益", china_opinion("1"), misc_income("-0.018"), stability("0.012"))),
    ("GNG_focus_show_the_fang", design("稳定/贫困/腐败", "劳资与族裔伤口重开，社会代价全面显现", stability("-0.035"), socdev("worsen_poverty_med"), corruption("0.5"))),
    ("GNG_focus_fujitsu_s_ridiculous", design("财政收入/腐败/贫困", "新朋友以利益换支持，国库受益而人民继续承压", misc_income("0.05"), corruption("1.25"), socdev("worsen_poverty_low"))),
    ("GNG_focus_the_lord_of_east", design("增长/东京关系/南京关系", "外交重审优先保住日本市场，并进一步疏远中国", gdp_growth("0.10"), japan_approval("1"), china_opinion("-2"))),
    ("GNG_focus_is_sony_ruling_the_guangdong", design("行政/廉洁/政治资本", "监督部门恢复部分效率和廉洁，为盛田集中权力", socdev("improve_admin_efficiency_low"), corruption("-0.5"), pp(30))),
    ("GNG_focus_guangdong_manchuria_friendship_agreement", design("行政/腐败/政治资本", "忠诚内环提高决策效率，也制度化裙带关系", socdev("improve_admin_efficiency_low"), corruption("1"), pp(40))),
    ("GNG_focus_who_is_the_chief_executive", design("税制/财政收入/腐败", "向基本盘抛出减税胡萝卜，换取现金和依附", tax("business", "-0.012"), misc_income("0.04"), corruption("0.75"))),
    ("GNG_focus_building_inner_ring_system", design("增长/财政收入/贫困", "保障投资者信用维持高增长，代价继续落在底层", gdp_growth("0.30"), misc_income("0.055"), socdev("worsen_poverty_low"))),
    ("GNG_focus_destroy_the_source_of_chaos", design("稳定/南京关系/腐败", "挥舞大棒暂时压住反对派，却恶化华人关系和法外寻租", stability("0.02"), china_opinion("-3"), corruption("1.5"))),
    ("GNG_focus_guangdong_awake", design("增长/稳定/腐败", "角斗场仍能榨出利润，但国家陷入不稳和寡头黑箱", "DOP_GNG_set_status_finance = yes", gdp_growth("0.22"), stability("-0.06"), corruption("2"))),
]
