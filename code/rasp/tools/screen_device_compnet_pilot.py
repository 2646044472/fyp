"""Frozen CompNet on active device cases using existing Pi ROI geometry only.

This offline screen reuses per-image features across cases, never at runtime.
Source geometry comes from the prior frozen Pi enrollment exports; the new
protocol supplies the current active archive members and enrollment/query sets.
"""
import argparse,hashlib,io,json,sys,time,zipfile
from pathlib import Path
import cv2,numpy as np
from PIL import Image
APP=Path(__file__).resolve().parents[1];sys.path.insert(0,str(APP))
from biometric import load_algorithm
from compnet_pilot import CompNetPilot
from pose_matcher import POSES


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('cohort',type=Path);p.add_argument('geometry',type=Path)
    p.add_argument('model',type=Path);p.add_argument('output',type=Path);args=p.parse_args()
    args.output.mkdir(exist_ok=False,parents=True)
    rows=json.loads((args.cohort/'manifest.json').read_text());cohort=json.loads((args.cohort/'protocol.json').read_text())
    records=json.loads(args.geometry.read_text())['records'];quads={}
    for r in records:
        if r['sample'] in quads:assert np.array_equal(quads[r['sample']],r['quad'])
        quads[r['sample']]=np.asarray(r['quad'],np.float32)
    lookup={r['sample']:i for i,r in enumerate(rows)}
    encoder=CompNetPilot(args.model);cv2.setNumThreads(1)
    algorithm=load_algorithm(APP/'vendor/palmprint-recognition-python',cohort['matcher'])
    protocol=dict(method='Frozen author Tongji CompNet, no device training; single/unchanged9poses; original five enrollment ROI templates',
        cohort=cohort,model=encoder.metadata,independent_validation=False,
        timing_warning='Offline frozen ROI geometry and feature reuse, no pipeline or Pi latency claim',
        thresholds='Nominal .32/.08, NOT equivalent to FastCC or calibrated unknown-person rejection',
        source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),APP/'compnet_pilot.py',args.geometry,args.cohort/'manifest.json']})
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2))
    repo=APP.parents[1];features=[];started=time.perf_counter()
    try:
        for row in rows:
            with zipfile.ZipFile(repo/row['archive']) as z:value=z.read(row['archive_member'])
            assert hashlib.sha256(value).hexdigest()==row['sha256']
            image=Image.open(io.BytesIO(value)).convert('RGB');gray=cv2.cvtColor(np.asarray(image),cv2.COLOR_RGB2GRAY)
            quad=quads[row['sample']];center=quad.mean(axis=0);bank=[]
            for angle,scale in POSES:
                rad=np.deg2rad(angle);rotation=np.asarray([[np.cos(rad),-np.sin(rad)],[np.sin(rad),np.cos(rad)]])
                candidate=((quad-center)@rotation.T*scale+center).astype(np.float32)
                if (candidate<0).any() or (candidate[:,0]>=image.width).any() or (candidate[:,1]>=image.height).any():
                    bank.append(None);continue
                raw=algorithm.geometry.getROIimg(gray,candidate);bank.append(encoder.extract(Image.fromarray(raw)))
            assert bank[0] is not None;features.append(bank)
            print('extracted',len(features),'/',len(rows),flush=True)
        gallery=np.asarray([b[0] for b in features]);matrices={};results=[]
        for method in ('single','nine_poses'):
            matrix=np.ones((len(rows),len(rows)),np.float64)
            for i,bank in enumerate(features):
                query=np.asarray([b for b in (bank[:1] if method=='single' else bank) if b is not None])
                matrix[i]=(np.arccos(np.clip(query@gallery.T,-1,1))/np.pi).min(axis=0)
            matrices[method]=matrix
            for case in cohort['cases']:
                enrolled={u:[lookup[s] for s in ss] for u,ss in case['enrollment'].items()};trials=[]
                for sample in case['queries']:
                    i=lookup[sample];scores={u:float(np.sort(matrix[i,ids])[:2].mean()) for u,ids in enrolled.items()}
                    predicted=min(scores,key=scores.get)
                    trials.append(dict(sample=sample,identity=rows[i]['identity'],predicted=predicted,correct=predicted==rows[i]['identity'],
                        nominal_confident=algorithm.confident(scores),scores=scores))
                results.append(dict(method=method,case=case['name'],correct=sum(t['correct'] for t in trials),total=len(trials),trials=trials))
        np.savez(args.output/'distances.npz',**matrices)
        summary=[dict(method=r['method'],case=r['case'],correct=r['correct'],total=r['total'],
            correct_confident=sum(t['correct'] and t['nominal_confident'] for t in r['trials']),
            wrong_confident=sum(not t['correct'] and t['nominal_confident'] for t in r['trials'])) for r in results]
        (args.output/'results.json').write_text(json.dumps(dict(protocol=protocol,results=results,summary=summary,
            complete=True,elapsed_offline_seconds=time.perf_counter()-started),indent=2))
        print(json.dumps(summary),flush=True)
    finally:algorithm.close()


if __name__=='__main__':main()
