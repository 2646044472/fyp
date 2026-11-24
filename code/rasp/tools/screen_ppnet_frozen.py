"""Predeclared frozen PPNet screen, all current/development queries retained."""
import argparse,hashlib,html,io,json,sys,time,zipfile
from pathlib import Path
import cv2,numpy as np
from PIL import Image
APP=Path(__file__).resolve().parents[1];sys.path.insert(0,str(APP))
from biometric import load_algorithm
from ppnet_pilot import PPNetPilot
from compnet_context_pilot import confident_identity


def write_report(result,path):
    def table(headers,rows):
        return '<div class="scroll"><table><tr>'+''.join('<th>'+html.escape(str(v))+'</th>' for v in headers)+'</tr>'+''.join(
            '<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in row)+'</tr>' for row in rows)+'</table></div>'
    text='''<!doctype html><html lang="en"><meta charset="utf-8"><title>Frozen PPNet: minimal screen</title>
<style>body{font:16px/1.65 system-ui;max-width:1450px;margin:32px auto;padding:0 20px;color:#203044}h1{font-size:28px}.scroll{overflow:auto}table{width:100%;border-collapse:collapse;font-size:14px}td,th{padding:9px;border:1px solid #ccd5df;text-align:left}th{background:#eaf0f7}.notice{background:#fff3dd;border-left:4px solid #a86a16;padding:14px}code{overflow-wrap:anywhere}</style>
<h1>Frozen pretrained PPNet: can one shared vector replace full fallback?</h1><p>2026-10-30 · Rejection criteria declared before the minimal offline test · No training or deployment</p>'''
    text+='<p class="notice">'+('Screen passed; Pi acceptance testing has not been performed.' if result['screen_passed'] else 'Did not pass: '+html.escape(', '.join(result['kill_reasons'])))+' The current production algorithm and full Pi results are unchanged: 164/168 correct, 146/168 correct within 2.5 s, P95 6.019 s and maximum 15.225 s.</p>'
    text+='<p>This convolutional representation differs from CompNet. It extracts one 512-dimensional vector per original primary ROI and shares it across the gallery to try to bypass multiwindow localization, SIFT and per-template registration. Only the authors’ public Tongji600 weights were tested. No training on device or public evaluation images, relabeling, failure removal or person/file-specific tuning. All 169 active originals and four within-device enrollment directions were used. The historical cohort before removal is retained separately.</p>'
    text+='<h2>Screening results (not the full recognizer or Pi speed)</h2>'+table(['Dataset','Queries','Correct Euclidean ranking on original features','Correct unit-vector angular ranking','Confident at fixed gates','Of these, incorrect','Current full fallbacks avoided correctly'],[
        [name,s['total'],s['raw_ranking_correct'],s['angular_ranking_correct'],s['confident'],s['wrong_confident'],s['current_exhaustive_correct_confident']] for name,s in result['summary'].items()])
    text+='<p>The authors’ example uses Euclidean distance on unnormalized features. Unit-vector angular distance was a predeclared control, still requiring ≤0.32 and a lead ≥0.08. Identical numeric gates do not calibrate FAR across representations. All 4,480 historical split queries are previously seen, correlated regression evidence, not independent generalization evidence.</p>'
    records=[t for r in result['results'] if r['cohort']=='active169' for t in r['trials'] if t.get('v26_route')=='exhaustive_fallback']
    rows=[]
    for t in records:
        ranking=sorted(t['scores']['angular'].items(),key=lambda p:p[1]);a,b=ranking[:2]
        rows.append([t['sample'],t['identity'],a[0],t['angular_correct'],f'{a[1]:.6f}',f'{b[1]:.6f}',f'{b[1]-a[1]:.6f}',t['confident']])
    text+='<h2>All 13 full fallbacks retained individually</h2>'+table(['Sample','True identity','Top angular-distance identity','Correct ranking','Best','Runner-up','Gap','Confident'],rows)
    text+='<p>The hardest image can rank first, but its lead is insufficient. Correct ranking alone is not reliable early acceptance; the 0.08 gap must not be reduced for this sample. No unenrolled people were tested, so stranger FAR and verification FRR are unmeasured. Zero incorrect confident returns does not imply zero FAR.</p>'
    meta=result['protocol']['model']
    text+='<h2>Model and export checks</h2><p>Author weights loaded with weights_only=True and a strict complete state match. The classification head was not used in inference. Original grayscale images were 128 pixels square; nonblack pixels were normalized with the authors’ mean and sample standard deviation. The model has about '+f"{meta['parameters']/1e6:.2f}"+'M parameters including the unused classification head. No random feature layer was substituted.</p>'
    text+=table(['Export sample','Maximum absolute raw-feature error','Maximum absolute unit-vector error'],[[i,e['raw_max_abs'],e['normalized_max_abs']] for i,e in enumerate(meta['export_parity'])])
    text+=table(['File','SHA256'],[[name,meta[key]] for name,key in [('Authors’ source code','source_sha256'),('Authors’ checkpoint','checkpoint_sha256'),('ONNX','onnx_sha256')]])
    text+='<h2>Stopping condition and outcome</h2><p>The predeclared rule skipped full Pi testing if any confident return was wrong or no current full fallback was newly covered. The latter occurred, so this configuration stopped. No alternative weights, preprocessing or weaker thresholds were searched to rescue exposed images. The running recognizer was not replaced. There are no PPNet Pi first-run, warm, HTTP, enrollment or readiness timings; local offline timings are not Pi latency.</p>'
    text+='<p>Weights and author code remain in ignored local directories and are not distributed with Git. No original biometric images were uploaded. <a href="https://github.com/xuliangcs/ppnet">Authors’ implementation</a> · <a href="../../compnet-v26-pi-20261030/report.html">Current full v26 Pi baseline</a>.</p></html>'
    path.write_text(text,encoding='utf-8')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('cohort',type=Path);p.add_argument('geometry',type=Path);p.add_argument('model',type=Path)
    p.add_argument('reference',type=Path);p.add_argument('development',type=Path);p.add_argument('output',type=Path);args=p.parse_args()
    rows=json.loads((args.cohort/'manifest.json').read_text());cohort=json.loads((args.cohort/'protocol.json').read_text())
    reference=json.loads(args.reference.read_text());assert reference['complete']
    refs={(r['case'],q['sample']):q for r in reference['runs'] for q in r['queries']}
    quads={r['sample']:np.asarray(r['quad'],np.float32) for r in json.loads(args.geometry.read_text())['records']}
    lookup={r['sample']:i for i,r in enumerate(rows)};truth={r['sample']:r['identity'] for r in rows}
    args.output.mkdir(exist_ok=False,parents=True);cv2.setNumThreads(1);encoder=PPNetPilot(args.model)
    algorithm=load_algorithm(APP/'vendor/palmprint-recognition-python',cohort['matcher'])
    protocol=dict(method='Single saved primary ROI; frozen author PPNet Tongji600; original five-frame best2 aggregation',
        controls=['Author raw-feature Euclidean ranking','Experimental unit-vector angular distance, unchanged nominal .32/.08'],
        kill_criteria='Any wrong confident angular result on current/development trials OR no correct confident current exhaustive query; no checkpoint/preprocess tuning',
        model=encoder.metadata,training_on_device_data=False,independent_validation=False,
        timing_scope='Offline original/geometry/feature reuse; not actual Pi HTTP latency',
        source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in
            [Path(__file__),APP/'ppnet_pilot.py',args.geometry,args.reference,args.development,args.cohort/'manifest.json']})
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2))
    raw=[];unit=[];started=time.perf_counter();repo=APP.parents[1]
    try:
        for row in rows:
            with zipfile.ZipFile(repo/row['archive']) as z:value=z.read(row['archive_member'])
            assert hashlib.sha256(value).hexdigest()==row['sha256']
            native=cv2.cvtColor(np.asarray(Image.open(io.BytesIO(value)).convert('RGB')),cv2.COLOR_RGB2GRAY)
            pixels=algorithm.geometry.getROIimg(native,quads[row['sample']])
            a,b=encoder.extract(Image.fromarray(pixels));raw.append(a);unit.append(b)
        raw=np.asarray(raw);unit=np.asarray(unit);a=raw.astype(np.float64);norm=np.sum(a*a,axis=1)
        euclidean=np.sqrt(np.maximum(norm[:,None]+norm[None,:]-2*a@a.T,0))
        angular=np.arccos(np.clip(unit@unit.T,-1,1))/np.pi
        cases=[dict(case=c['name'],gallery=c['enrollment'],trials=[dict(sample=s,identity=truth[s]) for s in c['queries']],cohort='active169') for c in cohort['cases']]
        cases.extend(dict(c,cohort='development') for c in json.loads(args.development.read_text()))
        results=[]
        for case in cases:
            enrolled={u:[lookup[s] for s in ss] for u,ss in case['gallery'].items()};trials=[]
            assert not ({t['sample'] for t in case['trials']}&{s for ss in case['gallery'].values() for s in ss})
            for trial in case['trials']:
                i=lookup[trial['sample']]
                scores={name:{u:float(np.sort(m[i,ids])[:2].mean()) for u,ids in enrolled.items()}
                    for name,m in [('euclidean',euclidean),('angular',angular)]}
                pred={k:min(s,key=s.get) for k,s in scores.items()};confident=confident_identity(scores['angular'])
                t=dict(sample=trial['sample'],identity=trial['identity'],predicted=pred,
                    raw_correct=pred['euclidean']==trial['identity'],angular_correct=pred['angular']==trial['identity'],
                    confident=confident is not None,confident_correct=confident==trial['identity'],scores=scores)
                if case['cohort']=='active169':t['v26_route']=refs[case['case'],trial['sample']]['result']['recognition_route']
                trials.append(t)
            results.append(dict(case=case['case'],cohort=case['cohort'],trials=trials))
        summary={}
        for name in ('active169','development'):
            trials=[t for r in results if r['cohort']==name for t in r['trials']]
            summary[name]=dict(total=len(trials),raw_ranking_correct=sum(t['raw_correct'] for t in trials),
                angular_ranking_correct=sum(t['angular_correct'] for t in trials),confident=sum(t['confident'] for t in trials),
                wrong_confident=sum(t['confident'] and not t['confident_correct'] for t in trials),
                current_exhaustive_correct_confident=sum(t['confident_correct'] and t.get('v26_route')=='exhaustive_fallback' for t in trials))
        reasons=[]
        if any(s['wrong_confident'] for s in summary.values()):reasons.append('Wrong confident angular result')
        if summary['active169']['current_exhaustive_correct_confident']==0:reasons.append('No current exhaustive rescue')
        result=dict(protocol=protocol,summary=summary,results=results,screen_passed=not reasons,kill_reasons=reasons,
            complete=True,elapsed_offline_seconds=time.perf_counter()-started)
        np.savez_compressed(args.output/'features-and-distances.npz',raw=raw,unit=unit,euclidean=euclidean,angular=angular)
        (args.output/'results.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(summary=summary,screen_passed=not reasons,kill_reasons=reasons)),flush=True)
        write_report(result,args.output/'report.html')
    finally:algorithm.close()


if __name__=='__main__':main()
