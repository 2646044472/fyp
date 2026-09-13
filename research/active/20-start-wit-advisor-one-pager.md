# START-WIT Advisor One-Pager

> **Superseded (KILL, 2026-09-03):** do not use this one-pager to request a
> thesis commitment. The post-audit decision is in
> [27-round-19-post-start-wit-reconciliation.md](27-round-19-post-start-wit-reconciliation.md).

## Proposed title

**Edge Verification of Shaft-Start Outcomes with Independent Mechanical
Witnesses**

中文可写为：**基于独立机械真值的转轴启动结果边缘验证**。

## Problem in one sentence

At a temporary site or mobile repair visit, a technician may issue a start
command when the network is unavailable or delayed and need to know locally
whether a non-personal motor shaft actually started before deciding the next
maintenance action.

## Research question

Can a low-cost edge node use only the first 2-5 seconds of electrical and
mechanical observations to choose `running`, `failed-to-start` or `inspect`
for a binary shaft-start target, with a better action-loss/latency trade-off
than one-sensor, fixed-full-prefix reject and always-inspect policies under
held-out loads and sensor mounts?

## What is measured

- **Policy inputs:** motor current and accelerometer prefixes.
- **Independent truth:** optical rotation or photointerrupter signal, withheld
  from the policy process.
- **Truth labels:** binary `started-before-deadline` or
  `not-started-before-deadline`; `inspect` is a policy action, not a label.
- **Action:** a local maintenance record, not a safety actuation.
- **Cost:** false `running`, false `failed-to-start`, `inspect`, decision
  latency, bytes and energy.
- **Connectivity:** disconnection/delay is an application condition; a
  networking contribution is claimed only if upload delay and a remote
  baseline are explicitly measured.

## Minimum system

Pi 5B, guarded 5 V fan or small DC motor, current monitor, accelerometer,
low-voltage switch, independent optical truth sensor, removable load, rigid
mount, emergency stop and local episode log. No worker data, production
machine, mains voltage or cloud dependency is required.

## Experimental comparison

1. Current-only fixed-window policy.
2. Acceleration-only fixed-window policy.
3. Fixed-full-prefix current-plus-acceleration reject baseline.
4. Sequential early-stop policy with the same observations and maximum window.
5. Always-`inspect` control.
6. Independent truth oracle used only for labels and post-hoc reporting.

The hold-out is a complete load/mount condition, not a random split of nearby
windows. Thresholds and action-loss weights are frozen before held-out testing.

## Research contribution allowed

The project may claim only a bounded edge decision study: whether the
shaft-start endpoint and its asymmetric action loss create a measurable
benefit for short sequential evidence. The contribution is invalid if it
reduces to a normal/fault motor classifier, a new neural architecture, a Pi
deployment report, or a claim that rotor motion proves pump flow, pressure,
valve position or downstream process success.

## Falsification and fallback

- If a single sensor or fixed fusion is Pareto-optimal, kill the positive
  mechanism claim.
- If the effect disappears on held-out load or remount cells, report the null.
- If truth is coupled to a policy sensor, invalidate the experiment and rebuild
  the fixture.
- If process-change and sensor-bias worlds can be made observationally
  identical, pivot to `CAUSE-NULL` and document the minimum independent witness
  needed to break the ambiguity.
- If the fixture cannot be made safe and repeatable, return to the existing
  RGB/NoIR optical backup rather than expanding the motor setup.

## Timeline gate

- **September 2026:** acquire only the minimum parts and verify wiring,
  timestamps, optical truth and offline logging.
- **October 2026:** collect normal/failed-start episodes across load and mount
  cells; freeze simple baselines.
- **November 2026:** decide continue, null-result or `CAUSE-NULL` pivot based
  on held-out action loss.
- **December 2026:** have a safe offline demo only if the measurement gate has
  passed. Do not postpone a failed direction by adding a larger model.

## Advisor decision requested

Approve the minimum feasibility pilot as a **conditional research direction**,
with an explicit kill/pivot decision in November 2026. Do not approve a claim
of new motor diagnosis or predictive maintenance.

## Status

**HOLD (Amber), conditional primary.** This one-pager is ready for advisor
discussion, but the thesis is not locked until the independent-truth and
held-out baseline gates pass.
