---
topic: nonreference-systems-lifecycle
created: 2026-08-31
last_verified: 2026-08-31
status: superseded
depth: deep
related:
  - ebr-i2c-action-boundary
  - edge-provenance-outage
sources:
  - url: https://datatracker.ietf.org/doc/html/rfc9019
    fetched: 2026-08-31
  - url: https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/system/ota.html
    fetched: 2026-08-31
  - url: https://arxiv.org/abs/2405.12089
    fetched: 2026-08-31
  - url: https://doi.org/10.1007/s10836-025-06170-w
    fetched: 2026-08-31
  - url: https://doi.org/10.5194/jsss-13-71-2024
    fetched: 2026-08-31
  - url: https://doi.org/10.1007/s10207-024-00825-z
    fetched: 2026-08-31
---

# Non-reference edge systems and lifecycle

## Summary

This round searched firmware recovery, deterministic-computation integrity, record-transition provenance, media retirement and offline ownership transfer. No primary FYP direction survived. RWE is superseded because established secure-update machinery already implements the benign interrupted-update decision. SDC-X remains useful only as a labelled, finite fault-injection/negative benchmark because heterogeneous re-execution is an established redundancy mechanism and two outputs do not identify general correctness.

## Findings

### RWE is superseded [KILL]

RFC 9019 specifies manifest verification, boot status and recovery requirements. ESP-IDF's documented OTA state machine provides persistent update state, first-boot self-test confirmation, rollback after unexpected reset and anti-rollback. Under RWE's explicitly benign interrupted-update model, an external reader hashes the same immutable image/manifest state and adds no decision-relevant information. If it instead detects a compromised self-report or future mutable application behavior, the threat/observation model has changed and the reader still cannot certify the later behavior.

### SDC-X is a benchmark pivot, not a method [PIVOT]

Formal and real-hardware work already use golden/faulty duplication, comparison and injected faults to classify SDC, crash and hang. A board mismatch provides detection of a registered one-replica fault but not its correction; a match is only meaningful under a justified independence assumption. Shared valid-but-wrong inputs, specification/compiler/library defects and post-comparison corruption remain. Thus a low-cost Pi/Pico study can publish a scoped injection/conformance map, but cannot claim a novel redundancy policy, board-level SDC prevalence or general correctness.

### Lifecycle controls are occupied [KILL]

Digital calibration certificates cover signed transition/procedure/reference metadata, while metadata alone cannot prove numerical comparability after a physical sensor/configuration change. Existing IoT decommissioning and media-sanitization guidance cover ordinary retirement mechanisms; host-visible deletion cannot prove controller-level erasure. AutoPKI covers signed ownership/trust transfer, and an offline device without trusted freshness evidence must report that freshness is unavailable rather than infer it from a signed replayable blob.

## Insights

- A second reader does not create a new information source when secure boot already verifies the identical immutable state under the same fault model.
- Diversity is an assumption that must be measured or justified, not an outcome of using two inexpensive boards.
- Lifecycle provenance can authenticate a declared transition without identifying its physical measurement consequences.

## Strongest objection

A named hardware platform with a separately trusted mutable-state sensor could create a different RWE observation model, and a fault model with physically justified independent channels could make a diversity study informative. Neither is currently specified or supported by a low-cost, one-year FYP data plan; neither result would revive the generic candidates without a fresh exact-claim audit.

## Discarded approaches

| Approach | Why dropped | Date |
|---|---|---|
| RWE external update-state reader | Secure update, self-test and rollback already implement the benign recovery decision; reader repeats immutable state | 2026-08-31 |
| SDC-X heterogeneous recomputation method | DMR/N-version and injection/golden apparatus are established; common-mode correctness remains unidentifiable | 2026-08-31 |
| DCC-SPLIT transition provenance | DCC records metadata, not numerical comparability | 2026-08-31 |
| REUSE-WIPE host-side retirement | Sanitization scope and decommissioning are established; host view cannot prove controller erasure | 2026-08-31 |
| OFT offline ownership transfer | Standard signed transfer exists; freshness without a trusted witness remains unavailable | 2026-08-31 |

## Open questions

- Is there a low-cost edge problem outside sensing and lifecycle where an allowed action creates a genuinely independent observable and a non-routine endpoint?
- Could LENS-RC's narrow camera-path witness preflight produce a physical condition map worth a separate exact-claim audit? It is not assumed to do so.

## Timeline

- 2026-08-31 - divergence generated RWE, SDC-X and three lifecycle controls.
- 2026-08-31 - independent validation killed RWE and all lifecycle controls, and demoted SDC-X to a finite labelled negative benchmark.
