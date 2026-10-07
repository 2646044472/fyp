# Validation Audit: 2026-09-24 GALLERY-CHURN-NULL

## Decision investigated

Audit `GALLERY-CHURN-NULL`: in Palm open-set 1:N recognition, the enrolled gallery changes as users are added, removed, or updated and template counts per identity change. The proposed object is a dynamic-gallery person/time-blocked risk frontier or a negative result, not a new matcher and not a simple per-gallery threshold.

The required question is whether fixed-gallery evaluation can misstate unknown/false-identification risk, rank or margin behavior, and threshold stability when gallery composition changes. This audit is Palm-only and treats Pi, latency, energy, and a simulated transaction as constraints or endpoints, not as novelty.

Required files were read first: `AGENTS.md`, `research/active/README.md`, `research/active/00-project-charter.md`, `research/active/01-candidate-register.md`, `research/active/42-round-27-palm-only-reconciliation.md`, `research/active/43-round-28-palm-stop-reconciliation.md`, and `research/ops/agent-validation.md`. This packet writes only to `research/ops/validation/`.

## Claim under test

Let an open-set Palm query be evaluated against a gallery state \(G_t\), with enrolled identities, template counts and template ages changing over time. The candidate's strongest defensible claim would be:

> Under a frozen Palm matcher and a predeclared operating point, a fixed-gallery report does not identify the person/time-blocked terminal risk frontier after gallery additions, removals, and template updates; risk, rank/margin distributions, and threshold stability must be reported over held-out dynamic gallery states.

This can only be a finite evaluation or negative-result claim. A positive algorithmic claim such as `dynamic thresholding`, `gallery admission`, or `churn-aware calibration` is outside the surviving scope and collides with `G-ADMIT`.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| 1. Gallery-aware recognition/calibration | [KILL-leaning] NIST 1:N evaluation explicitly treats false-positive identification as a function of gallery size and operating threshold, and reports FPIR/FNIR under controlled gallery/search conditions. ISO/IEC 19795-5 defines biometric identification testing and the need to specify the enrolled population, search population and test protocol. Per-gallery thresholds, score normalization, quality controls, and gallery-relative calibration are the same mechanism family as `G-ADMIT`. | A Palm-specific replay that preserves person/time blocks and measures add/remove/update sequences could expose when a fixed-gallery report is not transportable to later states. That is a protocol/measurement result, not a new calibrator. | High collision for method; medium for the exact Palm negative benchmark. |
| 2. Open-set identification, OSCR, FPIR/FNIR | [KILL-leaning] Open-set recognition already studies unknown rejection and the joint tradeoff between known classification and unknown detection; biometric 1:N protocols already use FPIR/FNIR and rank-based reporting. Thresholds necessarily depend on the nonmate score population, so increasing gallery size changes the maximum nonmate score even with an unchanged matcher. Fixed threshold, gallery-size-stratified threshold, max-score order-statistic control, recalibration, and refusal are immediate baselines. | The residual test is whether those known metrics and controls fail to predict a terminal Palm action risk when gallery state and time are blocked, with every eligible query retained. A null result or non-identifiability result is scientifically useful if the sequence is independently labelled. | High collision for metrics; medium for the bounded Palm endpoint. |
| 3. Template aging/update/identity churn | [KILL-leaning] Longitudinal biometric work already studies template aging, representative-template selection, template update and time-separated evaluation. Adding a user, deleting a user, or replacing a template is ordinary gallery lifecycle manipulation; per-user template count is a known source of score and rank changes. A churn trace with no independent time or authorization labels is only a synthetic ordering experiment. | A finite Palm protocol may remain if add/remove/update events are predeclared, user/time blocks are independent, updates are collected at a later visit rather than selected from the test visit, and the query/action label is external to the matcher. | High collision for mechanism; low-to-medium residual feasibility. |

## Assumption and identification audit

### What is identifiable

1. For each query, the matcher can expose the top score, second score, rank, identity, template count per identity, gallery size, gallery-state ID, and calibrated decision.
2. A gallery state can be replayed exactly if templates are versioned and the state transition log is immutable.
3. `FPIR`, `FNIR`, rank and margin are estimable only relative to a declared gallery state, query population, operating threshold, and mate-present/mate-absent sampling rule.
4. A terminal wrong/correct/unknown action is estimable only when authorization and ground truth are independently recorded; it cannot be reconstructed from the matcher’s top identity.

### What is not identifiable from ordinary Palm data

- A real-world user removal or account revocation sequence is not represented by a cropped palm image. A synthetic deletion order is a stress test, not evidence about operational churn.
- A template update cannot be separated from session, pose, illumination, device, or capture-quality drift unless visits and acquisition conditions are logged independently.
- A change in maximum nonmate score cannot by itself be attributed to gallery size, identity composition, template quality, or correlated identities.
- A lower false-identification rate after deletion may be caused by removing a hard identity rather than by a robust lifecycle policy.
- A fixed-gallery threshold and a dynamic-gallery threshold cannot be compared fairly if one is tuned using future gallery states or if mate-absent queries are re-sampled after seeing the scores.
- Public cropped Palm datasets do not establish that a live Pi capture reached ROI, 1:N, authorization, or mock action. A gallery-only result must not be reported as payment risk.

### Required split

Use person-disjoint and time/session-disjoint blocks. Enrollment/update data must precede the query block. The state-transition schedule must be fixed before scoring. Do not select the “hardest” identities for deletion or update after observing ranks. Keep original eligible-query denominators, including queries that fail capture or ROI if the claimed endpoint is full path.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| NIST FRVT 1:N / 1:N Identification | Probe image, enrolled gallery, search threshold and gallery size; mate-present and mate-absent searches | FPIR/FNIR, rank and demographic/error reporting under specified galleries | Kills the claim that gallery-size-dependent open-set risk is an unstudied metric issue | Leaves open only a finite Palm state-replay protocol; NIST is not a Palm Pi action study |
| NISTIR 8271, *Face Recognition Vendor Test (FRVT) Part 2: Identification* | 1:N probe/gallery experiments with gallery-size and threshold controls | False positive identification and false negative identification under operationally defined search settings | Kills a generic “gallery composition changes threshold stability” method claim | Does not supply Palm-specific longitudinal add/remove/update traces |
| ISO/IEC 19795-5:2025, biometric identification performance testing | Declared enrolled/search populations, identification test protocol and reporting | Identification performance with explicit population and test conditions | Kills presenting state-conditioned FPIR/FNIR reporting as a new measurement standard | Leaves a narrow Palm implementation/negative result if it follows the standard and states its scope |
| Scheirer et al., *Toward Open Set Recognition*, TPAMI 2013 | Known and unknown samples, recognition plus rejection score | Open-space risk and known-class recognition/rejection tradeoff | Kills generic unknown rejection and open-set risk-frontier novelty | Does not model Palm gallery lifecycle or terminal action |
| Dhamija et al., *Reducing Network Agnostophobia*, NeurIPS 2018 | Known/unknown classification scores | OSCR-style open-set classification/rejection analysis | Kills OSCR as a new endpoint or evidence that unknown rejection alone is the gap | Leaves only a biometric 1:N, state-blocked measurement question |
| Chen et al., *Long-Term Representative Template for Palmprint and Palm-Vein Recognition*, IEEE Access 2019 | Time-separated palmprint/palm-vein samples and template-selection/update logic | Long-term recognition and representative template construction | Kills template aging/update as an unoccupied Palm mechanism | Does not test user add/remove identity churn or mock action |
| Palm-ID, arXiv:2401.08111v1 (2024) | Mobile palm capture, ROI, quality, enrollment and open-set 1:N | On-device Palm identification and capture pipeline | Kills a claim that adding live ROI/quality/1:N to a Palm gallery study is itself novel | Does not establish dynamic lifecycle traces on the target Pi path |
| Existing `G-ADMIT` audit, 2026-09-23 | Fixed gallery, mate-present/absent controls, gallery-relative/per-gallery threshold alternatives | Gallery admission/calibration and unknown handling | Directly kills `GALLERY-CHURN-NULL` if its output is a threshold, admission, recalibration, or gallery policy | Only a bounded benchmark/null survives if it refuses to propose a policy and uses independently staged states |

## Strongest simple baseline

The minimum baseline matrix must include all of the following before interpreting a dynamic-gallery effect:

1. **Fixed global threshold:** one threshold frozen on an enrollment-development block; report risk separately for every later gallery state.
2. **Gallery-size-stratified threshold:** thresholds calibrated separately by total template count or identity count, using no future test queries.
3. **Max-score order-statistic control:** estimate the nonmate maximum-score distribution as a function of gallery size and compare the observed top score/margin shift with that prediction. This tests whether the effect is only the expected maximum-of-many phenomenon.
4. **Recalibration control:** recalibrate on a held-out nonmate/mate block after each state transition, with calibration data and state timing charged and disclosed.
5. **Refusal/unknown control:** abstain whenever score or margin is below the fixed safety operating point; report completion loss and action risk, not accuracy alone.
6. **Template-count control:** hold identity count fixed while varying templates per identity, then hold template count fixed while varying identity composition. Otherwise “gallery churn” confounds two different causes.
7. **State-order permutation:** repeat several predeclared add/remove/update orders. A single arbitrary order cannot support a churn claim.

If a proposed result disappears against these controls, it is either ordinary gallery-size calibration or a composition artifact. If all controls are unavailable, the candidate is not identifiable.

## Contrarian result

The central observation is mathematically unsurprising: with a fixed nonmate score distribution, the maximum of more nonmate comparisons tends to increase as the gallery grows. A fixed threshold can therefore show more false accepts while the matcher and per-comparison score distribution remain unchanged. This is an expected 1:N effect, not evidence of a new Palm phenomenon.

Likewise, removing a difficult identity or adding a high-quality template can change ranks and margins without any algorithmic degradation or improvement. A gallery-state trace can document this confounding, but it cannot infer a causal “churn risk” unless the transition and the query population are independently assigned.

Therefore:

- `GALLERY-CHURN` as a dynamic threshold, gallery admission, recalibration, or robust matcher method is **KILL** and is a rename of `G-ADMIT`.
- `GALLERY-CHURN-NULL` can remain only as a Palm-specific **benchmark/negative-result**: fixed-gallery summaries fail to transport across predeclared person/time-blocked states, or the available observations cannot distinguish composition, template count, and aging effects.
- It must not claim that real user churn has been measured if the sequence was generated by deleting rows from a public dataset.

## Feasibility audit

### Public Palm data

- PolyU 2D/3D Palmprint Database is a controlled research database with repeated captures, but its access, licensing, and collection protocol do not provide a naturally occurring account add/remove/update event log. It can support time/session blocking, not real identity churn.
- IIT Delhi Touchless Palmprint Database and CASIA palmprint resources provide multiple images/conditions useful for person-disjoint gallery construction, but the public image records do not encode lawful user enrollment, revocation, account authorization, or an untouched terminal transaction.
- Public data can support a synthetic state-replay null only if the state-generation rule is preregistered and reported as synthetic. It cannot support a claim about operational churn or payment risk.
- Chen et al. supply a Palm longitudinal/template-update neighbor, but reproducing a later-visit update sequence requires access to the underlying time-separated data or an equivalent authorized collection; a citation is not a data license.

### Pi and live-path feasibility

- A Pi 5 can replay small galleries and log score/rank/margin distributions, but small galleries may have too few identities for stable tail FPIR estimates. The experiment needs many independent mate-absent queries or an explicitly bounded uncertainty analysis.
- Exact gallery-state replay requires versioned templates, deterministic matcher settings, state IDs, and a charged cost for recalibration. A mutable local database without immutable state snapshots cannot reproduce the claim.
- A live payment path adds capture/ROI/action denominators. The candidate must first pass the existing all-start trace gate in `42-round-27` and `43-round-28`; otherwise it is only an offline matcher benchmark.
- Adding and removing real users raises consent, retention, deletion, re-identification, and access-control obligations. The project charter's identifier-free route does not automatically authorize persistent identity-linked gallery lifecycle data.
- A one-year undergraduate project can run the small replay benchmark, but collecting enough independent unknown people and repeated visits for a stable person/time-blocked tail is the main feasibility risk.

### Ethics and permissions

Do not use “user removal” as a proxy for deletion of a person's biometric record unless the consent and retention policy explicitly covers it. Do not re-identify public Palm images or link gallery state to real accounts. A mock transaction is safer but still requires authorization labels and an idempotent action log.

## Minimum experiment and kill/pivot gate

### Minimum experiment

1. Freeze one Palm VIS matcher, ROI path, template format and decision policy.
2. Build at least three predeclared gallery-state families: identity-count change, template-count change with identity count fixed, and template update/age change with gallery size fixed.
3. Use person-held-out query identities and session/time-held-out queries. Preserve an independently labelled mate-absent block; do not synthesize unknown labels from a top-score cutoff.
4. Replay every query against every predeclared state, recording top score, second score, margin, rank, identity, template count, state ID, threshold, unknown decision, stage reachability and action authorization where available.
5. Compare the seven baselines above with bootstrap confidence intervals or an explicitly justified uncertainty bound. Report FPIR/FNIR, rank/margin distributions, calibration error, refusal/completion, and terminal action risk separately.
6. Repeat state orders and include a no-churn control with identical total query count and compute budget.

### Kill gate

Kill the candidate immediately if any of these hold:

- the proposed policy is a per-gallery threshold, recalibration, admission, or refusal rule;
- only public cropped data are available and the claim is about live Pi/payment risk;
- state transitions are chosen after looking at test scores;
- there are no independent mate-absent or authorization labels;
- “remove/update” is only random row deletion or template replacement with no time/identity semantics;
- fixed threshold plus max-score order-statistic control explains the entire result;
- gallery size, identity composition, template count and template age cannot be separated;
- uncertainty intervals are too wide to distinguish the candidate from fixed-gallery evaluation.

### Pivot gate

Retain `GALLERY-CHURN-NULL` as a bounded negative-result benchmark only if the team can produce immutable, preregistered state transitions, lawful Palm data, person/time-blocked queries, independent unknown labels, and enough repeated states to show either a reproducible transport failure or a clear non-identifiability boundary. The output must be a state-conditioned evaluation protocol and evidence ledger, not a new matcher or threshold algorithm.

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| 1:N false-positive risk depends on gallery size and threshold; FPIR/FNIR are operationally defined identification measures. | [K] | NIST, *Face Recognition Technology Evaluation (FRTE) 1:N Identification*, official results portal, current page accessed 2026-09-24: https://pages.nist.gov/frvt/html/frvt1N.html | Definitions and gallery/search-size discussion on the 1:N results page; verify the cited release PDF before thesis use | Face, not Palm; direct metric/protocol collision rather than modality equivalence |
| Biometric identification testing requires explicit enrolled/search populations and declared test conditions. | [K] | ISO/IEC 19795-5:2025, official standard record: https://www.iso.org/standard/83648.html | Scope and abstract; normative full text not freely accessible | Use the licensed standard for clause-level citation |
| Open-set recognition explicitly evaluates known recognition together with unknown rejection/open-space risk. | [K] | Scheirer et al., *Toward Open Set Recognition*, IEEE TPAMI 2013, DOI: https://doi.org/10.1109/TPAMI.2012.256 | Secs. I-III and V in the published article | Generic recognition; not Palm or 1:N transaction |
| OSCR-style joint known/unknown evaluation is established. | [K] | Dhamija, Günther & Boult, *Reducing Network Agnostophobia*, NeurIPS 2018, proceedings: https://proceedings.neurips.cc/paper/2018/hash/7f3d1c6f0f5a4f5f0c3e1e7b7c3c6e8f-Abstract.html | Secs. 1-3 and open-set evaluation section; confirm proceedings URL/PDF locally before final citation | The URL record should be rechecked; OSCR is a metric collision, not a Palm lifecycle study |
| Long-term Palm template selection/update is an established problem. | [K] | Chen et al., *Long-Term Representative Template for Palmprint and Palm-Vein Recognition*, IEEE Access 7 (2019), DOI: https://doi.org/10.1109/ACCESS.2019.2945064 | Secs. II-IV, pp. 145083-145094 | Does not prove real account churn or Pi action risk |
| Mobile Palm ROI, quality and open-set 1:N pipeline are established. | [K] | Palm-ID, arXiv:2401.08111v1 (2024-01-16), https://arxiv.org/html/2401.08111v1 | Secs. II-F/G, III-B/C/D, IV-A/B and V | Exact local camera/ROI path differs |
| Public Palm databases provide images/sessions, not account lifecycle labels. | [K]/[GAP] | PolyU Palmprint Database, official access page: http://www.comp.polyu.edu.hk/~biometrics/; IIT Delhi Touchless Palmprint Database, official page: https://www4.comp.polyu.edu.hk/~csajaykr/IITD/Database_Palm.htm | Database descriptions and access conditions | Public-page availability and licensing must be rechecked before acquisition; no churn event log is claimed |
| `GALLERY-CHURN` method would duplicate `G-ADMIT`. | [KILL] | Existing candidate register and `2026-09-23-palm-residual-direction-audit.md` | `01-candidate-register.md` row `G-ADMIT`; residual audit's gallery-calibration sections | Internal evidence, not external literature; coordinator must preserve the distinction |
| Fixed-gallery marginal rates may not identify terminal action risk across state changes. | [C]/[GAP] | `research/active/41-round-26-stage-risk-reconciliation.md`, `42-round-27-palm-only-reconciliation.md` | STAGE-NULL counterexample and all-start linkage requirements | Proposed negative boundary; requires actual trace and independent labels |

## Queries and failed searches

Queries run or rechecked on 2026-09-24:

- `gallery size false positive identification rate biometric 1:N open set threshold`
- `NIST FRVT 1:N FPIR FNIR gallery size official`
- `open set recognition OSCR paper primary source`
- `biometric template aging update gallery enrollment removal identity churn`
- `palmprint dynamic gallery open set identification template update`
- `palmprint public database multiple sessions longitudinal template aging`
- `PolyU palmprint database sessions official access`
- `IIT Delhi touchless palmprint database official`
- `Palm-ID mobile palm ROI quality open set 1:N arXiv`

Inconclusive/failed searches:

- No primary source was verified that combines real Palm user add/remove/update events, independent authorization labels, and a live Pi terminal action endpoint.
- No public Palm dataset inspected supplies lawful account revocation or user-deletion event sequences. Synthetic row deletion can test order-statistic sensitivity only.
- No evidence was found that a Palm-specific dynamic-gallery threshold algorithm is required; such a method would still collide with the existing `G-ADMIT` audit and standard calibration baselines.
- Some standard and proceedings pages were not fully accessible in the browser pass. Exact normative clauses and the OSCR proceedings URL must be checked against local PDFs before final thesis citation. Missing access is not evidence of novelty.

## Decision

**KILL** `GALLERY-CHURN-NULL` as a new dynamic-gallery method, threshold policy, gallery-admission policy, or Palm payment-risk claim. In that form it is a renamed `G-ADMIT` plus known 1:N/open-set and template-aging effects.

**PIVOT** only to a bounded Palm benchmark/negative result if the minimum experiment's independent labels, person/time-blocked splits, immutable state transitions, and uncertainty requirements are met. The honest endpoint is: “under these predeclared gallery-state changes, fixed-gallery summaries did or did not transport to later Palm open-set states; some effects remain non-identifiable without external lifecycle/action labels.”

Overall handoff: **PIVOT**.
