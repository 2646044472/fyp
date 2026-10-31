"""Explicit operational continuation of the stopped v27 run; same3217 denominator.

The parent is never opened by an inference/store writer. Its sealed templates
and isolated empty-transaction payment database are copied byte-for-byte into
the child runtime. The original whole-gallery HTTP work code is unchanged.
"""
import argparse
from contextlib import ExitStack
import copy
import inspect
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import time
import types

import run_lossless_smpd as v27
from smpd_run_journal import atomic, digest, file_sha, inside, load, recover_inflight
from smpd_continuation import ReadOnlyTree, SegmentJournal, read_chain, verify_inventory

APP = v27.APP
PARENT_FP = '710aac923ffd87b71a20716c494000ae9e3302056218dbd879a6a0b4b711cdd2'
OLD_JOURNAL = '3326e39bb30cd7a220bf6488f5f8fe41d37460fafa217c9c5f842a59346c9ecc'
NEW_JOURNAL = '72a0ef3322e4fea1d37ea0b0620875ffc1a9c45913ad276f38e51af71c59f459'
TOOLS = ('smpd_continuation.py', 'run_smpd_continuation.py', 'report_smpd_continuation.py')


def valid_protocol(path):
    p = load(path)
    if digest({k:v for k,v in p.items() if k != 'run_fingerprint'}) != p['run_fingerprint']:
        raise ValueError('Protocol fingerprint mismatch')
    return p


def parent_chains(parent, p):
    rows = {stage:v27.previous.ordered_rows(p, stage == 'enrollment') for stage in ('enrollment','query')}
    records = {stage:read_chain(parent/'records'/stage,stage,p['run_fingerprint'],rows[stage]) for stage in rows}
    if len(records['enrollment']) != 460 or len(records['query']) != 216:
        raise ValueError('Expected exactly460 inherited registrations and216 inherited queries')
    return rows, records


def check_parent_execution(p):
    if p['run_fingerprint'] != PARENT_FP or p['source_commit'] != '3e66335ac7f22668a13d56521c0b3ef6a50eef44':
        raise ValueError('Unreviewed parent protocol')
    journal = str((APP/'tools/smpd_run_journal.py').resolve())
    if p['source_sha256'].get(journal) != OLD_JOURNAL or file_sha(journal) != NEW_JOURNAL:
        raise ValueError('Unreviewed journal patch')
    for group in ('source_sha256','models_sha256','metadata_sha256','dependency_sha256'):
        for path, expected in p[group].items():
            actual = file_sha(path)
            if actual != expected and not (group == 'source_sha256' and path == journal and actual == NEW_JOURNAL):
                raise ValueError('Parent execution asset mismatch: ' + path)
    if v27.previous.environment() != p['environment']:
        raise ValueError('Parent environment changed')


def audit_parent(parent, guard):
    """All numeric containers checked without image inference or asset writes."""
    from lossless_template_store import LosslessTemplateStore, digest as array_digest
    from pklnet_roi import ROI_GEOMETRY_VERSION
    p = valid_protocol(parent/'protocol.json')
    check_parent_execution(p)
    rows, records = parent_chains(parent,p)
    marker = load(parent/'inflight.json')
    expected = dict(stage='query',sequence=216,sample='smpd-007-RF-12',run_fingerprint=PARENT_FP)
    if any(marker.get(k) != v for k,v in expected.items()):
        raise ValueError('Unexpected inherited inflight boundary')
    error = (parent/'full.stderr.log').read_text(encoding='utf-8',errors='replace')
    if ("status('query_inflight',active_sample=row['sample'])" not in error
            or 'os.replace(temp, path)' not in error or '[WinError 5]' not in error):
        raise ValueError('No evidence that inherited inflight failed before HTTP')
    state = load(parent/'status.json'); supervisor = load(parent/'supervisor-status.json')
    if state.get('state') != 'failed_preserving_prefix' or supervisor.get('worker_exit_code') != 1:
        raise ValueError('Unexpected parent worker state')
    frames = {}; feature_paths = set()
    for row, record in zip(rows['enrollment'],records['enrollment']):
        if record['payload']['ok']:
            frame = v27.validate_feature(parent,p,row,record)
            frames[row['sample']] = array_digest(frame)
            feature_paths.add(inside(record['payload']['feature'],parent/'features'))
            del frame
    if feature_paths != set((parent/'features').glob('*.npz')) or len(frames) != 447:
        raise ValueError('Unexpected orphan/missing registration feature containers')
    store = LosslessTemplateStore(parent/'evaluation/runtime/demo_templates')
    gallery = load(parent/'gallery.json'); by_sample = {r['sample']:r for r in records['enrollment']}
    expected_entries = []; template_paths = []; seals = set()
    for identity in sorted({r['identity'] for r in p['rows']}):
        selected = [r for r in rows['enrollment'] if r['identity'] == identity]
        if len(selected) != 5 or [r['index'] for r in selected] != list(range(5)):
            raise ValueError('Fixed registration selection changed')
        selected_records = [by_sample[r['sample']] for r in selected]
        ok = all(r['payload']['ok'] for r in selected_records); user = identity.replace(':','-')
        entry = dict(identity=identity,user=user,samples=[r['sample'] for r in selected],registered=ok)
        if ok:
            paths = store.paths(user)
            if len(paths) != 1:
                raise ValueError('Expected v27 numeric container')
            entry['container_sha256'] = file_sha(paths[0]); template_paths.append(paths[0])
            batch, metadata = store.load(user)
            expected_meta = dict(user=user,display_name='EVAL '+identity,algorithm=p['matcher'],capture_profile='noir-ir',
                samples=5,roi_geometry=ROI_GEOMETRY_VERSION,roi_sources=['pklnet']*5,template_codec=p['codec'],
                template_storage_schema=p['storage'],run_fingerprint=PARENT_FP,
                frame_record_sha256=[r['record_sha256'] for r in selected_records],
                source='Fresh fixed SMPD original-image v27 extraction; no imported features')
            if metadata != expected_meta or any(array_digest(f) != frames[r['sample']] for f,r in zip(batch,selected)):
                raise ValueError('Gallery metadata/frame differs from inherited fresh registration')
            del batch
            seal = parent/'gallery-records'/(user+'.json'); seals.add(seal)
            if load(seal) != dict(run_fingerprint=PARENT_FP,**entry):
                raise ValueError('Gallery seal mismatch')
        elif store.exists(user):
            raise ValueError('Failed registration unexpectedly has a template')
        expected_entries.append(entry)
    expected_gallery = dict(run_fingerprint=PARENT_FP,enrollments=expected_entries,registered=86,codec=p['codec'],storage=p['storage'])
    if (gallery != expected_gallery or len(template_paths) != 86
            or set(store.list_users()) != {e['user'] for e in expected_entries if e['registered']}
            or set((parent/'gallery-records').glob('*.json')) != seals
            or set((parent/'evaluation/runtime/demo_templates').iterdir()) != set(template_paths)):
        raise ValueError('Complete86 identity gallery mismatch')
    db = parent/'evaluation/runtime/demo_payment.sqlite3'
    if any(db.with_name(db.name+s).exists() for s in ('-wal','-shm','-journal')):
        raise ValueError('Parent SQLite sidecar requires separate explicit recovery')
    with sqlite3.connect(db.as_uri()+'?mode=ro&immutable=1',uri=True) as connection:
        users = connection.execute('SELECT user_id,balance_cents FROM accounts ORDER BY user_id').fetchall()
        if users != [(e['user'],10000) for e in expected_entries if e['registered']] or connection.execute('SELECT count(*) FROM transactions').fetchone()[0] != 0:
            raise ValueError('Inherited isolated payment state mismatch')
    inventory = guard.inventory()
    scalar = {path:v['sha256'] for path,v in inventory.items() if Path(path).suffix in ('.json','.jsonl','.log','.tmp','.lock')}
    proof = load(APP/'docs/experiments/smpd-status-atomic-retry-20261031/verification.json')['before']
    if len(scalar) != 785 or digest(scalar) != proof['scalar_files_sha256']:
        raise ValueError('Original scalar prefix changed since reviewed snapshot')
    return dict(protocol=p,inventory=inventory,chains=records,marker=marker,gallery=gallery,
        verified_feature_containers=447,verified_template_containers=86,verified_template_frames=430,
        next_sample=rows['query'][216]['sample'],no_parent_writes=True)


def copy_exact(source, target, sha):
    target.parent.mkdir(parents=True,exist_ok=True)
    with source.open('rb') as src, target.open('xb') as dst:
        shutil.copyfileobj(src,dst,1024*1024);dst.flush();os.fsync(dst.fileno())
    if file_sha(target) != sha:
        raise ValueError('Byte-copy mismatch: '+str(target))


def expected_gallery(p, parent_gallery):
    return dict(parent_gallery,run_fingerprint=p['run_fingerprint'],origin_run_fingerprint=PARENT_FP,
                origin_gallery_sha256=p['lineage']['parent_gallery_sha256'])


def lineage_receipt(root, p, compatibility):
    return dict(compatibility=compatibility,compatibility_sha256=file_sha(root/'compatibility.json'),
                new_run_fingerprint=p['run_fingerprint'],new_protocol_sha256=file_sha(root/'protocol.json'))


def initialize(parent, root):
    parent,root = parent.resolve(),root.resolve()
    if root.exists() or root.is_relative_to(parent) or parent.is_relative_to(root):
        raise ValueError('New sibling continuation directory required')
    with ReadOnlyTree(parent) as guard:
        a = audit_parent(parent,guard); old = a['protocol']
        root.mkdir(parents=True)
        atomic(root/'parent-inventory.json',a['inventory'],exclusive=True)
        source = dict(old['source_sha256']); source[str((APP/'tools/smpd_run_journal.py').resolve())] = NEW_JOURNAL
        source.update({str((APP/'tools'/name).resolve()):file_sha(APP/'tools'/name) for name in TOOLS})
        lineage = dict(parent_root=str(parent),parent_run_fingerprint=PARENT_FP,parent_source_commit=old['source_commit'],
            parent_protocol_sha256=file_sha(parent/'protocol.json'),parent_gallery_sha256=file_sha(parent/'gallery.json'),
            parent_inventory_sha256=file_sha(root/'parent-inventory.json'),
            parent_chains={s:dict(count=len(rs),tip=rs[-1]['record_sha256']) for s,rs in a['chains'].items()},
            inherited_inflight=a['marker'],inherited_inflight_sha256=file_sha(parent/'inflight.json'),
            inherited_error_log_sha256=file_sha(parent/'full.stderr.log'),next_global_sequence=216,next_sample=a['next_sample'],
            denominator=3217,registration_attempts=460)
        compatibility = dict(schema='smpd-v27-operational-lineage-v1',**lineage,
            old_source_sha256=old['source_sha256'],new_source_sha256=source,dependency_sha256=old['dependency_sha256'],
            allowed_existing_source_changes={str((APP/'tools/smpd_run_journal.py').resolve()):dict(old=OLD_JOURNAL,new=NEW_JOURNAL,
                reason='Reviewed atomic WinError5 bounded retry; no recognition/codec/serialization change')},
            added_control_sources=[str((APP/'tools'/name).resolve()) for name in TOOLS],
            verified_feature_containers=447,verified_template_containers=86,verified_template_frames=430,
            denominator_policy='Parent216 plus new suffix; no old70/241; all failures retained',
            parent_write_protection='Windows FILE_SHARE_READ deny-write/delete handles plus audit hook and tree/hash checks')
        atomic(root/'compatibility.json',compatibility,exclusive=True)
        copies = {}
        for e in a['gallery']['enrollments']:
            if e['registered']:
                rel='evaluation/runtime/demo_templates/'+e['user']+'.union2.npz';copies[rel]=a['inventory'][rel]
        rel='evaluation/runtime/demo_payment.sqlite3';copies[rel]=a['inventory'][rel]
        for rel,info in copies.items():
            copy_exact(parent/rel,root/rel,info['sha256'])
        atomic(root/'copied-assets.json',copies,exclusive=True)
        p=copy.deepcopy(old);p.pop('run_fingerprint')
        p.update(run_root=str(root),created_unix=time.time(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=APP,text=True).strip(),
            source_sha256=source,lineage=lineage,independent_run=False,
            continuation='Explicit two-version operational continuation; inherited460 registrations and216 queries are counted once')
        p['metadata_sha256'].update({str(x.resolve()):file_sha(x) for x in (parent/'protocol.json',root/'parent-inventory.json',root/'compatibility.json',root/'copied-assets.json')})
        p['run_fingerprint']=digest(p)
        atomic(root/'protocol.json',p,exclusive=True)
        atomic(root/'lineage.json',lineage_receipt(root,p,compatibility),exclusive=True)
        atomic(root/'gallery.json',expected_gallery(p,a['gallery']),exclusive=True)
        atomic(root/'status.json',dict(state='frozen_continuation_not_started',complete=False,
            run_fingerprint=p['run_fingerprint'],parent_completed_queries=216,continuation_completed_queries=0,
            completed_queries=216,total_queries=3217,enrollment_completed=460),exclusive=True)
        verify_inventory(parent,a['inventory'])
        print(dict(state='continuation_frozen',root=str(root),fingerprint=p['run_fingerprint'],
            parent_queries=216,next_sample=a['next_sample'],verified_features=447,verified_templates=86),flush=True)


def load_lineage(root):
    p=valid_protocol(root/'protocol.json');parent=Path(p['lineage']['parent_root'])
    if str(root.resolve()) != p['run_root']:
        raise ValueError('Continuation moved')
    old=valid_protocol(parent/'protocol.json');compatibility=load(root/'compatibility.json')
    if (old['run_fingerprint'] != PARENT_FP or file_sha(parent/'protocol.json') != p['lineage']['parent_protocol_sha256']
            or load(root/'lineage.json') != lineage_receipt(root,p,compatibility)):
        raise ValueError('Lineage binding mismatch')
    invariant = set(old) - {'run_fingerprint','created_unix','run_root','source_commit','source_sha256','metadata_sha256'}
    if any(p.get(k) != old[k] for k in invariant) or p['run_fingerprint'] == PARENT_FP:
        raise ValueError('Inherited recognition/protocol invariant changed')
    if (compatibility['new_source_sha256'] != p['source_sha256']
            or compatibility['old_source_sha256'] != old['source_sha256']
            or any(compatibility.get(k) != v for k,v in p['lineage'].items())):
        raise ValueError('Compatibility manifest mismatch')
    source=dict(old['source_sha256']);source[str((APP/'tools/smpd_run_journal.py').resolve())]=NEW_JOURNAL
    source.update({str((APP/'tools'/name).resolve()):file_sha(APP/'tools'/name) for name in TOOLS})
    metadata=dict(old['metadata_sha256'])
    metadata.update({str(x.resolve()):file_sha(x) for x in (parent/'protocol.json',root/'parent-inventory.json',root/'compatibility.json',root/'copied-assets.json')})
    if p['source_sha256']!=source or p['metadata_sha256']!=metadata or str(parent.resolve())!=old['run_root']:
        raise ValueError('Unreviewed source/metadata or parent path exception')
    return p,parent,old


def work(args):
    root=args.root.resolve();p,parent,old=load_lineage(root)
    with ExitStack() as stack:
        guard=stack.enter_context(ReadOnlyTree(parent))
        inventory=load(root/'parent-inventory.json');verify_inventory(parent,inventory)
        rows,records=parent_chains(parent,old)
        allowed_features={Path(r['payload']['feature']).resolve() for r in records['enrollment'] if r['payload']['ok']}
        journals={}
        def factory(folder,stage,fingerprint,samples):
            if folder != root or fingerprint != p['run_fingerprint'] or samples != [r['sample'] for r in rows[stage]]:
                raise ValueError('Unexpected journal request')
            journals[stage]=SegmentJournal(root,stage,fingerprint,rows[stage],records[stage])
            return journals[stage]
        def feature_inside(path, requested_root):
            if Path(requested_root).resolve()==root/'features' and Path(path).resolve() in allowed_features:
                return inside(path,parent/'features')
            return inside(path,requested_root)
        def recover(folder, js):
            receipt=dict(parent_run_fingerprint=PARENT_FP,parent_marker=p['lineage']['inherited_inflight'],
                marker_sha256=p['lineage']['inherited_inflight_sha256'],action='Preserve parent marker; inherited pre-HTTP attempt is not a result; start at global216')
            target=root/'interruptions'/('parent-'+receipt['parent_marker']['attempt_id']+'.json')
            if target.exists():
                if load(target)!=receipt:raise ValueError('Inherited interruption receipt changed')
            else:atomic(target,receipt,exclusive=True)
            recover_inflight(root,js)
        def build(folder,protocol,enroll):
            if len(enroll.records)!=460:raise ValueError('Registration count changed')
            expected=expected_gallery(protocol,load(parent/'gallery.json'))
            if load(root/'gallery.json')!=expected:raise ValueError('Inherited child gallery changed')
            copies=load(root/'copied-assets.json')
            for rel,info in copies.items():
                if file_sha(root/rel)!=info['sha256']:raise ValueError('Inherited child asset changed: '+rel)
            templates=root/'evaluation/runtime/demo_templates'
            if {x.relative_to(root).as_posix() for x in templates.iterdir()} != {x for x in copies if '/demo_templates/' in x}:
                raise ValueError('Unexpected child template')
            template_guard=stack.enter_context(ReadOnlyTree(templates));extra_guards.append(template_guard)
            return expected
        extra_guards=[]
        def verify(protocol,*,dependencies=False):
            guard.verify()
            for g in extra_guards:g.verify()
            v27.verify(protocol,dependencies=dependencies)
        def publish(path,value,**kw):
            inside(path,root)
            if Path(path)==root/'status.json':
                from report_smpd_continuation import live_fields
                value=dict(value,**live_fields(root,p,journals.get('query')))
            atomic(path,value,**kw)
            if (Path(path)==root/'status.json' and value.get('state')=='query_checkpoint'
                    and (value['continuation_completed_queries'] in (1,2) or value['continuation_completed_queries']%25==0)):
                from report_smpd_continuation import write_report
                write_report(root)
        namespace=dict(vars(v27.previous),MATCHER=v27.MATCHER,POLICY=v27.POLICY,
            prepare_app=v27.prepare_app,build_gallery=build,verify=verify,Journal=factory,
            inside=feature_inside,recover_inflight=recover,atomic=publish)
        function=types.FunctionType(v27.previous.work.__code__,namespace,'work')
        try:
            function(args)
        finally:
            verify_inventory(parent,inventory)
            atomic(root/'parent-preservation-receipt.json',dict(checked_unix=time.time(),
                parent_inventory_sha256=digest(inventory),all_parent_bytes_unchanged=True,
                parent_fingerprint=PARENT_FP,continuation_fingerprint=p['run_fingerprint']))
            from report_smpd_continuation import write_report
            write_report(root)


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='mode',required=True)
    init=sub.add_parser('init');init.add_argument('parent',type=Path);init.add_argument('root',type=Path)
    run=sub.add_parser('work');run.add_argument('root',type=Path);run.add_argument('--pause-after-queries',type=int)
    args=parser.parse_args()
    if args.mode=='init':initialize(args.parent,args.root)
    else:
        if args.pause_after_queries is not None and args.pause_after_queries<1:parser.error('Positive query budget required')
        work(args)


if __name__=='__main__':main()
