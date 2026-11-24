"""Compare CPU thread overhead without changing any ROI or descriptor settings."""
import json,time,sys
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
APP=Path(__file__).resolve().parents[1];sys.path.insert(0,str(APP))
from palm_app.biometric import load_algorithm
root=Path(sys.argv[1]);out=root/'single-device/speed-v5';out.mkdir(exist_ok=True)
records=json.loads((root/'stability/records.json').read_text());selected=[records[0],records[40]]
base={r['sample']:r for c in ['new','old'] for r in json.loads((root/f'consistency-{c}/records.json').read_text())}
windows={r['sample']:r['candidates'] for r in json.loads((root/'single-device/localizer-windows/candidates.json').read_text())}
algorithm=load_algorithm(APP/'vendor/palmprint-recognition-python','FastCCAnchoredUnion-v5');default=cv2.getNumThreads();results=[]
try:
    for r in selected:
        image=Image.open(r['original']).convert('RGB');directory='new-runtime-consistent' if r['cohort']=='new' else 'old-runtime-consistent'
        roi=np.asarray(Image.open(root/directory/'rois'/r['sample']/'illumination/roi_128.png').convert('L'))
        candidates=[base[r['sample']]['variants'][k] for k in ['v4','gamma']]+[dict(h,kind='window') for h in windows[r['sample']]]
        reference=None
        for threads in dict.fromkeys([default,1,2,4]):
            cv2.setNumThreads(threads)
            for repeat in range(2):
                t=time.perf_counter();f=algorithm.extract_with_hypotheses(image,r['illumination']['details']['roi_quad_full'],roi,candidates);ms=(time.perf_counter()-t)*1000
                if reference is None:reference=f.copy()
                equal=np.array_equal(reference,f)
                results.append(dict(cohort=r['cohort'],sample=r['sample'],threads=threads,repeat=repeat,ms=ms,identical=equal));print(results[-1],flush=True)
finally:cv2.setNumThreads(default)
(out/'thread-profile.json').write_text(json.dumps(dict(default_threads=default,results=results),indent=2))
