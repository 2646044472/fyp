"""CPU checkpoint parity and small restoration-response control; no training."""
import argparse
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image
import torch

APP=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('experiment',type=Path)
    parser.add_argument('adaptation',type=Path)
    args=parser.parse_args();torch.set_num_threads(2)
    source=args.experiment/'palmir/models.py'
    spec=importlib.util.spec_from_file_location('checked_models',source)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    manifest=json.loads((APP/'models/local-palmir-ria.json').read_text())
    path=args.experiment/'runs/polyu_palm/ria/best.pt'
    assert hashlib.sha256(path.read_bytes()).hexdigest()==manifest['checkpoint_sha256']
    assert hashlib.sha256(source.read_bytes()).hexdigest()==manifest['source_sha256']
    ckpt=torch.load(path,map_location='cpu',weights_only=True)
    model=module.build_restorer(ckpt['model_config']).eval();model.load_state_dict(ckpt['model'])
    tensors=np.load(args.adaptation/'tensors.npz');parity={}
    with torch.inference_mode():
        for base in ('raw','normalized'):
            restored=np.concatenate([model(torch.from_numpy(x[None])).numpy() for x in tensors[base]])
            error=np.abs(restored-tensors[base+'_ria'])
            parity[base]=dict(max_abs_error=float(error.max()),mean_abs_error=float(error.mean()),
                torch_mean_change_8bit=float(np.abs(restored-tensors[base]).mean()*255))
    # A small known-domain response control, selected before scoring. Only
    # training images, one first image from each of eight distinct palms.
    manifest_path=args.experiment/'data/polyu_palm/manifest.csv'
    selected=[];seen=set()
    for row in csv.DictReader(manifest_path.open()):
        if row['split']=='train' and row['palm_id'] not in seen:
            selected.append(row);seen.add(row['palm_id'])
        if len(selected)==8:break
    rows=[]
    with torch.inference_mode():
        axis=torch.arange(-6,7,dtype=torch.float32);one=torch.exp(-.5*(axis/1.5)**2)
        kernel=one[:,None]*one[None,:];kernel/=kernel.sum()
        for row in selected:
            path=manifest_path.parent/row['path']
            assert hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256']
            x=np.asarray(Image.open(path).convert('RGB').resize((128,128),Image.Resampling.BILINEAR)).transpose(2,0,1).copy().astype(np.float32)[None]/255
            t=torch.from_numpy(x)
            blurred=torch.nn.functional.conv2d(torch.nn.functional.pad(t,(6,6,6,6),mode='replicate'),kernel.expand(3,1,13,13),groups=3)
            restored=model(blurred)
            rows.append(dict(sample=row['sample_id'],input_std_8bit=float(t.std()*255),
                blurred_mae=float((blurred-t).abs().mean()),restored_mae=float((restored-t).abs().mean()),
                output_change_8bit=float((restored-blurred).abs().mean()*255)))
    result=dict(parity=parity,synthetic_training_domain_control=rows,
        checkpoint_sha256=manifest['checkpoint_sha256'],source_sha256=manifest['source_sha256'],
        limitation='Eight training-domain images with synthetic Gaussian sigma1.5; response smoke only, not validation accuracy.')
    # Existing pixel-only checkpoint is a bounded alternative to identity-loss
    # restoration. Evaluate the same complete batch, without tuning either model.
    matcher_path=args.experiment/'runs/polyu_palm/matcher_clean/best.pt'
    matcher_manifest=json.loads((APP/'models/local-palmir-matcher.json').read_text())
    assert hashlib.sha256(matcher_path.read_bytes()).hexdigest()==matcher_manifest['checkpoint_sha256']
    mc=torch.load(matcher_path,map_location='cpu',weights_only=True)
    matcher=module.build_matcher(mc['model_config'],num_classes=len(mc['class_to_index'])).eval()
    matcher.load_state_dict(mc['model'])
    records=json.loads((args.adaptation/'records.json').read_text())
    identities=sorted({r['identity'] for r in records})
    results=[]
    for kind in ('ria','pixel'):
        cp=args.experiment/f'runs/polyu_palm/{kind}/best.pt'
        saved=torch.load(cp,map_location='cpu',weights_only=True)
        assert saved['provenance']['source_sha256']['models.py']==manifest['source_sha256']
        restore=module.build_restorer(saved['model_config']).eval();restore.load_state_dict(saved['model'])
        for base in ('raw','normalized'):
            with torch.inference_mode():
                f=torch.cat([matcher(restore(torch.from_numpy(x[None]))) for x in tensors[base]]).numpy()
            trials=[]
            for i,r in enumerate(records):
                if r['index']<=5:continue
                scores={k:float(np.median([1-float(np.dot(f[i],f[j])) for j,g in enumerate(records) if g['index']<=5 and g['identity']==k])) for k in identities}
                trials.append(dict(sample=r['sample'],scores=scores,correct=scores[r['identity']]<min(v for k,v in scores.items() if k!=r['identity'])))
            results.append(dict(variant=base+'_'+kind+'_both',correct=sum(t['correct'] for t in trials),total=20,
                checkpoint_sha256=hashlib.sha256(cp.read_bytes()).hexdigest(),trials=trials))
    result['existing_checkpoint_alternatives']=results
    (args.adaptation/'checkpoint-check.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
