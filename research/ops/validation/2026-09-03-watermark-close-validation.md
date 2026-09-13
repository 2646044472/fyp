# Decision investigated: whether WATERMARK-CLOSE can let a Raspberry Pi certify an event-time window as complete, late-but-usable, or unknown using event times, source epochs, sequence numbers, ACKs, and watermarks under a delay/clock model.

# Validation Audit: 2026-09-03 WATERMARK-CLOSE

## Claim under test

The divergence packet proposes Pi-local closure of a non-personal event-time window from source epoch, sequence number, event time, and watermark. Its claim is lower closure latency or fewer `unknown` results than a fixed grace rule while controlling false `complete` under declared clock-error and maximum-delay assumptions.

The question is not whether a Pi can execute this logic. It can. The question is whether its observations distinguish an absent event from an existing event that is not yet observable, and whether the mechanism differs from ordinary source-watermark plus window-grace processing.

## Three-round novelty audit

| Round | Evidence for collision | Remaining distinction | Confidence |
| --- | --- | --- | --- |
| Component | Event time, watermarks, source progress, timers, allowed lateness, offsets, epochs, sequences, ACKs, and durable commits are established components. | Pi integration is implementation work unless it adds a source-side observation/action unavailable to ordinary stream processing. | High |
| Exact claim | Watermark semantics already cover event-time closure and late data. Kafka Streams exposes window-end-plus-grace closure. | The packet specifies no different observation model, source protocol, guarantee, or endpoint. | High |
| Boundary | Without a conformant source-progress witness, delayed-exists and never-existed worlds have the same local prefix. With a valid witness/bound, fixed grace plus contiguous sequence uses the same information. | A source closure protocol could be engineering work, but then it is the claim, not local watermark logic. | High |

## Component and exact-claim collision

[K] Akidau et al. define a watermark as a lower bound on the event times of records not yet received. Its conformance property is what makes window closure meaningful; the source must account for events, clocks, logging, storage, and communication delays. This directly collides with WATERMARK-CLOSE's completeness/latency claim.

[K] Apache Beam treats a watermark as an estimate of input completeness and combines it with windows, triggers, and allowed lateness. Kafka Streams 3.8.1 supplies the direct fixed comparator: a window closes at end plus configured grace, and later records are dropped.

[K] Kafka KIP-98 uses producer identity, epoch, sequence, acknowledgments, and transactional/durable state. These establish transport/persistence ordering, not that no future source event belongs to an already closing event-time window.

[KILL] The proposed components are direct-neighbor composition. Its only possible extra premise is a source watermark/closure record already known to be conformant. That is a source contract, not evidence created by a Pi.

## Identification and impossibility boundary

Let a window end at event time `E`. At local time `T`, let `O_T` be every record delivered to the Pi and its event time, epoch, sequence, ACKs, and any watermark computed from or carried by those records.

Construct two worlds with identical `O_T`:

1. A: no additional event with event time at or before `E` exists after the largest received sequence.
2. B: such an event exists, has the next sequence number, but remains source-buffered, partitioned, or delayed until after `T`.

The Pi must choose the same output in both worlds. A `complete` output is false in B. Sequence numbers order records that entered a stream; they do not prove a next record will never exist. An ACK proves only the progress named by its protocol. TCP sequence/ACK fields concern reliable in-order byte streams, not source-event absence. DTN Bundle Protocol likewise says it does not itself ensure destination delivery and needs extensions and/or application mechanisms for end-to-end assurance.

[KILL] A receiver-only rule cannot safely convert silence, sequence continuity, or a non-conformant watermark into `complete`. This is asynchronous indistinguishability, not a hardware limitation. Chandra and Toueg establish the relevant separation between local observations and added timing/failure-detector assumptions.

## Required assumptions

| Assumption | Why it is required | Result |
| --- | --- | --- |
| Event-time definition | Measurement, source receipt, queue admission, and transmit time have different closure semantics. | [GAP] |
| Clock bound | Include every source, Pi, reboot behavior, and synchronization failure. | [GAP] |
| Source closure semantics | A watermark/high-watermark must mean all events through `E` were accounted for before advance. | [GAP] |
| Delay/loss envelope | Cover buffering, persistence, retries, partitions, backlogs, and recovery. | [GAP] |
| ACK meaning | Must name a durable source transition, not network receipt. | [GAP] |
| Late action | `late-but-usable` needs a concrete downstream action/loss function. | [GAP] |
| Truth labels | Must distinguish no event, nonpersisted event, unsent event, and late receipt. | [GAP] |

## Direct-neighbor table

| Work | Inputs/actions | Target/evaluation | Exact overlap | What it kills or leaves |
| --- | --- | --- | --- | --- |
| Akidau et al., PVLDB 2021 | Event timestamps, watermarks, source progress, timers, windows, late data. | Formal semantics and Flink/Dataflow comparison. | Watermark-driven event-time closure. | [KILL] Source conformance is required; it cannot be inferred from receiver silence. |
| Apache Beam docs | Source watermarks, windows, triggers, allowed lateness. | Production model semantics. | Complete/late/expired handling. | [KILL] This is the standard mechanism family. |
| Kafka Streams 3.8.1 `TimeWindows` | Record timestamp, stream time, fixed grace. | Close at window end plus grace. | Strong fixed-grace comparator. | [KILL] Dynamic local threshold must beat this at equal false-complete risk. |
| Chandra and Toueg, JACM 1996 | Local observations under delay/failure. | Failure detector conditions. | Delayed source versus absent source ambiguity. | [KILL] Silence is insufficient without extra assumptions. |
| RFC 9171 BPv7 | Store/forward bundles, local delivery, status reports. | DTN transport. | Offline/IoT local closure framing. | [KILL] DTN transport does not manufacture absence evidence. |
| RFC 9293 TCP | Sequence and ACK state. | Reliable in-order bytes. | Sequence/ACK closure argument. | [KILL] ACK scope is transport, not source completeness. |
| Kafka KIP-98 | Producer ID/epoch/sequence, transactional commits. | Exactly-once messaging. | Component collision. | Leaves only a new application closure contract. |

## Strongest fixed grace plus sequence baseline

Use the strongest fair baseline rather than a naked timeout:

1. Before send, the source durably assigns `(source_epoch, seq, event_time)`.
2. For a window it durably emits an authenticated closure record `(window_end, last_seq, source_epoch)`. Its protocol meaning is: every source event at or before `window_end` has been incorporated and `last_seq` is final for that epoch/window.
3. With declared maximum delay and clock error, choose a fixed grace `G`. At `E + G`, return `complete` only when the closure record and every contiguous record through `last_seq` have arrived. Otherwise return `unknown`.
4. Report an arriving record as `late-but-usable` only if a declared application action remains valid; record later correction separately from initial closure.

This baseline uses every fact needed to make `complete` meaningful. WATERMARK-CLOSE must reduce closure latency or `unknown` at the same source contract, clock/delay envelope, false-complete definition, and held-out fault traces. With the same observations, an adaptive watermark is only a different selection of grace/policy. Without the closure record or a conformant equivalent, both methods must remain `unknown` to avoid false `complete`.

## Feasibility audit

| Area | Finding |
| --- | --- |
| Hardware | [K] Pi hardware is sufficient but irrelevant to the decision; a simulator or laptop has the same local information. |
| Source and labels | [GAP] Need a separate durable source log, fault injector, and receiver log. One process cannot truthfully label whether a missing event was never generated, lost before persistence, or merely delayed. |
| Offline/DTN experiment | [GAP] Must specify contacts, queues, retries, TTL, bundle loss, and recovery. BPv7 alone supplies no end-to-end closure proof. |
| Time/fault model | [GAP] Must predeclare clock discipline, maximum delay, partitions, reboots, and whether backlog is included. Fitting grace on the test trace leaks the answer. |
| Metrics | [GAP] Need false-complete, false-unknown, closure latency, correction delay, and task utility of late data. Receipt count/uptime is insufficient. |
| Research endpoint | [GAP] No technician/operator action or harm is specified for `late-but-usable`; without one, this is ordinary fault classification. |

A prerecorded trace can provide labels, but it removes the live source uncertainty claimed by the candidate. A live test that restores those labels requires the durable source closure witness above, converting the work into a source-protocol/crash-consistency experiment rather than Pi-local watermark research.

## Evidence ledger

| Claim | Label | Primary source/version | Exact material read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Watermarks are lower bounds on unreceived event time; conformance/liveness govern completeness. | [K] | Tyler Akidau et al., "Watermarks in stream processing systems: semantics and comparative analysis of Apache Flink and Google Cloud Dataflow," PVLDB 14(12), 2021, pp. 3135-3147, DOI https://doi.org/10.14778/3476311.3476389, full text https://www.osti.gov/servlets/purl/1823361 | Sec. 2.1 p. 3136; Secs. 4.2-4.5 pp. 3140-3141; Secs. 5.1-5.2 pp. 3142-3143. | Direct semantic collision; source accounting is load-bearing. |
| Watermarks estimate completeness; windows/triggers/allowed lateness are standard. | [K] | Apache Beam documentation, current page read 2026-09-03, https://beam.apache.org/documentation/basics/ | Watermarks, Windowing, Triggers sections. | Official implementation documentation, used for family check. |
| Window closes at end plus configured grace. | [K] | Apache Kafka Streams 3.8.1 API, https://kafka.apache.org/38/javadoc/org/apache/kafka/streams/kstream/TimeWindows.html | `ofSizeAndGrace`, `gracePeriodMs`, window-close text. | Strong fixed baseline, not a lower-bound proof. |
| Local observations cannot resolve asynchronous failure/delay without added assumptions. | [K] | T. D. Chandra and S. Toueg, "Unreliable Failure Detectors for Reliable Distributed Systems," JACM 43(2), 1996, DOI https://doi.org/10.1145/226643.226647, PDF https://www.cs.toronto.edu/~christoff/files/UnreliableFailureDetectorsForReliableDistributedSystems.pdf | Sec. 2 pp. 231-232; Sec. 6.3 pp. 248-249. | Applied as an indistinguishability boundary, not an IoT-window paper. |
| BPv7 does not itself ensure bundle delivery; app mechanisms may be necessary. | [K] | RFC 9171, Bundle Protocol Version 7, April 2022, https://www.rfc-editor.org/rfc/rfc9171.html | Sec. 5.7, Local Bundle Delivery; delivery-assurance paragraph. | Rejects DTN as automatic completeness evidence. |
| TCP sequence and ACK fields refer to stream transport progress. | [K] | RFC 9293, Transmission Control Protocol, August 2022, https://www.rfc-editor.org/rfc/rfc9293.html | Sec. 2.2; Sec. 3.2. | Event-absence limitation follows from protocol scope. |
| Epoch/sequence/transactions are standard messaging components. | [K] | Apache Kafka KIP-98, revision read 2026-09-03; last updated 2026-03-04, https://cwiki.apache.org/confluence/spaces/KAFKA/pages/66854913/KIP-98%2B-%2BExactly%2BOnce%2BDelivery%2Band%2BTransactional%2BMessaging | Motivation, Proposed Changes, message-format fields. | Component collision only; exactly-once is not event-time completeness. |

## Queries and failed searches

Queries inspected:

- `"event time watermark completeness offline IoT local closure sequence number"`
- `"watermarks in stream processing systems completeness conformance source watermark"`
- `"offline completeness watermark delayed event IoT"`
- `"DTN local event-time window closure bundle status report"`
- `"sequence number ACK bounded delay event completeness"`
- `"Kafka Streams grace period window close event time"`
- `"source watermark delay bound late data"`

Unresolved:

- [GAP] No primary paper was established for the exact Raspberry-Pi packaging. This is not a global novelty claim; it is limited to the sources and queries listed here.
- [GAP] A current 2024-2026 Pi-specific DTN local-closure citation chain was not completed before audit close. It does not preserve the candidate because direct watermark semantics, the fixed baseline, and the identification boundary already decide the stated claim.
- [GAP] The packet supplies no source protocol, timing contract, downstream utility, or label-generation plan that could define a remaining falsifiable contribution.

## Decision

KILL the positive WATERMARK-CLOSE candidate. Under a bounded, conformant source closure contract it is standard watermark/grace processing with sequence/epoch components; without that contract it cannot safely certify completeness from local observations. A narrow source-protocol demonstration could be built, but it would require a concrete downstream action and should not be presented as a novel Pi-local watermark method.

KILL
