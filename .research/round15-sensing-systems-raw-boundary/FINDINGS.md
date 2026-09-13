---
topic: round15-sensing-systems-raw-boundary
created: 2026-08-31
last_verified: 2026-08-31
status: active
depth: deep
related: [pi5-rgb-noir-adaptive-sensing-boundaries, round12-sensing-divergence-boundary]
sources:
  - url: https://doi.org/10.1145/3773274.3774280
    fetched: 2026-08-31
  - url: https://arxiv.org/abs/2506.01947
    fetched: 2026-08-31
  - url: https://zenodo.org/records/17457791
    fetched: 2026-08-31
  - url: https://openaccess.thecvf.com/content/WACV2025/html/Boloor_PrivateEye_In-Sensor_Privacy_Preservation_Through_Optical_Feature_Separation_WACV_2025_paper.html
    fetched: 2026-08-31
---

# Round-15 sensing-systems/raw boundary

## Scope and date

New sensing and systems candidates beyond active IR and polarization for the purchased Pi 5 RGB/NoIR setup, researched and independently validated on 2026-08-31.

## Synthesis

`RAW-JPEG-GATE` is the only remaining new Amber hypothesis. `SLOW-CAP` was killed as a thesis mechanism by its dedicated validation: UCC/Bian/Stubbs occupy the generic stress, screen-confirm and Pi queue families. It survives only as a bounded Pi/workload replication. RAW-JPEG-GATE asks whether a scalar RAW-domain witness predicts exact-code failure beyond JPEG/decoder quality at matched bytes, latency and joules; it may legitimately return a null.

Task-aware data selectivity (TKDE 2024), Raw-JPEG Adapter (arXiv 2025) and TA-ISP (CVPR 2026) further occupy learned task-conditioned filtering, RAW/JPEG adaptation and task-aware RAW-to-RGB processing. A new adaptive compressor, modality router or task-aware ISP is therefore a component collision. The only residual claim is the finite same-exposure exact-marker test described in the preflight, with no learned router required.

`EXIF-WIT` is a preflight because the full ISM 2025 protocol and the purchased camera's raw/metadata behavior are not verified. `FRAME-ADMIT`, `PRIV-STORE` and `CHAIN-REPLAY` are KILL as thesis mechanisms: queue filtering, pre-capture/on-device privacy and post-capture integrity/provenance are already occupied or reduce to operational controls.

## Boundary

No inspected primary source establishes the exact Pi 5 RAW-vs-JPEG or telemetry-conditioned exact-marker action endpoint. This is a retrieval boundary, not evidence of novelty. A null can show that JPEG/latency-only/fixed-retry controls are sufficient.

## Strongest objection

RAW may be a strictly more expensive representation without incremental decision information: JPEG luma, blur, decoder confidence or capture metadata may be sufficient for the printed marker. Likewise, resource telemetry may only restate latency. Any positive claim must beat the matched simple baseline, not merely correlate with failure.

AAAI 2024's RAW detector/RCB and ReRAW CVPR 2025 already occupy broad “RAW improves robustness/edge vision” claims. The candidate must therefore be framed as a conditional sufficiency/action test only.

Afifi ICCV 2025 already uses RAW noise/SNR and histogram features for auto-white-balance control, and Kaparounakis et al. (Communications Engineering 2026) already quantify calibration-data representation uncertainty on-device with an edge-detection use case. These further kill a generic RAW uncertainty/quality-monitor claim.

Koukosias et al. (TKDE 2024), Chen et al. (CVPR 2026 TA-ISP), and Afifi et al. (Raw-JPEG Adapter, 2025) make generic task-aware filtering/RAW adaptation claims direct neighbors. Any positive result must be stated as a bounded physical endpoint, not as a new adaptive-sensing or compression method.

## Discarded approaches

Generic timeout tuning, frame admission, software privacy gating and hash-chain provenance are not thesis mechanisms under the inspected papers and controls.

## Open questions

- [GAP] Does the purchased Camera Module 3 expose a stable raw Bayer/DNG mode through the selected Pi software stack?
- [GAP] What are raw capture bytes, processing latency and energy on Pi 5 under the intended camera settings?
- [GAP] Does raw saturation/channel occupancy add information after JPEG/decoder quality is fixed?
- [GAP] Does CPU/memory/I/O stress change exact-code correctness independently of elapsed latency?
- [GAP] Does the finite marker endpoint expose any incremental RAW information after JPEG/decoder quality, fixed two-shot, and latency-only controls are matched?

The coordinator's executable preflight is `research/active/13-raw-jpeg-gate-preflight.md`; it requires RAW10 capability, same-exposure pairing, independent payload truth, matched cost accounting and held-out cells before any promotion.

## Decision

`SLOW-CAP`: KILL thesis / PIVOT replication. `RAW-JPEG-GATE`: HOLD (Amber). `EXIF-WIT`: PIVOT (Amber). `FRAME-ADMIT`, `PRIV-STORE`, `CHAIN-REPLAY`: KILL thesis. No candidate is PROMOTE.

## Sources

- Pourreza & Narasimhan, UCC 2025, https://doi.org/10.1145/3773274.3774280, Secs. 2, 4-7, pp. 1-10.
- Conde et al., NTIRE 2025 Challenge Report, arXiv v1 2025-06-02, https://arxiv.org/abs/2506.01947, Sec. 1 and Sec. 2.3/Table 1.
- Stubbs et al., operational poster 2025, https://zenodo.org/records/17457791, description lines 35-41.
- Boloor et al., PrivateEye, WACV 2025, https://openaccess.thecvf.com/content/WACV2025/html/Boloor_PrivateEye_In-Sensor_Privacy_Preservation_Through_Optical_Feature_Separation_WACV_2025_paper.html, abstract/Sec. 1.
- Sogabe et al., WACV 2025, https://openaccess.thecvf.com/content/WACV2025/html/Sogabe_Pre-Capture_Privacy_via_Adaptive_Single-Pixel_Imaging_WACV_2025_paper.html, Secs. 2-3.
- ZIRCON, JISA 2024, https://doi.org/10.1016/j.jisa.2024.103840, proposed system/Sec. 6.
- Vela-Koentarjo & Singh, WWW Companion 2026, https://doi.org/10.1145/3774905.3794702, pp. 1551-1555.
- Koukosias, Anagnostopoulos & Kolomvatsos, IEEE TKDE 2024, https://doi.org/10.1109/TKDE.2024.3485531, official accepted record/abstract.
- Chen et al., TA-ISP, CVPR 2026, https://openaccess.thecvf.com/content/CVPR2026/html/Chen_Task-Aware_Image_Signal_Processor_for_Advanced_Visual_Perception_CVPR_2026_paper.html, pp. 33672-33681 and official abstract.
- Afifi, Zhang & Brown, Raw-JPEG Adapter, arXiv v1 2025-09-23, https://arxiv.org/abs/2509.19624, Secs. 1, 3, 4.1, 5.
