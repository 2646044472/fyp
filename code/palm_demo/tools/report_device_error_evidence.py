"""Scalar export of full-gallery five-frame error diagnostics and fixed pilot."""
import argparse
from collections import Counter
import csv
import html
import json
from pathlib import Path

import numpy as np

from audit_halfturn_recovery import sha,save
from pilot_device_rf_distance import validate_audit


def build(audit,pilot,atlas):
    validate_audit(audit)
    assert pilot['complete'] and atlas['complete']
    assert all(f['code_equal_to_stored'] for r in atlas['records'] for g in r['groups'] for f in g['frames'])
    result=dict(complete=True,matcher=audit['matcher'],selection=audit['selection'],
        scope='Exposed original-device development diagnostics. Seven exact-parity observational HTTP queries; no independent generalization.',
        ordinary_calls=sum(q['matching_coverage']['calls'] for q in audit['queries']),
        unknown_query_calls=sum(q['matching_coverage']['unknown_query'] for q in audit['queries']),
        unknown_target_calls=sum(q['matching_coverage']['unknown_target'] for q in audit['queries']),
        all_calls_geometrically_supported=True,exact_reference_parity=7,
        atlas_enrollment_instances=sum(len(g['frames']) for r in atlas['records'] for g in r['groups']),
        atlas_all_stored_codes_equal=True,
        pilot={k:pilot[k] for k in ('summary','genuine_corrections','lost_correct','pilot_pass','templates_unchanged','originals_unchanged')},
        pilot_decisions=[dict(case=q['case'],sample=q['sample'],identity=q['identity'],before_correct=q['reference_correct'],after_correct=q['correct'],
            user_id=q['result'].get('user_id'),status=q['result'].get('status'),ms=q['ms'],rf_match_calls=q['rf_match_calls']) for q in pilot['queries']],
        errors=[],coverage_by_query=[],
        limits=['All queries were previously exposed development samples.',
            'Pose-only supported scores are diagnostics; they are not full-pipeline counterfactual identity results.',
            'Instrumented observational durations are not a speed baseline.',
            'A successful bounded pilot does not qualify the candidate without full168 regression.',
            'No raw images, masks, binary codes, descriptors or embeddings in these exports.'])
    ledger=[]
    for q in audit['queries']:
        result['coverage_by_query'].append(dict(case=q['case'],sample=q['sample'],reference_equal=q['reference_equal'],
            matching_coverage=q['matching_coverage'],geometric_observations=len(q['geometry_matches']),poses=len(q['poses'])))
        groups={}
        for pose in q['poses']:groups.setdefault(tuple(pose['target']),[]).append(pose)
        for (user,index),poses in sorted(groups.items()):
            old=min(p['original_score'] for p in poses);best=[p for p in poses if p['original_score']==old]
            new=min(p['supported_score'] for p in poses)
            first=best[0];win=first['original_winners'][0]
            ledger.append(dict(case=q['case'],sample=q['sample'],identity=user,frame_index=index,
                pose_only_minimum=old,pose_only_supported_minimum=new,
                representative_best_pose_index=first['pose_index'],angle=first['angle'],scale=first['scale'],
                tied_best_poses=len(best),dx=win['dx'],dy=win['dy'],total_bits=win['total_bits'],valid_bits=win['valid_bits'],
                invalid_bits=win['invalid_bits'],invalid_agreements=win['invalid_agreements'],invalid_mismatches=win['invalid_mismatches'],
                supported_at_original_winner=win['supported_score']))
        if q['reference_correct']:continue
        true=q['identity'].replace(':','-');wrong=q['result']['user_id'];evidence=[]
        for user in (true,wrong):
            rows=[r for r in ledger if r['case']==q['case'] and r['sample']==q['sample'] and r['identity']==user]
            assert len(rows)==5
            evidence.append(dict(identity=user,role='true' if user==true else 'wrong',frames=rows,
                pose_best_two_mean=float(np.mean(sorted(r['pose_only_minimum'] for r in rows)[:2])),
                supported_pose_best_two_mean=float(np.mean(sorted(r['pose_only_supported_minimum'] for r in rows)[:2])),
                actual_retained_frames={stage:[r for r in values if r['identity']==user] for stage,values in q['retained_frames'].items()}))
        result['errors'].append(dict(case=q['case'],sample=q['sample'],identity=q['identity'],returned=wrong,
            actual_full_gallery_scores=q['scores'],evidence=evidence,
            compnet=[dict(kind=c['kind'],ranking=c['ranking'],true_rank=c['ranking'].index(true)+1,top1=c['top1'],score=c['score'],
                gap=c['gap'],distance_pass=c['distance_pass'],margin_pass=c['margin_pass'],
                true_frames=[v for v in c['frames'] if v['identity']==true],wrong_frames=[v for v in c['frames'] if v['identity']==wrong]) for c in q['compnet']],
            exhaustive_pairs=[dict(target=p['target'],score=p['score'],attempt_count=len(p['attempts']),
                scored_attempts=[a for a in p['attempts'] if 'score' in a],
                rejected=dict(Counter(a['rejected'] for a in p['attempts'] if 'rejected' in a))) for p in q['exhaustive_pairs']]))
    return result,ledger


def render(result,atlas_root):
    errors=[]
    for q in result['errors']:
        entries=[]
        for e in q['evidence']:
            values=[e['role'],e['identity'],*[f"{r['pose_only_minimum']:.5f}" for r in e['frames']],f"{e['pose_best_two_mean']:.5f}",f"{e['supported_pose_best_two_mean']:.5f}"]
            entries.append('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in values)+'</tr>')
        errors.append(f"<h2>{html.escape(q['sample'])}</h2><img src='{(atlas_root/(q['sample']+'.jpg')).resolve().as_uri()}' style='width:100%'><table><tr><th>角色</th><th>身份</th><th>帧0</th><th>帧1</th><th>帧2</th><th>帧3</th><th>帧4</th><th>原pose最佳两帧均值</th><th>有效支持pose均值</th></tr>{''.join(entries)}</table>")
    return f'''<!doctype html><html lang="zh"><meta charset="utf-8"><title>三张误认的五帧证据</title>
<style>body{{font:16px/1.7 system-ui;margin:40px auto;max-width:1400px;padding:0 24px;background:#101722;color:#e8eef7}}td,th{{border:1px solid #4d607b;padding:6px}}table{{border-collapse:collapse;font-size:13px}}</style>
<h1>三张误认：原图、完整五帧与滤波有效支持</h1>
<p>这是已暴露设备开发样本的诊断，不是独立泛化。七张只读 HTTP 结果与整库基准完全一致；{result['ordinary_calls']} 次普通 FastCC 比较均有几何来源。图中每组五帧全部保留，30 个注册显示实例的特征码全部复现存储值。</p>
<p>原始图两张 xyt 的 ROI 偏向手腕/前臂，其中一张带入背景；cyw 的 ROI 大致在掌心。几何有效不等于解剖对应正确。归一化增强了显示对比度，也放大了噪声。</p>
<p>表中只比较 pose 分支，不能冒充完整流程识别。实际新距离小试为 5正确/2误认/0拒认，比原小试纠正1张且未损失原正确；完整168回归另报。阈值、所有身份和五帧聚合不变。</p>{''.join(errors)}</html>'''


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('audit','pilot','atlas','output','private_html'):p.add_argument(name,type=Path)
    a=p.parse_args();audit=json.loads(a.audit.read_text());pilot=json.loads(a.pilot.read_text());atlas=json.loads(a.atlas.read_text())
    result,ledger=build(audit,pilot,atlas);result['input_sha256']={name:sha(getattr(a,name)) for name in ('audit','pilot','atlas')}
    a.output.mkdir(exist_ok=False);save(a.output/'summary.json',result)
    with (a.output/'frame-ledger.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(ledger[0]));writer.writeheader();writer.writerows(ledger)
    a.private_html.write_text(render(result,a.atlas.parent),encoding='utf-8')
    print(json.dumps(dict(ordinary_calls=result['ordinary_calls'],exact_parity=result['exact_reference_parity'],pilot=result['pilot'])))


if __name__=='__main__':main()
