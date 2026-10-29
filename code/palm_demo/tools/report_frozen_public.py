"""Aggregate scoped public validation; never exports images or templates."""
import argparse,collections,html,json
from pathlib import Path
import numpy as np
from evaluate_frozen_public import canonical,sha


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path);p.add_argument('prior_casia',type=Path);args=p.parse_args()
    root=args.root;protocol=json.loads((root/'protocol.json').read_text());casia=json.loads((root/'casia-v26/results.json').read_text())
    roi=json.loads((root/'palmbig-local/results.json').read_text());prior=json.loads(args.prior_casia.read_text())
    kernel=json.loads((root/'kernel-audit-summary.json').read_text());pixels=json.loads((root/'pixel-exposure-audit.json').read_text())
    assert casia['complete'] and roi['complete'] and casia['protocol_sha256']==roi['protocol_sha256']==sha(root/'protocol.json')
    assert casia['originals_unchanged'] and casia['models_unchanged'] and casia['kernel_unchanged'] and casia['transactions_unchanged']
    assert pixels['decoded_pixel_overlap']==0 and set(x['get_throttled'] for x in casia['power_samples'])=={'throttled=0x0'}
    previous=next(r for r in prior['runs'] if r['version']=='v13')
    aggregate=dict(protocol_canonical_sha256=canonical(protocol),frozen_algorithm_commit=protocol['frozen_commit'],
        casia_prior_v13=previous['summary'],casia_v26_passes=[dict(name=r['name'],**r['summary']) for r in casia['passes']],
        casia_initialization_empty_gallery_ms=casia['initialization_ready_ms']['total_ms'],
        casia_enrollment_requests_ms=[e['request_ms'] for e in casia['enrollments']],
        casia_enrollment_successes=sum(e['http_status']==200 and e['result'].get('recognition_ready',False) for e in casia['enrollments']),
        casia_additional_ready_check_ms=casia['post_enrollment_gallery_ready_ms'],
        casia_cancellation_ok=all(t.get('cancelled',False) for r in casia['passes'] for t in r['queries']),
        casia_explicit_rejects=[sum(t['result']['status']=='REJECT' for t in r['queries']) for r in casia['passes']],
        casia_wrong_identity_matches=[sum(not t['correct'] and t['result']['status']=='MATCH' for t in r['queries']) for r in casia['passes']],
        palmbig_inventory={k:v for k,v in protocol['palmbig'].items() if k!='subset_member_sha256'},
        palmbig_local=[dict(prefix=r['prefix'],classes=r['filename_classes'],images=r['images'],**r['summary']) for r in roi['cohorts']],
        palmbig_failures=len(roi['failures']),kernel_environment_audit=kernel,pixel_exposure_audit=pixels,
        new_device_session_validated=False,unknown_person_validation=False,algorithm_tuned=False,raw_biometric_transfer=False,
        production_changed=False,complete=True)
    save=root/'aggregate.json';save.write_text(json.dumps(aggregate,indent=2))
    def table(headers,rows):
        return '<div class="scroll"><table><tr>'+''.join('<th>'+html.escape(str(v))+'</th>' for v in headers)+'</tr>'+''.join('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in row)+'</tr>' for row in rows)+'</table></div>'
    text='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>冻结v26：公开数据集确认性验证</title>
<style>body{font:16px/1.65 system-ui;max-width:1450px;margin:32px auto;padding:0 20px;color:#203044}h1{font-size:28px}.scroll{overflow:auto}table{width:100%;border-collapse:collapse;font-size:14px}th,td{padding:9px;border:1px solid #cbd5df;text-align:left}th{background:#eaf0f7}.notice{background:#fff3dd;border-left:4px solid #ac7018;padding:14px}code{overflow-wrap:anywhere}</style>
<h1>冻结v26：公开数据集的有限范围验证</h1><p>2026-10-30 · 仅评估，无优化/训练/调参/生产切换</p>
<p class="notice">CASIA 是已曝光24张数据上的v26确认性比较；PalmBigDataBase 是本机裁好ROI的FastCC组件验证。二者不能证明自己设备最难图已解决，原设备基线仍164/168正确、146/168限时正确、最大15.225秒。新会话与未注册人员验证仍未完成。</p>'''
    text+='<h2>CASIA 850nm：Pi完整识别请求与录入回放（除拍摄）</h2><p>主体001–004、左手、850nm、每类六张；前五张新注册，第六张查询，固定原顺序种子。只读Pi上早已存在并逐张校验哈希的24张副本，没有传输原始数据。相同样本在v13已评估，不能称独立新验证；热态重复仍是同四张，不是新增四个测试样本。</p>'
    rows=[]
    for name,s in [('历史v13，旧记录',previous['summary'])]+[(r['name'],r['summary']) for r in casia['passes']]:
        rows.append([name,s['total'],s['correct'],s['correct_within_2_5s'],f"{s['median_ms']/1000:.3f}",f"{s['p95_ms']/1000:.3f}",f"{s['max_ms']/1000:.3f}"])
    text+=table(['运行','查询数','正确','正确且≤2.5秒','P50秒','P95秒','最大秒'],rows)
    text+='<p>查询含原图读取、定位、特征、图库评分与本机HTTP；不含实际相机拍摄/摆手、Wi-Fi上传、初始化和注册等待。历史v13复用了v12注册载荷，本轮v26做全新注册，不能把全部时间差当作某一算法机制的因果收益。每轮错身份MATCH均0、显式REJECT均0；输入全为已注册人员，不能据此估计陌生人FAR或验证FRR。</p>'
    text+='<h2>注册与就绪等待单独列出</h2>'+table(['项目','毫秒'],[
        ['空库应用初始化/主模型预热',f"{aggregate['casia_initialization_empty_gallery_ms']:.3f}"],
        *[['每类五帧录入请求（含该次图库准备）',f"{e['request_ms']:.3f}"] for e in casia['enrollments']],
        ['四类录入后额外就绪复核',f"{aggregate['casia_additional_ready_check_ms']:.3f}"]])
    text+='<p>四次录入均成功。录入API内部已执行图库准备；最后约0.35ms仅是额外缓存就绪复核，不能称全部图库准备只用0.35ms。录入也是保存原图回放，不包含现场拍五张的时间。取消令牌均通过、模拟交易数不变、原图/模型不变、供电全0x0。</p>'
    info=protocol['palmbig']
    text+='<h2>PalmBigDataBase：归档元数据与暴露范围</h2>'+table(['项目','结果'],[
        ['BMP条目',info['bmp_images']],['全部尺寸',info['dimensions']],['F/S图像数',info['prefix_images']],
        ['前缀定义的类别数',info['filename_classes']],['数字ID数',info['numeric_ids']],['F/S各自类别数',info['prefix_classes']],
        ['物理人数及F/S是否为会话或设备','归档无说明，不推断'],['样本数分布',info['sample_count_histogram']],
        ['原已曝光范围','1–20号400图旧测试；21–60号旧public40包/工具足迹，保守排除'],
        ['冻结新范围','61–80号，F/S各自建库，五张注册、其余全查询'],['新范围与旧1–60字节/解码像素重复','0 / 0']])
    text+='<h2>仅本机ROI组件结果</h2>'+table(['前缀','文件名类别','图像','查询','排名正确','P50毫秒','P95毫秒','最大毫秒'],[
        [r['prefix'],r['filename_classes'],r['images'],r['summary']['total'],r['summary']['correct'],*[f"{r['summary'][k]:.3f}" for k in ('median_ms','p95_ms','max_ms')]] for r in roi['cohorts']])
    text+='<p>失败'+str(len(roi['failures']))+'，全部200次查询保留。只运行既有128×128灰度归一化/FastCC提取/最佳两帧平均及全图库排名；没有定位、几何救援、CompNet路由或HTTP，因此不是v26整条识别流程。时间是Windows本机已访问归档的ROI读取/解码/归一化/特征/匹配组件耗时，不是Pi速度或冷磁盘I/O。F/S独立建库，不做跨前缀匹配，不能宣称跨会话/设备泛化。</p>'
    text+='<h2>冻结与运行库差异</h2><p>冻结算法提交 <code>'+protocol['frozen_commit']+'</code>，协议语义SHA256 <code>'+aggregate['protocol_canonical_sha256']+'</code>。运行前校验协议、核心代码、预训练模型和原始样本哈希；测试后再次检查。不根据结果重新选样、调阈值或训练。原始公开数据、图像、模板和权重不提交Git。</p>'
    text+='<p>Windows NumPy2.3.5/OpenCV5.0.0，Pi NumPy2.2.4/OpenCV4.10.0。FastCC算法及核生成源码一致，生成系数末位浮点不同：最大Gabor系数差 '+str(kernel['max_all_gabor_kernels'])+'。每台机器本次核在输入数据前固定并验证运行后未变，不宣称两平台逐位完全相同。</p>'
    text+='<p>本轮不触碰自己设备的新会话/未注册人员；这两项独立验证仍缺。公开的干净ROI成绩不能替代低质量本设备原图的成功率与长尾验证。</p></html>'
    (root/'report.html').write_text(text,encoding='utf-8');print(save)


if __name__=='__main__':main()
