"""Separate JPEG decode, perspective interpolation, and gray conversion.

Consumes frozen coordinates, so no neural inference or identity scoring occurs.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import sys

import cv2
import numpy as np
from PIL import Image, __version__ as PIL_VERSION

APP=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(APP))
from pklnet_roi import PKLNET_ROOT, normalize_roi


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('extraction',type=Path)
    parser.add_argument('output',type=Path)
    parser.add_argument('--local-input',type=Path)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    rows=json.loads(args.extraction.read_text())
    local={r['sample']:r['original'] for r in json.loads(args.local_input.read_text())} if args.local_input else None
    spec=importlib.util.spec_from_file_location('warp_geometry',PKLNET_ROOT/'roiExtractor.py')
    geometry=importlib.util.module_from_spec(spec);spec.loader.exec_module(geometry)
    outputs={k:[] for k in ['rgb','gray','gray_integer','normalized']};records=[]
    for row in rows:
        path=Path(local[row['sample']] if local else row['original'])
        rgb=np.asarray(Image.open(path).convert('RGB'));quad=np.array(row['illumination']['details']['roi_quad_full'],np.float32)
        anticlock=geometry.isAntiClock(quad[:3].reshape(-1))
        dst=np.array([[128,0],[0,0],[0,128],[128,128]] if anticlock else [[0,0],[128,0],[128,128],[0,128]],np.float32)
        matrix=cv2.getPerspectiveTransform(quad,dst)
        warped=cv2.warpPerspective(rgb,matrix,(128,128))
        gray=cv2.cvtColor(warped,cv2.COLOR_RGB2GRAY)
        v=warped.astype(np.int32)
        exact=((v[:,:,0]*4899+v[:,:,1]*9617+v[:,:,2]*1868+8192)>>14).astype(np.uint8)
        for key,value in [('rgb',warped),('gray',gray),('gray_integer',exact),('normalized',normalize_roi(gray)[0])]:outputs[key].append(value)
        records.append(dict(sample=row['sample'],file_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                            decoded_sha256=hashlib.sha256(rgb.tobytes()).hexdigest(),matrix=matrix.tolist()))
    np.savez_compressed(args.output/'stages.npz',**{k:np.stack(v) for k,v in outputs.items()})
    (args.output/'records.json').write_text(json.dumps(records,indent=2))
    (args.output/'environment.json').write_text(json.dumps(dict(host=platform.node(),opencv=cv2.__version__,pillow=PIL_VERSION,numpy=np.__version__),indent=2))


if __name__=='__main__':main()
