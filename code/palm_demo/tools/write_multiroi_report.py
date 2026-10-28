"""Publish verified v3 development results without replacing historical v2 evidence."""
import hashlib
import html
import json
from pathlib import Path
import sys

root=Path(sys.argv[1]); out=root/'single-device'
def read(p): return json.loads(p.read_text(encoding='utf-8'))
records=read(root/'stability/records.json')
assert len(records)==80 and all(hashlib.sha256(Path(r['original']).read_bytes()).hexdigest()==r['sha256'] for r in records)
lookup={r['sample']:r for r in records}
cases=read(out/'runtime-v3/results.json')
for c in cases:
    gallery={s for samples in c['gallery'].values() for s in samples}
    assert len(c['trials'])==20
    for t in c['trials']:
        assert t['sample'] not in gallery
        assert all(lookup[s]['cohort']==lookup[t['sample']]['cohort'] for s in gallery)
summary=[r for r in read(out/'runtime-v3/summary.json') if r['method']=='registered_best2']
http=[]
for cohort in ['new','old']:
    r=read(out/f'http-v3-{cohort}/summary.json')
    assert r['demo_matcher']=='FastCCMultiROI-v3' and r['originals_unchanged']
    d=r['demo'];correct=sum(t['result'].get('user_id')==t['identity'].replace(':','-') for t in d['probes'])
    http.append(dict(cohort=cohort,correct=correct,total=len(d['probes']),enrollments=sum(t['http_status']==200 for t in d['enrollments']),transactions=d['payment']['transactions']))
def table(rows):
    return '<table>'+''.join('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in r)+'</tr>' for r in rows)+'</table>'
doc='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>具体图片问题与多ROI修复</title><style>body{font:17px/1.7 system-ui;background:#f3f5f6;color:#19333c;margin:30px auto;max-width:1150px;padding:20px}img{max-width:100%}td{padding:10px;border-bottom:1px solid #ccc}table{background:white;width:100%}a{color:#006c82}</style>
<h1>主要问题是ROI过小、偏向指根，导致同掌不同区域相互匹配</h1>
<p>本轮仅同设备；80张原图哈希未变，所有查询与录入分离。绿色为自动框，橙色是助手开发参考框，并非独立真值。</p>
<h2>Bankey右手第8张：漏掉掌心主纹</h2><p>原图仍能看到主纹，自动框却只取指根附近的小区域。扩大查询对齐范围后，固定112个划分中这张图的错误由51/63降到0/63。这支持定位覆盖不足的解释。</p><img src="image-review/bankey-right.jpg">
<h2>Stephen左手第1张：剩余最难样本</h2><p>自动框缩小并向指根偏移。现有局部特征只与第2张录入图形成稳定匹配，换一组录入图就可能失败。多ROI版本中仍错10/51次；重复次数来自同一张图的不同划分。</p><img src="image-review/stephen-left.jpg">
<h2>Stephen右手第5张：不能仅凭放大的ROI断言相机失焦</h2><p>原生像素仍有主纹。小框放大加重了颗粒、发糊的观感。原算法因为两个预测框不重合而放弃了更合适的gamma定位；保留两种有效候选并验证纹理后，该图53/53次错误消失。照明偏背光、掌心对比低，但成功图也有同样现象。</p><img src="image-review/stephen-right-native.jpg">
<h2>运行代码复测</h2><p>FastCCMultiROI-v3保留原图和gamma定位候选，用几何验证筛选纹理对应，并从原生灰度像素一次采样。默认DoN未改；新版本尚未部署Pi。</p>'''
doc+=table([['数据','划分','最低','最高','平均 /20']]+[[r['cohort'],r['split'],r['min'],r['max'],r['mean']] for r in summary])
doc+='<h2>真实本地HTTP历史图回放</h2>'+table([['数据','识别正确','查询数','录入成功','模拟交易']]+[list(r.values()) for r in http])
doc+='<p>以上是同两个人的开发数据；100次划分不是100次独立采集。尚未现场相机/Pi验收。模板未压缩约8.16MB/张，本机每对匹配中位数26.8ms，不能当作Pi性能。</p><h2>额外对照</h2>'
for folder in ['wide-context','dense-alignment','roi-hypotheses','coarse-structure','wider-field','palm-coverage','grid-alignment','window-hypotheses','window-coarse-union']:
    p=out/folder/'summary.json'
    if p.exists():
        doc+=f'<p><a href="{folder}/summary.json">{folder} 全部结果</a></p>'
        if folder in ['window-hypotheses','window-coarse-union']:doc+=table([[r['cohort'],r['split'],r['min'],r['max'],r['mean']] for r in read(p)])
doc+='<p>额外窗口解决了左手第1张的剩余失败；窗口实验唯一剩余错误是Stephen右手第6张，在seed 2026102984中本手距离0.37354、另一手0.37061，正确候选被微小分数差压过。统一合并已计算的粗尺度描述子对齐候选后，两设备各112个固定划分全部20/20。所有候选对所有图片使用同规则，没有按身份或失败图片选分支。此联合方案仅离线验证，尚未接入v3应用或部署Pi，也没有独立新会话证明泛化。</p>'
doc+='<p><a href="report.html">历史v2报告</a> · <a href="runtime-v3/results.json">v3全部逐样本成绩</a> · <a href="http-v3-new/summary.json">新图HTTP</a> · <a href="http-v3-old/summary.json">旧图HTTP</a></p></html>'
(out/'report-v3.html').write_text(doc,encoding='utf-8')
(out/'verified-v3.json').write_text(json.dumps(dict(original_hashes_verified=80,split_integrity=True,http=http),indent=2))
print(json.dumps(http));print(out/'report-v3.html')
