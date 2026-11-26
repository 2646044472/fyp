# Replacing the development workstation

Use the [root quickstart](../../README.md) first. The commands there test the **Linux x86-64 CPU path**, not a GPU environment or a Raspberry Pi.

| Goal | What Git supplies | What must be supplied separately |
| --- | --- | --- |
| Edit code and check a change | Current model definitions, training entry points, synthetic tests and station checks | Python environment and package installation; no project data |
| Start a new authorized training run | Local-input contracts, portable training objectives and weight export | Approved training-only inputs constructed to the documented contract. Restore the intended initialization if the run depends on it. |
| Run the historic station | Strict CPU loaders, manifest schema, preprocessing, model inference and station source | The two exact authorized releases and trusted provenance/hashes, plus physical camera/runtime for live use |
| Reproduce a historical metric | Split/evaluation descriptions, aggregate ranking of pre-extracted features, and paired-outcome accounting | Authorized originals or supplied ROIs, private split/admission decisions and experiment code/configuration for that exact benchmark. Ranking existing features or counting two outcome tables does not recreate a benchmark from images. |
| Continue at an exact optimizer step | Portable model source | A compatible full training-state snapshot including optimizer/scheduler, RNG, sampler and epoch/step, and exactly the same inputs. A safetensors model export alone cannot do this. |

## Recovery drill

1. On a clean replacement machine, install the CPU environment. Run `python tools/check_recovery.py all`. Run a single suite (`core`, `native`, or `training`) to isolate a failure.
2. For trained inference, restore the correct models from approved storage into a private directory outside Git. Restore trusted hashes from an independent source, not from the files being checked. Fill in a local copy of the [example manifest](../../code/rasp/fpn-c-e10.manifest.example.json). From the repository root:
   ```sh
   python code/rasp/fpn_c_e10_shadow.py --manifest /PATH/TO/PRIVATE/manifest.json preflight
   ```
   The preflight deliberately rejects mismatched files. A locally calculated hash in a synthetic test checks the file format, not the identity of a historical release. Do not relabel a retrained model as the released C E10 model.
3. For further training, follow the [current training guide](../../code/training/README.md); use a new private output file for each export. A warm start creates a new optimizer trajectory. For a historical comparison, recover an approved split and freeze it before training. A successful smoke does not establish recognition accuracy.
4. For live use, follow the [station guide](../../code/rasp/fpn-c-e10-station.md): start with a private mode-0700 runtime and the correct UVC or CSI backend. Verify `/station-health`, acquire a **fresh** frame, and measure end-to-end latency and memory on the actual device. Do not treat the demo threshold as calibrated for access control.

## What to verify before relying on a backup

The custodian should check whether a separate approved copy exists for each required item, whether it may be stored there, who is allowed to restore it, and how its identity can be verified. Keep that inventory, credentials and paths **outside this repository**. No private backup is created or verified by the synthetic drill. If a release or split existed only on the lost computer, use the code to start a new run and report it as new.

When comparing query outcomes, do not drop failed crops or missing enrollment from the planned denominator. Keep individual rows local and publish only approved aggregates. See the [evaluation notes](../../code/evaluation/README.md) and [dataset catalog](../../dataset/README.md).
