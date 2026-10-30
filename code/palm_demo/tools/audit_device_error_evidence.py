"""Observe frozen Windows v26 errors, five-frame evidence and geometric support.

Selection is all remaining mistakes plus four fixed controls. Decisions and
thresholds remain unchanged. Export scalar diagnostics only; arrays stay in RAM.
"""
import argparse,hashlib,inspect,json,os,shutil,threading
from pathlib import Path
import cv2,numpy as np
from evaluate_six_person_frozen import initialize
from replay_pi_pipeline import http_app,save_json
from replay_ready_queries import power_sample,power_fault
from retained_evidence_pilot import install_retained_evidence_pilot
from fastcc_valid_support import propagate_support,compare_codes,constant_rf_mask
from pose_matcher import POSES
import staged_index_matcher
from replay_pi_pipeline import ReplayCamera,debug_ui
from pklnet_roi import PKLNetROI
from templates import TemplateStore
from audit_halfturn_recovery import verify_sources,source_sha
import time

APP=Path(__file__).resolve().parents[1]
MATCHER='FastCCCompNetAlternateROI-v26-experimental'


def initialize_windows(runtime):
    begin=time.perf_counter();engine=PKLNetROI(threads=3);engine._ensure_loaded()
    engine._session.run(['keypoints','heatmap_keypoints','fc_keypoints'],{'image':np.zeros((1,3,400,300),np.float32)})
    camera=ReplayCamera(False,engine);debug_ui.common.RUNTIME=runtime
    app=debug_ui.App(camera,demo_matcher=MATCHER)
    assert app.demo_algorithm.name==MATCHER and type(app.demo_algorithm).__name__=='CompNetAlternateROIMatcher'
    return app,camera,dict(ms=(time.perf_counter()-begin)*1000,actual_matcher=app.demo_algorithm.name,
        actual_type=type(app.demo_algorithm).__name__,host='Windows; unchanged OpenCV BF registration')


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in('baseline','output'):p.add_argument(name,type=Path)
    p.add_argument('--model-root',required=True,type=Path)
    a=p.parse_args();assert os.name=='nt';verify_sources()
    b=json.loads((a.baseline/'results.json').read_text());assert b['complete'] and b['executed_matcher']==MATCHER
    a.manifest=APP/'runtime/halfturn-recovery-20261030/device-manifest-local.json'
    rows={r['sample']:r for r in json.loads(a.manifest.read_text())}
    protocol=json.loads((APP/'runtime/pi5-under2-20261028/active169-baseline-20261029/protocol.json').read_text());cases={c['name']:c for c in protocol['cases']}
    refs={(r['case'],q['sample']):q for r in b['runs']for q in r['queries']}
    historical=json.loads((APP/'runtime/pi5-under2-20261028/retained-evidence-full168-results-20261030.json').read_text())
    assert historical['complete'];oldrefs={(q['case'],q['sample']):q for q in historical['queries']}
    selected={k for k,q in refs.items()if not q['correct']}
    selected.add(max(refs,key=lambda k:refs[k]['ms']))
    selected.update(k for k,q in oldrefs.items()if q['correct']and not q['reference_correct'])
    case=next(k[0]for k in sorted(selected)if not refs[k]['correct'])
    selected.add(min((k for k,q in refs.items()if k[0]==case and q['correct']and q['result']['recognition_route']=='exhaustive_retained_fastcc_pilot'),key=lambda k:k[1]))
    selected.add(min((k for k,q in refs.items()if k[0]==case and q['correct']and q['ms']<=2500),key=lambda k:k[1]))
    assert len(selected)==7 and all(sha(Path(r['original']))==r['sha256'] for r in rows.values())
    assert not a.output.exists();a.output.mkdir();cv2.setNumThreads(1);os.environ['PALM_COMPNET_MODEL_ROOT']=str(a.model_root.resolve())
    patch=install_retained_evidence_pilot();report=dict(complete=False,selection=sorted(selected),queries=[],power_samples=[],
        baseline_sha256=sha(a.baseline/'results.json'),manifest_sha256=sha(a.manifest),
        evaluator_sha256=source_sha(__file__),helper_sha256=source_sha(Path(__file__).with_name('fastcc_valid_support.py')),
        matcher=MATCHER,host='Windows instrumented diagnostics; not performance timing',initializations=[],
        warning=__doc__,missing_in_old_logs=['FastCC dx/dy and receptive-field support','CompNet per-frame independent angular scores'])
    source_hashes={str(path):sha(path)for path in a.baseline.glob('*/runtime/demo_templates/*')if path.is_file()}
    def checkpoint():
        save_json(a.output/'results.json',report)
    checkpoint()
    try:
      for case in dict.fromkeys(k[0]for k in sorted(selected)):
        source=a.baseline/case/'runtime';runtime=a.output/case/'runtime';runtime.parent.mkdir()
        shutil.copytree(source,runtime,ignore=shutil.ignore_patterns('demo_templates'));store=runtime/'demo_templates';store.mkdir()
        for path in(source/'demo_templates').iterdir():
            if path.is_file():(store/path.name).symlink_to(path.resolve())
        app,camera,startup=initialize_windows(runtime);algorithm=app.demo_algorithm
        report['initializations'].append(dict(case=case,**startup))
        geometries={};template_store=TemplateStore(source/'demo_templates')
        for user,samples in cases[case]['enrollment'].items():
            features,metadata=template_store.load(user.replace(':','-'))
            assert metadata['algorithm']==MATCHER and len(features)==5
            for sample,feature in zip(samples,features):
                unpacked=algorithm._unpack(feature,decode_native=False)
                geometries[case,sample]=dict(source_matrix=unpacked[1][2].copy())
            del features
        assert getattr(app.demo.gallery,'acceptance_policy',None)is None and app.demo.gallery.threshold==1 and app.demo.gallery.min_margin==0
        algorithm._retain_fastcc_evidence_pilot=True;active=[None];local=threading.local();rf=constant_rf_mask()
        old_score=algorithm.score_gallery;old_extract=algorithm.extract_probe_with_context;old_pair=algorithm._match_unpacked;old_legacy=algorithm._legacy_pair
        old_embed=algorithm._embedding;old_warp=cv2.warpPerspective;old_feature=algorithm.base.extract;old_match=algorithm.base.match
        target_ids={};target_codes={};mask_cache={};grid_cache={};pose_maps={};gallery_keys=[];gallery_vectors=[]
        source_planes={}
        def support(shape,chain):
            key=(tuple(shape),tuple((np.asarray(m).tobytes(),tuple(size))for m,size in chain))
            if key not in mask_cache:
                # propagate_support uses actual raster operations; retaining an
                # all-one native plane saves allocation, not feature answers.
                if tuple(shape)not in source_planes:source_planes[tuple(shape)]=np.ones(shape,np.float32)
                mask_cache[key]=propagate_support(shape,chain,source_planes[tuple(shape)])
            return mask_cache[key]
        def compare(left,right,lmask,rmask):
            key=tuple(np.asarray(v,bool).tobytes()for v in(left,right,lmask,rmask))
            if key not in grid_cache:grid_cache[key]=compare_codes(left,right,lmask,rmask)
            return grid_cache[key]
        def capture(full,quad,pixels):
            if active[0]is not None:active[0]['query_quad']=np.asarray(quad).tolist()
            return old_extract(full,quad,pixels)
        def warper(src,matrix,size,*args,**kw):
            value=old_warp(src,matrix,size,*args,**kw)
            if active[0]is None or tuple(size)!=(128,128)or np.asarray(src).ndim!=2:return value
            frame=inspect.currentframe().f_back;owner=Path(frame.f_code.co_filename).name
            if owner not in {'registered_matcher.py','union_matcher.py','staged_index_matcher.py','linked_enrollment_matcher.py','affine_enrollment_matcher.py','pooled_enrollment_matcher.py','<isolated-retained-fastcc-pilot>'}:return value
            probe=active[0]['probe'];chain=[]
            if src.shape==probe.native.shape:chain=[(matrix,(128,128))]
            elif src.shape==(768,768):
                offset=np.asarray([[1.,0,192],[0,1.,192],[0,0,1.]])
                chain=[(offset@probe.source,(768,768)),(matrix,(128,128))]
            else:active[0]['missing'].append(dict(reason='Unmapped scored warp source',owner=owner,shape=list(src.shape)));return value
            valid,info=support(probe.native.shape,chain)
            local.pending=(value,valid,dict(owner=owner,function=frame.f_code.co_name,matrix=np.asarray(matrix).tolist(),source_shape=list(src.shape),support=info))
            return value
        def feature(pixels):
            value=old_feature(pixels);pending=getattr(local,'pending',None);local.pending=None;local.extracted=None
            if pending is not None:
                from pklnet_roi import normalize_roi_pixels
                crop,mask,info=pending
                if np.array_equal(pixels,normalize_roi_pixels(crop)):local.extracted=(value,mask,info)
                else:active[0]['missing'].append(dict(reason='Warp/extraction provenance mismatch',**info))
            return value
        def matching(left,right):
            value=old_match(left,right)
            if active[0]is None or not target_codes:return value
            counts=active[0]['matching_coverage'];counts['calls']+=1
            encoded=np.asarray(right,bool).tobytes();targets=target_ids.get(id(right))
            if targets is None:
                who=getattr(local,'target',None)
                targets=[v for v in target_codes.get(encoded,[])if who is None or v['key']==who]
            if not targets:counts['unknown_target']+=1;return value
            extracted=getattr(local,'extracted',None);local.extracted=None
            if extracted is not None and np.array_equal(left,extracted[0]):
                counts['geometric_calls']+=1
                _,valid,info=extracted
                for target in targets:
                    grid=compare(left,right,valid,target['mask']);assert grid['original_score']==value
                    active[0]['geometry_matches'].append(dict(target=target['key'],target_view=target['view'],**info,**grid,
                        full_rf_support=bool(np.array_equal(valid,rf)and np.array_equal(target['mask'],rf))))
            else:
                known=pose_maps.get(np.asarray(left,bool).tobytes(),[])
                if known:counts['pose_calls']+=1
                else:counts['unknown_query']+=1
                for pose in known:
                    for target in targets:
                        if target['view']!='base':continue
                        grid=compare(left,right,pose['mask'],target['mask']);assert grid['original_score']==value
                        key=(*target['key'],pose['index'])
                        if key not in active[0]['pose_map']:
                            active[0]['pose_map'][key]=dict(target=target['key'],pose_index=pose['index'],angle=POSES[pose['index']][0],scale=POSES[pose['index']][1],query_support=pose['info'],target_valid_features=int(target['mask'].sum()),
                                full_rf_support=bool(np.array_equal(pose['mask'],rf)and np.array_equal(target['mask'],rf)),**grid)
            return value
        def embedding(native,matrix):
            vector=old_embed(native,matrix)
            if active[0]is not None and gallery_keys:
                values=np.arccos(np.clip(np.asarray(gallery_vectors)@vector,-1,1))/np.pi
                pairs=dict(zip(gallery_keys,values));scores={u:algorithm._aggregate([pairs[u,j]for j in range(5)])for u in active[0]['users']}
                ranked=sorted(scores,key=scores.get);first,second=[scores[u]for u in ranked[:2]]
                active[0]['compnet'].append(dict(kind='primary'if np.array_equal(matrix,active[0]['probe'].source)else'alternate',source_matrix=matrix.tolist(),scores=scores,
                    frames=[dict(identity=u,index=j,score=float(pairs[u,j]))for u,j in gallery_keys],frame_dtype='float32',
                    ranking=ranked,top1=ranked[0],top2=ranked[1],score=first,second_score=second,gap=second-first,
                    distance_pass=first<=.32,margin_pass=second-first>=.08,confident=algorithm.confident(scores)))
            return vector
        def scoped(fn,query,target,*args):
            previous=getattr(local,'target',None);local.target=target_ids[id(target)][0]['key']
            try:return fn(query,target,*args)
            finally:local.target=previous
        def pair(query,target,details=None):
            trace=[] if details is None else details
            value=scoped(old_pair,query,target,trace)
            active[0]['exhaustive_pairs'].append(dict(target=target_ids[id(target)][0]['key'],score=value,attempts=trace))
            return value
        def legacy(probe,primary,secondary,target):
            previous=getattr(local,'target',None);local.target=target_ids[id(target)][0]['key']
            try:return old_legacy(probe,primary,secondary,target)
            finally:local.target=previous
        def scoring(probe,groups):
            target_ids.clear();target_codes.clear();pose_maps.clear();gallery_keys.clear();gallery_vectors.clear();grid_cache.clear()
            active[0].update(probe=probe,users=list(groups));quad=np.asarray(active[0]['query_quad'],np.float32);center=quad.mean(0)
            for i,bank in enumerate(probe.bank):
                if bank[0,0]<0:continue
                angle,scale=POSES[i];rad=np.deg2rad(angle);rot=np.asarray([[np.cos(rad),-np.sin(rad)],[np.sin(rad),np.cos(rad)]])
                candidate=quad if i==0 else((quad-center)@rot.T*scale+center).astype(np.float32)
                dst=np.asarray([[128,0],[0,0],[0,128],[128,128]]if algorithm.geometry.isAntiClock(candidate[:3].reshape(-1))else[[0,0],[128,0],[128,128],[0,128]],np.float32)
                mask,info=support(probe.native.shape,[(cv2.getPerspectiveTransform(candidate,dst),(128,128))])
                pose_maps.setdefault(bank.astype(bool).tobytes(),[]).append(dict(index=i,mask=mask,info=info))
            for user,samples in groups.items():
                for j,sample in enumerate(samples):
                    sample_id=next(ss[j]for u,ss in cases[case]['enrollment'].items()if u.replace(':','-')==user)
                    geo=geometries[case,sample_id];shape=(rows[sample_id]['height'],rows[sample_id]['width'])
                    mask,_=support(shape,[(np.diag([1/3,1/3,1])@np.asarray(geo['source_matrix']),(128,128))])
                    base=dict(key=(user,j),view='base',mask=mask);target_codes.setdefault(sample[0].astype(bool).tobytes(),[]).append(base)
                    for obj in(sample,sample[3],sample[0]):target_ids[id(obj)]=[base]
                    for vi,view in enumerate(sample[1]):
                        vm,_=support(shape,[(np.diag([1/3,1/3,1])@view[1],(128,128))]);entry=dict(key=(user,j),view=[vi],mask=vm)
                        target_codes.setdefault(np.asarray(view[4],bool).tobytes(),[]).append(entry)
                        if id(view[4])in target_ids:
                            previous=target_ids[id(view[4])][0];assert np.array_equal(previous['mask'],vm)
                            if isinstance(previous['view'],list):previous['view'].append(vi)
                        else:target_ids[id(view[4])]=[entry]
                    gallery_keys.append((user,j));gallery_vectors.append(sample[5])
            value=old_score(probe,groups);active[0]['scores']=dict(value)
            return value
        algorithm.extract_probe_with_context=capture;algorithm.score_gallery=scoring;algorithm._match_unpacked=pair;algorithm._legacy_pair=legacy;algorithm._embedding=embedding
        algorithm.base.extract=feature;algorithm.base.match=matching;cv2.warpPerspective=warper
        before=app.demo.payments.transaction_count()
        try:
            with http_app(app)as(request,trace):
                for key in sorted(k for k in selected if k[0]==case):
                    checkpoint();ref=refs[key];row=rows[key[1]];assert sha(Path(row['original']))==row['sha256'];camera.select([row])
                    algorithm._retained_evidence_trace=None
                    active[0]=dict(pose_map={},geometry_matches=[],compnet=[],missing=[],exhaustive_pairs=[],
                        matching_coverage=dict(calls=0,geometric_calls=0,pose_calls=0,unknown_target=0,unknown_query=0))
                    status,response=request('/api/demo/identify',{},None);record=active[0];active[0]=None
                    assert record['scores']==ref['diagnostics']['scores']and status==ref['http_status']
                    assert all(response.get(k)==ref['result'].get(k)for k in('status','user_id','score','second_score','recognition_route'))
                    record.pop('probe');record['poses']=list(record.pop('pose_map').values())
                    retained=algorithm._retained_evidence_trace
                    record['retained_frames']={name:[dict(identity=u,index=j,score=float(score))for(u,j),score in sorted(values.items())]
                        for name,values in retained.items()} if retained else None
                    record.update(case=case,sample=key[1],identity=row['identity'],reference_correct=ref['correct'],reference_equal=True,instrumented_ms=trace[-1]['ms'],
                        result={k:v for k,v in response.items()if k not in('token','roi_image','expires_at')})
                    report['queries'].append(record)
                    if response.get('token'):request('/api/demo/cancel',dict(token=response['token']),200)
                    checkpoint();print(case,key[1],len(record['poses']),len(record['geometry_matches']),len(record['compnet']),record['missing'],flush=True)
            assert app.demo.payments.transaction_count()==before
        finally:
            cv2.warpPerspective=old_warp;algorithm.base.extract=old_feature;algorithm.base.match=old_match;algorithm.close()
      report['source_templates_unchanged']=all(sha(Path(path))==value for path,value in source_hashes.items());assert report['source_templates_unchanged']
      verify_sources();report['originals_unchanged']=all(sha(Path(r['original']))==r['sha256'] for r in rows.values())
      report['complete']=True;checkpoint()
    except Exception as e:
      report['failure']=type(e).__name__+': '+str(e);checkpoint();raise
    finally:staged_index_matcher.StagedIndexMatcher.score_gallery=patch['original']


if __name__=='__main__':main()
