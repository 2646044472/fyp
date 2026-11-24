"""Visually annotated valley ROI control, frozen before recognition scoring.

Annotations are a single assistant review, not human ground truth or an automatic
localizer. Preserve all originals and the original gallery/probe split.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw

APP=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(APP))
sys.path.insert(0,str(APP/'vendor/palmprint-recognition-python'))
from pklnet_roi import PKLNET_ROOT, normalize_roi
from audit_roi_branches import classical, neural


def prepare(benchmark,out):
    out.mkdir(parents=True,exist_ok=False)
    records=json.loads((benchmark/'extraction_manifest.json').read_text())
    random.Random(20261026).shuffle(records)
    mapping={f'S{i:02}':r for i,r in enumerate(records)}
    (out/'mapping.json').write_text(json.dumps(mapping,indent=2))
    plan=dict(protocol='Index-middle valley and ring-little valley; third point inside palm selects side. Same PalmKit alpha=.15 beta=1.2 for all images.',
        coordinates='640x360 displayed original image, before label offset',reviewer='assistant visual estimates; not independently reviewed human ground truth',
        labels='Anonymous shuffled IDs in annotation sheets, no prediction overlays or recognition scores. Reviewer has seen earlier dataset reports; not a blinded study.',
        scoring='Freeze annotations before scoring; all40 originals, fixed first5 gallery last5 probe; no quality filter.')
    (out/'plan.json').write_text(json.dumps(plan,indent=2))
    for start in range(0,40,4):
        sheet=Image.new('RGB',(1280,800),'white')
        for j in range(4):
            key=f'S{start+j:02}';r=mapping[key]
            path=benchmark/'originals'/r['sample']/'full.jpg'
            assert hashlib.sha256(path.read_bytes()).hexdigest()==r['original_sha256']
            im=Image.open(path).convert('RGB').resize((640,360))
            draw=ImageDraw.Draw(im,'RGBA')
            for x in range(0,640,40):
                draw.line((x,0,x,359),fill=(255,255,0,45));draw.text((x+2,1),str(x),fill='yellow',stroke_fill='black',stroke_width=1)
            for y in range(40,360,40):
                draw.line((0,y,639,y),fill=(255,255,0,45));draw.text((1,y+1),str(y),fill='yellow',stroke_fill='black',stroke_width=1)
            x=(j%2)*640;y=(j//2)*400
            sheet.paste(im,(x,y+30));ImageDraw.Draw(sheet).text((x+5,y+8),key,fill='black')
        sheet.save(out/f'annotate-{start:02}.jpg',quality=97)


def render(benchmark,out):
    if (out/'scored-input-hashes.json').exists():
        raise RuntimeError('This annotation version has already been scored; use a new output directory for any revision.')
    mapping=json.loads((out/'mapping.json').read_text())
    annotations=json.loads((out/'annotations.json').read_text())
    assert set(annotations)==set(mapping)
    spec=importlib.util.spec_from_file_location('reference_geometry',PKLNET_ROOT/'roiExtractor.py')
    geometry=importlib.util.module_from_spec(spec);spec.loader.exec_module(geometry)
    old_records=json.loads((benchmark/'heatmap-v3-20261025/records.json').read_text())
    old_pixels=np.load(benchmark/'heatmap-v3-20261025/pixels.npz')['heatmap_runtime']
    heatmaps={r['sample']:p for r,p in zip(old_records,old_pixels)}
    records=[];pixels={k:[] for k in ('fused','heatmap','reference','heatmap_normalized','reference_normalized')};panels=[]
    for key,row in mapping.items():
        path=benchmark/'originals'/row['sample']/'full.jpg'
        assert hashlib.sha256(path.read_bytes()).hexdigest()==row['original_sha256']
        image=Image.open(path).convert('RGB')
        kp=np.asarray(annotations[key],np.float32).reshape(3,2)*np.array([image.width/640,image.height/360])
        quad=np.asarray(geometry.getROIckp(kp[0],kp[1],geometry.isAntiClock(kp.reshape(-1))),np.float32)
        assert (quad>=0).all() and (quad[:,0]<image.width).all() and (quad[:,1]<image.height).all(),key
        raw=geometry.getROIimg(cv2.cvtColor(np.asarray(image),cv2.COLOR_RGB2BGR),quad)
        original=np.asarray(Image.open(benchmark/'rois'/row['sample']/'roi_raw_128.png').convert('L'))
        pixels['fused'].append(original);pixels['reference'].append(raw)
        pixels['heatmap'].append(heatmaps[row['sample']])
        pixels['heatmap_normalized'].append(normalize_roi(heatmaps[row['sample']])[0])
        pixels['reference_normalized'].append(normalize_roi(raw)[0])
        records.append(dict(sample=row['sample'],annotation_id=key,identity=row['subject']+':'+row['hand'],index=int(row['sample_index']),
            fused_valid=row['roi_geometry_valid'],keypoints=kp.tolist(),quad=quad.tolist(),source_sha256=row['original_sha256']))
        draw=ImageDraw.Draw(image);pts=[tuple(p) for p in quad];draw.line(pts+pts[:1],fill='lime',width=6)
        for x,y in kp[:2]:draw.ellipse((x-6,y-6,x+6,y+6),fill='red')
        image.thumbnail((640,360));panel=Image.new('RGB',(800,400),'white');panel.paste(image,(0,30));panel.paste(Image.fromarray(raw),(660,40))
        ImageDraw.Draw(panel).text((5,5),key,fill='black');panels.append(panel)
    for start in range(0,40,4):
        sheet=Image.new('RGB',(1600,800),'white')
        for i,panel in enumerate(panels[start:start+4]):sheet.paste(panel,((i%2)*800,(i//2)*400))
        sheet.save(out/f'review-{start:02}.jpg',quality=96)
    (out/'records.json').write_text(json.dumps(records,indent=2))
    np.savez_compressed(out/'pixels.npz',**{k:np.stack(v) for k,v in pixels.items()})


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=['prepare','render','score'])
    parser.add_argument('benchmark',type=Path);parser.add_argument('output',type=Path);args=parser.parse_args()
    if args.mode=='prepare':prepare(args.benchmark,args.output)
    elif args.mode=='render':render(args.benchmark,args.output)
    else:
        frozen={name:hashlib.sha256((args.output/name).read_bytes()).hexdigest() for name in ('annotations.json','records.json','pixels.npz')}
        if (args.output/'scored-input-hashes.json').exists():
            assert frozen==json.loads((args.output/'scored-input-hashes.json').read_text()),'Scored inputs changed'
        (args.output/'scored-input-hashes.json').write_text(json.dumps(frozen,indent=2))
        classical(args.output);neural(args.output)


if __name__=='__main__':main()
