import importlib
from pathlib import Path

import cv2
import numpy as np


def test_synthetic_web_defects_follow_image_halfturn_and_polarity(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]/'tools'))
    module=importlib.import_module('observe_contour_valleys')
    image=np.zeros((256,256,3),np.uint8)
    cv2.rectangle(image,(60,130),(200,230),(220,220,220),-1)
    for left,top in [(65,70),(100,40),(135,25),(170,50)]:
        cv2.rectangle(image,(left,top),(left+18,145),(220,220,220),-1)
    _,records,_=module.silhouettes(image)
    assert records[0]['candidate_count']>=3
    _,rotated,_=module.silhouettes(np.rot90(image,2).copy())
    _,inverted,_=module.silhouettes(255-image)
    assert rotated[0]['candidate_count']==records[0]['candidate_count']
    assert inverted[1]['candidate_count']==records[0]['candidate_count']
    old=records[0]['candidate_valleys']
    restored=[255-np.asarray(p) for p in rotated[0]['candidate_valleys']]
    # A flat web floor has several equally deep pixels: both orientations
    # must locate each physical gap, rather than choose the same tied pixel.
    for points in [old,restored]:
        for left,right in [(83,100),(118,135),(153,170)]:
            assert any(left<=x<=right and 129<=y<=130 for x,y in points)
