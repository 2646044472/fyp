"""Frozen three-axis pilot on every development v24 fallback trial; no Pi timing."""
import argparse,hashlib,json,sys,time
from pathlib import Path
import cv2,numpy as np
APP=Path(__file__).resolve().parents[1];sys.path.insert(0,str(APP))
from biometric import load_algorithm
from multiaxis_quality_pilot import multiaxis_bank,multiaxis_distances
from quality_evidence_matcher import quality_bank,weighted_distances
from pose_matcher import POSES


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path);p.add_argument('baseline',type=Path);p.add_argument('output',type=Path)
    args=p.parse_args();args.output.mkdir(exist_ok=False,parents=True)
    cases=json.loads(args.baseline.read_text());trials=[(c,t) for c in cases for t in c['trials'] if t['route']=='exhaustive_fallback']
    algorithm=load_algorithm(APP/'vendor/palmprint-recognition-python','FastCCQualityEvidence-v24-experimental')
    kernels=[np.ascontiguousarray((algorithm.base.kernels[i]-algorithm.base.kernels[i+3])[::-1,::-1]) for i in range(3)]
    protocol=dict(method='Equal three orthogonal Gabor response-sign comparisons; sqrt-response weights, common shift, original nine poses, best2 enrollment',
        proposal_only=True,distance_changed=True,thresholds='Nominal existing .32/.08 gate; no independent unknown calibration',
        total_development_trials=sum(len(c['trials']) for c in cases),fallback_trials=len(trials),independent_validation=False,
        timing_warning='Offline feature reuse; not complete pipeline or Pi latency',
        source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),APP/'multiaxis_quality_pilot.py',args.baseline]})
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2))
    cv2.setNumThreads(1);features={};gallery={};probes={};records=[];started=time.perf_counter()
    def unpack(sample):
        if sample not in features:
            with np.load(args.root/(sample+'.npz'),allow_pickle=False) as z:f=z['feature']
            f[:4]=np.asarray([algorithm.magic],'<i4').view(np.uint8);features[sample]=algorithm._unpack(f)
        return features[sample]
    # Meaningful reduction check: a one-axis bank must reproduce the v24
    # distance and sampling, including optional poses and border weights.
    rng=np.random.default_rng(20261029);native=rng.integers(0,256,(900,900),np.uint8)
    source=np.asarray([[1.,0,-200],[0,1.,-200],[0,0,1.]])
    a=quality_bank(native,source,kernels[0]);b=multiaxis_bank(native,source,kernels[:1])
    assert all(np.array_equal(x,y[:,0]) for x,y in zip(a,b))
    assert np.allclose(weighted_distances(a,a),multiaxis_distances(b,b),atol=1e-12,rtol=0)
    try:
        for case,trial in trials:
            sample=trial['sample'];q=unpack(sample)
            if sample not in probes:probes[sample]=multiaxis_bank(q[3],q[1][2],kernels)
            ids=[s for values in case['gallery'].values() for s in values]
            for s in ids:
                if s not in gallery:
                    t=unpack(s);gallery[s]=multiaxis_bank(t[3],t[1][2],kernels,POSES[:1])
            if probes[sample] is None or any(gallery[s] is None for s in ids):scores={u:1. for u in case['gallery']}
            else:
                bank=tuple(np.concatenate([gallery[s][i] for s in ids]) for i in (0,1))
                distances=dict(zip(ids,multiaxis_distances(probes[sample],bank)))
                scores={u:float(np.mean(sorted(distances[s] for s in ss)[:2])) for u,ss in case['gallery'].items()}
            predicted=min(scores,key=scores.get);confident=algorithm.confident(scores)
            records.append(dict(case=case['case'],sample=sample,identity=trial['identity'],scores=scores,
                predicted=predicted,correct=predicted==trial['identity'],confident=confident))
            result=dict(protocol=protocol,records=records,rescued=sum(r['correct'] and r['confident'] for r in records),
                wrong_confident=sum(not r['correct'] and r['confident'] for r in records),
                complete=len(records)==len(trials),elapsed_offline_seconds=time.perf_counter()-started,one_axis_parity=True)
            (args.output/'results.json').write_text(json.dumps(result,indent=2))
            print(case['case'],sample,'confident',confident,'correct',records[-1]['correct'],flush=True)
        print(json.dumps({k:v for k,v in result.items() if k not in ('records','protocol')}),flush=True)
    finally:algorithm.close()


if __name__=='__main__':main()
