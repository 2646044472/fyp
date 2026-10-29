"""Frozen experimental matcher audit on unchanged development splits, not holdout validation."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
import numpy as np

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP))
from biometric import load_algorithm
from indexed_demo_matcher import IndexedDemoMatcher, IndexedProbe


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--smoke', action='store_true', help='Only original/reverse; not the full split audit')
    parser.add_argument('--cache-exhaustive-pairs', action='store_true', help='Offline only: reuse exact frozen query/gallery pair scores across splits; timings are not latency')
    parser.add_argument('--matcher', default='FastCCIndexed-v7-experimental',
                        choices=['FastCCIndexed-v7-experimental','FastCCProposedIndex-v8-experimental','FastCCGuardedIndex-v9-experimental','FastCCStagedIndex-v10-experimental','FastCCLinkedEnrollment-v12-experimental'])
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    base = args.root/'single-device'
    rows = json.loads((args.root/'stability/records.json').read_text())
    cases = json.loads((base/'runtime-v5/results.json').read_text())
    if args.smoke:
        cases = [c for c in cases if c['case'].endswith(('_original','_reverse'))]
    lookup = {r['sample']:i for i,r in enumerate(rows)}
    algorithm = load_algorithm(APP/'vendor/palmprint-recognition-python',args.matcher)
    protocol = dict(algorithm=algorithm.name, code_sha256=hashlib.sha256((APP/'indexed_demo_matcher.py').read_bytes()).hexdigest(),
                    exhaustive_pair_cache=args.cache_exhaustive_pairs,
                    development_images=80, independent_holdout=False, parameters_selected_on_development=True,
                    cases=len(cases), source='unchanged v5 localization and enrollment descriptors; no query identity in extraction/matching',
                    limitation='Cached geometry/descriptor audit; not a live end-to-end latency measurement')
    protocol['source_sha256'] = {name:hashlib.sha256((APP/name).read_bytes()).hexdigest()
        for name in ('indexed_demo_matcher.py','proposed_index_matcher.py','guarded_index_matcher.py','staged_index_matcher.py','linked_enrollment_matcher.py','registration_accelerated.py',
                     'registered_matcher.py','fastcc_accelerated.py') if (APP/name).exists()}
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2))
    gallery, probes = [], []
    for row in rows:
        assert hashlib.sha256(Path(row['original']).read_bytes()).hexdigest() == row['sha256']
        with np.load(base/'runtime-v5'/(row['sample']+'.npz'), allow_pickle=False) as z:
            feature = z['feature']
        feature[:4] = np.asarray([algorithm.magic],'<i4').view(np.uint8)
        q = algorithm._unpack(feature)
        gallery.append(algorithm.prepare_enrollment([feature])[0])
        probe=IndexedProbe(q[1][0].copy(),q[1][2].copy(),q[3])
        if getattr(algorithm,'requires_exhaustive_fallback',False):
            def exhaustive(path=base/'runtime-v5'/(row['sample']+'.npz')):
                with np.load(path,allow_pickle=False) as z:
                    full=z['feature']
                full[:4]=np.asarray([algorithm.magic],'<i4').view(np.uint8)
                return full
            probe.exhaustive=exhaustive
        probes.append(probe)
    results = []
    pair_cache, active_query = {}, [None]
    if args.cache_exhaustive_pairs:
        if not getattr(algorithm, 'requires_exhaustive_fallback', False):
            raise ValueError('Pair reuse supports exhaustive fallback matchers only')
        # Gallery objects are strongly retained for the entire audit. Query IDs
        # identify immutable, SHA-checked extraction inputs, never true labels.
        target_ids = {id(sample[3]): i for i,sample in enumerate(gallery)}
        original_pair = algorithm._match_unpacked
        def frozen_pair(query, target):
            key = active_query[0], target_ids[id(target)]
            if key not in pair_cache:
                pair_cache[key] = original_pair(query, target)
            return pair_cache[key]
        algorithm._match_unpacked = frozen_pair
    try:
        for case in cases:
            groups = {k:[gallery[lookup[s]] for s in ids] for k,ids in case['gallery'].items()}
            tick = time.perf_counter()
            algorithm.prepare_gallery(groups)
            index_ms = (time.perf_counter()-tick)*1000
            trials = []
            for trial in case['trials']:
                assert all(trial['sample'] not in ids for ids in case['gallery'].values())
                probe = probes[lookup[trial['sample']]]
                active_query[0] = lookup[trial['sample']]
                tick = time.perf_counter()
                scores = algorithm.score_gallery(probe,groups)
                correct = scores[trial['identity']] < min(v for k,v in scores.items() if k!=trial['identity'])
                trials.append(dict(sample=trial['sample'],identity=trial['identity'],correct=correct,
                                   scores=scores,route=probe.route,ms=(time.perf_counter()-tick)*1000))
            result = dict(case=case['case'],gallery=case['gallery'],correct=sum(t['correct'] for t in trials),
                          total=len(trials),index_ms=index_ms,trials=trials)
            results.append(result)
            (args.output/'results.json').write_text(json.dumps(results,indent=2))
            print(case['case'],result['correct'],'/',result['total'],flush=True)
    finally:
        algorithm.close()
    summary = {cohort:dict(cases=len(values),min=min(values),max=max(values),mean=float(np.mean(values)))
               for cohort in ('new','old')
               if (values:=[r['correct'] for r in results if r['case'].startswith(cohort+'_')])}
    (args.output/'summary.json').write_text(json.dumps(summary,indent=2))
    (args.output/'pair-cache.json').write_text(json.dumps(dict(enabled=args.cache_exhaustive_pairs,
        pairs=len(pair_cache), offline_only=True, runtime_query_cache=False),indent=2))
    print(json.dumps(summary),flush=True)


if __name__ == '__main__':
    main()
