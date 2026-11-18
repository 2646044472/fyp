"""Aggregate scoped public validation; never exports images or templates."""
import argparse,collections,html,json
from pathlib import Path
import numpy as np
from evaluate_frozen_public import canonical,sha


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path);p.add_argument('prior_casia',type=Path);args=p.parse_args()
    root=args.root;protocol=json.loads((root/'protocol.json').read_text());casia=json.loads((root/'casia-v26/results.json').read_text())
    roi=json.loads((root/'palmbig-local/results.json').read_text());prior=json.loads(args.prior_casia.read_text())
    kernel=json.loads((root/'kernel-audit-summary.json').read_text());pixels=json.loads((root/'pixel-exposure-audit.json').read_text())
    assert casia['complete'] and roi['complete'] and casia['protocol_sha256']==roi['protocol_sha256']==sha(root/'protocol.json')
    assert casia['originals_unchanged'] and casia['models_unchanged'] and casia['kernel_unchanged'] and casia['transactions_unchanged']
    assert pixels['decoded_pixel_overlap']==0 and set(x['get_throttled'] for x in casia['power_samples'])=={'throttled=0x0'}
    previous=next(r for r in prior['runs'] if r['version']=='v13')
    aggregate=dict(protocol_canonical_sha256=canonical(protocol),frozen_algorithm_commit=protocol['frozen_commit'],
        casia_prior_v13=previous['summary'],casia_v26_passes=[dict(name=r['name'],**r['summary']) for r in casia['passes']],
        casia_initialization_empty_gallery_ms=casia['initialization_ready_ms']['total_ms'],
        casia_enrollment_requests_ms=[e['request_ms'] for e in casia['enrollments']],
        casia_enrollment_successes=sum(e['http_status']==200 and e['result'].get('recognition_ready',False) for e in casia['enrollments']),
        casia_additional_ready_check_ms=casia['post_enrollment_gallery_ready_ms'],
        casia_cancellation_ok=all(t.get('cancelled',False) for r in casia['passes'] for t in r['queries']),
        casia_explicit_rejects=[sum(t['result']['status']=='REJECT' for t in r['queries']) for r in casia['passes']],
        casia_wrong_identity_matches=[sum(not t['correct'] and t['result']['status']=='MATCH' for t in r['queries']) for r in casia['passes']],
        palmbig_inventory={k:v for k,v in protocol['palmbig'].items() if k!='subset_member_sha256'},
        palmbig_local=[dict(prefix=r['prefix'],classes=r['filename_classes'],images=r['images'],**r['summary']) for r in roi['cohorts']],
        palmbig_failures=len(roi['failures']),kernel_environment_audit=kernel,pixel_exposure_audit=pixels,
        new_device_session_validated=False,unknown_person_validation=False,algorithm_tuned=False,raw_biometric_transfer=False,
        production_changed=False,complete=True)
    save=root/'aggregate.json';save.write_text(json.dumps(aggregate,indent=2))
    def table(headers,rows):
        return '<div class="scroll"><table><tr>'+''.join('<th>'+html.escape(str(v))+'</th>' for v in headers)+'</tr>'+''.join('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in row)+'</tr>' for row in rows)+'</table></div>'
    text='''<!doctype html><html lang="en"><meta charset="utf-8"><title>Frozen v26: confirmatory public-data evaluation</title>
<style>body{font:16px/1.65 system-ui;max-width:1450px;margin:32px auto;padding:0 20px;color:#203044}h1{font-size:28px}.scroll{overflow:auto}table{width:100%;border-collapse:collapse;font-size:14px}th,td{padding:9px;border:1px solid #cbd5df;text-align:left}th{background:#eaf0f7}.notice{background:#fff3dd;border-left:4px solid #ac7018;padding:14px}code{overflow-wrap:anywhere}</style>
<h1>Frozen v26: limited-scope public-data validation</h1><p>2026-10-30 · Evaluation only; no optimization, training, tuning or production switch</p>
<p class="notice">CASIA confirms v26 behavior on 24 previously seen images. PalmBigDataBase tests only the local FastCC component on precropped ROIs. Neither resolves the hardest device query: the device baseline remains 164/168 correct, 146/168 correct within the deadline and 15.225 s maximum. New sessions and unenrolled participants remain untested.</p>'''
    text+='<h2>CASIA 850 nm: full Pi enrollment and recognition request replay, excluding capture</h2><p>Subjects 001–004, left hand, 850 nm, six images per class: five for fresh enrollment and the sixth for querying, with the original fixed ordering seed. The 24 copies already on the Pi were hash-verified individually and read without transferring originals. v13 used the same samples; this is not independent new validation. Warm repeats use the same four queries, not four additional test samples.</p>'
    rows=[]
    for name,s in [('Historical v13 record',previous['summary'])]+[(r['name'],r['summary']) for r in casia['passes']]:
        rows.append([name,s['total'],s['correct'],s['correct_within_2_5s'],f"{s['median_ms']/1000:.3f}",f"{s['p95_ms']/1000:.3f}",f"{s['max_ms']/1000:.3f}"])
    text+=table(['Run','Queries','Correct','Correct within 2.5 s','P50 (s)','P95 (s)','Maximum (s)'],rows)
    text+='<p>Query time includes reading the original, localization, feature extraction, gallery scoring and local HTTP, but excludes camera capture, hand placement, Wi-Fi upload, initialization and enrollment waits. Historical v13 reused v12 enrollment payloads; v26 enrolled afresh. Timing differences cannot all be attributed to a single algorithm change. Each round had zero wrong-identity MATCH results and zero explicit REJECT results. All subjects were enrolled, so neither stranger FAR nor verification FRR can be estimated here.</p>'
    text+='<h2>Enrollment and ready time, reported separately</h2>'+table(['Operation','Milliseconds'],[
        ['Empty-gallery app initialization and primary model warm-up',f"{aggregate['casia_initialization_empty_gallery_ms']:.3f}"],
        *[['Five-frame enrollment request per class, including gallery preparation',f"{e['request_ms']:.3f}"] for e in casia['enrollments']],
        ['Additional readiness check after all four classes',f"{aggregate['casia_additional_ready_check_ms']:.3f}"]])
    text+='<p>All four enrollments succeeded. The API had already prepared the gallery; the final ~0.35 ms measured only a cached readiness check, not all gallery preparation. Enrollment replayed saved originals rather than timing five live captures. All token cancellations passed, simulated transaction counts and original images/models were unchanged, and all power flags were 0x0.</p>'
    info=protocol['palmbig']
    text+='<h2>PalmBigDataBase: archive metadata and previous exposure</h2>'+table(['Operation','Result'],[
        ['BMP entries',info['bmp_images']],['All image dimensions',info['dimensions']],['F/S image counts',info['prefix_images']],
        ['Prefix-defined classes',info['filename_classes']],['Numeric IDs',info['numeric_ids']],['Classes per F/S prefix',info['prefix_classes']],
        ['Participant count and whether F/S denotes sessions or devices','Not documented in the archive; no inference made'],['Sample-count distribution',info['sample_count_histogram']],
        ['Previously exposed range','IDs 1–20: 400 images previously tested; IDs 21–60: traces in the old public40 package/tools, conservatively excluded'],
        ['New frozen range','IDs 61–80, separate F/S galleries; five enrollment images and all remaining images queried'],['Duplicates between the new range and IDs 1–60 (bytes / decoded pixels)','0 / 0']])
    text+='<h2>Local ROI component only</h2>'+table(['Prefix','Filename-defined classes','Images','Queries','Correct top ranks','P50 (ms)','P95 (ms)','Maximum (ms)'],[
        [r['prefix'],r['filename_classes'],r['images'],r['summary']['total'],r['summary']['correct'],*[f"{r['summary'][k]:.3f}" for k in ('median_ms','p95_ms','max_ms')]] for r in roi['cohorts']])
    text+='<p>Failures'+str(len(roi['failures']))+'; all 200 queries retained. Only existing 128×128 grayscale normalization, FastCC extraction, best-two-frame averaging and full-gallery ranking ran. Localization, geometric rescue, CompNet routing and HTTP were absent; this is not the full v26 pipeline. Windows time covers ROI reading from a previously accessed archive, decoding, normalization, extraction and matching. It is neither Pi latency nor cold-disk I/O. F/S galleries were separate; there is no cross-prefix matching or evidence of cross-session/device generalization.</p>'
    text+='<h2>Frozen inputs and runtime differences</h2><p>Frozen algorithm commit: <code>'+protocol['frozen_commit']+'</code>; protocol semantic SHA-256: <code>'+aggregate['protocol_canonical_sha256']+'</code>. Hashes of the protocol, core code, pretrained model and source samples were checked before and after testing. No reselection, threshold tuning or training followed the results. Original public data, images, templates and weights are not committed to Git.</p>'
    text+='<p>Windows: NumPy 2.3.5/OpenCV 5.0.0; Pi: NumPy 2.2.4/OpenCV 4.10.0. FastCC and kernel-generation source matched, but final floating-point digits differed. Maximum Gabor coefficient difference: '+str(kernel['max_all_gabor_kernels'])+'. Each platform froze its kernel before reading inputs and verified it was unchanged afterward; cross-platform bitwise equality is not claimed.</p>'
    text+='<p>New device sessions and unenrolled participants were left untouched; both independent checks remain outstanding. Clean public ROIs cannot establish success rates or tail latency on low-quality device originals.</p></html>'
    (root/'report.html').write_text(text,encoding='utf-8');print(save)


if __name__=='__main__':main()
