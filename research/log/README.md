# Research Logs

`log/` preserves the detailed reasoning behind the concise conclusions in [`../core/`](../core/README.md). Logs are append-oriented: record what was read or inspected, the exact evidence available, the inference made, and the inference that remains unsupported.

## Existing logs

| Log | Focus |
| --- | --- |
| [`12-pad-protocol-reading-log.md`](12-pad-protocol-reading-log.md) | PAD protocol, final release risk, and metrics |
| [`13-b0-reproducibility-log.md`](13-b0-reproducibility-log.md) | B0 baseline artifacts, datasets, and implementation path |
| [`14-formal-survey-reading-log.md`](14-formal-survey-reading-log.md) | Formal palmprint survey reading |
| [`15-vis-nir-boundary-log.md`](15-vis-nir-boundary-log.md) | VIS/NIR matching versus PAD boundary |
| [`16-dynamic-terms-boundary-log.md`](16-dynamic-terms-boundary-log.md) | Meaning of “dynamic” and “sequence” in cited work |
| [`17-active-illumination-neighbor-log.md`](17-active-illumination-neighbor-log.md) | Flash/non-flash fingerprint PAD as a bounded neighbor |
| [`18-maintenance-story-evidence-log.md`](18-maintenance-story-evidence-log.md) | Maintenance-workflow evidence and story limits |
| [`19-sensing-reproducibility-log.md`](19-sensing-reproducibility-log.md) | Smart palm sensing artifacts and hardware transfer limits |
| [`20-random-order-boundary-log.md`](20-random-order-boundary-log.md) | NIR/UV random-order prior art and novelty boundary |
| [`21-pvasd-reproducibility-log.md`](21-pvasd-reproducibility-log.md) | Palm-vein PAD data, code, and deployment limits |
| [`22-palmrss-reproducibility-log.md`](22-palmrss-reproducibility-log.md) | Cross-domain palmprint baseline artifact audit |
| [`23-attack-layer-and-loo-protocol-log.md`](23-attack-layer-and-loo-protocol-log.md) | Attack-layer separation and leave-one-group-out PAD protocol |

## When to write a log

Write or extend a log only for deep reading, a reproducibility or availability audit, an experimental-protocol decision, or a materially revised inference. Link its result back to the relevant core document. Do not put transient search-result lists or uncited assertions here; the log should make later review easier, not create a second unsourced knowledge base.
