# Cross-device / cross-illumination transfer boundary

## Scope and date

Research round completed 2026-08-31 for the confirmed Raspberry Pi 5 RGB + NoIR pair. This entry records a bounded audit, not a novelty claim.

## Findings

- [K] CCMNet (ICCV 2025, arXiv:2504.07959, Secs. 1, 3.2-3.4, 4.2, App. C) already evaluates camera-disjoint zero-shot color transfer with calibrated device information. Lens (arXiv:2503.02170v3, Secs. 3.1-3.2, 4-5) occupies adaptive camera control under a capture budget.
- [K] Punnappurath et al. (arXiv:2508.14730v1, Secs. 1-3, App. C) document sensor/illumination mapping and warn that a single chart under-represents material diversity. Moravec & Sara (2024, Secs. 1-2, 4-5) and Wei et al. (2024) occupy online calibration monitoring/self-check.
- [K] CIE S 017:2020 Definition 17-21-060 defines illuminance as a photopic spectral weighting. Equal-lux spectra can differ in NIR power, so lux is not an independent NoIR witness.
- [K] Agnihotri et al. (CVPRW 2025, Secs. 1, 4.1-4.2, 5) occupy broad synthetic-versus-real corruption proxy testing; aggregate correlation can hide per-corruption failure (Pearson .270 for brightness/night and .349 for fog/fog).
- [K] Tesla Service Bulletin SB-24-17-005 R2 (2025-04-03, p. 1) documents reduced low-light driver-attentiveness performance as a camera-replacement condition. This validates an optical-maintenance context for a bounded IR-path study, but does not identify transparent-cover cause or establish a new Pi diagnosis method.
- [KILL] Rampure et al. (arXiv:2606.17376v1, 2026-06-16, Sec. III-A) already use a brightness threshold to select RGB/NIR/thermal/low-light on three heterogeneous robots and edge architectures. Their Sec. IV labels controlled breathing phases by expected BPM ranges rather than a concurrent reference (lines 117-121), so the only defensible residual is an externally labeled exact-marker physical action audit, not another adaptive selector.
- [KILL] Passive optical health is also occupied: Medici et al. (Acta IMEKO 14(2), 2025) use sharpness metrics for infrared-camera contamination diagnosis, and Aher (arXiv:2605.05439, 2026) uses a degradation-aware health index from a single RGB image across twelve degradation modes. `OPT-WIT` is therefore killed as a passive-health thesis; only active IR intervention with independent physical labels remains Amber.

 - [KILL] Chaichi Mellatshahi et al. (ICASSP 2026) already perform online Bayesian-risk sensor selection, defining risk as computation cost plus detection-error cost and switching between pipelines. The exact RGB/NoIR endpoint differs, but a risk-minimizing router is a method-level collision; retain only the finite physical action-ordering/non-identifiability question.
- [KILL] RGB/IR synchronization and registration are established method families: RocSync (arXiv:2511.14948, 2025) reports millisecond alignment with an LED Clock and downstream gains, while Kim & Baek (arXiv:2411.18025, 2024) provide pixel-aligned RGB-NIR stereo. Pi sequential-capture timing should be a logged/blocking factor, not a claimed contribution.

## Decision boundary

`XFER-ACT` is PIVOT/Amber: only a finite, preregistered exact-marker action-rank audit on blocked camera/lamp cells with independent oracle and matched joules is defensible. It cannot provide a camera-family transfer guarantee. `LUX-VOI` is KILL as a thesis and instrumentation-only; `PANEL-GATE` and `CAL-SCHED` are KILL as mechanisms; `REAL-DIG-RANK` is a bounded negative benchmark.

## Pilot gate

Use fixed RGB, fixed NoIR+IR, fixed two-shot, scalar brightness/blur/IR-ratio, random, and oracle controls. Freeze manual/logged exposure and white balance, block lamp/material/device cells before tuning, and run the two-world identifiability test. Promote only on a repeatable held-out action-rank inversion; otherwise report a useful null and do not lock the FYP.

## Sources

- https://arxiv.org/abs/2504.07959
- https://arxiv.org/html/2503.02170v3
- https://arxiv.org/abs/2508.14730
- https://link.springer.com/article/10.1007/s10044-024-01264-1
- https://doi.org/10.1088/1361-6501/ad6469
- https://cie.co.at/eilvterm/17-21-060
- https://arxiv.org/abs/2505.04835
- https://service.tesla.com/docs/ServiceBulletins/External/SB/SB-24-17-005_Replace_Interior_Camera_R2.pdf
- https://arxiv.org/abs/2606.17376
- https://doi.org/10.21014/actaimeko.v14i2.1944
- https://arxiv.org/abs/2605.05439
- https://doi.org/10.1109/ICASSP55912.2026.11463373
- https://arxiv.org/abs/2511.14948
- https://arxiv.org/abs/2411.18025
