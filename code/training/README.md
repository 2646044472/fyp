# Training the current models

These are project-owned, portable training implementations. The **FPN and C import their model classes directly from the station**. “E10” identifies the historical epoch-10 recognizer, not the identity of a file produced by this trainer. PalmBridge is a separate comparison recognizer. Do not use its weights with the C loader.

| Path | Model input and output | Source and objective |
| --- | --- | --- |
| [FPN trainer](fpn_train.py) · [data and flags](fpn-training.md) | Native RGB → letterboxed RGB canvas (320 H × 256 W) → four ordered corners and a confidence. The station warps the **original image pixels** to form its ROI. | Station [ResNet-50/FPN localizer](../rasp/frozen_fpn_c_e10.py); center, log-side, oriented axis, heatmap and support-confidence loss. |
| [C trainer](convnext_e10.py) · [data and flags](convnext-e10-training.md) | A 128 × 128 uint8 grayscale ROI → three normalized channels → 256-D global + 256-D local → 512-D feature. | Station [ConvNeXtV2-tiny dual-branch encoder](../rasp/frozen_fpn_c_e10.py); symmetric pair cross-entropy and source-local angular-margin proxies. |
| [PalmBridge trainer](palmbridge_train.py) · [architecture](palmbridge.py) | Same stored 128 × 128 grayscale ROIs → nonzero-pixel normalization → 512-D CompNet vector → nearest-codeword blend. Use `model.encode(uint8_batch)` for normalized 512-D descriptors. | Independently implemented [PalmBridge architecture](https://arxiv.org/abs/2601.20351), trained with the paired objective and bridge regularizers. Occupies a different parameter/feature space from C; not a station backend. |

## Check each model without external inputs

Install the [CPU development environment](../../README.md#start-on-a-new-computer) first. From the repository root:

```sh
python code/training/fpn_train.py --smoke
python code/training/convnext_e10.py --smoke
python code/training/palmbridge_train.py --smoke
```

These do real optimizer updates on artificial pixels. FPN takes one step. C and PalmBridge each take two, crossing the shallow-layer freeze/thaw boundary. For unit tests, real file-input paths and an FPN+C export-to-station round trip, run `python tools/check_recovery.py training`.

## Run the input adapters end to end

This example **creates** a tiny set of artificial numeric arrays. The same commands accept appropriately prepared, authorized **private FIT** inputs. Keep archives and weights outside Git. No sample downloads or private library imports are needed.

```sh
WORK=$(mktemp -d)
python code/training/synthetic_inputs.py --out-dir "$WORK/examples"
python code/training/make_fit_schedule.py \
  --input "$WORK/examples/crops.npz" --output "$WORK/scheduled.npz" \
  --epochs 2 --width 2 --seed 17
python code/training/fpn_train.py --npz "$WORK/examples/geometry.npz" \
  --epochs 1 --batch-size 2 --save "$WORK/dev-fpn.safetensors"
python code/training/convnext_e10.py --data "$WORK/scheduled.npz" \
  --save "$WORK/dev-c.safetensors"
python code/training/palmbridge_train.py --data "$WORK/scheduled.npz" \
  --save "$WORK/dev-pb.safetensors"
```

The example leaves its generated files in `$WORK`; remove that private temporary directory when you no longer need it. CLI fields such as `synthetic` indicate whether `--smoke` was used, not the provenance of a file supplied with `--data` or `--npz`. Persist (or compare) only aggregate logs that may be shared.

### Prepare real inputs locally

- **FPN:** start with authorized FIT-only source images and four ordered corners in **the same exposure and EXIF-corrected native coordinate system**. Use `fpn_train.pack_native(rgb, corners)` before stacking the three arrays `canvas_rgb`, `canvas_corners` and `support_mask`. It uses the same affine as station inference. The [FPN guide](fpn-training.md) specifies shape, winding and support. Do not substitute an arbitrary resized image and untransformed native coordinates.
- **C and PalmBridge:** start from the *same* chosen stored-orientation grayscale ROIs and explicit `source`, `person`, `palm`, `capture` arrays. The recognizer trainer does not estimate a crop: from full-hand images use the intended authorized cropper (the current station uses [`crop_gray`](../rasp/frozen_fpn_c_e10.py)), or use the proper author/manual-ROI path for a recognizer-only protocol. Do not silently replace failed automatic crops with manual ones or mix ROI protocols. Keep an admission ledger locally. Splits must be declared by person **before** training. The optional `holdout_person` and `holdout_capture` arrays can check provided labels but cannot establish cross-source identity independence.
- **New training schedule:** put the unscheduled `gray`, `source`, `person`, `palm`, `capture` arrays and optional holdout labels in a local NPZ, without pickled objects. The [schedule builder](make_fit_schedule.py) never selects the FIT cohort. It uses each admitted crop once per epoch, batches a single source with distinct people, pairs different captures of the same palm, and leaves an odd capture without a mate. Both trainers validate the resulting `batches`, `pair_count` and `epoch_start` arrays. This is a reproducible **new** ordering, not the historical one. If permitted and available, supply your already scheduled archive directly; see the [full field contract](convnext-e10-training.md).
- **Initialization and persistence:** the default is random initialization, no pretrained download. FPN and C can also initialize from a compatible, independently obtained, licensed local generic backbone. All three can use `--start-encoder` for an authorized model-only warm start and `--save` for a new terminal safetensors state. Use `--init-sha256 "$EXPECTED_SHA256"` to check an independently trusted initializer; it is required for FPN's generic backbone. An encoder export contains **no optimizer moments, classifier proxies, sampler state, or epoch progress**. It cannot resume an interrupted optimizer step or identify a historical release. No historical data access or provenance is granted by these commands.

The original private corpora, person/split/admission manifests, precise historical ordering, release selection metadata, model assets, and complete run state are not published here. A code-compatible fit is not bit-for-bit reproduction or a new accuracy result. Use the [recovery checklist](../../docs/development/recovery.md) for trained inference or a workstation move.
