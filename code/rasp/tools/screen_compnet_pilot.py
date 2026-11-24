"""Frozen external CompNet on all development splits; no target-data training.

Two predeclared controls: one original ROI and the existing fixed nine query
poses. Enrollment always uses the five original ROIs. Rank and nominal gates
are distinct; a new metric needs separate unknown-person calibration.
"""
import argparse,hashlib,json,sys,time
from pathlib import Path
import cv2,numpy as np
from PIL import Image
APP=Path(__file__).resolve().parents[1];sys.path.insert(0,str(APP))
from biometric import load_algorithm
from compnet_pilot import CompNetPilot
from anchored_matcher import source_quad
from pose_matcher import POSES


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path);p.add_argument('baseline',type=Path)
    p.add_argument('model',type=Path);p.add_argument('output',type=Path);args=p.parse_args()
    args.output.mkdir(exist_ok=False,parents=True)
    rows=json.loads((args.root/'stability/records.json').read_text());cases=json.loads(args.baseline.read_text())
    lookup={r['sample']:i for i,r in enumerate(rows)};encoder=CompNetPilot(args.model)
    cv2.setNumThreads(1);algorithm=load_algorithm(APP/'vendor/palmprint-recognition-python','FastCCQualityEvidence-v24-experimental')
    protocol=dict(method='Author Tongji CompNet embedding, no training; single/unchanged9poses; angular distance best2 of5',
        model=encoder.metadata,independent_validation=False,development_images=len(rows),
        timing_warning='Offline reuse across fixed splits; not pipeline or Pi latency',
        thresholds='Nominal .32/.08, NOT equivalent to FastCC acceptance or calibrated stranger rejection',
        source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),APP/'compnet_pilot.py',args.baseline]})
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2))
    started=time.perf_counter();features=[];extractions=[]
    try:
        for row in rows:
            assert hashlib.sha256(Path(row['original']).read_bytes()).hexdigest()==row['sha256']
            with np.load(args.root/'single-device/runtime-v5'/(row['sample']+'.npz'),allow_pickle=False) as z:f=z['feature']
            f[:4]=np.asarray([algorithm.magic],'<i4').view(np.uint8);parts=algorithm._unpack(f,decode_native=False)
            quad=source_quad(parts[1][2]);image=Image.open(row['original']).convert('RGB')
            gray=cv2.cvtColor(np.asarray(image),cv2.COLOR_RGB2GRAY);center=quad.mean(axis=0)
            bank=[];begin=time.perf_counter()
            for angle,scale in POSES:
                rad=np.deg2rad(angle);rotation=np.asarray([[np.cos(rad),-np.sin(rad)],[np.sin(rad),np.cos(rad)]])
                candidate=((quad-center)@rotation.T*scale+center).astype(np.float32)
                if (candidate<0).any() or (candidate[:,0]>=image.width).any() or (candidate[:,1]>=image.height).any():
                    bank.append(None);continue
                raw=algorithm.geometry.getROIimg(gray,candidate)
                bank.append(encoder.extract(Image.fromarray(raw)))
            assert bank[0] is not None
            features.append(bank);extractions.append(dict(sample=row['sample'],local_host_ms=(time.perf_counter()-begin)*1000,
                valid_poses=sum(b is not None for b in bank)))
            print('extracted',len(features),'/',len(rows),flush=True)
        gallery=np.asarray([b[0] for b in features]);matrices={}
        for method in ('single','nine_poses'):
            matrix=np.ones((len(rows),len(rows)),np.float64)
            for i,bank in enumerate(features):
                query=np.asarray([b for b in (bank[:1] if method=='single' else bank) if b is not None])
                distances=np.arccos(np.clip(query@gallery.T,-1,1))/np.pi
                matrix[i]=distances.min(axis=0)
            matrices[method]=matrix
        results=[]
        for method,matrix in matrices.items():
            for case in cases:
                enrolled={u:[lookup[s] for s in ids] for u,ids in case['gallery'].items()};trials=[]
                for t in case['trials']:
                    i=lookup[t['sample']];scores={u:float(np.sort(matrix[i,ids])[:2].mean()) for u,ids in enrolled.items()}
                    predicted=min(scores,key=scores.get)
                    trials.append(dict(sample=t['sample'],identity=t['identity'],predicted=predicted,correct=predicted==t['identity'],
                        nominal_confident=algorithm.confident(scores),scores=scores))
                results.append(dict(method=method,case=case['case'],correct=sum(t['correct'] for t in trials),total=len(trials),trials=trials))
        summary={method:{cohort:dict(cases=len(values),minimum=min(values),mean=float(np.mean(values)),maximum=max(values))
            for cohort in ('new','old') if (values:=[r['correct'] for r in results if r['method']==method and r['case'].startswith(cohort+'_')])}
            for method in matrices}
        np.savez(args.output/'distances.npz',**matrices)
        (args.output/'results.json').write_text(json.dumps(dict(protocol=protocol,results=results,summary=summary,extractions=extractions,
            nominal_wrong_confident=sum(t['nominal_confident'] and not t['correct'] for r in results for t in r['trials']),
            complete=True,elapsed_offline_seconds=time.perf_counter()-started),indent=2))
        print(json.dumps(summary),flush=True)
    finally:algorithm.close()


if __name__=='__main__':main()
