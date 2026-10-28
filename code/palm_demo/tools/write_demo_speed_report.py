"""Publish final isolated HTTP timings alongside exact-equivalence evidence."""
import json,html
from pathlib import Path
import sys
import numpy as np
root=Path(sys.argv[1]);base=root/'single-device'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def table(rows):return '<table>'+''.join('<tr>'+''.join('<td>'+html.escape(str(x))+'</td>' for x in row)+'</tr>' for row in rows)+'</table>'
parity=read(base/'speed-v5/prepared-parity-parallel.json');extraction=read(base/'speed-v5/parallel-extraction.json')
assert parity['pairs']==3120 and not parity['differences'] and len(extraction)==80 and all(r['identical'] for r in extraction)
metrics=[]
for cohort in ['new','old']:
    r=read(base/f'http-v6-final-{cohort}/summary.json');d=r['demo']
    assert r['originals_unchanged'] and r['demo_matcher']=='FastCCDemo-v6'
    correct=sum(t['result'].get('user_id')==t['identity'].replace(':','-') for t in d['probes'])
    times={k:[t['ms'] for t in d['http_trace'] if t['route']==k and t['status']==200] for k in ['/api/demo/enroll','/api/demo/identify']}
    stages={k:dict(median=float(np.median([t['result']['timing_ms'][k] for t in d['probes']])),p95=float(np.percentile([t['result']['timing_ms'][k] for t in d['probes']],95))) for k in ['capture_and_extract','gallery','total']}
    disk=list((base/f'http-v6-final-{cohort}/demo_runtime/demo_templates').glob('*.npz'))
    metrics.append(dict(cohort=cohort,correct=correct,total=len(d['probes']),enrolled=sum(t['http_status']==200 for t in d['enrollments']),transactions=d['payment']['transactions'],
                        enroll_ms_median=float(np.median(times['/api/demo/enroll'])),identify_ms_median=float(np.median(times['/api/demo/identify'])),identify_ms_p95=float(np.percentile(times['/api/demo/identify'],95)),
                        identify_cold_ms=times['/api/demo/identify'][0],identify_warm_median_ms=float(np.median(times['/api/demo/identify'][1:])),
                        stages=stages,compressed_gallery_bytes=sum(p.stat().st_size for p in disk)))
doc='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>Demo v6：ROI检查与提速验收</title><style>body{max-width:1150px;margin:30px auto;padding:20px;background:#f5f7f8;font:17px/1.7 system-ui;color:#19333c}img{max-width:100%}table{width:100%;background:white}td{padding:10px;border-bottom:1px solid #ccc}pre{white-space:pre-wrap;font-size:14px}a{color:#006c82}</style><h1>Demo v6：保留识别分数，减少录入和查询中的重复工作</h1>
<p>2026-10-28 · 本机Windows历史原图HTTP完整回放 · 最终新旧回放顺序执行，无其他本任务重型评测并行 · 未部署Pi</p>
<h2>最终完整流程与耗时</h2>'''
doc+=table([['设备','识别','录入','模拟支付','每人五张录入中位','查询中位','查询p95']]+[[r['cohort'],f'{r["correct"]}/{r["total"]}',r['enrolled'],r['transactions'],f'{r["enroll_ms_median"]/1000:.2f}s',f'{r["identify_ms_median"]/1000:.2f}s',f'{r["identify_ms_p95"]/1000:.2f}s'] for r in metrics])
doc+='<p>此前v5新图回放录入中位26.98s、查询7.09s，当时与其他审计并行，不能据此宣称严格受控的倍数提升。最新结果包含从历史原图开始的定位、提取、模板读取与HTTP识别；不含真实相机采集、预览线程竞争和Pi CPU成本。</p>'
doc+='<h2>改动</h2><ol><li>录入只计算gallery描述子，省去查询候选及原生PNG。</li><li>查询保留全部通过空间检查的候选；最多两个工作线程，不降低分辨率或删除难图。</li><li>查询只解码一次；录入端只保存匹配所需的紧凑内存数据，缓存上限64MiB，文件替换、重新录入、元数据改变和删除会失效。</li><li>登记与查询使用独立角色检查；仅录入模板不能冒充查询输入。版本隔离保留，旧账户重录不重置余额。</li></ol>'
doc+='<h2>精度与确定性</h2><p>全部80张查询图的并行提取与串行实现逐字节一致（版本号除外）；全部80张录入图保留的描述子与v5一致；全部3120个非自身同设备配对距离完全一致。新旧设备各112组固定划分仍为20/20。134项回归测试通过、2项跳过；既有test_existing_pipeline.py旧模块导入问题未计入。</p>'
doc+='<h2>截图中小ROI的问题</h2><p>空间检查排除了墙面候选3、4；9张图共48个描述子视图被移除，配对分数未变。主ROI仍可能偏小，本轮没有把它伪装成已修好的新定位器。紫色为实际用于此配对评分的区域，绿色为自动主框、橙色为候选框。</p><img src="runtime-v5/20261020T165429663138Z-946a03e6-contribution-1.jpg"><p><a href="report-v5.html">每张贡献模板的实际对齐区域及候选检查</a></p>'
doc+='<h2>启用可选demo</h2><pre>python debug_ui.py --enable-recognition --roi-mode pklnet --demo-matcher FastCCDemo-v6</pre><p>旧算法需重新录入。默认capture-only服务、默认DoN和网络未改。模拟支付仍需人工确认姓名。上述是反复检查过的两人开发数据，没有独立新会话、陌生人拒绝率或现场摄像头性能保证。</p><h2>阶段计时与证据</h2><pre>'+html.escape(json.dumps(metrics,indent=2))+'</pre><ul>'
for p in ['speed-v5/prepared-parity-parallel.json','speed-v5/parallel-extraction.json','speed-v5/thread-profile.json','speed-v5/parallel-profile.json','runtime-v5/results.json','http-v6-final-new/summary.json','http-v6-final-old/summary.json']:
    doc+=f'<li><a href="{p}">{p}</a></li>'
doc+='</ul></html>'
(base/'speed-v5/final-metrics.json').write_text(json.dumps(metrics,indent=2));(base/'report-v6.html').write_text(doc,encoding='utf-8');print(json.dumps(metrics,indent=2));print(base/'report-v6.html')
