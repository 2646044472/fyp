"""Summarize saved Pi v24 development runs without selecting or dropping queries."""
import argparse
import html
import json
from pathlib import Path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('evidence',type=Path)
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    rows=[];details=[]
    for path in sorted(args.evidence.glob('ready-quality-v24-*.json')):
        value=json.loads(path.read_text())
        for run in value['passes']:
            rows.append([path.stem,run['label'],f"{run['correct']}/{run['n']}",
                f"{run['correct_within_2_5s']}/{run['n']}",f"{run['median_ms']/1000:.3f}",f"{run['max_ms']/1000:.3f}"])
        details.append(dict(run=path.stem,startup_s=value['startup_s'],
            queue_correct=value['queue_correct'],queue_seconds=[q['ms']/1000 for q in value['concurrent_requests']]))
    for path in sorted(args.evidence.glob('quality-v24-fresh-*/summary.json')):
        value=json.loads(path.read_text());run=value['identify']
        rows.append([path.parent.name,'重新注册',f"{value['correct']}/{value['total']}",
            f"{value['correct_within_2_5s']}/{value['total']}",f"{run['median_ms']/1000:.3f}",f"{run['max_ms']/1000:.3f}"])
        details.append(dict(run=path.parent.name,enrollment_timing=value['enroll'],
            simulated_transactions=value['payment']['transactions'],
            originals_unchanged=value['originals_unchanged'],slow_queries=value['over_2s']))
    table='<table><tr>'+''.join(f'<th>{s}</th>' for s in ['实验','轮次','正确','正确且≤2.5秒','中位秒','最慢秒'])+'</tr>'
    table+=''.join('<tr>'+''.join(f'<td>{html.escape(str(s))}</td>' for s in row)+'</tr>' for row in rows)+'</table>'
    content='''<!doctype html><html lang="zh"><meta charset="utf-8"><title>本机数据 v24 实测</title>
<style>body{font:16px/1.65 system-ui;max-width:1250px;margin:40px auto;padding:0 24px;color:#182534}table{border-collapse:collapse;width:100%;font-size:14px}td,th{padding:9px;border:1px solid #ccd5df;text-align:left}th{background:#eaf0f6}pre{white-space:pre-wrap;overflow-wrap:anywhere}h1{font-size:28px}</style>
<h1>树莓派本机采集数据：v24 实验检查点</h1><p>2026-10-29 · 纯 Pi 5 · 实验隔离环境 · 正式 v6 未替换</p>
<p>所有计时均包含读取历史原图、预处理、ROI、特征、检索/配准、评分和本机 HTTP 返回；不含相机拍摄和外部上传。每个查询重新计算，不缓存识别答案。</p>
<h2>完整结果（包含超时）</h2>'''+table+'''
<h2>本轮结论</h2><p>四组空库重新注册共 80 次查询全部正确，77 次在 2.5 秒内。新相机反向分组暴露 13.886 秒长尾，尚未稳定达标。其早期搜索至约 2.59 秒仍不确定，完整回退再耗时约 11.30 秒；另两张超时主要是定位已花约 2 秒。不能降低置信门槛：最慢图的加权快速评分曾将错误身份排第一，原门槛成功拒绝了这一捷径。</p>
<h2>改动与边界</h2><p>两路独立 SIFT 并行、对应点分组中位数批量计算保持原数学结果。新的质量加权评分降低弱滤波响应、卷积边界的影响；仅在原有早期路径不确定时尝试，仍不确定就完整回退。这是新的距离定义，并非普通 Hamming 的等价加速。切换时整组替换评分，不混合两套距离。</p>
<p>224 个固定开发集划分均为 20/20；它们反复使用同一批 80 张开发图，不能当成独立泛化证据。阈值数值未放宽，但新距离仍需独立未知身份拒识校准。公开数据库暂未用于本轮优化；已经看过的保留数据也不用于选参数。</p>
<p>互换注册/查询照片仍是同设备实验。40 人容量、独立采集会话、真实拍摄均未通过验证。不能把这批开发数据的改善说成已解决此前保留队列的 10.681 秒长尾。并发排队和启动时间另列。</p>
<h2>启动、排队、重新注册和慢查询明细</h2><p>各 *_ms 数值单位为毫秒。</p><pre>'''+html.escape(json.dumps(details,ensure_ascii=False,indent=2))+'</pre></html>'
    args.output.write_text(content,encoding='utf-8')
    print(json.dumps(rows,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
