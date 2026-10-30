"""Publish scalar-only full v26 device reference; refuse partial/mislabeled runs."""
import argparse
import csv
import hashlib
import html
import json
from pathlib import Path

from report_raw_smpd import summarize,timing

MATCHER='FastCCCompNetAlternateROI-v26-experimental'


def build(report):
    assert report['complete'] and not report.get('failure')
    assert report['matcher']==report['executed_matcher']==MATCHER
    assert report['originals_unchanged']
    runs=report['runs'];assert len(runs)==4
    assert sum(len(r['queries']) for r in runs)==168
    assert sum(len(r['enrollments']) for r in runs)==34
    queries=[dict(q,case=r['case']) for r in runs for q in r['queries']]
    entries=[e for r in runs for e in r['enrollments']]
    assert all(r['startup']['actual_matcher']==MATCHER and r['startup']['actual_matcher_type']=='CompNetAlternateROIMatcher' for r in runs)
    assert all(r['summary']['payment_checks_complete'] for r in runs)
    assert all(e['http_status']==200 and e['result'].get('recognition_ready') is True for e in entries)
    result={k:report[k] for k in ('matcher','executed_matcher','standard_tag','manifest_sha256','protocol_sha256',
        'split_protocol_matcher','explicit_matcher_override','helper_sha256','evaluator_sha256','model_sha256','host',
        'thresholds','originals_unchanged','started_unix','ended_unix')}
    transitions=report['historical_pi_comparison']['transitions']
    result.update(complete=True,optimization_candidate=False,promoted=False,
        scope='Fresh Windows v26 + retained FastCC original-device reference, four frozen same-device splits. Live capture excluded.',
        overall=summarize(queries),cases={},
        enrollment=dict(requests=len(entries),frames=5*len(entries),failed=0,recognition_ready=len(entries),
            http_ms=timing([e['ms'] for e in entries]),
            last_frame_to_ready_response_ms=timing([e['last_frame_read_to_response_ms'] for e in entries])),
        immediate_after_enrollment=summarize([q for r in runs for q in r['immediate_queries']]),
        all_payment_guards_complete=True,
        historical_pi_identity_comparison=dict(scope=report['historical_pi_comparison']['scope'],
            previously_correct_lost=sum(t['pi_correct'] and not t['windows_correct'] for t in transitions),
            wrong_to_correct=sum(not t['pi_correct'] and t['windows_correct'] for t in transitions),
            transitions=transitions),decisions=[],
        limitations=['Exposed device cohort, no independent new-session/unknown-person generalization claim.',
            'PC timing is not Pi timing or 40-person capacity evidence.',
            'No new accuracy or speed algorithm is introduced by this reference.',
            'Immediate-after-enrollment probes use the gallery size available at that point; report separately from final complete-gallery queries.',
            'Startup includes model initialization and an initially empty gallery; registration request includes its actual preparation/ready work.'])
    for r in runs:
        result['cases'][r['case']]=dict(queries=summarize(r['queries']),startup=r['startup'],
            enrollment=dict(requests=len(r['enrollments']),http_ms=timing([e['ms'] for e in r['enrollments']]),
                last_frame_to_ready_response_ms=timing([e['last_frame_read_to_response_ms'] for e in r['enrollments']])),
            immediate_after_enrollment=summarize(r['immediate_queries']),
            first_complete_gallery_query_ms=r['queries'][0]['ms'],
            gallery_identities=len(r['enrollments']),payment_checks_complete=r['summary']['payment_checks_complete'])
        for q in r['queries']:
            result['decisions'].append(dict(case=r['case'],sample=q['sample'],identity=q['identity'],correct=q['correct'],
                http_status=q['http_status'],ms=q['ms'],**{k:q['result'].get(k) for k in ('status','user_id','score','second_score','recognition_route')}))
    return result


def render(result):
    def seconds(v):return f'{v/1000:.3f}'
    rows=[]
    for name,s in {'overall':result['overall'],**{name:r['queries'] for name,r in result['cases'].items()}}.items():
        values=[name,s['total'],s['correct'],s['wrong_identity_accepted'],s['rejected'],s['processing_failure'],s['correct_within_2500'],
            *[seconds(s['all_timing'][k]) for k in ('p50_ms','p95_ms','max_ms')]]
        rows.append('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in values)+'</tr>')
    enrollment=result['enrollment'];s=result['overall'];slow=max(result['decisions'],key=lambda q:q['ms'])
    wrong=[q for q in result['decisions'] if not q['correct']]
    detail=''.join('<li>'+html.escape(str((q['case'],q['sample'],q['identity'],q['user_id'],q['ms'])))+'</li>' for q in wrong)
    return f'''<!doctype html><html lang="zh"><meta charset="utf-8"><title>v26 设备全流程电脑基准</title>
<style>body{{font:16px/1.7 system-ui;max-width:1250px;margin:40px auto;padding:0 24px;background:#111827;color:#e5edf8}}table{{border-collapse:collapse;font-size:14px}}td,th{{padding:6px;border:1px solid #526178}}a{{color:#8dd1ff}}</style>
<h1>版本已核实的 v26 设备全流程基准</h1>
<p>Windows 原设备数据，四种同设备划分。实际 v26 + retained FastCC：<b>{s['correct']}/168 正确、{s['wrong_identity_accepted']} 误认、{s['rejected']} 拒认、{s['processing_failure']} 处理失败</b>。≤2.5秒正确 {s['correct_within_2500']}/168。这是纠正实验版本标注后的基准，未引入新优化，标准版未变、未部署。</p>
<table><tr>{''.join('<th>'+v+'</th>' for v in ('范围','查询','正确','误认','拒认','处理失败','≤2.5秒正确','P50秒','P95秒','最长秒'))}</tr>{''.join(rows)}</table>
<p>最慢：{html.escape(slow['sample'])}，{seconds(slow['ms'])} 秒，正确={slow['correct']}，路径={html.escape(slow['recognition_route'] or '')}。电脑数字不能替代 Pi 数字，也没有证明 40 人图库性能。</p>
<h2>真实录入、ready 与支付检查</h2><p>重新执行 {enrollment['requests']} 个五帧录入请求，{enrollment['frames']} 次帧输入，全部成功且 ready。录入 HTTP P50/P95/最长为 {seconds(enrollment['http_ms']['p50_ms'])}/{seconds(enrollment['http_ms']['p95_ms'])}/{seconds(enrollment['http_ms']['max_ms'])} 秒；最后一帧读入结束到 ready 响应的 P50 为 {seconds(enrollment['last_frame_to_ready_response_ms']['p50_ms'])} 秒。这些成本不混入单张查询。启动与录入后即时查询在 JSON 中另列。</p>
<p>四组的确认扣款、重复确认拦截、取消、取消后确认拦截均通过。所有账号和交易库位于独立实验目录；没有调用摄像头或修改正式服务。</p>
<h2>仍未解决的错误</h2><ul>{detail}</ul>
<p>19 张固定轮廓辅助 ROI 小试没有纠错，已淘汰；没有通过放宽阈值把拒认算成正确。两张 xyt 图原框偏向手腕/前臂，另一张原框大致在掌心，不能用同一个定位解释包办全部误认。</p>
<p>早前半转 Windows 回归实际使用 v24，外层 v26 标签已更正。这次直接从原图重新录入，逐组记录实际类名、版本 magic 和完整流程，历史数据未覆盖。独立旧 Pi 基准仍为165/168、3误认、0拒认、145/168正确且≤2.5秒。</p>
<p><a href="summary.json">完整标量证据</a> · <a href="decisions.csv">168条查询账本</a></p></html>'''


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    result=build(json.loads(a.input.read_text()));result['source_report_sha256']=hashlib.sha256(a.input.read_bytes()).hexdigest()
    a.output.mkdir(exist_ok=False)
    (a.output/'summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    (a.output/'report.html').write_text(render(result),encoding='utf-8')
    with (a.output/'decisions.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(result['decisions'][0]));writer.writeheader();writer.writerows(result['decisions'])
    print(json.dumps(result['overall']))


if __name__=='__main__':main()
