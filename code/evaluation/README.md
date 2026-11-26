# Evaluation tools

`paired_outcomes.py` compares two methods on exactly the same predeclared queries. It counts queries both methods got right, only one got right, and neither got right, without dropping attempts with a missing ROI, missing enrollment, or other failures. Use it on results already obtained locally; it does not run models or choose thresholds.

```sh
python code/evaluation/paired_outcomes.py --help
python code/evaluation/paired_outcomes.py --self-test
```

Keep per-query and participant-linked inputs outside Git and share only reviewed aggregates. See the [dataset catalog](../../dataset/README.md) for evaluation roles and the [experiment checks](../experiments/README.md) for split and coverage examples.

To compute strict Rank-1 directly from pre-extracted features, use the [local aggregate ranker](rank-features.md). It supports fixed-five or variable-size galleries and keeps every planned known query in the denominator. It does not extract features, estimate an acceptance threshold, or recreate historic splits.
