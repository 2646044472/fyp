"""One-shot dependency supervisor for this frozen run, never a recurring task.

Wait for the existing worker's two *formal* queries, validate operational
integrity/resources without selecting on correctness, then continue query3
using the very same runner/version. STOP/failure is never automatically resumed.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

from smpd_run_journal import atomic, digest, file_sha, load, run_lock
import run_terminal_smpd as run
from report_terminal_smpd import report


def seal(root):
    p=load(root/'protocol.json')
    if list((root/'records/query').glob('*.json')):
        raise ValueError('Supervisor must be sealed before the first formal query')
    value=dict(schema=1,run_fingerprint=p['run_fingerprint'],created_unix=time.time(),
        runner_sha256=file_sha(Path(run.__file__)),supervisor_sha256=file_sha(__file__),
        report_sha256=file_sha(Path(__file__).with_name('report_terminal_smpd.py')),
        preflight_completed_queries=2,requires_state='paused_preflight',
        selection='Operational integrity/resources only; correctness and score values never select continuation.',
        stop='STOP, worker failure/absence, incompatible locks, invalid prefix or insufficient memory stops supervision. No automatic crash restart.',
        scope='One continuation of the current full3217 evaluation; no other experiment, schedule or deployment.',
        python=str(Path(sys.executable).resolve()))
    value['operator_fingerprint']=digest(value)
    atomic(root/'operator-lock.json',value,exclusive=True)
    print(json.dumps(value),flush=True)


def validate_lock(root):
    value=load(root/'operator-lock.json');p=load(root/'protocol.json')
    if digest({k:v for k,v in value.items() if k!='operator_fingerprint'})!=value['operator_fingerprint']:
        raise ValueError('Operator lock fingerprint mismatch')
    for actual,expected in ((p['run_fingerprint'],value['run_fingerprint']),
        (file_sha(__file__),value['supervisor_sha256']),
        (file_sha(Path(run.__file__)),value['runner_sha256']),
        (file_sha(Path(__file__).with_name('report_terminal_smpd.py')),value['report_sha256']),
        (str(Path(sys.executable).resolve()),value['python'])):
        if actual!=expected: raise ValueError('Supplemental execution lock changed')
    return p,value


def validate_preflight(root):
    p,operator=validate_lock(root)
    summary,values=__import__('report_terminal_smpd').snapshot(root)
    state=summary['status']
    if state['state']!='paused_preflight' or summary['completed_queries']!=2:
        raise ValueError('Expected exact two-query operational pause')
    if summary['fixed_registration_attempts_completed']!=460 or not summary['registered_identities']:
        raise ValueError('Incomplete fixed registration/gallery')
    # Correct/wrong/ROI-failed are legitimate outcomes, never a branch condition.
    for q in values:
        if q['capture'].get('fatal') or q['capture'].get('input_sha256')!=q['source_sha256']:
            raise ValueError('Preflight input/resource integrity failed')
        if q['http_status']==200:
            trace=q['terminal_rf']
            if not trace or trace['policy']!=run.POLICY or trace['unknown_calls']:
                raise ValueError('Preflight candidate trace invalid')
    run.verify(p,dependencies=True)
    resources=run.resources_ok(p,startup=True)
    return dict(run_fingerprint=p['run_fingerprint'],operator_fingerprint=operator['operator_fingerprint'],
        checked_unix=time.time(),completed_prefix=2,query_record_tip=summary['journal_tip'],
        fixed_enrollments=460,registered_identities=summary['registered_identities'],
        first_query_ms=[q['ms'] for q in values],summary=summary['overall'],memory=resources,
        allowed=True,selection=operator['selection'],no_completed_queries_repeated=True)


def alive(pid):
    import psutil
    try:
        process=psutil.Process(pid)
        return process.is_running() and process.status()!=psutil.STATUS_ZOMBIE
    except psutil.NoSuchProcess:
        return False


def watch(root):
    validate_lock(root);started=time.time()
    with run_lock(root/'supervision'):
        def status(state,**extra):
            atomic(root/'supervisor-status.json',dict(state=state,pid=__import__('os').getpid(),
                started_unix=started,updated_unix=time.time(),**extra))
        try:
            # Current worker already owns its own runner.lock. Never start a
            # parallel worker, and never turn a user STOP into continuation.
            while True:
                validate_lock(root)
                state=load(root/'status.json')
                if (root/'STOP').exists(): status('stopped_by_STOP');return
                if state['state']=='failed_preserving_prefix':
                    status('worker_failed_no_restart',failure=state.get('failure'));return
                if state['state']=='paused_preflight': break
                if not state.get('pid') or not alive(state['pid']):
                    status('worker_absent_no_restart',last_worker_state=state['state']);return
                status('waiting_for_current_preflight',enrollment_completed=state.get('enrollment_completed',0),completed_queries=state['completed_queries'])
                time.sleep(15)
            while alive(state['pid']):
                if (root/'STOP').exists(): status('stopped_by_STOP');return
                time.sleep(2)
            receipt=validate_preflight(root)
            atomic(root/'preflight-receipt.json',receipt,exclusive=True)
            report(root,root/'report')
            if (root/'STOP').exists(): status('stopped_by_STOP');return
            command=[sys.executable,'-u',str(Path(run.__file__).resolve()),'work',str(root)]
            full_started=time.time()
            with (root/'full.stdout.log').open('xb') as stdout,(root/'full.stderr.log').open('xb') as stderr:
                process=subprocess.Popen(command,stdout=stdout,stderr=stderr,cwd=run.APP,
                    creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
                status('full_worker_started',launcher_pid=process.pid,completed_queries=2)
                last_report=2
                while process.poll() is None:
                    state=load(root/'status.json')
                    if state['completed_queries']>=last_report+25:
                        report(root,root/'report');last_report=state['completed_queries']
                    status('full_worker_running',launcher_pid=process.pid,
                           completed_queries=state['completed_queries'],worker_state=state['state'],
                           full_started_unix=full_started,full_elapsed_s=time.time()-full_started,
                           additional_completed_queries=max(0,state['completed_queries']-2),
                           wall_queries_per_hour=max(0,state['completed_queries']-2)/(time.time()-full_started)*3600,
                           timing_scope='Wall throughput since full worker launch, including gallery rebuild and checkpoints; early-prefix estimate only.')
                    time.sleep(15)
            summary=report(root,root/'report')
            status('complete' if summary['complete'] and process.returncode==0 else 'worker_stopped_no_restart',
                   worker_exit_code=process.returncode,completed_queries=summary['completed_queries'])
        except Exception as error:
            status('supervisor_failed_no_restart',failure=type(error).__name__+': '+str(error))
            raise


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=('seal','watch'));parser.add_argument('root',type=Path)
    args=parser.parse_args();root=args.root.resolve()
    if args.mode=='seal':
        (root/'supervision').mkdir(exist_ok=True);seal(root)
    else: watch(root)
