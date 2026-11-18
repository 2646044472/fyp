# Research code: from an image to a counted decision

This is the portable portion of the **project's own** offline research implementation. It is not the complete private experiment tree, a trained recognizer, or a redistribution of author detectors. The historical Pi demo lives separately in [palm_demo](../palm_demo/README.md).

| File | What it does | Where it was used |
| --- | --- | --- |
| `geometry.py` | Builds a palm quadrilateral from wrist/finger-base landmarks, reverses cardinal rotation then removes square padding, warps and contrast-normalizes the **original pixels**. | Landmark pipeline and November coordinate audit. External landmark detection is not included. |
| `intake.py` | Chooses two candidate filenames per person/session/device/hand group deterministically and extracts a 112px square from MPD manual marks. Rejects bad geometry; no silent substitution. | Training and validation intake. These marks were **not** available to the automatic test localizer. |
| `encoder.py` | Project residual encoder, four stages with two blocks each and a 512-component output. | Same architecture used by the 20-epoch MPD controlled training runs. |
| `augment.py` | Project random inverse-affine warp around the center, with replicated borders. | Geometry-only training arm, not a reproduction of an author augmentation system. |
| `train.py` | Portable RGB-input trainer: normalized features and class weights, target angular margin 0.5, logit scale 64, SGD, seed 18011, 20 epochs with LR drops at epochs 7 and 15 (zero-based). | Adapted from the matched 100-person jobs. The model and margin logic are retained; filesystem access, device selection and reporting were rewritten. The loss-adversarial generator, checkpoint persistence and private loaders are not included. |
| `protocol.py` | Checks disjoint **people** across roles; reports top-1 by hand class across every planned probe, including missing inputs and missing enrollment. | Portable version of local cohort and score-accounting logic, returning aggregates only. |

## Run without a camera, data or a network service

Use Python 3.10+ and an environment with dependencies in `requirements.txt`. From this directory:

```sh
python -m pytest -q
python train.py --device cpu --mode geometry
```

The second command runs one real optimizer update on four artificial RGB arrays, then scores two artificial probes. It checks training and validation wiring; it cannot reproduce or estimate recognition accuracy. No weights or biometric data are saved.

For authorized **local-only** data, `python train.py --npz INPUT.npz --mode none` expects uint8 RGB arrays `train_rgb` and `val_rgb` (N × 112 × 112 × 3); aligned integer or Unicode arrays `train_class, val_class` (person × side), `train_person, val_person`; boolean `val_gallery` (true for gallery); and `eval_person` containing evaluation-person identifiers for the overlap check. Do not include object arrays or upload this file. The trainer scores validation every epoch and prints counts; it does not open the held-out evaluation images. Use `protocol.evaluate` with a full planned probe list, including None for missing crops. Do not tune a threshold on a reported test set.

Historical outputs and interpretation: [integrated experiment report](../minutes_note/progress_reports/2026-11-18.md). Implementations were extracted or adapted from the project's geometry, matched-MPD intake/trainer and scoring routines, rather than repackaging vendor source. No original data, face/hand models, author checkpoints or biometric templates are required for the synthetic path.
