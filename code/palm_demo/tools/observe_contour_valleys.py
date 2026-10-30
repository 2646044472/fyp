"""Read-only silhouette/convexity-defect feasibility screen, not a ROI repair.

Image-only function, no labels/model/identity scores. Observe both Otsu
polarities without selecting a recognition winner. No source pipeline changes.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import time

import cv2
import numpy as np
from PIL import Image,ImageDraw


def silhouettes(rgb):
    rgb=np.asarray(rgb,np.uint8);height,width=rgb.shape[:2]
    scale=min(1.,640/max(width,height))
    small=cv2.resize(rgb,(round(width*scale),round(height*scale)),interpolation=cv2.INTER_AREA) if scale<1 else rgb.copy()
    gray=cv2.cvtColor(small,cv2.COLOR_RGB2GRAY)
    threshold,bright=cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    records=[];displays=[]
    for name,mask in [('bright',bright),('dark',255-bright)]:
        contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        record=dict(polarity=name,otsu_threshold=threshold,scale=scale,defects=[],candidate_valleys=[],error=None)
        display=cv2.cvtColor(mask,cv2.COLOR_GRAY2RGB)
        if contours:
            contour=np.asarray(max(contours,key=cv2.contourArea),np.int32).reshape(-1,1,2);area=float(cv2.contourArea(contour))
            component=np.zeros_like(mask);cv2.drawContours(component,[contour],-1,255,-1)
            record.update(component_area_fraction=area/mask.size,
                touched_image_edges=sum(bool(v.any()) for v in [component[0,:],component[-1,:],component[:,0],component[:,-1]]))
            padded=cv2.copyMakeBorder(component,1,1,1,1,cv2.BORDER_CONSTANT,value=0)
            distance=cv2.distanceTransform(padded,cv2.DIST_L2,5)[1:-1,1:-1]
            _,radius,_,center=cv2.minMaxLoc(distance);record.update(distance_center=list(center),distance_radius=radius)
            cv2.drawContours(display,[contour],-1,(180,150,100),1);cv2.circle(display,center,4,(255,60,60),-1)
            if len(contour)>=4:
                hull=cv2.convexHull(contour,returnPoints=False)
                try:defects=cv2.convexityDefects(contour,hull) if len(hull)>=3 else None
                except cv2.error as error:record['error']=str(error);defects=None
                for entry in [] if defects is None else np.asarray(defects).reshape(-1,4):
                    start,end,far,depth=map(int,entry)
                    a,b,c=[contour[i,0].astype(float) for i in [start,end,far]]
                    u,v=a-c,b-c;den=float(np.linalg.norm(u)*np.linalg.norm(v))
                    angle=math.degrees(math.acos(float(np.clip(np.dot(u,v)/den,-1,1)))) if den else 180.
                    depth=depth/256.;candidate=angle<90 and depth>=.02*max(mask.shape)
                    item=dict(start=a.tolist(),end=b.tolist(),far=c.tolist(),depth=depth,
                        normalized_depth=depth/max(mask.shape),angle_deg=angle,candidate=candidate)
                    record['defects'].append(item)
                    if candidate:
                        record['candidate_valleys'].append(c.tolist())
                        cv2.line(display,tuple(a.astype(int)),tuple(b.astype(int)),(70,130,240),1)
                        cv2.circle(display,tuple(c.astype(int)),4,(50,255,230),-1)
        else:record.update(component_area_fraction=0.,touched_image_edges=0)
        record['candidate_count']=len(record['candidate_valleys']);records.append(record);displays.append(display)
    return small,records,displays


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('manifest',type=Path);p.add_argument('output',type=Path);p.add_argument('--selection',required=True,type=Path);a=p.parse_args()
    a.output.mkdir(exist_ok=False);rows=json.loads(a.manifest.read_text());assert len(rows)==169
    selected=json.loads(a.selection.read_text())['samples']
    protocol=dict(scope=__doc__,selection=selected,selection_rule='All three remaining errors and one fixed original per device, declared before contour output.',
        input='Original device RGB, no EXIF adjustment (same frozen replay decoder). Largest component per Otsu polarity at at most 640px.',
        candidate_rule='Observe every convexity defect; fixed angle<90deg and normalized depth>=0.02 engineering screen, no fitting.',
        threshold_fit=False,roi_or_recognition_changed=False,
        limits='Candidate count is not anatomical correctness. Both polarities are retained; no score-guided polarity/pair choice. Fixed development photos, not independent validation.',
        source_sha256=hashlib.sha256(Path(__file__).read_bytes().replace(b'\r\n',b'\n')).hexdigest())
    (a.output/'protocol.json').write_text(json.dumps(protocol,indent=2),encoding='utf-8')
    canvas=Image.new('RGB',(1200,330*len(selected)),(20,25,34));records=[]
    for row in rows:
        data=Path(row['original']).read_bytes();assert hashlib.sha256(data).hexdigest()==row['sha256']
        with Image.open(row['original']) as encoded:rgb=np.asarray(encoded.convert('RGB'))
        tick=time.perf_counter();small,observations,displays=silhouettes(rgb)
        record=dict(sample=row['sample'],device=row['device'],ms=(time.perf_counter()-tick)*1000,observations=observations)
        records.append(record)
        if row['sample'] in selected:
            y=selected.index(row['sample'])*330
            for col,view in enumerate([small,*displays]):
                image=Image.fromarray(view);image.thumbnail((395,295));canvas.paste(image,(col*400,y))
                label=row['sample'] if col==0 else observations[col-1]['polarity']+' candidates='+str(observations[col-1]['candidate_count'])
                ImageDraw.Draw(canvas).text((col*400+5,y+300),label,fill='white')
    canvas.save(a.output/'fixed-originals-and-masks.jpg',quality=90)
    summary={device:{polarity:dict(frames=sum(r['device']==device for r in records),
        at_least_two=sum(r['device']==device and r['observations'][index]['candidate_count']>=2 for r in records),
        at_least_three=sum(r['device']==device and r['observations'][index]['candidate_count']>=3 for r in records))
        for index,polarity in enumerate(['bright','dark'])} for device in ['new-camera','old-camera']}
    result=dict(complete=True,protocol=protocol,summary=summary,records=records,
        originals_unchanged=all(hashlib.sha256(Path(r['original']).read_bytes()).hexdigest()==r['sha256'] for r in rows))
    (a.output/'results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(summary),flush=True)


if __name__=='__main__':main()
