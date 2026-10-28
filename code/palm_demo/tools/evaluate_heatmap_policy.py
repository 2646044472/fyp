"""Replay the runtime ROI on all originals, including every probe in the audit."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

import numpy as np
from PIL import Image, ImageDraw

APP=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(APP))
sys.path.insert(0,str(APP/'vendor/palmprint-recognition-python'))
from pklnet_roi import PKLNetROI, normalize_roi
from audit_roi_branches import score, neural
from palmprint.algorithms.registry import get_algorithm


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('benchmark',type=Path)
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    extractor=PKLNetROI(threads=2, policy="heatmap")
    manifest=json.loads((args.benchmark/'extraction_manifest.json').read_text())
    cached={r['sample']:r for r in json.loads((args.benchmark/'torch-diagnosis-all/diagnosis.json').read_text()) if r['variant']=='canonical'}
    records=[];pixels={'original':[],'heatmap_runtime':[]};panels=[]
    for row in manifest:
        path=args.benchmark/'originals'/row['sample']/'full.jpg'
        assert hashlib.sha256(path.read_bytes()).hexdigest()==row['original_sha256']
        image=Image.open(path).convert('RGB')
        started=time.perf_counter();raw,quad,details=extractor.extract(image)
        elapsed=(time.perf_counter()-started)*1000
        _,osize,rsize,scale=extractor._prepare(image)
        expected=extractor._unrotate_keypoints(np.asarray(cached[row['sample']]['heatmap_branch_keypoints']),osize,rsize,scale)
        error=float(np.max(np.abs(expected-details['pklnet_keypoints'])))
        assert error<.05
        old=np.asarray(Image.open(args.benchmark/'rois'/row['sample']/'roi_raw_128.png').convert('L'))
        pixels['original'].append(old);pixels['heatmap_runtime'].append(raw)
        records.append(dict(sample=row['sample'],identity=row['subject']+':'+row['hand'],index=int(row['sample_index']),
            fused_valid=row['roi_geometry_valid'],runtime_valid=details['roi_geometry_valid'],diagnostics=details,
            keypoint_parity_max_px=error,ms=elapsed))
        panel=Image.new('RGB',(900,350),'white');draw=ImageDraw.Draw(panel)
        for col,(label,q,crop) in enumerate([('Original fused',row['roi_quad_full'],old),('Heatmap runtime',quad,raw)]):
            view=image.copy();vd=ImageDraw.Draw(view);pts=[tuple(map(float,p)) for p in q]
            vd.line(pts+pts[:1],fill='lime',width=8);view.thumbnail((440,248));panel.paste(view,(col*450,20))
            panel.paste(Image.fromarray(crop).resize((80,80)),(col*450,268))
            draw.text((col*450+5,3),f"{records[-1]['identity']} #{row['sample_index']} {label}",fill='black')
            draw.text((col*450+90,278),f"side={np.linalg.norm(np.asarray(q)[1]-q[0]):.1f}px",fill='black')
        panels.append(panel)
        print(f"IMAGE {len(records)}/40 geometry={details['roi_geometry_valid']}",flush=True)
    (args.output/'records.json').write_text(json.dumps(records,indent=2))
    np.savez_compressed(args.output/'pixels.npz',**{k:np.stack(v) for k,v in pixels.items()})
    for start in range(0,len(panels),10):
        sheet=Image.new('RGB',(900,3500),'white')
        for i,panel in enumerate(panels[start:start+10]):sheet.paste(panel,(0,i*350))
        sheet.save(args.output/f'comparison-{start}.jpg',quality=93)
    results=[];live=[]
    for name in ('DoN','FastCC'):
        alg=get_algorithm(name);features={}
        for branch,values in pixels.items():
            f=[alg.extract(normalize_roi(v)[0]) for v in values];features[branch]=(f,f)
        results.extend(score(records,features,alg.match,name))
        # Report the real geometry guard separately, with failures in denominator.
        f=features['heatmap_runtime'][0];identities=sorted({r['identity'] for r in records})
        gallery={k:[i for i,r in enumerate(records) if r['index']<=5 and r['identity']==k and r['runtime_valid']] for k in identities}
        trials=[]
        for i,r in enumerate(records):
            if r['index']<=5:continue
            scores={k:float(np.median([alg.match(f[i],f[j]) for j in js])) for k,js in gallery.items()} if r['runtime_valid'] and all(gallery.values()) else {}
            correct=bool(scores) and scores[r['identity']]<min(v for k,v in scores.items() if k!=r['identity'])
            trials.append(dict(sample=r['sample'],correct=correct,geometry_valid=r['runtime_valid'],scores=scores))
        live.append(dict(algorithm=name,correct=sum(t['correct'] for t in trials),total=20,
            geometry_rejected_probes=sum(not t['geometry_valid'] for t in trials),gallery_sizes={k:len(v) for k,v in gallery.items()},trials=trials))
    (args.output/'classical.json').write_text(json.dumps(results,indent=2))
    (args.output/'runtime-guard.json').write_text(json.dumps(live,indent=2))
    neural(args.output)
    print(json.dumps(dict(images=len(records),geometry_pass=sum(r['runtime_valid'] for r in records),
        max_parity_px=max(r['keypoint_parity_max_px'] for r in records))),flush=True)


if __name__=='__main__':main()
