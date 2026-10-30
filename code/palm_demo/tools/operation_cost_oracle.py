"""Private-memory operation oracle and scalar-only thread-scoped cost recorder.

This diagnostic is NOT an optimization/cache for live recognition. Stored SIFT
outputs may only be replayed for the same prevalidated request/call graph.
"""
from collections import defaultdict
import hashlib,threading,time
import numpy as np


def spec(value,depth=0):
    if isinstance(value,np.ndarray):return dict(type='ndarray',shape=list(value.shape),dtype=value.dtype.str,bytes=value.nbytes,c_contiguous=bool(value.flags.c_contiguous))
    if depth>2:return dict(type=type(value).__name__)
    if isinstance(value,(tuple,list)):return [spec(v,depth+1)for v in value[:8]]
    if isinstance(value,dict):return {str(k):spec(v,depth+1)for k,v in list(value.items())[:8]}
    if isinstance(value,(int,float,bool,type(None))):return value
    return dict(type=type(value).__name__)


def clone(value):
    if isinstance(value,np.ndarray):return value.copy()
    if isinstance(value,tuple):return tuple(clone(v)for v in value)
    return value


def size(value):
    if isinstance(value,np.ndarray):return value.nbytes
    if isinstance(value,(tuple,list)):return sum(size(v)for v in value)
    return 0


class OperationTrace:
    def __init__(self):self.active=False;self.nodes=[];self.local=threading.local();self.lock=threading.Lock();self.originals=[]
    def function(self,fn,label,category):
        def call(*args,**kw):
            if not self.active:return fn(*args,**kw)
            inputs=spec(args);parent=getattr(self.local,'node',None);start=time.perf_counter();cpu=time.thread_time()
            with self.lock:
                node=dict(id=len(self.nodes),parent=None if parent is None else parent['id'],thread=threading.get_ident(),label=label,category=category,start_ms=(start-self.start)*1000,input_spec=inputs,child_cpu_ms=0.)
                self.nodes.append(node)
            self.local.node=node
            try:
                value=fn(*args,**kw)
                return value
            finally:
                end=time.perf_counter();used=(time.thread_time()-cpu)*1000
                node.update(end_ms=(end-self.start)*1000,inclusive_ms=(end-start)*1000,thread_cpu_ms=used,exclusive_thread_cpu_ms=used-node.pop('child_cpu_ms'))
                self.local.node=parent
                if parent is not None:parent['child_cpu_ms']+=used
                if 'value'in locals():node['output_spec']=spec(value)
        return call
    def wrap(self,owner,name,label,category,static=False):
        old=getattr(owner,name);self.originals.append((owner,name,owner.__dict__.get(name)if isinstance(owner,type)else old))
        value=self.function(old,label,category);setattr(owner,name,staticmethod(value)if static else value)
    def begin(self):self.nodes=[];self.start=time.perf_counter();self.active=True
    def finish(self):
        self.active=False;children=defaultdict(list)
        for n in self.nodes:
            if n['parent']is not None:children[n['parent']].append((n['start_ms'],n['end_ms']))
        segments=[]
        for n in self.nodes:
            cursor=n['start_ms'];exclusive=[]
            for lo,hi in sorted(children[n['id']]):
                if lo>cursor:exclusive.append((cursor,lo))
                cursor=max(cursor,hi)
            if cursor<n['end_ms']:exclusive.append((cursor,n['end_ms']))
            n['exclusive_wall_ms']=sum(hi-lo for lo,hi in exclusive)
            segments.extend((lo,hi,n['category'])for lo,hi in exclusive)
        # Across threads: use each same-thread-exclusive segment once on the
        # global wall clock. Simultaneous different operators get a mixed bin.
        endpoints=defaultdict(list)
        for lo,hi,cat in segments:endpoints[lo].append((cat,1));endpoints[hi].append((cat,-1))
        active=defaultdict(int);partition=defaultdict(float);last=None
        for instant,changes in sorted(endpoints.items()):
            if last is not None and instant>last:
                cats=sorted(k for k,v in active.items()if v>0 and k!='framework')
                if not cats and active.get('framework',0)>0:cats=['framework']
                if cats:partition[cats[0]if len(cats)==1 else 'parallel_mixed:'+'+'.join(cats)]+=instant-last
            for cat,delta in changes:active[cat]+=delta
            last=instant
        return dict(nodes=self.nodes,global_wall_partition_ms=dict(partition),
            warning='Thread CPU is issuing-thread CPU, excludes native worker CPU. Process CPU is reported once per HTTP. Global wall mixed bins preserve concurrency instead of adding overlapping durations.')
    def close(self):
        for owner,name,old in reversed(self.originals):
            if old is None:delattr(owner,name)
            else:setattr(owner,name,old)


class FeatureOracle:
    def __init__(self,trace,budget=256*1024*1024):
        self.trace=trace;self.budget=budget;self.mode=None;self.saved={};self.bytes=0;self.local=threading.local();self.lock=threading.Lock();self.originals=[]
    def begin(self,mode):
        self.mode=mode;self.dispatch=defaultdict(int);self.counts=defaultdict(int);self.seen=set();self.validation_ms=0.;self.snapshot_copy_ms=0.;self.replay_copy_ms=0.
    def clear(self):self.saved={};self.bytes=0
    def install_submit(self,owner):
        old=owner.submit;self.originals.append((owner,'submit',old))
        def submit(executor,fn,*args,**kw):
            if self.mode is None:return old(executor,fn,*args,**kw)
            parent=getattr(self.local,'task',())
            with self.lock:index=self.dispatch[parent];self.dispatch[parent]+=1
            task=parent+(index,)
            def run():
                previous=getattr(self.local,'task',());self.local.task=task
                try:return fn(*args,**kw)
                finally:self.local.task=previous
            return old(executor,run)
        owner.submit=submit
    def wrap(self,owner,name,label,static=False):
        old=getattr(owner,name);self.originals.append((owner,name,owner.__dict__.get(name)if isinstance(owner,type)else old));measured=self.trace.function(old,label,'local_features')
        def call(*args,**kw):
            if self.mode is None:return old(*args,**kw)
            task=getattr(self.local,'task',())
            with self.lock:
                key=(task,label,self.counts[task,label]);self.counts[task,label]+=1
            array=np.asarray(args[0]);signature=(array.shape,array.dtype.str)
            if self.mode=='record':
                t=time.perf_counter();digest=hashlib.sha256(array.tobytes()).hexdigest();self.validation_ms+=(time.perf_counter()-t)*1000
                value=measured(*args,**kw);t=time.perf_counter();copy=(array.copy(),clone(value));cost=size(copy)
                with self.lock:
                    assert self.bytes+cost<=self.budget,'Oracle memory budget exceeded'
                    self.saved[key]=(signature,digest,copy);self.bytes+=cost;self.snapshot_copy_ms+=(time.perf_counter()-t)*1000
                return value
            if self.mode=='plain':return old(*args,**kw)
            assert key in self.saved,('Unexpected structural feature call',key)
            expected,digest,(recorded,value)=self.saved[key];assert signature==expected,('Shape/type drift',key)
            with self.lock:self.seen.add(key)
            if self.mode=='verify':
                t=time.perf_counter();assert hashlib.sha256(array.tobytes()).hexdigest()==digest and np.array_equal(array,recorded),('Input drift',key)
                with self.lock:self.validation_ms+=(time.perf_counter()-t)*1000
            t=time.perf_counter();result=clone(value)
            with self.lock:self.replay_copy_ms+=(time.perf_counter()-t)*1000
            return result
        setattr(owner,name,staticmethod(call)if static else call)
    def finish(self):
        if self.mode in('verify','timed'):assert self.seen==set(self.saved),'Missing replay calls'
        value=dict(mode=self.mode,feature_calls=sum(self.counts.values()),saved_operations=len(self.saved),saved_bytes=self.bytes,validation_wall_ms=self.validation_ms,snapshot_copy_wall_ms=self.snapshot_copy_ms,replay_output_copy_wall_ms=self.replay_copy_ms)
        self.mode=None;return value
    def close(self):
        self.mode=None
        for owner,name,old in reversed(self.originals):
            if old is None:delattr(owner,name)
            else:setattr(owner,name,old)
