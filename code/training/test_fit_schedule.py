import numpy as np
import pytest
from make_fit_schedule import add_schedule
from paired_data import PairedData


def fixture():
    # Two sources, one dual-hand person, uneven samples, odd capture counts.
    groups = [(0, 0, 0, 5), (0, 0, 1, 3), (0, 1, 2, 8), (0, 2, 3, 1),
              (1, 3, 0, 5), (1, 4, 1, 4)]
    rows = np.array([g[:3] for g in groups for _ in range(g[3])])
    return dict(gray=np.random.default_rng(5).integers(256, size=(len(rows), 128, 128), dtype=np.uint8),
                source=rows[:, 0], person=rows[:, 1], palm=rows[:, 2], capture=np.arange(len(rows)))


def test_seeded_new_course_covers_every_exposure_once_per_epoch():
    src = fixture()
    out = add_schedule(src, epochs=3, width=2, seed=91)
    data = PairedData(**out)
    for begin, end in zip(data.epoch_start, data.epoch_start[1:]):
        rows = np.concatenate([data.step(i).rows for i in range(begin, end)])
        np.testing.assert_array_equal(np.sort(rows), np.arange(len(src['capture'])))
    np.testing.assert_array_equal(out['batches'], add_schedule(src, epochs=3, width=2, seed=91)['batches'])
    assert not np.array_equal(out['batches'], add_schedule(src, epochs=3, width=2, seed=11)['batches'])


def test_honors_holdouts_and_refuses_existing_course():
    src = fixture()
    with pytest.raises(ValueError, match="overlap"):
        add_schedule({**src, "holdout_person": np.array([0])})
    with pytest.raises(ValueError, match="pre-existing"):
        add_schedule({**src, "batches": []})


def test_detect_checkout_and_worktree_markers(tmp_path):
    from private_paths import outside_git
    marker = tmp_path / ".git"
    marker.mkdir()
    assert outside_git(tmp_path / "new.npz")
    (marker / "HEAD").write_text("ref: refs/heads/test\n", encoding="ascii")
    assert not outside_git(tmp_path / "new.npz")
    other = tmp_path.parent / (tmp_path.name + "-linked")
    other.mkdir()
    (other / ".git").write_text("gitdir: /placeholder\n", encoding="ascii")
    assert not outside_git(other / "new.npz")
