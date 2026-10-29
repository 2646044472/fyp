"""Evaluation-only public data protocols: no raw dataset transfer or tuning.

prepare inventories metadata/exposure and freezes code/models before inference.
roi tests only the frozen FastCC component locally. casia uses only existing,
hash-verified Pi originals and runs fresh enrollment plus first/warm HTTP passes.
"""
import argparse,collections,hashlib,io,json,os,random,re,struct,subprocess,sys,time,zipfile
from pathlib import Path
APP=Path(__file__).resolve().parents[1];sys.path.insert(0,str(APP))


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def canonical(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def source_sha(path):return hashlib.sha256(Path(path).read_bytes().replace(b'\r\n',b'\n')).hexdigest()
def save(path,value):Path(path).write_text(json.dumps(value,indent=2),encoding='utf-8')
def member_label(name):
    m=re.fullmatch(r'P_([FS])_(\d+)_(\d+)\.bmp',Path(name).name)
    return (m[1],int(m[2]),int(m[3])) if m else None


def prepare(args):
    root=APP/'runtime/pi5-under2-20261028';v26=json.loads((root/'compnet-v26-pi-20261030/results.json').read_text())
    assert v26['complete'];args.output.mkdir(exist_ok=False,parents=True)
    prior=json.loads((root/'palmbig-roi-validation-20261029/protocol.json').read_text())
    old_casia=json.loads((root/'casia850-validation-20261029/protocol.json').read_text())
    manifest=json.loads((root/'casia850-validation-20261029/inputs/manifest.json').read_text())
    assert len(manifest)==24 and len({r['identity'] for r in manifest})==4
    files=list(v26['code_sha256'])+['quality_evidence_matcher.py','pooled_enrollment_matcher.py','affine_enrollment_matcher.py',
        'linked_enrollment_matcher.py','guarded_index_matcher.py','proposed_index_matcher.py','indexed_demo_matcher.py',
        'demo_matcher.py','anchored_matcher.py','union_matcher.py','registered_matcher.py','pose_matcher.py',
        'fastcc_accelerated.py','pklnet_roi.py','pklnet_policy.py','window_roi.py','native_registration.py',
        'registration_accelerated.py','gallery.py','templates.py','demo_flow.py']
    for name,h in v26['code_sha256'].items():assert sha(APP/name)==h
    with zipfile.ZipFile(root/'public40-fixed-roi.zip') as z:
        prepared_labels=[member_label(n) for n in z.namelist() if member_label(n)]
    assert min(i for p,i,j in prepared_labels)==21 and max(i for p,i,j in prepared_labels)==60
    inventory=collections.Counter();groups=collections.defaultdict(list);dimensions=collections.Counter();hashes={};other=[]
    with zipfile.ZipFile(args.archive) as z:
        for n in z.namelist():
            if n.endswith('/'):continue
            label=member_label(n)
            if label is None:other.append(n);continue
            b=z.read(n);assert b[:2]==b'BM'
            width,height=struct.unpack_from('<ii',b,18);dimensions[f'{width}x{abs(height)}']+=1
            p,i,j=label;inventory[p]+=1;groups[p,i].append((j,n));hashes[n]=hashlib.sha256(b).hexdigest()
    selected={k:sorted(v) for k,v in groups.items() if 61<=k[1]<=80}
    exposed_hashes={h for n,h in hashes.items() if member_label(n)[1]<=60}
    overlap=[n for v in selected.values() for j,n in v if hashes[n] in exposed_hashes]
    eligible=(len(selected)==40 and all(len(v)>5 and len({j for j,n in v})==len(v) for v in selected.values()) and not overlap)
    protocol=dict(frozen_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=APP.parents[1],text=True).strip(),
        matcher=v26['matcher'],code_hashes={n:source_sha(APP/n) for n in dict.fromkeys(files)},
        source_hash_mode='SHA256 after CRLF-to-LF canonicalization; model binaries exact',
        evaluator_sha256=source_sha(__file__),parameters_tuned=False,thresholds=dict(early_distance=.32,early_margin=.08,final_closed_set_threshold=1.0,final_margin=0.0),
        models=dict(pklnet=v26['runs'][0]['startup']['localizer_sha256'],compnet=v26['model_metadata']['onnx_sha256'],
            native='272857b624cad687b7d87a32eb79ac0124f3d782be3e3a2b0ca092c92d87e600'),
        casia=dict(scope='Previously exposed confirmatory v26 comparison, not independent validation',manifest_canonical_sha256=canonical(manifest),
            images=24,identities=4,selection='Existing subject001..004, left,850nm,all6; enroll1..5,query6; no mixing wavelengths',
            archive_sha256=old_casia['archive_hashes'][0]['sha256'],query_seed=20261029,passes=['first_after_enrollment_and_ready','warm_repeat_same_four'],
            prior_protocol_sha256=sha(root/'casia850-validation-20261029/protocol.json'),raw_transfer_allowed=False),
        palmbig=dict(archive_sha256=sha(args.archive),prior_archive_match=sha(args.archive)==prior['archive_sha256'],
            bmp_images=sum(inventory.values()),prefix_images=dict(inventory),filename_classes=len(groups),numeric_ids=len({i for p,i in groups}),
            prefix_classes=dict(collections.Counter(p for p,i in groups)),sample_count_histogram=dict(collections.Counter(len(v) for v in groups.values())),
            dimensions=dict(dimensions),other_files=other,physical_identity_count=None,prefix_semantics='Unknown; not assumed sessions/devices',
            supplied_images='128x128 supplied palm patches; no full-original localization test',
            exposed_ids='1..20 previous400-image test;21..60 conservatively excluded from old public40 bundle/tool footprint',
            exposure_bundle_sha256=sha(root/'public40-fixed-roi.zip'),selection='All numeric IDs61..80 independently perF/S; no resampling if ineligible',
            enrollment='five lowest numeric sample indices',queries='all remaining samples',eligible=eligible,
            selected_images=sum(len(v) for v in selected.values()),selected_classes=len(selected),overlap_with_exposed_content=len(overlap),
            subset_member_sha256={n:hashes[n] for v in selected.values() for j,n in v},
            scope='Frozen normalized FastCC feature/best2 component only; local Windows timing; not v26 routing, ROI,HTTP or Pi latency'),
        reference_device=dict(correct=164,total=168,timely_correct=146,p95_ms=6019.3185,max_ms=15225.,new_session_validation=False,unknown_person_validation=False))
    assert protocol['palmbig']['prior_archive_match'] and sum(inventory.values())==7752
    save(args.output/'protocol.json',protocol)
    print(json.dumps(dict(frozen_commit=protocol['frozen_commit'],casia=protocol['casia']['scope'],palmbig={k:v for k,v in protocol['palmbig'].items() if k!='subset_member_sha256'})))


def verify(protocol):
    assert source_sha(__file__)==protocol['evaluator_sha256']
    for name,h in protocol['code_hashes'].items():assert source_sha(APP/name)==h,('Frozen code mismatch',name)


def roi(args):
    import cv2,numpy as np
    from PIL import Image
    from biometric import load_algorithm
    from fastcc_accelerated import AcceleratedFastCC
    from pklnet_roi import normalize_roi_pixels
    protocol=json.loads(args.protocol.read_text());verify(protocol);spec=protocol['palmbig']
    assert spec['eligible'] and sha(args.archive)==spec['archive_sha256']
    args.output.mkdir(exist_ok=False,parents=True);cv2.setNumThreads(1)
    algorithm=AcceleratedFastCC(load_algorithm(APP/'vendor/palmprint-recognition-python','FastCC'))
    kernel=hashlib.sha256(algorithm._difference.tobytes()).hexdigest()
    report=dict(protocol_sha256=sha(args.protocol),component='v26 normalized FastCC only; no model routing/localizer/HTTP',
        host='Windows local',opencv=cv2.__version__,kernel_sha256=kernel,cohorts=[],failures=[],independent_device_validation=False)
    with zipfile.ZipFile(args.archive) as z:
        groups=collections.defaultdict(list)
        for n,h in spec['subset_member_sha256'].items():
            p,i,j=member_label(n);groups[p,i].append((j,n,h))
        def extract(n,h):
            b=z.read(n);assert hashlib.sha256(b).hexdigest()==h
            pixels=np.asarray(Image.open(io.BytesIO(b)).convert('L'));assert pixels.shape==(128,128)
            return algorithm.extract(normalize_roi_pixels(pixels))
        for prefix in ('F','S'):
            cohort={i:sorted(v) for (p,i),v in groups.items() if p==prefix};gallery={};enroll=[]
            tick=time.perf_counter()
            for i,v in sorted(cohort.items()):
                gallery[i]=[]
                for j,n,h in v[:5]:
                    try:gallery[i].append(extract(n,h))
                    except Exception as e:report['failures'].append(dict(member=n,phase='enroll',error=str(e)))
                enroll.append(dict(identity=i,expected=5,valid=len(gallery[i])))
            record=dict(prefix=prefix,filename_classes=len(cohort),images=sum(map(len,cohort.values())),
                enrollment_component_ms=1000*(time.perf_counter()-tick),enrollments=enroll,trials=[]);report['cohorts'].append(record)
            for i,v in sorted(cohort.items()):
                for j,n,h in v[5:]:
                    begin=time.perf_counter();trial=dict(member=n,identity=i,correct=False)
                    try:
                        feature=extract(n,h);features_done=time.perf_counter()
                        scores={u:float(np.mean(sorted(algorithm.match(feature,f) for f in fs)[:2])) if len(fs)==5 else 1. for u,fs in gallery.items()}
                        ranked=sorted(scores,key=scores.get)
                        trial.update(prediction=ranked[0],scores=scores,correct=ranked[0]==i and scores[ranked[0]]<scores[ranked[1]],
                            read_decode_normalize_extract_ms=1000*(features_done-begin),match_ms=1000*(time.perf_counter()-features_done))
                    except Exception as e:
                        trial['error']=str(e);report['failures'].append(dict(member=n,phase='query',error=str(e)))
                    trial['local_roi_component_ms']=1000*(time.perf_counter()-begin);record['trials'].append(trial)
            ms=[t['local_roi_component_ms'] for t in record['trials']]
            record['summary']=dict(total=len(ms),correct=sum(t['correct'] for t in record['trials']),median_ms=float(np.median(ms)),p95_ms=float(np.percentile(ms,95)),max_ms=max(ms))
    assert hashlib.sha256(algorithm._difference.tobytes()).hexdigest()==kernel and sha(args.archive)==spec['archive_sha256']
    verify(protocol);report['complete']=True;save(args.output/'results.json',report)
    print(json.dumps([c['summary'] for c in report['cohorts']]))


def casia(args):
    import cv2,numpy as np
    from evaluate_six_person_frozen import initialize,sanitized,timed_summary
    from replay_pi_pipeline import http_app
    from replay_demo_manifest import correct_identification
    from replay_ready_queries import power_sample,power_fault
    from pklnet_roi import PKLNetROI
    protocol=json.loads(args.protocol.read_text());verify(protocol);rows=json.loads(args.manifest.read_text())
    assert canonical(rows)==protocol['casia']['manifest_canonical_sha256']
    # Existing Pi originals only. Failure here is a device-side restriction;
    # no upload, download, extraction or replacement of missing dataset files.
    assert all(Path(r['original']).is_file() and sha(r['original'])==r['sha256'] for r in rows)
    assert sha(args.native)==protocol['models']['native']
    assert sha(args.model/'compnet-tongji.onnx')==protocol['models']['compnet']
    assert sha(PKLNetROI().root/'pklnet-keypoints-diagnostics.onnx')==protocol['models']['pklnet']
    args.output.mkdir(exist_ok=False,parents=True);cv2.setNumThreads(1);os.environ['PALM_COMPNET_MODEL_ROOT']=str(args.model.resolve())
    result=dict(protocol_sha256=sha(args.protocol),matcher=protocol['matcher'],scope=protocol['casia']['scope'],
        raw_transfer_performed=False,enrollments=[],passes=[],power_samples=[])
    def checkpoint():
        sample=power_sample();result['power_samples'].append(sample);save(args.output/'results.json',result)
        if power_fault(sample):raise RuntimeError('Pi power/throttle fault')
    checkpoint();app,camera,startup=initialize(args.output/'runtime',protocol['matcher'],args.native)
    result['initialization_ready_ms']=startup
    result['kernel_sha256']=hashlib.sha256(app.demo_algorithm.base._difference.tobytes()).hexdigest()
    result['kernel_locked_before_enrollment']=True
    groups={u:sorted([r for r in rows if r['identity']==u],key=lambda r:r['index']) for u in sorted({r['identity'] for r in rows})}
    assert len(groups)==4 and all([r['index'] for r in v]==list(range(1,7)) for v in groups.values())
    try:
        with http_app(app) as (request,trace):
            for u,samples in groups.items():
                checkpoint();camera.select(samples[:5]);status,response=request('/api/demo/enroll',dict(user_id=u.replace(':','-'),display_name='CONFIRMATORY '+u),None)
                result['enrollments'].append(dict(identity=u,http_status=status,result=sanitized(response),request_ms=trace[-1]['ms']))
                checkpoint();print('enroll',u,status,round(trace[-1]['ms']),flush=True)
            tick=time.perf_counter();app.demo.gallery.warm_up();result['post_enrollment_gallery_ready_ms']=1000*(time.perf_counter()-tick)
            queries=[v[5] for v in groups.values()];random.Random(protocol['casia']['query_seed']).shuffle(queries)
            before=app.demo.payments.transaction_count()
            for name in protocol['casia']['passes']:
                run=dict(name=name,queries=[]);result['passes'].append(run)
                for row in queries:
                    checkpoint();camera.select([row]);status,response=request('/api/demo/identify',{},None)
                    trial=dict(sample=row['sample'],identity=row['identity'],http_status=status,result=sanitized(response),ms=trace[-1]['ms'])
                    trial['correct']=correct_identification(trial)
                    if response.get('token'):
                        cancelled,_=request('/api/demo/cancel',dict(token=response['token']),None);trial['cancelled']=cancelled==200
                    run['queries'].append(trial);checkpoint();print(name,row['sample'],trial['correct'],round(trial['ms']),flush=True)
                run['summary']=timed_summary(run['queries'])
            result['transactions_unchanged']=before==app.demo.payments.transaction_count()
    finally:app.demo_algorithm.close()
    result['originals_unchanged']=all(sha(r['original'])==r['sha256'] for r in rows)
    result['models_unchanged']=(sha(args.native)==protocol['models']['native'] and
        sha(args.model/'compnet-tongji.onnx')==protocol['models']['compnet'] and
        sha(PKLNetROI().root/'pklnet-keypoints-diagnostics.onnx')==protocol['models']['pklnet'])
    result['kernel_unchanged']=hashlib.sha256(app.demo_algorithm.base._difference.tobytes()).hexdigest()==result['kernel_sha256']
    verify(protocol);result['complete']=True;checkpoint();print(json.dumps([p['summary'] for p in result['passes']]),flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='mode',required=True)
    a=s.add_parser('prepare');a.add_argument('archive',type=Path);a.add_argument('output',type=Path)
    a=s.add_parser('roi');a.add_argument('archive',type=Path);a.add_argument('protocol',type=Path);a.add_argument('output',type=Path)
    a=s.add_parser('casia');a.add_argument('manifest',type=Path);a.add_argument('protocol',type=Path);a.add_argument('output',type=Path)
    a.add_argument('--model',type=Path,required=True);a.add_argument('--native',type=Path,required=True)
    args=p.parse_args();globals()[args.mode](args)


if __name__=='__main__':main()
