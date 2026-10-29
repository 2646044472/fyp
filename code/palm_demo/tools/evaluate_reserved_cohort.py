"""One frozen v12/v13 comparison on original held-out same-device images.

Keep all queries in the denominator even if enrollment or localization fails.
Fresh v12 enrollment is shared with v13 by verified payload-preserving tag
conversion. No recognition-driven filtering, tuning or query caching.
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
    parser.add_argument('--expected-images', type=int, default=80)
    parser.add_argument('--expected-identities', type=int, default=8)
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text())
    app_root = Path(__file__).resolve().parents[1]
    for name, expected in protocol['code_hashes'].items():
        assert hashlib.sha256((app_root/name).read_bytes()).hexdigest() == expected
    rows = json.loads(args.manifest.read_text())
    assert len(rows) == args.expected_images and len({r['identity'] for r in rows}) == args.expected_identities
    assert all(hashlib.sha256(Path(r['original']).read_bytes()).hexdigest() == r['sha256'] for r in rows)
    groups = {u:sorted([r for r in rows if r['identity'] == u], key=lambda r:r['index'])
              for u in sorted({r['identity'] for r in rows})}
    assert all(len(values)>5 and [r['index'] for r in values] == list(range(1, len(values)+1)) for values in groups.values())
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
    engine = PKLNetROI(threads=3)
    queries = [r for values in groups.values() for r in values[5:]]
    random.Random(20261029).shuffle(queries)
    baseline_root = args.output/'baseline_runtime'
    for label, matcher in [('v12', LinkedEnrollmentMatcher), ('v13', AffineEnrollmentMatcher)]:
        checkpoint()
        runtime = baseline_root if label == 'v12' else args.output/'candidate_runtime'
        payloads = []
        if label == 'v13':
            shutil.copytree(baseline_root, runtime)
            store = TemplateStore(runtime/'demo_templates')
            for user in store.list_users():
                features, meta = store.load(user)
                assert meta['algorithm'] == LinkedEnrollmentMatcher.name
                digest = hashlib.sha256(features[:, 4:].tobytes()).hexdigest()
                assert all(f[:4].view('<i4')[0] == LinkedEnrollmentMatcher.magic for f in features)
                for f in features:
                    f[:4] = np.asarray([matcher.magic], '<i4').view(np.uint8)
                meta['algorithm'] = matcher.name
                store.save(user, features, meta)
                copied, _ = store.load(user)
                assert hashlib.sha256(copied[:, 4:].tobytes()).hexdigest() == digest
                payloads.append(dict(user=user, sha256=digest))
        start = time.perf_counter()
        debug_ui.common.RUNTIME = runtime
        camera = ReplayCamera(False, engine)
        app = debug_ui.App(camera, demo_matcher=matcher.name)
        enable_native_registration(app.demo_algorithm, args.native_registration, 1)
        run = dict(version=label, matcher=matcher.name, initialization_s=time.perf_counter()-start,
                   enrollment_reused=label == 'v13', payloads=payloads, enrollments=[], queries=[])
        result['runs'].append(run)
        try:
            with http_app(app) as (request, trace):
                if label == 'v12':
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
        finally:
            app.demo_algorithm.close()
            save_json(destination, result)
    result['originals_unchanged'] = all(hashlib.sha256(Path(r['original']).read_bytes()).hexdigest() == r['sha256'] for r in rows)
    assert result['originals_unchanged']
    checkpoint()
    print(json.dumps([r['summary'] for r in result['runs']]), flush=True)


if __name__ == '__main__':
    main()
