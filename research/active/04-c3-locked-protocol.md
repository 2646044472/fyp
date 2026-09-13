# C3 Rejected Candidate Protocol: Local-Telemetry Transfer Boundary

> Status as of 2026-08-29: **KILL as a research direction.** This file is retained only to preserve the evidence and a possible bounded replication/negative appendix. UCC 2025 already asks the cross-device/workload/stress timeout-transfer question using the same hardware class, stressors and endpoint family. The remaining source-only frozen split is experimental hygiene, not an independent mechanism, action, observation model or endpoint. EdgeStressBench 2026 further occupies the apparatus/reproducibility framing; its inaccessible full text remains [GAP], which blocks rather than supports an innovation claim.

## Decision and bounded story

[C] Candidate story only: a lab edge-service maintainer would choose `continue`, `observe`, or `restart / route to a standby collector` for a periodic non-production sensing/inference service when its heartbeats slow under local resource contention. A false action records an avoidable availability gap and interrupts processing; a late action prolongs a timestamped service-contract breach. The decision is local because the test intentionally withholds a timely WAN/remote probe.

[KILL] It is not a safety interlock, production monitoring service, new detector, telemetry feature, stress harness, or universal failure guarantee.

## Exact empirical claim (Amber)

### Plain-language research question

> Existing methods may work on the devices, workloads, and faults used to tune them. Do they still work when moved to a device, workload, or fault condition that did not participate in tuning?

This asks about transfer of decision value, not whether failure detection exists or whether a new detector can be invented.

Let a monitor observe at heartbeat interval `h`:

`O_t = (phi_t, cpuPSI_t, memPSI_t, ioPSI_t, temp_t)`.

`phi_t` is the phi-accrual suspicion score; `*PSI_t` is Linux pressure-stall information over a fixed 10-second window; `temp_t` is the board CPU temperature. The action is one of `continue`, `observe`, and `fail over`.

For every source-only parameter tuple in the finite family `F` below, choose the tuple that satisfies a preregistered false-failover cap and minimizes source-cell p95 service-contract detection delay. Freeze it before the target cell is run. On a preregistered held-out device/workload/fault cell, compare the frozen policy with the named baselines at the same false-failover cap, monitor overhead budget, and action-cost definition.

`F` has only these parameters:

- `theta_phi` in the source-cell 80th, 90th, 95th, or 99th percentile of `phi_t`;
- one or two selected pressure indicators from `{cpuPSI, memPSI, ioPSI, temp}`;
- for each selected indicator, a source-cell 80th, 90th, 95th, or 99th percentile threshold;
- `m` in `{1, 2, 3}` observation intervals.

For a selected tuple, if `phi_t < theta_phi`, choose `continue`. If `phi_t >= theta_phi` and a selected pressure indicator exceeds its threshold, choose `observe`; after `m` consecutive such observations, choose `fail over`. If `phi_t >= theta_phi` without the selected pressure indication, choose `fail over`. No target-cell fitting, model training, feature construction, or post-hoc policy selection is allowed.

The empirical result is either:

1. a qualified transfer result for this exact family and the declared cells; or
2. a no-transfer / one-signal-suffices / simple-observe-suffices boundary.

No result generalizes beyond the board, workload, fault process, horizon, action cost, and observation model tested.

## Fixed comparison and labels

Required baselines:

1. fixed timeout;
2. rolling-percentile timeout;
3. phi-accrual;
4. each of the four selected signals one at a time, with the same source-only threshold rule;
5. `observe one extra interval` without resource telemetry;
6. Lifeguard in an actual three-peer SWIM topology; and
7. `always fail over`, `never fail over`, and a timely remote/redundant probe only as bounds.

[K] A false failover is a restart/routing action before a service-contract breach. A true breach is not inferred from resource telemetry: the source service emits a monotonic, externally logged request/result trace, and the controller labels a breach only when the required result is not visible before the frozen deadline. Service, monitor, controller, and fault injector must be separate processes and record monotonic timestamps.

Metrics are false-failover rate, p50/p95 detection delay from contract breach, action-caused interruption duration, monitor CPU/RAM/network/power, and per-cell availability cost. All source selection and target evaluation use the same episode accounting.

## Minimum viable experiment

- Three independently running Linux SBC peers, isolated local AP, and a simple non-hazardous periodic sensor/inference workload. One physical device/workload/fault cell remains untouched until target evaluation.
- End-2026 demo: timestamped trace schema; fixed/percentile/phi baselines; one safe stressor; one observable restart/routing action; and raw log export.
- 2027-H1: genuine Lifeguard topology, all declared baselines, two workloads, at least three injected resource/fault processes, one compound held-out cell, repeated target episodes, and power measurements.
- No personal data, real facility action, unsafe power work, or hazardous actuation. The fault injector must have a manual abort.

## Audit boundary

[KILL] Pourreza and Narasimhan, *When Timeouts Fail*, UCC 2025, version of record 2025-12-31, https://doi.org/10.1145/3773274.3774280, Secs. 1-2, pp. 1-3 and Sec. 3, pp. 3-4, already covers heterogeneous Pi/Jetson hardware, static timeout trade-offs, five resource stressors, and this outcome family. It eliminates any detector, static-timeout-brittleness, hardware, or stress-harness claim.

[K] Dadgar, Phillips, and Currey, *Lifeguard*, arXiv:1707.00788v2, 2018-04-03, https://arxiv.org/pdf/1707.00788, Secs. III-IV, pp. 2-7, shows that Lifeguard requires SWIM direct/indirect probes and local-health-aware suspicion. A two-node substitute is not comparable.

[K] Under indistinguishable finite observation prefixes, no local-observation policy can both eliminate false failovers and uniformly bound detection for all fail-slow/failure worlds. This constrains C3 to its finite injected protocol; see Chandra and Toueg, *JACM* 43(2), 1996, https://doi.org/10.1145/226643.226647, Sec. 2, pp. 225-231, and Fetzer, *IEEE Transactions on Computers* 52(2), 2003, https://doi.org/10.1109/TC.2003.1176979, Sec. I, pp. 99-101.

[GAP] EdgeStressBench, MobiSys Workshops 2026, pp. 300-306, https://doi.org/10.1145/3812836.3814778, has an official DBLP record dated 2026-07-04 at https://dblp.org/rec/conf/mobisys/PourrezaN26 but its exact protocol/artifact was not retrievable. The exact C3 split has not been verified absent from either neighbor. Amber status remains until that retrieval is resolved.

## Kill and pivot

Kill C3's positive hypothesis if any required strong baseline reaches the same held-out frontier with lower monitoring cost, if target labels fail the service-contract audit, or if the three-peer/held-out design cannot be executed. The resulting thesis output is still a bounded negative finding: for the declared edge-service family, resource telemetry did not add decision value beyond a simpler detector and should not justify extra monitor complexity.
