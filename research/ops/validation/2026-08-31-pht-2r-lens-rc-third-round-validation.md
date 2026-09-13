# Validation Audit: 2026-08-31 PHT-2R and LENS-RC

## Decision investigated

Try to falsify the two Amber proposals in
`2026-08-31-broad-reference-intervention-divergence.md`, rather than improve
their presentation:

1. `PHT-2R`: an edge node decides `accept / check one or two named reference
   buffers / unknown` for a non-production pH record, claiming a benefit from
   selecting a separated pair when gain and offset drift are ambiguous.
2. `LENS-RC`: an edge node decides `retain / capture a fixed chart / unknown`
   for a non-personal tabletop image record, claiming a benefit from an
   intervention-conditioned chart capture over passive camera-health features.

This audit is limited to benign, non-regulatory benches. It does not authorize
process actuation, environmental compliance measurement, clinical use,
surveillance, or collecting personal images.

## Claim under test

`PHT-2R` claims a lower held-out false-accepted interval-decision rate at the
same reference-use budget than fixed one-buffer, fixed two-buffer, and generic
uncertainty-only scheduling. `LENS-RC` claims a lower held-out false-retain
rate at the same chart-capture budget than passive quality/reference features
and fixed chart schedules.

## Three-round novelty audit

| Candidate / round | Evidence for collision | Evidence for remaining distinction | Verdict |
| --- | --- | --- | --- |
| PHT-2R: 1. component collision | [KILL] Cho et al. already built an *automated* pH/EC probe drift-compensation system using both one- and two-point normalization, stated that one point handles offset and two points handles sensitivity variation, and evaluated against laboratory analysis. Hurst et al. separately allocate a finite calibration budget dynamically from uncertainty. | [GAP] Neither inspected source reports the exact phrase `accept / unknown` or an adaptive *identity* choice among pH 4/7/10. | **Red as a component combination.** It is standard two-point calibration plus known calibration scheduling plus an abstention threshold. |
| PHT-2R: 2. exact-claim collision | [KILL] Cho et al.'s task is pH/EC accuracy and sensor-status information from automated reference measurements; its two-point method explicitly addresses both drift and sensitivity variation. Hurst et al. dynamically changes calibration intervals under a budget and compares to fixed intervals. The proposed false-accept metric relabels their accuracy/uncertainty result as a three-action record policy. | [GAP] No inspected primary source exactly evaluates the same finite-buffer `false accept / unknown / use` frontier on a student pH bench. Absence is not evidence of distinction. | **Red in substance.** The only remaining syntactic difference is the metric/reporting layer. |
| PHT-2R: 3. boundary / impossibility | [KILL] Under its stated stable affine model with equal-variance buffer readings, two reference values are all that identify slope and offset. The determinant of the two-point design matrix is `(q_2-q_1)^2`; hence maximum separation is the non-adaptive D-optimal choice. One buffer has rank one and cannot identify both parameters. If error is effectively offset-only, the second point has no decision-relevant value. | [GAP] An adaptive query identity could become nontrivial only after adding and measuring a new non-uniform noise, contamination, time-to-equilibrium, or buffer-depletion model. None is currently specified or independently labelable. | **KILL.** The advertised information result is routine algebra in the candidate's own assumptions, and is unidentifiable outside them without new measured state. |
| LENS-RC: 1. component collision | [KILL] Camera calibration with standardized charts and active targets is established optical metrology. Ma et al. provide a low-cost bounded streaming camera-health state machine with clean references, false-alarm constraints, explicit scope, and public diagnostics. SIDL blocks a new dirty-lens dataset/restoration contribution. | [C] I did not find an inspected source combining a commanded chart capture, `retain/chart/unknown`, and the exact false-retain/capture frontier. | **Amber only for the narrowly defined intervention protocol; Red for any generic camera-health or chart-calibration claim.** |
| LENS-RC: 2. exact-claim collision | [KILL] The physical action itself is routine calibration/self-test, while Ma et al. already implement the closest low-cost passive alternative and evaluate error controls. Established camera-calibration work already uses standardized charts to measure camera response. | [GAP] No direct paper retrieved with precisely the proposed budgeted router. | **Not sufficient to lock.** A new action label and an application-specific metric do not establish a new CS mechanism. |
| LENS-RC: 3. boundary / impossibility | [KILL] A chart only observes the camera/lens/illumination pathway. It cannot, by itself, establish that a different scene frame yields the right count/condition. If two scenes with different record truths have the same task observation and the same chart outcome, no policy using those observations can distinguish them. | [C] A much narrower one-sided claim is possible: conditioned on fixed exposure, illumination and chart geometry, the chart can be a witness of named image-path degradations. | **PIVOT REQUIRED.** The current `record-validity` target is not identified by the proposed intervention. |

## Assumption and identification audit

### PHT-2R

The candidate declares

`m = a*z + b + e`, with stable `a,b` in an episode.  For references `q1,q2`,
the calibration design matrix is

`X = [[q1, 1], [q2, 1]]`.

Its determinant is `q1 - q2`.  Therefore:

- [K] one reference has rank one, so it constrains only `a*q + b`; it cannot
  identify both `a` and `b`.
- [KILL] for two equal-noise references, the information determinant is
  proportional to `(q1-q2)^2`. Choosing the most separated validated buffers
  is a fixed design rule, not a learned adaptive policy.
- [KILL] after a two-point update, `accept` is the standard interval rule:
  accept only when the estimated pH confidence interval lies on one side of the
  declared non-regulatory boundary; otherwise issue `unknown`. It is not a
  distinct calibration mechanism.

The claimed benefit can survive only if a physical property makes the fixed
endpoint pair inadmissible at some times: for example, measured buffer-specific
noise, carry-over, settling time, depletion, or a nonlinear response. That is
not currently an assumption that the node can observe independently. If it is
added post hoc after looking at the same bench data, the apparent advantage
would be selection leakage rather than evidence of adaptive sensing.

### LENS-RC

Write the task image as `Y = F(S,H,L)+e`, where `S` is scene state, `H` is
camera/lens state, and `L` is illumination/exposure state. A fixed-chart image
is `C = G(H,L)+eta` (under the proposal it contains no independent observation
of `S`). Suppose two scene states `S0,S1` have different record truths but
produce the same task observation under a given camera state, while the chart
outcome is unchanged because the chart is separate from the scene. Then
`(Y,C)` is identical in both worlds and no `retain/chart/unknown` rule based on
those values can certify which record truth occurred. This is a direct
counterexample to the broad claim "chart capture validates the record."

It does not deny that a chart can reveal a named image-path degradation. It
means the claim must be narrowed to a *camera-health witness* and must state a
separate task-error link. A chart pass cannot certify focus, contamination, and
task correctness beyond the chart's spatial/photometric coverage. Ma et al.'s
declared scope independently illustrates the issue: mean-preserving defocus,
subtle partial covers and geometry changes are outside or weak for its passive
statistics; adding a chart does not make them automatically identified.

## Direct-neighbor table

| Work | Inputs / actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Cho et al., *Journal of the ASABE* 67(5), 2024 | Automated measurements of normalization solutions; one- and two-point normalization of pH/EC probes. | Drift compensation and sensor-status information, compared with sampling/laboratory analysis in open and closed hydroponics. | Directly overlaps low-cost pH probe, automated reference action, offset versus sensitivity handling, and independent laboratory comparison. | [KILL] PHT's physical method and basic evaluation are occupied. It does not by itself use `unknown`, but that is a threshold/reporting wrapper. |
| Hurst et al., arXiv:2506.09186v1, 2025 | Chemical-sensor response-function correction plus uncertainty-driven calibration *interval* optimization. | Accuracy versus calibration budget, compared with fixed intervals on dissolved-oxygen sensors. | Directly overlaps adaptive decision *whether/when* to spend calibration budget and a fixed-schedule baseline. | [KILL] Generic scheduler component. It does not select pH buffer identity. |
| Bresnahan et al., *Limnology and Oceanography: Methods* 19, 2021 | Autonomous sensor toggles ambient sample and calibration standard sources, with operator-set sampling and calibration frequency. | In-situ pH calibration operation/test-tank validation. | Automated known-reference fluid handling and two distinct inlet behavior. | [KILL] Treating a local pH reference action as unexplored system design. It is not a student-cost-equivalent setup. |
| Cheng and Zhu, *Sensors* 5, 2005 | pH-meter calibration analysis. | Calibration and electrode behavior. | Foundational pH calibration direct neighbor. | [KILL] Any assertion that slope/offset separation itself is a research contribution. |
| Ma, Yan and Wu, arXiv:2607.14760v1, 2026 | Clean-only sliding reference; sampled luminance/gradient/grid features; bounded state machine. | Low-FPR camera-health/tamper monitoring with controlled, public, and boundary evaluations. | Strongest passive low-cost rival for LENS-RC. It has state, explicit reference hygiene, action-like alarm/health output, and false-alarm budget. | [KILL] A passive quality/clean-reference baseline must be fully reproduced or fairly reimplemented; a new chart router cannot be compared only to a generic blur score. Leaves an external-chart action untested. |
| Peli et al., *Journal of Vision* 2009, PMC4080814 | Standardized gray-scale chart, controlled camera settings, OECF/MTF/lens characterization. | Camera response calibration, including limitations from lens, exposure, gain and illumination. | Direct chart-witness and camera-quality measurement family. | [KILL] Generic fixed-chart self-test is normal calibration, not a new sensing modality. Also shows the need for controlled settings. |
| Schmalz, Forster and Angelopoulou, *Optical Engineering* 50(11), 2011 | Active display calibration target versus passive checkerboard. | Camera calibration/reprojection and stereo reconstruction accuracy. | Direct active-reference-target family. | [KILL] An "active reference target" is established metrology. Leaves only a constrained routing/evaluation question. |
| Choi, Park and Kim, AAAI-25 SIDL | Physically degraded smartphone lens images over many scenes. | Lens-soiling restoration and benchmark. | Dirty-lens data/failure variation. | [KILL] New dirty-lens model/dataset as the alleged contribution. It does not solve chart scheduling. |

## Strongest simple baselines

### PHT-2R baseline that should be assumed dominant

At every planned calibration event, use the validated extreme pair (for example
the buffered values spanning the declared measurement interval), compute the
ordinary two-point calibration and propagated interval, then:

`accept` iff the whole interval is inside or outside the recorded range;
otherwise `unknown`.

Compare this to no check and a fixed one-buffer offset correction. For an equal
reference-use budget, the periodic two-point baseline needs no posterior policy
or learned selector. If PHT-2R does not beat it on electrode-held-out,
temperature-held-out and solution-batch-held-out episodes, there is no residual
research claim. If it does beat it only after fixing endpoint selection from the
same data, it needs a preregistered physical explanation and new holdout cells.

### LENS-RC fair active-router baseline

Every candidate LENS experiment needs both of these baselines, frozen before
the held-out blocks:

1. a Ma-style passive clean-reference monitor (luminance, gradient/edge and
   clean-reference difference with a health/unknown gate), and
2. fixed-period chart capture using the *same chart, exposure, actuation time,
   compute, and capture budget* as the proposed router.

The proposed active policy must also be compared to `always chart` at matching
or more conservative false-retain target. Comparing it only to a generic
no-reference image-quality score is unfair because Ma et al. already show
strong low-cost reference-based controls and boundary diagnostics.

## Contrarian result

### PHT-2R is routine calibration plus scheduling, not the intended FYP claim

[KILL] Cho et al.'s 2024 primary system is the decisive collision. Its official
abstract says it uses one- and two-point normalization for pH/EC drift; one
point compensates offset, and two points address sensitivity variation. This
matches the proposed gain-versus-offset motivation almost exactly. Hurst then
occupies the generic uncertainty-driven decision of when to pay a calibration
cost. The candidate's remaining elements, an abstain label and false-accept
rate, follow directly from a calibrated uncertainty interval and do not create
a distinct action or observation model.

**PHT-2R should not be implemented as the FYP primary direction.** It can be a
small calibration exercise or negative-control appendix only. A negative result
that extreme fixed two-point calibration dominates is predictable and would not
be a new empirical boundary absent a newly specified physical observation
model.

### LENS-RC is a health-monitor pivot, not a record-validity thesis

[KILL] A chart is not independent ground truth for a scene-derived count or
condition. The current claim confuses evidence about `H` (image path) with
evidence about `S` (scene truth). The strongest well-supported limited claim is
therefore: under fixed camera pose, exposure and illumination, a reference
target may witness a predeclared subset of camera-path degradations. That is a
sensor-health measurement, not general record validity.

The remaining empirical question is potentially useful but too weakly bounded
to lock: can an active chart at a stated cost improve a predefined camera-health
alarm frontier over passive clean-reference monitoring? It needs a physical
condition protocol before any method claim. If retained, it should become a
short **PIVOT preflight**, not a thesis commitment.

## Feasibility audit

| Candidate | Low-cost demo by 2026-12 | Truth / protocol problem | Safety / ethics | 2027-H1 work only if preflight passes |
| --- | --- | --- | --- | --- |
| PHT-2R | Hardware and nonhazardous commercial buffers are plausibly cheap, but this is not enough to establish a research contribution. | Reference buffers used for online calibration cannot also silently be the unknown-sample truth. Each unknown episode needs a separately blinded, traceably prepared value or independent laboratory comparator. Carry-over, temperature, electrode age and settling time must be randomized/block-logged. | Non-personal and manageable only as a benign teaching bench; no potable-water, hydroponic dosing, environmental compliance, or safety action. Disposal/SDS and advisor lab rules remain [GAP]. | No thesis optimization recommended. At most reproduce fixed one/two-point outcomes as a control. |
| LENS-RC | Webcam/Pi camera, a stable mount, non-personal tabletop objects and a chart make a visual December demo plausible. | A home-printed chart has unknown reflectance/geometry and is itself illumination-dependent. The task truth must be independently created (object count/condition controlled behind the operator's policy) and condition labels cannot be fed into routing features. Need camera-held-out and scene-held-out blocks. | No faces, no surveillance, no production inspection, no actuation. Reversible lens/illumination changes only. | Only after a pre-registered `chart distinguishes named camera condition` test with fixed exposure/lighting, passive baseline and fixed-chart baseline. A null result is valuable only as a narrow condition map. |

Official Cognex documentation warns that printed calibration-grid quality, lens
quality, vibration and image exposure/gain all limit calibration accuracy; this
supports treating a casual printed chart as an unverified reference rather than
ground truth. See the source in the ledger.

## Evidence ledger

| Claim | Label | Primary / official source and version | Exact section / page read | Scope / caveat |
| --- | --- | --- | --- | --- |
| Automated hydroponic pH/EC compensation used one- and two-point normalization; one point handles offset and two points sensitivity variation; results were compared to sampled laboratory analysis. | [KILL] | Cho et al., *Automated Drift Compensation System for Electrical Conductivity and pH Probes in Hydroponic Systems*, *Journal of the ASABE* 67(5):1203-1215 (2024), DOI https://doi.org/10.13031/ja.15603 | Official ASABE abstract, p. 1203 metadata/abstract, especially Highlights and paragraphs beginning "In this study" and "The results indicated". | Full text was subscriber-gated; the publisher's official abstract is explicit enough for the collision but exact apparatus details remain unverified. |
| GPR correction plus uncertainty-driven calibration *schedule* optimization is evaluated against fixed calibration intervals, with a finite calibration budget. | [KILL] | Hurst et al., *Not all those who drift are lost: Drift correction and calibration scheduling for the IoT*, arXiv:2506.09186v1, 2025-06-10, https://arxiv.org/html/2506.09186v1 | Abstract; Sec. 4.2 "Calibration Schedule Optimisation"; Sec. 5.3 and Fig. 11/Table 3; Conclusion. | Dissolved oxygen, not pH, and schedules interval rather than buffer identity. It is a component collision, not proof of exact endpoint collision. |
| Autonomous pH system toggles ambient and calibration-standard sources, allows calibration frequency setting, and tests distinct inlet flushing. | [KILL] | Bresnahan et al., *Autonomous in situ calibration of ion-sensitive field effect transistor pH sensors*, *Limnology and Oceanography: Methods* 19(2):132-144 (2021), DOI https://doi.org/10.1002/lom3.10410 | "Operation" and "Assessment / Test tank" sections at official HTML. | Oceanographic ISFET system, not a low-cost glass electrode. It invalidates novelty of automated reference-fluid action, not feasibility equivalence. |
| A standardized chart plus controlled camera settings measures OECF; response may depend on lens/exposure/gain, so a chart is not a context-free witness. | [KILL] | Peli et al., *Camera calibration for natural image studies and vision research*, *Journal of Vision* 9(4):9 (2009), PMC4080814, https://pmc.ncbi.nlm.nih.gov/articles/PMC4080814/ | Sec. 3 equipment; Sec. 6A, especially paragraphs P53-P61; Sec. 8/Table 1. | Scientific camera calibration, not a chart-router paper; strong against treating chart capture as a new observation model. |
| Active calibration targets are an established camera-calibration family. | [KILL] | Schmalz, Forster and Angelopoulou, *Camera Calibration: Active versus Passive Targets*, *Optical Engineering* 50(11), 2011, DOI https://doi.org/10.1117/1.3643726 | Abstract and Sec. 1 as available from publisher/search record. | Foundational metrology collision; active display differs from a printed chart. |
| Low-cost streaming camera-health monitor uses a clean-only reference, bounded state, explicit detector scope, false-alarm constrained evaluation and transparent baselines. | [KILL] | Ma, Yan and Wu, *Clean-Reference Streaming Detection of Lens Occlusion and Photometric Transitions for Camera Tamper Monitoring*, arXiv:2607.14760v1, 2026-07-16, https://arxiv.org/html/2607.14760v1 | Abstract; Secs. I-III, especially lines 67-79 and 118-128; Sec. V-A/B, lines 200-219; Supplementary V, XII and XIII as linked from the paper. | Preprint and passive only; strongest fair baseline, not a formal collision for a separately controlled chart intervention. |
| Physically degraded smartphone lens data/restoration is already a 2025 task; new dirty-lens model/dataset is not a direction. | [KILL] | Choi, Park and Kim, *SIDL: A Single Image Dataset for Lens Soiling and Its Application*, AAAI-25, 2025-04-11, https://ojs.aaai.org/index.php/AAAI/article/view/32257/34412 | PDF pp. 2545 (Introduction) and 2552 (Limitations/Conclusion). | Does not cover active chart routing. |
| A printed grid, lens quality, mount vibration, over-exposure and gain limit camera-calibration accuracy. | [K] | Cognex, *Calibration Accuracy*, official In-Sight documentation, accessed 2026-08-31, https://docs.cognex.com/is_650/web/en/ise/Content/How_To/Calibration/CalibrationAccuracy.htm | Entire official page, bullet list under "The accuracy of the calibration depends on..." | Vendor documentation, used only for bench feasibility/risk, not novelty. |

## Queries and failed searches

Queries run on 2026-08-31:

- `pH electrode two point calibration slope offset drift adaptive calibration reference buffer selection sensor 2024 2025 paper`
- `pH sensor adaptive calibration scheduling reference measurements drift active sensing paper`
- `"calibration scheduling" "sensor drift" 2025 paper IoT`
- `"Automated Drift Compensation System for Electrical Conductivity and pH Probes in Hydroponic Systems"`
- `camera reference chart self calibration sensor health active capture lens contamination reference target paper 2024 2025`
- `"reference chart" "camera health" monitoring image quality paper`
- `"test chart" camera "lens contamination" monitoring paper`
- `camera self test calibration target image quality degradation monitoring reference chart paper`
- `industrial vision camera health monitoring calibration chart active reference image quality inspection`

Failed/incomplete retrievals:

- Cho et al.'s full 2024 ASABE article requires subscription access; its official
  abstract was inspected, but exact equations, buffer values and implementation
  costs are [GAP].
- No inspected primary work exactly matched LENS-RC's three-action,
  chart-budgeted false-retain frontier. This is an absence after the listed
  searches, **not** a novelty result.
- No current price, product lifetime, traceable buffer certificate, chart
  reflectance certificate, lighting rig, or advisor permission has been
  verified. These are feasibility [GAP]s.

## Decision

**PIVOT.**

- `PHT-2R`: **KILL** as a primary FYP direction. The two reference points are
  routine calibration, the maximal separation choice follows algebraically
  under the proposed model, and the residual scheduling action is directly
  crowded by Hurst et al. plus the 2024 pH/EC automation paper.
- `LENS-RC`: **PIVOT / HOLD only for preflight.** Do not present a chart pass
  as record validity. The sole defensible next gate is a preregistered physical
  witness test for named camera-path degradations under locked exposure,
  illumination and geometry, against Ma-style passive monitoring and a
  fixed-period chart. If that chart does not improve a health-alarm frontier on
  camera- and scene-held-out blocks, kill it. Even a positive result requires a
  second exact-claim audit before any Amber promotion.
