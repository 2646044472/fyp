"""One frozen, development-only eight-image geometry observation. No matcher."""
import argparse
import copy
import hashlib
import importlib.metadata
import io
import json
import os
from pathlib import Path
import platform
import sys
import time

# Publication export: private sample bindings moved to an external manifest.
# The archived image runs used their original local drivers; this export has
# synthetic-test coverage only and has NOT been rerun on biometric images.
APP = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(APP), str(APP / 'tools')]
from halfturn_pilot_selection import arguments, bind
HERE = PARENT = CHILD = SELECTION_PATH = None
SAMPLES = []
NEGATIVE = None
BINDING = None


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def sha(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(',', ':')).encode()


def save_once(name, value):
    target = HERE / name
    with target.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=True, sort_keys=True, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def frozen_inventory():
    # Full file identity/stat inventory, plus byte hashes for every non-NPZ file.
    # Large immutable feature containers are not reread as a gratuitous I/O load.
    rows = {}
    for root in [PARENT, CHILD]:
        for path in sorted(root.rglob('*')):
            if not path.is_file():
                continue
            stat = path.stat()
            row = dict(bytes=stat.st_size, mtime_ns=stat.st_mtime_ns,
                       ctime_ns=stat.st_ctime_ns, inode=stat.st_ino)
            if path.suffix != '.npz':
                row['sha256'] = sha(path)
            rows[str(path)] = row
    return rows


def baseline_records():
    records = {}
    for folder in [PARENT / 'records/enrollment', PARENT / 'records/query', CHILD / 'records/query']:
        for path in sorted(folder.glob('*.json')):
            row = load(path)
            if row['sample'] in SAMPLES:
                if row['sample'] in records:
                    raise ValueError('Duplicate selected historical record')
                records[row['sample']] = (path, row)
    if set(records) != set(SAMPLES):
        raise ValueError('Selected historical records missing')
    return records


def verify_locks(protocol):
    if protocol['private_binding'] != BINDING:
        raise ValueError('Private selection or run directories changed')
    for field in ['sources_sha256', 'models_sha256', 'dependency_files_sha256', 'metadata_sha256']:
        for path, expected in protocol[field].items():
            if sha(path) != expected:
                raise ValueError('Frozen file changed: ' + path)
    for row in protocol['samples']:
        if sha(row['original']) != row['sha256']:
            raise ValueError('Original changed: ' + row['sample'])
    if not (CHILD / 'STOP').is_file() or (CHILD / 'inflight.json').exists():
        raise ValueError('Original continuation no longer paused at a boundary')
    if load(CHILD / 'status.json')['state'] != 'paused_STOP':
        raise ValueError('Original status changed')
    if str(Path(sys.executable).resolve()) != protocol['execution']['executable']:
        raise ValueError('Wrong interpreter')


def prepare():
    if (HERE / 'protocol.json').exists():
        raise ValueError('Protocol already exists; no overwrite or reselection')
    from report_smpd_continuation import snapshot
    state = snapshot(CHILD)
    if state['completed_queries'] != 1239:
        raise ValueError('Wrong paused boundary')
    frozen = load(CHILD / 'protocol.json')
    if Path(sys.executable).resolve() != Path(frozen['environment']['executable']).resolve():
        raise ValueError('Use the original CPU environment')
    records = baseline_records()
    reasons = [records[s][1]['payload']['capture']['localizations'][0]['details'].get('roi_geometry_reason') for s in SAMPLES]
    if (reasons.count('roi_out_of_bounds') != 5 or reasons.count(None) != 2
            or reasons[-1] != 'pklnet_keypoint_span_too_small'):
        raise ValueError('Expected five OOB, two valid and one span negative control')
    rows = []
    for sample in SAMPLES:
        original = next(r for r in frozen['rows'] if r['sample'] == sample)
        if int(original['subject']) % 5 == 0:
            raise ValueError('Protected sample forbidden')
        path, record = records[sample]
        capture = record['payload']['capture']
        rows.append(dict(sample=sample, original=original['original'], sha256=original['sha256'],
                         subject=original['subject'], enrollment=original['enrollment'],
                         record_path=str(path), record_sha256=sha(path),
                         decoded_rgb_sha256=capture['decoded_rgb_sha256'],
                         historical_localization=capture['localizations'][0]))
    sources = dict(frozen['source_sha256'])
    for path in [Path(__file__), APP / 'tools/halfturn_pilot_selection.py', APP / 'tools/halfturn_roi_recovery.py',
                 APP / 'tests/test_halfturn_roi_recovery.py', APP / 'tests/test_smpd_rotation_coordinates.py',
                 APP / 'tests/conftest.py']:
        sources[str(path)] = sha(path)
    models = dict(frozen['models_sha256'])
    model_root = APP.parent / 'pklnet'
    for name in ['pklnet-keypoints-diagnostics.json', 'net_params_500.pth']:
        path = model_root / name
        models[str(path)] = sha(path)
    metadata_paths = [PARENT / 'protocol.json', CHILD / 'protocol.json', CHILD / 'status.json',
                      CHILD / 'STOP', APP / 'docs/protocols/SMPD_PROSPECTIVE_OPTIMIZATION_SPLIT_20261030.json',
                      APP / 'runtime/halfturn-recovery-20261030/results.json']
    metadata_paths += [SELECTION_PATH] + [Path(row['record_path']) for row in rows]
    protocol = dict(schema=1, private_binding=BINDING, created_unix=time.time(), mode='geometry_only_no_matcher_no_gallery_no_HTTP',
        immutable_original_roots=[str(PARENT), str(CHILD)], samples=rows,
        selection='User-authorized fixed eight development images, ordered exactly as listed; no replacement or tuning.',
        candidate='Existing halfturn_roi_recovery.HalfTurnROIRecovery, unmodified',
        mechanism=dict(trigger='Only primary roi_geometry_reason == roi_out_of_bounds and invalid',
            primary='One PKLNetROI.extract call with existing illumination/aspect behavior',
            retry='At most one additional PKLNetROI.extract on exact PIL ROTATE_180; existing internal illumination/aspect behavior remains',
            mapping='(x,y) -> (width-1-x,height-1-y); existing mapped_details handles candidate/branch/crop coordinates',
            iou='quad_iou(primary_quad, mapped_retry_quad): convex polygon intersection over union; primary is NOT clipped to image bounds',
            minimum_iou=0.5, minimum_keypoint_span_ratio=0.1,
            sampling='Original RGB converted to BGR, mapped quadrilateral, existing roiExtractor.getROIimg(side=128, ratio=1.0)',
            valid_primary='Return exact original tuple/arrays/details without any retry',
            non_oob_failure='Return exact original tuple without retry; never relax span/bounds/IoU'),
        gates=['All eight attempted exactly once, with all errors and timings retained',
               'All source/model/input hashes and historical decoded RGB hashes unchanged',
               'Primary quad and full diagnostic dictionary exactly reproduce sealed historical records',
               'Every original valid output is the same tuple and byte/coordinate/diagnostic identical',
               'Span negative control unchanged with zero retries',
               'Every recovered quad in bounds and original retry geometry/span/IoU checks pass',
               'At least one targeted OOB geometry recovery; no identity success inference'],
        failure_policy='Failed geometry controls reject this pilot; do not tune/reselect/rerun. Exceptions retained. Integrity failure aborts further inference.',
        scope='Geometry only on previously seen public Windows development images. Not v27 recognition, accuracy, Pi latency, independent generalization, FAR, or deployment.',
        historical_limit='Prior all169 ROI audit exists; historical half-turn full168 HTTP run was v24 mislabeled v26, so confers no v26/v27 recognition qualification.',
        execution=dict(executable=str(Path(sys.executable).resolve()), python=sys.version, platform=platform.platform(),
                       roi_class='pklnet_roi.PKLNetROI', wrapper_class='halfturn_roi_recovery.HalfTurnROIRecovery',
                       matcher_instantiated=False, onnx_backend='CPUExecutionProvider', localizer_threads=3,
                       opencv_threads=1, side=128, synthetic_model_warmup=False,
                       environment={k:v for k,v in os.environ.items() if k.startswith(('PALM_','OMP_','MKL_','OPENBLAS_','ORT_'))},
                       packages={n:importlib.metadata.version(n) for n in ['numpy','Pillow','opencv-python-headless','onnxruntime','torch','pytest']}),
        sources_sha256=sources, models_sha256=models,
        dependency_files_sha256=frozen['dependency_sha256'],
        metadata_sha256={str(p):sha(p) for p in metadata_paths},
        frozen_boundary=dict(parent_fingerprint=state['version_boundary']['parent_run_fingerprint'],
                             continuation_fingerprint=frozen['run_fingerprint'], completed_queries=1239,
                             journal_tip=state['journal_tip']))
    verify_locks(protocol)
    inventory = frozen_inventory()
    save_once('preservation-before.json', inventory)
    protocol['preservation_inventory_sha256'] = sha(HERE / 'preservation-before.json')
    protocol['protocol_fingerprint'] = hashlib.sha256(canonical(protocol)).hexdigest()
    save_once('protocol.json', protocol)
    print(json.dumps(dict(prepared=True, protocol_fingerprint=protocol['protocol_fingerprint'], samples=SAMPLES)), flush=True)


def run():
    protocol = load(HERE / 'protocol.json')
    if hashlib.sha256(canonical({k:v for k,v in protocol.items() if k != 'protocol_fingerprint'})).hexdigest() != protocol['protocol_fingerprint']:
        raise ValueError('Protocol fingerprint mismatch')
    verify_locks(protocol)
    import xml.etree.ElementTree as ET
    test_root = ET.parse(HERE / 'fixtures.junit.xml').getroot()
    cases = list(test_root.iter('testcase'))
    if len(cases) != 8 or any(list(case) for case in cases):
        raise ValueError('All eight fixed non-biometric fixture tests must pass')
    before = load(HERE / 'preservation-before.json')
    if frozen_inventory() != before:
        raise ValueError('Preserved original inventory changed before inference')
    save_once('RUN_STARTED.json', dict(started_unix=time.time(), pid=os.getpid(), protocol_sha256=sha(HERE/'protocol.json'),
              fixture_report_sha256=sha(HERE/'fixtures.junit.xml'), note='Exclusive marker prohibits repeated image runs'))
    import cv2
    import numpy as np
    from PIL import Image, ImageOps
    from pklnet_roi import PKLNetROI, MIN_ILLUMINATION_IOU, MIN_KEYPOINT_SPAN_RATIO
    from halfturn_roi_recovery import HalfTurnROIRecovery
    cv2.setNumThreads(1)
    engine = PKLNetROI(threads=3, backend='onnx', policy='illumination')
    wrapper = HalfTurnROIRecovery(engine)
    if MIN_ILLUMINATION_IOU != 0.5 or MIN_KEYPOINT_SPAN_RATIO != 0.1:
        raise ValueError('Existing geometry constants changed')
    tick = time.perf_counter()
    engine._ensure_loaded()
    startup_ms = (time.perf_counter()-tick)*1000
    actual = dict(roi_class=type(engine).__module__+'.'+type(engine).__name__,
                  wrapper_class=type(wrapper).__module__+'.'+type(wrapper).__name__,
                  matcher_instantiated=False, backend=engine.backend_used,
                  providers=engine._session.get_providers(), threads=engine.threads, policy=engine.policy,
                  roi_geometry=engine.roi_geometry, opencv_threads=cv2.getNumThreads(), model_load_ms=startup_ms)
    if actual['providers'] != ['CPUExecutionProvider'] or actual['roi_class'] != 'pklnet_roi.PKLNetROI':
        raise ValueError('Unexpected actual ROI execution')
    report = dict(protocol_fingerprint=protocol['protocol_fingerprint'], complete=False, actual=actual,
                  started=load(HERE/'RUN_STARTED.json'), records=[], scope=protocol['scope'])
    try:
        with (HERE/'records.jsonl').open('x',encoding='utf-8',newline='\n') as journal:
            for spec in protocol['samples']:
                verify_locks(protocol)
                tick = time.perf_counter()
                row = dict(sample=spec['sample'], error=None)
                try:
                    raw_bytes=Path(spec['original']).read_bytes()
                    with Image.open(io.BytesIO(raw_bytes)) as encoded:
                        row['encoded_size']=list(encoded.size)
                        row['exif_orientation']=encoded.getexif().get(274)
                        full=ImageOps.exif_transpose(encoded).convert('RGB')
                    rgb_sha=hashlib.sha256(full.tobytes()).hexdigest()
                    if rgb_sha != spec['decoded_rgb_sha256']:
                        raise ValueError('Decoded RGB differs from original locked run')
                    row.update(decoded_size=list(full.size), decoded_rgb_sha256=rgb_sha,
                               read_decode_hash_ms=(time.perf_counter()-tick)*1000)
                    t=time.perf_counter();primary=engine.extract(full,side=128)
                    row['primary_ms']=(time.perf_counter()-t)*1000
                    pixels,quad,details=primary
                    raw_saved=pixels.copy();quad_saved=quad.copy();details_saved=copy.deepcopy(details)
                    historical=spec['historical_localization']
                    row['historical_primary_exact']=(np.array_equal(quad,np.asarray(historical['quad'],np.float32)) and details==historical['details'])
                    t=time.perf_counter();candidate=wrapper.recover(full,primary,side=128)
                    row['candidate_incremental_ms']=(time.perf_counter()-t)*1000
                    new_pixels,new_quad,new_details=candidate
                    unchanged=(np.array_equal(pixels,new_pixels) and np.array_equal(quad,new_quad) and details==new_details)
                    preserved=(np.array_equal(pixels,raw_saved) and np.array_equal(quad,quad_saved) and details==details_saved)
                    row.update(primary_valid=bool(details['roi_geometry_valid']), primary_reason=details.get('roi_geometry_reason'),
                        candidate_valid=bool(new_details['roi_geometry_valid']), candidate_reason=new_details.get('roi_geometry_reason'),
                        primary_quad=quad.tolist(), candidate_quad=new_quad.tolist(),
                        primary_details=details, candidate_details=new_details,
                        primary_roi_sha256=hashlib.sha256(pixels.tobytes()).hexdigest(),
                        candidate_roi_sha256=hashlib.sha256(new_pixels.tobytes()).hexdigest(),
                        primary_input_preserved=preserved, output_unchanged=unchanged, same_primary_tuple=(candidate is primary),
                        trace=copy.deepcopy(wrapper.last_trace))
                    if row['trace']['recovered']:
                        row['recovered_guards']=dict(in_bounds=bool((new_quad>=0).all() and (new_quad[:,0]<full.width).all() and (new_quad[:,1]<full.height).all()),
                            span=float(new_details['pklnet_keypoint_span_ratio']),span_pass=new_details['pklnet_keypoint_span_ratio']>=0.1,
                            iou=row['trace']['primary_retry_iou'],iou_pass=row['trace']['primary_retry_iou']>=0.5)
                    row['candidate_total_geometry_ms']=row['primary_ms']+row['candidate_incremental_ms']
                except Exception as error:
                    row['error']=type(error).__name__+': '+str(error)
                row['wall_ms']=(time.perf_counter()-tick)*1000
                report['records'].append(row)
                journal.write(json.dumps(row,ensure_ascii=True,sort_keys=True)+'\n');journal.flush();os.fsync(journal.fileno())
                print(json.dumps({k:row.get(k) for k in ['sample','error','primary_reason','candidate_valid','historical_primary_exact','candidate_incremental_ms']}),flush=True)
                if row['error'] and 'Decoded RGB differs' in row['error']:
                    raise ValueError('Image integrity failure; remaining inference prohibited')
        verify_locks(protocol)
        rows=report['records']
        all_ok=all(r['error'] is None for r in rows)
        guards=dict(all_eight_once=len(rows)==8 and [r['sample'] for r in rows]==SAMPLES,
            no_exceptions=all_ok,
            historical_primary_exact=all(r.get('historical_primary_exact',False) for r in rows),
            primary_inputs_preserved=all(r.get('primary_input_preserved',False) for r in rows),
            valid_controls_unchanged=all(r['output_unchanged'] and r['same_primary_tuple'] and not r['trace']['retry'] for r in rows if r.get('primary_valid')),
            span_negative_unchanged=all(r.get('output_unchanged') and r.get('same_primary_tuple') and not r.get('trace',{}).get('retry',True)
                for r in rows if r['sample']==NEGATIVE),
            every_recovery_passes_existing_guards=all(g['in_bounds'] and g['span_pass'] and g['iou_pass'] for r in rows if (g:=r.get('recovered_guards'))),
            at_least_one_oob_recovered=any(r.get('trace',{}).get('recovered') for r in rows))
        report.update(complete=True, gates=guards, geometry_pilot_pass=all(guards.values()),
                      retries=sum(r.get('trace',{}).get('retry',False) for r in rows),
                      recoveries=sum(r.get('trace',{}).get('recovered',False) for r in rows),
                      recognition_tested=False, recognition_stage_authorized=False)
    except Exception as error:
        report['fatal_error']=type(error).__name__+': '+str(error)
        report['geometry_pilot_pass']=False
    finally:
        current=frozen_inventory()
        report['preservation']=dict(all_original_file_stats_unchanged=current==before,
            original_files=len(before), non_npz_files_byte_hashed=sum('sha256' in v for v in before.values()),
            npz_scope='All NPZ identity/size/mtime/ctime unchanged; containers not byte-rehashed in this pilot',
            changed_paths=sorted(k for k in set(before)|set(current) if before.get(k)!=current.get(k)))
        if current!=before:report['geometry_pilot_pass']=False
        report['ended_unix']=time.time()
        save_once('results.json',report)
        print(json.dumps({k:report.get(k) for k in ['complete','geometry_pilot_pass','retries','recoveries','gates','fatal_error','preservation']}),flush=True)
    return 0 if report.get('geometry_pilot_pass') else 2


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    arguments(parser, 'geometry')
    args=parser.parse_args()
    globals().update(bind('geometry', args))
    if args.mode=='prepare':prepare()
    else:sys.exit(run())
