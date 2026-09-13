# Validation Audit: 2026-08-28 T1 edge timestamp-trust boundary

## Decision investigated

Whether T1 from `research/ops/divergence/2026-08-28-one-year-divergence.md` should survive as a one-year, low-cost edge sensing/reliability FYP direction: a local receiver uses `(sequence, reboot epoch, sender timestamp, clock-quality bound, arrival time)` to choose `accept / defer-resample / time-indeterminate`, and claims a finite false-fresh-accept versus defer boundary beyond ordinary timestamp and NTP baselines.

## Claim under test

The only admissible reading is the packet's finite, preregistered claim: on held-out combinations of sender, Wi-Fi delay/loss, reboot/clock reset, and sleep/wake, a three-action rule lowers *reference-labelled false-fresh accept* at no higher delay and defer rate than arrival-only, sender-timestamp-only, timestamp plus NTP offset, and `any gap => defer`.

This is not a new synchronization, provenance, checkpointing, or security claim. It is Amber until all three audits pass. The decisive question is whether the proposed `clock-quality bound` supplies any information or action not already present in a conventional epoch/sequence record plus a clock-error interval.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| Component collision | Siddiqi, Sivaraman and Jha already combine resource-constrained sensor timestamp trust, periodic delay-aware checks, per-synchronization epoch trust parameters, and special treatment of sensor reboot. NTP formally exposes offset, dispersion, jitter, and synchronization distance (a maximum error). | T1 omits cryptographic/adversarial objectives and calls its output an operational `accept/defer/indeterminate` choice. That is an application framing change, not yet a distinct mechanism. | High for component collision. |
| Exact-claim collision | Li and Zhang's OSDI 2024 work treats freshness as a timing constraint, instruments timestamp checks and mitigation in real CPS software, and evaluates end-to-end timing. Siddiqi et al. evaluate reliable sensor timestamps under variable latency and reboot epochs. Both materially overlap the observation and decision logic. | No source read here exactly reports T1's four named weak baselines, its particular finite Wi-Fi/reboot panel, and the exact false-fresh/defer ROC. That absence is [GAP], not evidence of novelty. | Medium: task endpoint differs, but the proposed information path does not. |
| Boundary / impossibility | With only `(q,e,s,u,r)`, two executions can have equal observations but acquisition times on opposite sides of the freshness deadline. Any policy must give them the same action. If `u` is a valid error bound, interval logic is the simple sufficient baseline; if it is not a valid bound, the claimed false-fresh cap is unidentifiable. | A finite bench can truthfully map which *instrumented* cells yield a usable interval. It cannot establish a general trust guarantee for unobserved clock drift, delay asymmetry, long outage, or reboot state. | High. |

## Assumption and identification audit

Let receiver time be `r`, sender-reported acquisition time be `s`, calibrated offset be `theta`, and a defensible all-in error bound be `epsilon` (clock, resynchronization, and the portion of delay assumptions needed to translate the timestamp). The receiver can only identify acquisition age as an interval:

`age in [r - (s + theta) - epsilon, r - (s + theta) + epsilon]`.

For freshness deadline `D`, the strongest ordinary non-learning policy is:

- `accept` only when the interval's upper end is `<= D`;
- `defer/resample` when the interval straddles `D` or epoch/sequence continuity is unknown;
- `indeterminate` when the epoch itself has no validated bound.

It uses exactly the information T1 proposes. Sequence and a persisted boot epoch establish ordering/restart provenance; they do **not** establish physical acquisition time. A clock-quality value cannot repair that missing information unless its derivation supplies a bounded `epsilon`. In that case it is the standard interval input, not a new feature.

**[KILL] Identification fork.** A capture node that only timestamps packet arrival cannot label whether an old reading was delayed or a new one was sampled; it repeats the receiver's ambiguity. To score false-fresh accept, the experiment must independently observe the acquisition event, for example through a source-toggled GPIO sampled by a separately clocked logic analyser/reference node. If that reference is used to calculate an upper bound online, it has introduced the trusted time service that the T1 story says is unavailable. If it is evaluation-only, it can validate only the frozen bench family.

**[KILL] Calibration fork.** The packet assumes that a rebooted node's `u` can be calibrated with a re-synchronization probe. NTP's own model distinguishes offset, delay, dispersion and jitter and makes the maximum error grow with clock tolerance. A single NTP offset, especially after loss/reboot, is not a certified `u`; using NTP's full error state is the necessary stronger baseline. No source inspected establishes that a cheap Wi-Fi probe yields a valid upper bound during T1's delay/loss/reboot cells. [GAP]

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Siddiqi, Sivaraman & Jha, *Timestamp Integrity in Wearable Healthcare Devices*, IEEE ANTS 2016 | Sensor timestamp; sync epoch; mean/standard deviation of residual time error from periodic challenges; reboot detection; server flags/rechecks a new epoch. | Timestamp reliability under variable latency, simulation plus implementation and energy/reliability trade-off. | Direct component collision with T1's epoch, clock-quality, reboot, and delayed-data story. The threat model is adversarial healthcare rather than non-adversarial lab sensing. | Kills any claim to introduce low-resource timestamp trust, epoch-bound clock quality, or reboot-aware verification. Leaves only an empirically narrow, non-adversarial decision-boundary measurement. |
| Li & Zhang, *Data-flow Availability: Achieving Timing Assurance in Autonomous Systems*, OSDI 2024 | Timestamped data, freshness constraints, run-time instrumentation, mitigation across scheduler layers. | Freshness/consistency/stability timing assurance on three CPS platforms. | Same general decision endpoint: use timestamps to accept/discard/mitigate stale physical data. T1's Wi-Fi-reset instrumentation is narrower. | Kills the framing that timestamp-based freshness checking plus run-time mitigation is a new edge-systems contribution. Leaves the exact low-cost reset panel only. |
| Mills et al., *Network Time Protocol Version 4*, RFC 5905 | Offset, delay, dispersion, jitter, root delay/dispersion; produces a synchronization distance/max-error quantity. | Standard time synchronization and error accounting. | T1's `timestamp + NTP offset + local clock-quality bound` is incomplete unless compared with the full error interval. | Supplies the strongest simple baseline, not a research collision by itself. If it matches T1, T1 has no distinct information or decision rule. |
| Kopetz & Steiner, *Temporal Consistency of Data and Information in Cyber-Physical Systems*, arXiv:2409.19309v1 (2024) | Global time, known interaction instants, time-triggered operation. | Temporal consistency between sensing and later action. | T1 explicitly tests the failure of those assumptions; the source establishes why timestamp values are conditional rather than self-authenticating. | Supports the boundary/impossibility result, not a positive T1 contribution. |
| Podhorsky et al., *System-Level Offline Time Synchronization Architecture for Distributed Electrical Signal Monitoring Using Raspberry Pi 5*, *Sensors* 26(8):2519 (2026) | RTC restoration at boot; chrony/ph2sys/PTP correction; documented pause/discontinuity. | Offline/boot time continuity on Raspberry Pi-class systems. | Direct practical component lead: RTC plus boot-time correction covers the packet's reset-time premise. | Exact full-text comparison is [GAP] because the official publisher returned HTTP 429 in this audit. Do not use it to claim exact collision, but T1 must include RTC/boot restoration as a baseline or explicitly exclude it. |

## Strongest simple baseline

**B\*: persisted `boot_epoch + sequence + calibrated clock-error interval` with a deterministic deadline guard.**

At each epoch start, persist an atomic epoch increment before sampling. Persist monotonic sequence only if T1 itself assumes it can be made durable. Run an ordinary NTP/chrony/PTP client when reachable and store its offset plus an error interval based on standard synchronization-distance/error state; otherwise mark the epoch unbounded. At the receiver apply the interval rule above. Under sequence discontinuity, reset, missing persistence acknowledgement, or unbounded interval, choose `indeterminate` or request a sample. This has no learned model and makes no assumptions absent from T1.

The proposed comparison `timestamp + NTP offset` is therefore too weak: it removes precisely the uncertainty term that T1 calls `u`. Unless B\* is matched on false-fresh cap, action latency, bytes, CPU/energy, and per-cell defer rate, an apparent T1 gain is a baseline omission rather than a research result.

## Contrarian result

**KILL as a standalone research direction in its current form.** The high-risk core does not survive: a clock-quality/error bound plus epoch/reboot handling is already a known timestamp-trust construction, and the T1 policy is either (a) ordinary interval guarding using that bound, or (b) unidentifiable because no valid bound exists. The claimed finite transfer map would still be an honest engineering measurement, but it is not yet a defensible FYP research contribution because it does not specify a new observable, action constraint, protocol property, or evaluation endpoint that B\* cannot reproduce.

**Permitted pivot:** do not make T1 the thesis. Retain its timestamp/epoch instrumentation as a control and label-quality layer for another candidate. A future T1-like proposal would need a separately justified, nontrivial observation unavailable to B\* (for example, a hardware timing signal whose error interval is independently calibrated) and a predeclared decision endpoint that differs from generic freshness checking. That would start a new three-round audit; it is not implied by this audit.

## Feasibility audit

| Area | Finding | Consequence |
| --- | --- | --- |
| Demo by 2026-12 | [K] Two low-cost boards, a local AP, scripted loss/delay, and low-voltage power cycling can demonstrate reboot, stale arrival, and interval rejection. | A demo is feasible, but a demo does not repair the research collision. |
| H1 2027 experiments | [C] A frozen single-fault panel with repetitions and energy logging is plausible in six months. | A full leave-one-cell-out claim needs a declared independent reference clock/event capture, fault injector, repeat count, and held-out-cell rule before data collection. |
| Ground-truth labels | [GAP] No specified reference captures **acquisition** time rather than delivery time. A receiver mirror is invalid. | This blocks the false-fresh metric until a GPIO/logic-analyser or equivalent external event-capture design is demonstrated. |
| Hardware assumptions | [GAP] No board, RTC, time service, logic analyser, safe low-voltage switching method, or BOM has been selected. An RTC is optional in the packet but becomes a decisive baseline. | Cannot claim a calibrated reboot-time `u` or power result yet. |
| Ethics/safety | [K] A non-hazardous bench sensor and software/network faults require no human data or real control action. | Keep claims out of clinical, safety, custody, or production-monitoring settings. |
| Time risk | [KILL] Building a trustworthy label path and a clock-bound calibration protocol is the actual hard part; it can consume the pre-December demo window while producing only a known baseline. | Do not allocate the FYP's critical path to T1 unless a new distinction passes audit first. |

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Resource-constrained sensor timestamp validation can use periodic challenge-derived residual error mean/standard deviation, per-sync epochs, and reboot detection/recheck. | [K] | Muhammad Siddiqi, Vijay Sivaraman & Sanjay Jha, *Timestamp Integrity in Wearable Healthcare Devices*, IEEE ANTS 2016, DOI https://doi.org/10.1109/ANTS.2016.7947783, pp. 1-6; author-hosted copy indexed at https://www.researchgate.net/publication/311632240_Timestamp_integrity_in_wearable_healthcare_devices | Sec. IV.C-D, pp. 3-4; Sec. IV.E-F, pp. 4-5; Sec. V, pp. 5-6. | Security/healthcare threat model differs; evidence is a component and mechanism collision, not proof of exact experimental overlap. |
| Timestamp-based freshness checking and mitigation are already common CPS practice; Kairos specifies/enforces temporal freshness and evaluates timing assurance. | [K] | Ao Li & Ning Zhang, *Data-flow Availability: Achieving Timing Assurance in Autonomous Systems*, OSDI 2024, official PDF https://www.usenix.org/system/files/osdi24-li.pdf | Sec. 3.1, printed pp. 447-448; Secs. 4-6, pp. 449-459; abstract/p. 445. | Autonomous CPS, not low-cost Wi-Fi nodes; rules out broad freshness-checking novelty only. |
| NTP exposes offset, delay, dispersion, jitter and synchronization distance/max error for dependent applications. | [K] | Mills et al., RFC 5905, June 2010, official standard https://www.rfc-editor.org/rfc/rfc5905.html | Sec. 4, pp. 8-9; Sec. 10 p. 37; Sec. 11.1 p. 40. | Standard baseline, not a primary research-paper claim. It shows why `NTP offset` alone is an inadequate comparator. |
| Dependable temporal consistency requires assumptions about global time, interaction instants, and time-triggered operation. | [K] | Hermann Kopetz & Wilfried Steiner, arXiv:2409.19309v1, 2024-09-28, https://arxiv.org/pdf/2409.19309 | Abstract and Sec. I p. 1; Sec. V pp. 6-7; Sec. VII p. 8; conclusion p. 9. | General CPS theory/design paper; supports only the conditionality/impossibility boundary. |
| A 2026 Raspberry-Pi offline synchronization paper uses RTC boot restoration and later chrony/PTP correction. | [K] bibliographic / [GAP] exact detail | *System-Level Offline Time Synchronization Architecture for Distributed Electrical Signal Monitoring Using Raspberry Pi 5*, *Sensors* 26(8):2519, 2026, DOI https://doi.org/10.3390/s26082519 | Search result abstract plus Sec. 3.1 excerpt; full official HTML/PDF returned HTTP 429 on 2026-08-28, so page verification is unavailable. | Direct practical lead only. It must be fully read before it can be used as an exact-claim collision. |
| T1's particular false-fresh/defer leave-one-cell-out protocol is absent from all literature. | [GAP] | Queries and sources below. | Not established. | Missing retrieval/search result is not novelty evidence. |
| The source clock-quality bound is valid after reboot/loss and independent of the reference evaluator. | [GAP] | T1 packet assumption only. | T1 formalization, bullet [A]. | This is a load-bearing unverified assumption. |

## Queries and failed searches

Queries executed on 2026-08-28:

- `"timestamp freshness" IoT sensor reboot sequence epoch 2024 paper`
- `"clock uncertainty" edge IoT sensor data freshness 2025 paper`
- `"age of information" "clock synchronization" IoT 2024 2025 paper`
- `"false fresh" timestamp sensor data reboot`
- `"sensor data freshness" sequence number clock offset journal IoT`
- `"sensor timestamp trust" epoch reboot IoT 2024`
- `"reboot" "timestamp integrity" IoT sensor 2025`
- `"reboot epoch" "timestamp" sensor 2024 paper`
- `"clock quality" sensor data timestamp 2024 "epoch"`

Failed/limited retrievals:

- The publisher page/PDF for Podhorsky et al. (*Sensors* 2026) returned HTTP 429, so it remains a component lead rather than load-bearing exact evidence.
- No citation-chain database with a verified full-text forward-citation set for Siddiqi et al. was available in this audit. The paper's 2024--2026 successor chain is [GAP].
- This audit did not find an accessible 2024--2026 primary paper that exactly uses T1's named four-baseline false-fresh/defer protocol. That is explicitly not an absence claim.

## Decision

**KILL.** Do not promote T1 as the FYP direction. Keep `epoch + sequence + clock-error interval` as a mandatory control/measurement layer; only reopen a timestamp problem if a new observable and endpoint survive B\* and a fresh three-round audit.
