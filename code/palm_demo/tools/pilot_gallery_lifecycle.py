"""One non-resumable CPU real-gallery lifetime experiment; zero query requests.

Copies the frozen 86-identity gallery, measures normal preparation and index
ownership, then checks collection after the epoch frame returns. No inference
backend, production policy, enrolled image or existing experiment is modified.
"""
import gc
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import threading
import time
import traceback
import weakref

APP = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(APP), str(APP / 'tools')]
import psutil
from experiment_resource_limits import resource_fault


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def save(path, value):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2), encoding='utf-8')
    temporary.replace(path)


def main(root):
    root = Path(root).resolve()
    root.mkdir(parents=True, exist_ok=False)
    process = psutil.Process()
    started = time.perf_counter()
    phase = ['preflight']
    stop = threading.Event()
    violations = []
    samples = []
    report = dict(complete=False, scope='Windows CPU real-gallery lifecycle only',
                  query_requests=0, fresh_enrollment_attempts=0, identity_scores=0,
                  limits=dict(start_free_GiB=12, running_free_GiB=2, max_RSS_GiB=14,
                              max_wall_seconds=600), phases=[], failure=None)

    def sample():
        info = process.memory_info()
        return dict(elapsed_s=time.perf_counter() - started, phase=phase[0],
                    rss=info.rss, private=getattr(info, 'private', None),
                    peak_wset=getattr(info, 'peak_wset', None),
                    available=psutil.virtual_memory().available,
                    cpu_s=sum(process.cpu_times()[:2]))

    def check(startup=False):
        value = sample()
        fault = resource_fault(value['available'], value['rss'], startup=startup)
        if fault is not None:
            raise MemoryError('Frozen resource limit (' + fault + '): ' + json.dumps(value))
        if violations:
            raise MemoryError('Sampler observed resource limit: ' + json.dumps(violations[0]))
        if value['elapsed_s'] > 600:
            raise TimeoutError('Frozen 600-second wall budget')
        if (root / 'STOP').exists():
            raise InterruptedError('Local STOP requested')
        return value

    def mark(name, **fields):
        phase[0] = name
        value = dict(sample(), **fields)
        report['phases'].append(value)
        save(root / 'status.json', dict(state=name, **value))
        print(json.dumps(value), flush=True)
        return value

    def watch():
        with (root / 'telemetry.jsonl').open('x', encoding='utf-8') as stream:
            while not stop.is_set():
                value = sample()
                samples.append(value)
                stream.write(json.dumps(value) + '\n')
                stream.flush()
                if resource_fault(value['available'], value['rss']) is not None:
                    violations.append(value)
                stop.wait(1)

    def public_boundary():
        folder = APP / 'runtime/smpd-v27-continuation-20261031-r1'
        status = json.loads((folder / 'status.json').read_text())
        if (status['state'] != 'paused_STOP' or status['completed_queries'] != 1239
                or not (folder / 'STOP').exists() or (folder / 'inflight.json').exists()):
            raise RuntimeError('Frozen public STOP boundary changed')
        return {str(folder / name): sha(folder / name) for name in ['status.json', 'STOP']}

    worker = None
    try:
        mark('startup_gate', measurement=check(startup=True))
        paused = public_boundary()
        parent = APP / 'runtime/terminal-rotation-six-20261101/protocol.json'
        protocol = json.loads(parent.read_text())
        original_files = protocol['templates_sha256']['public']
        if len(original_files) != 86:
            raise ValueError('Expected exactly 86 frozen template containers')
        sources = {str(APP / name): sha(APP / name) for name in [
            'gallery.py', 'demo_flow.py', 'indexed_demo_matcher.py',
            'palm_app/debug_ui.py', 'tools/pilot_epoch_cleanup.py',
            'tools/experiment_resource_limits.py',
            'tools/pilot_gallery_lifecycle.py']}
        own_protocol = dict(scope=report['scope'], parent_protocol_sha256=sha(parent),
                            source_sha256=sources, model_sha256=protocol['models_sha256'],
                            template_sha256=original_files, paused_boundary=paused,
                            resources=report['limits'], executable=sys.executable,
                            localizer_priming_inferences=0, query_requests=0,
                            gallery_embedding_inferences='normal loader, counted below',
                            reuse_original_five_frames=True, retry=False, resume=False)
        save(root / 'protocol.json', own_protocol)
        shutil.copyfile(__file__, root / 'executed-driver.py')
        worker = threading.Thread(target=watch, name='low-load-resource-sampler', daemon=True)
        worker.start()
        mark('copying_frozen_templates')
        templates = root / 'evaluation/runtime/demo_templates'
        templates.mkdir(parents=True)
        for source, expected in original_files.items():
            check()
            if sha(source) != expected:
                raise ValueError('Frozen original template changed: ' + source)
            destination = templates / Path(source).name
            shutil.copyfile(source, destination)
            if sha(destination) != expected:
                raise ValueError('Copied template differs: ' + source)
        for path, expected in protocol['models_sha256'].items():
            if sha(path) != expected:
                raise ValueError('Frozen model changed: ' + path)
        mark('imports_and_sessions')
        import cv2
        cv2.setNumThreads(1)
        from evaluate_raw_smpd import ExifReplay, install_windows_capacity
        from pklnet_roi import PKLNetROI
        from palm_app import debug_ui
        from lossless_union_matcher import LosslessUnionMatcher
        from gallery import Gallery
        from compnet_pilot import CompNetPilot
        from retained_evidence_pilot import install_retained_evidence_pilot
        from terminal_rf_evidence import install
        from pilot_epoch_cleanup import collect_finished_epoch
        report['windows_capacity'] = install_windows_capacity()
        install_retained_evidence_pilot()
        os.environ['PALM_COMPNET_MODEL_ROOT'] = protocol['model_root']
        old_load = Gallery._load_prepared
        old_extract = CompNetPilot.extract
        load_count = [0]
        embeddings = [0]

        def observed_load(self, user):
            check()
            value = old_load(self, user)
            load_count[0] += 1
            check()
            if load_count[0] % 10 == 0:
                mark('gallery_loading', loaded_identities=load_count[0],
                     gallery_embedding_inferences=embeddings[0])
            return value

        def observed_embedding(self, image):
            check()
            value = old_extract(self, image)
            embeddings[0] += 1
            check()
            return value

        Gallery._load_prepared = observed_load
        CompNetPilot.extract = observed_embedding
        check(startup=True)
        epoch_start = sample()
        mark('epoch_started')

        def epoch():
            engine = PKLNetROI(threads=3)
            engine._ensure_loaded()
            if engine._session.get_providers() != ['CPUExecutionProvider']:
                raise ValueError('Expected CPU-only localizer')
            camera = ExifReplay(False, engine)
            debug_ui.common.RUNTIME = root / 'evaluation/runtime'
            app = debug_ui.App(camera, demo_matcher=LosslessUnionMatcher.name)
            app.demo_algorithm._retain_fastcc_evidence_pilot = True
            install(app.demo_algorithm)
            if app.demo_algorithm.encoder.session.get_providers() != ['CPUExecutionProvider']:
                raise ValueError('Expected CPU-only gallery encoder')
            cache = app.demo.gallery._prepared_cache
            if len(cache) != 86 or any(len(entry[1]) != 5 for entry in cache.values()):
                raise ValueError('Incomplete original 86 x 5 gallery')
            if embeddings[0] != 430 or load_count[0] != 86:
                raise ValueError('Unexpected gallery embedding/preparation count')
            if set(app.demo_algorithm._references) != set(cache):
                raise ValueError('Index does not own the complete gallery')
            # As in the original driver, keep a handler closure and last entry
            # in the epoch frame. No socket, HTTP server or request is created.
            handler = debug_ui.make_handler(app)
            for entry in cache.values():
                if len(entry[1]) != 5:
                    raise ValueError('Enrollment frame count changed')
            refs = dict(app=weakref.ref(app), algorithm=weakref.ref(app.demo_algorithm),
                        localizer=weakref.ref(engine),
                        localizer_session=weakref.ref(engine._session),
                        embedding_session=weakref.ref(app.demo_algorithm.encoder.session),
                        last_frame_array=weakref.ref(entry[1][-1][0]))
            mark('gallery_ready', identities=86, enrollment_frames=430,
                 gallery_embedding_inferences=embeddings[0],
                 prepared_cache_bytes=app.demo.gallery._prepared_cache_bytes)
            check()
            app.demo_algorithm.close()
            app.demo.gallery._prepared_cache.clear()
            app.demo_algorithm._references = None
            app.demo_algorithm._index = None
            app.demo_algorithm.score_gallery = None
            del cache, app, engine, camera
            mark('closed_inside_epoch', collected_objects=gc.collect(),
                 weakrefs_alive={name: ref() is not None for name, ref in refs.items()})
            return refs

        references = epoch()
        mark('epoch_returned', weakrefs_alive={k: r() is not None for k, r in references.items()})
        receipt = collect_finished_epoch()
        after = mark('post_return_gc', cleanup=receipt,
                     weakrefs_alive={k: r() is not None for k, r in references.items()},
                     would_pass_next_startup_gate=psutil.virtual_memory().available >= 12 * 1024**3)
        check()
        report.update(identities_loaded=86, enrollment_frames_loaded=430,
                      gallery_embedding_inferences=embeddings[0], localizer_inferences=0,
                      epoch_wall_s=after['elapsed_s'] - epoch_start['elapsed_s'],
                      epoch_cpu_s=after['cpu_s'] - epoch_start['cpu_s'],
                      weakrefs_all_released=all(r() is None for r in references.values()),
                      post_gc_would_pass_next_startup_gate=after['would_pass_next_startup_gate'])
        Gallery._load_prepared = old_load
        CompNetPilot.extract = old_extract
        mark('verifying_originals')
        report['original_templates_unchanged'] = all(sha(path) == expected for path, expected in original_files.items())
        report['public_stop_boundary_unchanged'] = public_boundary() == paused
        report['complete'] = report['original_templates_unchanged'] and report['public_stop_boundary_unchanged']
    except Exception as error:
        report['failure'] = type(error).__name__ + ': ' + str(error)
        report['traceback'] = traceback.format_exc()
    finally:
        stop.set()
        if worker is not None:
            worker.join(timeout=3)
        final = sample()
        samples.append(final)
        report['telemetry'] = dict(samples=len(samples), interval_s=1,
            min_available=min(s['available'] for s in samples),
            peak_sampled_rss=max(s['rss'] for s in samples),
            peak_process_wset=final['peak_wset'], violations=violations,
            final=final)
        report['wall_s'] = time.perf_counter() - started
        save(root / 'results.json', report)
        save(root / 'status.json', dict(state='complete' if report['complete'] else 'failed',
                                      failure=report['failure'], elapsed_s=report['wall_s']))
        print(json.dumps({k: report.get(k) for k in ['complete', 'failure', 'wall_s',
              'identities_loaded', 'enrollment_frames_loaded', 'weakrefs_all_released',
              'post_gc_would_pass_next_startup_gate']}), flush=True)
    return 0 if report['complete'] else 1


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1]))
