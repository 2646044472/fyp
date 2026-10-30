"""Score-independent development-only quarter-turn localization observation.

Four predeclared development images; no matcher, identity-score ROI selection,
candidate adoption or accuracy claim. The full baseline is left untouched.
"""
import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import psutil
from PIL import Image, ImageDraw, ImageOps

APP=Path(__file__).resolve().parents[1];sys.path.insert(0,str(APP))
from pklnet_roi import PKLNetROI

SAMPLES=['smpd-001-F-00','smpd-001-RP-30','smpd-002-F-00','smpd-002-RF-10']


def rotation_matrix(width,height,turns):
    return np.asarray(([[1,0,0],[0,1,0],[0,0,1]],
        [[0,1,0],[-1,0,width-1],[0,0,1]],
        [[-1,0,width-1],[0,-1,height-1],[0,0,1]],
        [[0,-1,height-1],[1,0,0],[0,0,1]])[turns],np.float64)


def restore_quad(quad,width,height,turns):
    homogeneous=np.c_[np.asarray(quad,np.float64),np.ones(4)]
    return (homogeneous@np.linalg.inv(rotation_matrix(width,height,turns)).T)[:,:2].astype(np.float32)


def iou(left,right):
    a,b=np.asarray(left,np.float32),np.asarray(right,np.float32)
    area=max(0.,float(cv2.intersectConvexConvex(a,b)[0]))
    return area/max(1e-12,cv2.contourArea(a)+cv2.contourArea(b)-area)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path)
    p.add_argument('--samples',nargs='+',default=SAMPLES)
    p.add_argument('--output-name',default='development-rotation-observation');a=p.parse_args()
    rows=json.loads((a.root/'prepared/manifest.json').read_text())
    split=json.loads((APP/'docs/protocols/SMPD_PROSPECTIVE_OPTIMIZATION_SPLIT_20261030.json').read_text())
    selected=[next(r for r in rows if r['sample']==s) for s in a.samples]
    assert all(r['subject'] in split['development_subjects'] for r in selected)
    assert Path(a.output_name).name==a.output_name
    out=a.root/a.output_name;out.mkdir(exist_ok=False)
    count=lambda:len(json.loads((a.root/'evaluation/results.json').read_text())['queries'])
    concurrency=dict(start_unix=time.time(),queries_completed_before=count(),output=a.output_name,
        scope='Development-image localization observations, low-priority CPU process, no matching. Windows baseline timings in overlapping query interval may include contention; no queries removed.')
    concurrency_path=a.root/'localization-diagnostic-concurrency.json'
    history=json.loads(concurrency_path.read_text()) if concurrency_path.exists() else []
    if isinstance(history,dict):history=[history]
    history.append(concurrency)
    concurrency_path.write_text(json.dumps(history,indent=2),encoding='utf-8')
    if os.name=='nt':psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS)
    cv2.setNumThreads(1);engine=PKLNetROI(threads=1)
    report=dict(complete=False,selection=a.samples,selection_rule='Explicit development-only image selection, fixed before the quarter-turn predictions; no identity-score selection.',
        policy='Run all four exact quarter turns uniformly, map predictions back, record all overlaps. No winner selection, score, threshold fit or deployment.',
        evaluator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        model_sha256=hashlib.sha256((engine.root/'pklnet-keypoints-diagnostics.onnx').read_bytes()).hexdigest(),records=[])
    canvas=Image.new('RGB',(1440,300*len(selected)),(20,25,34))
    for row_index,r in enumerate(selected):
        with Image.open(r['original']) as encoded: original=ImageOps.exif_transpose(encoded).convert('RGB')
        assert hashlib.sha256(Path(r['original']).read_bytes()).hexdigest()==r['sha256']
        records=[]
        for turns in range(4):
            tick=time.perf_counter();image=Image.fromarray(np.rot90(np.asarray(original),turns).copy())
            try:
                _,quad,details=engine.extract(image)
                mapped=restore_quad(quad,original.width,original.height,turns)
                record=dict(turns=turns,valid=bool(details['roi_geometry_valid']),quad=mapped.tolist(),
                    reason=details.get('roi_geometry_reason'),span=details.get('pklnet_keypoint_span_ratio'))
                preview=original.copy();scale=min(350/original.width,260/original.height);preview.thumbnail((350,260))
                points=[(float(x)*scale,float(y)*scale) for x,y in mapped];draw=ImageDraw.Draw(preview)
                draw.line(points+[points[0]],fill=(80,230,100) if record['valid'] else (255,60,60),width=3)
                canvas.paste(preview,(turns*360,row_index*300))
            except (ValueError,RuntimeError,OSError) as error:
                record=dict(turns=turns,valid=False,error=type(error).__name__+': '+str(error))
            record['diagnostic_ms']=(time.perf_counter()-tick)*1000;records.append(record)
            draw=ImageDraw.Draw(canvas);draw.text((turns*360+4,row_index*300+265),f'{r["sample"]} rot={turns*90} valid={record["valid"]}',fill='white')
        overlaps=[[iou(x['quad'],y['quad']) if 'quad' in x and 'quad' in y else None for y in records] for x in records]
        report['records'].append(dict(sample=r['sample'],observations=records,iou_matrix=overlaps))
        (out/'results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        print(r['sample'],[r['valid'] for r in records],flush=True)
    canvas.save(out/'mapped-quarter-turns.jpg',quality=90)
    report['complete']=True;(out/'results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    concurrency.update(end_unix=time.time(),queries_completed_after=count(),
        potentially_overlapping_query_indices=[concurrency['queries_completed_before']+1,count()+1])
    concurrency_path.write_text(json.dumps(history,indent=2),encoding='utf-8')


if __name__=='__main__':main()
