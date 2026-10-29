"""Frozen CompNet with one predeclared local-contrast control, no fitting.

Only the original ROI is used; gallery and query both receive percentile
normalization then existing CLAHE(2,8x8). Raw embedding confidence keeps
precedence. All development/current queries remain in the denominator.
"""
import argparse,hashlib,io,json,sys,time,zipfile
from pathlib import Path
import cv2,numpy as np
from PIL import Image
APP=Path(__file__).resolve().parents[1];sys.path.insert(0,str(APP))
from biometric import load_algorithm
from compnet_pilot import CompNetPilot
from compnet_context_pilot import confident_identity
from pklnet_roi import normalize_roi_pixels


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('cohort',type=Path);p.add_argument('geometry',type=Path)
    p.add_argument('model',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--development',type=Path,required=True);args=p.parse_args()
    rows=json.loads((args.cohort/'manifest.json').read_text());cohort=json.loads((args.cohort/'protocol.json').read_text())
    quads={r['sample']:np.asarray(r['quad'],np.float32) for r in json.loads(args.geometry.read_text())['records']}
    lookup={r['sample']:i for i,r in enumerate(rows)};truth={r['sample']:r['identity'] for r in rows}
    encoder=CompNetPilot(args.model);cv2.setNumThreads(1)
    algorithm=load_algorithm(APP/'vendor/palmprint-recognition-python',cohort['matcher'])
    args.output.mkdir(exist_ok=False,parents=True)
    protocol=dict(method='Original ROI only; raw evidence first, then fixed percentile1/99 and CLAHE(clip2,tile8x8) on both gallery/query before frozen CompNet',
        thresholds='Unchanged numerical .32/.08 gates; no unknown-person calibration',model=encoder.metadata,
        training_on_device_data=False,independent_validation=False,timing_scope='Offline geometry/feature reuse, no Pi pipeline timing',
        source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in
            [Path(__file__),args.geometry,args.development,args.cohort/'manifest.json']})
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2))
    features={k:[] for k in ('raw','clahe')};repo=APP.parents[1];started=time.perf_counter()
    clahe=cv2.createCLAHE(clipLimit=2.,tileGridSize=(8,8))
    try:
        for row in rows:
            with zipfile.ZipFile(repo/row['archive']) as z:value=z.read(row['archive_member'])
            assert hashlib.sha256(value).hexdigest()==row['sha256']
            native=cv2.cvtColor(np.asarray(Image.open(io.BytesIO(value)).convert('RGB')),cv2.COLOR_RGB2GRAY)
            raw=algorithm.geometry.getROIimg(native,quads[row['sample']])
            contrast=clahe.apply(normalize_roi_pixels(raw))
            features['raw'].append(encoder.extract(Image.fromarray(raw)))
            features['clahe'].append(encoder.extract(Image.fromarray(contrast)))
        features={k:np.asarray(v) for k,v in features.items()}
        matrices={k:np.arccos(np.clip(v@v.T,-1,1))/np.pi for k,v in features.items()}
        cases=[dict(case=c['name'],gallery=c['enrollment'],trials=[dict(sample=s,identity=truth[s]) for s in c['queries']],cohort='active169') for c in cohort['cases']]
        cases.extend(dict(c,cohort='development') for c in json.loads(args.development.read_text()))
        results=[]
        for case in cases:
            enrolled={u:[lookup[s] for s in ss] for u,ss in case['gallery'].items()};trials=[]
            assert not ({t['sample'] for t in case['trials']}&{s for ss in case['gallery'].values() for s in ss})
            for t in case['trials']:
                i=lookup[t['sample']]
                scores={k:{u:float(np.sort(m[i,ids])[:2].mean()) for u,ids in enrolled.items()} for k,m in matrices.items()}
                raw=confident_identity(scores['raw']);contrast=confident_identity(scores['clahe'])
                predicted=raw if raw is not None else contrast
                trials.append(dict(sample=t['sample'],identity=t['identity'],predicted=predicted,
                    correct=predicted==t['identity'],confident=predicted is not None,
                    raw_confident=raw is not None,clahe_confident=contrast is not None,scores=scores))
            results.append(dict(case=case['case'],cohort=case['cohort'],trials=trials))
        summary={}
        for name in ('active169','development'):
            trials=[t for r in results if r['cohort']==name for t in r['trials']]
            extra=[t for t in trials if t['confident'] and not t['raw_confident']]
            summary[name]=dict(total=len(trials),extra_confident=len(extra),extra_wrong=sum(not t['correct'] for t in extra),
                confident=sum(t['confident'] for t in trials),wrong_confident=sum(t['confident'] and not t['correct'] for t in trials))
        np.savez_compressed(args.output/'embeddings.npz',**features)
        result=dict(protocol=protocol,summary=summary,results=results,complete=True,elapsed_offline_seconds=time.perf_counter()-started)
        (args.output/'results.json').write_text(json.dumps(result,indent=2));print(json.dumps(summary),flush=True)
    finally:algorithm.close()


if __name__=='__main__':main()
