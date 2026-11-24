"""Byte-compare all parallel query templates with the serial v5 implementation."""
import sys,json,time
from pathlib import Path
import numpy as np
from PIL import Image
APP=Path(__file__).resolve().parents[1];sys.path.insert(0,str(APP))
from palm_app.biometric import load_algorithm
root=Path(sys.argv[1]);base=root/'single-device';rows=json.loads((root/'stability/records.json').read_text())
original={r['sample']:r for c in ['new','old'] for r in json.loads((root/f'consistency-{c}/records.json').read_text())}
windows={r['sample']:r['candidates'] for r in json.loads((base/'localizer-windows/candidates.json').read_text())}
changed={r['sample'] for r in json.loads((base/'fresh-v4/results.json').read_text()) if not r['identical']}
fast=load_algorithm(APP/'vendor/palmprint-recognition-python','FastCCDemo-v6');serial=load_algorithm(APP/'vendor/palmprint-recognition-python','FastCCAnchoredUnion-v5');results=[]
for i,r in enumerate(rows):
    image=Image.open(r['original']).convert('RGB');directory='new-runtime-consistent' if r['cohort']=='new' else 'old-runtime-consistent'
    roi=np.asarray(Image.open(root/directory/'rois'/r['sample']/'illumination/roi_128.png').convert('L'));q=r['illumination']['details']['roi_quad_full']
    hypotheses=[original[r['sample']]['variants'][k] for k in ['v4','gamma']]+[dict(h,kind='window') for h in windows[r['sample']]]
    tick=time.perf_counter();actual=fast.extract_with_hypotheses(image,q,roi,hypotheses);ms=(time.perf_counter()-tick)*1000
    if r['sample'] in changed:expected=serial.extract_with_hypotheses(image,q,roi,hypotheses)
    else:
        with np.load(base/'runtime-v5'/(r['sample']+'.npz'),allow_pickle=False) as z:expected=z['feature']
    expected[:4]=np.asarray([fast.magic],'<i4').view(np.uint8)
    same=np.array_equal(actual,expected);results.append(dict(sample=r['sample'],identical=same,ms=ms));print(i+1,same,round(ms),flush=True)
fast.close();(base/'speed-v5/parallel-extraction.json').write_text(json.dumps(results,indent=2));assert all(r['identical'] for r in results)
