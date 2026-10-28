"""Test permutation-aware fusion on every frozen sample, without quality filtering."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw

APP=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(APP))
sys.path.insert(0,str(APP/'vendor/palmprint-recognition-python'))
from pklnet_roi import PKLNetROI,PKLNET_ROOT,normalize_roi
from pklnet_policy import align_endpoints_and_fuse
from audit_roi_branches import score,neural
from palmprint.algorithms.registry import get_algorithm


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('benchmark',type=Path)
    p.add_argument('output',type=Path)
    args=p.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    manifest=json.loads((args.benchmark/'extraction_manifest.json').read_text())
    cache={r['sample']:r for r in json.loads((args.benchmark/'torch-diagnosis-all/diagnosis.json').read_text()) if r['variant']=='canonical'}
    spec=importlib.util.spec_from_file_location('geometry',PKLNET_ROOT/'roiExtractor.py')
    geo=importlib.util.module_from_spec(spec);spec.loader.exec_module(geo)
    pixels={k:[] for k in ['original','endpoint_aligned']}
    records=[]
    panels=[]
    for r in manifest:
        path=args.benchmark/'originals'/r['sample']/'full.jpg'
        assert hashlib.sha256(path.read_bytes()).hexdigest()==r['original_sha256']
        image=Image.open(path).convert('RGB')
        _,osize,rsize,scale=PKLNetROI._prepare(image)
        d=cache[r['sample']]
        kp,detail=align_endpoints_and_fuse(d['heatmap_branch_keypoints'],d['fc_branch_keypoints'])
        native=PKLNetROI._unrotate_keypoints(kp,osize,rsize,scale)
        quad=np.asarray(geo.getROIckp(native[:2],native[2:4],geo.isAntiClock(native)),np.float32)
        original=np.asarray(Image.open(args.benchmark/'rois'/r['sample']/'roi_raw_128.png').convert('L'))
        # Preserve exact old pixels on unchanged endpoints; avoid attributing
        # cross-runtime interpolation noise to this one algorithmic change.
        corrected=geo.getROIimg(cv2.cvtColor(np.asarray(image),cv2.COLOR_RGB2BGR),quad) if detail['pklnet_endpoint_swap'] else original.copy()
        for k,v in [('original',original),('endpoint_aligned',corrected)]: pixels[k].append(v)
        in_bounds=bool((quad>=0).all() and (quad[:,0]<image.width).all() and (quad[:,1]<image.height).all())
        span=float(np.linalg.norm(native[:2]-native[2:4])/min(image.size))
        record=dict(sample=r['sample'],identity=r['subject']+':'+r['hand'],index=int(r['sample_index']),
                    fused_valid=r['roi_geometry_valid'],corrected_geometry_valid=in_bounds and span>=.1,
                    keypoints=native.tolist(),quad=quad.tolist(),span_ratio=span,**detail)
        records.append(record)
        if detail['pklnet_endpoint_swap']:
            panel=Image.new('RGB',(900,370),'white');draw=ImageDraw.Draw(panel)
            for col,(label,q,roi) in enumerate([('Original',r['roi_quad_full'],original),('Endpoint correspondence',quad,corrected)]):
                overlay=image.copy();od=ImageDraw.Draw(overlay);pts=[tuple(map(float,x)) for x in q]
                od.line(pts+pts[:1],fill='lime',width=8);overlay.thumbnail((440,248))
                panel.paste(overlay,(col*450+5,24));panel.paste(Image.fromarray(roi).resize((90,90)),(col*450+5,275))
                draw.text((col*450+5,4),f"{record['identity']} #{record['index']} {label}",fill='black')
                draw.text((col*450+110,280),f"side={np.linalg.norm(np.asarray(q)[1]-np.asarray(q)[0]):.1f}px",fill='black')
            panel.save(args.output/(r['sample']+'.jpg'),quality=94);panels.append(panel)
    np.savez_compressed(args.output/'pixels.npz',**{k:np.stack(v) for k,v in pixels.items()})
    (args.output/'records.json').write_text(json.dumps(records,indent=2))
    sheet=Image.new('RGB',(900,len(panels)*370),'white')
    for i,panel in enumerate(panels):sheet.paste(panel,(0,i*370))
    sheet.save(args.output/'changes.jpg',quality=94)
    results=[]
    for name in ('DoN','FastCC'):
        alg=get_algorithm(name);features={}
        for branch,values in pixels.items():
            f=[alg.extract(normalize_roi(v)[0]) for v in values];features[branch]=(f,f)
        results.extend(score(records,features,alg.match,name))
    (args.output/'classical.json').write_text(json.dumps(results,indent=2))
    neural(args.output)
    print(json.dumps({'images':len(records),'corrected':sum(r['pklnet_endpoint_swap'] for r in records),
                      'old_geometry_pass':sum(r['fused_valid'] for r in records),
                      'corrected_geometry_pass':sum(r['corrected_geometry_valid'] for r in records)}))


if __name__=='__main__':main()
