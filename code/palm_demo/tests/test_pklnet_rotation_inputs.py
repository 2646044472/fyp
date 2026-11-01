"""Right-angle views can be duplicate network inputs after portrait canonicalization.

Synthetic pixels only. No model/session/weights are loaded or inferred.
"""
from pathlib import Path

import numpy as np
import pytest
from PIL import Image


@pytest.mark.parametrize('size,groups', [((53,37),[(0,3),(1,2)]),
    ((37,53),[(0,1),(2,3)]), ((41,41),[(0,),(1,),(2,),(3,)])])
def test_effective_rotation_inputs_not_four_independent_observations(monkeypatch,size,groups):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]))
    from pklnet_roi import PKLNetROI
    def no_model(*args,**kwargs):
        raise AssertionError('Synthetic preprocessing must not load a model')
    monkeypatch.setattr(PKLNetROI,'_ensure_loaded',no_model)
    rng=np.random.default_rng(20261101)
    image=Image.fromarray(rng.integers(0,256,(size[1],size[0],3),dtype=np.uint8))
    operations=(None,Image.Transpose.ROTATE_90,Image.Transpose.ROTATE_180,Image.Transpose.ROTATE_270)
    inputs=[PKLNetROI._prepare(image if op is None else image.transpose(op))[0] for op in operations]
    for a in range(4):
        for b in range(4):
            expected=any(a in group and b in group for group in groups)
            assert np.array_equal(inputs[a],inputs[b]) == expected
