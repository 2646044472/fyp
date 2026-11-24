"""Require exact score parity for all pairs after compact prepared-template optimization."""
import json,time,sys
from pathlib import Path
import numpy as np
from PIL import Image
APP=Path(__file__).resolve().parents[1];sys.path.insert(0,str(APP))
from palm_app.biometric import load_algorithm
root=Path(sys.argv[1]);base=root/'single-device';out=base/'speed-v5';out.mkdir(exist_ok=True)
records=json.loads((root/'stability/records.json').read_text());algorithm=load_algorithm(APP/'vendor/palmprint-recognition-python','FastCCDemo-v6')
previous=load_algorithm(APP/'vendor/palmprint-recognition-python','FastCCAnchoredUnion-v5')
expected=np.load(base/'runtime-v5/distances.npy');gallery=[]
enrollment_ms=[]
for r in records:
    directory='new-runtime-consistent' if r['cohort']=='new' else 'old-runtime-consistent'
    roi=np.asarray(Image.open(root/directory/'rois'/r['sample']/'illumination/roi_128.png').convert('L'))
    tick=time.perf_counter()
    feature=algorithm.extract_gallery_with_context(Image.open(r['original']).convert('RGB'),r['illumination']['details']['roi_quad_full'],roi)
    enrollment_ms.append((time.perf_counter()-tick)*1000)
    with np.load(base/'runtime-v5'/(r['sample']+'.npz'),allow_pickle=False) as z:
        old=previous.prepare_enrollment([z['feature']])[0]
    new=algorithm.prepare_enrollment([feature])[0]
    # Each descriptor/bank required by scoring must be identical after skipping
    # query-only work at enrollment, for every image including reverse splits.
    for a,b in [(old[1][0],new[1][0]),(old[1][4],new[1][4]),(old[1][5],new[1][5]),*zip(old[2],new[2])]:np.testing.assert_array_equal(a,b)
    for a,b in zip(old[4],new[4]):
        for x,y in zip(a,b):np.testing.assert_array_equal(x,y)
    np.savez_compressed(out/(r['sample']+'.npz'),feature=feature)
    with np.load(out/(r['sample']+'.npz'),allow_pickle=False) as z:gallery.append(algorithm.prepare_enrollment([z['feature']])[0])
times=[];diff=[];started=time.perf_counter()
for i,r in enumerate(records):
    with np.load(base/'runtime-v5'/(r['sample']+'.npz'),allow_pickle=False) as z:f=z['feature']
    f[:4]=np.asarray([algorithm.magic],'<i4').view(np.uint8);query=algorithm.prepare_probe(f)
    indices=[j for j,g in enumerate(records) if i!=j and r['cohort']==g['cohort']]
    def compute(j):
        t=time.perf_counter();actual=algorithm._match_unpacked(query,gallery[j]);return j,actual,(time.perf_counter()-t)*1000
    for j,actual,elapsed in algorithm._workers.map(compute,indices):
        times.append(elapsed)
        if actual!=expected[i,j]:diff.append(dict(query=i,gallery=j,before=float(expected[i,j]),after=actual))
    if (i+1)%10==0:print(i+1,round(time.perf_counter()-started,1),flush=True)
result=dict(pairs=len(times),differences=diff,enrollment_extraction_ms_median=float(np.median(enrollment_ms)),prepared_gallery_bytes=algorithm.prepared_bytes(gallery),pair_ms_median=float(np.median(times)),pair_ms_p95=float(np.percentile(times,95)),seconds=time.perf_counter()-started)
(out/'prepared-parity-parallel.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
algorithm.close()
assert not diff
