# Divergence Packet: 2026-09-23 P1 cross-device robustness versus cross-service linkability

## Decision investigated

P1 asks whether a fixed palm feature extractor, running under a declared edge budget, can retain recognition utility across capture devices while reducing the ability of two services to link the same person. The registered wording is a **conditional protocol claim**, not permission to invent another palm network: measure a cross-device EER versus maximal-linkability frontier and test whether the frontier is monotone or not.

The current user-confirmed route is a Raspberry Pi 5 visible-light Palm Payment MVP: capture, automatic ROI, identifier-free open-set 1:N, frozen unknown rule, simulated debit and logs. The roadmap explicitly rules out cross-device research as the immediate route. Therefore P1 is a later branch and must not delay Phase 1 or be presented as the MVP's novelty.

## Search boundary

Read on 2026-09-23:

- `AGENTS.md`, `research/active/README.md`, `research/active/00-project-charter.md`, and the P1 row in `research/active/01-candidate-register.md`.
- `minutes/09-13-palm-payment-roadmap-update.md` and the archived Palm-ID reading log `research/archive/2026-08-edge-sensing/log/31-palm-id-mobile-system-reading-log.md`.
- Existing P1 packets: `research/ops/divergence/2026-08-29-palm-biometric-divergence.md` and `research/ops/validation/2026-08-29-palm-biometric-edge-audit.md`.
- X-Palm v2, Palm-ID, Shen et al. cross-device alignment, Jia et al. PalmRSS, AdaptPFL, Ali et al. cancelable palmprint, ISO/IEC 24745, Gomez-Barrero et al. unlinkability protocol, and Otroshi Shahreza et al. maximal linkability.

Search queries used:

1. `2024 2025 palmprint cross-device recognition privacy linkability biometric templates edge`
2. `2025 palmprint template inversion cross-device attack`
3. `ISO IEC 24745 biometric information protection unlinkability irreversibility official`
4. `maximal linkability biometric templates 2024`
5. `cross-device biometric recognition privacy utility tradeoff protected templates paper`
6. `edge biometric template protection latency Raspberry Pi palmprint`

This is a bounded search. Not finding a paper that joins all axes is not a global novelty result.

## Recent-paper limitation map

| Evidence | What it establishes | What it does not establish for P1 |
| --- | --- | --- |
| Shen et al., *Distribution alignment for cross-device palmprint recognition*, Pattern Recognition 132, 108942 (2022), publisher/author PDF | Cross-device RGB palm recognition is an explicit task; the paper supplies CrossDevice-A/B and a distribution-alignment loss. The task endpoint is recognition performance under device shift. | No protected-template threat model, cross-service adversary, linkability metric, revocation, or Pi resource budget. A new alignment loss would collide directly. |
| Jia et al., *Single source domain generalization for palm biometrics*, Pattern Recognition 165, 111620 (2025) | PalmRSS already targets device/environment shift from a single source using Fourier alignment, histogram matching and adversarial/feature losses. | No privacy/linkability endpoint or edge deployment proof. Generic unseen-device robustness is occupied. |
| Zhang et al., *AdaptPFL: Unlocking Cross-Device Palmprint Recognition via Adaptive Personalized Federated Learning with Feature Decoupling*, IJCAI 2025, pp. 7074-7082 | Federated personalization and feature decoupling are already used for device/lighting drift. | Federated training privacy is not the same as unlinkability of stored templates. Replacing its aggregator or adding a Pi timing table is not a P1 contribution. |
| X-Palm v2, arXiv:2606.08437v2 (2026-06-22) | Paired controlled multispectral and unconstrained smartphone acquisitions; 6,006 images, 103 participants/206 hands; cross-domain and open-set protocols; Raspberry Pi is used as a scanner control hub. | It is a dataset/recognition benchmark. Its public evaluation uses cosine gallery/probe matching and does not by itself measure protected-template linkability, multiple service keys, revocation, or the Palm Payment path. Its semi-automated ROI and compound mobile variability make device effect inseparable from nuisance effect unless the experiment is redesigned. |
| Ali et al., *Cancelable palmprint: intelligent framework toward secure and privacy-aware recognition system*, Journal on Information Security (version of record 2024-10-05) | A palm-specific cancelable scheme reports recognition plus revocability, non-invertibility and unlinkability under controlled databases. | It does not supply a paired cross-device edge protocol. Reimplementing the transform and adding two cameras would be an audit/replication unless the endpoint is a new threat or decision. |
| ISO/IEC 24745:2022 | Defines biometric-information protection requirements and terms including irreversibility, unlinkability, renewability and revocability; it separates privacy protection from general key/physical security. | It does not prescribe a palm algorithm, a Pi budget, or a particular linkability estimator. A claim must state the application model, keys, auxiliary data and attacker access. |
| Gomez-Barrero et al., *General Framework to Evaluate Unlinkability in Biometric Template Protection Systems*, TIFS 2018; arXiv version 2311.04633 | Provides score-wise/global linkability measures and a protocol using linkage functions; the framework evaluates salting, Bloom filters, homomorphic encryption and block re-mapping. | A single score-wise result is not enough: the linkage function must match the attacker, and reconstruction/statistical linkages can expose different failure modes. |
| Otroshi Shahreza, Shkel and Marcel, IEEE Access 12 (2024), 106619-106628 | Defines maximal linkability when an adversary can combine multiple similarity scores; experiments cover different systems, schemes and keys and show that extra scores/templates can increase linkability. | The experiments are not palm or Pi experiments. They nevertheless defeat the naive assumption that independent service salts automatically make a multi-service deployment unlinkable. |

## Candidate matrix

| ID | Story and harm | Exact candidate claim | Closest known work | Falsification / kill test | Feasibility |
| --- | --- | --- | --- | --- | --- |
| P1-A `FRONTIER-AUDIT` | A user enrolls with one service and later authenticates on another device/service. Device shift causes false rejects; shared or correlated protected templates enable cross-service tracking. | For one frozen extractor and fixed byte/RAM/latency/energy budget, a preregistered matrix of raw, device-normalized and service-keyed templates produces an empirical utility-linkability-cost frontier. The claim is only that the frontier is measured reproducibly; no monotonicity or superiority is assumed. | Shen 2022, PalmRSS 2025 and X-Palm occupy cross-device utility; ISO 24745, Gomez-Barrero 2018 and Ali 2024 occupy protected-template metrics. | Kill as a thesis if the frontier is reproduced by raw templates plus a standard salted transform, or if linkability is unchanged after service-keying. It remains a useful audit if the null result is complete and confidence intervals are honest. | Moderate offline computation; high data/ethics burden. Needs same identities across devices, at least two service keys, a fixed extractor, lawful biometric data, and an auditable edge budget. It is incompatible with the immediate single-Pi route until Phase 1 is stable. |
| P1-B `KEY-CROSSOVER` | Two relying parties want independent revocable templates but a user must authenticate across cameras without re-enrollment. A key rotation may either break legitimate matching or preserve a linkable representation. | Holding the extractor and device normalization fixed, service-keyed transforms can achieve a predeclared cross-device FNMR/FMR target while keeping maximal-linkability below a predeclared bound across same-person multi-key templates. The endpoint is the **key/device crossover cell**, not a new transform. | ISO 24745 renewability/revocability; Ali 2024 cancelable palmprint; maximal-linkability 2024 scenarios with different keys; X-Palm cross-domain benchmark. | A fixed salted baseline either meets the utility/privacy bound or dominates the proposed transform at equal bytes and latency. Any claim based on one key, one service or one linkage score is killed. | Feasible only as a controlled protocol using an existing transform and code. Requires key management, re-enrollment semantics, mated identities across devices, and a threat model for template-only versus score-access attackers. Edge timing is a secondary endpoint. |
| P1-C `DEVICE-NORMALIZATION-LEAK` | A provider applies device-specific normalization to recover recognition across cameras. The normalization metadata or intermediate scores may become a cross-service fingerprint even when final templates are salted. | Under fixed extractor and equal protected-template size, device normalization can reduce cross-device EER but increase maximal linkability when an attacker observes templates plus allowed metadata/scores. The proposed contribution would be a negative boundary: quantify which metadata/score disclosures create the crossover. | Shen/PalmRSS/X-Palm show device/domain variability; Gomez-Barrero and maximal-linkability define linkage evaluation; the prior packets identify multi-score and cross-device confounding. | If removing metadata and exposing only final salted templates preserves the same utility with no linkability increase, the mechanism-specific claim is killed. If linkability cannot distinguish device-known and device-hidden conditions, report a null boundary. | More realistic than designing a new transform but still needs a paired, crossed dataset and explicit attacker observations. The current Pi UI does not yet log a cross-device protocol or service metadata, so it is not executable now. |
| P1-D `PARETO-NEGATIVE` | A system designer assumes that “fixed extractor + per-service salt” gives a free privacy improvement while device-invariant representation gives free robustness. A false assurance could enable tracking or denial of service. | Under a restricted model of deterministic extractor, public device normalization, independent service salts, and template-only/multi-score attackers, construct either an empirical Pareto dominance result or a counterexample showing that no privacy gain is obtained without a utility loss or additional secret/cryptographic assumption. The result is a bounded negative statement, not a universal impossibility theorem. | ISO 24745 definitions; Gomez-Barrero linkage protocol; maximal-linkability multi-score/key scenarios; cross-device recognition papers. | The smallest counterexample is two devices, two services/keys, one fixed extractor, one standard salted baseline and one held-out identity split. If salting gives a statistically significant linkability reduction at unchanged cross-device FNMR/FMR and matched cost, the negative claim is killed. | Best scientific value per implementation effort, but it needs careful formal assumptions and enough paired identities. A null or counterexample is useful; a theorem would require a much narrower model than the current register states. |
| P1-E `EDGE-COST-FRONTIER` | A provider must choose between heavier device adaptation, larger protected templates and privacy processing on a Pi-class node. Excess cost causes timeout/thermal failure; under-protection enables tracking. | At fixed end-to-end p95 latency, peak RAM and template bytes, compare a small set of existing transforms/normalizers on cross-device utility and linkability; report a Pareto frontier and resource confidence intervals. No new model is proposed. | Palm-ID's mobile pipeline is a system precedent but not Pi end-to-end; X-Palm lists model GFLOPs; protected-template papers report accuracy/security but not this exact Pi frontier. | If one standard configuration dominates all alternatives, or if the privacy computation is negligible relative to capture/ROI and no frontier exists, the research claim collapses to deployment measurement. | Hardware is accessible in principle, but cross-device capture, service-key protocol and participant permission are not. This is an engineering audit unless the negative frontier survives strong controls. |

## Candidate details and strongest recommendation

### P1-A / P1-D pair

- **Actor and decision:** a biometric service provider decides whether to deploy a fixed extractor and a protected-template protocol across devices and relying parties; a privacy auditor decides whether a claimed privacy improvement survives an attacker with multiple service templates/scores.
- **Concrete harm:** cross-device FNMR denies a legitimate payment/access attempt; cross-service linkage creates an identity graph; a template leak is difficult to revoke because the underlying palm is not replaceable.
- **Observation/input:** raw or ROI palm samples from the same identities on at least two devices, device ID (visible/hidden according to threat model), fixed extractor output, protected templates, service key/salt, metadata and allowed scores. Identity, device, session and service must be crossed rather than inferred from pair counts.
- **Allowed action:** enrollment/re-enrollment, service-key rotation, template release or refusal, and a fixed accept/reject decision. No adaptive model update is needed.
- **Primary outcomes:** cross-device FNMR/FMR or EER at a frozen operating point; maximal-linkability and ISO-style score-wise/global linkability under template-only and multi-score attackers; template bytes, p95 latency, RAM and measured energy where available. Report identity/device/session confidence intervals, not just image-pair counts.
- **Strongest baselines:** unprotected fixed extractor; deterministic device normalization; standard per-service salting/cancelable transform; fixed two-key re-enrollment; always-recompute and no-metadata disclosure. A learned cross-device method must be compared with Shen/PalmRSS/AdaptPFL where training is allowed.
- **Smallest falsification:** two devices, two service keys, same held-out identities, one frozen extractor, one standard transform, one linkage function from Gomez-Barrero plus maximal-linkability multi-score analysis. A standard baseline that reaches the registered utility/linkability target at matched cost kills a positive method claim.

### What would count as a useful negative result

1. A reproducible counterexample showing that device normalization improves EER but makes same-person cross-service templates more linkable under a declared attacker.
2. A null result showing that service salting does not lower linkability once two scores or two keys are exposed, with confidence intervals and an explicit reason the attack surface is allowed.
3. A bounded Pareto result showing that under the Pi budget, capture/ROI dominates protected matching cost, so a claimed edge privacy mechanism cannot explain the observed deployment trade-off.

These are useful only within the declared devices, extractor, transforms, attacker observations and identity/session sample. They are not global claims about biometrics.

## Top two formalizations

### 1. Utility-linkability frontier (`FRONTIER-AUDIT`)

- **[D] Decision:** choose one deployment configuration `c` from a finite set of extractor, device-normalization, service-key and metadata-release options.
- **[A] Adversary:** observe the released protected templates and, in a separate condition, the similarity scores permitted by the service interface; test whether two records come from the same person.
- **[T] Threat/data:** a blocked identity x device x session x service design with held-out identities and at least two independent devices; fixed extractor and matched edge budget.
- **Observable outcome:** `(FNMR, FMR/EER, D_link, M_max, bytes, p95, RAM, energy)` with bootstrap/person-level intervals and a predeclared operating point.
- **Counterexample:** a standard salted template lies weakly below/left of the proposed configuration on all relevant axes, or the estimated linkability is indistinguishable from the unprotected control.
- **Negative-result value:** separates a real privacy-utility tradeoff from a measurement artifact and gives a reusable audit protocol.

### 2. Restricted no-free-lunch boundary (`PARETO-NEGATIVE`)

- **[D] Decision:** determine whether a service-keyed representation may be released as both cross-device robust and unlinkable under the restricted model.
- **[A] Adversary:** has two protected templates from the same or different services and may compute the declared similarity scores; does not see the raw palm unless the experiment explicitly adds a reconstruction condition.
- **[T] Threat/data:** deterministic fixed extractor, public device normalization, independent service salts, bounded template size and edge cost; same identities must be measured across devices and services.
- **Observable outcome:** whether any configuration improves linkability and retains utility relative to the strongest fixed baseline at matched cost; alternatively, a formal counterexample under the restricted mapping model.
- **Counterexample:** two configurations with identical utility/cost but different linkage, or a salted transform that demonstrably breaks the alleged impossibility. The latter is a positive result against the negative claim, not a failure of the experiment.
- **Negative-result value:** prevents overclaiming “on-device” or “salted” as privacy protection and can be completed without proposing a new neural architecture.

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Cross-device palmprint recognition is an explicit benchmark task with device-related image shifts | [K] | Shen et al., *Distribution alignment for cross-device palmprint recognition*, Pattern Recognition 132 (2022) 108942, https://doi.org/10.1016/j.patcog.2022.108942; author PDF https://kaiz.net/publications/pr2022distribution.pdf | Abstract; “Cross device palm datasets”; “Proposed method”; “Conclusion and future work” | RGB cross-device recognition, not privacy or Pi cost. |
| Single-source palm domain generalization already uses frequency/histogram alignment and adversarial/feature losses | [K] | Jia et al., *Single source domain generalization for palm biometrics*, Pattern Recognition 165 (2025) 111620, https://doi.org/10.1016/j.patcog.2025.111620; publisher record https://www.sciencedirect.com/science/article/pii/S0031320325002808 | Abstract; publisher highlights; full Section 1/experiments were not available in this pass | Exact page mapping and complete limitation text remain [GAP]. Do not use this source alone for a detailed method claim. |
| Federated personalization with feature decoupling already targets cross-device palm recognition | [K] | Zhang et al., *AdaptPFL*, IJCAI 2025, https://www.ijcai.org/proceedings/2025/0787.pdf | Secs. 1-4 and 6, pp. 7074-7082; PDF is 9 pages | Federated training/privacy is not template unlinkability; no direct cross-service metric. |
| X-Palm supplies paired multispectral-to-smartphone cross-domain data and a recognition benchmark | [K] | Seyedmohammadi et al., *X-Palm*, arXiv:2606.08437v2, submitted 2026-06-07, revised 2026-06-22, https://arxiv.org/html/2606.08437v2 | Abstract; Secs. 1, 2.1-2.4, 3.1-3.2, 4; Appendix A.6 listed in contents | 103 participants/206 hands overall; only 81 participants have paired scanner/smartphone data. Semi-automated ROI and compound nuisances limit causal device attribution. |
| Palm-specific cancelable protection already reports unlinkability/revocability/non-invertibility with recognition | [K] | Ali et al., *Cancelable palmprint: intelligent framework toward secure and privacy-aware recognition system*, version of record 2024-10-05, https://doi.org/10.1186/s13635-024-00179-y | Secs. 3-5 and conclusion; publisher HTML | Controlled databases and a particular transform; no paired cross-device edge protocol. |
| ISO defines unlinkability and renewability/revocability for protected biometric references | [K] | ISO/IEC 24745:2022 official browser text, https://www.iso.org/obp/ui?_escaped_fragment_=iso:std:iso-iec:24745:ed-2:v1:en | Scope; definitions 3.33-3.35; published 2022-02-08 | Normative full text may require access; it does not specify the experiment's algorithm or hardware. |
| Score-wise/global unlinkability requires an explicit linkage function and protocol | [K] | Gomez-Barrero et al., *General Framework to Evaluate Unlinkability in Biometric Template Protection Systems*, arXiv:2311.04633, 2023-11-08, https://arxiv.org/html/2311.04633 | Secs. II-VI; especially Sec. IV on measures, Sec. V protocol, Sec. VI experiments | The framework evaluates multiple protection families; a palm deployment still needs a declared attacker and linkage function. |
| Multiple protected templates, keys or scores can increase maximal linkability | [K] | Otroshi Shahreza, Shkel and Marcel, *On Measuring Linkability of Multiple Protected Biometric Templates Using Maximal Leakage*, IEEE Access 12 (2024), DOI https://doi.org/10.1109/ACCESS.2024.3433536; author PDF https://infoscience.epfl.ch/server/api/core/bitstreams/e9e420ba-16be-44be-9f7f-1e0f5a749719/content | Sec. III, Sec. IV-B3-IV-B5, Sec. IV-D, Sec. V; PDF pp. 3-10 | Face/voice experiments, not palm; it is a direct metric/threat-model boundary, not evidence about Pi measurements. |
| Palm-ID is a mobile local pipeline but its reported search timing is not Raspberry Pi end-to-end timing | [K] | Grosz, Godbole and Jain, *Mobile Contactless Palmprint Recognition: Use of Multiscale, Multimodel Embeddings*, arXiv:2401.08111v1 (2024-01-16), https://arxiv.org/html/2401.08111 | Secs. II-A/F/G, III-A/C/D, IV-A/B; local reading log records the CPU search environment and mobile pipeline | It is a useful protocol precedent, not evidence that a Pi protected-template frontier already exists. |

## Queries and failed searches

Successful queries are listed in the search boundary. The following searches were inconclusive: `2025 palmprint template inversion cross-device attack`, `edge biometric template protection latency Raspberry Pi palmprint`, and `cross-device biometric recognition privacy utility tradeoff protected templates paper`. They returned adjacent template-protection, cross-device recognition or generic edge papers, but no inspected primary paper with the exact joint endpoint of same-identity cross-device utility, multi-service linkability and Pi-class cost.

This residual is not a novelty claim. The combination may still be a protocol audit assembled from existing components. Dataset permission, IRB/consent, service-key threat model, same-identity device crossing, and implementation of maximal-linkability attacks remain unresolved.

## Feasibility and gate

The minimum gate before any P1 pilot is:

1. Freeze one extractor and one ROI/preprocessing path.
2. Obtain lawful paired captures for the same identities on at least two devices; do not reuse image-pair counts as independent people.
3. Specify service-key generation, template/metadata exposure and whether scores are available.
4. Implement the Gomez-Barrero linkage protocol and the maximal-linkability multi-score condition before collecting results.
5. Match raw, normalized and protected baselines on template bytes, p95 latency, RAM and energy where measured.
6. Run a small preflight first. If the standard salted baseline reaches the target or dominates, stop and retain the result as an audit/negative appendix.

## Decision

P1 does not support a new cross-device model or a generic protected-template thesis. The most defensible residual is `P1-D PARETO-NEGATIVE`, paired with `P1-A FRONTIER-AUDIT`, but both are blocked by the current Palm route, paired-data/permission requirements and the absence of a confirmed service threat model. No variant should be promoted before the minimum gate.

**HOLD**

