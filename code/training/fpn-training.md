# Train the FPN geometry localizer

Run from the repository root with the Torch, torchvision, OpenCV, Pillow, NumPy,
timm and safetensors versions in `code/rasp/requirements-fpn-c-e10.txt`:

```sh
python code/training/fpn_train.py --smoke
python -m unittest discover -s code/training -p test_fpn_train.py
```

The smoke command is one real CPU update on two artificial canvases. It sends
a gradient through the ResNet-50 stem, and checks one supported chart and one
unsupported chart. No data, model weights, downloads or checkpoint output.

## Local FIT input

For a FIT-only split that you are authorized to use locally, pass
`--npz /path/to/local-fit.npz`. The archive must contain exactly these arrays:

| Array | Shape and type | Contract |
| --- | --- | --- |
| `canvas_rgb` | `uint8[N,320,256,3]` | RGB, same device-independent letterboxed coordinates as the station preprocessor. |
| `canvas_corners` | `float32` or `float64[N,4,2]` | A physical chart's four ordered cyclic `(x,y)` corners; first edge defines the axis, positive image-coordinate winding. |
| `support_mask` | `bool` or 0/1 `uint8[N,320,256]` | Real image support, not a skin or non-black mask. A chart is supported only if all four sampled corners and its center remain in support. |

`pack_native(rgb, corners)` is a small Python helper for already EXIF-oriented
native RGB and approved same-exposure corner annotations. It uses the station
letterbox transform for both landmarks and its physically valid support mask.
The training CLI takes no identity data; the caller must ensure data
permissions, whole-person split disjointness, and source provenance before
preparing the archive. Keep the input and generated artifacts outside Git.

## Continue on another computer

Supply the same local FIT archive on the new computer. To start with the full
previous FPN state and save a new terminal checkpoint:

```sh
python code/training/fpn_train.py --npz /local/fit.npz --device cpu \
  --start-encoder /local/old-fpn.safetensors --init-sha256 "$EXPECTED_SHA256" \
  --save /local/new-fpn.safetensors
```

Only copy checkpoints and data by authorized local means. `--start-encoder`
loads the complete exact model state, not the optimizer, seed progression or
epoch. The learning-rate warm-up and batch schedule restart. The optional
`--init-sha256` verifies the expected digest for the full state; use the
digest recorded independently at the source. Alternatively use
`--init-backbone FILE --init-sha256 DIGEST` for an independently obtained,
licensed, local torchvision ResNet-50 safetensors state that includes the
generic 1000-class head (discarded). Nothing is downloaded and no palm-trained
initialization is bundled. Omitting both initializers starts with random weights.

`--save` (alias `--output`) writes only a new mode-0600 model file outside the
source tree, verifies the serialized tensors, and publishes atomically without
overwriting an existing file. The station's strict FPN loader reads this same
state schema with an independently supplied SHA-256. A resulting checkpoint
is **not** the released FPN and must not replace a trusted manifest without
separate validation. The ordinary synthetic smoke never reads or saves weights;
the round-trip unit test creates and automatically removes a synthetic checkpoint
outside the source tree.

## What is and is not reproduced

This adapter shares the exact inference model definition. It retains the
original direction-aware geometry and heatmap loss, group learning rates,
120-step warm-up, frozen backbone BN buffers, affine/photometric perturbations,
coded distal clipping, and final-epoch training policy. It deliberately
does **not** re-create the private corpus, signed roster/shards, shard-specific
iteration order or opaque release gates. The public batch schedule uses a
shuffled in-memory FIT archive; losses/weights are not a reproduction of the
historical run. Nothing here makes a Pi 5, accuracy or production claim.
