"""One authorized eight-query v27 geometry/gallery pilot, isolated and non-resumable."""
import argparse
import base64
import collections
import copy
import gc
import hashlib
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
import json
import os
from pathlib import Path
import shutil
import sys
import threading
import time
import xml.etree.ElementTree as ET

# Publication export: private sample bindings moved to an external manifest.
# The archived image runs used their original local drivers; this export has
# synthetic-test coverage only and has NOT been rerun on biometric images.
APP = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(APP), str(APP / 'tools')]
from halfturn_pilot_selection import arguments, bind
ROOT = PARENT = CHILD = GEOMETRY = SELECTION_PATH = None
ENROLL = []
QUERIES = []
CONTROLS = []
CANDIDATE_USER = RECOVERED_ENROLLMENT = None
BINDING = None


def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
def canonical(v):return json.dumps(v,ensure_ascii=True,sort_keys=True,separators=(',',':')).encode()
def digest(v):return hashlib.sha256(canonical(v)).hexdigest()
def save(name,value):
    path=ROOT/name;path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8',newline='\n') as f:
        json.dump(value,f,sort_keys=True,ensure_ascii=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def checkpoint(value):
    path=ROOT/'progress.json';temp=ROOT/'progress.tmp'
    with temp.open('w',encoding='utf-8',newline='\n') as f:
        json.dump(value,f,sort_keys=True,ensure_ascii=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    temp.replace(path)
def original_inventory():
    rows={}
    for root in [PARENT,CHILD]:
        for path in sorted(root.rglob('*')):
            if path.is_file():
                stat=path.stat();rows[str(path)]=dict(bytes=stat.st_size,mtime_ns=stat.st_mtime_ns,
                    ctime_ns=stat.st_ctime_ns,inode=stat.st_ino,sha256=sha(path))
    return rows
def original_stats_same(before):
    paths={str(p) for root in [PARENT,CHILD] for p in root.rglob('*') if p.is_file()}
    if paths!=set(before):return False
    return all((lambda s:(s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_ino)==
                (r['bytes'],r['mtime_ns'],r['ctime_ns'],r['inode']))(Path(p).stat()) for p,r in before.items())
def resources(startup=False):
    import psutil
    own=os.getpid();bad=[]
    for proc in psutil.process_iter(['pid','cmdline']):
        try:
            cmd=' '.join(proc.info['cmdline'] or [])
            if proc.pid!=own and any(x in cmd for x in ['run_smpd_continuation.py','run_lossless_smpd.py','supervise_lossless_smpd.py']):bad.append(proc.pid)
        except (psutil.AccessDenied,psutil.NoSuchProcess):pass
    available=psutil.virtual_memory().available;rss=psutil.Process().memory_info().rss
    if bad:raise RuntimeError('Original evaluation worker detected: '+str(bad))
    if available<(12 if startup else 2)*1024**3:raise MemoryError('Predeclared available-memory boundary failed')
    if rss>14*1024**3:raise MemoryError('Predeclared pilot RSS boundary exceeded')
    if not (CHILD/'STOP').is_file() or (CHILD/'inflight.json').exists() or load(CHILD/'status.json')['state']!='paused_STOP':
        raise RuntimeError('Original frozen pause boundary changed')
    return dict(available_bytes=available,rss_bytes=rss,original_workers=bad)
def validate_selection(samples):
    if samples!=QUERIES or len(set(samples))!=8:raise ValueError('Fixed query selection changed')
    if any(int(s.split('-')[1])%5==0 for s in samples):raise ValueError('Protected query selected')
def control_comparison(current,baseline,users):
    old=baseline['payload'];new=current
    return dict(correct_preserved=new.get('outcome')=='correct',
        route_unchanged=new.get('result',{}).get('recognition_route')==old['result'].get('recognition_route'),
        original86_scores_exact={u:new.get('scores',{}).get(u) for u in users}==old['scores'],
        original_roi_exact=new.get('primary_historical_exact',False) and new.get('selected_primary_verbatim',False))
def verify_locks(p):
    if p['private_binding'] != BINDING:
        raise ValueError('Private selection or run directories changed')
    for field in ['sources_sha256','models_sha256','dependencies_sha256','metadata_sha256']:
        for path,h in p[field].items():
            if sha(path)!=h:raise ValueError('Frozen lock changed: '+path)
    for row in p['rows']:
        if sha(row['original'])!=row['sha256']:raise ValueError('Original image changed: '+row['sample'])
    if Path(sys.executable).resolve()!=Path(p['executable']).resolve():raise ValueError('Wrong CPU environment')


def prepare():
    if (ROOT/'protocol.json').exists():raise ValueError('Already sealed; no reselection')
    from report_smpd_continuation import snapshot
    state=snapshot(CHILD);assert state['completed_queries']==1239
    frozen=load(CHILD/'protocol.json');geometry=load(GEOMETRY/'results.json')
    assert geometry['geometry_pilot_pass'] and geometry['complete']
    validate_selection(QUERIES);resources(startup=True)
    record_paths={}
    for folder in [PARENT/'records/enrollment',PARENT/'records/query',CHILD/'records/query']:
        for path in sorted(folder.glob('*.json')):
            r=load(path)
            if r['sample'] in ENROLL+QUERIES:record_paths[r['sample']]=path
    assert set(record_paths)==set(ENROLL+QUERIES)
    baseline={s:load(record_paths[s]) for s in ENROLL+QUERIES}
    assert collections.Counter(baseline[s]['payload']['outcome'] for s in QUERIES)==dict(correct=2,wrong_identity_accepted=5,processing_failure=1)
    assert all(baseline[s]['payload']['outcome']=='wrong_identity_accepted' for s in QUERIES[:5])
    assert all(baseline[s]['payload']['outcome']=='correct' for s in CONTROLS)
    assert baseline[QUERIES[-1]]['payload']['outcome']=='processing_failure'
    rows=[next(r for r in frozen['rows'] if r['sample']==s) for s in ENROLL+QUERIES]
    identity=rows[0]['identity']
    assert all(r['identity']==identity for r in rows[:10])
    assert [r['index'] for r in rows[:5]]==list(range(5)) and all(r['enrollment'] for r in rows[:5])
    assert not any(r['enrollment'] for r in rows[5:])
    assert identity.replace(':','-')==CANDIDATE_USER
    assert [s for s in ENROLL if not baseline[s]['payload']['ok']]==[RECOVERED_ENROLLMENT]
    assert all(int(r['subject'])%5 for r in rows)
    users=[e['user'] for e in load(CHILD/'gallery.json')['enrollments'] if e['registered']]
    assert len(users)==86 and CANDIDATE_USER not in users
    template_root=CHILD/'evaluation/runtime/demo_templates'
    templates={str(p):sha(p) for p in sorted(template_root.iterdir()) if p.is_file()}
    assert len(templates)==86
    source=dict(frozen['source_sha256'])
    for path in [Path(__file__),APP/'tools/halfturn_pilot_selection.py',APP/'tests/test_halfturn_identification_pilot.py',APP/'tools/halfturn_roi_recovery.py']:
        source[str(path)]=sha(path)
    model=dict(frozen['models_sha256'])
    for name in ['net_params_500.pth','pklnet-keypoints-diagnostics.json']:
        path=APP.parent/'pklnet'/name;model[str(path)]=sha(path)
    metadata=[SELECTION_PATH,PARENT/'protocol.json',CHILD/'protocol.json',CHILD/'gallery.json',CHILD/'STOP',CHILD/'status.json',
              GEOMETRY/'protocol.json',GEOMETRY/'results.json',*record_paths.values()]
    p=dict(schema=1,private_binding=BINDING,created_unix=time.time(),scope='Single fixed eight-query development v27 OOB recovery/gallery pilot; no full evaluation, no speed/adoption/generalization claim',
        executable=frozen['environment']['executable'],environment=frozen['environment'],model_root=frozen['model_root'],
        sources_sha256=source,models_sha256=model,dependencies_sha256=frozen['dependency_sha256'],
        metadata_sha256={str(x):sha(x) for x in metadata},source_templates_sha256=templates,
        baseline_records=baseline,rows=rows,enrollment_samples=ENROLL,query_samples=QUERIES,control_samples=CONTROLS,
        inherited_users=users,candidate_user=CANDIDATE_USER,expected_gallery=87,
        inherited_parent_fingerprint=state['version_boundary']['parent_run_fingerprint'],inherited_child_fingerprint=frozen['run_fingerprint'],
        policy=dict(matcher='FastCCCompNetAlternateROI-v27-lossless-experimental',magic=2801166,codec='union-lossless-variable-v2',
            storage='union-five-frame-npz-v2',retained_fastcc=True,terminal_rf='original-confident-paths-terminal-rf-v1',
            roi_candidate='Existing unmodified HalfTurnROIRecovery; original valid outputs pass verbatim; only OOB gets one 180-degree retry',
            roi_policy_details=load(GEOMETRY/'protocol.json')['mechanism'],thresholds=frozen['thresholds'],
            allowed_differences=['HalfTurnROIRecovery wraps localizer in independent enrollment and query runtimes',
              'The target original five frames freshly extracted; only after all5 success add one new gallery identity',
              'New candidate metadata binds new protocol fingerprint; all inherited86 template bytes preserved'],
            unchanged='All models, image bytes/labels, five-frame rule, stages/scoring, complete gallery, thresholds, rejection-off, runtime CPU dependencies'),
        limits=dict(start_free_bytes=12*1024**3,boundary_free_bytes=2*1024**3,max_rss_bytes=14*1024**3,
            max_http_seconds=1800,max_query_attempts=8,max_enrollment_attempts=5,
            resource_behavior='Check at startup and each frame/query boundary; resource/provenance/error stops future attempts; no retry. Existing feature/index/cache capacity guards retained.'),
        gates=['All five unchanged target frames succeed; no replacement or partial registration',
            'All originally valid target enrollment features exactly equal old arrays and codec',
            'All inherited86 template bytes and five-frame payloads unchanged; candidate metadata is new',
            'Actual LosslessUnionMatcher magic/CODEC/retained/terminalRF/thresholds verified',
            'One complete87 gallery/index prepared; every successful query scores all87',
            'Two old-correct controls remain correct with original effective ROI, route and86-projection scores exact',
            'The negative control remains same ROI processing failure with no recovery retry',
            'At least one target wrong-to-correct; none of the five target queries becomes a processing failure',
            'No token confirmation/payments; every issued token canceled; zero transactions/balance changes',
            'Original parents/chains/all file bytes/STOP unchanged at end'],
        timing='Historical baseline not rerun. Record candidate HTTP, enrollment and ready costs separately; no comparative speed claim.',
        no_retry=True,no_resume=True,no_threshold_scan=True,recognition_full168_not_authorized=True,promotion=False)
    verify_locks(p)
    print('Hashing all original parent/child files before the isolated pilot',flush=True)
    before=original_inventory();save('original-bytes-before.json',before)
    p['original_inventory_sha256']=sha(ROOT/'original-bytes-before.json')
    p['run_fingerprint']=digest(p);save('protocol.json',p)
    print(json.dumps(dict(prepared=True,fingerprint=p['run_fingerprint'],queries=QUERIES,original_files=len(before))),flush=True)


def attach_geometry(camera):
    import numpy as np
    from halfturn_roi_recovery import HalfTurnROIRecovery
    base=camera.tracker.extractor
    wrapper=HalfTurnROIRecovery(base)
    call=wrapper.extract
    def observed(image,*,side=128):
        result=call(image,side=side);raw,quad,details=result
        camera.audit.setdefault('selected_rois',[]).append(dict(quad=quad.tolist(),details=copy.deepcopy(details),
            raw_sha256=hashlib.sha256(raw.tobytes()).hexdigest(),trace=copy.deepcopy(wrapper.last_trace),
            primary_verbatim=wrapper.last_trace['reason'] in ('valid_primary_passthrough','failure_outside_candidate_scope')))
        return result
    wrapper.extract=observed;camera.tracker.extractor=wrapper
    return wrapper


def assert_app(app,camera,p):
    import cv2
    from lossless_union_matcher import LosslessUnionMatcher
    from lossless_template_store import LosslessTemplateStore,SCHEMA
    from union_lossless_codec import CODEC
    a=app.demo_algorithm
    assert type(a) is LosslessUnionMatcher and a.name==p['policy']['matcher'] and a.magic==2801166
    assert a.template_codec==CODEC==p['policy']['codec'] and a.template_storage_schema==SCHEMA
    assert isinstance(app.demo.store,LosslessTemplateStore)
    assert a._retain_fastcc_evidence_pilot and a._terminal_rf_installed
    assert app.demo.gallery.threshold==1.0 and app.demo.gallery.min_margin==0.0 and app.demo.gallery.acceptance_policy is None
    assert cv2.getNumThreads()==1 and camera.tracker.extractor.threads==3
    assert camera.tracker.extractor._session.get_providers()==['CPUExecutionProvider']
    return dict(class_name=type(a).__module__+'.'+type(a).__name__,name=a.name,magic=a.magic,codec=CODEC,storage=SCHEMA,
                retained=True,terminal_rf=True,threshold=1.0,margin=0.0,rejection=False,
                roi_base_class=type(camera.tracker.extractor).__module__+'.'+type(camera.tracker.extractor).__name__,
                roi_policy=camera.tracker.extractor.policy,providers=camera.tracker.extractor._session.get_providers())


def run():
    p=load(ROOT/'protocol.json')
    if digest({k:v for k,v in p.items() if k!='run_fingerprint'})!=p['run_fingerprint']:raise ValueError('Protocol changed')
    validate_selection(p['query_samples']);verify_locks(p);start_resources=resources(startup=True)
    cases=list(ET.parse(ROOT/'fixtures.junit.xml').getroot().iter('testcase'))
    if len(cases)!=5 or any(list(c) for c in cases):raise ValueError('Driver fixtures did not pass')
    before=load(ROOT/'original-bytes-before.json')
    if sha(ROOT/'original-bytes-before.json')!=p['original_inventory_sha256'] or not original_stats_same(before):raise ValueError('Original boundary changed')
    save('RUN_STARTED.json',dict(pid=os.getpid(),time=time.time(),protocol_sha256=sha(ROOT/'protocol.json'),resources=start_resources))
    import numpy as np
    import run_lossless_smpd as v27
    from run_terminal_smpd import clean
    from union_lossless_codec import CODEC,decode
    from lossless_template_store import LosslessTemplateStore
    from payment import PaymentService
    from pklnet_roi import ROI_GEOMETRY_VERSION
    from report_smpd_continuation import snapshot
    rows={r['sample']:r for r in p['rows']};baseline=p['baseline_records']
    report=dict(protocol_fingerprint=p['run_fingerprint'],complete=False,started_unix=time.time(),enrollments=[],queries=[],
        inherited_gallery=86,candidate_gallery=None,promotion=False,speed_claim=False,scope=p['scope'])
    app=None;server=None;server_thread=None
    try:
        runtime=ROOT/'enrollment/runtime';runtime.mkdir(parents=True,exist_ok=True)
        app,camera,ready=v27.prepare_app(runtime,p,gallery=False)
        report['enrollment_ready']=ready;report['actual_enrollment']=assert_app(app,camera,p)
        attach_geometry(camera);frames=[]
        checkpoint(report)
        for sample in ENROLL:
            resources();verify_locks(p);camera.audit={};camera.select([rows[sample]]);tick=time.perf_counter()
            report['active_stage']='enrollment';report['active_sample']=sample;checkpoint(report)
            save('enrollment-attempts/'+sample+'.json',dict(sample=sample,started_unix=time.time()))
            feature,roi_image,source=app.capture_demo_feature(enrollment=True)
            elapsed=(time.perf_counter()-tick)*1000
            if camera.audit.get('fatal'):raise RuntimeError(camera.audit['fatal'])
            assert decode(feature,decode_native=False).storage_codec==CODEC
            expected=baseline[sample]['payload'];assert camera.audit['decoded_rgb_sha256']==expected['capture']['decoded_rgb_sha256']
            equal=None
            if expected['ok']:
                if sha(expected['feature'])!=expected['feature_sha256']:raise ValueError('Old enrollment container changed')
                with np.load(expected['feature'],allow_pickle=False) as archive:old=archive['feature']
                equal=np.array_equal(feature,old) and decode(old,decode_native=False).storage_codec==CODEC
                if not equal:raise ValueError('Valid primary enrollment feature changed: '+sample)
            feature_path=ROOT/'features'/(sample+'.npz');feature_path.parent.mkdir(exist_ok=True)
            with feature_path.open('xb') as f:np.savez_compressed(f,feature=feature)
            roi_path=ROOT/'rois'/('enroll-'+sample+'.png');roi_path.parent.mkdir(exist_ok=True);roi_path.write_bytes(base64.b64decode(roi_image))
            item=dict(sample=sample,ok=True,ms=elapsed,feature_path=str(feature_path),feature_file_sha256=sha(feature_path),
                feature_array_sha256=hashlib.sha256(feature.tobytes()).hexdigest(),codec=CODEC,old_feature_exact=equal,
                fresh_candidate_provenance=p['run_fingerprint'],capture=clean(camera.audit),roi_source=source)
            item['record_sha256']=digest(item);save('enrollment-records/'+sample+'.json',item)
            report['enrollments'].append(item);frames.append(feature);checkpoint(report)
            print(json.dumps(dict(enrollment=sample,ok=True,old_feature_exact=equal,ms=elapsed)),flush=True)
        assert len(frames)==5 and all(r['old_feature_exact'] is True for r in report['enrollments'] if r['sample']!=RECOVERED_ENROLLMENT)
        app.demo_algorithm.close();app=None;gc.collect()
        runtime=ROOT/'evaluation/runtime';templates=runtime/'demo_templates';templates.mkdir(parents=True,exist_ok=False)
        for source,h in p['source_templates_sha256'].items():
            target=templates/Path(source).name
            with Path(source).open('rb') as src,target.open('xb') as dst:shutil.copyfileobj(src,dst,1024*1024)
            if sha(target)!=h:raise ValueError('Inherited template copy mismatch')
        store=LosslessTemplateStore(templates)
        meta=dict(user=CANDIDATE_USER,display_name='EVAL '+CANDIDATE_USER,algorithm=p['policy']['matcher'],capture_profile='noir-ir',
            samples=5,roi_geometry=ROI_GEOMETRY_VERSION,roi_sources=['pklnet']*5,run_fingerprint=p['run_fingerprint'],
            candidate_fingerprint=p['run_fingerprint'],recovery_policy='out-of-bounds-halfturn-recovery-pilot-v1',
            source='Five fresh original target frames; isolated candidate geometry, no replacement; original86 byte copies',
            frame_record_sha256=[r['record_sha256'] for r in report['enrollments']],
            original_frame_samples=ENROLL,inherited_gallery_fingerprint=p['inherited_child_fingerprint'])
        store.save(CANDIDATE_USER,frames,meta);del frames;gc.collect()
        expected_users=set(p['inherited_users'])|{CANDIDATE_USER}
        assert set(store.list_users())==expected_users
        payments=PaymentService(runtime/'demo_payment.sqlite3')
        for user in sorted(expected_users):payments.create_account(user,'EVAL '+user.replace('-',':',2),10000)
        assert payments.transaction_count()==0
        save('candidate-gallery.json',dict(registered=87,users=sorted(expected_users),new_identity_metadata=meta,
            files_sha256={path.name:sha(path) for path in sorted(templates.iterdir()) if path.is_file()}))
        report['candidate_gallery']=87
        # prepare_app writes only these explicitly new ancestor/status/phase paths.
        (ROOT/'query-phases').mkdir(exist_ok=True);save('status.json',dict(epoch='fixed-eight-queries',state='gallery_prepare',run_fingerprint=p['run_fingerprint']))
        resources(startup=True);verify_locks(p);tick=time.perf_counter()
        report['active_stage']='complete87_gallery_prepare';report['active_sample']=None;checkpoint(report)
        app,camera,ready=v27.prepare_app(runtime,p,gallery=True)
        report['full_gallery_ready']=ready;report['full_gallery_prepare_wall_ms']=(time.perf_counter()-tick)*1000
        report['actual_query']=assert_app(app,camera,p);attach_geometry(camera)
        assert len(app.demo.gallery._prepared_cache)==87 and set(app.demo.gallery._prepared_cache)==expected_users
        assert set(app.demo.store.list_users())==expected_users
        report['ready_cache_count']=len(app.demo.gallery._prepared_cache)
        numeric={};original_score=app.demo_algorithm.score_gallery
        def scoring(probe,groups):
            if set(groups)!=expected_users:raise ValueError('Complete87 gallery missing during scoring')
            value=original_score(probe,groups)
            if set(value)!=expected_users:raise ValueError('Complete87 scores missing')
            numeric.update(value);return value
        app.demo_algorithm.score_gallery=scoring
        from palm_app import debug_ui
        base_handler=debug_ui.make_handler(app)
        class Handler(base_handler):
            def log_message(self,*args):pass
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        server_thread=threading.Thread(target=server.serve_forever,daemon=True);server_thread.start()
        def request(route,payload):
            tick=time.perf_counter();connection=HTTPConnection(*server.server_address,timeout=p['limits']['max_http_seconds'])
            try:
                connection.request('POST',route,json.dumps(payload),{'Content-Type':'application/json'})
                response=connection.getresponse();value=json.loads(response.read())
                return response.status,value,(time.perf_counter()-tick)*1000
            finally:connection.close()
        checkpoint(report);print(json.dumps(dict(gallery_ready=87,ready_ms=report['full_gallery_prepare_wall_ms'])),flush=True)
        for index,sample in enumerate(QUERIES):
            resources();verify_locks(p)
            if not original_stats_same(before):raise ValueError('Original parent/child changed')
            camera.audit={};camera.select([rows[sample]]);numeric.clear();app.demo_algorithm._terminal_rf_trace=None
            report['active_stage']='query';report['active_sample']=sample;checkpoint(report)
            save('query-attempts/'+str(index)+'.json',dict(sample=sample,started_unix=time.time()))
            code,response,ms=request('/api/demo/identify',{})
            trace=clean(app.demo_algorithm._terminal_rf_trace);capture=clean(camera.audit)
            token=response.get('token');cancel=None
            if token:
                cc,cr,cm=request('/api/demo/cancel',dict(token=token));cancel=dict(http_status=cc,result=cr,ms=cm)
                if cc!=200 or app.demo.pending:raise ValueError('Token cancellation failed')
            if response.get('roi_image'):
                roi_path=ROOT/'rois'/('query-'+sample+'.png');roi_path.write_bytes(base64.b64decode(response['roi_image']))
            if app.demo.payments.transaction_count()!=0 or any(app.demo.payments.balance_for(u)!=10000 for u in expected_users):raise ValueError('Unexpected payment state')
            if capture.get('fatal'):raise RuntimeError(capture['fatal'])
            if code==200 and (not trace or set(numeric)!=expected_users or trace['unknown_calls']):raise ValueError('Incomplete query scoring provenance')
            historical=baseline[sample]['payload'];primary=capture['localizations'][0];selected=capture['selected_rois'][0]
            assert capture['decoded_rgb_sha256']==historical['capture']['decoded_rgb_sha256']
            item=dict(sample=sample,sequence=index,identity=rows[sample]['identity'],http_status=code,ms=ms,
                result={k:v for k,v in response.items() if k not in ['token','roi_image','expires_at']},scores=clean(numeric),
                terminal_rf=trace,capture=capture,cancellation=cancel,baseline_record_sha256=baseline[sample]['record_sha256'],
                primary_historical_exact=(primary['quad']==historical['capture']['localizations'][0]['quad'] and primary['details']==historical['capture']['localizations'][0]['details']),
                selected_primary_verbatim=selected['primary_verbatim'])
            item['outcome']=v27.previous.outcome(item)
            if sample in CONTROLS:item['control_comparison']=control_comparison(item,baseline[sample],p['inherited_users'])
            if sample==QUERIES[-1]:item['negative_control']=dict(same_failure=item['outcome']=='processing_failure' and item['http_status']==historical['http_status'],
                same_primary=item['primary_historical_exact'] and item['selected_primary_verbatim'],zero_retry=not selected['trace']['retry'])
            item['record_sha256']=digest(item);save('query-records/'+sample+'.json',item);report['queries'].append(item);checkpoint(report)
            print(json.dumps(dict(query=sample,outcome=item['outcome'],ms=ms,route=item['result'].get('recognition_route'),control=item.get('control_comparison'))),flush=True)
        controls=[r for r in report['queries'] if r['sample'] in CONTROLS];targets=report['queries'][:5];negative=report['queries'][-1]
        gates=dict(all8_complete=len(report['queries'])==8,all5_registration_success=len(report['enrollments'])==5,
            all4_valid_registration_features_exact=all(r['old_feature_exact'] for r in report['enrollments'] if r['sample']!=RECOVERED_ENROLLMENT),
            complete_gallery87=report['ready_cache_count']==87,
            controls_all_exact=all(all(r['control_comparison'].values()) for r in controls),
            negative_unchanged=all(negative['negative_control'].values()),
            target_genuine_correction=any(r['outcome']=='correct' for r in targets),
            target_no_new_processing_failure=all(r['outcome']!='processing_failure' for r in targets),
            no_new_wrong=not any(r['outcome']=='wrong_identity_accepted' and baseline[r['sample']]['payload']['outcome']!='wrong_identity_accepted' for r in report['queries']),
            zero_transactions=app.demo.payments.transaction_count()==0,
            inherited86_copies_byte_exact=all(sha(templates/Path(source).name)==h for source,h in p['source_templates_sha256'].items()))
        report.update(complete=True,gates=gates,pilot_pass=all(gates.values()),
            outcomes=dict(collections.Counter(r['outcome'] for r in report['queries'])),active_stage='completed',active_sample=None)
    except Exception as error:
        report.update(pilot_pass=False,failure=type(error).__name__+': '+str(error))
        # Preserve failed attempts; no retry, replacement or implicit continuation.
        print(report['failure'],flush=True)
    finally:
        if server is not None:server.shutdown();server.server_close()
        if server_thread is not None:server_thread.join()
        if app is not None:app.demo_algorithm.close()
        gc.collect()
        try:
            verify_locks(p)
            print('Hashing all original parent/child files after the isolated pilot',flush=True)
            after=original_inventory();same=before==after
            report['original_preservation']=dict(all_file_bytes_and_stats_unchanged=same,files=len(before),
                changed_paths=sorted(k for k in set(before)|set(after) if before.get(k)!=after.get(k)))
            snap=snapshot(CHILD);report['original_chain_after']=dict(completed_queries=snap['completed_queries'],journal_tip=snap['journal_tip'],state=snap['status']['state'],stop_exists=(CHILD/'STOP').exists())
            if not same or snap['completed_queries']!=1239:report['pilot_pass']=False
        except Exception as error:
            report['preservation_error']=type(error).__name__+': '+str(error);report['pilot_pass']=False
        report['ended_unix']=time.time();save('results.json',report);checkpoint(report)
        print(json.dumps({k:report.get(k) for k in ['complete','pilot_pass','outcomes','gates','failure','original_preservation','preservation_error']}),flush=True)
    return 0 if report.get('pilot_pass') else 2


if __name__=='__main__':
    parser=arguments(argparse.ArgumentParser(description=__doc__), 'identification')
    args=parser.parse_args()
    globals().update(bind('identification', args))
    if args.mode=='prepare':prepare()
    else:sys.exit(run())
