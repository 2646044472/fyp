"""Bounded device guard for an existing ROI policy; private artifacts stay local.

Prepare fixes a panel using stored reference roles, never recognition-time labels.
Panel runs one complete device-case gallery. Regression is a separate explicit
command, requires a passing panel and freshly enrolls both variants in four cases.
Neither command starts or resumes the public SMPD evaluation.
"""
import argparse
import collections
import gc
import hashlib
import json
import os
from pathlib import Path
import random
import shutil
import sys
import threading
import time

APP = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(APP), str(APP / 'tools')]
MATCHER = 'FastCCCompNetAlternateROI-v27-lossless-experimental'
PUBLIC = APP / 'runtime/smpd-v27-continuation-20261031-r1'
PARENT = APP / 'runtime/smpd-lossless-v27-20261031'


class ExtractorObserver:
    """Preserve the extractor interface used by feature/context extraction."""
    def __init__(self, base, observed):
        self.base, self.observed = base, observed

    def __getattr__(self, name):
        return getattr(self.base, name)

    def extract(self, *args, **kwargs):
        return self.observed(*args, **kwargs)


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def save(path, value, exclusive=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if exclusive:
        with path.open('x', encoding='utf-8') as f:
            json.dump(value, f, indent=2); f.flush(); os.fsync(f.fileno())
    else:
        temp = path.with_suffix(path.suffix + '.tmp')
        temp.write_text(json.dumps(value, indent=2), encoding='utf-8')
        temp.replace(path)


def select_panel(current, previous):
    old = {(r['case'], q['sample']): q for r in previous['runs'] for q in r['queries']}
    corrections = sorted((r['case'], q['sample']) for r in current['runs'] for q in r['queries']
                         if q['correct'] and not old[r['case'], q['sample']]['correct'])
    if not corrections:
        raise ValueError('No stored RF correction role')
    case_name, correction = corrections[0]
    queries = next(r['queries'] for r in current['runs'] if r['case'] == case_name)
    fast = min(q['sample'] for q in queries if q['correct']
               and q['result'].get('recognition_route') != 'exhaustive_terminal_rf_evidence')
    wrong = min(q['sample'] for q in queries if not q['correct'])
    return dict(case=case_name, queries=[fast, correction, wrong],
                roles=['stored_correct_fast', 'stored_RF_correction', 'stored_remaining_wrong'])


def exact_decision(a, b):
    fields = ('status', 'user_id', 'score', 'second_score', 'recognition_route')
    return (a['http_status'] == b['http_status'] and a['scores'] == b['scores']
            and all(a['result'].get(k) == b['result'].get(k) for k in fields))


def exact_roi(a, b):
    keys = ['primary_quad', 'primary_details', 'primary_roi_sha256',
            'candidate_quad', 'candidate_details', 'candidate_roi_sha256', 'verbatim']
    return (len(a['localizations']) == len(b['localizations'])
            and all(all(x[k] == y[k] for k in keys)
                    for x, y in zip(a['localizations'], b['localizations'])))


def summarize(rows):
    import numpy as np
    times = [q['ms'] for q in rows]
    c = collections.Counter(q['outcome'] for q in rows)
    return dict(total=len(rows), outcomes={k: c[k] for k in
                ['correct', 'wrong_identity_accepted', 'true_identity_nonunique', 'rejected', 'processing_failure']},
                correct_within_2500=sum(q['outcome'] == 'correct' and q['ms'] <= 2500 for q in rows),
                p50_ms=float(np.percentile(times, 50)), p95_ms=float(np.percentile(times, 95)), max_ms=max(times))


def boundary(root, startup=False):
    import psutil
    if (root / 'STOP').exists():
        raise InterruptedError('Local STOP at completed-request boundary')
    status = load(PUBLIC / 'status.json')
    if (status['state'] != 'paused_STOP' or status['completed_queries'] != 1239
            or not (PUBLIC / 'STOP').exists() or (PUBLIC / 'inflight.json').exists()):
        raise RuntimeError('Public pause boundary changed')
    own = psutil.Process()
    for p in psutil.process_iter(['cmdline']):
        try:
            argv = p.info['cmdline'] or []; cmd = ' '.join(argv)
            active = (any(s in cmd for s in ['run_smpd_continuation.py', 'run_lossless_smpd.py'])
                      or ('pilot_device_halfturn_guard.py' in cmd and any(m in argv for m in ['panel','regression'])))
            if p.pid not in [own.pid, own.ppid()] and active:
                raise RuntimeError('Competing evaluation worker')
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass
    mem = psutil.virtual_memory()
    rss = psutil.Process().memory_info().rss
    if mem.available < (12 if startup else 2) * 1024**3 or rss > 14 * 1024**3:
        raise MemoryError('Frozen available-memory/RSS limit')
    return dict(available=mem.available, rss=rss, cpu_s=sum(psutil.Process().cpu_times()[:2]))


def original_inventory():
    return {str(p): sha(p) for root in (PARENT, PUBLIC) for p in root.rglob('*') if p.is_file()}


def audited_core_compatibility(public):
    """Standard core plus exactly the previously frozen v27 container adapters.

    These three diffs were manually reviewed against their standard Git blobs:
    registry entry, store factory/batching/codec metadata, cache namespace only.
    Their exact byte hashes must match the immutable v27 protocol, not HEAD.
    """
    manifest = load(APP/'docs/protocols/STANDARD_DEVICE_BASELINE_20261030.json')
    allowed = {'code/palm_demo/biometric.py', 'code/palm_demo/demo_flow.py', 'code/palm_demo/gallery.py'}
    differences = {}
    for name, expected in manifest['core_sources'].items():
        path = APP.parents[1]/name
        normalized = hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()
        if normalized != expected['sha256_lf']:
            if name not in allowed or sha(path) != public['source_sha256'].get(str(path.resolve())):
                raise ValueError('Unreviewed core drift: '+name)
            differences[name] = dict(standard_sha256_lf=expected['sha256_lf'],
                                     frozen_v27_sha256=sha(path), standard_git_blob=expected['git_blob'])
    if set(differences) != allowed:
        raise ValueError('Reviewed compatibility set changed')
    return differences


def prepare(root, supersedes=None):
    if root.exists():
        raise FileExistsError('New isolated directory required')
    from run_terminal_smpd import source_files
    from report_smpd_continuation import snapshot
    assert snapshot(PUBLIC)['completed_queries'] == 1239
    public = load(PUBLIC/'protocol.json')
    assert public['run_fingerprint'] == '23778a4613d516f39138b3487238bad813484800c238d8b3916318bd19795e47'
    compatibility = audited_core_compatibility(public)
    terminal_path = APP / 'runtime/terminal-rf-full168-20261030/evaluation/results.json'
    previous_path = APP / 'runtime/v26-device-reference-20261030/evaluation/results.json'
    geometry_path = APP / 'runtime/smpd-roi-oob-pilot-20261101/results.json'
    identify_path = APP / 'runtime/smpd-oob-identification-pilot-20261101/results.json'
    terminal, previous = load(terminal_path), load(previous_path)
    geometry, identify = load(geometry_path), load(identify_path)
    assert terminal['complete'] and terminal['summary']['correct'] == 166
    assert geometry['geometry_pilot_pass'] and identify['pilot_pass']
    assert sha(APP/'tools/halfturn_roi_recovery.py') == load(APP/'runtime/smpd-roi-oob-pilot-20261101/protocol.json')['sources_sha256'][str((APP/'tools/halfturn_roi_recovery.py').resolve())]
    req_path = APP / 'docs/protocols/CANDIDATE_DEVICE_REGRESSION_REQUIREMENTS_20261030.json'
    req = load(req_path)
    manifest = APP.parents[1] / req['original_manifest']
    assert sha(manifest) == req['manifest_sha256']
    protocol_path = APP / 'runtime/pi5-under2-20261028/active169-baseline-20261029/protocol.json'
    protocol = load(protocol_path)
    rows_path = APP / 'runtime/halfturn-recovery-20261030/device-manifest-local.json'
    rows = load(rows_path)
    assert len(rows) == 169 and sum(len(c['queries']) for c in protocol['cases']) == 168
    assert sorted((r['sample'], r['sha256']) for r in rows) == sorted((r['sample'], r['sha256']) for r in load(manifest))
    assert all(sha(r['original']) == r['sha256'] for r in rows)
    code = set(source_files()) | {Path(__file__), APP / 'tools/halfturn_roi_recovery.py',
                                 APP / 'tools/terminal_rf_evidence.py', APP / 'tools/fastcc_valid_support.py'}
    artifacts = [terminal_path, previous_path, geometry_path, identify_path, req_path, manifest, protocol_path, rows_path,
                 PUBLIC/'protocol.json', APP/'docs/protocols/STANDARD_DEVICE_BASELINE_20261030.json']
    plan = dict(schema=1, panel=select_panel(terminal, previous), protocol=protocol, rows=rows,
                source_sha256={str(p): sha(p) for p in code}, audited_core_compatibility=compatibility,
                models_sha256=public['models_sha256'], dependencies_sha256=public['dependency_sha256'],
                metadata_sha256={str(p): sha(p) for p in artifacts}, model_root=public['model_root'],
                executable=str(Path(sys.executable).resolve()), matcher=MATCHER,
                thresholds=dict(early_distance=.32, early_margin=.08, final_distance=1., final_margin=0., rejection=False),
                stored_terminal=terminal, stored_previous=previous,
                archived_geometry=dict(retries=geometry['retries'], recoveries=geometry['recoveries'], gates=geometry['gates']),
                archived_identification=dict(outcomes=identify['outcomes'], gates=identify['gates']),
                archived_only='No public images inferred again; saved failure controls are not new observations',
                panel_template_reuse='Only fresh v27 baseline templates whose every enrollment primary is valid and halfturn recover returns the exact same tuple; copy bytes to independent runtime, load/index ready timed separately',
                full_template_reuse=False, full_fresh_enrollments_each_variant=34,
                guards=['No lost stored/current correct query', 'All paired scores/decisions/ROI exact on device panel',
                        'Every reused enrollment primary valid and candidate tuple identical',
                        'No new processing failure/rejection/wrong', 'Complete case galleries and five-frame enrollment',
                        'Original inputs/sources/public pause preserved', 'Tokens canceled; zero transactions'],
                resource_limits=dict(workers=1, start_free_GiB=12, boundary_free_GiB=2, max_RSS_GiB=14,
                                     no_GPU_install=True),
                stop='STOP in this new output root; finish current HTTP request, preserve records, no automatic resume',
                full_authorization='Separate explicit regression command only after panel passes and cost/status report',
                promotion=False, independent_generalization=False)
    if supersedes is not None:
        old = load(supersedes/'plan.json')
        failed = load(supersedes/'panel-results.json')
        assert not failed['complete'] and not failed['pass']
        assert old['panel'] == plan['panel'] and old['thresholds'] == plan['thresholds']
        assert sha(supersedes/'executed-driver.py') == old['source_sha256'][str(Path(__file__).resolve())]
        plan['supersedes_harness_failure'] = dict(root=str(supersedes),plan_sha256=sha(supersedes/'plan.json'),
            results_sha256=sha(supersedes/'panel-results.json'),executed_driver_sha256=sha(supersedes/'executed-driver.py'),
            reason='Observer failed to forward extractor.root before first enrollment completed; zero identify requests; fix forwards all attributes, same panel and no algorithm change')
        plan['metadata_sha256'].update({str(supersedes/p):sha(supersedes/p) for p in ['plan.json','panel-results.json','executed-driver.py']})
    plan['fingerprint'] = digest(plan)
    root.mkdir()
    save(root / 'plan.json', plan, True)
    print(json.dumps(dict(prepared=True, fingerprint=plan['fingerprint'], panel=plan['panel'])))


def verify(plan):
    if digest({k:v for k,v in plan.items() if k != 'fingerprint'}) != plan['fingerprint']:
        raise ValueError('Plan fingerprint changed')
    assert str(Path(sys.executable).resolve()) == plan['executable']
    for name in ['source_sha256', 'models_sha256', 'dependencies_sha256', 'metadata_sha256']:
        for path, h in plan[name].items():
            if sha(path) != h:
                raise ValueError('Frozen dependency/source changed: ' + path)


class Telemetry:
    def __init__(self, path):
        self.path = path; self.stop = threading.Event(); self.thread = None

    def __enter__(self):
        import psutil
        def observe():
            proc = psutil.Process(); psutil.cpu_percent(percpu=True)
            with self.path.open('x') as f:
                while not self.stop.wait(1):
                    io = psutil.disk_io_counters()
                    v = dict(time=time.time(), cpu_per_core=psutil.cpu_percent(percpu=True),
                             cpu_s=sum(proc.cpu_times()[:2]), rss=proc.memory_info().rss,
                             available=psutil.virtual_memory().available,
                             disk_read_bytes=io.read_bytes, disk_write_bytes=io.write_bytes)
                    f.write(json.dumps(v) + '\n'); f.flush()
        self.thread = threading.Thread(target=observe, daemon=True); self.thread.start()
        return self

    def __exit__(self, *args):
        self.stop.set(); self.thread.join()


def case_run(root, plan, case, samples, variant, baseline=None):
    import cv2
    import numpy as np
    from replay_pi_pipeline import ReplayCamera, debug_ui, http_app
    from pklnet_roi import PKLNetROI
    from halfturn_roi_recovery import HalfTurnROIRecovery
    from lossless_union_matcher import LosslessUnionMatcher
    from lossless_template_store import LosslessTemplateStore
    from terminal_rf_evidence import install as install_rf
    from run_terminal_smpd import clean, outcome
    from evaluate_six_person_frozen import EnrollmentStages
    from payment import PaymentService
    directory = root / variant / case['name']; directory.mkdir(parents=True, exist_ok=False)
    runtime = directory / 'runtime'
    lookup = {r['sample']:r for r in plan['rows']}
    enrollment = case['enrollment']
    if baseline is not None:
        assert baseline['enrollments_all_verbatim']
        source = Path(baseline['runtime']) / 'demo_templates'
        target = runtime / 'demo_templates'; target.mkdir(parents=True)
        for p in source.iterdir():
            shutil.copyfile(p, target / p.name)
            assert sha(p) == sha(target / p.name)
        payments = PaymentService(runtime / 'demo_payment.sqlite3')
        for identity in enrollment:
            payments.create_account(identity.replace(':','-'), 'EVAL '+identity, 10000)
    tick = time.perf_counter()
    engine = PKLNetROI(threads=3); engine._ensure_loaded()
    engine._session.run(['keypoints','heatmap_keypoints','fc_keypoints'], {'image':np.zeros((1,3,400,300),np.float32)})
    recovery = HalfTurnROIRecovery(engine); camera = ReplayCamera(False, recovery if variant == 'candidate' else engine)
    debug_ui.common.RUNTIME = runtime
    app = debug_ui.App(camera, demo_matcher=MATCHER)
    app.demo_algorithm._retain_fastcc_evidence_pilot = True; install_rf(app.demo_algorithm)
    assert type(app.demo_algorithm) is LosslessUnionMatcher and app.demo_algorithm.magic == 2801166
    assert isinstance(app.demo.store, LosslessTemplateStore)
    assert app.demo.gallery.threshold == 1 and app.demo.gallery.min_margin == 0 and app.demo.gallery.acceptance_policy is None
    assert engine._session.get_providers() == ['CPUExecutionProvider'] and cv2.getNumThreads() == 1
    result = dict(case=case['name'], variant=variant, runtime=str(runtime), startup_ready_ms=(time.perf_counter()-tick)*1000,
                  enrollment_reused=baseline is not None, enrollments=[], queries=[], localizations=[],
                  actual=dict(matcher=type(app.demo_algorithm).__module__+'.'+type(app.demo_algorithm).__name__,
                              magic=app.demo_algorithm.magic, codec=app.demo_algorithm.template_codec,
                              retained=True, terminal_rf=True, providers=engine._session.get_providers()))
    stage = ['idle']; locs = []; original = engine.extract
    # Primary is recomputed from each original image. The shadow is a pure
    # pass-through for valid primaries; invalid primaries prevent template reuse.
    def observed(image, *, side=128):
        start = time.perf_counter(); primary = original(image, side=side)
        candidate = recovery.recover(image, primary, side=side)
        locs.append(dict(sample=camera.last['sample'], stage=stage[0],
                         primary_quad=clean(primary[1]), primary_details=clean(primary[2]),
                         primary_roi_sha256=hashlib.sha256(primary[0].tobytes()).hexdigest(),
                         candidate_quad=clean(candidate[1]), candidate_details=clean(candidate[2]),
                         candidate_roi_sha256=hashlib.sha256(candidate[0].tobytes()).hexdigest(),
                         verbatim=candidate is primary, primary_valid=bool(primary[2]['roi_geometry_valid']),
                         trace=clean(recovery.last_trace), total_geometry_ms=(time.perf_counter()-start)*1000))
        return candidate if variant == 'candidate' else primary
    # Do not double-wrap the recovery: camera always delegates to this observer.
    camera.tracker.extractor = ExtractorObserver(engine, observed)
    scores = {}; scorer = app.demo_algorithm.score_gallery
    def scoring(probe, groups):
        values = scorer(probe, groups); scores.update(values)
        assert set(values) == {u.replace(':','-') for u in enrollment}
        return values
    app.demo_algorithm.score_gallery = scoring
    stages = EnrollmentStages(); stages.install()
    try:
        with http_app(app) as (request, trace):
            if baseline is None:
                for identity, selected in sorted(enrollment.items()):
                    boundary(root.parent); assert len(selected) == 5
                    stage[0] = 'enrollment'; locs.clear(); camera.select([lookup[s] for s in selected])
                    save(directory / 'inflight.json', dict(stage='enrollment', identity=identity, started=time.time()), True)
                    stages.start = time.perf_counter(); stages.events = []
                    code, response = request('/api/demo/enroll', dict(user_id=identity.replace(':','-'), display_name='EVAL '+identity))
                    events = stages.events; stages.events = None
                    item = dict(identity=identity, http_status=code, result={k:v for k,v in response.items() if k != 'roi_image'},
                                ms=trace[-1]['ms'], events=events, localizations=list(locs))
                    result['enrollments'].append(item)
                    (directory / 'inflight.json').unlink()
                    save(directory / 'progress.json', result)
                    if code != 200 or not response.get('recognition_ready') or len(locs) != 5:
                        raise RuntimeError('Five-frame enrollment/ready failure')
                    print(json.dumps(dict(case=case['name'],variant=variant,enrolled=len(result['enrollments']),total=len(enrollment))), flush=True)
            result['enrollments_all_verbatim'] = (all(l['verbatim'] and l['primary_valid'] for e in result['enrollments'] for l in e['localizations'])
                                                   if baseline is None else baseline['enrollments_all_verbatim'])
            assert set(app.demo.store.list_users()) == {u.replace(':','-') for u in enrollment}
            for sample in samples:
                boundary(root.parent); stage[0] = 'query'; locs.clear(); scores.clear()
                camera.select([lookup[sample]]); stages.start = time.perf_counter(); stages.events = []
                save(directory / 'inflight.json', dict(sample=sample, started=time.time()), True)
                code, response = request('/api/demo/identify', {})
                events = stages.events; stages.events = None
                item = dict(sample=sample, identity=lookup[sample]['identity'], http_status=code, ms=trace[-1]['ms'],
                            result={k:v for k,v in response.items() if k not in ['roi_image','token','expires_at']},
                            scores=clean(scores), terminal_rf=clean(app.demo_algorithm._terminal_rf_trace),
                            localizations=list(locs), events=events)
                item['outcome'] = outcome(item)
                if response.get('token'):
                    request('/api/demo/cancel', dict(token=response['token']), 200)
                assert not app.demo.pending and app.demo.payments.transaction_count() == 0
                result['queries'].append(item)
                save(directory / 'query-records' / (sample+'.json'), item, True)
                (directory / 'inflight.json').unlink()
                save(directory / 'progress.json', result)
                print(json.dumps(dict(case=case['name'],variant=variant,query=len(result['queries']),total=len(samples),outcome=item['outcome'],ms=item['ms'])), flush=True)
        result['summary'] = summarize(result['queries'])
        result['zero_transactions'] = app.demo.payments.transaction_count() == 0
        result['complete'] = True
        save(directory / 'results.json', result, True)
        return result
    finally:
        stages.restore(); app.demo_algorithm.close(); gc.collect()


def run(root, full=False):
    import cv2
    import psutil
    from retained_evidence_pilot import install_retained_evidence_pilot
    from report_smpd_continuation import snapshot
    plan = load(root / 'plan.json'); verify(plan); boundary(root, True)
    if psutil.cpu_percent(interval=1) > 35:
        raise RuntimeError('Host already busy; no evaluation launched')
    mode = 'regression' if full else 'panel'
    if full and not load(root / 'panel-results.json')['pass']:
        raise ValueError('Panel must pass before regression')
    output = root / mode; output.mkdir(exist_ok=False)
    save(output / 'RUN_STARTED.json', dict(pid=os.getpid(), started=time.time(), fingerprint=plan['fingerprint']), True)
    before = original_inventory()
    save(output / 'public-before.json', before, True)
    os.environ['PALM_COMPNET_MODEL_ROOT'] = plan['model_root']; cv2.setNumThreads(1)
    install_retained_evidence_pilot()
    report = dict(complete=False, runs=[], mode=mode, promotion=False, source_fingerprint=plan['fingerprint'])
    try:
        with Telemetry(output / 'telemetry.jsonl'):
            cases = plan['protocol']['cases'] if full else [next(c for c in plan['protocol']['cases'] if c['name'] == plan['panel']['case'])]
            for case in cases:
                samples = list(case['queries']) if full else plan['panel']['queries']
                if full:
                    random.Random(case['query_seed']).shuffle(samples)
                for variant in ['baseline', 'candidate']:
                    boundary(root, True)
                    reuse = report['runs'][-1] if variant == 'candidate' and not full else None
                    value = case_run(output, plan, case, samples, variant, reuse)
                    report['runs'].append(value); save(output / 'progress.json', report); gc.collect()
        pairs = {}
        for r in report['runs']:
            for q in r['queries']:
                pairs.setdefault((r['case'],q['sample']), {})[r['variant']] = q
        stored = {(r['case'],q['sample']):q for r in plan['stored_terminal']['runs'] for q in r['queries']}
        exact = all(exact_decision(v['baseline'], v['candidate']) for v in pairs.values())
        roi_exact = all(exact_roi(v['baseline'], v['candidate']) for v in pairs.values())
        from lossless_template_store import LosslessTemplateStore
        import numpy as np
        feature_parity = []
        for case_name in {r['case'] for r in report['runs']}:
            runs = [next(r for r in report['runs'] if r['case']==case_name and r['variant']==v)
                    for v in ['baseline','candidate']]
            stores = [LosslessTemplateStore(Path(r['runtime'])/'demo_templates') for r in runs]
            assert stores[0].list_users() == stores[1].list_users()
            for user in stores[0].list_users():
                arrays = [s.load(user)[0] for s in stores]
                same = len(arrays[0]) == len(arrays[1]) == 5 and all(np.array_equal(a,b) for a,b in zip(*arrays))
                feature_parity.append(dict(case=case_name,user=user,all_five_exact=same))
                del arrays
        historical_exact = all(v['baseline']['scores'] == stored[k]['diagnostics']['scores'] and
                               all(v['baseline']['result'].get(f) == stored[k]['result'].get(f) for f in
                                   ['status','user_id','score','second_score','recognition_route']) for k,v in pairs.items())
        no_loss = all(not stored[k]['correct'] or v['candidate']['outcome'] == 'correct' for k,v in pairs.items())
        valid_unchanged = all(l['primary_valid'] and l['verbatim'] for r in report['runs'] for e in r['enrollments'] for l in e['localizations'])
        # Existing public OOB-success/failure/span controls are archived evidence,
        # not rerun data. Device results can only establish preservation here.
        report.update(complete=True, pass_=exact and roi_exact and historical_exact and no_loss and valid_unchanged and all(p['all_five_exact'] for p in feature_parity),
                      gates=dict(paired_exact=exact, historical_terminal_exact=historical_exact,
                                 paired_roi_exact=roi_exact, all_five_feature_parity=all(p['all_five_exact'] for p in feature_parity),
                                 no_lost_correct=no_loss, enrollment_primary_verbatim=valid_unchanged),
                      feature_parity=feature_parity,
                      summaries={v:summarize([q for r in report['runs'] if r['variant']==v for q in r['queries']]) for v in ['baseline','candidate']})
        report['pass'] = report.pop('pass_')
    except Exception as e:
        report.update(failure=type(e).__name__+': '+str(e), **{'pass':False})
        print(report['failure'], flush=True)
    finally:
        try:
            verify(plan)
            report['public_bytes_unchanged'] = original_inventory() == before
            s = snapshot(PUBLIC)
            report['public_boundary'] = dict(state=s['status']['state'], completed=s['completed_queries'], tip=s['journal_tip'])
            report['original_images_unchanged'] = all(sha(r['original']) == r['sha256'] for r in plan['rows'])
            if not report['public_bytes_unchanged'] or not report['original_images_unchanged']:
                report['pass'] = False
        except Exception as e:
            report['preservation_failure'] = str(e); report['pass'] = False
        report['ended'] = time.time()
        save(root / (mode+'-results.json'), report, True)
        print(json.dumps({k:v for k,v in report.items() if k != 'runs'}), flush=True)
    return 0 if report['pass'] else 2


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=['prepare', 'panel', 'regression'])
    p.add_argument('output', type=Path)
    p.add_argument('--supersedes', type=Path, help='Preserved operationally invalid harness run; prepare only')
    a = p.parse_args(); directory = a.output.resolve()
    if not directory.is_relative_to(APP / 'runtime') or directory in [PUBLIC, PARENT] or any(directory.is_relative_to(r) or r.is_relative_to(directory) for r in [PUBLIC,PARENT]):
        p.error('New isolated runtime sibling required')
    if a.mode == 'prepare':
        prepare(directory, a.supersedes.resolve() if a.supersedes else None)
    else:
        sys.exit(run(directory, a.mode == 'regression'))
