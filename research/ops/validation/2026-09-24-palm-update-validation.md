# Validation Audit: 2026-09-24 PALM-UPDATE

## Decision investigated

**Candidate:** `PALM-UPDATE` — in Palm open-set 1:N transaction recognition, after a successful acceptance, decide whether the new observation may be added to or used to update the enrolled user's template. The motivating story is cross-session drift: accepting a good later observation might improve future recognition, while one false accept, abnormal capture, or presentation attack could poison the template and create identity drift.

**Decision under audit:** whether this is a defensible Palm-specific research direction, rather than a renamed version of `E-BOUND`, `GALLERY-CHURN`, or `G-ADMIT`; and, if the positive mechanism is occupied, whether a bounded Palm transaction audit remains scientifically useful.

**Scope:** identifier-free, local VIS Palm recognition on the planned Pi transaction path, open-set 1:N, simulated/mock action only. No production payment-security claim, no claim that a successful match is proof of identity, and no automatic update is assumed safe.

## Claim under test

The strongest positive form would be:

> Under a fixed Palm matcher and open-set 1:N transaction, an online update policy that admits a newly accepted observation can reduce later cross-session owner failure or latency at equal update/search cost, while keeping false-accept-driven template poisoning and identity drift below a predeclared bound, compared with never-update, fixed multi-template, quality-gated, human-confirmed and periodic re-enrollment controls.

This claim has a coherent story, but it is not a new mechanism merely because the device is at the edge or the subject is a palm. Template selection, score-based updating, adaptive enrollment, unsupervised update, and poisoning of feedback-driven updates are established families. The auditable remainder is narrower: whether a **frozen Palm physical transaction path**, with an explicit open-set action endpoint and person/session blocking, exposes a measurable update-versus-poisoning tradeoff that is not visible in ordinary offline Palm recognition metrics.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| 1. Component collision | Chen et al., *A Scheme of Template Selection and Updating for Palmprint Authentication Systems* (2017), DOI `10.1007/978-3-319-69923-3_27`, is Palm-specific and explicitly combines template selection and updating for Palmprint authentication. Chen et al., *A Generic Template Update Framework* (IEEE Access 2019, pp. 145082–145094) treats intra-class variation, candidate-template selection and update across biometric systems. Score-based selection/update, hybrid update, nearest-neighbor selection, and template aging are already in the cited chains of the 2019 framework. | The current candidate can add a different endpoint: open-set 1:N acceptance followed by a mock transaction and subsequent sessions, with poisoning and identity drift measured as episode outcomes. That is an evaluation boundary, not an unoccupied update mechanism. | High for collision; medium for the exact Palm transaction endpoint. |
| 2. Exact-claim collision | The 2017 Palm paper directly targets Palmprint authentication template selection/update. The 2019 framework's Sections I–V and experiments cover update candidates, acceptance/update rules and intra-class variation. Ryu et al., *Template adaptation based fingerprint verification* (ICPR 2006, DOI `10.1109/ICPR.2004.1334184` as cited by the 2019 paper) and later template-aging/update work show that accepted samples can be used to adapt biometric representations. The exact policy family is therefore occupied. | The planned system's exact observation model is a live Palm capture -> ROI -> frozen matcher -> open-set 1:N -> action authorization -> optional update, and the endpoint includes future session recognition, false accepts, unknowns, and template drift. The inspected sources do not establish that this exact Pi apparatus or mock-action protocol was evaluated. That absence is not evidence of novelty. | High that the positive algorithm claim collides; low-to-medium that the bounded endpoint is under-studied. |
| 3. Boundary and impossibility | Choudhary et al., *Biometric Backdoors: A Poisoning Attack Against Unsupervised Template Updating* (EuroS&P 2020, DOI `10.1109/EuroSP48549.2020.00020`) directly demonstrates the threat to unsupervised template updating: attacker-controlled or poisoned feedback can alter future recognition. *Analysis of unsupervised template update in biometric recognition systems* (Pattern Recognition Letters 2014, DOI `10.1016/j.patrec.2013.05.021`) studies error propagation and conditions under which unsupervised updating fails. A false accept followed by update is not independently distinguishable from a genuine accepted sample using only the local match result. | A finite Palm experiment can test an explicitly bounded policy under independent labels: owner/impostor, session, attack/benign condition, action authorization, update event and later outcome. It can also produce a negative result showing that no policy using only current score/quality can certify update safety under matched false-accept and genuine-drift worlds. This is a Palm-specific audit, not a new update algorithm. | High for non-identifiability of score-only safety; medium for a useful empirical Palm boundary. |

## Assumption and identification audit

### What must be observed

Every eligible transaction episode needs a stable random episode ID and immutable pre-update record:

1. physical capture start and source frame sequence;
2. ROI success/failure, quality and rejection reason;
3. 1:N top identity, second score, margin and threshold version;
4. independently assigned authorization/identity label, including permitted mate-absent or unknown episodes;
5. action decision and mock-action result;
6. whether the observation was admitted, which template version it changed, and update cost/latency/energy;
7. later sessions using the pre-update and post-update template states;
8. any manual confirmation, re-enrollment or rollback.

Without the independent label and template-version lineage, “poisoning” is not identifiable. A later rejection could be caused by capture/ROI drift, matcher instability, gallery state, threshold choice, a bad update, or a genuine change in the user's appearance. A later acceptance does not prove that the update was correct.

### Two-world non-identifiability test

Construct matched worlds with the same locally visible current observation, score, quality and action result:

- **World G:** the accepted sample belongs to the authorized owner but is a new legitimate session condition;
- **World P:** the accepted sample is an impostor/attack that happens to cross the threshold.

If both worlds produce the same current telemetry, any score-only update rule must take the same action in both. A later template divergence can be measured only with an external identity/session label or a controlled replay. This defeats any claim that confidence, quality, or a successful open-set match alone provides a safety certificate.

### Relationship to existing candidates

- `E-BOUND-X` asks whether enrollment selection or an additional visit changes later untouched transaction outcomes. `PALM-UPDATE` changes the enrolled representation after deployment. They overlap in cross-session drift and later outcome; a positive result that only says “more/better templates help” is not distinct.
- `GALLERY-CHURN-NULL` asks whether add/remove/update gallery states transfer fixed-gallery metrics. `PALM-UPDATE` is a per-user update operation inside a gallery state. If the analysis does not preserve template lineage and distinguish gallery membership from template content, it is a gallery-churn rename.
- `G-ADMIT` asks how to admit identities/templates under open-set conditions. `PALM-UPDATE` uses a post-accept observation as an admission event. A learned/dynamic acceptance threshold or quality gate is the same rejected admission family.
- A template update algorithm without an independently labelled future endpoint is therefore not a fourth Palm direction; it is a combination of the above three families.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Chen, Yu, Yue & Li, *A Scheme of Template Selection and Updating for Palmprint Authentication Systems*, CCBR 2017, DOI `10.1007/978-3-319-69923-3_27`, published 2017 | Palmprint authentication observations; template selection and update | Palmprint authentication under intra-class variation; conference chapter, pp. 250–258 in the Springer volume record | Direct Palm-specific overlap with selection/update. | Kills “first Palm template-update algorithm” and generic Palm update novelty. Leaves open only a different endpoint or controlled failure audit. |
| Chen, Yu, Yue, Li & Guo, *A Generic Template Update Framework: The Solution for Intra-Class Variations in Biometric Systems*, IEEE Access 7 (2019), pp. 145082–145094, DOI `10.1109/ACCESS.2019.2945064` | Enrolled templates, candidate samples, similarity/selection/update rules | Framework and experiments for reducing intra-class variation; Sections I–V, especially the update framework and experimental evaluation; conclusion in Section VI | Direct overlap with any quality/score/nearest-neighbor/periodic template update policy. | Kills new generic update mechanism. Leaves open a pre-registered Palm transaction endpoint if treated as an audit. |
| Freni & Rosa, *Template Editing & Replacement: Novel Methods for Biometric Template Selection & Update*, 2010, DOI listed in Chen et al. 2019 references | Candidate biometric samples and replacement/selection | Template editing/replacement for selection and update | Overlaps fixed multi-template, replacement and update variants. | Kills “keep only representative templates” as new contribution. |
| Ryu et al., *Template adaptation based fingerprint verification*, ICPR 2006, DOI `10.1109/ICPR.2004.1334184` | Accepted fingerprint observations and template adaptation | Verification adaptation under intra-class variation | Modality differs, but mechanism and risk are direct biometric-template neighbors. | Kills mechanism-by-modality argument; leaves Palm-specific endpoint only. |
| Marcialis et al., *Analysis of unsupervised template update in biometric recognition systems*, Pattern Recognition Letters 2014, DOI `10.1016/j.patrec.2013.05.021` | Unsupervised accepted samples and update feedback | Error propagation/recognition performance under unsupervised update | Directly overlaps acceptance-triggered self-update and feedback error. | Kills “automatic update is a new edge idea”; supports the contamination audit. |
| E. Chouchane et al., *Biometric Backdoors: A Poisoning Attack Against Unsupervised Template Updating*, IEEE EuroS&P 2020, DOI `10.1109/EuroSP48549.2020.00020` | Attacker-controlled samples/feedback entering an unsupervised update loop | Future recognition manipulation through template poisoning | Directly overlaps false accept/attack -> update -> future identity drift. | Kills any positive security claim without an explicit threat model and rollback/holdout labels. Leaves a finite poisoning susceptibility test. |
| Freni, Marcialis & Roli, *Template co-update in multimodal biometric systems*, 2008, DOI `10.1007/978-3-540-74549-5_124` | Multiple biometric template streams and update decisions | Co-update consistency | Not Palm-only, but shows that adding a modality does not make update semantics new. | Relevant if VIS/NIR is later invoked as a safety guard; does not prove the current VIS path feasible. |
| `E-BOUND-X`, current Palm reconciliation (2026-09-24) | Cross-session enrollment choice and later untouched transaction | Future owner/unknown/action outcome at equal enrollment burden | Same drift and later-session endpoint; differs in when the representation changes. | Any `PALM-UPDATE` result without a matched enrollment baseline is confounded with the existing longitudinal candidate. |
| `GALLERY-CHURN-NULL`, current Palm reconciliation (2026-09-24) | Synthetic add/remove/update gallery states | Fixed-gallery metric transfer and terminal risk | “Update” can mean gallery content or per-user template; the distinction must be explicit. | Kills aggregate gallery-state analysis as evidence for template-update safety. |

## Strongest simple baseline

The strongest low-complexity baseline is not one policy but a pre-registered matrix:

1. **Never update:** retain the original enrollment template(s); rollback is automatic because no mutation occurs.
2. **Fixed multi-template:** enroll a fixed number of owner samples at enrollment and never mutate them. This separates “more representation” from online adaptation.
3. **Quality-gated update:** update only when a pre-frozen quality threshold, ROI validity rule and score/margin threshold are met. No future-frame, future-session or post-action information may enter the gate.
4. **Human-confirmed update:** hold the candidate until an authorized operator confirms identity independently of the matcher. This is a useful upper-bound/control for false-update exposure, not a deployable payment claim.
5. **Periodic re-enrollment:** replace or append templates only at predeclared visits with an independent enrollment procedure; do not use the transaction's own acceptance as its label.
6. **Oracle rollback/holdout diagnostic:** keep an untouched reference template and report whether the update would have been accepted under an independent label. This is an analysis bound, not a permitted production policy.

All policies must be compared at matched capture opportunities and report: owner FNIR/FRR-like error, mate-absent FPIR/false accept, unknown rate, update frequency, update-triggered error, template-version drift, future-session error, time, compute/energy cost, and the fraction of episodes for which the endpoint is not identifiable. A positive result that only beats `never update` but loses to fixed multi-template or periodic re-enrollment is not evidence for online updating.

## Contrarian result

The positive `PALM-UPDATE` mechanism is **KILL**. “Update the template after a successful Palm match” is an established biometric adaptation pattern; “choose a high-quality accepted sample” is a standard selection/update baseline; and “an attacker can poison unsupervised updates” is a documented security result. Recasting these as a Pi edge method does not supply a new task, guarantee, or action.

The remaining bounded path is **`PALM-UPDATE-NULL` / `PALM-UPDATE-AUDIT`**:

> On a frozen Palm VIS open-set 1:N transaction path, measure whether current acceptance/quality telemetry can distinguish beneficial cross-session adaptation from false-accept-driven template poisoning, and whether any update policy improves future untouched-session outcomes relative to fixed multi-template and periodic re-enrollment at matched capture/update cost.

This is a finite Palm-specific evaluation and possible negative-identifiability result. It should be promoted only if it demonstrates a reproducible, held-out update-versus-poisoning frontier or a strong two-world non-identifiability result that is not already explained by gallery size, enrollment selection, or ordinary template aging. It must not be presented as a new online update algorithm, secure adaptive enrollment, anti-poisoning defense, or payment-security guarantee.

## Feasibility audit

### Data and labels

- A public Palm dataset is unlikely to provide the complete sequence needed here: authorized enrollment, accepted transaction, false-accept/impostor episode, template version, later untouched transaction and action authorization. Public-data replay can support representation-level experiments, but not the live transaction claim.
- The minimum useful local study needs repeat participants across at least three disjoint visits: enrollment, update opportunity, and untouched future evaluation. The later evaluation must not be used to decide the update.
- Mate-absent/unknown labels and attack labels are ethically and operationally difficult. If only enrolled genuine participants are available, false-accept poisoning risk cannot be estimated; report that as a missing endpoint rather than silently substituting genuine drift.

### Ethics and privacy

- A template update changes persistent biometric data. Consent must explicitly cover retention, versioning, rollback, deletion, future re-use and the possibility that a false match contaminates later decisions.
- Do not use real payment credentials. Use identifier-free pseudonyms and an idempotent mock action. Keep immutable pre-update records and access-controlled versioned templates; delete them under the approved protocol.
- Human-confirmed update requires an authorized operator and a documented decision procedure; it cannot be treated as ground truth merely because an operator saw the same image.

### Hardware and software

- The update experiment must first pass the Phase 1 VIS all-start trace gate: physical capture, ROI, matcher, open-set identity/unknown, mock action and stage timing must be stable and logged.
- Template versioning, rollback and dual-reference storage are engineering prerequisites. They are not the research contribution.
- Pi compute and storage costs are measurable constraints, but a lower latency or smaller template alone does not establish research novelty.

### Statistical feasibility

- False accepts may be too rare in a small FYP cohort to estimate poisoning risk. If so, report confidence intervals and an upper bound, not a claim of safety. Deliberately forcing false accepts by lowering the threshold changes the operating point and must be labelled as a stress test.
- Person-held-out and session-held-out splits are required. Random frame splits can leak identity and make an update look beneficial.
- A single update per user cannot establish long-term drift. At minimum, predeclare update count, observation order, template capacity, threshold, rollback rule and analysis window.

## Minimum falsification experiment

Do not begin with an update model. First run a low-cost, frozen-policy audit:

1. Freeze camera, illumination, ROI, matcher, gallery, threshold, action authorization and energy measurement.
2. Collect three disjoint visits per consenting participant where feasible: initial enrollment, candidate update transaction, and untouched later transaction. Keep original and candidate frames immutable.
3. Create person/session-held-out episodes with independent labels: owner, permitted mate-absent/unknown where feasible, and a separately approved controlled impostor/attack stress cell if ethics permits.
4. Re-run the same future episodes against each pre-registered state: never-update, fixed multi-template, quality-gated, human-confirmed, and periodic re-enrollment. Keep capture opportunity and search cost matched.
5. For each accepted candidate, compute both counterfactual outcomes: future recognition with and without that candidate. Record whether the candidate was later shown to be owner, unknown, or impostor under the independent label.
6. Test the two-world boundary by matching current score/quality distributions across a beneficial-genuine and poisoning-impostor cell. If telemetry-only policies cannot separate them, record `PALM-UPDATE-NULL` as the result.
7. Kill the positive claim if never-update or fixed multi-template matches the best update policy, if periodic re-enrollment dominates at lower burden, if independent labels are absent, if only genuine sessions are available, or if any observed gain disappears under person/session blocking.

### Minimum useful outputs

- update-trigger rate and template-version lineage;
- future owner FNIR/FRR-like rate and mate-absent false-accept/FPIR-like rate;
- unknown and mock-action outcomes from all eligible starts;
- first-update and cumulative poisoning/identity-drift rate;
- p50/p95 capture-to-action time and charged update/search energy;
- confidence intervals or explicit non-identifiability bounds;
- per-state results for all five simple baselines.

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Palm-specific template selection and updating is already a named research problem. | [K] | Chen, Yu, Yue & Li, *A Scheme of Template Selection and Updating for Palmprint Authentication Systems*, CCBR 2017, DOI `10.1007/978-3-319-69923-3_27`; DOI/publisher metadata and Springer chapter record, 2017. URL: https://doi.org/10.1007/978-3-319-69923-3_27 | Chapter title and abstract/metadata; Springer record identifies the chapter as pp. 250–258. Full chapter text was not available in the workspace during this audit. | Strong title-level collision; exact algorithm details and datasets remain [GAP] until full text is obtained. |
| Generic candidate-selection/update mechanisms already address intra-class variation. | [K] | Chen et al., *A Generic Template Update Framework*, IEEE Access 7, 2019, pp. 145082–145094, DOI `10.1109/ACCESS.2019.2945064`; IEEE record and version of record. URL: https://ieeexplore.ieee.org/document/8854794/ | Sections I–VI and the reference list were identified from the version-of-record metadata/PDF landing record; page range 145082–145094. The accessible local IEEE stamp response was blocked, so detailed paragraph-level claims are limited to the indexed record and citation metadata. | Supports mechanism collision; do not overstate experimental specifics until full text is read. |
| Unsupervised updating has a documented error-propagation problem. | [K] | *Analysis of unsupervised template update in biometric recognition systems*, Pattern Recognition Letters, 2014, DOI `10.1016/j.patrec.2013.05.021`. URL: https://doi.org/10.1016/j.patrec.2013.05.021 | Abstract and article metadata; section/page-level full-text retrieval remained [GAP]. | Supports the failure mode and need for independent labels; exact Palm applicability is not assumed. |
| Template poisoning against unsupervised update is a direct security neighbor. | [K] | Chouchane et al., *Biometric Backdoors: A Poisoning Attack Against Unsupervised Template Updating*, IEEE European Symposium on Security and Privacy, 2020, DOI `10.1109/EuroSP48549.2020.00020`. URL: https://doi.org/10.1109/EuroSP48549.2020.00020 | Paper metadata and title; full proceedings PDF/sections were not available in the workspace. | Establishes direct threat-family collision, not a quantitative claim about Palm or this Pi. |
| Score-based selection/update, hybrid update and template adaptation are established baselines/families. | [K] | Chen et al. 2019 reference list: score-based update DOI `10.1109/FGCN.2008.208`; hybrid update DOI `10.1109/BTAS.2012.6374539`; adaptation DOI `10.1109/ICPR.2004.1334184`. URLs: https://doi.org/10.1109/FGCN.2008.208 ; https://doi.org/10.1109/BTAS.2012.6374539 ; https://doi.org/10.1109/ICPR.2004.1334184 | Reference entries in Chen et al. 2019; titles and DOI metadata. | Mechanism-family evidence; exact baseline implementation must be checked before numerical comparison. |
| A transaction endpoint can remain a bounded distinction only if it adds independent action labels and future-session linkage. | [C] | Current project charter and Palm-only reconciliation: `research/active/00-project-charter.md`, `42-round-27-palm-only-reconciliation.md`, `43-round-28-palm-stop-reconciliation.md`, `44-round-29-gallery-churn-reconciliation.md`. | Candidate gates and all-start trace requirements in the cited local files. | Project evidence, not external proof; depends on the actual frozen executable and approved data collection. |
| Score/quality-only update safety is not identifiable in matched genuine/impostor worlds. | [C] | Inference from the two-world construction above, supported by the unsupervised-update failure and poisoning neighbors. | Formal observation/action argument in this audit; no theorem claimed. | Must be tested with matched physical cells and independent labels; otherwise remains a conjecture. |
| Public Palm data can support the full live update-to-action claim. | [GAP] | No source inspected in this audit establishes authorized lifecycle, template-version lineage, or mock-action labels in a public Palm dataset. | Dataset metadata audit not yet complete. | Do not infer absence globally; check the selected dataset and permissions before any experiment. |

## Queries and failed searches

### Queries run on 2026-09-24

- `biometric template update adaptive enrollment poisoning feedback loop primary paper`
- `palmprint template update long term template selection cross session paper`
- `biometric template update survey self update enrollment impostor contamination paper`
- `palmprint recognition template aging longitudinal enrollment selection paper`
- `"A Generic Template Update Framework" palmprint authors DOI`
- `"A Scheme of Template Selection and Updating for Palmprint Authentication Systems"`
- `biometric template update evaluation impostor contamination primary paper`
- `biometric backdoors poisoning attack unsupervised template updating`

### Retrieval limits and unresolved searches

- IEEE Xplore's PDF/stamp endpoint returned a blocked/insufficient response in the local retrieval attempt; the 2019 paper's DOI, page range and version-of-record metadata were verified through Crossref/IEEE metadata, but paragraph-level PDF reading remains incomplete.
- The 2017 Palm-specific chapter's publisher metadata and DOI were verified, but its full text was not retrieved. The collision conclusion is therefore high-confidence at the problem/title level and medium-confidence at the exact algorithm level.
- No claim is made that the inspected set is globally complete. The exact Palm hardware, open-set 1:N, post-action update and poisoning combination requires a later full-text citation-chain audit if the coordinator keeps the bounded audit.
- The project has no confirmed participant count, three-visit consent, mate-absent roster, attack material, independent authorization oracle, or charged per-update energy measurement. These remain feasibility gates, not assumptions.

## Decision

**KILL** as a positive online template-update algorithm or secure adaptive-enrollment thesis.

**PIVOT** only to `PALM-UPDATE-NULL` / a bounded Palm transaction audit if and only if the frozen VIS all-start trace, three disjoint visits, independent labels, template versioning, and ethical permissions become available. The audit must compare the five simple baselines and may conclude non-identifiability or no useful update frontier. It is a lower-priority extension of `E-BOUND-X`/`GALLERY-CHURN-NULL`, not a promoted fourth method direction.

PIVOT
