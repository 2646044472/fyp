# Palm-Payment Acceptance and Story Boundary Log

Last updated: 2026-08-21. This log tests whether palm payment is a defensible application story, using recent primary adoption studies. It is intentionally not a Macau market-size claim.

## Sources inspected

| Work | Material | Findings relevant to the story | Limits |
| --- | --- | --- | --- |
| [Domingo et al., Acta Psychologica 2025](https://doi.org/10.1016/j.actpsy.2025.105426) | Journal abstract/full page and methods/results summary | A survey of 421 valid responses used TAM plus valence factors. Behavioral intention, perceived ease of use, perceived usefulness and attitude were important; perceived risk did not significantly influence intention in this sample, while trust was still emphasized for secure transactions. Data were collected via social-media responses and made available on request. | Non-probability online sample; not Macau, not a deployment or throughput study, and no comparison against QR/cards or actual palm hardware. Do not convert coefficients into local demand or ROI. |
| [Nguyen et al., Discover Psychology 2025](https://doi.org/10.1007/s44202-025-00548-9) | Open full article page, methodology, findings and limitations | 413 respondents with prior mobile/biometric-payment experience were analyzed with PLS-SEM, ANN and fsQCA. Perceived trust was the strongest ANN predictor (100% normalized importance; PLS-SEM beta 0.252), with habit and effort expectancy also important. The paper stresses active participation, proximity and specialized NIR infrastructure; it reports palm-payment adoption intention, not real usage. | Judgmental/non-probability sampling, Vietnamese context, self-reported intention, and no palmprint-vs-palm-vein hardware comparison. The paper's claim that palm payment is “widely adopted” is background framing, not evidence for Macau. |

## What the reading changes

1. The user's lived observation that palm scanning is not a normal Macau experience is compatible with the literature: adoption depends on trust, habit, ease, facilitating infrastructure and an intentionally performed hand gesture. It is a hypothesis about local exposure, not evidence that a market gap exists.
2. Payment is a poor FYP story. It requires registration, settlement, backend risk controls, specialized NIR hardware and user trust; a Pi reader cannot test the economic system. Existing payment deployments and acceptance studies already occupy that problem.
3. A useful application story must prove a local operational bottleneck that QR/card/manual fallback does not already solve. Therefore the proposed maintenance/tool-issue scenario remains conditional and must be validated by interviews and timing observations.

## Interview implications

Ask about actual frequency, current alternative, failure/retry cost, acceptable gesture/time, consent and deletion. Do not ask “would you buy palm payment?” and treat a Likert score as deployment evidence. If no low-frequency single-person bottleneck exists, stop forcing an economic story and report a measurement benchmark.

## Wording

Use: “Recent adoption studies identify trust, effort, habit and infrastructure as conditions for palm-payment use; they do not establish a Macau need.”

Do not use: “Macau lacks palm payment,” “users will accept it,” or “palm payment creates a proven ROI.”

