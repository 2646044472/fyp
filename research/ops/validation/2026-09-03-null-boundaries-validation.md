# Decision investigated: whether CAUSE-NULL and OFFLINE-REV-NULL survive direct FDI/sensor-placement and revocation-freshness audits

## Decision investigated

`CAUSE-NULL` would use one non-personal temperature/current/vibration trace to
choose `equipment changed`, `sensor suspect`, or `unknown`, then demonstrate a
process-change/sensor-bias pair and an alleged minimum added witness.
`OFFLINE-REV-NULL` would use a cached signed capability during a partition to
choose `allow`, `defer`, or `deny`, then demonstrate valid/revoked worlds with
the same local state and an alleged minimum freshness witness.

## Claim under test

The question is whether the two proposed negative results provide a distinct,
one-year FYP contribution rather than instantiate established FDI fault
isolability/sensor placement or ordinary PKI revocation freshness.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| CAUSE-NULL component | FDI uses residual/fault signatures to distinguish process and sensor faults. Krysander and Frisk formulate adding sensors to meet stated detectability and isolability requirements. | A cheap fixture may illustrate one selected ambiguity; it adds no diagnostic mechanism. | High |
| CAUSE-NULL exact claim | The proposed process-change versus sensor-bias pair is exactly a fault-isolability question. Choosing a witness to break it is sensor placement. | No inspected source uses the exact low-cost fixture. Missing a fixture tuple is not a task, action, or guarantee distinction. | High |
| CAUSE-NULL boundary | With unrestricted process change and bias, one trace is non-identifying. With a declared model/fault set, established residual/structural analysis determines isolability and required sensors. | A finite fixture can measure one staged pair, not a general "minimum witness." | High |
| OFFLINE-REV-NULL component | CRLs, OCSP, cached status, expiry/leases, stapling, and fail-closed versus soft-fail are standard revocation mechanisms. | Pi plus a benign simulated job changes packaging only. | High |
| OFFLINE-REV-NULL exact claim | A cache cannot observe a remote revocation after caching. RFC 6960 supplies status-time semantics; RFC 5019 specifies cached-response freshness and accurate-time requirements. | The exact bench-job story is not a distinct observation or guarantee. | High |
| OFFLINE-REV-NULL boundary | Without updated status, a revocation receipt, or a precommitted lease interpreted by trusted monotonic time, valid and revoked worlds have identical local state. With one, the result is ordinary freshness handling. | A reset-specific script is a threat-model illustration, not a new authorization result. | High |

## Assumption and identification audit

### CAUSE-NULL

Let permitted observation be one trace plus equal device telemetry:

```text
o_t = h(x_t) + b_t + n_t,
```

where `x_t` is process state, `b_t` is sensor bias/gain expressed in output
units, and `n_t` is noise. Choose healthy `x_0` and a process deviation `d_t`.
The two worlds

```text
P: x_t = x_0 + d_t, b_t = 0
S: x_t = x_0,       b_t = h(x_0 + d_t) - h(x_0)
```

produce the same permitted trace. Every policy with only that trace must have
the same action distribution in P and S, so either cause label is wrong in one
world; `unknown` is the sound baseline.

[KILL] This is the standard FDI detectability/isolability problem, not a new
physical theorem. The claimed witness is either unrestricted, where no finite
passive witness is generally minimal because another unmodelled process change
can imitate it, or restricted, where the answer depends on an explicit process
graph, fault set, noise model, test assumptions, and placement cost. In the
restricted case it is sensor placement/FDI. The fixture can only show that one
named channel separates one preregistered staged pair.

### OFFLINE-REV-NULL

Let local observation at time `t` be

```text
O_t = (cap, signature, caveats, policyVersion, counter, localClock, linkDown).
```

No online query, newer signed status, trusted external event log, or physical
identity witness is permitted. Compare a world V where the authority never
revokes `cap` with a world R where it revokes immediately after cache issuance.
Hold every component of `O_t` equal. The correct allow decision differs, but
`O_t(V) = O_t(R)`.

[KILL] No policy can both always allow a valid cached capability and never
allow a remotely revoked one under that observation model. A local counter
contains no unreceived remote event. A clock helps only when it is non-rollback
and the issuer precommitted a signed expiry/lease; that gives the conventional
maximum-staleness bound. A resettable clock/counter only weakens the guarantee.
RFC 5019 Section 7.1 explicitly warns that a slow clock can accept expired
valid responses for certificates that may be revoked.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Krysander and Frisk, 2008 | Structural process model, faults, existing/addable sensors. | Select sensors for detectability/isolability requirements. | CAUSE-NULL's minimum witness. | [KILL] Generic witness/placement claim; leaves only a finite replication under a different declared model/cost. |
| Staroswiecki and Commault, 2001 | Analytical redundancy relations and residual generation. | Model-based FDI detectability/isolation. | Process-versus-sensor-fault signature ambiguity. | [KILL] A model-free cause claim. |
| RFC 6960, 2013 | Signed OCSP status with `thisUpdate`, `nextUpdate`, `producedAt`, revocation time. | Status and freshness semantics. | OFFLINE-REV-NULL freshness witness. | [KILL] New cached-status inference. |
| RFC 5019, 2007 | Cached OCSP responses, signed time fields, client time, nonce option. | Freshness and replay risk. | Cached state plus trusted-clock requirement. | [KILL] Short-TTL/cache experiment as a new mechanism. |
| Smith et al., NDSS 2020 | Pull/push/network-assisted revocation and cache behavior. | Timeliness, availability, failure handling. | Allow/defer/deny availability-security tradeoff. | [KILL] Pi-local revocation-distribution tradeoff. |

## Strongest simple baseline

### CAUSE-NULL

1. **Sound abstention:** output `unknown` whenever the declared one-channel
   signature is compatible with both causes.
2. **Declared-model FDI:** construct the ordinary residual/fault-signature
   table for the finite fixture and identify its detectable/isolable faults.
3. **Fixed witness/placement control:** choose the extra reference channel or
   controlled excitation from that table before outcomes are opened.

If the proposed witness equals the fixed control, it is an FDI replication. If
it assigns a cause despite overlapping signatures, the pair defeats it.

### OFFLINE-REV-NULL

1. **Fail closed/defer:** never use cached authorization while disconnected.
2. **Signed short lease:** allow only within a precommitted expiry interval
   according to a non-rollback trusted clock.
3. **Fresh signed status:** accept a cached OCSP/CRL-style receipt only when
   its signature and `thisUpdate`/`nextUpdate` interval are valid; otherwise
   defer until an update is obtained.

Every policy with a freshness witness is one of these standard designs; every
policy without one faces the valid/revoked pair.

## Contrarian result

[KILL] `CAUSE-NULL` is either a textbook/model-free confounding example or an
established FDI and sensor-placement instance once formalized. A staged load
change and sensor bias are useful laboratory controls, not a new FYP mechanism.

[KILL] `OFFLINE-REV-NULL` follows directly from an unobserved remote revocation.
Standards already provide the cache/clock/freshness controls, and revocation
systems already study timeliness and availability. Resetting a clock is not a
new result; it demonstrates that trusted time was required.

## Feasibility audit

| Candidate | One-year implementation feasibility | One-year FYP research feasibility | Consequence |
| --- | --- | --- | --- |
| CAUSE-NULL | A low-voltage fixture, injected bias, reference sensor, and staged labels are feasible. | Poor: substantial fixture work yields only finite FDI replication and cannot repair the collision. | Do not buy/build as primary thesis gate. |
| OFFLINE-REV-NULL | Pi/laptop simulation with signed test capabilities, partitions, and an inert command is easy. | Poor: the proof is immediate once `O_t` is stated; simulation only replays injected schedules. A meaningful security result needs a different protocol/threat model. | Do not build as a thesis system. |

Neither candidate has a credible December demo plus 2027-H1 expansion path with
an independent FYP contribution. Both can remain short negative-control
examples only.

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Sensor placement targets detectability and isolability requirements. | [K] | M. Krysander and E. Frisk, "Sensor Placement for Fault Diagnosis," IEEE TSMC-A 38(6), 2008, pp. 1398-1410, DOI https://doi.org/10.1109/TSMCA.2008.2003968; record https://ieeexplore.ieee.org/document/4648949 | Abstract and publisher record, accessed 2026-09-03; VOR pp. 1398-1410. | Full VOR was access-restricted, so no more specific theorem is attributed. |
| Analytical redundancy relations are an established FDI family. | [K] | M. Staroswiecki and M. Commault, "Analytical Redundancy Relations for Fault Detection and Isolation in Algebraic Dynamic Systems," Automatica 37(5), 2001, pp. 687-699, DOI https://doi.org/10.1016/S0005-1098(01)00005-X | Title and publisher metadata checked 2026-09-03. | Used only for the established FDI family; the specific pair is proved above. |
| OCSP defines status-time semantics. | [K] | RFC 6960, 2013, https://www.rfc-editor.org/rfc/rfc6960.html | Section 2.4, p. 9; Sections 4.2.2.1-4.2.2.2. | It does not itself make an offline cache current. |
| Cached OCSP freshness needs signed time fields and accurate time. | [K] | RFC 5019, 2007, https://www.rfc-editor.org/rfc/rfc5019.html | Sections 2.2.4 p. 7, 4 p. 8, 7.1 p. 12, 7.5 p. 13. | Direct cache/clock baseline; not a general impossibility theorem. |
| Revocation systems already study cache availability, timeliness and failure behavior. | [K] | T. Smith, L. Dickinson, K. Seamons, "Let's Revoke: Scalable Global Certificate Revocation," NDSS 2020, DOI https://doi.org/10.14722/ndss.2020.24084, PDF https://www.ndss-symposium.org/wp-content/uploads/2020/02/24084-paper.pdf | Abstract and Section I p. 1; cache/soft-fail related work pp. 2-3. | Web-PKI scope, but directly collides with the revocation-distribution tradeoff. |
| Macaroons already provide contextual capability credentials. | [K] | A. Birgisson et al., "Macaroons," NDSS 2014, https://research.google/pubs/pub41892/ | Sections 2-6, PDF pp. 2-8, rechecked 2026-09-03. | Kills a new capability format, not the logical pair alone. |
| The two pairs are indistinguishable under their declared observations. | [K] | Direct construction in this audit. | Assumption and identification audit above. | Depends on withholding the stated independent witness; not claimed as a new general theorem. |

## Queries and failed searches

Queries run on 2026-09-03:

- `"Sensor Placement for Fault Diagnosis" Krysander Frisk PDF`
- `fault isolability sensor placement process fault sensor fault primary paper`
- `analytical redundancy relations sensor fault process fault isolation`
- `offline certificate revocation freshness trusted clock cache primary paper`
- `certificate revocation cached status soft fail trusted time RFC`
- `offline authorization revocation disconnected trusted clock capability token primary paper`
- `certificate revocation impossibility offline cache freshness`
- `"Let's Revoke" scalable global certificate revocation PDF`

[GAP] No inspected source uses the exact cheap CAUSE-NULL fixture or resettable
Pi counter. These are not novelty evidence: the claimed cause/witness and
cache/freshness mechanisms are already decided by the direct-neighbor families
and the explicit observation models.

## Cross-packet reconciliation and next boundary

**No disagreement.** The divergence packet's final conclusion that both
`CAUSE-NULL` and `OFFLINE-REV-NULL` are KILL agrees with this validation
audit. The only earlier difference was sequencing: divergence had retained
`OFFLINE-REV-NULL` as a possible scoped negative boundary pending an exact
clock/reset audit. The explicit observation model here resolves that condition:
a resettable local clock/counter cannot report an unreceived revocation, while
a trusted clock plus signed lease/status is the standard freshness baseline.

The highest-value next search boundary is **PIN-WIT**, but only as a narrow
falsification audit, not a presumed thesis direction. Search the exact
software-only, no-boundary-scan harness model for a strict fault-class coverage
gap at a fixed pulse/energy budget against: (1) ordinary identity and
continuity checks; (2) a fixed exhaustive GPIO codebook; and (3) IEEE 1149.1
style interconnect testing where hardware support exists. First construct the
input-output equivalence classes for opens, shorts, swaps, pull-up faults and
held-out cable/connector cells. Kill it if the fixed codebook has equal
coverage, if the proposed responder recreates boundary-scan hardware, or if
the distinction vanishes under a changed harness topology. This is the only
remaining named boundary with a materially different physical observation
contract; it is still high-collision and has no promotion status.

## Decision

**KILL.** `CAUSE-NULL` reproduces FDI fault-isolability and sensor-placement
questions when formalized, and trivial confounding when not. `OFFLINE-REV-NULL`
reproduces the standard fact that a cache without a freshness witness cannot
learn a remote revocation; with trusted time, lease expiry, or signed status it
reduces to ordinary PKI controls. Retain both only as bounded negative examples,
not FYP directions.

KILL
