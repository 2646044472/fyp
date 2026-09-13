# Divergence Packet: 2026-09-03 contact evidence, radio transfer, and intermittent edge directions

## Decision investigated

Generate a fresh non-biometric edge-computing direction set without requiring a confirmed field deployment. The common setting is a repeated benign decision with independently checkable truth: a local node records a non-personal bench episode while contact, energy, or evidence capacity is constrained. A Pi, codec, model, or new sensor is not treated as the contribution.

The candidates are deliberately different from the current killed optical, motor-start, harness, sensor-cause, local-schema, update, and generic scheduling claims. No candidate is promoted.

## Search boundary

Read on 2026-09-03: AGENTS.md; research/active/README.md; research/active/00-project-charter.md; research/active/01-candidate-register.md; research/ops/agent-divergence.md; and the newest 2026-09-03 divergence packets on maintenance, weak-network data plane, null boundaries, PIN-WIT, and post-START-WIT alternatives.

Search boundary: primary papers, standards, and official documentation for bundle/event-time processing, physical-versus-emulated edge evaluation, verifiable computation/provenance, intermittent computing, and tool execution validation. Where this pass did not retrieve a full exact-neighbor paper, that is marked GAP and is not used as novelty evidence. No personal data, production service, or safety actuation is assumed.

## Recent-paper limitation map

| Mechanism | Evidence and limitation | Consequence |
| --- | --- | --- |
| Intermittent contacts and record selection | RFC 9171 standardizes bundles, lifetimes, fragmentation and status information. AoI and task/semantic communication already optimize freshness or task utility. | A raw/summary/defer scheduler is insufficient. A survivor must establish a remote verification boundary, not merely throughput. |
| Event-time closure | MillWheel and current stream systems use persistent state, event time and watermarks. The active register already KILLed a local closure method when fixed watermark/grace and source sequence suffice. | Do not repackage complete/late/unknown watermark logic. |
| Provenance and verifiable computation | C2PA/NIST and ZIRCON-style integrity chains occupy ordinary provenance. Pinocchio and verifiable-computation families establish computation proofs. | A hash, signature, Merkle chain or proof system is not itself a thesis. Only a finite evidence-sufficiency boundary remains. |
| Emulation-to-physical transfer | The active camera and sensor-fault audits already show broad synthetic-versus-physical claims are occupied. Network emulators/testbeds are established infrastructure. | A radio candidate can only be a finite policy-rank transfer audit over a declared AP/device/interference/contact matrix. |
| Intermittent computing | Stash, SCHEMATIC, intermittent DVFS, intermittent inference and timely batteryless execution cover energy storage, checkpoint placement and energy-aware work. | Capacitor-voltage capture/checkpoint/schedule policies are an established mechanism family. |

## Candidate matrix

| ID | Story and harm | Exact candidate claim | Closest known work | Falsification / kill test | Feasibility |
| --- | --- | --- | --- | --- | --- |
| CONTACT-EVIDENCE | A mobile bench node completes repeated non-personal test episodes while a short network contact cannot carry every raw trace. A remote reviewer chooses close, request raw, or reopen. Closing from insufficient evidence can require an avoidable repeat visit. | For one fixed closure predicate and source trace family, characterize whether a small local evidence object, such as declared extrema/window witnesses plus integrity commitment, lets an independent verifier make the same closure decision as full raw data. This is a finite evidence-sufficiency boundary, not a compressor or provenance protocol. | RFC 9171, task/semantic communication, C2PA/NIST provenance, and Pinocchio-style verifiable computation. | Freeze predicate and trace family. Compare raw, predicate value only, fixed summary, summary plus commitment, and request-raw. Kill the positive direction if predicate value or conventional summary preserves the decision. Paired raw traces with identical evidence but different closure truth give a useful null. | Two local nodes, shaped contacts, generated low-voltage sensor or deterministic software traces, and remote verifier. Full raw retained offline is the independent truth. High feasibility; novelty depends on a nontrivial predicate and byte frontier. HOLD/PIVOT. |
| RF-EMUL-RANK | A technician configures a Pi to upload repeated non-personal bench records during brief Wi-Fi contacts. A policy selected from tc/netem traces may choose the wrong representation or retry plan when physical interference changes the contact. | For a declared contact matrix, test whether emulator-ranked raw, fixed summary, resumable-chunk, and defer policies preserve their exact record-closure/action-cost ranking on physical Wi-Fi contacts with packet capture and full-payload truth. This is not a congestion controller. | Network emulation/testbed methodology, RFC 9171 contact handling, and active physical-versus-digital rank-audit constraints. | Freeze policies and emulator traces before physical runs. Kill if ranks/frontiers agree within preregistered bootstrap intervals, if a fixed representation dominates, or if contact labels are not independently logged. A repeatable inversion is only a bounded warning for declared cells. | Pi 5, second node/AP, scripted competing traffic, packet captures and synthetic payloads. Feasible by December, but an exact modern network-neighbor audit remains GAP. PIVOT as negative benchmark. |
| CAP-OUTCOME-NULL | A capacitor-backed edge node chooses attempt capture, checkpoint, or defer before a short non-personal test event. A failed attempt loses the event; unnecessary deferral loses coverage. | Under a declared capacitor/load/event model, test whether terminal voltage and local energy history identify enough available work to guarantee an exact record. The intended result is a physical paired-world counterexample with equal policy-visible energy state but opposite completion. | Timely batteryless execution, Stash, SCHEMATIC, intermittent DVFS and inference. | Kill as a positive direction if energy-state/checkpoint baselines match. Kill the null if the declared model makes voltage plus known load sufficient. If paired worlds can be staged, report only the finite non-identifiability boundary and minimum added witness. | Capacitor/harvester emulator, MCU, controllable load and independent current logging. Benign but hardware-control heavy. KILL as new mechanism; PIVOT only as teaching/negative appendix. |
| LOCAL-TOOL-CONTRACT | A disconnected Pi receives a non-personal scripted analysis tool and decides execute, quarantine, or request contract before it writes a bench annotation. A syntactically valid package can hide input normalization, label/unit convention, or side-effect mismatch. | Construct packages that pass runtime/type checks and finite test vectors but differ in hidden semantics; measure whether signed input/output contract plus a fixture test adds value over parsing and sandbox execution. | ONNX/LiteRT validation, software test selection, model-package metadata, and the active MODEL-SPEC-NULL and SCHEMA-QUARANTINE closures. | Kill if signed contract comparison plus ordinary test is sufficient, or if the mismatch remains indistinguishable under all permitted observations. Both outcomes make it a contract control, not a method. | Software-only on Pi/public toy tools. Strong collision with already killed schema/model package candidates. KILL. |

## Top two formalizations

### CONTACT-EVIDENCE

- [D] Decision: during each short contact, a remote reviewer emits close, request raw, or reopen for one non-personal episode.
- [A] Allowed action: local node transmits raw, fixed-format evidence, or nothing; remote node verifies declared integrity and may request raw at a stated byte/contact cost. It cannot trust an unverified local predicate value as truth.
- [T] Truth: complete locally retained raw trace and closure predicate fixed before collection, for example every declared interval contains a valid timestamped record inside a numeric range. Full raw is released only to offline evaluator or after request raw.
- Observable outcome: false-close, request-raw rate, bytes/contact, close latency, verification time and policy rank on held-out trace/contact cells.
- Counterexample: two raw traces map to the same evidence object but have different predicate value. A remote rule restricted to that object must make the same decision in both worlds. A commitment does not remove ambiguity unless evidence itself proves the predicate.
- Negative-result value: a measured lower bound on what the named evidence contract cannot support, preventing a claim that summaries or hashes make a record independently auditable.

### RF-EMUL-RANK

- [D] Decision: before or during short contact, choose send raw, send fixed summary, send resumable chunks, or defer.
- [A] Allowed action: policy uses queue bytes, measured or emulated contact state and fixed payload metadata. It cannot see future physical interference or packet capture online.
- [T] Truth: independent packet trace, application checksum/reconstruction, physical contact duration and remote closure result.
- Observable outcome: false-close caused by missing/partial evidence, successful closure, bytes, goodput, joules, completion time and emulator-to-physical policy-rank correlation.
- Counterexample: two physical contacts share emulator-visible bandwidth/loss/delay but differ in burst loss, contention or handshake behavior enough to reverse two policies. Conversely, a fixed representation dominating every cell eliminates a policy contribution.
- Negative-result value: a bounded statement that the declared emulator trace family was sufficient or insufficient for ranking the declared action set on the purchased network path.

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Bundle Protocol supplies bundle, lifetime, fragmentation and status semantics while leaving application utility to endpoints. | [K] | IETF RFC 9171, Bundle Protocol Version 7, April 2022, https://www.rfc-editor.org/rfc/rfc9171.html | Secs. 1-3, 5.1-5.12 and 9, audited in the 2026-09-03 weak-network packet | Protocol standard, not a new evidence-selection result. |
| Event-time systems use timestamps, persistent state and watermarks; this does not certify a hidden late event before a boundary. | [K] | Akidau et al., MillWheel, PVLDB 6(11), 2013, https://research.google/pubs/pub41378/ | Secs. 2-4 and 6; pp. 1033-1038 and 1042-1044, audited in weak-network packet | Foundational source that blocks watermark repackaging. |
| Ordinary provenance/integrity does not establish trace semantic truth. | [KILL] | C2PA specification and NIST AI 100-4, cited in active CHAIN-REPLAY record | CHAIN-REPLAY candidate-register row read 2026-09-03 | Local collision constraint; no provenance contribution claimed. |
| General verifiable computation is established. | [KILL] | Parno et al., Pinocchio, IEEE S&P 2013, DOI https://doi.org/10.1109/SP.2013.47 | Abstract and official record reviewed 2026-09-03; full section audit GAP | Blocks a new proof-system contribution; does not decide finite byte sufficiency. |
| Broad synthetic-versus-physical claims are occupied; finite preregistered action-rank audits are the allowed residual. | [KILL] | Agnihotri et al., Are Synthetic Corruptions A Reliable Proxy For Real-World Corruptions?, arXiv:2505.04835v1, 2025-05-07, https://arxiv.org/abs/2505.04835 | Secs. 1, 3, 4.1-4.2 and 5, audited in active README | Vision/weather, not Wi-Fi. It limits only broad transfer language. |
| Intermittent computing already covers storage, checkpoints, DVFS and intermittent inference. | [KILL] | Stash, ASPLOS 2024, DOI https://doi.org/10.1145/3641511; SCHEMATIC, CGO 2024, DOI https://doi.org/10.1109/CGO57630.2024.10444789; Dynamic Voltage and Frequency Scaling for Intermittent Computing, 2025, DOI https://doi.org/10.1145/3714470 | Official abstracts/records reviewed 2026-09-03; full PDFs/sections GAP | Strong family collision for CAP-OUTCOME-NULL. |
| Active register already KILLed semantic inference for hidden model/schema changes. | [KILL] | research/active/01-candidate-register.md, SCHEMA-QUARANTINE and MODEL-SPEC-NULL rows | Rows read 2026-09-03 | Prevents relabelling an existing boundary. |
| A sub-raw evidence object preserves remote closure at declared cost. | [C] | CONTACT-EVIDENCE hypothesis | No inspected source establishes exact endpoint | Must beat predicate-only, fixed-summary, raw and request-raw controls. |
| Emulator-ranked policies transfer to physical Wi-Fi contacts. | [C] | RF-EMUL-RANK hypothesis | No inspected source establishes exact endpoint | Requires frozen policies, packet truth and held-out physical cells. |
| Local energy state identifies capture completion in the declared intermittent fixture. | [GAP] | CAP-OUTCOME-NULL hypothesis | No local fixture or energy model measurement exists | Existing intermittent work rules out generic method language. |

## Queries and failed searches

Queries run or reviewed on 2026-09-03:

- verifiable streaming computation data summaries proof edge devices
- wireless network emulator physical testbed policy ranking simulation transfer 2024
- intermittent computing energy harvesting task completion voltage sensing
- edge local large language model tool execution verification abstention
- 2025 edge device model update physical regression testing sensor deployment paper
- 2025 edge computing end-to-end data integrity intermittent connectivity sensor records paper

Unresolved items:

- [GAP] This pass did not find or fully audit a modern primary paper with the exact RF-EMUL-RANK endpoint: fixed tc/netem contact traces versus physical Wi-Fi action-rank preservation for remote record closure. This is not novelty evidence; validation must search networking venues and citation chains before promotion.
- [GAP] CONTACT-EVIDENCE needs one real preregistered closure predicate whose fixed summary is not trivially sufficient. If no such predicate can be stated without an arbitrary workflow rule, the direction is not defensible.
- [KILL] CAP-OUTCOME-NULL cannot be promoted by replacing the capacitor or adding a Pi. Its task/action family is established intermittent scheduling/checkpointing unless validation finds materially different observation or guarantee.
- [KILL] LOCAL-TOOL-CONTRACT is a schema/model contract variation of already killed candidates and should not be reopened without new physical truth and a distinct endpoint.

## Decision

1. CONTACT-EVIDENCE: HOLD/PIVOT. It is the strongest new story only as a finite independently verifiable evidence-sufficiency boundary. The first gate is a nontrivial closure predicate and a raw-trace pair that defeats candidate evidence while raw or request-raw remains correct.
2. RF-EMUL-RANK: PIVOT. It is a feasible empirical negative-result benchmark, not a network controller. Retain only if validation finds a non-duplicative exact-neighbor distinction and frozen-policy physical rank test is realistic.
3. CAP-OUTCOME-NULL: KILL as positive direction. Retain only as intermittent-computing teaching or reproduction appendix.
4. LOCAL-TOOL-CONTRACT: KILL. It reproduces local model/schema contract validation and hidden-semantic non-identifiability already in the active register.

Overall status: PIVOT

PIVOT
