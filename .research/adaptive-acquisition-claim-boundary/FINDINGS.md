# Adaptive acquisition claim boundary

## Scope and date

Round completed 2026-08-31. The question is whether a low-cost edge FYP can claim a new adaptive sensing, abstention, or sensor-fault robustness mechanism using the Pi 5 RGB/NoIR pair.

## Established direct neighbors

- [K] QIC (SECON 2024, DOI 10.1109/SECON64284.2024.10934843) jointly selects sensor sources, DNN branches, placement and resources under latency, quality, reliability and energy objectives: https://research.chalmers.se/en/publication/545985.
- [K] Bian et al. (Sensors 26(16):5065, version of record 2026-08-10) use low-cost screening, high-information confirmation, uncertainty/OOD escalation, watchdog bounds, device/condition shift and few-shot commissioning: https://www.mdpi.com/1424-8220/26/16/5065, Secs. 1, 3.1, 5.1, 8.
- [K] BCEA (arXiv:2606.16667, 2026-06-15) formalizes `answer / abstain / acquire`, proves naive post-acquisition threshold reuse is anti-conservative, and requires post-acquisition recalibration: https://arxiv.org/abs/2606.16667, Secs. 1, 4.3, 5.
- [K] SensorFault-Bench (arXiv:2605.10822v1, 2026-05-11) standardizes value/timing/availability faults, disjoint fault-transfer splits and clean-vs-fault ranking disagreement: https://arxiv.org/abs/2605.10822, abstract and Secs. 1-5.
- [K] DeepArUco++ (arXiv:2411.05552, 2024) covers difficult-light marker detection, corner refinement, decoding, synthetic/real data and failure cases: https://arxiv.org/abs/2411.05552, Secs. 3-5.6.

## Decision boundary

Generic adaptive modality selection, energy-aware routing, conformal abstention wrappers, broad synthetic-vs-real robustness claims, and marker-decoder improvements are [KILL] as thesis mechanisms. `XFER-ACT`/`IR-CAUSE` survive only as [PIVOT]/[Amber] finite physical tests with a static exact marker, independent physical labels, an external oracle, blocked camera/lamp/material cells, logged exposure, and matched action/energy costs.

## Identifiability and negative path

If two physical worlds produce the same pre-action RGB preview/metadata but require different optimal actions (for example transparent-cover glare versus low visible light), no policy using those observations can certify the choice. A null or rank-preservation result is therefore scientifically useful and should be reported rather than converted into a model claim.

## Next gate

Run the preregistered pilot in `research/active/11-cross-device-action-rank-pilot.md` before buying more sensors. Promote only a repeatable held-out risk-cost rank inversion that fixed two-shot, conservative escalation and scalar quality controls cannot match.

