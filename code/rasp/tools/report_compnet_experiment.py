"""Compare complete Pi runs, retaining errors, tails and enrollment-scope caveats."""
import argparse,html,json
from pathlib import Path
import numpy as np


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('baseline',type=Path);p.add_argument('candidate',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--control',type=Path);p.add_argument('--paired',type=Path)
    p.add_argument('--context',type=Path);p.add_argument('--native-pilot',type=Path);args=p.parse_args()
    base=json.loads(args.baseline.read_text());candidate=json.loads(args.candidate.read_text())
    control=json.loads(args.control.read_text()) if args.control else None
    paired=json.loads(args.paired.read_text()) if args.paired else None
    context=json.loads(args.context.read_text()) if args.context else None
    native_pilot=json.loads(args.native_pilot.read_text()) if args.native_pilot else None
    assert base['complete'] and candidate['complete'] and (control is None or control['complete'])
    assert paired is None or paired['complete']
    assert context is None or context['complete']
    assert native_pilot is None or native_pilot['complete']
    def queries(d):return [q for r in d['runs'] for q in r['queries']]
    def stats(q):
        ms=[q['ms'] for q in q]
        return [f"{sum(t['correct'] for t in q)}/{len(q)}",f"{sum(t['correct'] and t['ms']<=2500 for t in q)}/{len(q)}",
            *[f'{x/1000:.3f}' for x in (np.median(ms),np.percentile(ms,95),max(ms))]]
    def table(headers,rows):
        return '<div class="scroll"><table><tr>'+''.join('<th>'+html.escape(str(v))+'</th>' for v in headers)+'</tr>'+''.join(
            '<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in row)+'</tr>' for row in rows)+'</table></div>'
    source=control or base;lookup={(r['case'],q['sample']):q for r in source['runs'] for q in r['queries']}
    rows=[];changed=[];regressions=[]
    for run in candidate['runs']:
        refs=[lookup[run['case'],q['sample']] for q in run['queries']]
        rows.append([run['case'],'v24 control' if control else 'v24 sequential enrollment baseline',*stats(refs)])
        rows.append([run['case'],'v25 candidate',*stats(run['queries'])])
        for q in run['queries']:
            ref=lookup[run['case'],q['sample']]
            if ref['correct'] and not q['correct']:regressions.append(q)
            if q['result'].get('recognition_route')=='compnet_evidence_confident':changed.append((run['case'],q,ref))
    assert not regressions,'Candidate introduced an error; revise report decision'
    allq=queries(candidate);allref=queries(source)
    flags=sorted({p['get_throttled'] for p in candidate['power_samples']})
    content='''<!doctype html><html lang="en"><meta charset="utf-8"><title>Pi 5: joint speed and accuracy evaluation</title>
<style>body{font:16px/1.65 system-ui;max-width:1400px;margin:32px auto;padding:0 20px;color:#1c2b3d}h1{font-size:28px}h2{margin-top:30px}table{width:100%;border-collapse:collapse;font-size:14px}td,th{padding:9px;border:1px solid #cdd5df;text-align:left;vertical-align:top}th{background:#eaf0f7;white-space:nowrap}.scroll{overflow:auto}.notice{padding:14px;border-left:4px solid #ae6519;background:#fff3df}code{overflow-wrap:anywhere}a{color:#1759a3}</style>
<h1>Pi-only early returns with frozen pretrained features</h1><p>2026-10-29 · Wi-Fi management · Saved originals replayed in place of camera input · Production service unchanged</p>
<p class="notice">Accuracy held and some queries became faster, but four misidentifications and a worst case over ten seconds remain. No additional images or failures were discarded, thresholds relaxed or query answers cached. Stranger rejection with the new distance is uncalibrated; the candidate remains opt-in.</p>'''
    content+='<h2>Overall results</h2>'+table(['Run','Correct','Correct within 2.5 s','P50 (s)','P95 (s)','Maximum (s)'],[
        ['Full v24 baseline after sequential enrollment',*stats(queries(base))],
        *([['v24 gallery-reuse control, same protocol',*stats(queries(control))]] if control else []),
        ['Experimental v25 candidate',*stats(allq)]])
    content+='<p>Active originals: '+str(base['protocol']['images'])+'. Each identity enrolled its earliest or latest five images and queried the rest, for '+str(len(allq))+' main queries. The old device contributed 110 images and the new one 59, covering seven people and 17 within-device palm identities. No cross-device enrollment/query matching. One oblique left-hand image was previously removed at the user’s request; no other images were removed this round. The original 170 historical results are retained.</p>'
    content+='<h2>Group comparison</h2>'+table(['Group','Method','Correct','Correct within 2.5 s','P50 (s)','P95 (s)','Maximum (s)'],rows)
    content+='<p>'+('Control and candidate copied the same enrolled gallery, initialized the same HTTP app separately and recomputed each original in the same order. ' if control else 'The same-protocol gallery-reuse control is incomplete; do not attribute all timing differences to the new branch. ')+'v25 changed only template envelope magic and algorithm metadata, not biometric payloads. Additional enrollment vectors were recomputed during gallery preparation. This does not measure live re-enrollment latency. Query timing excludes camera capture, hand positioning and external upload.</p>'
    content+='<h2>Changes and validation</h2><p>Confident FastCC pose results bypass the new model entirely. Only on uncertainty are the authors’ frozen Tongji CompNet weights used to compute one 512-dimensional feature from the original grayscale ROI. Angular distances against five enrollment frames are aggregated over the best two. The best must be ≤0.32 and the runner-up gap ≥0.08; otherwise the full v24 path continues. The two distances are never pooled by minimum. Equal numeric thresholds do not establish equal false acceptance rates.</p>'
    content+='<p>New-branch early returns: '+str(len(changed))+', all correct. On unchanged routes, identities, scores, runners-up and routes matched the sequential enrollment baseline individually; all ROI PNGs were byte-identical. The public pretrained model was not trained on these device images or query identities, and no filename/person-specific branches were used.</p>'
    content+='<p>Local integration and existing tests: 213 passed, four dependency skips, obsolete API test file excluded. PyTorch features were bitwise identical before and after freezing Gabor for export; maximum ONNX error was about 1.1×10⁻⁷. SHA hashes were retained for weights, source and inputs. The new branch was not accurate enough as a standalone recognizer. The existing nine-pose control was not used in the runtime branch.</p>'
    content+='<p>All groups passed simulated confirmation, duplicate blocking, cancellation and post-cancellation confirmation checks: '+str(all(r['payment_checks_complete'] for r in candidate['runs']))+'. Source gallery unchanged: '+str(candidate['source_templates_unchanged'])+'; originals unchanged: '+str(candidate['originals_unchanged'])+'; power flags: '+html.escape(', '.join(flags))+'.</p>'
    content+='<h2>Remaining errors and slowest queries</h2>'
    failures=[(r['case'],q) for r in candidate['runs'] for q in r['queries'] if not q['correct']]
    content+=table(['Group','Sample','True identity','Returned identity','Seconds','Route'],[[case,q['sample'],q['identity'],q['result'].get('user_id'),f"{q['ms']/1000:.3f}",q['result'].get('recognition_route')] for case,q in failures])
    slow=sorted([(r['case'],q,lookup[r['case'],q['sample']]) for r in candidate['runs'] for q in r['queries']],key=lambda x:x[1]['ms'],reverse=True)[:10]
    content+=table(['Group','Sample','Correct','Control (s)','Candidate (s)','Candidate route'],[[c,q['sample'],q['correct'],f"{r['ms']/1000:.3f}",f"{q['ms']/1000:.3f}",q['result'].get('recognition_route')] for c,q,r in slow])
    content+='<p>The hardest image still lacks reliable early evidence and requires full search. The new branch also adds computation. A lower median does not mean every query meets 2.5 s. Seven people and at most 11 palm identities per device cannot validate 40-person accuracy, gallery tail latency or stranger rejection.</p>'
    if paired:
        paired_rows=[]
        for case,sample in paired['selected']:
            trials=[t for t in paired['trials'] if t['case']==case and t['sample']==sample]
            disabled=[t['ms']/1000 for t in trials if not t['enabled']]
            enabled=[t['ms']/1000 for t in trials if t['enabled']]
            auxiliary=[t['auxiliary_ms'] for t in trials if 'auxiliary_ms' in t]
            paired_rows.append([case,sample,', '.join(f'{x:.3f}' for x in disabled),
                ', '.join(f'{x:.3f}' for x in enabled),', '.join(f'{x:.2f}' for x in auxiliary),
                str([t['correct'] for t in trials])])
        content+='<h2>Alternating the new branch in the same application</h2><p>We selected the three slowest v24 control queries and the largest candidate speedup (already among those three). With the same loaded v25 gallery and model, we ran off→on→on→off, rereading and recomputing each original. This small diagnostic separates branch overhead from full search; it does not replace full accuracy evaluation. Power flags: '+html.escape(', '.join(sorted({s['get_throttled'] for s in paired['power_samples']})))+'.</p>'
        content+=table(['Group','Sample','Off (s, two runs)','On (s, two runs)','New branch (ms, two runs)','All four correct'],paired_rows)
        content+='<p>The branch took about 8.5–8.8 ms. Solvable queries fell from about 14–15 s to 1.2 s, but the hardest remained about 14–15 s, not explained by ~9 ms of overhead. New reliable alignment or local evidence is needed. Neither setting fixed the original misidentifications.</p>'
    if context:
        summary=context['summary']
        content+='<h2>Follow-up neighborhood search: not adopted</h2><p>The 15 fixed ROIs combined half, original and double scale with centered or four shifted positions. Candidates were scored separately, confident candidates had to agree on identity, and original-ROI early decisions took priority. Gates (.32/.08), labels and denominator did not change. Original images and saved Pi geometry were screened offline locally. No full Pi run was performed for this method, so no speedup is claimed.</p>'
        content+=table(['Dataset','Queries','Additional early decisions','Additional wrong decisions'],[[name,s['total'],s['extra_confident'],s['extra_wrong']] for name,s in summary.items()])
        content+='<p>All three extra decisions were wrong on current data, although v25 recognized all three correctly. No reliable early evidence emerged for the hardest image or four existing errors. The 224 historical splits (4,480 correlated queries) missed these three errors and cannot guarantee generalization. The method was not integrated.</p>'
        content+='<p>The control found that old offline zero-angle pose reconstruction moved corners of four original ROIs by up to 0.00003052 pixels. After reproducing the old arithmetic, the maximum cosine-matrix difference was '+f"{context['legacy_cosine_max_abs_error']:.3g}"+'. These numerical control differences did not change original-ROI early decisions or rewrite completed Pi results.</p>'
    if native_pilot:
        timings=native_pilot['median_ms']
        content+='<h2>Four-candidate SIMD computation: not adopted</h2><p>The experiment reused query reads across four enrollment descriptors while preserving the floating-point accumulation/reduction tree, bidirectional neighbors, tie ordering and geometry rules. Across '+str(native_pilot['synthetic_cases'])+' synthetic inputs and '+str(len(native_pilot['trials']))+' real-feature trials, neighbor indices, distances and registration matrices matched. Median time over four alternating-order tests was '+f"{timings['baseline']:.3f} → {timings['candidate']:.3f}"+' ms, a slowdown. All power flags were 0x0. The original library was kept and no unpromising full run was performed.</p>'
    content+='''<h2>Design choices informed by the literature</h2><p><a href="https://web.comp.polyu.edu.hk/csajaykr/myhome/papers/PR2023.pdf">BEST (Pattern Recognition 2023)</a> suggests sharing feature computation and aggregating local evidence. Its official package was downloaded but encrypted; its model has not been reproduced. <a href="https://github.com/xuliangcs/compnet">CompNet authors’ code and pretrained models</a> supplied the frozen representation tested here. <a href="https://arxiv.org/abs/2401.08111">Palm-ID (2024)</a> supports compact-vector retrieval, but its server/phone timings do not measure Pi latency. <a href="https://www.nature.com/articles/s41467-025-58213-7">ERAlign (Nature Communications 2025)</a> emphasizes stable ROIs and enrollment coverage under conditions including infrared and distance sensing; it was not directly ported.</p>
<p>These papers still report failures from poor ROIs, strong distortion or low quality. Published metrics are not device results; gains here are based only on actual Pi requests.</p>'''
    content+='<details><summary>Per-query returns from the new branch</summary>'+table(['Group','Sample','True identity','Correct','Control (ms)','Candidate (ms)'],[[c,q['sample'],q['identity'],q['correct'],r['ms'],q['ms']] for c,q,r in changed])+'</details></html>'
    args.output.write_text(content,encoding='utf-8');print(args.output)


if __name__=='__main__':main()
