"""Reuse compatible isolated v10 enrollment for a v12/v13 query-only experiment.

No production migration: copied templates change only their outer version tag.
No query images/features/answers are computed or cached here. Preparation time
must not be reported as fresh enrollment time.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from staged_index_matcher import StagedIndexMatcher
from linked_enrollment_matcher import LinkedEnrollmentMatcher
from affine_enrollment_matcher import AffineEnrollmentMatcher
from templates import TemplateStore
from union_matcher import FEATURE_SIZE


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source',type=Path)
    p.add_argument('output',type=Path)
    p.add_argument('--matcher', choices=(LinkedEnrollmentMatcher.name, AffineEnrollmentMatcher.name), default=LinkedEnrollmentMatcher.name)
    args=p.parse_args()
    candidate = AffineEnrollmentMatcher if args.matcher == AffineEnrollmentMatcher.name else LinkedEnrollmentMatcher
    if args.output.resolve().is_relative_to(args.source.resolve()):
        raise ValueError('Output must be outside the source replay')
    summary=json.loads((args.source/'summary.json').read_text())
    assert summary['live_camera_tested'] is False
    assert summary['matcher']==StagedIndexMatcher.name
    assert args.source.name.startswith('http-staged-native-')
    args.output.mkdir(parents=True,exist_ok=False)
    shutil.copy2(args.source/'input-manifest.json',args.output/'input-manifest.json')
    shutil.copytree(args.source/'demo_runtime',args.output/'demo_runtime')
    store=TemplateStore(args.output/'demo_runtime/demo_templates')
    if not store.list_users():
        raise ValueError('Source replay has no enrollment templates')
    records=[]
    for user in store.list_users():
        features,metadata=store.load(user)
        assert metadata['algorithm']==StagedIndexMatcher.name
        assert features.dtype==np.uint8 and features.shape==(5,FEATURE_SIZE)
        assert all(f[:4].view('<i4')[0]==StagedIndexMatcher.magic for f in features)
        payload=hashlib.sha256(features[:,4:].tobytes()).hexdigest()
        for feature in features:
            feature[:4]=np.asarray([candidate.magic],'<i4').view(np.uint8)
        metadata['algorithm']=candidate.name
        store.save(user,features,metadata)
        saved,_=store.load(user)
        assert hashlib.sha256(saved[:,4:].tobytes()).hexdigest()==payload
        records.append(dict(user=user,payload_sha256=payload,samples=len(features)))
    # Preserve model provenance and input metadata, but do not copy v10 results
    # into a new candidate's summary as if they had been measured on v12.
    result={key:summary[key] for key in ('localizer_root','localizer_sha256') if key in summary}
    result.update(matcher=candidate.name,live_camera_tested=False,
                  enrollment_reused_from=str(args.source.resolve()),fresh_enrollment_measured=False)
    (args.output/'summary.json').write_text(json.dumps(result,indent=2))
    (args.output/'enrollment-reuse.json').write_text(json.dumps(records,indent=2))
    print('Copied and verified enrollment payloads for',len(records),'users',flush=True)


if __name__=='__main__':
    main()
