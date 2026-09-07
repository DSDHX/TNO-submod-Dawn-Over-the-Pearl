"""Verify cropped pie inlays and compile the shader; never controls the game."""
import argparse,ctypes as c,hashlib,json,re
from pathlib import Path
import numpy as np
from PIL import Image
from normalize_dop_pie_inlays import ROOT,prepare_one,SOURCES
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def named_block(text,name):
    at=text.index('name = "'+name+'"');start=text.rfind("progressbartype = {",0,at)
    begin=text.index("{",start);depth=1
    for j in range(begin+1,len(text)):
        depth+=(text[j]=="{")-(text[j]=="}")
        if depth==0:return text[start:j+1]
    raise AssertionError(name)
def blob_bytes(blob):
    if not blob:return b""
    v=c.cast(blob,c.POINTER(c.POINTER(c.c_void_p))).contents
    ptr=c.WINFUNCTYPE(c.c_void_p,c.c_void_p)(v[3])
    size=c.WINFUNCTYPE(c.c_size_t,c.c_void_p)(v[4])
    return c.string_at(ptr(blob),size(blob))
def release(blob):
    if blob:
        v=c.cast(blob,c.POINTER(c.POINTER(c.c_void_p))).contents
        c.WINFUNCTYPE(c.c_ulong,c.c_void_p)(v[2])(blob)
def compile_shader(source,tno):
    helpers="\n".join(re.findall(r"Code\s*\[\[(.*?)\]\]",(tno/"gfx/FX/tno_functions.fxh").read_text(),re.S))
    vi=re.search(r"VertexStruct VS_INPUT\s*\{(.*?)\};",source,re.S)[1]
    vo=re.search(r"VertexStruct VS_OUTPUT\s*\{(.*?)\};",source,re.S)[1].replace("PDX_POSITION","SV_POSITION")
    hdr=f"struct VS_INPUT{{{vi}}};struct VS_OUTPUT{{{vo}}};\n"
    hdr+="float4x4 WorldViewProjectionMatrix;float4 vFirstColor,vSecondColor;float CurrentState;\n"
    hdr+="sampler2D TextureOne:register(s0);sampler2D TextureTwo:register(s1);\nfloat mod(float a,float b){return a-floor(a/b)*b;}\n"+helpers
    compiler=c.WinDLL("d3dcompiler_47.dll").D3DCompile
    compiler.argtypes=[c.c_void_p,c.c_size_t,c.c_char_p,c.c_void_p,c.c_void_p,c.c_char_p,c.c_char_p,c.c_uint,c.c_uint,c.POINTER(c.c_void_p),c.POINTER(c.c_void_p)]
    compiler.restype=c.c_long
    result=[]
    for entry,profile in [("VertexShader","vs_4_0"),("PixelColor","ps_4_0"),("PixelTexture","ps_4_0")]:
        body=re.search(r"MainCode "+entry+r"\s*\[\[(.*?)\]\]",source,re.S)[1].replace("PDX_COLOR","SV_TARGET")
        code=(hdr+body).encode("ascii");b,e=c.c_void_p(),c.c_void_p()
        hr=compiler(code,len(code),b"pie_inlays",None,None,b"main",profile.encode(),1<<12,0,c.byref(b),c.byref(e))
        err=blob_bytes(e).decode(errors="replace").strip();size=len(blob_bytes(b));release(e);release(b)
        assert hr>=0 and size,(entry,err)
        result.append({"entry":entry,"bytes":size,"diagnostics":err})
    return result
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",type=Path,default=ROOT)
    ap.add_argument("--reference",type=Path,required=True)
    ap.add_argument("--tno-root",type=Path,default=Path(r"D:\Steam\steamapps\workshop\content\394360\2438003901"))
    args=ap.parse_args();root=args.root
    gfx=(root/"interface/GUI/SCW_generic.gfx").read_text(encoding="utf-8-sig")
    before=(args.reference/"before/interface/GUI/SCW_generic.gfx").read_text(encoding="utf-8-sig")
    restored=gfx;records=[]
    for tag in SOURCES:
        expected,m=prepare_one(tag)
        im=Image.open(root/m["runtime"]).convert("RGBA")
        assert np.array_equal(np.array(im),np.array(expected)),tag
        w,h=im.size
        assert im.getchannel("A").getbbox()==(0,0,w,h),"Transparent outer rows remain"
        sub=named_block(gfx,f"GFX_GCW_speedrun_pie_{tag}_chart")
        old=named_block(before,f"GFX_GCW_speedrun_pie_{tag}_chart")
        line=re.search(r"colortwo\s*=\s*\{([^}]+)\}",sub)[0]
        vals=np.array([float(v) for v in re.search(r"\{([^}]+)\}",line)[1].split()])
        assert np.max(abs(vals-np.array(m["colortwo"])))<1e-8
        assert abs(max(vals[:2]*360)-150)<1e-5
        assert abs((vals[0]/vals[1])-(w/h))<1e-7
        error=np.linalg.norm((np.array(m["alpha_pivot"])-vals[2:])*vals[:2]*360)
        assert error<.001
        quant=np.rint(vals*255)/255
        qerror=np.linalg.norm((np.array(m["alpha_pivot"])-quant[2:])*quant[:2]*360)
        assert qerror<.75
        old_line=re.search(r"colortwo\s*=\s*\{[^}]+\}",old)[0]
        repaired=sub.replace(line,old_line)
        assert repaired==old,"Changed fields other than inlay placement"
        restored=restored.replace(sub,old)
        assert m["original_crop_pixels_preserved"]
        records.append({"tag":tag,"size":im.size,"display":list(vals[:2]*360),
                        "centre_error_px":error,"centre_error_if_8bit":qerror,
                        "removed_noise":m["removed_exterior_specks"]})
    assert restored.rstrip()==before.rstrip(),"Other sprite registrations changed"
    for m in json.loads((args.reference/"protected.json").read_text()):
        assert sha(ROOT/m["path"])==m["sha256"],m["path"]
    for m in json.loads((args.reference/"manifest.json").read_text())["icons"]:
        assert sha(ROOT/m["source"])==m["source_sha256"]
    shader=(root/"gfx/FX/DOP_scw_faction_pie.shader").read_text()
    assert "float2 sourceUV = vSecondColor.zw" in shader
    assert "/ max(vSecondColor.xy" in shader
    assert "CurrentState * 100001.f - 1.f" in shader and "0.21 * float2" in shader
    programs=compile_shader(shader,args.tno_root)
    result={"result":"PASS","icons":records,"legend_layout_and_sources":"unchanged",
            "programs":programs,"boundary":"Pixel/data/compiler checks, not in-game execution"}
    (args.reference/"validation.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()

