import pytest
from protocol import check_people, evaluate


def test_denominator_includes_failed_and_unenrolled_hands():
    assert evaluate([('a',[1,0]), ('b',[0,1])],
                    [('a',[1,0]), ('a',[0,1]), ('a',None), ('c',[1,0])]) == {
        'planned':4, 'correct':1, 'incorrect':1, 'query_failed':1, 'true_gallery_missing':1}


def test_do_not_split_two_hands_of_one_person_across_cohorts():
    with pytest.raises(ValueError):
        check_people([1,2], [3], [2,4])


def test_intake_sampling_and_out_of_frame_rejection():
    import numpy as np
    from intake import select_two, crop_marks
    assert select_two(['a','b','c']) == select_two(['c','a','b'])
    rgb = np.zeros((128,128,3), dtype=np.uint8)
    marks = np.array([[52,48],[52,52],[72,48],[72,52]])
    assert crop_marks(rgb,marks,[1,2,3,4]).shape == (112,112,3)
    with pytest.raises(ValueError):
        crop_marks(rgb,marks-50,[1,2,3,4])
