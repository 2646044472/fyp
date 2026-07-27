# Edge AI Palmprint Recognition — FYP Exploration

> Status: exploratory; the final research question, dataset, baseline model,
> and target edge platform have not been selected.

## Direction

Explore how palmprint recognition models can be deployed and optimized on
smartphones, Jetson platforms, or Raspberry Pi-class devices.

## Motivation

- Reduce inference latency and network dependency.
- Improve privacy and suitability for real-time authentication.
- Study trade-offs among accuracy, memory, power, robustness, and device limits.

## Two-Week Outcomes

1. Literature and technology map.
2. Shortlist of suitable datasets and evaluation protocols.
3. One baseline palmprint recognition model.
4. One target deployment platform.
5. Preliminary bottlenecks and measurable research questions.

## Exploration Scope

- Palmprint recognition pipelines, datasets, and baseline models.
- ONNX, TensorFlow Lite, Core ML, and TensorRT deployment options.
- Quantization, pruning, and knowledge distillation.
- Accuracy, latency, memory, power, and model-size measurements.

## Getting Started

1. Read and update [the tracker](TRACKER.md).
2. Record sources and comparisons in [the literature notes](notes/literature.md).
3. Record decisions in [the meeting notes](notes/meetings.md).
4. Record reproducible trials in [the experiment log](notes/experiments.md).
5. Keep source code in `code/`; keep only data instructions and small
   manifests in `data/`.

## Repository Map

| Path | Purpose |
| --- | --- |
| `TRACKER.md` | Shared responsibilities, progress, and next actions |
| `notes/literature.md` | Papers, datasets, baselines, tools, and research ideas |
| `notes/meetings.md` | Meeting notes, decisions, and action items |
| `notes/experiments.md` | Experiment configurations, results, and conclusions |
| `code/` | Source code and data/deployment utilities |
| `data/` | Acquisition guidance, metadata, checksums, and small manifests |

## Collaboration

- Assign every active task to one owner.
- Update the tracker in the same commit as material research notes.
- Record decisions with rationale so they can be revisited.
- Commit small, reviewable changes with descriptive messages.

## Current Uncertainties

- Whether to prioritize recognition accuracy, deployment efficiency, security,
  or system design.
- Which dataset and evaluation protocol to use.
- Which edge platform is most relevant and feasible.
- Whether the lab has preferred models, datasets, or hardware.
- How to divide the exploration between teammates.

## Questions for Supervisor Discussion

1. Does this direction fit the expected FYP scope?
2. Which sub-area best aligns with the lab's current work?
3. Which lab datasets, models, repositories, or devices can the team reuse?
4. What deliverable is expected for the next meeting?
5. When should the exploration narrow into a formal research question?
