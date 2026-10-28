"""Cached control: accept adjusted localization only when quad IoU >= 0.5.

No labels or reference annotations enter the choice. Kept separate from the
earlier experiment so its hypotheses and results remain recoverable.
"""
import argparse
import json

import cv2
import numpy as np
from pathlib import Path

from audit_roi_robustness import evaluate, save


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path)
    parser.add_argument('output',type=Path)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    save(args.output/'plan.json',dict(min_iou=.5,rule='gamma if valid and overlaps v4 by at least 0.5 IoU; otherwise v4',
                                    limitation='Additional development-set experiment after inspecting prior results; not validation'))
    rows=json.loads((args.source/'records.json').read_text());pixels=np.load(args.source/'pixels.npz');selected=[]
    for r in rows:
        a=np.asarray(r['variants']['v4']['quad'],np.float32)
        b=np.asarray(r['variants']['gamma']['quad'],np.float32)
        area=cv2.intersectConvexConvex(a,b)[0]
        iou=area/max(1e-8,cv2.contourArea(a)+cv2.contourArea(b)-area)
        branch='gamma' if iou>=.5 and r['variants']['gamma']['valid'] else 'v4'
        r['variants']['consistent_gamma']={**r['variants'][branch], 'selected':branch,'cross_iou':float(iou)}
        selected.append(branch)
    arrays={'consistent_gamma':np.stack([pixels[b][i] for i,b in enumerate(selected)])}
    save(args.output/'records.json',rows);np.savez_compressed(args.output/'pixels.npz',**arrays)
    evaluate(rows,arrays,args.output)


if __name__=='__main__':main()
