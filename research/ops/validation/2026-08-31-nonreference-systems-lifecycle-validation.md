# Validation Audit: 2026-08-31 non-reference edge systems, lifecycle, and integrity

## Decision investigated

Can `RWE` (a separately powered reader of update-state bytes) or `SDC-X`
(heterogeneous local recomputation before retaining a deterministic result)
become a defensible low-cost edge FYP? This audit also checks `DCC-SPLIT`,
`REUSE-WIPE`, and `OFT` as controls. It does not revive C3, S1/S2/R1, SAP,
generic I2C recovery, or reference-action sensing.

## Claim under test

`RWE` observes device update/verified-boot status `O_d` plus an independent
reader hash of named boot/update bytes `O_e`, then chooses
`release / recover / unknown` after a benign interrupted signed update. The
claim is lower false release at equal technician time than self-report,
verified boot, and always reflash.

`SDC-X` has a main-board result `y_P`, a companion-board result `y_Q`, and an
input digest. Under a seeded post-input/pre-output corruption model, it chooses
`retain / recompute / unknown`. The claim is a better false-accept versus
energy/latency frontier than retry, checksum, and always-unknown.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| RWE component collision | RFC 9019 specifies firmware-manifest verification, boot-status exposure, and recovery; ESP-IDF implements persistent OTA state, self-test, rollback and anti-rollback. | A physical reader is a distinct trust anchor only if the device is adversarial or its read path is untrusted. | High |
| RWE exact-claim collision | The standard `NEW/PENDING_VERIFY/VALID/INVALID/ABORTED` state machine classifies the planted interrupted-update branches before application release. | [GAP] No paper exactly testing a cheap reader as a technician policy was found; this is not novelty evidence. | High for ordinary mechanism |
| RWE boundary | A verified image and manifest are compatible with a later mutable config/application fault. If the reader checks identical immutable bytes, it adds no information under the benign model. | A compromise-threat model would differ, but that is not this candidate. | High |
| SDC-X component collision | Xue and Zwolinski duplicate a golden/faulty core and compare outputs; Magliano et al. run reproducible golden-versus-faulty real-hardware campaigns; N-version execution is established. | A Pi/Pico three-action loss frontier is not their exact endpoint. | High component collision |
| SDC-X exact-claim collision | Conditional duplicate execution and comparison, plus retry/checksum baselines, is DMR/N-version fault detection. Picking a companion MCU does not change that mechanism. | [GAP] No inspected paper reports exactly this board pair and action frontier. | High as application variation |
| SDC-X boundary | With disagreement, two outputs do not identify the correct one. With agreement, correctness holds only under an independence model; shared valid-but-wrong input, specification defect, or post-comparison corruption survives. | A third trusted oracle, formal proof, or a physically justified fault channel would change the candidate. | High |

## Assumption and identification audit

### RWE

- [KILL] RFC 9019's verifier measures image/manifest and boot state, not all
  future application behavior. ESP-IDF has an immediately applicable
  rollback/self-test implementation for the benign interruption case.
- [KILL] In the candidate's non-adversarial lattice, secure boot is assumed to
  execute honestly. An external hash of the same immutable bytes is redundant.
  Treating a self-report as malicious changes to a security/compromise model.
- [KILL] Reading additional mutable state does not validate the claimed update
  endpoint and needs a separate golden-state/access-control model.

### SDC-X

- [KILL] The seeded fault is declared to alter `P` after input validation but
  not `Q`, the comparator, or the offline oracle. A result that `Q` detects it
  therefore follows from a deliberately single-replica fault model; it does
  not establish the decision value of board heterogeneity in deployment.
- [KILL] An input digest proves byte identity, not input semantics or algorithm
  correctness. Common input/specification/compiler/library faults remain.
- [KILL] `y_P != y_Q` cannot label one value correct; `y_P == y_Q` is not a
  correctness certificate without a stated independence assumption.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| RFC 9019 (2021) | Image/manifest verification, status, backup/recovery image. | Standard secure firmware update/recovery architecture. | RWE signed manifest, interrupted update, recover branch. | Kills the ordinary update-state mechanism; only a changed compromise threat model remains. |
| ESP-IDF OTA documentation | OTA state, self-test, rollback, anti-rollback. | Cheap ESP32 implementation. | Direct `release/recover` precondition after power interruption. | Kills a claim that external readout is required for standard partial-update classification. |
| Xue et al., TDSC 2025 | Bare-metal DFU authentication, acquisition, verification. | 1,637 companion apps and commercial systems. | DFU/lifecycle trust family. | Strong collision lead; full body unavailable, so not used for a more precise RWE claim. |
| Xue and Zwolinski, 2024 | Fault injection/model checking; duplicate golden/faulty core. | SDC/crash/hang in Ibex. | SDC-X's golden comparison and declared fault model. | Kills duplicate comparison as a new mechanism; leaves only a scoped diversity study. |
| Magliano et al., JET 2025 | Separate host/target, controlled injection, golden/faulty classification. | Real hardware/FreeRTOS fault-injection campaigns. | SDC-X seeded corruption/gold-oracle apparatus. | Kills generic injection-plus-comparison FYP. |
| Ron et al., arXiv 2024 | Functionally equivalent but diverse N-version variants. | Real miscompilation-bug experiments. | Diversity premise. | Diversity must be measured/argued, not inferred from two boards. |
| Mustapaa et al., JSSS 2024 | Signed calibration/procedure/reference metadata. | DCC exchange, including offline/asynchronous settings. | DCC-SPLIT provenance record. | Kills generic signed transition metadata. |
| Mangar et al., IOT 2025; NIST SP 800-88r2 | Device decommissioning; scope-bounded sanitization. | IoT-class validation and official media guidance. | REUSE-WIPE. | Kills a host-side wipe/decommission method; leaves a negative claim-scope matrix. |
| Hommel et al., AutoPKI 2024 | Signed IoT trust-transfer/certificates/optional attestation. | Automated ownership/trust transfer. | OFT local transfer state machine. | Kills an ordinary blob/QR transfer protocol; without freshness witness, output is `unknown`. |

## Strongest simple baseline

For `RWE`, enable standard secure boot, signed image verification, persistent
OTA state, first-boot self-test, rollback and anti-rollback; release only after
the stock confirmation. Under its benign fault model this reads the relevant
state without another board.

For `SDC-X`, execute twice and compare exact outputs; on mismatch choose
`unknown` or use a third independently implemented offline gold computation.
This is standard DMR with re-execution. A checksum is a necessary data-path
control but not a semantic-correctness certificate.

## Contrarian result

`RWE` is **KILL**. It adds a reader beside a secure-update state machine that
already defines manifest verification, recovery, rollback and confirmation.
Its apparent residual needs a new compromised-device threat model or a mutable
runtime observation, neither of which is the stated candidate.

`SDC-X` is **PIVOT / not promotable**. It can be an honest educational
fault-injection benchmark, but a positive result would be conditional on a
hand-selected single-board fault distribution plus standard DMR comparison.
No source establishes a relevant field SDC rate on Pi/Pico-class boards, and
the mechanism cannot certify against the common-mode cases it excludes.

`DCC-SPLIT`, `REUSE-WIPE`, and `OFT` are **KILL** as primary directions:
their ordinary mechanisms are already standardized/directly studied, and their
residuals are reporting boundaries rather than FYP mechanisms.

## Feasibility audit

| Candidate | Minimum apparatus | Result |
| --- | --- | --- |
| RWE | ESP32, dual OTA partitions, signed harmless images, deterministic interruption, external reader. | [KILL] Cheap, but flash-encryption/secure-boot choices make external bytes either uninterpretable or redundant. Stock rollback/full reflash are simpler valid controls. |
| SDC-X | Two boards, pinned implementations, offline gold, hidden injection schedule, energy/timing logger. | [PIVOT] Computation is feasible; a consumer USB meter may not resolve short per-score energy. Software seeding does not establish field relevance or independence. |
| DCC-SPLIT | Two sensor boards, configuration transitions, signed metadata, independent overlap truth. | [KILL] Provenance is easy; numeric continuity requires the excluded external calibration resource. |
| REUSE-WIPE | Removable medium, synthetic encrypted files, independent reader. | [KILL] Feasible only as a negative scope matrix, not a general physical-erasure result. |
| OFT | Two nodes and test certificates. | [KILL] Demo is feasible; freshness without trusted time/counter is not locally decidable. |

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Firmware verifier checks image/manifest, must expose boot status, and needs alternate-image/new-image recovery. | [K] | Moran et al., *A Firmware Update Architecture for Internet of Things*, RFC 9019, 2021-04. https://datatracker.ietf.org/doc/html/rfc9019 | Sec. 4 paras. 313-338; Sec. 4.1 paras. 320-346. | Official standard; covers the ordinary RWE state machine. |
| ESP32 OTA provides state, self-test confirmation, rollback after unconfirmed boot/power loss, and anti-rollback. | [K] | Espressif, *Over The Air Updates (OTA) - ESP32*, official ESP-IDF docs, accessed 2026-08-31. https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/system/ota.html | `Rollback Process`, lines 60-123; `Unexpected Reset`, 93-99; `Anti-rollback`, 124-146. | Board/framework-specific but directly matches RWE's cheap target. |
| Recent bare-metal DFU work finds flaws across authentication, acquisition and verification. | [K] | Xue et al., *Update If You Dare*, IEEE TDSC 22(3), 2025, pp. 2367-2384. https://research.polyu.edu.hk/en/publications/update-if-you-dare-demystifying-bare-metal-device-firmware-update/ | Official abstract/bibliographic record; full pages unavailable. | Collision lead only. |
| Formal SDC work duplicates a golden/faulty core with same input, compares signals, and excludes data/instruction memory faults by assumption. | [K] | Xue and Zwolinski, *Using Formal Verification to Evaluate Single Event Upsets in a RISC-V Core*, arXiv:2405.12089v1, 2024-05-20. https://arxiv.org/abs/2405.12089 | Sec. I pp. 1-2; Sec. II-B pp. 3-4; Sec. V-A pp. 8-10; Sec. VII-A pp. 15-17; Sec. VIII pp. 22-23. | Ibex/RTL, not consumer-board field frequency. |
| Real-time embedded fault injection can run on real FreeRTOS hardware and compare faulty execution with golden output to classify SDC. | [K] | Magliano et al., *Real-time Embedded System Fault Injector Framework for Micro-architectural State Based Reliability Assessment*, *Journal of Electronic Testing* 41, 193-208, 2025. https://doi.org/10.1007/s10836-025-06170-w | Sec. 2, HTML paras. 94-121; Sec. 3.2, 152-190; Sec. 4, 260-275. | Strong apparatus/endpoint neighbor, different target board. |
| N-version variants can be formally equivalent and runtime-diverse. | [K] | Ron et al., *Galapagos*, arXiv:2408.09536v1, 2024-08-18. https://arxiv.org/abs/2408.09536 | Abstract. | Preprint; supports only the need to establish diversity. |
| DCC metadata, decommissioning, sanitization and automated trust transfer have direct primary/official neighbors. | [K] | Mustapaa et al. 2024, https://doi.org/10.5194/jsss-13-71-2024; Mangar et al. 2025, https://doi.org/10.1145/3770501.3770522; NIST SP 800-88r2, https://doi.org/10.6028/NIST.SP.800-88r2; Hommel et al. 2024, https://doi.org/10.1007/s10207-024-00825-z | Mustapaa Secs. 1-3.4; Mangar Abstract/Secs. 1-3; NIST record; AutoPKI Secs. 7.4, 8.1-8.4, 11.3-11.4. | Controls only; controller behavior and board freshness capabilities remain [GAP]. |
| Two output values alone cannot identify which disagreement is correct; agreement is conditional on fault independence. | [K] | Logical consequence of the stated two-observer model, bounded by the above fault models. | Assumption audit above. | Not presented as a universal external impossibility theorem. |

## Queries and failed searches

- `2024 2025 embedded firmware update power interruption recovery verified boot manifest external programmer attestation paper`
- `2024 2025 heterogeneous redundant execution silent data corruption embedded systems fault injection paper`
- `diverse double execution silent data corruption embedded fault tolerance paper`
- `site:docs.espressif.com OTA rollback secure boot ESP-IDF power failure official`
- `heterogeneous redundancy silent data corruption 2024 embedded`
- `diverse redundancy silent data corruption 2024 2025`
- `dual modular redundancy silent data corruption embedded 2025`
- `N-version programming silent data corruption embedded systems 2024`

The full BareDFU paper was unavailable. No 2024--2026 primary paper was found
that exactly tests a cheap read-only second board for benign update-release
decisions; this is [GAP], not an absence/novelty claim. No reliable consumer
Pi/Pico field-SDC rate was found. No source was found that lets two disagreeing
outputs identify the correct value without another oracle; that conclusion is
instead a limited inference from the candidate model.

## Decision

**KILL for RWE and this packet as a primary-direction source; PIVOT only for
SDC-X as a labelled fault-injection/negative benchmark.** Neither candidate
passes all three novelty rounds. `RWE` is covered by secure-update/rollback
machinery under its own benign assumptions. `SDC-X` needs a non-tautological
fault/independence model and a mechanism beyond DMR/N-version comparison
before another research gate.
