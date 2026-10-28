"""Present corrected DoN results and preserve the earlier CNN assay separately."""
import json
from pathlib import Path
import sys


def write(root):
    don=json.loads((root/'audit/don_summary.json').read_text())['5']
    blur=json.loads((root/'audit/blur_probe_pytorch/summary.json').read_text())
    audit=json.loads((root/'audit/roi_audit.json').read_text())
    low=sum(r['std']<12 for r in audit)
    rows=''
    cases=[('历史原图（未加人工模糊）',don),('人工高斯模糊 σ=1.5',blur['gaussian_1.5']),
           ('人工高斯模糊 σ=2.5',blur['gaussian_2.5']),('人工运动模糊 9px / 45°',blur['motion_9_45deg'])]
    for name,result in cases:
        raw,restored=result['raw'],result['restored']
        rows+=f"<tr><td>{name}</td><td>{raw['true_accepts']}/20 → {restored['true_accepts']}/20</td><td>{raw['false_accepts']}/60 → {restored['false_accepts']}/60</td></tr>"
    images=''.join(f'<details><summary>查看第 {i} 组全部 10 张原图与 ROI</summary><img src="/palmir-audit-{i}.jpg" alt="原图裁剪叠加与恢复对比"></details>' for i in range(1,5))
    html=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>PalmIR × DoN 复核报告</title><style>body{{font:16px system-ui;max-width:1100px;margin:auto;padding:24px;background:#f4f7f5;color:#172d31;line-height:1.7}}section{{background:white;padding:22px;margin:20px 0;border-radius:14px}}h1{{font-size:25px}}h2{{font-size:21px}}table{{width:100%;border-collapse:collapse}}td,th{{text-align:left;padding:12px 7px;border-bottom:1px solid #dce5e3}}img{{width:100%;height:auto}}a{{color:#17654b}}.warn{{border-left:4px solid #c58a31}}summary{{cursor:pointer;padding:12px 0}}.note{{color:#566d68}}</style>
<a href="/palmir">返回实时恢复与 DoN 比较</a><h1>PalmIR 风格本地模型 × 原项目 DoN：复核结果</h1>
<section><h2>目前没有证据支持默认开启恢复来提高本人通过率</h2>
<p>历史原图中 DoN 已通过 20/20；恢复后仍为 20/20。人工模糊对照中，有的条件降低误通过，有的条件使本人通过从 20/20 降到 7/20，收益不稳定。</p>
<table><tr><th>输入条件</th><th>本人通过：不恢复 → 恢复</th><th>其他掌纹误通过：不恢复 → 恢复</th></tr>{rows}</table>
<p>2 人、4 只手、40 张历史原图。每只手第 1–5 张作未恢复的注册图，第 6–10 张测试。DoN 比较取与 5 张注册图的距离中位数；固定阈值 {don['threshold']:.6f} 来自原图第 2–5 张对其他掌纹的校准比较，全部分支保持一致。</p>
<p class="note">校准样本与注册集有重叠，且来自同一采集短序列；这是小样本探索，不能证明总体准确率，不能用来校准新 USB 摄像头。人工模糊不是真实相机失焦。它们没有替代或覆盖原图。本人通过为 100% 时，本批样本不能再展示通过率提升。</p></section>
<section class="warn"><h2>对前一版报告的纠正</h2><p>之前的 55% 使用 PolyU 训练的本地 CNN，不能当作原项目 DoN 的通过率。原 CNN 数值和逐项分数均保留，没有因结果不好删除样本。本表已改为原项目的 DoN。</p>
<p>检查发现低对比模糊输入对浮点运算敏感，ONNX 与 PyTorch 在部分图像上不满足最初的严格误差界；σ=2.5 的误通过计数可相差 1 次。表中人工模糊结果以原始 PyTorch 检查点复核为准，不能承诺树莓派 ONNX 得到完全相同的判定。实时页面只提供距离对比，不部署通过阈值。</p></section>
<section><h2>你提到的“有些掌纹有问题”</h2><p>已检查全部 40 张原图与绿色裁剪框。未见明显裁到掌外，但这不能证明关键点定位精度。确实存在阴影、对比度偏低和姿态造成的取景变化；这类问题不等同于模型训练中的高斯/运动模糊。</p>
<p>按工程提醒值“灰度标准差低于 12”，有 {low}/40 张被提醒，未因此剔除。尤其 bankey 右手第 9、10 张对比度约 5.5、5.8。部分裁剪下方的暗块来自原图阴影，不是凭空补出的黑边。优先补光、稳定距离和对齐，再评估恢复。</p>
{images}</section><section><h2>人工模糊诊断示例</h2><p>每组依次为历史 ROI、人工加模糊、原始 PyTorch 模型恢复；恢复可能改变掌纹细节。</p><img src="/palmir-blur-examples.jpg" alt="原图人工模糊与恢复三列对比"></section>
<section><h2>当前接入状态</h2><p>树莓派 USB 连接、连续自动对焦和 640×480 预览正常；高清拍摄为 1920×1080。页面已加入原 DoN 的恢复前后距离比较，并提示低对比输入。使用的是本地 CompactRestorer RIA，不是官方 PalmIR 网络。没有重启暂停的训练队列。</p></section></html>'''
    (root/'report.html').write_text(html,encoding='utf-8')


if __name__=='__main__':write(Path(sys.argv[1]))
