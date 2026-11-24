"""Full published SMPD original-image evaluation of the frozen staged demo.

prepare streams verified members from the ongoing ordinary ZIP download,
audits every ROI and captures the fixed five enrollment features per identity.
run uses all successfully registered identities together, with the same actual
demo HTTP recognition handlers, fresh original-image ROI/features per query.
No threshold tuning, replacement enrollment frames or cropped-only substitute.
"""
import argparse,base64,binascii,collections,hashlib,inspect,io,json,os,platform,re,struct,sys,textwrap,time,zlib
from pathlib import Path
APP=Path(__file__).resolve().parents[1];sys.path.insert(0,str(APP))
import cv2,numpy as np,psutil
from PIL import Image,ImageOps
from pklnet_roi import PKLNetROI,normalize_roi_pixels,ROI_GEOMETRY_VERSION
from replay_pi_pipeline import ReplayCamera,debug_ui
from retained_evidence_pilot import install_retained_evidence_pilot
from templates import TemplateStore
from payment import PaymentService

MATCHER='FastCCCompNetAlternateROI-v26-experimental'
SOURCES=['biometric.py','compnet_pilot.py','compnet_evidence_matcher.py','compnet_alternate_roi_matcher.py',
    'quality_evidence_matcher.py','pooled_enrollment_matcher.py','affine_enrollment_matcher.py','linked_enrollment_matcher.py',
    'staged_index_matcher.py','guarded_index_matcher.py','proposed_index_matcher.py','indexed_demo_matcher.py',
    'demo_matcher.py','anchored_matcher.py','union_matcher.py','registered_matcher.py','pose_matcher.py',
    'fastcc_accelerated.py','registration_accelerated.py','pklnet_roi.py','pklnet_policy.py','window_roi.py',
    'gallery.py','templates.py','demo_flow.py','acceptance_policy.py','palm_app/debug_ui.py']


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def source_sha(path):return hashlib.sha256(Path(path).read_bytes().replace(b'\r\n',b'\n')).hexdigest()
def save(path,value):
    temp=Path(str(path)+'.tmp');temp.write_text(json.dumps(value,indent=2,default=scalar),encoding='utf-8');temp.replace(path)
def scalar(value):
    if isinstance(value,np.ndarray):return value.tolist()
    if isinstance(value,np.generic):return value.item()
    raise TypeError(type(value).__name__)


def label(member):
    m=re.fullmatch(r'(\d{3})_(F|RF|P|RP)_(\d+)\.[jJ][pP][gG]',Path(member).name)
    if not m:raise ValueError('Unrecognized SMPD image label: '+member)
    person,condition,index=m[1],m[2],int(m[3]);return person,condition,index


class DownloadParts:
    def __init__(self,root,size,block=64*1024**2):self.root=root;self.size=size;self.block=block
    def read(self,offset,count):
        if not 0<=offset<=offset+count<=self.size:raise ValueError('Archive read outside bounds')
        pieces=[]
        while count:
            index,inside=divmod(offset,self.block);length=min(count,self.block-inside);path=self.root/f'{index:04d}.part'
            expected=min(self.block,self.size-index*self.block)
            while not(path.exists()and path.stat().st_size==expected):time.sleep(1)
            with path.open('rb')as stream:stream.seek(inside);data=stream.read(length)
            if len(data)!=length:raise RuntimeError('Incomplete downloaded part')
            pieces.append(data);offset+=length;count-=length
        return b''.join(pieces)
    def member(self,entry):
        header=self.read(entry['offset'],30)
        if header[:4]!=b'PK\x03\x04':raise ValueError('Invalid ZIP local header')
        flags,method=struct.unpack_from('<HH',header,6);name_len,extra_len=struct.unpack_from('<HH',header,26)
        if flags&1:raise ValueError('Encrypted public archive member')
        compressed=self.read(entry['offset']+30+name_len+extra_len,entry['compressed_bytes'])
        if method==0:data=compressed
        elif method==8:data=zlib.decompress(compressed,-15)
        else:raise ValueError('Unsupported public ZIP compression')
        if len(data)!=entry['bytes']or binascii.crc32(data)&0xffffffff!=entry['crc']:raise ValueError('Member size/CRC mismatch')
        return data


class ExifReplay(ReplayCamera):
    def capture_highres(self):
        if not self.queue:raise RuntimeError('Dataset replay input exhausted')
        self.last=self.queue.pop(0);data=Path(self.last['original']).read_bytes()
        if hashlib.sha256(data).hexdigest()!=self.last['sha256']:raise RuntimeError('INPUT_INTEGRITY_FAILURE')
        with Image.open(io.BytesIO(data))as image:full=ImageOps.exif_transpose(image).convert('RGB')
        self.size=list(full.size)
        return full.resize((640,360)),full,{'replay_source_sha256':self.last['sha256']}


def install_windows_capacity():
    """Only resource guards differ: no pose, index, candidate or score change."""
    import indexed_demo_matcher as module
    source=inspect.getsource(module.IndexedDemoMatcher.prepare_gallery)
    old='if packed.nbytes > 256*1024*1024:';assert source.count(old)==1
    candidate=textwrap.dedent(source.replace(old,'if packed.nbytes > 2*1024*1024*1024:').replace('exceeds 256 MiB','exceeds 2 GiB'))
    space=dict(module.__dict__);exec(compile(candidate,'<Windows-evaluation-memory-guard>','exec'),space)
    module.IndexedDemoMatcher.prepare_gallery=space['prepare_gallery']
    module.IndexedDemoMatcher.prepared_cache_limit_bytes=6*1024**3
    return dict(index_bytes=2*1024**3,prepared_cache_bytes=6*1024**3,
        scope='Windows resource allowance only; Pi retains 256MiB limits. Identical complete gallery/candidates/scoring.',
        original_function_sha256=hashlib.sha256(source.encode()).hexdigest(),evaluation_function_sha256=hashlib.sha256(candidate.encode()).hexdigest())


def initialize(runtime,model,*,capacity=False):
    os.environ['PALM_COMPNET_MODEL_ROOT']=str(model.resolve());cv2.setNumThreads(1)
    if capacity:install_windows_capacity()
    install_retained_evidence_pilot();start=time.perf_counter();engine=PKLNetROI(threads=3);engine._ensure_loaded()
    engine._session.run(['keypoints','heatmap_keypoints','fc_keypoints'],{'image':np.zeros((1,3,400,300),np.float32)})
    debug_ui.common.RUNTIME=runtime;camera=ExifReplay(False,engine);app=debug_ui.App(camera,demo_matcher=MATCHER)
    app.demo_algorithm._retain_fastcc_evidence_pilot=True
    if app.demo.gallery.acceptance_policy is not None:raise ValueError('Frozen public evaluation must not enable rejection policy')
    return app,camera,engine,(time.perf_counter()-start)*1000


def make_protocol(root,model):
    inventory=json.loads((root/'zip-inventory.json').read_text());entries=inventory['inventory']
    assert len(entries)==3677 and inventory['subjects']==92
    samples=[]
    for item in entries:
        person,condition,index=label(item['name'])
        samples.append(dict(member=item['name'],subject=person,condition=condition,index=index,
            enrollment=condition=='F'and index<5,identity='smpd:'+person+':right'))
    assert sum(s['enrollment']for s in samples)==460
    protocol=dict(scope='Full actual public release, not nominal original 110-person collection',images=3677,people=92,palms=92,
        enrollment_images=460,query_images=3217,missing_nominal_members=3,missing_nominal_people=18,
        split='Fixed F0..F4 per person; every remaining published file queried; no replacement or subset',
        decoding='PIL decode + uniform metadata-driven EXIF transpose, then RGB; no score-guided rotations or resizing',
        matcher=MATCHER,retained_evidence=True,rejection_policy=False,
        thresholds=dict(early_distance=.32,early_margin=.08,final_distance=1.,final_margin=0.),
        source_hash_mode='CRLF-normalized source; exact binary model SHA256',source_sha256={n:source_sha(APP/n)for n in SOURCES},
        evaluator_sha256=source_sha(__file__),inventory_sha256=sha(root/'zip-inventory.json'),samples=samples,
        model_sha256=dict(compnet=sha(model/'compnet-tongji.onnx'),pklnet=sha(PKLNetROI().root/'pklnet-keypoints-diagnostics.onnx')),
        environment=dict(python=sys.version,platform=platform.platform(),opencv=cv2.__version__,numpy=np.__version__,
            registration='Unchanged original OpenCV BF reference; ARM64 NEON acceleration cannot load on Windows. Not a Pi numeric/latency claim.'),
        score_scope='Actual staged algorithm, all successful identities in one gallery; no cropped-component substitution or person partition',
        timing_scope='Windows original read/hash/decode/EXIF/ROI/features/staged matching and local HTTP. No camera/external upload; gallery ready/startup separate.',
        pretraining_limit='Frozen Tongji CompNet checkpoint; PKLNet original training exposure not fully established; no target-data fitting')
    assert protocol['model_sha256']['compnet']=='b513e614a8b1a4448ef58c1b7f288f760fc991ce31d0a35079b4f9226146d1ea'
    assert protocol['model_sha256']['pklnet']=='bf477f1778f03ccc203b64dd0c84d418c9bb22839a23ba923f479ab991aa067f'
    return protocol


def verify(protocol):
    assert source_sha(__file__)==protocol['evaluator_sha256']
    for name,h in protocol['source_sha256'].items():assert source_sha(APP/name)==h,('Frozen source changed',name)


def prepare(a):
    root=a.root;out=root/'prepared';out.mkdir(exist_ok=False);(root/'inputs').mkdir(exist_ok=True);(out/'features').mkdir();(out/'rois').mkdir()
    protocol=make_protocol(root,a.model);save(root/'protocol.json',protocol);verify(protocol)
    app,camera,engine,startup=initialize(out/'capture_runtime',a.model)
    inventory=json.loads((root/'zip-inventory.json').read_text());parts=DownloadParts(root/'SMPD.parts',inventory['archive_bytes'])
    records=[];start=time.perf_counter();counts=collections.Counter();byte_hashes=collections.defaultdict(list)
    try:
      with(out/'records.jsonl').open('x',encoding='utf-8')as log:
       for entry in sorted(inventory['inventory'],key=lambda e:e['offset']):
        person,condition,index=label(entry['name']);sample=f'smpd-{person}-{condition}-{index:02d}';data=parts.member(entry)
        path=root/'inputs'/(hashlib.sha256(entry['name'].encode()).hexdigest()[:24]+'.jpg');assert not path.exists();path.write_bytes(data)
        row=dict(sample=sample,identity=f'smpd:{person}:right',subject=person,hand='right',condition=condition,index=index,member=entry['name'],
            original=str(path.resolve()),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),enrollment=condition=='F'and index<5)
        byte_hashes[row['sha256']].append(sample);tick=time.perf_counter()
        try:
            with Image.open(io.BytesIO(data))as encoded:
                row['encoded_size']=list(encoded.size);row['exif_orientation']=encoded.getexif().get(274);full=ImageOps.exif_transpose(encoded).convert('RGB')
            row['decoded_size']=list(full.size);raw,quad,details=engine.extract(full);row['roi_diagnostics']=details;row['roi_quad']=quad.tolist()
            row['roi_valid']=bool(details['roi_geometry_valid'])
            if row['roi_valid']:
                roi=normalize_roi_pixels(raw);Image.fromarray(roi).save(out/'rois'/(sample+'.png'))
            else:row['roi_error']=details['roi_geometry_reason']
        except (ValueError,RuntimeError,OSError)as error:row.update(roi_valid=False,roi_error=type(error).__name__+': '+str(error))
        row['read_decode_roi_ms']=(time.perf_counter()-tick)*1000
        if row['enrollment']:
            tick=time.perf_counter();camera.select([row])
            try:
                feature,image,source=app.capture_demo_feature(enrollment=True)
                actual=np.asarray(Image.open(io.BytesIO(base64.b64decode(image))))
                assert row['roi_valid']and np.array_equal(actual,roi),'ROI audit/capture mismatch'
                target=out/'features'/(sample+'.npz');np.savez_compressed(target,feature=feature)
                row.update(enrollment_feature_ok=True,enrollment_feature=str(target.resolve()),enrollment_feature_sha256=sha(target))
            except (ValueError,RuntimeError)as error:row.update(enrollment_feature_ok=False,enrollment_error=type(error).__name__+': '+str(error))
            row['enrollment_capture_ms']=(time.perf_counter()-tick)*1000
        records.append(row);counts['images']+=1;counts['roi_valid'if row['roi_valid']else'roi_failed']+=1
        if row['enrollment']:counts['enrollment_feature_ok'if row['enrollment_feature_ok']else'enrollment_feature_failed']+=1
        log.write(json.dumps(row,default=scalar)+'\n');log.flush()
        if len(records)%10==0 or len(records)==len(inventory['inventory']):
            save(out/'progress.json',dict(complete=False,counts=dict(counts),elapsed_s=time.perf_counter()-start,startup_ms=startup,last_sample=sample))
            print('prepare',len(records),dict(counts),round(time.perf_counter()-start),flush=True)
       assert len(records)==protocol['images'];verify(protocol)
       duplicates=[samples for samples in byte_hashes.values()if len(samples)>1]
       save(out/'manifest.json',records);save(out/'duplicates.json',dict(unique_files=len(byte_hashes),groups=duplicates))
       save(out/'progress.json',dict(complete=True,counts=dict(counts),elapsed_s=time.perf_counter()-start,startup_ms=startup,manifest_sha256=sha(out/'manifest.json')))
    finally:app.demo_algorithm.close()


def run(a):
    from http.client import HTTPConnection
    from http.server import ThreadingHTTPServer
    import threading
    from replay_demo_manifest import correct_identification
    root=a.root;protocol=json.loads((root/'protocol.json').read_text());verify(protocol)
    prepared=json.loads((root/'prepared/progress.json').read_text());assert prepared['complete']
    download=json.loads((root/'SMPD.download.json').read_text());assert download['complete']and download['zip_crc_checked']
    rows=json.loads((root/'prepared/manifest.json').read_text());out=root/'evaluation';out.mkdir(exist_ok=False);runtime=out/'runtime'
    store=TemplateStore(runtime/'demo_templates',compression_level=1);payments=PaymentService(runtime/'demo_payment.sqlite3')
    enrollments=[]
    for identity in sorted({r['identity']for r in rows}):
        selected=sorted((r for r in rows if r['identity']==identity and r['enrollment']),key=lambda r:r['index']);assert len(selected)==5
        ok=all(r.get('enrollment_feature_ok')for r in selected);user=identity.replace(':','-')
        item=dict(identity=identity,samples=[r['sample']for r in selected],registered=ok);enrollments.append(item)
        if ok:
            features=[]
            for row in selected:
                assert sha(row['enrollment_feature'])==row['enrollment_feature_sha256']
                with np.load(row['enrollment_feature'],allow_pickle=False)as z:features.append(z['feature'].copy())
            store.save(user,np.stack(features),dict(user=user,display_name='EVAL '+identity,algorithm=MATCHER,capture_profile='noir-ir',samples=5,
                source='Published SMPD original images, uniform EXIF decoding',roi_geometry=ROI_GEOMETRY_VERSION,roi_sources=['pklnet']*5))
            payments.create_account(user,'EVAL '+identity,10000)
    save(out/'enrollments.json',enrollments);registered=set(store.list_users())
    app,camera,engine,startup=initialize(runtime,a.model,capacity=True)
    if len(app.demo.gallery._prepared_cache)!=len(registered):raise RuntimeError('WINDOWS_PREPARED_CACHE_CAPACITY; no gallery subsets allowed')
    report=dict(complete=False,protocol_sha256=sha(root/'protocol.json'),archive_sha256=download['sha256'],enrollments=enrollments,
        actual_gallery_identities=len(registered),startup_and_gallery_ready_ms=startup,queries=[],warnings=[],resources=dict(index_limit=2*1024**3,prepared_cache_limit=6*1024**3),
        scope=protocol['timing_scope'],host_environment=protocol['environment'])
    numeric={};old=app.demo_algorithm.score_gallery
    def scoring(probe,groups):value=old(probe,groups);numeric.update(value);return value
    app.demo_algorithm.score_gallery=scoring
    handler=debug_ui.make_handler(app)
    class QuietHandler(handler):
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),QuietHandler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    def request(route,payload):
        start=time.perf_counter();connection=HTTPConnection(*server.server_address,timeout=1800)
        connection.request('POST',route,json.dumps(payload),{'Content-Type':'application/json'});response=connection.getresponse();data=json.loads(response.read());status=response.status;connection.close()
        return status,data,(time.perf_counter()-start)*1000
    before=app.demo.payments.transaction_count();query_rois=out/'query-rois';query_rois.mkdir()
    try:
      with(out/'queries.jsonl').open('x',encoding='utf-8')as log:
       for row in sorted((r for r in rows if not r['enrollment']),key=lambda r:(r['subject'],r['index'])):
        if psutil.virtual_memory().available<1024**3:raise MemoryError('Less than 1GiB available; stopping rather than changing gallery')
        camera.select([row]);numeric.clear();status,response,elapsed=request('/api/demo/identify',{})
        if 'INPUT_INTEGRITY_FAILURE'in str(response):raise RuntimeError('Original-image integrity failed')
        trial=dict(sample=row['sample'],identity=row['identity'],condition=row['condition'],http_status=status,ms=elapsed,
            truth_enrolled=row['identity'].replace(':','-')in registered,roi_audit_valid=row['roi_valid'],
            result={k:v for k,v in response.items()if k not in('roi_image','token','expires_at')},scores=dict(numeric),
            duplicates_enrollment=any(r['enrollment']and r['sha256']==row['sha256']for r in rows))
        trial['correct']=correct_identification(trial)
        if response.get('roi_image'):(query_rois/(row['sample']+'.png')).write_bytes(base64.b64decode(response['roi_image']))
        if response.get('token'):
            code,_,_=request('/api/demo/cancel',dict(token=response['token']));assert code==200
        log.write(json.dumps(trial,default=scalar)+'\n');log.flush();report['queries'].append(trial)
        values=report['queries'];report['summary']=dict(total=len(values),correct=sum(q['correct']for q in values),
            wrong_match=sum(not q['correct']and q['result'].get('status')=='MATCH'for q in values),
            rejected=sum(q['http_status']==200 and q['result'].get('status')!='MATCH'for q in values),
            processing_failures=sum(q['http_status']!=200 for q in values),correct_within_2500=sum(q['correct']and q['ms']<=2500 for q in values),
            p50_ms=float(np.median([q['ms']for q in values])),p95_ms=float(np.percentile([q['ms']for q in values],95)),max_ms=max(q['ms']for q in values))
        save(out/'results.json',report);print('query',len(values),row['sample'],trial['correct'],response.get('status',response.get('message')),round(elapsed),flush=True)
       assert len(report['queries'])==protocol['query_images'];assert app.demo.payments.transaction_count()==before;verify(protocol)
       report.update(complete=True,transactions_unchanged=True,originals_unchanged=all(sha(r['original'])==r['sha256']for r in rows))
       save(out/'results.json',report)
    finally:server.shutdown();server.server_close();thread.join();app.demo_algorithm.close()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=('prepare','run'));p.add_argument('root',type=Path);p.add_argument('--model',required=True,type=Path);a=p.parse_args()
    globals()[a.mode](a)


if __name__=='__main__':main()
