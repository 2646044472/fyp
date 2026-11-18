"""Write the complete restoration adaptation results and practical next steps."""
import argparse
import html
import json
from pathlib import Path


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('output',type=Path)
    args=parser.parse_args();out=args.output
    read=lambda name:json.loads((out/name).read_text())
    results=read('neural.json')+read('classical.json')
    names={'raw_both':'Raw ROI','raw_ria_both':'Raw + RIA (both sides)','raw_blend50_both':'Raw + half-strength restoration (both sides)',
        'normalized_both':'Brightness normalization','normalized_ria_both':'Normalized + RIA (both sides)','normalized_blend50_both':'Normalized + half-strength restoration (both sides)',
        'raw_ria_probe':'Raw + RIA (query only)','raw_blend50_probe':'Raw + half-strength restoration (query only)',
        'normalized_ria_probe':'Normalized + RIA (query only)','normalized_blend50_probe':'Normalized + half-strength restoration (query only)'}
    rows=''
    for key,label in names.items():
        values=[next(r['correct'] for r in results if r['algorithm']==a and r['variant']==key and r['subset']=='all') for a in ('DoN','FastCC','local_training_matcher')]
        rows+='<tr><td>'+label+'</td>'+''.join(f'<td>{v}/20</td>' for v in values)+'</tr>'
    check=read('checkpoint-check.json');stats=read('stats.json')['stats']
    alternative=''.join(f"<li>{html.escape(r['variant'])}: {r['correct']}/20</li>" for r in check['existing_checkpoint_alternatives'])
    text=f'''<!doctype html><html lang="en"><meta charset="utf-8"><title>Local restoration model audit</title>
<style>body{{max-width:1100px;margin:40px auto;padding:0 24px;font:17px/1.65 system-ui;color:#213547;background:#f8fafc}}table{{width:100%;border-collapse:collapse;background:white}}td,th{{border:1px solid #cbd5e1;padding:10px;text-align:left}}.note{{padding:18px;background:#e0f2fe;border-radius:10px}}img{{max-width:100%}}details{{margin:20px 0}}a{{color:#0369a1}}</style><body>
<h1>Local PalmIR-style restoration: what could improve?</h1><p class="note">The existing weights return nearly unchanged camera ROIs.
The one additional correct match came from brightness normalization, not restoration. The ROI repair remains; restoration is not forced into the default matcher.</p>
<p><a href="../heatmap-v3-20261025/report.html">ROI repair report and latest patch</a></p>
<h2>All 40 images; fixed 20 enrollments / 20 queries</h2><p>Fixed heatmap crops, original split and median distance within identity.
No filtering by quality or geometry. The parameter menu was saved to plan.json before scoring. These images have been examined repeatedly, so all results are exploratory development findings.
DoN/FastCC already used percentile normalization; the neural matcher previously received raw pixels on a 0–1 scale.</p>
<table><tr><th>Input configuration</th><th>DoN</th><th>FastCC</th><th>Paired neural matcher</th></tr>{rows}</table>
<h2>Was the wrong model loaded?</h2><p>RIA, matcher, checkpoint and implementation hashes agree; the pairing was verified.
models.py, data.py, losses.py and training.py match training provenance.</p>
<ul><li>Raw camera input: mean pixel change {stats['raw']['mean_abs_change_8bit']:.3f}/255。</li>
<li>Normalized input: mean pixel change {stats['normalized']['mean_abs_change_8bit']:.3f}/255。</li>
<li>Maximum absolute PyTorch–ONNX error on 40 raw inputs {check['parity']['raw']['max_abs_error']:.8f} (0–1 scale); both return nearly unchanged images.</li></ul>
<p>One preselected image from each of 8 different training-domain palm classes received Gaussian blur, sigma=1.5, for a response check. Mean output change was about 11.07/255;
 mean pixel error fell from 0.04991 to 0.02127. The network is not unconditionally an identity mapping. This synthetic response on training images does not establish independent restoration performance.</p>
<h2>Control: substitute existing restoration weights</h2><p>Same paired neural matcher, CPU PyTorch, all 20 probes. Existing checkpoints were read only; no retraining.</p><ul>{alternative}</ul>
<h2>Possible improvements and limits of evidence</h2><ol>
<li><strong>First standardize inputs and ROIs.</strong>Normalization alone shifted development results from 14 to 15/20; new sessions are needed. A local restorer cannot recover a wrongly placed crop.</li>
<li><strong>Design for the camera domain.</strong>Training used fixed PolyU-II palm-class ROIs with Gaussian or motion blur and 10% clear inputs. It did not combine camera exposure, noise, compression, scale and localization perturbations.
Generate such degradations using training identities, keep original images for supervision, and constrain changes to clear inputs. Ablate each factor separately. This remains a proposal, not proof of benefit or that the camera images are blurred.</li>
<li><strong>Match the final recognition objective.</strong>RIA's identity loss uses frozen PalmMatcher features; the default demo uses DoN. A neural matcher requires end-to-end validation; for DoN, test distance separation on independent development data rather than assuming transfer.</li>
<li><strong>Validate recognition gains, not just apparent sharpness.</strong>Compare no restoration, normalization only, pixel restoration and RIA. Hold out identities and sessions and record same- and different-hand scores. The current 40 are not independent. Without a paired reference, do not treat another photo of the person as a pixel-aligned target.</li></ol>
<p>This round did not train, download weights, change the research queue, deploy to Pi, or increase restoration strength as a substitute for a fix. These weights do not support a general claim of benefit.</p>
<h2>Reproducibility and per-image outcomes</h2><p><a href="plan.json">Frozen experiment menu</a> · <a href="neural.json">Full neural matching scores</a> ·
<a href="classical.json">Full conventional matching scores</a> · <a href="checkpoint-check.json">Checkpoint integrity and response checks</a> · <a href="stats.json">Output changes and model details</a></p>
<p>Run tools/audit_restoration_adaptation.py &lt;heatmap-replay&gt; &lt;new-output&gt;;
 then run tools/check_restoration_checkpoint.py &lt;experiment&gt; &lt;output&gt; in the existing PyTorch environment.</p>
'''
    for start in range(0,40,10):text+=f'<details><summary>Sample {start+1}–{start+10}: six input/output comparisons</summary><img src="comparison-{start}.jpg"></details>'
    (out/'report.html').write_text(text+'</body></html>',encoding='utf-8')
    print(out/'report.html')


if __name__=='__main__':main()
