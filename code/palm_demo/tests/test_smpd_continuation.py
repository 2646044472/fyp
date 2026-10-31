"""Non-biometric fault fixtures; no SMPD images, models or inference."""
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


@pytest.fixture
def modules(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]/'tools'))
    return importlib.import_module('smpd_continuation'),importlib.import_module('smpd_run_journal')


@pytest.fixture
def linked(modules,tmp_path):
    c,j=modules;parent=tmp_path/'parent';child=tmp_path/'continuation';child.mkdir()
    rows=[dict(sample=f'fixture-{i}',sha256=f'input-{i}') for i in range(5)]
    old=j.Journal(parent,'query','parent-version',[r['sample'] for r in rows])
    for row in rows[:2]:old.append(row['sample'],dict(source_sha256=row['sha256'],capture={'input_sha256':row['sha256']},outcome='processing_failure',ms=10))
    records=c.read_chain(parent/'records/query','query','parent-version',rows)
    journal=c.SegmentJournal(child,'query','new-version',rows,records)
    before={p.name:p.read_bytes() for p in (parent/'records/query').glob('*.json')}
    return c,j,parent,child,rows,records,journal,before


def payload(row):return dict(source_sha256=row['sha256'],capture={'input_sha256':row['sha256']},outcome='correct',correct=True,ms=1)


def test_two_fingerprints_link_once_without_rewriting_parent(linked):
    c,j,parent,child,rows,records,journal,before=linked
    new=journal.append(rows[2]['sample'],payload(rows[2]))
    assert len(journal.records)==3 and journal.parent_count==2
    assert new['sequence']==2 and new['run_fingerprint']=='new-version'
    assert new['previous_record_sha256']==records[-1]['record_sha256']
    assert len(list((child/'records/query').glob('*.json')))==1
    assert c.SegmentJournal(child,'query','new-version',rows,records).records==journal.records
    assert {p.name:p.read_bytes() for p in (parent/'records/query').glob('*.json')}==before


@pytest.mark.parametrize('change',['digest','fingerprint','sample','sequence','previous','input'])
def test_corrupt_parent_prefix_is_rejected(linked,change):
    c,j,parent,child,rows,records,journal,before=linked
    path=parent/'records/query/00001.json';value=j.load(path)
    if change=='digest':value['payload']['ms']=11
    elif change=='input':value['payload']['capture']['input_sha256']='wrong'
    else:
        key={'fingerprint':'run_fingerprint','sample':'sample','sequence':'sequence','previous':'previous_record_sha256'}[change]
        value[key]={'fingerprint':'new-version','sample':rows[0]['sample'],'sequence':0,'previous':None}[change]
    if change!='digest':value['record_sha256']=j.digest({k:v for k,v in value.items() if k!='record_sha256'})
    j.atomic(path,value)
    with pytest.raises(ValueError):c.read_chain(parent/'records/query','query','parent-version',rows)


def test_wrong_suffix_version_gap_and_repeated_sample_rejected(linked):
    c,j,parent,child,rows,records,journal,before=linked
    journal.append(rows[2]['sample'],payload(rows[2]))
    with pytest.raises(ValueError):c.SegmentJournal(child,'query','other-version',rows,records)
    with pytest.raises(ValueError):journal.append(rows[2]['sample'],payload(rows[2]))
    with pytest.raises(ValueError):journal.append(rows[4]['sample'],payload(rows[4]))
    p=child/'records/query/00002.json';p.rename(p.with_name('00003.json'))
    with pytest.raises(ValueError):c.SegmentJournal(child,'query','new-version',rows,records)


def test_duplicate_frozen_rows_rejected(linked):
    c,j,parent,child,rows,records,journal,before=linked
    with pytest.raises(ValueError,match='Duplicate'):
        c.SegmentJournal(child,'query','new-version',rows+[rows[0]],records)


def test_pre_http_inflight_then_commit_and_residual_marker_never_repeats_http(linked):
    c,j,parent,child,rows,records,journal,before=linked
    # Simulate a failure in status publication, before the request is called.
    marker=j.begin_attempt(child,journal,'interrupted-epoch');calls=[]
    assert marker['sequence']==2
    j.recover_inflight(child,{'query':journal})
    assert not calls and not (child/'inflight.json').exists()
    receipt=j.load(child/'interruptions'/(marker['attempt_id']+'.json'))
    assert not receipt['already_committed']
    marker2=j.begin_attempt(child,journal,'resumed-epoch')
    calls.append(rows[len(journal.records)]['sample'])  # synthetic HTTP endpoint
    journal.append(rows[2]['sample'],payload(rows[2]))
    # Crash after durable commit, before marker deletion: rebuild then recover.
    resumed=c.SegmentJournal(child,'query','new-version',rows,records)
    j.recover_inflight(child,{'query':resumed})
    assert j.load(child/'interruptions'/(marker2['attempt_id']+'.json'))['already_committed']
    assert len(resumed.records)==3 and calls==[rows[2]['sample']]
    assert resumed.samples[len(resumed.records)]==rows[3]['sample']
    assert {p.name:p.read_bytes() for p in (parent/'records/query').glob('*.json')}==before


def test_registration_cannot_be_recomputed(linked):
    c,j,parent,child,rows,records,journal,before=linked
    reg=c.SegmentJournal(child,'enrollment','new-version',rows[:2],records)
    with pytest.raises(ValueError):reg.append(rows[0]['sample'],payload(rows[0]))
    with pytest.raises(ValueError):c.SegmentJournal(child,'enrollment','new-version',rows,records)


def test_asset_inventory_mismatch_is_fatal(modules,tmp_path):
    c,j=modules;parent=tmp_path/'parent';parent.mkdir();p=parent/'numeric.bin';p.write_bytes(b'non-biometric-fixture')
    expected={'numeric.bin':{'bytes':p.stat().st_size,'sha256':j.file_sha(p)}}
    assert c.verify_inventory(parent,expected)==j.digest(expected)
    p.write_bytes(b'changed')
    with pytest.raises(ValueError):c.verify_inventory(parent,expected)


@pytest.mark.skipif(os.name!='nt',reason='Windows deny-write implementation')
def test_parent_protection_blocks_python_and_other_process_writes(modules,tmp_path):
    c,j=modules;parent=tmp_path/'parent';parent.mkdir();p=parent/'numeric.bin';p.write_bytes(b'fixture')
    with c.ReadOnlyTree(parent) as guard:
        inventory=guard.inventory()
        for action in (lambda:p.write_bytes(b'bad'),lambda:p.unlink(),lambda:(parent/'new').mkdir()):
            with pytest.raises(PermissionError):action()
        # A separate interpreter has no audit hook: Windows handles must deny it.
        for code in ("from pathlib import Path;import sys;Path(sys.argv[1]).write_bytes(b'bad')",
                     "from pathlib import Path;import sys;Path(sys.argv[1]).unlink()"):
            result=subprocess.run([sys.executable,'-B','-c',code,str(p)],capture_output=True,text=True)
            assert result.returncode!=0 and ('PermissionError' in result.stderr or 'WinError' in result.stderr)
        assert p.read_bytes()==b'fixture'
        assert c.verify_inventory(parent,inventory)==j.digest(inventory)
    p.write_bytes(b'allowed-after-release')


@pytest.mark.skipif(os.name!='nt',reason='Windows handle compatibility')
def test_existing_write_handle_prevents_claiming_read_only(modules,tmp_path):
    c,j=modules;parent=tmp_path/'parent';parent.mkdir();p=parent/'data.bin';p.write_bytes(b'fixture')
    with p.open('r+b'):
        with pytest.raises(OSError):
            with c.ReadOnlyTree(parent):pass


def test_metrics_preserve_failed_prefix_and_fixed_accounting(modules,monkeypatch,tmp_path):
    c,j=modules;r=importlib.import_module('report_smpd_continuation')
    rows=[{'payload':dict(outcome='processing_failure',ms=30)},
          {'payload':dict(outcome='wrong_identity_accepted',ms=40)},
          {'payload':dict(outcome='correct',ms=2000)}]
    summary=r.summarize(rows)
    assert summary['total']==3 and summary['correct_within_2500']==1
    assert sum(summary['outcomes'].values())==3
    assert summary['http']['p50_ms']==40


def test_same_original_http_work_code_and_unchanged_serializer(modules):
    c,j=modules;r=importlib.import_module('run_smpd_continuation')
    assert r.v27.previous.work.__code__.co_name=='work'
    import hashlib,inspect
    assert hashlib.sha256(inspect.getsource(r.v27.previous.work).encode()).hexdigest()=='71c8933b0f6a817c0414198e18e47ba126085672fab01db7cbeb147eb92c5a5e'
    assert j.canonical({'b':2,'a':1})==b'{"a":1,"b":2}'


@pytest.mark.skipif(os.name!='nt',reason='Whole bridge enforces Windows read-only handles')
def test_bridge_actual_http_loop_starts_at217_once_and_keeps_parent_bytes(modules,tmp_path,monkeypatch):
    from types import SimpleNamespace
    from http.server import BaseHTTPRequestHandler
    import time
    c,j=modules;run=importlib.import_module('run_smpd_continuation')
    parent=tmp_path/'parent';root=tmp_path/'continuation';parent.mkdir();root.mkdir()
    user='fixture-001-right';identity='fixture:001:right'
    enroll=[dict(sample=f'enroll-{i}',sha256=f'e-{i}',enrollment=True,subject='001',index=i,identity=identity) for i in range(460)]
    query=[dict(sample=f'query-{i}',sha256=f'q-{i}',enrollment=False,subject='001',index=i,identity=identity,condition='F') for i in range(218)]
    rows={'enrollment':enroll,'query':query};records={}
    for stage,selected in rows.items():
        rs=j.Journal(parent,stage,run.PARENT_FP,[r['sample'] for r in selected])
        for row in selected[:460 if stage=='enrollment' else 216]:
            rs.append(row['sample'],dict(payload(row),ok=False,correct=False,outcome='processing_failure'))
        records[stage]=rs.records
    parent_gallery=dict(run_fingerprint=run.PARENT_FP,registered=1,enrollments=[dict(user=user,registered=True)])
    j.atomic(parent/'gallery.json',parent_gallery)
    old=dict(run_fingerprint=run.PARENT_FP,rows=enroll+query);j.atomic(parent/'protocol.json',old)
    inventory={p.relative_to(parent).as_posix():{'bytes':p.stat().st_size,'sha256':j.file_sha(p)} for p in parent.rglob('*') if p.is_file()}
    j.atomic(root/'parent-inventory.json',inventory)
    templates=root/'evaluation/runtime/demo_templates';templates.mkdir(parents=True)
    fixture=templates/'non-biometric.bin';fixture.write_bytes(b'non-biometric-fixture')
    j.atomic(root/'copied-assets.json',{fixture.relative_to(root).as_posix():{'bytes':fixture.stat().st_size,'sha256':j.file_sha(fixture)}})
    p=dict(run_root=str(root),rows=enroll+query,resources={'http_timeout_seconds':10,'start_available_bytes':0,'minimum_available_bytes':0},
        lineage=dict(parent_root=str(parent),parent_run_fingerprint=run.PARENT_FP,
        parent_protocol_sha256=j.file_sha(parent/'protocol.json'),parent_gallery_sha256=j.file_sha(parent/'gallery.json'),
        parent_chains={'query':{'count':216}},inherited_inflight={'attempt_id':'fixture-pre-http'},inherited_inflight_sha256='fixture-marker'))
    p['run_fingerprint']=j.digest(p);j.atomic(root/'protocol.json',p)
    j.atomic(root/'gallery.json',run.expected_gallery(p,parent_gallery))
    monkeypatch.setattr(run,'load_lineage',lambda _:(p,parent,old))
    monkeypatch.setattr(run,'parent_chains',lambda *_:(rows,records))
    monkeypatch.setattr(run.v27,'verify',lambda *a,**k:None)
    calls=[];camera=SimpleNamespace(audit={},queue=[])
    camera.select=lambda rs:setattr(camera,'queue',list(rs))
    algorithm=SimpleNamespace(score_gallery=lambda probe,groups:{user:.1},close=lambda:None,_terminal_rf_trace=None)
    app=SimpleNamespace(demo_algorithm=algorithm,demo=SimpleNamespace(
        gallery=SimpleNamespace(_prepared_cache={user:object()}),payments=SimpleNamespace(transaction_count=lambda:0),pending={}))
    def prepare(runtime,protocol,*,gallery):
        state=j.load(root/'status.json')
        j.atomic(root/'query-phases'/(state['epoch']+'.json'),dict(epoch=state['epoch'],started_unix=time.time()))
        return app,camera,{'fixture':True}
    monkeypatch.setattr(run.v27,'prepare_app',prepare)
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_POST(self):
            row=camera.queue.pop(0);calls.append(row['sample'])
            camera.audit['input_sha256']=row['sha256']
            algorithm.score_gallery(None,{user:None})
            algorithm._terminal_rf_trace={'unknown_calls':0}
            data=json.dumps(dict(status='MATCH',user_id=user,score=.1,second_score=.3)).encode()
            self.send_response(200);self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
    from palm_app import debug_ui
    monkeypatch.setattr(debug_ui,'make_handler',lambda _:Handler)
    run.work(SimpleNamespace(root=root,pause_after_queries=1))
    assert calls==['query-216']
    assert j.load(root/'status.json')['completed_queries']==217
    assert j.load(root/'status.json')['continuation_completed_queries']==1
    assert j.load(root/'status.json')['state']=='paused_preflight'
    assert j.load(root/'records/query/00216.json')['sample']=='query-216'
    assert len(list((root/'records/query').glob('*.json')))==1
    assert c.verify_inventory(parent,inventory)==j.digest(inventory)
    assert j.load(root/'parent-preservation-receipt.json')['all_parent_bytes_unchanged']
