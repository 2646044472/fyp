# Divergence Packet: 2026-09-03 PIN-WIT software-only harness audit

## Decision investigated

Whether PIN-WIT can be a defensible undergraduate FYP direction: before a non-personal, disconnected bench node commissions a replaced sensor harness, two ordinary programmable MCUs use only declared GPIO drive/read capability to choose commission, inspect, or unknown. The proposed positive form was that a GPIO transition codebook could identify more opens, shorts, swaps and pull-up faults at a fixed pulse/energy budget than identity reads, continuity, and fixed patterns, without IEEE 1149.1 boundary-scan hardware.

**Divergence result:** [KILL] as a primary FYP direction. The relevant object is a standard finite interconnect-test/diagnostic-test design problem. When the harness fault model is deterministic and declared, any GPIO policy is a conventional test-pattern decision tree; a fixed exhaustive codebook exposes the same input-output equivalence classes. When a shorter adaptive tree is useful, that is the established adaptive test-pattern/diagnosis formulation, not a new edge-computing mechanism. The proposed bench story also has no verified operational deadline, pulse-energy ceiling, or field restriction that makes ordinary fixture testing or a physical test point unavailable.

This packet was written as the divergence role only. It does not modify research/active/ and does not promote an absence-of-search result to novelty.

## Search boundary

Read on 2026-09-03:

- AGENTS.md and research/ops/agent-divergence.md.
- research/active/README.md, 00-project-charter.md, 01-candidate-register.md, and 28-round-20-null-boundaries-reconciliation.md.
- research/ops/divergence/2026-09-03-post-start-wit-divergence.md.
- Historical I2C fault-injection/recovery material only as a constraint, not as evidence that PIN-WIT is new.

The retained project restrictions are: no personal data, no production or safety actuation, low-cost one-year undergraduate scope, a repeatable benign workflow, independently available truth, a direct baseline, and a useful negative path. The user has not supplied a real recurring harness-commission workflow, a documented error consequence beyond a repeat check, or a measured deadline that prevents a technician from using an ordinary fixture test.

Primary/official sources were searched for IEEE boundary scan, functional loopback, software GPIO fault injection, interconnect fault diagnosis, and test-pattern design. A source is used only for the task, observation, action, or mechanism it actually covers.

## Formal observation, fault, and test model

Let the declared harness have m controller-side drive-capable nets and r responder-side read-capable nets. Its nominal mapping is a known relation H0. A finite staged fault set is:

F = {f0 = nominal, open(i), short(i,j), swap(i,j), pull(i,v), stuck(i,v), ...}.

Every member must state its electrical model: drive mode, pull value and resistance, source/sink limit, threshold, sampling time, cable/connector, and whether the responder can actively drive a return line. A label such as short without those details is not a unique observation model.

At test step t, a policy selects a legal stimulus xt in X, where X contains the permitted GPIO values/modes, such as {0, 1, Z} per driven net and a declared dwell time. The harness plus responder returns yt = Of(xt, qt), where qt includes declared responder state and timing tolerance. Its transcript is zf(pi) = ((x1,y1), ..., (xT,yT)) with T <= B for pulse, time, and energy budget B. Commission, inspect, and unknown are functions of that transcript. Independent truth is the documented physical wiring/fault insertion plus an external logic-analyzer capture; it is withheld from the deployable policy.

Two faults are indistinguishable under the allowed test family when f is equivalent to g if Of(x,q) = Og(x,q) for every permitted x and reachable q. No GPIO policy can distinguish members of the same class. Conversely, for a finite deterministic F, a fixed battery containing a distinguisher for every separable pair yields the same equivalence partition as an adaptive policy. Adaptivity can change test order or reduce expected length only under an explicit fault-prior/cost model. This is the established diagnostic-test-pattern problem. It is not a new result claimed here; it is the reduction that makes PIN-WIT's proposed novelty testable.

The proposed comparison to a fixed all-pattern test is malformed unless it fixes the stimulus alphabet, timing, fault model and budget. If all patterns means all permitted finite stimuli, it reveals every separable class. If it means a smaller arbitrary fixed set, an adaptive advantage only shows that the baseline was not the appropriate diagnostic codebook.

## Direct-neighbor map

| Mechanism | Direct source inspected | Consequence for PIN-WIT |
| --- | --- | --- |
| Board-level structural interconnect test through controllable/observable boundary cells | IEEE Std 1149.1-2013 specifies a test-access port and boundary-scan architecture whose stated purpose includes board-level and interconnect test. | [KILL] Pin-pattern interconnect testing/fault isolation is already a standard test architecture. Lack of boundary cells is a fixture restriction, not a contribution. |
| Fault equivalence, observability and diagnosability from test patterns | Harris, Pavo, and Mercer formulate interconnect-fault diagnosis from test configurations and distinguish fault effects rather than merely detect an error. | [KILL] The proposed open/short/swap coverage matrix is a direct instance of established fault diagnosis/test-pattern reasoning. |
| Functional loopback as a physical-interface test | TI's DP83TC811 document provides internal and external loopback modes to isolate routing, connector, MAC/PHY and cable-side faults. | [KILL] A loopback responder is ordinary bring-up/isolation apparatus. It does not become research because its pins are GPIO rather than Ethernet PHY pins. |
| Software-controlled low-level fault injection | Linux's GPIO I2C fault-injection driver drives/releases bus lines and stages wire/incomplete-transfer faults against a controller under test. | [KILL] Software-driven wire states and a second controller are established test infrastructure. It also shows that a fault label must include protocol/electrical state, not a loose word such as line failure. |
| Standard I2C recovery/line testing | TI SCPA069 and NXP AN10148 document stuck-line recovery by clocks, STOP/restart/reset and define I2C wire-level failure handling. | [KILL] Recasting a two-wire sensor harness as an adaptive GPIO test/recovery project collides with an already audited protocol-control family. |

Boundary scan is not literally implementable on every RP2040-style harness, and the Ethernet/I2C examples do not prove an exact match to a chosen two-MCU board. That scope difference is real but insufficient: the claimed mechanism remains finite active test-pattern design and functional loopback, both established families.

## Candidate matrix

| ID | Story and harm | Exact candidate claim | Strongest baseline | Smallest falsification / kill test | Feasibility |
| --- | --- | --- | --- | --- | --- |
| PIN-WIT | A technician swaps a non-personal low-voltage sensor harness on a lab bench. A wrong map can invalidate a later bench record and require a recheck. | A software-only GPIO policy identifies strictly more declared fault classes at equal pulse/energy budget than ordinary checks and a fixed codebook. | A fault-model-complete fixed diagnostic codebook; continuity/identity checks; IEEE-1149.1-style interconnect test where supported; direct manual/logic-analyzer inspection. | Freeze H0, F, X, timing and B; enumerate Of(x,q). Kill if fixed pairwise distinguishers produce the same equivalence partition, if the responder adds dedicated test hardware/functionality equivalent to boundary scan, or if an advantage disappears on one held-out cable/connector topology. | Cheap hardware is feasible. [KILL] It supplies a classroom/bring-up experiment, not a research distinction. |

## Positive or residual possibility

[C] A non-thesis conformance/negative benchmark remains possible. It can retain a reproducible fault dictionary for one named MCU, cable, connector and voltage domain; report which staged faults are distinguishable from deployable GPIO observations; and show whether a precomputed fixed codebook, an identity/continuity check, or direct inspection is sufficient. That is useful engineering evidence for the fixture owner.

It is not sufficient for the FYP slot because:

1. Commission / inspect / unknown is a conventional diagnostic decision after ordinary functional tests.
2. A selected pulse/energy limit without a real commissioning deadline makes any adaptive-vs-fixed difference a chosen implementation trade-off.
3. A two-MCU responder creates test controllability/observability by adding a test endpoint; calling it software-only does not remove the physical fixture assumption.
4. A finite open/short/swap board exercises staged wiring states, not a deployable harness population or a general theorem.

The only conceivable positive route would require an externally evidenced workflow in which a physical probe, continuity fixture, boundary scan and fixed complete codebook are genuinely unavailable; a hard measured test time/energy limit makes a particular diagnostic prior operationally necessary; and the contribution differs from existing adaptive diagnostic-test generation in a formal observation or guarantee. No such workflow or distinction is currently available. This is a [GAP], not a reason to hold the candidate open.

## Kill criteria

PIN-WIT must remain killed if any of the following holds:

1. The complete fixed codebook separates the same staged fault classes as the adaptive policy within the declared budget, or a fixed codebook with a modest extra pulse cost is operationally acceptable.
2. The responder requires dedicated loopback/test firmware, reserved lines, an external analyzer, or a fault board not present in the stated field workflow; then it is a fixture test, not a deployable commissioning method.
3. Extra coverage depends on a fault prior, class weights, or inspect cost without workflow evidence.
4. A topology/cable/connector change changes the observed equivalence classes or reverses the apparent policy advantage.
5. Direct inspection, continuity, a sensor identity register, or a standard interface self-test resolves the stated harm at lower practical cost.

Any positive empirical result after such checks would still be a bounded test-fixture characterization. It cannot support a new general interconnect diagnosis or edge-reliability mechanism.

## Evidence ledger

| Claim | Label | Primary or official source, version/date | Sections/pages read | Scope and caveat |
| --- | --- | --- | --- | --- |
| Boundary scan is an established standard architecture for board-level interconnect testing. | [KILL] | IEEE, *IEEE Standard for Test Access Port and Boundary-Scan Architecture*, IEEE 1149.1-2013, official record: https://standards.ieee.org/ieee/1149.1/6465/ | Official title, scope/abstract, standard record; accessed 2026-09-03. | The record does not make generic MCU GPIO boundary scan. It establishes the direct architecture and terminology. |
| Interconnect diagnosis uses test configurations, fault effects, observability, and equivalence/distinguishability reasoning. | [KILL] | I. G. Harris, S. Pavo, and J. Mercer, *Diagnosis of Interconnect Faults in Cluster-Based FPGAs*, ICCAD 2000, author-hosted original paper: https://ics.uci.edu/~iharris/pubdir/iccad00fpga.pdf | PDF pp. 1-6: abstract; Secs. 1-3 on fault model, testing and diagnosis; Sec. 4 results; downloaded 2026-09-03. | FPGA cluster routing differs from a two-MCU cable. It is a direct mechanism neighbor for fault equivalence and test-pattern diagnosis, not an exact apparatus match. |
| Loopback is a standard way to isolate physical-interface paths in product bring-up. | [KILL] | Texas Instruments, *DP83TC811 IEEE 802.3bw Compliance and Debug*, application report SNLA276, November 2017: https://www.ti.com/lit/pdf/snla276 | Sec. 4.2, especially xMII and reverse loopback, PDF pp. 9-11; downloaded 2026-09-03. | Ethernet PHY hardware is not GPIO. It blocks treating a responder/loopback test architecture itself as new. |
| A software GPIO driver can create known low-level wire and incomplete-transfer fault states against a controller under test. | [KILL] | Linux kernel documentation, *Linux I2C fault injection*, current official documentation: https://cdn.kernel.org/doc/html/latest/i2c/gpio-fault-injection.html | Linux I2C fault injection, Wire states, Incomplete transfers, and incomplete_write_byte; retrieved 2026-09-03. | I2C-specific; it establishes existing software-operated fault-injection infrastructure and the need for explicit electrical/protocol fault semantics. |
| Wire-level stuck-bus recovery and test actions are established vendor practice. | [KILL] | Texas Instruments, *I2C Bus Recovery*, SCPA069, July 2024: https://www.ti.com/lit/an/scpa069/scpa069.pdf ; NXP, *I2C Manual*, AN10148 Rev. 4, 2014: https://www.nxp.com/docs/en/application-note/AN10148.pdf | TI PDF pp. 5-7; NXP Bus Recovery - SDA Stuck Low Error section, accessed/retrieved 2026-09-03. | Protocol-specific controls; no exact harness-equivalence claim. They prevent a generic GPIO probe/recovery story from being treated as a fresh mechanism. |
| The project has no verified real process requiring this proposed tester. | [GAP] | Local source: minutes/08-17.md; project charter and current candidate register read 2026-09-03. | User notes list weak-network/mobile-repair context and hardware interest, but no recurring harness commissioning task, records, deadline, or outcome source. | A requirements gap, not evidence against harness testing generally. |

## Queries and failed searches

Queries run or rechecked on 2026-09-03:

- IEEE 1149.1 boundary scan interconnect test official
- software based interconnect test microcontroller GPIO loopback
- interconnect fault diagnosis test patterns bridging open short
- diagnostic test pattern generation interconnect open short IEEE
- GPIO loopback test application note interconnect
- Linux I2C GPIO fault injection wire states incomplete transfers
- I2C recovery stuck SDA SCL vendor application note

Failed or unresolved checks:

- [GAP] No primary source was retrieved that is exactly a two-general-purpose-MCU, no-DFT, finite-cable commission / inspect / unknown study. This is not novelty evidence; it is narrower than the established testing families.
- [GAP] No real user-owned harness workflow, expected fault incidence, field topology, deadline, pulse/energy budget, or independent service record was supplied. Without these, an adaptive ordering benefit has no grounded decision value.
- [GAP] The electrical response of an open, short, swapped pair or pull fault depends on unprovided I/O modes, impedances, capacitance, timing and receiver thresholds. A future fixture can measure these facts but cannot elevate the family into a new FYP mechanism.

## Decision

**KILL.** PIN-WIT is not a defensible primary undergraduate FYP direction in its current form. Keep it only as a benign fixed-codebook/logic-analyzer bring-up control or a future candidate's instrumentation appendix. Do not purchase or build it as the thesis direction, and do not relabel a GPIO loopback fixture or fixed patterns as a new tester.

KILL
