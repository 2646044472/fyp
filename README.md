# FYP: Contactless palmprint recognition

This repository contains the trainable FPN palm localizer, the C E10 recognizer, a PalmBridge comparison model, and the Raspberry Pi capture station. You can develop and test all three model paths on a Linux CPU without a camera, pretrained weights, or palm images.

## Start on a new computer

Use **Python 3.12 on Linux x86-64** for the tested development path. Install Git, Python venv support, and Node.js (the station UI test calls the `node` executable). On Windows, use a Linux distribution under WSL2 for this workflow; native Windows, WSL camera forwarding and Pi deployment were not tested. Run these commands from a shell:

```sh
git clone https://github.com/2646044472/fyp.git
cd fyp
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -r code/requirements-test.txt
python -m pip install --index-url https://download.pytorch.org/whl/cpu torch==2.8.0 torchvision==0.23.0
python -m pip install -r code/training/requirements.txt
python tools/check_recovery.py all
```

The last command runs the exact model architectures on random inputs, takes real optimizer steps on synthetic examples, exports both current station model formats and loads them through the station's strict preflight. It also checks evaluation accounting and exercises the station's HTTP enrollment flow with generated frames and substitute models. Allow room in your temporary directory for all three model exports. No training data, camera, or GPU is needed. A pass is a software recovery check, not an accuracy or Pi speed result.

For a quicker check without PyTorch, install **only** `code/requirements-test.txt` and run `python tools/check_recovery.py core`. Two tests need no packages at all: `python code/evaluation/paired_outcomes.py --self-test` and `python code/experiments/coverage_policy.py`.

## Where to work

| Task | Entry point |
| --- | --- |
| Train the FPN cropper, C recognizer or PalmBridge comparison; supply authorized local training inputs | [Training guide](code/training/README.md) |
| Change the station model definitions or the pixel-to-feature path | [Native FPN and C definitions](code/rasp/frozen_fpn_c_e10.py) |
| Load a trusted release and score a query against five enrollment photos of one palm | [Offline inference](code/rasp/fpn-c-e10-shadow.md) |
| Develop the capture, enrollment and review UI, or connect a physical camera | [Station guide](code/rasp/fpn-c-e10-station.md) |
| Rank pre-extracted local embeddings on a declared gallery and query set (aggregates only) | [Rank-1 scoring and coverage](code/evaluation/rank-features.md) |
| Compare outcomes on a fixed query list, counting missing attempts | [Evaluation tools](code/evaluation/README.md) |
| Work on the older residual encoder, geometry experiments or protocol helpers | [Earlier experiments](code/experiments/README.md) |
| Find the data providers and check gallery/query roles and reporting denominators | [Dataset catalog](dataset/README.md) |
| Review historical graded reports | [School Gitea sync tree](gitea-um/README.md); preserved on `main`, not a deployment target |

## If the original workstation is lost

**Git restores source and synthetic development.** To run the historically trained station, separately restore the approved FPN and C E10 safetensors files **and their independently trusted SHA-256 values** from authorized storage. On that machine, follow the [manifest and preflight procedure](code/rasp/fpn-c-e10-shadow.md). Files newly trained from random initialization are compatible development artifacts, not replacements for either trusted release.

Historical experiment reproduction also needs legally accessible data, the original enrollment/query and training splits, preprocessing/admission records, initialization assets and exact run state. The [recovery checklist](docs/development/recovery.md) distinguishes these from source recovery. Git is not a backup of them. Do not move materials off-device unless their terms and project authorization permit it.

Read [AGENTS.md](AGENTS.md) before staging changes. Keep originals, cropped palms, identifiers, per-query results, templates, embeddings, model weights and runtime directories out of Git. Do not restructure the graded school tree or sync it to school Gitea as part of developer maintenance. The [historical revision](https://github.com/2646044472/fyp/tree/dbe26352633e58769a1adeb12009c19eeb3df12a) is for reference; no older model package is needed for the current station.
