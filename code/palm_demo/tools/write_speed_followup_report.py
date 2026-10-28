"""Render the completed fixed-cohort Pi speed audit without hiding slow queries."""
import argparse
import html
import json
from pathlib import Path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root',type=Path)
    args=parser.parse_args();root=args.root
    def read(path):return json.loads((root/path).read_text(encoding='utf-8'))
    runs={c:read(f'pi-staged-{c}-summary.json') for c in ('new','old')}
    ready={c:read(f'ready-staged-{c}.json') for c in runs}
    cases=read('staged-final-all-splits/results.json')
    assert len(cases)==224, 'Do not present an incomplete audit as complete'
    integrity=read('final-data-integrity.json')
    baseline=json.loads((root.parent/'pi5-v6-20261028/comparison.json').read_text())['runs']
    labels={'new':'新相机','old':'旧相机'}
    escape=lambda value:html.escape(str(value))
    def table(headers,rows):
        return '<table><thead><tr>'+''.join('<th>'+escape(x)+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+escape(x)+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table>'
    seconds=lambda ms:f'{ms/1000:.3f} s'
    rows=[]
    for c,r in runs.items():
        rows.append([labels[c],f"{r['correct']}/{r['total']}",f"{r['correct_within_2s']}/{r['total']}",
            seconds(baseline['final-'+c]['identify']['median_ms'])+' → '+seconds(r['identify']['median_ms']),
            seconds(r['identify']['p95_ms']),seconds(r['identify']['max_ms'])])
    body='<h1>树莓派 5：识别速度与准确率</h1><p>2026-10-29 · v10 分阶段检索 + ARM 原生配准 · 正式服务仍为 v6</p>'
    passed=all(c['correct']==c['total'] for c in cases) and all(r['correct_within_2s']==r['total'] for r in runs.values())
    body+='<div class="notice">'+('历史数据速度验收通过；独立验证仍待完成。' if passed else '仍未达到“全部 2 秒内且不降识别率”。中位数改善不能掩盖困难图的长尾。')+'</div>'
    body+='<h2>完整 HTTP 流程</h2>'+table(['数据','正确','2 秒内正确','识别中位数：v6 → 实验版','P95','最大值'],rows)
    body+='<p>从原图重新定位、提取和匹配，包含 HTTP 往返。使用隔离的模拟账户；相机拍摄由文件回放替代，未验证实时预览竞争。</p>'
    body+='<h2>固定划分回归与防过拟合</h2>'+table(['数据','完成划分','每组正确数范围'],[[labels[c],sum(x['case'].startswith(c+'_') for x in cases),str(min(x['correct'] for x in cases if x['case'].startswith(c+'_')))+'–'+str(max(x['correct'] for x in cases if x['case'].startswith(c+'_')))+'/20'] for c in runs])
    body+='<p>这些划分重复使用同一批 80 张开发图，不能当作独立准确率。预留的 4 人、80 张旧相机图仍未用于识别或调参；没有身份特例、删图或放宽判定。</p>'
    body+='<p>原始开发图校验：'+escape(integrity['development_unchanged'])+'；预留归档校验：'+escape(integrity['reserved_unchanged'])+'。</p>'
    cold=[]
    for c,r in ready.items():
        for p in r['passes']:
            cold.append([labels[c],p['label'],f"{p['correct']}/{p['n']}",f"{p['correct_within_2s']}/{p['n']}",seconds(p['median_ms']),seconds(p['p95_ms']),seconds(p['first_ms'])])
    body+='<h2>重启后与重复查询</h2>'+table(['数据','轮次','正确','2 秒内正确','中位数','P95','本轮首次'],cold)
    body+='<p>启动索引加载另计：新图 '+f"{ready['new']['startup_s']:.3f}"+' 秒，旧图 '+f"{ready['old']['startup_s']:.3f}"+' 秒。未提前计算查询身份；每轮都重新处理原图。</p>'
    body+='<h2>所有超过 2 秒的完整流程查询</h2>'+table(['数据','样本','耗时','路线'],[[labels[c],q['sample'],seconds(q['ms']),q['route']] for c,r in runs.items() for q in r['over_2s']])
    body+='<h2>录入、资源与交互</h2>'+table(['数据','五图录入中位数','峰值 RSS','并发两次请求耗时'],[[labels[c],seconds(r['enroll']['median_ms']),f"{r['peak_rss_bytes']/1024**3:.2f} GiB",' / '.join(seconds(q['ms']) for q in ready[c]['concurrent_requests'])] for c,r in runs.items()])
    body+='<p>新旧数据共八次模拟支付及取消、重复确认检查通过。并发查询返回正确身份，测试后交易数未增加。Python：151 通过、2 个 PalmIR/ONNX 测试因环境缺依赖跳过；另明确排除 5 个旧 API 测试。前端交互检查通过。</p>'
    body+='<h2>为什么仍有长尾</h2><p>普通图在姿态或局部配准阶段就能明确排序；不明确的图继续扩大搜索，最后保留原来的完整搜索。完整搜索仍需多次定位和大量特征配准。不能把这些耗时删掉，也不能降低置信要求来凑 2 秒。</p>'
    body+='<p>ARM 内核的 4,760 次配准与参考实现逐次一致。更快但漏匹配的 v7/v8 结果均保留。热图模型裁剪只有约 10 ms 推理收益，未接入。未使用预留数据反复选择参数。</p>'
    body+='<p><a href="pi-staged-new-summary.json">新图原始统计</a> · <a href="pi-staged-old-summary.json">旧图原始统计</a> · <a href="staged-final-all-splits/summary.json">全部划分汇总</a></p>'
    page='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Pi 5 识别加速验证</title><style>body{font:16px/1.6 system-ui,sans-serif;background:#f4f6fa;color:#182331;margin:0}main{max-width:1150px;margin:30px auto;background:white;padding:32px;border-radius:16px}h1{font-size:30px}h2{font-size:21px;margin-top:30px}p{color:#465568}.notice{background:#fff1d4;border-left:5px solid #c98418;padding:16px;font-weight:600}table{border-collapse:collapse;width:100%;font-size:14px}th,td{padding:10px;border-bottom:1px solid #e2e7ef;text-align:left;overflow-wrap:anywhere}th{background:#eef3f9}a{color:#1764a1}@media(max-width:800px){main{margin:0;padding:16px}table{font-size:12px}th,td{padding:5px}}</style><main>'+body+'</main></html>'
    output=root/'report.html';output.write_text(page,encoding='utf-8');print(output.resolve())


if __name__=='__main__':main()
