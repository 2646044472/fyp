"""Once-only terminal-RF SMPD evaluation: new features, one gallery, durable prefix.

No production imports until an explicit work command. Init only freezes metadata
and hashes; work pauses on STOP or an operational query budget. Completed queries
are never repeated. Public data are development-exposed, not blind validation.
"""
import argparse
import base64
import gc
import importlib.metadata
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import threading
import time
import uuid

from smpd_run_journal import (Journal, atomic, begin_attempt, canonical, digest,
                             file_sha, inside, load, recover_inflight, run_lock)

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP))
MATCHER = 'FastCCCompNetAlternateROI-v26-experimental'
POLICY = 'original-confident-paths-terminal-rf-v1'
FIELDS = ('sample', 'identity', 'subject', 'hand', 'condition', 'index', 'member',
          'original', 'sha256', 'bytes', 'enrollment')
COMP = 'b513e614a8b1a4448ef58c1b7f288f760fc991ce31d0a35079b4f9226146d1ea'
PKL = 'bf477f1778f03ccc203b64dd0c84d418c9bb22839a23ba923f479ab991aa067f'


def clean(value):
    if hasattr(value, 'tolist'):
        return value.tolist()
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [clean(v) for v in value]
    return value


def source_files():
    paths = list(APP.glob('*.py')) + list((APP/'palm_app').rglob('*.py'))
    for name in ('run_terminal_smpd.py', 'smpd_run_journal.py', 'report_terminal_smpd.py',
                 'evaluate_raw_smpd.py', 'replay_pi_pipeline.py', 'terminal_rf_evidence.py',
                 'fastcc_valid_support.py', 'retained_evidence_pilot.py'):
        paths.append(APP/'tools'/name)
    # Include the actual dynamically imported baseline package and ROI sampler.
    from palm_app.common import DEFAULT_BASELINE
    paths += list((Path(DEFAULT_BASELINE)/'palmprint').rglob('*.py'))
    paths.append(APP.parent/'pklnet/roiExtractor.py')
    return sorted(set(p.resolve() for p in paths))


def environment():
    return dict(python=sys.version, executable=str(Path(sys.executable).resolve()),
                platform=platform.platform(), machine=platform.machine(),
                packages=sorted([d.metadata['Name'], d.version] for d in importlib.metadata.distributions()),
                relevant_environment={k: v for k, v in os.environ.items()
                    if k.startswith(('PALM_', 'OMP_', 'MKL_', 'OPENBLAS_', 'ORT_'))
                    and k != 'PALM_COMPNET_MODEL_ROOT'})


def dependency_files():
    """Hash installed inference packages, binaries and distribution metadata."""
    paths = {Path(sys.executable).resolve()}
    names = ('numpy', 'scipy', 'pillow', 'onnxruntime', 'opencv-python',
             'opencv-python-headless', 'scikit-image', 'psutil')
    for name in names:
        try:
            dist = importlib.metadata.distribution(name)
        except importlib.metadata.PackageNotFoundError:
            continue
        for entry in dist.files or []:
            path = Path(dist.locate_file(entry)).resolve()
            if path.is_file() and path.suffix.lower() not in ('.pyc', '.pyo'):
                paths.add(path)
    # Runtime DLL and stdlib archive participate in Python execution too.
    for root in {Path(sys.base_prefix), Path(sys.executable).parent}:
        paths.update(root.glob('python*.dll')); paths.update(root.glob('python*.zip'))
    return sorted(paths)


def verify_metadata(p):
    for path, expected in p['metadata_sha256'].items():
        if file_sha(path) != expected:
            raise ValueError('Frozen source metadata changed: ' + path)


def verify(p, *, dependencies=False):
    if digest({k: v for k, v in p.items() if k != 'run_fingerprint'}) != p['run_fingerprint']:
        raise ValueError('Protocol fingerprint mismatch')
    if environment() != p['environment']:
        raise ValueError('Execution environment changed')
    groups = ['source_sha256', 'models_sha256']
    if dependencies:
        groups.append('dependency_sha256')
    for group in groups:
        for path, expected in p[group].items():
            if file_sha(path) != expected:
                raise ValueError('Frozen execution file changed: ' + path)
    verify_metadata(p)


def initialize_protocol(a):
    from evaluate_raw_smpd import verify as verify_old
    source, root, model = a.source.resolve(), a.root.resolve(), a.model.resolve()
    if root.exists() or root.is_relative_to(source) or source.is_relative_to(root):
        raise ValueError('Candidate needs a new sibling root')
    old_protocol = load(source/'protocol.json'); verify_old(old_protocol)
    old_manifest = source/'prepared/manifest.json'
    boundary = load(APP/'docs/experiments/terminal-rf-smpd-boundary-20261030/summary.json')
    if file_sha(old_manifest) != boundary['feature_protocol']['prepared_manifest_sha256']:
        raise ValueError('Original manifest changed')
    rows = [{k: r[k] for k in FIELDS} for r in load(old_manifest)]
    # Stable original prefix order; retain the existing ordinal as a tie breaker.
    for ordinal, row in enumerate(rows):
        row['inventory_ordinal'] = ordinal
        original = inside(row['original'], source)
        # Historical parallel extraction kept originals under both the root
        # inputs/ and prepare-worker-N/inputs/. The immutable manifest fixes the
        # exact source path; all must still be raw JPEGs inside the source root.
        if original.parent.name != 'inputs' or original.suffix.lower() != '.jpg' or not original.is_file():
            raise ValueError('Raw original absent or outside source inputs')
        if original.stat().st_size != row['bytes']:
            raise ValueError('Original size mismatch')
    if len(rows) != 3677 or len({r['sample'] for r in rows}) != 3677:
        raise ValueError('Invalid complete release')
    if len({r['identity'] for r in rows}) != 92 or sum(r['enrollment'] for r in rows) != 460:
        raise ValueError('Invalid fixed gallery selection')
    declared = {r['member']: r for r in old_protocol['samples']}
    for row in rows:
        if any(row[k] != declared[row['member']][k] for k in ('identity','subject','condition','index','enrollment')):
            raise ValueError('Release protocol/manifest mismatch')
        if row['enrollment'] != (row['condition'] == 'F' and row['index'] < 5):
            raise ValueError('Not fixed F0-F4')
    split_path = APP/'docs/protocols/SMPD_PROSPECTIVE_OPTIMIZATION_SPLIT_20261030.json'
    split = load(split_path)
    if split['original_manifest_sha256'] != file_sha(old_manifest):
        raise ValueError('Split binding mismatch')
    if sorted(split['development_subjects'] + split['reserved_subjects']) != sorted({r['subject'] for r in rows}):
        raise ValueError('Invalid prospective split')
    reference_path = APP/'runtime/terminal-rf-full168-20261030/evaluation/results.json'
    reference = load(reference_path)
    from evaluate_raw_smpd import source_sha
    if not reference['complete'] or not reference['local_candidate_pass']:
        raise ValueError('Candidate device regression not qualified')
    for field, name in (('candidate_sha256','terminal_rf_evidence.py'),
                        ('kernel_sha256','fastcc_valid_support.py'),
                        ('helper_sha256','retained_evidence_pilot.py')):
        if source_sha(APP/'tools'/name) != reference[field]:
            raise ValueError('Candidate differs from device regression')
    models = {str(model/'compnet-tongji.onnx'): COMP,
              str((APP.parent/'pklnet/pklnet-keypoints-diagnostics.onnx').resolve()): PKL}
    if any(file_sha(path) != expected for path, expected in models.items()):
        raise ValueError('Model mismatch')
    download = load(source/'SMPD.download.json')
    if not download['complete'] or not download['zip_crc_checked']:
        raise ValueError('Historical archive verification absent')
    metadata_paths = [old_manifest, source/'protocol.json', source/'SMPD.download.json',
        source/'zip-inventory.json', source/'evaluation/results.json', source/'evaluation/queries.jsonl',
        source/'stop-receipt-20261030-144708/receipt.json', split_path, reference_path,
        APP/'docs/experiments/terminal-rf-smpd-boundary-20261030/summary.json']
    receipt = load(metadata_paths[6])
    if (file_sha(source/'evaluation/results.json') != receipt['results_sha256'] or
            file_sha(source/'evaluation/queries.jsonl') != receipt['queries_jsonl_sha256']):
        raise ValueError('Old241 checkpoint changed')
    source_paths = source_files() + [model/'metadata.json']
    p = dict(schema=1, candidate=POLICY, matcher=MATCHER, created_unix=time.time(),
        run_root=str(root), raw_source_root=str(source), model_root=str(model), rows=rows,
        thresholds=dict(early_distance=.32, early_margin=.08, final_distance=1., final_margin=0., rejection=False),
        source_sha256={str(p): file_sha(p) for p in source_paths},
        models_sha256=models, dependency_sha256={str(p): file_sha(p) for p in dependency_files()},
        metadata_sha256={str(p.resolve()): file_sha(p) for p in metadata_paths},
        environment=environment(), archive_sha256=download['sha256'],
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'], cwd=APP, text=True).strip(),
        source_lock='Exact bytes; source/model verification every epoch and query boundary; dependencies every epoch/end.',
        split=split, registration=dict(frames=5, identities=92, selected_files=460, replacement=False),
        resources=dict(index_bytes=2*1024**3, prepared_cache_bytes=6*1024**3,
                       start_available_bytes=10*1024**3, minimum_available_bytes=1024**3,
                       opencv_threads=1, pklnet_threads=3, compnet_threads=1, http_timeout_seconds=1800),
        timing_scope='Windows original read/hash/JPEG+EXIF/ROI/features/matching/loopback HTTP. No camera or external upload. Record/report I/O and token cancellation excluded and separately timed. Cold/gallery start separate.',
        order='Stable (subject,index) sort of frozen inventory order; no correctness/outcome filtering.',
        duplicate_policy='All files primary. Secondary lexicographically first sample per exact-byte hash; separate enrollment overlap.',
        stop_policy='STOP file at complete-record boundaries; same-version prefix resume; preserve inflight attempts. No accuracy-based stop or retries of completed failures.',
        unknown_policy='Natural registration-failure cohort diagnostic only; no new person-removal experiment or FAR claim.',
        exposure='Seen public development data. Prospective split is not independent blind validation. Pretraining exposure unknown.',
        old_feature_reuse=False, old_score_reuse=False, independent_run=True,
        preflight='First two formal queries retained as exact prefix; operational pause, not candidate selection.')
    p['run_fingerprint'] = digest(p)
    root.mkdir(parents=True)
    atomic(root/'protocol.json', p, exclusive=True)
    atomic(root/'status.json', dict(state='frozen_not_started', run_fingerprint=p['run_fingerprint'],
                                   completed_queries=0, total_queries=3217, complete=False))
    print(json.dumps(dict(root=str(root), fingerprint=p['run_fingerprint'], originals=len(rows),
                          queries=3217, dependency_files=len(p['dependency_sha256']))), flush=True)


def memory():
    import psutil
    process = psutil.Process()
    info = process.memory_info()
    return dict(rss_bytes=info.rss, peak_rss_bytes=getattr(info,'peak_wset',info.rss),
                private_bytes=getattr(info,'private',None), available_bytes=psutil.virtual_memory().available,
                process_cpu_s=sum(process.cpu_times()[:2]))


def resources_ok(p, *, startup=False):
    state = memory()
    limit = p['resources']['start_available_bytes' if startup else 'minimum_available_bytes']
    if state['available_bytes'] < limit:
        raise MemoryError('Insufficient host memory; keep complete gallery and checkpoint unchanged')
    return state


def prepare_app(root, p, *, gallery):
    import numpy as np
    import cv2
    from PIL import Image, ImageOps
    from evaluate_raw_smpd import install_windows_capacity, ExifReplay
    from retained_evidence_pilot import install_retained_evidence_pilot
    from pklnet_roi import PKLNetROI
    from palm_app import debug_ui
    from terminal_rf_evidence import install
    started = time.perf_counter()
    os.environ['PALM_COMPNET_MODEL_ROOT']=p['model_root'];cv2.setNumThreads(1)
    if gallery: install_windows_capacity()
    # The frozen hook modifies a class method process-wide. Install once,
    # including when one epoch extracts enrollments then opens its full gallery.
    if not getattr(prepare_app,'retained_installed',False):
        install_retained_evidence_pilot();prepare_app.retained_installed=True
    engine=PKLNetROI(threads=3);engine._ensure_loaded()
    engine._session.run(['keypoints','heatmap_keypoints','fc_keypoints'],{'image':np.zeros((1,3,400,300),np.float32)})
    camera=ExifReplay(False,engine);debug_ui.common.RUNTIME=root
    app=debug_ui.App(camera,demo_matcher=MATCHER);app.demo_algorithm._retain_fastcc_evidence_pilot=True
    inner_startup=(time.perf_counter()-started)*1000
    install(app.demo_algorithm)
    assert app.demo_algorithm.name == MATCHER and app.demo_algorithm.magic == 2801066
    assert app.demo.gallery.threshold == 1 and app.demo.gallery.min_margin == 0
    assert app.demo.gallery.acceptance_policy is None and cv2.getNumThreads() == 1
    if engine.policy != 'illumination' or engine.threads != 3:
        raise ValueError('Localizer setting mismatch')
    camera.audit = {}
    # Avoid ReplayCamera.select's untimed extra image-header read. Both decode
    # and integrity checks belong to the actual measured HTTP capture boundary.
    camera.select = lambda rows: setattr(camera, 'queue', list(rows))
    def capture():
        camera.last = row = camera.queue.pop(0)
        tick = time.perf_counter()
        data = Path(row['original']).read_bytes()
        import hashlib
        actual_hash = hashlib.sha256(data).hexdigest()
        camera.audit['read_hash_ms'] = (time.perf_counter()-tick)*1000
        camera.audit['input_sha256'] = actual_hash
        if actual_hash != row['sha256']:
            camera.audit['fatal'] = 'INPUT_INTEGRITY_FAILURE'
            raise RuntimeError('INPUT_INTEGRITY_FAILURE')
        tick = time.perf_counter()
        with Image.open(io.BytesIO(data)) as encoded:
            camera.audit.update(encoded_size=list(encoded.size), exif_orientation=encoded.getexif().get(274))
            full = ImageOps.exif_transpose(encoded).convert('RGB')
        camera.size = list(full.size)
        preview = full.resize((640,360))
        camera.audit.update(decoded_size=list(full.size), decode_preview_ms=(time.perf_counter()-tick)*1000)
        return preview, full, dict(replay_source_sha256=actual_hash)
    camera.capture_highres = capture
    extract = engine.extract
    def traced_extract(*args, **kwargs):
        tick = time.perf_counter()
        try:
            raw, quad, details = extract(*args, **kwargs)
            camera.audit.setdefault('localizations', []).append(dict(details=clean(details), quad=clean(quad),
                ms=(time.perf_counter()-tick)*1000))
            return raw, quad, details
        except Exception as error:
            camera.audit['localizer_exception'] = type(error).__name__ + ': ' + str(error)
            if isinstance(error, MemoryError): camera.audit['fatal'] = 'MemoryError'
            raise
    engine.extract = traced_extract
    return app, camera, dict(total_ms=(time.perf_counter()-started)*1000,
        model_and_gallery_ms=inner_startup, actual_matcher=app.demo_algorithm.name,
        feature_magic=app.demo_algorithm.magic, candidate=POLICY, memory=memory())


def ordered_rows(p, enrollment):
    return sorted((r for r in p['rows'] if r['enrollment'] == enrollment), key=lambda r:(r['subject'],r['index']))


def validate_feature(root, p, row, record):
    payload = record['payload']
    if payload['source_sha256'] != row['sha256']:
        raise ValueError('Enrollment source hash mismatch')
    if not payload['ok']:
        return None
    path = inside(payload['feature'], root/'features')
    if file_sha(path) != payload['feature_sha256']:
        raise ValueError('Candidate feature bytes changed')
    import numpy as np
    with np.load(path, allow_pickle=False) as z:
        feature = z['feature'].copy()
    if feature.dtype != np.uint8 or feature.shape != (16777216,) or int.from_bytes(feature[:4].tobytes(),'little',signed=True) != 2801066:
        raise ValueError('Candidate feature schema mismatch')
    return feature


def build_gallery(root, p, journal):
    import numpy as np
    from templates import TemplateStore
    from payment import PaymentService
    from pklnet_roi import ROI_GEOMETRY_VERSION
    runtime = root/'evaluation/runtime'
    store = TemplateStore(runtime/'demo_templates', compression_level=1)
    payments = PaymentService(runtime/'demo_payment.sqlite3')
    expected = []; by_sample = {r['sample']:r for r in journal.records}
    for identity in sorted({r['identity'] for r in p['rows']}):
        selected = [r for r in ordered_rows(p, True) if r['identity'] == identity]
        assert len(selected) == 5 and [r['index'] for r in selected] == list(range(5))
        records = [by_sample[r['sample']] for r in selected]
        ok = all(r['payload']['ok'] for r in records)
        user = identity.replace(':','-')
        entry = dict(identity=identity, user=user, samples=[r['sample'] for r in selected], registered=ok)
        expected.append(entry)
        if not ok:
            if store.exists(user) or payments.user_exists(user):
                raise ValueError('Unexpected failed-identity template/account')
            continue
        metadata = dict(user=user, display_name='EVAL '+identity, algorithm=MATCHER,
            capture_profile='noir-ir', samples=5, roi_geometry=ROI_GEOMETRY_VERSION,
            roi_sources=['pklnet']*5, run_fingerprint=p['run_fingerprint'],
            frame_record_sha256=[r['record_sha256'] for r in records], source='Fresh SMPD original-image candidate extraction')
        template, meta = store.paths(user)
        if template.exists() != meta.exists():
            raise ValueError('Partial template commit; preserve for explicit recovery')
        if store.exists(user):
            if load(meta) != metadata:
                raise ValueError('Wrong-version gallery metadata')
            seal=root/'gallery-records'/(user+'.json')
            if not seal.exists():
                # Crash after the template's atomic pair commit, before its
                # identity checkpoint: compare only same-run freshly generated
                # arrays. Never infer again or import historical features.
                features=[validate_feature(root,p,row,record) for row,record in zip(selected,records)]
                actual,_=store.load(user)
                if not np.array_equal(actual,np.stack(features)):
                    raise ValueError('Unsealed template differs from fresh frame records')
                del actual,features
        else:
            features = [validate_feature(root,p,row,record) for row,record in zip(selected,records)]
            store.save(user,np.stack(features),metadata)
            del features
        if not payments.user_exists(user): payments.create_account(user,'EVAL '+identity,10000)
        if payments.balance_for(user) != 10000 or payments.transaction_count() != 0:
            raise ValueError('Isolated account state changed')
        entry.update(template_sha256=file_sha(template), metadata_sha256=file_sha(meta))
        seal=root/'gallery-records'/(user+'.json')
        if seal.exists():
            if load(seal)!=dict(run_fingerprint=p['run_fingerprint'],**entry):
                raise ValueError('Identity gallery checkpoint changed')
        else:
            atomic(seal,dict(run_fingerprint=p['run_fingerprint'],**entry),exclusive=True)
    expected_users = sorted(e['user'] for e in expected if e['registered'])
    if store.list_users() != expected_users:
        raise ValueError('Gallery users differ from all successful fixed enrollments')
    value = dict(run_fingerprint=p['run_fingerprint'], enrollments=expected, registered=len(expected_users))
    if (root/'gallery.json').exists():
        if load(root/'gallery.json') != value: raise ValueError('Sealed gallery changed')
    else:
        atomic(root/'gallery.json',value,exclusive=True)
    return value


def outcome(q):
    response = q['result']
    if q['http_status'] != 200: return 'processing_failure'
    if response.get('status') != 'MATCH': return 'rejected'
    if response.get('user_id') != q['identity'].replace(':','-'): return 'wrong_identity_accepted'
    if response.get('score') is None or (response.get('second_score') is not None and not response['score'] < response['second_score']):
        return 'true_identity_nonunique'
    return 'correct'


def work(a):
    root = a.root.resolve(); p = load(root/'protocol.json')
    if str(root) != p['run_root']: raise ValueError('Run root moved')
    with run_lock(root):
        verify(p, dependencies=True)
        enroll_rows, query_rows = ordered_rows(p,True), ordered_rows(p,False)
        enroll = Journal(root,'enrollment',p['run_fingerprint'],[r['sample'] for r in enroll_rows])
        queries = Journal(root,'query',p['run_fingerprint'],[r['sample'] for r in query_rows])
        recover_inflight(root,dict(enrollment=enroll,query=queries))
        if len(queries.records)==3217 and load(root/'status.json').get('complete'):
            print('already_complete; no queries or status repeated',flush=True)
            return
        for row, record in zip(enroll_rows,enroll.records):
            if record['payload']['ok']:
                path=inside(record['payload']['feature'],root/'features')
                if file_sha(path)!=record['payload']['feature_sha256']: raise ValueError('Fresh feature integrity changed')
        epoch = uuid.uuid4().hex; start = time.perf_counter()
        epoch_path=root/'epochs'/(epoch+'.json')
        epoch_data=dict(epoch=epoch,pid=os.getpid(),started_unix=time.time(),
            enrollment_prefix=len(enroll.records),query_prefix=len(queries.records),run_fingerprint=p['run_fingerprint'])
        atomic(epoch_path,epoch_data,exclusive=True)
        def status(state, **extra):
            atomic(root/'status.json',dict(state=state,complete=False,epoch=epoch,pid=os.getpid(),
                run_fingerprint=p['run_fingerprint'],updated_unix=time.time(),
                enrollment_completed=len(enroll.records),completed_queries=len(queries.records),total_queries=3217,
                epoch_elapsed_s=time.perf_counter()-start,memory=memory(),**extra))
        def stop(): return (root/'STOP').exists()
        app = None
        try:
            resources_ok(p,startup=True)
            if len(enroll.records)<len(enroll_rows):
                status('fresh_enrollment_model_start')
                app,camera,ready=prepare_app(root/'enrollment-runtime',p,gallery=False)
                epoch_data['enrollment_ready']=ready;atomic(epoch_path,epoch_data)
                for row in enroll_rows[len(enroll.records):]:
                    if stop(): status('paused_STOP');return
                    verify(p);resources_ok(p);begin_attempt(root,enroll,epoch)
                    camera.audit={};camera.select([row]);tick=time.perf_counter()
                    status('extracting_fixed_enrollment',active_sample=row['sample'])
                    record=dict(source_sha256=row['sha256'],ok=False)
                    try:
                        feature,image,source=app.capture_demo_feature(enrollment=True)
                    except (ValueError,RuntimeError,OSError) as error:
                        if camera.audit.get('fatal'): raise
                        record['error']=type(error).__name__+': '+str(error)
                    else:
                        record['capture_ms']=(time.perf_counter()-tick)*1000
                        serialize=time.perf_counter()
                        import numpy as np
                        # Refuse an orphan from an interrupted uncommitted frame;
                        # it is retained, never silently imported as fresh evidence.
                        target=root/'features'/(row['sample']+'-'+epoch+'.npz')
                        target.parent.mkdir(exist_ok=True)
                        with target.open('xb') as stream:
                            np.savez_compressed(stream,feature=feature);stream.flush();os.fsync(stream.fileno())
                        record.update(ok=True,feature=str(target.resolve()),feature_sha256=file_sha(target),roi_source=source,
                            feature_serialization_hash_ms=(time.perf_counter()-serialize)*1000)
                        del feature,image
                    if camera.audit.get('fatal'): raise RuntimeError(camera.audit['fatal'])
                    record.update(ms=(time.perf_counter()-tick)*1000,capture=clean(camera.audit),memory=memory(),epoch=epoch)
                    if record.get('ok') and camera.audit.get('input_sha256') != row['sha256']: raise ValueError('Missing source hash verification')
                    verify(p);enroll.append(row['sample'],record);(root/'inflight.json').unlink()
                    status('fresh_enrollment',last_sample=row['sample'],last_ok=record['ok'])
                    print('enrollment',len(enroll.records),row['sample'],record['ok'],round(record['ms']),flush=True)
                app.demo_algorithm.close();app=None;gc.collect()
            if stop(): status('paused_STOP');return
            verify(p);status('building_complete_gallery')
            tick=time.perf_counter();gallery=build_gallery(root,p,enroll)
            epoch_data['bulk_registration_ms']=(time.perf_counter()-tick)*1000
            status('model_and_complete_gallery_start',registered=gallery['registered'])
            app,camera,ready=prepare_app(root/'evaluation/runtime',p,gallery=True)
            epoch_data['gallery_ready']=ready;atomic(epoch_path,epoch_data)
            if len(app.demo.gallery._prepared_cache)!=gallery['registered']:
                raise MemoryError('Full eligible gallery not resident; no partitions permitted')
            users={e['user'] for e in gallery['enrollments'] if e['registered']}
            if app.demo.payments.transaction_count()!=0: raise ValueError('Unexpected transactions')
            numeric={};original=app.demo_algorithm.score_gallery
            def scoring(probe,groups):
                try:
                    if set(groups)!=users: raise ValueError('Complete gallery changed')
                    value=original(probe,groups);numeric.update(value);return value
                except Exception as error:
                    camera.audit['fatal']='Scoring invariant/resource failure: '+type(error).__name__+': '+str(error)
                    raise
            app.demo_algorithm.score_gallery=scoring
            from http.client import HTTPConnection
            from http.server import ThreadingHTTPServer
            from palm_app import debug_ui
            handler=debug_ui.make_handler(app)
            class Quiet(handler):
                def log_message(self,*args): pass
            server=ThreadingHTTPServer(('127.0.0.1',0),Quiet)
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            def request(route,payload):
                tick=time.perf_counter();connection=HTTPConnection(*server.server_address,timeout=p['resources']['http_timeout_seconds'])
                try:
                    connection.request('POST',route,json.dumps(payload),{'Content-Type':'application/json'})
                    response=connection.getresponse();value=json.loads(response.read())
                    return response.status,value,(time.perf_counter()-tick)*1000
                finally: connection.close()
            done_epoch=0
            try:
                for row in query_rows[len(queries.records):]:
                    if stop() or (a.pause_after_queries is not None and done_epoch>=a.pause_after_queries):
                        status('paused_preflight' if not stop() else 'paused_STOP');return
                    verify(p);resources_ok(p);begin_attempt(root,queries,epoch)
                    camera.audit={};camera.select([row]);numeric.clear();app.demo_algorithm._terminal_rf_trace=None
                    status('query_inflight',active_sample=row['sample'])
                    before=memory();code,response,ms=request('/api/demo/identify',{})
                    if camera.audit.get('fatal'): raise RuntimeError(camera.audit['fatal'])
                    trace=clean(app.demo_algorithm._terminal_rf_trace)
                    if trace and trace['unknown_calls']: raise ValueError('Unknown RF comparison provenance')
                    if code==200 and (not trace or set(numeric)!=users): raise ValueError('Missing candidate whole-gallery scores')
                    cancellation_ms=0.
                    if response.get('token'):
                        cancelled,_,cancellation_ms=request('/api/demo/cancel',dict(token=response['token']))
                        if cancelled!=200 or app.demo.pending: raise ValueError('Cancellation failed')
                    if app.demo.payments.transaction_count()!=0: raise ValueError('Unexpected payment')
                    record=dict(identity=row['identity'],subject=row['subject'],condition=row['condition'],
                        source_sha256=row['sha256'],truth_enrolled=row['identity'].replace(':','-') in users,
                        http_status=code,ms=ms,cancellation_ms=cancellation_ms,
                        result={k:v for k,v in response.items() if k not in ('roi_image','token','expires_at')},
                        scores=clean(numeric),terminal_rf=trace,capture=clean(camera.audit),
                        before_memory=before,after_memory=memory(),epoch=epoch)
                    if camera.audit.get('input_sha256')!=row['sha256']: raise ValueError('Missing input hash verification')
                    record['outcome']=outcome(record);record['correct']=record['outcome']=='correct'
                    verify(p);queries.append(row['sample'],record);(root/'inflight.json').unlink();done_epoch+=1
                    elapsed=sum(r['payload']['ms'] for r in queries.records)/1000
                    throughput=len(queries.records)/elapsed if elapsed else None
                    status('query_checkpoint',last_sample=row['sample'],last_ms=ms,
                        summary=counts(queries),query_requests_s=elapsed,queries_per_hour=throughput*3600 if throughput else None,
                        linear_remaining_hours=(3217-len(queries.records))/throughput/3600 if throughput else None,
                        eta_warning='Observed prefix only; changing poses/branches make extrapolation uncertain.')
                    print('query',len(queries.records),row['sample'],record['outcome'],round(ms),flush=True)
                verify(p,dependencies=True)
                epoch_data.update(completed_unix=time.time(),final_memory=memory());atomic(epoch_path,epoch_data)
                status('complete',summary=counts(queries))
                final=load(root/'status.json');final['complete']=True;atomic(root/'status.json',final)
            finally:
                server.shutdown();server.server_close();thread.join()
        except Exception as error:
            status('failed_preserving_prefix',failure=type(error).__name__+': '+str(error))
            raise
        finally:
            if app is not None: app.demo_algorithm.close()
            epoch_data.update(ended_unix=time.time(),enrollment_final=len(enroll.records),query_final=len(queries.records),final_memory=memory())
            atomic(epoch_path,epoch_data)


def counts(journal):
    from collections import Counter
    values=[r['payload'] for r in journal.records]
    c=Counter(q['outcome'] for q in values)
    return dict(total=len(values),outcomes=dict(c),correct_within_2500=sum(q['correct'] and q['ms']<=2500 for q in values))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    init=sub.add_parser('init');init.add_argument('root',type=Path);init.add_argument('--source',type=Path,required=True);init.add_argument('--model',type=Path,required=True)
    run=sub.add_parser('work');run.add_argument('root',type=Path);run.add_argument('--pause-after-queries',type=int)
    args=parser.parse_args()
    if args.command=='init': initialize_protocol(args)
    else:
        if args.pause_after_queries is not None and args.pause_after_queries<1: parser.error('Positive query budget required')
        work(args)


if __name__=='__main__': main()
