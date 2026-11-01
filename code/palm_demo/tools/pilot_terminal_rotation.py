"""Freeze and execute one six-query CPU development pilot, never a full run.

Private plans contain role bindings, original paths and complete score records.
No sample/identity literals enter the candidate or this selection procedure.
"""
import argparse
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

APP = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(APP), str(APP/'tools')]
from pilot_device_halfturn_guard import load, save, sha, digest, boundary, original_inventory, Telemetry
from terminal_rotation_consensus import POLICY, TERMINAL_ROUTE

DEVICE = APP/'runtime/device-halfturn-guard-20261101-r1'
PUBLIC = APP/'runtime/smpd-v27-continuation-20261031-r1'
PARENT = APP/'runtime/smpd-lossless-v27-20261031'


def select_device(runs):
    baselines = [r for r in runs if r['variant'] == 'baseline']
    choices = sorted((r['case'], q['sample'], q) for r in baselines for q in r['queries'])
    wrong = [(c, s, q) for c, s, q in choices if q['outcome'] == 'wrong_identity_accepted']
    if len(wrong) != 2 or wrong[0][0] != wrong[1][0]:
        raise ValueError('Expected exactly two stored errors in one complete case')
    case = wrong[0][0]
    def conflict(q):
        return q['localizations'][0]['primary_details'].get('pklnet_consensus_valid') is False
    terminal = next((v for v in choices if v[0] == case and v[2]['outcome'] == 'correct'
                     and v[2]['result']['recognition_route'] == TERMINAL_ROUTE and conflict(v[2])), None)
    fast = next((v for v in choices if v[0] == case and v[2]['outcome'] == 'correct'
                 and v[2]['result']['recognition_route'] != TERMINAL_ROUTE and conflict(v[2])), None)
    if terminal is None or fast is None:
        raise ValueError('Missing preregistered conflicting correct controls')
    selected = [*wrong, terminal, fast]
    if len({s for _, s, _ in selected}) != 4:
        raise ValueError('Duplicate device role binding')
    return selected


def select_public(rows, development, excluded):
    """Read only eligible development records, in fixed global baseline order."""
    found = {}
    queries = sorted((r for r in rows if not r['enrollment']), key=lambda r: (r['subject'], r['index']))
    for sequence, row in enumerate(queries[:1239]):
        if row['subject'] not in development or row['sample'] in excluded:
            continue
        path = (PARENT if sequence < 216 else PUBLIC)/'records/query'/f'{sequence:05d}.json'
        record = load(path)
        if record['sample'] != row['sample']:
            raise ValueError('Public ordinal binding changed')
        q = record['payload']; route = q['result'].get('recognition_route')
        loc = q['capture'].get('localizations', [])
        details = loc[0]['details'] if loc else {}
        if (row['condition'] == 'F' and q['outcome'] == 'wrong_identity_accepted'
                and q['truth_enrolled'] and route == TERMINAL_ROUTE
                and details.get('pklnet_consensus_valid') is False):
            found.setdefault('public_frontal_wrong_terminal_conflict', (row, q, path))
        if q['outcome'] == 'correct' and route != TERMINAL_ROUTE:
            found.setdefault('public_correct_fast', (row, q, path))
        if len(found) == 2:
            return found
    raise ValueError('Six fixed roles unavailable; no outcome-based replacement')


def historical_equal(current, reference):
    fields = ('status', 'user_id', 'score', 'second_score', 'recognition_route')
    return (current['http_status'] == reference['http_status'] and current['scores'] == reference['scores']
            and all(current['result'].get(k) == reference['result'].get(k) for k in fields))


def gates(rows):
    pairs = {r['label']: {} for r in rows}
    for r in rows:
        if r['variant'] in pairs[r['label']]:
            raise ValueError('Duplicate variant/query')
        pairs[r['label']][r['variant']] = r
    complete = len(pairs) == 6 and all(set(p) == {'baseline', 'candidate'} for p in pairs.values())
    result = dict(all_six_paired=complete,
                  baseline_exact=all(r.get('historical_exact', False) for r in rows if r['variant'] == 'baseline'),
                  candidate_original_shadow_exact=all(r.get('shadow_exact', False) for r in rows if r['variant'] == 'candidate'))
    result['real_correction'] = any(set(p) == {'baseline', 'candidate'} and
        p['baseline']['outcome'] == 'wrong_identity_accepted' and p['candidate']['outcome'] == 'correct' for p in pairs.values())
    result['all_correct_preserved'] = all(p['candidate']['outcome'] == 'correct' for p in pairs.values()
        if set(p) == {'baseline', 'candidate'} and p['baseline']['outcome'] == 'correct')
    result['no_new_failure_rejection_or_wrong'] = all(
        p['candidate']['outcome'] not in ('processing_failure', 'rejected', 'true_identity_nonunique') and
        not (p['baseline']['outcome'] != 'wrong_identity_accepted' and p['candidate']['outcome'] == 'wrong_identity_accepted')
        for p in pairs.values() if set(p) == {'baseline', 'candidate'})
    return result


def prepare(root):
    if root.exists():
        raise FileExistsError('New isolated pilot root required')
    old = load(DEVICE/'plan.json'); public = load(PUBLIC/'protocol.json')
    if load(PUBLIC/'status.json')['state'] != 'paused_STOP' or not (PUBLIC/'STOP').exists():
        raise ValueError('Public pause not intact')
    selected = select_device(load(DEVICE/'regression-results.json')['runs'])
    lookup = {r['sample']: r for r in old['rows']}
    items = []
    roles = ['device_wrong_a', 'device_wrong_b', 'device_correct_terminal_conflict', 'device_correct_fast_conflict']
    for i, ((case, sample, reference), role) in enumerate(zip(selected, roles), 1):
        items.append(dict(label=f'D{i}', domain='device', role=role, case=case,
                          row=lookup[sample], reference=reference))
    split_path = APP/'docs/protocols/SMPD_PROSPECTIVE_OPTIMIZATION_SPLIT_20261030.json'
    split = load(split_path)
    previous_path = APP/'runtime/smpd-oob-identification-pilot-20261101/results.json'
    excluded = {q['sample'] for q in load(previous_path)['queries']}
    chosen = select_public(public['rows'], set(split['development_subjects']), excluded)
    for i, role in enumerate(('public_frontal_wrong_terminal_conflict', 'public_correct_fast'), 1):
        row, reference, path = chosen[role]
        items.append(dict(label=f'P{i}', domain='public', role=role, case='public86', row=row,
                          reference=reference, record_path=str(path)))
    if len({r['row']['sample'] for r in items}) != 6:
        raise ValueError('Fixed six unique queries required')
    case = selected[0][0]
    folders = dict(device=DEVICE/'regression/baseline'/case/'runtime/demo_templates',
                   public=PUBLIC/'evaluation/runtime/demo_templates')
    files = {domain: {str(p): sha(p) for p in sorted(folder.iterdir()) if p.is_file()}
             for domain, folder in folders.items()}
    paths = [DEVICE/'plan.json', DEVICE/'regression-results.json', PUBLIC/'protocol.json', PUBLIC/'gallery.json',
             PUBLIC/'status.json', PUBLIC/'STOP', split_path, previous_path,
             *[Path(r['record_path']) for r in items if 'record_path' in r]]
    sources = dict(old['source_sha256'])
    for path in [Path(__file__), APP/'tools/terminal_rotation_consensus.py',
                 APP/'tools/pilot_epoch_cleanup.py', APP/'tests/test_pilot_epoch_cleanup.py',
                 APP/'tests/test_terminal_rotation_consensus.py', APP/'tests/test_terminal_rotation_pilot.py',
                 APP/'tests/test_pklnet_rotation_inputs.py']:
        sources[str(path.resolve())] = sha(path)
    p = dict(schema=1, policy=POLICY, model_setting='gpt-6.1-sol (developer-supplied identifier; no independent tool runtime-model receipt)',
        scope='One six-query Windows CPU seen-development pilot; no full evaluation/deployment/generalization qualification',
        created_unix=time.time(), executable=old['executable'], model_root=old['model_root'],
        sources_sha256=sources, models_sha256=old['models_sha256'], dependencies_sha256=old['dependencies_sha256'],
        metadata_sha256={str(x): sha(x) for x in paths}, templates_sha256=files, items=items,
        expected_gallery=dict(device=11, public=86), thresholds=old['thresholds'],
        protocol_change_from_draft='This authorized panel has four device + two public queries rather than six device then six public. Public wrong role is the first eligible frontal F query; no reserve results or former eight pilot images used.',
        rule=dict(turns=[0, 1, 2, 3], min_distinct_views=3, unique_largest_pairwise_clique=True,
                  min_quad_iou=.5, medoid='maximum summed IoU; tie by ascending turn',
                  trigger='original terminal RF route AND valid primary AND double-head consensus false',
                  no_score_ROI_selection=True, query_only=True, gallery_unchanged=True, max_rescore=1),
        resources=dict(start_free_GiB=12, running_free_GiB=2, max_RSS_GiB=14, workers=1),
        max_seconds=1800, max_http_seconds=600, no_retry=True, no_resume=True, promotion=False,
        rejection_is_not_correct=True, no_full168_unless_pilot_passes=True,
        historical_memory_difference='Prior device continuation used 8 GiB startup for last55; never qualified as12GiB throughout. New pilot freezes12GiB.',
        timing='Templates copied, not freshly enrolled; initialization/gallery-ready and HTTP reported separately; no Pi or causal speedup claim')
    for item in items:
        if sha(item['row']['original']) != item['row']['sha256']:
            raise ValueError('Original image hash mismatch')
    p['fingerprint'] = digest(p)
    save(root/'protocol.json', p, True)
    print(json.dumps(dict(prepared=True, fingerprint=p['fingerprint'],
        six=[dict(label=r['label'], role=r['role'], sample=r['row']['sample'], outcome=r['reference']['outcome']) for r in items])), flush=True)


def verify(p):
    if digest({k:v for k,v in p.items() if k != 'fingerprint'}) != p['fingerprint']:
        raise ValueError('Frozen protocol changed')
    if str(Path(sys.executable).resolve()) != p['executable']:
        raise ValueError('Wrong executable')
    for field in ('sources_sha256', 'models_sha256', 'dependencies_sha256', 'metadata_sha256'):
        for path, h in p[field].items():
            if sha(path) != h:
                raise ValueError('Frozen source/dependency changed: '+path)
    for files in p['templates_sha256'].values():
        if any(sha(path) != h for path, h in files.items()):
            raise ValueError('Original template bytes changed')
    for item in p['items']:
        if sha(item['row']['original']) != item['row']['sha256']:
            raise ValueError('Original image changed')


def run_group(root, p, domain, variant, report, check):
    from evaluate_raw_smpd import ExifReplay
    from pklnet_roi import PKLNetROI
    from palm_app import debug_ui
    from payment import PaymentService
    from lossless_union_matcher import LosslessUnionMatcher
    from lossless_template_store import LosslessTemplateStore
    from terminal_rf_evidence import install
    from terminal_rotation_consensus import TerminalRepair
    from run_terminal_smpd import outcome, clean
    from pilot_device_halfturn_guard import ExtractorObserver
    import cv2
    import numpy as np
    from PIL import Image, ImageOps
    check(startup=True)
    folder = root/domain/variant; runtime = folder/'runtime'
    templates = runtime/'demo_templates'; templates.mkdir(parents=True, exist_ok=False)
    for path, h in p['templates_sha256'][domain].items():
        destination = templates/Path(path).name; shutil.copyfile(path, destination)
        if sha(destination) != h:
            raise ValueError('Template byte copy mismatch')
    store = LosslessTemplateStore(templates); users = set(store.list_users())
    if len(users) != p['expected_gallery'][domain]:
        raise ValueError('Incomplete frozen gallery')
    payments = PaymentService(runtime/'demo_payment.sqlite3')
    for user in sorted(users): payments.create_account(user, 'EVAL '+user, 10000)
    engine = PKLNetROI(threads=3)
    camera = ExifReplay(False, engine)
    debug_ui.common.RUNTIME = runtime
    tick = time.perf_counter(); engine._ensure_loaded()
    engine._session.run(['keypoints', 'heatmap_keypoints', 'fc_keypoints'], {'image': np.zeros((1,3,400,300), np.float32)})
    app = debug_ui.App(camera, demo_matcher=LosslessUnionMatcher.name)
    app.demo_algorithm._retain_fastcc_evidence_pilot = True; install(app.demo_algorithm)
    app.demo.gallery.warm_up('noir-ir')
    ready_ms = (time.perf_counter()-tick)*1000
    check()
    assert type(app.demo_algorithm) is LosslessUnionMatcher and app.demo_algorithm.magic == 2801166
    assert app.demo.gallery.threshold == 1 and app.demo.gallery.min_margin == 0 and app.demo.gallery.acceptance_policy is None
    assert engine._session.get_providers() == ['CPUExecutionProvider'] and cv2.getNumThreads() == 1
    assert set(app.demo.gallery._prepared_cache) == users
    for entry in app.demo.gallery._prepared_cache.values():
        assert len(entry[1]) == 5
    group = dict(domain=domain, variant=variant, copied_gallery=len(users), fresh_enrollment_attempts=0,
                 initialization_and_gallery_ready_ms=ready_ms, complete=False)
    report['groups'].append(group); save(root/'progress.json', report)
    print(json.dumps(dict(stage='gallery_ready', **group)), flush=True)
    repair = TerminalRepair(app.demo_algorithm, engine, check) if variant == 'candidate' else None
    primary = {}; scored = {}; captured = {}
    extract = engine.extract
    def observed(image, **kw):
        result = extract(image, **kw)
        raw, quad, details = result
        primary.update(quad=clean(quad), details=clean(details), raw_sha256=hashlib.sha256(raw.tobytes()).hexdigest())
        if repair: repair.observe(image, result)
        return result
    camera.tracker.extractor = ExtractorObserver(engine, observed)
    def capture():
        row = camera.queue.pop(0); camera.last = row
        data = Path(row['original']).read_bytes()
        if hashlib.sha256(data).hexdigest() != row['sha256']:
            raise ValueError('Capture bytes changed')
        import io
        with Image.open(io.BytesIO(data)) as encoded:
            full = ImageOps.exif_transpose(encoded).convert('RGB')
        captured['decoded_rgb_sha256'] = hashlib.sha256(full.tobytes()).hexdigest()
        camera.size = list(full.size)
        return full.resize((640,360)), full, dict(replay_source_sha256=row['sha256'])
    camera.capture_highres = capture
    call_score = app.demo_algorithm.score_gallery
    def score(probe, groups):
        if set(groups) != users or any(len(s) != 5 for s in groups.values()):
            raise ValueError('Missing identity/enrollment frame during scoring')
        value = call_score(probe, groups)
        if set(value) != users:
            raise ValueError('Missing full-gallery score')
        scored.update(value); return value
    app.demo_algorithm.score_gallery = score
    handler = debug_ui.make_handler(app)
    class QuietHandler(handler):
        def log_message(self, *args): pass
    server = ThreadingHTTPServer(('127.0.0.1', 0), QuietHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    def request(route, payload):
        tick = time.perf_counter(); connection = HTTPConnection(*server.server_address, timeout=p['max_http_seconds'])
        try:
            connection.request('POST', route, json.dumps(payload), {'Content-Type':'application/json'})
            response = connection.getresponse()
            return response.status, json.loads(response.read()), (time.perf_counter()-tick)*1000
        finally: connection.close()
    try:
        for item in [r for r in p['items'] if r['domain'] == domain]:
            check(); primary.clear(); scored.clear(); captured.clear()
            app.demo_algorithm._terminal_rf_trace = None
            if repair: repair.trace = None; repair.context = None
            camera.select([item['row']])
            save(folder/'inflight.json', dict(label=item['label'], started=time.time()), True)
            code, response, ms = request('/api/demo/identify', {})
            row = dict(label=item['label'], role=item['role'], domain=domain, variant=variant,
                       sample=item['row']['sample'], identity=item['row']['identity'],
                       http_status=code, ms=ms,
                       result={k:v for k,v in response.items() if k not in ('roi_image', 'token', 'expires_at')},
                       scores=clean(scored), primary=copy.deepcopy(primary), capture=copy.deepcopy(captured),
                       terminal_rf=clean(app.demo_algorithm._terminal_rf_trace),
                       repair=clean(repair.trace) if repair else None)
            row['outcome'] = outcome(row)
            if response.get('token'):
                cc, cr, cm = request('/api/demo/cancel', dict(token=response['token']))
                if cc != 200: raise ValueError('Cancellation failed')
                row['cancellation_ms'] = cm
            if app.demo.pending or app.demo.payments.transaction_count() or any(app.demo.payments.balance_for(u) != 10000 for u in users):
                raise ValueError('Payment invariant failed')
            ref = item['reference']
            historical_primary = (ref['localizations'][0] if domain == 'device' else ref['capture']['localizations'][0])
            expected_quad = historical_primary['primary_quad' if domain == 'device' else 'quad']
            expected_details = historical_primary['primary_details' if domain == 'device' else 'details']
            row['primary_historical_exact'] = primary.get('quad') == expected_quad and primary.get('details') == expected_details
            row['historical_exact'] = historical_equal(row, ref) and row['primary_historical_exact']
            if repair and repair.trace:
                shadow = dict(row, scores=repair.trace['original_scores'], result=dict(row['result'],
                              recognition_route=repair.trace['original_route']))
                # Only the scorer's full vector/route are shadow data; the new HTTP
                # decision must not be relabeled as an old decision.
                row['shadow_exact'] = (shadow['scores'] == ref['scores'] and
                    repair.trace['original_route'] == ref['result']['recognition_route'] and row['primary_historical_exact'])
            else: row['shadow_exact'] = variant == 'baseline'
            row['record_sha256'] = digest(row)
            save(folder/'records'/(item['label']+'.json'), row, True)
            report['queries'].append(row); save(root/'progress.json', report)
            (folder/'inflight.json').unlink()
            print(json.dumps(dict(label=row['label'], variant=variant, outcome=row['outcome'], ms=ms,
                route=row['result'].get('recognition_route'), returned=row['result'].get('user_id'),
                geometry_changed=bool(row['repair'] and row['repair'].get('rescored')), historical=row['historical_exact'],
                shadow=row['shadow_exact'])), flush=True)
            if not row['primary_historical_exact'] or (variant == 'baseline' and not row['historical_exact']) or not row['shadow_exact']:
                raise ValueError('Frozen baseline/localization/shadow parity failed; no further queries')
        group['complete'] = True
        assert all(sha(templates/Path(path).name) == h for path, h in p['templates_sha256'][domain].items())
    finally:
        server.shutdown(); server.server_close(); thread.join()
        app.demo_algorithm.close(); app.demo.gallery._prepared_cache.clear()
        # Release bound-method cycles and the complete gallery before next epoch.
        if repair: repair.context = None
        app.demo_algorithm._references = None; app.demo_algorithm._index = None
        app.demo_algorithm.score_gallery = None
        del score, call_score, app, camera, engine, repair
        gc.collect()


def run(root):
    p = load(root/'protocol.json'); verify(p)
    if (root/'RUN_STARTED.json').exists(): raise ValueError('Non-resumable pilot already started')
    boundary(root, True)
    save(root/'RUN_STARTED.json', dict(pid=os.getpid(), started=time.time(), fingerprint=p['fingerprint']), True)
    report = dict(complete=False, pilot_pass=False, fingerprint=p['fingerprint'], groups=[], queries=[], failure=None)
    started = time.perf_counter()
    def check(startup=False):
        value = boundary(root, startup)
        if time.perf_counter()-started > p['max_seconds']:
            raise TimeoutError('Fixed 30-minute wall budget at completed boundary')
        return value
    before = None
    try:
        print('Protecting original public bytes before pilot', flush=True)
        before = original_inventory(); save(root/'public-before.json', before, True)
        from evaluate_raw_smpd import install_windows_capacity
        from retained_evidence_pilot import install_retained_evidence_pilot
        import cv2
        cv2.setNumThreads(1); os.environ['PALM_COMPNET_MODEL_ROOT'] = p['model_root']
        report['windows_capacity'] = install_windows_capacity()
        install_retained_evidence_pilot()
        with Telemetry(root/'telemetry.jsonl'):
            for domain in ('device', 'public'):
                for variant in ('baseline', 'candidate'):
                    run_group(root, p, domain, variant, report, check)
                    # run_group's HTTP handler/server/closure locals are gone
                    # only now. Its inner gc.collect still sees those owners.
                    from pilot_epoch_cleanup import collect_finished_epoch
                    cleanup = dict(domain=domain, variant=variant, **collect_finished_epoch())
                    report.setdefault('epoch_cleanup', []).append(cleanup)
                    save(root/'progress.json', report)
                    print(json.dumps(dict(stage='finished_epoch_cleanup', **cleanup)), flush=True)
        report['gates'] = gates(report['queries'])
        report.update(complete=report['gates']['all_six_paired'], pilot_pass=all(report['gates'].values()))
    except Exception as error:
        report['failure'] = type(error).__name__+': '+str(error)
        import traceback
        report['traceback'] = traceback.format_exc()
        print(report['failure'], flush=True)
    finally:
        try:
            verify(p)
            report['public_bytes_unchanged'] = before == original_inventory() if before is not None else False
            if not report['public_bytes_unchanged']: report['pilot_pass'] = False
        except Exception as error:
            report['preservation_error'] = type(error).__name__+': '+str(error); report['pilot_pass'] = False
        report['ended_unix'] = time.time(); report['wall_seconds'] = time.perf_counter()-started
        import psutil
        memory = psutil.Process().memory_info()
        report['final_memory'] = dict(rss=memory.rss, peak_wset=getattr(memory, 'peak_wset', None),
                                      available=psutil.virtual_memory().available)
        save(root/'results.json', report, True); save(root/'progress.json', report)
        print(json.dumps({k:report.get(k) for k in ('complete','pilot_pass','gates','failure','public_bytes_unchanged','wall_seconds','final_memory')}), flush=True)
    return 0 if report['pilot_pass'] else 2


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('prepare','run')); parser.add_argument('root', type=Path)
    args = parser.parse_args()
    if args.mode == 'prepare': prepare(args.root.resolve())
    else: sys.exit(run(args.root.resolve()))
