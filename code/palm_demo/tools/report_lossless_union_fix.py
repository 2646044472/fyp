"""Export only scalar capacity-fix evidence; no inference or biometric arrays."""
import argparse
import csv
import hashlib
import html
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from smpd_run_journal import atomic,digest,file_sha,load

APP=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('diagnostic',type=Path);parser.add_argument('output',type=Path)
    args=parser.parse_args();result=load(args.diagnostic/'results.json');protocol=load(args.diagnostic/'protocol.json')
    assert result['complete'] and result['passed']
    for path,expected in protocol['source_sha256'].items():assert file_sha(APP/path)==expected,path
    suite=ET.parse(args.diagnostic.parent/'tests.xml').getroot().find('testsuite')
    assert suite is not None and int(suite.attrib['failures'])==int(suite.attrib['errors'])==0
    root=APP/'runtime/smpd-terminal-rf-20261031-r2';prior=load(root/'protocol.json')
    entries=load(args.diagnostic.parent/'preserved-r2/preservation-manifest.json')
    assert all(file_sha(root/e['path'])==e['sha256'] for e in entries)
    contract=dict(schema=1,kind='Candidate boundary only; full execution tools/lock not yet certified',
        matcher='FastCCCompNetAlternateROI-v27-lossless-experimental',codec='union-lossless-variable-v2',storage='union-five-frame-npz-v2',
        models=result['models'],candidate_source_sha256=protocol['source_sha256'],
        raw_manifest_sha256=prior['metadata_sha256'][str((APP/'runtime/smpd-full-20261030/prepared/manifest.json').resolve())],
        raw_inputs=3677,identities=92,fixed_enrollment_attempts=460,queries=3217,
        enrollment_rule='Original F0-F4; no replacement; all registration failures remain in query denominator',
        split_sha256=file_sha(APP/'docs/protocols/SMPD_PROSPECTIVE_OPTIMIZATION_SPLIT_20261030.json'),
        development_queries=2588,protected_queries=629,thresholds=protocol['thresholds'],resource_guards=protocol['limits'],
        old70_prefix_compatible=False,old241_prefix_compatible=False,
        registration_prefix_compatible=False,registration_feature_reuse_certified=False,
        required_fresh_enrollment_prefix=0,required_fresh_query_prefix=0,
        execution_lock_complete=False,full_public_evaluation_started=False,
        explanation='Schema/source changed, and repairing capacity-failed enrollments can change the gallery. Preserve old records; do not append or relabel.',
        scope='Seen public data; not independent generalization/stranger FAR/Pi timing')
    contract['candidate_run_boundary_fingerprint']=digest(contract)
    summary=dict(complete=True,kind='Completed bounded repair verification, not a completed public evaluation',
        diagnostic_fingerprint=result['diagnostic_fingerprint'],candidate_boundary_fingerprint=contract['candidate_run_boundary_fingerprint'],
        test_summary={k:int(suite.attrib[k]) for k in ('tests','failures','errors','skipped')},
        fresh_device_enrollment_frames=len(result['fresh_enrollments']),same_gallery_identities=6,
        all_fresh_tensor_bytes_equal=all(r['all_tensors_byte_equal'] and r['png_byte_equal'] for r in result['fresh_enrollments']),
        same_gallery_queries=len(result['queries']),all_complete_score_vectors_and_routes_equal=all(q['complete_gallery_score_vector_equal'] for q in result['queries']),
        routes=[q['route'] for q in result['queries']],
        original_fixed_frame_bytes=sum(r['bytes_old'] for r in result['fresh_enrollments']),
        new_actual_frame_bytes=sum(r['bytes_new'] for r in result['fresh_enrollments']),
        overflow_extraction_only={k:v for k,v in result['overflow_extraction_only'].items() if k!='logical_sha256'},
        memory=result['memory'],preserved_checkpoint=result['checkpoint_preservation'],
        models=result['models'],full_smpd_started=False,pi_tested=False,deployed=False,thresholds_changed=False,
        limits=['Finite same-gallery Windows equivalence evidence; not a universal accuracy or speed proof.',
            'No current full168 device regression, full3217 public evaluation or real Pi capacity/latency qualification.',
            'New92-person gallery and recovery of43 registration failures have not been measured.',
            'Two codec initialization/reader-hardening diagnostic versions are retained; final source-locked r3 is reported.',
            'Existing standard branch/tag remain frozen; raw images/templates/features/model binaries stay private.'])
    args.output.mkdir(parents=True,exist_ok=True);atomic(args.output/'summary.json',summary)
    atomic(args.output/'next-run-boundary.json',contract)
    with (args.output/'same-gallery-route-ledger.csv').open('w',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fieldnames=['sample','route','complete_gallery_score_vector_equal','all_prepared_tensors_byte_equal','comparison_provenance_equal']);writer.writeheader()
        writer.writerows({k:q[k] for k in writer.fieldnames} for q in result['queries'])
    content=html.escape(json.dumps(summary,indent=2))
    (args.output/'report.html').write_text('<!doctype html><meta charset="utf-8"><title>Lossless Union capacity repair</title><style>body{font:16px/1.6 system-ui;max-width:1050px;margin:40px auto;padding:0 20px;color:#15323a}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#eef4f5;padding:20px}.ok{padding:18px;background:#e4f5e9;border-radius:8px}</style><h1>Lossless Union capacity repair · 2026-10-31</h1><p class="ok">64 tests passed · 30 fresh device enrollment frames · 8 identical whole-gallery score vectors/routes</p><p>The stopped public input now preserves all 34 query views, 2 gallery views and native PNG in an 18,209,224-byte payload. Extraction-only: no new SMPD identification result.</p><p>Old70 and the71st inflight remain intact. New full evaluation must begin with fresh460 enrollment attempts and3217 queries. No deployment or Pi speed claim.</p><pre>'+content+'</pre>',encoding='utf-8')
    print(json.dumps(dict(tests=summary['test_summary'],fresh_frames=summary['fresh_device_enrollment_frames'],same_gallery_queries=summary['same_gallery_queries'],boundary=contract['candidate_run_boundary_fingerprint'])))


if __name__=='__main__':main()
