"""Fixed two-pass localization control using cached segmentation, no identity routing."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import cv2
import numpy as np
from PIL import Image,ImageDraw

APP=Path(__file__).resolve().parents[1];sys.path.insert(0,str(APP));sys.path.insert(0,str(APP/'vendor/palmprint-recognition-python'))
from pklnet_roi import PKLNetROI
from audit_roi_branches import classical,neural


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('benchmark',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False)
    (a.output/'plan.json').write_text(json.dumps(dict(segmentation='canonical cached model foreground; close3x3; largest component',
        crop='bounding square with 1.2 side multiplier, shifted inside frame; no identity/annotation-based selection',
        inference='same heatmap model on full-resolution crop',limitation='Prototype uses saved segmentation, not deployable until live parity is checked.'),indent=2))
    rows=json.loads((a.benchmark/'heatmap-v3-20261025/records.json').read_text());old=np.load(a.benchmark/'heatmap-v3-20261025/pixels.npz')
    refs={r['sample']:r for r in json.loads((a.benchmark/'reference-roi-20261026/records.json').read_text())}
    ext=PKLNetROI(threads=2,policy="heatmap");pixels={'fused':old['original'],'heatmap':old['heatmap_runtime'],'zoom':[]};records=[];panels=[]
    for i,r in enumerate(rows):
        im=Image.open(a.benchmark/'originals'/r['sample']/'full.jpg').convert('RGB')
        mask=np.asarray(Image.open(a.benchmark/'torch-diagnosis-all'/(r['sample']+'-canonical-foreground.png')).convert('L'))
        mask=cv2.morphologyEx((mask>0).astype(np.uint8),cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
        count,labels,stats,_=cv2.connectedComponentsWithStats(mask)
        if count<2:raise ValueError('empty foreground '+r['sample'])
        x,y,w,h,_=stats[1+int(np.argmax(stats[1:,cv2.CC_STAT_AREA]))]
        _,os,rs,scale=ext._prepare(im)
        # Segmenter emits 75x100. Map its cells to the 300x400 standardized view.
        box_std=np.array([x*4,y*4,(x+w)*4,(y+h)*4],np.float32)
        ends=ext._unrotate_keypoints(box_std,os,rs,scale).reshape(2,2)
        lo=ends.min(0);hi=ends.max(0);center=(hi+lo)/2
        side=min(min(im.size),max(32,float(max(hi-lo))*1.2))
        origin=np.minimum(np.maximum(center-side/2,0),np.array(im.size)-side)
        box=tuple(np.rint(np.r_[origin,origin+side]).astype(int))
        raw,q,d=ext.extract(im.crop(box));q=q+np.array(box[:2]);kp=np.asarray(d['pklnet_keypoints']).reshape(3,2)+np.array(box[:2])
        ref=np.array(refs[r['sample']]['quad'],np.float32)
        intersection=max(0,float(cv2.intersectConvexConvex(q.astype(np.float32),ref)[0]))
        iou=intersection/max(abs(cv2.contourArea(q.astype(np.float32)))+abs(cv2.contourArea(ref))-intersection,1e-9)
        records.append(dict(sample=r['sample'],identity=r['identity'],index=r['index'],fused_valid=r['fused_valid'],
            crop_box=list(map(int,box)),quad=q.tolist(),keypoints=kp.tolist(),reference_iou=iou,diagnostics=d))
        pixels['zoom'].append(raw)
        view=im.copy();draw=ImageDraw.Draw(view);draw.rectangle(box,outline='orange',width=6)
        for polygon,color in [(q,'lime'),(ref,'cyan')]:
            pts=[tuple(map(float,v)) for v in polygon];draw.line(pts+pts[:1],fill=color,width=6)
        view.thumbnail((640,360));panel=Image.new('RGB',(800,390),'white');panel.paste(view,(0,25));panel.paste(Image.fromarray(raw),(660,40))
        ImageDraw.Draw(panel).text((5,3),f"{r['identity']} #{r['index']} IoU {iou:.2f}",fill='black');panels.append(panel)
        print(i+1,round(iou,3),flush=True)
    (a.output/'records.json').write_text(json.dumps(records,indent=2))
    np.savez_compressed(a.output/'pixels.npz',**{k:np.asarray(v) for k,v in pixels.items()})
    for start in range(0,40,10):
        sheet=Image.new('RGB',(1600,1950),'white')
        for j,panel in enumerate(panels[start:start+10]):sheet.paste(panel,((j%2)*800,(j//2)*390))
        sheet.save(a.output/f'comparison-{start}.jpg',quality=94)
    classical(a.output);neural(a.output)


if __name__=='__main__':main()
