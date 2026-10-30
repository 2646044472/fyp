"""Read-only stopped-SMPD version boundary; no query outcomes used for tuning."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import platform
import sys
import zipfile

import numpy as np

import evaluate_raw_smpd as original
from resume_raw_smpd import remaining
from terminal_rf_evidence import POLICY
from audit_halfturn_recovery import source_sha,save
from union_matcher import FEATURE_SIZE


def read_feature_schema(path,expected_shape=None):
    """Read only NPY header and four-byte format tag; never load feature arrays."""
    with zipfile.ZipFile(path) as archive:
        if archive.namelist()!=['feature.npy']:raise ValueError('Unexpected prepared-feature container fields')
        with archive.open('feature.npy') as stream:
            version=np.lib.format.read_magic(stream)
            if version==(1,0):shape,fortran,dtype=np.lib.format.read_array_header_1_0(stream)
            elif version==(2,0):shape,fortran,dtype=np.lib.format.read_array_header_2_0(stream)
            else:raise ValueError('Unsupported NPY feature-header version')
            if dtype!=np.dtype('uint8') or fortran:raise ValueError('Unexpected feature dtype/order')
            if expected_shape is not None and tuple(shape)!=tuple(expected_shape):raise ValueError('Unexpected feature shape')
            tag=stream.read(4)
            if len(tag)!=4 or int.from_bytes(tag,'little',signed=True)!=2801066:
                raise ValueError('Prepared feature does not have the frozen v26 format tag')
    return dict(shape=list(shape),dtype=dtype.str,fortran_order=fortran,npy_version=list(version),magic=2801066)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--model',required=True,type=Path);p.add_argument('--local-result',type=Path);a=p.parse_args()
    receipt_path=a.root/'stop-receipt-20261030-144708/receipt.json';receipt=json.loads(receipt_path.read_text())
    ledger=a.root/'evaluation/queries.jsonl';result=a.root/'evaluation/results.json'
    assert original.sha(ledger)==receipt['queries_jsonl_sha256'] and original.sha(result)==receipt['results_sha256']
    raw=ledger.read_bytes();queries=[json.loads(line) for line in raw.splitlines() if line]
    historical=json.loads(result.read_text())
    assert raw.endswith(b'\n') and queries==historical['queries']
    rows=json.loads((a.root/'prepared/manifest.json').read_text());todo=remaining(rows,queries)
    assert len(queries)==241 and len(todo)==2976
    protocol=json.loads((a.root/'protocol.json').read_text());original.verify(protocol)
    assert historical['protocol_sha256']==original.sha(a.root/'protocol.json')
    dependencies=json.loads((a.root/'dependency-lock.json').read_text())
    for path,digest in dependencies['source_sha256'].items():assert original.source_sha(path)==digest,path
    download=json.loads((a.root/'SMPD.download.json').read_text());prepared=json.loads((a.root/'prepared/progress.json').read_text())
    assert download['complete'] and download['zip_crc_checked'] and prepared['complete']
    assert historical['archive_sha256']==download['sha256']
    assert prepared['manifest_sha256']==original.sha(a.root/'prepared/manifest.json')
    assert protocol['inventory_sha256']==original.sha(a.root/'zip-inventory.json')
    assert len(rows)==len(protocol['samples'])==3677
    declared={r['member']:{k:r[k] for k in ('identity','subject','condition','index','enrollment')} for r in protocol['samples']}
    assert len(declared)==3677 and set(declared)=={r['member'] for r in rows}
    assert all(declared[r['member']]=={k:r[k] for k in ('identity','subject','condition','index','enrollment')} for r in rows)
    enrollments=json.loads((a.root/'evaluation/enrollments.json').read_text())
    assert enrollments==historical['enrollments'] and len(enrollments)==92
    for entry in enrollments:
        selected=sorted((r for r in rows if r['identity']==entry['identity'] and r['enrollment']),key=lambda r:r['index'])
        assert len(selected)==5 and entry['samples']==[r['sample'] for r in selected]
        assert entry['registered']==all(r.get('enrollment_feature_ok') for r in selected)
    assert sum(e['registered'] for e in enrollments)==historical['actual_gallery_identities']==76
    compnet=original.sha(a.model/'compnet-tongji.onnx');pklnet=original.sha(original.PKLNetROI().root/'pklnet-keypoints-diagnostics.onnx')
    assert compnet==protocol['model_sha256']['compnet'] and pklnet==protocol['model_sha256']['pklnet']
    paths=[original.APP/'tools'/name for name in ('terminal_rf_evidence.py','fastcc_valid_support.py','retained_evidence_pilot.py')]
    candidate=dict(policy=POLICY,helper_sha256={p.name:source_sha(p) for p in paths},model_sha256=dict(compnet=compnet,pklnet=pklnet),
        original_source_sha256=protocol['source_sha256'],thresholds=protocol['thresholds'],rejection=False)
    local=json.loads(a.local_result.read_text()) if a.local_result and a.local_result.exists() else None
    qualified=bool(local and local.get('complete') and local.get('local_candidate_pass'))
    if qualified:
        assert local['candidate_sha256']==candidate['helper_sha256']['terminal_rf_evidence.py']
        assert local['kernel_sha256']==candidate['helper_sha256']['fastcc_valid_support.py']
        assert local['helper_sha256']==candidate['helper_sha256']['retained_evidence_pilot.py']
        assert local['evaluator_sha256']==source_sha(original.APP/'tools/replay_terminal_rf_device.py')
        assert local['model_sha256']==compnet and not local['thresholds']['rejection']
        assert all(local['thresholds'][k]==v for k,v in protocol['thresholds'].items())
        assert len(local['enrollment_feature_parity'])==34 and all(e['equal'] for e in local['enrollment_feature_parity'])
    feature_files=[r for r in rows if r.get('enrollment_feature_ok')]
    assert len(feature_files)==417
    schemas=Counter()
    for row in feature_files:
        assert original.sha(row['enrollment_feature'])==row['enrollment_feature_sha256']
        schema=read_feature_schema(row['enrollment_feature'],expected_shape=(FEATURE_SIZE,))
        schemas[json.dumps(schema,sort_keys=True)]+=1
    feature_protocol=dict(roi_geometry=original.ROI_GEOMETRY_VERSION,schemas=[dict(schema=json.loads(s),files=n) for s,n in sorted(schemas.items())],
        prepared_manifest_sha256=prepared['manifest_sha256'],
        feature_container_manifest_sha256=hashlib.sha256(json.dumps(sorted((r['sample'],r['enrollment_feature_sha256']) for r in feature_files)).encode()).hexdigest())
    split_path=original.APP/'docs/protocols/SMPD_PROSPECTIVE_OPTIMIZATION_SPLIT_20261030.json'
    split=json.loads(split_path.read_text());development=set(split['development_subjects']);reserved=set(split['reserved_subjects'])
    subjects={r['subject'] for r in rows}
    assert not development&reserved and development|reserved==subjects
    assert all(int(s)%5==0 for s in reserved) and all(int(s)%5!=0 for s in development)
    dev_queries=sum(not r['enrollment'] and r['subject'] in development for r in rows)
    reserved_queries=sum(not r['enrollment'] and r['subject'] in reserved for r in rows)
    assert (dev_queries,reserved_queries)==(2588,629)==(split['development_queries'],split['reserved_queries'])
    assert split['source_inventory_sha256']==protocol['inventory_sha256']
    assert split['original_manifest_sha256']==prepared['manifest_sha256']
    byte_groups={}
    for row in rows:byte_groups.setdefault(row['sha256'],[]).append(row)
    enrollment_hashes={r['sha256'] for r in rows if r['enrollment']}
    duplicate_summary=dict(unique_file_contents=len(byte_groups),redundant_files=len(rows)-len(byte_groups),
        duplicate_groups=sum(len(g)>1 for g in byte_groups.values()),
        cross_identity_byte_conflicts=sum(len({r['identity'] for r in group})>1 for group in byte_groups.values()),
        query_files_overlapping_enrollment=sum(not r['enrollment'] and r['sha256'] in enrollment_hashes for r in rows),
        unique_query_byte_contents=len({r['sha256'] for r in rows if not r['enrollment']}),
        method='Existing source-byte SHA256 metadata only, not a new pixel/perceptual duplicate audit.',
        primary_denominator='All original release files; no outcome-driven removal.')
    environment=dict(python=sys.version,platform=platform.platform(),numpy=np.__version__,opencv=original.cv2.__version__)
    historical_environment=protocol['environment']
    report=dict(complete=True,read_only=True,checkpoint_queries=241,expected_queries=3217,remaining_queries=2976,
        last_completed=queries[-1]['sample'],next_original_baseline=todo[0]['sample'],
        result_sha256=original.sha(result),ledger_sha256=original.sha(ledger),receipt_sha256=original.sha(receipt_path),
        source_and_dependency_locks_valid=True,archive_crc_verified_at_download=True,archive_crc_rechecked_by_this_audit=False,prepared_feature_files_hashed=417,
        historical_protocol_sha256=historical['protocol_sha256'],historical_archive_sha256=historical['archive_sha256'],
        checkpoint_record_fields=sorted(set().union(*(q.keys() for q in queries))),
        checkpoint_result_fields=sorted(set().union(*(q['result'].keys() for q in queries))),
        protocol_manifest_equal=True,gallery_registration_manifest_equal=True,registered_identities=76,
        feature_protocol=feature_protocol,feature_protocol_sha256=hashlib.sha256(json.dumps(feature_protocol,sort_keys=True).encode()).hexdigest(),
        audit_source_sha256=source_sha(__file__),remaining_validator_sha256=source_sha(original.APP/'tools/resume_raw_smpd.py'),
        strict_unique_ordered_prefix_validated=True,
        prospective_split=dict(sha256=original.sha(split_path),development_people=len(development),reserved_people=len(reserved),
            development_queries=dev_queries,reserved_queries=reserved_queries,source_inventory_and_manifest_match=True,
            meaning='Prospective protection from later tuning, not a never-evaluated blind cohort. Entire SMPD treated as seen public data.'),
        duplicates=duplicate_summary,current_environment=environment,
        historical_environment=historical_environment,
        recorded_python_numpy_opencv_equal=all(environment[k]==historical_environment[k] for k in ('python','numpy','opencv')),
        old_scoring_policy='v26 retained ordinary FastCC, including ordinary terminal score vector',
        candidate=candidate,candidate_fingerprint=hashlib.sha256(json.dumps(candidate,sort_keys=True).encode()).hexdigest(),
        score_prefix_compatible_with_candidate=False,
        reason='Terminal score definition changed while original confident paths are preserved. Same models/feature representation do not make old query scores candidate outcomes.',
        feature_representation_sources_equal=True,
        candidate_feature_reuse=False,
        action='Future protocol requirement: preserve old241; a separate frozen candidate evaluation needs fresh original-image enrollments and all3217 queries. No append/merge of old scores. Not launched by this audit.',
        public_evaluation_started=False,
        future_execution_lock_complete=False,
        future_execution_isolation_enforced=False,
        local_candidate_qualified=qualified,
        local_result_sha256=original.sha(a.local_result) if qualified else None,
        public_tuning_allowed=False,pi_timing_claim=False,
        limits=['This audit inspects checkpoint equality/order/hashes, not per-query correctness or reserved failure images.',
            'Read-only source-data audit writes a new scalar report; it does not alter old checkpoint, feature containers or manifest.',
            'No fresh whole-archive CRC or every-original-image byte scan is performed here; historical CRC record and metadata provenance are disclosed.',
            'Same feature extractor/model sources are established, but old feature arrays are not reused for the new candidate protocol.',
            'Known development exposure includes source images001, partial scalar outputs002 and half-turn analysis/pilot008. No independent generalization claim.',
            'This boundary audit is not a complete frozen public execution protocol: future evaluation/resume scripts and environment locks must be finalized before first query.',
            'CASIA/PalmBig completed same-version protocols are not reused for tuning; closed set does not establish stranger rejection.'])
    assert not a.output.exists();save(a.output,report)
    assert original.sha(ledger)==receipt['queries_jsonl_sha256'] and original.sha(result)==receipt['results_sha256']
    print(json.dumps({k:report[k] for k in ('checkpoint_queries','remaining_queries','source_and_dependency_locks_valid','score_prefix_compatible_with_candidate','candidate_feature_reuse','local_candidate_qualified')}))


if __name__=='__main__':main()
