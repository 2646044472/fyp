"""Summarize single-device error concentration, geometry and actual runtime checks."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from write_stability_report import table


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('root',type=Path);args=parser.parse_args()
    root=args.root;out=root/'single-device'
    records=read(root/'stability/records.json');lookup={r['sample']:i for i,r in enumerate(records)}
    assert len(records)==80 and all(hashlib.sha256(Path(r['original']).read_bytes()).hexdigest()==r['sha256'] for r in records)
    old_cases=[r for r in read(root/'stability/results.json') if r['algorithm']=='FastCCPoseNearest-v1' and r['case'].startswith('new_') and '_to_' not in r['case']]
    seen=Counter(t['sample'] for c in old_cases for t in c['trials'])
    failures=Counter(t['sample'] for c in old_cases for t in c['trials'] if not t['correct'])
    reference=Path(__file__).resolve().parents[1]/'runtime/pi5-new-camera-20261021/reference-roi-20261026'
    references={r['sample']:r for r in read(reference/'records.json')}
    error_rows=[];diagnostics=[]
    for sample,n in failures.most_common():
        r=records[lookup[sample]];a=np.asarray(r['illumination']['details']['roi_quad_full'],np.float32);b=np.asarray(references[sample]['quad'],np.float32)
        area=cv2.intersectConvexConvex(a,b)[0];iou=area/(cv2.contourArea(a)+cv2.contourArea(b)-area)
        ratio=float(np.linalg.norm(a[1]-a[0])/np.linalg.norm(b[1]-b[0]));shift=float(np.linalg.norm(a.mean(0)-b.mean(0))/np.linalg.norm(b[1]-b[0]))
        diagnostics.append(dict(sample=sample,identity=r['identity'],index=r['index'],failures=n,queries=seen[sample],reference_iou=iou,side_ratio=ratio,center_shift_sides=shift))
        error_rows.append([r['identity']+' #'+str(r['index']),f'{n}/{seen[sample]}',f'{iou:.2f}',f'{ratio:.2f}',f'{shift:.2f}'])
    (out/'error-diagnosis.json').write_text(json.dumps(diagnostics,indent=2),encoding='utf-8')
    summary=read(out/'runtime-v2/summary.json');runtime=read(out/'runtime-v2/results.json')
    metrics={(r['method'],r['cohort'],r['split']):r for r in summary}
    def format_score(r):
        spread=str(r['min']) if r['min']==r['max'] else f'{r["min"]}–{r["max"]}'
        return spread+'/20'+(f'（平均{r["mean"]:.2f}）' if r['count']>1 else '')
    metric_rows=[]
    for split,label in [('original','新图：前五录入、后五查询'),('reverse','新图：后五录入、前五查询'),('random','新图：原十种随机划分'),('extra','新图：额外一百种随机划分')]:
        metric_rows.append([label,*[format_score(metrics[m,'new',split]) for m in ['pose_nearest','registered_best2']]])
    metric_rows.append(['旧图：以上所有划分','全部20/20','全部20/20'])
    before={r['case']:r for r in runtime if r['method']=='pose_nearest'}
    extra=[r for r in runtime if r['method']=='registered_best2' and r['case'].startswith('new_extra_')]
    improvements=dict(better=sum(r['correct']>before[r['case']]['correct'] for r in extra),same=sum(r['correct']==before[r['case']]['correct'] for r in extra),worse=sum(r['correct']<before[r['case']]['correct'] for r in extra))
    (out/'split-comparison.json').write_text(json.dumps(improvements,indent=2))
    http_rows=[];http=[]
    for c,label in [('new','新图'),('old','旧图')]:
        replay=read(out/f'http-v2-{c}/summary.json');assert replay['demo_matcher']=='FastCCRegisteredBest2-v2' and replay['originals_unchanged']
        d=replay['demo'];correct=sum(t['result'].get('user_id')==t['identity'].replace(':','-') for t in d['probes'])
        http.append(correct)
        http_rows.append([label,f'{correct}/{len(d["probes"])}',f'{sum(t["http_status"]==200 for t in d["enrollments"])}/4',d['payment']['transactions']])
    latency=read(out/'runtime-v2/latency.json')
    # Save all simple aggregation controls attempted before local registration.
    distances=np.load(root/'stability/distances.npz');pose=distances['FastCCPoseNearest-v1'];controls=[]
    for name,matrix in [('directed',pose),('symmetric_mean',(pose+pose.T)/2),('mutual_max',np.maximum(pose,pose.T)),('either_min',np.minimum(pose,pose.T))]:
        for count in [1,2,3]:
            values=[]
            for c in old_cases:
                gs={k:[lookup[s] for s in ids] for k,ids in c['gallery'].items()};correct=0
                for t in c['trials']:
                    i=lookup[t['sample']];sc={k:float(np.sort(matrix[i,ids])[:count].mean()) for k,ids in gs.items()}
                    correct+=sc[t['identity']]<min(v for k,v in sc.items() if k!=t['identity'])
                values.append(int(correct))
            controls.append(dict(distance=name,best_templates=count,original=values[0],reverse=values[1],random=values[2:]))
    (out/'aggregation-controls.json').write_text(json.dumps(controls,indent=2))
    doc='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>单设备识别稳定性修复</title><style>
body{margin:0;background:#f3f5f6;color:#19333c;font:17px/1.75 system-ui,"Microsoft YaHei",sans-serif}main{max-width:1150px;margin:auto;padding:32px 24px 64px}h1{font-size:36px;line-height:1.4}h2{margin-top:36px}.card{background:white;padding:22px;border-radius:12px;margin:22px 0}.warning{border-left:5px solid #c78736}table{border-collapse:collapse;width:100%;background:white;font-size:15px}td,th{padding:11px;border-bottom:1px solid #d6e0e5;text-align:left}th{background:#e1edf0}.scroll{overflow:auto}img{max-width:100%;height:auto}a{color:#006c82}code{font-size:14px;overflow-wrap:anywhere}figcaption,.small{font-size:14px;color:#50656e}</style><main>
<p>2026-10-28 · 仅评估单设备 · 新候选已接入本地流程，未部署Pi</p>
<h1>波动集中在少数裁偏的照片；<br>自动对齐让同设备识别更稳定。</h1>
<div class="card"><a href="image-review/report.html">新增：直接查看失败原图、正常对照和原生像素，具体解释ROI偏差</a>。后续扩展对齐实验仍在继续；以下表格保留已完成HTTP验收的v2结果。</div>
<div class="card"><strong>本轮范围：只比较同一设备的录入与查询。</strong><p>新旧相机各自独立测试。跨设备匹配不再作为修复目标。所有80张原图保留，失败不从分母中删除。</p></div>
<h2>修复前后，使用相同划分</h2>'''+table(['同设备测试','九姿态候选（修复前）','自动对齐＋双视图（修复后）'],metric_rows)
    doc+=f'<p>额外100种新图划分中，{improvements["better"]}组改善、{improvements["same"]}组持平、{improvements["worse"]}组退步。它们仍复用同40张已参与开发的照片，不是新采集的独立验证，也不能按2000张独立查询计算准确率。</p>'
    doc+='''<h2>为什么原来会在15–18/20之间变？</h2><p>这不是同一图片重复推理时随机抖动。原十种划分加正反向划分中，错误集中于下列少数照片：它们落在查询侧时经常失败，落在录入侧时又会改变可用模板的覆盖。少数“看起来相似”的错误模板也会吸引nearest匹配。于是换一组录入照片，就改变了识别成绩。</p>'''+table(['样本（原标签＋编号）','作为查询时错误/出现次数','自动/参考框IoU','自动/参考边长','中心偏移/参考边长'],error_rows)
    doc+='''<p>其中bankey:right #8的自动框边长只有参考框的约45%，掌纹在裁图里被放大并移位；其他几张也存在尺度或掌区偏差。这里的参考框是之前助手的目视开发标注，不是独立人工金标准。仅把ROI换成这些固定参考框，FastCC中位数匹配在原十种划分达到18–20/20，支持定位/对齐是重要瓶颈，但不证明其为唯一原因。</p>
<figure><img src="roi-grid.jpg" alt="新相机四类掌纹各十张自动ROI"><figcaption>每行同一只手，按原始编号1–10排列；全部自动v5裁图。部分照片的主掌纹位置、尺度与其他照片明显不同。不能仅凭对比度或锐度筛掉这些图。</figcaption></figure>
<h2>已经实现的修复</h2><ol>
<li>在自动ROI的384像素图上寻找局部纹理对应点，利用一致的旋转、缩放、平移关系对齐掌纹。仍使用自动v5定位，没有把参考点、身份标签写进算法。</li>
<li>同时使用原始纹理与固定轻度平滑的纹理寻找对应点，降低细碎纹理对对应点的干扰。最终用于FastCC识别的像素始终来自原始图；没有对识别图做美化或生成式修复。</li>
<li>对应点需满足数量、分布面积和几何约束；对齐后的采样区必须在原图和保存的上下文内。无可靠对齐时保留原九姿态结果，避免黑色补边参与匹配。</li>
<li>每个身份使用最好的两个录入模板的平均距离，使单个偶然很近的模板不再独自决定结果。五张录入样本都保留，所有身份采用同一套规则。</li></ol>
<p>纯粹改距离汇总、双向平均或只使用局部关键点计数都未解决问题；局部对齐后重新计算掌纹特征才有较明确收益。已有PalmIR恢复仍没有额外收益，继续不启用。</p>
<h2>真实应用回放</h2>'''+table(['本地HTTP','查询正确','录入成功','隔离模拟支付'],http_rows)
    doc+='''<p>图像入口由历史原图回放，ROI定位、特征提取、压缩模板保存与读取、HTTP识别、确认模拟支付均为真实代码。原图哈希未变，生产账户和余额未改；没有声称通过现场实时采集验收。</p>
<p>可选参数：<code>--demo-matcher FastCCRegisteredBest2-v2</code>，要求<code>--roi-mode pklnet</code>。采用独立模板版本，需重新录入；旧DoN、九姿态或v1模板不能混用。默认DoN和Pi现有capture-only服务未改变。Pi网络仍未恢复，本轮未部署。</p>'''
    doc+=f'<p>本机测得特征提取中位数约{latency["extraction_ms"]["median"]:.0f}ms（不含ROI定位），每对模板匹配中位数约{latency["pair_match_ms"]["median"]:.1f}ms；单张未压缩特征约{latency["template_bytes"]/1e6:.2f}MB，磁盘使用压缩NPZ。这些是本机开发测量，不能当Pi时延承诺。27项匹配、模板、支付和capture-only相关测试通过。</p>'
    doc+='''<div class="card warning"><strong>剩余限制</strong><p>没有修到完全稳定。额外划分最差仍16/20，反向划分18/20，少数裁框过小或掌纹对应不足的样本仍会失败。固定划分20/20不能取代未参与调参的新会话验收。本轮两个被反复检查的人的数据，只能支持开发阶段的同设备改善结论。</p></div>
<h2>证据与复现</h2><ul>
<li><a href="runtime-v2/summary.json">最终运行代码稳定性汇总</a> · <a href="runtime-v2/results.json">全部划分、模板与逐查询分数</a> · <a href="runtime-v2/plan.json">协议</a></li>
<li><a href="error-diagnosis.json">错误集中与框偏差</a> · <a href="reference-controls.json">参考框对照</a> · <a href="aggregation-controls.json">汇总方式对照</a></li>
<li><a href="http-v2-new/summary.json">新图HTTP回放</a> · <a href="http-v2-old/summary.json">旧图HTTP回放</a> · <a href="runtime-v2/latency.json">耗时与模板大小</a></li>
<li><a href="local-alignment/results.json">纯局部特征失败对照</a> · <a href="registered/results.json">全原图对齐原型</a> · <a href="descriptor-smoothing/results.json">单视图平滑对照</a></li>
<li><a href="../stability/report.html">上一轮完整稳定性审计（含已不再作为目标的跨设备对照）</a></li></ul></main></html>'''
    (out/'report.html').write_text(doc,encoding='utf-8');print(out/'report.html')


if __name__=='__main__':main()
