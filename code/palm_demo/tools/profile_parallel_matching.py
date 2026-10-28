"""Measure exact matching parallelism on fixed examples without changing scores."""
import sys,json,time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import numpy as np
APP=Path(__file__).resolve().parents[1];sys.path.insert(0,str(APP))
from palm_app.biometric import load_algorithm
root=Path(sys.argv[1]);base=root/'single-device';records=json.loads((root/'stability/records.json').read_text())
a=load_algorithm(APP/'vendor/palmprint-recognition-python','FastCCDemo-v6');results=[]
for cohort in ['new','old']:
    rows=[r for r in records if r['cohort']==cohort];gallery=[]
    for r in rows:
        if r['index']>5:continue
        with np.load(base/'speed-v5'/(r['sample']+'.npz'),allow_pickle=False) as z:gallery.append(a.prepare_enrollment([z['feature']])[0])
    r=next(r for r in rows if r['index']==8)
    with np.load(base/'runtime-v5'/(r['sample']+'.npz'),allow_pickle=False) as z:f=z['feature']
    f[:4]=np.asarray([a.magic],'<i4').view(np.uint8);query=a.prepare_probe(f);reference=None
    for workers in [1,2,4]:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            for repeat in range(2):
                tick=time.perf_counter();scores=list(executor.map(lambda candidate:a._match_unpacked(query,candidate),gallery));ms=(time.perf_counter()-tick)*1000
                if reference is None:reference=scores
                same=np.array_equal(scores,reference);results.append(dict(cohort=cohort,workers=workers,repeat=repeat,ms=ms,identical=same));print(results[-1],flush=True)
(base/'speed-v5/parallel-profile.json').write_text(json.dumps(results,indent=2))
