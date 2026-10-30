"""Resume an interrupted frozen full run, preserving its exact logged prefix.

Only operational statements of the source-locked evaluator are adapted in RAM:
read/validate existing registration, load prior report, append the next original
in the fixed order. Scoring/model/decoder/HTTP statements stay untouched.
"""
import argparse
import copy
import hashlib
import inspect
import json
import os
from pathlib import Path
import time

import psutil
import evaluate_raw_smpd as base


def remaining(rows,queries):
    ordered=sorted((r for r in rows if not r['enrollment']),key=lambda r:(r['subject'],r['index']))
    names=[q['sample'] for q in queries]
    assert len(names)==len(set(names)),'Duplicate completed query'
    assert names==[r['sample'] for r in ordered[:len(names)]],'Completed results are not the exact fixed-order prefix'
    return ordered[len(names):]


def resumed_report(fresh,previous,startup):
    assert fresh['protocol_sha256']==previous['protocol_sha256']
    assert fresh['archive_sha256']==previous['archive_sha256']
    assert fresh['enrollments']==previous['enrollments']
    assert fresh['actual_gallery_identities']==previous['actual_gallery_identities']
    report=copy.deepcopy(previous);assert not report['complete']
    report.setdefault('resume_epochs',[]).append(dict(started_after_queries=len(report['queries']),
        startup_and_gallery_ready_ms=startup,started_unix=time.time(),reason='Previous inference process absent; exact prefix preserved',
        resume_helper_sha256=base.source_sha(__file__)))
    report.setdefault('warnings',[]).append('Operational restart: same full gallery/models/parameters; startup separately measured. Not one uninterrupted process or exclusive-CPU timing.')
    return report


def validate_enrollments(store,payments,rows,expected):
    records=[]
    for identity in sorted({r['identity'] for r in rows}):
        selected=sorted((r for r in rows if r['identity']==identity and r['enrollment']),key=lambda r:r['index'])
        assert len(selected)==5;ok=all(r.get('enrollment_feature_ok') for r in selected);user=identity.replace(':','-')
        records.append(dict(identity=identity,samples=[r['sample'] for r in selected],registered=ok))
        assert store.exists(user)==ok and payments.user_exists(user)==ok
        if ok:
            features,metadata=store.load(user)
            assert features.shape[0]==5 and metadata['algorithm']==base.MATCHER and metadata['roi_geometry']==base.ROI_GEOMETRY_VERSION
            for index,row in enumerate(selected):
                assert base.sha(row['enrollment_feature'])==row['enrollment_feature_sha256']
                with base.np.load(row['enrollment_feature'],allow_pickle=False) as data:
                    assert base.np.array_equal(features[index],data['feature']),row['sample']
            assert payments.balance_for(user)==10000
    assert records==expected and payments.transaction_count()==0
    return records


def adapt(source):
    begin=source.index('    enrollments=[]\n');end=source.index('    app,camera,engine,startup=',begin)
    source=source[:begin]+"    enrollments=_validate_enrollments(store,payments,rows,_previous['enrollments']);registered=set(store.list_users())\n"+source[end:]
    changes=[('out.mkdir(exist_ok=False)','assert out.is_dir()'),
        ('    numeric={};old=app.demo_algorithm.score_gallery',
         '    report=_resumed_report(report,_previous,startup)\n    numeric={};old=app.demo_algorithm.score_gallery'),
        ('query_rois.mkdir()','query_rois.mkdir(exist_ok=True)'),
        ("(out/'queries.jsonl').open('x',encoding='utf-8')","(out/'queries.jsonl').open('a',encoding='utf-8')"),
        ("for row in sorted((r for r in rows if not r['enrollment']),key=lambda r:(r['subject'],r['index'])):",
         "for row in _remaining(rows,_previous['queries']):")]
    for old,new in changes:
        assert source.count(old)==1,old
        source=source.replace(old,new)
    return source


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path);p.add_argument('--model',required=True,type=Path)
    p.add_argument('--wait-pilot',type=Path);a=p.parse_args();a.root=a.root.resolve();a.model=a.model.resolve()
    status=a.root/'resume-status.json'
    def checkpoint(state,**extra):base.save(status,dict(complete=False,state=state,inference_pid=os.getpid(),updated_unix=time.time(),**extra))
    if a.wait_pilot:
        while True:
            file=a.wait_pilot/'results.json'
            pilot=json.loads(file.read_text()) if file.exists() else {}
            if pilot.get('failure'):raise RuntimeError('Pilot operational failure; preserve evidence before manual recovery: '+pilot['failure'])
            if pilot.get('complete'):break
            checkpoint('waiting_for_current_pilot');time.sleep(20)
    while psutil.virtual_memory().available<10*1024**3:
        checkpoint('waiting_for_full_gallery_memory',available_bytes=psutil.virtual_memory().available);time.sleep(20)
    protocol=json.loads((a.root/'protocol.json').read_text());base.verify(protocol)
    dependencies=json.loads((a.root/'dependency-lock.json').read_text())
    for path,digest in dependencies['source_sha256'].items():assert base.source_sha(path)==digest,path
    assert base.sha(a.model/'compnet-tongji.onnx')==protocol['model_sha256']['compnet']
    assert base.sha(base.PKLNetROI().root/'pklnet-keypoints-diagnostics.onnx')==protocol['model_sha256']['pklnet']
    previous=json.loads((a.root/'evaluation/results.json').read_text());assert not previous['complete']
    ledger=a.root/'evaluation/queries.jsonl';raw=ledger.read_bytes();assert not raw or raw.endswith(b'\n'),'Incomplete JSONL record; do not truncate it'
    queries=[json.loads(line) for line in raw.splitlines() if line]
    assert queries==previous['queries'],'Report/JSONL prefix disagree; do not discard either'
    rows=json.loads((a.root/'prepared/manifest.json').read_text());todo=remaining(rows,queries)
    assert len(queries)+len(todo)==3217
    stamp=str(time.time_ns());folder=a.root/('resume-epoch-'+stamp);folder.mkdir()
    (folder/'prefix-results.json').write_bytes((a.root/'evaluation/results.json').read_bytes())
    (folder/'prefix-queries.jsonl').write_bytes(raw)
    original=inspect.getsource(base.run);candidate=adapt(original)
    (folder/'adapted-evaluator.py').write_text(candidate,encoding='utf-8')
    base.save(folder/'provenance.json',dict(helper_sha256=base.source_sha(__file__),original_function_sha256=hashlib.sha256(original.encode()).hexdigest(),
        adapted_function_sha256=hashlib.sha256(candidate.encode()).hexdigest(),preserved_prefix=len(queries),remaining=len(todo),
        original_prefix_sha256=hashlib.sha256(raw).hexdigest(),algorithm_parameters_changed=False,
        pipeline_scope='Only process restart, existing enrollment validation, report loading, prefix iteration and append mode changed. Fresh original read/ROI/features/HTTP per remaining query.'))
    namespace=dict(base.__dict__,_previous=previous,_remaining=remaining,_resumed_report=resumed_report,_validate_enrollments=validate_enrollments)
    exec(compile(candidate,'<frozen-full-run-operational-resume>','exec'),namespace)
    checkpoint('validating_registration_and_rebuilding_complete_gallery',preserved_queries=len(queries),remaining=len(todo))
    try:
        namespace['run'](a)
        assert ledger.read_bytes().startswith(raw),'Previously logged bytes changed'
        for path,digest in dependencies['source_sha256'].items():assert base.source_sha(path)==digest,path
        final=json.loads((a.root/'evaluation/results.json').read_text());assert final['complete'] and final['originals_unchanged']
        base.save(status,dict(complete=True,state='complete',queries=3217,inference_pid=os.getpid()))
    except Exception as error:
        checkpoint('failed_preserving_all_results',failure=type(error).__name__+': '+str(error));raise


if __name__=='__main__':main()
