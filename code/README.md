# FYP Development and Experiment Handoff

On a new computer, start with [`code/rasp/`](rasp/README.md). Do not maintain a second copy of the school handoff snapshot. This repository contains only shareable source code, synthetic tests, and aggregate documentation. Authorized staff manage models, original images and ROIs, templates, participant lists, and per-sample results locally on the device.

## Choose a starting point

| Task | Where to start | Scope |
| --- | --- | --- |
| New recognition baseline and camera demo | [Standalone FPN + C E10 station](rasp/fpn-c-e10-station.md) · [CPU preflight and single-query scoring](rasp/fpn-c-e10-shadow.md) | Native PyTorch; ONNX is not required. You need two trusted local model files and a manifest outside the repository. This handoff did not validate the current revision on a Pi 5. |
| Update or roll back the legacy Pi service | [PKLNet + FastCC v6](rasp/README.md#deploy-to-pi-5) · [Legacy engine and original-image capture](rasp/ENGINE-README.md) | The legacy Pi service runs on port 8088. Do not replace its environment, templates, or data with those of the new station. |
| Reproduce research methods or counting procedures | [Portable research code](../gitea-um/research_code/README.md) · [Protocols and aggregate results](rasp/docs/protocols/README.md) | This is not a complete, frozen experiment package. Training data, frozen checkpoints, and per-sample evidence are not included. |
| Audit experiment dependencies or inspect offline palm-crop geometry | [Experiment registry](experiment_registry/README.md) · [ROI geometry checks](offline_roi_audit/README.md) | Synthetic tests and offline tools only. These are not the live crop policy. |
| Find authorized data sources and historical results | [Dataset sources](../dataset/README.md) · [School handoff and reports](../gitea-um/README.md) | Historical reports and the school snapshot are not a second deployment target. |

## Raspberry Pi and Yesand

- Set up a separate Python environment and private runtime directory using the [station startup instructions](rasp/fpn-c-e10-station.md). Follow the [model manifest instructions](rasp/fpn-c-e10-shadow.md#load-frozen-models-only-on-authorized-devices) to verify the trusted SHA-256 hashes, then run `preflight`. Check that the CPU dependencies match your host. Installation, latency, and live capture on Pi 5 ARM64 still need separate validation.
- The **current station listens on the Pi's loopback port 8080**. From Yesand, forward an available local port, for example: `ssh -N -o ExitOnForwardFailure=yes -L 127.0.0.1:8080:127.0.0.1:8080 PI_SSH_ALIAS`. Replace the alias with your own and change the left-hand port if local port 8080 is already in use. Check `/station-health` locally for `backend: fpn-c-e10-frozen`. A `ready` status does not mean the current frame is suitable. The documented legacy example forwards Yesand port 8089 to Pi port 8088. An old bookmark will not verify the new engine. An earlier revision used Pi port 8089; use the instructions for your checked-out revision. Do not let both stations use the camera at the same time or expose either to the public internet.
- The **current station** requires at least 60 seconds of active capture; pauses do not count. When at least 10 candidate sets are available, choose **Select 10 photos**. Capture can continue after the timer ends; 60 seconds is not the maximum for the full workflow. For first-time enrollment, the five highest-ranked sets build the template. Before clicking **Confirm and save**, review the original image, high-resolution ROI, and 128×128 model ROI from each exposure. You can remove and recapture candidates. After saving, check the photo library and dimensions at the new station's `/collect`. For separate full-resolution original-image capture using the legacy engine, use that station's own `/collect` and release the camera before switching. Keep directories, templates, and participant information separate.
- The new station's `/gate` page uses 0.80 as the default demo match threshold. **This threshold is uncalibrated and must not be used for access control.** Separately evaluate same-palm and previously unenrolled-palm comparisons, end-to-end latency, and capture compatibility with authorized live samples. Synthetic regression results are not evidence of performance on the Pi.

## Pick up existing experiments

| Existing experiment code | Public reproduction entry point | Not distributed with the repository |
| --- | --- | --- |
| Geometry and augmentation, MPD landmark-based cropping, historical 20-epoch training, and scoring conventions | [Research code](../gitea-um/research_code/README.md): `geometry.py`, `intake.py`, `augment.py`, `train.py`, and `protocol.py`. The synthetic CPU training check runs a single step. | Private loaders used for historical training, participant-level splits, real images, and model weights |
| Frozen FPN + C E10, fixed five-photo enrollment and one-photo query | [Standalone native inference](rasp/fpn-c-e10-shadow.md): run `preflight` or run `shadow-score` on explicit local inputs. See the [protocol directory](rasp/docs/protocols/README.md) for evaluation rules. | Dataset-wide runs on X, private role manifests, and frozen models. A single-query entry point does not reproduce the paper's batch experiments. |
| Matched C/PalmBridge runs on MPD, Tongji cross-session pairs, multi-dataset runs outside MPD, and MPD full-image and hand-field-of-view diagnostics | Complete run scripts exist locally on X. In the public checkout, consult the [counting protocol](../gitea-um/research_code/README.md), [analysis reports](../gitea-um/README.md), and [dataset sources](../dataset/README.md) for the conditions. | The reviewed historical scripts still depend on local experiments, data adapters, or authorized artifacts. The public checkout cannot rerun those frozen results. The scripts are not bundled into the app or presented as a portable CLI. |
| Missing ROIs, orientation, visible coverage, and switching crop rules | [Offline geometry tools](offline_roi_audit/README.md) and the [coverage-counting example](../gitea-um/research_code/README.md#replay-the-crop-fallback-without-biometric-data) | Original images and diagnostic samples. Held-out validation beyond the existing checks, deployment replacements, and new optimizations are outside this handoff. |

If you already have per-query results for two methods on the local device, use the [paired outcome counter](experiment_registry/paired_outcomes.py) with a fixed query plan to produce aggregate counts only. The self-test has no external dependencies: `python code/experiment_registry/paired_outcomes.py --self-test`. The tool does not run models, fit thresholds, or repeat historical experiments.

Keep every planned query in the denominator, including queries with no enrollment, missing images, or no extracted ROI. Report identification rank separately from accept/reject decisions, and do not tune thresholds on the test set. Use the same independent roster, fixed enrollment photo count, and identical queries for paired comparisons.

## Run synthetic checks before changing code

```sh
cd code/rasp
python3 verify_best_frame.py
python3 verify_review.py
python3 verify_ranked_window.py
python3 verify_adapter.py
python3 verify_fpn_c_e10_shadow.py
python3 verify_fpn_c_e10_native.py   # Requires the native dependencies
python3 verify_fpn_c_e10_station.py # Requires the image and service dependencies; uses a simulated camera
```

For offline diagnostics, use the unit tests listed in their READMEs. In a change summary, identify the affected paths, commands and results, and any checks still needed on a physical Pi. Follow the [repository data rules](../AGENTS.md) and commit only reviewed files. Do not commit local manifests, weights, original images or ROIs, identity information, runtime logs, or credentials.
