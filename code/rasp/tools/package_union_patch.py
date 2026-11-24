"""Create a local versioned source patch after verification; never deploy."""
import hashlib
import json
from pathlib import Path
import sys
import zipfile

app=Path(__file__).resolve().parents[1];out=Path(sys.argv[1])/'single-device'
assert (out/'report-v4.html').is_file()
files=list(json.loads((out/'patch-manifest.json').read_text())['sha256'])
files+=['multiroi_matcher.py','union_matcher.py','window_roi.py','docs/ROI_PIPELINE.md',
        'deploy/make_deploy_bundle.ps1','tests/test_multiroi_matcher.py','tests/test_union_matcher.py',
        'tools/audit_registered_runtime.py','tools/audit_union_fresh_features.py','tools/audit_union_fresh_distances.py',
        'tools/verify_union_runtime.py','tools/write_union_report.py','tools/audit_hypothesis_union.py',
        'tools/audit_roi_hypotheses.py','tools/audit_expanded_query.py','tools/audit_localizer_windows.py']
manifest=dict(matcher='FastCCWindowUnion-v4',status='local validated source patch; not deployed',
              requires='Existing v5 models/dependencies; version-specific reenrollment; preserve accounts',
              scope='same device only; repeated development data, no independent generalization evidence',
              sha256={p:hashlib.sha256((app/p).read_bytes()).hexdigest() for p in sorted(set(files))})
(out/'patch-v4-manifest.json').write_text(json.dumps(manifest,indent=2))
with zipfile.ZipFile(out/'single-device-v4-patch.zip','x',compression=zipfile.ZIP_DEFLATED) as z:
    for p in manifest['sha256']:z.write(app/p,p)
    z.writestr('patch-v4-manifest.json',json.dumps(manifest,indent=2))
with zipfile.ZipFile(out/'single-device-v4-patch.zip') as z:
    assert all(hashlib.sha256(z.read(p)).hexdigest()==h for p,h in manifest['sha256'].items())
print(out/'single-device-v4-patch.zip')
