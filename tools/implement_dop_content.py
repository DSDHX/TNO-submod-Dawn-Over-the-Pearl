from __future__ import annotations
import argparse,re
from pathlib import Path

NAME_FIXES={
"DOP_GNG_reiterate_our_pos":"重申《地位协定》",
"GNG_focus_amend_ethnic_regulation":"修约民族条例",
"GNG_focus_cooperate_with_GFT":"与广工联合作",
"GNG_focus_stick_and_carrot":"胡萝卜和大棒",
"GNG_focus_forget_it":"让他们忘了这一茬",
"GNG_focus_local_power_re_decide":"民主之唤",
"GNG_focus_local_power_loss":"基层部分民主",
"GNG_focus_good_job":"政通人和",
"DOP_GNG_Guangdong_New_Railway":"广东新干线企划",
"GNG_focus_build_Joint_Campus":"建立索尼富士通联合创新园区",
"GNG_focus_Secret_Force_May":"秘密实动部队“梅”",
"GNG_focus_force_major_terrorism":"应对特大恐怖袭击事件...",
"GNG_focus_CK_want_pie":"长江实业也来分杯羹",
"GNG_focus_Air_Self_Defense_Forces":"我们的翅膀，航空自卫队",
"GNG_focus_set_recruitment_mechanism":"完善人员征募机制",
"GNG_focus_mature_military_products":"引进成熟工业产品",
"GNG_focus_level_up_equipment":"提升装备水平",
"GNG_focus_cultural_affairs_bureau":"康乐及文化事务属",
"GNG_focus_reduce_the_budget_of_product_cycle":"削减产品周期拨款",
"GNG_focus_laying_the_foundation_for_kouu":"网络番组全面链接",
"GNG_focus_think_about_good":"往好处想嘛...",
}

WARTIME_NAMES=[
"战鼓渐响","固守待援","乱世需用重典","东京速递","扩大适役人口范围","警民合作","何惜百死卫吾乡",
"来自盟友的援助","加强北方防御","扩大军警招募","收买极道","分化三合会","效忠自有奖赏",
"财政捉襟见肘……","不忘立足之本","火烧眉头","保障物资供应","民用工业军事化",
"此乃吾等家园……","……为广东之存继……","……我们死而后已！"]
WARTIME_IDS=[
"GNG_focus_black_cloud_roming","GNG_focus_a_state_of_unstay","GNG_focus_allow_chinese_escape",
"GNG_focus_zhujin_loyalty","GNG_focus_japanese_support","GNG_focus_walking_on_tightrope",
"GNG_focus_prepare_never_stop","GNG_focus_until_the_end","GNG_focus_deployment_special_police",
"GNG_focus_train_triads","GNG_focus_never_surrunder","GNG_focus_ahead_uncertain",
"DOP_GNG_wartime_loyalty_rewards","DOP_GNG_wartime_finance_strained","DOP_GNG_wartime_civil_foundation",
"DOP_GNG_wartime_fire_at_brows","DOP_GNG_wartime_supply","DOP_GNG_wartime_militarize_civilian_industry",
"DOP_GNG_wartime_our_home","DOP_GNG_wartime_for_future","DOP_GNG_wartime_until_death"]

RECON_NAMES=[
"永远的和平？","……或暂时的喘息","我们脚下的家园","拾起电缆","霓虹荧屏再亮","走出残垣断壁",
"围栏与关口","沐浴暖阳之下","凝视深渊之中","（年份）年共荣圈经济大会","地位协定重议定",
"新产品，老朋友","立身之本","群蚁附膻","细大无遗","落后即灾难","新硎初试","计不旋踵",
"丰墙硗下","企业狼吞虎咽","工会目光灼灼","文官登台亮相","广东的雁式经济","开幕式",
"开工！","回归平凡的日常","预备权力下放","向西行……","人才再投资","驻军退潮时",
"资源出口计划表","笨蛋！问题是经济！","增进本地行政效能","内地的日用品与房屋"]
RECON_NEW={
"（年份）年共荣圈经济大会":"DOP_GNG_recon_economic_conference",
"地位协定重议定":"DOP_GNG_recon_status_agreement",
"立身之本":"DOP_GNG_recon_foundation",
"群蚁附膻":"DOP_GNG_recon_swarming_investors",
"细大无遗":"DOP_GNG_recon_leave_nothing_out",
"落后即灾难":"DOP_GNG_recon_backwardness_disaster",
"新硎初试":"DOP_GNG_recon_first_trial",
"计不旋踵":"DOP_GNG_recon_no_time_to_turn",
"丰墙硗下":"DOP_GNG_recon_grand_wall_weak_foundation",
"文官登台亮相":"DOP_GNG_recon_civilian_officials",
"广东的雁式经济":"DOP_GNG_recon_flying_geese",
"开幕式":"DOP_GNG_recon_opening_ceremony",
}
RECON_ALIAS={"拾起电缆":"GNG_focus_retrieve_the_cable","工会目光灼灼":"GNG_focus_trade_union_highly_vigilant"}

FINANCE_NAMES=["阴影之下","分崩离析","老搭档的不满","伤口再度撕裂","新朋友的贪婪","对外联系重审视","监督各部门","建立内环","抛出胡萝卜","保持经济增长","挥舞大棒","众企业的角斗场"]

SPIRITS={
"DOP_GNG_first_national_crisis":("第一次国难","这是广东第一次作为一个国家实体面对直接的外部军事冲击，我们与广西军阀漫长的微妙平衡终于随着一场盛大的地缘危机而彻底破裂。战场上的鲜血注定会浇灌出集体记忆与伤痕；从这场劫难中活下来的，都会成为广东的孩子。","GNG_state_path"),
"DOP_GNG_lingnan_spring":("岭南之春","卷入战争并非广东之愿，她却也因此收复法定疆界并获得广西的开发权。熬过风霜后，这个以经济实验为立国之本的政权迎来了属于它的春天；百花争艳之时，潜藏的蠹虫也不会缺席。","GNG_silicon_years"),
"DOP_GNG_status_lee":("反认他乡是故乡","盛田昭夫与李嘉诚始终站在一起，将这片土地重新变成一个可以称作家的港湾。索尼与长实推动本土企业发展，也让珠人与华人得到了本应属于他们的权利。","GNG_state_path"),
"DOP_GNG_status_ibuka":("还有明天","盛田终于舍得同井深大重修旧好。尽管不一定事事如愿，但为了广东，他们还有明天，广东也还有明天。","GNG_ibuka_path"),
"DOP_GNG_status_finance":("狮子山日暮","恐袭之后，立法会前所未有地离心离德。太阳从狮子山上落下，失去增长的广东将被她的孩子们撕扯、分割，迎来黑暗时代。","GNG_hitachi_path"),
"DOP_GNG_status_1962":("重奏1962序曲","历史从不重复自己的舞蹈，却总押着相似的韵脚。广东的地主从迷茫中苏醒，誓要重新占有这片土地生长出来的一切。","GNG_martial_law"),
"DOP_GNG_status_second_riot":("铅色年华","这是铅一样沉重的年代。宵禁与戒严一日又一日，自卫队与民族主义者从高楼对峙到群山，无数人的家乡在炸弹火光中化为飞灰。","GNG_the_guangdong_riots"),
"DOP_GNG_security_southwest_war":("西南战争安保","西南战争期间的紧急安保体制。","GNG_security_the_militarized_state"),
"DOP_GNG_security_postwar":("战后安保","战后重整中的广东安保体系。","GNG_security_transitional_security_apparatus"),
"DOP_GNG_security_reformed":("军改成功安保","完成军警改革后的广东安保体系。","GNG_security_the_guangdong_network"),
"DOP_GNG_integrity_waltz":("珠江圆舞曲","嗒、嗒、嗒。秩序和发展是社会的主旋律，全世界投资者的目光都聚焦在行政长官和他的同僚身上。","GNG_fiscal_sound"),
"DOP_GNG_integrity_chorus":("多声部合唱","行政长官的指挥棒调动着整个社会。尽管偶有错拍，总体而言一切仍在掌握之中。","GNG_fiscal_caution"),
"DOP_GNG_integrity_dissonance":("不和谐音","演出错漏百出，演员动作生硬，观众开始窃窃私语，贵宾席的耐心也正在被消磨。","GNG_fiscal_warning"),
"DOP_GNG_integrity_chaos":("鸡飞狗跳","演员随心所欲的动作造成全面混乱，行政长官的指挥已被忽视，观众正失望离场。","GNG_fiscal_emergency"),
"DOP_GNG_identity_initial":("南国乡愁","广东的民族问题随着中日关系紧张而激化。华人坚持旧有认同，珠人也未能与原本身份完全切割。","GNG_between_two_worlds"),
"DOP_GNG_identity_dual":("枯叶的漫漫归途","立法会将华人与珠人一并确认为法律上的主体民族，为民族问题留下了回旋余地。","GNG_state_path"),
"DOP_GNG_identity_zhujin":("新生儿的啼哭","立法会确立珠人为广东的主体民族，并制定界定珠人身份的政策；新的认同更稳定，也会激怒大量华人。","GNG_state_path"),
"DOP_GNG_wartime_triangle":("战火中的珠三角","战争正在撕裂广东的社会、财政和政治机器。","GNG_yasuda_crisis"),
"DOP_GNG_strangle_guerrillas":("绞杀游击队","广警与自卫队将切断游击队同农村社会之间的联系。","GNG_security_blunt_force_policing"),
"DOP_GNG_civil_priority":("民事优先","政府优先维持社会运转与民用物资供应。","GNG_silicon_years"),
"DOP_GNG_civil_priority_supply":("民事优先：保障供应","民事预算正在反哺前线，供应链也得到改善。","GNG_silicon_years"),
"DOP_GNG_military_priority":("军事优先","政府将有限的预算优先交给前线。","GNG_south_china_area_army"),
"DOP_GNG_military_priority_industry":("军事优先：工业军事化","发达的民营工业正在转向军需生产。","GNG_south_china_area_army"),
}

def norm(s):
    return re.sub(r"[，。！？…·、《》“”‘’（）() \t]","",s).lower()
def esc(s):
    s=s.replace("\r", "").replace("\n", "\\n")
    s=re.sub(r'\\+n', r'\\n', s)
    return re.sub(r'\\*"', r'\\"', s)
def readloc(root):
    out={}
    pat=re.compile(r'^\s*([^\s:#]+):\d*\s+"(.*)"\s*$')
    for p in (root/"localisation"/"simp_chinese").glob("*.yml"):
        for line in p.read_text(encoding="utf-8-sig",errors="replace").splitlines():
            m=pat.match(line)
            if m:out[m.group(1)]=m.group(2)
    return out
def focusblocks(path):
    text=path.read_text(encoding="utf-8-sig")
    out={}
    pos=0
    while True:
        m=re.search(r"(?m)^\s*shared_focus\s*=\s*\{",text[pos:])
        if not m:break
        start=pos+m.start(); i=pos+m.end(); depth=1
        while i<len(text) and depth:
            depth+=text[i].count("{")-text[i].count("}");i+=1
        block=text[start:i];im=re.search(r"(?m)^\s*id\s*=\s*([^\s#}]+)",block)
        if im:out[im.group(1)]=block
        pos=i
    return out
MISSING_ICONS = {"GFX_GNG_focus_ahead_uncertain","GFX_GNG_focus_allow_chinese_escape","GFX_GNG_focus_building_inner_ring_system","GFX_GNG_focus_corporate_voraciousness","GFX_GNG_focus_decentralization_authority","GFX_GNG_focus_destroy_the_source_of_chaos","GFX_GNG_focus_fool_cheung_kong","GFX_GNG_focus_garrison_withdrew","GFX_GNG_focus_gazing_into_abyss","GFX_GNG_focus_get_to_work","GFX_GNG_focus_go_west","GFX_GNG_focus_guangdong_awake","GFX_GNG_focus_in_the_warm_sun","GFX_GNG_focus_is_sony_ruling_the_guangdong","GFX_GNG_focus_japanese_support","GFX_GNG_focus_problem_is_economy","GFX_GNG_focus_promote_local_efficacy","GFX_GNG_focus_reinvestment_talents","GFX_GNG_focus_resource_export_plan","GFX_GNG_focus_temporary_relief","GFX_GNG_focus_trade_union_highly_vigilant","GFX_GNG_focus_weak_up_from_dream","GFX_GNG_focus_zhujin_loyalty"}
MISSING_ICONS.update({"GFX_GNG_focus_academic_golden_age","GFX_GNG_focus_adults_forgetting_histor","GFX_GNG_focus_aftermath_of_no_confidence_vote","GFX_GNG_focus_call_of_IJA","GFX_GNG_focus_chinese_chief_secretary","GFX_GNG_focus_contract_tycoon_s_political_power","GFX_GNG_focus_cultural_affairs_bureau","GFX_GNG_focus_erase_organized_crime","GFX_GNG_focus_feed_back_china","GFX_GNG_focus_grasping_executive_authority","GFX_GNG_focus_halt_unnecessary_spending","GFX_GNG_focus_industrial_restructing_and_antimonopoly_act","GFX_GNG_focus_is_order_prevails_in_guangdong","GFX_GNG_focus_laying_the_foundation_for_kouu","GFX_GNG_focus_level_up_equipment","GFX_GNG_focus_meet_up_with_new_Japanese_bureaucrats","GFX_GNG_focus_never_look_back","GFX_GNG_focus_never_stop","GFX_GNG_focus_normalize_curfew_policy","GFX_GNG_focus_onward_to_Tomorrow","GFX_GNG_focus_personal_safety_of_the_japanese","GFX_GNG_focus_policy_report_system","GFX_GNG_focus_population_of_chinese","GFX_GNG_focus_prison_of_enterprises","GFX_GNG_focus_property_safety_of_the_zhujin","GFX_GNG_focus_reduce_the_budget_of_product_cycle","GFX_GNG_focus_reform_inefficient_administration","GFX_GNG_focus_risk_clearance","GFX_GNG_focus_samurais_kirisute_gomen","GFX_GNG_focus_state_of_guangdong_in_emergency","GFX_GNG_focus_tear_the_capital_and_trade_union","GFX_GNG_focus_the_forgotten","GFX_GNG_focus_the_ultimate_enemy","GFX_GNG_focus_while_adolescence_losing_homeland","GFX_GNG_foucs_tear_the_capital_and_trade_union","GFX_gal_unknown"})
MISSING_ICONS.update({"DOP_GNG_Build_New_villages_gfx","DOP_GNG_Cotton_Medical_Insurance_gfx","DOP_GNG_Guangdong_Modernized_gfx","DOP_GNG_Guangdong_New_Curriculum_gfx","DOP_GNG_Industrial_Upgrade_gfx","DOP_GNG_Lay_Infrastructure_gfx","DOP_GNG_Look_Inland_gfx","DOP_GNG_New_Livelihood_Project_gfx","DOP_GNG_North_Guangdong_Heavy_Industry_gfx","DOP_GNG_Not_Only_Pearl_River_Delta_gfx","DOP_GNG_Other_Possibility_Guangzhou_Bay_gfx","DOP_GNG_Passenger_Railway_Company_gfx","DOP_GNG_Public_Housing_Construction_gfx","DOP_GNG_Rural_Credit_Bank_gfx","DOP_GNG_Rural_Crisis_gfx","DOP_GNG_Seek_Granary_gfx","DOP_GNG_Urban_Issue_gfx","DOP_GNG_Wealthy_Citizens_gfx","DOP_GNG_West_Guangdong_Resources_gfx","DOP_GNG_army_of_gadfly_gfx","DOP_GNG_cps_info_co_gfx","DOP_GNG_deal_w_labors_gfx","DOP_GNG_expand_d_gfx","DOP_GNG_faux_opening_gfx","DOP_GNG_fill_resp_troops_gfx","DOP_GNG_gd_mex_col_gfx","DOP_GNG_legal_compromise_gfx","DOP_GNG_lower_barrier_gfx","DOP_GNG_maoming_ins_gfx","DOP_GNG_more_jobs_gfx","DOP_GNG_pan_thai_bay_gfx","DOP_GNG_rearm_pol_gfx","DOP_GNG_regen_econ_gfx","DOP_GNG_reiterate_our_pos_gfx","DOP_GNG_res_from_oc_gfx","DOP_GNG_rightous_def_gfx","DOP_GNG_save_unemp_gfx","DOP_GNG_wrecking_world_gfx","DOP_GNG_year_of_the_rain_gfx"})
def iconof(block,default="GFX_GNG_focus_a_state_of_unstay"):
    m=re.search(r"(?m)^\s*icon\s*=\s*([^\s#}]+)",block or "")
    icon=m.group(1) if m else default
    return default if icon in MISSING_ICONS else icon
def rewardof(block):
    if not block:return []
    m=re.search(r"completion_reward\s*=\s*\{",block)
    if not m:return []
    i=m.end();start=i;depth=1
    while i<len(block) and depth:
        depth+=block[i].count("{")-block[i].count("}");i+=1
    body=block[start:i-1].splitlines()
    non=[len(x)-len(x.lstrip()) for x in body if x.strip()]
    cut=min(non) if non else 0
    return [x[cut:].rstrip() for x in body if x.strip()]
def docdesc(path):
    if not path.exists():return ""
    ls=[x.strip() for x in path.read_text(encoding="utf-8-sig").splitlines() if x.strip()]
    body=[]
    for x in ls[1:]:
        if x.startswith("效果"):break
        body.append(x)
    return "\n\n".join(body)
def sectiondoc(path,heads):
    ls=[x.strip() for x in path.read_text(encoding="utf-8-sig").splitlines() if x.strip()]
    out={}
    positions={h:ls.index(h) for h in heads if h in ls}
    for h,i in positions.items():
        a=i+1
        b=min([j for j in positions.values() if j>i] or [len(ls)])
        out[h]="\\n\\n".join(ls[a:b])
    return out
def tree_text(tree_id,items,cols=7):
    root=items[0]["id"]
    out=["focus_tree = {",f"\tid = {tree_id}","\tcountry = { factor = 0 modifier = { add = 10 tag = GNG } }","\tdefault = no",f"\tshared_focus = {root}","}",""]
    for i,it in enumerate(items):
        out+=["shared_focus = {",f"\tid = {it['id']}",f"\ticon = {it['icon']}"]
        if i==0:out+=["\tx = 8","\ty = 0"]
        else:
            j=i-1;row=j//cols+1;col=j%cols;x=(col-(cols//2))*2
            parent=0 if row==1 else 1+(row-2)*cols+col
            if parent>=i:parent=i-1
            out += [f"\trelative_position_id = {root}",f"\tx = {x}",f"\ty = {row}",f"\tprerequisite = {{ focus = {items[parent]['id']} }}"]
        out.append(f"\tcost = {it.get('cost',1)}")
        out.append("\tcompletion_reward = {")
        out += ["\t\t"+x for x in it.get("reward",[])]
        out += ["\t}","}",""]
    return "\n".join(out)
def write_tree(root,path,locpath,tree_id,tree_name,items,cols=7):
    path.write_text(tree_text(tree_id,items,cols),encoding="utf-8")
    ls=["l_simp_chinese:",f' {tree_id}:0 "{esc(tree_name)}"']
    for it in items:
        ls += [f' {it["id"]}:0 "{esc(it["name"])}"',f' {it["id"]}_desc:0 "{esc(it.get("desc",""))}"']
    locpath.write_text("\n".join(ls)+"\n",encoding="utf-8-sig")
def event_reward(eid):
    return [f"country_event = {{ id = {eid} days = 1 }}"]
def fix_missing_focus_icons(root):
    pattern=re.compile(r"(?m)^(\s*icon\s*=\s*)([A-Za-z0-9_]+)")
    for path in (root/"common"/"national_focus").glob("*.txt"):
        source=path.read_text(encoding="utf-8-sig")
        updated=pattern.sub(lambda match: (match.group(1)+"GFX_GNG_focus_a_state_of_unstay") if match.group(2) in MISSING_ICONS else match.group(0),source)
        if updated != source:
            path.write_text(updated,encoding="utf-8")
def fix_names(root):
    for p in (root/"localisation"/"simp_chinese").glob("*.yml"):
        raw=p.read_text(encoding="utf-8-sig");lines=raw.splitlines();changed=False
        for i,line in enumerate(lines):
            m=re.match(r'^(\s*)([^\s:#]+):(\d*)\s+"(.*)"\s*$',line)
            if not m:continue
            key=m.group(2);base=key[:-5] if key.endswith("_desc") else key
            if base not in NAME_FIXES:continue
            old=re.match(r'^(.*?)(?:\\n|$)',m.group(4)).group(1)
            val=m.group(4)
            if key.endswith("_desc") and old:val=val.replace(old,NAME_FIXES[base],1)
            elif not key.endswith("_desc"):val=NAME_FIXES[base]
            lines[i]=f'{m.group(1)}{key}:{m.group(3)} "{val}"';changed=True
        if changed:p.write_text("\n".join(lines)+"\n",encoding="utf-8-sig")
def add_to_focus(path,fid,effect):
    text=path.read_text(encoding="utf-8-sig")
    if effect in text:return
    startm=re.search(r"(?ms)^\s*shared_focus\s*=\s*\{(?:(?!^\s*shared_focus\s*=).)*?^\s*id\s*=\s*"+re.escape(fid)+r"\b",text)
    if not startm:raise RuntimeError(f"focus not found {fid}")
    start=startm.start();i=startm.end();depth=text[start:i].count("{")-text[start:i].count("}")
    while i<len(text) and depth:
        depth+=text[i].count("{")-text[i].count("}");i+=1
    block=text[start:i];m=re.search(r"completion_reward\s*=\s*\{",block)
    if not m:raise RuntimeError(f"reward not found {fid}")
    j=m.end();d=1
    while j<len(block) and d:
        d+=block[j].count("{")-block[j].count("}");j+=1
    prefix=re.sub(r"[ \t]+$", "", block[:j-1])
    block=prefix+"\n\t\t"+effect+"\n\t"+block[j-1:]
    path.write_text(text[:start]+block+text[i:],encoding="utf-8")
def ideas_text():
    mods={
"DOP_GNG_strangle_guerrillas":["resistance_damage_to_garrison = -0.15","army_defence_factor = 0.10"],
"DOP_GNG_civil_priority":["production_factory_efficiency_gain_factor = 0.10","production_factory_start_efficiency_factor = 0.10","industrial_capacity_factory = 0.10","army_attack_factor = -0.05","army_defence_factor = -0.05"],
"DOP_GNG_civil_priority_supply":["stability_factor = 0.05","war_support_factor = 0.05","attrition = -0.05","max_organisation_factor = 0.10","production_factory_efficiency_gain_factor = 0.10","production_factory_start_efficiency_factor = 0.10","industrial_capacity_factory = 0.10","army_attack_factor = -0.05","army_defence_factor = -0.05"],
"DOP_GNG_military_priority":["stability_factor = -0.05","war_support_factor = 0.10","industrial_capacity_factory = 0.20","army_attack_factor = 0.05","army_defence_factor = 0.05"],
"DOP_GNG_military_priority_industry":["stability_factor = -0.05","war_support_factor = 0.10","industrial_capacity_factory = 0.25","production_factory_efficiency_gain_factor = 0.05","production_lack_of_resource_penalty_factor = -0.05","army_attack_factor = 0.05","army_defence_factor = 0.05"],
}
    out=["ideas = {","\tcountry = {"]
    for k,(_,_,pic) in SPIRITS.items():
        out += [f"\t\t{k} = {{","\t\t\tallowed = { original_tag = GNG }","\t\t\tremoval_cost = -1",f"\t\t\tpicture = {pic}"]
        if k in mods:
            out.append("\t\t\tmodifier = {");out += ["\t\t\t\t"+x for x in mods[k]];out.append("\t\t\t}")
        out.append("\t\t}")
    out += ["\t}","}",""]
    return "\n".join(out)
def effects_text():
    statuses=["DOP_GNG_first_national_crisis","DOP_GNG_lingnan_spring","DOP_GNG_status_lee","DOP_GNG_status_ibuka","DOP_GNG_status_finance","DOP_GNG_status_1962","DOP_GNG_status_second_riot"]
    security=["DOP_GNG_security_southwest_war","DOP_GNG_security_postwar","DOP_GNG_security_reformed"]
    identity=["DOP_GNG_identity_initial","DOP_GNG_identity_dual","DOP_GNG_identity_zhujin"]
    def swap(name,pool,target):
        a=[f"{name} = {{"]+[f"\tremove_ideas = {x}" for x in pool]+[f"\tadd_ideas = {target}","}",""]
        return a
    out=[]
    for name,target in [("DOP_GNG_set_status_first_crisis",statuses[0]),("DOP_GNG_set_status_postwar",statuses[1]),("DOP_GNG_set_status_lee",statuses[2]),("DOP_GNG_set_status_ibuka",statuses[3]),("DOP_GNG_set_status_finance",statuses[4]),("DOP_GNG_set_status_1962",statuses[5]),("DOP_GNG_set_status_second_riot",statuses[6])]:out+=swap(name,statuses,target)
    for name,target in [("DOP_GNG_set_security_war",security[0]),("DOP_GNG_set_security_postwar",security[1]),("DOP_GNG_set_security_reformed",security[2])]:out+=swap(name,security,target)
    for name,target in [("DOP_GNG_set_identity_initial",identity[0]),("DOP_GNG_set_identity_dual",identity[1]),("DOP_GNG_set_identity_zhujin",identity[2])]:out+=swap(name,identity,target)
    integ=["DOP_GNG_integrity_waltz","DOP_GNG_integrity_chorus","DOP_GNG_integrity_dissonance","DOP_GNG_integrity_chaos"]
    out += ["DOP_GNG_update_stage_integrity = {"]+[f"\tremove_ideas = {x}" for x in integ]+["\tif = {","\t\tlimit = { check_variable = { DOP_GNG_stage_integrity >= 75 } }",f"\t\tadd_ideas = {integ[0]}","\t}","\telse_if = {","\t\tlimit = { check_variable = { DOP_GNG_stage_integrity >= 50 } }",f"\t\tadd_ideas = {integ[1]}","\t}","\telse_if = {","\t\tlimit = { check_variable = { DOP_GNG_stage_integrity >= 25 } }",f"\t\tadd_ideas = {integ[2]}","\t}","\telse = {",f"\t\tadd_ideas = {integ[3]}","\t}","}",""]
    return "\n".join(out)

def product_cycle_effects_text():
    # Intentionally override only TNO's dispatcher. All product data, GUI,
    # deadlines and settlement effects continue to come from the base mod.
    out=["# Intentional narrow override of TNO's product-cycle dispatcher.","GNG_product_cycle_event_initializer = {"]
    out += ["\tif = {","\t\tlimit = {","\t\t\thas_country_flag = DOP_GNG_open_product_cycle_investment","\t\t\tOR = {"]
    out += [f"\t\t\t\tcheck_variable = {{ GNG_product_cycle_tracker = {year} }}" for year in range(2,13)]
    out += ["\t\t\t}","\t\t}","\t\tcountry_event = DOP_GNG_product_cycle.1","\t}"]
    for year in range(2,14):
        out += ["\telse_if = {",f"\t\tlimit = {{ check_variable = {{ GNG_product_cycle_tracker = {year} }} }}","\t\tcountry_event = GNG_Product_Cycle.3","\t}"]
    out += ["}",""]
    for company,value,offset in [("sony",1,8),("matsushita",2,9),("fujitsu",3,10),("hitachi",4,11)]:
        out += [f"DOP_GNG_start_product_cycle_as_{company} = {{",f"\tset_temp_variable = {{ GNG_product_cycle_company_temp = {value} }}","\tset_temp_variable = { DOP_GNG_product_id_temp = GNG_product_cycle_tracker }","\tmultiply_temp_variable = { DOP_GNG_product_id_temp = 4 }",f"\tadd_to_temp_variable = {{ DOP_GNG_product_id_temp = {offset} }}","\tset_variable = { GNG_current_product_id = DOP_GNG_product_id_temp }","\tGNG_new_product_cycle_start = yes","}",""]
    return "\n".join(out)

def product_cycle_event_text():
    out=["add_namespace = DOP_GNG_product_cycle","","country_event = {","\tid = DOP_GNG_product_cycle.1","\ttitle = GNG_Product_Cycle.3.t","\tdesc = GNG_Product_Cycle.3.desc","\tpicture = GFX_report_event_GNG_generic_engineers_2","\tis_triggered_only = yes",""]
    for suffix,company in [("a","sony"),("b","matsushita"),("c","fujitsu"),("d","hitachi")]:
        out += ["\toption = {",f"\t\tname = GNG_Product_Cycle.3.{suffix}","\t\tai_chance = { factor = 1 }",f"\t\tDOP_GNG_start_product_cycle_as_{company} = yes","\t}"]
    out += ["}",""]
    return "\n".join(out)

def main(root,kdocs):
    loc=readloc(root)
    # Wartime descriptions from the downloaded source documents.
    files={"战鼓渐响":"战鼓渐响.txt","东京速递":"东京速递.txt","来自盟友的援助":"来自盟友的援助.txt","加强北方防御":"加强北方防御.txt","扩大军警招募":"扩大军警招募.txt","收买极道":"收买极道.txt","分化三合会":"分化三合会.txt","效忠自有奖赏":"效忠自有奖赏.txt","财政捉襟见肘……":"财政捉襟见肘…….txt","不忘立足之本":"不忘立足之本.txt","火烧眉头":"火烧眉毛.txt","保障物资供应":"保障物资供应.txt","民用工业军事化":"民用工业军事化.txt","此乃吾等家园……":"此乃吾等家园…….txt","……为广东之存继……":"……为广东之未来…….txt","……我们死而后已！":"……我们死而后已！.txt"}
    desc={n:docdesc(kdocs/f) for n,f in files.items()}
    old=focusblocks(root/"common"/"national_focus"/"dop_sony-japan_prewar.txt")
    icons=[iconof(old.get(fid,"")) for fid in WARTIME_IDS]
    rewards={n:[] for n in WARTIME_NAMES}
    for n,stub in zip(["固守待援","乱世需用重典","扩大适役人口范围","警民合作","何惜百死卫吾乡"],range(1,6)):rewards[n]=event_reward(f"DOP_GNG_focus_stub.{stub}")
    rewards["战鼓渐响"]=["DOP_GNG_set_status_first_crisis = yes","DOP_GNG_set_security_war = yes","add_ideas = DOP_GNG_wartime_triangle"]
    rewards["东京速递"]=["set_temp_variable = { money_reserves_temp = 0.5 }","econ_money_reserves_change_raw_money = yes","add_equipment_to_stockpile = { type = infantry_equipment_3 amount = 2000 producer = JAP }"]
    rewards["来自盟友的援助"]=["add_equipment_to_stockpile = { type = infantry_equipment_3 amount = 5000 producer = JAP }","add_equipment_to_stockpile = { type = artillery_equipment_2 amount = 2500 producer = JAP }","add_equipment_to_stockpile = { type = anti_air_equipment_2 amount = 2500 producer = JAP }","add_command_power = 100"]
    rewards["加强北方防御"]=["every_owned_state = {","\tadd_building_construction = { type = bunker level = 2 instant_build = yes }","\tset_temp_variable = { chi_app_temp = -1.25 }","\tGNG_chinese_app_change = yes","}","add_ideas = DOP_GNG_strangle_guerrillas"]
    rewards["扩大军警招募"]=["add_manpower = 2500","every_owned_state = {","\tset_temp_variable = { sar_spt_temp = -1.25 }","\tGNG_police_control_change = yes","}"]
    rewards["收买极道"]=["add_manpower = 50000","every_owned_state = {","\tset_temp_variable = { yak_spt_temp = 2.5 }","\tGNG_yakuza_control_change = yes","}","country_event = { id = DOP_GNG_event.180 days = 1 }"]
    rewards["分化三合会"]=["add_manpower = 10000","every_owned_state = {","\tset_temp_variable = { tri_spt_temp = 2.5 }","\tGNG_triad_control_change = yes","}","country_event = { id = DOP_GNG_event.158 days = 1 }"]
    rewards["效忠自有奖赏"]=["add_manpower = 50000","every_owned_state = {","\tset_temp_variable = { yak_spt_temp = 1 }","\tGNG_yakuza_control_change = yes","\tset_temp_variable = { tri_spt_temp = 1 }","\tGNG_triad_control_change = yes","}","add_equipment_to_stockpile = { type = infantry_equipment_3 amount = 1000 producer = JAP }","add_equipment_to_stockpile = { type = infantry_equipment_3 amount = 1000 producer = CHI }"]
    rewards["财政捉襟见肘……"]=event_reward("DOP_GNG_event.93")
    rewards["不忘立足之本"]=["army_funding_maximal_decrease_high = yes","social_funding_maximal_increase_high = yes","every_owned_state = {","\tset_temp_variable = { jap_app_temp = 3 }","\tGNG_japanese_app_change = yes","\tset_temp_variable = { zhu_app_temp = 3 }","\tGNG_zhujin_app_change = yes","\tset_temp_variable = { chi_app_temp = 3 }","\tGNG_chinese_app_change = yes","}","add_ideas = DOP_GNG_civil_priority"]
    rewards["火烧眉头"]=["social_funding_maximal_decrease_high = yes","army_funding_minimal_increase_high = yes","every_owned_state = {","\tset_temp_variable = { chi_app_temp = -1.25 }","\tGNG_chinese_app_change = yes","}","add_ideas = DOP_GNG_military_priority"]
    rewards["保障物资供应"]=["remove_ideas = DOP_GNG_civil_priority","add_ideas = DOP_GNG_civil_priority_supply"]
    rewards["民用工业军事化"]=["random_owned_state = { add_building_construction = { type = industrial_complex level = 3 instant_build = yes } }","remove_ideas = DOP_GNG_military_priority","add_ideas = DOP_GNG_military_priority_industry"]
    rewards["此乃吾等家园……"]=["add_stability = 0.10"]
    rewards["……为广东之存继……"]=["add_war_support = 0.10"]
    rewards["……我们死而后已！"]=["add_political_power = 100","set_temp_variable = { gdp_growth_temp = 0.5 }","econ_gdp_growth_change = yes","remove_ideas = DOP_GNG_wartime_triangle","DOP_GNG_set_status_postwar = yes","DOP_GNG_set_security_postwar = yes"]
    items=[{"id":fid,"name":n,"desc":desc.get(n,""),"icon":icons[i] if i<len(icons) else "GFX_GNG_focus_a_state_of_unstay","reward":rewards[n]} for i,(fid,n) in enumerate(zip(WARTIME_IDS,WARTIME_NAMES))]
    write_tree(root,root/"common"/"national_focus"/"dop_sony-japan_prewar.txt",root/"localisation"/"simp_chinese"/"dop_sony-japan_prewar_focus-tree_l_simp_chinese.yml","dop_sonyjapan_prewar_tree","盛田与西南战争",items)

    # Reconstruction: exact active nodes retain their existing rewards; obsolete nodes are dropped.
    rpath=root/"common"/"national_focus"/"dop_sony-japan_reconstruction.txt";rblocks=focusblocks(rpath)
    byname={loc.get(fid,""):fid for fid in rblocks};bynorm={norm(n):fid for n,fid in byname.items() if n}
    shared=sectiondoc(kdocs/"重建国策.txt",["地位协定重议定","广东的雁行经济","官僚登台亮相","共荣圈经济会议"])
    ritems=[]
    stub=6
    for n in RECON_NAMES:
        if n in RECON_NEW:
            fid=RECON_NEW[n];reward=[]
            if n=="地位协定重议定":reward=event_reward("DOP_GNG_event.209")
            elif n=="广东的雁式经济":reward=event_reward("DOP_GNG_event.210")
            elif n=="（年份）年共荣圈经济大会":reward=["country_event = { id = DOP_GNG_event.211 days = 1 }","country_event = { id = DOP_GNG_event.212 days = 5 }"]
            elif n=="文官登台亮相":reward=event_reward("DOP_GNG_event.213")
            else:reward=event_reward(f"DOP_GNG_focus_stub.{stub}");stub+=1
            d={"地位协定重议定":shared.get("地位协定重议定",""),"广东的雁式经济":shared.get("广东的雁行经济",""),"文官登台亮相":shared.get("官僚登台亮相",""),"（年份）年共荣圈经济大会":shared.get("共荣圈经济会议","")}.get(n,"")
            ritems.append({"id":fid,"name":n,"desc":d,"icon":"GFX_GNG_focus_a_state_of_unstay","reward":reward});continue
        fid=RECON_ALIAS.get(n) or byname.get(n) or bynorm.get(norm(n))
        if not fid:raise RuntimeError(f"reconstruction mapping missing: {n}")
        block=rblocks[fid]
        ritems.append({"id":fid,"name":n,"desc":loc.get(fid+"_desc",""),"icon":iconof(block),"reward":rewardof(block)})
    if len(ritems)!=34:raise RuntimeError("reconstruction count")
    write_tree(root,rpath,root/"localisation"/"simp_chinese"/"dop_sony-japan_reconstruction_focus-tree_l_simp_chinese.yml","dop_sonyjapan_reconsturuction_tree","盛田与战后重建",ritems)

    # New finance ending reuses the old branch's icon registrations, but none of its deprecated effects.
    fpath=root/"common"/"national_focus"/"dop_sony-japan_ending3_hitachi.txt";fblocks=focusblocks(fpath);oldids=list(fblocks);fdoc=sectiondoc(kdocs/"新财界国策.txt",FINANCE_NAMES)
    fitems=[]
    for i,(n,fid) in enumerate(zip(FINANCE_NAMES,oldids)):
        reward=event_reward(f"DOP_GNG_zip.{23+i}") if i<9 else event_reward(f"DOP_GNG_focus_stub.{14+i-9}")
        if i==11:reward.append("DOP_GNG_set_status_finance = yes")
        fitems.append({"id":fid,"name":n,"desc":fdoc.get(n,""),"icon":iconof(fblocks[fid]),"reward":reward})
    write_tree(root,fpath,root/"localisation"/"simp_chinese"/"dop_sony-japan_ending3_hitachi_focus-tree_l_simp_chinese.yml","dop_sonyjapan_ending3_hitachi_tree","盛田与§L财界迷局§!",fitems,3)

    # Empty events requested for new focuses whose event text is not supplied.
    stub_lines=["add_namespace = DOP_GNG_focus_stub",""]
    for i in range(1,17):stub_lines += ["country_event = {",f"\tid = DOP_GNG_focus_stub.{i}","\thidden = yes","\tis_triggered_only = yes","\timmediate = { }","}",""]
    (root/"events"/"DOP_GNG_focus_stubs.txt").write_text("\n".join(stub_lines),encoding="utf-8")

    (root/"common"/"ideas"/"DOP_GNG_postwar_ideas.txt").write_text(ideas_text(),encoding="utf-8")
    (root/"common"/"scripted_effects"/"DOP_GNG_postwar_effects.txt").write_text(effects_text(),encoding="utf-8")
    (root/"common"/"scripted_effects"/"zz_DOP_GNG_product_cycle_override.txt").write_text(product_cycle_effects_text(),encoding="utf-8")
    (root/"events"/"DOP_GNG_product_cycle.txt").write_text(product_cycle_event_text(),encoding="utf-8")
    iloc=["l_simp_chinese:"]
    for k,(name,d,_) in SPIRITS.items():iloc += [f' {k}:0 "{esc(name)}"',f' {k}_desc:0 "{esc(d)}"']
    (root/"localisation"/"simp_chinese"/"DOP_GNG_postwar_ideas_l_simp_chinese.yml").write_text("\n".join(iloc)+"\n",encoding="utf-8-sig")

    fix_names(root)
    fix_missing_focus_icons(root)
    for file,fid,effect in [
("dop_sony-japan_ending1_lee.txt","GNG_focus_a_place_for_all","DOP_GNG_set_status_lee = yes"),
("dop_sony-japan_ending2_ibuka.txt","GNG_focus_onward_to_Tomorrow","DOP_GNG_set_status_ibuka = yes"),
("dop_sony-japan_ending4_return1962.txt","GNG_focus_prison_of_enterprises","DOP_GNG_set_status_1962 = yes"),
("dop_sony-japan_ending5_second_riot.txt","GNG_focus_is_order_prevails_in_guangdong","DOP_GNG_set_status_second_riot = yes"),
("dop_sony-japan_ending4_return1962.txt","GNG_focus_reduce_the_budget_of_product_cycle","set_country_flag = DOP_GNG_open_product_cycle_investment"),
("dop_sony-japan_core.txt","GNG_focus_establish_chi_zhu_binary_system","DOP_GNG_set_identity_dual = yes"),
("dop_sony-japan_core.txt","GNG_focus_accelerate_chi_assimilation","DOP_GNG_set_identity_zhujin = yes")]:
        add_to_focus(root/"common"/"national_focus"/file,fid,effect)
    core_path=root/"common"/"national_focus"/"dop_sony-japan_core.txt"
    core_text=core_path.read_text(encoding="utf-8-sig")
    if "id = DOP_GNG_focus_exquisite_equipment" not in core_text:
        core_text += """
shared_focus = {
    id = DOP_GNG_focus_exquisite_equipment
    icon = GFX_GNG_focus_a_state_of_unstay
    relative_position_id = GNG_focus_level_up_equipment
    x = 2
    y = 1
    prerequisite = { focus = GNG_focus_level_up_equipment }
    cost = 1
    completion_reward = { }
}
"""
        core_path.write_text(core_text,encoding="utf-8")
    core_loc=root/"localisation"/"simp_chinese"/"dop_sony-japan_core_focus-tree_l_simp_chinese.yml"
    core_loc_text=core_loc.read_text(encoding="utf-8-sig")
    if "DOP_GNG_focus_exquisite_equipment:" not in core_loc_text:
        core_loc_text += ' DOP_GNG_focus_exquisite_equipment:0 "精湛装备"\n DOP_GNG_focus_exquisite_equipment_desc:0 ""\n'
        core_loc.write_text(core_loc_text,encoding="utf-8-sig")
    print("wartime=21 reconstruction=34 finance=12 spirits=23 focus_stubs=16")

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument("--kdocs-dir",type=Path,required=True);a=p.parse_args();main(a.root.resolve(),a.kdocs_dir.resolve())
