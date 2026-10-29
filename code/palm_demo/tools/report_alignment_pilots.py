"""Report completed proposal screens without claiming deployment or Pi latency."""
import argparse,html,json
from pathlib import Path


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path);p.add_argument('output',type=Path)
    args=p.parse_args();rows=[];evidence=[]
    configurations=[('局部对比度 + SIFT','local-contrast-screen-20261029', 'device-contrast-screen-20261029'),
        ('XFeat + 原 SIFT 比率检验','xfeat-pilot-20261029/development-screen',None),
        ('XFeat + 上游默认 MNN','xfeat-pilot-20261029/development-mnn-screen','xfeat-pilot-20261029/device-mnn-screen'),
        ('XFeat + 默认 MNN + 注册帧关系','xfeat-pilot-20261029/development-linked-screen','xfeat-pilot-20261029/device-linked-screen')]
    for name,dev,device in configurations:
        row=[name];entry=dict(method=name)
        for label,path in (('development',dev),('expanded_device',device)):
            if path is None:row+=['未运行','—'];continue
            result=json.loads((args.root/path/'results.json').read_text(encoding='utf-8'))
            assert result['complete']
            entry[label]=result
            row.extend([f"{result['rescued']}/{len(result['records'])}",str(result['wrong_confident'])])
        rows.append(row);evidence.append(entry)
    def table(headers,rows):
        return '<table><tr>'+''.join('<th>'+html.escape(v)+'</th>' for v in headers)+'</tr>'+''.join(
            '<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in row)+'</tr>' for row in rows)+'</table>'
    content='''<!doctype html><meta charset="utf-8"><title>困难查询通用对齐实验</title>
<style>body{font:16px/1.65 system-ui;max-width:1200px;margin:35px auto;padding:0 20px;color:#183046}table{border-collapse:collapse;width:100%}th,td{border:1px solid #ccd5df;padding:10px;text-align:left}th{background:#eaf0f7}.note{background:#fff3db;padding:15px;border-left:4px solid #a65c13}pre{white-space:pre-wrap;overflow-wrap:anywhere}</style>
<h1>困难查询：通用对齐路径筛查</h1><p>2026-10-29 · 原图回放 · 实验路径均未接入 demo</p>
<p class="note">这轮没有证明新的准确率或整流程速度提升。现有纯 Pi 基线仍是 165/170 正确、139/170 在 2.5 秒内正确；中位 1.564 秒、最大 14.342 秒。</p>
<p>先检查原 80 张开发图的全部 224 个划分中、v24 进入完整搜索的 30 次查询（仅 3 张不同图片）。其他原有提前返回路径保持不变。参数冻结后复查扩展 7 人基线中的全部 16 次完整搜索。数据已被反复查看，不能称独立未见验证。</p>
<h2>达到原置信门槛并正确返回的次数</h2>'''
    content+=table(['固定方案','开发集困难查询','开发集错误高置信','扩展困难查询','扩展错误高置信'],rows)
    rotation_path=args.root/'rotation-localizer-screen-20261029/results.json'
    if rotation_path.is_file():
        rotation=json.loads(rotation_path.read_text(encoding='utf-8'));assert rotation['complete']
        content+='<h2>固定旋转定位控制</h2><p>所有定位输入统一旋转 180° 后映回原图，仍用原像素评分；80 张开发图中 '+str(rotation['valid_images'])+' 张通过几何检查。检查所有 224 个划分，没有按身份选择旋转。</p>'
        content+=table(['控制','正确高置信/全部查询','错误高置信','原完整搜索被救回'],[
            [name,str(s['correct_confident'])+'/'+str(s['total']),s['wrong_confident'],s['fallback_rescued']]
            for name,s in rotation['summary'].items()])
        content+='<p>query_only：旋转定位查询/原注册；both：查询和注册都统一旋转定位。原 pose 路径高置信次数为 2554/4480，两个旋转控制更少；未做扩展数据和 Pi 整流程测速，也未接入。</p>'
    content+='''<p>每次都要求最佳原图 FastCC 分数≤0.32、第二名差≥0.08。几何和采样边界保护保持不变。原图身份只用于事后统计。高置信返回条件不满足时，保留原有完整搜索结果；候选第一名碰巧正确不计为修复。未尝试通过放宽门槛或按身份分支取得数字改善。</p>
<h2>方案和结论</h2><p>局部对比度采用固定 CLAHE clip=2、8×8 网格，SIFT 原始/σ2 两路。XFeat 使用公开预训练权重，无新增训练；先检查原比率匹配，再检查上游默认的互为最近邻且 cosine&gt;0.82。查询视野为 768×768 上下文，注册视野为 384×384。最终均对原始灰度图重新裁剪并计算掌纹分数，注册五帧取最佳两帧。</p>
<p>关系复用仅将有效查询对齐通过同一注册身份已有的 SIFT 帧间变换转移，再用原始查询像素重新评分。开发集增加 27 次、扩展集增加 60 次有效评分，但没有增加满足门槛的提前返回。</p>
<p>三个方案在扩展数据均未触发新的提前返回，五张误认仍未修复。没有接入运行路径，也没有为不合格候选进行树莓派整流程测速；表中次数不代表节省的秒数。</p>
<h2>模型与平台核对</h2><p>XFeat 的 384/768 固定形状 ONNX 输出已与 PyTorch 比较；随机输入最大绝对误差约 5×10⁻⁵，稀疏关键点坐标一致，描述子解码通过 10⁻⁴ 容差核对。此核对只验证转换和实现一致性，不证明真实掌纹精度或目标设备速度。</p>
<p>扩展筛查读取全部 170 张原始 JPEG 的 SHA 校验、树莓派实际查询矩阵、注册矩阵和注册参考编码。注册帧关系由 Pi 计算，原模板哈希不变，供电标志全为 0x0。Windows 离线特征/成对结果复用只用于实验，不在运行查询中缓存结果；相机、生产服务和账户未改动。</p>
<p>下一步仍应围绕 ROI 稳定性和可重复对应关系展开。这轮排除了“仅增强局部对比度”及这个固定轻量特征组合；不能外推所有学习特征或全部预处理方案都无效。</p>
<details><summary>完整协议与逐次记录</summary><pre>'''+html.escape(json.dumps(evidence,ensure_ascii=False,indent=2))+'</pre></details>'
    args.output.write_text(content,encoding='utf-8');print(args.output)


if __name__=='__main__':main()
