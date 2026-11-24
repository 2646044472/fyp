from types import SimpleNamespace
import numpy as np
from demo_flow import DemoFlow
from lossless_template_store import LosslessTemplateStore, SCHEMA
from union_lossless_codec import CODEC, pack
from test_union_lossless_capacity import blocks


def fake_algorithm():
    return SimpleNamespace(name='test-lossless', template_codec=CODEC, template_storage_schema=SCHEMA,
        template_store_factory=LosslessTemplateStore,
        prepare_probe=lambda x:x, prepare_enrollment=lambda x:x,
        prepared_bytes=lambda frames:sum(x.nbytes for x in frames), score_prepared=lambda probe, frames:0.1)


def test_variable_frames_keep_strict_integrity_and_fail_closed(tmp_path):
    frames=[pack(*blocks(queries=i,points=4)) for i in (1,2,3,4,5)]
    queue=list(frames)
    flow=DemoFlow(tmp_path,fake_algorithm(),lambda:(queue.pop(0),'','pklnet'),roi_geometry='fixed')
    flow.enroll('person','Person')
    assert flow._gallery_integrity_reason() is None
    assert flow.store.list_template_ids()==['person']
    assert flow.gallery._signature('person')[0]==(SCHEMA,CODEC)
    with flow.store.paths('person')[0].open('r+b') as f: f.truncate(30)
    assert flow._gallery_integrity_reason()=='GALLERY_INVALID_TEMPLATES'


def test_lossless_metadata_listing_does_not_expand_biometric_frames(tmp_path,monkeypatch):
    store=LosslessTemplateStore(tmp_path)
    store.save('person',[pack(*blocks(queries=i,points=3)) for i in (1,2,3,4,5)],
        {'user':'person','samples':5,'template_codec':CODEC,'template_storage_schema':SCHEMA})
    monkeypatch.setattr('lossless_template_store._read_npy',
        lambda *args,**kwargs: (_ for _ in ()).throw(AssertionError('metadata read expanded a frame')))
    metadata=store.read_metadata('person')
    assert metadata['user']=='person'


def test_incomplete_legacy_file_is_detected_and_not_skipped(tmp_path):
    flow=DemoFlow(tmp_path,fake_algorithm(),lambda:(None,'','pklnet'),roi_geometry='fixed')
    flow.store.root.mkdir(parents=True)
    (flow.store.root/'orphan.npz').write_bytes(b'incomplete')
    assert flow.store.list_template_ids()==['orphan']
    assert flow._gallery_integrity_reason()=='GALLERY_INCOMPLETE_TEMPLATES'


def test_retained_candidate_is_explicit_and_uses_compatible_logical_payload():
    from lossless_retained_matcher import LosslessRetainedMatcher
    from union_lossless_codec import decode
    from test_union_lossless_capacity import old_matcher
    parts=blocks(queries=3,points=4)
    candidate=object.__new__(LosslessRetainedMatcher)
    actual=candidate._pack(*parts)
    legacy=old_matcher()._pack(*parts)
    assert candidate.name=='FastCCRetainedLossless-experimental'
    assert decode(actual).logical_sha256()==decode(legacy).logical_sha256()
    assert candidate._unpack(actual)[0].tobytes()==decode(legacy).parts[0].tobytes()
