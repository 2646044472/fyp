---
topic: c3-transfer-boundary
created: 2026-08-28
last_verified: 2026-08-29
status: killed
depth: medium
related:
  - low-cost-edge-reliability-gate1
sources:
  - url: https://doi.org/10.1145/3773274.3774280
    fetched: 2026-08-28
  - url: https://doi.org/10.1145/3812836.3814778
    fetched: 2026-08-28
  - url: https://arxiv.org/pdf/1707.00788
    fetched: 2026-08-28
---

# C3: Local-Telemetry Transfer Boundary

## Candidate

The candidate is an empirical boundary study, not a new failure detector: for fixed low-cost edge boards, workloads, injected resource/fault processes, and a matched false-failover budget, does local resource telemetry transfer beyond strong timing-only baselines to a previously unseen device/workload/fault cell?

The actor is a maintainer deciding whether to restart/fail over an on-device sensing/inference service. A false action interrupts the local sensing record; delayed action extends a real service outage. Edge matters because the monitor must act from local timing and resource observations under contention, without assuming a cloud probe or surplus hardware.

## Superseded Protocol Boundary (2026-08-28)

The user confirms a one-year project, an end-2026 runnable demo, 2027-H1 for experiment expansion, and self-purchase authority for affordable components. C3 was selected with Amber innovation status after an earlier 2026-08-28 audit. A later independent red-team audit returned it to HOLD, so this protocol is a candidate registration, not authorization to claim novelty or begin thesis implementation.

Before the demo, publish a one-page preregistration that fixes:

- a finite, non-learning telemetry policy family `F` and its source-only threshold grid; `F` is an evaluated reference family, never a new detector claim;
- the source cells, one untouched held-out device/workload/fault cell, warm-up/tuning budget, and target-blind selection rule;
- a three-peer Linux topology when comparing Lifeguard; otherwise mark Lifeguard topology-inapplicable rather than silently omitting it;
- an externally timestamped service-contract breach label, separate service/monitor/failover-controller processes, and a common definition of false failover, action interruption, detection delay, CPU/RAM/network/power overhead;
- fixed timeout, rolling-percentile timeout, phi-accrual, four one-signal rules, `observe one extra interval`, and genuine Lifeguard as baselines/bounds.

The strongest direct neighbor is Pourreza and Narasimhan, UCC 2025. The project must not claim novelty of a detector, resource-health signal, stress harness, static-timeout brittleness result, or global reliability property. EdgeStressBench's exact protocol/artifact remains [GAP].

## Fresh Red-Team Result (2026-08-28)

[KILL] UCC 2025 asks whether timeout configurations transfer across heterogeneous devices, workloads, and stressors while measuring the same false-positive/detection-delay/overhead outcome family (Secs. 1-2, pp. 1-3; Secs. 4-6, pp. 4-9; https://doi.org/10.1145/3773274.3774280). The residual cannot be framed as a new transfer question.

[GAP] EdgeStressBench 2026 has metadata/abstract overlap with C3's stress orchestration and reproducibility apparatus, but its full paper/repository could not be retrieved: https://doi.org/10.1145/3812836.3814778. The exact baseline/tuning/split collision is therefore unresolved, not absent.

[KILL] The initial `F` enumeration is a 1,344-member source-selected policy family. Without a smaller preregistered family, independent source selection episodes, multiplicity treatment, and at least two target cells, it supports only a single-cell demonstration, not a claim about transferability. The strongest simple baseline is source-tuned phi-accrual plus `observe one extra interval`.

**Status: KILL.** UCC 2025 already asks the cross-device/workload/resource-stress timeout-transfer question with the same outcome family. EdgeStressBench's exact protocol remains [GAP], which blocks a claimed distinction rather than preserving a candidate. This file is retained as a boundary/negative-study record only.

## Exact Claim

Let `O_t = (heartbeat inter-arrival, CPU, memory pressure, I/O, temperature)` and let an action be `continue`, `observe`, or `fail over`. Before target evaluation, select one member of a finite non-learning policy family `F` on source cells only. On preregistered target cells, that frozen member is compared with fixed timeout, percentile timeout, phi-accrual, genuine three-peer Lifeguard, `observe one extra interval`, and each single resource signal. The study reports either:

- an improvement in p95 true-fault detection time at no higher false-failover rate and monitor overhead; or
- a no-transfer / one-signal-suffices boundary.

It must not claim a universal classifier, a new telemetry feature, or a new stress harness.

## Direct-Neighbour Boundary

Pourreza and Narasimhan, UCC 2025, Sec. 2 and Secs. 4--6, study static timeout behavior under five resource stressors on Pi 4B/Jetson Nano and six workloads, restricting the main study to single-fault scenarios. The paper itself names phi-accrual, Lifeguard, SafeTimer, and adaptive approaches in Sec. 3. It therefore kills generic resource-aware detection claims.

The allowed residual is narrower: a preregistered transfer/no-transfer comparison against those stronger baselines, including held-out cross-device/workload/fault cells. This is an auditable distinction only if the UCC paper did not already run that exact baseline/split. Accessible official full text makes the static-timeout and single-fault scope [K]; exact comparison-table coverage remains [GAP] until a downloadable PDF is inspected.

EdgeStressBench, MobiSys Workshops 2026, pp. 300--306, is a direct harness collision. Its public bibliographic record currently marks access closed; exact repository revision remains [GAP]. It can be a reproduction aid but cannot be the claimed contribution.

## Boundary

If a healthy service under resource contention and a fail-slow service have the same finite prefix of `O_t`, any policy restricted to `O_t` must take the same action in both worlds. It cannot simultaneously guarantee zero false failover and a uniformly bounded detection delay. C3 can only make conditional empirical statements about its injected process and observation horizon.

## Minimum Experiment

- Three inexpensive Linux edge peers so that the Lifeguard baseline uses its actual SWIM direct/indirect-probe topology; at least one device/workload/fault cell is never used in tuning.
- Two bounded workloads and three fault/resource processes, one compound target cell; each episode has explicit process-state ground truth.
- A local monitor records heartbeat, resource telemetry, action, restart/failover cost, CPU/RAM overhead, and power for repeated batches.
- Tune once on source cells; do not tune on target cells, but run repeated target episodes. Report false failover, p50/p95 detection time, availability cost, and ablations.
- No personal data, production service, or hazardous actuation. A manual abort isolates fault injection.

## Kill Conditions

- phi-accrual, Lifeguard, percentile timeout, or any one signal reaches the same matched-budget frontier;
- the apparent benefit disappears on the held-out board/workload/fault process;
- trace labels do not distinguish induced resource stress from actual fail-slow/fail-stop ground truth;
- the board count or FYP calendar cannot support a held-out target cell.

## Remaining Execution Checks

- Exact UCC comparison coverage and the EdgeStressBench implementation/artifact must be rechecked from accessible primary material. This preserves Amber status; it does not reopen detector/harness claims.
- Select the exact three-peer SBC/network/power-measurement bill of materials before procurement and preserve the three-peer Lifeguard condition.
