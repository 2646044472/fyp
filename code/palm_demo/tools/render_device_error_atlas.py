"""Private original/ROI atlas for every error and both five-frame identities.

Labels select diagnostic pages only. No inference rule is changed. Images and
code arrays remain private; the manifest exports hashes/geometry/scalars only.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path

import cv2
import numpy as np
from PIL import Image,ImageDraw

from replay_pi_pipeline import debug_ui
from templates import TemplateStore
from anchored_matcher import source_quad
from pklnet_roi import PKLNetROI,normalize_roi_pixels
from audit_halfturn_recovery import verify_sources,sha,save


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('baseline',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--model-root',required=True,type=Path);a=p.parse_args();verify_sources()
    report=json.loads((a.baseline/'results.json').read_text());assert report['complete'] and report['executed_matcher']=='FastCCCompNetAlternateROI-v26-experimental'
    app=Path(__file__).resolve().parents[1]
    rows={r['sample']:r for r in json.loads((app/'runtime/halfturn-recovery-20261030/device-manifest-local.json').read_text())}
    os.environ['PALM_COMPNET_MODEL_ROOT']=str(a.model_root.resolve())
    algorithm=debug_ui.load_algorithm(debug_ui.common.DEFAULT_BASELINE,report['executed_matcher']);cv2.setNumThreads(1)
    engine=PKLNetROI(threads=3)
    a.output.mkdir(exist_ok=False);records=[];cache={}
    def panel(sample,source,expected=None):
        row=rows[sample];assert sha(row['original'])==row['sha256']
        with Image.open(row['original']) as image:full=image.convert('RGB');rgb=np.asarray(full)
        raw,quad,details=engine.extract(full);assert details['roi_geometry_valid']
        normalized=normalize_roi_pixels(raw)
        stored_quad=source_quad(np.asarray(source))
        code=algorithm.base.extract(normalized)
        photo=Image.fromarray(rgb);photo.thumbnail((265,190));scale=np.array([photo.width/rgb.shape[1],photo.height/rgb.shape[0]])
        pts=[tuple(p) for p in quad*scale];ImageDraw.Draw(photo).line(pts+[pts[0]],fill='#48e4a0',width=2)
        tile=Image.new('RGB',(280,350),(20,25,34));tile.paste(photo,((280-photo.width)//2,0));draw=ImageDraw.Draw(tile)
        tile.paste(Image.fromarray(raw).convert('RGB').resize((128,128)),(6,193))
        tile.paste(Image.fromarray(normalized).convert('RGB').resize((128,128)),(144,193))
        draw.text((6,322),'raw                         normalized',fill='white')
        draw.text((6,336),sample[-8:],fill='white')
        record=dict(sample=sample,original_sha256=row['sha256'],source_matrix=np.asarray(source).tolist(),quad=quad.tolist(),
            roi_source='Fresh unchanged PKLNet extraction, original RGB/BGR warp then grayscale; no gray-before-warp reconstruction',
            saved_quad_center_error_px=float(np.linalg.norm(stored_quad.mean(0)-quad.mean(0))),
            raw_contrast=float(raw.std()),normalized_contrast=float(normalized.std()),
            raw_roi_sha256=hashlib.sha256(raw.tobytes()).hexdigest(),
            code_equal_to_stored=None if expected is None else bool(np.array_equal(code,np.asarray(expected,bool))))
        if expected is not None:assert record['code_equal_to_stored'],'Actual enrollment pixels must reproduce stored base code'
        return tile,record
    try:
        for run in report['runs']:
            store=TemplateStore(a.baseline/run['case']/'runtime/demo_templates')
            for query in [q for q in run['queries'] if not q['correct']]:
                sheet=Image.new('RGB',(1400,1170),(13,19,29));draw=ImageDraw.Draw(sheet)
                qt,qr=panel(query['sample'],query['diagnostics']['source_matrix']);sheet.paste(qt,(0,35))
                draw.text((295,50),'Query: '+query['sample'],fill='white')
                draw.text((295,78),'True: '+query['identity']+' | Returned: '+str(query['result'].get('user_id')),fill='white')
                draw.text((295,106),'All five enrollment frames shown, in protocol order. Green = stored primary ROI.',fill='white')
                entry=dict(case=run['case'],sample=query['sample'],query=qr,groups=[])
                for gi,user in enumerate((query['identity'].replace(':','-'),query['result']['user_id'])):
                    key=(run['case'],user)
                    if key not in cache:
                        features,metadata=store.load(user);assert metadata['algorithm']==report['executed_matcher'] and len(features)==5
                        enrollment=next(e for e in run['enrollments'] if e['identity'].replace(':','-')==user)
                        tiles=[];items=[]
                        for feature,sample in zip(features,enrollment['samples']):
                            parts=algorithm._unpack(feature,decode_native=False)
                            tile,item=panel(sample,parts[1][2],parts[1][0][0]);tiles.append(tile);items.append(item)
                        cache[key]=(tiles,items);del features
                    tiles,items=cache[key];y=410+gi*375
                    draw.text((6,y-22),('TRUE' if gi==0 else 'RETURNED WRONG')+' identity: '+user,fill='#a6d6ff')
                    for j,tile in enumerate(tiles):sheet.paste(tile,(j*280,y))
                    entry['groups'].append(dict(role='true' if gi==0 else 'wrong',user=user,frames=items))
                destination=a.output/(query['sample']+'.jpg');sheet.save(destination,quality=94)
                entry['atlas']=destination.name;records.append(entry);save(a.output/'manifest.json',dict(complete=False,records=records))
                print(query['sample'],'stored enrollment code equality',[(g['role'],[x['code_equal_to_stored'] for x in g['frames']]) for g in entry['groups']],flush=True)
        assert len(records)==3;verify_sources()
        save(a.output/'manifest.json',dict(complete=True,records=records,baseline_sha256=sha(a.baseline/'results.json'),
            original_bytes_unchanged=True,limit='Actual frozen PKLNet pixels; all enrollment base codes verified. Anatomical interpretation is exposed qualitative review.'))
    finally:algorithm.close()


if __name__=='__main__':main()
