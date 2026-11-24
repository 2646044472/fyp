"""Small fixed ablation: normalization, restoration and residual blending.

No training or per-identity routing. All 40 inputs and the original split remain.
Results are exploratory on an already inspected development batch.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import cv2
import numpy as np
import onnxruntime as ort
from PIL import Image, ImageDraw

APP=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(APP));sys.path.insert(0,str(APP/'vendor/palmprint-recognition-python'))
from pklnet_roi import normalize_roi
from audit_roi_branches import score, environment
from palmprint.algorithms.registry import get_algorithm


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('replay',type=Path)
    parser.add_argument('output',type=Path)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    records=json.loads((args.replay/'records.json').read_text())
    raw=np.load(args.replay/'pixels.npz')['heatmap_runtime']
    variants=['raw','raw_ria','raw_blend50','normalized','normalized_ria','normalized_blend50']
    plan=dict(variants=variants,normalization='1/99 percentile; same existing matcher normalization',
        blend='0.5 * input + 0.5 * restored',gallery='both transformed and un-restored paired control',
        split='index1-5 gallery;6-10 probe; all40; no quality or geometry filtering',
        limitation='Exploratory development-set ablation, not independent validation. No training.')
    (args.output/'plan.json').write_text(json.dumps(plan,indent=2))
    options=ort.SessionOptions();options.intra_op_num_threads=2;options.inter_op_num_threads=1
    sessions={};manifests={}
    for kind in ('ria','matcher'):
        path=APP/'models'/f'local-palmir-{kind}.onnx'
        meta=json.loads(path.with_suffix('.json').read_text())
        assert hashlib.sha256(path.read_bytes()).hexdigest()==meta['onnx_sha256']
        sessions[kind]=ort.InferenceSession(str(path),sess_options=options,providers=['CPUExecutionProvider'])
        manifests[kind]=meta
    assert manifests['matcher']['checkpoint_sha256']==manifests['ria']['training_matcher_checkpoint_sha256']
    tensors={};features={};stats={}
    for base,images in [('raw',raw),('normalized',np.stack([normalize_roi(im)[0] for im in raw]))]:
        original=np.repeat(images[:,None],3,axis=1).astype(np.float32)/255
        restored=np.concatenate([sessions['ria'].run(None,{'image':x[None]})[0] for x in original])
        tensors[base]=original;tensors[base+'_ria']=restored;tensors[base+'_blend50']=(original+restored)*.5
        stats[base]=dict(mean_abs_change_8bit=float(np.abs(restored-original).mean()*255),
            mean_input_std_8bit=float(original.std(axis=(1,2,3)).mean()*255),
            mean_output_std_8bit=float(restored.std(axis=(1,2,3)).mean()*255),
            clipped_output_fraction=float(((restored<=0)|(restored>=1)).mean()))
    for name,values in tensors.items():
        features[name]=np.stack([sessions['matcher'].run(None,{'image':x[None]})[0][0] for x in values])
    cosine=lambda a,b:1-float(np.dot(a,b)/max(np.linalg.norm(a)*np.linalg.norm(b),1e-12))
    def pairs(f):
        out={name+'_both':(values,values) for name,values in f.items()}
        for base in ('raw','normalized'):
            for suffix in ('_ria','_blend50'):out[base+suffix+'_probe']=(f[base+suffix],f[base])
        return out
    neural=score(records,pairs(features),cosine,'local_training_matcher')
    (args.output/'neural.json').write_text(json.dumps(neural,indent=2))
    # Save tensors for exact PyTorch parity checks; preserve float outputs.
    np.savez_compressed(args.output/'tensors.npz',**tensors)
    (args.output/'stats.json').write_text(json.dumps(dict(stats=stats,models=manifests),indent=2))
    (args.output/'records.json').write_text(json.dumps(records,indent=2))
    pixels={name:np.stack([cv2.cvtColor(np.rint(x.transpose(1,2,0).clip(0,1)*255).astype(np.uint8),cv2.COLOR_RGB2GRAY) for x in v]) for name,v in tensors.items()}
    np.savez_compressed(args.output/'pixels.npz',**pixels)
    environment(args.output,'restoration-adaptation')
    panels=[]
    for i,r in enumerate(records):
        panel=Image.new('RGB',(900,185),'white');draw=ImageDraw.Draw(panel)
        draw.text((5,3),f"{r['identity']} #{r['index']}",fill='black')
        for col,name in enumerate(variants):
            draw.text((col*150+4,22),name,fill='black');panel.paste(Image.fromarray(pixels[name][i]),(col*150+4,48))
        panels.append(panel)
    for start in range(0,40,10):
        sheet=Image.new('RGB',(900,1850),'white')
        for i,panel in enumerate(panels[start:start+10]):sheet.paste(panel,(0,i*185))
        sheet.save(args.output/f'comparison-{start}.jpg',quality=94)
    results=[]
    for name in ('DoN','FastCC'):
        alg=get_algorithm(name)
        f={variant:[alg.extract(normalize_roi(im)[0]) for im in ims] for variant,ims in pixels.items()}
        results.extend(score(records,pairs(f),alg.match,name))
    (args.output/'classical.json').write_text(json.dumps(results,indent=2))


if __name__=='__main__':main()
