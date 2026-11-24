"""Supplemental frozen FastCC test on pre-cropped ROI images, not v13 end-to-end.

Use numeric filename IDs 1..20, independently within each F/S prefix. These
prefixes are not assumed to establish sessions or devices without metadata.
First five numbered images enroll; every remaining image queries. No tuning.
"""
import argparse
from collections import defaultdict
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import time
import zipfile
import cv2
import numpy as np
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from biometric import load_algorithm
from fastcc_accelerated import AcceleratedFastCC
from pklnet_roi import normalize_roi_pixels


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('archive',type=Path)
    p.add_argument('output',type=Path)
    args=p.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    protocol=dict(archive_sha256=hashlib.sha256(args.archive.read_bytes()).hexdigest(),
        selection='All filenames with numeric ID 1..20, independently per F/S prefix',
        enrollment='lowest five sample indices',query='all remaining indices',
        scoring='unchanged normalized 128x128 FastCC; mean of best two enrollment distances',
        localizer_used=False,affine_rescue_used=False,parameters_tuned=False,
        limitation='Cropped ROI feature-only test on Windows; not v13 full pipeline or Pi speed; prefixes are filename cohorts, not verified sessions')
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2))
    cv2.setNumThreads(1)
    algorithm=AcceleratedFastCC(load_algorithm(Path(__file__).resolve().parents[1]/'vendor/palmprint-recognition-python','FastCC'))
    groups=defaultdict(list);failures=[]
    with zipfile.ZipFile(args.archive) as z:
        for name in sorted(z.namelist()):
            m=re.fullmatch(r'P_([FS])_(\d+)_(\d+)\.bmp',Path(name).name)
            if not m or not 1<=int(m[2])<=20:continue
            record=dict(member=name,prefix=m[1],identity=int(m[2]),index=int(m[3]))
            try:
                data=z.read(name);record['sha256']=hashlib.sha256(data).hexdigest()
                pixels=np.asarray(Image.open(io.BytesIO(data)).convert('L'))
                if pixels.shape!=(128,128):raise ValueError('Expected supplied 128x128 ROI; no inferred crop')
                record['feature']=algorithm.extract(normalize_roi_pixels(pixels))
            except Exception as error:
                record['error']=str(error);failures.append({k:v for k,v in record.items() if k!='feature'})
            groups[m[1],int(m[2])].append(record)
    results=[]
    for prefix in ('F','S'):
        cohort={identity:sorted(rows,key=lambda r:r['index']) for (p,identity),rows in groups.items() if p==prefix}
        assert set(cohort)==set(range(1,21))
        assert all(len(v)>5 for v in cohort.values())
        gallery={u:[r['feature'] for r in rows[:5] if 'feature' in r] for u,rows in cohort.items()}
        trials=[]
        for identity,rows in sorted(cohort.items()):
            for row in rows[5:]:
                start=time.perf_counter();scores={}
                if 'feature' in row:
                    for user,features in gallery.items():
                        scores[user]=float(np.mean(sorted(algorithm.match(row['feature'],f) for f in features)[:2])) if len(features)==5 else 1.
                ranking=sorted(scores,key=scores.get)
                correct=bool(ranking and ranking[0]==identity and scores[ranking[0]]<scores[ranking[1]])
                trials.append(dict(member=row['member'],identity=identity,correct=correct,
                    prediction=ranking[0] if ranking else None,scores=scores,desktop_match_ms=1000*(time.perf_counter()-start)))
        results.append(dict(prefix=prefix,identities=len(cohort),images=sum(map(len,cohort.values())),
                            total=len(trials),correct=sum(t['correct'] for t in trials),trials=trials))
        print(prefix,results[-1]['correct'],'/',len(trials),flush=True)
    (args.output/'results.json').write_text(json.dumps(dict(protocol=protocol,failures=failures,cohorts=results),indent=2))


if __name__=='__main__':main()
