"""Fixed, identity-independent localization controls on saved camera frames.

Development experiment only. Original pixels feed the matcher; photometric
transforms affect landmark inference only. Never selects using identity scores.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

import cv2
import numpy as np
from PIL import Image

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP))
from pklnet_roi import PKLNetROI, normalize_roi, MIN_KEYPOINT_SPAN_RATIO
from palm_app.biometric import load_algorithm


def save(path, value):
    path.write_text(json.dumps(value, indent=2), encoding='utf-8')


def geometry(points, image, engine):
    points = np.asarray(points, np.float32).reshape(3, 2)
    quad = engine.getROIckp(points[0], points[1], engine.isAntiClock(points.reshape(-1)))
    if quad is None:
        return None, False
    quad = np.asarray(quad, np.float32)
    valid = bool(np.isfinite(quad).all() and (quad >= 0).all()
                 and (quad[:, 0] < image.width).all() and (quad[:, 1] < image.height).all()
                 and np.linalg.norm(points[0]-points[1])/min(image.size) >= MIN_KEYPOINT_SPAN_RATIO)
    return quad, valid


def consensus(predictions, image, engine):
    """Medoid coordinate frame, then endpoint-aligned median; geometry fallback."""
    candidates = [np.asarray(p, np.float32).reshape(3, 2) for p in predictions
                  if geometry(p, image, engine)[1]]
    if not candidates:
        return np.asarray(predictions[0], np.float32).reshape(3, 2)
    # Compare both endpoint orders, but preserve the third palm-side point.
    distances = np.zeros((len(candidates), len(candidates)))
    for i, p in enumerate(candidates):
        for j, q in enumerate(candidates):
            distances[i, j] = min(np.linalg.norm(p[:2]-q[:2]), np.linalg.norm(p[:2]-q[1::-1]))
    medoid = candidates[int(np.argmin(distances.sum(axis=1)))]
    aligned = [p if np.linalg.norm(p[:2]-medoid[:2]) <= np.linalg.norm(p[1::-1]-medoid[:2])
               else p[[1, 0, 2]] for p in candidates]
    merged = np.median(aligned, axis=0).astype(np.float32)
    return merged if geometry(merged, image, engine)[1] else medoid


def evaluate(rows, pixels, out):
    results = []
    identities = sorted({r['identity'] for r in rows})
    for name in ('DoN', 'FastCC'):
        alg = load_algorithm(APP/'vendor/palmprint-recognition-python', name)
        for variant, images in pixels.items():
            features = [alg.extract(normalize_roi(im)[0]) for im in images]
            gallery = {k: [i for i, r in enumerate(rows) if r['identity']==k and r['index']<=5
                           and r['variants'][variant]['valid']] for k in identities}
            trials = []
            for i, r in enumerate(rows):
                if r['index'] <= 5:
                    continue
                scores = {k: float(np.median([alg.match(features[i], features[j]) for j in ids]))
                          for k, ids in gallery.items() if ids} if r['variants'][variant]['valid'] else {}
                correct = bool(len(scores)==len(identities) and scores[r['identity']] <
                               min(v for k,v in scores.items() if k!=r['identity']))
                trials.append(dict(sample=r['sample'], identity=r['identity'], correct=correct, scores=scores))
            result = dict(variant=variant, algorithm=name, correct=sum(t['correct'] for t in trials),
                          total=len(trials), valid=sum(r['variants'][variant]['valid'] for r in rows),
                          gallery_sizes={k:len(v) for k,v in gallery.items()}, trials=trials)
            results.append(result)
            print(json.dumps({k:v for k,v in result.items() if k!='trials'}), flush=True)
            save(out/'recognition.json', results)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('replay', type=Path)
    parser.add_argument('output', type=Path)
    args=parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    variants=['v4','gamma','clahe','photometric_consensus','view_consensus']
    save(args.output/'plan.json', dict(variants=variants, gamma=.6, clahe='LAB L, clipLimit=2, grid8x8',
        views='full + largest 4:3 at left/center/right (top/center/bottom for portrait)',
        consensus='valid candidates only; endpoint-aligned median in medoid orientation; invalid merge falls back to medoid',
        evaluation='all images; indices1-5 gallery,6-10 probes; no probe deletion; original geometry guard',
        limitation='Repeatedly inspected development data; no per-identity selection; no training',
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()))
    sources=json.loads((args.replay/'extraction.json').read_text())
    ext=PKLNetROI(threads=2, policy='aspect');ext._ensure_loaded();engine=ext._roi_extractor
    rows=[];pixels={k:[] for k in variants}
    for n, src in enumerate(sources,1):
        path=Path(src['original']);assert hashlib.sha256(path.read_bytes()).hexdigest()==src['sha256']
        image=Image.open(path).convert('RGB');rgb=np.asarray(image);bgr=cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR)
        base=np.asarray(src['aspect']['details']['pklnet_keypoints'],np.float32).reshape(3,2)
        gamma=np.rint((rgb.astype(np.float32)/255)**.6*255).astype(np.uint8)
        lab=cv2.cvtColor(rgb,cv2.COLOR_RGB2LAB)
        lab[:,:,0]=cv2.createCLAHE(clipLimit=2,tileGridSize=(8,8)).apply(lab[:,:,0])
        adjusted={'gamma':gamma,'clahe':cv2.cvtColor(lab,cv2.COLOR_LAB2RGB)}
        predictions={'v4':base};started=time.perf_counter()
        for name, arr in adjusted.items():
            _,_,d=ext.extract(Image.fromarray(arr));predictions[name]=np.asarray(d['pklnet_keypoints']).reshape(3,2)
        predictions['photometric_consensus']=consensus(list(predictions.values()),image,engine)
        view_predictions=[base]
        box=ext._aspect_retry_box(image.size);w,h=box[2]-box[0],box[3]-box[1]
        if (w,h)!=image.size:
            for offset in (0,.5,1):
                x=round((image.width-w)*offset);y=round((image.height-h)*offset)
                _,_,d=ext._extract_once(image.crop((x,y,x+w,y+h)))
                view_predictions.append(np.asarray(d['pklnet_keypoints']).reshape(3,2)+[x,y])
        predictions['view_consensus']=consensus(view_predictions,image,engine)
        row={k:src[k] for k in ('sample','identity','index','original','sha256')};row['variants']={}
        for name, kp in predictions.items():
            quad,valid=geometry(kp,image,engine)
            assert quad is not None, 'Degenerate experiment must be recorded rather than silently removed'
            raw=engine.getROIimg(bgr,quad,side=128)
            row['variants'][name]=dict(keypoints=kp.tolist(),quad=quad.tolist(),valid=valid)
            pixels[name].append(raw)
        rows.append(row)
        print(f'EXTRACT {n}/{len(sources)} {time.perf_counter()-started:.2f}s',flush=True)
    save(args.output/'records.json',rows)
    arrays={k:np.stack(v) for k,v in pixels.items()}
    np.savez_compressed(args.output/'pixels.npz',**arrays)
    evaluate(rows,arrays,args.output)
    save(args.output/'integrity.json',dict(originals_unchanged=all(hashlib.sha256(Path(r['original']).read_bytes()).hexdigest()==r['sha256'] for r in rows)))


if __name__=='__main__':
    main()
