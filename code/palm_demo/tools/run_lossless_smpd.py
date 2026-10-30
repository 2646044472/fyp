"""Independent v27 SMPD execution; fresh460 registrations and all3217 queries.

Reuse the tested operational journal/HTTP loop through a frozen explicit adapter.
No historical feature/score prefix is imported. Source images/metadata only.
"""
import argparse
import hashlib
import inspect
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import types

import numpy as np

import run_terminal_smpd as previous
from smpd_run_journal import Journal,atomic,digest,file_sha,inside,load
from lossless_template_store import LosslessTemplateStore,SCHEMA,_open_archive,_read_npy
from lossless_union_matcher import LosslessUnionMatcher
from union_lossless_codec import CODEC,MAX_FEATURE_BYTES,decode

APP=previous.APP
MATCHER=LosslessUnionMatcher.name
POLICY=previous.POLICY
resources_ok=previous.resources_ok
_verified={}


def reuse_audit(source):
    """Batch metadata audit; do not load/convert even one historical feature."""
    p=load(source/'protocol.json')
    rows=[load(path) for path in sorted((source/'records/enrollment').glob('*.json'))]
    successful=[r for r in rows if r['payload']['ok']]
    assert len(rows)==460 and len(successful)==417
    return dict(records=460,successful=417,failed=43,
        raw_input_hash_present=sum(bool(r['payload'].get('source_sha256')) for r in successful),
        decoded_rgb_hash_present=sum(bool(r['payload'].get('capture',{}).get('decoded_rgb_sha256')) for r in successful),
        source_protocol_sha256=file_sha(source/'protocol.json'),historical_feature_arrays_loaded=0,
        feature_reuse=False,decision='Regenerate all460 fixed originals: historical records contain no decoded RGB byte hashes for a whole-batch comparison.',
        historical_schema='fixed v26; logical codec equality on a pilot does not certify all417 frames')


def preparer_source():
    source=inspect.getsource(previous.prepare_app)
    old='app.demo_algorithm.magic == 2801066'
    assert source.count(old)==1
    source=source.replace(old,'app.demo_algorithm.magic == 2801166')
    old="        camera.size = list(full.size)\n"
    assert source.count(old)==1
    source=source.replace(old,"        camera.audit['decoded_rgb_sha256'] = hashlib.sha256(full.tobytes()).hexdigest()\n"+old)
    return source


def _prepared_impl():
    namespace=dict(vars(previous),MATCHER=MATCHER,POLICY=POLICY)
    source=preparer_source();exec(compile(source,'<frozen-v27-smpd-preparer>','exec'),namespace)
    return namespace['prepare_app']


_preparer=None


def prepare_app(root,p,*,gallery):
    global _preparer
    if _preparer is None:_preparer=_prepared_impl()
    app,camera,ready=_preparer(root,p,gallery=gallery)
    assert isinstance(app.demo.store,LosslessTemplateStore)
    assert app.demo.gallery.required_metadata['template_codec']==CODEC
    assert app.demo.gallery.required_metadata['template_storage_schema']==SCHEMA
    actual=app.capture_demo_feature
    def guard(call):
        try:return call()
        except Exception as error:
            message=str(error).lower()
            if isinstance(error,MemoryError) or any(t in message for t in ('resource limit','capacity exceeded','allocation limit')):
                camera.audit['fatal']='Capacity/memory guard: '+type(error).__name__+': '+str(error)
            raise
    def observe(feature):
        decoded=decode(feature,decode_native=False)
        if decoded.storage_codec!=CODEC:raise ValueError('New run produced a historical-codec feature')
        camera.audit['feature_bytes']=max(camera.audit.get('feature_bytes',0),feature.size)
        camera.audit['feature_codec']=CODEC
        camera.audit['feature_views']=dict(query=len(decoded.query_chunks),gallery=len(decoded.gallery_chunks))
        return feature
    def capture(*,enrollment=False):
        feature,image,source=guard(lambda:actual(enrollment=enrollment))
        if isinstance(feature,np.ndarray):guard(lambda:observe(feature))
        else:
            fallback=getattr(feature,'exhaustive',None)
            if callable(fallback):feature.exhaustive=lambda:guard(lambda:observe(fallback()))
        return feature,image,source
    app.capture_demo_feature=capture
    app.demo.capture_feature=lambda:capture(enrollment=False)
    app.demo.capture_enrollment_feature=lambda:capture(enrollment=True)
    if gallery:
        run_root=root.parent.parent;state=load(run_root/'status.json')
        atomic(run_root/'query-phases'/(state['epoch']+'.json'),dict(epoch=state['epoch'],started_unix=time.time(),memory=previous.memory()))
    return app,camera,dict(ready,codec=CODEC,storage=SCHEMA)


def validate_feature(root,p,row,record):
    payload=record['payload']
    if payload['source_sha256']!=row['sha256']:raise ValueError('Enrollment source hash changed')
    if not payload['ok']:return None
    if not payload['capture'].get('decoded_rgb_sha256'):raise ValueError('Missing new-version decoded RGB hash')
    path=inside(payload['feature'],root/'features')
    if file_sha(path)!=payload['feature_sha256']:raise ValueError('Fresh feature container hash changed')
    size=payload['capture'].get('feature_bytes')
    if type(size)!=int or not 0<size<=MAX_FEATURE_BYTES:raise ValueError('Invalid variable feature length')
    with _open_archive(path,1) as archive:
        if archive.namelist()!=['feature.npy']:raise ValueError('Unexpected fresh feature members')
        feature=_read_npy(archive,archive.getinfo('feature.npy'),(size,))
    if decode(feature,decode_native=False).storage_codec!=CODEC:raise ValueError('Old feature reuse forbidden')
    return feature


def build_gallery(root,p,journal):
    from payment import PaymentService
    from pklnet_roi import ROI_GEOMETRY_VERSION
    runtime=root/'evaluation/runtime';store=LosslessTemplateStore(runtime/'demo_templates')
    payments=PaymentService(runtime/'demo_payment.sqlite3');by_sample={r['sample']:r for r in journal.records};entries=[]
    for identity in sorted({r['identity'] for r in p['rows']}):
        selected=[r for r in previous.ordered_rows(p,True) if r['identity']==identity]
        assert len(selected)==5 and [r['index'] for r in selected]==list(range(5))
        records=[by_sample[r['sample']] for r in selected];ok=all(r['payload']['ok'] for r in records);user=identity.replace(':','-')
        entry=dict(identity=identity,user=user,samples=[r['sample'] for r in selected],registered=ok)
        entries.append(entry)
        atomic(root/'gallery-progress.json',dict(updated_unix=time.time(),identities_considered=len(entries),
            registered_so_far=sum(e['registered'] for e in entries),current_identity=identity))
        if not ok:
            if store.exists(user) or payments.user_exists(user):raise ValueError('Failed enrollment unexpectedly registered')
            continue
        meta=dict(user=user,display_name='EVAL '+identity,algorithm=MATCHER,capture_profile='noir-ir',samples=5,
            roi_geometry=ROI_GEOMETRY_VERSION,roi_sources=['pklnet']*5,template_codec=CODEC,template_storage_schema=SCHEMA,
            run_fingerprint=p['run_fingerprint'],frame_record_sha256=[r['record_sha256'] for r in records],
            source='Fresh fixed SMPD original-image v27 extraction; no imported features')
        seal=root/'gallery-records'/(user+'.json')
        if store.exists(user):
            frames,metadata=store.load(user)
            if metadata!=meta:raise ValueError('Wrong-version gallery metadata')
            if not seal.exists():
                original=[validate_feature(root,p,row,record) for row,record in zip(selected,records)]
                if not all(np.array_equal(a,b) for a,b in zip(frames,original)):raise ValueError('Unsealed gallery differs from fresh frame records')
                del original
            del frames
        else:
            frames=[validate_feature(root,p,row,record) for row,record in zip(selected,records)]
            store.save(user,frames,meta);del frames
        if not payments.user_exists(user):payments.create_account(user,'EVAL '+identity,10000)
        if payments.balance_for(user)!=10000 or payments.transaction_count()!=0:raise ValueError('Isolated payment state changed')
        entry['container_sha256']=file_sha(store.paths(user)[0])
        value=dict(run_fingerprint=p['run_fingerprint'],**entry)
        if seal.exists():
            if load(seal)!=value:raise ValueError('Identity gallery seal changed')
        else:atomic(seal,value,exclusive=True)
    users=sorted(e['user'] for e in entries if e['registered'])
    if store.list_users()!=users:raise ValueError('Complete eligible gallery mismatch')
    value=dict(run_fingerprint=p['run_fingerprint'],enrollments=entries,registered=len(users),codec=CODEC,storage=SCHEMA)
    if (root/'gallery.json').exists():
        if load(root/'gallery.json')!=value:raise ValueError('Complete gallery seal changed')
    else:atomic(root/'gallery.json',value,exclusive=True)
    return value


def _critical_stamps(p):
    result={}
    for group in ('source_sha256','models_sha256','metadata_sha256'):
        for path in p[group]:
            stat=Path(path).stat();result[path]=tuple(getattr(stat,field) for field in ('st_dev','st_ino','st_size','st_mtime_ns','st_ctime_ns'))
    return result


def verify(p,*,dependencies=False):
    key=p['run_fingerprint'];now=time.monotonic();cached=_verified.get(key)
    if digest({k:v for k,v in p.items() if k!='run_fingerprint'})!=key:raise ValueError('Run fingerprint changed')
    if cached is not None and _critical_stamps(p)!=cached['stamps']:raise ValueError('Frozen source/model/metadata file identity changed')
    if dependencies or cached is None or now-cached['verified_at']>=60:
        previous.verify(p,dependencies=dependencies)
        _verified[key]=dict(stamps=_critical_stamps(p),verified_at=now)
    elif {k:v for k,v in os.environ.items() if k.startswith(('PALM_','OMP_','MKL_','OPENBLAS_','ORT_')) and k!='PALM_COMPNET_MODEL_ROOT'}!=p['environment']['relevant_environment']:
        raise ValueError('Execution environment changed')


def execution_work(a):
    namespace=dict(vars(previous),MATCHER=MATCHER,POLICY=POLICY,prepare_app=prepare_app,
                   build_gallery=build_gallery,validate_feature=validate_feature,verify=verify)
    # Exact same durable prefix, whole-gallery HTTP loop, failure/cancel guards
    # and query order. Only explicit format/initializer/verification hooks vary.
    function=types.FunctionType(previous.work.__code__,namespace,previous.work.__name__)
    return function(a)


def initialize(a):
    root=a.root.resolve();source=a.source.resolve();history=a.history.resolve();model=a.model.resolve()
    if root.exists() or root.is_relative_to(source) or root.is_relative_to(history):raise ValueError('New isolated sibling root required')
    historical=load(history/'protocol.json');rows=[{k:r[k] for k in previous.FIELDS} for r in load(source/'prepared/manifest.json')]
    if len(rows)!=3677 or len({r['sample'] for r in rows})!=3677 or len({r['identity'] for r in rows})!=92:raise ValueError('Incomplete original release')
    assert sum(r['enrollment'] for r in rows)==460
    for ordinal,row in enumerate(rows):
        row['inventory_ordinal']=ordinal
        path=inside(row['original'],source)
        if path.parent.name!='inputs' or not path.is_file() or path.stat().st_size!=row['bytes']:raise ValueError('Raw input absent/size changed')
        if row['enrollment']!=(row['condition']=='F' and row['index']<5):raise ValueError('Fixed F0-F4 selection changed')
    if [{k:r[k] for k in previous.FIELDS} for r in rows]!=[{k:r[k] for k in previous.FIELDS} for r in historical['rows']]:raise ValueError('Original fixed sample/ordering changed')
    reuse=reuse_audit(history)
    assert reuse['decoded_rgb_hash_present']==0
    diagnostic=load(APP/'runtime/union-lossless-fix-20261031/verification-r3/results.json')
    assert diagnostic['complete'] and diagnostic['passed'] and len(diagnostic['fresh_enrollments'])==30 and len(diagnostic['queries'])==8
    boundary=load(APP/'docs/experiments/union-lossless-fix-20261031/next-run-boundary.json')
    for relative,expected in boundary['candidate_source_sha256'].items():
        if file_sha(APP/relative)!=expected:raise ValueError('Capacity-qualified candidate changed: '+relative)
    models={str(model/'compnet-tongji.onnx'):previous.COMP,str((APP.parent/'pklnet/pklnet-keypoints-diagnostics.onnx').resolve()):previous.PKL}
    assert all(file_sha(path)==expected for path,expected in models.items())
    metadata=[source/'prepared/manifest.json',source/'zip-inventory.json',source/'SMPD.download.json',
        source/'evaluation/results.json',source/'evaluation/queries.jsonl',source/'stop-receipt-20261030-144708/receipt.json',
        history/'protocol.json',history/'status.json',history/'inflight.json',history/'gallery.json',
        APP/'runtime/union-lossless-fix-20261031/verification-r3/results.json',
        APP/'docs/experiments/union-lossless-fix-20261031/next-run-boundary.json',
        APP/'docs/protocols/SMPD_PROSPECTIVE_OPTIMIZATION_SPLIT_20261030.json']
    metadata+=sorted((history/'records/query').glob('*.json'))+sorted((history/'records/enrollment').glob('*.json'))
    download=load(source/'SMPD.download.json');assert download['complete'] and download['zip_crc_checked']
    receipt=load(source/'stop-receipt-20261030-144708/receipt.json')
    assert file_sha(source/'evaluation/results.json')==receipt['results_sha256'] and file_sha(source/'evaluation/queries.jsonl')==receipt['queries_jsonl_sha256']
    split=load(metadata[12]);assert split['original_manifest_sha256']==file_sha(source/'prepared/manifest.json')
    files=previous.source_files()+[Path(__file__).resolve(),APP/'tools/supervise_lossless_smpd.py',APP/'tools/supervise_terminal_smpd.py',APP/'tools/report_lossless_smpd.py',model/'metadata.json']
    p=dict(schema=2,run_root=str(root),raw_source_root=str(source),model_root=str(model),created_unix=time.time(),
        matcher=MATCHER,candidate=POLICY,codec=CODEC,storage=SCHEMA,rows=rows,split=split,archive_sha256=download['sha256'],
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=APP,text=True).strip(),
        source_sha256={str(path.resolve()):file_sha(path) for path in files},models_sha256=models,
        metadata_sha256={str(path.resolve()):file_sha(path) for path in metadata},
        dependency_sha256={str(path):file_sha(path) for path in previous.dependency_files()},environment=previous.environment(),
        thresholds=dict(early_distance=.32,early_margin=.08,final_distance=1.,final_margin=0.,rejection=False),
        resources=dict(index_bytes=2*1024**3,prepared_cache_bytes=6*1024**3,start_available_bytes=10*1024**3,
            minimum_available_bytes=1024**3,opencv_threads=1,pklnet_threads=3,compnet_threads=1,http_timeout_seconds=1800),
        reuse_audit=reuse,old70_prefix_compatible=False,old241_prefix_compatible=False,registration_feature_reuse=False,
        registration=dict(people=92,attempts=460,frames_per_identity=5,replacement=False),
        expected_queries=3217,exposure='Seen public development data; not independent generalization or stranger FAR.',
        timing_scope='Windows fresh raw read/hash/PIL EXIF RGB/ROI/features/staged matching and loopback HTTP; decoder RGB hashing included. Camera/external upload excluded; checkpoint/cancel and gallery readiness separate.',
        verification='Byte hashes at epoch start/end and every60 seconds; stat identity/size/mtime/ctime at each frame/query boundary, any change stops; environment versions every60 seconds; installed dependency content hashes at epoch start/end.',
        adapter=dict(preparer_sha256=hashlib.sha256(preparer_source().encode()).hexdigest(),
            http_work_code_sha256=hashlib.sha256(inspect.getsource(previous.work).encode()).hexdigest(),
            changes='v27 magic check + RGB digest observation; new format gallery/feature loader and frozen-lock fast guards. Complete original HTTP work body unchanged.'),
        stop_policy='STOP at record boundaries. Capacity/memory/invariant failure preserves inflight/prefix. No automatic crash restart or scoring change.',
        preflight='Two actual formal queries are retained, then same-version continuation begins at query3; no correctness-based selection.',
        reporting_interval_minutes=20)
    p['run_fingerprint']=digest(p);root.mkdir(parents=True)
    atomic(root/'protocol.json',p,exclusive=True);atomic(root/'reuse-audit.json',reuse,exclusive=True)
    atomic(root/'status.json',dict(state='frozen_not_started',complete=False,run_fingerprint=p['run_fingerprint'],completed_queries=0,enrollment_completed=0,total_queries=3217))
    print(json.dumps(dict(root=str(root),fingerprint=p['run_fingerprint'],feature_reuse=False,registrations=460,queries=3217)),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='mode',required=True)
    init=sub.add_parser('init');init.add_argument('root',type=Path);init.add_argument('--source',required=True,type=Path);init.add_argument('--history',required=True,type=Path);init.add_argument('--model',required=True,type=Path)
    work=sub.add_parser('work');work.add_argument('root',type=Path);work.add_argument('--pause-after-queries',type=int)
    args=parser.parse_args()
    if args.mode=='init':initialize(args)
    else:execution_work(args)
