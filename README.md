# FYP: Contactless palmprint recognition

This developer repository contains the current FPN + C E10 station, evaluation utilities, the dataset catalog, and portable training and experiment code.

| Task | Start here |
| --- | --- |
| Develop or start the Raspberry Pi capture and verification station | [Current station](code/rasp/README.md) |
| Load the native models or score a single query without a camera | [FPN + C E10 inference](code/rasp/fpn-c-e10-shadow.md) |
| Compare outcomes on a fixed set of queries | [Evaluation tools](code/evaluation/README.md) |
| Find a dataset, its source, or the train/gallery/query protocol | [Dataset catalog](dataset/README.md) |
| Reproduce the portable training and experiment checks | [Training and experiments](code/experiments/README.md) |

Quick check without models, a camera, or a dataset:

```sh
python code/evaluation/paired_outcomes.py --self-test
python code/experiments/coverage_policy.py
```

Models and real captures stay on authorized devices. Passing the synthetic checks is not a Raspberry Pi hardware or recognition-accuracy result. See [repository data rules](AGENTS.md).

[Historical revision](https://github.com/2646044472/fyp/tree/dbe26352633e58769a1adeb12009c19eeb3df12a): school handoff, original benchmark write-ups, offline geometry audit, and the legacy station. Do not use the old stack or model files as dependencies for the current station.
