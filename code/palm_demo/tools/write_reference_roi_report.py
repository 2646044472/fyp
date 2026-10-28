"""Report reference-ROI controls, geometry errors and unsuccessful prototypes."""
import argparse
import hashlib
import html
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image,ImageDraw


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('benchmark',type=Path);parser.add_argument('output',type=Path);args=parser.parse_args()
    out=args.output
    read=lambda p:json.loads(p.read_text())
    refs=read(out/'records.json');runtime={r['sample']:r for r in read(args.benchmark/'heatmap-v3-20261025/records.json')}
    assert all(hashlib.sha256((out/n).read_bytes()).hexdigest()==h for n,h in read(out/'scored-input-hashes.json').items())
    errors=[];groups={}
    for r in refs:
        a=runtime[r['sample']];q=np.array(a['diagnostics']['roi_quad_full'],np.float32);ref=np.array(r['quad'],np.float32)
        inter=max(0,float(cv2.intersectConvexConvex(q,ref)[0]));iou=inter/max(abs(cv2.contourArea(q))+abs(cv2.contourArea(ref))-inter,1e-9)
        side=float(np.linalg.norm(q[1]-q[0]));refside=float(np.linalg.norm(ref[1]-ref[0]))
        e=dict(sample=r['sample'],identity=r['identity'],index=r['index'],iou=iou,auto_side_px=side,reference_side_px=refside,
               side_ratio=side/refside,center_shift_in_reference_sides=float(np.linalg.norm(q.mean(0)-ref.mean(0))/refside))
        errors.append(e)
        image=Image.open(args.benchmark/'originals'/r['sample']/'full.jpg').convert('RGB')
        draw=ImageDraw.Draw(image)
        for quad,color in ((q,'lime'),(ref,'cyan')):
            pts=[tuple(map(float,p)) for p in quad];draw.line(pts+pts[:1],fill=color,width=7)
        image.thumbnail((480,270));panel=Image.new('RGB',(620,300),'white');panel.paste(image,(0,25))
        draw=ImageDraw.Draw(panel);draw.text((4,4),f"{r['identity']} #{r['index']} green=auto cyan=reference",fill='black')
        draw.text((486,40),f"IoU {iou:.2f}\nside ratio\n{side/refside:.2f}\ncenter shift\n{e['center_shift_in_reference_sides']:.2f}",fill='black')
        groups.setdefault(r['identity'],[]).append((r['index'],panel))
    sheets=[]
    for identity,panels in groups.items():
        sheet=Image.new('RGB',(1240,1500),'white')
        for j,(_,panel) in enumerate(sorted(panels)):sheet.paste(panel,((j%2)*620,(j//2)*300))
        name=identity.replace(':','-')+'-geometry.jpg';sheet.save(out/name,quality=95);sheets.append((identity,name))
    results=read(out/'classical.json')+read(out/'neural.json')['results']
    table=''
    for alg,variants in [('DoN',['fused_normalized','heatmap_normalized','reference_normalized']),('FastCC',['fused_normalized','heatmap_normalized','reference_normalized']),('local_training_matcher',['fused_raw','heatmap_raw','reference_raw'])]:
        values=[next(r['correct'] for r in results if r['algorithm']==alg and r['variant']==v and r['subset']=='all') for v in variants]
        table+=f'<tr><td>{alg}</td>'+''.join(f'<td>{n}/20</td>' for n in values)+'</tr>'
    summary=dict(images=40,probes=20,annotations_sha256=read(out/'scored-input-hashes.json')['annotations.json'],
        runtime_median_iou=float(np.median([e['iou'] for e in errors])),runtime_iou_below_half=sum(e['iou']<.5 for e in errors),geometry_errors=errors,
        annotation_scope='Single assistant visual estimates before recognition scoring; no independent human adjudication. Exploratory developer dataset.',
        runtime='Default heatmap-v3 unchanged; reference coordinates never loaded by the app; no Pi deployment.')
    (out/'geometry-summary.json').write_text(json.dumps(summary,indent=2))
    worst=''.join(f"<tr><td>{html.escape(r['identity'])} #{r['index']}</td><td>{r['iou']:.2f}</td><td>{r['auto_side_px']:.0f}</td><td>{r['reference_side_px']:.0f}</td><td>{r['side_ratio']:.2f}</td></tr>" for r in sorted(errors,key=lambda r:r['iou'])[:9])
    text=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>ROI 对照 · 2026-10-26</title>
<style>body{{max-width:1120px;margin:40px auto;padding:0 24px;font:17px/1.65 system-ui;color:#213547;background:#f8fafc}}table{{border-collapse:collapse;width:100%;background:white}}td,th{{border:1px solid #cbd5e1;padding:10px;text-align:left}}img{{max-width:100%}}.note{{padding:18px;background:#dcfce7;border-radius:10px}}details{{margin:20px 0}}a{{color:#0369a1}}</style><body>
<h1>ROI 是当前主要瓶颈：参考裁框对照</h1><p class="note">不删样本、不改匹配器，只换成按统一指缝规则标出的 ROI：FastCC 11→19/20，DoN 11→17/20。
这是参考坐标实验，不是自动系统已经达到 19/20。</p>
<h2>完整 40 张 / 固定 20 张查询</h2><table><tr><th>匹配器</th><th>旧融合</th><th>当前自动 heatmap</th><th>参考指缝 ROI</th></tr>{table}</table>
<p>每只手前五张录入、后五张查询；身份内五个距离取中位数；全部图保留，包括原来定位失败的图。传统匹配沿用现有百分位归一化，神经主表使用原始灰度 ROI。
对参考 ROI 再做亮度归一化，神经结果为16/20；RIA仅查询或双侧恢复均没有增加正确数（原始17/20、归一化16/20）。</p>
<h2>参考坐标怎么得到</h2><p>40张原图随机编号显示，图上没有旧预测或匹配分数。我逐张目视标出食指–中指、无名指–小指两个指缝，另取掌心侧点；统一使用原PalmKit alpha=0.15、beta=1.2生成裁框。
全部裁框目视复查后冻结坐标与像素哈希，再进行识别评分。S05一个指缝位置在评分前纠正，记录保留。</p>
<p><strong>局限：</strong>这是助手目视估计，未经独立人工复核，不称人工金标准；此前已看过数据与身份，不能声称盲法研究。该开发集只有两个人、四只手，19/20不能代表独立部署准确率或误认率。
目前40张参考框均在画面内，但真实手掌姿态变化与标注误差仍存在。</p>
<h2>自动框偏在哪里</h2><p>当前自动框与参考框的 IoU 中位数为 {summary['runtime_median_iou']:.3f}；{summary['runtime_iou_below_half']}/40 的 IoU 小于0.5。
所以不仅是原先4张几何失败；部分通过边界/跨度检查的框也没有覆盖一致掌心区域。下表是重叠最差的9张，尺度单位为原图像素。</p>
<table><tr><th>样本</th><th>IoU</th><th>自动边长</th><th>参考边长</th><th>边长比</th></tr>{worst}</table>
<h2>自动修正原型：不隐藏失败结果</h2><ul>
<li>先用分割范围放大再定位：DoN6/20、FastCC10/20、神经12/20，未启用。</li>
<li>GrabCut轮廓细化＋三个指缝凹陷：16/40使用轮廓，其余保留heatmap；DoN7/20、FastCC4/20、神经13/20，未启用。部分轮廓仍受背景和指缝边界错误影响。</li>
<li>现有手检测器去色＋四方向：19/40返回裁图，不用成功子集报准确率，未启用。一张原图的同输入OpenCV/ONNX对照中，输出差很小，未发现能解释该图失败的推理后端差异。</li></ul>
<h2>下一处修复目标</h2><p>优先解决两个指缝的稳定定位，并用这些坐标分别量化端点误差、尺度误差与ROI重叠。
对定位模型做相机域校准/微调时，当前40张只能作开发标注，必须另留新拍摄会话验收；不能拟合这40张后继续拿同批识别分数当验证。
当前heatmap-v3代码保留，没有把目视参考点或失败原型接入默认识别，没有部署Pi。</p>
<h2>可复现材料</h2><p><a href="annotations.json">参考坐标</a> · <a href="plan.json">规则与边界</a> · <a href="scored-input-hashes.json">评分前固定哈希</a> ·
<a href="geometry-summary.json">逐图几何误差</a> · <a href="classical.json">全部传统分数</a> · <a href="neural.json">全部神经与RIA分数</a> ·
<a href="../heatmap-v3-20261025/report.html">当前自动版报告</a></p>
<h2>全部40张：绿框自动 / 青框参考</h2>'''
    for identity,name in sheets:text+=f'<details open><summary>{html.escape(identity)}</summary><img src="{name}"></details>'
    (out/'report.html').write_text(text+'</body></html>',encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k!='geometry_errors'},indent=2))


if __name__=='__main__':main()
