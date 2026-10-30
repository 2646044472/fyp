"""Bounded container equivalence diagnostic, never a public evaluation runner.

Fresh original-device references in one fixed six-identity gallery; one query
per previously recorded route. The stopped SMPD input is extraction-only. No
old feature arrays imported, no public query result appended, no thresholds fit.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

import cv2
import numpy as np
from PIL import Image,ImageOps
import psutil

APP=Path(__file__).resolve().parents[1];sys.path.insert(0,str(APP))
from smpd_run_journal import atomic,digest,file_sha,load
from biometric import load_algorithm
from compnet_alternate_roi_matcher import CompNetAlternateROIMatcher
from lossless_union_matcher import LosslessUnionMatcher
from lossless_template_store import LosslessTemplateStore,SCHEMA
from templates import TemplateStore
from pklnet_roi import PKLNetROI,normalize_roi
from union_lossless_codec import decode,MAX_FEATURE_BYTES,MAX_NATIVE_PIXELS,MAX_NATIVE_SIDE,CODEC,HEADER
from retained_evidence_pilot import install_retained_evidence_pilot
from terminal_rf_evidence import install as install_rf


def equal(left,right):
    if isinstance(left,np.ndarray):
        return isinstance(right,np.ndarray) and left.dtype==right.dtype and left.shape==right.shape and left.tobytes()==right.tobytes()
    if isinstance(left,(tuple,list)):
        return isinstance(right,(tuple,list)) and len(left)==len(right) and all(equal(a,b) for a,b in zip(left,right))
    return left==right


def resources():
    info=psutil.Process().memory_info()
    return dict(rss_bytes=info.rss,peak_rss_bytes=getattr(info,'peak_wset',info.rss),available_bytes=psutil.virtual_memory().available)


def preserved():
    root=APP/'runtime/smpd-terminal-rf-20261031-r2'
    snapshot=APP/'runtime/union-lossless-fix-20261031/preserved-r2'
    entries=load(snapshot/'preservation-manifest.json')
    for row in entries:
        if file_sha(root/row['path'])!=row['sha256']:raise ValueError('Preserved stopped checkpoint changed: '+row['path'])
    original=APP/'runtime/smpd-full-20261030'
    receipt=load(original/'stop-receipt-20261030-144708/receipt.json')
    assert file_sha(original/'evaluation/results.json')==receipt['results_sha256']
    assert file_sha(original/'evaluation/queries.jsonl')==receipt['queries_jsonl_sha256']
    return dict(files=len(entries),query_records=70,inflight=load(root/'inflight.json')['sample'],old241_unchanged=True)


def inputs(row,engine,exif=False):
    data=Path(row['original']).read_bytes()
    assert hashlib.sha256(data).hexdigest()==row['sha256']
    import io
    with Image.open(io.BytesIO(data)) as encoded:
        image=(ImageOps.exif_transpose(encoded) if exif else encoded).convert('RGB')
    raw,quad,details=engine.extract(image)
    if not details['roi_geometry_valid']:raise ValueError('Fixed diagnostic ROI failed: '+row['sample'])
    roi,_=normalize_roi(raw)
    return image,quad,roi,details


def source_lock():
    files=list(APP.glob('*.py'))+list((APP/'palm_app').rglob('*.py'))
    files+=[Path(__file__),APP/'tools/terminal_rf_evidence.py',APP/'tools/fastcc_valid_support.py',APP/'tools/retained_evidence_pilot.py']
    return {str(p.relative_to(APP)):file_sha(p) for p in sorted(set(files))}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('output',type=Path);parser.add_argument('--model',required=True,type=Path)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    fixed=load(APP/'runtime/pi5-under2-20261028/active169-baseline-20261029/protocol.json')
    case=next(c for c in fixed['cases'] if c['name']=='new-camera-original')
    reference=load(APP/'runtime/terminal-rf-full168-20261030/evaluation/results.json')
    run=next(r for r in reference['runs'] if r['case']==case['name'])
    refs={q['sample']:q for q in run['queries']};queries=[];routes=set()
    for sample in case['queries']:
        route=refs[sample]['terminal_rf']['original_route']
        if route not in routes:queries.append(sample);routes.add(route)
    rows={r['sample']:r for r in load(APP/'runtime/halfturn-recovery-20261030/device-manifest-local.json')}
    model=args.model.resolve();engine=PKLNetROI(threads=3)
    hashes={'compnet':file_sha(model/'compnet-tongji.onnx'),'pklnet':file_sha(engine.root/'pklnet-keypoints-diagnostics.onnx')}
    assert hashes==dict(compnet='b513e614a8b1a4448ef58c1b7f288f760fc991ce31d0a35079b4f9226146d1ea',
        pklnet='bf477f1778f03ccc203b64dd0c84d418c9bb22839a23ba923f479ab991aa067f')
    plan=dict(scope=__doc__,case=case,queries=queries,query_rule='First recorded query per original route, in fixed protocol order; no accuracy selection.',
        models=hashes,source_sha256=source_lock(),public_query_results_started=False,full_smpd_started=False,
        checkpoint_preservation=preserved(),thresholds=dict(early_distance=.32,early_margin=.08,final_distance=1.,final_margin=0.,rejection=False),
        limits=dict(max_feature_bytes=MAX_FEATURE_BYTES,max_native_pixels=MAX_NATIVE_PIXELS,max_native_side=MAX_NATIVE_SIDE),
        registration_feature_reuse=False,query_feature_reuse=False)
    plan['diagnostic_fingerprint']=digest(plan);atomic(args.output/'protocol.json',plan,exclusive=True)
    report=dict(complete=False,diagnostic_fingerprint=plan['diagnostic_fingerprint'],fresh_enrollments=[],queries=[],models=hashes,
        scope='Bounded Windows lossless-format diagnostic; no full public evaluation or Pi timing claim.',started_unix=time.time())
    checkpoint=lambda:atomic(args.output/'results.json',report)
    checkpoint();cv2.setNumThreads(1);install_retained_evidence_pilot()
    baseline=APP/'vendor/palmprint-recognition-python'
    old=CompNetAlternateROIMatcher(load_algorithm(baseline,'FastCC'),model_root=model)
    new=LosslessUnionMatcher(load_algorithm(baseline,'FastCC'),model_root=model)
    old._retain_fastcc_evidence_pilot=True;new._retain_fastcc_evidence_pilot=True
    install_rf(old);install_rf(new);old_store=TemplateStore(args.output/'fresh-v26');new_store=LosslessTemplateStore(args.output/'fresh-v27')
    try:
        groups_old={};groups_new={}
        for identity,samples in case['enrollment'].items():
            left=[];right=[]
            for sample in samples:
                if psutil.virtual_memory().available<2*1024**3:raise MemoryError('Diagnostic host resource guard')
                full,quad,roi,details=inputs(rows[sample],engine)
                hypotheses=old.complete_hypotheses(full,details['pklnet_roi_candidates'],engine)
                a=old.extract_with_hypotheses(full,quad,roi,hypotheses)
                b=new.extract_with_hypotheses(full,quad,roi,hypotheses)
                da,db=decode(a),decode(b)
                assert equal(da.parts,db.parts) and da.logical_sha256()==db.logical_sha256()
                left.append(a);right.append(b)
                report['fresh_enrollments'].append(dict(sample=sample,bytes_old=a.size,bytes_new=b.size,
                    query_views=len(db.query_chunks),gallery_views=len(db.gallery_chunks),all_tensors_byte_equal=True,
                    png_byte_equal=da.png.tobytes()==db.png.tobytes(),logical_sha256=db.logical_sha256()))
                checkpoint();print('fresh-frame',len(report['fresh_enrollments']),sample,b.size,flush=True)
            user=identity.replace(':','-');meta=dict(user=user,algorithm=old.name,roi_geometry=engine.roi_geometry,capture_profile='noir-ir',samples=5)
            old_store.save(user,np.stack(left),meta);new_store.save(user,right,dict(meta,algorithm=new.name))
            loaded_a,_=old_store.load(user);loaded_b,_=new_store.load(user)
            groups_old[user]=old.prepare_enrollment(loaded_a);groups_new[user]=new.prepare_enrollment(loaded_b)
            assert equal(groups_old[user],groups_new[user])
            del left,right,loaded_a,loaded_b
        for sample in queries:
            full,quad,roi,details=inputs(rows[sample],engine)
            def probe(algorithm):
                feature=algorithm.extract_probe_with_context(full,quad,roi)
                feature.localization_candidates=details['pklnet_roi_candidates']
                def exhaustive():
                    h=algorithm.complete_hypotheses(full,details['pklnet_roi_candidates'],engine)
                    return algorithm.extract_with_hypotheses(full,quad,roi,h)
                feature.exhaustive=exhaustive
                return feature
            a,b=probe(old),probe(new)
            scores_old=old.score_gallery(a,groups_old);scores_new=new.score_gallery(b,groups_new)
            assert scores_old==scores_new and a.route==b.route
            trace_old,trace_new=old._terminal_rf_trace,new._terminal_rf_trace
            for key in ('original_scores','original_route','ordinary_calls','unknown_calls','exhaustive_callback_calls','captured_pairs','rf_applied','rf_unique_comparisons'):
                assert trace_old[key]==trace_new[key],key
            assert trace_new['unknown_calls']==0
            report['queries'].append(dict(sample=sample,route=a.route,original_route=trace_new['original_route'],
                complete_gallery_score_vector_equal=True,all_prepared_tensors_byte_equal=True,scores=scores_new,
                original_scores_equal=True,comparison_provenance_equal=True,rf_applied=trace_new['rf_applied']))
            report['memory']=resources();checkpoint();print('same-gallery-query',sample,a.route,flush=True)
        # Reproduce only the packing failure; do not rank this public query or
        # create a new SMPD query/checkpoint/result. Its original remains intact.
        public=load(APP/'runtime/smpd-terminal-rf-20261031-r2/protocol.json')
        row=next(r for r in public['rows'] if r['sample']=='smpd-003-F-05')
        full,quad,roi,details=inputs(row,engine,exif=True)
        hypotheses=old.complete_hypotheses(full,details['pklnet_roi_candidates'],engine)
        original_pack=old._pack;captured=[]
        def observe(*parts):
            captured.append(parts)
            return original_pack(*parts)
        old._pack=observe
        try:old.extract_with_hypotheses(full,quad,roi,hypotheses)
        except ValueError as error:
            assert 'capacity exceeded' in str(error);old_error=str(error)
        else:raise AssertionError('Fixed public overflow did not reproduce')
        finally:old._pack=original_pack
        assert len(captured)==1
        payload=new.extract_with_hypotheses(full,quad,roi,hypotheses);parts=decode(payload)
        legacy,png,views,gallery=captured[0]
        before=(legacy,png,*gallery,*views)
        assert len(before)==len(parts.chunks) and all(equal(a,b) for a,b in zip(before,parts.chunks))
        report['overflow_extraction_only']=dict(sample=row['sample'],old_error=old_error,new_bytes=payload.size,
            used_before_old_header=20+sum(c.size for c in before),legacy_bytes=legacy.size,png_bytes=png.size,
            query_views=len(views),gallery_views=len(gallery),all_input_blocks_byte_equal=True,
            scored=False,correctness_claim=False,logical_sha256=parts.logical_sha256())
        report['memory']=resources();report['checkpoint_preservation']=preserved()
        assert source_lock()==plan['source_sha256']
        report.update(complete=True,passed=True,ended_unix=time.time(),next_public_run_required=True,
            old70_prefix_compatible=False,registration_reuse_certified=False,full_public_evaluation_started=False)
        checkpoint();print(json.dumps(dict(passed=True,enrollment_frames=len(report['fresh_enrollments']),same_gallery_queries=len(report['queries']),overflow_bytes=payload.size,memory=report['memory'])),flush=True)
    except Exception as error:
        report['failure']=type(error).__name__+': '+str(error);checkpoint();raise
    finally:old.close();new.close()


if __name__=='__main__':main()
