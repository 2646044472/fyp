# Validation Audit: 2026-09-24 new edge direction families

## Decision investigated

Independent contrarian scan of five edge-computing families that are easy to mislabel as undergraduate research novelty:

1. model update, rollback, and ML supply-chain controls;
2. flash/memory/thermal state as a cause of inference non-reproducibility;
3. device-to-device state migration and edge collaboration;
4. privacy consent, deletion, and data lifecycle enforcement;
5. edge measurement uncertainty and reproducibility.

The scan deliberately excludes the already registered Palm/visual-transport/active-sensing/stage-risk/general-scheduling directions. It does not modify `research/active/`, `research/archive/`, or `.research/`.

## Claim under test

The candidate claims below are deliberately stronger than an engineering implementation so that the audit can try to falsify them.

| Candidate label | Claim under test | Apparent reason it may look new |
| --- | --- | --- |
| `SAFE-ROLL` | A lightweight edge controller can accept, quarantine, or roll back a new model using signed provenance plus runtime health telemetry, and thereby guarantee that an update does not increase task risk without labels. | It combines model signatures, rollback, a Raspberry Pi canary, and drift/latency telemetry in one small system. |
| `STATE-REPRO` | Flash wear, memory pressure, and thermal state explain otherwise unexplained inference variation; a state-aware controller can restore reproducible output/latency across edge runs. | The same model and input can produce different latency or outputs after sustained operation, so “hardware state” sounds like an unoccupied causal variable. |
| `STATE-MOVE` | A portable checkpoint/hidden state can be moved between heterogeneous edge devices while preserving the application’s decisions and reducing interruption compared with restart. | Cross-device migration looks like a smaller edge-specific version of distributed systems migration. |
| `CONSENT-LIFE` | A local consent ledger with TTL, deletion, and audit evidence can ensure that edge data and model-derived state are processed only while consent is valid and are actually erased after revocation. | A small edge implementation could appear to turn privacy requirements into a new verifiable systems mechanism. |
| `MEAS-REPRO` | A measurement-aware uncertainty envelope, learned from edge telemetry and repeated observations, can identify when a sensor/model result is unreliable across devices without an external reference. | It joins sensor uncertainty, model confidence, and reproducibility in one edge-facing score. |

## Three-round novelty audit

| Candidate | Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- | --- |
| `SAFE-ROLL` | Component collision | TUF already specifies signed metadata, version checks, expiration/freeze protection, mix-and-match protection, and rollback rejection. Uptane specializes the same family for embedded/vehicle update threats. Minerva provides state-preserving ML model updates for deeply embedded MCUs. The 2025 ICML position paper applies supply-chain provenance and Sigstore ideas directly to ML models. | A genuinely different target could be semantic acceptance of a model under a named, independently observable safety contract. No such contract is supplied by signatures or generic telemetry. | High |
| `SAFE-ROLL` | Exact-claim collision | “Signed model + staged/canary deployment + rollback” is an ordinary MLOps/update composition. Minerva’s Chapter 3 already targets no-reboot model updates; TUF/Uptane already target rollback/freeze/integrity. A Pi implementation changes scale, not task/action/guarantee. | A claim about label-free causal risk increase might remain distinct, but it is not identifiable from input/prediction/telemetry alone. | High |
| `SAFE-ROLL` | Boundary/impossibility | Two candidate models can have identical signatures, hashes, confidence distributions, latency, temperature, and input telemetry while differing on an unobserved slice that matters to the action. Without delayed labels, an external oracle, or a restricted-shift theorem, the controller cannot know which model is safer. | A bounded negative result can construct indistinguishable telemetry worlds with opposite update decisions. A protocol implementation can remain an engineering artifact. | High |
| `STATE-REPRO` | Component collision | Edge thermal throttling and frequency management are established. Lotus studies online thermal/latency variation management for edge detectors (2024). Earlier Raspberry Pi work measured long-term visual inference under thermal throttling across models/frameworks/OSes. SAVE (ATC 2025) handles GPU-memory bit flips caused by voltage, temperature, and radiation. | A narrowly controlled Pi 5 flash/thermal matrix with exact repeated inputs could reveal a local reproducibility envelope not reported for that device/model. | High |
| `STATE-REPRO` | Exact-claim collision | The claim “telemetry predicts unstable edge inference and a controller fixes it” collides with thermal management, DVFS, reliability/fault-tolerance, and reproducibility work. The 2026 LIO letter reports non-deterministic implementations as major causes of non-reproducibility under constant experimental conditions and gives a general detection procedure. | A Pi-specific measurement study could be new as a scoped dataset, but not as a general mechanism or guarantee. | Medium-high |
| `STATE-REPRO` | Boundary/impossibility | Thermal state is confounded with governor, background load, cache/warm state, runtime/kernel version, and input order. Flash wear is not observable as a unique cause from latency/output alone. A single device also cannot support a transfer claim. If output labels are absent, changed output may be numerical nondeterminism, sensor change, or data corruption. | Preserve a negative boundary: with only device telemetry and repeated outputs, causal attribution to flash versus thermal versus software state is not identifiable; an external reference or controlled intervention is required. | High |
| `STATE-MOVE` | Component collision | CLAID provides cross-platform edge-cloud modules and an “ML-Model in the Loop” verification path for server-to-edge migration. Walle is a production device-cloud collaborative ML system with deployment, stream processing, and cross-platform compute containers. ServerlessLLM (OSDI 2024) implements checkpoint loading and live migration of LLM inference, including multi-round transfer of intermediate tokens and destination KV-cache recomputation. | A tiny-device state format or a named non-LLM task may remain a local systems exercise. It does not establish a new state-equivalence result. | High |
| `STATE-MOVE` | Exact-claim collision | “Move model/state from device A to device B with low downtime” is already the exact systems endpoint in CLAID/ServerlessLLM families. “Collaborative edge inference” is also directly occupied by Walle and the broader device-cloud literature. | A new distinction would require a different state object, adversarial failure model, or formal preservation guarantee. None is specified. | High |
| `STATE-MOVE` | Boundary/impossibility | Exact equality of decisions after migration cannot be assumed across CPU/NPU/runtime/quantization/input preprocessing. If the destination recomputes state, the claim is about semantic equivalence under a declared tolerance; if no oracle is available, semantic equivalence is only tested on a finite suite. Network interruption and partial state introduce ordinary two-phase/rollback issues. | A negative result can show that byte-identical checkpoints do not imply decision-identical outputs across two supported runtimes, or that a finite conformance suite cannot certify all inputs. | High |
| `CONSENT-LIFE` | Component collision | NIST identity/privacy guidance already frames consent as meaningful, predictable, and manageable, including alteration, deletion, and selective disclosure. NISTIR 8112 discusses consent metadata and deletion dates. IoT consent reference designs provide centralized consent management. Machine unlearning work addresses deletion of a sample’s influence; the 2025 edge-specific “Price of Unlearning” studies risks of distributed unlearning requests. | A concrete edge data-flow with a formally named retention contract may expose an implementation gap, especially for transient buffers and model-derived state. | High |
| `CONSENT-LIFE` | Exact-claim collision | “Consent token + TTL + delete local cache/log/model state + audit trail” is lifecycle engineering and governance, not a new privacy method. Unlearning and deletion-aware data selection already cover model-derived state, while ordinary secure deletion/encrypted storage cover raw buffers. | A new exact endpoint could be a machine-checkable proof of erasure under a restricted storage model; this is a systems/security proof problem, not a generic consent dashboard. | High |
| `CONSENT-LIFE` | Boundary/impossibility | A local device cannot prove deletion from remote backups, logs, swap, snapshots, wear-leveled flash, or a collaborator that already received a copy unless those components are in the threat model and provide evidence. Consent validity also cannot be inferred from the data stream. A malicious or stale consent issuer defeats local-only inference. | Preserve an impossibility/negative audit: under an explicit copy graph, identify which deletion obligations are observable and which are not. Do not collect personal or biometric data merely to demonstrate a ledger. | High |
| `MEAS-REPRO` | Component collision | NIST AI RMF requires validity/reliability assessment over intended conditions and ongoing monitoring; it emphasizes realistic test sets and methodology. Measurement science already separates accuracy, repeatability, reproducibility, calibration, and uncertainty. Recent primary work covers uncertainty-aware edge/measurement correction, while LIO work directly studies reproducibility failures. | A finite, non-personal instrument test could quantify a reproducibility envelope and expose a missing reference channel. | Medium-high |
| `MEAS-REPRO` | Exact-claim collision | “Use confidence/telemetry to abstain when edge measurements are unreliable” collides with selective prediction, calibration, conformal prediction, sensor-health monitoring, and measurement uncertainty. A confidence score is not an uncertainty guarantee without a reference and coverage assumptions. | A narrow negative result relating marginal confidence and repeated-measure reproducibility under a fixed device state may remain useful. | High |
| `MEAS-REPRO` | Boundary/impossibility | Without an independent reference, a consistently biased sensor and a correct sensor observing a shifted environment can produce the same local trace. Without repeated independent units or calibration artifacts, reproducibility and accuracy cannot be separated. | Preserve a counterexample showing identical local telemetry/confidence with opposite truth error, plus the minimum reference/intervention needed to identify it. | High |

## Assumption and identification audit

### `SAFE-ROLL`

The proposed safety decision is not identified by provenance. A signed artifact proves origin/integrity relative to a key policy, not task correctness, data representativeness, or action safety. Telemetry-only rollback additionally assumes that drift, latency, temperature, and confidence are valid proxies for task loss. A simple two-world construction defeats that assumption: the old and new models have equal telemetry and equal aggregate confidence, but the new model differs on a rare action-critical subpopulation. A controller without labels or an independent witness must make the same decision in both worlds and is wrong in one.

### `STATE-REPRO`

The causal question must separate at least: thermal state, CPU/GPU frequency, background load, memory pressure, filesystem/cache state, runtime/kernel version, random seeds, input order, sensor exposure, and bit faults. A single-board experiment that changes all of these together cannot attribute a result to flash or temperature. To identify a state effect, freeze software, inject one controlled intervention at a time, repeat across independent devices, and use an external timing/power/reference-output channel. Even then the result is a device/model envelope, not a universal edge law.

### `STATE-MOVE`

“State” must be specified: weights, optimizer state, recurrent hidden state, KV cache, preprocessing buffers, pending requests, or user-specific personalization. Byte equality is insufficient because kernels, precision, operator ordering, and sensor preprocessing can differ. A conformance claim needs an input trace, output tolerance, action equivalence rule, failure/abort semantics, and an independent reference. If the destination simply reloads and re-runs, the baseline is cold restart; if it sends only a compact state and recomputes, ServerlessLLM already supplies the relevant systems pattern.

### `CONSENT-LIFE`

The storage/copy graph is the critical missing assumption. A local ledger can govern only components that enforce the same policy and expose deletion evidence. It cannot establish what a remote peer, backup, OS swap layer, crash dump, or learned model retained unless those are included. “Consent” also has legal/contextual meaning that a technical token cannot decide. The safest undergraduate boundary is a synthetic, non-personal trace with an explicit closed-world copy graph; no claim about legal compliance or real biometric consent follows.

### `MEAS-REPRO`

Uncertainty requires a measurand, reference, error model, and coverage target. Model confidence is not a measurement uncertainty interval. Repeated local agreement can be repeatability, not accuracy. Cross-device disagreement can be due to calibration, environment, software, or sampling. Any positive claim needs independent reference measurements and a declared population of devices/conditions; otherwise the result is observational and non-identifying.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| TUF Specification v1.0.36/latest pages, current site; v1.0.27 dated 2021-12-14 | Signed metadata, versions, hashes, expiration, update client | Reject rollback, freeze, mix-and-match, arbitrary software and key-compromise paths | Directly overlaps signed update/rollback claim | Kills `SAFE-ROLL`’s protocol novelty. Leaves semantic model-safety acceptance open, but not identifiable from signatures. URL: https://theupdateframework.github.io/specification/ and https://theupdateframework.github.io/specification/v1.0.27/ |
| Uptane Standard 2.0.0 PDF, 2025 mirror; project history records 2.1.0 release 2023-06-27 | Vehicle ECU metadata, image/version state, repository/Director roles | Prevent rollback, freeze, mix-and-match, partial bundle and repository attacks | Direct embedded update/rollback neighbor | Kills “edge-specific anti-rollback” as a new mechanism. URL: https://uptane.org/assets/files/uptane-standard.2.0.0-94cd1d1cb759590fa96076b5302053bd.pdf |
| Meiklejohn et al., ICML 2025, PMLR 267:81774–81785 | Open ML models, publishers, datasets, framework provenance | Model supply-chain threats and Sigstore transparency | Direct ML-model supply-chain neighbor | Kills “sign models and record provenance” as new. Leaves a bounded device-side policy evaluation only. URL: https://proceedings.mlr.press/v267/meiklejohn25a.html; PDF: https://raw.githubusercontent.com/mlresearch/v267/main/assets/meiklejohn25a/meiklejohn25a.pdf |
| Minerva, Berkeley EECS-2024-1 technical report, 2024, Chapter 3 pp. 21–39 | MCU model image/capsule and OTA update | Low-bandwidth, state-preserving, no-reboot model update | Direct edge model-update neighbor | Kills “hot model update on constrained edge” as new. Leaves a different threat model only if precisely stated. URL: https://www2.eecs.berkeley.edu/Pubs/TechRpts/2024/Archive/EECS-2024-1.pdf |
| Zheng et al., SAVE, USENIX ATC 2025, pp. 1585–1605, §§1–3 | GPU memory bit flips, model computation, reliable memory | Maintain inference accuracy under bit flips with under 9% overhead | Direct hardware-state/reliability neighbor | Kills generic “memory faults change inference; add a detector” claim. Leaves a Pi/flash reproducibility audit, not mitigation novelty. URL: https://www.usenix.org/system/files/atc25-zheng.pdf |
| Ortega et al., Impact of Thermal Throttling on Long-Term Visual Inference in a CPU-Based Edge Device, 2020, Raspberry Pi 4B | Long-running CNN inference, frameworks, OS, cooling | Measures thermal-throttling effects on long-term inference | Direct thermal-state edge measurement neighbor | Kills “thermal state affects edge inference” as a new observation. Leaves a new device/model replication. URL: https://idus.us.es/items/0df7204b-dd10-4184-9e7e-340ef6ae72b4 |
| Huang et al., “Unveiling Non-Reproducibility in LiDAR-Inertial Odometry,” IEEE RA-L 11(1), 2026, pp. 994–1001, DOI 10.1109/LRA.2025.3636030 | Same datasets/conditions, LIO implementations | Defines noteworthy non-reproducibility, identifies five nondeterministic implementations, proposes deterministic fixes | Direct reproducibility/diagnosis neighbor | Kills broad “edge reproducibility is unexplored” claim. Leaves a scoped non-LIO negative result. URL: https://ieeexplore.ieee.org/document/11266943/ |
| Langer et al., CLAID, Future Generation Computer Systems 159 (2024), pp. 505–521, §§2 and 3.2.2 | Server test data, model/pre/postprocessing modules, Android/iOS sensors | Cross-platform edge-cloud integration and ML-Model-in-the-Loop migration verification | Direct cross-device deployment and verification neighbor | Kills “stream known-good data through a migrated model to verify edge deployment” as new. URL: https://www.research-collection.ethz.ch/server/api/core/bitstreams/40429d73-1cdc-4a39-872e-c97313ba365d/content |
| Lv et al., Walle, OSDI 2022, pp. 249–265 | Device-cloud ML tasks, streams, model/runtime components | Production-scale deployment and cross-platform execution | Direct device-cloud collaboration neighbor | Kills small-scale “device collaboration middleware” claim. URL: https://www.usenix.org/system/files/osdi22-lv.pdf |
| Fu et al., ServerlessLLM, OSDI 2024, pp. 135–153, §§3–5 | LLM checkpoints, tokens/KV cache, server storage hierarchy | Fast load and live inference migration with minimal interruption | Direct state migration and checkpoint locality neighbor | Kills “move inference state between edge nodes” as a generic novelty. URL: https://www.usenix.org/conference/osdi24/presentation/fu; PDF: https://www.usenix.org/system/files/osdi24-fu.pdf |
| NIST SP 800-63-4 Privacy Considerations, §2.4.3; NISTIR 8112 draft | Subscriber attributes, consent metadata, deletion dates | Predictability, manageability, meaningful consent, deletion/processing controls | Direct privacy consent/lifecycle requirements | Kills consent-ledger novelty as a governance concept. Leaves a closed-world enforcement audit. URLs: https://pages.nist.gov/800-63-4/sp800-63b/privacy/ and https://pages.nist.gov/NISTIR-8112/NISTIR-8112.html |
| Liu et al., “The Price of Unlearning: Identifying Unlearning Risk in Edge Computing,” ACM TOMM, article 218, 2025, DOI 10.1145/3662184 | Distributed unlearning requests and edge nodes | Identifies risks from malicious/fake unlearning requests and behavior inference | Direct edge deletion/model-state neighbor | Kills “edge unlearning/deletion risk is untouched.” Leaves a very specific closed-world protocol counterexample. URL: https://doi.org/10.1145/3662184 |
| NIST AI RMF Trustworthiness Characteristics, current web version, §3.1 | Intended-use conditions, test sets, monitoring, reliability | Validity/reliability over time and conditions, realistic test methodology | Direct uncertainty/reliability evaluation requirements | Kills generic “add an uncertainty score and monitor it” as a contribution. URL: https://airc.nist.gov/airmf-resources/airmf/3-sec-characteristics/ |

## Strongest simple baseline

The strongest combined baseline for this family is deliberately boring:

1. **Update:** TUF/Uptane-style signed manifest, monotonic version/expiration check, A/B slot or immutable previous artifact, fixed canary holdout, and manual/threshold rollback. If no trusted labels exist, abstain rather than claim risk-aware acceptance.
2. **Hardware state:** pin the governor/runtime, warm up, cool or pause at a fixed temperature band, record CPU/GPU frequency and memory pressure, and report repeated-run intervals. For memory faults, use hardware ECC/checks or a restart/retry policy; SAVE demonstrates that a real mitigation requires a defined fault model.
3. **Migration:** cold restart from a verified checkpoint, then compare against simple file/checkpoint transfer and a replayed input trace. A compact state is useful only if it beats restart under a declared output-tolerance and interruption metric.
4. **Privacy lifecycle:** encrypted local storage, explicit retention TTL, key destruction, a closed-world append-only audit log, and no model training on retained personal data. This is a control implementation, not proof of deletion outside the declared graph.
5. **Measurement:** calibration against an independent reference, repeated measurements, device/condition blocking, bootstrap confidence intervals, and an abstain/refuse rule. Any learned uncertainty model must beat fixed calibration and conformal/selective baselines at the same coverage target.

## Contrarian result

### Seemingly new but killed: `SAFE-ROLL`

The story is plausible: a Pi receives a new model, checks a signature, runs a short canary, observes confidence/latency/temperature, and automatically rolls back if the new model appears unsafe. However, the mechanisms are already split across established update security (TUF/Uptane), embedded ML updating (Minerva), ML provenance/Sigstore (ICML 2025), and ordinary canary/rollback operations. The remaining “no labels but guaranteed no increase in task risk” claim is impossible under the proposed observations: two worlds can have identical hashes, provenance, telemetry, confidence, and canary outcomes while differing on an unobserved action-critical slice. **Decision: KILL as a positive FYP method.** Keep only a protocol conformance test or a negative indistinguishability example.

### Possible negative-result boundary: `STATE-NULL` / `MEAS-NULL`

Under a closed, non-personal test setup, construct matched traces across two device states (for example, cold versus thermally throttled, or clean versus memory-pressure/cache state) with identical local telemetry summaries and identical marginal accuracy/latency summaries, but different joint tail behavior or different outputs on an independently held reference set. The result would be useful only if it demonstrates one of the following:

- marginal latency/accuracy/confidence cannot identify a state-conditioned reliability risk;
- output agreement across repeated runs does not establish measurement accuracy without a reference;
- byte-identical model state does not imply action-equivalent behavior across runtimes/devices.

This is a falsifiable boundary, not a new controller. It requires controlled interventions, independent reference measurements, repeated runs, and a clear statement of what remains unidentifiable. **Decision: PIVOT, bounded negative-result/reproducibility audit only.**

## Feasibility audit

| Risk | Finding |
| --- | --- |
| Hardware | A Pi-class board can measure temperature, frequency, memory pressure, latency, and storage behavior, but cannot emulate GPU bit flips, prove flash wear causality, or support a general cross-device theorem. A second matched board is the minimum for a device comparison. |
| Data/labels | Positive model-risk rollback and uncertainty claims need task labels or an independent reference. Without them, only protocol correctness and identifiability can be tested. |
| State migration | LLM-style state migration is not undergraduate-hardware feasible; a small model can test checkpoint transfer but the endpoint is then ordinary file transfer/restart unless a new state semantics is supplied. |
| Privacy/ethics | Real consent/deletion claims involving biometric, health, or identifiable data require an approved data-flow, participant consent, retention/deletion plan, and authorization for all copies. A synthetic closed-world test is safer but cannot establish legal compliance. |
| Supply chain/security | Signing keys, rollback attacks, malicious model artifacts, and update recovery require a defined threat model. A local demo with self-generated keys cannot support a production-security claim. |
| Reproducibility | One purchased board and one software stack yield a case study. Claims about edge devices generally require multiple units, version pinning, raw logs, repeated trials, and exact artifact release. |
| Time | A minimal negative audit is feasible within an FYP: freeze one model/runtime, define 2–3 controlled device states, collect repeated outputs/timing, and compare marginal summaries with episode/joint outcomes. Building a new updater, migration runtime, or privacy ledger is likely to consume the FYP without creating a distinct claim. |

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| TUF explicitly rejects rollback and addresses freeze, mix-and-match, arbitrary software, and key-compromise attacks. | [K] | TUF Specification v1.0.27, modified 2021-12-14; current specification index | §2.2 threat model and §5.4 timestamp/update checks; current site lists v1.0.36 | Software-update protocol, not semantic model safety. |
| Uptane is an embedded/automotive adaptation with rollback/freeze/mix-and-match threat handling. | [K] | Uptane Standard 2.0.0 PDF; project history notes 2.1.0 on 2023-06-27 | §4.3.3 and update verification text around PDF p. 30 | Automotive assumptions may not transfer directly to Pi, but the mechanism collision is direct. |
| ML model supply-chain risks and Sigstore-style transparency are directly discussed in 2025 primary work. | [K] | Meiklejohn et al., ICML 2025, PMLR 267 | Abstract and pp. 81774–81785; full PDF | Position paper, not a deployed edge updater. Still enough to kill provenance-only novelty. |
| Minerva supplies state-preserving, no-reboot ML model updates for deeply embedded MCUs. | [K] | Berkeley EECS-2024-1 technical report, 2024 | Chapter 3, pp. 21–39; especially pp. 22 and 29 | Technical report rather than peer-reviewed conference version; direct method collision remains. |
| Thermal throttling and device state materially affect long-running edge inference. | [K] | Ortega et al., Raspberry Pi 4B study, accepted/published 2020-12-10 | Full repository record and study description; exact PDF pages require local download | Older than the requested recent window, but foundational direct neighbor. |
| GPU memory bit flips caused by voltage, temperature, and radiation can corrupt inference, and SAVE mitigates a defined fault model. | [K] | Zheng et al., SAVE, USENIX ATC 2025 | pp. 1585–1587, §§1–3 | GPU memory bit flips are not the same as flash wear or ordinary Pi thermal drift. |
| Non-deterministic implementations can dominate reproducibility under constant LIO conditions. | [K] | Huang et al., IEEE RA-L 11(1), 2026 | pp. 994–1001; abstract and DOI record | LIO-specific, but it directly occupies broad reproducibility methodology. |
| CLAID verifies migrated model components using known-good server data and compares Android/iOS results. | [K] | Langer et al., FGCS 159 (2024), pp. 505–521 | §3.2.2 pp. 515–516 and §4.2 p. 517 | Digital-biomarker setting; exact task differs, migration-verification mechanism does not. |
| Walle is a production device-cloud collaborative ML system with deployment and cross-platform runtime components. | [K] | Lv et al., OSDI 2022 | pp. 249–265, abstract and §1 | Large production system; kills generic collaboration middleware novelty. |
| ServerlessLLM implements checkpoint locality and live migration of LLM inference. | [K] | Fu et al., OSDI 2024 | pp. 135–153, especially §§3–5 | GPU-server/LLM setting; exact hardware differs but state-migration endpoint is occupied. |
| Consent is required to be meaningful/predictable/manageable in applicable NIST identity/privacy guidance, with deletion/manageability considerations. | [K] | NIST SP 800-63-4 privacy page and NISTIR 8112 draft | SP 800-63-4 §2.4.3; NISTIR 8112 consent metadata/deletion-date passages | Guidance, not a theorem; kills governance-concept novelty. |
| Edge unlearning has direct risk and privacy work. | [K] | “The Price of Unlearning: Identifying Unlearning Risk in Edge Computing,” ACM TOMM article 218, 2025 | Abstract and article pp. 1–23 | Exact attack details require full-text access; enough to reject “unlearning in edge is untouched.” |
| Validity/reliability require intended-use conditions, realistic test sets, methodology, and monitoring. | [K] | NIST AI RMF Trustworthiness Characteristics, current page | §3.1, lines on pp. web sections 71–81 | Framework guidance, not a new uncertainty estimator. |
| A local telemetry-only decision cannot generally identify latent task risk or measurement error. | [C]/[GAP] | Derived counterexample in this audit, informed by the above sources | Assumption audit; no external theorem claimed | Requires a future formal construction and controlled empirical test. |
| A bounded negative reproducibility/identifiability study may be feasible on a Pi-class device. | [C] | Engineering feasibility inference from the cited methods and current project constraints | Feasibility audit | Not evidence of novelty or promotion. |

## Queries and failed searches

Search date: **2026-09-24**. Search engines and source databases inspected included USENIX, PMLR, IEEE Xplore, official NIST pages, TUF/Uptane official pages, Berkeley EECS repository, arXiv, and publisher pages.

Queries used:

- `machine learning model update rollback supply chain edge device paper 2024 2025 primary`
- `official Uptane standard rollback attack anti-rollback metadata version`
- `machine learning model supply chain security Sigstore 2025`
- `edge device machine learning reproducibility hardware nondeterminism paper 2024 2025`
- `edge device thermal throttling inference reproducibility paper 2024`
- `device cloud state migration machine learning inference 2024 2025 paper`
- `live migration LLM inference OSDI 2024 paper`
- `machine learning consent data deletion lifecycle edge devices paper 2024 2025 primary`
- `NIST privacy data processing consent deletion edge AI official 2024`
- `NIST AI RMF monitoring validity reliability reproducibility official`

Failed or insufficient searches:

- No primary paper was found that establishes a general theorem saying a Pi-class device can infer task-risk changes from temperature/flash telemetry alone. The absence is not treated as novelty evidence.
- No primary paper was found that proves deletion from arbitrary remote edge copies using a local consent ledger. The more defensible reading is that this is a threat-model/attestation problem, not an open generic FYP method.
- Search results for “reproducibility” often returned surveys, benchmark blogs, or application-specific measurement corrections. Those were used only as leads; load-bearing claims rely on the LIO primary letter, SAVE, CLAID, NIST, and the named system papers.
- Exact full-text page verification for the 2020 Raspberry Pi thermal study and ACM TOMM unlearning paper remains incomplete in this environment. Their metadata/abstract pages were not used to assert a stronger exact overlap than stated above.

## Unresolved uncertainties

1. Whether a newer 2026 primary paper has a Pi-specific flash-wear/inference-output experiment not indexed by the queried databases.
2. Whether the full ACM TOMM paper defines a threat model that exactly includes local consent revocation rather than distributed unlearning requests only.
3. Whether ServerlessLLM’s released implementation can be reduced to a non-LLM two-device workload without importing its GPU-server assumptions.
4. Whether a controlled two-device, non-personal reproducibility study would produce a sufficiently sharp negative result rather than a routine benchmark.
5. Whether the current FYP has access to an independent measurement reference and a second matched device; without both, `STATE-NULL`/`MEAS-NULL` should remain a paper-level counterexample, not an experiment.

## Decision

`SAFE-ROLL`, `STATE-REPRO`, `STATE-MOVE`, `CONSENT-LIFE`, and `MEAS-REPRO` do not survive as positive undergraduate thesis methods under the claims tested. The strongest apparent novelty, `SAFE-ROLL`, is killed by direct protocol/model-supply-chain neighbors and an unidentifiable label-free safety claim. Preserve only a tightly scoped `STATE-NULL`/`MEAS-NULL` negative-result boundary if an independent reference, controlled interventions, and repeated traces can be obtained. Do not add hardware, collect personal data, or implement a new updater/migration stack before that gate.

PIVOT

