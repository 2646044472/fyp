"""Fixed 180-degree localization equivariance control on all 80 development images.

Frozen PKLNet weights and original-pixel FastCC; no identity-selected rotation.
This is an offline screening tool, not a deployed policy or latency benchmark.
"""
import argparse,hashlib,json,sys,time
from pathlib import Path
import cv2,numpy as np
from PIL import Image
APP=Path(__file__).resolve().parents[1];sys.path.insert(0,str(APP))
from biometric import load_algorithm
from pklnet_roi import PKLNetROI,normalize_roi_pixels


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--baseline',type=Path,required=True)
    args=p.parse_args();args.output.mkdir(exist_ok=False,parents=True)
    rows=json.loads((args.root/'stability/records.json').read_text(encoding='utf-8'))
    cases=json.loads(args.baseline.read_text(encoding='utf-8'));lookup={r['sample']:i for i,r in enumerate(rows)}
    protocol=dict(method='Rotate every localizer input by180, map quad back; frozen illumination policy; original grayscale scoring',
        controls=['rotated query / existing enrollment','rotated query / rotated enrollment'],
        candidate_selection='No label/quality-specific rotation selection; same fixed rotation for every image',
        acceptance='Existing .32/.08 confidence gate; every query retained; offline only',
        independent_unseen_validation=False,tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        baseline_sha256=hashlib.sha256(args.baseline.read_bytes()).hexdigest())
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2),encoding='utf-8')
    cv2.setNumThreads(1);engine=PKLNetROI(threads=2)
    algorithm=load_algorithm(APP/'vendor/palmprint-recognition-python','FastCCQualityEvidence-v24-experimental')
    original=[];rotated=[];diagnostics=[];started=time.perf_counter()
    try:
        for row in rows:
            path=Path(row['original']);assert hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256']
            with np.load(args.root/'single-device/runtime-v5'/(row['sample']+'.npz'),allow_pickle=False) as z:f=z['feature']
            f[:4]=np.asarray([algorithm.magic],'<i4').view(np.uint8)
            q=algorithm._unpack(f,decode_native=False);original.append(q[1][0].copy())
            image=Image.open(path).convert('RGB');begin=time.perf_counter()
            try:
                _,quad,detail=engine.extract(image.transpose(Image.Transpose.ROTATE_180))
                quad=np.asarray([image.width-1,image.height-1],np.float32)-quad
                valid=bool(detail['roi_geometry_valid'])
                if valid:
                    raw=algorithm.geometry.getROIimg(cv2.cvtColor(np.asarray(image),cv2.COLOR_RGB2BGR),quad)
                    bank=algorithm._pose.extract_with_context(image,quad,normalize_roi_pixels(raw))
                else:bank=None
                diagnostics.append(dict(sample=row['sample'],valid=valid,quad=quad.tolist(),details=detail,
                    local_host_ms=(time.perf_counter()-begin)*1000))
            except Exception as error:
                bank=None;diagnostics.append(dict(sample=row['sample'],valid=False,error=str(error)))
            rotated.append(bank)
            (args.output/'localization.json').write_text(json.dumps(diagnostics,indent=2),encoding='utf-8')
            print('localized',len(rotated),'/',len(rows),bank is not None,flush=True)
        n=len(rows);matrices={k:np.ones((n,n),np.float64) for k in ('query_only','both')}
        for i,row in enumerate(rows):
            if rotated[i] is None:continue
            for j,target in enumerate(rows):
                if i==j or row['cohort']!=target['cohort']:continue
                for name,gallery in (('query_only',original[j]),('both',rotated[j])):
                    if gallery is not None:
                        matrices[name][i,j]=min(float(algorithm.base.match(b.astype(bool),gallery[0].astype(bool)))
                            for b in rotated[i] if b[0,0]>=0)
        np.savez(args.output/'distances.npz',**matrices)
        results=[]
        for name,matrix in matrices.items():
            for case in cases:
                enrolled={u:[lookup[s] for s in ids] for u,ids in case['gallery'].items()};trials=[]
                for trial in case['trials']:
                    i=lookup[trial['sample']]
                    scores={u:float(np.sort(matrix[i,ids])[:2].mean()) for u,ids in enrolled.items()}
                    predicted=min(scores,key=scores.get);confident=algorithm.confident(scores)
                    trials.append(dict(sample=trial['sample'],identity=trial['identity'],predicted=predicted,
                        correct=predicted==trial['identity'],confident=confident,scores=scores,
                        baseline_route=trial['route']))
                results.append(dict(method=name,case=case['case'],trials=trials))
        summary={name:dict(total=sum(len(c['trials']) for c in results if c['method']==name),
            correct_confident=sum(t['confident'] and t['correct'] for c in results if c['method']==name for t in c['trials']),
            wrong_confident=sum(t['confident'] and not t['correct'] for c in results if c['method']==name for t in c['trials']),
            fallback_rescued=sum(t['confident'] and t['correct'] and t['baseline_route']=='exhaustive_fallback'
                for c in results if c['method']==name for t in c['trials'])) for name in matrices}
        (args.output/'results.json').write_text(json.dumps(dict(protocol=protocol,results=results,summary=summary,
            valid_images=sum(r['valid'] for r in diagnostics),complete=True,elapsed_offline_seconds=time.perf_counter()-started),indent=2),encoding='utf-8')
        print(json.dumps(summary),flush=True)
    finally:algorithm.close()


if __name__=='__main__':main()
