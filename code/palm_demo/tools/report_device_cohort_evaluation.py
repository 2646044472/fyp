"""Render all frozen device cohorts and preserve every error/latency denominator."""
import argparse,json
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
from report_six_person_evaluation import esc,seconds,table,summarize


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('evidence',type=Path);p.add_argument('output',type=Path)
    args=p.parse_args();data=json.loads(args.evidence.read_text());protocol=data['protocol']
    feature_path=args.evidence.parent/'feature-diagnostics.json'
    diagnostic_rows={}
    if feature_path.is_file():
        feature_data=json.loads(feature_path.read_text(encoding='utf-8'))
        assert feature_data.get('complete') and feature_data.get('all_reference_equal')
        diagnostic_rows={(q['case'],q['sample']):q for q in feature_data['queries']}
    cases={c['name']:c for c in protocol['cases']}
    status='已完成' if data.get('complete') else '进行中，部分分组尚未完成'
    chunks=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>七人分设备完整流程实验</title>',
      '<style>body{font:16px/1.6 system-ui,sans-serif;max-width:1450px;margin:32px auto;padding:0 22px;color:#182637}h1{font-size:29px}h2{margin-top:32px}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;font-size:14px}td,th{padding:8px;border:1px solid #cdd6e1;text-align:left;vertical-align:top}th{background:#edf2f8;white-space:nowrap}.notice{padding:12px 16px;border-left:4px solid #ac6914;background:#fff6e7}.failure{border:1px solid #d0d8e1;border-radius:8px;margin:16px 0;padding:16px}.failure img{max-width:100%;height:auto}code{overflow-wrap:anywhere}small{color:#526276}</style>',
      '<h1>七人分设备：冻结版本完整流程与错图分析</h1>',
      '<p>2026-10-29 · 纯 Raspberry Pi 5 · Wi-Fi 管理连接 · '+status+'</p>',
      '<p class="notice">当前在用数据共 170 张：旧相机 110 张、6 个人员标签、11 个掌纹身份；新相机 60 张、3 人、6 个掌纹身份（含 billy）。bankey/stephen 在两设备重复出现，按人员合并计 7 人；匹配图库始终按设备分别建立。</p>',
      '<p>固定识别版本：<code>'+esc(protocol['matcher'])+'</code>，算法快照提交 <code>'+esc(protocol['frozen_commit'])+'</code>。全部识别源文件和测试工具的 SHA 在协议中固定；本轮不根据这些结果调参。</p>',
      '<p>每个设备分别做最早 5 张注册/其余查询，以及最晚 5 张注册/其余查询。旧相机每组 55 次主查询，新相机每组 30 次，共 170 次主查询。每组从空库重新注册；不跨设备注册查询。已移出的 syr 会话不参与本轮，旧版 120 张实验的 62/65 保留为历史记录。</p>',
      '<h2>完整主查询结果</h2><p>正确要求成功返回 MATCH 且掌纹身份一致；“≤2.5 秒正确”还要求本次完整 HTTP 请求不超过 2500 ms。失败、误认、定位错误及超时全部保留。</p>']
    summaries=[]
    for run in data['runs']:
        q=run['queries'];s=run.get('summary',{})
        summaries.append([run['case'],f"{len(q)}/{len(cases[run['case']]['queries'])}"]+summarize(q)+[
            seconds(s.get('p95_ms')),sum(e['result'].get('recognition_ready') is True for e in run['enrollments'])])
    chunks.append(table(['分组','进度','正确','≤2.5秒正确','P50秒（含错误）','最大秒','P95秒','ready身份数'],summaries))
    chunks.append('<p>每次查询均重新读原图并计算，计时包含预处理、ROI、特征、检索/配准、评分和树莓派本机 HTTP 返回。Wi-Fi 用于连接和管理；相机拍摄、摆手、外部网络上传、注册和启动等待另计。</p>')
    for run in data['runs']:
        case=cases[run['case']]
        chunks.append('<h2>'+esc(run['case'])+'：逐身份结果</h2>')
        groups=defaultdict(list)
        for q in run['queries']:groups[q['identity']].append(q)
        chunks.append(table(['身份','正确','≤2.5秒正确','P50秒','最大秒'],[[u]+summarize(groups[u]) for u in case['enrollment']]))
        chunks.append('<h2>'+esc(run['case'])+'：注册→ready→立即首查</h2>')
        immediate={q['identity']:q for q in run['immediate_queries']};registration=[]
        for e in run['enrollments']:
            q=immediate.get(e['identity']);stage=lambda label:sum(v['ms'] for v in e['events'] if v['stage']==label)
            registration.append([e['identity'],e['http_status'],e['result'].get('recognition_ready'),seconds(e['ms']),
              seconds(e.get('last_frame_read_to_response_ms')),seconds(stage('primary_roi')),seconds(stage('alternate_roi')),
              seconds(stage('complete_features')),seconds(stage('template_save')),seconds(stage('prepare_enrollment')),
              seconds(stage('descriptor_index')),seconds(stage('index_and_enrollment_links')),
              seconds(q['ms']) if q else '—',q['correct'] if q else '—'])
        chunks.append(table(['身份','HTTP','ready','注册总秒','末帧读取后秒','主ROI秒','备用ROI秒','完整特征秒','保存秒','模板准备秒','全索引秒','索引+对齐秒','立即首查秒','首查正确'],registration))
        chunks.append('<p>嵌套/并行阶段不可相加。“末帧读取后”来自文件回放，不是真实相机拍摄时延。额外即时首查不计入主查询分母；同一原图在主查询时重新计算。</p>')
        startup=run['startup'];chunks.append('<p>通用模型启动 '+seconds(startup['generic_model_startup_ms'])+' 秒；空库应用初始化 '+seconds(startup['app_and_gallery_ms'])+' 秒。仅使用全零输入作模型启动预热。</p>')
        restart=run.get('restart')
        if restart:chunks.append('<p>独立新进程：模型启动 '+seconds(restart['startup']['generic_model_startup_ms'])+' 秒，应用/图库重建 '+seconds(restart['startup']['app_and_gallery_ms'])+' 秒；首次查询 '+seconds(restart['first_query']['ms'])+' 秒，正确='+esc(restart['first_query']['correct'])+'。这是进程重启，不是树莓派重启。</p>')
        if run.get('summary'):chunks.append('<p>模拟交易 '+str(run['summary']['payment_transactions'])+' 笔；各身份确认、重复确认拦截、取消及取消后确认检查全部通过：'+esc(run['summary']['payment_checks_complete'])+'。</p>')
        chunks.append('<h2>'+esc(run['case'])+'：错误逐张记录</h2>')
        failures=[q for q in run['queries'] if not q['correct']]
        if not failures:chunks.append('<p>当前已完成查询中未发现错误；未完成分组不作全通过结论。</p>')
        for q in failures:
            result=q['result'];scores=q.get('diagnostics',{}).get('scores',{})
            ranked=sorted(scores.items(),key=lambda item:item[1]);truth=q['identity'].replace(':','-')
            rank=next((i+1 for i,(u,_) in enumerate(ranked) if u==truth),None)
            margin=(result['second_score']-result['score']) if result.get('second_score') is not None and result.get('score') is not None else None
            chunks.append('<div class="failure"><p><b>'+esc(q['sample'])+'</b><br>真实：'+esc(q['identity'])+'；预测：'+esc(result.get('user_id'))+'；'+seconds(q['ms'])+' 秒；路径 '+esc(result.get('recognition_route'))+'。</p>')
            chunks.append('<p>真身份排名 '+esc(rank)+'；最佳/第二名分差 '+esc(None if margin is None else round(margin,6))+'。标签保持原始活动数据记录，不按识别结果改标签。</p>')
            overlay=args.output.parent/'failure-images'/(run['case']+'-'+q['sample']+'.jpg')
            if overlay.is_file():chunks.append('<img src="'+esc(str(overlay.relative_to(args.output.parent)).replace('\\','/'))+'" alt="原图和树莓派实际ROI">')
            elif q.get('roi_artifact') and (args.output.parent/q['roi_artifact']).is_file():chunks.append('<img width="256" src="'+esc(q['roi_artifact'])+'" alt="树莓派实际主ROI">')
            chunks.append(table(['候选身份','分数（越小越好）'],[[u,f'{value:.6f}'+(' ← 真身份' if u==truth else '')] for u,value in ranked]))
            detail=diagnostic_rows.get((run['case'],q['sample']))
            if detail:
                assert detail['reference_equal'] and detail.get('roi_byte_equal')
                attempts=[r for r in detail['registrations'] if r['kind']=='registration']
                counts=Counter(r['reason'] for r in attempts)
                true_attempts=[r for r in attempts if (r.get('target') or {}).get('identity')==truth]
                true_counts=Counter(r['reason'] for r in true_attempts)
                labels={'accepted':'配准通过','too_few_descriptors':'描述子不足4个',
                    'too_few_mutual_pairs':'互相匹配点不足4对','ransac_or_geometric_guard':'RANSAC或几何约束未通过'}
                chunks.append('<p>诊断复跑身份、分数、路径及实际 ROI PNG 均与基线完全一致；诊断计时不替代基线耗时。主/备用关键点：'+esc(detail['query_feature_counts']['primary'])+'/'+esc(detail['query_feature_counts']['secondary'])+'。</p>')
                chunks.append(table(['配准结果','全图库尝试次数','真身份尝试次数'],
                    [[label,counts[key],true_counts[key]] for key,label in labels.items()]))
                chunks.append('<p>次数包含多区域、多尺度、多注册帧的重复尝试，不是独立图片数；关键点多不代表纹理可用。RANSAC/几何失败尚未细分为内点、覆盖率、尺度和角度原因。所有生成的基础 ROI 候选均保留，没有证据表明正确候选被重叠保护过滤。</p>')
            chunks.append('</div>')
        chunks.append('<details><summary>全部主查询，按耗时降序（包含所有失败）</summary>')
        chunks.append(table(['样本','真实身份','返回身份','正确','≤2.5秒正确','秒','HTTP','状态','最佳分数','第二分数','路径'],[
          [q['sample'],q['identity'],q['result'].get('user_id','—'),q['correct'],q['correct'] and q['ms']<=2500,seconds(q['ms']),q['http_status'],q['result'].get('status',q['result'].get('message','—')),q['result'].get('score','—'),q['result'].get('second_score','—'),q['result'].get('recognition_route','—')]
          for q in sorted(run['queries'],key=lambda q:q['ms'],reverse=True)]))
        chunks.append('</details>')
    flags=sorted({s['get_throttled'] for s in data['power_samples']})
    chunks.append('<h2>解释与完整性边界</h2><p>提前返回条件要求最佳分数≤0.32且与第二名差≥0.08。完整回退后的模拟 demo 最终采用闭集排序，未校准陌生人拒识；低证据图即使不满足提前返回门槛，仍可能被分给某个身份。这一行为需与 ROI/对齐问题分别评估，不能靠删失败或单改阈值声称解决。</p>')
    if diagnostic_rows:
        chunks.append('<p>五张错误都经过完整搜索，没有错误的高置信提前返回。xyt 两张实际 ROI 偏向掌根/手腕，与注册掌心区域不一致；cyw 的 ROI 仍在掌心，但纹理较弱、配准不稳；billy 左右手两张仍在掌内，细纹弱、明暗和视角变化较大，尚不能断言是裁剪位置导致。完整配准的真身份候选未形成通过约束的稳定对应。</p>')
    slowest=max((q for run in data['runs'] for q in run['queries']),key=lambda q:q['ms'])
    chunks.append('<p>最慢样本：'+esc(slowest['sample'])+'，'+esc(slowest['identity'])+'，'+seconds(slowest['ms'])+' 秒。提高提前返回率必须先提高 ROI/对齐证据质量；放宽置信门槛会增加误认风险。本轮算法保持冻结，没有按新增人员调参。</p>')
    chunks.append('<p>已采样电源/降频标志：'+esc(', '.join(flags))+'；原图最终复核未变：'+esc(data.get('originals_unchanged','等待全部完成'))+'。11/6 个设备内掌纹身份不能证明 40 人容量。已查看的数据不再称为独立未见验证；正反两组的查询图片不同，不能把结果差异完全归因于注册图。</p></html>')
    args.output.write_text(''.join(chunks),encoding='utf-8')
    print(json.dumps(dict(complete=data.get('complete',False),summary=summaries),ensure_ascii=False))


if __name__=='__main__':main()
