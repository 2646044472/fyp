"""Prototype image-boundary refinement, using no manual landmarks at inference."""
import argparse
import itertools
import json
from pathlib import Path
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw

APP=Path(__file__).resolve().parents[1];sys.path.insert(0,str(APP));sys.path.insert(0,str(APP/'vendor/palmprint-recognition-python'))
from pklnet_roi import PKLNetROI
from audit_roi_branches import classical,neural


def refine(image,smallmask):
    view=image.resize((640,360));bgr=cv2.cvtColor(np.asarray(view),cv2.COLOR_RGB2BGR)
    _,_,rotated,scale=PKLNetROI._prepare(image)
    mask=cv2.resize(smallmask,(300,400),interpolation=cv2.INTER_NEAREST)
    mask=mask[:round(rotated[0]/scale[1]),:round(rotated[1]/scale[0])]
    if image.width>image.height:mask=cv2.rotate(mask,cv2.ROTATE_90_COUNTERCLOCKWISE)
    mask=cv2.resize(mask,(640,360),interpolation=cv2.INTER_NEAREST)
    mask=(mask>0).astype(np.uint8)
    mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    search=cv2.dilate(mask,np.ones((31,31),np.uint8))
    sure=cv2.erode(mask,np.ones((5,5),np.uint8))
    gc=np.where(search,cv2.GC_PR_BGD,cv2.GC_BGD).astype(np.uint8)
    gc[mask>0]=cv2.GC_PR_FGD;gc[sure>0]=cv2.GC_FGD
    cv2.setRNGSeed(20261026)
    cv2.grabCut(bgr,gc,None,np.zeros((1,65)),np.zeros((1,65)),3,cv2.GC_INIT_WITH_MASK)
    binary=((gc==cv2.GC_FGD)|(gc==cv2.GC_PR_FGD)).astype(np.uint8)
    contours,_=cv2.findContours(binary,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    contour=max(contours,key=cv2.contourArea)
    contour=cv2.approxPolyDP(contour,1.5,True)
    hull=cv2.convexHull(contour,returnPoints=False);defects=cv2.convexityDefects(contour,hull)
    candidates=[]
    if defects is not None:
        for start,end,far,depth in defects.reshape(-1,4):
            a,b,c=[contour.reshape(-1,2)[n].astype(float) for n in (start,end,far)]
            angle=np.degrees(np.arccos(np.clip(np.dot(a-c,b-c)/(np.linalg.norm(a-c)*np.linalg.norm(b-c)),-1,1)))
            if depth/256>5 and angle<100:candidates.append(dict(point=c.tolist(),depth=depth/256,angle=float(angle)))
    candidates=sorted(candidates,key=lambda c:-c['depth'])[:7]
    triples=[]
    for triple in itertools.combinations(candidates,3):
        points=np.array([c['point'] for c in triple]);dist=np.linalg.norm(points[:,None]-points[None,:],axis=2)
        ia,ib=np.unravel_index(dist.argmax(),dist.shape);ic=3-ia-ib
        span=dist[ia,ib];a,b,c=points[ia],points[ib],points[ic]
        if span<24:continue
        t=float(np.dot(c-a,b-a)/span**2);height=abs(float(np.linalg.det(np.stack((b-a,c-a)))))/span
        if not .2<t<.8 or height/span>.4:continue
        # Three adjacent finger webs should form a roughly straight, evenly
        # spaced chain. Selection uses contour geometry only, not reference IDs.
        penalty=height/span+abs(t-.5)
        triples.append((penalty,a,b,triple))
    if not triples:return None,binary,candidates
    _,a,b,triple=min(triples,key=lambda row:row[0])
    moments=cv2.moments(contour);center=np.array([moments['m10']/moments['m00'],moments['m01']/moments['m00']])
    return np.stack((a,b,center)),binary,candidates


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('benchmark',type=Path);parser.add_argument('output',type=Path);args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=False);cv2.setNumThreads(1)
    (args.output/'plan.json').write_text(json.dumps(dict(method='cached segmenter + fixed GrabCut refinement + three narrow convexity defects',
        selection='roughly collinear equally spaced triplet; outside two webs; contour centroid picks palm side',fallback='unchanged heatmap if no triplet',
        boundary='prototype, no per-ID selection, no manual annotations used at inference'),indent=2))
    rows=json.loads((args.benchmark/'heatmap-v3-20261025/records.json').read_text());old=np.load(args.benchmark/'heatmap-v3-20261025/pixels.npz')
    ext=PKLNetROI(policy="heatmap");ext._ensure_loaded();geo=ext._roi_extractor
    pixels={'fused':old['original'],'heatmap':old['heatmap_runtime'],'contour':[]};records=[];panels=[]
    for i,r in enumerate(rows):
        image=Image.open(args.benchmark/'originals'/r['sample']/'full.jpg').convert('RGB')
        small=np.asarray(Image.open(args.benchmark/'torch-diagnosis-all'/(r['sample']+'-canonical-foreground.png')).convert('L'))
        kp,mask,candidates=refine(image,small)
        if kp is not None:
            native=kp*np.array([image.width/640,image.height/360]);quad=np.array(geo.getROIckp(native[0],native[1],geo.isAntiClock(native.reshape(-1))),np.float32)
            valid=bool((quad>=0).all() and (quad[:,0]<image.width).all() and (quad[:,1]<image.height).all())
        else:valid=False
        if valid:raw=geo.getROIimg(cv2.cvtColor(np.asarray(image),cv2.COLOR_RGB2BGR),quad)
        else:raw=old['heatmap_runtime'][i];quad=np.array(r['diagnostics']['roi_quad_full'])
        pixels['contour'].append(raw)
        records.append(dict(sample=r['sample'],identity=r['identity'],index=r['index'],fused_valid=r['fused_valid'],
            used_contour=valid,quad=quad.tolist(),candidates=candidates))
        overlay=image.resize((640,360));draw=ImageDraw.Draw(overlay)
        for c in candidates:
            x,y=c['point'];draw.ellipse((x-3,y-3,x+3,y+3),fill='red')
        q=quad/np.array([image.width/640,image.height/360]);pts=[tuple(p) for p in q];draw.line(pts+pts[:1],fill='lime',width=2)
        panel=Image.new('RGB',(800,390),'white');panel.paste(overlay,(0,25));panel.paste(Image.fromarray(raw),(660,25))
        panel.paste(Image.fromarray(mask*255).resize((128,72)),(660,170));ImageDraw.Draw(panel).text((5,3),f"{r['identity']} #{r['index']} contour={valid}",fill='black');panels.append(panel)
        print(i+1,valid,flush=True)
    (args.output/'records.json').write_text(json.dumps(records,indent=2))
    np.savez_compressed(args.output/'pixels.npz',**{k:np.asarray(v) for k,v in pixels.items()})
    for start in range(0,40,10):
        sheet=Image.new('RGB',(1600,1950),'white')
        for j,panel in enumerate(panels[start:start+10]):sheet.paste(panel,((j%2)*800,(j//2)*390))
        sheet.save(args.output/f'comparison-{start}.jpg',quality=94)
    classical(args.output);neural(args.output)


if __name__=='__main__':main()
