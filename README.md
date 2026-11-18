# FYP: Palmprint recognition

This project studies how to locate a palm in a camera frame and recognize the correct enrolled hand without mistaking an unusable image for a successful match.

| Start here | Contents |
| --- | --- |
| [code/](code/README.md) | Raspberry Pi application, offline ROI and evaluation utilities, PKLNet integration and experiment-dependency checks. |
| [gitea-um/](gitea-um/README.md) | School-facing project handoff: meeting minutes, dated progress reports, dataset comparisons and runnable research examples. |

For the offline research, read [Progress Reports](gitea-um/minutes_note/progress/README.md), then run the [synthetic training and geometry checks](gitea-um/research_code/README.md). For the device application, start with the [Pi demo guide](code/palm_demo/README.md). The offline experiments are not a new Pi hardware acceptance test.

Historical root-level notes and retired workflows were separated from active code. This layout change does not alter Git history or certify earlier commits as free of private data. Follow the [project data-handling rules](AGENTS.md); do not stage local captures, templates, caches, unverified weights or workstation-specific outputs.
