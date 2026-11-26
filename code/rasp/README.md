# Current Raspberry Pi station

Start with the [native CPU and model manifest guide](fpn-c-e10-shadow.md), then follow the [60-second FPN + C E10 station guide](fpn-c-e10-station.md). The browser station listens only on port **8080** on localhost. From another development computer, use the SSH forwarding command in the station guide and verify that `/station-health` reports `fpn-c-e10-frozen`.

Main entry points:

| File | Purpose |
| --- | --- |
| `fpn_c_e10_station.py` | Camera preview, enrollment, photo library, and verification |
| `fpn_c_e10_shadow.py` | CPU preflight and offline single-query scoring |
| `frozen_fpn_c_e10.py` | Native FPN cropper and C E10 feature encoder |
| `fpn-c-e10.manifest.example.json` | Example input manifest; fill it outside this repository |
| `verify_fpn_c_e10_station.py` | Synthetic-camera test of enrollment and verification |
| `verify_fpn_c_e10_native.py` | Synthetic-input test of the native model architecture |

Shared camera, enrollment, and page modules retain their project filenames so the current station can reuse them. They are not separate supported deployments. The FPN station uses its native model, not the removed PKLNet checkpoint or ONNX exports.

From this directory, in an environment with the documented dependencies:

```sh
python verify_best_frame.py
python verify_review.py
python verify_ranked_window.py
python verify_adapter.py
python verify_render.py
python verify_fpn_c_e10_shadow.py
python verify_fpn_c_e10_native.py
python verify_fpn_c_e10_station.py
```

The tests do not exercise a physical camera, Pi latency, or recognition accuracy. Keep the runtime and model files outside this repository. The default match threshold is only a demo setting, not a calibrated acceptance threshold.
