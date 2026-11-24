"""Frozen-quad controls: uint8 OpenCV, float OpenCV, float/rounded NumPy.

No re-localization, template-dependent crop selection, or discarded samples.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import cv2
import numpy as np
from PIL import Image

APP=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(APP))
from pklnet_roi import PKLNET_ROOT
from roi_sampling import sample_palm_quad
from audit_roi_robustness import evaluate, save


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('extraction',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--local-input',type=Path);p.add_argument('--extract-only',action='store_true');args=p.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    save(args.output/'plan.json',dict(variants=['opencv_u8','opencv_float','numpy_float','numpy_rounded'],
         policy='Frozen v5 geometry; all40; first5 gallery last5 probe; unchanged percentile normalization',
         hypothesis='Avoid low-contrast signal quantization and platform-dependent uint8 warp rounding'))
    sources=json.loads(args.extraction.read_text());local={r['sample']:r['original'] for r in json.loads(args.local_input.read_text())} if args.local_input else None
    spec=importlib.util.spec_from_file_location('sampling_geometry',PKLNET_ROOT/'roiExtractor.py');geo=importlib.util.module_from_spec(spec);spec.loader.exec_module(geo)
    pixels={k:[] for k in ['opencv_u8','opencv_float','numpy_float','numpy_rounded']};rows=[]
    for source in sources:
        path=Path(local[source['sample']] if local else source['original']);assert hashlib.sha256(path.read_bytes()).hexdigest()==source['sha256']
        rgb=np.asarray(Image.open(path).convert('RGB'));bgr=cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR)
        d=source['illumination']['details'];quad=np.asarray(d['roi_quad_full'],np.float32)
        precise=sample_palm_quad(rgb,quad)
        values={'opencv_u8':geo.getROIimg(bgr,quad), 'opencv_float':geo.getROIimg(bgr.astype(np.float32),quad),
                'numpy_float':precise,'numpy_rounded':np.rint(precise).clip(0,255).astype(np.uint8)}
        rows.append({**{k:source[k] for k in ['sample','identity','index','sha256']},'original':str(path),
                     'variants':{k:dict(valid=d['roi_geometry_valid'],quad=quad.tolist()) for k in values}})
        for k,v in values.items():pixels[k].append(v)
    arrays={k:np.stack(v) for k,v in pixels.items()};np.savez_compressed(args.output/'pixels.npz',**arrays);save(args.output/'records.json',rows)
    if not args.extract_only:evaluate(rows,arrays,args.output)


if __name__=='__main__':main()
