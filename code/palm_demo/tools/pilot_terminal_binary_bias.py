"""One device-only, non-resumable RF binary-bias mechanism screen.

Four original baseline HTTP queries capture actual compared codes once. Only
after all four exact historical parity gates pass are A/B/C calculated offline.
C alone is a candidate; B is diagnostic. No public query or fresh enrollment.
Private codes, role bindings and full rankings must remain in ignored runtime.
"""
import argparse
import copy
import gc
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading
import time
import traceback

APP = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(APP), str(APP/'tools')]
from pilot_device_halfturn_guard import load, save, sha, digest
from experiment_resource_limits import resource_fault
from terminal_binary_bias import POLICY, ARMS, BinaryMarginalRF, distances, aggregate_frames, classify

PARENT = APP/'runtime/terminal-rotation-six-20261101'
PUBLIC = APP/'runtime/smpd-v27-continuation-20261031-r1'


def pause():
    status=load(PUBLIC/'status.json')
    if (status['state']!='paused_STOP' or status['completed_queries']!=1239 or
        not (PUBLIC/'STOP').exists() or (PUBLIC/'inflight.json').exists()):
        raise RuntimeError('Original public pause changed')
    return {str(PUBLIC/name):sha(PUBLIC/name) for name in ('status.json','STOP')}


def no_workers():
    import psutil
    own=psutil.Process();exclude={own.pid,*(p.pid for p in own.parents())}
    for process in psutil.process_iter(['pid','name']):
        if process.pid in exclude or (process.info['name'] or '').lower() not in {
            'python.exe','pythonw.exe','powershell.exe','pwsh.exe','cmd.exe','uv.exe','git.exe'}:
            continue
        try:command=' '.join(process.cmdline()).lower()
        except psutil.NoSuchProcess:continue
        # An explicit access denial is not ignored or retried another way.
        if any(token in command for token in ('palm_demo','smpd','fyp')):
            raise RuntimeError('Other project process is active: '+str(process.pid))


def prepare(root):
    if root.exists():raise FileExistsError('Fresh isolated output required')
    no_workers(); boundary=pause(); old=load(PARENT/'protocol.json')
    items=[copy.deepcopy(item) for item in old['items'] if item['domain']=='device']
    if [i['label'] for i in items]!=['D1','D2','D3','D4']:
        raise ValueError('Expected frozen four roles')
    for item in items:
        record=PARENT/'device/baseline/records'/(item['label']+'.json')
        item['exact_record']=load(record); item['exact_record_path']=str(record)
    # Reviewed migrations: opt-in diagnostics, optional immutable pair export,
    # and post-return lifecycle cleanup (run_group itself remains identical).
    changed={'registered_matcher.py','tools/terminal_rf_evidence.py','tools/pilot_terminal_rotation.py'}
    sources={}
    for path,expected in old['sources_sha256'].items():
        path=Path(path); current=sha(path)
        if current!=expected and path.relative_to(APP).as_posix() not in changed:
            raise ValueError('Unreviewed inherited source change: '+str(path))
        sources[str(path)]=current
    tracked=subprocess.check_output(['git','ls-files','*.py'],cwd=APP,text=True).splitlines()
    extra=['tools/terminal_binary_bias.py','tools/pilot_terminal_binary_bias.py','tests/test_terminal_binary_bias.py',
           'tools/experiment_resource_limits.py']
    for name in [*tracked,*extra]:sources[str((APP/name).resolve())]=sha(APP/name)
    metadata={str(PARENT/'protocol.json'):sha(PARENT/'protocol.json'),
              **{i['exact_record_path']:sha(i['exact_record_path']) for i in items},**boundary}
    import xml.etree.ElementTree as ET
    tests=APP/'runtime/terminal-binary-bias-build-20261102/tests.xml'
    suites=ET.parse(tests).getroot()
    if any(int(s.get('failures','0')) or int(s.get('errors','0')) for s in suites.iter('testsuite')):
        raise ValueError('Unit tests have failures')
    metadata[str(tests)]=sha(tests)
    p=dict(schema=1,policy=POLICY,scope='Four seen device queries; offline metric screen, not candidate HTTP or Pi timing',
           created_unix=time.time(),executable=sys.executable,model_root=old['model_root'],
           model_setting='No independently verified execution-model receipt',
           sources_sha256=sources,models_sha256=old['models_sha256'],dependencies_sha256=old['dependencies_sha256'],
           metadata_sha256=metadata,templates_sha256={'device':old['templates_sha256']['device']},items=items,
           expected_gallery={'device':11},thresholds=old['thresholds'],
           formulas={'A':'(a+b-2c)/n','B':'A+0.5*(2a/n-1)*(2b/n-1)',
                     'C':'0.5*(1-(n*c-a*b)/sqrt(a*(n-a)*b*(n-b)))',
                     'constant_C':1,'sole_candidate':'C','B_diagnostic_only':True,
                     'scope':'original terminal RF only; identical pairs,81 shifts,min per frame,mean best2 of5'},
           gates={'all_four_exact_baselines_before_offline':True,
                  'mechanism':'at least one error has greater mean-product penalty on original wrong-winning cells than true-winning cells',
                  'candidate':'C corrects >=1 error; preserves both controls; no added processing failure,rejection or tie',
                  'no_parameter_or_sample_retry':True},
           resources={'startup_available_GiB':12,'running_available_GiB':2,'max_RSS_GiB':14,
                      'workers':1,'sample_interval_s':1},
           max_seconds=1800,max_http_seconds=600,retry=False,resume=False,public_queries=0,full168=False)
    p['fingerprint']=digest(p)
    root.mkdir(parents=True,exist_ok=False)
    save(root/'protocol.json',p,True)
    shutil.copyfile(__file__,root/'executed-driver.py')
    print(json.dumps({'prepared':True,'fingerprint':p['fingerprint'],'roles':4}),flush=True)


def verify(p):
    if digest({k:v for k,v in p.items() if k!='fingerprint'})!=p['fingerprint']:
        raise ValueError('Protocol modified')
    if str(Path(sys.executable).resolve())!=p['executable']:raise ValueError('Wrong executable')
    for field in ('sources_sha256','models_sha256','dependencies_sha256','metadata_sha256'):
        for path,expected in p[field].items():
            if sha(path)!=expected:raise ValueError('Locked file changed: '+path)
    for files in p['templates_sha256'].values():
        for path,expected in files.items():
            if sha(path)!=expected:raise ValueError('Original template changed: '+path)
    for item in p['items']:
        if sha(item['row']['original'])!=item['row']['sha256']:raise ValueError('Original image changed')
    pause()


class Monitor:
    def __init__(self,root,budget):
        import psutil
        self.psutil=psutil;self.process=psutil.Process();self.root=root;self.budget=budget
        self.start=time.perf_counter();self.stop=threading.Event();self.violations=[];self.samples=[];self.phase='preflight'
        self.thread=threading.Thread(target=self.watch,name='bounded-resource-sampler',daemon=True)
    def sample(self):
        info=self.process.memory_info()
        return dict(elapsed_s=time.perf_counter()-self.start,phase=self.phase,rss=info.rss,
                    peak_wset=getattr(info,'peak_wset',None),available=self.psutil.virtual_memory().available,
                    cpu_s=sum(self.process.cpu_times()[:2]))
    def check(self,startup=False):
        value=self.sample();fault=resource_fault(value['available'],value['rss'],startup=startup)
        if fault or self.violations:raise MemoryError('Frozen resource limit: '+json.dumps(dict(fault=fault,sample=value,first_violation=self.violations[:1])))
        if value['elapsed_s']>self.budget:raise TimeoutError('Fixed 30-minute wall budget')
        if (self.root/'STOP').exists():raise InterruptedError('Local STOP')
        pause()
        return value
    def watch(self):
        with (self.root/'telemetry.jsonl').open('x',encoding='utf-8') as stream:
            while not self.stop.is_set():
                value=self.sample();self.samples.append(value);stream.write(json.dumps(value)+'\n');stream.flush()
                if resource_fault(value['available'],value['rss']):self.violations.append(value)
                self.stop.wait(1)
    def mark(self,name,report,**extra):
        self.phase=name;value=dict(self.check(),**extra);report['phases'].append(value)
        print(json.dumps({'phase':name,**value}),flush=True)


def export_pairs(root,item,p,pairs,trace):
    import numpy as np
    unique=sorted(set().union(*pairs.values()))
    index={pair:i for i,pair in enumerate(unique)}
    codes=np.asarray([[list(a),list(b)] for a,b in unique],np.uint8)
    folder=root/'captured'/item['label'];folder.mkdir(parents=True,exist_ok=False)
    with (folder/'codes.npz').open('xb') as stream:np.savez(stream,codes=codes)
    manifest=dict(cache_key=digest(dict(protocol=p['fingerprint'],policy=POLICY,backend='CPUExecutionProvider',
                                      image_sha256=item['row']['sha256'],role=item['label'])),
                  protocol=p['fingerprint'],role=item['label'],codes_sha256=sha(folder/'codes.npz'),
                  order=list(dict.fromkeys(user for user,j in pairs)),trace=trace,
                  frames=[dict(user=user,frame=j,pairs=sorted(index[v] for v in values)) for (user,j),values in pairs.items()])
    if len(manifest['frames'])!=55 or any(not row['pairs'] for row in manifest['frames']):
        raise ValueError('Incomplete 11 x 5 comparison provenance')
    save(folder/'manifest.json',manifest,True)
    return folder


def offline(folder,item,baseline,monitor,fingerprint):
    import numpy as np
    started=time.perf_counter();m=load(folder/'manifest.json')
    expected_key=digest(dict(protocol=fingerprint,policy=POLICY,backend='CPUExecutionProvider',
                             image_sha256=item['row']['sha256'],role=item['label']))
    if m['cache_key']!=expected_key or m['protocol']!=fingerprint or m['role']!=item['label']:
        raise ValueError('Incompatible capture dependency/backend/role cache key')
    if sha(folder/'codes.npz')!=m['codes_sha256']:raise ValueError('Captured code cache changed')
    with np.load(folder/'codes.npz',allow_pickle=False) as archive:codes=archive['codes']
    terminal=baseline['terminal_rf']['rf_applied']
    kernel=BinaryMarginalRF();counts=[];metric=[]
    for row in codes:
        monitor.check()
        left,right=[np.unpackbits(v,bitorder='little').reshape(32,32) for v in row]
        table=kernel.counts(left,right);counts.append(table)
        if terminal:metric.append(distances(table))
    with (folder/'counts.npz').open('xb') as stream:np.savez(stream,counts=np.asarray(counts,np.uint16))
    if not terminal:
        result=dict(label=item['label'],terminal=False,
                    arms={arm:dict(scores=baseline['scores'],decision=classify(baseline['scores'],item['row']['identity'].replace(':','-'),m['order'])) for arm in ARMS},
                    mechanism=None,unique_code_pairs=len(codes),frame_cells=55,shifts_per_pair=81,
                    counts_sha256=sha(folder/'counts.npz'),offline_ms=(time.perf_counter()-started)*1000,
                    note='Counts retained diagnostically; all arms preserve original confident result, no new distance evaluated')
        save(folder/'offline.json',result,True)
        return result
    pair_values={arm:[float(v[arm].min()) for v in metric] for arm in ARMS}
    frames={};penalties={};winners={}
    for frame in m['frames']:
        key=frame['user'],frame['frame'];indices=frame['pairs']
        frames[key]={arm:min(pair_values[arm][i] for i in indices) for arm in ARMS}
        best=frames[key]['A']; cells=[(i,int(j)) for i in indices for j in np.flatnonzero(metric[i]['A']==best)]
        penalty=[.5*float(metric[i]['signed_mean_product'][j]) for i,j in cells]
        # Keep all tied original winning cells. Interval comparisons avoid choosing
        # whichever tie would make the proposed explanation look strongest.
        penalties[key]=(min(penalty),max(penalty));winners[key]=cells
    scores={arm:{user:aggregate_frames([frames[user,j][arm] for j in range(5)]) for user in m['order']} for arm in ARMS}
    if scores['A']!=baseline['scores']:raise ValueError('Offline A full-gallery RF vector not exact')
    truth=item['row']['identity'].replace(':','-')
    arms={arm:dict(scores=scores[arm],decision=classify(scores[arm],truth,m['order'])) for arm in ARMS}
    mechanism=None
    if item['role'].startswith('device_wrong'):
        wrong=baseline['result']['user_id']
        def winning_penalty_interval(user):
            ordered=sorted((frames[user,j]['A'],j) for j in range(5))
            # Enumerate every best-two tie selection, no label-based tie pick.
            import itertools
            selections=[js for js in itertools.combinations(range(5),2)
                        if sorted(frames[user,j]['A'] for j in js)==[v[0] for v in ordered[:2]]]
            return (min(sum(penalties[user,j][0] for j in js)/2 for js in selections),
                    max(sum(penalties[user,j][1] for j in js)/2 for js in selections))
        wp,tp=winning_penalty_interval(wrong),winning_penalty_interval(truth)
        mechanism=dict(wrong_penalty_interval=wp,true_penalty_interval=tp,
                       conservative_bias_advantage=wp[0]-tp[1],bias_supported=wp[0]>tp[1],
                       rule='wrong minimum penalty > true maximum penalty across all original-winning ties')
    result=dict(label=item['label'],terminal=True,arms=arms,mechanism=mechanism,
                unique_code_pairs=len(codes),frame_cells=55,shifts_per_pair=81,
                constant_overlap_cells=sum(int(v['constant'].sum()) for v in metric),
                counts_sha256=sha(folder/'counts.npz'),offline_ms=(time.perf_counter()-started)*1000,
                per_frame=[dict(user=u,frame=j,scores=v,original_winners=winners[u,j],
                                original_penalty_interval=penalties[u,j]) for (u,j),v in frames.items()])
    save(folder/'offline.json',result,True)
    return result


def evaluate(rows):
    if len(rows)!=4 or [r['label'] for r in rows]!=['D1','D2','D3','D4']:
        raise ValueError('Four fixed results required')
    evidence=any(r['mechanism'] and r['mechanism']['bias_supported'] for r in rows[:2])
    correction=any(r['arms']['C']['decision']['outcome']=='correct' for r in rows[:2])
    controls=all(r['arms']['C']['decision']['outcome']=='correct' for r in rows[2:])
    no_new_bad=all(r['arms']['C']['decision']['outcome'] not in {'rejected','processing_failure','true_identity_nonunique'}
                   and not r['arms']['C']['decision']['tied'] for r in rows)
    return dict(mechanism_supported=evidence,C_correction=correction,correct_controls_preserved=controls,
                no_new_failure_rejection_or_tie=no_new_bad,pilot_pass=evidence and correction and controls and no_new_bad)


def run(root):
    p=load(root/'protocol.json')
    if (root/'ATTEMPTED.json').exists():raise RuntimeError('One attempt only; no resume or retry')
    save(root/'ATTEMPTED.json',{'utc_unix':time.time(),'pid':os.getpid()},True)
    monitor=Monitor(root,p['max_seconds']);captures=[]
    report=dict(complete=False,pilot_pass=False,denominator=4,groups=[],queries=[],offline=[],phases=[],
                fingerprint=p['fingerprint'],failure=None,public_queries=0,candidate_http_queries=0,
                fresh_enrollment_attempts=0,scope=p['scope'])
    try:
        no_workers();monitor.mark('initial_startup',report,startup_measurement=monitor.check(startup=True))
        monitor.thread.start();monitor.mark('verify_frozen_protocol',report);verify(p)
        from evaluate_raw_smpd import install_windows_capacity
        from retained_evidence_pilot import install_retained_evidence_pilot
        from compnet_pilot import CompNetPilot
        from gallery import Gallery
        from pilot_terminal_rotation import run_group
        import terminal_rf_evidence
        import cv2
        cv2.setNumThreads(1);os.environ['PALM_COMPNET_MODEL_ROOT']=p['model_root']
        report['windows_capacity']=install_windows_capacity();install_retained_evidence_pilot()
        real_install=terminal_rf_evidence.install
        def capture(pairs,trace):captures.append((pairs,trace))
        def capture_install(algorithm):
            real_install(algorithm,capture=capture)
            old=algorithm.base.match;calls=[0]
            def guarded(a,b):
                calls[0]+=1
                if calls[0]%32==0:monitor.check()
                return old(a,b)
            algorithm.base.match=guarded
            return algorithm
        terminal_rf_evidence.install=capture_install
        old_load=Gallery._load_prepared;old_embed=CompNetPilot.extract
        observations={'gallery_load_calls':0,'compnet_embedding_calls':0}
        def checked_load(self,*a,**kw):
            monitor.check();result=old_load(self,*a,**kw);observations['gallery_load_calls']+=1;monitor.check();return result
        def checked_embed(self,*a,**kw):
            monitor.check()
            if self.session.get_providers()!=['CPUExecutionProvider']:raise ValueError('Expected CPU-only CompNet session')
            result=old_embed(self,*a,**kw);observations['compnet_embedding_calls']+=1;monitor.check();return result
        Gallery._load_prepared=checked_load;CompNetPilot.extract=checked_embed
        monitor.mark('baseline_epoch',report)
        try:run_group(root,p,'device','baseline',report,monitor.check)
        finally:
            terminal_rf_evidence.install=real_install;Gallery._load_prepared=old_load;CompNetPilot.extract=old_embed
            from pilot_epoch_cleanup import collect_finished_epoch
            report['epoch_cleanup']=collect_finished_epoch()
            report['observations']=observations
        if len(captures)!=4 or len(report['queries'])!=4:raise ValueError('Incomplete fixed baseline capture')
        for item,current in zip(p['items'],report['queries']):
            expected=item['exact_record']
            if (current['label']!=item['label'] or current['primary']!=expected['primary'] or
                current['capture']!=expected['capture'] or current['scores']!=expected['scores'] or
                any(current['result'].get(k)!=expected['result'].get(k) for k in
                    ('status','user_id','score','second_score','recognition_route')) or
                current['http_status']!=expected['http_status']):
                raise ValueError('Exact four-baseline ROI/pixel/full-vector/route/decision parity failed')
        report['all_four_baselines_exact']=True
        monitor.mark('export_captured_pairs',report)
        folders=[]
        for item,(pairs,trace) in zip(p['items'],captures):
            monitor.check();folders.append(export_pairs(root,item,p,pairs,trace))
        captures.clear();gc.collect()
        monitor.mark('offline_paired_metrics',report)
        for item,current,folder in zip(p['items'],report['queries'],folders):
            monitor.check();result=offline(folder,item,current,monitor,p['fingerprint']);report['offline'].append(result)
            save(root/'progress.json',report)
            print(json.dumps({'offline_role':result['label'],'outcomes':{a:result['arms'][a]['decision']['outcome'] for a in ARMS},
                              'mechanism':result['mechanism'],'offline_ms':result['offline_ms']}),flush=True)
        report['gates']=evaluate(report['offline']);report['pilot_pass']=report['gates']['pilot_pass'];report['complete']=True
    except Exception as error:
        report['failure']=type(error).__name__+': '+str(error);report['traceback']=traceback.format_exc()
        print(report['failure'],flush=True)
    finally:
        monitor.stop.set()
        if monitor.thread.is_alive():monitor.thread.join(3)
        report['final_resource']=monitor.sample();report['violations']=monitor.violations
        report['min_sampled_available']=min((s['available'] for s in monitor.samples),default=None)
        report['max_sampled_rss']=max((s['rss'] for s in monitor.samples),default=None)
        report['sample_count']=len(monitor.samples)
        try:verify(p);report['frozen_originals_and_protocol_verified_after']=True
        except Exception as error:report['preservation_error']=str(error);report['pilot_pass']=False
        report['wall_s']=time.perf_counter()-monitor.start
        if monitor.violations:report['pilot_pass']=False
        save(root/'results.json',report,True);save(root/'progress.json',report)
        print(json.dumps({k:report.get(k) for k in ('complete','pilot_pass','failure','gates','wall_s','sample_count','final_resource')}),flush=True)
    return 0 if report['pilot_pass'] else 2


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=('prepare','run'))
    parser.add_argument('root',type=Path);args=parser.parse_args()
    if args.mode=='prepare':prepare(args.root.resolve())
    else:sys.exit(run(args.root.resolve()))
