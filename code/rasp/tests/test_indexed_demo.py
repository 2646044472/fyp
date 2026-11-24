from pathlib import Path
import numpy as np
import pytest
from biometric import load_algorithm
from gallery import Gallery
from templates import TemplateStore


class GlobalDistance:
    prepared_cache_limit_bytes = 4096
    def __init__(self): self.generations = []
    def prepare_probe(self, probe): return probe
    def prepare_enrollment(self, features): return features.copy()
    def prepared_bytes(self, features): return features.nbytes
    def score_prepared(self, *_args): raise AssertionError('must use the global index path')
    def prepare_gallery(self, groups):
        self.generations.append({k:v.copy() for k,v in groups.items()})
    def score_gallery(self, probe, groups):
        self.prepare_gallery(groups)
        return {k:float(np.min(np.abs(features-probe))) for k,features in groups.items()}


def test_global_gallery_warmup_and_queries_respect_updates_and_metadata(tmp_path):
    store = TemplateStore(tmp_path)
    algorithm = GlobalDistance()
    gallery = Gallery(store, algorithm, threshold=1, required_metadata={'algorithm':'indexed'})
    metadata = {'capture_profile':'noir-ir','algorithm':'indexed'}
    store.save('a',np.array([[.1]]),metadata)
    store.save('b',np.array([[.8]]),metadata)
    store.save('old',np.array([[.0]]),{**metadata,'algorithm':'obsolete'})
    gallery.warm_up()
    assert set(algorithm.generations[-1]) == {'a','b'}
    assert gallery.prepared_cache_limit_bytes == 4096
    assert gallery.identify(np.array([.1]),'noir-ir').user_id == 'a'
    store.save('a',np.array([[.9]]),metadata)
    assert gallery.identify(np.array([.1]),'noir-ir').user_id == 'b'
    store.delete('b')
    assert gallery.identify(np.array([.1]),'noir-ir').user_id == 'a'
    assert set(algorithm.generations[-1]) == {'a'}


def test_indexed_matcher_is_opt_in_and_does_not_accept_enrollment_as_probe():
    root = Path(__file__).resolve().parents[1]/'vendor/palmprint-recognition-python'
    algorithm = load_algorithm(root, 'FastCCIndexed-v7-experimental')
    try:
        from PIL import Image
        image = Image.fromarray(np.random.default_rng(3).integers(0,256,(256,256,3),dtype=np.uint8))
        probe = algorithm.extract_probe_with_context(image, np.array([[64,64],[192,64],[192,192],[64,192]],np.float32), np.asarray(image.convert('L').resize((128,128))))
        assert probe.bank.shape == (9,32,32)
        assert algorithm.prepare_probe(probe) is probe
        with pytest.raises(ValueError, match='fresh query'):
            algorithm.prepare_probe(np.zeros(128,dtype=np.uint8))
        algorithm.prepare_gallery({})
        assert algorithm._index is None and algorithm._references == {}
        assert algorithm.enrollment_requires_hypotheses
    finally:
        algorithm.close()
    assert load_algorithm(root, 'DoN').name == 'DoN'
