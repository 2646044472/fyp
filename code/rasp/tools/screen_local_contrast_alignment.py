"""Fixed local-contrast or pretrained-feature pilot on v24 development fallbacks.

Offline descriptor reuse only; not an end-to-end speed benchmark. Labels are
used after matching to evaluate predictions, never to construct a transform.
No runtime matcher or production setting is changed by this screen.
"""
import argparse
from collections import Counter
import hashlib,json,sys,time
from pathlib import Path
import cv2
import numpy as np

APP=Path(__file__).resolve().parents[1];sys.path.insert(0,str(APP))
from biometric import load_algorithm
from registered_matcher import local_features,registration
from affine_enrollment_matcher import affine_registration
from registration_accelerated import estimate_pairs
from linked_enrollment_matcher import composed_transform
from pklnet_roi import normalize_roi_pixels


def contrast_views(native,source,wide):
    offset=192 if wide else 0
    size=768 if wide else 384
    shift=np.asarray([[1.,0,offset],[0,1.,offset],[0,0,1.]])
    pixels=normalize_roi_pixels(cv2.warpPerspective(native,shift@source,(size,size)))
    # Fixed conventional parameters, not chosen using observed recognition.
    pixels=cv2.createCLAHE(clipLimit=2.,tileGridSize=(8,8)).apply(pixels)
    result=[]
    for sigma in (0,2):
        p,d=local_features(cv2.GaussianBlur(pixels,(0,0),sigma) if sigma else pixels)
        result.append((p-offset,d))
    return result


def score_transform(algorithm,native,source,transform,bank):
    corners=np.asarray([[0.,0,1],[128,0,1],[128,128,1],[0,128,1]])
    warp=np.diag([1/3,1/3,1])@transform@source
    mapped=corners@np.linalg.inv(warp).T;mapped=mapped[:,:2]/mapped[:,2:]
    if (not np.isfinite(mapped).all() or (mapped<1).any()
        or (mapped[:,0]>=native.shape[1]-1).any() or (mapped[:,1]>=native.shape[0]-1).any()
        or not algorithm._accept_alignment((None,None,source),mapped)):return None
    try:pixels=normalize_roi_pixels(cv2.warpPerspective(native,warp,(128,128)))
    except ValueError:return None
    return float(algorithm.base.match(algorithm.base.extract(pixels),bank))


def transfer_scores(algorithm,native,source,enrolled,banks,direct,distances,links):
    updated=dict(zip(enrolled,distances));counts=Counter()
    for sample in enrolled:
        for target,link in links.get(sample,[]):
            if target not in updated:continue
            for transform in direct[sample]:
                composed=composed_transform(link,transform)
                if composed is None:counts['link_geometry_rejected']+=1;continue
                score=score_transform(algorithm,native,source,composed,banks[target])
                if score is None:counts['link_sampling_rejected']+=1;continue
                counts['link_scored']+=1;updated[target]=min(updated[target],score)
    return [updated[s] for s in enrolled],counts


def aligned_scores(algorithm,native,source,query,target,bank,pair_finder=None,transforms=None):
    best=1.;counts=Counter()
    for a,b in zip(query,target):
        if pair_finder is None:estimators=(('similarity',registration),('affine',affine_registration))
        else:
            pairs=pair_finder(a[1],b[1])
            estimators=(('similarity',lambda a,b:estimate_pairs(a[0],b[0],pairs)),
                ('affine',lambda a,b:affine_registration(a,b,lambda a,b:pairs)))
        for model,estimate in estimators:
            transform=estimate(a,b)
            if transform is None:counts[model+'_no_transform']+=1;continue
            score=score_transform(algorithm,native,source,transform,bank)
            if score is None:counts[model+'_sampling_guard']+=1;continue
            if transforms is not None:transforms.append(transform)
            best=min(best,score)
            counts[model+'_scored']+=1
    return best,counts


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('root',type=Path);p.add_argument('baseline',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--xfeat-root',type=Path,help='Alternative frozen XFeat proposal pilot; no CLAHE')
    p.add_argument('--enrollment-links',action='store_true',help='Transfer direct alignments through unchanged within-enrollment similarity links')
    args=p.parse_args();args.output.mkdir(exist_ok=False,parents=True)
    cases=json.loads(args.baseline.read_text(encoding='utf-8'))
    trials=[(c,t) for c in cases for t in c['trials'] if t['route']=='exhaustive_fallback']
    protocol=dict(method='CLAHE clip2 tiles8; SIFT raw/sigma2; query768 center/enrollment384; original-pixel FastCC best2',
        gates='unchanged similarity/affine geometry and .32/.08 early confidence',
        scope='All development fallback trials, inserted only after every existing v24 early stage fails',
        fallback_trials=len(trials),total_trials=sum(len(c['trials']) for c in cases),independent_validation=False,
        runtime_query_cache=False,timing_warning='Offline feature/pair reuse; timings are not live recognition latency',
        baseline_sha256=hashlib.sha256(args.baseline.read_bytes()).hexdigest(),
        tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    protocol['enrollment_links']=args.enrollment_links
    extractor=contrast_views;pair_finder=None
    if args.xfeat_root:
        from xfeat_alignment_pilot import XFeatProposal,xfeat_pairs
        extractor=XFeatProposal(args.xfeat_root)
        pair_finder=xfeat_pairs
        protocol.update(method='Pretrained XFeat sparse top1000 threshold.05; query768 center/enrollment384; original-pixel FastCC best2',
            correspondences='Upstream MNN with default cosine>.82; original geometric and final confidence guards',
            model_metadata=json.loads((args.xfeat_root/'metadata.json').read_text(encoding='utf-8')))
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2),encoding='utf-8')
    cv2.setNumThreads(1)
    algorithm=load_algorithm(APP/'vendor/palmprint-recognition-python','FastCCQualityEvidence-v24-experimental')
    features={};gallery={};probes={};pairs={};direct={};link_cache={};counts=Counter();records=[];started=time.perf_counter()
    def unpack(sample):
        if sample not in features:
            with np.load(args.root/(sample+'.npz'),allow_pickle=False) as z:f=z['feature']
            f[:4]=np.asarray([algorithm.magic],'<i4').view(np.uint8)
            features[sample]=algorithm._unpack(f)
        return features[sample]
    try:
        for case,trial in trials:
            sample=trial['sample'];q=unpack(sample)
            if sample not in probes:probes[sample]=extractor(q[3],q[1][2],True)
            scores={}
            for identity,enrolled in case['gallery'].items():
                distances=[]
                for target in enrolled:
                    if target not in gallery:
                        t=unpack(target);gallery[target]=extractor(t[3],t[1][2],False)
                    key=sample,target
                    if key not in pairs:
                        t=unpack(target)
                        direct[key]=[]
                        pairs[key],trace=aligned_scores(algorithm,q[3],q[1][2],probes[sample],gallery[target],t[1][0][0].astype(bool),pair_finder,direct[key])
                        counts.update(trace)
                    distances.append(pairs[key])
                if args.enrollment_links:
                    links={s:[] for s in enrolled}
                    for a in enrolled:
                        for b in enrolled:
                            if a==b:continue
                            if (a,b) not in link_cache:
                                left,right=unpack(a),unpack(b);link_cache[a,b]=[]
                                for x,y in (((left[1][4],left[1][5]),(right[1][4],right[1][5])),(left[2],right[2])):
                                    matrix=registration(x,y)
                                    if matrix is not None:link_cache[a,b].append(matrix)
                            links[a].extend((b,m) for m in link_cache[a,b])
                    distances,trace=transfer_scores(algorithm,q[3],q[1][2],enrolled,
                        {t:unpack(t)[1][0][0].astype(bool) for t in enrolled},
                        {t:direct[sample,t] for t in enrolled},distances,links)
                    counts.update(trace)
                scores[identity]=float(np.mean(sorted(distances)[:2]))
            predicted=min(scores,key=scores.get);confident=algorithm.confident(scores)
            records.append(dict(case=case['case'],sample=sample,identity=trial['identity'],scores=scores,
                predicted=predicted,correct=predicted==trial['identity'],confident=confident))
            result=dict(protocol=protocol,records=records,unique_pairs=len(pairs),counts=dict(counts),
                rescued=sum(r['confident'] and r['correct'] for r in records),
                wrong_confident=sum(r['confident'] and not r['correct'] for r in records),
                elapsed_offline_seconds=time.perf_counter()-started,complete=len(records)==len(trials))
            (args.output/'results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
            print(case['case'],sample,'confident',confident,'correct',records[-1]['correct'],flush=True)
    finally:algorithm.close()
    print(json.dumps({k:v for k,v in result.items() if k not in ('records','protocol')}),flush=True)


if __name__=='__main__':main()
