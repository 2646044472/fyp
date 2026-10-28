"""Show actual scoring regions per contributing template, never a fictitious global ROI."""
import json,html
from pathlib import Path
import sys
import cv2
import numpy as np
from PIL import Image,ImageDraw

APP=Path(__file__).resolve().parents[1];sys.path.insert(0,str(APP))
from anchored_matcher import source_quad

root=Path(sys.argv[1]);base=root/'single-device';out=base/'runtime-v5'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
records={r['sample']:r for r in read(root/'stability/records.json')}
cases=read(out/'results.json');pair={(r['query'],r['gallery']):r for r in read(out/'pair-winners.json')}
counts=read(out/'candidate-counts.json');summary=read(out/'summary.json')
def table(rows):return '<table>'+''.join('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in row)+'</tr>' for row in rows)+'</table>'
doc='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>候选背景排除与实际评分区域</title><style>body{max-width:1200px;margin:30px auto;padding:20px;background:#f5f7f8;font:17px/1.7 system-ui;color:#19333c}img{max-width:100%}table{width:100%;background:white}td{padding:8px;border-bottom:1px solid #ccc}a{color:#006c82}</style><h1>排除脱离主ROI的候选，显示真正参与评分的区域</h1>
<p>可选FastCCAnchoredUnion-v5。主ROI定位器未更换，绿色小框仍可能偏小；本轮修复的是候选和对齐区域的空间一致性，以及评分过程的可追踪性。不是手部分割，也不声称仅靠重叠检查证明掌心定位正确。</p>
<p>新规则：候选quad与自动主ROI交面积必须大于1像素²；对齐后的实际评分quad也必须重叠。所有图片同一规则，不读身份或参考标注。截图中的墙面候选3、4被排除，所有80张图片仍参加评测。旧v4完整保留。</p>
<h2>既定全部划分</h2>'''
doc+=table([['设备','划分','组数','最低','最高','平均 /20']]+[[r['cohort'],r['split'],r['count'],r['min'],r['max'],r['mean']] for r in summary])
doc+=f'<p>描述子视图总数 {sum(r["views_before"] for r in counts)} → {sum(r["views_after"] for r in counts)}；{sum(r["views_after"]<r["views_before"] for r in counts)} 张图排除了至少一个候选分支。这里视图包括不同搜索尺寸/平滑尺度，不等于独立ROI数量。</p>'
selected=['20261020T165429663138Z-946a03e6','20261020T165604274940Z-f7ec5fe1','20261020T165710063889Z-9dea7e47','20261020T165712288733Z-fc94c36e']
evidence=[]
for sample in selected:
    rec=records[sample];case=next(c for c in cases if c['case']=='new_'+('original' if rec['index']>5 else 'reverse'))
    trial=next(t for t in case['trials'] if t['sample']==sample);identity=min(trial['scores'],key=trial['scores'].get)
    chosen=sorted(case['gallery'][identity],key=lambda s:pair[sample,s]['winner']['score'])[:2]
    doc+=f'<h2>{html.escape(rec["identity"])} #{rec["index"]}</h2><p>划分：{case["case"]}；实际第一名：{identity}；正确：{trial["correct"]}。以下为该身份分数中实际贡献的两张录入模板，不是预先选定同一张最终ROI。</p>'
    for rank,target in enumerate(chosen):
        winner=pair[sample,target]['winner'];g=records[target];image=Image.open(rec['original']).convert('RGB');draw=ImageDraw.Draw(image)
        anchor=np.asarray(rec['illumination']['details']['roi_quad_full'])
        draw.polygon([tuple(p) for p in anchor],outline='lime',width=10)
        if winner['branch']=='union':
            q=source_quad(np.asarray(winner['source_matrix']))
            draw.polygon([tuple(p) for p in q],outline='orange',width=3)
            draw.polygon([tuple(p) for p in winner['aligned_quad']],outline='magenta',width=7)
        image.thumbnail((800,550));sheet=Image.new('RGB',(1200,620),'white');sheet.paste(image,(0,60));text=ImageDraw.Draw(sheet)
        text.text((10,10),f'Query {rec["identity"]} #{rec["index"]} -> gallery {g["identity"]} #{g["index"]}',fill='black')
        text.text((10,30),f'Branch {winner["branch"]}, view {winner.get("view_index","N/A")}, sigma {winner.get("sigma","N/A")}, distance {winner["score"]:.6f}',fill='black')
        text.text((800,60),'Green: automatic anchor',fill='green');text.text((800,85),'Orange: candidate ROI',fill='orange');text.text((800,110),'Magenta: actual scoring ROI',fill='purple')
        roi_dir=root/('new-runtime-consistent' if g['cohort']=='new' else 'old-runtime-consistent')/'rois'/target/'illumination/roi_128.png'
        thumb=Image.open(roi_dir).convert('RGB').resize((300,300));sheet.paste(thumb,(850,200));text.text((850,175),'Gallery base ROI',fill='black')
        if winner['branch']!='union':text.text((800,140),'Legacy fallback: no invented quad',fill='black')
        name=f'{sample}-contribution-{rank+1}.jpg';sheet.save(out/name)
        doc+=f'<img src="runtime-v5/{name}"><p>录入 #{g["index"]}：{winner["branch"]}，距离 {winner["score"]:.6f}；view_index={winner.get("view_index","不适用")}。该索引是模板内描述子视图编号，不是截图候选编号。</p>'
        evidence.append(dict(query=sample,case=case['case'],predicted=identity,gallery=target,winner=winner,image=name))
(out/'contributions.json').write_text(json.dumps(evidence,indent=2))
if '--images-only' in sys.argv:
    print(out/'contributions.json');raise SystemExit(0)
http=[]
for cohort in ['new','old']:
    r=read(base/f'http-v5-{cohort}/summary.json');assert r['originals_unchanged'] and r['demo_matcher']=='FastCCAnchoredUnion-v5'
    d=r['demo'];http.append([cohort,sum(t['result'].get('user_id')==t['identity'].replace(':','-') for t in d['probes']),len(d['probes']),sum(t['http_status']==200 for t in d['enrollments']),d['payment']['transactions']])
doc+='<h2>本地HTTP回放</h2>'+table([['设备','正确','查询','录入','模拟支付']]+http)
doc+='<p>配对诊断与普通匹配共用同一评分函数；没有用标签重选赢家。旧回退胜出时只标回退，不伪造候选区域。主ROI若错到别处，新检查也可能排除真正有用的候选，因此仍需独立新会话验收。当前测试反复使用同80张开发图；未部署Pi、未改变默认DoN。</p><p><a href="runtime-v5/pair-winners.json">全部3120配对赢家</a> · <a href="runtime-v5/results.json">全部逐查询结果</a> · <a href="report-v4.html">v4原对照</a> · <a href="../../../docs/ROI_PIPELINE.md">流程说明</a></p></html>'
(out/'contributions.json').write_text(json.dumps(evidence,indent=2));(base/'report-v5.html').write_text(doc,encoding='utf-8')
print(json.dumps(http));print(base/'report-v5.html')
