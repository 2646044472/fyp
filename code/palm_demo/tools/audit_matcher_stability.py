"""Enrollment-choice and cross-camera stability, with all saved samples retained.

The identities and repeated captures are small, previously inspected development
data. Repeated splits are sensitivity checks, never independent accuracy trials.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

import numpy as np
from PIL import Image

APP=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(APP))
from palm_app.biometric import load_algorithm
from audit_pose_matching import fast_don_match


def save(path,value):path.write_text(json.dumps(value,indent=2),encoding='utf-8')


def canonical(identity):
    subject,hand=identity.split(':')
    if subject in ('bankey','bankey-10-12'):return 'bankey:'+hand
    if subject in ('stephen','stephen-10-13'):return 'stephen:'+hand
    raise ValueError('Unknown cross-session identity mapping: '+identity)


def evaluate(records,matrices,case,gallery,queries):
    results=[]
    for algorithm,matrix in matrices.items():
        trials=[]
        for i in queries:
            assert all(i not in ids for ids in gallery.values()),'Query leaked into enrollment'
            scores={k:float(np.min(matrix[i,ids]) if algorithm=='FastCCPoseNearest-v1' else np.median(matrix[i,ids])) for k,ids in gallery.items()}
            expected=records[i]['canonical_identity'];ranking=sorted(scores,key=scores.get)
            own=scores[expected];other=min(v for k,v in scores.items() if k!=expected)
            trials.append(dict(sample=records[i]['sample'],identity=expected,predicted=ranking[0],correct=own<other,
                               own_score=own,nearest_impostor=other,margin=other-own,scores=scores))
        results.append(dict(case=case,algorithm=algorithm,correct=sum(t['correct'] for t in trials),total=len(trials),
            gallery={k:[records[i]['sample'] for i in ids] for k,ids in gallery.items()},
            per_identity={k:dict(correct=sum(t['correct'] for t in trials if t['identity']==k),total=sum(t['identity']==k for t in trials)) for k in gallery},trials=trials))
    return results


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('new_replay',type=Path);p.add_argument('old_replay',type=Path);p.add_argument('output',type=Path);args=p.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    save(args.output/'plan.json',dict(algorithms=['DoN_median','FastCC_median','FastCCPoseNearest-v1'],
        enrollment='five per identity; original1-5 split, reversed6-10 split, ten seeded random5-of10 splits',
        seeds=list(range(2026102800,2026102810)),
        cross_camera='old1-5 enroll/new6-10 query; reverse; all40 queries from distinct camera also reported',
        controls='all samples retained; no self-match; known subject aliases explicit; source hashes checked',
        limitation='Sensitivity tests on two known people, not independent trials, open-set validation or real-world reliability'))
    records=[];pixels=[];features=[];repeat=[]
    matcher=load_algorithm(APP/'vendor/palmprint-recognition-python','FastCCPoseNearest-v1')
    for cohort,replay in [('new',args.new_replay),('old',args.old_replay)]:
        for n,r in enumerate(json.loads((replay/'extraction.json').read_text())):
            path=Path(r['original']);assert hashlib.sha256(path.read_bytes()).hexdigest()==r['sha256']
            image=Image.open(path).convert('RGB');roi=np.asarray(Image.open(replay/'rois'/r['sample']/'illumination/roi_128.png').convert('L'))
            q=np.asarray(r['illumination']['details']['roi_quad_full'],np.float32)
            bank=matcher.extract_with_context(image,q,roi)
            if n in [0,9,19,29,39]:repeat.append(dict(cohort=cohort,sample=r['sample'],identical=bool(np.array_equal(bank,matcher.extract_with_context(image,q,roi)))))
            features.append(bank);pixels.append(roi);records.append({**r,'cohort':cohort,'canonical_identity':canonical(r['identity'])})
    assert all(r['identical'] for r in repeat)
    save(args.output/'repeatability.json',repeat);save(args.output/'records.json',records)
    np.savez_compressed(args.output/'features.npz',pose=np.stack(features))
    don=load_algorithm(APP/'vendor/palmprint-recognition-python','DoN');don_features=[don.extract(p) for p in pixels]
    matrices={name:np.empty((len(records),len(records)),np.float64) for name in ['DoN_median','FastCC_median','FastCCPoseNearest-v1']}
    started=time.perf_counter()
    for i,left in enumerate(features):
        for j,right in enumerate(features):
            matrices['DoN_median'][i,j]=fast_don_match(don_features[i],don_features[j])
            matrices['FastCC_median'][i,j]=matcher.base.match(left[0].astype(bool),right[0].astype(bool))
            matrices['FastCCPoseNearest-v1'][i,j]=matcher.match(left,right)
        if (i+1)%10==0:print(f'DISTANCES {i+1}/{len(records)} elapsed={time.perf_counter()-started:.1f}s',flush=True)
    np.savez_compressed(args.output/'distances.npz',**matrices)
    identities=sorted({r['canonical_identity'] for r in records});results=[]
    for cohort in ['new','old']:
        groups={k:[i for i,r in enumerate(records) if r['cohort']==cohort and r['canonical_identity']==k] for k in identities}
        for reverse in [False,True]:
            gallery={k:[i for i in ids if (records[i]['index']<=5)!=reverse] for k,ids in groups.items()}
            queries=[i for ids in groups.values() for i in ids if (records[i]['index']>5)!=reverse]
            results+=evaluate(records,matrices,cohort+('_reverse' if reverse else '_original'),gallery,queries)
        for seed in range(2026102800,2026102810):
            rng=np.random.default_rng(seed);gallery={k:sorted(map(int,rng.choice(ids,5,replace=False))) for k,ids in groups.items()}
            queries=[i for k,ids in groups.items() for i in ids if i not in gallery[k]]
            results+=evaluate(records,matrices,f'{cohort}_random_{seed}',gallery,queries)
    for enroll,query in [('old','new'),('new','old')]:
        gallery={k:[i for i,r in enumerate(records) if r['cohort']==enroll and r['canonical_identity']==k and r['index']<=5] for k in identities}
        for subset in ['last5','all10']:
            queries=[i for i,r in enumerate(records) if r['cohort']==query and (subset=='all10' or r['index']>5)]
            results+=evaluate(records,matrices,f'{enroll}_to_{query}_{subset}',gallery,queries)
    save(args.output/'results.json',results)
    summary=[]
    for cohort in ['new','old']:
        for algorithm in matrices:
            trials=[r for r in results if r['algorithm']==algorithm and r['case'].startswith(cohort+'_random_')]
            summary.append(dict(cohort=cohort,algorithm=algorithm,random_splits=len(trials),
                min_correct=min(r['correct'] for r in trials),max_correct=max(r['correct'] for r in trials),
                mean_correct=float(np.mean([r['correct'] for r in trials])),queries_per_split=20,
                warning='Same40 development images reused across splits; totals must not be treated as200 independent observations'))
    save(args.output/'summary.json',dict(enrollment_sensitivity=summary,
        fixed_cases=[{k:v for k,v in r.items() if k not in ['trials','gallery']} for r in results if '_random_' not in r['case']],
        originals_unchanged=all(hashlib.sha256(Path(r['original']).read_bytes()).hexdigest()==r['sha256'] for r in records)))
    print(json.dumps(summary),flush=True)


if __name__=='__main__':main()
