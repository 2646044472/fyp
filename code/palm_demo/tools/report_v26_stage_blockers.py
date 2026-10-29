"""Summarize actual unchanged-result Pi profiles without summing nested timers."""
import argparse,hashlib,html,json
from collections import Counter
from pathlib import Path
import numpy as np


def covered_ms(events,labels):
    intervals=sorted((e['start_ms'],e['start_ms']+e['ms']) for e in events if e['label'] in labels)
    total=0.;end=-float('inf')
    for left,right in intervals:
        if right>end:total+=right-max(left,end);end=right
    return total


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('diagnosis',type=Path);p.add_argument('reference',type=Path);args=p.parse_args()
    root=args.diagnosis;protocol=json.loads((root/'protocol.json').read_text());assert protocol['complete'] and protocol['source_files_unchanged']
    assert hashlib.sha256(args.reference.read_bytes()).hexdigest()==protocol['source_results_sha256']
    data=json.loads(args.reference.read_text());assert data['complete']
    reference={(r['case'],q['sample']):q for r in data['runs'] for q in r['queries']}
    profiles=[(r['case'],json.loads((root/r['case']/'profile.json').read_text())) for r in protocol['runs']]
    assert all(p['complete'] and p['transactions_unchanged'] and p['model_primed'] for c,p in profiles)
    rows=[];power=[];ready=[]
    for case,profile in profiles:
        power.append(profile['preflight']['get_throttled']);ready.append([case,profile['initialization_ready_ms']/1000])
        for q in profile['queries']:
            assert q['reference_equal'] and q['correct']==reference[case,q['sample']]['correct']
            power.append(q['power_after']['get_throttled']);events=q['events']
            complete=[e for e in events if e['label']=='complete_hypotheses'];assert len(complete)==1
            gates=[g for g in q['gates'] if g['ms']<=2500];last=gates[-1] if gates else None
            latest=min(last['scores'],key=last['scores'].get) if last else None
            rows.append(dict(case=case,sample=q['sample'],repeat=q['repeat'],correct=q['correct'],http_ms=q['http_ms'],
                capture_ms=q['result']['timing_ms']['capture_and_extract'],early_elapsed_ms=complete[0]['start_ms'],
                additional_localization_ms=covered_ms(events,{'complete_hypotheses'}),
                complete_features_ms=covered_ms(events,{'complete_features'}),
                full_matching_ms=covered_ms(events,{'complete_identity_match'}),
                native_active_ms=covered_ms(events,{'native_correspondences','native_registration'}),
                confident_gate_before_2500=any(g['confident'] for g in gates),
                latest_gate_before_2500_identity=latest,
                latest_gate_before_2500_correct=latest==reference[case,q['sample']]['identity'].replace(':','-'),
                latest_gate_before_2500_ms=last['ms'] if last else None))
    assert set(power)=={'throttled=0x0'}
    values=list(reference.values());times=[q['ms'] for q in values]
    summary=dict(reference_correct=sum(q['correct'] for q in values),reference_total=len(values),
        reference_timely=sum(q['correct'] and q['ms']<=2500 for q in values),
        reference_p95_ms=float(np.percentile(times,95)),reference_max_ms=max(times),
        statuses=dict(Counter(q['result']['status'] for q in values)),
        wrong_identity_matches=sum(not q['correct'] and q['result']['status']=='MATCH' for q in values),
        explicit_rejects=sum(q['result']['status']=='REJECT' for q in values),
        unknown_person_far=None,verification_frr=None,ready_seconds=ready,profiles=rows,
        diagnosis_does_not_change_algorithm=True,full_reference_unchanged=True,power_flags=sorted(set(power)))
    (root/'summary.json').write_text(json.dumps(summary,indent=2))
    def table(headers,records):
        return '<div class="scroll"><table><tr>'+''.join('<th>'+html.escape(str(v))+'</th>' for v in headers)+'</tr>'+''.join(
            '<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in row)+'</tr>' for row in records)+'</table></div>'
    text='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>v26 最难图与误认：实际阻碍</title>
<style>body{font:16px/1.65 system-ui;max-width:1500px;margin:32px auto;padding:0 20px;color:#203044}h1{font-size:28px}table{border-collapse:collapse;width:100%;font-size:14px}th,td{padding:8px;border:1px solid #ccd5df;text-align:left}th{background:#edf2f8;white-space:nowrap}.scroll{overflow:auto}.notice{background:#fff3dd;border-left:4px solid #a86a16;padding:14px}code{overflow-wrap:anywhere}</style>
<h1>v26：最难长尾与四次误认的实际阻碍</h1><p>2026-10-30 · Pi 实际 HTTP 分阶段诊断 · 无算法/阈值/标签/部署改动</p>
<p class="notice">这轮没有新增可采用的加速方案。v26完整结果保持164/168正确、146/168正确且≤2.5秒，P95 6.019秒、最大15.225秒。这里只诊断全局最慢查询及所有误认，各重复两次；不能当作新的168次完整验收。</p>'''
    text+='<h2>实际查询分解</h2><p>进入回退前累计已经包含初次定位提取，不要重复相加。补定位、回退特征、回退匹配使用事件区间并集；内部原生匹配活跃时间也取并集，包含在其它阶段中，不能再相加。插桩有额外开销，正式限时率仍来自v26完整回放。</p>'
    text+=table(['分组','样本','重复','正确','初次定位提取秒','进入回退前累计秒','补定位秒','回退特征秒','回退匹配秒','原生匹配活跃秒（重叠）','整次HTTP秒'],[
        [q['case'],q['sample'],q['repeat'],q['correct'],*[f"{q[k]/1000:.3f}" for k in
         ('capture_ms','early_elapsed_ms','additional_localization_ms','complete_features_ms','full_matching_ms','native_active_ms','http_ms')]] for q in rows])
    text+='<h2>初始化与就绪等待另计</h2><p>下面是加载已有注册图库、构建索引、载入并预热主定位模型直到应用可查询的耗时。补充窗口模型沿用原有首次使用时延迟加载。没有重新注册人员，不是现场注册时间，也不计入上表查询耗时。</p>'
    text+=table(['分组','本次初始化/就绪秒'],[[c,f'{s:.3f}'] for c,s in ready])
    text+='<p>最难图首遍第一个补定位调用约1.364秒，第二遍对应调用约0.506秒，存在约0.86秒首次调用差异。提前预热可能处理这一小段，但本轮未做独立预热因果对照；第二遍总请求仍约14.31秒，不能把预热当作2.5秒方案。</p>'
    text+='<h2>2.5秒之前的证据</h2>'+table(['分组','样本','重复','曾达到可信提前门槛','截止前最后一轮领先身份','领先身份正确'],[
        [q['case'],q['sample'],q['repeat'],q['confident_gate_before_2500'],q['latest_gate_before_2500_identity'],q['latest_gate_before_2500_correct']] for q in rows])
    failures=[q for q in values if not q['correct']]
    text+='<h2>身份错误与拒绝口径</h2><p>168次输入全是已注册身份，全部返回MATCH；其中4次身份错误，显式REJECT为0。不能把0次显式拒绝称为0%验证FRR，也不能把4/168错身份率当作陌生人FAR；没有陌生人试验，二者未测。现有DemoFlow最终Gallery是阈值1.0、无最小差值的闭集排名兜底，弱证据仍可返回第一名。本轮不修改策略。</p>'
    text+=table(['样本','返回距离','第二名距离','差值'],[[q['sample'],f"{q['result']['score']:.6f}",f"{q['result']['second_score']:.6f}",f"{q['result']['second_score']-q['result']['score']:.6f}"] for q in failures])
    text+='<h2>当前具体阻碍与继续条件</h2><p>最难图在2.5秒内没有通过原有可靠提前门槛；完整回退的补定位、特征构建和匹配各自已占数秒。此前实际配准裁图对照也没有提供可提前使用的强特征证据。仅优化最后的距离计算不能省掉前面数秒；在2.5秒直接返回当前领先者则会改变决策，不能当作保准确率优化。没有证据证明所有未来方法都不行，但当前没有已验证的小改动能同时解决这张长尾和四次误认。</p>'
    text+='<p>可接受的下一项实验必须提出不同且可复现的ROI/表征机制，在不改标签、阈值、不删除失败或按文件特调的条件下，先通过全部已曝光数据回归，再在Pi证明最难图正确且≤2.5秒、没有新增错身份，并报告全量限时率/P95/max。新会话和未注册人员数据还需要作为独立验证；现有重复划分不能替代它们。当前不重复已否决的邻域、SIMD或阈值放宽路线。</p>'
    text+='<p>10次诊断的身份、分数、第二名、状态、路径均与v26原结果相同；四次原有错误保留。模拟交易数不变，来源文件不变，供电标志全0x0。<a href="../compnet-v26-pi-20261030/report.html">v26完整回放与实际ROI对照</a>。</p></html>'
    (root/'report.html').write_text(text,encoding='utf-8');print(json.dumps({k:v for k,v in summary.items() if k not in ('profiles','ready_seconds')}))


if __name__=='__main__':main()
