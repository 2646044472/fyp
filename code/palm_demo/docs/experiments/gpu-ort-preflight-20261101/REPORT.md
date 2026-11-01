# GPU ONNX Runtime preparation — 2026-11-01

Status: blocked during pip bootstrapping. No model session, image inference,
CPU/GPU paired query, latency experiment, full168 run, or public evaluation was
started. These artifacts do not establish an accuracy improvement or GPU speedup.

## Observed local capabilities

The new local execution context read the repository and source successfully.
Its branch initially matched `experiment/smpd-roi-20261030`, commit
`c4469b1af4f521a8e9cc98dd56b1d7275aa85191`.
No applicable ancestor `AGENTS.md` or `.agents/skills` was found.

| UTC observation | Result |
| --- | --- |
| 14:36:14 and 14:37:27 | `Get-Process` found no python/pythonw processes, with no query errors |
| 14:39:09 | No python/pythonw processes before environment preparation |
| 14:36:56 | 31.55 GiB total RAM; 12.83 GiB available |
| 14:41:02 | 13.47 GiB available; CUDA Driver API calls succeeded |
| 14:49:28 | 13.75 GiB available; diagnostic RSS 26.09 MiB |

CUDA Driver API identified device ordinal 0 as RTX 4070 SUPER, PCI bus
`0000:04:00.0`, compute capability 8.9, driver API version 13030 (CUDA 13.3).
This proves device discovery, not model execution. CIM and nvidia-smi were not
retried in this task. Earlier successful nvidia-smi measurements belong to the
original task and are not new resource measurements here.

The existing CPU environment remains at `runtime/pi5-under2-20261028/export-env`:
Python 3.13.9, ORT 1.31.1 with Azure/CPU providers, Torch 2.15.0+cpu,
NumPy 2.3.5, SciPy 1.16.3 and Pillow 12.0.0. Its OpenCV reports 5.0.0.
It inherits system site packages. No installation command targeted it.
A local fingerprint is retained under the new runtime preparation directory.

The ordinary profile startup emitted a Conda `StandardOutputEncoding` error.
No-profile calls succeeded. This does not establish the cause of the older
bridge's separate CIM access failure. Ripgrep was unavailable in that clean
shell's PATH; repository searches used `git grep`.

## Exact blocked action

The new project environment is `runtime/gpu-ort-20261101-r1/venv`.
Its `pyvenv.cfg` confirms `include-system-site-packages = false` and Python
3.13.9. Creation reached the pip bootstrap stage, then failed. A diagnostic
ensurepip invocation exposed:

```text
PermissionError: [Errno 13] Permission denied:
<sandbox-package>/AC/Temp/<temporary-directory>/pip-25.2-py3-none-any.whl
```

Temporary-directory cleanup also returned `PermissionError: [WinError 5]`.
The failure occurred while copying the bundled pip wheel, before pip ran.
Pip was absent when the partially created environment was inspected.
No alternative temporary directory, pip bootstrap route, elevated installation,
permission repair, profile change, or security setting change was attempted
after the explicit denial. The sandbox temporary directory was not inspected
or cleaned manually. Its cleanup outcome remains uncertain.

This is a local runtime filesystem denial, not an automatic approval-review
rejection. Ordinary metadata networking separately failed DNS resolution;
approved metadata-only reads of official PyPI subsequently succeeded. Those
reads did not install or download package wheels.

## Reviewed dependency plan

The planned GPU ORT version is 1.31.1, matching the existing CPU ORT version.
Official PyPI supplies a CPython 3.13 Windows x64 wheel and CUDA/cuDNN extras.
Newer GPU distributions use CUDA 13; see the
[ORT CUDA requirements and preload API](https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html#requirements)
and [ORT 1.31.1 package files](https://pypi.org/project/onnxruntime-gpu/1.31.1/#files).

The latest cuBLAS release lacked a Windows wheel, so unconstrained latest
selection was rejected. The final NVIDIA pins follow the
[CUDA 13.0 Update 2 component table](https://docs.nvidia.com/cuda/archive/13.0.2/cuda-toolkit-release-notes/index.html#cuda-toolkit-major-components):
runtime 13.0.96, NVRTC/nvJitLink 13.0.88, cuBLAS 13.1.0.3,
cuFFT 12.0.0.61, cuRAND 10.4.0.35. cuDNN is 9.13.1.26;
the [cuDNN 9.13.1 support matrix](https://docs.nvidia.com/deeplearning/cudnn/backend/v9.13.1/reference/support-matrix.html)
documents CUDA 13.0 and Ada/compute capability 8.9.

`metadata-cuda13u2/requirements-gpu-planned.lock` pins all 16 packages and hashes.
`dependency-plan.json` records official wheel URLs, metadata constraints and
compatible interpreter tags. Runtime dependencies are metadata-consistent;
installation, DLL loading, MSVC runtime compatibility and inference remain
unverified. Metadata compatibility alone is not an operational qualification.
No Torch installation is included: the intended ONNX path does not need it.

## Frozen next verification

The private `runtime/gpu-ort-20261101-r1/paired-panel.json` reuses the previously
authorized D1–D4 device bindings: two remaining wrong-identity cases, one correct
terminal control and one fast correct control. All share the complete frozen
11-identity gallery and five enrollment frames per identity. No public queries,
replacement samples, failed rotation repair, or common-pose candidate is enabled.
Private paths, identities and original images are excluded from this report.

Predeclared numerical tolerances are localizer outputs `atol=1e-4, rtol=1e-5`,
embeddings `atol=1e-5, rtol=1e-4`, identity scores `atol=1e-7, rtol=1e-6`.
ROI pixel hashes, identity sets, HTTP status, decision, outcome and recognition
route must match exactly. A change stops expansion for diagnosis; it cannot be
called an accuracy improvement. Nonfinite values and output-shape differences
also fail validation. These gates have only been exercised on synthetic data.

The planned CUDA configuration fixes device 0, disables TF32, uses heuristic
cuDNN selection, caps the EP arena at 4 GiB and disables maximum convolution
workspace. Actual profiling must demonstrate executed CUDA Conv/MatMul/Gemm
nodes and enumerate CPU fallback; advertised providers alone cannot pass.
Heavy-op CPU fallback is a stop condition.

Resource gates remain startup available RAM >=12 GiB, running available RAM
>=2 GiB and worker RSS <14 GiB. Recheck no competing worker and startup RAM
before any future run. Never loosen the gate or terminate another application.

Future timing must separately record process startup, session creation, first
inference, warmup, transfers, bound inference, matching and full HTTP query wall
time, with RAM/VRAM telemetry. Transfer microbenchmarks are separate measurements;
they must not be added or subtracted to manufacture full-query time. Cache keys
must include backend, dependency/model hashes, ORT and CUDA options.

## Validation and remaining work

`tools/gpu_ort_preflight.py` is an offline planning/comparison helper, not a
model runner or environment installer. Five tests pass: frozen resource limits,
executed GPU-compute evidence versus provider/copy events, numeric/nonfinite/
shape drift, identity/ROI changes despite close scores, and dependency conflict
rejection. No synthetic test establishes real-model parity.

The requested installation and paired validation remain blocked. The exact
denied ensurepip operation must not be retried or rerouted without materially
new evidence addressing that denial. Once permitted, installation and DLL
qualification must succeed before implementing/running the supervised query
runner. No model experiment, Pi measurement, promotion or deployment is claimed.
