"""Full v26 evidence report, including failures and unchanged-path checks."""
import argparse,hashlib,html,io,json,sys,zipfile
from pathlib import Path
import numpy as np


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('baseline',type=Path);p.add_argument('control',type=Path)
    p.add_argument('previous',type=Path);p.add_argument('candidate',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--manifest',type=Path,help='Optionally render original/actual alternate ROI comparison sheets from the immutable archives')
    p.add_argument('--paired',type=Path,help='Completed same-app v25/v26 ABBA timing diagnostic')
    args=p.parse_args();paths=[args.baseline,args.control,args.previous,args.candidate]
    baseline,control,previous,candidate=[json.loads(p.read_text()) for p in paths]
    paired=json.loads(args.paired.read_text()) if args.paired else None
    assert paired is None or paired['complete']
    assert all(d['complete'] for d in (baseline,control,previous,candidate))
    def queries(d):return {(r['case'],q['sample']):q for r in d['runs'] for q in r['queries']}
    old,new=queries(previous),queries(candidate);assert old.keys()==new.keys()
    def stats(values):
        values=list(values);ms=[t['ms'] for t in values]
        return [f"{sum(t['correct'] for t in values)}/{len(values)}",f"{sum(t['correct'] and t['ms']<=2500 for t in values)}/{len(values)}",
            *[f'{v/1000:.3f}' for v in (np.median(ms),np.percentile(ms,95),max(ms))]]
    def table(headers,rows):
        return '<div class="scroll"><table><tr>'+''.join('<th>'+html.escape(str(v))+'</th>' for v in headers)+'</tr>'+''.join(
            '<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in row)+'</tr>' for row in rows)+'</table></div>'
    changed=[k for k,q in new.items() if q['result'].get('recognition_route')=='compnet_alternate_roi_confident']
    regressions=[k for k,q in new.items() if old[k]['correct'] and not q['correct']]
    fields=('status','user_id','score','second_score','recognition_route')
    differences=[k for k,q in new.items() if k not in changed and any(q['result'].get(f)!=old[k]['result'].get(f) for f in fields)]
    roi_equal=all(q.get('roi_byte_equal') for q in new.values())
    power=sorted({s['get_throttled'] for s in candidate['power_samples']})
    checks=all(r['payment_checks_complete'] for r in candidate['runs'])
    integrity=candidate['source_templates_unchanged'] and candidate['originals_unchanged']
    valid=not regressions and not differences and roi_equal and checks and integrity and power==['throttled=0x0']
    text='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>Pi 5 v26：复用定位候选完整实验</title>
<style>body{font:16px/1.65 system-ui;max-width:1450px;margin:32px auto;padding:0 22px;color:#1c2b3d}h1{font-size:28px}h2{margin-top:30px}table{width:100%;border-collapse:collapse;font-size:14px}td,th{padding:9px;border:1px solid #cdd5df;text-align:left;vertical-align:top}th{background:#eaf0f7;white-space:nowrap}.scroll{overflow:auto}.notice{padding:14px;border-left:4px solid #ae6519;background:#fff3df}code{overflow-wrap:anywhere}a{color:#1759a3}</style>
<h1>纯 Pi 5 v26：复用已经算好的另一个基础 ROI</h1><p>2026-10-30 · 原图回放完整 HTTP 流程 · 正式服务未切换</p>'''
    text+='<p class="notice">'+('完整性与无新增误认检查通过。' if valid else '存在回归或完整性问题，请勿采用，详见下表。')+'这是小范围提前返回优化，最难长尾及原有误认仍须保留，不能表述为所有查询≤2.5秒。</p>'
    text+='<h2>完整 Pi 结果</h2>'+table(['版本/协议','正确','正确且≤2.5秒','P50秒','P95秒','最大秒'],[
        ['v24 空库重新注册基线',*stats(queries(baseline).values())],
        ['v24 同协议图库复用对照',*stats(queries(control).values())],
        ['v25 主 ROI 冻结表征',*stats(old.values())],
        ['v26 复用基础 ROI 候选',*stats(new.values())]])
    text+='<p>活动原图169张、七个人、17个设备内掌纹身份。每个设备最早/最晚五张注册后查询其余原图，共168次查询；不跨设备。用户删除的一张历史斜拍图已在所有本表实验前排除，旧170次查询结果另存，不与本表直接算算法增益。所有失败和超时都在分母内。</p>'
    rows=[]
    for run in candidate['runs']:
        case=run['case'];refs=[old[case,q['sample']] for q in run['queries']]
        rows.extend([[case,'v25',*stats(refs)],[case,'v26',*stats(run['queries'])]])
    text+='<h2>逐设备、注册方向对照</h2>'+table(['分组','版本','正确','正确且≤2.5秒','P50秒','P95秒','最大秒'],rows)
    text+='<h2>改动及作用边界</h2><p>保留已有 pose 判断、主 ROI 的 v25 向量判断。只有两者不确定时，才读取初次定位已产生的 original/gamma 两个候选中另一块有效、与主 ROI 相交的区域，计算一次相同冻结 CompNet 特征，对整个图库评分。没有额外运行定位网络，没有增加窗口/尺度/平移，没有降低 .32/.08 数字门槛；不同 ROI 的距离不取混合最小值，有把握的候选身份冲突则继续原流程。注册向量仍只有每帧原始主 ROI。</p>'
    text+='<p>原图显示 ROI 保持原主 ROI，v26 的实际辅助匹配区域另记在每条诊断的 <code>auxiliary_roi_quad</code>。这避免把显示 ROI 的字节一致误解为辅助匹配没有改区域。模型不在这些设备图上训练，无文件名/人员特例；4480次历史划分都是已曝光的相关回归证据，不是独立泛化验证。</p>'
    text+='<p>v24对照、v25、v26均复制同一份完成注册图库；换版只改变模板 envelope magic 与算法元数据，生物特征 payload 不变，初始化时重建准备图库。每次查询重新读原图、定位、提取与匹配。查询计时包含本机 HTTP，排除拍摄、摆手、外网上传；启动和现场重新注册耗时另计，未宣称测到了 v26 现场注册速度。</p>'
    text+='<h2>新增分支逐张对照</h2>'+table(['分组','样本','真实身份','正确','v25秒','v26秒'],[
        [case,sample,new[case,sample]['identity'],new[case,sample]['correct'],f"{old[case,sample]['ms']/1000:.3f}",f"{new[case,sample]['ms']/1000:.3f}"] for case,sample in changed])
    if args.manifest:
        import cv2
        from PIL import Image,ImageDraw
        app=Path(__file__).resolve().parents[1];sys.path.insert(0,str(app))
        from biometric import load_algorithm
        from anchored_matcher import source_quad
        from pklnet_roi import normalize_roi_pixels
        algorithm=load_algorithm(app/'vendor/palmprint-recognition-python','FastCCQualityEvidence-v24-experimental')
        manifest={r['sample']:r for r in json.loads(args.manifest.read_text())}
        folder=args.output.parent/'roi-evidence';folder.mkdir(exist_ok=True)
        try:
            for case,sample in changed:
                row=manifest[sample];q=new[case,sample]
                with zipfile.ZipFile(app.parents[1]/row['archive']) as archive:value=archive.read(row['archive_member'])
                assert hashlib.sha256(value).hexdigest()==row['sha256']
                original=Image.open(io.BytesIO(value)).convert('RGB');native=cv2.cvtColor(np.asarray(original),cv2.COLOR_RGB2GRAY)
                primary=source_quad(np.asarray(q['diagnostics']['source_matrix']))
                alternate=np.asarray(q['diagnostics']['auxiliary_roi_quad'],np.float32)
                canvas=Image.new('RGB',(1200,650),'#162332');draw=ImageDraw.Draw(canvas)
                for i,(label,quad,color) in enumerate((('Original primary ROI',primary,'lime'),('Actual alternate ROI used',alternate,'orange'))):
                    overlay=original.copy();painter=ImageDraw.Draw(overlay)
                    points=[tuple(p) for p in quad];painter.line(points+points[:1],fill=color,width=max(3,original.width//400))
                    overlay.thumbnail((590,350));canvas.paste(overlay,(i*600,35))
                    raw=algorithm.geometry.getROIimg(native,quad)
                    pixels=normalize_roi_pixels(raw)
                    canvas.paste(Image.fromarray(pixels).resize((210,210)),(i*600+10,400))
                    draw.text((i*600+10,10),label,fill='white')
                draw.text((10,625),case+' '+sample,fill='white')
                path=folder/(case+'-'+sample+'.png');canvas.save(path)
                relative=path.relative_to(args.output.parent).as_posix()
                text+='<figure><img style="max-width:100%" src="'+html.escape(relative,quote=True)+'"><figcaption>'+html.escape(sample)+'：绿色为原主 ROI，橙色为实际辅助匹配 ROI；下方仅为显示进行1–99%灰度拉伸，模型使用原始灰度。</figcaption></figure>'
        finally:algorithm.close()
    text+='<h2>回归与流程检查</h2>'+table(['检查','结果'],[
        ['新增误认',len(regressions)],['非新增分支的身份/分数/第二名/状态/路径差异',len(differences)],
        ['全部显示主 ROI 与 v24 字节相同',roi_equal],['模拟确认/重复确认/取消/取消后确认',checks],
        ['源模板及原图不变',integrity],['供电标志',', '.join(power)],['本地完整测试','224 passed, 4 optional skips; obsolete API test excluded']])
    failures=[(k,q) for k,q in new.items() if not q['correct']]
    text+='<h2>保留的误认</h2>'+table(['分组','样本','真实身份','返回身份','秒','路径'],[
        [case,sample,q['identity'],q['result'].get('user_id'),f"{q['ms']/1000:.3f}",q['result'].get('recognition_route')] for (case,sample),q in failures])
    slow=sorted(new,key=lambda k:new[k]['ms'],reverse=True)[:10]
    text+='<h2>最长十次查询</h2>'+table(['分组','样本','正确','v25秒','v26秒','路径'],[
        [case,sample,new[case,sample]['correct'],f"{old[case,sample]['ms']/1000:.3f}",f"{new[case,sample]['ms']/1000:.3f}",new[case,sample]['result'].get('recognition_route')] for case,sample in slow])
    text+='<h2>仍未解决的最难图</h2><p>对 v25 最慢图的实际配准裁图记录显示：快速阶段约2.00/2.66秒出现的两块区域，CompNet均无可靠证据；约13.33秒后两块较好区域，真身份角距离约0.363，仍高于0.32门槛。没有为此降低门槛。固定 CLAHE 双侧预处理只额外覆盖一张原已在1.80秒内正确的图，未接入。完整存储窗口候选的离线筛查可额外覆盖6次，但最难图及四张误认仍未获救，且额外定位成本不属于本轮免费候选优化。</p>'
    text+='<p>未知人员拒识尚未校准，闭集兜底可能在证据不足时返回身份。七人数据也不足以证明40人容量或新会话泛化。预训练权重及作者源代码不随Git分发。<a href="../compnet-v25-pi-20261029/report.html">此前v25论文、对照及已否决实验</a>。</p></html>'
    if paired:
        rows=[]
        for case,sample in paired['selected']:
            trials=[t for t in paired['trials'] if t['case']==case and t['sample']==sample]
            def times(enabled,field,scale):return ', '.join(f'{t[field]/scale:.3f}' for t in trials if t['enabled']==enabled)
            rows.append([case,sample,times(False,'ms',1000),times(True,'ms',1000),
                times(False,'auxiliary_ms',1),times(True,'auxiliary_ms',1),all(t['correct'] for t in trials)])
        section='<h2>同一应用交替开关辅助 ROI</h2><p>机械选择全部新增三次提前返回，按关闭→开启→开启→关闭运行；关闭仅使用v25原始特征证据，模型和已加载v26图库相同，每次重算原图。这是三个查询的机制复核，不能当作全量限时率的重复测量。</p>'
        section+=table(['分组','样本','v25两次秒','v26两次秒','v25辅助阶段毫秒','v26辅助阶段毫秒','四次均正确'],rows)
        section+='<p>本轮供电标志：'+html.escape(', '.join(sorted({s['get_throttled'] for s in paired['power_samples']})))+'。完整全量P95/最大耗时没有因此被替换为这三张有利样本的数字。</p>'
        text=text.replace('</html>',section+'</html>')
    args.output.write_text(text,encoding='utf-8')
    print(json.dumps(dict(report=str(args.output),valid=valid,new_branch=len(changed),regressions=regressions,unchanged_path_differences=differences)))


if __name__=='__main__':main()
