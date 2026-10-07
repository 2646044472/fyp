# E-BOUND-X Sample-Size and Estimand Gate (2026-09-27)

## Decision

The user confirmed that three separate visits can be arranged and asked the coordinator to determine the remaining feasibility independently. This supports preparing `E-BOUND-X`, but the total number of three-visit participants is not confirmed. Under illustrative paired-outcome assumptions, a small cohort would detect only very large differences in successful terminal outcomes. Keep the direction conditional and describe it as an empirical evaluation, not a new enrollment algorithm or payment-safety method.

## Two estimands that must not be conflated

### A. Matched template-policy comparison among three-visit completers

For each consenting participant with three distinct visits, freeze the matcher, gallery construction, threshold, and action policy before the untouched third visit. From visits 1 and 2, construct a small, predeclared set of shadow gallery versions for that same identity:

1. best-quality single template from visit 1;
2. fixed-size, diverse multi-template set from visit 1 (same template count as the cross-visit arm);
3. fixed-size template set with a predeclared mix from visits 1 and 2.

Capture one physical visit-3 probe, bind its frame context atomically, then evaluate it against each isolated shadow gallery/action state. Count capture/ROI failure and wrong/unknown/correct terminal decisions; do not use visit 3 to select templates, calibrate the threshold, or change any arm. Report visit-2 time and burden separately. This is a within-person comparison of later recognition/transaction decisions, conditional on people who complete all three visits. It does **not** estimate whether offering an extra visit changes return or enrollment rates. A shadow action is an offline replay of the same visit-3 episode, not repeated real payment behavior.

This is the most feasible primary estimand if the project can arrange a return cohort but cannot justify a randomized policy trial. If total template count differs, matcher search/cost differs by arm and the result no longer isolates cross-session diversity; keep template counts equal and report stored bytes/search time.

### B. Effect of offering a confirmation visit to every eligible person

If the actual decision is whether a service should ask someone to return, randomize the offer after visit 1. Keep all initially eligible people in the assigned arm, including non-returners, refusal, and enrollment failure. Compare the visit-3 transaction endpoint by intention to treat. A completer-only analysis is secondary because return attendance is selected. This estimand tests a real enrollment policy, but is a between-person randomized comparison and generally needs a larger cohort than the matched template comparison. Do not infer this policy effect from Estimand A.

## Approximate power sensitivity for the matched primary endpoint

For a paired binary endpoint such as correct terminal completion, define:

- `q = P(the two enrollment policies disagree on a person's visit-3 result)`;
- `delta = P(cross-visit policy succeeds, single-visit control fails) - P(single-visit control succeeds, cross-visit policy fails)`.

For an initial two-sided 5% / 80% power approximation, the normal paired-difference calculation is

`n ≈ (1.96 + 0.84)^2 * (q - delta^2) / delta^2`.

The table shows **complete, independent participants**, not visits, frames, or repeated probes. It assumes the specified `q` and `delta`; neither is known for this apparatus. It is a planning sensitivity only. The final calculation must use an exact McNemar power calculation for the selected endpoint and a predeclared discordance assumption, with incomplete third visits counted in the attrition plan.

| Paired discordance `q` | Net difference `delta = 20 pp` | `delta = 15 pp` | `delta = 10 pp` |
| ---: | ---: | ---: | ---: |
| 0.20 | 32 | 62 | 149 |
| 0.30 | 51 | 97 | 228 |
| 0.40 | 71 | 132 | 306 |

Thus, **about 50–70 complete people only targets a very large 20 percentage-point net gain** under `q=0.30–0.40`; a 15-point gain needs about 97–132, and a 10-point gain roughly 228–306. These are not proposed Palm performance expectations. They show the consequence of effect-size assumptions. With only 20–40 complete people, plan an exploratory paired estimate and interval, not a decisive superiority claim about terminal transactions. Visits and captures from one person do not increase the number of independent identity units.

For a zero-count wrong-action result among independent unknown people, the exact one-sided 95% upper bound is `1 - 0.05^(1/n)`: 13.9% at `n=20`, 7.2% at `n=40`, 4.9% at `n=60`, and 3.0% at `n=100`. Repeated trials of the same unknown person are clustered and cannot be substituted for independent people. Do not describe a small zero-error pilot as a low-risk or safe payment system.

## Recommended FYP-sized route

1. **Readiness gate:** freeze the local VIS executable and threshold; atomically return `(image, frame_id, timestamp, capture_id)`; store every enrollment template's source capture and visit; define an eligible start before collection; log capture, ROI, matcher, authorization/unknown label, terminal mock-action result, and all failures. Existing code inspection shows this gate is not complete.
2. **Permission gate:** obtain institutional/supervisor approval, participant consent, retention/deletion plan, and permission for later visits before collecting longitudinal biometric data. The user's statement confirms that visits can be arranged, not that approval has been granted or data collection has started.
3. **Blinded feasibility pilot:** use a small approved pilot only to measure fresh-frame/provenance integrity, visit completion, stage failures, and paired discordance `q`; do not tune on visit 3. If pilot participants or visit-3 outcomes will be used to choose the method, label the later result exploratory or reserve new people for confirmation.
4. **Primary analysis:** use a single prespecified primary contrast, e.g., cross-visit fixed templates vs equal-count within-visit diverse templates, with the same visit-3 probe and frozen threshold. Keep best-quality single-template and conservative refusal as secondary controls. Use person-level paired estimates and intervals, report all-start stage counts, and disclose that it conditions on three-visit completers.
5. **Policy claim boundary:** if the thesis story claims a confirmation visit is a practical enrollment policy, randomize the offer and count every initially eligible person by assignment; otherwise state that visit cost is observed and the matching comparison is conditional, with no causal estimate of refusal/return burden.
6. **Stop rule:** if atomic lineage, independent owner/unknown authorization, a third untouched visit, threshold freeze, or enough independent people cannot be achieved, stop `E-BOUND-X` as a confirmatory direction. Report capability/process estimates only and fall back to `OPEN-ACTION-EP` / `STAGE-NULL` if the all-start trace supports that bounded audit.

## Research boundary and kill condition

The potential result is a finite, person-blocked empirical frontier between template temporal diversity, enrollment burden, and later full-path outcome on this specific VIS apparatus. Palm-ID already supplies a strong mobile/quality/open-set/time-separated baseline, and Palm-specific template selection/update and multi-template systems are prior art. The audit found a local transaction/action endpoint difference but no method-level novelty. If equal-count same-visit templates or quality controls match the cross-visit arm, if an effect appears only after excluding non-returners/failures, or if the confidence interval remains too wide to distinguish a useful effect, do not promote the thesis claim.

## Evidence ledger

| Claim | Label | Source | Exact location / caveat |
| --- | --- | --- | --- |
| Paired binary sample size depends on the discordant outcome cells; competing approximations can differ in power accuracy. | [K] | Lachin, “Power and sample size evaluation for the McNemar test with application to matched case-control studies,” *Statistics in Medicine* 11(9), 1992, 1239–1251. https://doi.org/10.1002/sim.4780110909 | Publisher abstract and bibliographic record reviewed; it compares unconditional expressions against exact power and cautions that some approximations under- or over-estimate. |
| Incomplete paired outcomes affect both inference and sample-size planning. | [K] | Zhang, Cao & Ahn, “Inference and sample size calculation for clinical trials with incomplete observations of paired binary outcomes,” *Statistics in Medicine* 36(4), 2017, 581–591. https://doi.org/10.1002/sim.7168 | Publisher abstract reviewed; applies as a missing-visit design warning, not a Palm-specific estimate. |
| The ordinary paired-proportion comparison is based on paired outcomes/McNemar and needs explicit assumptions. | [K] | Zhang et al., “Sample Size Calculations for Comparing Groups with Binary Outcomes,” *Shanghai Archives of Psychiatry* 29(5), 2017, 316–324. https://doi.org/10.11919/j.issn.1002-0829.217132 | Publisher/PubMed record and article text summary reviewed; examples set alpha/power and use G*Power. The table above is separately calculated with the stated first-order normal approximation. |
| E-BOUND direct-neighbor boundary and local implementation/log readiness. | [K]/[E] | 2026-09-27 validation and divergence packets; workspace files `code/palm_demo/camera.py`, `palm_payment_ui.py`, `workflow.py` | See the two packets' exact section/page audit and code/log inspection. No participant experiment was conducted. |
| User can arrange three separate visits. | [K] | User response, 2026-09-27 | Confirms planned access only; participant count and completed approval remain [GAP]. |

## Queries

- `paired binary outcomes McNemar sample size formula discordant pairs primary paper power`
- `McNemar test sample size power paired proportions discordant probability exact method journal article`
- `Sample Size Calculations for Comparing Groups with Binary Outcomes DOI`
- `Inference and sample size calculation for clinical trials with incomplete observations of paired binary outcomes DOI`

## Decision

HOLD/PIVOT — prepare the matched three-visit evaluation, but do not lock it as a confirmatory thesis direction until its participant count, all-start trace, and approval/consent gates are satisfied. Do not make a superiority claim from a small convenience cohort or from a completer-only randomized-policy analysis.
