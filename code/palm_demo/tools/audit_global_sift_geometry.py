"""Four-image, all-gallery geometric prerequisite audit; no identity scoring.

A new global query descriptor is observational: it does not inherit the
reference recognizer's accuracy. Existing enrollment descriptors, ratio/mutual
matching, deterministic similarity fitting and geometric limits are reused.
Labels are used only after all 55 registrations to evaluate a locked panel.
"""
import hashlib
import itertools
import json
from pathlib import Path
import shutil
import sys
import time
import traceback

APP = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(APP), str(APP / 'tools')]
import cv2
import numpy as np
import psutil
from PIL import Image, ImageOps
from registered_matcher import local_features, registration
from pklnet_roi import normalize_roi_pixels
from lossless_template_store import LosslessTemplateStore
from union_lossless_codec import decode
from halfturn_roi_recovery import quad_iou
from experiment_resource_limits import resource_fault


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def save(path, value):
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, indent=2), encoding='utf-8')
    temp.replace(path)


def mapped(points, matrix):
    homogeneous = np.column_stack([points, np.ones(len(points))]) @ matrix.T
    return (homogeneous[:, :2] / homogeneous[:, 2:]).astype(np.float32)


def primary_source(quad):
    q = np.asarray(quad, np.float32)
    a, b, c = q[:3]
    ab, ac = b - a, c - a
    anticlock = float(ab[0] * ac[1] - ab[1] * ac[0]) < 0
    target = [[384, 0], [0, 0], [0, 384], [384, 384]] if anticlock else [
        [0, 0], [384, 0], [384, 384], [0, 384]]
    return cv2.getPerspectiveTransform(q, np.asarray(target, np.float32))


def maximum_consistent_frames(rows):
    valid = [row for row in rows if row['accepted']]
    best = []
    for count in range(1, len(valid) + 1):
        for group in itertools.combinations(valid, count):
            if all(quad_iou(np.asarray(a['quad'], np.float32), np.asarray(b['quad'], np.float32)) >= .5
                   for a, b in itertools.combinations(group, 2)):
                if len(group) > len(best):
                    best = list(group)
    return [row['frame_index'] for row in best]


def main(root):
    root = Path(root).resolve()
    root.mkdir(parents=True, exist_ok=False)
    process = psutil.Process()
    started = time.perf_counter()
    report = dict(complete=False, failure=None, queries=[], identity_scores=0,
                  neural_inferences=0, http_requests=0,
                  scope='Windows exposed device geometry prerequisite; not recognition or Pi timing')
    samples = []

    def check(startup=False):
        memory = process.memory_info()
        observation = dict(wall_s=time.perf_counter()-started, rss=memory.rss,
                           peak_wset=getattr(memory, 'peak_wset', None),
                           available=psutil.virtual_memory().available,
                           cpu_s=sum(process.cpu_times()[:2]))
        samples.append(observation)
        fault = resource_fault(observation['available'], memory.rss, startup=startup)
        if fault is not None:
            raise MemoryError('Frozen resource limit (' + fault + '): ' + json.dumps(observation))
        if observation['wall_s'] > 600:
            raise TimeoutError('600-second frozen budget')
        if (root / 'STOP').exists():
            raise InterruptedError('Local STOP requested')
        return observation

    try:
        check(startup=True)
        cv2.setNumThreads(1)
        parent = APP / 'runtime/terminal-rotation-six-20261101'
        plan = json.loads((parent / 'protocol.json').read_text())
        items = [item for item in plan['items'] if item['domain'] == 'device']
        if [item['label'] for item in items] != ['D1', 'D2', 'D3', 'D4']:
            raise ValueError('Original fixed four-image panel changed')
        template_files = plan['templates_sha256']['device']
        if len(template_files) != 11:
            raise ValueError('Expected complete 11-identity gallery')
        public = APP / 'runtime/smpd-v27-continuation-20261031-r1'
        public_before = {str(public / name): sha(public / name) for name in ['status.json', 'STOP']}
        if json.loads((public / 'status.json').read_text())['state'] != 'paused_STOP':
            raise ValueError('Public evaluation must remain stopped')
        parameters = dict(query_long_side_cap=1536, query_normalization='existing 1st/99th percentile',
            query_descriptor='existing RootSIFT, max1000, contrast .02, edge10',
            query_pixel_scale='native gray uniformly resized, no crop or learned ROI',
            query_point_coordinates='mapped through frozen primary matrix only for existing fit bounds',
            enrollment_descriptor='unchanged primary 384px SIFT, all original five frames',
            registration='existing .85 mutual ratio, seeded similarity, original scale/angle/coverage gates',
            anchor_overlap='measured, not used to discard global observational fits',
            consistency_iou=.5, min_distinct_enrollment_frames=2,
            gate='both device errors must have >=2 consistent true-frame fits and no wrong identity with >=2; otherwise no recognition integration',
            retry=False, resume=False, identity_scoring=False)
        paths = [Path(__file__), APP / 'registered_matcher.py', APP / 'pklnet_roi.py',
                 APP / 'lossless_template_store.py', APP / 'union_lossless_codec.py',
                 APP / 'tools/halfturn_roi_recovery.py', APP / 'tools/experiment_resource_limits.py']
        protocol = dict(parameters=parameters, resources=dict(start_GiB=12, running_GiB=2, rss_GiB=14),
            parent_sha256=sha(parent / 'protocol.json'), items=items,
            template_sha256=template_files, source_sha256={str(p): sha(p) for p in paths},
            public_boundary=public_before, model_setting='gpt-6.1-sol; developer identifier only')
        save(root / 'protocol.json', protocol)
        shutil.copyfile(__file__, root / 'executed-driver.py')
        print(json.dumps(dict(stage='locked', parameters=parameters)), flush=True)
        gallery = {}
        for source, expected in template_files.items():
            check()
            path = Path(source)
            if sha(path) != expected:
                raise ValueError('Frozen enrollment bytes changed')
            user = path.name.removesuffix('.union2.npz')
            features, metadata = LosslessTemplateStore(path.parent).load(user)
            if len(features) != 5:
                raise ValueError('Original five enrollment frames required')
            gallery[user] = []
            for feature in features:
                primary = decode(feature, decode_native=False).parts[1]
                gallery[user].append((primary[4].copy(), primary[5].copy()))
            del features, feature, primary
        if len(gallery) != 11 or sum(map(len, gallery.values())) != 55:
            raise ValueError('Gallery incomplete')
        for item in items:
            check()
            tick = time.perf_counter()
            row = item['row']
            if sha(row['original']) != row['sha256']:
                raise ValueError('Frozen original image changed')
            baseline = json.loads((parent / 'device/baseline/records' / (item['label'] + '.json')).read_text())
            with Image.open(row['original']) as encoded:
                rgb = np.asarray(ImageOps.exif_transpose(encoded).convert('RGB'))
            if hashlib.sha256(rgb.tobytes()).hexdigest() != baseline['capture']['decoded_rgb_sha256']:
                raise ValueError('Original decoding differs from fixed baseline')
            gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
            height, width = gray.shape
            scale = min(1., 1536 / max(width, height))
            size = (round(width * scale), round(height * scale))
            resized = cv2.resize(gray, size, interpolation=cv2.INTER_AREA) if scale < 1 else gray
            descriptor_tick = time.perf_counter()
            points, descriptors = local_features(normalize_roi_pixels(resized))
            descriptor_ms = (time.perf_counter() - descriptor_tick) * 1000
            source_matrix = primary_source(baseline['primary']['quad'])
            native_points = points / np.asarray([size[0]/width, size[1]/height], np.float32)
            canonical_points = mapped(native_points, source_matrix)
            left = canonical_points, descriptors
            fits = []
            corners = np.asarray([[0, 0], [384, 0], [384, 384], [0, 384]], np.float32)
            anchor = cv2.convexHull(np.asarray(baseline['primary']['quad'], np.float32)).reshape(4, 2)
            for user, frames in sorted(gallery.items()):
                for index, target in enumerate(frames):
                    check()
                    diagnostic = {}
                    try:
                        matrix = registration(left, target, diagnostics=diagnostic)
                    except Exception:
                        report['registration_failure'] = dict(label=item['label'], identity=user,
                            frame_index=index, accepted=None, reason=None, registration=diagnostic)
                        raise
                    fit = dict(identity=user, frame_index=index, accepted=False)
                    fit['registration'] = diagnostic
                    if matrix is None:
                        fit['reason'] = 'existing_correspondence_or_geometry_gate'
                    else:
                        transform = matrix @ source_matrix
                        quad = mapped(corners, np.linalg.inv(transform))
                        bounded = bool(np.isfinite(quad).all() and (quad >= 1).all()
                            and (quad[:, 0] < width-1).all() and (quad[:, 1] < height-1).all())
                        fit.update(matrix=transform.tolist(), quad=quad.tolist(),
                            accepted=bounded, reason='valid_source_bounds' if bounded else 'sampling_bounds',
                            primary_iou=quad_iou(cv2.convexHull(quad).reshape(4, 2), anchor))
                    fits.append(fit)
            consistent = {u: maximum_consistent_frames([f for f in fits if f['identity'] == u]) for u in gallery}
            truth = row['identity'].replace(':', '-')
            wrong_support = max((len(v) for u, v in consistent.items() if u != truth), default=0)
            record = dict(label=item['label'], role=item['role'], sample=row['sample'],
                baseline_outcome=baseline['outcome'], query_size=[width, height], sift_size=list(size),
                keypoints=len(points), descriptor_ms=descriptor_ms,
                total_geometry_ms=(time.perf_counter() - tick) * 1000,
                attempted_registrations=len(fits), fits=fits, consistent_frames=consistent,
                true_consistent_frames=len(consistent[truth]), maximum_wrong_consistent_frames=wrong_support,
                geometry_prerequisite=len(consistent[truth]) >= 2 and wrong_support < 2)
            report['queries'].append(record)
            save(root / 'results.json', report)
            print(json.dumps({k: record[k] for k in ['label', 'keypoints', 'descriptor_ms',
                'total_geometry_ms', 'true_consistent_frames', 'maximum_wrong_consistent_frames',
                'geometry_prerequisite']}), flush=True)
        errors = [q for q in report['queries'] if q['baseline_outcome'] == 'wrong_identity_accepted']
        report['eligible_for_recognition_pilot'] = len(errors) == 2 and all(q['geometry_prerequisite'] for q in errors)
        report['original_templates_unchanged'] = all(sha(path) == expected for path, expected in template_files.items())
        report['original_images_unchanged'] = all(sha(i['row']['original']) == i['row']['sha256'] for i in items)
        report['public_boundary_unchanged'] = all(sha(path) == expected for path, expected in public_before.items())
        report['complete'] = all(report[k] for k in ['original_templates_unchanged',
            'original_images_unchanged', 'public_boundary_unchanged'])
    except Exception as error:
        report.update(failure=type(error).__name__ + ': ' + str(error), traceback=traceback.format_exc())
    finally:
        report['resources'] = dict(final=check_final(process, started),
            peak_sampled_rss=max((s['rss'] for s in samples), default=0),
            min_sampled_available=min((s['available'] for s in samples), default=0))
        report['wall_s'] = time.perf_counter() - started
        save(root / 'results.json', report)
        print(json.dumps({k: report.get(k) for k in ['complete', 'failure', 'eligible_for_recognition_pilot', 'wall_s']}), flush=True)
    return 0 if report['complete'] else 1


def check_final(process, started):
    memory = process.memory_info()
    return dict(wall_s=time.perf_counter()-started, rss=memory.rss,
                peak_wset=getattr(memory, 'peak_wset', None),
                available=psutil.virtual_memory().available,
                cpu_s=sum(process.cpu_times()[:2]))


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1]))
