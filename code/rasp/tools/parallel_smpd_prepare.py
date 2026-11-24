"""Partition independent raw-image preparation, never recognition galleries.

Reuses every completed record (including failures) from the initial sequential
prepare. Each worker executes the unchanged frozen prepare code/model/threads.
Only inventory/accounting is sliced; the merged run still evaluates one gallery.
"""
import argparse,collections,copy,hashlib,json,subprocess,sys,time
from pathlib import Path
import evaluate_raw_smpd as base


def records(path):
    if not path.exists():return []
    result=[]
    for line in path.read_text(encoding='utf-8').splitlines():
        try:result.append(json.loads(line))
        except json.JSONDecodeError:raise RuntimeError('Partial original JSONL record; preserve and resolve explicitly')
    return result


def worker(a):
    global_protocol=json.loads((a.parent/'protocol.json').read_text());base.verify(global_protocol)
    inventory=json.loads((a.root/'zip-inventory.json').read_text());members={v['name']for v in inventory['inventory']}
    protocol=copy.deepcopy(global_protocol);protocol['samples']=[s for s in global_protocol['samples']if s['member']in members]
    protocol.update(images=len(members),people=len({s['subject']for s in protocol['samples']}),palms=len({s['identity']for s in protocol['samples']}),
        enrollment_images=sum(s['enrollment']for s in protocol['samples']),query_images=sum(not s['enrollment']for s in protocol['samples']),
        scope='Preparation worker only; not an independent gallery/recognition experiment',
        inventory_sha256=base.sha(a.root/'zip-inventory.json'),parallel_wrapper_sha256=base.source_sha(__file__))
    # Replace data-manifest construction only. All per-image inference, feature
    # extraction, failure recording, serialization and source checks are frozen.
    base.make_protocol=lambda root,model:protocol
    base.prepare(a)


def main_run(a):
    root=a.root.resolve();global_protocol=json.loads((root/'protocol.json').read_text());base.verify(global_protocol)
    initial=records(root/'prepared/records.jsonl');assert initial
    complete_members={r['member']for r in initial};assert len(complete_members)==len(initial)
    inventory=json.loads((root/'zip-inventory.json').read_text());ordered=sorted(inventory['inventory'],key=lambda e:e['offset'])
    assert {r['member']for r in initial}=={r['name']for r in ordered[:len(initial)]},'Initial records must be the complete prefix, not selected successes'
    remaining=[e for e in ordered if e['name']not in complete_members]
    subjects=sorted({base.label(e['name'])[0]for e in remaining});assignment={s:i%a.workers for i,s in enumerate(subjects)}
    jobs=[];start=time.perf_counter()
    plan=dict(complete=False,wrapper_sha256=base.source_sha(__file__),global_protocol_sha256=base.sha(root/'protocol.json'),
        preserved_prefix=len(initial),preserved_failures=sum(not r['roi_valid']for r in initial),workers=a.workers,
        scope='Parallel preparation only; final recognition uses all registered identities in one gallery',jobs=[])
    for number in range(a.workers):
        folder=root/f'prepare-worker-{number}';folder.mkdir(exist_ok=False)
        entries=[e for e in remaining if assignment[base.label(e['name'])[0]]==number]
        assert entries
        base.save(folder/'zip-inventory.json',dict(inventory,inventory=entries,files=len(entries)))
        # Windows directory junction is a local read path to existing downloaded
        # chunks. It neither copies nor modifies any source part.
        target=(root/'SMPD.parts').resolve();link=(folder/'SMPD.parts').absolute()
        assert target.is_relative_to(root)and link.is_relative_to(root)
        command=f"New-Item -ItemType Junction -Path '{str(link).replace(chr(39),chr(39)*2)}' -Target '{str(target).replace(chr(39),chr(39)*2)}' | Out-Null"
        subprocess.run(['powershell','-NoProfile','-Command',command],check=True,capture_output=True)
        log=(folder/'run.log').open('wb')
        process=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'worker',str(folder),'--parent',str(root),'--model',str(a.model.resolve())],stdout=log,stderr=subprocess.STDOUT)
        jobs.append((process,folder,log));plan['jobs'].append(dict(worker=number,images=len(entries),folder=str(folder),pid=process.pid))
    base.save(root/'parallel-prepare.json',plan)
    while any(process.poll()is None for process,folder,log in jobs):
        counts=collections.Counter(images=len(initial),roi_valid=sum(r['roi_valid']for r in initial),roi_failed=sum(not r['roi_valid']for r in initial))
        for process,folder,log in jobs:
            path=folder/'prepared/progress.json'
            if path.exists():counts.update(json.loads(path.read_text())['counts'])
        plan.update(counts=dict(counts),parallel_elapsed_s=time.perf_counter()-start)
        base.save(root/'parallel-prepare.json',plan);print(dict(counts),round(plan['parallel_elapsed_s']),flush=True)
        time.sleep(15)
    combined=list(initial)
    for process,folder,log in jobs:
        log.close()
        if process.returncode:raise RuntimeError('Preparation worker failed: '+str(folder))
        state=json.loads((folder/'prepared/progress.json').read_text());assert state['complete']
        combined.extend(records(folder/'prepared/records.jsonl'))
    assert len(combined)==global_protocol['images']and{r['member']for r in combined}=={e['name']for e in ordered}
    by_member={r['member']:r for r in combined};combined=[by_member[e['name']]for e in ordered]
    hashes=collections.defaultdict(list)
    for r in combined:hashes[r['sha256']].append(r['sample'])
    base.verify(global_protocol);base.save(root/'prepared/manifest.json',combined)
    base.save(root/'prepared/duplicates.json',dict(unique_files=len(hashes),groups=[v for v in hashes.values()if len(v)>1]))
    counts=dict(images=len(combined),roi_valid=sum(r['roi_valid']for r in combined),roi_failed=sum(not r['roi_valid']for r in combined),
        enrollment_feature_ok=sum(r.get('enrollment_feature_ok',False)for r in combined),
        enrollment_feature_failed=sum(r['enrollment']and not r.get('enrollment_feature_ok',False)for r in combined))
    base.save(root/'prepared/progress.json',dict(complete=True,counts=counts,parallel=True,parallel_elapsed_s=time.perf_counter()-start,
        preserved_sequential_prefix=len(initial),manifest_sha256=base.sha(root/'prepared/manifest.json')))
    plan.update(complete=True,counts=counts,parallel_elapsed_s=time.perf_counter()-start);base.save(root/'parallel-prepare.json',plan)
    print('complete',counts,flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=('run','worker'));p.add_argument('root',type=Path)
    p.add_argument('--parent',type=Path);p.add_argument('--model',required=True,type=Path);p.add_argument('--workers',type=int,choices=(2,3),default=3)
    a=p.parse_args();(worker if a.mode=='worker'else main_run)(a)


if __name__=='__main__':main()
