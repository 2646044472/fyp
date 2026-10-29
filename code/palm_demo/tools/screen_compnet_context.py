"""Frozen spatial-pyramid CompNet screen on all active and development cases.

Uses saved primary Pi geometry and immutable originals. No localization rerun,
training, query rejection or Pi runtime claim. All confidences are diagnostic;
unknown-person calibration is still absent.
"""
import argparse,hashlib,io,json,sys,time,zipfile
from pathlib import Path
import cv2,numpy as np
from PIL import Image
APP=Path(__file__).resolve().parents[1];sys.path.insert(0,str(APP))
from biometric import load_algorithm
from compnet_pilot import CompNetPilot
from compnet_context_pilot import CONTEXT_VIEWS,context_quads,context_evidence,confident_identity


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('cohort',type=Path);p.add_argument('geometry',type=Path)
    p.add_argument('model',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--development',type=Path,required=True)
    p.add_argument('--single-reference',type=Path,required=True)
    p.add_argument('--feature-bank',type=Path,help='Offline embeddings from the same model/images/quads; never used in runtime recognition')
    args=p.parse_args();args.output.mkdir(exist_ok=False,parents=True)
    rows=json.loads((args.cohort/'manifest.json').read_text());cohort=json.loads((args.cohort/'protocol.json').read_text())
    quads={r['sample']:np.asarray(r['quad'],np.float32) for r in json.loads(args.geometry.read_text())['records']}
    lookup={r['sample']:i for i,r in enumerate(rows)};truth={r['sample']:r['identity'] for r in rows}
    encoder=CompNetPilot(args.model);cv2.setNumThreads(1)
    algorithm=load_algorithm(APP/'vendor/palmprint-recognition-python',cohort['matcher'])
    protocol=dict(views=CONTEXT_VIEWS,method='Fixed 15-view spatial pyramid; independently scored crops; primary precedence, confident identity consensus',
        training_on_device_data=False,independent_validation=False,model=encoder.metadata,
        confidence='Nominal .32/.08 only; no unknown-person calibration',
        timing_scope='Offline frozen Pi primary geometry and feature reuse; no full Pi latency claim',
        source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in
            [Path(__file__),APP/'compnet_context_pilot.py',args.geometry,args.development,args.cohort/'manifest.json']})
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2))
    features=[];indices=[];legacy_features=[];changed_quads=[];started=time.perf_counter();repo=APP.parents[1]
    cache=np.load(args.feature_bank) if args.feature_bank else None
    if cache is not None:
        previous=json.loads((args.feature_bank.parent/'protocol.json').read_text())
        assert previous['model']==protocol['model'] and previous['views']==json.loads(json.dumps(CONTEXT_VIEWS))
        for name in (args.geometry.name,'manifest.json','compnet_context_pilot.py'):
            assert previous['source_sha256'][name]==protocol['source_sha256'][name]
        protocol['offline_feature_bank_sha256']=hashlib.sha256(args.feature_bank.read_bytes()).hexdigest()
    try:
        for row in rows:
            with zipfile.ZipFile(repo/row['archive']) as z:value=z.read(row['archive_member'])
            assert hashlib.sha256(value).hexdigest()==row['sha256']
            image=Image.open(io.BytesIO(value)).convert('RGB')
            native=cv2.cvtColor(np.asarray(image),cv2.COLOR_RGB2GRAY)
            bank=[];valid=[];crops=context_quads(quads[row['sample']],image.size)
            for j,(i,q) in enumerate(crops):
                bank.append(cache[row['sample']][j] if cache is not None else encoder.extract(Image.fromarray(algorithm.geometry.getROIimg(native,q))))
                valid.append(i)
            assert np.asarray(bank).shape==(len(crops),512)
            assert valid[0]==0;features.append(np.asarray(bank));indices.append(valid)
            q=quads[row['sample']];center=q.mean(axis=0)
            legacy=((q-center)@np.eye(2)+center).astype(np.float32)
            if np.array_equal(legacy,q):legacy_features.append(bank[0])
            else:
                changed_quads.append(dict(sample=row['sample'],max_corner_delta=float(np.max(np.abs(legacy-q)))))
                legacy_features.append(encoder.extract(Image.fromarray(algorithm.geometry.getROIimg(native,legacy))))
            print('extracted',len(features),'/',len(rows),flush=True)
        np.savez_compressed(args.output/'embeddings.npz',**{row['sample']:f for row,f in zip(rows,features)})
        gallery=np.asarray([f[0] for f in features]);distances=[np.arccos(np.clip(f@gallery.T,-1,1))/np.pi for f in features]
        reference=np.load(args.single_reference)['single']
        assert reference.shape==(len(rows),len(rows))
        # Self-comparison is not a protocol query. float32 GEMM changes near-1
        # self dot products by an ulp, amplified by acos; inspect separately.
        delta=np.abs(np.asarray([d[0] for d in distances])-reference)
        self_error=float(np.max(np.diag(delta)))
        error=float(np.max(delta[~np.eye(len(rows),dtype=bool)]))
        legacy_gallery=np.asarray(legacy_features)
        # Reconstruct the earlier screen's angle=0 arithmetic. Compare cosine
        # products before acos, including near-identical/self dot products.
        legacy_cosine=np.clip(legacy_gallery@legacy_gallery.T,-1,1)
        reference_cosine=np.cos(reference*np.pi)
        legacy_cosine_error=float(np.max(np.abs(legacy_cosine-reference_cosine)))
        assert legacy_cosine_error<1e-6,('Legacy encoder parity failed',legacy_cosine_error)
        cases=[dict(case=c['name'],gallery=c['enrollment'],trials=[dict(sample=s,identity=truth[s]) for s in c['queries']],cohort='active169') for c in cohort['cases']]
        cases.extend(dict(c,cohort='development') for c in json.loads(args.development.read_text()))
        results=[]
        for case in cases:
            enrolled={u:[lookup[s] for s in ss] for u,ss in case['gallery'].items()};trials=[]
            assert not ({t['sample'] for t in case['trials']}&{s for ss in case['gallery'].values() for s in ss})
            for t in case['trials']:
                i=lookup[t['sample']]
                scores=[{u:float(np.sort(d[ids])[:2].mean()) for u,ids in enrolled.items()} for d in distances[i]]
                predicted,votes=context_evidence(scores);primary=confident_identity(scores[0])
                trials.append(dict(sample=t['sample'],identity=t['identity'],predicted=predicted,
                    correct=predicted==t['identity'],confident=predicted is not None,primary_confident=primary is not None,
                    view_ids=indices[i],confident_views=votes,score_views=scores))
            results.append(dict(case=case['case'],cohort=case['cohort'],trials=trials))
        summary={}
        for name in ('active169','development'):
            trials=[t for r in results if r['cohort']==name for t in r['trials']]
            extra=[t for t in trials if t['confident'] and not t['primary_confident']]
            summary[name]=dict(total=len(trials),confident=sum(t['confident'] for t in trials),
                wrong_confident=sum(t['confident'] and not t['correct'] for t in trials),
                extra_confident=len(extra),extra_wrong=sum(not t['correct'] for t in extra))
        result=dict(protocol=protocol,summary=summary,results=results,primary_max_abs_error=error,primary_self_comparison_max_abs_error=self_error,
                    legacy_cosine_max_abs_error=legacy_cosine_error,legacy_angle_zero_corner_changes=changed_quads,
                    complete=True,elapsed_offline_seconds=time.perf_counter()-started)
        (args.output/'results.json').write_text(json.dumps(result,indent=2));print(json.dumps(summary),flush=True)
    finally:
        algorithm.close()
        if cache is not None:cache.close()


if __name__=='__main__':main()
