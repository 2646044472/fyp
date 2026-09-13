# Validation Audit: 2026-08-29 S1/S2 source-side outage observability

## Decision investigated

Whether S1/S2 has a defensible research object beyond this already-known boundary: a receiver that observes no source traffic cannot tell whether a source durably sampled and was partitioned or halted before sampling; whether a source-side durable record makes the two executions distinguishable after reconnection; and whether this adds anything beyond R1's crash-atomic durable-journal verifier.

## Claim under test

For a scheduled source index `j=(epoch, sequence)`, receiver observations `Y` during an outage comprise only packets already received, receiver-clock time, and heartbeat outcomes.  S2 proposes that there are two executions with identical `Y`:

- `P`: source acquires `j`, atomically persists a record binding `j` to the sample, then the network partitions; and
- `H`: source halts before acquiring `j`.

It further proposes that a trusted, durable source counter/evidence schema later distinguishes `P` from `H`, and that the smallest such observation is an FYP contribution.  This audit tests that full claim, not the weaker engineering fact that a journal is useful.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| Component collision | [KILL] The proposed epoch, monotonically increasing sequence, durable record/commit state, and post-restart recovery are standard producer-log ingredients. Kafka's adopted KIP-98 uses a producer identity, monotonically increasing per-partition sequence numbers, producer epochs, and persistent transaction state to handle retries/restarts. MQTT 5.0 separately specifies retained client/server session state and warns that implementations must assess loss/corruption of that state. R1's B-journal can store every S1 field plus the sample itself. | [GAP] Kafka is a brokered stream design, not a low-cost sensor's exact `P`/`H` post-outage lab protocol. It establishes component collision, not an exact application-paper collision. | High for components; medium for exact literature collision. |
| Exact-claim collision | [KILL] The receiver-only result is the direct two-execution indistinguishability construction, not a new detector. In an asynchronous model there is no bound on message delay, clocks, or execution time; Chandra and Toueg explicitly construct a delayed-partition execution that is indistinguishable to each partition from a crash execution up to a decision time. For S2, set `Y` to no packets over the interval in both `P` and `H`; any receiver-only `g(Y)` returns the same answer. | [GAP] I did not retrieve a primary paper with S2's exact wording, low-cost hardware, or `wait / inspect` label. This absence is not evidence of novelty. The exact paired trace is nevertheless an immediate corollary of the stated observation model, so it cannot carry a standalone algorithmic claim. | High for the boundary; low that the wording itself is a literature-first contribution. |
| Boundary / impossibility | [KILL] A later source report cannot improve the receiver's *current* distinction while the source remains unreachable: it is not in `Y`. After reconnection, an atomically committed `last_committed=(epoch,seq)` distinguishes `P` (`>=j`) from `H` (`<j`) only under the specified atomicity/storage/trust contract. A crash after acquisition but before commit is observationally equal to `H` for that record; a counter alone also fails unless it is bound to `j` and a boot epoch. | A finite post-reconnection **measurement** can report which injected crash/write windows remain ambiguous. It must be framed as a replication/boundary experiment, with B-journal and no assertion about physical correctness or about an outage-time maintenance decision. | High. |

## Assumption and identification audit

1. **Online decision is unidentifiable.**  At time `t` before reconnection, both executions yield the same no-arrival/failed-heartbeat prefix.  Extra source state has no causal path to the receiver then.  Therefore the target action cannot honestly be `wait for sync` versus `inspect source` *during* the outage unless a separately reachable witness is added.  The only sound online label is `unknown`; the source record supports retrospective reconciliation once it arrives.
2. **Counter is not synonymous with sampled-and-persisted.**  A counter increment before a sample write proves at most an attempt; an increment after a non-atomic data write can survive a torn value; a value write followed by crash before the counter cannot distinguish a genuine acquisition from `H`.  The minimal sufficient positive evidence for this narrow question is a durable state that binds the scheduled `(epoch,sequence)` to an atomic commit of the record.  For a known schedule, that can be one durable high-watermark plus an epoch and an atomic commit rule; signed batch identity, queue watermark, and a hash are not necessary unless the threat model adds rollback/tampering or later data-integrity queries.
3. **A journal absorbs the claimed observation.**  Define `B-journal` as an append-only, crash-atomic record `COMMIT(epoch, seq, read-status, value-or-null, commit-marker)` plus a recoverable high-watermark.  On reconnection, it transmits the committed range and applies the same compatible-history verifier.  It contains strictly more information than S1/S2's watermark/queue/hash schema, at the same sensor and radio budget when metadata and samples are batched.  A claimed lower-byte result against *full raw duplication* is not a mechanism win: the appropriate primary baseline is B-journal's high-watermark/range encoding, not retransmitting an entire duplicate raw log merely to answer `P`/`H`.
4. **Crash atomicity is load-bearing, not a field name.**  Storage literature notes that `fsync`/ordering and multi-page atomicity are non-trivial; an application-level commit protocol is required where storage does not provide the needed atomic update.  Therefore a claimed durable watermark is [C] until the exact MCU, flash/SD mode, record checksum/commit layout, brown-out timing, and recovery parser have been fault-injected.  It may prove local record preservation under that device model, not physical sensor truth.
5. **Provenance syntax is not trusted evidence.**  W3C PROV-DM can describe activity, generation, agents, and time, but is explicitly domain-agnostic.  A self-authored provenance event does not prove that the reported activity occurred.  Authentication/key storage is necessary for a malicious-source model; it is unnecessary overhead for the declared non-adversarial crash/partition model and does not cure a faulty/stuck sensor.
6. **Independent truth is feasible only for a narrow label.**  An independently powered MCU/logic analyser can capture a source GPIO line and clock each sample-attempt strobe cheaply enough for a benchtop protocol [C].  It is a valid evaluation trace only if its power, clock and capture path are independent of the source and the strobe is emitted at a pre-registered point.  If strobe precedes flash commit it labels attempted sampling; if it follows firmware's claimed commit it still shares the firmware's assertion and cannot prove nonvolatile persistence.  A power-cut/reboot recovery readback is required to label commit durability.  Neither instrument establishes sensor-value correctness.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Chandra & Toueg, *Unreliable Failure Detectors for Reliable Distributed Systems*, JACM 43(2), 1996 | Asynchronous messages, crash patterns, suspicion histories; reason under no timing bound. | Defines failure-detector completeness/accuracy and uses an execution whose delayed partitions are indistinguishable from crash runs. | Same information-theoretic reason a receiver cannot identify `P` versus `H` from a no-message prefix. | [KILL] framing the paired no-arrival proof as new. Leaves only a narrowly measured device/storage boundary. |
| Apache Kafka KIP-98, adopted design, current official revision 4 Mar. 2026 | Producer ID, monotone sequence, producer epoch, transaction log and a stable transaction ID across application sessions. | Idempotent/exactly-once log persistence and transaction recovery across producer restarts. | Strong component overlap with S1/S2's epoch/counter/durable watermark/recovery. | [KILL] a source-counter/epoch/commit-provenance mechanism claim. It is not an exact sensor-outage study and does not prove MCU flash atomicity. |
| OASIS, *MQTT Version 5.0*, 7 Mar. 2019 | Client/server session state, acknowledged QoS messages and delivery retry. | Network message delivery/session behavior. | Shows that retained transport state is distinct from local acquisition/persistence state. | [KILL] any claim that QoS/heartbeat alone proves `P`; supports B-journal as an application-layer requirement. |
| Park et al., *Lightweight Application-Level Crash Consistency*, USENIX ATC 2015 | Ordered persistence operations, `fsync`, logging/CoW, transactional flash commits. | Application-level all-or-nothing durable update under crashes. | Direct to S2's assertion that `durable watermark` proves a committed sample. | [KILL] treating a counter append as automatically crash-atomic. Leaves a device-specific crash-injection replication. |
| W3C, *PROV-DM: The PROV Data Model*, Recommendation 30 Apr. 2013 | Entities, activities, agents, generation/use and time. | Exchange/representation of provenance for quality/reliability assessment. | General representational overlap with a provenance schema. | [KILL] a generic provenance-schema contribution. It does not offer a trusted physical event witness or exact `P`/`H` protocol. |
| Rubambiza et al., *Demystifying Digital Agriculture*, USENIX ATC 2023 | Offline collection and an active twin that notifies on configurable missing telemetry. | Operational handling of telemetry discontinuities in digital agriculture. | Direct receiver-side outage/notification neighbor. | [KILL] a timeout/notification contribution; leaves source-persistence evidence only as an implementation detail subject to B-journal. |

## Strongest simple baseline

**B-journal range proof.**  At each scheduled `j`, locally and crash-atomically append one record containing `epoch`, `seq`, `read-status`, value/null and a checksum/commit marker.  After restart, scan to the last valid commit; after reconnection, send `(epoch, first_committed, last_committed, records)` or only the range if the task is solely `P`/`H`.  The receiver labels `P` only when the committed range contains `j`; otherwise it remains `unknown` rather than asserting `H` unless a bounded halt observation is independently available.

This subsumes S1's durable watermark, queue watermark, and batch identity.  It makes clear that the information needed for one scheduled index is a persistent distinction between committed and not-committed states, not a new signed provenance stack.  It also exposes the unresolved case: `not-committed` combines stopped-before-sampling, sampled-but-crashed-before-commit, storage failure, and a corrupt/rolled-back source under stronger threat models.

## Contrarian result

**[KILL] S2's positive claim has no remaining decision-time advantage.**  Receiver-only indistinguishability is an expected consequence of the model and the source datum becomes available only after the outage has ended.  The datum makes retrospective reconciliation more informative, but it does not distinguish a stopped source from a partitioned live source at the time an operator must choose whether to wait or inspect.

**[KILL] S1's proposed schema is not a distinguishable mechanism over B-journal.**  Under a non-adversarial, crash-atomic storage contract it is a compact projection of the journal; under a weaker contract it cannot establish `sampled-and-persistent`.  Hashes/signatures add integrity/authentication assumptions, not observational power against a storage crash.

The only honest residual is a **PIVOT** to a finite replication: map, for one device/flash implementation and preregistered cut points, which source event-orderings can be recovered by B-journal and which collapse to `unknown`.  This is useful negative evidence, but it is not a new source-observability protocol or a live failure-attribution method.

## Feasibility audit

| Item | Result | Gate consequence |
| --- | --- | --- |
| Paired receiver trace | [K] Easily reproducible: suppress all source-to-gateway traffic after a committed record in `P`; halt before the scheduled callback in `H`; receiver trace is identical by construction. | It is a demonstration/control, not evidence of a novel theorem. |
| Source durability | [GAP] ESP32 internal flash, SD card, filesystem, power-loss behavior, record encoding and brown-out cut points are unspecified. A reliable high-watermark cannot be assumed from an in-memory counter or an acknowledged application write. | No experiment may call a record durable until power-cut/reboot recovery over each transition has been measured. |
| Independent capture | [C] A second, separately powered microcontroller or logic analyser is affordable for a benchtop scheduled-strobe trace. | Freeze the strobe ordering and independently log capture-clock uncertainty. It labels attempts, not persistence, without readback. |
| Source trust | [GAP] No key/attestation, rollback, physical-access or malicious firmware assumptions are specified. | Exclude malicious-source claims. If tamper resistance is required, secure element/key custody becomes a new feasibility and threat-model gate. |
| Outcome/labels | [KILL] The proposed `wait / inspect` endpoint conflates outage-time action with post-reconnection diagnosis. | Score only retrospective `committed / uncommitted-or-ambiguous` classification, or add a genuine independent reachable witness and reopen the problem formulation. |

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| In an asynchronous system, no bound exists on message delay, clock drift or step time; failure detectors must have stated accuracy/completeness properties. | [K] | Chandra & Toueg, JACM 43(2), 1996, pp. 225-267, DOI https://doi.org/10.1145/226643.226647 ; author-hosted PDF https://www.cs.toronto.edu/~christoff/files/UnreliableFailureDetectorsForReliableDistributedSystems.pdf | Sec. 2, printed pp. 231-232; Sec. 6.3 proof, printed pp. 248-249. | Its partition/crash construction is for consensus and not an S2 exact theorem. It supports the model and indistinguishability reasoning. |
| Producer identity, monotone sequences, durable transaction state and epochs are established recovery mechanisms. | [K] | Apache Kafka, KIP-98, adopted; official page last updated 2026-03-04: https://cwiki.apache.org/confluence/spaces/KAFKA/pages/66854913/KIP-98%2B-%2BExactly%2BOnce%2BDelivery%2Band%2BTransactional%2BMessaging | Motivation; "Summary of Guarantees / Idempotent Producer Guarantees"; "Transactional Guarantees"; "Proposed Changes," items 1-5. | Broker semantics; collision is components, not exact low-end edge hardware. |
| MQTT session/delivery state does not establish durable local acquisition; nonvolatile storage before transmission is an application choice for loss-sensitive messages. | [K] | OASIS, *MQTT Version 5.0*, 7 Mar. 2019, official PDF https://docs.oasis-open.org/mqtt/mqtt/v5.0/os/mqtt-v5.0-os.pdf | Sec. 4.1-4.1.1, pp. 92-93; Secs. 4.3.2-4.3.3, pp. 94-95. | Does not define application sample provenance. It prevents using QoS as a source-persistence witness. |
| Conventional storage lacks general application-level atomicity; crash consistency requires explicit ordered persistence/logging or atomic transactional storage. | [K] | Park et al., *Lightweight Application-Level Crash Consistency*, USENIX ATC 2015, pp. 321-335, official PDF https://www.usenix.org/system/files/conference/atc15/atc15-paper-min.pdf | Sec. 1, p. 321; Sec. 2.1, pp. 322-323; Sec. 2.2 and Sec. 3, pp. 323-324. | Studied file systems/transactional flash, not the intended MCU. It makes the MCU crash model a required measurement, not an assumed fact. |
| Provenance describes entities, activities, agents, time and derivation, but is domain-agnostic. | [K] | W3C, *PROV-DM: The PROV Data Model*, Recommendation 30 Apr. 2013, https://www.w3.org/TR/prov-dm/ | Abstract and Sec. 2, especially lines/sections equivalent to pp. 1-3; Sec. 5.1 (entities/activities) and Sec. 5.3 (agents). | A vocabulary/constraint model, not an independent witness or crash-proof logging protocol. |
| FarmBIOS treats offline collection and missing-telemetry notification as operational concerns, while recognizing discontinuities from faulty sensors and human error. | [K] | Rubambiza et al., *Demystifying Digital Agriculture*, USENIX ATC 2023, official PDF https://www.usenix.org/system/files/atc23-rubambiza.pdf | Secs. 6.1-6.2, pp. 9-10; Sec. 7, pp. 10-11. | Direct receiver-side neighbor; not proof of S1/S2 exact source-record collision. |
| `P` and `H` have identical receiver observations during the partition, and an uncommitted source state cannot identify which occurred. | [KILL] logical result | S1/S2's stated observation model; instantiated paired executions in this audit. | Assumption audit items 1-3. | Conditional on no independent reachable witness and the receiver observing no source state during the interval. |
| A two-state durable high-watermark is sufficient for post-reconnection `P` evidence only when it is atomically bound to the scheduled sample record. | [C] / [GAP] | Derived from the specified two-hypothesis model; crash-model sources above identify the required atomicity issue. | Assumption audit item 2. | No formal minimality proof under reset, tamper, arbitrary schedules or arbitrary values was retrieved. Do not call it "the minimal schema." |

## Queries and failed searches

Queries run 2026-08-29:

- `"Unreliable Failure Detectors for Reliable Distributed Systems" partition indistinguishable crash PDF`
- `Kafka producer epoch sequence number durable state exactly once official KIP-98`
- `"crash consistency" durable watermark append counter atomic commit paper PDF`
- `"IoT data provenance" source durable counter sequence number offline sensor`
- `"minimal source state" distinguish network partition from process crash`
- `"sensor data" sampled persisted network partition source counter provenance`
- `MQTT 5.0 nonvolatile memory before transmission meter reading official`

Failed/limited retrievals:

- No primary source was retrieved that proves a general *minimum* source-evidence schema for S2's exact scheduled sensor model.  The result here is a narrow logical sufficiency/necessity observation, not a published lower-bound claim.
- No 2024-2026 primary paper was retrieved with S1/S2's exact low-cost paired-fault endpoint.  That is a search limitation, not evidence of novelty.
- FarmBIOS PDF text extraction did not permit a fresh line-level search in this round; the cited sections/pages were independently recorded in the supplied divergence packet and were treated only as the existing receiver-side neighbor, not as load-bearing proof of the central impossibility.

## Decision

Do not advance S1/S2 as a standalone research direction, source-evidence mechanism, or live root-cause decision.  The receiver-only result is a standard information boundary; post-reconnection durable source evidence is subsumed by R1's B-journal when crash atomicity is actually demonstrated; and the proposed independent capture cannot validate the claimed persistence without destructive recovery tests.  Retain only a clearly scoped B-journal crash-window replication/negative-result appendix if the coordinator needs an implementation control.

KILL
