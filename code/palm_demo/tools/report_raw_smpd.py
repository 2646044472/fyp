"""Summarize the frozen full raw-image run without importing its algorithm.

Private photographs stay in runtime. Only scalar summaries/ledgers are exported.
Incomplete runs require --partial and are prominently labeled as incomplete.
"""
import argparse
import collections
import csv
import hashlib
import html
import json
import sys
from pathlib import Path

import numpy as np


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def outcome(query):
    result = query['result']
    if query['http_status'] != 200:
        return 'processing_failure'
    if result.get('status') != 'MATCH':
        return 'rejected'
    if result.get('user_id') != query['identity'].replace(':', '-'):
        return 'wrong_identity_accepted'
    score, second = result.get('score'), result.get('second_score')
    if score is None or (second is not None and not score < second):
        return 'true_identity_nonunique'
    return 'correct'


def timing(values):
    if not values:
        return dict(n=0, p50_ms=None, p95_ms=None, max_ms=None)
    return dict(n=len(values), p50_ms=float(np.median(values)),
                p95_ms=float(np.percentile(values, 95)), max_ms=max(values))


def summarize(queries):
    counts = collections.Counter(outcome(q) for q in queries)
    result = {name: counts[name] for name in ('correct', 'wrong_identity_accepted',
              'true_identity_nonunique', 'rejected', 'processing_failure')}
    result.update(total=len(queries), correct_within_2500=sum(
        outcome(q) == 'correct' and q['ms'] <= 2500 for q in queries))
    assert sum(counts.values()) == result['total']
    result['accuracy'] = result['correct'] / len(queries) if queries else None
    result['all_timing'] = timing([q['ms'] for q in queries])
    result['correct_timing'] = timing([q['ms'] for q in queries if outcome(q) == 'correct'])
    result['routes'] = dict(collections.Counter(q['result'].get('recognition_route', 'none') for q in queries))
    return result


def duplicate_audit(rows, queries):
    groups = collections.defaultdict(list)
    for row in rows:
        groups[row['sha256']].append(row)
    enrollment_hashes = {r['sha256'] for r in rows if r['enrollment']}
    query_by_sample = {q['sample']: q for q in queries}
    first_queries = []; independent_queries = []; inconsistent_decisions = []
    for digest, members in sorted(groups.items()):
        available = sorted((r for r in members if r['sample'] in query_by_sample), key=lambda r: r['sample'])
        if available:
            first_queries.append(query_by_sample[available[0]['sample']])
            if digest not in enrollment_hashes:
                independent_queries.append(query_by_sample[available[0]['sample']])
            signatures={(q['http_status'],q['result'].get('status'),q['result'].get('user_id'),
                         q['result'].get('score'),q['result'].get('second_score'))
                for q in (query_by_sample[r['sample']] for r in available)}
            if len(signatures)>1:
                inconsistent_decisions.append(dict(sha256=digest,samples=[r['sample'] for r in available]))
    return dict(original_files=len(rows), unique_byte_contents=len(groups),
        redundant_files=len(rows)-len(groups), duplicate_groups=sum(len(v)>1 for v in groups.values()),
        conflicting_identity_groups=[dict(sha256=h, samples=[r['sample'] for r in v])
            for h,v in groups.items() if len({r['identity'] for r in v})>1],
        query_files_overlapping_enrollment=sum(not r['enrollment'] and r['sha256'] in enrollment_hashes for r in rows),
        unique_query_byte_contents=len({r['sha256'] for r in rows if not r['enrollment']}),
        unique_content_diagnostic=summarize(first_queries),
        unique_content_without_enrollment_overlap=summarize(independent_queries),
        repeated_content_decision_conflicts=inconsistent_decisions,
        diagnostic_rule='One query per byte hash, lexicographically first sample, independent of its outcome. Primary file-level results unchanged. Pixel/reencoded duplicates not audited.')


def frozen_policy_shadow(queries):
    """Evaluate just the pre-SMPD .02 policy; never fit or sweep a limit here."""
    app=Path(__file__).resolve().parents[1];sys.path.insert(0,str(app))
    from acceptance_policy import AcceptancePolicy
    path=app/'docs/protocols/DEVELOPMENT_REJECTION_POLICY_20261030.json'
    document=load(path)
    assert document==dict(version=1,name='development-margin-0.02-v1',profiles=dict(
        fastcc=dict(max_distance=1.,min_margin=.02),compnet=dict(max_distance=.32,min_margin=.08),
        quality=dict(max_distance=.32,min_margin=.08))), 'Pre-existing policy changed'
    policy=AcceptancePolicy(document);shadow=[];lost=[];blocked=[]
    for q in queries:
        copy=dict(q,result=dict(q['result']));result=copy['result']
        if q['http_status']==200 and result.get('status')=='MATCH':
            rejection=policy.rejection(result.get('score'),result.get('second_score'),result.get('recognition_route'))
            if rejection:
                if outcome(q)=='correct':lost.append(q['sample'])
                elif outcome(q)=='wrong_identity_accepted':blocked.append(q['sample'])
                result.update(status=rejection[0],reason=rejection[1]);result.pop('user_id',None)
        shadow.append(copy)
    result=summarize(shadow)
    result.update(lost_previously_correct=lost,wrong_identities_blocked=blocked,
        genuine_wrong_to_correct=0,policy=document,policy_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        policy_code_sha256=hashlib.sha256((app/'acceptance_policy.py').read_bytes()).hexdigest(),
        scope='Saved-score shadow only of pre-existing .02 policy; no new inference, threshold fitting, speed gain or production activation. Query times reused unchanged.')
    return result


def build_summary(root, partial=False):
    protocol = load(root/'protocol.json')
    rows = load(root/'prepared/manifest.json')
    result_bytes=(root/'evaluation/results.json').read_bytes()
    results = json.loads(result_bytes)
    queries = results['queries']
    assert len(rows) == protocol['images'] == 3677
    assert len({r['sample'] for r in rows}) == len(rows)
    expected = {r['sample'] for r in rows if not r['enrollment']}
    assert len({q['sample'] for q in queries}) == len(queries)
    assert {q['sample'] for q in queries} <= expected
    if not partial:
        assert results['complete'] and len(queries) == len(expected) == 3217, 'Full recognition incomplete'
        assert results['originals_unchanged'] and results['transactions_unchanged']
    for q in queries:
        assert q['correct'] == (outcome(q) == 'correct'), q['sample']
    enrolled = [e for e in results['enrollments'] if e['registered']]
    summary = dict(complete=results['complete'], expected_queries=len(expected), completed_queries=len(queries),
        original_images=len(rows), original_people=protocol['people'], selected_enrollment_images=460,
        enrollment_feature_ok=sum(bool(r.get('enrollment_feature_ok')) for r in rows),
        gallery_identities=results['actual_gallery_identities'], registration_failures=len(results['enrollments'])-len(enrolled),
        roi_geometry_pass=sum(r['roi_valid'] for r in rows), roi_geometry_fail=sum(not r['roi_valid'] for r in rows),
        roi_error_counts=dict(collections.Counter(r.get('roi_error', 'unspecified') for r in rows if not r['roi_valid'])),
        overall=summarize(queries), truth_enrolled=summarize([q for q in queries if q['truth_enrolled']]),
        truth_unregistered=summarize([q for q in queries if not q['truth_enrolled']]),
        per_view={c:summarize([q for q in queries if q['condition']==c]) for c in ('F','RF','P','RP')},
        per_subject={identity:summarize([q for q in queries if q['identity']==identity])
            for identity in sorted({r['identity'] for r in rows})},
        per_view_originals={c:dict(total=sum(r['condition']==c for r in rows), roi_geometry_fail=sum(
            r['condition']==c and not r['roi_valid'] for r in rows)) for c in ('F','RF','P','RP')},
        duplicates=duplicate_audit(rows, queries), startup_and_gallery_ready_ms=results['startup_and_gallery_ready_ms'],
        frozen_preexisting_policy_shadow=frozen_policy_shadow(queries),
        concurrent_localization_diagnostics=load(root/'localization-diagnostic-concurrency.json')
            if (root/'localization-diagnostic-concurrency.json').exists() else [],
        resume_epochs=results.get('resume_epochs',[]),
        interruption_evidence=load(root/'interruption-detected-20261030.json')
            if (root/'interruption-detected-20261030.json').exists() else None,
        original_integrity=results.get('originals_unchanged'), transactions_unchanged=results.get('transactions_unchanged'),
        archive_sha256=results['archive_sha256'], protocol_sha256=results['protocol_sha256'],
        results_sha256=hashlib.sha256(result_bytes).hexdigest(),
        algorithm=protocol['matcher'], timing_scope=protocol['timing_scope'],
        limitations=['Windows timings and increased memory allowance do not establish Pi performance.',
            'No anatomical ROI ground truth. Geometric validity is not anatomical ROI accuracy.',
            'Nominal 110-person/4400-image collection is not fully public: actual release 92/3677.',
            'Dark backgrounds and pose variation do not cover all demo capture conditions.',
            'Byte duplicates disclosed; perceptual/pixel duplicates not audited.',
            'Localizer original training exposure unknown; no claim of fully blind validation.',
            'All selected enrollment failures retained; all remaining query files in primary denominator.',
            'No new thresholds, training, test-driven enrollment replacements or failure exclusions.'])
    assert summary['gallery_identities'] == len(enrolled)
    return summary, rows, queries


def write_scalars(destination, summary, rows, queries):
    destination.mkdir(exist_ok=True, parents=True)
    (destination/'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    manifest = {r['sample']:r for r in rows}
    with (destination/'query-ledger.csv').open('w', newline='', encoding='utf-8') as stream:
        fields = ['sample','identity','condition','sha256','truth_enrolled','roi_audit_valid','outcome',
                  'http_status','ms','user_id','score','second_score','recognition_route','duplicates_enrollment']
        writer = csv.DictWriter(stream, fieldnames=fields); writer.writeheader()
        for q in queries:
            row = {k:q.get(k) for k in fields}
            row.update({k:q['result'].get(k) for k in ('user_id','score','second_score','recognition_route')})
            row.update(sha256=manifest[q['sample']]['sha256'], outcome=outcome(q)); writer.writerow(row)
    with (destination/'original-ledger.csv').open('w', newline='', encoding='utf-8') as stream:
        fields=['sample','identity','condition','index','sha256','bytes','enrollment','roi_valid','roi_error','enrollment_feature_ok']
        writer=csv.DictWriter(stream,fieldnames=fields); writer.writeheader()
        writer.writerows({k:r.get(k) for k in fields} for r in rows)


def make_examples(root, rows, queries):
    from PIL import Image, ImageDraw, ImageOps
    by_sample = {r['sample']:r for r in rows}; selected = []; seen = set()
    # Illustrative fixed ordering within each category; never used to score/filter.
    buckets = [('geometry_failure', [r for r in rows if not r['roi_valid']]),
        ('wrong_identity', [by_sample[q['sample']] for q in queries if outcome(q)=='wrong_identity_accepted']),
        ('rejected', [by_sample[q['sample']] for q in queries if outcome(q)=='rejected'])]
    buckets += [(c, [r for r in rows if r['condition']==c and r['roi_valid']]) for c in ('F','RF','P','RP')]
    for category, candidates in buckets:
        count=0
        for r in sorted(candidates,key=lambda r:r['sample']):
            if r['sha256'] in seen: continue
            seen.add(r['sha256']); selected.append((category,r)); count+=1
            if count==3:break
    folder=root/'report-images';folder.mkdir(exist_ok=True)
    cards=[]
    for category,r in selected:
        with Image.open(r['original']) as encoded: image=ImageOps.exif_transpose(encoded).convert('RGB')
        scale=min(440/image.width,300/image.height);image.thumbnail((440,300));draw=ImageDraw.Draw(image)
        quad=r.get('roi_quad')
        if quad:
            points=[(float(p[0])*scale,float(p[1])*scale) for p in quad]
            draw.line(points+[points[0]],fill=(80,230,100) if r['roi_valid'] else (255,70,70),width=3)
        canvas=Image.new('RGB',(600,330),(20,25,34));canvas.paste(image,(0,0))
        roi_path=Path(r['original']).parent.parent/'prepared/rois'/(r['sample']+'.png')
        if roi_path.exists():
            with Image.open(roi_path) as roi:canvas.paste(roi.convert('RGB').resize((150,150)),(445,0))
        draw=ImageDraw.Draw(canvas);draw.text((8,307),r['sample']+' | '+category,fill='white')
        path=folder/(r['sample']+'.jpg');canvas.save(path,quality=88)
        cards.append(f'<figure><img src="report-images/{path.name}" loading="lazy"><figcaption>{html.escape(r["sample"])} — {html.escape(category)}<br>{html.escape(str(r.get("roi_error") or "Geometry pass; anatomical correctness unverified"))}</figcaption></figure>')
    return ''.join(cards)


def render_html(root, summary, rows, queries):
    labels={'F':'正面','RF':'旋转正面','P':'透视','RP':'旋转透视'}
    def cells(name, result):
        t=result['all_timing']; seconds=lambda v:'—' if v is None else f'{v/1000:.2f}'
        return '<tr>'+''.join(f'<td>{html.escape(str(v))}</td>' for v in (name,result['total'],result['correct'],
            result['wrong_identity_accepted'],result['true_identity_nonunique'],result['rejected'],result['processing_failure'],
            result['correct_within_2500'],seconds(t['p50_ms']),seconds(t['p95_ms']),seconds(t['max_ms'])))+'</tr>'
    table=''.join(cells(n,s) for n,s in [('全部',summary['overall']),('真身份注册成功',summary['truth_enrolled']),
        ('真身份未注册',summary['truth_unregistered'])]+[(labels[c],summary['per_view'][c]) for c in labels])
    state='全量完成' if summary['complete'] else '运行中：以下为中间结果，不能代表全量'
    body=f'''<!doctype html><html lang="zh"><meta charset="utf-8"><title>SMPD 原图全流程实验</title>
<style>body{{font:16px/1.6 system-ui;max-width:1250px;margin:40px auto;padding:0 24px;background:#101722;color:#e9eef6}}h1,h2{{color:#83cbff}}table{{border-collapse:collapse;width:100%;font-size:14px}}td,th{{padding:8px;border:1px solid #42516a}}.grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}}figure{{margin:0;background:#1c2738;padding:10px}}img{{width:100%}}figcaption{{font-size:13px}}pre{{white-space:pre-wrap}}a{{color:#83cbff}}</style>
<h1>SMPD：原图 → ROI → 特征 → 同库识别</h1><p><b>{state}</b> · {len(queries)}/3217 次查询 · Windows 电脑测试</p>
<p>作者公开 ZIP 实际有 92 人 / 3,677 张，{summary['duplicates']['unique_byte_contents']} 个不同字节内容。固定 F0–F4 注册，剩余全部查询。注册成功 {summary['gallery_identities']}/92 人；失败 {summary['registration_failures']} 人的查询也留在总分母。单一完整图库，不分小组。</p>
<p>ROI 几何检查失败 {summary['roi_geometry_fail']}/3677。没有解剖标注，几何通过率不能当 ROI 准确率。全图库启动准备 {summary['startup_and_gallery_ready_ms']/1000:.2f} 秒，单独计量。</p>
<p>优化范围按用户要求收窄到参考指缝可见的图片。没有全量指缝可见性标注，以下全量统计含定位前提不满足的原图；不能直接当成“指缝可见条件下”的性能。</p>
<table><tr><th>范围</th><th>查询</th><th>正确</th><th>错身份接受</th><th>真身份但非唯一</th><th>拒认</th><th>处理失败</th><th>≤2.5秒正确</th><th>P50秒</th><th>P95秒</th><th>最长秒</th></tr>{table}</table>
<p>正确必须是唯一正确身份；拒认、ROI/特征失败都不算正确。耗时包含原图读取、校验、EXIF 解码、ROI、特征、匹配及本机 HTTP；不含拍摄/外部上传。电脑扩大了内存容量，不能据此声称 Pi 的速度或人数容量。</p>
<p>电脑同期运行了开发定位诊断及原设备回归。重叠查询范围保存在 summary.json 的 concurrent_localization_diagnostics 字段；这些查询保留统计。没有独占 CPU 计时或成对加速结论。</p>
<h2>已有拒认机制的迁移检查</h2><p>只检查下载 SMPD 前已有的 .02 示例策略，不扫描新阈值。保存分数上的影子结果：正确 {summary['frozen_preexisting_policy_shadow']['correct']}、错误接受 {summary['frozen_preexisting_policy_shadow']['wrong_identity_accepted']}、拒认 {summary['frozen_preexisting_policy_shadow']['rejected']}；损失原本正确 {len(summary['frozen_preexisting_policy_shadow']['lost_previously_correct'])} 张，真正由错变对 0 张。这不是新一轮 HTTP 或速度改善，未启用到基线。</p>
<h2>重复与完整性</h2><pre>{html.escape(json.dumps({k:v for k,v in summary['duplicates'].items() if k!='unique_content_diagnostic'},indent=2,ensure_ascii=False))}</pre>
<p>原图最终校验：{summary['original_integrity']}；交易记录保持不变：{summary['transactions_unchanged']}。全量基线参数冻结；本数据集未用于训练或阈值拟合。局部定位器原训练暴露未知。</p>
<h2>原图与 ROI 示例</h2><p>按类别与文件名固定选取，重复字节只展示一次。绿框表示几何检查通过，红框表示失败；框是否位于正确解剖区域仍需人工判断。示例只用于看图，不改变任何分母。</p><div class="grid">{make_examples(root,rows,queries)}</div>
<h2>来源与边界</h2><p><a href="https://www.kaggle.com/datasets/mahdieizadpanah/sapienza-university-mobile-palmprint-databasesmpd">作者 SMPD 发布</a> · <a href="https://doi.org/10.1504/IJGUC.2019.102016">2019 数据论文</a>。论文名义 110 人 / 4,400 张；实际下载缺少 18 人及另外 3 帧，不能宣称测了名义完整集。暗背景、调过拍摄距离，不覆盖所有现场质量问题。</p></html>'''
    (root/'report.html').write_text(body,encoding='utf-8')


def write_markdown(destination, summary):
    state='COMPLETE' if summary['complete'] else 'INCOMPLETE — preliminary only'
    lines=[f'# SMPD full original-image evaluation — {state}', '',
        f"Processed original inventory: {summary['original_images']} / 92 right palms. "
        f"Queries completed: {summary['completed_queries']} / {summary['expected_queries']}.", '',
        f"Fixed enrollment F0..F4: {summary['enrollment_feature_ok']}/460 feature captures succeeded. "
        f"Complete five-frame identities registered together: {summary['gallery_identities']}/92. "
        'No replacement frames. Queries of unregistered true identities stay in the overall denominator.', '',
        '| Scope | N | Correct | Wrong identity accepted | True-ID nonunique | Rejected | Processing failure | Correct ≤2.5s | P50 s | P95 s | Max s |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    scopes=[('Overall',summary['overall']),('Truth enrolled',summary['truth_enrolled']),
            ('Truth unregistered',summary['truth_unregistered'])]+list(summary['per_view'].items())
    for name,s in scopes:
        seconds=lambda value:'—' if value is None else f'{value/1000:.3f}'
        values=[name,s['total'],s['correct'],s['wrong_identity_accepted'],s['true_identity_nonunique'],s['rejected'],
            s['processing_failure'],s['correct_within_2500']]+[seconds(s['all_timing'][k]) for k in ('p50_ms','p95_ms','max_ms')]
        lines.append('| '+' | '.join(map(str,values))+' |')
    d=summary['duplicates']
    policy=summary['frozen_preexisting_policy_shadow']
    lines += ['', f"Geometry audit: {summary['roi_geometry_fail']}/3677 failed; no anatomical ground truth.", '',
        'User-scoped optimization targets images with both required finger valleys visible. '
        'The full release has no complete visibility annotation; primary results include out-of-scope originals '
        'and must not be presented as performance conditional on visible valleys.', '',
        f"Byte-content audit: {d['unique_byte_contents']} unique originals, {d['redundant_files']} redundant files "
        f"in {d['duplicate_groups']} groups; {len(d['conflicting_identity_groups'])} cross-identity byte conflicts. "
        f"Query/enrollment byte overlap: {d['query_files_overlapping_enrollment']} query files. "
        f"Unique query byte contents: {d['unique_query_byte_contents']}.", '',
        'The summary JSON contains a secondary deterministic one-query-per-byte-content diagnostic. '
        'Primary results retain every file; no deduplication or failure exclusion changes the protocol.', '',
        f"Pre-existing .02 policy saved-score shadow (no fitting): {policy['correct']} correct, "
        f"{policy['wrong_identity_accepted']} wrong accepted, {policy['rejected']} rejected, "
        f"{len(policy['lost_previously_correct'])} previously correct decisions lost. "
        'Zero genuine wrong-to-correct changes; no measured speed improvement or new HTTP run.', '',
        f"Windows model/gallery ready time: {summary['startup_and_gallery_ready_ms']/1000:.3f} s, separate from query timing.", '',
        'Development localization diagnostics and original-device regression overlapped the Windows baseline. '
        'Exact affected query-index intervals are retained in summary.json; no queries are excluded. '
        'This is not exclusive-CPU timing or paired acceleration evidence.', '',
        f"Final original-integrity flag: {summary['original_integrity']}; transactions unchanged: {summary['transactions_unchanged']}.", '',
        'Limits:', '']+[f'- {item}' for item in summary['limitations']]
    lines += ['', 'Archive SHA256: `'+summary['archive_sha256']+'`.', '',
        'Protocol SHA256: `'+summary['protocol_sha256']+'`.', '',
        'Result snapshot SHA256: `'+summary['results_sha256']+'`.', '',
        '[Dataset author release](https://www.kaggle.com/datasets/mahdieizadpanah/sapienza-university-mobile-palmprint-databasesmpd) · '
        '[Dataset paper](https://doi.org/10.1504/IJGUC.2019.102016).', '']
    destination.write_text('\n'.join(lines),encoding='utf-8')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path)
    p.add_argument('--scalar-output',type=Path);p.add_argument('--partial',action='store_true');a=p.parse_args()
    summary,rows,queries=build_summary(a.root,a.partial)
    write_scalars(a.scalar_output or a.root/'report-scalars',summary,rows,queries)
    render_html(a.root,summary,rows,queries)
    write_markdown((a.scalar_output or a.root/'report-scalars')/'RESULTS.md',summary)
    print(json.dumps({k:summary[k] for k in ('complete','completed_queries','gallery_identities','overall')},indent=2))


if __name__=='__main__':main()
