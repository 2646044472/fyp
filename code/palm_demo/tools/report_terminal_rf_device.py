"""Publish completed terminal-RF pilot/full168 scalar evidence; no inference."""
import argparse
import csv
import html
import json
from pathlib import Path

from audit_halfturn_recovery import sha,source_sha,save
from report_rf_device_regression import summarize_run,mapping
from report_raw_smpd import timing
from terminal_rf_evidence import POLICY,ORIGINAL_TERMINAL


def build(reference,all_stage,candidate,pilot):
    assert candidate['complete'] and not candidate.get('failure') and candidate['distance_policy']==POLICY
    assert pilot['complete'] and pilot['pilot_pass']
    assert candidate['candidate_sha256']==source_sha(Path(__file__).with_name('terminal_rf_evidence.py'))
    assert len(candidate['enrollment_feature_parity'])==34 and all(v['equal'] for v in candidate['enrollment_feature_parity'])
    refs,rows=mapping(reference),mapping(candidate);assert refs.keys()==rows.keys() and len(rows)==168
    fast=[];terminal=[];decisions=[];transitions=[]
    for key,q in rows.items():
        original=refs[key];t=q['terminal_rf']
        assert t['original_scores']==original['diagnostics']['scores'] and t['original_route']==original['result']['recognition_route']
        assert t['unknown_calls']==0
        if t['original_route']!=ORIGINAL_TERMINAL:
            assert not t['rf_applied'] and t['rf_unique_comparisons']==0 and t['exhaustive_callback_calls']==0
            assert q['diagnostics']['scores']==original['diagnostics']['scores']
            assert all(q['result'].get(k)==original['result'].get(k) for k in ('status','user_id','score','second_score','recognition_route'))
            fast.append(q)
        else:
            assert t['rf_applied'] and t['exhaustive_callback_calls']==1 and q['diagnostics']['scores']==t['rf_scores']
            terminal.append(q)
        transitions.append(dict(case=key[0],sample=key[1],before_correct=original['correct'],after_correct=q['correct'],
            before_user=original['result'].get('user_id'),after_user=q['result'].get('user_id'),
            reference_ms=original['ms'],candidate_ms=q['ms'],original_route=t['original_route'],candidate_route=q['result'].get('recognition_route')))
    assert len(fast)==155 and len(terminal)==13
    result=dict(complete=True,policy=POLICY,standard_tag='standard-device-20261030',
        candidate_sha256=candidate['candidate_sha256'],kernel_sha256=candidate['kernel_sha256'],evaluator_sha256=candidate['evaluator_sha256'],
        candidate_execution_baseline_sha256=candidate['baseline_sha256'],
        model_sha256=candidate['model_sha256'],manifest_sha256=candidate['manifest_sha256'],thresholds=candidate['thresholds'],
        variants={'stored-standard':summarize_run(reference),'all-stage-rf':summarize_run(all_stage),'terminal-rf':summarize_run(candidate)},
        original_score_and_route_parity=168,fast_paths_verbatim=155,terminal_queries=13,unknown_calls=0,
        genuine_corrections=sum(not t['before_correct'] and t['after_correct'] for t in transitions),
        lost_correct=sum(t['before_correct'] and not t['after_correct'] for t in transitions),transitions=transitions,
        all34_enrollment_arrays_equal=True,originals_unchanged=candidate['originals_unchanged'],
        prior_corrections_retained=candidate['retained_prior_corrections'],
        mechanism_gate_pass=candidate['local_candidate_pass'],timely_coverage_nonregression=candidate['timely_coverage_nonregression'],
        demo_replacement_qualified=False,promoted=False,
        terminal_rf_time_ms=timing([q['terminal_rf']['rf_ms'] for q in terminal]),
        speed_controls=[dict(case=key[0],sample=key[1],correct=rows[tuple(key)]['correct'],ms=rows[tuple(key)]['ms'],
            route=rows[tuple(key)]['result']['recognition_route'],rf_applied=rows[tuple(key)]['terminal_rf']['rf_applied'],
            exhaustive_callback_calls=rows[tuple(key)]['terminal_rf']['exhaustive_callback_calls']) for key in pilot['speed_controls']],
        pilot=dict(summary=pilot['summary'],genuine_corrections=pilot['genuine_corrections'],lost_correct=pilot['lost_correct'],
            pass_=pilot['pilot_pass'],speed_controls_pass=pilot['speed_controls_pass']),
        decisions=decisions,
        limits=['Known/exposed device development cohort; no independent generalization or stranger-rejection claim.',
            'Stored standard and candidates are separate Windows epochs, not Pi measurements or randomized timing trials.',
            'The earlier SMPD417 feature-container hash audit overlapped this candidate run; wall times are nonexclusive.',
            'Capturing one-request code pairs has overhead even when the original fast route is preserved.',
            'Passing accuracy/path gates is not meeting the latency target; two wrong identities and a long tail remain.',
            'No new public evaluation, production deployment, threshold fitting or enrollment replacement is part of this report.'])
    for name,report in [('stored-standard',reference),('all-stage-rf',all_stage),('terminal-rf',candidate)]:
        for key,q in mapping(report).items():
            row=dict(variant=name,case=key[0],sample=key[1],identity=q['identity'],correct=q['correct'],http_status=q['http_status'],ms=q['ms'],
                **{k:q['result'].get(k) for k in ('status','user_id','score','second_score','recognition_route')})
            if name=='terminal-rf':
                row.update(original_route=q['terminal_rf']['original_route'],rf_applied=q['terminal_rf']['rf_applied'],
                    rf_ms=q['terminal_rf']['rf_ms'],exhaustive_callback_calls=q['terminal_rf']['exhaustive_callback_calls'])
            decisions.append(row)
    result['timely_correct_lost']=[t for t in transitions if t['before_correct'] and t['reference_ms']<=2500 and not(t['after_correct'] and t['candidate_ms']<=2500)]
    return result


def render(result):
    rows=[]
    for name,variant in result['variants'].items():
        for scope,s in {'overall':variant['overall'],**variant['cases']}.items():
            values=[name,scope,s['total'],s['correct'],s['wrong_identity_accepted'],s['rejected'],s['processing_failure'],s['correct_within_2500'],
                *[f"{s['all_timing'][k]/1000:.3f}" for k in ('p50_ms','p95_ms','max_ms')]]
            rows.append('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in values)+'</tr>')
    controls=''.join('<li>'+html.escape(f"{q['sample']}: {q['ms']/1000:.3f}s, {q['route']}, exhaustive={q['exhaustive_callback_calls']}, RF={q['rf_applied']}")+'</li>' for q in result['speed_controls'])
    return f'''<!doctype html><html lang="zh"><meta charset="utf-8"><title>保留快路径，仅终局使用RF证据</title>
<style>body{{font:16px/1.7 system-ui;max-width:1400px;margin:40px auto;padding:0 24px;background:#101722;color:#e9eff8}}table{{border-collapse:collapse;font-size:13px}}td,th{{border:1px solid #526782;padding:6px}}a{{color:#a2d8ff}}</style>
<h1>保留原快路径，仅在穷尽分支使用独立新距离</h1>
<p><b>166/168正确、2误认、0拒认</b>；保住原165正确并保留一张真正纠错。原评分阶段的168条整库分数/路由完全复现，155条原快路径的最终分数/身份/路由不变，且无新增穷尽搜索和RF计算。原13条穷尽请求才使用独立RF分数，不混合两种距离。</p>
<table><tr>{''.join('<th>'+v+'</th>' for v in ('版本','范围','查询','正确','误认','拒认','处理失败','≤2.5秒正确','P50秒','P95秒','最长秒'))}</tr>{''.join(rows)}</table>
<p>这些均为电脑原图回放，摄像头采集与外部上传不计入。本次未重跑标准版；表中标准为已有完整结果。时长来自不同运行时段；417个SMPD特征容器的只读哈希核验与本次实验有重叠，不能视作独占CPU/磁盘的因果加速试验。</p>
<h2>两张已知速度回退图</h2><ul>{controls}</ul>
<p>它们恢复原快路由，但整体限时正确仍为157/168，低于标准158/168；P95为4.094秒、最长8.933秒。流程上的新增全搜问题已解决，整体速度目标仍未达成。请求内编码记录也有开销，不应把路径相同解释为耗时零增加。</p>
<h2>完整流程与边界</h2><p>34次五帧重新录入全部成功并ready，34组注册特征数组与原基准逐字节相同。所有确认/扣款、重复确认拦截、取消、取消后确认拦截均通过。启动、录入、最后帧到ready、即时查询及完整图库首查询分列于JSON。</p>
<p>阈值、原图、注册选择和标准分支未变；未部署，也没有新Pi成绩。仍有两张xyt手腕/前臂错定位误认。当前仅为已知开发集回归，不能当独立泛化或陌生人拒识证据。</p>
<p><a href="summary.json">标量报告</a> · <a href="decisions.csv">三版504条查询账本</a></p></html>'''


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('reference','all_stage','candidate','pilot','output'):p.add_argument(name,type=Path)
    a=p.parse_args();inputs={name:json.loads(getattr(a,name).read_text()) for name in ('reference','all_stage','candidate','pilot')}
    result=build(inputs['reference'],inputs['all_stage'],inputs['candidate'],inputs['pilot'])
    result['input_sha256']={name:sha(getattr(a,name)) for name in inputs}
    a.output.mkdir(exist_ok=False);save(a.output/'summary.json',result)
    fields=['variant','case','sample','identity','correct','http_status','ms','status','user_id','score','second_score','recognition_route','original_route','rf_applied','rf_ms','exhaustive_callback_calls']
    with (a.output/'decisions.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(result['decisions'])
    (a.output/'report.html').write_text(render(result),encoding='utf-8')
    print(json.dumps({name:variant['overall'] for name,variant in result['variants'].items()}))


if __name__=='__main__':main()
