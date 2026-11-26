# C E10 portable offline trainer

The exact C embedding class and normalization used by the tracked station inference code are imported from `code/rasp/frozen_fpn_c_e10.py`. This lane does not make a second definition of the model. It preserves native grayscale 128, S2 local and S4 global heads, 512 dimensions, .60 symmetric pair CE/.40 source-local ArcFace, 100-step warmup and cosine, grouped AdamW, first epoch shallow freeze, and gradient clipping. External libraries are dependencies, not vendored here. The underlying architecture is [ConvNeXt V2](https://arxiv.org/abs/2301.00808), instantiated via the inference contract's pinned timm release.

From a checkout root, with Python supporting the pinned package wheels:

```sh
python -m pip install -r code/training/requirements.txt
python code/training/convnext_e10.py --smoke
python -m unittest discover -s code/training -p test_convnext_e10.py
```

The smoke does two genuine optimizer updates on artificial pixels, freezes/thaws the shallow trunk, and uses the same inference entry to return a 512-wide descriptor. It checks wiring, not recognition accuracy, device setup or Pi latency.

## Train on authorized local inputs

```sh
python code/training/convnext_e10.py --data /path/outside/repository/fit.npz \
  --device cuda --init-backbone /path/to/authorized-generic.safetensors \
  --init-sha256 "$EXPECTED_SHA256" \
  --save /path/outside/repository/new-c-encoder.safetensors
```

Input NPZ keys (no pickle, paths, or objects in the file):

| Key | Contract |
| --- | --- |
| `gray` | N×128×128 uint8, nonconstant grayscale ROIs, in their canonical stored orientation. Generate via an authorized original-pixel cropper or the appropriate authorized author-ROI path. |
| `source`, `person`, `palm`, `capture` | Aligned length-N integer or Unicode labels. `person` must represent the same person across sources; `palm` is unique within its source and distinct for each hand; `capture` is unique and must identify the physical exposure, not a derived view. These arrays stay local. |
| `batches` | Signed integer S×2×P, 1≤P≤12. Each step fixes a source. First row is distinct-person anchor indices, second row contains same-palm positives or −1. No capture row reuse in the same step; entries beyond each planned width are −1. |
| `pair_count` | Length S planned widths. This determines the 2P denominator; a missing positive does not compress it. |
| `epoch_start` | Strictly increasing integer boundaries starting at 0 and ending at S. This explicit schedule determines the number of epochs. |
| `holdout_person`, `holdout_capture` (optional) | 1-D labels only for a local disjointness check; the trainer never accesses held-out image pixels. This check depends on correct caller-supplied global person/exposure labels. |

The loader rejects unknown fields, constant crops, malformed steps, cross-source pairs and supplied holdout collisions. It does not derive identities or verify metadata/physical independence on its own. A simple valid two-epoch schedule is in `synthetic_paired()`. Use the checkpoint directory outside the source tree and maintain a private authorized backup of the exact local model/manifest if needed. New C weights produced by this trainer match the station's 201-tensor encoder layout but are not the published historical selection. The station must only read a manifest for the intended trusted checkpoint; do not automatically switch a real Pi to new weights.

With no initialization flag the trainer starts from random weights. `--init-backbone` strictly loads the generic local timm trunk with its 1,000-class head and then drops that head. `--start-encoder` loads an authorized compatible C checkpoint but starts a **fresh** optimizer and new source proxies; it is a warm start, not a bitwise optimizer resume. No automatic download, included or redistributed checkpoint, private cohort, exact historical signed schedule, prepared crop cache or old sealed workstation run files. Even with the same mathematics, this portable entry cannot reproduce the historical E10 final weights without recreating the separate authorized inputs, initial state, original schedule and environment. It does not choose checkpoints against held-out images and does not report biometric scores.
