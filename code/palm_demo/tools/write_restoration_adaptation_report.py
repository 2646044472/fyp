"""Write the complete restoration adaptation results and practical next steps."""
import argparse
import html
import json
from pathlib import Path


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('output',type=Path)
    args=parser.parse_args();out=args.output
    read=lambda name:json.loads((out/name).read_text())
    results=read('neural.json')+read('classical.json')
    names={'raw_both':'原始 ROI','raw_ria_both':'原始 + RIA（双侧）','raw_blend50_both':'原始 + 半强度恢复（双侧）',
        'normalized_both':'亮度归一化','normalized_ria_both':'归一化 + RIA（双侧）','normalized_blend50_both':'归一化 + 半强度恢复（双侧）',
        'raw_ria_probe':'原始 + RIA（仅查询）','raw_blend50_probe':'原始 + 半强度恢复（仅查询）',
        'normalized_ria_probe':'归一化 + RIA（仅查询）','normalized_blend50_probe':'归一化 + 半强度恢复（仅查询）'}
    rows=''
    for key,label in names.items():
        values=[next(r['correct'] for r in results if r['algorithm']==a and r['variant']==key and r['subset']=='all') for a in ('DoN','FastCC','local_training_matcher')]
        rows+='<tr><td>'+label+'</td>'+''.join(f'<td>{v}/20</td>' for v in values)+'</tr>'
    check=read('checkpoint-check.json');stats=read('stats.json')['stats']
    alternative=''.join(f"<li>{html.escape(r['variant'])}: {r['correct']}/20</li>" for r in check['existing_checkpoint_alternatives'])
    text=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>本地恢复模型排查</title>
<style>body{{max-width:1100px;margin:40px auto;padding:0 24px;font:17px/1.65 system-ui;color:#213547;background:#f8fafc}}table{{width:100%;border-collapse:collapse;background:white}}td,th{{border:1px solid #cbd5e1;padding:10px;text-align:left}}.note{{padding:18px;background:#e0f2fe;border-radius:10px}}img{{max-width:100%}}details{{margin:20px 0}}a{{color:#0369a1}}</style><body>
<h1>本地 PalmIR 式恢复：有什么实际可改</h1><p class="note">现有权重在相机 ROI 上几乎输出原图。
目前测到的一分提升来自亮度归一化，不能归功于恢复。ROI 修复已保留，恢复没有强制接入默认匹配。</p>
<p><a href="../heatmap-v3-20261025/report.html">ROI 修复报告与最新补丁</a></p>
<h2>全部 40 张，固定 20 张录入 / 20 张查询</h2><p>固定 heatmap ROI、原划分、身份内距离中位数。
不做质量或几何筛样本。参数菜单在此次评分前写入 plan.json；这批图已用于多轮排查，所有结果都是开发集探索。
DoN/FastCC 本来已有百分位归一化；神经 matcher 原来直接接收 0–1 原像素。</p>
<table><tr><th>输入方式</th><th>DoN</th><th>FastCC</th><th>配套神经 matcher</th></tr>{rows}</table>
<h2>模型是否没有正确加载</h2><p>RIA、matcher、checkpoint 和模型实现哈希一致，配套关系核验通过。
models.py、data.py、losses.py、training.py 都与训练 provenance 一致。</p>
<ul><li>相机原始输入：平均像素改变 {stats['raw']['mean_abs_change_8bit']:.3f}/255。</li>
<li>归一化输入：平均像素改变 {stats['normalized']['mean_abs_change_8bit']:.3f}/255。</li>
<li>40 张原始输入 PyTorch 对 ONNX 最大绝对误差 {check['parity']['raw']['max_abs_error']:.8f}（0–1 标度），两者均几乎原样返回。</li></ul>
<p>另取训练域预先选定的 8 个不同掌类别各一张图，加 Gaussian σ=1.5 做响应检查：平均输出改变约 11.07/255，
平均像素误差从 0.04991 降为 0.02127。说明网络并非无条件恒等映射；这是训练图上的合成响应检查，不是独立恢复性能验证。</p>
<h2>替换已有恢复权重的对照</h2><p>同一配套神经 matcher，CPU PyTorch，完整 20 查询；只读已有 checkpoint，没有重训。</p><ul>{alternative}</ul>
<h2>可行的改法及证据边界</h2><ol>
<li><strong>先统一输入和 ROI。</strong>归一化单独有 14→15/20 的开发集变化，但还需新会话验证。错误裁框不能靠局部恢复器补救。</li>
<li><strong>针对相机域设计训练。</strong>当前训练集是固定 PolyU-II 掌类别 ROI，退化只有 Gaussian / motion blur（另有 10% clear），没有相机域曝光、噪声、压缩、缩放与裁框扰动的联合训练。
可以用训练身份生成这些退化，保留原图做监督，加入清晰输入的保持约束；各因素应单独消融。这是待验证路线，不能据当前结果断言必然有效，也不代表这批相机图就是模糊。</li>
<li><strong>匹配最终识别目标。</strong>现有 RIA 的身份损失来自冻结 PalmMatcher 的特征，而默认 demo 使用 DoN。若最终采用神经 matcher，应配套验证整个链；若保留 DoN，需要用独立开发数据验证恢复对其距离分离是否改善，不能假定 RIA 会迁移。</li>
<li><strong>验证增益而非只看锐化。</strong>比较不恢复、仅归一化、pixel、RIA；留出新身份和新拍摄会话，记录同手与异手分数。当前40张不再作为独立测试。没有真实配对参考时，不把同一人另一张照片直接当逐像素恢复目标。</li></ol>
<p>这轮没有启动训练、下载模型、改变研究队列或部署到 Pi；也没有把恢复强度开大当作修复。现有权重不支持“加恢复就会改善”的结论。</p>
<h2>复现与逐图结果</h2><p><a href="plan.json">固定实验菜单</a> · <a href="neural.json">神经匹配完整分数</a> ·
<a href="classical.json">传统匹配完整分数</a> · <a href="checkpoint-check.json">checkpoint 校验与响应检查</a> · <a href="stats.json">输出变化与模型信息</a></p>
<p>运行 tools/audit_restoration_adaptation.py &lt;heatmap-replay&gt; &lt;new-output&gt;；
再用现有 PyTorch 环境运行 tools/check_restoration_checkpoint.py &lt;experiment&gt; &lt;output&gt;。</p>
'''
    for start in range(0,40,10):text+=f'<details><summary>样本 {start+1}–{start+10}：六种输入/输出对照</summary><img src="comparison-{start}.jpg"></details>'
    (out/'report.html').write_text(text+'</body></html>',encoding='utf-8')
    print(out/'report.html')


if __name__=='__main__':main()
