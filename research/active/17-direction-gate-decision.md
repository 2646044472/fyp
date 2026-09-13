# Direction Gate Decision: START-WIT

> **Superseded (KILL, 2026-09-03):** the post-audit decision is recorded in
> [27-round-19-post-start-wit-reconciliation.md](27-round-19-post-start-wit-reconciliation.md).

## Decision investigated

Which direction should receive the next hardware and experiment budget after
the palm/biometric branch was rejected?

## Decision as of 2026-09-03

Keep `START-WIT` as the **conditional primary direction**, but do not call it
the thesis topic yet. The title-level object is:

> Edge verification of whether a maintenance start command took effect; an
> intermittent connection is the motivating deployment condition, not yet a
> measured networking contribution.

The object is not motor fault diagnosis, predictive maintenance, a new
current-vibration fusion model, or a production safety controller.

## Why this is the next direction

- [K] It matches the user's stated factory, temporary-site and mobile-repair
  context without requiring personal data, legal-status labels, payment access
  or production machinery.
- [K] It has a concrete local decision and asymmetric harm:
  `running / failed-to-start / inspect` after a command.
- [K] The decision can be evaluated with an independent mechanical truth
  channel, while current and acceleration remain the only policy inputs.
- [C] A short sequential policy may improve the action-loss/latency frontier
  over one-sensor, fixed-window and always-inspect controls.
- [GAP] The weak-network part is only a context constraint until local deadline,
  upload delay and a remote/cloud baseline are measured. It must not be claimed
  as a networking contribution before that measurement.

## Collision warning

The inspected primary sources show that edge motor monitoring with current,
vibration or inertial signals, including Raspberry Pi deployment and
normal/fault or predictive-maintenance endpoints, is already an active family:

- Abo-Khalil et al., *The Edge Application of Machine Learning Techniques for
  Fault Diagnosis in Electrical Machines*, Sensors 23(5):2649 (2023),
  abstract and Sections 1-2: edge motor-current fault diagnosis on a
  resource-constrained platform, https://www.mdpi.com/1424-8220/23/5/2649.
- Zhou et al., *A Deployment Method for Motor Fault Diagnosis Application Based
  on Edge Intelligence*, Sensors 25(1):9 (published 2024-12-24), abstract and
  Sections 1-2 and 6: Raspberry Pi 4B deployment, acceleration/voltage signals,
  six normal/fault classes, and edge inference, https://www.mdpi.com/1424-8220/25/1/9.
- Baddou et al., *Towards a Resilience-Oriented Framework for Fault Diagnosis
  Under Varying Operating Conditions*, Sensors 26(16):5239 (published
  2026-08-19), abstract and Sections 3.1, 3.4.1, 3.5.1-3.5.2 and 5.1:
  multi-sensor vibration/current fusion, healthy/fault screening and
  deployability assessment, https://www.mdpi.com/1424-8220/26/16/5239.

These sources are not a global novelty conclusion. They establish a high-risk
collision family; the exact command-outcome endpoint remains a scoped [GAP]
that must be checked against the experiment, not assumed to be open.

Therefore the only claim allowed through the next gate is the narrower one:
whether a frozen, short-deadline evidence policy changes a maintenance-record
action frontier when truth is independently measured. If the experiment is
only a classifier separating normal and failed motor traces, the candidate is
already out of scope and must be killed.

## Next gate

Run the existing [START-WIT minimal pilot protocol](16-start-wit-pilot-protocol.md)
with the minimum fixture only:

1. low-voltage fan or motor;
2. current monitor;
3. accelerometer;
4. independent optical tachometer or equivalent mechanical truth;
5. local logging while the network is disconnected.

Do not buy a larger model, extra camera or elaborate enclosure before the
truth channel and baseline matrix work.

## Continue / kill rules

Continue only when all conditions hold:

- independent truth is stable and not derived from current or acceleration;
- at least one load or remount cell is held out before thresholds are frozen;
- sequential early stopping produces a repeatable action-loss or
  latency-cost advantage over current-only, acceleration-only and fixed fusion;
- the endpoint remains command-outcome recording rather than ordinary fault
  classification.

Kill the positive direction if any of the following occurs:

- a single sensor or fixed fusion is Pareto-optimal;
- the effect disappears under held-out load/remount conditions;
- the tachometer/relay truth is coupled to a policy sensor;
- the result depends on one motor and one staged failure;
- the network is mentioned but no local-versus-upload deadline is measured.

If the process-change versus sensor-bias paired-world test succeeds, pivot to
`CAUSE-NULL`: a scoped negative result about what the permitted edge evidence
cannot identify and what named independent witness is minimally required.

## Procurement decision

The minimum sensors are justified only as an identification and feasibility
gate. No purchase should be framed as evidence that `START-WIT` is novel. If
the independent truth channel cannot be built safely and repeatably, return to
the existing Pi RGB/NoIR optical backup rather than expanding the motor setup.

## Status

**HOLD (Amber), high collision risk.** This file records the next direction
and its falsification gate; it does not lock the FYP thesis.
