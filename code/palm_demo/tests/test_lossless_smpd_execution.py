"""Operational protocol tests only; no public recognition or threshold fitting."""
import importlib
import inspect
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest


@pytest.fixture
def module(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]/'tools'))
    return importlib.import_module('run_lossless_smpd')


def test_prepare_adapter_changes_only_version_and_decoder_observation(module):
    before=inspect.getsource(module.previous.prepare_app)
    after=module.preparer_source()
    restored=after.replace('app.demo_algorithm.magic == 2801166','app.demo_algorithm.magic == 2801066')
    restored=restored.replace("        camera.audit['decoded_rgb_sha256'] = hashlib.sha256(full.tobytes()).hexdigest()\n",'')
    assert restored==before
    compile(after,'<tested-v27-preparer>','exec')


def test_no_historical_array_is_loaded_to_decide_whole_batch_reuse(module,tmp_path,monkeypatch):
    (tmp_path/'records/enrollment').mkdir(parents=True)
    (tmp_path/'protocol.json').write_text('{}')
    for index in range(460):
        payload=dict(ok=index<417,source_sha256='raw',capture={'decoded_size':[100,100]})
        (tmp_path/'records/enrollment'/f'{index:05d}.json').write_text(json.dumps({'payload':payload}))
    monkeypatch.setattr(np,'load',lambda *a,**k:pytest.fail('Never load features for an uncertified reuse audit'))
    value=module.reuse_audit(tmp_path)
    assert value['successful']==417 and value['failed']==43
    assert value['decoded_rgb_hash_present']==0 and value['historical_feature_arrays_loaded']==0 and not value['feature_reuse']


def test_lock_hot_guard_detects_changes_before_next_record(module,tmp_path,monkeypatch):
    file=tmp_path/'locked.py';file.write_text('one')
    p=dict(run_fingerprint='test',source_sha256={str(file):'hash'},models_sha256={},metadata_sha256={},environment={'relevant_environment':{}})
    monkeypatch.setattr(module,'digest',lambda value:'test')
    monkeypatch.setattr(module.previous,'verify',lambda *a,**k:None)
    module._verified.clear();module.verify(p,dependencies=True)
    file.write_text('changed source')
    with pytest.raises(ValueError,match='file identity changed'):module.verify(p)
    module._verified.clear()


def test_new_feature_loader_requires_fresh_variable_bytes_and_rgb_digest(module,tmp_path):
    import test_union_lossless_capacity as fixture
    from union_lossless_codec import pack
    from smpd_run_journal import file_sha
    root=tmp_path/'new';folder=root/'features';folder.mkdir(parents=True)
    frame=pack(*fixture.blocks());path=folder/'fresh.npz';np.savez_compressed(path,feature=frame)
    payload=dict(ok=True,source_sha256='S',feature=str(path),feature_sha256=file_sha(path),
                 capture=dict(feature_bytes=frame.size,decoded_rgb_sha256='D'))
    row={'sha256':'S'};record={'payload':payload}
    assert np.array_equal(module.validate_feature(root,{},row,record),frame)
    payload['capture'].pop('decoded_rgb_sha256')
    with pytest.raises(ValueError,match='RGB'):module.validate_feature(root,{},row,record)
    payload['capture']['decoded_rgb_sha256']='D';payload['feature']=str(tmp_path/'old.npz')
    with pytest.raises(ValueError,match='outside'):module.validate_feature(root,{},row,record)


def test_v27_gallery_seal_has_all_fixed_successes_without_stacking(module,tmp_path):
    import test_union_lossless_capacity as fixture
    from union_lossless_codec import pack
    from smpd_run_journal import file_sha
    root=tmp_path/'new';folder=root/'features';folder.mkdir(parents=True)
    rows=[];records=[]
    for person in ('001','002'):
        for index in range(5):
            sample=f'{person}-{index}';row=dict(sample=sample,identity='smpd:'+person+':right',enrollment=True,subject=person,index=index,sha256='S')
            frame=pack(*fixture.blocks(queries=index+1));path=folder/(sample+'.npz');np.savez_compressed(path,feature=frame)
            payload=dict(ok=not(person=='002' and index==4),source_sha256='S',feature=str(path),feature_sha256=file_sha(path),
                capture=dict(decoded_rgb_sha256='D',feature_bytes=frame.size))
            rows.append(row);records.append(dict(sample=sample,payload=payload,record_sha256=sample))
    p=dict(rows=rows,run_fingerprint='new-v27');journal=SimpleNamespace(records=records)
    first=module.build_gallery(root,p,journal)
    assert first['registered']==1 and len(first['enrollments'])==2
    assert module.build_gallery(root,p,journal)==first
    entry=next(e for e in first['enrollments'] if e['registered'])
    from lossless_template_store import LosslessTemplateStore
    frames,_=LosslessTemplateStore(root/'evaluation/runtime/demo_templates').load(entry['user'])
    assert len(frames)==5 and len({f.size for f in frames})==5


def test_supervisor_uses_new_runner_and_report_without_changing_retry_policy(module):
    supervisor=importlib.import_module('supervise_lossless_smpd');namespace=supervisor.functions()
    assert namespace['run'] is module
    assert namespace['report'].__module__=='report_lossless_smpd'
    assert 'report_lossless_smpd' in namespace['validate_preflight'].__code__.co_consts
    assert namespace['watch'].__code__ is supervisor.previous.watch.__code__
