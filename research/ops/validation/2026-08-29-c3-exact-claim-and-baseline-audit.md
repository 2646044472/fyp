# Validation Audit: 2026-08-29 C3 exact-claim and baseline audit

## Decision investigated

Whether C3, the proposed low-cost edge-service-maintainer decision to `continue`, `observe`, or `fail over` after a heartbeat anomaly under local resource contention, remains a defensible FYP research direction rather than a reproduction of existing timeout/stress evaluation.

This is a validation-only packet. It reads the active C3 protocol and tries to defeat its remaining Amber claim. The allowed user constraints are one year, a benign runnable demo by 2026-12, later experiment work in 2027-H1, self-purchased inexpensive parts, and no production service, personal data, or safety actuation.

## Claim under test

The active protocol permits only this empirical claim: choose a policy from a source-only family using `phi`, Linux CPU/memory/I/O PSI and temperature; freeze it; then compare on an untouched device/workload/fault cell with timing-only, one-signal, `observe-one-extra-interval`, and genuine three-peer Lifeguard baselines at matched false-failover, delay, and monitor-overhead budgets.

It disavows a new detector, a new stress harness, and a general reliability guarantee.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| Component collision | [KILL] Pourreza and Narasimhan's UCC 2025 study already combines Pi 4B/Jetson Nano, six workloads, CPU/memory/I/O/cache/page-fault stress, timeouts, false positives, detection sensitivity/delay, resource overhead and CPU/memory/I/O/temperature observations. EdgeStressBench 2026, the only retrieved later citation to UCC, adds workload orchestration, parameterized injection, structured application/system measurement, heterogenous Pi/Jetson use and replication-aware execution. | [GAP] The full EdgeStressBench paper/artifact was not retrievable, so its detector-policy comparison and target split cannot be checked. No mechanism distinct from resource-conditioned waiting is specified in C3. | High collision; exact EdgeStressBench method unresolved. |
| Exact-claim collision | [KILL] UCC Secs. 1-2, printed pp. 1-3, explicitly asks whether timeout configurations transfer across heterogeneous devices, workloads and stress scenarios, measuring the same false-positive/sensitivity/overhead family. The source-only freeze is a stricter analysis split of that question, not a different decision, observation model or endpoint. | [GAP] UCC evaluates static timeouts, not the exact 1,344-member policy grid or a frozen source-to-target comparison against C3's named baselines. No retrievable source establishes the absence of that protocol from EdgeStressBench. | High risk. The remaining difference is experimental hygiene, not an independently falsifiable mechanism. |
| Boundary / impossibility | [KILL] A finite prefix of heartbeat plus resource readings can be shared by a healthy-but-delayed and a failed/fail-slow service. The C3 policy must make the same action under that prefix, so it cannot guarantee both no false failovers and bounded detection. Its admitted finite injected experiment is possible, but cannot turn this into a general result. [KILL] In addition, the policy's telemetry only decides whether to wait after `phi` is high; it does not identify cause. | A finite, externally timestamped service-contract label permits a tightly scoped comparison. It does not establish causal value of `fail over` unless the experiment also measures post-action service restoration, which is absent from the current endpoint definition. | High for the universal boundary; high for the missing action-value identification. |

## Assumption and identification audit

1. **The apparent policy class is a 1,344-way source search.** From the active protocol, there are four `phi` quantiles, 16 one-signal threshold choices or 96 two-signal choices, and three wait lengths: `4 x (16 + 96) x 3 = 1,344`. [KILL] The protocol registers neither independent source tuning/selection episodes, a selection criterion robust to this search, nor an inferential rule. A selected source winner and one target cell can demonstrate one run, but cannot identify transferability rather than selection noise.

2. **The action story is not yet evaluated as an action.** [KILL] C3 measures a false action, a breach-to-detection interval, interruption caused by an action and monitor cost. It does not define an externally measured service-restoration benefit of the restart/routing action relative to `continue` or `observe`. Hence it can assess alarm timing but not the stated maintainer decision's net harm/benefit. This is not repaired by calling a late completion a service-contract breach.

3. **Local PSI/temperature are not causal fault labels.** [K] UCC reports that memory contention and elevated memory/thermal signals co-occur with anomalies; it does not imply that a PSI or temperature threshold distinguishes a harmless slow episode from an actionable one. [C] C3 can test conditional association in its finite fault injector, but must not describe the selected signal as fault cause or generalizable root-cause evidence.

4. **Missing lower-layer baselines leave an avoidable alternative explanation.** [K] SafeTimer checks pending/dropped heartbeats at the receiver and blocks a sender that misses its heartbeat deadline. Its proof/evaluation target is precisely OS/application processing delay that otherwise produces false failure reports. For C3's resource-contention story, that is a stronger explanatory baseline than interpreting a high PSI reading as a reason to wait. SafeTimer has Linux/NIC/driver assumptions and is not a drop-in Pi baseline; that limits feasibility, not the relevance of the mechanism collision.

5. **The actual recent follow-up makes the audit stricter, not safer.** [K] Crossref lists UCC 2025 as a reference of EdgeStressBench 2026. OpenAlex returned it as UCC's one indexed citation on 2026-08-29. The public abstract reconstructs an end-to-end resource-stress evaluation framework and promises code, workload definitions, experiment configurations and scripts. [GAP] Its PDF, repository and exact sections were unavailable; GitHub repository-name search returned zero results. A missing retrievable artifact blocks the required exact-neighbor audit and cannot be used as evidence of separation.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Pourreza & Narasimhan, *When Timeouts Fail*, UCC 2025 VOR, 2025-12-31, https://doi.org/10.1145/3773274.3774280 | Pi 4B/Jetson Nano, six workloads, five resource stressors, static heartbeat timeouts; CPU/memory/I/O/thermal measurement. | Secs. 1-2, pp. 1-3 ask the same cross-device/workload/stress timeout-transfer question; Secs. 4-6, pp. 4-9 measure false positives, sensitivity/delay and overhead. | Same actor-level failure response, hardware class, stress family and outcome family. | [KILL] C3 cannot claim the problem, cross-condition question, hardware/stress setting or outcome family. A source-only split is not yet a distinct research contribution. |
| Pourreza & Narasimhan, *EdgeStressBench*, MobiSys Workshops 2026, pp. 300-306, DOI https://doi.org/10.1145/3812836.3814778 | Reconstructed official-index abstract: workload orchestration, parameterized injection, structured application/system metrics, heterogeneous devices and optional replication-aware modes. | Crossref VOR metadata: online 2026-06-20, CC BY-NC-ND. OpenAlex says Pi/Jetson case study and open-source code/workload/config/script artifact. Exact PDF sections and artifact are [GAP]. | Same experimental apparatus, measurement and reproducibility framing; it cites UCC. | [KILL] new harness, injector, trace schema or reproducibility claim. [GAP] Its exact policy/split may additionally collide, but has not been verified. |
| Ma & Wang, *Accurate Timeout Detection Despite Arbitrary Processing Delays*, USENIX ATC 2018, https://www.usenix.org/system/files/conference/atc18/atc18-ma-sixiang.pdf | Receiver inspects pending/dropped heartbeats with a barrier; sender-side validity blocks a late sender. | Secs. 1-2, printed pp. 467-469; Sec. 4, pp. 470-472; Sec. 5.1-5.2, pp. 473-474; Sec. 6, pp. 474-477. It proves/report-tests prevention of false reports caused by arbitrary OS/application processing delays. | C3 treats local resource-induced heartbeat delay as a `observe` case. SafeTimer directly distinguishes a portion of that ambiguity using lower-layer observations. | [KILL] broad claim that PSI/temperature-conditioned waiting is the necessary or privileged response to local delay. Leaves only an explicitly user-space, stock-kernel limitation study, not C3's current broad story. |
| Naim et al., *Double check method*, Journal of Network and Computer Applications 253, 2026, article 104538, DOI https://doi.org/10.1016/j.jnca.2026.104538 | Publisher/search metadata describes a second validation stage using socket and port engagement after heartbeat suspicion. | Crossref version metadata identifies the VOR but the full text was not obtainable before its listed 2026-09 issue date. | Potential direct `observe then validate` baseline. | [GAP] Do not use its search-result performance claims. It is a required retrieval/baseline check if C3 is ever reopened. |

## Strongest simple baseline

**Source-tuned `phi` plus one extra observation interval, without resource telemetry**, is still the first mandatory baseline. It shares C3's action vocabulary and avoids its monitor collection cost. A slightly stronger, still simple check is `phi` followed by a socket/port liveness probe; the recent Double Check paper makes this a direct-neighbor risk, though its full protocol is [GAP].

For the portion of false failovers caused by local OS/application processing delays, SafeTimer is the decisive mechanism baseline. It is not a routine low-cost user-space implementation because it uses netfilter, kprobes and NIC/driver statistics; therefore C3 may omit it only by explicitly limiting the study to stock-kernel user-space telemetry and abandoning any broad claim about resource-delay ambiguity.

## Contrarian result

[KILL] C3 should not continue as an Amber research-direction candidate. UCC 2025 already asks and evaluates its central transfer question in the same edge resource-stress setting. EdgeStressBench subsequently packages the experiment apparatus and makes exact separation impossible to audit without an accessible artifact. The remaining source-freeze design is a replication/analysis protocol, while its planned policy has no independently specified mechanism or action-utility endpoint.

The honest pivot is a **bounded replication/negative appendix**: reproduce one UCC resource-stress cell on a stock low-cost board and show whether `phi + observe` or a lower-layer/second-probe baseline explains the false-failover trade-off. It is useful implementation evidence but not a direction to lock as a research contribution.

## Feasibility audit

| Requirement | Finding | Consequence |
| --- | --- | --- |
| Hardware and demo | [K] Three SBC peers, a local AP, a benign periodic workload and injected non-destructive stress are physically plausible within the stated calendar. | Feasibility does not cure the direct-neighbor collision. |
| Baseline implementation | [K] Fixed timeout, rolling percentile, `phi` and `observe-one-extra-interval` are feasible. [GAP] A genuine Lifeguard topology needs three live peers; SafeTimer needs OS/NIC adaptation; no delivered board/AP/power/action BOM is registered. | A C3 result would either omit strong alternatives or require more systems work than the candidate claim admits. |
| Labels and decision endpoint | [C] An external service-result trace can identify a declared deadline breach. [KILL] It does not by itself identify whether failover improved the service outcome. | Add service-restoration/availability utility to evaluate an action, or state the work as detection-only replication. |
| Evaluation scale | [KILL] 1,344 source choices and one target cell lack the registered selection/replication controls required for a transfer conclusion. | Reducing the grid alone leaves the UCC collision; increasing replication makes the one-year FYP less feasible. |

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| UCC already studies cross-scenario timeout transfer on Pi/Jetson under the same stressors and outcome family. | [KILL] | Pourreza & Narasimhan, UCC 2025 VOR, published 2025-12-31, https://doi.org/10.1145/3773274.3774280 | Secs. 1-2, printed pp. 1-3; Sec. 3, pp. 3-4; Secs. 4-6, pp. 4-9; conclusion p. 10. | Kills C3's central problem/endpoint. It does not by itself disclose C3's exact grid. |
| EdgeStressBench is UCC's retrieved later citation and contains stress orchestration, parameterized injection, structured measurements, heterogeneous hardware and a claimed artifact. | [K] / [GAP] | Pourreza & Narasimhan, MobiSys Workshops 2026 VOR metadata, https://doi.org/10.1145/3812836.3814778; Crossref record https://api.crossref.org/works/10.1145/3812836.3814778; OpenAlex record https://api.openalex.org/works/W7163161912 | Crossref metadata and OpenAlex reconstructed abstract retrieved 2026-08-29; article pp. 300-306. No PDF section/page or public repository was accessible. | Metadata/abstract establish apparatus collision, not an exact detector/split collision. |
| SafeTimer supplies a different and stronger way to handle OS/application-induced heartbeat delay. | [K] | Ma & Wang, USENIX ATC 2018, https://www.usenix.org/system/files/conference/atc18/atc18-ma-sixiang.pdf | Secs. 1-2, pp. 467-469; Sec. 4, pp. 470-472; Sec. 5.1-5.2, pp. 473-474; Sec. 6, pp. 474-477; Appendix, pp. 479-480. | Kernel/NIC assumptions restrict stock-SBC feasibility, so it is a mechanism boundary, not proof of exact empirical domination. |
| C3 cannot make a universal accurate-and-timely decision from finite local prefixes. | [K] | Chandra & Toueg, *Unreliable Failure Detectors for Reliable Distributed Systems*, JACM 43(2), 1996, https://doi.org/10.1145/226643.226647; Fetzer, *Perfect Failure Detection in Timed Asynchronous Systems*, IEEE TC 52(2), 2003, https://doi.org/10.1109/TC.2003.1176979 | Chandra & Toueg Sec. 2, pp. 225-231 and Sec. 6.3, pp. 248-249; Fetzer Sec. I, pp. 99-101. | Bounds universal claims, not a finite injected comparison. |
| A 2026 socket/port double-check is a potentially direct observe/validate baseline. | [GAP] | Naim et al., *Double check method*, JNCA 253, 2026, DOI https://doi.org/10.1016/j.jnca.2026.104538; Crossref record https://api.crossref.org/works/10.1016/j.jnca.2026.104538 | Crossref title/metadata retrieved 2026-08-29; full article not read. | Do not rely on it for quantitative or exact-method claims until the VOR becomes accessible. |

## Queries and failed searches

Queries run on 2026-08-29:

- `"When Timeouts Fail" "Revisiting Fault Detection" edge computing full paper`
- `"EdgeStressBench" "Framework for Reproducible Evaluation"`
- `edge failure detection resource telemetry heartbeat transfer evaluation 2024 2025 2026`
- `"resource-aware fault detection" edge "failure detector" 2025 2026`
- `"adaptive timeout" edge computing "resource" 2025 2026 fault detection`
- `SafeTimer failure detector Raspberry Pi ARM Linux`
- `"Accurate Timeout Detection Despite Arbitrary Processing Delays" citations 2024 2025 2026`
- `failure detector evaluation false positives detection delay failover recovery time decision utility paper`
- `"failure detection" "Linux PSI" heartbeat timeout`
- `"EdgeStressBench" GitHub`

Failed/limited retrievals:

- The EdgeStressBench DOI/ACM page exposes bibliographic information, but the PDF/full text and a public repository could not be retrieved. GitHub repository-name search returned zero results. This is [GAP], not evidence of absence.
- Double Check VOR metadata is available, but its full article could not be read before the listed 2026-09 issue date. Its exact task and results remain [GAP].
- No 2024-2026 primary paper was retrieved that establishes C3's exact 1,344-policy source-to-target protocol as a distinct research task. This failed search is not novelty evidence.

## Decision

**KILL.** C3's claimed research contribution is not sufficiently distinct from UCC 2025, and its apparatus overlaps the UCC follow-up EdgeStressBench. The remaining source-only freeze is not a new mechanism and fails the required exact-neighbor audit while EdgeStressBench remains unavailable. Retain only the bounded replication/negative-study pivot described above; do not lock C3 as the FYP direction.
