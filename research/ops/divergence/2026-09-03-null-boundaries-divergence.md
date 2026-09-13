# Divergence Packet: 2026-09-03 null-boundary comparison

## Decision investigated

Whether either post-`START-WIT` negative-result candidate can become the undergraduate FYP direction rather than a known diagnosability or authorization boundary:

1. `CAUSE-NULL`: distinguish a real non-personal physical-process change from an additive sensor bias using only a permitted local trace, then identify the least independent witness that makes the pair distinguishable.
2. `OFFLINE-REV-NULL`: locally allow, defer, or deny a benign simulated bench job while disconnected after an authority may have revoked a cached capability, then identify the least freshness witness.

**Recommendation: no promotion.** Both pairs have a valid, useful local counterexample under a deliberately restricted observation model, but neither survives as a new FYP mechanism. `CAUSE-NULL` is the classical fault-isolability/sensor-placement problem in a small fixture. `OFFLINE-REV-NULL` is the standard revocation-freshness trade-off: without a fresh authority fact or an unrollbackable expiry witness, the resource cannot learn a hidden revocation; with either, normal expiry, CRL/introspection, or a revocation witness is the baseline.

## Search boundary

Read on 2026-09-03: `AGENTS.md`, `research/ops/agent-divergence.md`, `research/active/README.md`, `research/active/00-project-charter.md`, `research/active/01-candidate-register.md`, and `research/active/27-round-19-post-start-wit-reconciliation.md`.

The audit retains the charter constraints: a benign, non-personal bench story; no production or safety actuation; a runnable 2026-12 demonstration; one-year undergraduate scope; a falsifiable CS claim; and a useful null path. It excludes inventing a diagnostic classifier, a new sensor-placement algorithm, a new capability format, or a new revocation protocol. Primary research, standards, and official protocol documents were checked first. Absence of a paper matching the exact small fixture is not treated as evidence of novelty.

## Recent-paper limitation map

| Mechanism | Primary/official evidence inspected | Consequence for the candidate |
| --- | --- | --- |
| DES diagnosability | Sampath et al. define diagnosability under partial observations and establish a formal diagnoser construction. | A two-world trace construction is a direct instance of an established observation-equivalence boundary, not a new theory claim. |
| Fault isolability and sensor placement | Krysander treats sensor selection for fault detectability/isolability; Trothe et al. explicitly analyse isolability and add sensors to make a model diagnosable. | Calling the extra channel the "minimum independent witness" renames a standard isolability/sensor-placement objective unless it has a materially different theorem or deployment constraint. |
| Active diagnosis | Sampath, Lafortune and Teneketzis already study choosing controlled events to distinguish failures; the active project has separately audited modern active FDI neighbours. | A proposed probe, self-test, or active sensing intervention does not rescue `CAUSE-NULL`. |
| Offline IoT revocation | EVOKE provides credential revocation/update mechanisms for intermittently connected IoT nodes and disables trusted communication after a stale update state. | A peer-update, accumulator, epoch, or local revocation state-machine contribution is directly occupied. |
| Standard revocation freshness | RFC 7009 describes immediate server-side revocation and explicitly identifies backend interaction or short-lived tokens as the options for limiting revocation delay; RFC 7662 defines a network introspection query for current token state. | A `valid / revoked` pair with no new received fact is expected. Reintroducing contact, signed update, or lease expiry is a baseline, not a discovered witness mechanism. |
| Time and reset | X.509 CRLs contain `thisUpdate` and `nextUpdate`; their use as freshness evidence requires a current time whose rollback/reset behaviour is outside the candidate's ordinary local-state model. | A locally resettable clock/counter cannot be silently treated as a freshness oracle. A protected clock/counter is an additional trusted witness whose cost and trust assumptions must be declared. |

## Candidate matrix

No positive candidate survived the obvious collision, so this matrix contains only the two required boundary formulations rather than manufacturing three to five renamed variants.

| ID | Story and harm | Exact candidate claim | Closest known work | Falsification / kill test | Feasibility |
| --- | --- | --- | --- | --- | --- |
| `CAUSE-NULL` | A technician sees one local temperature/current/vibration trace on a benign bench and must record `process changed`, `sensor suspect`, or `unknown`. A wrong causal label sends inspection to the wrong part; `unknown` costs a repeat check. | Under a declared one-channel observation model, exhibit a physical-change world and a sensor-bias world with the same policy-visible trace. Add one independently specified channel and measure whether it separates the declared pair. No universal cause diagnosis is claimed. | Diagnosability, fault isolability, active diagnosis, and sensor placement. | **KILL as an FYP direction** if the result is merely that one measurement cannot isolate its source and a second independent sensor resolves the selected fault pair. A physical fixture that only demonstrates this textbook pair supplies no new mechanism, theorem, or system constraint. | A benign thermal/light/electrical fixture is cheap, but building trace equality and a valid independent witness creates measurement work without an identified research distinction. At most a teaching/control appendix. |
| `OFFLINE-REV-NULL` | An owner has cached authorization for a benign simulated local job during a partition. A hidden revocation makes `allow` wrong; permanent `defer` removes availability. No user identity, payment, worker-status, production service, or safety action is involved. | With capability, local policy version, link state, and resettable clock/counter as the only observations, construct valid and revoked executions with identical local state until a freshness witness arrives. Quantify only the explicitly assumed lease/contact trade-off. | RFC 7009/7662, CRL freshness, Macaroons, and EVOKE. | **KILL as an FYP direction** if a short-lived signed capability with fail-closed/defer, or normal update/introspection, implements the whole allowed design space once its maximum stale-allow window is stated. It is also killed if a protected clock/counter is simply assumed rather than supplied and costed. | Software-only and easy to demonstrate, but a partition script plus a TTL curve is a protocol tutorial/control, not a research contribution. |

## Top two formalizations

### CAUSE-NULL

- **[D] Decision:** output `process changed`, `sensor suspect`, or `unknown` for a single non-personal bench episode. The action controls only what to inspect next; it controls no production process.
- **[A] Allowed observation/action:** the decision rule receives the sampled primary trace `y(t)`, its own timestamps and declared device telemetry. It may not use fixture labels, a second reference trace, a photograph, or manual inspection before deciding.
- **[T] Truth:** a pre-registered staged cause: either a physical change in the measured quantity or a bias in the primary sensor path. A separate independently calibrated reference is used only to label the experiment.
- **Counterexample:** for any finite trace perturbation `u(t)`, let the primary channel report `y(t) = x(t) + b(t)`. World P has `x(t) = x0(t) + u(t)` and `b(t) = 0`; World B has `x(t) = x0(t)` and `b(t) = u(t)`. The allowed trace is identical, so every deterministic or randomized policy conditioned only on that trace has the same output distribution. The construction requires a physical fixture only to establish that the selected process and bias paths can be matched over its declared bandwidth; it is not a new general theorem.
- **Minimum witness:** a second channel `z(t)` may break this pair only after its independence is defined: it must respond to `x` in the selected process family, not share the staged sensor-bias path, have a clock/latency bound, and itself remain within calibration tolerance. A second copy of the same sensor on the same power/reference path is not automatically independent.
- **Observable outcome:** paired-world trace distance at the primary channel, separation error at the witness, witness cost, timing uncertainty, and residual `unknown` rate. These are a finite fixture characterization, not an estimate of general process diagnosability.
- **Negative-result value:** good experimental hygiene for any later sensor study. It tells the user exactly which causal sentence the one-channel data cannot support. It does **not** justify a standalone FYP after the direct diagnosability/sensor-placement collision.

### OFFLINE-REV-NULL

- **[D] Decision:** locally `allow`, `defer`, or `deny` a simulated benign bench job before reconnection.
- **[A] Allowed observation/action:** a previously valid signed capability, cached policy and key material, current connectivity result, and device clock/counter state. No online introspection, revocation receipt, updated CRL/accumulator witness, or non-resettable trusted-time fact is available.
- **[T] Truth:** the authority's revocation ledger records whether revocation occurred before the decision deadline.
- **Counterexample:** World V issues a capability and never revokes it. World R issues the same capability, revokes it immediately after the cache event, and partitions the node before any update is delivered. Hold every allowed local byte, clock/counter reading, policy version, and link-error trace equal. The local policy must make the same decision in both worlds, although `allow` has opposite correctness. The proof is a scoped local-observation argument, not a new revocation impossibility theorem.
- **Minimum witness:** either (a) a post-revocation authority fact such as introspection, CRL/accumulator update, or signed revocation receipt, or (b) a pre-issued expiry/lease whose comparison uses a trustworthy, non-rollbackable notion of time. A TTL only bounds stale permission; it does not reveal a revocation before expiry. A resettable OS clock or counter does not establish that bound under the stated reset model.
- **Observable outcome:** maximum stale-allow interval under a named lease, false-defer availability loss during partitions, update/contact overhead, and the exact reset/clock assumptions. A plot of these quantities has value only as a protocol-control illustration because the frontier is prescribed by the chosen witness and TTL.
- **Negative-result value:** it prevents a false claim that a cached signature remains evidence of *current* authorization after an unobserved revocation. It is less suitable than `CAUSE-NULL` even as an appendix because RFC 7009 already states the backend-interaction versus short-lived-token design space, and EVOKE directly occupies intermittently connected IoT revocation.

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Diagnosability is a formal property of a failure model observed through a partial event projection, rather than a property conferred by a classifier. | [K] | Sampath, Sengupta, Lafortune, Sinnamohideen and Teneketzis, *Diagnosability of Discrete-Event Systems*, IEEE Transactions on Automatic Control 40(9), 1995, pp. 1555-1575, DOI: https://doi.org/10.1109/9.412626 | Publisher abstract/metadata and opening problem statement, pp. 1555-1558; full IEEE PDF text was not available in this pass [GAP]. | Establishes terminology and observation-dependence, not a physical sensor-bias fixture. |
| Sensor placement for fault detectability and isolability is an established model-based diagnosis objective. | [KILL] | Krysander and Frisk, *Sensor Placement for Fault Diagnosis*, IEEE Transactions on Systems, Man, and Cybernetics Part A 38(6), 2008, pp. 1398-1410, DOI: https://doi.org/10.1109/TSMCA.2008.2003968 | Publisher metadata/abstract, pp. 1398-1399; full text unavailable in this pass [GAP]. | Directly blocks naming an additional independent channel or minimum sensor set as a new mechanism. |
| A concrete modern application analyses fault isolability, then adds sensors to achieve full diagnosability in selected scenarios. | [KILL] | Trothe et al., *Fault Isolability Analysis and Optimal Sensor Placement for Fault Diagnosis in Smart Buildings*, Energies 12(9):1601, 2019, https://doi.org/10.3390/en12091601 | Publisher/Crossref abstract, accessed 2026-09-03; publisher full text was access-blocked in this pass [GAP]. | Buildings differ from the proposed benign fixture; it is a direct endpoint collision for "measure the least new sensor that resolves an ambiguity." |
| Active diagnosis by choosing controlled events is established, so an intervention does not by itself rescue the physical candidate. | [KILL] | Sampath, Lafortune and Teneketzis, *Active Diagnosis of Discrete-Event Systems*, IEEE Transactions on Automatic Control 43(7), 1998, pp. 908-929, DOI: https://doi.org/10.1109/9.701089 | Publisher metadata/abstract; method sections not retrieved in full [GAP]. | This supports only the component collision. The current project also has a separate modern active-FDI audit. |
| Offline/IoT credential revocation with update witnesses is already an active systems mechanism. | [KILL] | Mazzocca et al., *EVOKE: Efficient Revocation of Verifiable Credentials in IoT Networks*, USENIX Security 2024, pp. 1279-1295, https://www.usenix.org/system/files/usenixsecurity24-mazzocca.pdf | Abstract/intro p. 1280; Sec. 4.2 pp. 1283-1284; Sec. 6.3 pp. 1288-1289; Sec. 7 p. 1292. | Kills an IoT peer-update, accumulator, or stale-state revocation mechanism. It does not alone prove the scoped pair construction. |
| Immediate revocation of self-contained tokens requires backend interaction if desired; short-lived tokens instead bound the exposure interval. | [KILL] | Lodderstedt, Dronia and Scurtescu, RFC 7009, *OAuth 2.0 Token Revocation*, August 2013, https://www.rfc-editor.org/rfc/rfc7009.txt | Sec. 2 pp. 3-5; Sec. 3 p. 7; Sec. 5 p. 9. | Official standard rather than research paper. It directly closes a new "TTL versus contact" revocation mechanism. |
| Token introspection is an online query for a token's current metadata, including active/expired/revoked state. | [K] | Richer, RFC 7662, *OAuth 2.0 Token Introspection*, October 2015, https://www.rfc-editor.org/rfc/rfc7662.txt | Sec. 1 pp. 2-3; Secs. 2-2.2 pp. 3-6. | Shows that this witness is online contact, not a local inference method. |
| CRL freshness is represented by `thisUpdate`/`nextUpdate`, making trusted current-time assumptions load-bearing for a local freshness decision. | [K] | Cooper et al., RFC 5280, *Internet X.509 Public Key Infrastructure Certificate and CRL Profile*, May 2008, https://www.rfc-editor.org/rfc/rfc5280.txt | Secs. 5.1.2.4-5.1.2.5, pp. 58-59; Sec. 6.3, pp. 90-94. | The standard defines fields and validation context; the reset/rollback counterexample is the present observation-model inference and must be stated as such. |

## Queries and failed searches

Queries run or checked on 2026-09-03:

- `diagnosability discrete event systems Sampath Sengupta Lafortune 1995`
- `sensor placement fault isolability structural model fault diagnosis`
- `sensor bias process fault isolation structural diagnosability`
- `active diagnosis discrete event systems controlled events fault isolation`
- `offline authorization revocation freshness leases clock reset capability credentials`
- `offline access revocation intermittent IoT verifiable credential trusted clock`
- `RFC 7009 token revocation RFC 7662 introspection RFC 5280 CRL nextUpdate`

Unresolved items:

- [GAP] No reviewed source states an exact theorem for the proposed tiny temperature/current/vibration fixture and its selected bias mechanism. That is not a novelty signal because the candidate's abstract task is already sensor-fault isolability plus added observation.
- [GAP] No reviewed source yields a distinct undergraduate-scale theorem for the exact resettable Pi clock/counter model. The local two-world argument is straightforward, but a contribution would need a materially new threat or witness model, not an unexamined variation of ordinary expiry.
- [KILL] No new candidate formulation was generated. Recasting either boundary as causal diagnosis, active probing, sensor placement, trusted-clock design, revocation propagation, or token construction would collide with the sources above or with already killed project candidates.

## Decision

1. **`CAUSE-NULL`: KILL as a primary FYP direction.** Retain only as an explicit one-channel-cannot-isolate-cause control if a later physical candidate needs it. A second witness experiment is valid measurement hygiene, but is already the standard diagnosability/sensor-placement move.
2. **`OFFLINE-REV-NULL`: KILL as a primary FYP direction.** Retain only as a short protocol counterexample/control. Offline revocation either has no freshness fact, in which case the pair is indistinguishable, or receives a standard freshness fact, in which case expiry/update/introspection is the baseline.
3. **No promotion.** The next divergence round must leave these two non-identifiability templates rather than search for another mechanism that merely hides a standard witness. It needs a materially different real decision, observation contract, action, and falsifiable endpoint.

KILL
