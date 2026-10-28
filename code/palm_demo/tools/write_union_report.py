"""Summarize completed runtime and fresh-inference evidence, not prototype scores."""
import hashlib
import html
import json
from pathlib import Path
import sys
import numpy as np

root=Path(sys.argv[1]);out=root/'single-device'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def table(rows):return '<table>'+''.join('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in r)+'</tr>' for r in rows)+'</table>'
audit=read(out/'union-audit.json');fresh=read(out/'fresh-v4/summary.json');summary=read(out/'runtime-v4-fresh/summary.json')
assert audit['runtime_cases_verified']==224
http=[];timing=[]
for cohort in ['new','old']:
    r=read(out/f'http-v4-{cohort}/summary.json')
    assert r['demo_matcher']=='FastCCWindowUnion-v4' and r['originals_unchanged']
    d=r['demo'];correct=sum(t['result'].get('user_id')==t['identity'].replace(':','-') for t in d['probes'])
    http.append([cohort,correct,len(d['probes']),sum(t['http_status']==200 for t in d['enrollments']),d['payment']['transactions']])
    routes={t['route'] for t in d['http_trace']}
    for route in sorted(routes):
        times=[t['ms'] for t in d['http_trace'] if t['route']==route and t['status']==200]
        if times:timing.append(dict(cohort=cohort,route=route,count=len(times),median_ms=float(np.median(times)),p95_ms=float(np.percentile(times,95))))
disk=[p.stat().st_size for p in (out/'runtime-v4').glob('*.npz')]
resource=dict(template_envelope_bytes=16*1024*1024,compressed_template_bytes=dict(median=float(np.median(disk)),max=max(disk),total=sum(disk)),
              cached_geometry_runtime=read(out/'runtime-v4/latency.json'),fresh_localization=fresh['inference_plus_extraction_ms'],http=timing,
              caveat='Local Windows CPU, some audits run concurrently; not Pi latency or an isolated performance benchmark')
(out/'resource-v4.json').write_text(json.dumps(resource,indent=2))
doc='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>v4单设备运行验收</title><style>body{font:17px/1.75 system-ui;background:#f3f5f6;color:#19333c;margin:30px auto;max-width:1150px;padding:20px}td{padding:10px;border-bottom:1px solid #ccc}table{background:white;width:100%}a{color:#006c82}pre{white-space:pre-wrap;font-size:14px}</style><h1>单设备多候选ROI：运行版与真实入口验收</h1>
<p>2026-10-28 · 可选FastCCWindowUnion-v4 · 未部署Pi、未改网络或默认DoN</p>
<p>完整定位、搜索、对齐与评分说明：<a href="../../../docs/ROI_PIPELINE.md">ROI_PIPELINE.md</a>。<a href="report-v3.html">具体失败图片与历史对照</a>。</p>
<h2>重新推理后，未改变的全部划分</h2>'''
doc+=table([['设备','划分','组数','最低 /20','最高 /20','平均 /20']]+[[r['cohort'],r['split'],r['count'],r['min'],r['max'],r['mean']] for r in summary])
doc+=f'<p>80张原图哈希保持，查询不在录入中、设备不混用。新旧设备各112组。重新执行ONNX定位后，{fresh["identical"]}/80张模板与缓存定位版本逐字节一致；其余模板的全部相关有向配对重新计算。缓存一致的配对才复用成绩。</p>'
doc+='<h2>本地真实HTTP历史图回放</h2>'+table([['设备','正确','查询数','录入成功','模拟支付']]+http)
doc+='<p>相机边界使用历史原图，定位、模板、查询、支付执行真实应用代码；不代表实时相机或Pi验收。48项回归测试通过。</p>'
doc+='<h2>统一方案审计</h2><p>所有图片统一合并候选，不按身份或错误样本选分支；匹配函数不接收标签。base_full为独立对照，未隐式纳入。缓存运行距离与离线联合矩阵的对照如下：</p><pre>'+html.escape(json.dumps(audit['runtime_parity'],indent=2))+'</pre>'
doc+='<h2>耗时与资源</h2><pre>'+html.escape(json.dumps(resource,indent=2))+'</pre>'
doc+='<p>16MiB为未压缩模板容量，包含无损灰度和描述子，实际磁盘NPZ大小见上表。重新录入才能使用v4，不混用旧版本。批量80模板评测峰值工作集曾测得约1.6GB，此为开发工具观测，不是Pi或应用峰值承诺。</p>'
doc+='<h2>限制和可复现证据</h2><p>所有照片已反复用于开发选择，没有独立新会话泛化、陌生人拒绝率或现场性能证明。即便当前划分全部20/20，也不能据此宣布识别系统完全稳定。历史失败对照与v2/v3结果全部保留。</p><ul>'
for p in ['union-audit.json','runtime-v4/summary.json','runtime-v4-fresh/results.json','fresh-v4/results.json','runtime-v4-fresh/plan.json','http-v4-new/summary.json','http-v4-old/summary.json','resource-v4.json','window-coarse-union/plan.json']:
    doc+=f'<li><a href="{p}">{p}</a></li>'
doc+='</ul></html>'
(out/'report-v4.html').write_text(doc,encoding='utf-8')
print(json.dumps(http));print(out/'report-v4.html')
