"""Prepare tightly cropped pie-only emblem copies without redrawing/resampling source art."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

ROOT=Path(__file__).resolve().parents[1]
SOURCES={"GNG":"广东黑白.png","USA":"美国国徽.png","ITA":"意大利方案1.png","GER":"德国黑白.png","JAP":"日本黑白.png"}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest().upper()
def prepare_one(tag,long_edge=150):
    path=ROOT/"gfx/resources"/SOURCES[tag]
    original=np.array(Image.open(path).convert("RGBA"))
    rgba=original.copy();alpha=rgba[...,3]
    labels,n=ndimage.label(alpha>0,structure=np.ones((3,3),bool))
    sizes=np.bincount(labels.ravel());sizes[0]=0
    major=sizes[labels]>8
    removed=[]
    if major.any():
        yy,xx=np.nonzero(major);main=(int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1))
        slices=ndimage.find_objects(labels)
        candidates=[]
        for label_id,area in enumerate(sizes):
            if not 0<area<=8:continue
            sy,sx=slices[label_id-1]
            gap=max(main[0]-sx.stop,sx.start-main[2],main[1]-sy.stop,sy.start-main[3],0)
            if gap>8:candidates.append(label_id)
        noise=np.isin(labels,candidates) if candidates else np.zeros_like(alpha,bool)
        # Only isolated exterior specks, never connected lines, small stars or interior detail.
        if noise.sum()<=8 and alpha[noise].sum()/max(float(alpha.sum()),1)<.00025:
            rgba[noise,3]=0
            removed=[{"bbox":[slices[i-1][1].start,slices[i-1][0].start,slices[i-1][1].stop,slices[i-1][0].stop],
                      "pixels":int(sizes[i])} for i in candidates]
    bbox=Image.fromarray(rgba[...,3]).getbbox()
    if not bbox:raise ValueError(f"Empty alpha: {path}")
    x0,y0,x1,y1=bbox
    cropped=Image.fromarray(rgba[y0:y1,x0:x1])
    a=np.array(cropped.getchannel("A"),dtype=float)/255
    h,w=a.shape
    xx=np.arange(w,dtype=float)+.5;yy=np.arange(h,dtype=float)+.5
    pivot=[float((a.sum(axis=0)*xx).sum()/a.sum()/w),
           float((a.sum(axis=1)*yy).sum()/a.sum()/h)]
    scale=long_edge/max(w,h);display=[w*scale,h*scale]
    transform=[display[0]/360,display[1]/360,*pivot]
    detail={"tag":tag,"source":path.relative_to(ROOT).as_posix(),"source_sha256":sha(path),
            "runtime":f"gfx/interface/bop/DOP_SCW_pie_faction_{tag}.png",
            "source_size":[original.shape[1],original.shape[0]],"crop":list(bbox),"cropped_size":[w,h],
            "removed_exterior_specks":removed,"alpha_pivot":pivot,
            "display_size_px":display,"colortwo":transform,
            "original_crop_pixels_preserved":bool(np.array_equal(np.array(cropped),original[y0:y1,x0:x1]))}
    return cropped,detail

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--long-edge",type=float,default=150)
    args=parser.parse_args()
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    if not 80<=args.long_edge<=220:raise ValueError("Choose a bounded inlay size")
    assets=out/"assets";assets.mkdir(exist_ok=True)
    sheet=Image.new("RGB",(1050,255),(20,31,39));d=ImageDraw.Draw(sheet)
    font=ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf",14)
    report={"size_rule":"All five visible alpha bounds share one long edge",
            "long_edge_px":args.long_edge,"pivot":"Alpha-weighted visible centre",
            "source_policy":"Original gfx/resources PNGs unchanged; only runtime copies are trimmed",
            "icons":[]}
    for i,tag in enumerate(SOURCES):
        im,m=prepare_one(tag,args.long_edge)
        target=assets/Path(m["runtime"]).name
        im.save(target)
        assert np.array_equal(np.array(Image.open(target)),np.array(im))
        m["output_sha256"]=sha(target);report["icons"].append(m)
        width,height=[round(x) for x in m["display_size_px"]]
        a=im.getchannel("A").resize((width,height),Image.Resampling.LANCZOS)
        tile=Image.new("RGBA",(width,height),(215,227,233,255));tile.putalpha(a)
        center=(i*210+105,116)
        pos=(round(center[0]-m["alpha_pivot"][0]*width),round(center[1]-m["alpha_pivot"][1]*height))
        sheet.paste(tile,pos,tile)
        d.line((center[0]-6,center[1],center[0]+6,center[1]),fill=(91,160,167))
        d.line((center[0],center[1]-6,center[0],center[1]+6),fill=(91,160,167))
        d.text((i*210+12,218),f"{tag}: {width} x {height}",font=font,fill=(183,208,216))
    d.text((12,240),"ALPHA-PLACEMENT CHECK / NOT A GAME CAPTURE",font=ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf",11),fill=(124,157,170))
    sheet.save(out/"placement_check.png")
    (out/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
