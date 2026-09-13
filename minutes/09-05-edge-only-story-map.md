# Edge-Only Story Map (2026-09-05)

## Scope change

[K] The user no longer requires a camera. The fixed boundary is now broadly
edge computing; inexpensive boards, sensors and network fixtures are allowed.
This reopens systems stories, but it does not reopen the previously killed
generic mechanisms: adaptive sensing, storage recovery, model-package checks,
schema quarantine, generic scheduling, offline authentication protocols or
emulator-versus-physical comparison as a stand-alone methodology.

## Decision rule

Every candidate must name:

1. a non-personal role and repeated local decision;
2. the concrete consequence of a wrong action;
3. an independently observable outcome; and
4. an action/baseline that can falsify the claim.

An edge board, artificial network loss, a dashboard or a new scheduling model
is not a contribution by itself.

## Candidate stories

| ID | Story and local decision | Independent outcome | Research identity | Current judgment |
| --- | --- | --- | --- | --- |
| EMUL-TRANSFER | A field-maintenance team configures a Pi recorder's retry/flush policy in a lab emulator before taking it to a site with short, intermittent Wi-Fi contacts. The recorder chooses a declared retry/flush policy or marks the upload unresolved. A wrong lab choice misses a work-record deadline or creates an unnecessary revisit. | Application completion receipt, packet capture and a separately logged physical Wi-Fi contact trace. | Do emulator-selected policy rankings transfer to a small declared physical Wi-Fi/contact fixture? This is not a new emulator or congestion-control algorithm. | **PIVOT, appendix only.** The project already validated that emulation-to-real comparison is established testbed methodology. It can report a finite negative audit, but is not an edge-only FYP main direction. |
| CONTACT-UTILITY | A disconnected inspection kit gets a short contact window and must send a complete record, a compact summary, or defer. Sending the wrong item first delays closing the only urgent non-personal work item. | Predeclared work-item deadline/value plus receiver acknowledgement and contact trace. | Does a simple static priority rule remain adequate under declared short contacts, or does a finite task-value policy change completion loss at equal bytes? | **HOLD/PIVOT.** It becomes ordinary edge scheduling unless actual priority/deadline labels come from a real workflow. Do not claim a new utility scheduler. |
| OFFLINE-REV-NULL | A shared non-production lab fixture receives a benign simulated job while the Pi is disconnected. It must allow, defer, or deny a cached capability after a possible remote revocation. Wrong allow violates the bench policy; wrong defer delays a harmless job. | Authoritative revocation log after reconnection; local clock/counter/reset trace. | What minimum freshness witness is necessary to make an offline decision sound under a stated reset/revocation model? | **PIVOT, negative-result only.** The useful result is an explicit indistinguishable valid/revoked pair and cost of the missing witness, not a new authorization protocol. |
| POWER-RECORD | A sensor/logger sees a brownout or sudden loss of power while a record is being written and must retain it, recover it, or mark it unknown. | External source record plus controlled power-cut trace and post-recovery media state. | Whether a local power signal changes record-admission error beyond journal recovery. | **KILL as a main direction.** Crash recovery and physical power-cut validation are direct families; a valid-prefix journal is the required baseline. |
| SEMANTIC-QUARANTINE | A field node receives records after a firmware/calibration change and must merge, convert, or quarantine them while offline. | Declared firmware/calibration contract and, if available, a calibrated overlap/reference measurement. | Whether local metadata plus a small fixture check identifies unsafe record joins. | **KILL as a main direction.** Standards already carry version/unit/procedure provenance, while hidden semantic changes can preserve all permitted observations. |
| MODEL-SPEC-NULL | A Pi receives an offline model package and must load, quarantine, or request inspection before the model annotates a benign test record. | Signed preprocessing/label contract plus a frozen fixture test. | What observable contract is sufficient to rule out a specified semantic mismatch? | **KILL as a main direction.** Normal runtime/package validation handles declared incompatibility; undeclared semantics are unidentifiable without a new witness. |

## Why EMUL-TRANSFER cannot rank first

The actor and error are concrete: a maintainer selects a client policy based on
lab evidence, then deploys it under a different connectivity process. The
experiment can keep the policy family deliberately small:

- fixed periodic flush;
- fixed retry/backoff;
- fixed acknowledgement-aware flush;
- one source-fitted rule, only if it beats the fixed controls.

The endpoint is not average throughput. It is whether the same policy remains
non-dominated on delivery-deadline misses, local storage/energy, retries and
operator-visible unresolved records when moved from a configured emulator to a
predeclared physical contact fixture.

[KILL] Do not claim that NetEm or physical Wi-Fi emulation is generally
inadequate. Network emulation fidelity is already an established systems
problem: Becker et al. study limits of NetEm in virtual edge testbeds, and
MirrorNet is a production-scale high-fidelity WAN emulator. Do not claim a new
scheduler either: recent IoT-edge-cloud work explicitly formulates
latency-aware data-oriented task scheduling. The only permissible residual is
a finite policy-transfer boundary with application-level action loss.

The project's prior independent validation is stronger than this broad
literature warning. QOMB already evaluates emulation against real wireless
trials with real traffic/protocols. The PRF-style policy-rank framing changes
the outcome table, but not the fact that a frozen emulator-to-physical
comparison is established methodology. The existing audit therefore assigns
RF-EMUL-RANK to a bounded negative appendix, not a primary FYP slot.

## Minimal EMUL-TRANSFER gate

1. Two Pis or one Pi plus one laptop, with a fixed local application protocol;
2. one reproducible physical Wi-Fi/contact intervention and one held-out
   contact condition;
3. a separately captured packet/application completion log;
4. fixed flush/retry baselines before any learned or tuned policy;
5. a preregistered action-loss ledger: deadline miss, bytes, retries, local
   queue age, energy if reliably measured and unresolved records;
6. a stop rule: if fixed periodic or acknowledgement-aware flush is
   non-dominated in both worlds, report a bounded null and do not create a new
   scheduler.

## Research position

No edge-only story in this table is currently promotable as the main FYP
direction:

- EMUL-TRANSFER is an established evaluation methodology with a bounded
  negative-result use only.
- CONTACT-UTILITY still needs a real workflow that supplies pre-existing item
  urgency, deadline and completion labels; otherwise it is generic scheduling.
- OFFLINE-REV-NULL is a formal negative exercise whose positive protocol claim
  is already occupied.
- The remaining three candidates are killed by direct systems/lifecycle work.

Removing the camera constraint creates more application stories but does not
by itself create a research asset. A new edge-only main candidate must begin
with an accessible repeated workflow or an independent physical/operational
truth source that is not present in the current workspace.

## Sources checked

- Becker et al., *Network Emulation in Large-Scale Virtual Edge Testbeds: A
  Note of Caution and the Way Forward*, arXiv:2208.05862,
  https://arxiv.org/abs/2208.05862 .
- Miao et al., *MirrorNet: High-fidelity and Scalable Network Emulation for
  Software-defined WAN*, NSDI 2026,
  https://www.usenix.org/conference/nsdi26/presentation/miao .
- Liu et al., *Latency-aware scheduling for data-oriented service requests in
  collaborative IoT-edge-cloud networks*, Future Generation Computer Systems
  163 (2025), https://doi.org/10.1016/j.future.2024.107538 .
- Existing local negative audits: research/active/02-decision-log.md and
  research/ops/divergence/2026-09-03-weak-network-data-plane-divergence.md.
- Direct validation: research/ops/validation/2026-09-03-contact-evidence-rf-emul-rank-validation.md.

PIVOT.
