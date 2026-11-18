# G15 Biometrics | Palm recognition on Raspberry Pi

This folder continues the supplied school repository snapshot `e5cba8e2dfaeea008e4b56720394bd4e0c850292`. Start with [Progress Reports](minutes_note/progress_reports/README.md) for what changed and [the original demo](palm_demo/README.md) for how the system is structured. The demo and the later offline recognition experiments are separate: the latter are not a new Pi release.

## Meeting and experiment notes

- [4 September: project scope](minutes_note/2026-09-04.md)
- [18 September: acquisition, alignment and outstanding validation](minutes_note/2026-09-18.md)
- [22 September: IR setup and pilot limitations](minutes_note/2026-09-22.md)
- [20 October: recognition at different distances](minutes_note/2026-10-20.md)
- [30 October: data collection and evaluation](minutes_note/2026-10-30.md)
- [17 November: white-background comparison, ROI refinement and proposed video trial](minutes_note/2026-11-17.md)

These are historical notes. Later progress reports are retrospective summaries of dated work, not invented meeting minutes. Reports are dated by the supporting evidence, not an assumed weekly schedule.

## Code and evidence

For the offline work, start with [research code and run instructions](research_code/README.md), [integrated experiment report](minutes_note/progress_reports/2026-11-18.md).

The school snapshot's `palm_demo/` contains capture, landmark-based ROI extraction, gallery, matching, simulated payment, tests and offline evaluation tools. See its README and requirements before running anything. Optional model files and original capture data are not redistributed here. A clean checkout alone does not reproduce the private trained systems or the reported dataset scores.

[Latest offline findings](minutes_note/progress_reports/2026-11-18.md) explain corrected coordinate handling, a difficult-scene failure analysis and the limits of the X-Palm reproduction. Rank-1 counts include the planned query denominator; failure to return a crop must not disappear from the headline score.


Two later project modules are included alongside the original code: `palm_demo/roi_sampling.py` samples an original RGB image at a supplied quadrilateral (it does not find the palm), while `palm_demo/palm_app/frame_scheduler.py` prevents stale frames from being reused by a busy inference worker. Their tests use artificial arrays and timestamps. From `palm_demo/`, with Python 3.10+, NumPy and pytest installed:

```sh
python -m pytest -q tests/test_roi_sampling.py tests/test_frame_scheduler.py
```

The original local 22 September pilot Word report and two original ONNX model files are retained in the supplied school snapshot but excluded from the public Git copy. The source snapshot, not this curated mirror, is the record of those binary files. Runtime model/vendor dependencies are not bundled. The synthetic checks above do not require a model, a camera or private records.

Attendee names in the public meeting headers, machine-specific setup examples and names used in synthetic test fixtures have been generalized. The supplied school ZIP is unchanged.
