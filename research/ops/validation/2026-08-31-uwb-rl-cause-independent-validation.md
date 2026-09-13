# Validation Audit: 2026-08-31 UWB-RL-CAUSE

## Decision investigated

Whether **UWB-RL-CAUSE** should receive an Amber thesis slot: a fixed-rail
benchtop logger observes a target UWB link plus fixed reference links and outputs
`retain`, `target-path ambiguous`, `infrastructure-wide ambiguous`, or `unknown`.
The claimed difference is a better distinction of a target-path obstruction from
shared anchor/radio/infrastructure conditions than target-link CIR/FQA/RSSI alone.
The action annotates a non-personal laboratory record; it does not steer navigation,
operate machinery, or make a safety claim.

## Claim under test

**[C]** Given the proposed target and reference UWB-link diagnostics, a local policy
can identify the stated two fault-cause classes more accurately than target-only
diagnostics, periodic reference ranging, and an equally informed generic classifier,
on held-out physical condition cells.

The claim is deliberately narrower than universal NLOS identification or corrected
range accuracy.  That restriction makes the story harmless, but does not by itself
make the causal label identifiable or create a research distinction.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| 1. Component collision | Peterseil et al. already use UWB-transceiver/intermediate metrics, including link RSSI and CIR-based anomaly detection, separate node/link/system indicators, assess them online locally, and filter untrusted anchor links. Yang et al. use CIR and range data for credibility and fine-grained ranging-error categories. | The candidate calls one link the movable target and other links fixed references; neither paper's headline uses that rail vocabulary. | High collision; wording distinction only. |
| 2. Exact-claim collision | Peterseil's sequential procedure first tests each anchor link, then uses the surviving links to update node and system state. Its evaluation includes improper anchor configuration and active interference. Yang's explicit `retain / delete / mitigate` decision and error-source classification occupy the range-quality decision endpoint. | I did **not** locate a primary work whose headline exactly says `target-path ambiguous` versus `infrastructure-wide ambiguous` for a fixed rail logger. This is [GAP], not evidence of novelty. | High that the natural multi-link baseline implements the candidate's action family; medium on literal task-title overlap. |
| 3. Boundary / impossibility | The observed vector contains radio-path effects, not a witness of their physical cause. The same finite reference-link pattern can be produced by target-only obstruction plus geometry/multipath, or by a shared RF/anchor condition that affects a subset of links; an unrestricted cause label is therefore non-identifiable from the planned observation. An equally informed classifier can reproduce any deterministic proposed policy exactly. | A narrowly predeclared fixture taxonomy can be labelled by the experimenter and empirically classified within that taxonomy. It cannot establish a general cause interpretation, unseen-fixture transfer, or measurement truth. | High for the unrestricted claim; high that finite-panel evidence is only local. |

## Assumption and identification audit

Let `O = (q_target, q_ref1, ..., q_refk, h)`, where every `q` is a CIR/FQA/RSSI/
range summary and `h` is declared radio configuration.  Let `Z` be the asserted
physical cause (`target-path`, `shared infrastructure`, or `other`).  The policy
observes `O`, not an independent propagation-path map, radio-internal fault state,
or true first arrival for every link.

**[KILL] Observational ambiguity.** For any finite set of reference links, an
unobserved reflector/absorber or interference source can be placed/configured so that
the recorded summaries match a target-path episode while the asserted cause is
shared, or match a shared episode while only a subset of paths is disturbed.  The
diagnostic state does not supply an intervention that separates those worlds.  Thus
`P(O | Z=target-path)` and `P(O | Z=shared)` may overlap under the permitted
nuisance conditions. A classifier can be useful on a *restricted, labelled fixture
distribution*, but a predicted class is not causal evidence outside that distribution.

**[KILL] Equal-information reduction.** If the proposed policy is `f(O)`, an
equally informed generic classifier/router `g(O)=f(O)` has the same outputs and
cost. Therefore the claim cannot be “reference-aware structure beats an equally
informed classifier.” A target-link-only baseline is correctly required but merely
demonstrates that extra reference-link information was supplied. It cannot establish
a distinct policy mechanism unless the candidate pre-specifies a different guarantee
(for example, sample efficiency under a fixed fixture distribution) and survives that
new exact-claim audit.

**[K] Direct literature mechanism.** Peterseil et al. explicitly categorize metrics
by node, individual node--anchor link, and whole-system state, assess them online,
and in their sequential method remove anchors whose link indicators are untrusted
before updating the other indicators. The candidate's target/reference partition is
a relabelling of this multi-link state diagnosis rather than a new observation/action
structure.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Peterseil et al., *Sensors* 2024 | Locally available UWB/intermediate metrics: node temperature/battery, per-link RSSI and ML CIR anomaly score, and system configuration/geometry. Basic and sequential trustworthiness; sequentially filters anchors with untrusted links. | Online UWB self-localization trustworthiness; evaluates improper anchor configuration and an active attack, including link, node and system indicators. | Component and decision-family collision. Per-link versus node/system status is the proposed target-path versus infrastructure distinction at the observable-system level. | [KILL] The natural multi-anchor sequential baseline already uses the candidate's central information and performs a stronger downstream action than lab annotation. It does not prove the rail's named physical cause, which is exactly the proposed boundary problem. |
| Yang et al., *Measurement* 2025 | CIR sequence/features and range; credibility score; fine-grained error categories; retain/delete/mitigate action. | Ranging quality and targeted error mitigation in several LOS/NLOS scenarios, with vision position reference for evaluation. | Direct range-quality/error-source classification and retain/discard endpoint; not the exact target/reference vocabulary. | [KILL] Rules out presenting CIR-based fault/error class triage plus `retain` as a new endpoint. It leaves only the reference-link causal wording, which fails the identification audit. |
| Qorvo, DW3xxx API Guide v4.12 | Official API exposes CIR/diagnostics from accumulator memory after reception. | Hardware capability and timing constraints, not a research comparator. | Confirms the proposed observation can be collected in principle. | [K] Feasibility is not the differentiator. The guide states these reads are diagnostics, not normal operation, must precede receiver re-enable, and require substantial samples/bytes. |

## Strongest simple baseline

1. **Peterseil-style sequential multi-link monitor:** calculate the documented
   per-link anomaly/RSSI indicators on every anchor; mark weak links; derive
   node/system status after filtering. Map its output to `retain` or `unknown` and
   report it before any new model.
2. **Equally informed generic classifier:** input the complete proposed vector `O`
   (all target/reference CIR summaries, radio configuration, and any timing feature),
   trained and tested on exactly the same group-held-out fixture blocks. This is an
   equality baseline: it can instantiate the candidate policy, so a structured method
   needs a separately stated and tested advantage such as sample efficiency.
3. **Target-only quality triage:** Yang-style CIR/range quality score and
   `retain / delete` threshold. This is the honest lower-information ablation, not
   evidence that reference links create a new mechanism.
4. **Fixed periodic reference scan / always-reference equal-cost control:** use
   the same ranging budget as the candidate. It tests whether adaptivity, rather than
   merely observing references, changes the result.

If any of (1), (2), or (4) matches cause-label error and retained-record false rate at
the same `unknown` rate and radio budget, the candidate has no residual contribution.

## Contrarian result

**[KILL]** This is not saved by changing `NLOS` to `target-path ambiguous`.
Peterseil's 2024 framework already connects per-link channel evidence to node and
system state in an online local decision, while Yang's 2025 paper already performs
fine-grained error-source credibility classification with retain/discard decisions.
The remaining phrase, “what physical cause produced this reference-link pattern,” is
not observed by the radio summaries.  Restricting the physical world to deliberately
applied rail fixtures makes a publishable-looking classification table possible, but
not a defensible edge reliability claim beyond that table.

The honest residual is a **replication/negative benchmark appendix**: test whether
raw-CIR access on a named DWM3000/DW3720 stack and a named rail/fixture set supplies
incremental data beyond Peterseil-style link/node/system indicators. A negative result
is meaningful configuration evidence; a positive result remains confined to that
fixture distribution until a new exact-claim and external-holdout audit passes.

## Feasibility audit

| Requirement | Audit | Status |
| --- | --- | --- |
| Hardware | Four affordable UWB nodes, removable obstructions, a fixed rail and independent encoder/tape truth are plausible. Qorvo's current API documents CIR access. | [K] board-level collection is plausible; exact board, delivery and CIR feature extraction are [GAP]. |
| Edge path | The official guide says accumulator reads are diagnostic rather than normal-operation reads; the accumulator is not double-buffered and must be read before re-enabling the receiver. It holds 992/1016 complex Ipatov samples (six bytes each) plus optional STS samples. | [K] The claimed real-time budget cannot be assumed from a board purchase. Measure range rate, SPI/MCU cost, loss and latency before collecting the main panel. |
| Labels | The operator can label *which fixture was applied*, and a rail/encoder can label position. Neither labels the radio's general physical cause. | [KILL] fixture labels must not be reported as ground-truth causal attribution outside the finite fault taxonomy. |
| Evaluation | At minimum, hold out complete radio-unit, anchor placement, obstruction material/position and time blocks; random packets from the same run are invalid for a transfer claim. | [GAP] Four units are insufficient for a broad device-family claim; a finite-board result is a bounded configuration result. |
| Ethics/safety | No personal data or safety actuation is needed for a non-personal slider/tool experiment. | [K] feasible within stated constraints. |
| Calendar | A December demo can read diagnostics and display a conservative `unknown`; the 2027-H1 window can run blocked repetitions. | [K] Demonstrability is not evidence of a thesis contribution. |

## Evidence ledger

| Claim | Label | Primary or official source and version/date | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| The UWB trustworthiness method assesses link, node and system indicators online; its sequential approach filters untrusted anchor links before updating the remaining state, and is local/decentralized. | [KILL] | Peterseil, Etzlinger, Horáček, Khanzadeh & Springer, [*Trustworthiness for an Ultra-Wideband Localization Service*](https://doi.org/10.3390/s24165268), *Sensors* 24(16):5268, published 2024-08-14; author PDF [version](https://www.digidow.eu/publications/2024-peterseil-sensors/Peterseil_2024_Sensors_TrustworthyUWBLocalization.pdf). | pp. 4--5, Sec. 1.3 and Fig. 2; p. 12, Sec. 4.4; pp. 16--17, Secs. 6.1--6.2. | Same observation/action family, although its service is self-localization rather than a rail logger. |
| The paper's metrics include per-link RSSI and CIR-based ML anomaly detection, distinct node metrics, and system metrics; the CIR monitor detects obstruction and active interference in its evaluated threat model. | [KILL] | Same Peterseil et al. 2024 source. | p. 10, Sec. 4.1; p. 13, Secs. 5.3--5.4 and Fig. 7. | Does not label every physical cause. That limitation supports, rather than solves, the candidate's causal-identification failure. |
| A published UWB method forms a ranging credibility evaluation, fine-grained classification by ranging-error source, and a retain/delete/mitigate policy using CIR sequence/features and range. | [KILL] | Yang et al., [*A Novel Credibility Evaluation and Mitigation for Ranging Measurement in UWB Localization*](https://doi.org/10.1016/j.measurement.2025.117721), *Measurement* 256, 117721, online 2025-05-31; [accepted manuscript PDF](https://eprints.gla.ac.uk/362922/3/362922.pdf). | Accepted manuscript PDF: pp. 2--3 (Abstract, Sec. 1 and stated contributions); pp. 8--9, Sec. 4.2; pp. 10--11, Sec. 5 and Table 2. | Direct for quality/error source triage and retain/discard; it is not proof of literal target/reference wording collision. |
| DW3xxx exposes CIR diagnostic reads, but these are not normal-operation reads; full accumulator access must happen before receiver re-enable because the accumulator is not double buffered. | [K] | Qorvo, [*DW3xxx/QM33xxx Device Driver API Guide* v4.12](https://forum.qorvo.com/uploads/short-url/xD3TlXKvkujjdUaJWXv2b4E7GQN.pdf), Release 17 / driver 08.19.02, 2025-04-23. | PDF p. 1 (v4.9 header, later history records v4.12); pp. 92--94, Sec. 5.4.1 `dwt_readaccdata`; pp. 189--190, document history / Release 4.12. | Hardware documentation, not literature novelty evidence. It makes timing and throughput a preregistered feasibility check. |
| The radio observation does not, without an independent causal witness or intervention, identify an unrestricted physical fault cause; an equally informed classifier can reproduce the proposed policy. | [KILL] | Formal observation-equivalence argument in this audit; no external source is required for the logical reduction. | “Assumption and identification audit” above. | This is a boundary result under the candidate's stated observation model; a restricted fixture classifier is still empirically testable. |

## Queries and failed searches

Queries run on 2026-08-31:

- `2024 UWB ranging NLOS reference link integrity confidence measurement paper CIR`
- `2025 UWB range quality indicator multi link reference NLOS detection paper`
- `2025 UWB ranging measurement credibility detection CIR paper open access`
- `2025 commodity UWB ranging integrity multipath edge sensor reliability paper`
- `Peterseil Trustworthiness for an Ultra-Wideband Localization Service Sensors 2024 5268 PDF`
- `A novel credibility evaluation and mitigation for ranging measurement in UWB localization pdf`
- `site:qorvo.com DWM3000 user manual CIR accumulator diagnostics register pdf`

Failed / unresolved retrieval:

- I found no primary paper with the literal fixed-rail labels `target-path ambiguous`
  and `infrastructure-wide ambiguous`. That absence is **not** a novelty finding.
- The exact raw-CIR API throughput on the eventual board/MCU/range-rate combination,
  synchronized fixture timestamps, and a stable bill of materials are [GAP].
- No result supports interpreting a reference-link pattern as universal ground truth of
  scene path, target displacement, or physical root cause.

## Decision

**KILL.** UWB-RL-CAUSE should not receive the FYP thesis slot. It collides with
multi-link UWB trustworthiness and error-source credibility systems, and its residual
cause-label claim is not identifiable from the stated passive observations. Retain only
the bounded rail experiment as a replication or negative benchmark appendix, with the
four required equal-cost baselines above and no cross-fixture causal claim.
