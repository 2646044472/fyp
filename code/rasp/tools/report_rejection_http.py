"""Export scalar-only rejection HTTP evidence and preserve every failure."""
import argparse,hashlib,json
from pathlib import Path
from acceptance_policy import AcceptancePolicy


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in('http','audit','output'):p.add_argument(name,type=Path)
    a=p.parse_args();run=json.loads(a.http.read_text());audit=json.loads(a.audit.read_text())
    assert run['complete']and run['source_templates_unchanged']
    profile=next(v for v in audit['profiles']if v['policy']==run['policy'])
    assert run['policy_code_sha256']==audit['policy_code_sha256']
    expected={(r['case'],r['sample_suffix']):r for r in profile['known']['rows']}
    out=dict(http_sha256=sha(a.http),audit_sha256=sha(a.audit),policy=run['policy'],
        gateway_code_sha256=run['gateway_code_sha256'],policy_code_sha256=run['policy_code_sha256'],
        evaluator_sha256=run['evaluator_sha256'],summary=run['summary'],groups=[],
        full168_postranking={k:v for k,v in profile['known'].items()if k!='rows'},fixed_grid_unknown=[],
        warning='Full168 figures use saved retained-evidence scores through the actual policy; 17 known plus 17 person-removed original-image HTTP requests are new observations. Person removal uses already-exposed development images, not independently collected strangers or an unseen-training-person claim. No rejection is counted as correct recognition.',
        source_templates_unchanged=True,all_transactions_unchanged=True,power_samples=len(run['power_samples']))
    assert all(p['get_throttled']=='throttled=0x0'for p in run['power_samples'])
    for g in run['groups']:
        assert g['transactions_unchanged']
        record=dict(case=g['case'],mode=g['mode'],removed_labels=len(g['removed']),retained_labels=len(g['retained']),queries=[])
        for q in g['queries']:
            result=q['result'];suffix=q['sample'][-8:]
            if g['mode']=='known':
                ref=expected[g['case'],suffix];assert result['status']==ref['status']and result['reason']==ref['reason']
            if result['status']!='MATCH':assert q['no_payment_token']and 'token'not in result and 'user_id'not in result
            record['queries'].append(dict(sample_suffix=suffix,http_status=q['http_status'],http_ms=q['http_ms'],status=result['status'],reason=result['reason'],route=result['recognition_route'],
                score=result['score'],second_score=result['second_score'],gap=result['second_score']-result['score']if result['second_score']is not None else None,
                previously_correct=q['reference_correct'],correct=q['correct'],no_payment_token=q['no_payment_token']))
        out['groups'].append(record)
    unknown=[q for g in run['groups']if g['mode']=='whole_person_removed'for q in g['queries']]
    for point in audit['profiles']:
        policy=AcceptancePolicy(point['policy'])
        decisions=[policy.rejection(q['result']['score'],q['result'].get('second_score'),q['result']['recognition_route'])for q in unknown]
        out['fixed_grid_unknown'].append(dict(margin=point['policy']['profiles']['fastcc']['min_margin'],
            correct_accept=point['known']['correct_accept'],known_wrong_accept=point['known']['wrong_accept'],known_rejected=point['known']['rejected'],
            correct_falsely_rejected=point['known']['correct_falsely_rejected'],unknown_accepted=sum(v is None for v in decisions),unknown_rejected=sum(v is not None for v in decisions),
            scope='Same preregistered four margin points applied post hoc to all 17 recorded removal-query scores; only .02 was exercised as the live HTTP policy; no independent calibration'))
    assert not a.output.exists();a.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out['summary'],indent=2))


if __name__=='__main__':main()
