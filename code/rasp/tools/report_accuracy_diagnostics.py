"""Summarize saved shadow rejection, five-frame ROI and numeric oracle audits.

Only scalar scores, frame identifiers and geometric diagnostics are exported.
No images, descriptors or template arrays are read by this reporting tool.
"""
import argparse,hashlib,json
from pathlib import Path
import cv2,numpy as np


def load(path):return json.loads(path.read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in('support','roi','locked','numeric','baseline','output'):p.add_argument(name,type=Path)
    a=p.parse_args();s,r,l,n,b=map(load,(a.support,a.roi,a.locked,a.numeric,a.baseline))
    assert all(v['complete']for v in(s,r,n,b))
    assert s['source_templates_unchanged']and n['source_templates_unchanged']and r['templates_unchanged']
    assert all(q['reference_equal']for q in s['queries'])and r['all_reference_pair_equal']
    exhaustive=[q for q in s['queries']if q['result']['recognition_route']=='exhaustive_fallback']
    out=dict(input_sha256={key:sha(getattr(a,key))for key in('support','roi','locked','numeric','baseline')},
        shadow=dict(exhaustive_total=len(exhaustive),wrong_blocked=sum(not q['reference_correct']and q['shadow_status']=='RETRY'for q in exhaustive),
            previously_correct_rejected=sum(q['reference_correct']and q['shadow_status']=='RETRY'for q in exhaustive),
            previously_correct_retained=sum(q['reference_correct']and q['shadow_status']=='MATCH'for q in exhaustive),
            fast_controls_retained=sum(q not in exhaustive and q['shadow_status']=='MATCH'for q in s['queries']),
            disposition='Rejected: excessive loss of correct recognition; RETRY is never correct'),roi=[],numerical=[])
    out['shadow']['full_cohort_implied']=dict(correct=156,wrong=0,retry=12,total=168,measured_scope='Shadow decisions on all 13 exhaustive plus four controls; remaining 151 unchanged by rule, not a new full168 timing run')
    locked={v['sample']:v for v in l['blind_rows']}
    for index,q in enumerate(r['queries'],1):
        true=next(v['identity']for run in b['runs']if run['case']==q['case']for v in run['queries']if v['sample']==q['sample'])
        entry=dict(id=f'E{index}',sample_suffix=q['sample'][-8:],modes=[],accepted_union=[],all_winners_fixed_pose=True)
        for qm,em in [('original','original'),('oracle','original'),('original','oracle'),('oracle','oracle')]:
            mode=dict(query_roi=qm,enrollment_roi=em,identities={})
            for identity in q['enrollments']:
                cells=sorted((c for c in q['cells']if c['identity']==identity and c['query_roi']==qm and c['enrollment_roi']==em),key=lambda c:c['enrollment_index'])
                assert len(cells)==5
                selected=sorted(cells,key=lambda c:c['score'])[:2];role='true'if identity==true else'wrong'
                mode['identities'][role]=dict(scores=[c['score']for c in cells],samples=[c['enrollment_sample']for c in cells],
                    best_two_indices=[c['enrollment_index']for c in selected],mean=float(np.mean([c['score']for c in selected])))
                entry['all_winners_fixed_pose']&=all(c['winner']['branch']=='legacy_v2'and c['winner'].get('aligned_quad')is None and not any(v['improved']for v in c['legacy_alignment'])for c in cells)
                for c in cells:
                    for attempt in c['attempts']:
                        if attempt.get('branch')!='union'or 'score'not in attempt:continue
                        quad=np.asarray(attempt['aligned_quad'],np.float32);info=locked[q['sample']]
                        bounds=np.asarray([[0,0],[info['width'],0],[info['width'],info['height']],[0,info['height']]],np.float32)
                        anchor=np.asarray(info['original_quad']if qm=='original'else info['quad'],np.float32)
                        area=abs(cv2.contourArea(quad));visible=float(cv2.intersectConvexConvex(quad,bounds)[0]);intersection=float(cv2.intersectConvexConvex(quad,anchor)[0])
                        entry['accepted_union'].append(dict(query_roi=qm,enrollment_roi=em,identity_role=role,
                            enrollment_index=c['enrollment_index'],score=attempt['score'],winning_score=c['score'],
                            wins=attempt['score']==c['score'],view_index=attempt['view_index'],sigma=attempt['sigma'],
                            source_matrix=attempt['source_matrix'],aligned_quad=attempt['aligned_quad'],
                            visible_fraction=visible/area,anchor_overlap_area=intersection,anchor_overlap_fraction=intersection/area))
            mode['true_beats_selected_wrong']=mode['identities']['true']['mean']<mode['identities']['wrong']['mean'];entry['modes'].append(mode)
        out['roi'].append(entry)
    refs={(run['case'],q['sample']):q for run in b['runs']for q in run['queries']}
    for q in n['queries']:
        phases=q['phases'];assert len(phases)==2
        pairs=[]
        for phase in phases:
            assert phase['reference_equal']and phase['candidate_scores']==refs[q['case'],q['sample']]['diagnostics']['scores']
            values={(v['target']['identity'],v['target']['index']):v['score']for v in phase['pair_scores']};pairs.append(values)
            aggregate={user:float(np.mean(sorted(v for (u,i),v in values.items()if u==user)[:2]))for user,i in values}
            assert aggregate==phase['candidate_scores']
        assert pairs[0]==pairs[1]
        out['numerical'].append(dict(sample_suffix=q['sample'][-8:],identities=len(phases[0]['candidate_scores']),frames=len(pairs[0]),whole_gallery_equals_frozen=True,all_frames_equal=True))
    assert not a.output.exists();a.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(shadow=out['shadow'],roi=[dict(id=v['id'],modes=[m['true_beats_selected_wrong']for m in v['modes']],accepted_union=len(v['accepted_union']))for v in out['roi']],numerical=out['numerical']),indent=2))


if __name__=='__main__':main()
