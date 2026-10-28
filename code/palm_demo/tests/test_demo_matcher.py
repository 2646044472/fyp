from pathlib import Path
import cv2
import numpy as np
import pytest
from PIL import Image
from palm_app.biometric import load_algorithm


def test_enrollment_role_is_exact_for_scoring_and_cannot_be_queried():
    a=load_algorithm(Path(__file__).resolve().parents[1]/'vendor/palmprint-recognition-python','FastCCDemo-v6')
    rgb=np.random.default_rng(103).integers(0,256,(300,400,3),dtype=np.uint8)
    image=Image.fromarray(rgb);q=np.array([[80,50],[250,50],[250,220],[80,220]],np.float32)
    roi=cv2.resize(cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY),(128,128))
    hypotheses=[dict(quad=q,valid=True),dict(quad=q+10,valid=True,kind='window')]
    full=a.extract_with_hypotheses(image,q,roi,hypotheses)
    old=load_algorithm(Path(__file__).resolve().parents[1]/'vendor/palmprint-recognition-python','FastCCAnchoredUnion-v5')
    serial=old.extract_with_hypotheses(image,q,roi,hypotheses)
    serial[:4]=np.asarray([a.magic],'<i4').view(np.uint8)
    np.testing.assert_array_equal(full,serial)
    gallery=a.extract_gallery_with_context(image,q,roi)
    assert a._unpack(gallery)[3] is None
    assert a.match(full,full)==a.match(full,gallery)==0
    assert a.score_prepared(a.prepare_probe(full),a.prepare_enrollment([gallery]))==a.score_enrollment(full,[full])
    with pytest.raises(ValueError,match='Enrollment-only'):a.prepare_probe(gallery)
    with pytest.raises(ValueError,match='Enrollment-only'):a.match(gallery,full)
    with pytest.raises(ValueError,match='Enrollment-only'):a.match_with_diagnostics(gallery,full)
    a.close()
