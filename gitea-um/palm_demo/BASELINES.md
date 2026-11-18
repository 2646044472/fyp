# Edge Palm Baseline Register

This register distinguishes a runnable engineering baseline from research comparisons. None of these choices makes a Raspberry Pi deployment a research contribution by itself.

| Priority | Baseline | Current role | Why it is useful | Deployment status | Do not claim |
| --- | --- | --- | --- | --- | --- |
| 0 | Fast-CC, Li-ChengYan Python implementation | Default Pi demo matcher | MIT code; two Gabor directions plus shifted Hamming distance; no model checkpoint/GPU dependency | **Runnable now** through `install_pi.sh`, pinned to `d556f455a6cbdcb4264ec1cd75de2e451cf241b3` | Its PolyU benchmark score is not a Pi-camera score, and it has no liveness/PAD property. |
| 1 | PPNet | Later offline comparison | Published contactless-palm CNN, includes a Pi 4B setup note and pretrained-model links | **Hold**: old Python 3.7-3.8 and PyTorch 1.2-1.7 stack; model hash and Pi 5 execution must be independently verified | “Lightweight” or a Pi guide means it is ready for current Pi OS, or it establishes performance on our camera. |
| 2 | X-Palm scripts: CompNet/CCNet/PPNet etc. | Research-protocol baseline | Public benchmark scripts cover device/domain splits and multiple model families | **Later**: academic EULA and data approval first; training document uses RTX A6000 | The script package provides a Pi model or an authorised dataset download. |
| Reference | Palm-ID | Pipeline/upper-bound reference | End-to-end mobile pipeline and compact template research | **Not a deployment dependency**: no verified public Pi artefact; reported timing includes AMD EPYC server search | Its reported 18 ms template extraction is Pi timing or proof of anti-spoofing. |

## Promotion rule

A baseline may move from `Hold` to runtime only after it has a lawful model/data source, a frozen commit and model hash, repeatable ARM64 installation, deterministic image test, and recorded Pi 5 capture-to-decision latency/RSS/temperature. Run it alongside Fast-CC, not in place of it, so a model/runtime failure remains diagnosable.

## Sources

- Fast-CC reimplementation and MIT licence: https://github.com/Li-ChengYan/palmprint-recognition-python
- PPNet code, licence and Pi guide: https://github.com/xuliangcs/ppnet
- X-Palm scripts/data access: https://github.com/X-Palm/X-Palm-2026
- Palm-ID paper: https://arxiv.org/abs/2401.08111
