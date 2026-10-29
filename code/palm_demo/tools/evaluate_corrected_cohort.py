"""Fresh v12/v13 HTTP evaluation after collector-confirmed label corrections.

Keep all queries in the denominator even if enrollment or localization fails.
Both versions enroll independently; explicit manifest roles preserve query separation. No recognition-driven filtering, tuning or query caching.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import shutil
import time
import cv2
import numpy as np
from replay_pi_pipeline import ReplayCamera, debug_ui, http_app, save_json
from replay_demo_manifest import correct_identification
from replay_ready_queries import power_sample, power_fault
from pklnet_roi import PKLNetROI
from native_registration import enable_native_registration
from linked_enrollment_matcher import LinkedEnrollmentMatcher
from affine_enrollment_matcher import AffineEnrollmentMatcher
from templates import TemplateStore


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('protocol', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--native-registration', type=Path, required=True)
    parser.add_argument('--expected-images', type=int, default=70)
    parser.add_argument('--expected-identities', type=int, default=7)
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text())
    app_root = Path(__file__).resolve().parents[1]
    for name, expected in protocol['code_hashes'].items():
        assert hashlib.sha256((app_root/name).read_bytes()).hexdigest() == expected
    rows = json.loads(args.manifest.read_text())
    assert len(rows) == args.expected_images and len({r['identity'] for r in rows}) == args.expected_identities
    assert all(hashlib.sha256(Path(r['original']).read_bytes()).hexdigest() == r['sha256'] for r in rows)
    assert all(r['role'] in ('enroll', 'query', 'unused_duplicate_enrollment') for r in rows)
    assert len({r['sample'] for r in rows}) == len(rows)
    groups = {u: sorted([r for r in rows if r['identity'] == u and r['role'] == 'enroll'], key=lambda r:r['index'])
              for u in sorted({r['identity'] for r in rows})}
    assert all(len(values) == 5 and [r['index'] for r in values] == list(range(1, 6)) for values in groups.values())
    assert all(r['index'] > 5 for r in rows if r['role'] == 'query')
    args.output.mkdir(parents=True, exist_ok=False)
    result = dict(protocol=protocol, live_camera_tested=False, cpu_affinity=sorted(os.sched_getaffinity(0)),
                  thread_settings=dict(opencv=1, onnx=3, native=1), runs=[], power_samples=[])
    destination = args.output/'results.json'
    def checkpoint():
        sample = power_sample()
        result['power_samples'].append(sample)
        if power_fault(sample):
            result['aborted_power_fault'] = sample
            save_json(destination, result)
            raise RuntimeError('Power fault; retained partial held-out evidence')
        save_json(destination, result)
    checkpoint()
    cv2.setNumThreads(1)
    queries = sorted([r for r in rows if r['role'] == 'query'], key=lambda r:(r['original_identity'], r['index']))
    assert len(queries) == 40
    random.Random(20261029).shuffle(queries)
    baseline_root = args.output/'baseline_runtime'
    for label, matcher in [('v12', LinkedEnrollmentMatcher), ('v13', AffineEnrollmentMatcher)]:
        checkpoint()
        runtime = baseline_root if label == 'v12' else args.output/'candidate_runtime'
        payloads = []
        start = time.perf_counter()
        engine = PKLNetROI(threads=3)
        debug_ui.common.RUNTIME = runtime
        camera = ReplayCamera(False, engine)
        app = debug_ui.App(camera, demo_matcher=matcher.name)
        enable_native_registration(app.demo_algorithm, args.native_registration, 1)
        run = dict(version=label, matcher=matcher.name, initialization_s=time.perf_counter()-start,
                   enrollment_reused=False, payloads=payloads, enrollments=[], queries=[])
        result['runs'].append(run)
        try:
            with http_app(app) as (request, trace):
                if True:
                    for identity, samples in groups.items():
                        camera.select(samples[:5])
                        status, response = request('/api/demo/enroll', dict(user_id=identity.replace(':', '-'), display_name='VALIDATION '+identity))
                        run['enrollments'].append(dict(identity=identity, status=status, result=response, ms=trace[-1]['ms']))
                        checkpoint()
                        print(label, 'enroll', len(run['enrollments']), status, flush=True)
                start = time.perf_counter()
                app.demo.gallery.warm_up()
                run['gallery_ready_s'] = time.perf_counter()-start
                before = app.demo.payments.transaction_count()
                for row in queries:
                    camera.select([row])
                    status, response = request('/api/demo/identify', {})
                    ms = trace[-1]['ms']
                    response.pop('roi_image', None)
                    trial = dict(sample=row['sample'], identity=row['identity'], http_status=status, result=response, ms=ms)
                    trial['correct'] = correct_identification(trial)
                    run['queries'].append(trial)
                    if response.get('token'):
                        request('/api/demo/cancel', dict(token=response['token']), 200)
                    checkpoint()
                    print(label, 'query', len(run['queries']), trial['correct'], round(ms), flush=True)
                trials = run['queries'];times = [q['ms'] for q in trials]
                run['summary'] = dict(total=len(queries), correct=sum(q['correct'] for q in trials),
                    correct_within_2_5s=sum(q['correct'] and q['ms'] <= 2500 for q in trials),
                    median_ms=float(np.median(times)), p95_ms=float(np.percentile(times, 95)), max_ms=max(times),
                    enrolled_identities=len(app.demo.store.list_users()),
                    transactions_unchanged=before == app.demo.payments.transaction_count())
                assert run['summary']['transactions_unchanged']
                # Isolated simulated payment tests, after timed accuracy queries.
                payment_tests = []
                for identity in sorted(groups):
                    trial = next((q for q in trials if q['identity'] == identity and q['correct']), None)
                    if trial is None:
                        payment_tests.append(dict(identity=identity, skipped='No correctly identified query'))
                        continue
                    row = next(r for r in queries if r['sample'] == trial['sample'])
                    camera.select([row])
                    _, response = request('/api/demo/identify', {}, 200)
                    assert response.get('user_id') == identity.replace(':', '-')
                    confirmation = dict(token=response['token'], user_id=response['user_id'])
                    old_balance = app.demo.payments.balance_for(response['user_id'])
                    _, confirmed = request('/api/demo/confirm', confirmation, 200)
                    confirm_ms = trace[-1]['ms']
                    assert confirmed['balance_cents'] == old_balance - 2000
                    request('/api/demo/confirm', confirmation, 400)
                    assert app.demo.payments.balance_for(response['user_id']) == old_balance - 2000
                    camera.select([row])
                    _, response = request('/api/demo/identify', {}, 200)
                    confirmation = dict(token=response['token'], user_id=response['user_id'])
                    request('/api/demo/cancel', dict(token=response['token']), 200)
                    request('/api/demo/confirm', confirmation, 400)
                    payment_tests.append(dict(identity=identity, confirm_ms=confirm_ms, confirmed=True, duplicate_blocked=True, cancelled_confirmation_blocked=True))
                    checkpoint()
                run['payment_tests'] = payment_tests
                run['payment_transactions'] = app.demo.payments.transaction_count() - before
                assert run['payment_transactions'] == sum(bool(p.get('confirmed')) for p in payment_tests)
                run['http_trace'] = trace
        finally:
            app.demo_algorithm.close()
            save_json(destination, result)
    result['originals_unchanged'] = all(hashlib.sha256(Path(r['original']).read_bytes()).hexdigest() == r['sha256'] for r in rows)
    assert result['originals_unchanged']
    checkpoint()
    print(json.dumps([r['summary'] for r in result['runs']]), flush=True)


if __name__ == '__main__':
    main()
