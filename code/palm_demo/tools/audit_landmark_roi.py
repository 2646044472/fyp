"""Independent anatomical ROI control; fixed split, no image-quality filtering."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP))
sys.path.insert(0, str(APP/'vendor/palmprint-recognition-python'))
from palm_roi import HandLandmarkTracker, landmarks_to_palm_quad, warp_palm_roi
from pklnet_roi import normalize_roi
from audit_roi_branches import score, neural
from palmprint.algorithms.registry import get_algorithm


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('benchmark', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--detector-grayscale',action='store_true',help='Neutralize camera color only for detector/pose inference; crop the original.')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    tracker = HandLandmarkTracker(APP/'models/palm_detection_mediapipe_2023feb.onnx',
        APP/'models/handpose_estimation_mediapipe_2023feb.onnx', input_size=(640,360), refine_pose=True)
    records, pixels, panels, failures = [], {'original':[], 'landmark':[]}, [], []
    for record in json.loads((args.benchmark/'extraction_manifest.json').read_text()):
        path = args.benchmark/'originals'/record['sample']/'full.jpg'
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record['original_sha256']
        image = Image.open(path).convert('RGB')
        candidates=[]
        for angle in (0,90,180,270):
            rotated=image.rotate(angle,expand=True)
            view=rotated.copy();view.thumbnail((640,640))
            bgr=cv2.cvtColor(np.asarray(view),cv2.COLOR_RGB2BGR)
            if args.detector_grayscale:
                bgr=cv2.cvtColor(cv2.cvtColor(bgr,cv2.COLOR_BGR2GRAY),cv2.COLOR_GRAY2BGR)
            detection=tracker._infer(bgr)
            candidates.append((detection.score,angle,rotated,view,bgr,detection))
        _,angle,image,view,bgr,detection=max(candidates,key=lambda c:c[0])
        if detection.points is None:
            failures.append(dict(sample=record['sample'],score=detection.score,reason='detection_failed'))
            print('FAILED',record['sample'],detection.score,flush=True)
            continue
        palm = np.r_[detection.box, detection.points.reshape(-1)]
        hand = tracker._handpose.infer(bgr, palm)
        source = 'handpose'
        if hand is None:
            source = 'palm_detector'
            landmarks = np.zeros((21,2), np.float32)
            landmarks[[0,5,9,13,17]] = detection.points[:5]
        else:
            landmarks = hand[4:67].reshape(21,3)[:,:2]
        landmarks = landmarks / np.array(view.size)
        # Fixed geometric parameters from the existing anatomical crop, not a label search.
        try:
            quad = landmarks_to_palm_quad(landmarks,image.size,width_scale=1.15,
                height_scale=1.25,center_offset=.30,min_span_px=24,fit_to_frame=False)
        except ValueError as error:
            failures.append(dict(sample=record['sample'],reason=str(error)))
            continue
        raw = np.asarray(warp_palm_roi(image,quad))
        original = np.asarray(Image.open(args.benchmark/'rois'/record['sample']/'roi_raw_128.png').convert('L'))
        pixels['original'].append(original); pixels['landmark'].append(raw)
        records.append(dict(sample=record['sample'],identity=record['subject']+':'+record['hand'],
            index=int(record['sample_index']),fused_valid=record['roi_geometry_valid'],source=source,
            landmarks=landmarks.tolist(),quad=quad.tolist(),detection_score=detection.score,rotation=angle,
            detector_grayscale=args.detector_grayscale))
        overlay=image.copy(); draw=ImageDraw.Draw(overlay); pts=[tuple(p) for p in quad]
        draw.line(pts+pts[:1], fill='lime',width=7)
        overlay.thumbnail((480,270)); panel=Image.new('RGB',(620,305),'white')
        panel.paste(overlay,(0,25)); panel.paste(Image.fromarray(raw),(485,25))
        ImageDraw.Draw(panel).text((5,5),record['sample']+' '+source,fill='black');panels.append(panel)
        print(record['sample'],source,flush=True)
    tracker.close()
    (args.output/'coverage.json').write_text(json.dumps(dict(total=40,extracted=len(records),failures=failures),indent=2))
    (args.output/'records.json').write_text(json.dumps(records,indent=2))
    np.savez_compressed(args.output/'pixels.npz',**{k:np.stack(v) for k,v in pixels.items()})
    for start in range(0,40,10):
        sheet=Image.new('RGB',(1240,1525),'white')
        for i,panel in enumerate(panels[start:start+10]):sheet.paste(panel,((i%2)*620,(i//2)*305))
        sheet.save(args.output/f'landmarks-{start}.jpg',quality=93)
    if failures:
        print('Incomplete extraction: no subset accuracy reported.',flush=True)
        return
    results=[]
    for name in ('DoN','FastCC'):
        alg=get_algorithm(name);features={}
        for branch,values in pixels.items():
            f=[alg.extract(normalize_roi(v)[0]) for v in values];features[branch]=(f,f)
        results.extend(score(records,features,alg.match,name))
    (args.output/'classical.json').write_text(json.dumps(results,indent=2))
    neural(args.output)


if __name__=='__main__': main()
