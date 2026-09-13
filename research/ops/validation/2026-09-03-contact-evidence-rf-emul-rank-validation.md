# Decision investigated: whether CONTACT-EVIDENCE or RF-EMUL-RANK can occupy the FYP research slot

# Validation Audit: 2026-09-03 CONTACT-EVIDENCE and RF-EMUL-RANK

## Decision investigated

Audit only the two candidates in the 2026-09-03 divergence packet.

1. CONTACT-EVIDENCE: can a compact local evidence object let a remote reviewer make the same close / request-raw / reopen decision as full raw during a short contact?
2. RF-EMUL-RANK: does a policy order selected under tc netem remain valid on a finite physical Wi-Fi contact matrix?

## Claim under test

CONTACT-EVIDENCE claims a finite evidence-sufficiency boundary for a fixed trace family and closure predicate. RF-EMUL-RANK claims an emulator-to-physical policy-rank audit for raw, fixed summary, resumable chunks, and defer.

## Formalization

Let x be the complete local episode trace, c:X -> {0,1} the frozen closure predicate, e:X -> E an evidence encoder, and V:E -> {close, request-raw, reopen} the remote rule. Exact direct-close equivalence requires

    V(e(x)) = close iff c(x) = 1

for every trace in the declared family. A hash or commitment does not by itself make this property true.

For RF-EMUL-RANK, fix payload x, deadline d, transport, authentication, fragment/repair policy, and contact realization w. A representation r is a valid close action only if the received bytes are sufficient to decide the same c(x). If s(x) is sufficient and L(s(x)) <= L(x), raw has no byte-based completion advantage under the same w. If s(x) is insufficient, summary and raw do not perform the same correct close action. Partial chunks require their own frozen sufficient predicate.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| Component collision | RFC 9171 standardizes intermittent-contact bundle fragmentation, reassembly, and status. Cormode--Thaler--Yi give streaming verification where verifier and prover observe the same input stream. Pinocchio gives public verification of a declared computation on specified input. QOMB evaluates emulation against real wireless trials with real traffic and protocols. | No inspected source has the exact Pi, tc netem, raw/summary/chunk/defer, record-close tuple. That tuple is not itself a research distinction. | High collision; medium exact-tuple search boundary. |
| Exact-claim collision | CONTACT-EVIDENCE is either (a) a fixed sufficient statistic, (b) proof of a computation over a specified/committed trace, or (c) source-event attestation. RF-EMUL-RANK repeats an established testbed methodology: freeze an emulated scenario, run the application/protocol, and compare against physical trials. | QOMB uses WLAN/MANET throughput/routing rather than record closure; the proof sources do not certify physical capture. No exact benchmark collision was established. | High for CONTACT reduction and RF methodology collision. |
| Boundary / impossibility | Honest source: c(x) itself is a one-bit sufficient result. Untrusted computation with trusted input: standard streaming proof or verifiable-computation families apply. Untrusted capture: different physical traces can yield the same selected submitted trace z, hash H(z), and certificate; the remote observations are identical. A full upload of z proves only a predicate of z, not omitted events. | A survivor would need an independently trusted append-only capture/input path and a nontrivial certificate-size lower bound under a specified proof/interaction model. Neither exists in the candidate. | High. |

## Assumption and identification audit

### CONTACT-EVIDENCE

[KILL] The candidate has a forced trilemma.

- Benign source: if the node honestly captures and computes c(x), transmit an authenticated close/reopen bit. For the proposed example, every declared interval contains an in-range timestamped record, fixed count plus min/max plus authenticated sequence bounds is a sufficient conventional summary. Full raw cannot improve the closure decision.
- Untrusted computation, trusted input: Cormode--Thaler--Yi require the verifier to see the stream; Pinocchio verifies F(u) on stated input u. An extrema certificate plus commitment is therefore either weaker than standard proof or a direct reimplementation of it.
- Untrusted capture: the local node can omit or fabricate before choosing z. Worlds with distinct actual captures but identical z, H(z), and evidence are indistinguishable to the remote rule. The desired conclusion is not identified. A hash binds selected bytes, not physical completeness.

[KILL] The claim is not a new compact-verification mechanism. It reduces to a fixed application summary, an established verification family, or an unidentifiable source-truth assertion. A compact result is not independent evidence unless an external trusted capture path defines the input first.

### RF-EMUL-RANK

[K] RFC 9171, Sections 5.8--5.9, already supplies the proposed intermittent-contact fragmentation/reassembly control. Chunks are a transport baseline; they do not create an application closure proof.

[KILL] The policy comparison is semantically under-specified. A smallest sufficient fixed summary weakly dominates raw in bytes under matched transport. An insufficient summary cannot correctly close. Defer is ordinary deadline fallback. Any claimed policy benefit must first specify a predicate under which each representation has the same decision semantics.

[K] The tc-netem manual documents delay, loss, corruption, duplication, reordering, rate, and slot controls, and warns that placement and kernel queue/timer behavior affect realistic TCP experiments. It is a finite packet-impairment tool, not an oracle for Wi-Fi contention, rate adaptation, driver queues, association, or physical interference.

[PIVOT] A rank inversion can be a useful finite negative result: the declared netem model did not preserve the order of these frozen policies on these exact Pi/AP/channel/kernel/load cells. It cannot support a general emulator inadequacy, Wi-Fi transfer, or network-controller claim.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Burleigh, Fall & Birrane, RFC 9171, Bundle Protocol Version 7, January 2022 | Intermittent contacts, fragments, reassembly, status | Transport of known application data | Direct chunks/reassembly baseline | [KILL] Transport mechanics as contribution. Leaves source truth and application semantics outside BPv7. |
| Cormode, Thaler & Yi, Verifying Computations with Streaming Interactive Proofs, PVLDB 5(1), 2011 | Verifier observes stream; prover supplies proof after stream | Exact streaming/database query verification with small verifier state/communication | Same compact remote-verification family | [KILL] A post-hoc source-selected hash/certificate called independent streaming verification. Leaves only a new trusted-input model, not supplied. |
| Parno, Gentry, Howell & Raykova, Pinocchio, IEEE S&P 2013 | Declared F and input u, public verification key, untrusted worker proof | Verify F(u)=y | Same proof-of-local-predicate family | [KILL] A new proof/certificate over fixed data. It highlights that computation proof does not establish physical completeness of u. |
| Beuran, Nguyen & Shinoda, QOMB Wireless Network Emulation Testbed: Evaluation and Case Study, WiNTECH 2010 | Frozen wireless model, link emulation, real traffic/protocols, real trials | Compare emulation with real/simulated UDP/TCP and routing; repeated tests | Same emulation-to-physical validation method | [KILL] Methodology-as-mechanism. Leaves only a bounded Pi/netem replication/negative audit. |
| Linux tc-netem(8) manual | Packet impairment parameters | Protocol testing | Proposed emulator apparatus | [KILL] Treating an impairment trace as a physical-Wi-Fi witness. |

## Strongest simple baseline

CONTACT-EVIDENCE B1: authenticated predicate bit plus source sequence range; for interval/range closure add only authenticated count/min/max. Compare it with raw and request-raw. If B1 agrees, there is no evidence-sufficiency result.

CONTACT-EVIDENCE B2: when trusted input is added, use a conventional proof/attestation over that input. This is a control, not a new proof method.

RF-EMUL-RANK R1: fixed smallest sufficient representation plus standard fragmentation/reassembly, then always-defer and request-raw. Freeze MTU, transport, authentication, repair, and deadline. If policies differ only in bytes, R1 is the decisive baseline.

## Contrarian result

CONTACT-EVIDENCE is KILL as a positive FYP direction. Its decisive defect is not missing implementation: it has no stated trusted-input boundary and no nontrivial predicate/certificate lower bound. Honest capture makes the result trivial; proof over trusted input is established; untrusted capture is non-identifiable.

RF-EMUL-RANK is PIVOT only as a finite negative audit. QOMB is a direct benchmark/testbed-methodology collision, though not an exact raw/summary policy-rank paper. A properly frozen and preregistered rank-inversion study may be an appendix for another project; it is not a stand-alone edge-systems contribution.

## Feasibility audit

| Requirement | CONTACT-EVIDENCE | RF-EMUL-RANK | Consequence |
| --- | --- | --- | --- |
| Independent truth | [GAP] Locally retained raw is not independent truth about omitted capture. | Endpoint packet/application checksums are feasible, but do not make radio state or a contact distribution independent truth. | Do not call raw or packet capture an independent physical record oracle. |
| Real workflow | [GAP] No operator, permitted source-trust model, closure predicate, or revisit cost is confirmed. | [GAP] No real decision makes the representation table consequential rather than synthetic transport exercise. | Stories remain lab mechanisms. |
| Repeatability | Deterministic software traces make a hand-designed certificate especially likely to be trivial. | Requires blocked AP/channel/firmware/kernel/load cells and endpoint traces; still only finite cells. | No population or universal transfer claim. |
| Time/hardware | Two local nodes are feasible; trusted capture/attestation is not in the BOM. | Pi/AP/netem trial is feasible. | Feasibility does not repair collision or identification. |

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| BPv7 handles intermittent connectivity and fragmentation/reassembly of application data. | [K] RFC 9171, Standards Track, January 2022. https://www.rfc-editor.org/rfc/rfc9171.html | Sections 1, 3.1, 5.8, 5.9, 6.1.1. | Transport standard only; it does not establish application truth. |
| Streaming proof verification assumes the verifier sees the input stream. | [K] Cormode, Thaler & Yi, PVLDB 5(1), 2011; arXiv:1109.6882v1, 2011-09-30. https://arxiv.org/abs/1109.6882 | PDF pp. 25--29: Abstract, Section 1, Section 1.1, Section 2. | Essential shared-stream assumption blocks a post-hoc source-capture claim. |
| Public verifiable computation checks a declared F on specified input u; Pinocchio has a compact proof construction. | [K] Parno et al., IEEE S&P 2013. DOI: https://doi.org/10.1109/SP.2013.47 ; author PDF: https://eprint.iacr.org/2013/279.pdf | PDF pp. 1--4: Abstract, Sections 1, 2.1, 2.3. | It does not attest that u was a complete physical trace. |
| Wireless emulation validation against real trials with real traffic/protocols is established, and missing scenario detail produces discrepancies. | [K] Beuran, Nguyen & Shinoda, WiNTECH 2010. https://www.jaist.ac.jp/~razvan/publications/qomb_evaluation_case_study.pdf | pp. 1--3; p. 8 conclusion reports 2--16% differences and scenario-complexity limitation. | WLAN/MANET, OLSR and throughput, not record closure. It is a methodology collision. |
| tc netem is a parameterized packet-impairment queue discipline with limitations for realistic TCP experiments. | [K] Linux tc-netem(8) manual, accessed 2026-09-03. https://man7.org/linux/man-pages/man8/tc-netem.8.html | NAME, SYNOPSIS, DESCRIPTION, OPTIONS, LIMITATIONS. | Tool documentation, not a Wi-Fi fidelity theorem. |
| Exact Pi tc-netem raw/summary/chunk/defer policy-rank study found. | [GAP] Searches below, 2026-09-03. | No inspected source establishes this exact tuple. | Search absence is not novelty evidence. |

## Queries and failed searches

Queries reviewed on 2026-09-03:

- verifiable streaming computation data summaries proof edge devices
- distributed functional monitoring communication complexity exact predicates streaming summaries proof
- Pinocchio Nearly Practical Verifiable Computation full paper pdf
- verifiable computation data streams succinct proof streaming paper full pdf
- network emulation wireless testbed validation real world protocol performance comparison paper
- QOMB Wireless Network Emulation Testbed Evaluation and Case Study DOI 2010 ACM
- network emulation real-world wireless testbed TCP paper
- Wi-Fi emulation testbed validation TCP pdf
- tc-netem manual loss delay reorder limitations
- RFC 9171 fragmentation reassembly intermittent contacts

Failed to establish:

- an exact published Pi tc netem raw/fixed-summary/resumable-chunk/defer policy-rank endpoint;
- a non-arbitrary real closure predicate that defeats fixed sufficient summaries;
- a trusted input/capture model making remote physical-completeness conclusions identifiable;
- a user-owned deadline or revisit cost making either action table a real workflow.

These are gaps, not novelty evidence.

## Decision

CONTACT-EVIDENCE: KILL. Do not promote it as a weak-network evidence-verification FYP mechanism.

RF-EMUL-RANK: PIVOT. Retain only as a finite preregistered negative appendix for another direction, reporting exact cell-level rank agreement/inversion with no transfer/controller/general-inadequacy claim.

Overall: PIVOT.

PIVOT

