"""Reconcile frozen error distances against original protocol and response fields.

Read-only input audit. Outputs scalar scores/IDs and geometry metadata only;
never exports images, templates, feature codes or changes the gallery.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import numpy as np


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(baseline, diagnostics, manifest, protocol, geometry, app_root):
    b,d,m,p,g=[json.loads(v.read_text()) for v in (baseline,diagnostics,manifest,protocol,geometry)]
    assert b['complete'] and d['complete'] and d['all_reference_equal']
    assert d['baseline_results_sha256']==digest(baseline)
    assert len(m)==p['images']==169
    assert len({v['sample'] for v in m})==169
    assert all(digest(app_root/name)==sha for name,sha in b['code_sha256'].items())
    rows={v['sample']:v for v in m}
    cases={v['name']:v for v in p['cases']}
    records={(v['case'],v['sample']):v for v in g['records']}
    references={}
    for run in b['runs']:
        assert sorted(q['sample'] for q in run['queries'])==sorted(cases[run['case']]['queries'])
        for q in run['queries']:
            assert rows[q['sample']]['identity']==q['identity']
            if not q['correct']:references[run['case'],q['sample']]=q
    assert sum(len(v['queries']) for v in b['runs'])==168
    assert len(references)==len(d['queries'])==4
    result=dict(complete=False,inputs={str(v):digest(v) for v in (baseline,diagnostics,manifest,protocol,geometry)},
        cohort=dict(images=169,main_queries=168,legacy_170_queries_reused=False),
        formula='float(np.mean(sorted(five_pair_distances)[:2]))',queries=[])
    for q in d['queries']:
        ref=references[q['case'],q['sample']]
        assert q['reference_equal'] and q['roi_byte_equal']
        assert all(q['result'].get(k)==ref['result'].get(k) for k in
            ('status','user_id','score','second_score','recognition_route'))
        groups={u.replace(':','-'):samples for u,samples in cases[q['case']]['enrollment'].items()}
        pairs={(v['target']['identity'],v['target']['index']):v for v in q['pairs']}
        assert len(pairs)==len(q['pairs'])==len(groups)*5
        identities=[]
        for user,samples in groups.items():
            frames=[]
            for i,sample in enumerate(samples):
                v=pairs[user,i];record=records[q['case'],sample]
                assert record['identity'].replace(':','-')==user
                winner=min((a for a in v['attempts'] if 'score' in a),key=lambda a:a['score'])
                assert winner['score']==v['score']
                frames.append(dict(sample=sample,index=i,distance=v['score'],winning_branch=winner['branch'],
                    winning_aligned_quad=winner.get('aligned_quad'),primary_roi_quad=record['quad'],
                    geometry_summary=dict(
                        accepted=[e for e in q['geometry'] if e['target']==v['target'] and e['reason']=='geometry_accepted'],
                        reasons=dict(Counter(e['reason'] for e in q['geometry'] if e['target']==v['target'])),
                        max_inliers=max((e.get('inliers',0) for e in q['geometry'] if e['target']==v['target']),default=0)),
                    pose_scores=[e for e in q['pose_scores'] if e['target']==v['target']],
                    legacy_alignment=[e for e in q['legacy_alignments'] if e['target']==v['target']]))
            chosen=sorted(frames,key=lambda v:v['distance'])[:2]
            score=float(np.mean([v['distance'] for v in chosen]))
            assert score==q['scores'][user],(q['sample'],user,score,q['scores'][user])
            identities.append(dict(identity=user,score=score,best_two_samples=[v['sample']for v in chosen],frames=frames))
        identities.sort(key=lambda v:v['score'])
        assert identities[0]['identity']==ref['result']['user_id']
        assert identities[0]['score']==ref['result']['score']
        assert identities[1]['score']==ref['result']['second_score']
        for rank,identity in enumerate(identities,1):identity['rank']=rank
        true_user=q['identity'].replace(':','-');true=next(v for v in identities if v['identity']==true_user)
        result['queries'].append(dict(case=q['case'],sample=q['sample'],true_identity=true_user,
            true_rank=true['rank'],true_score=true['score'],returned_identity=identities[0]['identity'],
            second_rank_identity=identities[1]['identity'],second_rank_ties=[v['identity']for v in identities if v['score']==identities[1]['score']],
            score=ref['result']['score'],second_score=ref['result']['second_score'],
            margin=ref['result']['second_score']-ref['result']['score'],status=ref['result']['status'],
            baseline_http_ms=ref['ms'],identities=identities))
    result['complete']=True
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('baseline','diagnostics','manifest','protocol','geometry','output'):parser.add_argument(name,type=Path)
    args=parser.parse_args()
    report=audit(args.baseline,args.diagnostics,args.manifest,args.protocol,args.geometry,Path(__file__).resolve().parents[1])
    with args.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps([dict(sample=q['sample'],true_rank=q['true_rank'],true_score=q['true_score'],second=q['second_rank_identity'])for q in report['queries']],indent=2))


if __name__=='__main__':main()
