from __future__ import annotations
import argparse,re,zipfile
from pathlib import Path

FILES=[("收地事件链.txt",1),("索长.txt",5),("西南危机风味事件.txt",11),("新财界配套事件.txt",23),("政改.txt",32),("GAW预告.txt",39)]
CHAIN={(1,0):[4],(1,1):[2],(2,0):[3],(3,0):[4],(7,0):[8],(8,0):[9],(9,0):[10],(11,0):[12],(12,0):[13],(13,0):[14],(14,0):[15],(15,0):[16],(16,0):[17,18,19,20,21],(21,0):[22],(23,0):[24],(24,0):[25],(25,0):[26],(26,0):[27],(27,0):[28],(28,0):[29],(29,0):[30],(30,0):[31],(32,0):[33],(33,0):[34],(34,0):[35],(36,0):[38],(37,0):[38]}
SEATS={6:[(3,2),(6,2)],9:[(3,-3),(6,3)],10:[(3,-7),(4,3),(5,2),(7,2)]}
OPT=re.compile(r"^选项(?:\s*([0-9一二三四五六七八九十]+))?\s*[：:]\s*(.*)$")
TT=re.compile(r"^【tooltip】\s*(.*)$",re.I)
EFF=re.compile(r"^【效果】\s*(.*)$")

def esc(x): return x.replace("\\","\\\\").replace('"','\\"').replace("\r","").replace("\n","\\n")
def norm(x): return x.replace("【领导人名称】","[ROOT.GetLeader]").strip()
def decode(b):
    for e in ("utf-8-sig","gb18030","utf-16"):
        try:return b.decode(e)
        except UnicodeDecodeError:pass
    raise RuntimeError("unsupported encoding")
def blocks(x):return [p.strip() for p in re.split(r"(?:\r?\n){2,}",x) if p.strip()]
def parse(b):
    ls=[x.strip() for x in b.splitlines() if x.strip()]
    title=norm(ls[0]); body=[]; opts=[]; cur=None
    for line in ls[1:]:
        m=OPT.match(line)
        if m:
            cur={"text":norm(m.group(2)),"tooltips":[],"effects":[]};opts.append(cur);continue
        m=TT.match(line)
        if m and cur is not None:cur["tooltips"].append(norm(m.group(1)));continue
        m=EFF.match(line)
        if m and cur is not None:cur["effects"].append(norm(m.group(1)));continue
        (body if cur is None else cur["tooltips"]).append(norm(line))
    return title,"\n\n".join(body),opts or [{"text":"继续。","tooltips":[],"effects":[]}]

def legco(f,n):return [f"set_temp_variable = {{ GNG_legco_faction_temp = {f} }}",f"set_temp_variable = {{ GNG_legco_seat_temp = {n} }}","GNG_change_legco_seats = yes"]
def effects(eid):
    out=[]
    for f,n in SEATS.get(eid,[]):out+=legco(f,n)
    if eid==16:out+=["for_each_loop = {","    array = GNG_states_list","    GNG_japanese_pop_change = -7.5","    GNG_chinese_pop_change = -7.5","    GNG_japanese_app_change = -2.5","    GNG_zhujin_app_change = -2.5","    GNG_chinese_app_change = -5","}"]
    return out
def chain(eid,oi):
    if eid==35:return ["if = {","    limit = { check_variable = { GNG_ending_referendum = 1 } }","    country_event = { id = DOP_GNG_zip.36 days = 1 }","    else = { country_event = { id = DOP_GNG_zip.37 days = 1 } }","}"]
    ts=CHAIN.get((eid,oi),[])
    return [f"country_event = {{ id = DOP_GNG_zip.{t} days = {1 if len(ts)==1 else (i+1)*2} }}" for i,t in enumerate(ts)]

def generate(zpath,root):
    parsed=[]
    with zipfile.ZipFile(zpath) as z:
        for name,start in FILES:
            for i,b in enumerate(blocks(decode(z.read(name)))):
                parsed.append((start+i,*parse(b)))
    ids=[x[0] for x in parsed]
    if ids!=list(range(1,44)):raise RuntimeError(f"unexpected ids {ids}")
    ev=["# Generated from 事件.zip by tools/import_dop_zip.py.","# Only explicitly annotated effects are scripted.","add_namespace = DOP_GNG_zip",""]
    loc=["l_simp_chinese:"]
    for eid,title,desc,opts in parsed:
        k=f"DOP_GNG_zip.{eid}"
        loc += [f' {k}.t:0 "{esc(title)}"',f' {k}.d:0 "{esc(desc)}"']
        ev += ["country_event = {",f"    id = {k}",f"    title = {k}.t",f"    desc = {k}.d","    picture = GFX_report_event_IBR_meeting_small","    is_triggered_only = yes",""]
        for oi,o in enumerate(opts):
            ok=f"{k}.a{oi+1}";loc.append(f' {ok}:0 "{esc(o["text"])}"')
            ev += ["    option = {",f"        name = {ok}"]
            tips=o["tooltips"]+o["effects"]
            if tips:
                tk=f"{ok}.tt";loc.append(f' {tk}:0 "{esc(chr(10).join(tips))}"');ev.append(f"        custom_effect_tooltip = {tk}")
            lines=(effects(eid) if oi==0 else [])+chain(eid,oi)
            ev += ["        "+x for x in lines]+["    }",""]
        ev += ["}",""]
    ep=root/"events"/"DOP_GNG_zip.txt";lp=root/"localisation"/"simp_chinese"/"DOP_GNG_zip_l_simp_chinese.yml"
    ep.parent.mkdir(parents=True,exist_ok=True);lp.parent.mkdir(parents=True,exist_ok=True)
    ep.write_text("\n".join(ev),encoding="utf-8");lp.write_text("\n".join(loc)+"\n",encoding="utf-8-sig")
    return len(parsed),sum(len(x[3]) for x in parsed)

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--zip",required=True,type=Path);p.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args()
    e,o=generate(a.zip,a.root);print(f"generated_events={e}\ngenerated_options={o}")
