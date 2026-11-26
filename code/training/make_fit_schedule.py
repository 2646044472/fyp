"""Plan a NEW recognizer course from an authorized FIT-only crop archive.

For each epoch, visit every supplied row exactly once. Group captures of a
source-local palm into pairs (an odd capture is a singleton); put at most
one palm of each person into a step. This is not the historical sampler.
"""
import argparse
from collections import defaultdict, deque
import os
from pathlib import Path
import tempfile

import numpy as np

from paired_data import PairedData
from private_paths import outside_git

REQUIRED = {"gray", "source", "person", "palm", "capture"}
OPTIONAL = {"holdout_person", "holdout_capture"}


def add_schedule(archive, *, epochs=10, width=12, seed=0):
    if not REQUIRED <= archive.keys() <= REQUIRED | OPTIONAL:
        raise ValueError("expected FIT crop arrays, without a pre-existing schedule")
    if epochs < 1 or not 1 <= width <= 12:
        raise ValueError("epochs must be positive; width must be between 1 and 12")
    n = len(archive["gray"])
    groups = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for key in ("source", "person", "palm"):
        vals = np.asarray(archive[key])
        if vals.shape != (n,) or vals.dtype.kind not in "iuU":
            raise ValueError("unaligned or invalid source/person/palm labels")
    for i, (source, person, palm) in enumerate(zip(archive["source"], archive["person"], archive["palm"])):
        groups[source.item()][person.item()][palm.item()].append(i)
    rng = np.random.default_rng(seed)
    steps, widths, boundaries = [], [], [0]
    for _ in range(epochs):
        course = []
        for people in groups.values():
            pending = {}
            for person, palms in people.items():
                units = []
                for rows in palms.values():
                    order = rng.permutation(rows).tolist()
                    units += [(order[i], order[i + 1] if i + 1 < len(order) else -1)
                              for i in range(0, len(order), 2)]
                rng.shuffle(units)
                pending[person] = units
            rotation = list(pending)
            rng.shuffle(rotation)
            active = deque(rotation)
            while active:
                select = [active.popleft() for _ in range(min(width, len(active)))]
                slots = np.full((2, width), -1, dtype=np.int64)
                for j, person in enumerate(select):
                    slots[:, j] = pending[person].pop()
                    if pending[person]:
                        active.append(person)
                course.append((slots, len(select)))
        rng.shuffle(course)
        for slots, size in course:
            steps.append(slots)
            widths.append(size)
        boundaries.append(len(steps))
    if not steps:
        raise ValueError("empty FIT set")
    out = {**archive, "batches": np.stack(steps), "pair_count": np.array(widths),
           "epoch_start": np.array(boundaries)}
    PairedData(**out)  # check actual trainer constraints, including supplied holdouts
    return out


def write_new_npz(path, arrays):
    """Never replace a FIT archive; publish only after serialization succeeds."""
    path = Path(path)
    out = path.parent.resolve(strict=True) / path.name
    if out.suffix != ".npz" or not outside_git(out) or out.exists() or out.is_symlink():
        raise ValueError("output must be a new .npz outside Git checkouts")
    with tempfile.NamedTemporaryFile(dir=out.parent, prefix=".fit-", suffix=".npz") as tmp:
        np.savez(tmp, **arrays)
        tmp.flush()
        os.fsync(tmp.fileno())
        os.link(tmp.name, out)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="local unscheduled FIT crop .npz")
    parser.add_argument("--output", type=Path, required=True, help="new, private scheduled .npz")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--width", type=int, default=12)
    parser.add_argument("--seed", type=int, default=0)
    a = parser.parse_args()
    if a.input.suffix != ".npz" or not outside_git(a.input):
        parser.error("input must be a FIT-only .npz outside Git")
    with np.load(a.input, allow_pickle=False) as z:
        if not REQUIRED <= set(z.files) <= REQUIRED | OPTIONAL or len(set(z.files)) != len(z.files):
            parser.error("unexpected or duplicate fields in unscheduled FIT input")
        arrays = add_schedule({key: z[key] for key in z.files}, epochs=a.epochs, width=a.width, seed=a.seed)
    write_new_npz(a.output, arrays)
    print(f"Planned {len(arrays['batches'])} updates over {a.epochs} epochs for a NEW course.")


if __name__ == "__main__":
    main()
