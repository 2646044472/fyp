"""Full168 RF-distance accounting; fresh standard required for qualification."""
import argparse
import csv
import html
import json
from pathlib import Path

from audit_halfturn_recovery import sha,save
from report_raw_smpd import summarize,timing


def summarize_run(report):
    assert report['complete'] and not report.get('failure')
    assert report['executed_matcher']=='FastCCCompNetAlternateROI-v26-experimental'
    queries=[dict(q,case=r['case']) for r in report['runs'] for q in r['queries']]
    enrollments=[e for r in report['runs'] for e in r['enrollments']]
    assert len(queries)==168 and len(enrollments)==34 and report['originals_unchanged']
    return dict(overall=summarize(queries),
        cases={r['case']:summarize(r['queries']) for r in report['runs']},
        enrollment=dict(requests=34,failed=sum(e['http_status']!=200 for e in enrollments),
            ready=sum(e['result'].get('recognition_ready') is True for e in enrollments),
            http_ms=timing([e['ms'] for e in enrollments]),
            last_frame_to_ready_response_ms=timing([e['last_frame_read_to_response_ms'] for e in enrollments if 'last_frame_read_to_response_ms' in e])),
        startup={r['case']:r['startup'] for r in report['runs']},
        immediate_after_enrollment=summarize([q for r in report['runs'] for q in r['immediate_queries']]),
        first_complete_gallery_query_ms={r['case']:r['queries'][0]['ms'] for r in report['runs']},
        payment_guards_complete=all(r['summary']['payment_checks_complete'] for r in report['runs']))


def mapping(report):return {(r['case'],q['sample']):q for r in report['runs'] for q in r['queries']}


def build(reference,candidate,fresh=None):
    assert candidate['distance_policy']=='uniform-fully-supported-FastCC-responses-v1'
    assert len(candidate['enrollment_feature_parity'])==34 and all(x['equal'] for x in candidate['enrollment_feature_parity'])
    variants={'frozen-standard':summarize_run(reference),'candidate':summarize_run(candidate)}
    refs,changed=mapping(reference),mapping(candidate);assert refs.keys()==changed.keys() and len(refs)==168
    transitions=[]
    for key,before in refs.items():
        after=changed[key]
        transitions.append(dict(case=key[0],sample=key[1],before_correct=before['correct'],after_correct=after['correct'],
            before_status=before['result'].get('status'),after_status=after['result'].get('status'),
            before_user=before['result'].get('user_id'),after_user=after['result'].get('user_id'),
            candidate_ms=after['ms']))
    corrections=sum(not t['before_correct'] and t['after_correct'] for t in transitions)
    losses=sum(t['before_correct'] and not t['after_correct'] for t in transitions)
    result=dict(complete=True,scope='Windows same-device full168 RF-distance experiment; not Pi latency or independent generalization.',
        standard_tag='standard-device-20261030',distance_policy=candidate['distance_policy'],
        thresholds=candidate['thresholds'],kernel_sha256=candidate['kernel_sha256'],evaluator_sha256=candidate['evaluator_sha256'],
        variants=variants,transitions=transitions,genuine_corrections=corrections,lost_correct=losses,
        all34_enrollment_feature_arrays_equal=True,originals_unchanged=True,
        fresh_standard_run=fresh is not None,fresh_standard_exact_decisions=None,
        accuracy_gate=corrections>0 and losses==0 and variants['candidate']['payment_guards_complete'] and variants['candidate']['enrollment']['ready']==34,
        promoted=False,decisions=[],
        limits=['Entire cohort is exposed development data; no unseen-session/unknown-person validation.',
            'RF score is a different metric. Existing thresholds stayed fixed; open-set calibration is unestablished.',
            'All normal FastCC stages share the new metric; CompNet/weighted-quality metrics remain separate.',
            'PC wall times cannot establish Pi speed or 40-person gallery capacity.',
            'Candidate-first then fresh standard is a fixed sequential comparison, not randomized interleaving; do not infer significance from small differences.'])
    if fresh is not None:
        variants['fresh-standard']=summarize_run(fresh);freshmap=mapping(fresh);assert freshmap.keys()==refs.keys()
        fields=('status','user_id','score','second_score','recognition_route')
        result['fresh_standard_exact_decisions']=sum(refs[key]['http_status']==q['http_status'] and all(refs[key]['result'].get(k)==q['result'].get(k) for k in fields)
            and refs[key]['diagnostics']['scores']==q['diagnostics']['scores'] for key,q in freshmap.items())
    result['paired_regression_qualified']=result['accuracy_gate'] and fresh is not None and result['fresh_standard_exact_decisions']==168
    result['disposition']='Reject without parameter scan' if not result['accuracy_gate'] else (
        'Full Windows paired regression qualified; Pi regression still required, standard remains frozen' if result['paired_regression_qualified'] else 'Accuracy gate passed; fresh standard/pipeline parity still required')
    for name,report in [('frozen-standard',reference),('candidate',candidate)]+([('fresh-standard',fresh)] if fresh is not None else []):
        for key,q in mapping(report).items():
            result['decisions'].append(dict(variant=name,case=key[0],sample=key[1],identity=q['identity'],correct=q['correct'],http_status=q['http_status'],ms=q['ms'],
                **{k:q['result'].get(k) for k in ('status','user_id','score','second_score','recognition_route')}))
    return result


def render(result):
    rows=[]
    for name,variant in result['variants'].items():
        for case,s in {'overall':variant['overall'],**variant['cases']}.items():
            values=[name,case,s['total'],s['correct'],s['wrong_identity_accepted'],s['rejected'],s['processing_failure'],s['correct_within_2500'],
                *[f"{s['all_timing'][k]/1000:.3f}" for k in ('p50_ms','p95_ms','max_ms')]]
            rows.append('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in values)+'</tr>')
    lost=[q for q in result['transitions'] if q['before_correct'] and not q['after_correct']]
    corrected=[q for q in result['transitions'] if not q['before_correct'] and q['after_correct']]
    return f'''<!doctype html><html lang="zh"><meta charset="utf-8"><title>滤波有效支持完整回归</title>
<style>body{{font:16px/1.7 system-ui;max-width:1400px;margin:40px auto;padding:0 24px;background:#101722;color:#e9eff8}}table{{border-collapse:collapse;font-size:13px}}td,th{{border:1px solid #536780;padding:6px}}a{{color:#95d1ff}}</style>
<h1>统一排除滤波补零响应：完整 168 张设备回归</h1>
<p><b>真正纠错 {result['genuine_corrections']}，原正确损失 {result['lost_correct']}。</b>裁定：{html.escape(result['disposition'])}。标准版未改、未部署。拒认不计正确。</p>
<p>保持原 ROI、特征、所有身份、五帧聚合和全部阈值；唯一变化是在普通 FastCC 的所有阶段中，只比较具有完整 17×17 原图支持的编码响应，并使用每个位移实际有效重叠数作分母。七张只读观测的8081次比较均验证了支持范围；固定小试纠正一张且不损失正确，才进入本次回归。</p>
<table><tr>{''.join('<th>'+v+'</th>' for v in ('版本','范围','查询','正确','误认','拒认','处理失败','≤2.5秒正确','P50秒','P95秒','最长秒'))}</tr>{''.join(rows)}</table>
<p>每个完整运行均重新执行34个五帧录入请求，启动、录入HTTP、最后帧到ready响应、录入后即时查询及完整图库首查询分别在 summary.json 中。候选的34组注册特征数组与原基准全部逐字节相同；没有因结果调整注册数据。</p>
<p>新的标准复跑是否完成：{result['fresh_standard_run']}；与冻结电脑基准逐条整库分数、身份和路径完全一致：{result['fresh_standard_exact_decisions']}/168。先候选、后标准的顺序已在完整回归前固定。表中是电脑时长，不能声称Pi加速，也不能把小幅波动当成显著差异。</p>
<h2>全部纠错与损失</h2><pre>{html.escape(json.dumps(dict(corrected=corrected,lost_correct=lost),ensure_ascii=False,indent=2))}</pre>
<p><a href="summary.json">完整标量报告</a> · <a href="decisions.csv">全部查询账本</a>。这是已暴露开发数据；新会话、陌生人拒识、Pi速度和40人规模均须另行验证。</p></html>'''


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('reference','candidate','output'):p.add_argument(name,type=Path)
    p.add_argument('--fresh-standard',type=Path);a=p.parse_args()
    data={name:json.loads(getattr(a,name).read_text()) for name in ('reference','candidate')}
    fresh=json.loads(a.fresh_standard.read_text()) if a.fresh_standard else None
    result=build(data['reference'],data['candidate'],fresh);result['input_sha256']={name:sha(getattr(a,name)) for name in data}
    if a.fresh_standard:result['input_sha256']['fresh_standard']=sha(a.fresh_standard)
    a.output.mkdir(exist_ok=False);save(a.output/'summary.json',result)
    with (a.output/'decisions.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(result['decisions'][0]));writer.writeheader();writer.writerows(result['decisions'])
    (a.output/'report.html').write_text(render(result),encoding='utf-8')
    print(json.dumps({k:v['overall'] for k,v in result['variants'].items()}))


if __name__=='__main__':main()
