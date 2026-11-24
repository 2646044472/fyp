"""Evaluate frozen alignment proposals on expanded device fallback cases.

Uses original JPEG bytes, actual Pi enrollment transforms/codes and actual Pi
query transforms. No localizer is rerun. This is an offline proposal screen,
not a complete pipeline or target-device latency measurement.
"""
import argparse
from collections import Counter
import hashlib,json,sys,time,zipfile
from pathlib import Path
import cv2,numpy as np
from screen_local_contrast_alignment import contrast_views,aligned_scores,transfer_scores,APP
from biometric import load_algorithm


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('evidence',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--xfeat-root',type=Path,help='Alternative frozen XFeat proposal pilot; no CLAHE')
    p.add_argument('--enrollment-links',type=Path,help='Frozen actual Pi within-enrollment link export')
    args=p.parse_args();args.output.mkdir(exist_ok=False,parents=True)
    data=json.loads((args.evidence/'results.json').read_text(encoding='utf-8'))
    assert data['complete'] and data['originals_unchanged']
    manifest={r['sample']:r for r in json.loads((args.evidence/'manifest.json').read_text(encoding='utf-8'))}
    geometry=json.loads((args.evidence/'all-enrollment-geometry.json').read_text(encoding='utf-8'))
    targets={(r['case'],r['sample']):r for r in geometry['records']}
    links={}
    if args.enrollment_links:
        for link in json.loads(args.enrollment_links.read_text(encoding='utf-8'))['links']:
            links.setdefault((link['case'],link['source']),[]).append((link['target'],np.asarray(link['matrix'])))
    protocol=dict(method='Frozen CLAHE clip2 tiles8, SIFT raw/sigma2, query768 center/enrollment384',
        scoring='Unchanged original-pixel FastCC best2, similarity/affine guards, .32/.08 gate',
        scope='Every exhaustive fallback in the completed 170-query device baseline; other routes unchanged',
        timing_warning='Offline cached feature/pair screen; no full-pipeline or Pi latency claim',
        tuning=False,independent_unseen_validation=False,
        source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in
            [Path(__file__),APP/'tools/screen_local_contrast_alignment.py',args.evidence/'results.json',
             args.evidence/'all-enrollment-geometry.json']})
    protocol['enrollment_link_export_sha256']=hashlib.sha256(args.enrollment_links.read_bytes()).hexdigest() if args.enrollment_links else None
    extractor=contrast_views;pair_finder=None
    if args.xfeat_root:
        from xfeat_alignment_pilot import XFeatProposal,xfeat_pairs
        extractor=XFeatProposal(args.xfeat_root)
        pair_finder=xfeat_pairs
        protocol.update(method='Pretrained XFeat sparse top1000 threshold.05; query768 center/enrollment384',
            correspondences='Upstream MNN with default cosine>.82; original geometric and final confidence guards',
            model_metadata=json.loads((args.xfeat_root/'metadata.json').read_text(encoding='utf-8')))
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2),encoding='utf-8')
    algorithm=load_algorithm(APP/'vendor/palmprint-recognition-python',data['protocol']['matcher'])
    cv2.setNumThreads(1);natives={};gallery={};query_views={};pairs={};direct={};records=[];counts=Counter()
    repo=APP.parents[1];cases={c['name']:c for c in data['protocol']['cases']};started=time.perf_counter()
    def native(sample):
        if sample not in natives:
            row=manifest[sample]
            with zipfile.ZipFile(repo/row['archive']) as z:value=z.read(row['archive_member'])
            assert hashlib.sha256(value).hexdigest()==row['sha256']
            pixels=cv2.imdecode(np.frombuffer(value,np.uint8),cv2.IMREAD_COLOR)
            natives[sample]=cv2.cvtColor(pixels,cv2.COLOR_BGR2GRAY)
        return natives[sample]
    try:
        for run in data['runs']:
            for trial in run['queries']:
                if trial['result'].get('recognition_route')!='exhaustive_fallback':continue
                sample=trial['sample'];source=np.asarray(trial['diagnostics']['source_matrix'])
                query_key=run['case'],sample
                query_views[query_key]=extractor(native(sample),source,True)
                scores={}
                for identity,enrolled in cases[run['case']]['enrollment'].items():
                    distances=[]
                    for target in enrolled:
                        key=run['case'],target
                        entry=targets[key]
                        if key not in gallery:
                            gallery[key]=extractor(native(target),np.asarray(entry['source_matrix']),False)
                        pair_key=run['case'],sample,target
                        if pair_key not in pairs:
                            direct[pair_key]=[]
                            pairs[pair_key],trace=aligned_scores(algorithm,native(sample),source,query_views[query_key],
                                gallery[key],np.asarray(entry['reference_code']).astype(bool),pair_finder,direct[pair_key])
                            counts.update(trace)
                        distances.append(pairs[pair_key])
                    if args.enrollment_links:
                        distances,trace=transfer_scores(algorithm,native(sample),source,enrolled,
                            {t:np.asarray(targets[run['case'],t]['reference_code']).astype(bool) for t in enrolled},
                            {t:direct[run['case'],sample,t] for t in enrolled},distances,
                            {t:links.get((run['case'],t),[]) for t in enrolled})
                        counts.update(trace)
                    scores[identity]=float(np.mean(sorted(distances)[:2]))
                predicted=min(scores,key=scores.get);confident=algorithm.confident(scores)
                records.append(dict(case=run['case'],sample=sample,identity=trial['identity'],
                    baseline_correct=trial['correct'],baseline_ms=trial['ms'],scores=scores,
                    predicted=predicted,correct=predicted==trial['identity'],confident=confident,
                    proposed_correct=predicted==trial['identity'] if confident else trial['correct']))
                result=dict(protocol=protocol,records=records,counts=dict(counts),
                    baseline_correct=sum(t['correct'] for r in data['runs'] for t in r['queries']),
                    proposed_correct=sum(t['correct'] for r in data['runs'] for t in r['queries']
                        if t['result'].get('recognition_route')!='exhaustive_fallback')+sum(r['proposed_correct'] for r in records),
                    rescued=sum(r['confident'] and r['correct'] for r in records),
                    wrong_confident=sum(r['confident'] and not r['correct'] for r in records),
                    elapsed_offline_seconds=time.perf_counter()-started,complete=False)
                (args.output/'results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
                print(run['case'],sample,'base',trial['correct'],'candidate',records[-1]['correct'],
                    'confident',confident,flush=True)
        result['complete']=True
        (args.output/'results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
        print(json.dumps({k:v for k,v in result.items() if k not in ('records','protocol')}),flush=True)
    finally:algorithm.close()


if __name__=='__main__':main()
