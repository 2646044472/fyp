"""Fresh ONNX inference vs cached-geometry runtime templates, all 80 images."""
import hashlib
import json
from pathlib import Path
import sys
import time
import numpy as np
from PIL import Image

APP=Path(__file__).resolve().parents[1];sys.path.insert(0,str(APP))
from palm_app.biometric import load_algorithm
from pklnet_roi import PKLNetROI,normalize_roi

root=Path(sys.argv[1]);out=root/'single-device/fresh-v4';out.mkdir(exist_ok=False)
records=json.loads((root/'stability/records.json').read_text())
algorithm=load_algorithm(APP/'vendor/palmprint-recognition-python','FastCCWindowUnion-v4')
engine=PKLNetROI(threads=2);results=[]
for i,r in enumerate(records):
    assert hashlib.sha256(Path(r['original']).read_bytes()).hexdigest()==r['sha256']
    tick=time.perf_counter();image=Image.open(r['original']).convert('RGB')
    raw,quad,details=engine.extract(image)
    assert details['roi_geometry_valid']
    candidates=algorithm.complete_hypotheses(image,details['pklnet_roi_candidates'],engine)
    feature=algorithm.extract_with_hypotheses(image,quad,normalize_roi(raw)[0],candidates)
    ms=(time.perf_counter()-tick)*1000
    with np.load(root/'single-device/runtime-v4'/(r['sample']+'.npz'),allow_pickle=False) as saved:cached=saved['feature']
    same=np.array_equal(feature,cached)
    if not same:np.savez_compressed(out/(r['sample']+'.npz'),feature=feature)
    results.append(dict(sample=r['sample'],identical=same,changed_bytes=int(np.count_nonzero(feature!=cached)),
                        extraction_with_inference_ms=ms,valid_candidates=sum(c['valid'] for c in candidates),
                        feature_sha256=hashlib.sha256(feature.tobytes()).hexdigest()))
    (out/'results.json').write_text(json.dumps(results,indent=2))
    print(i+1,same,round(ms),flush=True)
summary=dict(images=len(results),identical=sum(r['identical'] for r in results),
             inference_plus_extraction_ms=dict(median=float(np.median([r['extraction_with_inference_ms'] for r in results])),p95=float(np.percentile([r['extraction_with_inference_ms'] for r in results],95))),
             caveat='Local CPU measurement, not Pi; nonidentical templates require complete distance reevaluation')
(out/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary),flush=True)
