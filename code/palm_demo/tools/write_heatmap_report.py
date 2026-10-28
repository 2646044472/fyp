"""Package the locally verified heatmap repair and its full-denominator report."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import zipfile

APP=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output',type=Path)
    args=parser.parse_args();out=args.output
    read=lambda name:json.loads((out/name).read_text())
    records=read('records.json')
    results=read('classical.json')+read('neural.json')['results']
    rows=''
    for alg,old,new in [('DoN','original','heatmap_runtime'),('FastCC','original','heatmap_runtime'),
                        ('local_training_matcher','original_raw','heatmap_runtime_raw')]:
        values=[next(r['correct'] for r in results if r['algorithm']==alg and r['variant']==v and r['subset']=='all') for v in (old,new)]
        rows+=f'<tr><td>{alg}</td><td>{values[0]}/20</td><td>{values[1]}/20</td></tr>'
    failures=''.join(f"<li>{html.escape(r['identity'])} #{r['index']}: {html.escape(r['diagnostics']['roi_geometry_reason'])}</li>" for r in records if not r['runtime_valid'])
    live=''.join(f"<li>{r['algorithm']}: {r['correct']}/{r['total']}；几何拒绝 {r['geometry_rejected_probes']} 个查询，仍计入分母。</li>" for r in read('runtime-guard.json'))
    images=''.join(f'<details><summary>全部样本对照 {i+1}–{i+10}</summary><img src="comparison-{i}.jpg"></details>' for i in range(0,40,10))
    text=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>ROI 算法修复 v3</title>
<style>body{{max-width:1100px;margin:40px auto;padding:0 24px;font:17px/1.65 system-ui;color:#213547;background:#f8fafc}}h1,h2{{line-height:1.3}}table{{border-collapse:collapse;background:white;width:100%}}td,th{{padding:12px;border:1px solid #cbd5e1;text-align:left}}.note{{padding:18px;background:#e0f2fe;border-radius:10px}}img{{max-width:100%}}details{{margin:18px 0}}a{{color:#0369a1}}</style>
<h1>ROI 算法修复 v3 · 本地已验证</h1><p class="note">默认固定使用 PKLNet heatmap 分支，取消分支平均。
对比度、锐度只记录，不拦截。尚未部署到 Pi。此版本取代之前 consensus-v2 的拒绝方案。</p>
<h2>完整 40 张原图，固定 20 张录入 / 20 张查询</h2>
<p>每只手前五张录入、后五张查询，身份内取五个距离的中位数。以下保留所有样本，包含几何失败的裁图；没有通过筛样本提高分数。
这是同一开发集上的 rank-one 诊断，不是独立验证，也不是交易接受率或误认率。</p>
<table><tr><th>匹配器</th><th>旧融合 ROI</th><th>新运行代码 ROI</th></tr>{rows}</table>
<p>实际 ONNX 推理全部 40 张；与独立缓存 PyTorch heatmap 最大坐标差 {max(r['keypoint_parity_max_px'] for r in records):.5f} px。
几何通过由 31/40 变为 36/40。92 项相关测试通过；历史 test_existing_pipeline.py 仍引用迁移前模块，未计入。</p>
<h2>运行时几何检查另行报告</h2><p>应用仍不允许越界、塌缩裁框进入匹配。下面计入几何拒绝，不与上述无筛选实验混算。</p><ul>{live}</ul>
<h2>修复原因与剩余问题</h2><p>两个分支在 8/40 张图上端点方向相反，直接按数组位置平均会缩小甚至塌缩 ROI。
修复采用同一空间分支，不根据身份或匹配分数为每张图挑选分支。它移除了错误融合，但不能修复 heatmap 自身所有错误。</p><ul>{failures}</ul>
<p>端点先对齐再平均的对照：DoN 5/20、FastCC 7/20、神经匹配 13/20，因此未启用。
现有 OpenCV 检测器加四方向搜索的独立对照仅返回 22/40 个裁框，且可见背景误检；没有用成功子集报准确率，也没有将它设为自动回退。</p>
<h2>PalmIR</h2><p>本地是 CompactRestorer PalmIR-style RIA，并非官方 PalmIR 权重。对新 ROI，神经 matcher 原始输入、仅查询恢复、双侧恢复均为 14/20。
当前没有证据支持把恢复设成默认。检查官方项目时未找到可直接部署的完整预训练发布；这不代表官方方法无效。</p>
<p>后续已完成归一化、半强度恢复、纯像素恢复权重和 PyTorch 对照，见 <a href="../restoration-adaptation-20261025/report.html">本地恢复模型排查与可行改法</a>。</p>
<h2>部署与可复现材料</h2><p>旧模板需要用原编号重新录入五张；账户姓名、余额和交易保留。服务模式不随代码更新改变。
补丁依赖现有应用、PKLNet 权重及几何代码，不是全新安装包。部署前比对并备份远端文件，先做离线推理验收，再按原有模式启动。
Pi 网络由用户处理，本轮未部署。</p><p><a href="heatmap-v3-patch.zip">最新补丁</a> · <a href="patch-manifest.json">文件 SHA-256</a> ·
<a href="classical.json">全部传统匹配分数</a> · <a href="neural.json">神经 / RIA 分数</a> · <a href="runtime-guard.json">实际几何拦截结果</a> ·
<a href="records.json">逐图坐标与诊断</a></p><p>复跑：python tools/evaluate_heatmap_policy.py &lt;benchmark&gt; &lt;new-output-directory&gt;</p>
<h2>逐张裁框与原始 ROI 对照</h2>{images}</html>'''
    (out/'report.html').write_text(text,encoding='utf-8')
    files=['pklnet_roi.py','pklnet_policy.py','demo_flow.py','demo_page.py','gallery.py','palm_app/debug_ui.py',
        'README.md','docs/SETUP.md','deploy/make_deploy_bundle.ps1','tools/expose_pklnet_branches.py',
        'tools/export_pklnet_onnx.py','tools/audit_roi_branches.py','tools/evaluate_pklnet_policy.py',
        'tools/evaluate_heatmap_policy.py','tools/audit_endpoint_fusion.py','tools/audit_landmark_roi.py',
        'tools/write_heatmap_report.py','tools/audit_restoration_adaptation.py','tools/check_restoration_checkpoint.py',
        'tools/write_restoration_adaptation_report.py','tests/test_pklnet_consensus.py']
    entries={name:APP/name for name in files}
    for suffix in ('onnx','json'):
        name='pklnet-keypoints-diagnostics.'+suffix
        entries['pklnet/'+name]=APP.parent/'pklnet'/name
    manifest={name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in entries.items()}
    (out/'patch-manifest.json').write_text(json.dumps(manifest,indent=2))
    with zipfile.ZipFile(out/'heatmap-v3-patch.zip','w',zipfile.ZIP_DEFLATED) as archive:
        for name,path in entries.items():archive.write(path,name)
        archive.write(out/'patch-manifest.json','patch-manifest.json')
    with zipfile.ZipFile(out/'heatmap-v3-patch.zip') as archive:
        assert all(hashlib.sha256(archive.read(name)).hexdigest()==digest for name,digest in manifest.items())
    print(out/'report.html')


if __name__=='__main__':main()
