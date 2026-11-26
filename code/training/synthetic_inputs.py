"""Write two artificial FIT input examples to a NEW temporary/private directory."""
import argparse
from pathlib import Path
import numpy as np
from make_fit_schedule import write_new_npz
from private_paths import outside_git


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", required=True, type=Path, help="new directory outside Git")
    out = parser.parse_args().out_dir
    if not outside_git(out):
        parser.error("choose a new directory outside Git")
    out.mkdir(mode=0o700, exist_ok=False)
    rng = np.random.default_rng(17)
    canvas = rng.integers(256, size=(2, 320, 256, 3), dtype=np.uint8)
    corners = np.array([[50, 85], [180, 85], [180, 215], [50, 215]], dtype=np.float32)
    write_new_npz(out / "geometry.npz", dict(canvas_rgb=canvas, canvas_corners=np.stack([corners, corners]),
                                            support_mask=np.ones((2, 320, 256), dtype=bool)))
    write_new_npz(out / "crops.npz", dict(gray=rng.integers(256, size=(4, 128, 128), dtype=np.uint8),
                                         source=np.zeros(4, dtype=int), person=np.array([0, 0, 1, 1]),
                                         palm=np.array([0, 0, 1, 1]), capture=np.arange(4)))
    print("Wrote geometry.npz and unscheduled crops.npz with artificial random pixels only.")


if __name__ == "__main__":
    main()
