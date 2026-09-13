# Decision investigated: historical SAP and EBR-AIM residuals, and the equally informed router boundary (2026-08-31)

## Decision investigated

Try to revive only the two historical edge candidates that still appear superficially defensible after the broader search:

1. `SAP`: a tabletop record policy which names sensor health, scene observability and task sufficiency, then chooses accept, one diagnostic/re-acquisition action, or review.
2. `EBR-AIM`: a low-voltage I2C node which uses a counted probe after a read failure before selecting retry, standard recovery, target reset/power isolation, or unknown/manual.

The common claim under attack is stronger than either candidate: a structured intervention policy provides decision value beyond an equally informed cost-sensitive router. This audit treats a router as able to request every action/probe available to the candidate and to use every result available before its final decision. It does not permit a comparison that gives the proposed policy an extra sensor, extra action, or post-action observation.

## Claim under test

`SAP` [C]: an explicit health/observability/task hierarchy reduces false accepted tabletop records under a fixed re-acquisition/review budget.

`EBR-AIM` [C]: an independently measured, budgeted bus/target probe changes the post-action utility of recovery choices beyond a matched staged I2C driver.

The only possible residual is not a new policy: for a specified physical instrument, does a named probe actually distinguish an otherwise ambiguous prefix and change measured *post-action* loss? This is a device-bound empirical boundary, not evidence of a generally better router or recovery mechanism.

## Three-round novelty audit

| Round | SAP evidence for collision / kill | EBR-AIM evidence for collision / kill | What remains, if any | Confidence |
| --- | --- | --- | --- | --- |
| Component collision | RASMF already combines confidence-triggered conditional acquisition, reliability descriptors, availability, cross-modal disagreement, OOD safeguard, fallback actions, cost and latency. MAMMOTH combines modality routing and task-level action outcomes. | Linux fault injection/recovery, TI/NXP recovery guidance, two 2024-2025 I2C recovery patents, and the 2025 I2C monitoring/isolation patent already cover observing SCL/SDA/ACK/address, retry, clock recovery, reset, target isolation/power cycling and escalation. | A particular low-cost test fixture may yield a reusable trace dataset. That is an apparatus/measurement distinction, not a new component. | High |
| Exact-claim collision | RASMF's image-first conditional acquisition and quality-aware final decision have the same "screen, acquire, use quality, fallback" shape. Its dataset is not a physical tabletop intervention study, but that scope difference does not make a state hierarchy a contribution. | US20250068503A1 observes bus state and read/write/address information, identifies the target, isolates/resets it, retries and reports the result. Its endpoint is operability rather than the proposed preregistered utility; no retrieved 2024-2026 source exactly matches the proposed finite utility table. | An exact device-specific *measurement protocol* has not been found. Absence of a retrieved match is [GAP], not novelty. | High for SAP; medium for EBR endpoint |
| Boundary / impossibility | If hierarchy labels are computed from passive vector `X`, then a direct router `r(X)` can reproduce the structured policy exactly. If the hierarchy receives witness `W`, a fair router receives `(X,W)` and can reproduce it. | If the probe response `P` is available, an adaptive router can choose the same probe after `X` and choose the same final action from `(X,P)`. If `P` is not available, a positive probe effect is an engineering fact about that topology, not superiority of the named policy. | A null map of indistinguishable prefixes is honest and potentially useful. A positive map only survives as a device-bound observation/action result with a matched active-router comparator. | High |

## Assumption and identification audit

### The router dominance boundary [KILL]

Let `X` include every passive signal, telemetry feature and history available before an action. Let a structured policy emit labels `H=g(X)` and choose `a=p(H)`. The direct policy `r(X)=p(g(X))` has exactly the same action and loss for every `X`; state names cannot lower the attainable decision risk by themselves.

If the candidate chooses a probe `q` and sees result `P`, its final decision is `a=p(X,P)`. A matched active router can choose the same `q` and use `r(X,P)=p(X,P)`. Thus a result against a *fixed staged driver* only establishes that adaptivity/value of information can beat that particular fixed driver. It cannot establish that the structured policy is better than an equally informed, equal-action, cost-sensitive router. This is a direct functional counterexample, not a claim that an extra observation can never be useful.

The measured question is therefore narrower: is `P` conditionally action-relevant after `X`, i.e. does an estimate of the held-out action-loss distribution differ between `P` values after conditioning on `X`? If not, any added probe is expense without demonstrated decision value. If yes, the comparator must be an active router that also obtains `P`, not a passive threshold or a fixed recovery ladder.

### SAP identification failure [KILL]

- A reference patch, re-acquisition pose or device diagnostic is valid only if it is separately measured, repeatable, available online, and has a predeclared post-action outcome. An image-quality score extracted from the existing frame is already part of `X`.
- A reference patch establishes the imaging-chain state, not target observability. A second pose is generic active perception; absent measured success after the pose, it is indistinguishable from a manual retry.
- The record story remains under-specified: no named technician workflow, object acceptance criterion, independent task truth, or concrete false-accept loss has been frozen. The existing claim cannot pass the project's real-decision gate.
- RASMF itself exposes why its result is not evidence for revival: its 4,094 image/audio pairs are paired by filename rather than established simultaneous physical acquisitions, and loss/degradation are introduced in evaluation (Secs. 3.2-3.3). A new physical log would be useful data, but not proof that a hierarchy beats the fair router.

### EBR-AIM identification and safety failure [KILL / PIVOT]

- `SCL-toggle response` is not an independent diagnostic by default. Linux documents a held-SDA case for which the master should attempt bus recovery, and it documents the incomplete-address case in which the target releases SDA after SCL toggling. Treating that standard recovery response as a proprietary probe double-counts an occupied mechanism.
- A target reset-status line can be an additional observable, but it is target-specific. A result from it says only that a particular part exposes useful reset state under registered faults. It cannot support a general I2C action-policy claim.
- The proposed collateral-write endpoint is physically real: Linux's `incomplete_write_byte` case warns that extra SCL pulses may write data to register `0x00`. But it creates a feasibility gate, not a contribution: a safe, sacrificial/read-only target and a ground-truth method must be proven before there can be an experiment.
- Fault labels created by a clamp/controller may be ground truth for evaluation only. Feeding equivalent control state, timing marker, or analyzer output to the policy would leak the latent state and invalidate the claim.
- US20250068503A1 already makes a strong contrary assumption from the same sorts of line/protocol observations: it identifies target malfunction, isolates or resets the target, and retries. This means EBR-AIM must not claim that state-attributed recovery action selection is new.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Fallahy et al., *Reliability-Aware Selective Multimodal Fusion for Concrete Crack Detection Under Sensor Degradation*, Preprints.org v1, posted 2026-07-28, https://www.preprints.org/manuscript/202607.2018 | Image screen; conditional acoustic acquisition; calibrated scores, quality, availability, disagreement and OOD; image/acoustic/fusion/fallback branches. | 4,094 paired observations; error, calibration, sensing rate/cost and latency across degradation/missingness (Secs. 1.3, 2.1, 2.4-2.6, 3.2-3.3, 4). | Direct SAP component and decision-shape collision. | [KILL] Kills selective sensing, reliability state, fallback, cost reporting and a simple quality router as contributions. It uses controlled degradations and lacks physical re-acquisition; that is only a protocol scope difference. |
| Kotian et al., *MAMMOTH*, arXiv:2607.12965v1, 2026-07-14, https://arxiv.org/html/2607.12965v1 | RGB, thermal, 3D point cloud and velocity; sparse routing with modality combinations; trajectory action. | Real off-road conditions, missing-modality masks and downstream mobility outcomes (Intro/Sec. III). | Broad SAP collision: adaptive use of multimodal inputs and action-level outcome. | [KILL] Removes any claim that an edge action policy with modality-aware fallback or task harm is absent. Its hardware/task differs and does not rescue the tabletop story. |
| Linux kernel, *I2C GPIO fault injection*, current documentation retrieved 2026-08-31, https://cdn.kernel.org/doc/html/latest/i2c/gpio-fault-injection.html | Read SCL/SDA state; force/release lines; incomplete address/write, arbitration and panic fault cases; recovery is expected. | Driver-under-test behavior; scope/logic-analyzer verification ("Wire states" and "Incomplete transfers"). | EBR fault family, observable prefix, recovery response and collateral-write hazard. | [KILL] Kills a claim that counted SCL response, ordinary I2C fault injection, nine-clock recovery, or measuring incomplete-write consequences is a new mechanism. |
| US20250068503A1, *Circuit for Status Monitoring, and Fault Recovery and Isolation for I2C Bus*, published 2025-02-27, https://patents.google.com/patent/US20250068503A1/en | SCL/SDA, protocol conformance, ACK, target address and R/W bit; identify target; reset/power-isolate/disconnect; retry/notify. | Restores/isolates an I2C bus; description paras. 73-83, 103-152; claims 8-9. | EBR's observation-to-target-attributed action ladder. | [KILL] Kills generic state-attributed, staged I2C recovery. It does not report the proposed finite loss table, so it leaves only an empirical conformance boundary. |
| US20240111619A1, *I2C Device with Internal Bus Stuck Recovery*, published 2024-04-04; patent granted 2026-02-17, https://patents.google.com/patent/US20240111619A1/en | Counts SCL cycles while internal SDA remains low, detects local fault and releases bus without power cycle. | Local target recovery; Description paras. 95-108, 131-139, 210-215. | EBR's candidate "counted probe" and its intended distinction between internal target state and a global stuck line. | [KILL] Kills a generic claim that counted SCL/SDA behavior plus local recovery is unexplored. It reinforces that any reset-status result must be confined to the named part. |
| More et al., *SentryBus*, arXiv:2608.17082v1, 2026-08-17, https://arxiv.org/html/2608.17082v1 | Transaction timing, read/write sequence, transfer length, address, register/FIFO state and data transitions; multi-vantage ground truth. | I2C observability boundary and low-cost analyzer characterization; Secs. I-II, VII-VIII. Controlled attack detection is still outstanding. | EBR observability/instrumentation framing. | [KILL] Kills generic claims that adding an analyzer/ground-truth bus vantage is itself an edge-reliability contribution. [K] Leaves only benign recovery-specific post-action measurement, not a security claim. |
| Yu et al., *Decentralized system-centric sensor fault diagnosis and recovery using edge computing for wireless structural health monitoring systems*, Measurement 261 (2026) 119994, DOI https://doi.org/10.1016/j.measurement.2025.119994 | Local anomaly classification, rule-based source diagnosis and iterative recovery. | Lab tests plus an IoT edge node; publisher abstract/highlights inspected. | General "edge-local source diagnosis then recovery" narrative. | [KILL] Kills using edge deployment plus diagnosis/recovery as the novelty story. Full text/sections were not available here, so it is not used for an exact I2C collision. |

## Strongest simple baseline

The mandatory baseline for either candidate is an **equally informed finite-action router**:

1. Input before a probe: every field in `X` used by the structured state classifier or staged driver.
2. Allowed action set: the exact same `retry`, standard recovery, target reset/power isolation, `probe`, abstain/manual/review, or re-acquisition actions, with identical deadline/energy/operator budget.
3. Input after a probe: the same `P`, plus its time/energy cost and the same post-action observation.
4. Training/selection: source cells only; freeze policy and action-cost weights before held-out fault, target, timing or scene cells.

The baseline can be a small tabular cost-sensitive policy, calibrated conditional loss table, or a direct learned router. It need not be a deep network. For each candidate it should be compared with fixed retry/always-on/manual controls, but those weak controls cannot be the decisive comparator.

[KILL] If the structured policy wins only against a fixed ladder, quality threshold, or router denied a probe/witness, the result does not support the proposed contribution. If the equal router matches it, the named state decomposition is interpretable engineering only.

## Contrarian result

The historical candidates share an adverse selection effect: because the student defines the fault injection and the new probe, it is easy to manufacture cells for which that probe is predictive. The relevant held-out test is not random repetitions of the same clamp/target, but a blocked target/timing/fault mechanism cell where the direct active router receives the same observation/action privileges. Linux already documents that even familiar I2C incomplete transfers differ materially in recovery behavior and can cause collateral writes; this makes a safe finite replication worthwhile, but makes broad recovery claims less credible.

## Feasibility audit

| Requirement | SAP | EBR-AIM |
| --- | --- | --- |
| Real decision/harm | [KILL] no concrete workflow, acceptance criterion or independently measured record harm is fixed. | [K] narrow technician/node story is coherent, but only non-production, low-voltage recovery is authorized. |
| Data and truth | [KILL] needs physical fault, healthy-hard, task truth, intervention and post-action labels; none is confirmed. | [GAP] needs a sacrificial/read-only target, independent clamp/reset truth, safe current limits, and proof that writes can be detected without leaking labels. |
| Hardware/time | [GAP] no sensor API, witness, fixture, power meter or item list is verified. | [GAP] affordable parts are plausible, but board SKU, voltage compatibility, analyzer rate, power measurement and delivery remain unverified. |
| Compute/ethics | [C] a compact policy and non-personal tabletop setting could be feasible, but the object story is not yet defined. | [K] small MCU/host logic and non-personal benchtop collection are feasible in principle; no production/safety actuation or personal data is necessary. |
| Negative value | A failed SAP policy simply restates router sufficiency unless it supplies a reusable, independently labeled physical-event dataset. | [K] a preregistered ambiguity/conformance result can be useful: specified prefixes plus specified probe do not beat standard recovery at equal cost. It is a negative/reproduction result, not a positive direction. |

## Sharply constrained residual

No historical candidate survives as a primary FYP direction. The narrowest defensible residual is a **device-bound I2C recovery observability/conformance study**, only after a preflight clears all conditions below:

- Observation: a datasheet-exposed target reset/fault status or an electrically separate, independently characterized diagnostic line; it must not be SCL-toggle behavior already used by standard recovery, the fault injector control state, or analyzer-only ground truth.
- Action: one bounded, harmless recovery action with an observed transition, for example target reset followed by a documented read-only health check. The result must be available to the deployable controller.
- Endpoint: held-out *post-action* recovery success, latency, energy and detected collateral-write/unknown rate, compared against the equal active router and a standard staged driver.
- Scope: one named topology, target revision, fault family and cost/deadline table. No generic I2C, edge reliability, adaptive sensing, security, or policy-superiority statement.

If the probe has zero conditional action value or the equal active router matches the table, publish/report only the finite ambiguity map and conformance data. If it has value, the contribution is still the measured hardware boundary, not the structured policy. This residual is therefore **not sufficient to re-lock EBR-AIM** without a second exact-claim audit after the target/probe/topology are frozen.

## Evidence ledger

| Claim | Label | Primary / official source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| A passive state hierarchy cannot outperform a direct policy given identical information; an active-probe policy can be replicated by a router given the same probe action and result. | [KILL] | Formal functional reduction in this audit. | "The router dominance boundary" above. | A mathematical baseline argument, not a claim that all probes have zero value. It requires matching information/action budget. |
| RASMF conditionally acquires a second modality and combines confidence, quality, availability, disagreement, OOD safeguard, fallback, cost and latency. | [KILL] | Fallahy et al., Preprints.org v1, 2026-07-28, https://www.preprints.org/manuscript/202607.2018 | Sec. 1.3; Secs. 2.1, 2.4-2.6; Sec. 4. | Preprint, not peer reviewed; inspection image/audio, not SAP tabletop. Strong component/baseline collision. |
| RASMF data are 4,094 indexed image/audio pairs; pairing confirms correspondence, not simultaneous physical acquisition. | [K] | Same RASMF v1 URL. | Secs. 3.2-3.3. | Supports only the need for real physical logs, not an inference of novelty. |
| I2C fault injection explicitly includes held SCL/SDA, incomplete address/write, arbitration loss and panic; incomplete write may cause a random register write under recovery clocks. | [KILL] | Linux I2C documentation, current page retrieved 2026-08-31, https://cdn.kernel.org/doc/html/latest/i2c/gpio-fault-injection.html | "Wire states"; "Incomplete transfers"; `incomplete_write_byte`. | Official documentation; it establishes available mechanisms and safety risk, not expected outcomes on a specific target. |
| I2C monitoring/recovery can infer target from signal/protocol/address/RW, then isolate/reset/power-cycle and retry. | [KILL] | US20250068503A1, published 2025-02-27, https://patents.google.com/patent/US20250068503A1/en | Description paras. 73-83, 103-152; claims 8-9. | Patent disclosure, not a peer-reviewed measured utility study. It is a direct action-family collision. |
| Internal SDA fault detection/recovery may use counted SCL cycles and release the SDA bus without power cycle. | [KILL] | US20240111619A1, published 2024-04-04; granted patent 12,554,572 on 2026-02-17, https://patents.google.com/patent/US20240111619A1/en | Description paras. 95-108, 131-139, 210-215. | Device-internal architecture, not the full EBR protocol; it defeats the claimed generic counted-probe component. |
| A low-cost I2C instrument needs verified observation-vantage separation; its measurement result must not exceed built/validated apparatus. | [K] / [KILL] | More et al., SentryBus arXiv:2608.17082v1, 2026-08-17, https://arxiv.org/html/2608.17082v1 | Abstract; Secs. I-II; Sec. VII-A/B; Sec. VIII-A/D. | Preprint; security manipulation scope differs. It is used only for instrumentation/observability discipline, not security claims. |
| Decentralized edge sensor diagnosis plus recovery is already an active 2026 system research frame. | [KILL] | Yu et al., Measurement 261 (2026) 119994, DOI https://doi.org/10.1016/j.measurement.2025.119994 | Publisher abstract and highlights inspected 2026-08-31. | Full text unavailable in this audit; no exact task/endpoint collision asserted. |

## Queries and failed searches

Queries run on 2026-08-31:

- `2024 2025 2026 I2C fault diagnosis recovery action selection probe sensor bus paper`
- `2024 2025 2026 I2C bus recovery fault injection power cycle retry diagnostic official`
- `"I2C" "fault diagnosis" "recovery" 2025 paper`
- `"I2C" "post-action" recovery fault 2024 2025 2026`
- `"I2C" "staged recovery" fault injection 2024 2025 2026`
- `"active diagnosis" "value of information" "sensor" 2024 2025 2026 decision action paper`
- `"sensor fault diagnosis and recovery" edge computing 2026 source code paper`
- `2024 2025 2026 active perception sensor failure diagnosis recovery action camera calibration inspection paper`

Failed / unresolved:

- [GAP] No primary 2024-2026 work was retrieved that exactly evaluates an independently exposed I2C reset-status probe versus an equally informed *active* cost-sensitive router on a preregistered post-action loss table. This is not novelty evidence.
- [GAP] No low-cost target SKU with a documented, safely observable reset/fault line and sacrificial register behavior was verified.
- [GAP] The full text of Yu et al. was inaccessible; it is not used for exact overlap.
- [GAP] A paper whose full method simultaneously joins real partial tabletop faults, independent witness, a human-safe re-acquisition action and post-action record endpoint was not retrieved. Existing RASMF/MAMMOTH coverage and the router-dominance reduction still defeat SAP's current policy claim.

## Decision

- `SAP`: **KILL** as a research-policy candidate. It is either a reparameterized quality/router decision or a generic active-perception protocol; a real physical log could become a benchmark/negative appendix only.
- `EBR-AIM`: **PIVOT** to a named-device, benign I2C recovery observability/conformance experiment. It is not locked and must not claim a new recovery mechanism, adaptive sensing policy, or a general superiority result. Its positive branch requires the four residual gates above and a third exact-claim audit after protocol freeze.
- Common pattern: **KILL** the claim that any intervention policy exceeds an equally informed router. Extra information can help, but the fair direct active router must receive the same information, action set and cost.

PIVOT
