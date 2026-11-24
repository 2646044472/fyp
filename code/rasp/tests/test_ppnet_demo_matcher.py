import numpy as np
import pytest
import hashlib
import json
import zipfile
from PIL import Image

from biometric import score_probe
from compnet_pilot import preprocess_compnet
from demo_flow import DemoFlow
from ppnet_demo_matcher import PPNetDemoMatcher, create_demo_runtime, open_demo_runtime


class FakeEncoder:
    def extract(self, image):
        assert isinstance(image, Image.Image)
        return np.arange(512, dtype=np.float32), np.ones(512, dtype=np.float32)


def runtime_identity(model='model-a'):
    return {
        'matcher': PPNetDemoMatcher.name,
        'source_sha256': 'source', 'checkpoint_sha256': 'checkpoint', 'onnx_sha256': model,
        'feature_contract': 'gray-bilinear-128-zero-mask-sample-std-1e-6-raw-512-v1',
        'score_contract': 'raw-512-five-template-min-l2-v1',
        'threshold': PPNetDemoMatcher.default_threshold,
        'min_margin': PPNetDemoMatcher.default_min_margin,
    }


def test_extract_and_nearest_raw_distance():
    matcher = PPNetDemoMatcher(None, encoder=FakeEncoder())
    image = np.zeros((128, 128), dtype=np.uint8)
    assert np.array_equal(matcher.extract(image), matcher.extract(Image.fromarray(image)))
    probe = np.zeros(512, dtype=np.float32)
    templates = np.stack([np.full(512, n, dtype=np.float32) for n in (4, 1, 3, 2, 5)])
    assert score_probe(matcher, probe, templates) == pytest.approx(np.sqrt(512))
    with pytest.raises(ValueError):
        matcher.score_enrollment(probe, templates[:4])
    with pytest.raises(ValueError):
        matcher.score_enrollment(np.full(512, np.nan), templates)


def test_numpy_roi_preprocessing_matches_frozen_torch_contract():
    import torch

    roi = np.arange(128 * 128, dtype=np.uint32).reshape(128, 128).astype(np.uint8)
    roi[::3, ::5] = 0
    actual = preprocess_compnet(Image.fromarray(roi))
    tensor = torch.from_numpy(roi.copy()).unsqueeze(0).contiguous().float().div_(255.0)
    flat = tensor.view(1, -1)
    mask = flat > 0
    values = flat[mask]
    flat[mask] = (values - values.mean()) / (values.std() + 1e-6)
    expected = flat.view(1, 1, 128, 128).numpy()
    assert np.allclose(actual, expected, atol=1e-6, rtol=1e-6)


def test_runtime_is_fresh_and_policy_is_rejected(tmp_path):
    matcher = PPNetDemoMatcher(None, encoder=FakeEncoder())
    old = tmp_path / 'demo_templates'
    old.mkdir()
    (old / 'keep').write_text('untouched')
    with pytest.raises(ValueError, match='isolated'):
        DemoFlow(tmp_path, matcher, lambda: None)
    isolated = create_demo_runtime(tmp_path, 'ppnet-demo-first')
    flow = DemoFlow(isolated, matcher, lambda: None)
    assert flow.store.root == isolated / 'demo_templates'
    assert flow.gallery.threshold == matcher.default_threshold
    assert flow.gallery.min_margin == matcher.default_min_margin
    assert (old / 'keep').read_text() == 'untouched'
    with pytest.raises(FileExistsError):
        create_demo_runtime(tmp_path, 'ppnet-demo-first')
    (isolated / 'demo_acceptance_policy.json').write_text('{}')
    with pytest.raises(ValueError, match='acceptance policies'):
        DemoFlow(isolated, matcher, lambda: None)
    (tmp_path / 'demo_acceptance_policy.json').write_text('{}')
    with pytest.raises(ValueError, match='acceptance policy'):
        create_demo_runtime(tmp_path, 'ppnet-demo-second')


def test_runtime_resume_preserves_matching_candidate_gallery_and_account(tmp_path):
    from payment import PaymentService
    from templates import TemplateStore

    identity = runtime_identity()
    runtime = create_demo_runtime(tmp_path, 'ppnet-demo-resume', runtime_identity=identity)
    store = TemplateStore(runtime / 'demo_templates')
    vectors = np.arange(5 * 512, dtype=np.float32).reshape(5, 512) / 1000
    store.save('smoke_left', vectors, {
        'algorithm': identity['matcher'], 'capture_profile': 'test', 'roi_geometry': 'pklnet-test',
        'matcher_runtime_identity': identity})
    payments = PaymentService(runtime / 'demo_payment.sqlite3')
    payments.create_account('smoke_left', 'Synthetic fixture', 12345)

    reopened = open_demo_runtime(tmp_path, 'ppnet-demo-resume', runtime_identity=identity)
    restored, metadata = TemplateStore(reopened / 'demo_templates').load('smoke_left')
    assert np.array_equal(restored, vectors)
    assert metadata['algorithm'] == identity['matcher']
    assert PaymentService(reopened / 'demo_payment.sqlite3').balance_for('smoke_left') == 12345
    with pytest.raises(FileExistsError):
        create_demo_runtime(tmp_path, 'ppnet-demo-resume', runtime_identity=identity)


def test_runtime_resume_rejects_wrong_model_legacy_marker_and_policy_without_mutation(tmp_path):
    import hashlib
    from ppnet_demo_matcher import open_demo_runtime

    identity = runtime_identity()
    runtime = create_demo_runtime(tmp_path, 'ppnet-demo-identity', runtime_identity=identity)
    before = hashlib.sha256((runtime / '.ppnet-demo-runtime').read_bytes()).hexdigest()
    with pytest.raises(ValueError, match='identity does not match'):
        open_demo_runtime(tmp_path, 'ppnet-demo-identity',
                          runtime_identity=runtime_identity('model-b'))
    assert hashlib.sha256((runtime / '.ppnet-demo-runtime').read_bytes()).hexdigest() == before

    legacy = create_demo_runtime(tmp_path, 'ppnet-demo-legacy')
    (legacy / '.ppnet-demo-runtime').write_text('PPNet isolated demo runtime\n')
    with pytest.raises(ValueError, match='legacy'):
        open_demo_runtime(tmp_path, 'ppnet-demo-legacy', runtime_identity=identity)

    (runtime / 'demo_acceptance_policy.json').write_text('{}')
    with pytest.raises(ValueError, match='acceptance policies'):
        open_demo_runtime(tmp_path, 'ppnet-demo-identity', runtime_identity=identity)


def test_runtime_resume_rejects_do_n_template_and_external_symlink(tmp_path):
    from templates import TemplateStore

    identity = runtime_identity()
    runtime = create_demo_runtime(tmp_path, 'ppnet-demo-do-not-open-don', runtime_identity=identity)
    TemplateStore(runtime / 'demo_templates').save(
        'old_left', np.zeros((5, 512), dtype=np.float32), {'algorithm': 'DoN'})
    with pytest.raises(ValueError, match='another matcher'):
        open_demo_runtime(tmp_path, 'ppnet-demo-do-not-open-don', runtime_identity=identity)

    wrong_model = create_demo_runtime(tmp_path, 'ppnet-demo-wrong-template-model', runtime_identity=identity)
    TemplateStore(wrong_model / 'demo_templates').save('other_left', np.zeros((5, 512), dtype=np.float32), {
        'algorithm': identity['matcher'], 'capture_profile': 'test', 'roi_geometry': 'pklnet-test',
        'matcher_runtime_identity': runtime_identity('model-b')})
    with pytest.raises(ValueError, match='another matcher'):
        open_demo_runtime(tmp_path, 'ppnet-demo-wrong-template-model', runtime_identity=identity)

    outside = tmp_path.parent / (tmp_path.name + '-outside')
    outside.mkdir()
    link = tmp_path / 'ppnet-demo-external'
    link.symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match='direct, non-symlink'):
        open_demo_runtime(tmp_path, 'ppnet-demo-external', runtime_identity=identity)


@pytest.mark.parametrize('link_name,target_is_dir', [
    ('demo_templates', True), ('demo_payment.sqlite3', False),
])
def test_runtime_resume_rejects_external_store_symlinks(tmp_path, link_name, target_is_dir):
    identity = runtime_identity()
    runtime = create_demo_runtime(tmp_path, 'ppnet-demo-store-link', runtime_identity=identity)
    outside = tmp_path.parent / (tmp_path.name + '-' + link_name.replace('.', '-'))
    if target_is_dir:
        outside.mkdir()
    else:
        outside.write_bytes(b'not a database')
    (runtime / link_name).symlink_to(outside, target_is_directory=target_is_dir)
    with pytest.raises(ValueError, match='symlink'):
        open_demo_runtime(tmp_path, 'ppnet-demo-store-link', runtime_identity=identity)


def test_runtime_resume_rejects_external_database_hardlink_without_mutation(tmp_path):
    import hashlib
    import os
    from payment import PaymentService

    identity = runtime_identity()
    runtime = create_demo_runtime(tmp_path, 'ppnet-demo-db-hardlink', runtime_identity=identity)
    database = runtime / 'demo_payment.sqlite3'
    PaymentService(database)
    external = tmp_path.parent / (tmp_path.name + '-payment-hardlink.sqlite3')
    os.link(database, external)
    before = hashlib.sha256(database.read_bytes()).hexdigest()
    with pytest.raises(ValueError, match='hard-linked'):
        open_demo_runtime(tmp_path, 'ppnet-demo-db-hardlink', runtime_identity=identity)
    assert hashlib.sha256(database.read_bytes()).hexdigest() == before


def test_runtime_resume_requires_a_complete_verified_identity_and_existing_path(tmp_path):
    from ppnet_demo_matcher import open_demo_runtime

    identity = runtime_identity()
    create_demo_runtime(tmp_path, 'ppnet-demo-no-restore', runtime_identity=identity)
    with pytest.raises(ValueError, match='verified model identity'):
        open_demo_runtime(tmp_path, 'ppnet-demo-no-restore', runtime_identity={'matcher': identity['matcher']})
    with pytest.raises(ValueError, match='existing isolated runtime'):
        open_demo_runtime(tmp_path, 'ppnet-demo-missing', runtime_identity=identity)
    with pytest.raises(ValueError, match='namespace named'):
        open_demo_runtime(tmp_path, '../outside', runtime_identity=identity)


def test_registry_and_default_are_explicit(monkeypatch, tmp_path):
    import biometric
    import palm_app.biometric as package_biometric
    import palm_app.debug_ui as ui
    import ppnet_demo_matcher
    monkeypatch.setattr(ppnet_demo_matcher, 'PPNetDemoMatcher', lambda root: PPNetDemoMatcher(root, encoder=FakeEncoder()))
    assert ui.DEMO_MATCHER == 'DoN'
    for registry in (biometric, package_biometric):
        with pytest.raises(ValueError, match='explicit'):
            registry.load_algorithm(tmp_path, PPNetDemoMatcher.name)
        value = registry.load_algorithm(tmp_path, PPNetDemoMatcher.name, ppnet_model_root=tmp_path)
        assert value.extract(np.zeros((4, 4), dtype=np.uint8)).shape == (512,)


def test_gallery_applies_nearest_and_fixed_decision(tmp_path):
    matcher = PPNetDemoMatcher(None, encoder=FakeEncoder())
    runtime = create_demo_runtime(tmp_path, 'ppnet-demo-gallery')
    flow = DemoFlow(runtime, matcher, lambda: None, capture_profile='test')
    metadata = {'algorithm': matcher.name, 'capture_profile': 'test'}
    vectors = np.full((5, 512), 0.1, dtype=np.float32)
    vectors[0] = 0
    flow.store.save('a', vectors, metadata)
    flow.store.save('b', np.full((5, 512), 0.2, dtype=np.float32), metadata)
    result = flow.gallery.identify(np.zeros(512, dtype=np.float32), capture_profile='test')
    assert result.status == 'MATCH' and result.user_id == 'a' and result.score == 0
    result = flow.gallery.identify(np.full(512, 2, dtype=np.float32), capture_profile='test')
    assert result.status == 'UNKNOWN'


def test_non_ppnet_demo_thresholds_remain_unchanged(tmp_path):
    class ExistingAlgorithm(FakeEncoder):
        name = 'existing-test-matcher'
        default_threshold = 0.2
        default_min_margin = 0.1
        def match(self, probe, candidate):
            return float(np.linalg.norm(probe - candidate))

    flow = DemoFlow(tmp_path, ExistingAlgorithm(), lambda: None)
    assert flow.gallery.threshold == 1.0
    assert flow.gallery.min_margin == 0.0


def test_export_identity_and_hash_are_checked_before_opening(monkeypatch, tmp_path):
    import ppnet_demo_matcher as module
    model = tmp_path / 'ppnet-tongji.onnx'
    model.write_bytes(b'synthetic')
    metadata = {
        'source_sha256': 'e83d6905bb0ca22fd202923e6b114324ddb41d90865c96a6685d0feb1f2be6b7',
        'checkpoint_sha256': 'c542c9daf893ac7cacee01402b39a12367bb137313f9d7c8825287263f0d21bb',
        'onnx_sha256': hashlib.sha256(model.read_bytes()).hexdigest(),
    }
    meta = tmp_path / 'metadata.json'
    meta.write_text(json.dumps(metadata))
    monkeypatch.setattr(module, 'PPNetPilot', lambda root: FakeEncoder())
    matcher = module.PPNetDemoMatcher(tmp_path)
    assert matcher.extract(np.zeros((4, 4), dtype=np.uint8)).shape == (512,)
    assert matcher.runtime_identity['onnx_sha256'] == metadata['onnx_sha256']
    assert matcher.runtime_identity['checkpoint_sha256'] == metadata['checkpoint_sha256']
    model.write_bytes(b'changed')
    with pytest.raises(ValueError, match='ONNX hash'):
        module.PPNetDemoMatcher(tmp_path)
    metadata['checkpoint_sha256'] = 'wrong'
    meta.write_text(json.dumps(metadata))
    with pytest.raises(ValueError, match='frozen Axon'):
        module.PPNetDemoMatcher(tmp_path)


def test_prepared_gallery_reuses_templates_and_invalidates_updates(tmp_path, monkeypatch):
    from gallery import Gallery
    from templates import TemplateStore

    store = TemplateStore(tmp_path / 'templates')
    metadata = {'capture_profile': 'rgb', 'algorithm': PPNetDemoMatcher.name}
    store.save('left', np.zeros((5, 512), dtype=np.float32), metadata)
    matcher = PPNetDemoMatcher(None, encoder=FakeEncoder())
    gallery = Gallery(store, matcher, threshold=matcher.default_threshold,
                      min_margin=matcher.default_min_margin, strict_integrity=True)
    original_load = store.load
    loads = []
    def counted_load(user_id):
        loads.append(user_id)
        return original_load(user_id)
    monkeypatch.setattr(store, 'load', counted_load)
    probe = np.zeros(512, dtype=np.float32)
    for _ in range(3):
        result = gallery.identify(probe)
        assert result.status == 'MATCH' and result.user_id == 'left' and result.score == 0
    assert loads == ['left']
    store.save('left', np.ones((5, 512), dtype=np.float32), metadata)
    result = gallery.identify(probe)
    assert result.status == 'UNKNOWN' and result.reason == 'SCORE_ABOVE_THRESHOLD'
    # The save validates the previous archive before replacing it.
    assert loads == ['left', 'left', 'left']
    store.paths('left')[0].write_bytes(b'invalid')
    result = gallery.identify(probe)
    assert result.status == 'RETRY' and result.reason == 'GALLERY_INVALID_TEMPLATES'


def test_runtime_recovery_accepts_legacy_refresh_and_abandoned_temp_but_rejects_corruption(tmp_path):
    from payment import PaymentService
    from templates import TemplateStore
    identity = runtime_identity()
    runtime = create_demo_runtime(tmp_path, 'ppnet-demo-atomic-check', runtime_identity=identity)
    root = runtime / 'demo_templates'
    root.mkdir(exist_ok=True)
    metadata = {'algorithm': identity['matcher'], 'capture_profile': 'test',
                'roi_geometry': 'pklnet-test', 'matcher_runtime_identity': identity}
    np.savez_compressed(root / 'a.npz', features=np.zeros((5, 512), dtype=np.float32))
    (root / 'a.json').write_text(json.dumps(metadata), encoding='utf-8')
    old = (root / 'a.npz').read_bytes(), (root / 'a.json').read_bytes()
    TemplateStore(root).save('a', np.ones((5, 512), dtype=np.float32), metadata)
    PaymentService(runtime / 'demo_payment.sqlite3').create_account('a', 'a', 100)
    (root / '.template-abandoned.tmp').write_bytes(b'incomplete')
    assert open_demo_runtime(tmp_path, 'ppnet-demo-atomic-check', runtime_identity=identity) == runtime
    assert ((root / 'a.npz').read_bytes(), (root / 'a.json').read_bytes()) == old
    (root / 'a.atomic.npz').write_bytes(b'broken')
    with pytest.raises((ValueError, OSError, EOFError, zipfile.BadZipFile)):
        open_demo_runtime(tmp_path, 'ppnet-demo-atomic-check', runtime_identity=identity)
