from __future__ import annotations
import re
from pathlib import Path

PROJECTS=[
("sky_tower","珠三角","白鹅新区晴空塔",150000,"广佛同城之后的新核心区——这个世界的珠江新城与广州塔。"),
("rose_garden","珠三角","玫瑰园计划",100000,"香港超级城建计划，包含新机场、海底隧道与填海工程。"),
("alice_dream_factory","珠三角","粤海爱丽丝梦工厂",30000,"一座落在澳门的迪士尼式主题乐园。"),
("daya_bay_nuclear_plant","珠三角","大亚湾核电站",45000,"在大亚湾建设大型核能发电设施。"),
("guangdong_shinkansen","珠三角","广东新干线",90000,"澳湛高铁与港汕高铁组成的高速铁路骨架。"),
("chaoshan_university","潮汕","潮汕大学",8000,"服务潮汕地区的综合性大学。"),
("xinfengjiang_reservoir","粤北","新丰江水库",20000,"新丰江流域的大型水利与供电工程。"),
("luoding_granary","粤西","罗定粮仓",4000,"推动罗定盆地农业集中化与机械化。"),
("pinglu_canal","交洋","平陆运河",100000,"贯通内河与北部湾航运体系的运河工程。"),
("south_china_sea_drilling_platform","交洋","南海深水钻井平台",4000,"面向南海深水油气资源的海上开采平台。"),
("wenchang_space_center","交洋","文昌卫星发射中心",12000,"面向未来航天计划的卫星发射场。"),
("guangxi_industrial_institute","邕宁","重整广西实业院",50000,"将桂柳一带的工业资源与机构逐步迁往南宁。"),
("guangxi_expressway_network","邕宁","广西高速公路网新规划",80000,"连接桂柳、南宁、钦廉与肇庆方向的高速公路网。"),
("nanyue_folk_memorial_park","苍梧","南粤民俗纪念公园",1000,"纪念南粤民俗与乡土文化，以安抚本土认同。"),
("lijiang_waterway","桂柳","漓江航道开发工程",1000,"加强桂柳同沿岸地区的交通、沟通与商贸。"),
("honghe_fan_asia_friendship_pass","田南","红河泛亚友谊关",1000,"加强友谊关沿红河—湄公河方向与印支半岛的交通和商贸。"),
]

def var(slug,suffix):return f"DOP_construction_{slug}_{suffix}"
def add_block(lines,name,body):
    lines.append(f"{name} = {{");lines += ["\t"+x for x in body];lines += ["}",""]
def recalc_body(slug,total):
    v=lambda x:var(slug,x)
    return [
f"set_variable = {{ {v('actual_speed')} = DOP_construction_base_speed }}",
f"add_to_variable = {{ {v('actual_speed')} = {v('speed_add')} }}",
f"multiply_variable = {{ {v('actual_speed')} = {v('speed_factor')} }}",
f"set_temp_variable = {{ DOP_construction_input_sum = {v('funding')} }}",
f"add_to_temp_variable = {{ DOP_construction_input_sum = {v('manpower')} }}",
"divide_temp_variable = { DOP_construction_input_sum = 100 }",
f"multiply_variable = {{ {v('actual_speed')} = DOP_construction_input_sum }}",
f"clamp_variable = {{ var = {v('actual_speed')} min = 0 }}",
f"set_variable = {{ {v('percent')} = {v('progress')} }}",
f"divide_variable = {{ {v('percent')} = {total} }}",
f"multiply_variable = {{ {v('percent')} = 100 }}",
f"clamp_variable = {{ var = {v('percent')} min = 0 max = 100 }}",
]
def complete_body(i,slug,total):
    v=lambda x:var(slug,x)
    return ["if = {",f"\tlimit = {{ NOT = {{ has_country_flag = DOP_construction_{slug}_completed }} check_variable = {{ {v('progress')} >= {total} }} }}",f"\tset_variable = {{ {v('progress')} = {total} }}",f"\tset_variable = {{ {v('percent')} = 100 }}",f"\tset_country_flag = DOP_construction_{slug}_completed",f"\tcountry_event = {{ id = DOP_GNG_construction.{i} days = 1 }}","}"]
def sync_selected_body():
    out=[]
    for i,(slug,_,_,_,_) in enumerate(PROJECTS,1):
        v=lambda x:var(slug,x)
        key="if" if i==1 else "else_if"
        out += [f"{key} = {{",f"\tlimit = {{ check_variable = {{ DOP_construction_selected = {i} }} }}"]
        for suf in ("progress","total","percent","funding","manpower","funding_min","funding_max","manpower_min","manpower_max","actual_speed","speed_add","speed_factor"):
            out.append(f"\tset_variable = {{ DOP_construction_selected_{suf} = {v(suf)} }}")
        out += ["}"]
    out += [
"set_variable = { DOP_construction_funding_thumb_x = DOP_construction_selected_funding }",
"subtract_from_variable = { DOP_construction_funding_thumb_x = DOP_construction_selected_funding_min }",
"set_temp_variable = { DOP_construction_selected_range = DOP_construction_selected_funding_max }",
"subtract_from_temp_variable = { DOP_construction_selected_range = DOP_construction_selected_funding_min }",
"if = { limit = { check_variable = { DOP_construction_selected_range > 0 } } divide_variable = { DOP_construction_funding_thumb_x = DOP_construction_selected_range } }",
"multiply_variable = { DOP_construction_funding_thumb_x = 300 }",
"add_to_variable = { DOP_construction_funding_thumb_x = 6 }",
"set_variable = { DOP_construction_manpower_thumb_x = DOP_construction_selected_manpower }",
"subtract_from_variable = { DOP_construction_manpower_thumb_x = DOP_construction_selected_manpower_min }",
"set_temp_variable = { DOP_construction_selected_range = DOP_construction_selected_manpower_max }",
"subtract_from_temp_variable = { DOP_construction_selected_range = DOP_construction_selected_manpower_min }",
"if = { limit = { check_variable = { DOP_construction_selected_range > 0 } } divide_variable = { DOP_construction_manpower_thumb_x = DOP_construction_selected_range } }",
"multiply_variable = { DOP_construction_manpower_thumb_x = 300 }",
"add_to_variable = { DOP_construction_manpower_thumb_x = 6 }",
]
    return out
def selected_adjust_body(kind,op,amount=None,endpoint=None):
    out=[]
    for i,(slug,_,_,_,_) in enumerate(PROJECTS,1):
        v=var(slug,kind);lo=var(slug,kind+"_min");hi=var(slug,kind+"_max")
        key="if" if i==1 else "else_if";out += [f"{key} = {{",f"\tlimit = {{ check_variable = {{ DOP_construction_selected = {i} }} }}"]
        if endpoint=="min":out.append(f"\tset_variable = {{ {v} = {lo} }}")
        elif endpoint=="max":out.append(f"\tset_variable = {{ {v} = {hi} }}")
        elif op=="add":out.append(f"\tadd_to_variable = {{ {v} = {amount} }}")
        else:out.append(f"\tsubtract_from_variable = {{ {v} = {amount} }}")
        out += [f"\tclamp_variable = {{ var = {v} min = {lo} max = {hi} }}",f"\tDOP_construction_{slug}_recalculate = yes","}"]
    out.append("DOP_construction_sync_selected = yes")
    return out
def init_body():
    out=["set_variable = { DOP_construction_base_speed = 1000 }","set_variable = { DOP_construction_selected = 1 }"]
    for slug,_,_,total,_ in PROJECTS:
        for flag in [f"DOP_construction_{slug}_completed"]:out.append(f"clr_country_flag = {flag}")
        vals={"progress":0,"total":total,"funding":50,"manpower":50,"funding_min":10,"funding_max":100,"manpower_min":10,"manpower_max":100,"speed_add":0,"speed_factor":1,"percent":0,"actual_speed":1000}
        out += [f"set_variable = {{ {var(slug,k)} = {v} }}" for k,v in vals.items()]
    out += ["set_country_flag = DOP_construction_initialized","set_variable = { DOP_GNG_stage_integrity = 100 }","DOP_GNG_update_stage_integrity = yes"]
    for slug,_,_,_,_ in PROJECTS:out.append(f"DOP_construction_{slug}_recalculate = yes")
    out.append("DOP_construction_sync_selected = yes")
    return out
def effects_file():
    out=["# Generated by tools/generate_dop_construction.py","# All sixteen projects advance concurrently on the monthly on_action.",""]
    add_block(out,"DOP_construction_initialize_variables",init_body())
    add_block(out,"GNG_BOP_Construction_Initialize",["if = {","\tlimit = { NOT = { has_country_flag = DOP_construction_tab_enabled } }","\tset_temp_variable = { TabName = token:BoP_Tab_DOPConstruction }","\tTNO_BoP_GNG_AddTab = yes","\tset_country_flag = DOP_construction_tab_enabled","}","if = {","\tlimit = { NOT = { has_country_flag = DOP_construction_initialized } }","\tDOP_construction_initialize_variables = yes","}","DOP_construction_sync_selected = yes"])
    add_block(out,"DOP_construction_reset",init_body())
    for i,(slug,_,_,total,_) in enumerate(PROJECTS,1):
        add_block(out,f"DOP_construction_{slug}_recalculate",recalc_body(slug,total))
        add_block(out,f"DOP_construction_{slug}_complete_if_needed",complete_body(i,slug,total))
        add_block(out,f"DOP_construction_{slug}_tick",[f"if = {{",f"\tlimit = {{ NOT = {{ has_country_flag = DOP_construction_{slug}_completed }} }}",f"\tDOP_construction_{slug}_recalculate = yes",f"\tadd_to_variable = {{ {var(slug,'progress')} = {var(slug,'actual_speed')} }}",f"\tDOP_construction_{slug}_complete_if_needed = yes","}"])
    add_block(out,"DOP_construction_monthly_tick",[f"DOP_construction_{s}_tick = yes" for s,_,_,_,_ in PROJECTS]+["DOP_construction_sync_selected = yes"])
    add_block(out,"DOP_construction_sync_selected",sync_selected_body())
    for i,(slug,_,_,_,_) in enumerate(PROJECTS,1):
        add_block(out,f"DOP_construction_select_{i}",[f"set_variable = {{ DOP_construction_selected = {i} }}","DOP_construction_sync_selected = yes"])
    for kind in ("funding","manpower"):
        add_block(out,f"DOP_construction_selected_{kind}_increase",selected_adjust_body(kind,"add",5))
        add_block(out,f"DOP_construction_selected_{kind}_decrease",selected_adjust_body(kind,"sub",5))
        add_block(out,f"DOP_construction_selected_{kind}_maximum",selected_adjust_body(kind,"set",endpoint="max"))
        add_block(out,f"DOP_construction_selected_{kind}_minimum",selected_adjust_body(kind,"set",endpoint="min"))
    add_block(out,"DOP_construction_set_base_speed",["set_variable = { DOP_construction_base_speed = DOP_construction_value }","clamp_variable = { var = DOP_construction_base_speed min = 0 }"]+[f"DOP_construction_{s}_recalculate = yes" for s,_,_,_,_ in PROJECTS]+["DOP_construction_sync_selected = yes"])
    for i,(slug,_,_,_,_) in enumerate(PROJECTS,1):
        for op,suf in [("set_progress","progress"),("add_progress","progress"),("set_speed_add","speed_add"),("add_speed_add","speed_add"),("set_speed_factor","speed_factor"),("add_speed_factor","speed_factor"),("set_funding","funding"),("set_manpower","manpower")]:
            cmd=("set_variable" if op.startswith("set_") else "add_to_variable")
            body=[f"{cmd} = {{ {var(slug,suf)} = DOP_construction_value }}"]
            if suf in ("progress","speed_factor"):body.append(f"clamp_variable = {{ var = {var(slug,suf)} min = 0 }}")
            if suf=="funding":body.append(f"clamp_variable = {{ var = {var(slug,suf)} min = {var(slug,'funding_min')} max = {var(slug,'funding_max')} }}")
            if suf=="manpower":body.append(f"clamp_variable = {{ var = {var(slug,suf)} min = {var(slug,'manpower_min')} max = {var(slug,'manpower_max')} }}")
            body += [f"DOP_construction_{slug}_recalculate = yes",f"DOP_construction_{slug}_complete_if_needed = yes",f"if = {{ limit = {{ check_variable = {{ DOP_construction_selected = {i} }} }} DOP_construction_sync_selected = yes }}"]
            add_block(out,f"DOP_construction_{slug}_{op}",body)
        for kind in ("funding","manpower"):
            body=[f"set_variable = {{ {var(slug,kind+'_min')} = DOP_construction_min_value }}",f"set_variable = {{ {var(slug,kind+'_max')} = DOP_construction_max_value }}",f"clamp_variable = {{ var = {var(slug,kind+'_min')} min = 0 max = 100 }}",f"clamp_variable = {{ var = {var(slug,kind+'_max')} min = {var(slug,kind+'_min')} max = 100 }}",f"clamp_variable = {{ var = {var(slug,kind)} min = {var(slug,kind+'_min')} max = {var(slug,kind+'_max')} }}",f"DOP_construction_{slug}_recalculate = yes",f"if = {{ limit = {{ check_variable = {{ DOP_construction_selected = {i} }} }} DOP_construction_sync_selected = yes }}"]
            add_block(out,f"DOP_construction_{slug}_set_{kind}_bounds",body)
    return "\n".join(out)
def scripted_gui_file():
    out=["scripted_gui = {","\tDOP_construction_base_container = {",'\t\twindow_name = "DOP_construction_base_container"',"\t\tcontext_type = player_context","\t\tparent_window_name = powerbalanceview","\t\tvisible = { check_variable = { TNO_BoP_SelectedTab = token:BoP_Tab_DOPConstruction } }","\t\tai_enabled = { always = no }","\t\teffects = {"]
    for i in range(1,17):out += [f"\t\t\tconstruction_project_{i}_click = {{ DOP_construction_select_{i} = yes }}"]
    for kind in ("funding","manpower"):
        out += [f"\t\t\tconstruction_{kind}_decrease_click = {{ DOP_construction_selected_{kind}_decrease = yes }}",f"\t\t\tconstruction_{kind}_increase_click = {{ DOP_construction_selected_{kind}_increase = yes }}",f"\t\t\tconstruction_{kind}_decrease_control_click = {{ DOP_construction_selected_{kind}_minimum = yes }}",f"\t\t\tconstruction_{kind}_increase_control_click = {{ DOP_construction_selected_{kind}_maximum = yes }}"]
    out += ["\t\t}","\t\tproperties = {","\t\t\tconstruction_main_progress = { frame = var:DOP_construction_selected_percent }","\t\t\tconstruction_funding_dot = { x = DOP_construction_funding_thumb_x }","\t\t\tconstruction_manpower_dot = { x = DOP_construction_manpower_thumb_x }"]
    for i,(slug,_,_,_,_) in enumerate(PROJECTS,1):out += [f"\t\t\tconstruction_project_{i}_progress = {{ frame = var:{var(slug,'percent')} }}"]
    out += ["\t\t}","\t}","}",""]
    return "\n".join(out)
def defined_text(name,keyprefix):
    out=["defined_text = {",f"\tname = {name}"]
    for i,_ in enumerate(PROJECTS,1):out += ["\ttext = {",f"\t\ttrigger = {{ check_variable = {{ DOP_construction_selected = {i} }} }}",f"\t\tlocalization_key = {keyprefix}_{i}","\t}"]
    out += ["}",""]
    return out
def scripted_loc_file():
    out=defined_text("DOP_construction_GetName","DOP_construction_project_name")+defined_text("DOP_construction_GetDesc","DOP_construction_project_desc")+defined_text("DOP_construction_GetRegion","DOP_construction_project_region")
    out += ["defined_text = {","\tname = DOP_construction_GetStatus"]
    for i,(slug,_,_,_,_) in enumerate(PROJECTS,1):out += ["\ttext = {",f"\t\ttrigger = {{ check_variable = {{ DOP_construction_selected = {i} }} has_country_flag = DOP_construction_{slug}_completed }}","\t\tlocalization_key = DOP_construction_status_completed","\t}"]
    out += ["\ttext = { localization_key = DOP_construction_status_pending }","}",""]
    return "\n".join(out)
def gfx_file():
    return """spriteTypes = {
\tspriteType = {
\t\tname = "GFX_BoP_Tab_DOPConstruction_Icon"
\t\ttextureFile = "gfx/interface/bop/GFX_BoP_Tab_GSA_Icon.dds"
\t}
\tprogressbartype = {
\t\tname = "GFX_DOP_construction_main_progress"
\t\tsize = { x = 430 y = 37 }
\t\ttextureFile1 = "gfx/interface/bop/GSA_research_prgbarfull.dds"
\t\ttextureFile2 = "gfx/interface/bop/GSA_research_prgbarempty.dds"
\t\teffectFile = "gfx/FX/progress.lua"
\t}
\tprogressbartype = {
\t\tname = "GFX_DOP_construction_row_progress"
\t\tsize = { x = 160 y = 24 }
\t\ttextureFile1 = "gfx/interface/bop/GSA_research_prgbarfull.dds"
\t\ttextureFile2 = "gfx/interface/bop/GSA_research_prgbarempty.dds"
\t\teffectFile = "gfx/FX/progress.lua"
\t}
}
"""
def gui_file():
    out=["guiTypes = {","\tcontainerWindowType = {",'\t\tname = "DOP_construction_base_container"',"\t\tposition = { x = 25 y = 19 }","\t\tsize = { width = 1040 height = 618 }",""]
    def icon(name,sprite,x,y,tooltip=""):
        out.extend(["\t\ticonType = {",f'\t\t\tname = "{name}"',f'\t\t\tspriteType = "{sprite}"',f"\t\t\tposition = {{ x = {x} y = {y} }}"])
        if tooltip:out.append(f"\t\t\tpdx_tooltip = {tooltip}")
        out.extend(["\t\t\talwaystransparent = yes","\t\t}",""])
    def text_box(name,text,x,y,width,height,font="aldrich_18_outline",fmt="left",indent="\t\t"):
        out.extend([indent+"instantTextBoxType = {",indent+f'\tname = "{name}"',indent+f"\tposition = {{ x = {x} y = {y} }}",indent+f'\tfont = "{font}"',indent+f"\ttext = {text}",indent+f"\tmaxWidth = {width}",indent+f"\tmaxHeight = {height}",indent+f"\tformat = {fmt}",indent+"\tfixedsize = yes",indent+"\talwaystransparent = yes",indent+"}"])
    icon("construction_background","GFX_GSA_bg_on",-15,-15)
    out.extend(["\t\tcontainerWindowType = {",'\t\t\tname = "DOP_construction_topbar"',"\t\t\tposition = { x = 41 y = -24 }"])
    text_box("DOP_construction_title","[GetGCname]",0,0,857,58,"vt323_72_WT_outline","center","\t\t\t")
    out.extend(["\t\t}",""])
    icon("construction_divider_left","GFX_BoP_Base_Vertical_Divider_Full",225,67)
    icon("construction_divider_right","GFX_BoP_Base_Vertical_Divider_Full",745,67)
    out.extend(["\t\tcontainerWindowType = {",'\t\t\tname = "construction_catalog_scroll"',"\t\t\tposition = { x = 40 y = 82 }","\t\t\tsize = { width = 180 height = 515 }",'\t\t\tverticalScrollbar = "right_vertical_slider"',"\t\t\tclipping = yes",""])
    y=0;last_region=None
    for i,(slug,region,name,total,desc) in enumerate(PROJECTS,1):
        if region!=last_region:
            text_box(f"construction_region_{i}",f"DOP_construction_region_{i}",2,y,160,22,"aldrich_18_outline","left","\t\t\t")
            out.append("");y+=24;last_region=region
        out.extend(["\t\t\ticonType = {",f'\t\t\t\tname = "construction_project_{i}_progress"',f"\t\t\t\tposition = {{ x = 2 y = {y} }}",'\t\t\t\tspriteType = "GFX_DOP_construction_row_progress"',"\t\t\t\talwaystransparent = yes","\t\t\t}"])
        text_box(f"construction_project_{i}_label",f"DOP_construction_catalog_{i}",8,y+2,148,20,"aldrich_14_outline","left","\t\t\t")
        out.extend(["\t\t\tbuttonType = {",f'\t\t\t\tname = "construction_project_{i}"',f"\t\t\t\tposition = {{ x = 2 y = {y} }}","\t\t\t\tsize = { x = 160 y = 24 }",'\t\t\t\tquadTextureSprite = "GFX_tiled_window_transparent"',f"\t\t\t\tpdx_tooltip = DOP_construction_project_desc_{i}","\t\t\t}",""]);y+=29
    out.extend(["\t\t}",""])
    text_box("construction_selected_region","DOP_construction_selected_region",252,82,470,22,"aldrich_18_outline","center")
    text_box("construction_selected_name","DOP_construction_selected_name",252,106,470,38,"aldrich_32_outline","center")
    out.append("")
    icon("construction_main_progress","GFX_DOP_construction_main_progress",272,150,"DOP_construction_main_progress_tt")
    text_box("construction_status","DOP_construction_selected_status",252,188,470,22,"aldrich_18_outline","center")
    out.extend(["","\t\tcontainerWindowType = {",'\t\t\tname = "construction_description_scroll"',"\t\t\tposition = { x = 255 y = 218 }","\t\t\tsize = { width = 285 height = 150 }",'\t\t\tverticalScrollbar = "right_vertical_slider"',"\t\t\tclipping = yes"])
    text_box("construction_description","DOP_construction_selected_desc",0,0,265,500,"aldrich_16_outline","left","\t\t\t")
    out.extend(["\t\t}",""])
    text_box("construction_numbers","DOP_construction_selected_numbers",550,218,185,150,"aldrich_16_outline","left")
    for kind,yv,label in [("funding",405,"DOP_construction_funding_label"),("manpower",485,"DOP_construction_manpower_label")]:
        text_box(f"construction_{kind}_label",label,315,yv-30,330,24,"aldrich_18_outline","center")
        out.extend(["\t\tcontainerWindowType = {",f'\t\t\tname = "construction_{kind}_slider"',f"\t\t\tposition = {{ x = 330 y = {yv} }}","\t\t\tsize = { width = 303 height = 24 }","\t\t\tclipping = no","\t\t\ticonType = {",f'\t\t\t\tname = "construction_{kind}_background"','\t\t\t\tspriteType = "GFX_econ_crt_slider_bg"',"\t\t\t\tposition = { x = 0 y = 11 }","\t\t\t\talwaystransparent = yes","\t\t\t}","\t\t\ticonType = {",f'\t\t\t\tname = "construction_{kind}_dot"','\t\t\t\tspriteType = "GFX_econ_crt_slider_dot"',"\t\t\t\tposition = { x = 0 y = 12 }","\t\t\t\talwaystransparent = yes","\t\t\t\tcenterposition = yes","\t\t\t}","\t\t\tbuttonType = {",f'\t\t\t\tname = "construction_{kind}_decrease"','\t\t\t\tspriteType = "GFX_econ_crt_slider_left"',"\t\t\t\tposition = { x = -9 y = 12 }","\t\t\t\tcenterposition = yes","\t\t\t\tpdx_tooltip = DOP_construction_slider_decrease_tt","\t\t\t}","\t\t\tbuttonType = {",f'\t\t\t\tname = "construction_{kind}_increase"','\t\t\t\tspriteType = "GFX_econ_crt_slider_right"',"\t\t\t\tposition = { x = 312 y = 12 }","\t\t\t\tcenterposition = yes","\t\t\t\tpdx_tooltip = DOP_construction_slider_increase_tt","\t\t\t}","\t\t}",""])
    icon("construction_project_image","GFX_GSA_kanton_shenkansen_research",720,-60)
    out.extend(["\t}","}",""])
    return "\n".join(out)
def loc_file():
    out=["l_simp_chinese:",' BoP_Tab_DOPConstruction:0 "岭南建设总署"',' TNO_DOP_Construction_GUI_Title:0 "岭南建设总署"',' DOP_GNG_construction_category:0 "岭南建设总署"',' GNG_dop_debug_enable_BOP_Construction:0 "§MDOP调试§!：启用岭南建设GUI"',' GNG_dop_debug_reset_construction:0 "§MDOP调试§!：重置全部建设项目"',' GNG_dop_debug_tick_construction:0 "§MDOP调试§!：结算一个建设月"',' DOP_construction_selected_name:0 "[DOP_construction_GetName]"',' DOP_construction_selected_desc:0 "[DOP_construction_GetDesc]"',' DOP_construction_selected_region:0 "§B[DOP_construction_GetRegion]§!"',' DOP_construction_selected_status:0 "状态：[DOP_construction_GetStatus]"',' DOP_construction_status_pending:0 "§Y待完成§!"',' DOP_construction_status_completed:0 "§G已完工§!"',' DOP_construction_selected_numbers:0 "总工程量：[?DOP_construction_selected_total|0]\\n已完成：[?DOP_construction_selected_progress|0]（[?DOP_construction_selected_percent|1]%）\\n基础速度：[?DOP_construction_base_speed|0]/月\\n实际速度：[?DOP_construction_selected_actual_speed|1]/月\\n速度加成：[?DOP_construction_selected_speed_add|1]\\n速度倍率：[?DOP_construction_selected_speed_factor|2]×"',' DOP_construction_funding_label:0 "资金投入：[?DOP_construction_selected_funding|0]%　（[?DOP_construction_selected_funding_min|0]–[?DOP_construction_selected_funding_max|0]%）"',' DOP_construction_manpower_label:0 "人力投入：[?DOP_construction_selected_manpower|0]%　（[?DOP_construction_selected_manpower_min|0]–[?DOP_construction_selected_manpower_max|0]%）"',' DOP_construction_main_progress_tt:0 "每月实际速度 =（基础速度 + 项目速度加成）× 项目速度倍率 ×（资金投入 + 人力投入）÷ 100。"',' DOP_construction_slider_decrease_tt:0 "点击降低 5%。按住 Ctrl 点击直接降至当前下限。"',' DOP_construction_slider_increase_tt:0 "点击提高 5%。按住 Ctrl 点击直接升至当前上限。"']
    seen={}
    for i,(slug,region,name,total,desc) in enumerate(PROJECTS,1):
        out += [f' DOP_construction_project_name_{i}:0 "{name}"',f' DOP_construction_project_desc_{i}:0 "{desc}"',f' DOP_construction_project_region_{i}:0 "{region}"',f' DOP_construction_catalog_{i}:0 "{name}  [?{var(slug,"percent")}|0]%"']
        if region not in seen:out.append(f' DOP_construction_region_{i}:0 "§B{region}§!"');seen[region]=i
    return "\n".join(out)+"\n"
def events_file():
    out=["add_namespace = DOP_GNG_construction",""]
    for i in range(1,17):out += ["country_event = {",f"\tid = DOP_GNG_construction.{i}","\thidden = yes","\tis_triggered_only = yes","\timmediate = { }","}",""]
    return "\n".join(out)
def insert_before_last_brace(text,block):
    pos=text.rfind("}")
    if pos<0:raise RuntimeError("no closing brace")
    return text[:pos].rstrip()+"\n"+block.rstrip()+"\n"+text[pos:]
def modify_existing(root):
    bop=root/"common"/"bop"/"DOP_BoP_Defines.txt";t=bop.read_text(encoding="utf-8-sig")
    line="BoP_Tab_DOPConstruction_GNG = { decision_category = DOP_GNG_construction_category }"
    if line not in t:bop.write_text(t.rstrip()+"\n"+line+"\n",encoding="utf-8")
    ideas=root/"common"/"ideas"/"DOP_BoP_Tab_Dummy.txt";t=ideas.read_text(encoding="utf-8-sig")
    if "BoP_Tab_DOPConstruction =" not in t:
        marker="\t\tBoP_Tab_DOPScienceAcademy = {\n\t\t\t#\n\t\t}"
        t=t.replace(marker,marker+"\n\t\tBoP_Tab_DOPConstruction = {\n\t\t\t#\n\t\t}")
        ideas.write_text(t,encoding="utf-8")
    oa=root/"common"/"on_actions"/"dop_bop_on_actions.txt";t=oa.read_text(encoding="utf-8-sig")
    if "DOP_construction_monthly_tick" not in t:
        block="""    on_monthly = {
        effect = {
            if = {
                limit = { has_country_flag = DOP_construction_initialized }
                DOP_construction_monthly_tick = yes
            }
        }
    }
"""
        t=insert_before_last_brace(t,block);oa.write_text(t,encoding="utf-8")
    debug=root/"common"/"decisions"/"DOP_debug_decision.txt";t=debug.read_text(encoding="utf-8-sig")
    if "GNG_dop_debug_enable_BOP_Construction" not in t:
        block="""\tGNG_dop_debug_enable_BOP_Construction = {
\t\tallowed = { original_tag = GNG }
\t\ticon = GFX_decision_GNG_generic
\t\tvisible = { has_country_flag = GNG_show_debug_decisions NOT = { has_country_flag = DOP_construction_tab_enabled } }
\t\tcomplete_effect = { GNG_BOP_Construction_Initialize = yes }
\t}
\tGNG_dop_debug_reset_construction = {
\t\tallowed = { original_tag = GNG }
\t\ticon = GFX_decision_GNG_generic
\t\tvisible = { has_country_flag = GNG_show_debug_decisions has_country_flag = DOP_construction_tab_enabled }
\t\tcomplete_effect = { DOP_construction_reset = yes }
\t}
\tGNG_dop_debug_tick_construction = {
\t\tallowed = { original_tag = GNG }
\t\ticon = GFX_decision_GNG_generic
\t\tvisible = { has_country_flag = GNG_show_debug_decisions has_country_flag = DOP_construction_initialized }
\t\tcomplete_effect = { DOP_construction_monthly_tick = yes }
\t}
"""
        t=insert_before_last_brace(t,block);debug.write_text(t,encoding="utf-8")
    sl=root/"common"/"scripted_localisation"/"DOP_BOP_Scripted_loc.txt";t=sl.read_text(encoding="utf-8-sig")
    if "BoP_Tab_DOPConstruction" not in t:
        default='\ttext = {\n\t\tlocalization_key = TNO_GlobalConflicts_GUI_Title\n\t}'
        new='\ttext = {\n\t\ttrigger = {\n\t\t\tTag = GNG\n\t\t\tcheck_variable = { TNO_BoP_SelectedTab = token:BoP_Tab_DOPConstruction }\n\t\t}\n\t\tlocalization_key = TNO_DOP_Construction_GUI_Title\n\t}\n'+default
        if default not in t:raise RuntimeError("GetGCname default branch not found")
        sl.write_text(t.replace(default,new,1),encoding="utf-8")
def main():
    root=Path(__file__).resolve().parents[1]
    files={
root/"common"/"scripted_effects"/"DOP_construction_effects.txt":effects_file(),
root/"common"/"scripted_guis"/"DOP_Construction_GUI.txt":scripted_gui_file(),
root/"common"/"scripted_localisation"/"DOP_Construction_Scripted_loc.txt":scripted_loc_file(),
root/"interface"/"GUI"/"DOP_construction.gfx":gfx_file(),
root/"interface"/"GUI"/"DOP_construction_interface.gui":gui_file(),
root/"localisation"/"simp_chinese"/"DOP_Construction_l_simp_chinese.yml":loc_file(),
root/"events"/"DOP_GNG_construction.txt":events_file(),
}
    for p,text in files.items():p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding="utf-8-sig" if p.suffix==".yml" else "utf-8")
    modify_existing(root)
    print(f"projects={len(PROJECTS)} generated_files={len(files)}")
if __name__=="__main__":main()
