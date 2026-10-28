"""Offline branch ablation on frozen, labelled camera captures.

Cached branch predictions are reused, never selected by recognition labels.
This is an exploratory diagnostic, not a replacement localization policy.
"""
import argparse
import hashlib
import importlib.util
import json
import platform
from pathlib import Path
import sys
import time

import cv2
import numpy as np
from PIL import Image, ImageDraw

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP))
sys.path.insert(0, str(APP / 'vendor/palmprint-recognition-python'))
from pklnet_roi import PKLNetROI, PKLNET_ROOT, normalize_roi


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, data):
    Path(path).write_text(json.dumps(data, indent=2), encoding='utf-8')


def environment(output, stage):
    import importlib.metadata
    packages={}
    for name in ('numpy','scipy','Pillow','onnxruntime'):
        try: packages[name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError: pass
    save(output/('environment-'+stage+'.json'),dict(
        host=platform.node(),machine=platform.machine(),python=sys.version,
        packages=packages,opencv=cv2.__version__,argv=sys.argv,
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        input_sha256={name:hashlib.sha256((output/name).read_bytes()).hexdigest()
                      for name in ('pixels.npz','records.json')}))


def prepare(benchmark, output):
    output.mkdir(parents=True, exist_ok=False)
    manifest = read(benchmark / 'extraction_manifest.json')
    predictions = {r['sample']: r for r in read(benchmark / 'torch-diagnosis-all/diagnosis.json') if r['variant'] == 'canonical'}
    spec = importlib.util.spec_from_file_location('roi_geometry', PKLNET_ROOT / 'roiExtractor.py')
    geometry = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(geometry)
    pixels = {k: [] for k in ('fused', 'heatmap', 'fc')}
    records, panels = [], {}
    for row in manifest:
        sample = row['sample']
        original_path = benchmark / 'originals' / sample / 'full.jpg'
        assert hashlib.sha256(original_path.read_bytes()).hexdigest() == row['original_sha256']
        image = Image.open(original_path).convert('RGB')
        bgr = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)
        d = predictions[sample]
        _, osize, rsize, scale = PKLNetROI._prepare(image)
        record = dict(sample=sample, identity=row['subject'] + ':' + row['hand'], index=int(row['sample_index']),
                      fused_valid=row['roi_geometry_valid'], branch_axis_cosine=d['branch_axis_cosine'], branches={})
        panel = Image.new('RGB', (1080, 330), 'white')
        pd = ImageDraw.Draw(panel)
        for col, branch in enumerate(pixels):
            if branch == 'fused':
                kp = np.asarray(row['pklnet_keypoints'], dtype=np.float32)
                quad = np.asarray(row['roi_quad_full'], dtype=np.float32)
                raw = np.asarray(Image.open(benchmark / 'rois' / sample / 'roi_raw_128.png').convert('L'))
            else:
                key = 'heatmap_branch_keypoints' if branch == 'heatmap' else 'fc_branch_keypoints'
                kp = PKLNetROI._unrotate_keypoints(np.asarray(d[key]), osize, rsize, scale)
                quad = np.asarray(geometry.getROIckp(kp[:2], kp[2:4], geometry.isAntiClock(kp[:6])), dtype=np.float32)
                raw = geometry.getROIimg(bgr, quad, side=128)
            pixels[branch].append(raw)
            span = float(np.linalg.norm(kp[2:4] - kp[:2]))
            in_bounds = bool((quad >= 0).all() and (quad[:, 0] < image.width).all() and (quad[:, 1] < image.height).all())
            branch_data = dict(keypoints=kp.tolist(), quad=quad.tolist(), side_px=float(np.linalg.norm(quad[1]-quad[0])),
                               span_ratio=span/min(image.size), in_bounds=in_bounds, geometry_valid=in_bounds and span/min(image.size)>=.1,
                               angle_deg=float(np.degrees(np.arctan2(*(kp[2:4]-kp[:2])[::-1]))),
                               winding=bool(geometry.isAntiClock(kp[:6])), contrast=float(raw.std()),
                               laplacian_variance=float(cv2.Laplacian(raw,cv2.CV_64F).var()))
            record['branches'][branch] = branch_data
            overlay = image.copy()
            od = ImageDraw.Draw(overlay)
            points = [tuple(map(float,p)) for p in quad]
            od.line(points+points[:1], fill='lime', width=7)
            for j,(x,y) in enumerate(kp.reshape(-1,2)):
                od.ellipse((x-6,y-6,x+6,y+6), fill='red')
                od.text((x+8,y),str(j+1),fill='yellow',stroke_width=1)
            overlay.thumbnail((350,197))
            panel.paste(overlay,(col*360+5,25))
            panel.paste(Image.fromarray(raw).resize((96,96)),(col*360+5,226))
            pd.text((col*360+5,5),f"{record['identity']} #{record['index']} {branch}",fill='black')
            pd.text((col*360+110,230),f"side={branch_data['side_px']:.1f}px\ncontrast={raw.std():.1f}\ngeometry={branch_data['geometry_valid']}",fill='black')
        records.append(record)
        panels.setdefault(record['identity'],[]).append((record['index'],panel))
    for identity, rows in panels.items():
        sheet=Image.new('RGB',(1080,len(rows)*330),'white')
        for i,(_,panel) in enumerate(sorted(rows)):
            sheet.paste(panel,(0,i*330))
        sheet.save(output/(identity.replace(':','-')+'.jpg'),quality=93)
    np.savez_compressed(output/'pixels.npz',**{k:np.stack(v) for k,v in pixels.items()})
    save(output/'records.json',records)
    print(json.dumps({'prepared':len(records),'opposing_branches':sum(r['branch_axis_cosine']<0 for r in records),
                      'geometry_valid':{k:sum(r['branches'][k]['geometry_valid'] for r in records) for k in pixels}}),flush=True)


def score(records, feature_sets, match, algorithm):
    identities=sorted({r['identity'] for r in records})
    results=[]
    for name, (probe_features,gallery_features) in feature_sets.items():
        # All comparisons share the original index split. Geometry subset is
        # always the ORIGINAL fused guard, not a branch-specific filtered set.
        distances={(i,j):float(match(probe_features[i],gallery_features[j]))
                   for i,r in enumerate(records) if r['index']>5
                   for j,g in enumerate(records) if g['index']<=5}
        for subset in ('all','original_geometry_pass'):
            allowed=[i for i,r in enumerate(records) if subset=='all' or r['fused_valid']]
            gallery={k:[i for i in allowed if records[i]['identity']==k and records[i]['index']<=5] for k in identities}
            if not all(gallery.values()):
                continue
            trials=[]
            for i in allowed:
                r=records[i]
                if r['index']<=5: continue
                scores={k:float(np.median([distances[i,j] for j in js])) for k,js in gallery.items()}
                own=scores[r['identity']]
                other=min(v for k,v in scores.items() if k!=r['identity'])
                trials.append(dict(sample=r['sample'],identity=r['identity'],index=r['index'],correct=own<other,
                                   own=own,nearest_other=other,margin=other-own,scores=scores))
            result=dict(algorithm=algorithm,variant=name,subset=subset,correct=sum(t['correct'] for t in trials),
                        probes=len(trials),per_identity={k:sum(t['correct'] for t in trials if t['identity']==k) for k in identities},
                        gallery_sizes={k:len(v) for k,v in gallery.items()},trials=trials)
            results.append(result)
            print(json.dumps({k:v for k,v in result.items() if k!='trials'}),flush=True)
    return results


def classical(output):
    from palmprint.algorithms.registry import get_algorithm
    environment(output,'classical')
    records=read(output/'records.json')
    with np.load(output/'pixels.npz') as data:
        branches={k:data[k] for k in data.files}
    results=[]
    for name in ('DoN','FastCC'):
        algorithm=get_algorithm(name)
        feature_sets={}
        for branch, images in branches.items():
            features=[algorithm.extract(normalize_roi(im)[0]) for im in images]
            feature_sets[branch+'_normalized']=(features,features)
        # Raw fused is an illumination-normalization ablation, not retraining.
        raw=[algorithm.extract(im) for im in branches['fused']]
        feature_sets['fused_unnormalized']=(raw,raw)
        results.extend(score(records,feature_sets,algorithm.match,name))
    save(output/'classical.json',results)


def neural(output):
    import onnxruntime as ort
    environment(output,'neural')
    options=ort.SessionOptions()
    options.intra_op_num_threads=2
    options.inter_op_num_threads=1
    sessions,manifests={},{}
    for kind in ('matcher','ria'):
        path=APP/'models'/f'local-palmir-{kind}.onnx'
        meta=read(path.with_suffix('.json'))
        assert hashlib.sha256(path.read_bytes()).hexdigest()==meta['onnx_sha256']
        manifests[kind]=meta
        sessions[kind]=ort.InferenceSession(str(path),sess_options=options,providers=['CPUExecutionProvider'])
    assert manifests['matcher']['checkpoint_sha256']==manifests['ria']['training_matcher_checkpoint_sha256']
    records=read(output/'records.json')
    feature_sets={}
    timings=[]
    with np.load(output/'pixels.npz') as data:
        for branch in data.files:
            raw_features,restored_features=[],[]
            for im in data[branch]:
                tensor=np.repeat(im[None,None],3,axis=1).astype(np.float32)/255
                t=time.perf_counter()
                restored=sessions['ria'].run(None,{'image':tensor})[0]
                timings.append((time.perf_counter()-t)*1000)
                raw_features.append(sessions['matcher'].run(None,{'image':tensor})[0][0])
                restored_features.append(sessions['matcher'].run(None,{'image':restored})[0][0])
            feature_sets[branch+'_raw']=(raw_features,raw_features)
            feature_sets[branch+'_ria_probe']=(restored_features,raw_features)
            feature_sets[branch+'_ria_both']=(restored_features,restored_features)
    def cosine(a,b):
        return 1-float(np.dot(a,b)/max(np.linalg.norm(a)*np.linalg.norm(b),1e-12))
    results=score(records,feature_sets,cosine,'local_training_matcher')
    save(output/'neural.json',dict(results=results,model_manifests=manifests,
                                  ria_ms_p50=float(np.median(timings[1:])),ria_ms_p95=float(np.percentile(timings[1:],95))))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode',choices=['prepare','classical','neural'])
    p.add_argument('output',type=Path)
    p.add_argument('--benchmark',type=Path)
    args=p.parse_args()
    if args.mode=='prepare':
        if args.benchmark is None: p.error('--benchmark required')
        prepare(args.benchmark,args.output)
    elif args.mode=='classical': classical(args.output)
    else: neural(args.output)
