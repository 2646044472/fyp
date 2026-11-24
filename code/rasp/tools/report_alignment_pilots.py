"""Report completed proposal screens without claiming deployment or Pi latency."""
import argparse,html,json
from pathlib import Path


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path);p.add_argument('output',type=Path)
    args=p.parse_args();rows=[];evidence=[]
    configurations=[('Local contrast + SIFT','local-contrast-screen-20261029', 'device-contrast-screen-20261029'),
        ('XFeat + original SIFT ratio test','xfeat-pilot-20261029/development-screen',None),
        ('XFeat + upstream default MNN','xfeat-pilot-20261029/development-mnn-screen','xfeat-pilot-20261029/device-mnn-screen'),
        ('XFeat + default MNN + enrollment-frame transforms','xfeat-pilot-20261029/development-linked-screen','xfeat-pilot-20261029/device-linked-screen')]
    for name,dev,device in configurations:
        row=[name];entry=dict(method=name)
        for label,path in (('development',dev),('expanded_device',device)):
            if path is None:row+=['Not run','—'];continue
            result=json.loads((args.root/path/'results.json').read_text(encoding='utf-8'))
            assert result['complete']
            entry[label]=result
            row.extend([f"{result['rescued']}/{len(result['records'])}",str(result['wrong_confident'])])
        rows.append(row);evidence.append(entry)
    def table(headers,rows):
        return '<table><tr>'+''.join('<th>'+html.escape(v)+'</th>' for v in headers)+'</tr>'+''.join(
            '<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in row)+'</tr>' for row in rows)+'</table>'
    content='''<!doctype html><meta charset="utf-8"><title>General alignment experiments for difficult queries</title>
<style>body{font:16px/1.65 system-ui;max-width:1200px;margin:35px auto;padding:0 20px;color:#183046}table{border-collapse:collapse;width:100%}th,td{border:1px solid #ccd5df;padding:10px;text-align:left}th{background:#eaf0f7}.note{background:#fff3db;padding:15px;border-left:4px solid #a65c13}pre{white-space:pre-wrap;overflow-wrap:anywhere}</style>
<h1>Screening alignment methods on difficult queries</h1><p>2026-10-29 · Original-image replay · No experimental path enabled in the demo</p>
<p class="note">This round did not demonstrate better accuracy or end-to-end speed. The Pi-only baseline remains 165/170 correct, with 139/170 correct within 2.5 s. Median latency was 1.564 s and the maximum was 14.342 s.</p>
<p>Across all 224 splits of the 80 development images, v24 reached full search on 30 queries (only three distinct images). Other early-return paths were unchanged. After freezing the parameters, we checked all 16 full searches in the expanded seven-person baseline. Repeated inspection means these data are not an independent holdout.</p>
<h2>Correct returns meeting the original confidence criteria</h2>'''
    content+=table(['Fixed method','Difficult development queries','Incorrect confident development returns','Difficult expanded-set queries','Incorrect confident expanded-set returns'],rows)
    rotation_path=args.root/'rotation-localizer-screen-20261029/results.json'
    if rotation_path.is_file():
        rotation=json.loads(rotation_path.read_text(encoding='utf-8'));assert rotation['complete']
        content+='<h2>Fixed-rotation localization control</h2><p>All localization inputs were rotated 180° and mapped back; scoring used the original pixels. Of 80 development images, '+str(rotation['valid_images'])+' passed the geometric checks. All 224 splits were checked without selecting rotations by identity.</p>'
        content+=table(['Control','Correct confident returns / all queries','Incorrect confident returns','Full searches avoided correctly'],[
            [name,str(s['correct_confident'])+'/'+str(s['total']),s['wrong_confident'],s['fallback_rescued']]
            for name,s in rotation['summary'].items()])
        content+='<p>query_only rotates only the query during localization; both rotates enrollment and query inputs. Both controls had fewer confident returns than the original pose path (2554/4480). Neither was integrated or tested on the expanded set or timed end to end on the Pi.</p>'
    content+='''<p>Every return required a best original-image FastCC score ≤0.32 and a runner-up gap ≥0.08. Geometry and sampling-boundary safeguards were unchanged. Identity labels were used only for retrospective evaluation. Without a confident return the original full-search result stood; a correct top-ranked candidate alone did not count as a recovery. No thresholds were relaxed and no identity-specific branches were introduced.</p>
<h2>Methods and conclusions</h2><p>Local contrast used fixed CLAHE (clip limit 2, 8×8 grid), with original and σ=2 SIFT paths. XFeat used public pretrained weights without further training. We tested the original ratio matcher and then upstream mutual nearest neighbors with cosine similarity &gt;0.82. Query context was 768×768; enrollment context was 384×384. All methods recropped the original grayscale images and scored the best two of five enrollment frames.</p>
<p>Valid query alignments were transferred through existing SIFT transforms between frames of the same enrolled identity, then rescored against original query pixels. This produced 27 more valid scores on development data and 60 on expanded data, but no additional qualifying early returns.</p>
<p>None of the three methods produced a new early return on the expanded set or corrected the five misidentifications. None entered the runtime path or warranted end-to-end Pi timing. Counts in the table do not represent seconds saved.</p>
<h2>Model and platform checks</h2><p>Fixed-shape XFeat ONNX outputs (384/768) were compared with PyTorch. On random inputs the maximum absolute error was about 5×10⁻⁵; sparse keypoint coordinates agreed and descriptor decoding matched within 10⁻⁴. This checks conversion and implementation, not palmprint accuracy or target-device speed.</p>
<p>The expanded screen checked SHA hashes of all 170 original JPEGs and used actual Pi query matrices, enrollment matrices and reference encodings. The Pi computed enrollment-frame transforms; source template hashes were unchanged and all power flags were 0x0. Offline Windows experiments reused features and pair results, but runtime queries did not cache answers. The camera, production service and accounts were unchanged.</p>
<p>Further work should focus on ROI stability and repeatable correspondences. These results rule out contrast enhancement alone and this particular lightweight feature configuration, not all learned features or preprocessing methods.</p>
<details><summary>Full protocol and per-query records</summary><pre>'''+html.escape(json.dumps(evidence,ensure_ascii=False,indent=2))+'</pre></details>'
    args.output.write_text(content,encoding='utf-8');print(args.output)


if __name__=='__main__':main()
