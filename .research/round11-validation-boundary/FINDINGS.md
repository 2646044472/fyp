# Round-11 validation boundary

## Scope and date

Independent validation of divergence rounds 8--10 and the current Pi 5 RGB/NoIR reopening, completed 2026-08-31. This is a falsification record, not a novelty claim.

## Decision

No candidate passes all three audits. `CSI-BaselineGate`, `UWB-RL-CAUSE`, `MAG-GeometryWitness`, `MMW-ClutterWitness`, `AQ-ReferenceFreeAudit`, `SCHED-PUB-STREAM`, `PSI-EVENT-JOIN`, `RVK-LOCAL-LEASE`, `DP-BUDGET-MICROEDGE`, `FLICK-PHASE`, `RS-DRIFT`, generic RGB/NoIR adaptive or Bayesian-risk routing, passive optical health, and standalone synchronization are KILL. `PWR-WIT` is instrumentation-only; `CRDT-ESCROW-LIMIT` is a baseline/negative replication; `PLAR-Safe` is only a negative privacy--deadline frontier. `PRF-TR`/`PHY-MASK`/`FULL-CAP` remain finite physical-vs-digital action audits. `IR-CAUSE` is the sole HOLD/Amber candidate, restricted to an active IR incremental-information test.

## Evidence

- OpenCSI (arXiv:2607.26665) occupies CSI stale-baseline reliability and abstention.
- Peterseil et al. (Sensors 24:5268, 2024) and Yang et al. (Measurement 256:117721, 2025) occupy UWB link/system trust and ranging-error credibility.
- Medici (Acta IMEKO 2025), Aher (arXiv:2605.05439) and Ma et al. (arXiv:2607.14760) occupy passive optical health.
- Basmer (AAAI 2025), DPack (EuroSys 2025), PEPSI (USENIX Security 2024) and EVOKE (USENIX Security 2024) occupy schedule privacy, DP-budget scheduling, private joining and offline revocation.
- Lens, AdaptiveAE, CM-ASAP, Rampure (arXiv:2606.17376) and Chaichi Mellatshahi (ICASSP 2026) occupy camera/adaptive/risk routing.
- RocSync (arXiv:2511.14948 v1; Sensors 26(3):1036) and Kim & Baek (arXiv:2411.18025 v2) occupy RGB/IR synchronization and alignment. Full-text audit confirms RocSync Secs. 2.3-2.4, 3.1-3.2, 5.1 and 6 (pp. 3-8, 14-15), and Kim--Baek pp. 1-4 and 7.

## Boundary

Passive observations can be shared by two physical worlds that require different actions. A finite fixture can still be identifiable if labels, marker oracle, exposure/white balance, timing, energy and held-out cells are independent and frozen. Any positive result is a bounded empirical effect, not a transfer theorem or causal-diagnosis framework. Full Yang/VCIP PDFs and a modern CRDT primary remain [GAP]; RocSync/Kim--Baek retrieval and page audits are complete.

## Next gate

Run the preregistered RGB/NoIR pilot with fixed two-shot, always-reacquire and scalar-quality controls. Promote only a repeatable held-out action-rank inversion; otherwise report rank preservation or a two-world non-identifiability result.

## Round-12 extension

The new physical-frequency divergence was audited independently. `IR-MOD-ID` is HOLD/Amber only as a two-frequency IR incremental-information test; `LUX-AMBIG` is a matched-spectrum negative benchmark; `ABSENCE-PULSE`, `IMU-BLUR-ATTR` and `EVENT-DROP` are replication or infeasible branches. The validation packet confirms that no candidate passes all three audits, so the minimum active-IR pilot remains the only live gate.

## Source packet

See `research/ops/validation/2026-08-31-round11-validation.md` for search queries, exact source sections/pages and candidate-by-candidate kill tests.
