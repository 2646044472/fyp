"""Predetermined synthetic blur diagnostic; not a real-camera success-rate claim."""
import csv
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw
import onnxruntime as ort
import torch

APP=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(APP));sys.path.insert(0,str(APP/'vendor/palmprint-recognition-python'))
from pklnet_roi import normalize_roi
from palmprint.algorithms.don import DoNAlgorithm


def run(root, experiment, backend='onnx'):
    spec=importlib.util.spec_from_file_location('trained_data',experiment/'palmir/data.py')
    data=importlib.util.module_from_spec(spec);spec.loader.exec_module(data)
    torch.set_num_threads(2)
    out=root/('audit/blur_probe_pytorch' if backend=='pytorch' else 'audit/blur_probe');out.mkdir(exist_ok=True)
    conditions={
        'gaussian_1.5':dict(kinds=['gaussian'],gaussian_sigmas=[1.5],clear_probability=0),
        'gaussian_2.5':dict(kinds=['gaussian'],gaussian_sigmas=[2.5],clear_probability=0),
        'motion_9_45deg':dict(kinds=['motion'],motion_lengths=[9],motion_angles=[45],clear_probability=0)}
    (out/'plan.json').write_text(json.dumps(dict(conditions=conditions,threshold='Frozen raw natural calibration, five raw gallery references',purpose='Synthetic diagnostic only, no checkpoint selection or retraining'),indent=2))
    if backend=='pytorch':
        spec=importlib.util.spec_from_file_location('trained_models',experiment/'palmir/models.py')
        definitions=importlib.util.module_from_spec(spec);spec.loader.exec_module(definitions)
        checkpoint=torch.load(experiment/'runs/polyu_palm/ria/best.pt',map_location='cpu',weights_only=True)
        model=definitions.build_restorer(checkpoint['model_config']).eval();model.load_state_dict(checkpoint['model'])
        def restore(tensor):
            with torch.no_grad():return model(torch.from_numpy(tensor)).numpy()
    else:
        model=ort.InferenceSession(str(APP/'models/local-palmir-ria.onnx'),providers=['CPUExecutionProvider'])
        def restore(tensor):return model.run(None,{'image':tensor})[0]
    matcher=DoNAlgorithm();frames=[]
    for path in sorted((root/'rois').glob('*/*/original_roi.png')):
        identity=path.parent.parent.name;index=int(path.parent.name)
        rgb=np.asarray(Image.open(path).convert('RGB'))
        gray=np.asarray(Image.fromarray(rgb).convert('L'))
        normalized,_=normalize_roi(gray)
        frames.append(dict(identity=identity,index=index,rgb=rgb,feature=matcher.extract(normalized)))
    identities=sorted(set(f['identity'] for f in frames))
    gallery={key:[f['feature'] for f in frames if f['identity']==key and f['index']<=5] for key in identities}
    operating=json.loads((root/'audit/don_summary.json').read_text())['5']['threshold']
    summaries={};rows=[];panels=[]
    for condition,settings in conditions.items():
        quality=[];trials=[]
        for frame in [f for f in frames if f['index']>=6]:
            original=frame['rgb'].astype(np.float32).transpose(2,0,1)/255
            blurred=data.apply_degradation(torch.from_numpy(original),seed=2026,config=settings).numpy()[None]
            restored=restore(blurred)
            features={}
            for branch,tensor in [('raw',blurred),('restored',restored)]:
                rgb=np.rint(tensor[0].transpose(1,2,0).clip(0,1)*255).astype(np.uint8)
                gray=np.asarray(Image.fromarray(rgb).convert('L'))
                normalized,_=normalize_roi(gray);features[branch]=matcher.extract(normalized)
            quality.append(dict(raw_mse=float(np.square(blurred[0]-original).mean()),restored_mse=float(np.square(restored[0]-original).mean()),mean_abs_change_8bit=float(np.abs(restored-blurred).mean()*255)))
            for key,refs in gallery.items():
                row=dict(condition=condition,identity=frame['identity'],index=frame['index'],target=key,genuine=key==frame['identity'])
                for branch in features:
                    row[branch]=float(np.median([matcher.match(features[branch],ref) for ref in refs]))
                rows.append(row);trials.append(row)
            if frame['index']==6:
                panel=Image.new('RGB',(620,260),'white');draw=ImageDraw.Draw(panel)
                draw.text((8,8),f"{condition} {frame['identity']} | original / synthetic blur / restored",fill='black')
                for n,tensor in enumerate([original[None],blurred,restored]):
                    im=Image.fromarray(np.rint(tensor[0].transpose(1,2,0).clip(0,1)*255).astype(np.uint8))
                    panel.paste(im.resize((192,192)),(8+n*204,50))
                panels.append(panel)
        result=dict(threshold=operating,synthetic=True,backend=backend,quality={key:float(np.mean([q[key] for q in quality])) for key in quality[0]})
        for branch in ['raw','restored']:
            g=[r for r in trials if r['genuine']];im=[r for r in trials if not r['genuine']]
            result[branch]=dict(true_accepts=sum(r[branch]<=operating for r in g),n_genuine=len(g),false_accepts=sum(r[branch]<=operating for r in im),n_impostor=len(im))
        summaries[condition]=result;print(condition,json.dumps(result),flush=True)
    (out/'summary.json').write_text(json.dumps(summaries,indent=2))
    with (out/'scores.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    sheet=Image.new('RGB',(1240,260*((len(panels)+1)//2)),'#e8eeec')
    for n,panel in enumerate(panels):sheet.paste(panel,((n%2)*620,(n//2)*260))
    sheet.save(out/'examples.jpg',quality=94)


if __name__=='__main__':run(Path(sys.argv[1]),Path(sys.argv[2]),sys.argv[3] if len(sys.argv)>3 else 'onnx')
