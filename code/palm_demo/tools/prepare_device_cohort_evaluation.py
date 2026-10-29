"""Freeze active device captures into separate same-device HTTP experiments."""
import argparse
from collections import Counter
import hashlib,json,subprocess,zipfile
from pathlib import Path


def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('output',type=Path)
    p.add_argument('--include-excluded',action='store_true',help='Historical reproduction only: retain explicitly excluded archived samples')
    args=p.parse_args()
    app=Path(__file__).resolve().parents[1];repo=app.parents[1]
    args.output.mkdir(parents=True,exist_ok=False)
    previous=app/'runtime/pi5-under2-20261028/six-person-v24-frozen-20261029/manifest.json'
    old_paths={r['sample']:r for r in json.loads(previous.read_text())}
    sources=[('old-camera',repo/'code/data/pi-captures-2026-10-15'),
             ('new-camera',repo/'code/data/pi-captures-20261020'),
             ('new-camera',repo/'code/data/pi-captures-20261029')]
    rows=[];archives=[];exclusions=[];seen=set();archived_count=0
    for device,folder in sources:
        exclusion_path=folder/'sample-exclusions.json'
        local_exclusions=[]
        if exclusion_path.is_file():
            local_exclusions=json.loads(exclusion_path.read_text(encoding='utf-8'))['excluded_samples']
            assert all(r['requested_by']=='user' and r['scope'] in ('future_active_experiments','active_collection_and_future_experiments') for r in local_exclusions)
            exclusions.extend(local_exclusions)
        excluded={r['sample_id'] for r in local_exclusions}
        sessions=json.loads((folder/'sessions.json').read_text())['sessions']
        for session in sessions:
            sid=session['session_id'];path=folder/session.get('archive',sid+'.zip')
            archives.append(dict(device=device,archive=str(path.relative_to(repo)).replace('\\','/'),sha256=sha(path.read_bytes())))
            with zipfile.ZipFile(path) as archive:
                names=archive.namelist();manifest_name=next(n for n in names if n.endswith('/manifest.json'))
                manifest=json.loads(archive.read(manifest_name));prefix=manifest_name.rsplit('/',1)[0]
                assert manifest['session_id']==sid and manifest['phase'] in ('complete','await_hand')
                assert len(manifest['sample_ids'])==session['sample_count']
                assert (manifest['subject'],manifest['hand'])==(session['subject'],session['hand'])
                for index,sample in enumerate(manifest['sample_ids'],1):
                    archived_count+=1;seen.add(sample)
                    base=f'{prefix}/sample_{index:03d}'
                    metadata=json.loads(archive.read(base+'/metadata.json'))
                    assert metadata['session_id']==sid and metadata['sample_id']==sample and metadata['sample_index']==index
                    assert (metadata['subject'],metadata['hand'])==(manifest['subject'],manifest['hand'])
                    digest=sha(archive.read(base+'/full.jpg'))
                    if sample in excluded and not args.include_excluded:continue
                    if device=='old-camera':
                        assert old_paths[sample]['sha256']==digest
                        original=old_paths[sample]['original']
                    else:original='/home/fyp5/palm_demo/runtime/highres_capture/'+sample+'/full.jpg'
                    rows.append(dict(device=device,sample=sample,session=sid,subject=manifest['subject'],hand=manifest['hand'],
                        identity=device+':'+manifest['subject']+':'+manifest['hand'],index=index,session_index=index,
                        original=original,sha256=digest,width=metadata['width'],height=metadata['height'],
                        archive=str(path.relative_to(repo)).replace('\\','/'),archive_member=base+'/full.jpg'))
    assert len({r['sample_id'] for r in exclusions})==len(exclusions)
    assert all(r['sample_id'] in seen or r['scope']=='active_collection_and_future_experiments' for r in exclusions)
    expected=archived_count-(0 if args.include_excluded else sum(r['sample_id'] in seen for r in exclusions))
    assert len(rows)==expected and len({r['sample'] for r in rows})==expected and len({r['sha256'] for r in rows})==expected
    cases=[]
    for device in ('new-camera','old-camera'):
        groups={u:sorted((r for r in rows if r['identity']==u),key=lambda r:r['sample'])
            for u in sorted({r['identity'] for r in rows if r['device']==device})}
        assert all(len(g)>=6 for g in groups.values()),'Each identity needs five enrollment images and at least one query'
        for reverse in (False,True):
            enrolled={u:[r['sample'] for r in (values[-5:] if reverse else values[:5])] for u,values in groups.items()}
            query=[r['sample'] for u,values in groups.items() for r in values if r['sample'] not in enrolled[u]]
            assert len(query)==sum(len(values)-5 for values in groups.values())
            cases.append(dict(name=device+('-reverse' if reverse else '-original'),device=device,
                enrollment=enrolled,queries=query,query_seed=20261029))
    code=[*app.glob('*.py'),*(app/'palm_app').rglob('*.py'),Path(__file__),
        *[app/'tools'/name for name in ('evaluate_six_person_frozen.py','replay_pi_pipeline.py','replay_demo_manifest.py','replay_ready_queries.py')]]
    protocol=dict(frozen_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip(),
        matcher='FastCCQualityEvidence-v24-experimental',tuning_allowed=False,images=len(rows),
        palm_identities=len({r['identity'] for r in rows}),people=7,
        subject_aliases_for_reporting_only={'bankey-10-12':'bankey','stephen-10-13':'stephen'},
        cases=cases,archives=archives,
        archived_images=archived_count,user_sample_exclusions=exclusions,
        excluded_samples_included=args.include_excluded,
        excluded_retired_session='20261013T111838871161Z-df3d072b',
        device_images=dict(Counter(r['device'] for r in rows)),
        limitations=['No cross-device enrollment/query matching',
            'Previously exposed old captures; new participant not used to tune this version',
            'Saved-image replay excludes camera capture and external upload',
            'No calibrated unknown-person rejection claim'],
        native_sha256='272857b624cad687b7d87a32eb79ac0124f3d782be3e3a2b0ca092c92d87e600',
        code_hashes={str(path.relative_to(app)).replace('\\','/'):sha(path.read_bytes()) for path in code})
    (args.output/'manifest.json').write_text(json.dumps(rows,indent=2))
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2))
    print(json.dumps(dict(images=len(rows),identities=protocol['palm_identities'],cases=[dict(case=c['name'],identities=len(c['enrollment']),queries=len(c['queries'])) for c in cases]),indent=2))


if __name__=='__main__':main()
