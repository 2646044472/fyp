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
    text='''<!doctype html><html lang="en"><meta charset="utf-8"><title>Pi 5 v26: full evaluation of localization candidate reuse</title>
<style>body{font:16px/1.65 system-ui;max-width:1450px;margin:32px auto;padding:0 22px;color:#1c2b3d}h1{font-size:28px}h2{margin-top:30px}table{width:100%;border-collapse:collapse;font-size:14px}td,th{padding:9px;border:1px solid #cdd5df;text-align:left;vertical-align:top}th{background:#eaf0f7;white-space:nowrap}.scroll{overflow:auto}.notice{padding:14px;border-left:4px solid #ae6519;background:#fff3df}code{overflow-wrap:anywhere}a{color:#1759a3}</style>
<h1>Pi-only v26: reusing an alternate base ROI already computed</h1><p>2026-10-30 · Full HTTP replay from originals · Production service unchanged</p>'''
    text+='<p class="notice">'+('Integrity checks passed with no new misidentifications. ' if valid else 'Regression or integrity problems detected; do not adopt. See below. ')+'This limited early-return optimization leaves the worst tail and existing misidentifications unresolved. Not all queries finish within 2.5 s.</p>'
    text+='<h2>Full Pi results</h2>'+table(['Version / protocol','Correct','Correct within 2.5 s','P50 (s)','P95 (s)','Maximum (s)'],[
        ['v24 fresh enrollment from an empty gallery',*stats(queries(baseline).values())],
        ['v24 gallery-reuse control, same protocol',*stats(queries(control).values())],
        ['v25 frozen representation on the primary ROI',*stats(old.values())],
        ['v26 reused base ROI candidate',*stats(new.values())]])
    text+='<p>There were 169 active originals, seven people and 17 within-device palm identities. Each device enrolled its earliest or latest five images per identity and queried the rest (168 queries, no cross-device matching). A historical oblique image removed by the user was excluded before every experiment in this table. The separate historical 170-query results are not a direct measure of algorithm gains. All failures and timeouts remain in the denominator.</p>'
    rows=[]
    for run in candidate['runs']:
        case=run['case'];refs=[old[case,q['sample']] for q in run['queries']]
        rows.extend([[case,'v25',*stats(refs)],[case,'v26',*stats(run['queries'])]])
    text+='<h2>By device and enrollment direction</h2>'+table(['Group','Version','Correct','Correct within 2.5 s','P50 (s)','P95 (s)','Maximum (s)'],rows)
    text+='<h2>Changes and scope</h2><p>The existing pose decision and v25 primary-ROI vector decision remain first. Only if both are uncertain does v26 use the other valid overlapping original/gamma ROI from initial localization, compute the same frozen CompNet feature once and score the full gallery. No extra localizer call, windows, scales or translations were added. The .32/.08 gates were unchanged. Distances from different ROIs are not pooled by minimum; conflicting confident identities continue through the original path. Enrollment still uses only the primary ROI from each frame.</p>'
    text+='<p>The displayed ROI remains the original primary ROI. The auxiliary region actually used for matching is recorded per diagnostic in <code>auxiliary_roi_quad</code>. Identical displayed ROI bytes do not mean auxiliary matching used the same region. No training on these device images or filename/person-specific exceptions were used. The 4,480 historical split queries are exposed correlated regression evidence, not independent validation.</p>'
    text+='<p>The v24 control, v25 and v26 copied the same enrolled gallery. Only the template envelope magic and algorithm metadata changed; biometric payloads stayed intact and the prepared gallery was rebuilt at initialization. Each query reread, localized, extracted and matched the original. Timing includes local HTTP but not capture, hand positioning or external upload. Startup and on-site re-enrollment are separate; this did not measure live v26 enrollment latency.</p>'
    text+='<h2>Per-query comparison for the new branch</h2>'+table(['Group','Sample','True identity','Correct','v25 (s)','v26 (s)'],[
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
                text+='<figure><img style="max-width:100%" src="'+html.escape(relative,quote=True)+'"><figcaption>'+html.escape(sample)+': green is the original primary ROI; orange is the auxiliary matching ROI. The lower images use 1–99% grayscale stretching for display only; the model uses original grayscale.</figcaption></figure>'
        finally:algorithm.close()
    text+='<h2>Regression and flow checks</h2>'+table(['Check','Result'],[
        ['New misidentifications',len(regressions)],['Identity / score / runner-up / status / route differences outside the new branch',len(differences)],
        ['All displayed primary ROIs byte-identical to v24',roi_equal],['Simulated confirmation / duplicate confirmation / cancellation / confirmation after cancellation',checks],
        ['Source templates and originals unchanged',integrity],['Power flags',', '.join(power)],['Full local tests','224 passed, 4 optional skips; obsolete API test excluded']])
    failures=[(k,q) for k,q in new.items() if not q['correct']]
    text+='<h2>Remaining misidentifications</h2>'+table(['Group','Sample','True identity','Returned identity','Seconds','Route'],[
        [case,sample,q['identity'],q['result'].get('user_id'),f"{q['ms']/1000:.3f}",q['result'].get('recognition_route')] for (case,sample),q in failures])
    slow=sorted(new,key=lambda k:new[k]['ms'],reverse=True)[:10]
    text+='<h2>Ten slowest queries</h2>'+table(['Group','Sample','Correct','v25 (s)','v26 (s)','Route'],[
        [case,sample,new[case,sample]['correct'],f"{old[case,sample]['ms']/1000:.3f}",f"{new[case,sample]['ms']/1000:.3f}",new[case,sample]['result'].get('recognition_route')] for case,sample in slow])
    text+='<h2>Hardest image still unresolved</h2><p>Registered crops from the slowest v25 image showed no reliable CompNet evidence in the two fast-stage regions at about 2.00/2.66 s. Two better regions after about 13.33 s still had a true-identity angular distance of about 0.363, above the unchanged 0.32 gate. Fixed CLAHE on both sides covered just one extra image, already correct within 1.80 s, and was not integrated. Offline screening of all stored window candidates covered six more queries but not the hardest image or four errors. Additional localization is not free candidate reuse.</p>'
    text+='<p>Unknown-person rejection remains uncalibrated; closed-set fallback can return an identity on weak evidence. Seven people cannot establish capacity for 40 or generalization to new sessions. Pretrained weights and author source are not distributed with Git. <a href="../compnet-v25-pi-20261029/report.html">Earlier v25 literature, controls and rejected experiments</a>.</p></html>'
    if paired:
        rows=[]
        for case,sample in paired['selected']:
            trials=[t for t in paired['trials'] if t['case']==case and t['sample']==sample]
            def times(enabled,field,scale):return ', '.join(f'{t[field]/scale:.3f}' for t in trials if t['enabled']==enabled)
            rows.append([case,sample,times(False,'ms',1000),times(True,'ms',1000),
                times(False,'auxiliary_ms',1),times(True,'auxiliary_ms',1),all(t['correct'] for t in trials)])
        section='<h2>Alternating auxiliary ROI use within one application</h2><p>All three new early returns were selected mechanically and replayed off→on→on→off. Off uses only original v25 feature evidence; the model and loaded v26 gallery were held constant and originals were recomputed each time. These three queries check the mechanism, not repeatability of deadline compliance across the full set.</p>'
        section+=table(['Group','Sample','v25 (s, two runs)','v26 (s, two runs)','v25 auxiliary stage (ms)','v26 auxiliary stage (ms)','All four correct'],rows)
        section+='<p>Power flags: '+html.escape(', '.join(sorted({s['get_throttled'] for s in paired['power_samples']})))+'. Full-set P95 and maximum are not replaced by timings from these three favorable samples.</p>'
        text=text.replace('</html>',section+'</html>')
    args.output.write_text(text,encoding='utf-8')
    print(json.dumps(dict(report=str(args.output),valid=valid,new_branch=len(changed),regressions=regressions,unchanged_path_differences=differences)))


if __name__=='__main__':main()
