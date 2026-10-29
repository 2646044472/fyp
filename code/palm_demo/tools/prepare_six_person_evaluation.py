"""Freeze all 120 local captures into two 11-identity evaluation protocols.

Original archives remain unchanged. Pi paths are reused only after matching
sample IDs and original JPEG SHA-256, never by recognition outcome.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('collection',type=Path)
    p.add_argument('output',type=Path)
    p.add_argument('pi_manifests',type=Path,nargs='+')
    args=p.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    assert not (args.output/'protocol.json').exists()
    remote={}
    for path in args.pi_manifests:
        for row in json.loads(path.read_text()):
            assert row['sample'] not in remote
            remote[row['sample']]=row
    sessions=json.loads((args.collection/'sessions.json').read_text())['sessions']
    corrections=json.loads((args.collection/'label-corrections.json').read_text())
    correction={r['session_id']:r for r in corrections['sessions']}
    assert len(sessions)==12 and len(remote)==120
    rows=[];archives=[]
    for session in sorted(sessions,key=lambda r:r['session_id']):
        path=args.collection/(session['session_id']+'.zip')
        archives.append(dict(session=session['session_id'],sha256=sha(path)))
        with zipfile.ZipFile(path) as archive:
            manifest_name=next(n for n in archive.namelist() if n.endswith('/manifest.json'))
            original=json.loads(archive.read(manifest_name));prefix=manifest_name.rsplit('/',1)[0]
            assert original['session_id']==session['session_id']
            assert original['subject']==session['subject']
            assert len(original['sample_ids'])==session['sample_count']==10
            for index,sample in enumerate(original['sample_ids'],1):
                relative=f'{prefix}/sample_{index:03d}'
                metadata=json.loads(archive.read(relative+'/metadata.json'))
                assert metadata['sample_id']==sample and metadata['sample_index']==index
                assert metadata['hand']==original['hand']
                hand=original['hand'];applied=None
                if session['session_id'] in correction:
                    applied=correction[session['session_id']]
                    assert applied['subject']==session['subject'] and applied['original_hand']==hand
                    assert index in applied['sample_indices']
                    hand=applied['corrected_hand']
                assert hand==session['hand']
                digest=hashlib.sha256(archive.read(relative+'/full.jpg')).hexdigest()
                assert remote[sample]['sha256']==digest
                rows.append(dict(sample=sample,subject=session['subject'],hand=hand,
                    identity=session['subject']+':'+hand,original_identity=original['subject']+':'+original['hand'],
                    session=session['session_id'],session_index=index,original=remote[sample]['original'],
                    sha256=digest,label_correction_applied=applied is not None))
    assert len(rows)==120 and len({r['sample'] for r in rows})==120
    assert len({r['sha256'] for r in rows})==120
    groups={u:sorted((r for r in rows if r['identity']==u),key=lambda r:r['sample'])
        for u in sorted({r['identity'] for r in rows})}
    assert len(groups)==11 and len({r['subject'] for r in rows})==6
    assert sorted(map(len,groups.values()))==[10]*10+[20]
    for values in groups.values():
        for index,row in enumerate(values,1):row['index']=index
    cases=[]
    for reverse in (False,True):
        enrolled={u:[r['sample'] for r in (values[-5:] if reverse else values[:5])] for u,values in groups.items()}
        queries=[r['sample'] for u,values in groups.items() for r in values if r['sample'] not in enrolled[u]]
        assert sum(map(len,enrolled.values()))==55 and len(queries)==65
        cases.append(dict(name='reverse' if reverse else 'original',enrollment=enrolled,queries=queries,query_seed=20261029))
    app=Path(__file__).resolve().parents[1]
    sources=[*app.glob('*.py'),*(app/'palm_app').rglob('*.py'),Path(__file__),
        *[app/'tools'/name for name in ('evaluate_six_person_frozen.py','replay_pi_pipeline.py',
            'replay_demo_manifest.py','replay_ready_queries.py')]]
    protocol=dict(frozen_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=app,text=True).strip(),
        matcher='FastCCQualityEvidence-v24-experimental',tuning_allowed=False,
        people=6,palm_identities=11,images=120,enrollment_images_per_case=55,queries_per_case=65,
        subject_images=dict(sorted(Counter(r['subject'] for r in rows).items())),
        palm_images=dict(sorted(Counter(r['identity'] for r in rows).items())),
        label_corrections=corrections,archives=archives,
        sessions_sha256=sha(args.collection/'sessions.json'),corrections_sha256=sha(args.collection/'label-corrections.json'),
        original_archives_unchanged=True,cases=cases,
        limitations=['Previously exposed participants; not an unseen-person validation',
            'Single old device; no cross-device claim',
            'Saved original-image replay excludes camera acquisition and external upload',
            'No calibrated unknown-person rejection claim'],
        code_hashes={str(path.relative_to(app)).replace('\\','/'):sha(path) for path in sources},
        native_sha256='272857b624cad687b7d87a32eb79ac0124f3d782be3e3a2b0ca092c92d87e600')
    (args.output/'manifest.json').write_text(json.dumps(sorted(rows,key=lambda r:(r['identity'],r['index'])),indent=2))
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2))
    print(json.dumps({k:protocol[k] for k in ('frozen_commit','people','palm_identities','images','subject_images','palm_images')},indent=2))


if __name__=='__main__':main()
