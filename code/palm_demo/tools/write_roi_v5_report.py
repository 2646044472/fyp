"""Render the saved v5/PalmIR development evidence without rerunning inference."""
import argparse
import html
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pklnet_roi import normalize_roi


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('output',type=Path);args=parser.parse_args();root=args.output
    original=read(root/'new-camera/recognition.json');guarded=read(root/'consistency-new/recognition.json')
    baseline=next(x for x in original if x['variant']=='v4' and x['algorithm']=='DoN')
    current=next(x for x in guarded if x['algorithm']=='DoN')
    old={x['sample']:x for x in baseline['trials']}
    fixed=[x for x in current['trials'] if x['correct'] and not old[x['sample']]['correct']]
    worse=[x for x in current['trials'] if not x['correct'] and old[x['sample']]['correct']]
    rows=read(root/'consistency-new/records.json');by_id={r['sample']:(i,r) for i,r in enumerate(rows)}
    pixels={'v4':np.load(root/'new-camera/pixels.npz')['v4'],
            'v5':np.load(root/'consistency-new/pixels.npz')['consistent_gamma']}
    figures=[]
    for count,(label,t) in enumerate([('纠正的错配',x) for x in fixed]+[('新增错配，保留披露',x) for x in worse],1):
        i,r=by_id[t['sample']];im=Image.open(r['original']).convert('RGB');panel=Image.new('RGB',(1200,510),'white')
        for col,(p,k) in enumerate([('v4','v4'),('v5','consistent_gamma')]):
            view=im.copy();d=ImageDraw.Draw(view);q=[tuple(v) for v in r['variants'][k]['quad']];d.line(q+q[:1],fill='lime',width=7)
            view.thumbnail((590,330));panel.paste(view,(col*600,25));panel.paste(Image.fromarray(normalize_roi(pixels[p][i])[0]),(col*600,365))
            ImageDraw.Draw(panel).text((col*600,5),f'{p} {r["identity"]} #{r["index"]}',fill='black')
        panel.save(root/f'comparison-{count}.jpg',quality=94)
        figures.append(f'<figure><img src="comparison-{count}.jpg"><figcaption>{label} · {html.escape(r["identity"])} · 第 {r["index"]} 张。左 v4，右 v5；下方为归一化 ROI。</figcaption></figure>')
    stress=read(root/'stress/results.json') if (root/'stress/results.json').exists() else []
    conditions={'dark_065':'亮度 × 0.65','blur_sigma3':'高斯模糊 σ=3 原图像素','shift_3pct':'水平/垂直平移 3%'}
    stress_rows=''.join(f'<tr><td>{conditions[c]}</td>'+''.join(f'<td>{next(x["correct"] for x in stress if x["condition"]==c and x["policy"]==p and x["algorithm"]==a)}/20</td>' for p,a in [('v4','DoN'),('v5','DoN'),('v4','FastCC'),('v5','FastCC')])+'</tr>' for c in conditions if any(x['condition']==c for x in stress))
    classical=read(root/'palmir-consistent/classical.json');neural=read(root/'palmir-consistent/neural.json')
    restoration_rows=''
    for name,data in [('DoN',classical),('FastCC',classical),('配套神经匹配器',neural)]:
        alg='local_training_matcher' if name=='配套神经匹配器' else name
        values=[next(x['correct'] for x in data if x['subset']=='all' and x['algorithm']==alg and x['variant']==v) for v in ['raw_both','raw_ria_both','raw_ria_probe']]
        restoration_rows+=f'<tr><td>{name}</td>'+''.join(f'<td>{v}/20</td>' for v in values)+'</tr>'
    stats=read(root/'palmir-consistent/stats.json')['stats']
    deployment=read(root/'deployment.json') if (root/'deployment.json').exists() else None
    pi=read(root/'pi-consistent/summary.json') if (root/'pi-consistent/summary.json').exists() else None
    state='已部署，文件哈希与服务状态已核对' if deployment else '候选版，尚未确认部署'
    pi_text='Pi 最终版本回放尚未完成。'
    if pi:
        d=pi['demo'];n=sum(p['result'].get('user_id')==p['identity'].replace(':','-') for p in d['probes']);lat=pi['latency_ms']['illumination']
        pi_text=f'Pi 最终版本：40/40 几何通过、{sum(x["http_status"]==200 for x in d["enrollments"])}/4 组录入、实际 HTTP DoN {n}/20、{d["payment"]["transactions"]} 笔隔离模拟扣款；重复确认与取消后确认检查通过。单核 ROI 中位 {lat["median"]/1000:.2f} 秒，p95 {lat["p95"]/1000:.2f} 秒。'
    candidates=''.join(f'<tr><td>{html.escape(x["variant"])}</td><td>{x["algorithm"]}</td><td>{x["correct"]}/20</td><td>{x["valid"]}/40</td></tr>' for x in original)
    doc='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ROI v5 与 PalmIR 实测</title><style>body{margin:0;background:#f2f5f4;color:#17352e;font:17px/1.75 system-ui,"Microsoft YaHei",sans-serif}main{max-width:1120px;margin:auto;padding:38px 24px}h1{font-size:38px;line-height:1.35}h2{margin-top:35px}.card,figure{background:white;padding:22px;border-radius:14px;margin:22px 0}img{width:100%;height:auto}figcaption,.small{font-size:14px;color:#4b635b}table{border-collapse:collapse;width:100%;background:white;font-size:16px}td,th{padding:12px;border-bottom:1px solid #d3dfd8;text-align:left}th{background:#dfebe3}a{color:#007263}code{overflow-wrap:anywhere;font-size:14px}.note{border-left:5px solid #d59b37;padding-left:18px}summary{cursor:pointer}</style><main>'''
    doc+=f'<p>2026-10-28 · {state}</p><div class="card"><a href="stability/report.html">更新：新旧相机稳定性与九姿态候选完整评估</a>。新图换录入组合仍波动，跨相机不可靠；候选尚未部署。</div><h1>Pi 上 DoN 改善到 14/20；<br>PalmIR 本轮没有额外识别收益。</h1>'
    doc+='''<p>最终候选 <code>pklnet-illumination-consistent-v5</code> 同时检查原始和适度提亮的定位输入。两者裁框重叠至少一半，才采用提亮后的定位；否则保留 v4。最终 ROI 总是从原始照片裁出，模型权重、匹配算法和原有几何门槛不变。</p>
<table><tr><th>开发集指标</th><th>v4</th><th>v5 本地</th><th>v5 Pi</th></tr><tr><td>新相机 DoN 正确识别</td><td>13/20</td><td>15/20</td><td>14/20</td></tr><tr><td>新相机 FastCC 正确识别</td><td>12/20</td><td>15/20</td><td>15/20</td></tr><tr><td>新相机 ROI 几何通过</td><td>40/40</td><td>40/40</td><td>40/40</td></tr><tr><td>旧相机 DoN / FastCC</td><td>20/20</td><td>20/20</td><td>本轮未重跑</td></tr></table>
<p class="note">不是每张都变好：本地 DoN 纠正3张，同时新增1张错配，净增2张；Pi 有一张边界查询进一步变错，最终仍有6/20错误。几何合法不等于掌纹对齐准确。本批只有两个人的左右手，已反复用于开发，不能把本地75%或Pi70%称作现场可靠性。</p>
<p>电脑/Pi坐标最大差约0.00193像素，归一化ROI平均绝对像素差约0.2503/255。把Pi的40张ROI交给电脑匹配，也得到14/20，差异已缩小到ROI像素生成而非HTTP或匹配器流程；具体解码/透视插值环节尚待进一步隔离。差异查询的正确人与错误人得分十分接近，暴露了识别不稳定性。<a href="backend-parity.json">跨平台像素对照</a></p>
<h2>为什么加定位一致性检查？</h2><p>单独提亮也得到15/20，但7张照片的ROI与原定位差异较大。采用固定0.5交并比规则保留原定位后，DoN/FastCC仍为15/20，与助手参考框重叠低于0.5的图片从8张回到6张。规则只看预测几何，不读身份标签或匹配分数。参考框是助手开发标注，不能当独立金标准；这一额外规则也经过同批数据比较，需新会话验证。</p>
<h2>模拟现场画质变化</h2><p>录入保持原来每组第1–5张，只改变第6–10张查询。每个条件都保留全部20张，定位失败也计错。这是开发集的合成压力测试，不是新采集数据；模糊偶尔提高成绩，说明定位和匹配仍有不稳定性，不代表应主动模糊相机。</p>
<table><tr><th>查询变化</th><th>v4 DoN</th><th>v5 DoN</th><th>v4 FastCC</th><th>v5 FastCC</th></tr>'''+stress_rows+'</table>'
    doc+='''<h2>PalmIR 实际测试</h2><p>使用项目已有 <strong>Local PalmIR-style RIA / CompactRestorer</strong>，在PolyU-II掌纹ROI上训练；不是官方PalmIR。对完整40张最终v5 ROI测试了原始/归一化输入、全部恢复/仅查询恢复、50%混合，所有查询计入分母。</p><table><tr><th>匹配器</th><th>未恢复</th><th>录入与查询均恢复</th><th>仅查询恢复</th></tr>'''+restoration_rows+'</table>'
    doc+=f'<p>原始ROI平均绝对像素变化仅 {stats["raw"]["mean_abs_change_8bit"]:.4f}/255，归一化输入为 {stats["normalized"]["mean_abs_change_8bit"]:.4f}/255。各恢复设置均未增加正确识别数。本地模型对这些输入接近恒等输出；结合此前训练域模糊响应正常的对照，更像训练退化与当前相机域不匹配，尚不能断言现场图像模糊。默认识别不增加这一步。</p>'
    doc+='<h2>本地修复与退步对比</h2><p>以下是本地逐张对照，不能替代上表中的Pi实测成绩。</p>'+''.join(figures)
    doc+='<h2>完整流程、代价与回退</h2><p>'+pi_text+'</p><p>旧相机40张在本地以最终运行代码复核：40张有效、4组录入、20/20实际HTTP识别、4笔模拟扣款。所有生产账户与原图保留，服务保持capture-only；摄像头未连接，因此没有声称通过实时现场验收。v5需要两遍定位，有重试时更多，延迟高于v4。旧模板需要重录，账户余额保留。</p>'
    doc+='<p>本次v5部署时43项相关单元测试通过。仍需改善几何合法但掌区不一致的样本，评估更多真实会话，以及将恢复训练的退化分布与现场图像对应起来。每小时自动任务已删除；后续主动迭代结果见上方稳定性报告。</p>'
    doc+='<details><summary>保留所有定位实验成绩，包括失败方案</summary><table><tr><th>方案</th><th>算法</th><th>正确</th><th>几何通过</th></tr>'+candidates+'</table></details>'
    doc+='''<div class="card"><strong>证据</strong><ul><li><a href="consistency-new/recognition.json">最终候选逐张评分</a> · <a href="stress/results.json">固定压力测试</a></li><li><a href="palmir-consistent/classical.json">PalmIR DoN/FastCC</a> · <a href="palmir-consistent/neural.json">神经匹配器</a> · <a href="palmir-consistent/stats.json">模型哈希与变化量</a></li><li><a href="old-runtime-consistent/summary.json">旧数据真实流程</a> · <a href="pi-consistent/summary.json">Pi真实流程</a> · <a href="deployment.json">部署与备份</a></li><li><a href="../pi5-roi-v4-20261027/report.html">上一版报告</a></li></ul><p class="small">部分历史评分文件同时包含 original_geometry_pass 子集。本文一律使用 all 全20查询成绩，不使用删样本后的分数。</p></div></main></html>'''
    (root/'report.html').write_text(doc,encoding='utf-8')
    print(root/'report.html')


if __name__=='__main__':main()
