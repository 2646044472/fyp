# EBR-AIM Prospectus

## Status

**LOCKED WORKING DIRECTION, Amber innovation.** This is a conditional boundary study for a low-cost edge sensor node. It is not a claim of a new I2C recovery mechanism, a new driver, or global novelty. The first gate is an intervention pilot; until that gate passes, the honest contribution is a finite ambiguity map and a negative result about when standard recovery is already sufficient.

## Working title

**EBR-AIM: Evidence-Bounded Recovery Actions for Low-Cost Edge I2C Sensor Nodes**

## Real story and scope

A lab technician maintains a non-production environmental sensor node at the edge. After an I2C read failure, the node must choose one bounded action: retry, apply the standard nine-clock bus recovery, power-cycle the target, or mark the sample unknown for manual review. A bad choice can create a local data gap, lose samples before a deadline, or cause a collateral register write after an incomplete transaction; an unnecessary power-cycle adds recovery time and energy. Edge constraints matter because the node must act locally during a disconnected or delayed remote-maintenance interval, with a small GPIO/CPU/energy budget and no safe assumption that a remote operator can inspect the bus in time.

The study is deliberately non-production and non-safety-critical. The target uses a sacrificial or read-only register map, and all fault injection is performed on a current-limited benchtop circuit.

## Precise research question

For a fixed, explicitly documented I2C topology and injected fault family, **does an independently measured and countable probe of the bus or target state change the post-action utility of `retry`, standard clock recovery, target power-cycle, or manual/unknown compared with a matched staged driver that uses the same probe budget?**

The claim is only about the registered topology, fault cells, deadlines and cost weights. It must be rejected if the probe does not improve held-out loss, or if all fault states with the same observable prefix have the same optimal action.

## Formal model and falsifiable hypotheses

Let the hidden fault state be
`Z = {target absent, SDA held low, SCL held low, incomplete address/write ACK, transient NACK}`.
The policy receives a pre-action observation `X`: a bounded GPIO trace prefix containing SCL/SDA levels, transaction phase, ACK/NACK bits and timeout duration. It chooses
`A = {retry, clock_recover, power_cycle, manual}`.
The post-action outcome `Y` records read success before deadline, recovery latency, lost samples, collateral register writes, and measured energy.

Use a preregistered loss
`L = lambda_fail * failure + lambda_time * latency + lambda_loss * lost_samples + lambda_write * collateral_write + lambda_energy * energy`.
Weights, deadline and probe budget are fixed before target-cell results are opened. A probe `P` is an independent, countable intervention or observable (for example, bounded SCL-toggle response or a target reset-status line); its time and energy are included in every policy's budget.

**Positive hypothesis [C].** On held-out timing, target and fault cells, a probe-informed policy lowers expected `L` or increases action utility relative to the matched staged driver, with a confidence interval that excludes the preregistered practical-equivalence margin.

**Negative hypothesis [C].** The probe does not change held-out utility, or the staged driver is no worse. This is a publishable boundary result: passive prefixes and/or the tested probe are insufficient for action selection, and the standard policy is adequate for the registered scope.

## Minimal counterexample

Construct two executions with the same visible prefix `SCL=1, SDA=0, NACK/timeout` but different hidden causes: an unplugged target and an externally clamped SDA line. If retry is harmless in the first state but clock recovery or power isolation is required in the second, the passive prefix is non-identifying. The policy must return `manual/unknown` or pay for an independent probe; it may not infer cause from the prefix alone. The logic analyzer and fault controller provide hidden truth for evaluation, never an input to the policy.

## Three-round audit and exact distinction

| Audit | What is already occupied | Residual distinction (Amber) | Kill test |
| --- | --- | --- | --- |
| Component collision | Linux `i2c_generic_scl_recovery`, vendor bus-recovery notes, and US20250068503A1 disclose clocking, STOP/reset, target isolation and escalation. | No new recovery implementation; only measure whether an independent probe changes action utility under a fixed fault family. | Any claimed recovery mechanism or generic fault monitor is removed. |
| Exact-claim collision | US20250068503A1 already sequences monitor, identify target, reset/power-isolate, retry and notify; SentryBus covers generic reliability observability. | A finite post-action utility/indistinguishability endpoint with a matched staged-driver baseline, if it survives the exact-query recheck. | If the same endpoint and protocol are found, retain replication/negative boundary only. |
| Boundary / impossibility | The same passive SCL/SDA/ACK/timeout prefix can arise from multiple causes; Linux warns that recovery after incomplete writes can create a random register write. | Quantify which independently probed cells separate and which remain observationally equivalent. | If no cell is separated, the negative ambiguity map is the result. |

All innovation language remains **Amber** until these three audits are rerun against the final protocol and search date.

## Direct-neighbor evidence

- Linux kernel GPIO fault injection documentation, current 2026-08-29, sections “Wire states”, “Incomplete transfers” and “incomplete_write_byte”; Linux source `i2c_generic_scl_recovery` and `RECOVERY_CLK_CNT 9`: <https://cdn.kernel.org/doc/html/latest/i2c/gpio-fault-injection.html>, <https://github.com/torvalds/linux/blob/master/drivers/i2c/i2c-core-base.c>.
- TI SCPA069, July 2024, “Resolving a Stuck Bus”, pp. 5-7: <https://www.ti.com/lit/an/scpa069/scpa069.pdf>.
- NXP AN10148, “Bus Recovery – SDA Stuck Low Error”: <https://www.nxp.com.cn/docs/en/application-note/AN10148.pdf>.
- US20250068503A1, published 2025-02-27, description paragraphs 122-152 and claims 8-9: <https://patents.google.com/patent/US20250068503A1/en>.
- SentryBus, arXiv v1 posted 2026-08-17, pp. 1-7: <https://arxiv.org/abs/2608.17082>.

These sources establish occupied mechanisms and the need for an explicit boundary. They do **not** establish that EBR-AIM is novel; the residual exact endpoint is [GAP] until the pilot and recheck.

## Minimum experiment

Use one ESP32 or RP2040-class controller, one Raspberry Pi or equivalent edge host if Linux recovery is under test, two cheap I2C sensor breakouts (for example BME280/SHT31/VL53-class parts), pull-ups, a MOSFET or analog switch for target power, and an inexpensive logic analyzer. Fault cells are generated with open-drain clamps and target firmware that stops after address ACK, write-byte ACK, or a held line. Each cell receives 100--500 repetitions, with source-selected timing and target cells held out from policy selection.

Compare:

1. always retry;
2. always nine-clock recovery;
3. always power-cycle;
4. the fixed staged driver (bounded read, retry if bus free, standard recovery if SDA is low and SCL toggles, power-cycle after fixed failures, otherwise manual);
5. the probe-informed policy;
6. an oracle using hidden fault labels, for an upper bound only.

Log read success, deadline miss, latency, lost samples, collateral register writes and energy. Use the analyzer/controller only to establish ground truth and timing; never leak its hidden labels into a policy.

## Feasibility and ethics gates

The benchtop circuit is low voltage, non-production and contains no personal data or safety actuation. Before purchase, verify GPIO voltage compatibility, sensor reset behavior, sacrificial/read-only registers, MOSFET clamp current, logic-analyzer sampling rate and the availability of a power measurement method. Exact board SKU, instrument access, delivery time and budget ceiling remain [GAP] and are a September preflight gate, not an assumption.

## One-year plan

- **September 2026:** buy/borrow parts, freeze topology, register fault cells, loss weights and probe budget; run electrical preflight.
- **October:** implement transaction logger and fault injector; reproduce Linux/TI/NXP recovery behavior and measure collateral-write cases.
- **November:** run staged-driver baselines and the first intervention pilot; stop the positive claim if the probe cannot be independently counted or does not change outcomes.
- **December:** deliver the runnable benchtop demo showing fault injection, bounded action selection, outcome logging and an ambiguity/unknown state.
- **January--June 2027:** add held-out target/timing cells, repetitions, confidence intervals, sensitivity to cost weights, and only then optimize the policy or hardware.

## Kill and pivot rules

Kill the positive thesis if the probe-informed policy fails to beat the matched staged driver at equal budget, if the probe is not independent of the injected fault label, if collateral writes cannot be detected, or if the exact-claim recheck finds the same endpoint. Pivot to a device-specific replication of Linux/vendor recovery with a measured finite ambiguity map, or to a pure negative result showing that passive prefixes and the tested probe are insufficient. Do not add a neural model, extra modality or larger deployment to rescue a failed identification claim.

## Mentorship and audit requirements

One advisor review is needed for I2C electrical safety/reset semantics; one for experimental design and confidence intervals. The report must include the complete fault-state table, raw traces, action budgets, preregistered weights, all baseline results, negative cells, and exact literature queries/dates. No claim may exceed the registered topology and tested fault family.
