# FYP: Palmprint recognition

Can a camera recognize the same hand after its distance, pose or device changes, and can it decline a match when it should? This project separates finding a usable palm crop, ranking enrolled hands and accepting or rejecting the proposed match.

| If you want to… | Start here |
| --- | --- |
| Prepare a project update | [School handoff](gitea-um/README.md) for the dated meeting record; [progress notes](gitea-um/minutes_note/progess%20notes/README.md) for experiments completed after those meetings. |
| Check the evidence for a result | [17-table benchmark](gitea-um/minutes_note/progess%20notes/2026-11-18-experimental-results.md) for datasets and denominators; [crop fallback and augmentation](gitea-um/minutes_note/progess%20notes/2026-11-18-crop-routing-and-training.md) for paired comparisons and acceptance decisions. |
| Run an example without a device or biometric data | [Research code](gitea-um/research_code/README.md) for the crop, trainer and decision-accounting examples. |
| Work on the Raspberry Pi prototype | [Code map](code/README.md) → [camera app](code/palm_demo/README.md) → [setup and hardware precautions](code/palm_demo/docs/SETUP.md). |

**Try one decision from the report.** With stock Python 3.10+ at the repository root:

```sh
python gitea-um/research_code/coverage_policy.py
```

The example scores four invented attempts. Look for `rank1_correct: 2` but only one correct acceptance: the other correct match fell below the cutoff. No model, dataset, camera or network is needed. It illustrates the counting rule rather than reproducing the measured scores.

**Which copy should change?** `code/` holds the device application and offline diagnostics. `gitea-um/` preserves a school snapshot plus separately identified research examples and reports; its demo is not a second deployment target. Offline recognition gains are not a new Pi hardware acceptance test.

**Sharing.** The school folder is a reading guide, not an access boundary. For a handoff, select reviewed reports and source files; do not distribute the entire repository, its history or a workstation archive as a substitute. See [project data-handling rules](AGENTS.md) before adding captures, templates, logs, weights or results. Historical root-level notes and retired workflows were separated from the active tree; rearranging files does not change Git history.
