"""Audit provenance, fixed protocol, baseline differences and runtime parity."""
import hashlib
import json
from pathlib import Path
import sys
import numpy as np

root=Path(sys.argv[1]); out=root/'single-device'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
records=read(root/'stability/records.json');lookup={r['sample']:r for r in records}
assert len(lookup)==80 and all(digest(Path(r['original']))==r['sha256'] for r in records)
paths=['runtime-v2/distances.npy','wide-context/distances.npz','roi-hypotheses/distances.npy',
       'coarse-structure/distances.npy','window-hypotheses/distances.npy','window-coarse-union/distances.npy']
provenance={p:digest(out/p) for p in paths}
v2=np.load(out/paths[0]);wide=np.load(out/paths[1]);roi=np.load(out/paths[2]);coarse=np.load(out/paths[3]);window=np.load(out/paths[4]);union=np.load(out/paths[5])
mask=np.isfinite(union)&~np.eye(80,dtype=bool)
np.testing.assert_array_equal(union,np.minimum(window,coarse))
assert np.all(roi[mask]<=wide['expanded_strict'][mask]) and np.all(window[mask]<=roi[mask]) and np.all(coarse[mask]<=roi[mask])
audit=dict(originals_unchanged=80,sources_sha256=provenance,
           union='min(window-hypotheses, coarse-structure) for every same-device pair, then mean best2 enrollment distances',
           baseline='v2 -> expanded_strict -> roi-hypotheses -> window/coarse union',
           base_full='separate control, not included in expanded_strict or union baseline',
           base_full_pairs_improved_vs_v2=int(np.sum(wide['base_full'][mask]<v2[mask])),
           base_full_pairs_still_better_than_union=int(np.sum(wide['base_full'][mask]<union[mask])),
           max_extra_base_full_improvement=float(np.max(np.maximum(union[mask]-wide['base_full'][mask],0))),
           label_use='Only evaluation aggregates distances by gallery identity. Feature extraction and pair matching receive pixels and geometry, no names/labels.',
           caveat='Development-selected methods and hyperparameters on repeatedly inspected data. No independent generalization evidence.')
baseline_cases={c['case']:c for c in read(out/'runtime-v3/results.json') if c['method']=='registered_best2'}
for case in baseline_cases.values():
    gallery={s for ids in case['gallery'].values() for s in ids};trials=case['trials']
    assert len(gallery)==20 and len(trials)==20
    for t in trials:
        assert t['sample'] not in gallery
        assert all(lookup[s]['cohort']==lookup[t['sample']]['cohort'] for s in gallery)
audit['unchanged_cases']=len(baseline_cases)
if (out/'runtime-v4/results.json').exists():
    runtime=np.load(out/'runtime-v4/distances.npy');differences=np.abs(runtime[mask]-union[mask])
    audit['runtime_parity']=dict(pairs=int(mask.sum()),different_pairs=int(np.sum(differences>1e-12)),max_abs_difference=float(differences.max()))
    cases=[c for c in read(out/'runtime-v4/results.json') if c['method']=='registered_best2']
    assert len(cases)==len(baseline_cases)
    for c in cases:
        b=baseline_cases[c['case']]
        assert c['gallery']==b['gallery']
        assert [(t['sample'],t['identity']) for t in c['trials']]==[(t['sample'],t['identity']) for t in b['trials']]
    audit['runtime_cases_verified']=len(cases)
(out/'union-audit.json').write_text(json.dumps(audit,indent=2))
print(json.dumps(audit,indent=2))
