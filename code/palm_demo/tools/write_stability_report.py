"""Build a Chinese stability report from saved evidence, without rescoring."""
import argparse
import html
import json
from pathlib import Path


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def table(headers, rows):
    def cell(x):
        return html.escape(str(x))
    return '<div class="scroll"><table><thead><tr>' + ''.join('<th>'+cell(x)+'</th>' for x in headers) + '</tr></thead><tbody>' + ''.join('<tr>'+''.join('<td>'+cell(x)+'</td>' for x in row)+'</tr>' for row in rows) + '</tbody></table></div>'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    root = args.root
    data = read(root/'stability/summary.json')
    algs = ['DoN_median', 'FastCC_median', 'FastCCPoseNearest-v1']
    fixed = {(r['case'], r['algorithm']): r for r in data['fixed_cases']}
    def score(case, alg):
        r = fixed[case, alg]
        return f'{r["correct"]}/{r["total"]}'
    cases = [('old_original', 'Old: enroll first five, query last five'), ('old_reverse', 'Old: enroll last five, query first five'),
             ('new_original', 'New: enroll first five, query last five'), ('new_reverse', 'New: enroll last five, query first five'),
             ('old_to_new_last5', 'Old enrollment → new queries'), ('new_to_old_last5', 'New enrollment → old queries')]
    fixed_table = table(['Fixed split', 'DoN', 'FastCC', 'Nine-pose candidate'], [[label, *[score(case, a) for a in algs]] for case, label in cases])
    sensitivity = {(r['cohort'], r['algorithm']): r for r in data['enrollment_sensitivity']}
    random_rows = []
    for c, label in [('old', 'Old images'), ('new', 'New images')]:
        for a in algs:
            r = sensitivity[c, a]
            random_rows.append([label, a, f'{r["min_correct"]}–{r["max_correct"]}/20', f'{r["mean_correct"]:.1f}/20'])
    mixed = read(root/'mixed-enrollment/summary.json')
    mixed_rows = []
    for no, nn in [(5, 0), (0, 5), (3, 2), (2, 3), (5, 5)]:
        pair = [next(r for r in mixed if r['old_templates']==no and r['new_templates']==nn and r['query_cohort']==c and r['algorithm']==algs[-1]) for c in ['old', 'new']]
        mixed_rows.append([f'Old {no} + new {nn}', *[f'{r["first_correct"]}/20' for r in pair],
                           f'{pair[1]["random_min"]}–{pair[1]["random_max"]}/20'])
    stress_rows = []
    for condition, label in [('dark_065', 'Brightness ×0.65'), ('blur_sigma3', 'Original-image Gaussian blur, σ=3'), ('shift_3pct', 'Original-image translation, 3%')]:
        control = read(root/f'pose-stress-{condition}/aggregation-controls.json')
        r = next(r for r in control if r['algorithm']=='FastCC' and r['pose']=='rotation_scale' and r['rule']=='nearest')
        stress_rows.append([label, f'{r["correct"]}/{r["total"]}'])
    orientations = read(root/'cross-orientation/results.json')
    orientation_rows = []
    for direction in ['old_to_new', 'new_to_old']:
        for a in ['DoN', 'FastCC']:
            rows = [r for r in orientations if r['direction']==direction and r['algorithm']==a]
            assert len(rows)==16
            base = next(r for r in rows if r['rotation']==0 and not r['mirror'] and not r['inverse'])
            orientation_rows.append([direction, a, f'{base["correct"]}/20', f'{max(r["correct"] for r in rows)}/20'])
    http_rows = []
    for c, label in [('old', 'Old images'), ('new', 'New images')]:
        replay = read(root/f'pose-http-{c}/summary.json')
        demo = replay['demo']
        correct = sum(p['result'].get('user_id')==p['identity'].replace(':','-') for p in demo['probes'])
        assert replay['originals_unchanged'] and replay['demo_matcher']==algs[-1]
        http_rows.append([label, f'{correct}/{len(demo["probes"])}', f'{sum(e["http_status"]==200 for e in demo["enrollments"])}/4', demo['payment']['transactions']])
    repeat = read(root/'stability/repeatability.json')
    assert len(repeat)==10 and all(r['identical'] for r in repeat) and data['originals_unchanged']
    doc = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Stability evaluation with old and new cameras</title>
<style>body{margin:0;background:#f3f5f7;color:#182d3c;font:17px/1.75 system-ui,"Microsoft YaHei",sans-serif}main{max-width:1120px;margin:auto;padding:30px 24px 70px}h1{font-size:36px;line-height:1.3}h2{margin-top:38px;font-size:25px}.card{background:white;border-radius:12px;padding:22px;margin:20px 0}.warning{border-left:5px solid #c46c31}table{border-collapse:collapse;background:white;width:100%;font-size:15px}td,th{padding:11px;border-bottom:1px solid #dae1e7;text-align:left}th{background:#e3ebf1}.scroll{overflow:auto}a{color:#006b96}img{max-width:100%;height:auto}.small,figcaption{font-size:14px;color:#4c6170}code{font-size:14px;overflow-wrap:anywhere}</style><main>
<p>2026-10-28 · Local development-set stability audit · Candidate not deployed</p>
<div class="card"><a href="../single-device/report.html">Update: within-device optimization only, with automatic alignment and full replay results</a>. This earlier audit is retained. Cross-device performance is no longer an acceptance target.</div>
<h1>Results on the old data were stable; <br>new-data results varied and cross-camera identification was unreliable.</h1>
<div class="card warning"><strong>The best single result of 18/20 is not a stable accuracy estimate.</strong><p>On ten random new-data enrollment splits the nine-pose candidate scored 15–18/20, dropping to 16/20 on the reverse split. All old-data splits scored 20/20. Enrollment on the old camera and querying on the new gave just 6/20; reversing the cameras gave 10/20.</p></div>
<p>Each camera contributed 40 originals: 80 images, two people and four palm classes (both hands). There were ten images per class per batch; the standard split enrolled 1–5 and queried 6–10. All failures counted, no query matched itself, and original hashes were unchanged. Identity correspondence came from source metadata. Repeated development use means these splits are not new independent samples or an estimate of field or stranger recognition accuracy.</p>
<h2>Fixed splits and cross-camera controls</h2>''' + fixed_table
    doc += '<p>The candidate uses nine fixed rotation/scale poses cropped from full originals. Each query uses the nearest distance to each identity’s five original templates, with identical rules for all identities. On the reverse split DoN scored 18/20 versus 16/20 for the candidate, so the candidate is not always better.</p>'
    doc += '<h2>What changes when different images are enrolled?</h2>' + table(['Data', 'Algorithm', 'Range across ten splits', 'Mean correct'], random_rows)
    doc += '<p>For each class, five random images were enrolled and the other five queried using ten fixed seeds. The new-data candidate averaged 16.7/20 versus 15.1/20 for DoN. Resplitting the same 40 images does not provide 200 independent queries. Repeated feature extraction on five old and five new images gave 10/10 identical outputs: computation is reproducible on fixed inputs, but recognition varies with enrollment composition.</p>'
    doc += '<h2>Does enrolling both cameras help?</h2>' + table(['Enrollment composition per class', 'Old queries: fixed choice', 'New queries: fixed choice', 'New queries: range across template choices'], mixed_rows)
    doc += '<p>Queries always used images 6–10 from each batch. Enrollment used only 1–5; random selection did not use query outcomes. Mixing was unstable: with five total templates the worst new-data results were 8/20 or 9/20; even with five from each camera new-data accuracy fell from 18/20 to 15/20. Out-of-domain templates can compete incorrectly, so mixing is not a demonstrated fix. Ten templates were an offline control only; the app still enrolls five.</p>'
    doc += '<h2>Orientation and image-quality controls</h2>' + table(['Direction', 'Algorithm', 'Unchanged', 'Best of 16 uniform transforms'], orientation_rows)
    doc += '<p>Four right-angle rotations × optional mirroring × optional intensity inversion. One uniform transform was applied to every query per run. Even post hoc the best results reached only 9–10/20 or lower; no uniform flip or rotation solved the problem. Do not change identity or handedness labels on this basis.</p>' + table(['Synthetic query change', 'Nine-pose candidate'], stress_rows)
    doc += '<p>Enrollment images stayed unchanged under synthetic stress. One translated query failed geometry and still counted as wrong. These are variants of development images, not real new sessions. Existing local PalmIR-style RIA did not add correct queries on final v5 ROIs, so default restoration stays off.</p>'
    doc += '<figure><img src="camera-context.jpg" alt="Original images and automatic ROIs from both cameras for four palm classes"><figcaption>The first image of each class is shown: old camera left, new right, automatic ROI in green. Palm size in the frame, backlighting, pose and cropped palm region differ. This demonstrates differences in acquisition conditions, not camera hardware damage. Names and handedness come from metadata.</figcaption></figure>'
    doc += '<h2>End-to-end flow and deployment status</h2>' + table(['Actual local HTTP replay', 'Queries correct', 'Successful enrollments', 'Isolated simulated payment count'], http_rows)
    doc += '''<p>The candidate is available through optional parameter <code>--demo-matcher FastCCPoseNearest-v1</code>. It uses a separate algorithm identifier and requires re-enrollment; old templates cannot be mixed. Enrollment, querying, template saving and simulated payments ran actual application code, but historical images replaced camera inputs. Live camera acceptance is not claimed.</p>
<p><strong>The default and deployed version remain v5 ROI + DoN.</strong>The last actual Pi HTTP replay scored 14/20; the local candidate’s 18/20 was not validated on the Pi. The Pi network route used a VPN and SSH did not connect, so all tests this round ran locally. Production accounts and capture-only mode were unchanged. The hourly automation had been removed; this was a separately initiated experiment.</p>
<h2>Engineering assessment</h2><p>Nine-pose matching improved some new-data splits but did not resolve cross-camera differences in palm region or imaging. Nearest-template selection can also introduce mismatches. Do not make it the default or promise demo reliability from one 18/20 result. The useful next step is consistent localization and alignment of the same palm region across capture conditions, followed by acceptance on new sessions not used in tuning. More poses, floating-point sampling, the existing restoration model and direct template mixing have not produced a stable solution.</p>
<div class="card"><strong>Evidence for review</strong><ul>
<li><a href="summary.json">Stability summary</a> · <a href="results.json">Each split and per-query results</a> · <a href="repeatability.json">Repeatability</a></li>
<li><a href="../mixed-enrollment/summary.json">Mixed-enrollment summary</a> · <a href="../mixed-enrollment/results.json">All template and query scores</a></li>
<li><a href="../cross-orientation/results.json">Uniform orientation control</a> · <a href="../warp-stage-comparison.json">Cross-platform interpolation differences</a></li>
<li><a href="../pose-http-new/summary.json">Candidate HTTP replay: new images</a> · <a href="../pose-http-old/summary.json">Candidate HTTP replay: old images</a></li>
<li><a href="../report.html">Historical v5 deployment and PalmIR report</a></li></ul></div></main></html>'''
    target = root/'stability/report.html'
    target.write_text(doc, encoding='utf-8')
    print(target)


if __name__ == '__main__':
    main()
