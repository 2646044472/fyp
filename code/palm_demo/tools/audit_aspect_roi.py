"""Camera-aspect controls that preserve PKLNet's landscape/portrait rotation."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP))
from pklnet_roi import PKLNetROI, normalize_roi
from palm_app.biometric import load_algorithm


def score_saved(output):
    rows=json.loads((output/'records.json').read_text())
    cached=np.load(output/'pixels.npz')
    selected=['full' if r['branches']['full']['geometry_valid'] else 'center_4x3' for r in rows]
    pixels={'full':cached['full'], 'geometry_fallback':np.stack([cached[k][i] for i,k in enumerate(selected)])}
    records=[dict(sample=r['sample'],identity=r['identity'],index=r['index'],selected=selected[i],
                  **r['branches'][selected[i]]) for i,r in enumerate(rows)]
    results=[]
    for name in ['DoN','FastCC']:
        algorithm=load_algorithm(APP/'vendor/palmprint-recognition-python',name)
        for branch,values in pixels.items():
            features=[algorithm.extract(normalize_roi(value)[0]) for value in values]
            identities=sorted({r['identity'] for r in rows})
            gallery={k:[i for i,r in enumerate(rows) if r['identity']==k and r['index']<=5] for k in identities}
            trials=[]
            for i,row in enumerate(rows):
                if row['index']<=5:continue
                scores={k:float(np.median([algorithm.match(features[i],features[j]) for j in indices])) for k,indices in gallery.items()}
                correct=scores[row['identity']]<min(v for k,v in scores.items() if k!=row['identity'])
                trials.append(dict(sample=row['sample'],identity=row['identity'],scores=scores,correct=bool(correct)))
            results.append(dict(branch=branch,algorithm=name,correct=sum(t['correct'] for t in trials),total=len(trials),trials=trials))
    (output/'fallback-records.json').write_text(json.dumps(records,indent=2))
    (output/'recognition.json').write_text(json.dumps(results,indent=2))
    np.savez_compressed(output/'fallback-pixels.npz',**pixels)
    print(json.dumps([{k:v for k,v in r.items() if k!='trials'} for r in results]),flush=True)


def box_for(image, center, size):
    size = np.minimum(np.asarray(size, float), image.size)
    origin = np.clip(np.asarray(center)-size/2, 0, np.asarray(image.size)-size)
    return tuple(np.rint(np.r_[origin, origin+size]).astype(int))


def foreground_box(image, mask):
    _, osize, rsize, scale = PKLNetROI._prepare(image)
    mask = cv2.morphologyEx((mask > 0).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3,3), np.uint8))
    n, labels, stats, centers = cv2.connectedComponentsWithStats(mask)
    if n < 2:
        return (0, 0, image.width, image.height)
    x,y,w,h,_ = stats[1+int(np.argmax(stats[1:,cv2.CC_STAT_AREA]))]
    ends = PKLNetROI._unrotate_keypoints(np.array([x*4,y*4,(x+w)*4,(y+h)*4], np.float32),osize,rsize,scale).reshape(2,2)
    lo,hi = ends.min(0),ends.max(0)
    aspect = 4/3 if image.width > image.height else 3/4
    width,height = (hi-lo)*1.2
    width = max(width, height*aspect)
    height = width/aspect
    factor = min(1, image.width/width, image.height/height)
    return box_for(image,(hi+lo)/2,(width*factor,height*factor))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("benchmark",type=Path)
    p.add_argument("output",type=Path)
    args=p.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    (args.output/"plan.json").write_text(json.dumps(dict(
        methods=["full", "center_4x3", "foreground_4x3"],
        rules="center: largest 4:3 centered view. foreground: segmentation bounding box, 20% margin, preserve landscape/portrait and 4:3 aspect.",
        selection="Fixed variants, never chosen by sample identity. Prototype foreground uses cached model segmentation.",
        validation="Original-image minimum span unchanged. All images retained. Reference geometry first, then fixed gallery/probe scoring."
    ),indent=2))
    ext=PKLNetROI(threads=2,policy="heatmap");ext._ensure_loaded();geo=ext._roi_extractor
    refs={r['sample']:r for r in json.loads((args.benchmark/'reference-roi-20261026/records.json').read_text())}
    inputs=json.loads((args.benchmark/'extraction_manifest.json').read_text())
    records=[];pixels={k:[] for k in ['full','center_4x3','foreground_4x3']}
    for count,src in enumerate(inputs,1):
        path=args.benchmark/'originals'/src['sample']/'full.jpg'
        assert hashlib.sha256(path.read_bytes()).hexdigest()==src['original_sha256']
        image=Image.open(path).convert('RGB')
        mask=np.asarray(Image.open(args.benchmark/'torch-diagnosis-all'/(src['sample']+'-canonical-foreground.png')).convert('L'))
        aspect=4/3 if image.width>image.height else 3/4
        width=min(image.width,image.height*aspect);height=width/aspect
        boxes={'full':(0,0,*image.size), 'center_4x3':box_for(image,np.asarray(image.size)/2,(width,height)),
               'foreground_4x3':foreground_box(image,mask)}
        row=dict(sample=src['sample'],identity=src['subject']+':'+src['hand'],index=src['sample_index'],fused_valid=src['roi_geometry_valid'],branches={})
        panel=Image.new('RGB',(1200,350),'white')
        for col,(name,box) in enumerate(boxes.items()):
            raw,quad,details=ext.extract(image.crop(box));quad+=np.asarray(box[:2])
            kp=np.asarray(details['pklnet_keypoints']).reshape(3,2)+np.asarray(box[:2])
            span=float(np.linalg.norm(kp[0]-kp[1])/min(image.size))
            valid=bool((quad>=0).all() and (quad[:,0]<image.width).all() and (quad[:,1]<image.height).all() and span>=.1)
            ref=np.asarray(refs[row['sample']]['quad'],np.float32)
            area=max(0,cv2.intersectConvexConvex(quad.astype(np.float32),ref)[0])
            iou=area/max(cv2.contourArea(quad)+cv2.contourArea(ref)-area,1e-9)
            row['branches'][name]=dict(box=list(map(int,box)),keypoints=kp.tolist(),quad=quad.tolist(),reference_iou=iou,geometry_valid=valid)
            pixels[name].append(raw)
            view=image.copy();draw=ImageDraw.Draw(view);draw.rectangle(box,outline='orange',width=5)
            for polygon,color in [(quad,'lime'),(ref,'cyan')]:
                pts=[tuple(map(float,p)) for p in polygon];draw.line(pts+pts[:1],fill=color,width=7)
            view.thumbnail((390,220));panel.paste(view,(col*400,25));panel.paste(Image.fromarray(raw).resize((96,96)),(col*400,250))
            ImageDraw.Draw(panel).text((col*400+3,3),f'{name} #{count} IoU={iou:.2f} valid={valid}',fill='black')
        panel.save(args.output/(row['sample']+'.jpg'),quality=92);records.append(row)
        print(count,{k:round(v['reference_iou'],3) for k,v in row['branches'].items()},flush=True)
    summary={name:dict(median_iou=float(np.median([r['branches'][name]['reference_iou'] for r in records])),
                       below_half=sum(r['branches'][name]['reference_iou']<.5 for r in records),
                       geometry_pass=sum(r['branches'][name]['geometry_valid'] for r in records)) for name in pixels}
    (args.output/'records.json').write_text(json.dumps(records,indent=2));(args.output/'geometry.json').write_text(json.dumps(summary,indent=2))
    np.savez_compressed(args.output/'pixels.npz',**{k:np.stack(v) for k,v in pixels.items()})
    print(json.dumps(summary),flush=True)
    score_saved(args.output)


if __name__=='__main__':main()
