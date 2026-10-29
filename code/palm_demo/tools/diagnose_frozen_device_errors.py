"""Trace every frozen-cohort mistake and one fallback control per case.

Only diagnostics are added. No candidate, transform, score or gate is changed.
Instrumented time is not a replacement for the baseline HTTP latency evidence.
"""
import argparse,base64,hashlib,json,os,shutil,time
import threading
from pathlib import Path
import cv2
import numpy as np
from replay_pi_pipeline import ReplayCamera,debug_ui,http_app,save_json
from replay_ready_queries import power_sample,power_fault
from replay_demo_manifest import correct_identification
from evaluate_six_person_frozen import initialize,sanitized
from anchored_matcher import FastCCAnchoredUnionMatcher
from pose_matcher import FastCCPoseMatcher


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('manifest',type=Path);p.add_argument('baseline',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--native-registration',type=Path,required=True)
    p.add_argument('--wrong-only',action='store_true',help='Drill into only erroneous queries; omit correct controls')
    p.add_argument('--geometry-details',action='store_true',help='Observe actual RANSAC outputs without rerunning or changing estimators')
    p.add_argument('--model-root',type=Path,help='Frozen CompNet model directory for v25/v26')
    args=p.parse_args();data=json.loads((args.baseline/'results.json').read_text())
    protocol=data.get('protocol')
    if protocol is None:
        source=Path(data['baseline'])/'results.json'
        assert hashlib.sha256(source.read_bytes()).hexdigest()==data['baseline_results_sha256']
        protocol=json.loads(source.read_text())['protocol']
    matcher=data.get('matcher',protocol['matcher'])
    if args.model_root:os.environ['PALM_COMPNET_MODEL_ROOT']=str(args.model_root.resolve())
    assert data.get('complete') is True
    app_root=Path(__file__).resolve().parents[1]
    for name,value in data.get('code_sha256',protocol['code_hashes']).items():assert hashlib.sha256((app_root/name).read_bytes()).hexdigest()==value,name
    assert hashlib.sha256(args.native_registration.read_bytes()).hexdigest()==protocol['native_sha256']
    rows={r['sample']:r for r in json.loads(args.manifest.read_text())}
    args.output.mkdir(exist_ok=False);(args.output/'rois').mkdir()
    source_hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest()
        for p in args.baseline.glob('*/runtime/demo_templates/*') if p.is_file()}
    cv2.setNumThreads(1)
    report=dict(timing_warning='Instrumented HTTP includes trace creation; use frozen baseline for latency.',
        matcher=matcher,baseline_results_sha256=hashlib.sha256((args.baseline/'results.json').read_bytes()).hexdigest(),selection=('All incorrect main queries only.' if args.wrong_only else
            'All incorrect main queries plus first correct fallback query per case (first correct query if none fall back).'),queries=[],power_samples=[])
    def checkpoint():
        sample=power_sample();report['power_samples'].append(sample);save_json(args.output/'diagnostics.json',report)
        if power_fault(sample):raise RuntimeError('Power fault; partial diagnostics saved')
    checkpoint()
    for run in data['runs']:
        selected=[q for q in run['queries'] if not q['correct']]
        controls=[q for q in run['queries'] if q['correct'] and q['result'].get('recognition_route')=='exhaustive_fallback']
        if not controls:controls=[q for q in run['queries'] if q['correct']]
        if controls and not args.wrong_only:selected.append(min(controls,key=lambda q:q['sample']))
        if not selected:continue
        runtime=args.output/run['case']/'runtime'
        runtime.parent.mkdir(parents=True)
        shutil.copytree(args.baseline/run['case']/'runtime',runtime)
        app,camera,startup=initialize(runtime,matcher,args.native_registration)
        original_pose=FastCCPoseMatcher.match
        original_aligned=app.demo_algorithm.legacy._aligned_score
        def traced_pose(owner,probe,candidate):
            probe=owner._validate(probe);candidate=owner._validate(candidate)
            base=candidate[0].astype(bool)
            values=[dict(index=i,score=float(owner.base.match(p.astype(bool),base)))
                for i,p in enumerate(probe) if p[0,0]>=0]
            score=min(v['score'] for v in values)
            if active[0] is not None:
                active[0]['pose_scores'].append(dict(target=getattr(local,'target',None),
                    score=score,winner=min(values,key=lambda v:v['score'])['index'],views=values))
            return score
        def traced_aligned(context,source,size,other,transform,fallback):
            score=original_aligned(context,source,size,other,transform,fallback)
            if active[0] is not None:
                active[0]['legacy_alignments'].append(dict(target=getattr(local,'target',None),
                    score=score,fallback=fallback,improved=score<fallback,
                    transform=transform.tolist(),source_matrix=source.tolist()))
            return score
        FastCCPoseMatcher.match=traced_pose
        app.demo_algorithm.legacy._aligned_score=traced_aligned
        original_pair=app.demo_algorithm._match_unpacked
        original_score=app.demo_algorithm.score_gallery
        original_decisions=FastCCAnchoredUnionMatcher.candidate_decisions
        active=[None];target_ids={}
        local=threading.local();native=app.demo_algorithm.registration;native_pairs=native.pairs
        geometry_originals=[]
        if args.geometry_details:
            for function_name,model in (('estimateAffinePartial2D','similarity'),('estimateAffine2D','affine')):
                original=getattr(cv2,function_name);geometry_originals.append((function_name,original))
                def observe_geometry(*a,_original=original,_model=model,**kw):
                    started=time.perf_counter()
                    value=_original(*a,**kw)
                    estimator_ms=(time.perf_counter()-started)*1000
                    if active[0] is None:return value
                    matrix,mask=value
                    points=[np.asarray(v,np.float32).reshape(-1,2) for v in a[:2]]
                    # Every inlier hull lies within the all-correspondence box.
                    # Observe only: this does not skip or change any estimator.
                    box_bound=min(float(np.prod(np.ptp(v,axis=0))) for v in points)/(384*384)
                    item=dict(model=_model,target=getattr(local,'target',None),pairs=len(a[0]),
                        estimator_ms=estimator_ms,coverage_bbox_upper_bound=box_bound,
                        safely_below_existing_coverage=bool(np.isfinite(box_bound) and box_bound<.02-1e-6))
                    if matrix is None or not np.isfinite(matrix).all():
                        item.update(reason='no_finite_transform',violations=['no_finite_transform'])
                    elif mask is None:
                        item.update(reason='no_inlier_mask',violations=['no_inlier_mask'])
                    else:
                        pa,pb=(np.asarray(v,np.float32).reshape(-1,2) for v in a[:2])
                        keep=mask.ravel().astype(bool);count=int(keep.sum())
                        coverage=min(cv2.contourArea(cv2.convexHull(v[keep])) if count>=3 else 0. for v in (pa,pb))/(384*384)
                        scale=float(np.hypot(matrix[0,0],matrix[1,0]))
                        angle=float(np.rad2deg(np.arctan2(matrix[1,0],matrix[0,0])))
                        singular=np.linalg.svd(matrix[:,:2],compute_uv=False)
                        violations=[]
                        minimum=4 if _model=='similarity' else 6
                        if count<minimum:violations.append('too_few_inliers')
                        if coverage<.02:violations.append('insufficient_coverage')
                        if _model=='similarity':
                            if not .5<=scale<=2:violations.append('scale_out_of_bounds')
                        else:
                            if np.linalg.det(matrix[:,:2])<=0:violations.append('nonpositive_determinant')
                            if singular.min()<.5 or singular.max()>2:violations.append('scale_out_of_bounds')
                            if singular.min()<=0 or singular.max()/singular.min()>1.5:violations.append('excessive_anisotropy')
                        if abs(angle)>40:violations.append('angle_out_of_bounds')
                        if _model=='affine' and not violations:
                            from affine_enrollment_matcher import bounded_affine
                            if not bounded_affine(np.linalg.inv(np.vstack([matrix,[0.,0.,1.]]))):violations.append('inverse_geometry_rejected')
                        item.update(inliers=count,inlier_ratio=count/max(1,len(pa)),coverage=float(coverage),
                            scale=scale,angle=angle,singular_values=singular.tolist(),
                            reason=violations[0] if violations else 'geometry_accepted',violations=violations,
                            matrix=matrix.tolist())
                    active[0]['geometry'].append(item)
                    return value
                setattr(cv2,function_name,observe_geometry)
        def counted_pairs(a,b):
            values=native_pairs(a,b)
            current=getattr(local,'registration',None)
            if current is not None:current['mutual_pairs']=len(values)
            elif active[0] is not None:active[0]['registrations'].append(dict(kind='direct_pairs',left_points=len(a),right_points=len(b),mutual_pairs=len(values)))
            return values
        native.pairs=counted_pairs
        class RegistrationTrace:
            def pairs(self,a,b):return native.pairs(a,b)
            def __call__(self,left,right):
                item=dict(kind='registration',left_points=len(left[1]),right_points=len(right[1]),target=getattr(local,'target',None))
                previous=getattr(local,'registration',None);local.registration=item
                try:
                    value=native(left,right)
                    item['accepted']=value is not None
                    item['reason']=('accepted' if value is not None else 'too_few_descriptors' if min(len(left[1]),len(right[1]))<4
                        else 'too_few_mutual_pairs' if item.get('mutual_pairs',0)<4 else 'ransac_or_geometric_guard')
                    if active[0] is not None:active[0]['registrations'].append(item)
                    return value
                finally:local.registration=previous
        app.demo_algorithm.registration=app.demo_algorithm.legacy.registration=RegistrationTrace()
        def decisions(quad,hypotheses):
            values=original_decisions(quad,hypotheses)
            if active[0] is not None:active[0]['candidate_decisions'].append(dict(anchor=quad.tolist(),decisions=values))
            return values
        def pair(query,target,details=None):
            entries=[] if details is None else details
            previous=getattr(local,'target',None);local.target=target_ids.get(id(target))
            try:score=original_pair(query,target,entries)
            finally:local.target=previous
            if active[0] is not None:
                active[0]['pairs'].append(dict(target=target_ids.get(id(target)),score=score,attempts=entries))
                if 'query_feature_counts' not in active[0]:active[0]['query_feature_counts']=dict(
                    primary=len(query[1][4]),secondary=len(query[2][0]),
                    views=[dict(sigma=sigma,points=len(points)) for sigma,source,points,desc in query[-1]])
            return score
        def scores(probe,groups):
            target_ids.clear();target_ids.update({id(sample[3]):dict(identity=user,index=index)
                for user,samples in groups.items() for index,sample in enumerate(samples)})
            values=original_score(probe,groups)
            if active[0] is not None:active[0].update(scores=dict(values),source_matrix=probe.source.tolist())
            return values
        app.demo_algorithm._match_unpacked=pair;app.demo_algorithm.score_gallery=scores
        FastCCAnchoredUnionMatcher.candidate_decisions=staticmethod(decisions)
        try:
            before=app.demo.payments.transaction_count()
            with http_app(app) as (request,trace):
                for reference in selected:
                    row=rows[reference['sample']]
                    assert hashlib.sha256(Path(row['original']).read_bytes()).hexdigest()==row['sha256']
                    checkpoint();camera.select([row]);active[0]=dict(pairs=[],candidate_decisions=[],registrations=[],geometry=[],pose_scores=[],legacy_alignments=[])
                    status,response=request('/api/demo/identify',{},None)
                    details=active[0];active[0]=None
                    record=dict(case=run['case'],sample=row['sample'],identity=row['identity'],
                        role='wrong' if not reference['correct'] else 'correct_control',http_status=status,
                        result=sanitized(response),instrumented_http_ms=trace[-1]['ms'],baseline_ms=reference['ms'],
                        correct=correct_identification(dict(http_status=status,result=response,identity=row['identity'])),
                        reference_equal=status==reference['http_status'] and all(response.get(k)==reference['result'].get(k)
                            for k in ('status','user_id','score','second_score','recognition_route')),**details)
                    if response.get('roi_image'):
                        value=base64.b64decode(response['roi_image'].split(',')[-1])
                        path=args.output/'rois'/(run['case']+'-'+row['sample']+'.png');path.write_bytes(value)
                        baseline_roi=args.baseline/run['case']/'query-rois'/(row['sample']+'.png')
                        record['roi_byte_equal']=baseline_roi.read_bytes()==value
                    if response.get('token'):request('/api/demo/cancel',dict(token=response['token']),200)
                    report['queries'].append(record);checkpoint()
                    print(run['case'],row['sample'],record['role'],record['reference_equal'],flush=True)
            assert app.demo.payments.transaction_count()==before
        finally:
            FastCCPoseMatcher.match=original_pose
            for name,original in geometry_originals:setattr(cv2,name,original)
            FastCCAnchoredUnionMatcher.candidate_decisions=staticmethod(original_decisions)
            app.demo_algorithm.close()
    report['source_templates_unchanged']=all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==v for p,v in source_hashes.items())
    assert report['source_templates_unchanged']
    report['complete']=True;report['all_reference_equal']=all(q['reference_equal'] for q in report['queries'])
    checkpoint()


if __name__=='__main__':main()
