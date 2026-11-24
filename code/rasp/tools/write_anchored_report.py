"""Show actual scoring regions per contributing template, never a fictitious global ROI."""
import json,html
from pathlib import Path
import sys
import cv2
import numpy as np
from PIL import Image,ImageDraw

APP=Path(__file__).resolve().parents[1];sys.path.insert(0,str(APP))
from anchored_matcher import source_quad

root=Path(sys.argv[1]);base=root/'single-device';out=base/'runtime-v5'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
records={r['sample']:r for r in read(root/'stability/records.json')}
cases=read(out/'results.json');pair={(r['query'],r['gallery']):r for r in read(out/'pair-winners.json')}
counts=read(out/'candidate-counts.json');summary=read(out/'summary.json')
def table(rows):return '<table>'+''.join('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in row)+'</tr>' for row in rows)+'</table>'
doc='''<!doctype html><html lang="en"><meta charset="utf-8"><title>Candidate background rejection and actual scoring regions</title><style>body{max-width:1200px;margin:30px auto;padding:20px;background:#f5f7f8;font:17px/1.7 system-ui;color:#19333c}img{max-width:100%}table{width:100%;background:white}td{padding:8px;border-bottom:1px solid #ccc}a{color:#006c82}</style><h1>Rejecting candidates outside the primary ROI and showing the region actually scored</h1>
<p>Optional FastCCAnchoredUnion-v5 retains the primary ROI localizer; the small green box may still be undersized. This update checks spatial consistency and traces how a score was obtained. It is not hand segmentation; overlap alone cannot validate a palm crop.</p>
<p>Both the candidate quad and the aligned scoring quad must intersect the automatic primary ROI; candidate overlap must exceed 1 square pixel. All images use the same rule without identity or reference labels. Wall candidates 3 and 4 are excluded in the illustration. All 80 images remain in evaluation, and v4 is preserved.</p>
<h2>All predefined splits</h2>'''
doc+=table([['Device','Split','Splits','Minimum','Maximum','Mean /20']]+[[r['cohort'],r['split'],r['count'],r['min'],r['max'],r['mean']] for r in summary])
doc+=f'<p>Total descriptor views: {sum(r["views_before"] for r in counts)} → {sum(r["views_after"] for r in counts)}; {sum(r["views_after"]<r["views_before"] for r in counts)}  images lost at least one candidate branch. Views include different search areas and smoothing scales, not independent ROIs.</p>'
# An optional private case list is read locally, never embedded in the public source.
selected=json.loads(Path(sys.argv[2]).read_text()) if len(sys.argv)>2 else []
evidence=[]
for sample in selected:
    rec=records[sample];case=next(c for c in cases if c['case']=='new_'+('original' if rec['index']>5 else 'reverse'))
    trial=next(t for t in case['trials'] if t['sample']==sample);identity=min(trial['scores'],key=trial['scores'].get)
    chosen=sorted(case['gallery'][identity],key=lambda s:pair[sample,s]['winner']['score'])[:2]
    doc+=f'<h2>{html.escape(rec["identity"])} #{rec["index"]}</h2><p>Split:{case["case"]}; actual first-ranked identity:{identity}; correct:{trial["correct"]}. These are the two enrollment templates contributing to that identity score, not one final ROI chosen in advance.</p>'
    for rank,target in enumerate(chosen):
        winner=pair[sample,target]['winner'];g=records[target];image=Image.open(rec['original']).convert('RGB');draw=ImageDraw.Draw(image)
        anchor=np.asarray(rec['illumination']['details']['roi_quad_full'])
        draw.polygon([tuple(p) for p in anchor],outline='lime',width=10)
        if winner['branch']=='union':
            q=source_quad(np.asarray(winner['source_matrix']))
            draw.polygon([tuple(p) for p in q],outline='orange',width=3)
            draw.polygon([tuple(p) for p in winner['aligned_quad']],outline='magenta',width=7)
        image.thumbnail((800,550));sheet=Image.new('RGB',(1200,620),'white');sheet.paste(image,(0,60));text=ImageDraw.Draw(sheet)
        text.text((10,10),f'Query {rec["identity"]} #{rec["index"]} -> gallery {g["identity"]} #{g["index"]}',fill='black')
        text.text((10,30),f'Branch {winner["branch"]}, view {winner.get("view_index","N/A")}, sigma {winner.get("sigma","N/A")}, distance {winner["score"]:.6f}',fill='black')
        text.text((800,60),'Green: automatic anchor',fill='green');text.text((800,85),'Orange: candidate ROI',fill='orange');text.text((800,110),'Magenta: actual scoring ROI',fill='purple')
        roi_dir=root/('new-runtime-consistent' if g['cohort']=='new' else 'old-runtime-consistent')/'rois'/target/'illumination/roi_128.png'
        thumb=Image.open(roi_dir).convert('RGB').resize((300,300));sheet.paste(thumb,(850,200));text.text((850,175),'Gallery base ROI',fill='black')
        if winner['branch']!='union':text.text((800,140),'Legacy fallback: no invented quad',fill='black')
        name=f'{sample}-contribution-{rank+1}.jpg';sheet.save(out/name)
        doc+=f'<img src="runtime-v5/{name}"><p>Enrollment #{g["index"]}: {winner["branch"]}, distance {winner["score"]:.6f}; view_index={winner.get("view_index","Not applicable")}. This is a descriptor-view index within the template, not a candidate number in the illustration.</p>'
        evidence.append(dict(query=sample,case=case['case'],predicted=identity,gallery=target,winner=winner,image=name))
(out/'contributions.json').write_text(json.dumps(evidence,indent=2))
if '--images-only' in sys.argv:
    print(out/'contributions.json');raise SystemExit(0)
http=[]
for cohort in ['new','old']:
    r=read(base/f'http-v5-{cohort}/summary.json');assert r['originals_unchanged'] and r['demo_matcher']=='FastCCAnchoredUnion-v5'
    d=r['demo'];http.append([cohort,sum(t['result'].get('user_id')==t['identity'].replace(':','-') for t in d['probes']),len(d['probes']),sum(t['http_status']==200 for t in d['enrollments']),d['payment']['transactions']])
doc+='<h2>Local HTTP replay</h2>'+table([['Device','Correct','Queries','Enrollment','Simulated payment']]+http)
doc+='<p>Diagnostics and normal matching share the scoring function. Labels are not used to reselect winners; a winning legacy fallback is recorded without inventing a candidate region. A misplaced primary ROI could exclude a valid candidate, so independent-session validation remains necessary. The same 80 development images were reused. No Pi deployment or default DoN change.</p><p><a href="runtime-v5/pair-winners.json">Winners for all 3,120 pairs</a> · <a href="runtime-v5/results.json">All query results</a> · <a href="report-v4.html">Original v4 comparison</a> · <a href="../../../docs/ROI_PIPELINE.md">Pipeline guide</a></p></html>'
(out/'contributions.json').write_text(json.dumps(evidence,indent=2));(base/'report-v5.html').write_text(doc,encoding='utf-8')
print(json.dumps(http));print(base/'report-v5.html')
