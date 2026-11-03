"""Publish scalar results from the completed fixed pilot; never run inference."""
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
APP=OUT.parents[2]
RUN=APP/'runtime/smpd-oob-identification-pilot-20261101'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    protocol=json.loads((RUN/'protocol.json').read_text(encoding='utf-8'))
    result=json.loads((RUN/'results.json').read_text(encoding='utf-8'))
    rows=[]
    for r in result['queries']:
        baseline=protocol['baseline_records'][r['sample']]['payload']
        rows.append(dict(sample=r['sample'],baseline_outcome=baseline['outcome'],candidate_outcome=r['outcome'],
            candidate_http_ms=r['ms'],candidate_user=r['result'].get('user_id'),
            candidate_score=r['result'].get('score'),second_score=r['result'].get('second_score'),
            candidate_route=r['result'].get('recognition_route'),original86_score_count=len(baseline['scores']),
            candidate_score_count=len(r['scores']),control_comparison=r.get('control_comparison'),
            negative_control=r.get('negative_control'),primary_historical_exact=r['primary_historical_exact'],
            selected_primary_verbatim=r['selected_primary_verbatim'],record_sha256=r['record_sha256']))
    value=dict(protocol_fingerprint=protocol['run_fingerprint'],protocol_sha256=sha(RUN/'protocol.json'),
        results_sha256=sha(RUN/'results.json'),complete=result['complete'],pilot_pass=result['pilot_pass'],
        outcomes=result.get('outcomes'),gates=result.get('gates'),failure=result.get('failure'),
        actual_enrollment=result.get('actual_enrollment'),actual_query=result.get('actual_query'),
        candidate_gallery=result.get('candidate_gallery'),ready_cache_count=result.get('ready_cache_count'),
        full_gallery_prepare_wall_ms=result.get('full_gallery_prepare_wall_ms'),
        enrollment=[{k:r.get(k) for k in ['sample','ok','ms','old_feature_exact','feature_file_sha256','feature_array_sha256','codec','record_sha256']}
                    for r in result['enrollments']],queries=rows,
        original_preservation=result.get('original_preservation'),original_chain_after=result.get('original_chain_after'),
        preservation_error=result.get('preservation_error'),
        source_byte_overlap_queries_with_new_enrollments=[r['sample'] for r in protocol['rows']
            if r['sample'] in protocol['query_samples'] and r['sha256'] in {e['sha256'] for e in protocol['rows'] if e['sample'] in protocol['enrollment_samples']}],
        scope='Only this fixed development pilot. No new full168/3217 evaluation or Pi test; no speed, generalization or FAR claim; no deployment.',
        visual_observation_from_parent='Parent visually viewed original008-F03 and candidate enrollment ROI: visible finger valleys and palm texture, with some edge background. Qualitative only; not landmark/anatomical ground truth.')
    target=OUT/'recognition-pilot-summary.json'
    with target.open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=True,sort_keys=True,indent=2);f.write('\n')
    lines=['\n## 后续：唯一固定8查询真实识别小试\n',
           '这一步在几何结果报告后另外获得明确授权，使用独立新目录 `runtime/smpd-oob-identification-pilot-20261101`。没有续写原3217记录。',
           f"协议在推理前封存，fp `{protocol['run_fingerprint']}`；driver fixtures 5/5通过。实际执行结果complete={result['complete']}，预设pilot_pass={result['pilot_pass']}。",
           '008原F00..04五张均重新提取，原本有效F00/F01/F02/F04与父特征数组及codec严格一致。原86模板byte-copy保留，008模板使用新候选指纹/恢复来源；041未加入。实际LosslessUnionMatcher、magic2801166、UNIONV2、retained＋terminal RF、final1/margin0/rejection-off均断言。全87图库/cache/index只准备一次，原阈值及评分源不改。',
           '\n|样本|原结果|候选结果|返回身份|route|本次HTTP秒|\n|---|---|---|---|---|---:|']
    for r in rows:
        lines.append(f"|{r['sample']}|{r['baseline_outcome']}|{r['candidate_outcome']}|{r['candidate_user']}|{r['candidate_route']}|{r['candidate_http_ms']/1000:.3f}|")
    lines += ['\n预设门逐项结果（失败不调参、不重试）：', '```json',json.dumps(result.get('gates'),ensure_ascii=False,indent=2),'```',
              f"运行异常：`{result.get('failure')}`。只报告实际保存的{len(rows)}条；没有补样本。",
              'candidate HTTP时间为历史基线之后的单独epoch，注册/全图库ready另计，不能据此声称公平提速；原基线未重跑。所有token仅取消，无confirm/扣款。',
              f"原始保护回执：`{json.dumps(result.get('original_preservation'),ensure_ascii=False)}`。",
              f"原链结束快照：`{json.dumps(result.get('original_chain_after'),ensure_ascii=False)}`。",
              '完整机器摘要见recognition-pilot-summary.json；私有运行目录保留protocol、8条attempt/结果、5条注册记录、新特征和ROI、完整scores、支付/ready与source hash信息。',
              '主agent对008-F03原图/候选ROI的视觉观察：可见指缝/掌纹及部分边缘背景；不作为关键点或解剖位置认证。',
              '小试结论不代替原168守护，也不证明整个SMPD提升。不得推广、全量续跑、安装CUDA依赖或启动新的速度实验。']
    report=OUT/'REPORT.md';text=report.read_text(encoding='utf-8')
    if '## 后续：唯一固定8查询真实识别小试' in text:raise ValueError('Already appended')
    report.write_text(text+'\n'.join(lines)+'\n',encoding='utf-8')
    with (RUN/'README.md').open('x',encoding='utf-8') as f:
        f.write('# 固定8查询识别小试\n\n'+ '\n'.join(lines[1:])+'\n')
    manifest=dict(note='Supersedes initial artifact-manifest for current new diagnosis files; initial manifest remains a historical pre-recognition snapshot.',
        files={p.name:sha(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='artifact-manifest-after-pilot.json'})
    with (OUT/'artifact-manifest-after-pilot.json').open('x',encoding='utf-8') as f:json.dump(manifest,f,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps(dict(complete=value['complete'],pilot_pass=value['pilot_pass'],queries=len(rows),outcomes=value['outcomes'],report=str(report))))


if __name__=='__main__':main()
