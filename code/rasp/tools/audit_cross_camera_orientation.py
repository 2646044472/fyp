"""Global cross-camera orientation/polarity controls, never per-identity routing."""
import argparse
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image

APP=Path(__file__).resolve().parents[1];sys.path.insert(0,str(APP))
from palm_app.biometric import load_algorithm
from audit_pose_matching import fast_don_match
from audit_matcher_stability import canonical


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('new_replay',type=Path);p.add_argument('old_replay',type=Path);p.add_argument('output',type=Path);args=p.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    rows={};pixels={};features={};algs={n:load_algorithm(APP/'vendor/palmprint-recognition-python',n) for n in ['DoN','FastCC']}
    for cohort,path in [('new',args.new_replay),('old',args.old_replay)]:
        rows[cohort]=json.loads((path/'extraction.json').read_text())
        pixels[cohort]=[np.asarray(Image.open(path/'rois'/r['sample']/'illumination/roi_128.png').convert('L')) for r in rows[cohort]]
        features[cohort]={n:[alg.extract(im) for im in pixels[cohort]] for n,alg in algs.items()}
    plan=dict(transforms='four right-angle rotations, optional horizontal reflection, optional intensity inversion; one fixed transform for whole query cohort',
              galleries='other-camera indices1-5; query indices6-10; all20 retained',
              purpose='diagnose globally inconsistent ROI convention; no best-per-person or best-per-query transformation')
    (args.output/'plan.json').write_text(json.dumps(plan,indent=2));results=[]
    for enroll,query in [('old','new'),('new','old')]:
        identities=sorted({canonical(r['identity']) for r in rows[enroll]});gallery={k:[i for i,r in enumerate(rows[enroll]) if canonical(r['identity'])==k and r['index']<=5] for k in identities}
        for rotation in range(4):
            for mirror in [False,True]:
                for inverse in [False,True]:
                    for name,alg in algs.items():
                        trials=[]
                        for i,r in enumerate(rows[query]):
                            if r['index']<=5:continue
                            im=np.rot90(pixels[query][i],rotation)
                            if mirror:im=np.fliplr(im)
                            if inverse:im=255-im
                            f=alg.extract(np.ascontiguousarray(im));match=fast_don_match if name=='DoN' else alg.match
                            scores={k:float(np.median([match(f,features[enroll][name][j]) for j in ids])) for k,ids in gallery.items()}
                            expected=canonical(r['identity']);trials.append(dict(sample=r['sample'],identity=expected,correct=scores[expected]<min(v for k,v in scores.items() if k!=expected),scores=scores))
                        result=dict(direction=enroll+'_to_'+query,algorithm=name,rotation=rotation*90,mirror=mirror,inverse=inverse,correct=sum(x['correct'] for x in trials),total=len(trials),trials=trials);results.append(result)
                    print(enroll,query,rotation,mirror,inverse,[(x['algorithm'],x['correct']) for x in results[-2:]],flush=True)
                    (args.output/'results.json').write_text(json.dumps(results,indent=2))


if __name__=='__main__':main()
