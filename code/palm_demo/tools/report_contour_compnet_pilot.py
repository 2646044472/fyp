"""Export completed contour pilot scalar evidence; never export palm pixels/features."""
import argparse
import csv
import hashlib
import html
import json
from pathlib import Path

from report_raw_smpd import summarize,timing


def build(report):
    assert report['complete'] and not report.get('failure')
    assert report['matcher']=='FastCCCompNetAlternateROI-v26-experimental'
    assert report['originals_unchanged'] and report['templates_unchanged']
    result={k:report[k] for k in ('policy','matcher','selection','selection_rule','selection_reference_sha256',
        'historical_reference_warning','helper_sha256','runner_sha256','model_sha256','host','thresholds',
        'lost_correct','genuine_corrections','pilot_pass','next_step','originals_unchanged','templates_unchanged')}
    result.update(complete=True,promoted=False,full168_candidate_regression_run=False,
        limitations=['Fixed exposed development pilot, not full168 accuracy or independent generalization.',
            'Windows HTTP timing; no Pi acceleration or 40-person capacity claim.',
            'Original five-frame enrollment payload reused; enrollment requests and incremental enrollment timing not measured.',
            'Only cancellation/unchanged transaction count tested here; full payment guards require later full regression.'],
        variants={},mistake_traces=[],decisions=[])
    for name,variant in report['variants'].items():
        assert len(variant['queries'])==len(report['selection'])
        cases={c['case']:c for c in variant['cases']}
        result['variants'][name]=dict(overall=summarize(variant['queries']),cases={},
            ready_by_case={case:dict(actual_matcher=c['actual_matcher'],actual_matcher_type=c['actual_matcher_type'],
                gallery_size=c['gallery_size'],startup_and_gallery_ready_ms=c['startup_and_gallery_ready_ms'],
                offline_enrollment_copy_ms=c['offline_enrollment_copy_ms'],enrollment_requests=0,
                transactions_unchanged=c['transactions_unchanged'],
                contour_prepared_frames=sum(t['reason']=='unique_candidate' for t in c.get('preparation_trace',[])),
                total_enrollment_frames=5*c['gallery_size']) for case,c in cases.items()})
        for case in cases:
            result['variants'][name]['cases'][case]=summarize([q for q in variant['queries'] if q['case']==case])
        for q in variant['queries']:
            r=q['result']
            result['decisions'].append(dict(variant=name,case=q['case'],sample=q['sample'],identity=q['identity'],
                correct=q['correct'],http_status=q['http_status'],ms=q['ms'],
                **{k:r.get(k) for k in ('status','user_id','score','second_score','recognition_route')}))
            if name=='candidate' and not q['correct']:
                result['mistake_traces'].append(dict(case=q['case'],sample=q['sample'],trace=q['contour_trace']))
    maps={name:{(q['case'],q['sample']):q for q in variant['queries']} for name,variant in report['variants'].items()}
    fields=('status','user_id','score','second_score','recognition_route')
    result['exact_decisions']=sum(all(maps['standard'][key]['result'].get(k)==maps['candidate'][key]['result'].get(k) for k in fields)
        and maps['standard'][key]['http_status']==maps['candidate'][key]['http_status'] for key in maps['standard'])
    return result


def render(result):
    rows=[]
    for variant,data in result['variants'].items():
        for case,s in {'overall':data['overall'],**data['cases']}.items():
            t=s['all_timing'];values=[variant,case,s['total'],s['correct'],s['wrong_identity_accepted'],s['rejected'],s['processing_failure'],s['correct_within_2500'],
                *[f"{t[k]/1000:.3f}" for k in ('p50_ms','p95_ms','max_ms')]]
            rows.append('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in values)+'</tr>')
    return f'''<!doctype html><html lang="zh"><meta charset="utf-8"><title>轮廓辅助 ROI 配对小试</title>
<style>body{{font:16px/1.7 system-ui;margin:40px auto;max-width:1250px;padding:0 24px;background:#111827;color:#e5edf8}}table{{border-collapse:collapse;font-size:14px}}td,th{{border:1px solid #526178;padding:6px}}a{{color:#8dd1ff}}.warn{{border:2px solid #eeac58;padding:16px}}</style>
<h1>轮廓辅助 ROI：固定设备困难图小试</h1>
<p class="warn">小试通过：{result['pilot_pass']}。真正错→对 {result['genuine_corrections']}，原正确损失 {result['lost_correct']}。这 {len(result['selection'])} 张是已暴露的开发选图，不能作为全量或泛化准确率。标准版未变，未部署。</p>
<p>先保留原算法的可信结果；仅不确定时，用轮廓上独立的指缝几何提出一次辅助 ROI，并用冻结的 CompNet 特征做完整图库比较。五帧注册、所有身份和原有 .32/.08 提前结束条件保留，拒认未启用。</p>
<table><tr>{''.join('<th>'+v+'</th>' for v in ('版本','范围','查询','正确','误认','拒认','处理失败','≤2.5秒正确','P50秒','P95秒','最长秒'))}</tr>{''.join(rows)}</table>
<h2>证据与边界</h2><p>新旧配对的身份、分数、第二名和路径完全一致：{result['exact_decisions']}/{len(result['selection'])}。启动到整库 ready 及离线模板复制耗时单列在 summary.json；本试没有新注册请求。这里只测取消和交易数不变，不冒充完整支付验证。</p>
<p>早前 Windows 半转回归的外层 v26 标签错误，实际执行 v24。这次两版均检查了实际 v26 类名、五帧格式与完整图库，复用注册时只对隔离副本按原 Pi 方法修改版本封装，并验证其余载荷不变。历史 v24 报告只用于预先固定选图，不当作这次 v26 对照。</p>
<p>下一步：{html.escape(result['next_step'])}。电脑耗时不能代替 Pi 耗时；不通过的小试不继续扫阈值或按照片改规则。<a href="summary.json">完整标量证据</a></p></html>'''


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    report=json.loads(a.input.read_text());result=build(report)
    result['source_report_sha256']=hashlib.sha256(a.input.read_bytes()).hexdigest()
    a.output.mkdir(exist_ok=False)
    (a.output/'summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    with (a.output/'decisions.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(result['decisions'][0]));writer.writeheader();writer.writerows(result['decisions'])
    (a.output/'report.html').write_text(render(result),encoding='utf-8')
    print(json.dumps({k:v['overall'] for k,v in result['variants'].items()}))


if __name__=='__main__':main()
