"""Fixed mixed-camera enrollment controls on cached, disjoint sample distances.

This is development-data sensitivity analysis, not an independent validation.
No images, runtime templates, matching rules, or labels are changed.
"""
import argparse
import json
from pathlib import Path

import numpy as np

from audit_matcher_stability import evaluate, save


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stability', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    records = json.loads((args.stability / 'records.json').read_text())
    with np.load(args.stability / 'distances.npz') as cached:
        matrices = {k: cached[k] for k in cached.files}
    identities = sorted({r['canonical_identity'] for r in records})
    pool = {c: {k: [i for i, r in enumerate(records)
                    if r['cohort'] == c and r['canonical_identity'] == k and r['index'] <= 5]
                for k in identities} for c in ['old', 'new']}
    queries = {c: [i for i, r in enumerate(records) if r['cohort'] == c and r['index'] > 5]
               for c in pool}
    save(args.output / 'plan.json', dict(
        source=str(args.stability), enrollment_pool='indices 1-5 only; query indices 6-10 from each camera',
        gallery_sizes=[[5, 0], [0, 5], [3, 2], [2, 3], [5, 5]],
        selection='first k, plus ten seeded choices from enrollment pool; no query scores used',
        seeds=list(range(2026102810, 2026102820)),
        caveat='Same 80 previously inspected images; mixed enrollment includes the query camera. '
               'This does not measure generalization to an unseen camera. Ten-template control is audit only.'))
    results = []
    for nold, nnew in [(5, 0), (0, 5), (3, 2), (2, 3), (5, 5)]:
        for seed in [None, *range(2026102810, 2026102820)]:
            rng = np.random.default_rng(seed)
            gallery = {}
            for identity in identities:
                gallery[identity] = []
                for cohort, count in [('old', nold), ('new', nnew)]:
                    ids = pool[cohort][identity]
                    chosen = ids[:count] if seed is None else sorted(map(int, rng.choice(ids, count, replace=False)))
                    gallery[identity].extend(chosen)
            for cohort in queries:
                case = f'old{nold}_new{nnew}_{cohort}_{seed if seed is not None else "first"}'
                rows = evaluate(records, matrices, case, gallery, queries[cohort])
                for row in rows:
                    row.update(old_templates=nold, new_templates=nnew, query_cohort=cohort, seed=seed)
                results.extend(rows)
    save(args.output / 'results.json', results)
    summary = []
    for nold, nnew in [(5, 0), (0, 5), (3, 2), (2, 3), (5, 5)]:
        for algorithm in matrices:
            for cohort in queries:
                rows = [r for r in results if r['old_templates'] == nold and r['new_templates'] == nnew
                        and r['algorithm'] == algorithm and r['query_cohort'] == cohort]
                random = [r['correct'] for r in rows if r['seed'] is not None]
                summary.append(dict(old_templates=nold, new_templates=nnew, algorithm=algorithm,
                                    query_cohort=cohort, first_correct=rows[0]['correct'], total=20,
                                    random_min=min(random), random_max=max(random), random_mean=float(np.mean(random))))
    save(args.output / 'summary.json', summary)
    print(json.dumps([r for r in summary if r['algorithm'] == 'FastCCPoseNearest-v1'], indent=2))


if __name__ == '__main__':
    main()
