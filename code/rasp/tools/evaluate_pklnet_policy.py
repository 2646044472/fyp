"""Replay the consensus guard, showing rejected probes against the full denominator."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
import time

import numpy as np
from PIL import Image

APP=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(APP))
sys.path.insert(0,str(APP/'vendor/palmprint-recognition-python'))
from pklnet_roi import PKLNetROI, normalize_roi
from pklnet_policy import require_matchable_quality
from palmprint.algorithms.registry import get_algorithm


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('benchmark',type=Path)
    p.add_argument('output',type=Path)
    args=p.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    manifest=json.loads((args.benchmark/'extraction_manifest.json').read_text())
    diagnostic=json.loads((args.benchmark/'torch-diagnosis-all/diagnosis.json').read_text())
    diagnostic={r['sample']:r for r in diagnostic if r['variant']=='canonical'}
    extractor=PKLNetROI(threads=2,policy="consensus")
    records=[]
    pixels=[]
    for row in manifest:
        path=args.benchmark/'originals'/row['sample']/'full.jpg'
        assert hashlib.sha256(path.read_bytes()).hexdigest()==row['original_sha256']
        image=Image.open(path).convert('RGB')
        t=time.perf_counter()
        raw,quad,detail=extractor.extract(image)
        elapsed=(time.perf_counter()-t)*1000
        frozen=np.asarray(Image.open(args.benchmark/'rois'/row['sample']/'roi_raw_128.png').convert('L'))
        normalized,quality=normalize_roi(frozen)
        pixels.append(normalized)
        quality_reason=None
        try: require_matchable_quality(quality)
        except ValueError as e: quality_reason=str(e)
        old_kp=np.asarray(row['pklnet_keypoints'])
        fused_error=float(np.abs(np.asarray(detail['pklnet_keypoints'])-old_kp).max())
        # Verify exposed graph branches against independently captured PyTorch
        # branch predictions. No labels enter either export or guard decisions.
        _,osize,rsize,scale=extractor._prepare(image)
        errors=[]
        for branch,key in [('heatmap','heatmap_branch_keypoints'),('fc','fc_branch_keypoints')]:
            if f'pklnet_{branch}_keypoints' in detail:
                expected=extractor._unrotate_keypoints(np.asarray(diagnostic[row['sample']][key]),osize,rsize,scale)
                errors.append(float(np.abs(expected-detail[f'pklnet_{branch}_keypoints']).max()))
        assert fused_error<.05 and max(errors,default=0)<.05
        records.append(dict(sample=row['sample'],identity=row['subject']+':'+row['hand'],index=int(row['sample_index']),
                            legacy_geometry=row['roi_geometry_valid'],consensus=detail['roi_geometry_valid'],
                            full_quality=detail['roi_geometry_valid'] and quality_reason is None,
                            quality=quality,quality_reason=quality_reason,diagnostics=detail,
                            fused_keypoint_error_px=fused_error,branch_error_px=max(errors,default=0),
                            frozen_pixel_max_error=int(np.abs(frozen.astype(int)-raw.astype(int)).max()),ms=elapsed))
        print(f"IMAGE {len(records)}/{len(manifest)} accepted={detail['roi_geometry_valid']} {detail['roi_geometry_reason']}",flush=True)
    identities=sorted({r['identity'] for r in records})
    coverages=[]
    for stage in ('legacy_geometry','consensus','full_quality'):
        gallery={k:[i for i,r in enumerate(records) if r['index']<=5 and r[stage] and r['identity']==k] for k in identities}
        probes=[i for i,r in enumerate(records) if r['index']>5 and r[stage]]
        coverages.append(dict(stage=stage,images_kept=sum(r[stage] for r in records),images_total=len(records),
                              gallery_sizes={k:len(v) for k,v in gallery.items()},probe_kept=len(probes),probe_total=20,
                              missing_gallery=[k for k,v in gallery.items() if not v]))
    results=[]
    for algorithm_name in ('DoN','FastCC'):
        algorithm=get_algorithm(algorithm_name)
        features=[algorithm.extract(im) for im in pixels]
        distances={(i,j):float(algorithm.match(features[i],features[j]))
                   for i,r in enumerate(records) if r['index']>5 for j,g in enumerate(records) if g['index']<=5}
        for stage in ('legacy_geometry','consensus','full_quality'):
            gallery={k:[i for i,r in enumerate(records) if r['index']<=5 and r[stage] and r['identity']==k] for k in identities}
            probes=[i for i,r in enumerate(records) if r['index']>5 and r[stage]]
            trials=[]
            if all(gallery.values()):
                for i in probes:
                    scores={k:float(np.median([distances[i,j] for j in js])) for k,js in gallery.items()}
                    own=scores[records[i]['identity']]
                    other=min(v for k,v in scores.items() if k!=records[i]['identity'])
                    trials.append(dict(sample=records[i]['sample'],correct=own<other,own=own,other=other))
            result=dict(algorithm=algorithm_name,stage=stage,status='ok' if all(gallery.values()) else 'insufficient_valid_enrollment',
                        correct=sum(t['correct'] for t in trials),scored=len(trials),total_original_probes=20,
                        rejected_probes=20-len(probes),missing_gallery=[k for k,v in gallery.items() if not v],trials=trials)
            print(json.dumps({k:v for k,v in result.items() if k!='trials'}),flush=True)
            results.append(result)
    summary=dict(records=records,coverage=coverages,recognition=results,
                 geometry_reasons=dict(Counter(r['diagnostics']['roi_geometry_reason'] or 'accepted' for r in records)),
                 max_fused_keypoint_error_px=max(r['fused_keypoint_error_px'] for r in records),
                 max_branch_error_px=max(r['branch_error_px'] for r in records),
                 max_frozen_pixel_error=max(r['frozen_pixel_max_error'] for r in records),
                 limitation='Diagnostic reuse of two-person dataset. Guard thresholds are engineering tolerances, not fitted to identity labels. Rejections are reported against all 20 original probes. Classification uses exact frozen pixels to isolate the guard effect. No recognition threshold is calibrated.')
    (args.output/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(coverages),flush=True)


if __name__=='__main__': main()
