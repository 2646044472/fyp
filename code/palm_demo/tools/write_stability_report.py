"""Build a Chinese stability report from saved evidence, without rescoring."""
import argparse
import html
import json
from pathlib import Path


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def table(headers, rows):
    def cell(x):
        return html.escape(str(x))
    return '<div class="scroll"><table><thead><tr>' + ''.join('<th>'+cell(x)+'</th>' for x in headers) + '</tr></thead><tbody>' + ''.join('<tr>'+''.join('<td>'+cell(x)+'</td>' for x in row)+'</tr>' for row in rows) + '</tbody></table></div>'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    root = args.root
    data = read(root/'stability/summary.json')
    algs = ['DoN_median', 'FastCC_median', 'FastCCPoseNearest-v1']
    fixed = {(r['case'], r['algorithm']): r for r in data['fixed_cases']}
    def score(case, alg):
        r = fixed[case, alg]
        return f'{r["correct"]}/{r["total"]}'
    cases = [('old_original', '旧图：前五录入、后五查询'), ('old_reverse', '旧图：后五录入、前五查询'),
             ('new_original', '新图：前五录入、后五查询'), ('new_reverse', '新图：后五录入、前五查询'),
             ('old_to_new_last5', '旧图录入 → 新图查询'), ('new_to_old_last5', '新图录入 → 旧图查询')]
    fixed_table = table(['固定划分', 'DoN', 'FastCC', '九姿态候选'], [[label, *[score(case, a) for a in algs]] for case, label in cases])
    sensitivity = {(r['cohort'], r['algorithm']): r for r in data['enrollment_sensitivity']}
    random_rows = []
    for c, label in [('old', '旧图'), ('new', '新图')]:
        for a in algs:
            r = sensitivity[c, a]
            random_rows.append([label, a, f'{r["min_correct"]}–{r["max_correct"]}/20', f'{r["mean_correct"]:.1f}/20'])
    mixed = read(root/'mixed-enrollment/summary.json')
    mixed_rows = []
    for no, nn in [(5, 0), (0, 5), (3, 2), (2, 3), (5, 5)]:
        pair = [next(r for r in mixed if r['old_templates']==no and r['new_templates']==nn and r['query_cohort']==c and r['algorithm']==algs[-1]) for c in ['old', 'new']]
        mixed_rows.append([f'旧 {no} + 新 {nn}', *[f'{r["first_correct"]}/20' for r in pair],
                           f'{pair[1]["random_min"]}–{pair[1]["random_max"]}/20'])
    stress_rows = []
    for condition, label in [('dark_065', '亮度 ×0.65'), ('blur_sigma3', '原图高斯模糊 σ=3'), ('shift_3pct', '原图平移 3%')]:
        control = read(root/f'pose-stress-{condition}/aggregation-controls.json')
        r = next(r for r in control if r['algorithm']=='FastCC' and r['pose']=='rotation_scale' and r['rule']=='nearest')
        stress_rows.append([label, f'{r["correct"]}/{r["total"]}'])
    orientations = read(root/'cross-orientation/results.json')
    orientation_rows = []
    for direction in ['old_to_new', 'new_to_old']:
        for a in ['DoN', 'FastCC']:
            rows = [r for r in orientations if r['direction']==direction and r['algorithm']==a]
            assert len(rows)==16
            base = next(r for r in rows if r['rotation']==0 and not r['mirror'] and not r['inverse'])
            orientation_rows.append([direction, a, f'{base["correct"]}/20', f'{max(r["correct"] for r in rows)}/20'])
    http_rows = []
    for c, label in [('old', '旧图'), ('new', '新图')]:
        replay = read(root/f'pose-http-{c}/summary.json')
        demo = replay['demo']
        correct = sum(p['result'].get('user_id')==p['identity'].replace(':','-') for p in demo['probes'])
        assert replay['originals_unchanged'] and replay['demo_matcher']==algs[-1]
        http_rows.append([label, f'{correct}/{len(demo["probes"])}', f'{sum(e["http_status"]==200 for e in demo["enrollments"])}/4', demo['payment']['transactions']])
    repeat = read(root/'stability/repeatability.json')
    assert len(repeat)==10 and all(r['identical'] for r in repeat) and data['originals_unchanged']
    doc = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>新旧相机算法稳定性实测</title>
<style>body{margin:0;background:#f3f5f7;color:#182d3c;font:17px/1.75 system-ui,"Microsoft YaHei",sans-serif}main{max-width:1120px;margin:auto;padding:30px 24px 70px}h1{font-size:36px;line-height:1.3}h2{margin-top:38px;font-size:25px}.card{background:white;border-radius:12px;padding:22px;margin:20px 0}.warning{border-left:5px solid #c46c31}table{border-collapse:collapse;background:white;width:100%;font-size:15px}td,th{padding:11px;border-bottom:1px solid #dae1e7;text-align:left}th{background:#e3ebf1}.scroll{overflow:auto}a{color:#006b96}img{max-width:100%;height:auto}.small,figcaption{font-size:14px;color:#4c6170}code{font-size:14px;overflow-wrap:anywhere}</style><main>
<p>2026-10-28 · 本地开发集稳定性审计 · 候选尚未部署</p>
<div class="card"><a href="../single-device/report.html">最新：按用户要求仅优化单设备，查看自动对齐修复与完整回放结果</a>。下文保留上一轮审计记录；跨设备已不作为后续验收目标。</div>
<h1>旧数据表现稳定；<br>新数据仍有波动，跨相机识别不可靠。</h1>
<div class="card warning"><strong>不能把最好一次的18/20当成稳定准确率。</strong><p>九姿态候选在新数据十种随机录入划分中为15–18/20，反向划分降到16/20；旧数据所有划分均20/20。旧相机录入后识别新图只有6/20，反过来10/20。</p></div>
<p>使用新旧各40张原图，共80张、2个人的左右手共4个掌纹类别。每类每批10张；标准划分为1–5录入、6–10查询。所有失败均计入分母，无查询自匹配，原图哈希未变。身份对应关系来自原始元数据。数据已反复参与开发，下面的重复划分不是额外的独立样本，也不代表现场或陌生人识别准确率。</p>
<h2>固定划分与跨相机对照</h2>''' + fixed_table
    doc += '<p>新候选使用固定九种旋转/尺度，从完整原图裁取，查询与每个身份的五个原始模板取最近距离。所有身份采用相同规则。反向划分时，DoN为18/20，候选只有16/20；候选并非在所有条件下都更好。</p>'
    doc += '<h2>换一组录入照片，会不会变？</h2>' + table(['数据', '算法', '十种划分范围', '平均正确数'], random_rows)
    doc += '<p>每类随机选5张录入，其余5张查询，固定十个种子。新数据候选平均16.7/20，DoN为15.1/20；只有同一批40张反复重分，不能按200张独立查询计算可靠性。另抽取新旧各5张重复提取特征，10/10完全一致：代码的重复计算可复现，但换样本后的识别不稳定。</p>'
    doc += '<h2>同时录入两种相机，能否补救？</h2>' + table(['每类录入组成', '旧图查询：固定选择', '新图查询：固定选择', '新图查询：更换模板范围'], mixed_rows)
    doc += '<p>查询始终是两批各自第6–10张；录入只从第1–5张选择，随机选择不读取查询成绩。混合后并不稳定：总共五张模板时，新图最差只有8/20或9/20；即使新旧各五张，新图也从18/20降到15/20。说明增加异域模板会引入竞争错配，不能直接把混合录入当作修复。十模板只是离线对照，未改应用的五张录入流程。</p>'
    doc += '<h2>方向与画质对照</h2>' + table(['方向', '算法', '不变换', '16种统一变换的最高值'], orientation_rows)
    doc += '<p>四个直角方向 × 是否镜像 × 是否反转亮度；每次对全部查询采用一个统一变换。即便事后选择最好的设置，也只有9–10/20或更低，未发现统一镜像/旋转即可解决的证据。不能据此修改身份或左右手标签。</p>' + table(['合成查询变化', '九姿态候选'], stress_rows)
    doc += '<p>合成压力测试中保持录入图不变；平移条件有一张几何失败，仍计错。它们仍是开发图的变体，不能替代真实新会话。现有Local PalmIR-style RIA在最终v5 ROI上没有增加正确查询数，因此继续关闭默认恢复。</p>'
    doc += '<figure><img src="camera-context.jpg" alt="四类掌纹的新旧相机原图与自动ROI对照"><figcaption>每类固定第1张，左旧、右新，绿色为自动ROI。可见手掌占比、背景逆光、姿态和裁取掌区不同；这说明采集条件存在差异，不能单凭这些图认定相机硬件损坏。姓名与左右手来自元数据。</figcaption></figure>'
    doc += '<h2>完整流程与部署状态</h2>' + table(['本地实际HTTP回放', '查询正确', '录入成功', '隔离模拟支付笔数'], http_rows)
    doc += '''<p>候选代码已接入可选参数 <code>--demo-matcher FastCCPoseNearest-v1</code>；使用独立算法标识，需重新录入，不能混用旧模板。录入、查询、模板保存和模拟支付均执行真实应用代码，相机入口以历史图片替代，因此没有声称实时相机验收通过。</p>
<p><strong>默认与已部署版仍为v5 ROI + DoN。</strong>最后一次Pi实际HTTP为14/20；本地候选18/20尚未在Pi验收。Pi当前网络路径经过VPN且SSH未建立连接，本轮均在本地完成。未改生产账户与capture-only服务模式。每小时自动任务已删除，本轮是主动执行的实验。</p>
<h2>目前的工程判断</h2><p>九姿态匹配提高了新数据的部分划分表现，但没有解决跨相机掌区/成像差异，nearest模板规则也可能引入错配。此时不宜把候选设为默认或用单次18/20承诺demo可靠。接下来的有效修复方向是跨拍摄条件保持同一掌区的定位与对齐，并在未参与调参的新会话上验收；增加姿态数量、浮点采样、套现有恢复模型和直接混合模板都没有形成稳定的解决方案。</p>
<div class="card"><strong>可复核证据</strong><ul>
<li><a href="summary.json">稳定性汇总</a> · <a href="results.json">每次划分与逐查询结果</a> · <a href="repeatability.json">重复计算</a></li>
<li><a href="../mixed-enrollment/summary.json">混合录入汇总</a> · <a href="../mixed-enrollment/results.json">全部模板与查询评分</a></li>
<li><a href="../cross-orientation/results.json">统一方向对照</a> · <a href="../warp-stage-comparison.json">跨平台插值差异</a></li>
<li><a href="../pose-http-new/summary.json">候选新图HTTP</a> · <a href="../pose-http-old/summary.json">候选旧图HTTP</a></li>
<li><a href="../report.html">v5部署与PalmIR历史报告</a></li></ul></div></main></html>'''
    target = root/'stability/report.html'
    target.write_text(doc, encoding='utf-8')
    print(target)


if __name__ == '__main__':
    main()
