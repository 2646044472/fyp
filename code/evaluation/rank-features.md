# Local aggregate Rank-1 scoring

`rank_features.py` scores already-extracted local embeddings. It does not load a model, open a camera, download a dataset, fit thresholds, or export an identity or score table. Keep the manifest and archives off Git and on authorized storage. Sample keys establish declared row linkage, not identity correctness, release provenance, consent, or split independence.

## Input contract

Use three local files:

1. One JSON plan with `schema: 1`, `gallery` and `queries` arrays. Each row has `sample` (nonempty unique string across both roles), `hand` (nonempty string, or `null` for a declared unknown query only), and `feature_row` (the zero-based matrix row, or `null` when absent). Every planned query stays in the array. Use `null` rather than dropping a query whose crop or extraction failed.
2. One gallery `.npz` archive containing just a real floating-point `features` array of shape N×D. Use `np.savez(path, features=matrix)` or `np.savez_compressed`. Use floating point, not object arrays or pickled Python structures.
3. One query `.npz` archive with the same contract and feature dimension D. There must be an exact one-to-one linkage between non-null row references and physical matrix rows in each role. Even a role without any available embeddings uses a shaped `(0, D)` archive.

An artificial plan illustrating linkage, not a sample dataset:

```json
{"schema":1,
 "gallery":[{"sample":"synthetic-enroll","hand":"synthetic-A","feature_row":0}],
 "queries":[{"sample":"synthetic-good","hand":"synthetic-A","feature_row":0},
            {"sample":"synthetic-missing","hand":"synthetic-A","feature_row":null},
            {"sample":"synthetic-other","hand":null,"feature_row":1}]}
```

## Run

Install NumPy in the development environment and choose the exact scoring route and gallery policy before examining results:

```sh
python code/evaluation/rank_features.py \
  --plan /LOCAL/plan.json \
  --gallery-features /LOCAL/gallery.npz \
  --query-features /LOCAL/query.npz \
  --route cosine --gallery-policy fixed-five

python -m unittest discover -s code/evaluation -p test_rank_features.py
```

- `cosine` normalizes each valid vector before scoring. `dot` uses the original vector magnitudes. Both use float64 arithmetic and treat missing, zero, or nonfinite embeddings as unavailable. A nonfinite computed score makes that whole query unscored, rather than silently dropping the affected comparison.
- `fixed-five` requires exactly five **planned** gallery rows for every declared enrolled hand, and will only rank hands with all five vectors usable. A malformed four- or six-row plan is an input error. Five planned rows with unavailable features are valid input but make the associated hand unavailable; there is no substitute enrollment. `available` instead uses hands with at least one usable reference. Use `available` for the one-reference artificial plan above or an intentionally variable-size legacy protocol.
- For each eligible hand, rank its maximum similarity over its gallery vectors. An exact top-score tie across distinct hands is counted separately and is not a correct Rank-1. A tie between two gallery vectors of the same hand is not a between-hand tie.
- Known queries with unavailable true-hand galleries and known queries without usable vectors remain in the planned-known denominator. When both fail, the missing query feature is the reported outcome. Unknown queries are reported separately as coverage/ties; this is not a thresholded unknown-identity rejection test.

The JSON output contains aggregate counts and strict Rank-1 over all planned known queries. It does not calculate acceptance metrics, EER, replay/normalization studies, or all-query top-k hubness. Record input provenance, the declared plan, and any experiment's split guarantees separately on authorized storage. Synthetic checks establish the software contract only.
