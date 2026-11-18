import pytest

from coverage_policy import Match, audit


def test_route_choice_does_not_depend_on_score_or_truth():
    primary = Match("A-L", .4)
    alternate = Match("A-R", .99)
    counts = audit([("A-L", primary, alternate), ("A-R", primary, alternate),
                    (None, primary, alternate)], .7)
    assert counts == {"known_planned": 2, "unknown_planned": 1, "used_upright": 3,
                      "rank1_correct": 1, "rank1_wrong": 1, "known_reject": 2,
                      "unknown_reject": 1}


def test_missing_is_not_rejection_and_threshold_tie_accepts():
    x = Match("A-R", .7)
    counts = audit([("A-R", None, x), ("A-L", None, x), ("A-L", None, None),
                    (None, None, x), (None, None, None)], .7)
    assert counts == {"used_direct": 3, "known_planned": 3, "unknown_planned": 2,
                      "rank1_correct": 1, "rank1_wrong": 1, "known_correct_accept": 1,
                      "known_wrong_accept": 1, "known_missing": 1,
                      "unknown_false_accept": 1, "unknown_missing": 1}


@pytest.mark.parametrize("bad", [float("nan"), float("-inf"), float("inf")])
def test_reject_nonfinite_inputs(bad):
    with pytest.raises(ValueError):
        Match("A-L", bad)
    with pytest.raises(ValueError):
        audit([], bad)
