# Code workspace

Use this tree for the **device implementation and offline diagnostics**. For the school-facing record, start instead with the [meeting and progress index](../gitea-um/README.md); its historical demo is not the development copy.

| Task | Entry point | What it verifies |
| --- | --- | --- |
| Run or inspect the Pi camera app | [palm_demo](palm_demo/README.md), [setup](palm_demo/docs/SETUP.md) | Camera acquisition, enrollment, verification and on-device behavior. Historical timing is specific to the named pipeline and hardware. |
| Interpret a replay or evaluation | [Protocol index](palm_demo/docs/protocols/README.md), then the corresponding script in `palm_demo/tools/` | The intended dataset, split, gallery and limitations. Some historical scripts need local inputs not supplied with a clean checkout. |
| Measure crop geometry separately from identity | [offline_roi_audit](offline_roi_audit/README.md) | Coverage and intrusion proxies. These are not segmentation ground truth or recognition accuracy. |
| Check whether a changed dependency invalidates a result | [experiment_registry](experiment_registry/README.md) | Dependency consistency and propagation. Its local live registry is not required for the examples. |
| Understand the third-party palm-keypoint localizer | [pklnet](pklnet/README.md) | The upstream localization component, not a complete hand-recognition or verification system. |

## Start without a camera

From the repository root, the registry tests use only the Python standard library. The geometry tests need NumPy, OpenCV and Pillow. Both use synthetic inputs:

```sh
(cd code/experiment_registry && python -m unittest discover -s tests)
(cd code/offline_roi_audit && python -m unittest discover)
```

For a synthetic end-to-end **training** smoke test rather than these component checks, see the [portable research trainer](../gitea-um/research_code/README.md). Passing any of these checks does not verify a physical Pi or the accuracy of a trained model.

## Workstation and deployment boundaries

Run installation, connection and packaging tools from the application root under `palm_demo/deploy/` as directed by the [setup guide](palm_demo/docs/SETUP.md). Do not remove local model or vendor dependencies as “cleanup,” and do not add local checkpoints to Git to make an example run. Handle capture archives, derived crops, templates and per-sample outputs independently of source cleanup, following the [repository rules](../AGENTS.md). The capture data directory and case-level ledgers are intentionally absent from the current public tree. A clean checkout supplies code, not local research inputs.
