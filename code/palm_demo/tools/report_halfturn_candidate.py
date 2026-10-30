"""Publish scalar-only completed candidate evidence and a private HTML report."""
import argparse
import csv
import html
import hashlib
import importlib.util
import json
from pathlib import Path

from report_raw_smpd import summarize,timing


def load(path):return json.loads(path.read_text(encoding='utf-8'))


def build(audit,regression,pilot):
    assert audit['complete'] and regression['complete'] and pilot['complete']
    assert regression.get('executed_matcher')=='FastCCCompNetAlternateROI-v26-experimental', (
        'Missing verified executed matcher: historical half-turn replay inherited v24 from the split protocol. '
        'Its top-level v26 label is insufficient; see MATCHER_PROVENANCE_CORRECTION_20261030.md.')
    assert all(run['startup'].get('actual_matcher')==regression['executed_matcher']
        for variant in regression['variants'].values() for run in variant['runs'])
    assert audit['originals_unchanged'] and regression['originals_unchanged']
    assert pilot['originals_unchanged'] and pilot['source_templates_unchanged']
    results={}
    ledgers=[]
    for name,variant in regression['variants'].items():
        rows=[q for run in variant['runs'] for q in run['queries']]
        assert len(rows)==168
        results[name]=dict(overall=summarize(rows),
            cases={run['case']:summarize(run['queries']) for run in variant['runs']},
            enrollment_count=sum(len(run['enrollments']) for run in variant['runs']),
            failed_enrollments=sum(e['http_status']!=200 for run in variant['runs'] for e in run['enrollments']),
            enrollment_timing=timing([e['ms'] for run in variant['runs'] for e in run['enrollments']]),
            immediate_queries=summarize([q for run in variant['runs'] for q in run['immediate_queries']]),
            startup_by_case={run['case']:run['startup'] for run in variant['runs']},
            payment_checks_complete=variant['summary']['payment_checks_complete'])
        for run in variant['runs']:
            for q in run['queries']:
                ledgers.append(dict(variant=name,case=run['case'],sample=q['sample'],identity=q['identity'],
                    correct=q['correct'],http_status=q['http_status'],ms=q['ms'],
                    **{field:q['result'].get(field) for field in ('status','user_id','score','second_score','recognition_route')}))
    public=dict(scope='Single development person, five fixed enrollment originals and five later frontal queries in the complete 76/77 eligible gallery. Not full-cohort validation.',
        registered_before=pilot['variants']['standard']['registered'],registered_after=pilot['variants']['candidate']['registered'],
        standard_enrollment=pilot['variants']['standard']['enrollment'],candidate_enrollment=pilot['variants']['candidate']['enrollment'],
        standard_enrollment_ms=pilot['variants']['standard']['http_trace'][0]['ms'],
        candidate_enrollment_ms=pilot['variants']['candidate']['http_trace'][0]['ms'],
        query_summary=summarize(pilot['query_results']),pilot_pass=pilot['pilot_pass'],
        query_enrollment_byte_overlap=pilot['query_enrollment_byte_overlap'],
        payment_checks=pilot['variants']['candidate']['payment_checks'],payment_transactions=pilot['variants']['candidate']['payment_transactions'])
    captures=[regression['variants'][name]['localizations'] for name in ('standard','candidate')]
    return dict(complete=True,standard_tag='standard-device-20261030',candidate='out-of-bounds-halfturn-recovery-pilot-v1',
        candidate_sha256=audit['candidate_sha256'],evaluator_sha256=regression['evaluator_sha256'],
        device_geometry=audit['device_summary'],device_http=results,
        exact_device_decisions=regression['exact_decisions'],lost_correct=regression['lost_correct'],
        full_capture_roi_hashes_equal=(len(captures[0])==len(captures[1]) and all(
            a['sample']==b['sample'] and a['roi_sha256']==b['roi_sha256'] for a,b in zip(*captures))),
        original_captures_per_variant=[len(v) for v in captures],
        genuine_device_corrections=regression['genuine_corrections'],device_regression_pass=regression['regression_pass'],
        public_mechanism_pilot=public,
        candidate_retained_for_further_evaluation=bool(regression['regression_pass'] and pilot['pilot_pass']),
        promoted_to_standard=False,
        limits=['Frozen standard is unchanged; this remains an experiment.',
            'ROI recovery is not identity recognition and does not establish anatomical ground truth.',
            'Original-device cohort is exposed development data; no independent-device generalization claim.',
            'Public pilot is one development person and five same-view queries; no full-release or reserved-person success claim.',
            'Windows CPU inference overlapped the full public baseline. No exclusive-CPU or Pi speed improvement claim.',
            'This failure-only recovery does not repair the existing valid-ROI mistakes or prove that long search tails are solved.',
            'Pi regression is still required before any device performance/promotion claim.']),ledgers


def render(summary):
    def number(value):return '—' if value is None else f'{value/1000:.3f}'
    rows=[]
    for scope in ('overall','new-camera-original','new-camera-reverse','old-camera-original','old-camera-reverse'):
        for name,value in summary['device_http'].items():
            s=value['overall'] if scope=='overall' else value['cases'][scope];t=s['all_timing']
            cells=[scope,name,s['total'],s['correct'],s['wrong_identity_accepted'],s['rejected'],s['processing_failure'],
                s['correct_within_2500'],number(t['p50_ms']),number(t['p95_ms']),number(t['max_ms'])]
            rows.append('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in cells)+'</tr>')
    public=summary['public_mechanism_pilot'];p=public['query_summary'];d=summary['device_geometry']
    return f'''<!doctype html><html lang="zh"><meta charset="utf-8"><title>ROI 边界恢复候选实验</title>
<style>body{{font:16px/1.6 system-ui;max-width:1250px;margin:40px auto;padding:0 24px;background:#101722;color:#e9eef6}}h1,h2{{color:#83cbff}}table{{border-collapse:collapse;width:100%;font-size:14px}}td,th{{padding:7px;border:1px solid #42516a}}code{{color:#ffd49a}}a{{color:#83cbff}}</style>
<h1>ROI 越界时的一次反向定位恢复</h1><p><b>已完成电脑机制验证与原数据回归；仍为实验候选，标准版未改。</b></p>
<p>标准标签 <code>standard-device-20261030</code>。有效 ROI 沿用原结果；只有越界时尝试一次 180° 定位，使用原有几何与重叠检查。没有身份特例、模型训练或识别阈值修改。</p>
<h2>原设备 169 张图 / 四种划分 168 次查询</h2><p>169 张的原 ROI 均有效；候选触发重试 {d['retries']} 次，原有效 ROI 改变 {d['changed_valid']} 张。下表两种版本各完整重新注册和识别。逐查询决策完全相同 {summary['exact_device_decisions']}/168；原本正确损失 {summary['lost_correct']}，真正由错变对 {summary['genuine_device_corrections']}。</p>
<table><tr><th>范围</th><th>版本</th><th>查询</th><th>正确</th><th>误认</th><th>拒认</th><th>处理失败</th><th>≤2.5秒正确</th><th>P50秒</th><th>P95秒</th><th>最长秒</th></tr>{''.join(rows)}</table>
<p>这些是 Windows 原图→ROI→注册/识别→隔离模拟支付流程。电脑同期运行公开集全量基线；耗时用于完整记录，不作为独占 CPU 或 Pi 加速证据。Pi 接上后仍须实测。</p>
<p>两版各重新执行 34 个五帧注册请求：标准 P50 {number(summary['device_http']['standard']['enrollment_timing']['p50_ms'])} 秒，候选 P50 {number(summary['device_http']['candidate']['enrollment_timing']['p50_ms'])} 秒，包含各阶段图库准备。启动和即时查询另列于 JSON，不与单张查询混算。</p>
<h2>公开集指缝可见的单人机制验证</h2><p>008 原定 F0–F4 中 F3 越界，标准版注册状态：{public['registered_before']}；候选注册状态：{public['registered_after']}。保留原全部 76 个成功身份，候选成功后图库为 77 个身份。没有替换注册图或分小图库。</p>
<p>候选这次离线接入全部已有模板、首次构建完整 77 身份图库的录入请求用了 {number(public['candidate_enrollment_ms'])} 秒；这是五帧处理及整库准备，不能当成正常已预热图库的单人追加注册或单张查询时间。</p>
<p>后续 F5–F9 共 5 张：正确 {p['correct']}，误认 {p['wrong_identity_accepted']}，拒认 {p['rejected']}，处理失败 {p['processing_failure']}。注册/查询字节重叠 {public['query_enrollment_byte_overlap']}。机制验证通过：{public['pilot_pass']}。</p>
<p><img src="recovered-boundary-example.jpg" alt="同一原图上的原始越界框和恢复框，以及校验过的实际ROI像素" style="max-width:100%"></p>
<p>只验证一个已用于开发分析的人、五张正面查询，不能当成公开集全量或留出人员准确率。修复注册覆盖不等于解决其他有效 ROI 误认，也没有证明最慢尾部已解决。</p>
<h2>后续</h2><p>标准版继续冻结；继续看适用范围内的公开集失败。候选源代码与接受规则冻结后才做留出验证，并在树莓派上回归原数据和速度。</p></html>'''


def make_example(audit,source,output):
    """Display only original pixels; verify reconstructed crop hashes first."""
    import cv2
    import numpy as np
    from PIL import Image,ImageDraw,ImageOps
    selected=next(r for r in audit['public_controls'] if r['trace']['recovered'])
    row=next(r for r in load(source/'prepared/manifest.json') if r['sample']==selected['sample'])
    data=Path(row['original']).read_bytes();assert hashlib.sha256(data).hexdigest()==row['sha256']
    with Image.open(row['original']) as raw:full=ImageOps.exif_transpose(raw).convert('RGB')
    geometry_path=Path(__file__).resolve().parents[2]/'pklnet/roiExtractor.py'
    spec=importlib.util.spec_from_file_location('report_frozen_roi_geometry',geometry_path)
    geometry=importlib.util.module_from_spec(spec);spec.loader.exec_module(geometry)
    canvas=Image.new('RGB',(1200,570),(20,25,34))
    cases=[('Original: out of bounds',row['roi_quad'],selected['primary_roi_sha256'],(255,75,75)),
           ('Recovered: geometry only',selected['trace']['mapped_quad'],selected['candidate_roi_sha256'],(70,230,100))]
    for i,(label,quad,digest,color) in enumerate(cases):
        quad=np.asarray(quad,np.float32)
        crop=geometry.getROIimg(cv2.cvtColor(np.asarray(full),cv2.COLOR_RGB2BGR),quad,side=128,ratio=1.)
        assert hashlib.sha256(crop.tobytes()).hexdigest()==digest,'Illustration does not reproduce actual audit ROI'
        image=full.copy();scale=min(390/full.width,520/full.height);image.thumbnail((390,520))
        points=[(float(x)*scale,float(y)*scale) for x,y in quad];ImageDraw.Draw(image).line(points+[points[0]],fill=color,width=3)
        x=i*600;canvas.paste(image,(x,0));canvas.paste(Image.fromarray(crop).convert('RGB').resize((190,190)),(x+400,0))
        draw=ImageDraw.Draw(canvas);draw.text((x+5,535),row['sample']+' | '+label,fill=color)
    canvas.save(output/'recovered-boundary-example.jpg',quality=90)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('audit','regression','pilot','scalar_output'):p.add_argument(name,type=Path)
    p.add_argument('--smpd-root',required=True,type=Path)
    a=p.parse_args();audit=load(a.audit/'results.json');summary,ledgers=build(audit,load(a.regression/'results.json'),load(a.pilot/'results.json'))
    a.scalar_output.mkdir(exist_ok=True,parents=True)
    (a.scalar_output/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    with (a.scalar_output/'device-query-ledger.csv').open('w',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(ledgers[0]));writer.writeheader();writer.writerows(ledgers)
    (a.regression/'report.html').write_text(render(summary),encoding='utf-8')
    make_example(audit,a.smpd_root,a.regression)
    print(json.dumps({k:summary[k] for k in ('exact_device_decisions','lost_correct','genuine_device_corrections','device_regression_pass','candidate_retained_for_further_evaluation')}))


if __name__=='__main__':main()
