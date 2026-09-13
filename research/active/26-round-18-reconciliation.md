# Round-18 Reconciliation: Shaft-Start and Weak-Network Data Plane

> **Superseded for direction status (2026-09-03):** `START-WIT` was later
> KILLed as a positive mechanism. See
> [27-round-19-post-start-wit-reconciliation.md](27-round-19-post-start-wit-reconciliation.md).

## Inputs checked by the coordinator

- [Divergence packet: weak-network data plane and offline semantics](../ops/divergence/2026-09-03-weak-network-data-plane-divergence.md)
- [Validation audit: START-WIT command-outcome verification](../ops/validation/2026-09-03-start-wit-command-outcome-validation.md)
- Current `START-WIT` prospectus, protocol, data schema, acquisition design and
  policy specification in active files 15-25.

## Reconciled decision

`START-WIT` remains the physical first gate, but only as **shaft-start
verification** on a declared low-voltage fan/motor fixture. The optical truth
can establish whether a shaft reached a declared pulse/RPM threshold before a
deadline. It cannot establish pump flow, pressure, valve position or general
equipment success. The endpoint, title and protocol have been narrowed
accordingly.

The first positive claim is now especially narrow: a sequential prefix policy
must beat current-only, acceleration-only, and a calibrated fixed-full-prefix
fusion-with-reject policy on held-out load/mount cells with independent optical
truth. A Pi deployment, current/vibration fusion, startup transient analysis,
fault classification, reject action, or weak-network story is not a standalone
contribution.

## Reconciled constraints

- [KILL] Broad motor diagnosis, predictive maintenance, startup-transient
  feature extraction, Pi deployment, generic screen/confirm acquisition and
  multi-sensor fault fusion are occupied direct-neighbor families.
- [KILL boundary] The shaft witness cannot justify a pump/valve/process-success
  statement without a separate flow/pressure/position witness.
- [GAP] The exact three-action shaft-start action-loss endpoint was not
  established as occupied in the inspected sources. This search boundary is not
  evidence of novelty.
- [K] The decisive baseline is fixed-full-prefix fusion with a calibrated
  `running / failed-to-start / inspect` reject band, not a bare classifier.
- [K] INA219 effective timing, conversion mode, averaging and drops must be
  measured before current-prefix results are interpreted. Replace it with an
  analog shunt/MCU ADC only if that measured gate fails.
- [K] Optical truth, policy acquisition and command timing require separate
  paths and measured trigger jitter.

## Backup candidates from divergence

`WATERMARK-CLOSE` is **KILL** after independent validation. Without a
conformant source closure witness, delayed-exists and never-existed worlds have
the same receiver observation; with that witness, fixed grace plus contiguous
sequence/watermark handling is the existing baseline. It remains only as a
negative boundary example, not a fallback implementation.

`SCHEMA-QUARANTINE` is also **KILL** after independent validation. A cached,
signed semantic contract plus conservative quarantine is the direct baseline
for declared changes; hidden RMS/peak or calibration-meaning changes remain
unidentifiable from local metadata and finite traces. It remains only as a
negative boundary example.

## Advisor-fit boundary

[GAP] The archived Bob Zhang/PAMI audit establishes only a general thematic
connection to unreliable or incomplete observations, uncertainty and
conservative decision-making. It identifies no named public paper with a
non-superficial overlap with the shaft-start task, observation model or action
endpoint. Treat this as discussion context only: it is not evidence of
novelty, a title claim, or a technical contribution for `START-WIT`.

## Ordered next gates

1. Run the 100-trigger and sensor-rate acceptance tests in the acquisition
   architecture.
2. If timing and independent optical truth pass, run the preregistered
   shaft-start pilot against the full-prefix reject baseline.
3. If a simple baseline ties or dominates, kill the positive `START-WIT`
   mechanism and decide between the `CAUSE-NULL` paired-world study and the
   existing-hardware `IR-CAUSE` backup gate.
4. Do not purchase a second motor, larger model, cloud service or extra camera
   to rescue a failed gate.

## Status

**`START-WIT`: HOLD (Amber), high collision risk, physical first gate.**

**`WATERMARK-CLOSE`: KILL. `SCHEMA-QUARANTINE`: KILL.**

No thesis direction is locked.
