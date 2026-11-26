# FPN + C E10: Standalone CPU Shadow Check

This command-line tool runs the same **automatic FPN palm cropper + dual-branch C E10 recognizer** build as the one on X. It leaves the deployed 8088 service, thresholds, accounts, and existing templates unchanged. It neither connects to access control nor returns a pass/fail decision. Performance on the Pi, live capture, and rejection thresholds for previously unseen palms are still unverified. Do not use these offline scores for access decisions.

For browser-based 60-second enrollment and review with the same models, use the [standalone capture station](fpn-c-e10-station.md). It is separate from this single-query tool.

## Check the code on a new computer

Run these commands from `code/rasp/`. Use a separate virtual environment rather than replacing the capture station's existing environment. `requirements-fpn-c-e10.txt` records the versions used on X. This is native PyTorch inference; it does not require ONNX. Before installing, verify that compatible PyTorch and Torchvision **CPU** wheels are available for the target OS and architecture. Pi 5 AArch64 dependencies, memory use, and frame rate still need hardware validation. Do not copy the GPU wheels used on X to the Pi.

```sh
python verify_fpn_c_e10_shadow.py
python verify_fpn_c_e10_native.py  # Run only after installing all dependencies
python fpn_c_e10_shadow.py --help
```

The synthetic CLI regression check needs only NumPy and Pillow. It uses stand-in models and small synthetic solid-color images; it does not need checkpoints, a camera, or real palmprints.

## Load frozen models only on authorized devices

Get the two **exact releases** of the safetensors files from an authorized project source on the local device: the automatic FPN cropper and its corresponding C epoch 10 model. The repository does not include the models or their checksums. Copy the [example manifest](fpn-c-e10.manifest.example.json) outside the repository into the same directory as both model files. Enter the original release hashes as lowercase hexadecimal SHA-256 values from a trusted model custodian. Hashing an arbitrary file does not verify its provenance. The tool checks the format, hashes, tensor names, and shapes, and stops if a file fails to match the trusted release hash. Do not commit model files, completed manifests, sample path lists, or runtime output.

```sh
python fpn_c_e10_shadow.py --manifest /PATH/TO/LOCAL/manifest.json preflight
```

`preflight` attempts to load both models on the CPU without reading any images. It exits with a nonzero status if dependencies or checkpoints are missing, and does not fall back to another model. Passing this check does not validate deployment on the Pi or measure camera throughput.

## Score one query without saving or authorizing access

Run this manually only on local inputs allowed by the capture conditions and evaluation protocol. Fix five enrollment photos of the same palm in advance and use a separate image as the query:

```sh
python fpn_c_e10_shadow.py --manifest /PATH/TO/LOCAL/manifest.json shadow-score \
  --query /PATH/TO/LOCAL/query.jpg \
  --enroll /PATH/TO/LOCAL/e1.jpg /PATH/TO/LOCAL/e2.jpg /PATH/TO/LOCAL/e3.jpg \
           /PATH/TO/LOCAL/e4.jpg /PATH/TO/LOCAL/e5.jpg
```

The six files must be distinct. Duplicate checks detect only byte-identical files, not whether two images show the same palm or whether the split is independent. Every input goes through the frozen FPN. The same C E10 recognizer produces 512-dimensional features. The tool renormalizes them in float64 and reports the maximum cosine similarity between the query and the five enrollment images. If any crop fails, it reports the failed stage, returns no score, and does not fill in the template. On success, it prints only one unnamed score. Do not publish scores linked to participant IDs in Git or public logs. This does not perform face liveness checks or make identity or access decisions.

Before replacing the on-site 8088 service, validate native Pi dependencies and memory use, measure end-to-end camera-to-ROI-to-recognition latency on authorized data, confirm that the new verifier's geometry and scores agree with the frozen reference on identical inputs, and separately calibrate rejection on previously unseen palms and measure genuine rejection. Until then, keep the original capture service and its local data separate.
