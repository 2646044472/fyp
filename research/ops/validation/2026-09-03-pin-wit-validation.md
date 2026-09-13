# Validation Audit: 2026-09-03 PIN-WIT

## Decision investigated

Whether `PIN-WIT` can be promoted from an unvalidated constrained benchmark
to a primary FYP direction. The candidate proposes that, for a declared
two-MCU sensor-harness graph and finite staged set of open, short, swapped,
and pull-up faults, a GPIO transition codebook can choose `commission`,
`inspect`, or `unknown` and identify more fault classes at a fixed pulse or
energy budget than I2C identity, continuity, static plausibility, and a fixed
all-pattern control.

## Claim under test

The only possible research claim is a nontrivial software-only harness
diagnosability boundary: without IEEE 1149.1/DFT support, an adaptive GPIO
policy has a theorem, mechanism, or repeatable deployment endpoint that a
fixed pattern battery and ordinary commissioning controls do not have. This
audit tests that exact residual, not whether two RP2040-class boards can send
and receive GPIO signals.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| Component collision | IEEE 1149.1 defines IC test logic and procedures for PCB interconnect testing, IC testing, and observing/modifying/loading IC data. A two-MCU responder deliberately creates the controllability and observability that a test-access design supplies. BIST, test-pattern generation, and fault dictionaries are established test families. | RP2040-class boards may not expose IEEE 1149.1 boundary-scan cells, so the fixture is not literally compliant boundary scan. That is a hardware limitation, not a new test architecture. | High |
| Exact-claim collision | Lin, Lu, and Cheng explicitly study adaptive diagnostic test-pattern generation for multiple faults. The candidate's choose-next-GPIO-pattern-after-response mechanism is this family applied to jumper wires. A fixed codebook/fault-signature table is the ordinary comparator. | No source inspected has the exact two-MCU jumper graph, selected connector lengths, or four named staged faults. That missing tuple is not a task, observation, action, guarantee, or endpoint distinction. | High for mechanism; medium for exact-fixture search boundary |
| Boundary and necessity | For a finite declared fault set, two faults with equal response under every allowed stimulus word are indistinguishable to every adaptive policy. If a predeclared battery gives every staged fault a unique response signature, it already classifies the whole declared set; adaptivity can only reduce test count or expected energy. Diagnosability under partial observations is an established formal object. | A new result would require an original, externally motivated harness class, fault process, and formal cost/guarantee that differs from test-pattern selection. None is supplied. | High |

## Assumption and identification audit

### Fixed-versus-adaptive test boundary

Let `F` be the finite injected-fault set, `Q_b` the set of all electrically
safe GPIO stimulus words of at most `b` transitions permitted by the stated
budget, and `r_f(q)` the entire policy-visible response transcript of harness
fault `f` to word `q`. The graph, drive modes, series protection, sampling
times, responder firmware, and reset state must be part of this definition.

If faults `f` and `g` satisfy

```text
r_f(q) = r_g(q) for every q in Q_b,
```

then no adaptive policy can distinguish them within the budget. After any
identical response history it chooses the same next stimulus in both worlds;
induction on the length of the history gives identical terminal transcripts.
The sound action is `unknown` or `inspect`, not a new diagnosis claim.

Conversely, if a fixed, budget-honest battery `S` yields a unique signature

```text
sigma_f(S) = (r_f(q) : q in S)
```

for each staged `f`, a lookup table classifies every member of the stated
fault set. It supplies the same `commission / inspect / unknown` action
surface without online information-gain logic. A policy that stops after a
prefix can reduce *expected* pulses, but this is precisely adaptive
diagnostic-test selection; it does not identify additional information absent
from the responses.

[KILL] The candidate's phrase "fixed all-pattern test at a fixed budget" is
not currently a well-defined baseline. If the all-pattern battery fits the
same maximum transition/energy budget, it must be the main baseline and can
match full staged-fault coverage. If it does not fit, the candidate has only
changed fixed worst-case budget into expected stopping cost, which is a known
adaptive-test objective. A comparison cannot call the latter "strictly more
fault classes at the same budget" without first fixing whether the budget is
worst-case, expected, or per-fault.

### Fault labels are topology-specific, not portable classes

`open`, `short`, `swap`, and `pull-up fault` are physical descriptions, not
policy-visible labels. For example, a short to a rail, an unintended pull-up,
a responder drive-mode error, and a cable swap can coincide on the same
sampled logic level for selected stimuli. Whether any are separable depends
on direction changes, contention-safe current limiting, both-end access,
reset behavior, and timing. The divergence packet supplies none of these as a
declared graph or a production-like fault model.

[KILL] A table of manually inserted jumper faults therefore measures the
chosen fault board, not a harness population. Holding out cable length or a
connector type does not repair the absence of a source of real harness
replacement episodes or field fault incidence.

### Identity and continuity are not weak straw baselines

I2C `WHO_AM_I` or a responder challenge can establish that an expected device
answers at an expected endpoint; it cannot alone prove every conductor map or
electrical margin. Continuity/identity checks are nevertheless the direct
commissioning controls for the claimed actor. A fair evaluation must state
exactly which conductor pairs, rails, and directions are accessible to them.
If a technician can access both connector ends before deployment, fixed
continuity plus a fixed walk-0/walk-1/loopback battery is the stronger
operational baseline. If that access is unavailable, the second powered MCU
is a deliberately installed remote test endpoint, which supplies a custom
test-access mechanism rather than revealing an ordinary deployed harness.

### Boundary scan and BIST do not rescue the residual

IEEE 1149.1 does not apply to an arbitrary RP2040/jumper assembly without
boundary-scan-capable parts, and this audit does not claim it does. Its
relevance is architectural: standardized board testing already uses explicit
test logic to create controllability/observability at interconnects. The
candidate's responder firmware plays that role for its own declared pins.

Likewise, a firmware routine that drives test patterns, reads signatures, and
reports pass/fail is an embedded functional self-test/BIST-style control. It
may be useful engineering, but no new theorem follows merely from placing the
routine on two cheap MCUs rather than in DFT cells. The proposed no-DFT
condition makes the result narrower, not more original.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| IEEE Std 1149.1-2013, *Test Access Port and Boundary-Scan Architecture* | Explicit test logic; standardized procedures/languages; observe, modify, load, and test IC/PCB interconnect state | Board/interconnect and IC test | Same controllability/observability purpose for interconnect checking | [KILL] Calling active GPIO interconnect testing a new test architecture. It does not require a non-1149.1 MCU fixture to be compliant. |
| Lin, Lu, and Cheng, *Multiple-Fault Diagnosis Based On Adaptive Diagnostic Test Pattern Generation*, IEEE TCAD 26(5), 2007 | Select diagnostic patterns based on responses | Distinguish multiple faults with generated tests | Same adaptive pattern-versus-signature mechanism | [KILL] A next-pattern policy, pulse minimization, or fault-class-coverage claim. It leaves no exact two-MCU deployment endpoint. |
| Agrawal, Kime, and Saluja, *A Tutorial on Built-In Self-Test. 2. Applications*, IEEE Design & Test 10(2), 1993 | Self-applied test stimuli and response analysis | Embedded pass/fail test applications | Two firmware-controlled endpoints create the same broad self-test structure | [KILL] Calling firmware GPIO exercise itself a research mechanism. It leaves a bounded implementation demonstration. |
| Sampath et al., *Diagnosability of Discrete-Event Systems*, IEEE TAC 40(9), 1995 | Partial event observations and failure model | Whether failures can be diagnosed from observations | The observation-equivalence boundary in the candidate | [KILL] Treating an indistinguishable pair as a new theorem. It leaves only a new, justified formal model with a distinct result. |
| Linux kernel I2C GPIO fault-injection and generic SCL recovery documentation; TI, *I2C Stuck Bus: Prevention and Workarounds*, SCPA069, 2024 | Controlled SCL/SDA line states, pulses, STOP/reset/isolation controls | Recover and test ordinary I2C wire-level faults | Shows active GPIO probing and fixed recovery sequences are standard embedded controls | [KILL] Generic active-pin-test or "edge node chooses a wire action" framing. These sources do not prove the exact multi-wire codebook covers PIN-WIT's invented fault matrix. |

## Strongest simple baseline

For the exact declared harness, build the following **before** collecting
staged-fault outcomes:

1. A fixed commissioning battery: reset, declared idle levels, per-line
   walk-0/walk-1, direction reversal where electrically safe, declared pulse
   widths, and responder loopback/identity challenge.
2. A fault-signature table derived from the known graph and the finite staged
   fault set. `commission` is permitted only for a healthy unique signature;
   collisions produce `inspect` or `unknown`.
3. Conventional controls: I2C address/identity read when the sensor supports
   it, connector/pin-map check, and continuity for every physically accessible
   conductor pair.
4. A test-budget report with separate worst-case transitions, expected
   transitions, joules, elapsed time, and any risk of output contention.

This baseline is stronger than a single continuity test or a plausible-range
check and is the correct direct comparator to any adaptive codebook. It is
not acceptable to omit it in favor of an underspecified "fixed all-pattern"
control.

## Contrarian result

**[KILL] `PIN-WIT` has no credible positive FYP contribution in its present
form.**

1. With a fixed finite harness graph and injected fault list, the study is a
   fault-dictionary/test-pattern characterization. A full fixed signature
   battery either has equal coverage or exposes exactly which classes are
   observationally identical.
2. If adaptivity shortens a test, it instantiates established adaptive
   diagnostic-test generation. No new codebook theorem, observation model,
   or endpoint is stated.
3. If the remote MCU is necessary to make the test work, it is a bespoke
   test-access/self-test architecture. Calling it "without DFT hardware"
   does not produce a distinct mechanism; it trades standardized DFT cells
   for application firmware and a cooperative endpoint.
4. The stated technician, harness swapping workflow, false-record harm,
   independent operational result, and repetition rate are not confirmed in
   the current project record. The only user note describes palm/weak-network
   ideas and possible sensor purchase; it does not establish a sensor-harness
   commissioning process. This fails the charter's real-actor and repeated
   outcome requirements before literature novelty is considered.

The fixture can remain a short engineering or teaching control. It must not
be promoted as a thesis direction, a general software-only diagnosability
boundary, or a maintenance deployment result.

## Feasibility audit

| Requirement | Audit result | Consequence |
| --- | --- | --- |
| Credible actor and deployment | [GAP] No confirmed user-owned workflow has a technician repeatedly replacing this harness, recording commission decisions, or suffering the stated harm. | The fixture story is invented; do not claim field relevance. |
| Independent truth | A manual wiring map plus external logic-analyzer trace can label staged episodes if it is withheld from the policy. | It validates only injected fixture states, not the unobserved physical cause in deployment. |
| Safe fault injection | [GAP] Shorts, pull-up faults, direction reversals, and drive contention require declared voltages, series resistors/current limits, reset states, and a safe injection board. | Without these, the test changes hardware behavior or risks damaging pins; no data collection should begin. |
| Fixed-codebook comparator | [GAP] No graph, transition alphabet, fault-signature matrix, or fair worst-case/expected budget is specified. | The central adaptive-versus-fixed claim is currently untestable. |
| Generalisation | Held-out cable length/connector cells are finite bench perturbations, not samples from a supported harness population. | Report only per-fixture coverage if built. |
| One-year research value | Cheap hardware can yield a December demo, but the 2027-H1 extension is a larger staged matrix with no surviving mechanism or deployment contribution. | Do not spend the FYP slot or purchase around it. |

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Boundary scan standardizes test logic for PCB interconnect test, IC test, and internal observation/modification/loading. | [K] | IEEE Std 1149.1-2013, official record: https://standards.ieee.org/ieee/1149.1/10977 | Official scope/description, accessed 2026-09-03. | The standard does not make an RP2040 fixture boundary-scan compliant; it is an architectural direct neighbor. |
| Adaptive diagnostic test-pattern generation for multiple-fault diagnosis is an established research family. | [KILL] | Y.-C. Lin, F. Lu, and K.-T. Cheng, *Multiple-Fault Diagnosis Based On Adaptive Diagnostic Test Pattern Generation*, IEEE TCAD 26(5):932-942, May 2007, DOI: https://doi.org/10.1109/TCAD.2006.884486 | Publisher/Crossref metadata and title/venue/pages read 2026-09-03; full VOR was access-restricted. | The title and bibliographic record directly establish the mechanism family; detailed method or guarantee beyond that is not attributed here. |
| BIST includes application-side use of embedded test stimulus/response mechanisms. | [K] | V. D. Agrawal, C. R. Kime, and K. K. Saluja, *A Tutorial on Built-In Self-Test. 2. Applications*, IEEE Design & Test of Computers 10(2):69-77, June 1993, DOI: https://doi.org/10.1109/54.211530 | Publisher/Crossref bibliographic record read 2026-09-03; VOR not retrieved. | Supports family-level BIST collision only, not an exact firmware implementation claim. |
| Diagnosability depends on an explicit partial-observation/failure model. | [K] | M. Sampath, R. Sengupta, S. Lafortune, K. Sinnamohideen, and D. Teneketzis, *Diagnosability of Discrete-Event Systems*, IEEE TAC 40(9):1555-1575, 1995, DOI: https://doi.org/10.1109/9.412626 | Opening problem statement and publisher metadata; local prior audit records pp. 1555-1558, rechecked 2026-09-03. | Discrete-event theory, not a jumper-harness result; it supports the observation-equivalence framing. |
| Standard embedded I2C controls already use GPIO-controlled wire states, pulse clocks, reset and recovery. | [K] | Linux kernel, *I2C GPIO fault injection*, https://docs.kernel.org/i2c/gpio-fault-injection.html and `i2c_generic_scl_recovery`; Texas Instruments, *I2C Stuck Bus: Prevention and Workarounds*, SCPA069, July 2024, https://www.ti.com/lit/an/scpa069/scpa069.pdf | Linux sections "Wire states" and "Incomplete transfers"; TI pp. 5-7, as inspected in the existing 2026-08-29 EBR validation record and reread as local evidence on 2026-09-03. | I2C recovery is not an exact GPIO codebook result; it blocks a generic active-wire-action narrative. |
| No current project source establishes a real recurring sensor-harness commissioning workflow or field fault distribution. | [KILL] | Local user/coordinator record: `minutes/08-17.md`; project charter and current Round 20 reconciliation. | Entire note and current charter/reconciliation read 2026-09-03. | This is a feasibility/actor deficiency, not literature absence. |
| Fixed and adaptive policy limits above. | [K] | Direct construction in "Fixed-versus-adaptive test boundary" above. | Explicit finite `F`, safe stimulus-word set `Q_b`, and response map assumptions. | It is a scoped logical result, not claimed as a new theorem; stateful/analogue cases must be included in `r_f`. |

## Queries and failed searches

Queries run or reviewed on 2026-09-03:

- `IEEE 1149.1 boundary scan interconnect testing official scope`
- `adaptive diagnostic test pattern generation fault diagnosis digital circuits`
- `fault dictionary diagnosability test pattern generation digital circuits`
- `embedded GPIO loopback wiring fault diagnosis primary paper`
- `built in self test applications test stimulus response analysis IEEE`
- `testability diagnosability finite fault set input output relation theorem`
- `I2C identity continuity connector wiring fault commissioning GPIO`
- `software-only no boundary scan microcontroller harness fault diagnosis`

Failed or unresolved checks:

- No primary paper was found that establishes the exact two-RP2040,
  no-boundary-scan, finite-jumper fault tuple as a new research endpoint.
  This is **not** novelty evidence.
- No source or user record establishes a recurring technician harness-swap
  workflow, independent commission outcome record, error rate, deadline, or
  true pulse/energy constraint for the proposed actor.
- Full text for the 2007 adaptive diagnostic-test paper and the 1993 BIST
  tutorial was access-restricted in this pass. They are used only at the
  carefully stated family level; the direct finite-transcript argument does
  not depend on inaccessible details.

## Decision

**KILL.** `PIN-WIT` is a fixture-specific fixed-codebook/adaptive-test
comparison inside established interconnect testing, BIST, and diagnosability
families. Its software-only two-MCU architecture adds no demonstrated new
theorem or mechanism, and it lacks a credible actor, repeated deployment, and
independent operational endpoint. Retain it only as an optional bounded
engineering control; do not promote it as the FYP direction.

KILL
