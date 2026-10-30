"""Operational isolation/failure preservation; no public inference or tuning."""
import importlib
import json
from pathlib import Path
import subprocess
import sys

import pytest


@pytest.fixture
def modules(monkeypatch):
    tools=Path(__file__).resolve().parents[1]/'tools'
    monkeypatch.syspath_prepend(str(tools))
    return importlib.import_module('smpd_run_journal'),importlib.import_module('run_terminal_smpd')


def test_failed_records_preserved_and_same_version_exact_prefix_only(modules,tmp_path):
    j,_=modules
    first=j.Journal(tmp_path,'query','one',['a','b','c'])
    first.append('a',dict(ok=False,http_status=400))
    first.append('b',dict(ok=False,http_status=200))
    before=[p.read_bytes() for p in sorted(first.folder.glob('*.json'))]
    again=j.Journal(tmp_path,'query','one',['a','b','c'])
    assert len(again.records)==2 and not again.records[0]['payload']['ok']
    again.append('c',dict(ok=True))
    assert [p.read_bytes() for p in sorted(first.folder.glob('*.json'))[:2]]==before
    with pytest.raises(ValueError,match='same-version'): j.Journal(tmp_path,'query','two',['a','b','c'])
    with pytest.raises(ValueError,match='same-version'): j.Journal(tmp_path,'query','one',['b','a','c'])
    with pytest.raises(ValueError,match='next fixed'): again.append('c',{})


def test_corruption_gap_and_partial_record_never_silently_truncated(modules,tmp_path):
    j,_=modules;v=j.Journal(tmp_path,'query','one',['a','b']);v.append('a',{})
    path=v.folder/'00000.json';before=path.read_bytes();path.write_bytes(before[:-4])
    with pytest.raises(json.JSONDecodeError): j.Journal(tmp_path,'query','one',['a','b'])
    assert path.read_bytes()==before[:-4]
    path.write_bytes(before);path.rename(v.folder/'00001.json')
    with pytest.raises(ValueError,match='gap'): j.Journal(tmp_path,'query','one',['a','b'])


def test_tampered_record_digest_and_duplicate_samples_rejected(modules,tmp_path):
    j,_=modules;v=j.Journal(tmp_path,'query','one',['a']);v.append('a',dict(correct=False))
    path=v.folder/'00000.json';value=j.load(path);value['payload']['correct']=True;j.atomic(path,value)
    with pytest.raises(ValueError,match='digest'): j.Journal(tmp_path,'query','one',['a'])
    with pytest.raises(ValueError,match='Duplicate'): j.Journal(tmp_path,'query','one',['a','a'])


@pytest.mark.parametrize('committed',[False,True])
def test_interrupted_attempt_retained_without_repeating_committed_record(modules,tmp_path,committed):
    j,_=modules;v=j.Journal(tmp_path,'query','one',['a','b'])
    attempt=j.begin_attempt(tmp_path,v,'epoch')
    if committed: v.append('a',dict(correct=False))
    j.recover_inflight(tmp_path,{'query':v})
    receipt=j.load(next((tmp_path/'interruptions').glob('*.json')))
    assert receipt['attempt_id']==attempt['attempt_id'] and receipt['already_committed']==committed
    assert len(v.records)==int(committed) and not (tmp_path/'inflight.json').exists()
    j.recover_inflight(tmp_path,{'query':v})
    assert len(list((tmp_path/'interruptions').glob('*.json')))==1


def test_old_feature_and_symlink_escape_rejected_before_array_load(modules,tmp_path):
    j,runner=modules;root=tmp_path/'candidate';root.mkdir();old=tmp_path/'old.npz';old.write_bytes(b'not a feature')
    row={'sha256':'A'};record={'payload':dict(ok=True,source_sha256='A',feature=str(old),feature_sha256=j.file_sha(old))}
    with pytest.raises(ValueError,match='outside'): runner.validate_feature(root,{},row,record)
    with pytest.raises(ValueError,match='outside'): j.inside(root/'..'/'old.npz',root)


def test_exclusive_atomic_does_not_overwrite_old_failure(modules,tmp_path):
    j,_=modules;path=tmp_path/'record.json';j.atomic(path,{'correct':False},exclusive=True);before=path.read_bytes()
    with pytest.raises(FileExistsError): j.atomic(path,{'correct':True},exclusive=True)
    assert path.read_bytes()==before


def test_kernel_lock_blocks_second_process_and_releases_on_exit(modules,tmp_path):
    j,_=modules
    script="import sys;sys.path.insert(0,sys.argv[1]);from smpd_run_journal import run_lock\nwith run_lock(sys.argv[2]): pass"
    command=[sys.executable,'-c',script,str(Path(j.__file__).parent),str(tmp_path)]
    with j.run_lock(tmp_path):
        result=subprocess.run(command,capture_output=True,text=True)
        assert result.returncode!=0
    assert subprocess.run(command,capture_output=True,text=True).returncode==0


def test_fixed_order_keeps_all_failures_and_inventory_tie_order(modules):
    _,runner=modules
    p={'rows':[dict(sample='b',subject='001',index=5,enrollment=False,old_failed=True),
               dict(sample='a',subject='001',index=5,enrollment=False,old_failed=False),
               dict(sample='e',subject='001',index=0,enrollment=True)]}
    assert [r['sample'] for r in runner.ordered_rows(p,False)]==['b','a']


def test_environment_lock_survives_json_round_trip(modules):
    _,runner=modules;value=runner.environment()
    assert json.loads(json.dumps(value))==value


def test_outcomes_are_disjoint_and_rejection_is_not_correct(modules):
    _,r=modules
    q=dict(http_status=200,identity='smpd:001:right',result=dict(status='MATCH',user_id='smpd-001-right',score=.2,second_score=.3))
    assert r.outcome(q)=='correct'
    assert r.outcome(dict(q,result=dict(q['result'],second_score=.2)))=='true_identity_nonunique'
    assert r.outcome(dict(q,result=dict(q['result'],user_id='other')))=='wrong_identity_accepted'
    assert r.outcome(dict(q,result=dict(status='RETRY')))=='rejected'
    assert r.outcome(dict(q,http_status=400))=='processing_failure'


def test_report_keeps_primary_duplicates_and_unregistered_failures(modules,tmp_path):
    j,_=modules;report=importlib.import_module('report_terminal_smpd')
    rows=[dict(outcome='correct',ms=1,result={},truth_enrolled=True),
          dict(outcome='wrong_identity_accepted',ms=3000,result={},truth_enrolled=False),
          dict(outcome='processing_failure',ms=2,result={},truth_enrolled=False)]
    value=report.summarize(rows)
    assert value['total']==3 and sum(value['outcomes'].values())==3
    assert value['accuracy']==1/3 and value['correct_within_2500']==1


def test_supervisor_continuation_does_not_select_on_correctness(modules,monkeypatch,tmp_path):
    _,runner=modules;supervisor=importlib.import_module('supervise_terminal_smpd')
    report=importlib.import_module('report_terminal_smpd')
    p={'run_fingerprint':'F'};op={'operator_fingerprint':'O','selection':'operational only'}
    monkeypatch.setattr(supervisor,'validate_lock',lambda root:(p,op))
    monkeypatch.setattr(runner,'verify',lambda *args,**kwargs:None)
    monkeypatch.setattr(runner,'resources_ok',lambda *args,**kwargs:{'available_bytes':12*1024**3})
    values=[dict(capture={'input_sha256':'S'},source_sha256='S',http_status=200,
        terminal_rf={'policy':runner.POLICY,'unknown_calls':0},ms=4000,correct=False),
        dict(capture={'input_sha256':'T'},source_sha256='T',http_status=400,terminal_rf=None,ms=500,correct=False)]
    summary=dict(status={'state':'paused_preflight'},completed_queries=2,
        fixed_registration_attempts_completed=460,registered_identities=76,journal_tip='J',
        overall={'correct':0,'wrong':1,'processing_failure':1})
    monkeypatch.setattr(report,'snapshot',lambda root:(summary,values))
    receipt=supervisor.validate_preflight(tmp_path)
    assert receipt['allowed'] and receipt['completed_prefix']==2
    values[0]['terminal_rf']['unknown_calls']=1
    with pytest.raises(ValueError,match='trace'):supervisor.validate_preflight(tmp_path)


@pytest.mark.parametrize('state,stop', [('failed_preserving_prefix',False),('query_checkpoint',True)])
def test_supervisor_never_restarts_failure_or_user_stop(modules,monkeypatch,tmp_path,state,stop):
    j,_=modules;s=importlib.import_module('supervise_terminal_smpd');(tmp_path/'supervision').mkdir()
    j.atomic(tmp_path/'status.json',dict(state=state,completed_queries=0))
    if stop:(tmp_path/'STOP').touch()
    monkeypatch.setattr(s,'validate_lock',lambda root:None)
    def forbidden(*args,**kwargs):raise AssertionError('Must not start a worker')
    monkeypatch.setattr(s.subprocess,'Popen',forbidden)
    s.watch(tmp_path)
    assert j.load(tmp_path/'supervisor-status.json')['state'] in ('stopped_by_STOP','worker_failed_no_restart')
