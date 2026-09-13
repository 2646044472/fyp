# Divergence Packet: 2026-09-03 post-START-WIT alternatives

## Decision investigated

Whether START-WIT should remain the current physical FYP gate once two closer
mechanism families are treated as direct neighbors: (1) motor-control software
already has explicit start-up, transition, stall and fault states; and (2)
early time-series classification (ETSC) already makes a decision from a prefix
with earliness/error cost and a reject option. The second decision was whether
a substantially different non-personal, low-cost, one-year edge candidate
remains after deliberately excluding generic sensor fusion, active diagnosis,
offline log closure, schema inference, adaptive sensing and a Pi deployment as
contributions.

**Divergence conclusion:** kill START-WIT as a positive sequential-policy
method candidate. It can still be a useful low-voltage instrumentation or
negative-control fixture, but its proposed algorithmic mechanism is a
combination of established motor state handling and ETSC. Independent
validation has now also KILLed START-WIT. This packet does not alter
research/active/; it is the divergence handoff for the coordinator's next
selection gate.

## Search boundary

Read on 2026-09-03: AGENTS.md, research/ops/agent-divergence.md,
research/active/README.md, research/active/00-project-charter.md,
research/active/01-candidate-register.md, the current START-WIT
prospectus/direct-neighbor comparison/reconciliation, minutes/08-17.md, and
the edge-sensing archive README. The user constraints retained here are:

- no biometric or other personal input;
- no worker-status, payment, production-service, or safety-interlock claim;
- an affordable benchtop/software fixture and one-year FYP scope;
- a local decision under weak/unavailable connectivity, not a Pi demo;
- independent truth withheld from the proposed decision rule;
- a direct baseline and an explicit null/kill path.

Searches were restricted to original papers, standards, and vendor/runtime
documentation. A source is treated as a collision only at the stated task,
observation, action, or mechanism scope. No absence-of-search-result is
treated as novelty evidence.

## Recent-paper limitation map

| Mechanism | Primary evidence inspected | Consequence |
| --- | --- | --- |
| Motor start and fault handling | TI's *MSPM0 FOC Motor Control User Guide* defines motor-startup registers, open/closed-loop transition, MOTOR_STALL, abnormal-speed/BEMF faults, no-motor fault, voltage/load-stall and hardware-overcurrent handling. | A new controller-side started / failed / inspect state machine using current and timing is not a distinct motor-control mechanism. |
| Prefix, earliness, reject and action cost | Hatami and Chira's ETSC classifier already makes online prefix decisions with a reject option; Russwurm et al. formalize when early classification has value; earliness-aware ETSC explicitly optimizes early decision behavior. | A frozen current/accelerometer prefix policy with inspect as reject/action is ETSC plus a motor fixture unless it has a new observation/guarantee, not merely a different sensor. |
| Software-only harness diagnosis | IEEE 1149.1 provides boundary-scan interconnect test. Recent hardware/software interface-fault localization and standard board bring-up cover active pattern tests, loopback and fault isolation. | PIN-WIT cannot claim invention of active pin-pattern diagnosis. Its only possible FYP value is a constrained microcontroller-board diagnosability boundary with no DFT hardware. |
| Disconnected authorization/revocation | Macaroons establish attenuated capability credentials; X.509/OCSP-style validity and short-lived credentials provide ordinary freshness controls. | A token format or allow / defer / deny state machine is not a thesis. The remaining scientific object is the no-witness revocation indistinguishability boundary. |
| File/package preflight | Firmware/G-code parsers, simulators and model runtimes already parse, validate and reject unsupported artifacts. Their accepted input contracts do not establish hidden physical intent or undeclared preprocessing semantics. | A new checker is either standard static validation or cannot infer a hidden semantic mismatch. These are useful kill examples, not current FYP leads. |

## Candidate matrix

| ID | Story and harm | Exact candidate claim | Closest known work | Falsification / kill test | Feasibility |
| --- | --- | --- | --- | --- | --- |
| **PIN-WIT** | A technician swaps a low-cost non-personal sensor harness on a disconnected bench node. A wrong pin map, swapped data line, open, short, or pull-up fault can make subsequent bench records invalid and waste an on-site recheck. It does not control a production process. | For a declared two-MCU harness graph and finite injected-fault set, a predeclared GPIO transition codebook can decide commission / inspect / unknown and identify strictly more fault classes at a fixed test-pulse/energy budget than I2C WHO_AM_I, static plausible-range checks, a single continuity test, and a fixed all-pattern test. The possible contribution is a constrained **diagnosability boundary**, not a new tester. | IEEE 1149.1 boundary scan; active board bring-up/BIST and interface-fault localization. | Use a labelled open/short/swap/pull-up fault matrix and an external logic analyzer plus manual wiring map as truth. Kill if a deterministic fixed pattern battery or ordinary identity/continuity checks reaches the same coverage, if the required remote responder is equivalent to adding boundary-scan hardware, or if unseen harness lengths/connectors reverse the result. | Pi plus two RP2040-class MCUs, jumper harness, passive fault board, USB logic analyzer and no personal data. Cheap and runnable by December. **HOLD only as a negative/benchmark candidate; high collision.** |
| **OFFLINE-REV-NULL** | An owner of a non-critical lab fixture has cached authorization for a local test job while disconnected. A false allow after a hidden revocation causes an unapproved bench operation; false denial delays a benign test. The endpoint is a software-only simulated command, not worker access or payment. | Under observations limited to a cached signed capability, local monotonic counter/clock state, policy version and connectivity status, construct a valid-versus-revoked pair with identical permitted observations before reconnection. Prove that no local allow / defer / deny policy can guarantee both revocation soundness and availability without a named freshness witness; measure the minimum witness cost (trusted lease/clock or online revocation proof). | Macaroons; certificate expiry/revocation mechanisms; standard offline-first authorization. | The negative result fails only if an allowed local witness differs between worlds before decision time. The positive system claim is killed if conservative short-TTL signed credentials plus fail-closed/defer matches every measured frontier. A proof that merely restates certificate expiry without the declared reset/revocation model is also kill. | Two local software clients on Pi/laptop, signed synthetic capabilities, scripted partitions and a resettable counter/clock. No hardware purchase required. **PIVOT: viable only as a scoped negative security boundary.** |
| **GCODE-GATE** | A maker wants an offline Pi to decide simulate / reject / queue for a shared low-voltage 3D-printer job before consuming filament or bench time. The experiment remains in a simulator/dry-run envelope and makes no safety or production claim. | A candidate would statically prove that a G-code file respects a declared machine envelope, firmware dialect and resource budget, then reduce false-ready jobs relative to checksum, syntax parse, slicer preview and firmware parser baselines. | G-code interpreters/simulators, firmware command validation, additive-manufacturing security and process simulation (including GPAMS). | Kill if parser plus simulator already implements the invariant, if the distinction rests on manually annotated hidden intent, or if a malformed command is rejected by the normal firmware parser. A simulated execution trace is not independent proof of physical print quality. | Software-only initially; a low-cost 3D printed enclosure could be a fixture, never the contribution. Strong direct collision and weak new-CS margin. **KILL.** |
| **MODEL-SPEC-NULL** | A repair/bench node receives an edge model package while offline and must decide load / quarantine / inspect before it is used to annotate a non-personal test record. A numerically runnable model with a hidden input-normalization, label-order, aggregation or calibration mismatch can corrupt records; excessive quarantine delays the bench. | With only a signed model file, declared graph/operators, runtime metadata and finite local test inputs, construct paired packages that are observationally identical to the gate but have incompatible hidden source semantics. Establish the minimum additional witness: signed preprocessing/label contract plus a fixture test. | LiteRT/TFLite and ONNX runtime operator/model validation; model cards and MLOps artifact metadata. | Kill the positive guard if a signed explicit contract comparison is sufficient, or if hidden semantics remain indistinguishable despite every permitted test. The latter is a useful limited impossibility result but collides with the already-killed SCHEMA-QUARANTINE family if it is not materially model-specific. | Pi 5 and public toy models; no sensor data. Easy to implement but likely merely schema validation or the same non-identifiability argument. **KILL as a thesis; retain only as a control/example.** |

## Top two formalizations

### PIN-WIT

- **[D] Decision:** commission a declared low-cost sensor harness, request a physical inspection, or leave it unknown before logging ordinary bench data.
- **[A] Allowed action:** emit a finite sequence of GPIO levels/pulses and read the declared return lines. The policy cannot use logic-analyzer data, manual photos, or the fault-insertion labels at decision time.
- **[T] Truth:** a manually documented wiring graph plus independent logic analyzer capture and staged physical fault label for each episode.
- **Observable outcome:** unique fault-class coverage, ambiguity rate, false-commission rate, test duration, GPIO pulses, joules and robustness to held-out harness length/connector cells.
- **Counterexample:** if two harness faults induce exactly the same allowed input-output relation for every permitted pattern, no policy can distinguish them. If a fixed exhaustive pattern set identifies every staged fault, an adaptive/information-gain policy has no mechanism claim.
- **Negative-result value:** establishes the exact fault classes that software-only edge commissioning cannot identify without a physical test point, boundary-scan support, or changed harness design.

### OFFLINE-REV-NULL

- **[D] Decision:** locally allow a simulated benign bench job, defer it until contact, or deny it.
- **[A] Allowed action:** inspect a capability signature/caveats, cached policy version, local counter/clock state and link state. No online query, trusted revocation receipt, or physical user identity is available.
- **[T] Truth:** a controller-held revocation schedule and independent trace of whether the authority revoked before the decision deadline.
- **Observable outcome:** a pair of executions with equal local observations before the deadline but opposite correct allow decision, plus the availability loss induced by the smallest permitted witness.
- **Counterexample:** World A never revokes a capability; World B revokes it immediately after cache issuance. Hold the local capability, device clock, counter, policy version and partition trace equal. Every local policy has the same pre-contact output in both worlds.
- **Negative-result value:** makes the practical cost of a trusted clock, short lease, revocation receipt, or deferred operation explicit rather than inventing a new offline token scheme.

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| TI's MSPM0 FOC software includes start-up configuration, transition to closed loop, motor-stall/abnormal-speed/BEMF/no-motor faults and customized-board verification. | [KILL] | Texas Instruments, *MSPM0 FOC Motor Control User Guide*, document SLUUDM5, revised 2026, https://www.ti.com/lit/ug/sluudm5/sluudm5.pdf | Table of contents and Secs. 5.3.2.2.2 (MOTOR_STARTUP1), 7.7.1.1-7.7.1.6 (startup, transition, fault handling), and 8.4 (custom-board verification), downloaded 2026-09-03 | This is sensorless BLDC/FOC documentation, not the exact low-voltage fan fixture. It nevertheless directly blocks presenting start/fault state handling as a new controller mechanism. |
| Early prefix classification with reject is established. | [KILL] | Hatami and Chira, *Classifiers With a Reject Option for Early Time-Series Classification*, IEEE Symposium on Computational Intelligence and Ensemble Learning, 2013; arXiv v1 2013-12-14, https://arxiv.org/abs/1312.3989 | Abstract and paper Secs. 1-4, PDF pp. 1-8 | Uses odor/gas signals rather than motor sensing. It establishes the prefix-plus-reject mechanism, not the physical shaft label. |
| ETSC requires a genuine accuracy/earliness tradeoff rather than merely stopping early. | [K] | Russwurm et al., *Early Classification of Time Series is Meaningful*, 2021; arXiv v2, https://arxiv.org/abs/2104.13257 | Abstract, Secs. 1-4 and conclusion, downloaded 2026-09-03 | The paper is a theory/method critique. It reinforces the need for a nontrivial decision difference; it does not prove every motor endpoint is occupied. |
| Boundary scan is a standard architecture for board-level interconnect testing. | [KILL] | IEEE, *IEEE Standard for Test Access Port and Boundary-Scan Architecture*, IEEE 1149.1-2013, official record https://standards.ieee.org/ieee/1149.1/6465/ | Official scope/abstract and interconnect-test description, accessed 2026-09-03 | A low-cost MCU harness may not expose boundary-scan cells. PIN-WIT can only study what software-only test can and cannot recover under that explicit limitation. |
| Capability credentials can be attenuated with contextual caveats. | [KILL] | Birgisson et al., *Macaroons: Cookies with Contextual Caveats for Decentralized Authorization in the Cloud*, NDSS 2014, https://research.google/pubs/pub41892/ | Secs. 2-6, PDF pp. 2-8 | Cloud rather than a disconnected Pi. It kills a claim to invent a capability format; it leaves only an explicit local-freshness boundary. |
| Firmware/G-code processing and additive-manufacturing simulation are established tool families. | [KILL] | Liu et al., *GPAMS: A G-code processor for advanced additive manufacturing simulations*, Additive Manufacturing 68 (2023), article 103279, DOI https://doi.org/10.1016/j.addma.2022.103279 | Abstract and Secs. 1-3 as available from publisher record, accessed 2026-09-03 | Simulation is not a proof of physical print quality, but it is a direct collision for a generic G-code parser/simulator contribution. |
| Model-format/runtime checks validate declared graph/operator compatibility, not an undeclared preprocessing or label semantic. | [K] | ONNX, *ONNX IR Specification*, current official specification, https://onnx.ai/onnx/repo-docs/IR.html ; Google AI Edge, *LiteRT Model Analyzer*, official documentation, https://ai.google.dev/edge/litert/models/model_analyzer | ONNX IR ModelProto/opset sections and LiteRT Model Analyzer usage/operation listing, accessed 2026-09-03 | This is a runtime/documentation boundary, not a primary research result. It supports treating MODEL-SPEC-NULL as a schema/semantics collision rather than a fresh model method. |
| The active project already established hidden semantic-change non-identifiability and standard contract/quarantine baselines. | [KILL] | Local primary decision record: research/ops/validation/2026-09-03-schema-quarantine-validation.md | Decision, counterexamples and evidence ledger read 2026-09-03 | This is not independent literature evidence. It prevents relabelling the same schema argument as a model-package topic. |

## Queries and failed searches

Queries run/reviewed on 2026-09-03:

- TI MSPM0 FOC startup motor stall BEMF fault handling user guide
- early time series classification reject option earliness cost primary paper
- early classification meaningful prefix reject time series paper
- IEEE 1149.1 boundary scan interconnect testing standard official
- embedded GPIO loopback wiring fault diagnosis primary paper
- offline authorization revocation disconnected trusted clock capability token primary paper
- 3D printer G-code static analysis verification simulator primary paper
- ONNX model compatibility validation operator support edge runtime official documentation

Failed or unresolved checks:

- No primary source was found in this pass that proves an exact match to the proposed PIN-WIT finite, software-only, no-boundary-scan diagnostic matrix. This is a **gap to validate**, not novelty evidence; IEEE 1149.1 is a strong mechanism collision.
- No audited source in this pass gives a nontrivial offline-revocation theorem for exactly the declared Pi counter/clock reset model. The paired-world proof must be written from the specified observation model and audited by validation before it can be a research direction.
- No additional physical sensor, motor, camera, larger model, or cloud service is justified by these candidates. Hardware purchase before the above distinguishability tests would be evidence-free.

## Decision

1. **START-WIT: KILL as a positive sequential-policy/method direction.** The motor-specific start/fault mechanism and the ETSC prefix/reject/cost mechanism are each already occupied. A shaft-start bench can remain an engineering demonstration or a measurement control, but not the thesis contribution merely by combining those mechanisms.
2. **PIN-WIT: HOLD only for independent validation as a constrained diagnosability/negative benchmark.** It is the sole candidate here with a potentially different physical observation contract, but it must beat or delimit fixed patterns and boundary-scan-style controls before any positive claim.
3. **OFFLINE-REV-NULL: PIVOT as the best useful negative-result path.** It is feasible, non-personal and formal, but should not be dressed up as a new authorization protocol.
4. **GCODE-GATE and MODEL-SPEC-NULL: KILL.** They reproduce established parser/runtime validation or the already-killed hidden-semantic-change boundary.

Overall status: **PIVOT**. No new thesis direction is promoted from this
divergence pass. The next validation work is limited to killing PIN-WIT against
fixed-pattern/boundary-scan controls and checking whether OFFLINE-REV-NULL is
anything more than a standard certificate-freshness observation.

PIVOT
