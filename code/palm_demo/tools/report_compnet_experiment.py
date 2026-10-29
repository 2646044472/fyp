"""Compare complete Pi runs, retaining errors, tails and enrollment-scope caveats."""
import argparse,html,json
from pathlib import Path
import numpy as np


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('baseline',type=Path);p.add_argument('candidate',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--control',type=Path);p.add_argument('--paired',type=Path);args=p.parse_args()
    base=json.loads(args.baseline.read_text());candidate=json.loads(args.candidate.read_text())
    control=json.loads(args.control.read_text()) if args.control else None
    paired=json.loads(args.paired.read_text()) if args.paired else None
    assert base['complete'] and candidate['complete'] and (control is None or control['complete'])
    assert paired is None or paired['complete']
    def queries(d):return [q for r in d['runs'] for q in r['queries']]
    def stats(q):
        ms=[q['ms'] for q in q]
        return [f"{sum(t['correct'] for t in q)}/{len(q)}",f"{sum(t['correct'] and t['ms']<=2500 for t in q)}/{len(q)}",
            *[f'{x/1000:.3f}' for x in (np.median(ms),np.percentile(ms,95),max(ms))]]
    def table(headers,rows):
        return '<div class="scroll"><table><tr>'+''.join('<th>'+html.escape(str(v))+'</th>' for v in headers)+'</tr>'+''.join(
            '<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in row)+'</tr>' for row in rows)+'</table></div>'
    source=control or base;lookup={(r['case'],q['sample']):q for r in source['runs'] for q in r['queries']}
    rows=[];changed=[];regressions=[]
    for run in candidate['runs']:
        refs=[lookup[run['case'],q['sample']] for q in run['queries']]
        rows.append([run['case'],'v24 对照' if control else 'v24 连续注册基线',*stats(refs)])
        rows.append([run['case'],'v25 候选',*stats(run['queries'])])
        for q in run['queries']:
            ref=lookup[run['case'],q['sample']]
            if ref['correct'] and not q['correct']:regressions.append(q)
            if q['result'].get('recognition_route')=='compnet_evidence_confident':changed.append((run['case'],q,ref))
    assert not regressions,'Candidate introduced an error; revise report decision'
    allq=queries(candidate);allref=queries(source)
    flags=sorted({p['get_throttled'] for p in candidate['power_samples']})
    content='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>Pi 5：速度与准确率联合实验</title>
<style>body{font:16px/1.65 system-ui;max-width:1400px;margin:32px auto;padding:0 20px;color:#1c2b3d}h1{font-size:28px}h2{margin-top:30px}table{width:100%;border-collapse:collapse;font-size:14px}td,th{padding:9px;border:1px solid #cdd5df;text-align:left;vertical-align:top}th{background:#eaf0f7;white-space:nowrap}.scroll{overflow:auto}.notice{padding:14px;border-left:4px solid #ae6519;background:#fff3df}code{overflow-wrap:anywhere}a{color:#1759a3}</style>
<h1>纯 Pi 5：冻结预训练特征的提前返回实验</h1><p>2026-10-29 · Wi-Fi 管理连接 · 摄像头以保存原图回放 · 正式服务未切换</p>
<p class="notice">本轮保持识别率，部分查询更快；四张误认及最长十余秒的查询仍未解决。没有通过继续删图、降低门槛、丢弃失败或缓存查询答案取得数字改善。新距离的陌生人拒识尚未校准，候选仍是显式 opt-in。</p>'''
    content+='<h2>总体结果</h2>'+table(['运行','正确','正确且≤2.5秒','P50秒','P95秒','最大秒'],[
        ['v24 连续注册后完整基线',*stats(queries(base))],
        *([['v24 同协议图库复用对照',*stats(queries(control))]] if control else []),
        ['v25 实验候选',*stats(allq)]])
    content+='<p>活动原图 '+str(base['protocol']['images'])+' 张；每身份最早/最晚五张注册后分别查询其余图片，合计 '+str(len(allq))+' 次主查询。旧设备 110 张、新设备 59 张，七个人、17 个设备内掌纹身份；不跨设备注册/查询。用户指定删除的一张 billy 左手斜拍图已移出活动数据，本轮不再删除其他图片。原 170 次历史结果保留。</p>'
    content+='<h2>分组对照</h2>'+table(['分组','方法','正确','正确且≤2.5秒','P50秒','P95秒','最大秒'],rows)
    content+='<p>'+('对照与候选均从同一份完成的注册图库复制，独立初始化同样的 HTTP 应用并按同样顺序重算每张原图。' if control else '同协议图库复用对照尚未完成，暂勿把所有时间差归因于新分支。')+'v25 仅对模板 envelope magic 和算法元数据换版，生物特征 payload 不变；额外模型的录入向量在图库准备时重新计算。此对照不声称测到了 v25 现场重新注册时延。相机拍摄、摆手与外网上传均不在查询计时中。</p>'
    content+='<h2>实际改动及验证</h2><p>原有 FastCC pose 已有把握时直接返回，完全跳过新模型。仅在其不确定时，使用冻结的作者 Tongji CompNet 权重，从当前原始灰度 ROI 计算一次 512 维特征，对五帧注册模板进行角距离匹配并取最佳两帧。仍要求最佳≤0.32、与第二名差≥0.08；不足则继续原 v24 全路径。两套距离不混合取最小值。数字门槛相同不表示两套距离的错误接受率已等价。</p>'
    content+='<p>新分支实际提前返回 '+str(len(changed))+' 次，全部身份正确。未改变路径的身份、分数、第二名与路径均与连续注册基线逐项一致；所有 ROI PNG 字节一致。使用同一公开预训练模型，不在这些设备图或查询身份上训练，不按文件名/人员写分支。</p>'
    content+='<p>局部集成测试与完整现有测试共 213 项通过，4 项依赖跳过，旧 API 测试文件单独排除。导出前后 Gabor 固定化的 PyTorch 特征逐位一致，ONNX 最大误差约 1.1×10⁻⁷。模型权重、源代码和输入均留存 SHA。新分支单独替代原识别器的准确率不够，因此没有直接替换整个算法；现有 9-pose 对照也未用于运行分支。</p>'
    content+='<p>各组模拟确认、重复确认拦截、取消、取消后确认检查：'+str(all(r['payment_checks_complete'] for r in candidate['runs']))+'。原图库文件未变：'+str(candidate['source_templates_unchanged'])+'；原图未变：'+str(candidate['originals_unchanged'])+'；供电标志 '+html.escape(', '.join(flags))+'。</p>'
    content+='<h2>未解决的错误与最慢查询</h2>'
    failures=[(r['case'],q) for r in candidate['runs'] for q in r['queries'] if not q['correct']]
    content+=table(['分组','样本','真实身份','返回身份','秒','路径'],[[case,q['sample'],q['identity'],q['result'].get('user_id'),f"{q['ms']/1000:.3f}",q['result'].get('recognition_route')] for case,q in failures])
    slow=sorted([(r['case'],q,lookup[r['case'],q['sample']]) for r in candidate['runs'] for q in r['queries']],key=lambda x:x[1]['ms'],reverse=True)[:10]
    content+=table(['分组','样本','正确','对照秒','候选秒','候选路径'],[[c,q['sample'],q['correct'],f"{r['ms']/1000:.3f}",f"{q['ms']/1000:.3f}",q['result'].get('recognition_route')] for c,q,r in slow])
    content+='<p>最难图未获得新的可靠提前返回证据，仍会完整搜索；新分支也有额外计算成本。不能把中位数下降表述为所有查询≤2.5秒。七人、设备内最多11个掌纹身份不足以验证40人的准确率、图库长尾或陌生人拒识。</p>'
    if paired:
        paired_rows=[]
        for case,sample in paired['selected']:
            trials=[t for t in paired['trials'] if t['case']==case and t['sample']==sample]
            disabled=[t['ms']/1000 for t in trials if not t['enabled']]
            enabled=[t['ms']/1000 for t in trials if t['enabled']]
            auxiliary=[t['auxiliary_ms'] for t in trials if 'auxiliary_ms' in t]
            paired_rows.append([case,sample,', '.join(f'{x:.3f}' for x in disabled),
                ', '.join(f'{x:.3f}' for x in enabled),', '.join(f'{x:.2f}' for x in auxiliary),
                str([t['correct'] for t in trials])])
        content+='<h2>同一应用交替开关新分支</h2><p>机械选择 v24 对照中最慢三次查询，并加入候选最大提速查询（已在前三中）；保持同一份已加载 v25 图库和模型，按关闭→开启→开启→关闭运行，每次重读原图并重算。此小样本诊断用于区分新分支开销与完整搜索，不代替全量准确率实验。所有电源标志为 '+html.escape(', '.join(sorted({s['get_throttled'] for s in paired['power_samples']})))+'。</p>'
        content+=table(['分组','样本','关闭秒（两次）','开启秒（两次）','新增分支毫秒（两次）','四次正确'],paired_rows)
        content+='<p>新分支本身约 8.5–8.8 毫秒；可解样本从约 14–15 秒降至约 1.2 秒。最难样本仍约 14–15 秒，不能归因于这约 9 毫秒；需要新的可靠对齐/局部证据。关闭与开启均未修复原有误认。</p>'
    content+='''<h2>论文带来的结构选择</h2><p><a href="https://web.comp.polyu.edu.hk/csajaykr/myhome/papers/PR2023.pdf">BEST（Pattern Recognition 2023）</a>提示共享特征计算、汇总局部证据；官方包已下载但加密，尚未复现其模型。<a href="https://github.com/xuliangcs/compnet">CompNet 作者代码与预训练模型</a>提供本轮实际测试的冻结表征。<a href="https://arxiv.org/abs/2401.08111">Palm-ID（2024）</a>支持紧凑向量检索的设计方向，但其服务器/手机耗时不等于 Pi 耗时。<a href="https://www.nature.com/articles/s41467-025-58213-7">ERAlign（Nature Communications 2025）</a>强调稳定 ROI 和注册覆盖，包含红外及距离传感条件，尚未直接移植。</p>
<p>上述论文仍报告 ROI、强畸变或低质量失败。文献指标不是本设备效果；本轮收益只按实际 Pi 请求统计。</p>'''
    content+='<details><summary>新分支逐张返回记录</summary>'+table(['分组','样本','真实身份','正确','对照毫秒','候选毫秒'],[[c,q['sample'],q['identity'],q['correct'],r['ms'],q['ms']] for c,q,r in changed])+'</details></html>'
    args.output.write_text(content,encoding='utf-8');print(args.output)


if __name__=='__main__':main()
