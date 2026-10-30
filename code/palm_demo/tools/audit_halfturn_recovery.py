"""Audit the bounded candidate on every original-device frame, plus two dev controls."""
import argparse
from contextlib import ExitStack
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import time
import zipfile

import cv2
import numpy as np
import psutil
from PIL import Image,ImageOps

APP=Path(__file__).resolve().parents[1];sys.path.insert(0,str(APP))
from pklnet_roi import PKLNetROI
from halfturn_roi_recovery import HalfTurnROIRecovery


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def source_sha(path):return hashlib.sha256(Path(path).read_bytes().replace(b'\r\n',b'\n')).hexdigest()
def save(path,data):
    temp=Path(str(path)+'.tmp');temp.write_text(json.dumps(data,indent=2),encoding='utf-8');temp.replace(path)


def verify_sources():
    manifest=json.loads((APP/'docs/protocols/STANDARD_DEVICE_BASELINE_20261030.json').read_text())
    for name,value in manifest['core_sources'].items():
        assert source_sha(APP.parents[1]/name)==value['sha256_lf'],name


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path)
    p.add_argument('--smpd-root',required=True,type=Path);a=p.parse_args()
    verify_sources();a.output.mkdir(exist_ok=False);(a.output/'inputs').mkdir()
    required=json.loads((APP/'docs/protocols/CANDIDATE_DEVICE_REGRESSION_REQUIREMENTS_20261030.json').read_text())
    manifest=APP.parents[1]/required['original_manifest'];assert sha(manifest)==required['manifest_sha256']
    originals=json.loads(manifest.read_text());assert len(originals)==169
    rows=[]
    with ExitStack() as stack:
        archives={}
        for r in originals:
            name=r['archive']
            if name not in archives:archives[name]=stack.enter_context(zipfile.ZipFile(APP.parents[1]/name))
            data=archives[name].read(r['archive_member']);assert hashlib.sha256(data).hexdigest()==r['sha256']
            path=a.output/'inputs'/(r['sample']+'.jpg');path.write_bytes(data)
            rows.append(dict(r,original=str(path.resolve()),decode='device_original_RGB'))
    save(a.output/'device-manifest-local.json',rows)
    public=json.loads((a.smpd_root/'prepared/manifest.json').read_text())
    public_rows=[dict(next(r for r in public if r['sample']==sample),decode='public_EXIF_RGB')
        for sample in ['smpd-008-F-00','smpd-008-F-03']]
    def count():return len(json.loads((a.smpd_root/'evaluation/results.json').read_text())['queries'])
    concurrency_path=a.smpd_root/'localization-diagnostic-concurrency.json'
    history=json.loads(concurrency_path.read_text()) if concurrency_path.exists() else []
    if isinstance(history,dict):history=[history]
    concurrency=dict(start_unix=time.time(),queries_completed_before=count(),output=str(a.output),
        scope='All-169-device plus two development-original ROI audit. Low-priority independent CPU process. No identity matching; overlapping Windows baseline timings may include contention.')
    history.append(concurrency);save(concurrency_path,history)
    if os.name=='nt':psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS)
    cv2.setNumThreads(1);engine=PKLNetROI(threads=3);pilot=HalfTurnROIRecovery(engine)
    report=dict(complete=False,scope=__doc__,evaluator_sha256=source_sha(__file__),candidate_sha256=source_sha(Path(__file__).with_name('halfturn_roi_recovery.py')),
        manifest_sha256=sha(manifest),standard='standard-device-20261030',records=[])
    with (a.output/'records.jsonl').open('x',encoding='utf-8') as log:
        for index,r in enumerate(rows+public_rows):
            data=Path(r['original']).read_bytes();assert hashlib.sha256(data).hexdigest()==r['sha256']
            with Image.open(io.BytesIO(data)) as image:
                full=(ImageOps.exif_transpose(image) if r['decode']=='public_EXIF_RGB' else image).convert('RGB')
            primary=engine.extract(full);candidate=pilot.recover(full,primary)
            raw,quad,details=primary;new_raw,new_quad,new_details=candidate
            unchanged=(np.array_equal(raw,new_raw) and np.array_equal(quad,new_quad) and details==new_details)
            row=dict(sample=r['sample'],device=r.get('device','SMPD-development'),
                primary_valid=bool(details['roi_geometry_valid']),primary_reason=details.get('roi_geometry_reason'),
                candidate_valid=bool(new_details['roi_geometry_valid']),valid_primary_verbatim=(candidate is primary) if details['roi_geometry_valid'] else None,
                output_unchanged=unchanged,primary_roi_sha256=hashlib.sha256(raw.tobytes()).hexdigest(),
                candidate_roi_sha256=hashlib.sha256(new_raw.tobytes()).hexdigest(),trace=pilot.last_trace)
            if details['roi_geometry_valid']:assert unchanged and candidate is primary,r['sample']
            report['records'].append(row);log.write(json.dumps(row)+'\n');log.flush()
            report['processed']=index+1;save(a.output/'results.json',report)
            if (index+1)%10==0:print('ROI audit',index+1,'/171',flush=True)
    assert len(report['records'])==171;verify_sources()
    device=report['records'][:169]
    report.update(complete=True,originals_unchanged=all(sha(r['original'])==r['sha256'] for r in rows+public_rows),
        device_summary=dict(total=169,primary_valid=sum(r['primary_valid'] for r in device),
            candidate_valid=sum(r['candidate_valid'] for r in device),retries=sum(r['trace']['retry'] for r in device),
            recoveries=sum(r['trace']['recovered'] for r in device),changed_valid=sum(r['primary_valid'] and not r['output_unchanged'] for r in device)),
        public_controls=report['records'][169:])
    save(a.output/'results.json',report)
    concurrency.update(end_unix=time.time(),queries_completed_after=count(),
        potentially_overlapping_query_indices=[concurrency['queries_completed_before']+1,count()+1]);save(concurrency_path,history)
    print(json.dumps(report['device_summary']),flush=True)


if __name__=='__main__':main()
