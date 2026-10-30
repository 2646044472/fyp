import io
import json
from pathlib import Path
from types import SimpleNamespace
import zipfile

import cv2
import numpy as np
import pytest

import union_lossless_codec as codec
import lossless_template_store as storage
from registered_matcher import FastCCRegisteredMatcher,FastCCDualRegisteredMatcher
from union_matcher import FastCCWindowUnionMatcher
from templates import TemplateStore
from gallery import Gallery


def blocks(queries=2,points=4,seed=8):
    rng=np.random.default_rng(seed)
    legacy=FastCCRegisteredMatcher._pack(np.zeros((9,32,32),np.int8),size=(80,64))
    legacy=FastCCDualRegisteredMatcher._append_view(legacy)
    ok,png=cv2.imencode('.png',rng.integers(0,256,(64,80),np.uint8));assert ok
    positions=rng.uniform(0,383,(points,2)).astype(np.float32)
    descriptors=np.sqrt(rng.dirichlet(np.ones(128),points)).astype(np.float32)
    view=lambda sigma:FastCCWindowUnionMatcher._encode_view(sigma,np.eye(3),positions,descriptors)
    return legacy,png.ravel(),[view((0,2)[i%2]) for i in range(queries)],[view(4),view(8)]


def old_matcher():
    old=FastCCWindowUnionMatcher.__new__(FastCCWindowUnionMatcher)
    old.magic=codec.SEMANTIC_MAGIC;old.allow_gallery_only=True
    old.legacy=SimpleNamespace(_views=FastCCDualRegisteredMatcher._views)
    return old


def metadata():
    return dict(algorithm='FastCCCompNetAlternateROI-v27-lossless-experimental',capture_profile='noir-ir',samples=5)


def assert_tensors_equal(a,b):
    if isinstance(a,np.ndarray):
        assert isinstance(b,np.ndarray) and a.dtype==b.dtype and a.shape==b.shape and a.tobytes()==b.tobytes()
    elif isinstance(a,(tuple,list)):
        assert len(a)==len(b)
        for x,y in zip(a,b):assert_tensors_equal(x,y)
    else:assert a==b


def rewrite(path,change):
    with zipfile.ZipFile(path) as archive:entries=[(i.filename,archive.read(i)) for i in archive.infolist()]
    entries=change(entries)
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED) as archive:
        for name,value in entries:archive.writestr(name,value)


def test_all_decoded_tensors_native_png_and_view_order_are_byte_equal():
    parts=blocks(queries=7);old=old_matcher();before=old._pack(*parts)
    after=codec.pack(*parts)
    assert_tensors_equal(old._unpack(before),codec.decode(after).parts)
    a,b=codec.decode(before),codec.decode(after)
    assert a.logical_sha256()==b.logical_sha256() and a.png.tobytes()==b.png.tobytes()
    assert_tensors_equal(codec.decode(codec.convert_legacy(before)).parts,a.parts)
    with pytest.raises(ValueError):old._unpack(after)


def test_full_42_query_views_and_2_gallery_views_exceed_16mib_without_loss(tmp_path):
    parts=blocks(queries=42,points=1000)
    with pytest.raises(ValueError,match='capacity'):old_matcher()._pack(*parts)
    payload=codec.pack(*parts);restored=codec.decode(payload)
    assert payload.nbytes>16*1024*1024 and len(restored.parts[-1])==42 and len(restored.parts[-2])==2
    for original,chunk in zip((*parts[3],*parts[2]),(*restored.gallery_chunks,*restored.query_chunks)):
        assert original.tobytes()==chunk.tobytes()
    frames=[codec.pack(*blocks(queries=i,points=3)) for i in (1,2,3,4)]+[payload]
    store=storage.LosslessTemplateStore(tmp_path);store.save('person',frames,metadata())
    loaded,meta=store.load('person')
    assert len(set(f.size for f in loaded))==5 and meta['template_codec']==codec.CODEC
    for original,frame in zip(frames,loaded):assert_tensors_equal(frame,original)
    assert not list(tmp_path.glob('*.tmp'))


@pytest.mark.parametrize('field,value',[(1,3),(2,7),(3,2**63),(4,2**63),(5,43),(6,1),(7,1),(8,0)])
def test_header_corruption_is_rejected_without_silent_view_loss(field,value):
    payload=codec.pack(*blocks());values=list(codec.HEADER.unpack_from(payload));values[field]=value
    payload[:codec.HEADER.size]=np.frombuffer(codec.HEADER.pack(*values),np.uint8)
    with pytest.raises(ValueError):codec.decode(payload)


def test_native_pixel_budget_applies_before_decoder(monkeypatch):
    parts=list(blocks());legacy=parts[0].copy()
    legacy[:16].view('<i4')[2:]=[codec.MAX_NATIVE_SIDE+1,64]
    parts[0]=legacy
    monkeypatch.setattr(cv2,'imdecode',lambda *a:pytest.fail('Budget must be checked before decode'))
    with pytest.raises(ValueError,match='resource limit'):codec.pack(*parts)


def test_legacy_reader_is_bounded_and_new_store_is_not_readable_by_old_store(tmp_path):
    old=old_matcher()._pack(*blocks());TemplateStore(tmp_path).save('old',np.stack([old]*5),{'algorithm':'FastCCCompNetAlternateROI-v26-experimental'})
    new=storage.LosslessTemplateStore(tmp_path);frames,meta=new.load('old')
    assert len(frames)==5 and all(codec.decode(f).storage_codec=='union-fixed-v26' for f in frames)
    assert_tensors_equal(frames[0],old)
    with pytest.raises(ValueError,match='isolated root'):new.save('old',[codec.convert_legacy(old)]*5,metadata())
    new.save('new',[codec.pack(*blocks())]*5,metadata())
    with pytest.raises(FileNotFoundError):TemplateStore(tmp_path).load('new')
    assert TemplateStore(tmp_path).list_users()==['old'] and new.list_users()==['new','old']


@pytest.mark.parametrize('kind',['duplicate','path','missing','checksum','shape','object','trailing','manifest_duplicate','frame_count'])
def test_corrupt_or_unsafe_archive_is_rejected(tmp_path,kind):
    store=storage.LosslessTemplateStore(tmp_path);store.save('person',[codec.pack(*blocks())]*5,metadata());path=store.paths('person')[0]
    def alter(entries):
        if kind=='duplicate':return entries+[entries[-1]]
        if kind=='path':return entries+[('../outside.npy',b'anything')]
        if kind=='missing':return entries[:-1]
        if kind=='manifest_duplicate':return [(n,v.replace(b'"schema":',b'"schema":"wrong","schema":',1) if n=='manifest.json' else v) for n,v in entries]
        if kind=='frame_count':
            result=[]
            for name,value in entries:
                if name=='manifest.json':
                    m=json.loads(value);m['frames']=m['frames'][:-1];value=json.dumps(m).encode()
                result.append((name,value))
            return result
        result=[]
        for name,value in entries:
            if name=='frame_000.npy':
                if kind=='checksum':value=value[:-1]+bytes([value[-1]^1])
                elif kind=='trailing':value+=b'X'
                else:
                    stream=io.BytesIO()
                    if kind=='shape':np.lib.format.write_array_header_1_0(stream,dict(descr='|u1',fortran_order=False,shape=(2**50,)))
                    else:np.lib.format.write_array_header_1_0(stream,dict(descr='|O',fortran_order=False,shape=(1,)))
                    value=stream.getvalue()
            result.append((name,value))
        return result
    with __import__('warnings').catch_warnings():
        __import__('warnings').simplefilter('ignore',UserWarning);rewrite(path,alter)
    with pytest.raises((ValueError,zipfile.BadZipFile)):store.load('person')


def test_declared_zip_expansion_limit_is_checked_before_member_open():
    class Archive:
        def infolist(self):
            info=zipfile.ZipInfo('features.npy');info.file_size=storage.MAX_ARCHIVE_EXPANDED_BYTES+1
            return [info]
    with pytest.raises(ValueError,match='expanded-size'):storage._members(Archive(),['features.npy'])


def test_atomic_replace_failure_leaves_old_generation_and_metadata_usable(tmp_path,monkeypatch):
    store=storage.LosslessTemplateStore(tmp_path);frames=[codec.pack(*blocks())]*5;store.save('person',frames,metadata())
    path=store.paths('person')[0];before=path.read_bytes()
    def fail(*a):raise OSError('Injected pre-commit failure')
    with monkeypatch.context() as patch:
        patch.setattr(storage.os,'replace',fail)
        with pytest.raises(OSError):store.save('person',[codec.pack(*blocks(queries=3))]*5,dict(metadata(),revision=2))
    assert path.read_bytes()==before and store.load('person')[1].get('revision') is None
    assert not list(tmp_path.glob('*.tmp'))


def test_bad_fifth_frame_preserves_existing_identity_and_account(tmp_path):
    from demo_flow import DemoFlow
    from lossless_union_matcher import LosslessUnionMatcher
    algorithm=SimpleNamespace(name=LosslessUnionMatcher.name,template_codec=codec.CODEC,
        template_storage_schema=storage.SCHEMA,template_store_factory=storage.LosslessTemplateStore)
    frames=[codec.pack(*blocks(queries=i)) for i in (1,2,3,4,5)]
    queue=list(frames)
    flow=DemoFlow(tmp_path,algorithm,lambda:(queue.pop(0),'','pklnet'),roi_geometry='fixed-test')
    flow.enroll('person','Person');before=flow.store.paths('person')[0].read_bytes()
    # Force a metadata refresh while keeping the existing committed account.
    flow.gallery.required_metadata['roi_geometry']='next-test'
    queue[:]=frames[:4]+[np.zeros(20,np.uint8)]
    with pytest.raises(ValueError):flow.enroll('person','Person')
    assert flow.store.paths('person')[0].read_bytes()==before and flow.payments.balance_for('person')==10000
    assert flow.payments.transaction_count()==0


def test_cache_key_includes_codec_and_invalidates_on_atomic_new_generation(tmp_path):
    store=storage.LosslessTemplateStore(tmp_path);frames=[codec.pack(*blocks())]*5;store.save('person',frames,metadata())
    gallery=Gallery(store,SimpleNamespace(),required_metadata={'template_codec':codec.CODEC})
    a=gallery._signature('person');assert a[0]==(storage.SCHEMA,codec.CODEC)
    store.save('person',[codec.pack(*blocks(queries=3))]*5,metadata())
    assert gallery._signature('person')!=a


def test_store_rejects_incompatible_metadata_before_overwrite(tmp_path):
    store=storage.LosslessTemplateStore(tmp_path);frames=[codec.pack(*blocks())]*5;store.save('person',frames,metadata());before=store.paths('person')[0].read_bytes()
    for changed in (dict(user='other'),dict(template_codec='wrong'),dict(samples=4)):
        with pytest.raises(ValueError):store.save('person',frames,dict(metadata(),**changed))
        assert store.paths('person')[0].read_bytes()==before


def test_real_http_enrollment_load_cancel_confirm_and_duplicate_guard(tmp_path):
    from http.client import HTTPConnection
    from http.server import ThreadingHTTPServer
    import threading
    from demo_flow import DemoFlow
    from palm_app.debug_ui import make_handler
    class Algorithm:
        name=metadata()['algorithm'];template_codec=codec.CODEC;template_storage_schema=storage.SCHEMA
        template_store_factory=storage.LosslessTemplateStore
        def prepare_probe(self,feature):return codec.decode(feature).parts
        def prepare_enrollment(self,features):return [codec.decode(f).parts for f in features]
        def prepared_bytes(self,features):return 1
        def score_prepared(self,probe,features):return 0.
    frames=[codec.pack(*blocks(queries=i)) for i in (1,2,3,4,5)]
    queue=list(frames)
    flow=DemoFlow(tmp_path,Algorithm(),lambda:(queue.pop(0),'','pklnet'),roi_geometry='fixed-test')
    parent=make_handler(SimpleNamespace(capture_only=False,demo=flow))
    class Quiet(parent):
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),Quiet)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    def request(route,payload):
        connection=HTTPConnection(*server.server_address)
        try:
            connection.request('POST',route,json.dumps(payload),{'Content-Type':'application/json'})
            response=connection.getresponse();return response.status,json.loads(response.read())
        finally:connection.close()
    try:
        code,value=request('/api/demo/enroll',dict(user_id='person',display_name='Person'));assert code==200
        loaded,meta=flow.store.load('person');assert [f.size for f in loaded]==[f.size for f in frames]
        assert not flow.users()[0]['needs_reenrollment']
        queue[:]=frames[:1]
        code,value=request('/api/demo/identify',{});assert code==200 and value['user_id']=='person'
        token=value['token'];assert request('/api/demo/cancel',dict(token=token))[0]==200
        assert request('/api/demo/confirm',dict(token=token,user_id='person'))[0]==400
        queue[:]=frames[:1]
        code,value=request('/api/demo/identify',{});assert code==200
        token=value['token'];assert request('/api/demo/confirm',dict(token=token,user_id='person'))[0]==200
        assert request('/api/demo/confirm',dict(token=token,user_id='person'))[0]==400
        assert flow.payments.transaction_count()==1 and flow.payments.balance_for('person')==8000
    finally:server.shutdown();server.server_close();thread.join()


def test_oversized_central_directory_is_rejected_before_zipfile_allocation(tmp_path,monkeypatch):
    import struct
    store=storage.LosslessTemplateStore(tmp_path);store.save('person',[codec.pack(*blocks())]*5,metadata())
    path=store.paths('person')[0];value=bytearray(path.read_bytes());fields=list(struct.unpack('<4sHHHHIIH',value[-22:]));fields[5]=16385
    value[-22:]=struct.pack('<4sHHHHIIH',*fields);path.write_bytes(value)
    monkeypatch.setattr(zipfile,'ZipFile',lambda *a,**k:pytest.fail('Central directory must be bounded first'))
    with pytest.raises(ValueError,match='central-directory'):store.load('person')


def test_huge_npy_header_is_rejected_before_array_allocation(monkeypatch):
    import struct
    archive=SimpleNamespace(open=lambda info:io.BytesIO(b'\x93NUMPY\x02\x00'+struct.pack('<I',2**32-1)))
    info=SimpleNamespace(file_size=128)
    monkeypatch.setattr(np,'empty',lambda *a,**k:pytest.fail('Header must be bounded before allocation'))
    with pytest.raises(ValueError,match='header resource limit'):storage._read_npy(archive,info,(4,))


def test_wrong_algorithm_metadata_is_rejected_before_matcher_preparation(tmp_path):
    store=storage.LosslessTemplateStore(tmp_path);store.save('person',[codec.pack(*blocks())]*5,dict(metadata(),algorithm='unrelated'))
    algorithm=SimpleNamespace(match=lambda *a:pytest.fail('Wrong algorithm must never score'))
    gallery=Gallery(store,algorithm,required_metadata={'algorithm':metadata()['algorithm'],'template_codec':codec.CODEC})
    result=gallery.identify(np.zeros(1),'noir-ir')
    assert result.status=='UNKNOWN' and result.reason=='INCOMPATIBLE_TEMPLATES'


def test_archive_preflight_and_decode_pin_the_same_open_generation(tmp_path,monkeypatch):
    store=storage.LosslessTemplateStore(tmp_path);store.save('person',[codec.pack(*blocks())]*5,metadata())
    preflight=storage._preflight_zip;constructor=zipfile.ZipFile;seen=[]
    def checked(source,count):
        assert hasattr(source,'fileno');seen.append(source);return preflight(source,count)
    def opened(source,*a,**k):
        assert source is seen[-1];return constructor(source,*a,**k)
    monkeypatch.setattr(storage,'_preflight_zip',checked);monkeypatch.setattr(zipfile,'ZipFile',opened)
    loaded,_=store.load('person');assert len(loaded)==5 and len(seen)==1
